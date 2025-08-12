#brain/models.py

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

    class RunType(models.TextChoices):
        DOCUMENT_PARSING = "doc_parse", "Document Parsing"
        ROADMAP_GENERATION = "roadmap_gen", "Roadmap Generation"
        ENTITY_EXTRACTION = "entity_extract", "Entity Extraction"
        STRATEGIC_ANALYSIS = "strategic_analysis", "Strategic Analysis"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "accounts.Organization", on_delete=models.CASCADE, related_name="brain_runs"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="brain_runs"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    run_type = models.CharField(max_length=20, choices=RunType.choices, null=True, blank=True)
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
            models.Index(fields=["run_type", "status"]),
        ]

    def __str__(self):
        return f"BrainRun {self.id} ({self.status})"

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

    def mark_needs_review(self, reason: str = ""):
        self.status = self.Status.NEEDS_REVIEW
        self.error_message = reason[:8000] if reason else ""
        self.save(update_fields=["status", "error_message", "updated_at"])

    @property
    def duration_seconds(self):
        if self.started_at and self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None


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
    duration_ms = models.PositiveIntegerField(null=True, blank=True)  # For OUTPUT events
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["run", "seq"]
        unique_together = [("run", "seq")]
        indexes = [
            models.Index(fields=["run", "seq"]),
            models.Index(fields=["node_name"]),
            models.Index(fields=["event_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Event {self.seq}: {self.node_name} ({self.event_type})"
