from django.contrib import admin

# Register your models here.

from .models import BusinessObjectiveInitiative
from .models import Roadmap
from .models import CustomerSegment
from .models import CustomerObjective
from .models import ProductInitiative
from .models import CustomerObjectiveInitiative

@admin.register(BusinessObjectiveInitiative)
class BusinessObjectiveInitiativeAdmin(admin.ModelAdmin):
    list_display = ("contribution_type", "business_objective")
    # search_fields = ("contribution_type__name")
    # list_filter = ("contribution_type")


@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "created_by", "start_date", "end_date", "is_active", "created_at")
    list_filter = ("organization", "is_active")
    search_fields = ("name", "description")

@admin.register(CustomerSegment)
class CustomerSegmentAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "created_at")
    search_fields = ("name",)
    list_filter = ("organization",)

@admin.register(CustomerObjective)
class CustomerObjectiveAdmin(admin.ModelAdmin):
    list_display = ("name", "metric_name", "current_value", "target_value", "unit", "created_at")
    search_fields = ("name", "metric_name")
    list_filter = ("organization",)

    # ✅ Add this line to show a widget for M2M relationships
    filter_horizontal = ("customer_segments",)

    # filter_horizontal = ("product_initiatives",)


class CustomerObjectiveInline(admin.TabularInline):
    model = CustomerObjectiveInitiative
    extra = 1
    verbose_name = "Customer Objective Initiative"
    verbose_name_plural = "Customer Objective Initiatives"

@admin.register(ProductInitiative)
class ProductInitiativeAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "created_at")
    search_fields = ("title",)
    list_filter = ("title",)

    # ✅ Correct way to manage related through-model
    inlines = [CustomerObjectiveInline]