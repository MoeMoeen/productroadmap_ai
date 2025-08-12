# brain/serializers.py

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import BrainRun, BrainRunEvent

class BrainRunSerializer(serializers.ModelSerializer):
    duration_seconds = serializers.ReadOnlyField()
    
    class Meta:
        model = BrainRun
        read_only_fields = (
            "id", "status", "started_at", "finished_at", "current_node",
            "error_code", "error_message", "created_at", "updated_at", "duration_seconds"
        )
        fields = (
            "id", "organization", "created_by", "status", "run_type", "started_at", "finished_at",
            "current_node", "error_code", "error_message", "meta", "created_at", "updated_at", "duration_seconds"
        )

    def create(self, validated_data):
        # Force org/user from request context for safety
        request = self.context["request"]
        validated_data["organization"] = request.user.organization
        validated_data["created_by"] = request.user
        return super().create(validated_data)


class BrainRunEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrainRunEvent
        read_only_fields = ("id", "run", "seq", "node_name", "event_type", "payload", "duration_ms", "created_at")
        fields = ("id", "run", "seq", "node_name", "event_type", "payload", "duration_ms", "created_at")


class BrainRunSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for run listings"""
    event_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BrainRun
        fields = (
            "id", "status", "run_type", "current_node", "started_at", "finished_at", 
            "duration_seconds", "created_at", "event_count"
        )
    
    @extend_schema_field(serializers.IntegerField)
    def get_event_count(self, obj) -> int:
        return obj.events.count()
