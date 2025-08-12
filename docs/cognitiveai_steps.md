STEP 1: Observability Foundatoin 

Awesome — kicking off **Step 1: Observability foundation** exactly as agreed. I’ll add org‑scoped run tracing so every node emits typed events you can debug, review, and regress-test.

I’ll do this in **one thin vertical slice**, then pause for your review before wiring the decorator into nodes.

---

# Step 1 — Code Drop (models → serializers → views → URLs → telemetry helper)

## 1) `brain/models.py`

Adds `BrainRun` and `BrainRunEvent` with org scoping, status enums, and useful indexes.

```python
# brain/models.py
import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone

class BrainRun(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        NEEDS_REVIEW = "needs_review", "Needs Review"
        FAILED = "failed", "Failed"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "accounts.Organization", on_delete=models.CASCADE, related_name="brain_runs"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="brain_runs"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    current_node = models.CharField(max_length=100, blank=True, default="")
    error_code = models.CharField(max_length=100, blank=True, default="")
    error_message = models.TextField(blank=True, default="")
    meta = models.JSONField(default=dict, blank=True)  # input config, doc ids, etc.

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["created_by"]),
            models.Index(fields=["created_at"]),
        ]

    def mark_started(self):
        self.status = self.Status.RUNNING
        self.started_at = timezone.now()
        self.save(update_fields=["status", "started_at", "updated_at"])

    def mark_completed(self):
        self.status = self.Status.COMPLETED
        self.finished_at = timezone.now()
        self.save(update_fields=["status", "finished_at", "updated_at"])

    def mark_failed(self, code: str, message: str):
        self.status = self.Status.FAILED
        self.error_code = code
        self.error_message = message[:8000]
        self.finished_at = timezone.now()
        self.save(update_fields=["status", "error_code", "error_message", "finished_at", "updated_at"])


class BrainRunEvent(models.Model):
    class EventType(models.TextChoices):
        INPUT = "input", "Input"
        OUTPUT = "output", "Output"
        VALIDATION = "validation", "Validation"
        ERROR = "error", "Error"
        INFO = "info", "Info"

    id = models.BigAutoField(primary_key=True)
    run = models.ForeignKey(BrainRun, on_delete=models.CASCADE, related_name="events")
    seq = models.PositiveIntegerField()  # monotonically increasing per run
    node_name = models.CharField(max_length=100)
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["run", "seq"]
        unique_together = [("run", "seq")]
        indexes = [
            models.Index(fields=["run", "seq"]),
            models.Index(fields=["node_name"]),
            models.Index(fields=["event_type"]),
        ]
```

> **Why**:
>
> * `BrainRun` is the episodic container (org/user scoped) with state and error fields.
> * `BrainRunEvent` is the append‑only trace (input/output/validation/error) with a simple `seq` you can replay.
> * Helper methods make status transitions explicit and auditable.

---

## 2) `brain/admin.py`

Registers admin with useful list displays.

```python
# brain/admin.py
from django.contrib import admin
from .models import BrainRun, BrainRunEvent

@admin.register(BrainRun)
class BrainRunAdmin(admin.ModelAdmin):
    list_display = ("id", "organization", "created_by", "status", "current_node", "created_at", "finished_at")
    list_filter = ("status", "organization")
    search_fields = ("id", "current_node", "error_code", "error_message")
    readonly_fields = ("created_at", "updated_at", "started_at", "finished_at")

@admin.register(BrainRunEvent)
class BrainRunEventAdmin(admin.ModelAdmin):
    list_display = ("id", "run", "seq", "node_name", "event_type", "created_at")
    list_filter = ("event_type", "node_name")
    search_fields = ("run__id", "node_name")
    readonly_fields = ("created_at",)
```

---

## 3) `brain/serializers.py`

Typed I/O for runs and events; org & user set from request.

```python
# brain/serializers.py
from rest_framework import serializers
from .models import BrainRun, BrainRunEvent

class BrainRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrainRun
        read_only_fields = (
            "id","status","started_at","finished_at","current_node",
            "error_code","error_message","created_at","updated_at",
        )
        fields = ("id","organization","created_by","status","started_at","finished_at",
                  "current_node","error_code","error_message","meta","created_at","updated_at")

    def create(self, validated_data):
        # Force org/user from request context for safety
        request = self.context["request"]
        validated_data["organization"] = request.user.organization
        validated_data["created_by"] = request.user
        return super().create(validated_data)


class BrainRunEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrainRunEvent
        read_only_fields = ("id","run","seq","node_name","event_type","payload","created_at")
        fields = ("id","run","seq","node_name","event_type","payload","created_at")
```

---

## 4) `brain/utils/telemetry.py`

Single source of truth for emitting events + a decorator to auto‑log node I/O.

