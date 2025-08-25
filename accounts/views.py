# accounts/views.py
"""
ViewSets for the Accounts app.
- OrganizationViewSet: CRUD for organizations (superuser-only for create/update/delete)
- UserViewSet: CRUD for users, org-scoped for non-superusers

Notes
-----
• Uses IsAuthenticated + SuperuserOnly / IsOrgMember for fine-grained control.
• Uses org-scoped querysets for non-superusers.
• Adds select_related(), search & ordering to make admin life easier.
• Keeps perform_* checks as a hard backstop, though permissions should cover 99%.
"""
from __future__ import annotations
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from rest_framework import viewsets, filters
from rest_framework.exceptions import PermissionDenied

from accounts.models import Organization
from accounts.serializers import OrganizationSerializer, UserSerializer
from accounts.permissions import IsOrgMember, SuperuserOnly
from accounts.utils import get_user_org

# from accounts.utils import get_user_org   # Step 5 (org scoping utility)

User = get_user_model()


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    Only superusers may create/update/delete organizations.
    Non-superusers are restricted to listing/retrieving their own org.
    """
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()  # base queryset for docs/schema
    permission_classes = [SuperuserOnly, IsOrgMember]  # Both permissions checked; logic handled in permission classes
    http_method_names = ["get", "post", "patch", "put", "delete"]

    def get_queryset(self) -> QuerySet[Organization]:
        user = self.request.user
        if user.is_superuser:
            return Organization.objects.all()
        org = get_user_org(user)
        if org:
            return Organization.objects.filter(id=org.pk)
        return Organization.objects.none()

    # Redundant once SuperuserOnly is in play, but left for safety
    def perform_create(self, serializer: OrganizationSerializer) -> None:
        if not self.request.user.is_superuser:
            raise PermissionDenied("Only superusers can create organizations.")
        serializer.save()

    def perform_update(self, serializer: OrganizationSerializer) -> None:
        if not self.request.user.is_superuser:
            raise PermissionDenied("Only superusers can update organizations.")
        serializer.save()

    def perform_destroy(self, instance: Organization) -> None:
        if not self.request.user.is_superuser:
            raise PermissionDenied("Only superusers can delete organizations.")
        instance.delete()


class UserViewSet(viewsets.ModelViewSet):
    """
    Users are org-scoped for non-superusers.
    Superusers can manage all users across orgs.
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()  # base queryset for docs/schema
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated, IsOrgMember]
    http_method_names = ["get", "post", "patch", "put", "delete"]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["id", "date_joined", "last_login", "username", "email"]
    ordering = ["id"]

    def get_queryset(self) -> QuerySet:
        user = self.request.user
        base = User.objects.all().select_related("organization")
        if user.is_superuser:
            return base
        org = get_user_org(user)
        if org:
            return base.filter(organization_id=org.pk)
        return base.none()

    def perform_create(self, serializer: UserSerializer) -> None:
        serializer.save()

    def perform_update(self, serializer: UserSerializer) -> None:
        serializer.save()

    def perform_destroy(self, instance) -> None:
        instance.delete()
