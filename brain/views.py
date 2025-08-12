# brain/views.py

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from django.db import transaction
from django.db.models import Count, Q, QuerySet

from .models import BrainRun, BrainRunEvent
from .serializers import BrainRunSerializer, BrainRunEventSerializer, BrainRunSummarySerializer
from .utils.telemetry import log_info_event

class OrgScopedMixin:
    """Mixin to scope querysets to the user's organization"""
    request: Request  # Type hint for the request attribute
    
    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()  # type: ignore
        user = self.request.user
        organization = getattr(user, 'organization', None)
        if not organization:
            return qs.none()
        
        # Handle different model types
        model = qs.model
        if hasattr(model, 'organization'):
            # Direct organization field (e.g., BrainRun)
            return qs.filter(organization=organization)
        elif hasattr(model, 'run'):
            # Nested through run field (e.g., BrainRunEvent)
            return qs.filter(run__organization=organization)
        else:
            # Fallback - no organization filtering
            return qs

class BrainRunViewSet(OrgScopedMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BrainRunSerializer
    queryset = BrainRun.objects.select_related("organization", "created_by")

    def get_serializer_class(self):
        if self.action == 'list':
            return BrainRunSummarySerializer
        return BrainRunSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # Add filtering by status and run_type
        status_filter = self.request.query_params.get('status')
        run_type_filter = self.request.query_params.get('run_type')
        
        if status_filter:
            qs = qs.filter(status=status_filter)
        if run_type_filter:
            qs = qs.filter(run_type=run_type_filter)
            
        return qs

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        run = self.get_object()
        if run.status not in [BrainRun.Status.PENDING, BrainRun.Status.NEEDS_REVIEW]:
            return Response(
                {"detail": "Run already started or finished."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            run.mark_started()
            log_info_event(run, "orchestrator", "Run started", {"user_id": request.user.id})

        # NOTE: In Step 2 we'll hand this to LangGraph; for now we just acknowledge.
        return Response(self.get_serializer(run).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def trace(self, request, pk=None):
        run = self.get_object()
        events = run.events.all().order_by("seq")
        
        # Optional filtering by event type or node name
        event_type_filter = request.query_params.get('event_type')
        node_name_filter = request.query_params.get('node_name')
        
        if event_type_filter:
            events = events.filter(event_type=event_type_filter)
        if node_name_filter:
            events = events.filter(node_name=node_name_filter)
        
        data = BrainRunEventSerializer(events, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def mark_needs_review(self, request, pk=None):
        run = self.get_object()
        reason = request.data.get('reason', '')
        
        if run.status not in [BrainRun.Status.RUNNING, BrainRun.Status.PENDING]:
            return Response(
                {"detail": "Run cannot be marked for review in current status."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            run.mark_needs_review(reason)
            log_info_event(run, "orchestrator", "Run marked for review", {"reason": reason})

        return Response(self.get_serializer(run).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get organization-level run statistics"""
        user = request.user
        organization = getattr(user, 'organization', None)
        if not organization:
            return Response({"detail": "No organization found"}, status=status.HTTP_400_BAD_REQUEST)

        stats = BrainRun.objects.filter(organization=organization).aggregate(
            total_runs=Count('id'),
            pending_runs=Count('id', filter=Q(status=BrainRun.Status.PENDING)),
            running_runs=Count('id', filter=Q(status=BrainRun.Status.RUNNING)),
            completed_runs=Count('id', filter=Q(status=BrainRun.Status.COMPLETED)),
            failed_runs=Count('id', filter=Q(status=BrainRun.Status.FAILED)),
            needs_review_runs=Count('id', filter=Q(status=BrainRun.Status.NEEDS_REVIEW)),
        )

        return Response(stats, status=status.HTTP_200_OK)


class BrainRunEventViewSet(OrgScopedMixin,
                           mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BrainRunEventSerializer
    queryset = BrainRunEvent.objects.select_related("run", "run__organization")

    def get_queryset(self):
        qs = super().get_queryset()
        # Filter by run if provided
        run_id = self.request.query_params.get('run')
        if run_id:
            qs = qs.filter(run__id=run_id)
        return qs