```python
# brain/utils/telemetry.py
from typing import Callable, Any, Dict
from django.db import transaction
from ..models import BrainRun, BrainRunEvent

def _next_seq(run: BrainRun) -> int:
    # Lightweight way to get next sequence; safe under transaction
    last = BrainRunEvent.objects.filter(run=run).order_by("-seq").values_list("seq", flat=True).first()
    return (last or 0) + 1

@transaction.atomic
def emit_event(run: BrainRun, node_name: str, event_type: str, payload: Dict[str, Any]) -> int:
    seq = _next_seq(run)
    BrainRunEvent.objects.create(
        run=run, seq=seq, node_name=node_name, event_type=event_type, payload=payload or {}
    )
    return seq

def log_node_io(node_name: str):
    """
    Decorator for node functions: logs INPUT and OUTPUT events automatically.
    Node signature: func(run: BrainRun, state: dict) -> dict
    """
    def _wrap(func: Callable[[BrainRun, dict], dict]):
        def _inner(run: BrainRun, state: dict) -> dict:
            emit_event(run, node_name, BrainRunEvent.EventType.INPUT, {"state": state})
            try:
                result = func(run, state)
                emit_event(run, node_name, BrainRunEvent.EventType.OUTPUT, {"state": result})
                return result
            except Exception as exc:
                emit_event(run, node_name, BrainRunEvent.EventType.ERROR, {"message": str(exc)})
                run.mark_failed(code=f"{node_name}_error", message=str(exc))
                raise
        return _inner
    return _wrap
```

---

## 5) `brain/views.py`

ViewSets for runs and run events, org‑scoped. Includes a `start` action as a thin entrypoint.

```python
# brain/views.py
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction

from .models import BrainRun, BrainRunEvent
from .serializers import BrainRunSerializer, BrainRunEventSerializer
from .utils.telemetry import emit_event

class OrgScopedMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        return qs.filter(organization=user.organization)

class BrainRunViewSet(OrgScopedMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BrainRunSerializer
    queryset = BrainRun.objects.select_related("organization","created_by")

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        run = self.get_object()
        if run.status not in [BrainRun.Status.PENDING, BrainRun.Status.NEEDS_REVIEW]:
            return Response({"detail":"Run already started or finished."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            run.mark_started()
            emit_event(run, "orchestrator", BrainRunEvent.EventType.INFO, {"message":"Run started"})

        # NOTE: In Step 2 we’ll hand this to LangGraph; for now we just acknowledge.
        return Response(self.get_serializer(run).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def trace(self, request, pk=None):
        run = self.get_object()
        events = run.events.all().order_by("seq")
        data = BrainRunEventSerializer(events, many=True).data
        return Response(data, status=status.HTTP_200_OK)


class BrainRunEventViewSet(OrgScopedMixin,
                           mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BrainRunEventSerializer
    queryset = BrainRunEvent.objects.select_related("run","run__organization")
```

---

## 6) `brain/urls.py`

Registers the routes; we’ll include this from `config/urls.py`.

```python
# brain/urls.py
from rest_framework.routers import DefaultRouter
from .views import BrainRunViewSet, BrainRunEventViewSet

router = DefaultRouter()
router.register(r"runs", BrainRunViewSet, basename="brain-run")
router.register(r"events", BrainRunEventViewSet, basename="brain-run-event")

urlpatterns = router.urls
```

### Add to `config/urls.py`

```python
# config/urls.py (snippet)
from django.urls import path, include

urlpatterns = [
    # ...
    path("api/brain/", include("brain.urls")),  # ← add this line
    # ...
]
```

---

## 7) Example: wrapping a node with logging

When we implement real node logic, decorate it so inputs/outputs/errors are auto‑traced.

```python
# brain/langgraph_flow/nodes/parse_documents.py
from ..state.schema import GraphState  # your existing Pydantic state
from ...utils.telemetry import log_node_io
from ...models import BrainRun

@log_node_io("parse_documents")
def run_parse_documents(run: BrainRun, state: dict) -> dict:
    # TODO: Replace placeholder with real parsing (Step 2).
    # Keep it deterministic & small for now.
    state = dict(state or {})
    state["parsed_docs"] = []
    return state
```

In the orchestrator (graph) entrypoint you’ll pass the `BrainRun` instance and the state; every node emits INPUT/OUTPUT/ERROR with consistent payloads.

---

# How to roll this out (quick)

1. **Migrations**: `python manage.py makemigrations brain && python manage.py migrate`
2. **Auth**: ensure `IsAuthenticated` works (Session or Token); we’ll wire proper auth in Step 2.
3. **Smoke test**:

   * `POST /api/brain/runs/` (empty body is fine; org/user auto‑set).
   * `POST /api/brain/runs/{id}/start/` → returns `running` + first INFO event.
   * `GET /api/brain/runs/{id}/trace/` → see events list.

---

# What this unlocks

* **Immediate debuggability**: Inspect every node’s I/O without combing logs.
* **Human‑in‑the‑loop**: We can add `needs_review` transitions later and show the exact payload to approve/modify.
* **Regression tests**: Stable event schema allows snapshot testing per node.
* **Org safety**: All run data is scoped by organization by default.

---

