from django.contrib import admin

# Register your models here.

from .models import BusinessObjectiveInitiative
from .models import Roadmap
from .models import CustomerSegment
from .models import CustomerObjective
from .models import ProductInitiative
from .models import CustomerObjectiveProductInitiative
from .models import RoadmapEntry
from .models import BusinessInitiative
from .models import BusinessKPI
from .models import BusinessObjective
from .models import BusinessInitiativeProductInitiative

@admin.register(BusinessObjectiveInitiative)
class BusinessObjectiveInitiativeAdmin(admin.ModelAdmin):
    list_display = ("contribution_type", "business_objective")
    # search_fields = ("contribution_type__name")
    # list_filter = ("contribution_type")


class RoadmapEntryInline(admin.TabularInline):
    model = RoadmapEntry
    extra = 1
    verbose_name = "Roadmap Entry"
    verbose_name_plural = "Roadmap Entries"
    autocomplete_fields = ["product_initiative"]

@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "created_by", "start_date", "end_date", "is_active", "created_at")
    list_filter = ("organization", "is_active")
    search_fields = ("name", "description")
    inlines = [
        RoadmapEntryInline,
    ]

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
    model = CustomerObjectiveProductInitiative
    extra = 1
    verbose_name = "Customer Objective Initiative"
    verbose_name_plural = "Customer Objective Initiatives"

class businessInitiativeInline(admin.TabularInline):
    model = BusinessInitiative
    extra = 1
    verbose_name = "Business Initiative"
    verbose_name_plural = "Business Initiatives"


class BusinessinitiativeProductInitiativeInline(admin.TabularInline):
    model = BusinessInitiativeProductInitiative
    extra = 1
    verbose_name = "Business Initiative Product Initiative"
    verbose_name_plural = "Business Initiative Product Initiatives"

@admin.register(ProductInitiative)
class ProductInitiativeAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "created_at")
    search_fields = ("title",)
    list_filter = ("title",)

    # ✅ Correct way to manage related through-model
    inlines = [CustomerObjectiveInline, 
               BusinessinitiativeProductInitiativeInline]


@admin.register(RoadmapEntry)
class RoadmapEntryAdmin(admin.ModelAdmin):
    list_display = ("roadmap", "product_initiative")
    search_fields = ("roadmap__name", "product_initiative__title")
    #list_filter = ("roadmap")
    #inlines = [RoadmapEntryInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('roadmap', 'product_initiative')
    



@admin.register(BusinessInitiative)
class BusinessInitiativeAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "created_at")
    search_fields = ("title",)
    #list_filter = ("created_at",)



@admin.register(BusinessKPI)
class BusinessKPIAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")
    search_fields = ("name",)
    #list_filter = ("created_at",)