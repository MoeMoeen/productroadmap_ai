from django.contrib import admin

# Register your models here.

from .models import Organization, User, Product

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("-created_at",)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "organization", "is_staff", "is_active")
    search_fields = ("username", "email")
    list_filter = ("is_staff", "is_active", "organization")
    ordering = ("-date_joined",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('organization')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "description")
    search_fields = ("name",)