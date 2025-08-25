# accounts/permissions.py
"""
accounts/permissions.py

Custom permissions for org-based access control in the Accounts app.
- IsOrgMember: Only allow access to objects within the user's organization (unless superuser).
"""
from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model
from accounts.models import Organization
from accounts.utils import get_user_org
# from roadmap import permissions

User = get_user_model()

class IsOrgMember(BasePermission):
    """Allow access only to objects within the user's organization, or if superuser."""
    def has_permission(self, request, view) -> bool:
        """Check if the user has permission to access the view."""
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        # For list/create, restrict to org members
        return hasattr(user, "organization") and user.organization is not None

    def has_object_permission(self, request, view, obj) -> bool:
        """Check if the user has permission to access the object."""
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        # For Organization objects
        if isinstance(obj, Organization):
            return hasattr(user, "organization") and obj.pk == getattr(user.organization, "pk", None)
        # For User objects
        if hasattr(obj, "organization"):
            return hasattr(user, "organization") and obj.organization == getattr(user, "organization", None)
        # For other objects with an organization field
        org = getattr(obj, "organization", None)
        user_org = get_user_org(user)
        return user_org is not None and org == user_org


class SuperuserOnly(BasePermission):
    """Allow access only to superusers."""

    def has_permission(self, request, view) -> bool:
        return request.user and request.user.is_authenticated and request.user.is_superuser