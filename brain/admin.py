from django.contrib import admin
from .models import BrainRun, BrainRunEvent

@admin.register(BrainRun)
class BrainRunAdmin(admin.ModelAdmin):
    list_display = ("id", "organization", "created_by", "run_type", "status", "current_node", "created_at", "finished_at")
    list_filter = ("status", "run_type", "organization")
    search_fields = ("id", "current_node", "error_code", "error_message")
    readonly_fields = ("created_at", "updated_at", "started_at", "finished_at", "duration_seconds")
    fieldsets = (
        (None, {
            'fields': ('id', 'organization', 'created_by', 'run_type')
        }),
        ('Status', {
            'fields': ('status', 'current_node', 'error_code', 'error_message')
        }),
        ('Timing', {
            'fields': ('started_at', 'finished_at', 'duration_seconds')
        }),
        ('Metadata', {
            'fields': ('meta',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(BrainRunEvent)
class BrainRunEventAdmin(admin.ModelAdmin):
    list_display = ("id", "run", "seq", "node_name", "event_type", "duration_ms", "created_at")
    list_filter = ("event_type", "node_name")
    search_fields = ("run__id", "node_name")
    readonly_fields = ("created_at",)
    raw_id_fields = ("run",)
