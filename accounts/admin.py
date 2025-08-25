from django.contrib import admin

# Register your models here.

from .models import Organization, User, Product

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "vision", "headcount", "created_at", "updated_at")
    search_fields = ("name", "vision")
    list_filter = ("created_at", "updated_at")
    ordering = ("-created_at",)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "first_name", "last_name", "is_active", "is_staff", "is_superuser", "organization")
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("is_active", "is_staff", "is_superuser", "organization")
    ordering = ("-date_joined",)
    autocomplete_fields = ("organization",)
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('organization')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "description")
    search_fields = ("name",)