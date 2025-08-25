# accounts/serializers.py

"""
accounts/serializers.py

DRF serializers for the Accounts app.
- OrganizationSerializer: standard read/write serializer for Organization
- UserSerializer: safe org-scoped serializer for the custom User model

Design notes
------------
1) Multi-tenant system: every User belongs to exactly one Organization.
2) Non-superusers are restricted to creating/updating users only within their own organization.
3) Expose `organization` as a read-only nested object and accept `organization_id` as a write-only field for clarity.
4) Fields are explicit (not "__all__") to avoid overexposure.
"""
from __future__ import annotations
from typing import Any, Dict, Optional
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied
from rest_framework import serializers
from accounts.models import Organization
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class RequestUserMixin:
    """Convenience mixin to access `request.user` from serializer context safely."""
    @property
    def request(self) -> Optional[Any]:
        context = getattr(self, "context", None)
        if context is not None:
            return context.get("request")
        return None
    @property
    def request_user(self) -> Optional[Any]:
        req = self.request
        return getattr(req, "user", None)
    def user_is_superuser(self) -> bool:
        u = self.request_user
        return bool(u and getattr(u, "is_superuser", False))
    def user_org(self) -> Optional[Organization]:
        u = self.request_user
        return getattr(u, "organization", None)

class OrganizationSerializer(RequestUserMixin, serializers.ModelSerializer):
    """Serializer for Organization objects."""
    class Meta:
        model = Organization
        fields = [
            "id", "name", "vision", "departments", "headcount", "created", "modified"
        ]
        read_only_fields = ["id", "created", "modified"]
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Restrict non-superusers from creating organizations."""
        user = self.request_user
        if user and not self.user_is_superuser():
            if self.instance is None:
                raise PermissionDenied("You are not allowed to create organizations.")
            if getattr(user, "organization_id", None) != self.instance.id:
                raise PermissionDenied("You can only modify your own organization.")
        return attrs

class UserSerializer(RequestUserMixin, serializers.ModelSerializer):
    """Serializer for User objects, org-scoped and safe for multi-tenant use."""
    organization = OrganizationSerializer(read_only=True)
    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(), source="organization", write_only=True, required=False
    )
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name", "is_active",
            "organization", "organization_id", "password", "is_staff", "is_superuser"
        ]
        read_only_fields = ["id", "is_staff", "is_superuser"]

    def to_representation(self, instance) -> Dict[str, Any]:
        """Hide organization_id and password on read."""
        rep = super().to_representation(instance)
        rep.pop("organization_id", None)
        rep.pop("password", None)
        return rep

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce org-scoped writes for non-superusers.
        On create: if `organization` not provided, default to request.user.organization (if present).
        On update: prevent moving users across orgs unless superuser.
        """
        req_user = self.request_user
        if not req_user:
            return attrs
        is_super = self.user_is_superuser()
        req_org = self.user_org()
        target_org = attrs.get("organization")

        if target_org is None and self.instance is None and req_org is not None:
            attrs["organization"] = req_org
            target_org = req_org

        if not is_super:
            if self.instance is not None:
                existing_org = getattr(self.instance, "organization", None)
                if target_org is not None and existing_org and target_org != existing_org:
                    raise PermissionDenied("You cannot move a user to another organization.")
            if self.instance is None and target_org is not None and req_org is not None and target_org != req_org:
                raise PermissionDenied("You can only create users in your own organization.")

        if not is_super and any(k in attrs for k in ("is_active", "is_staff", "is_superuser")):
            raise PermissionDenied("You are not allowed to modify account status/roles.")

        # Validate password: Here, we ensure the password meets the requirements.
        pwd = attrs.get("password")
        if self.instance is None and not pwd:
            raise serializers.ValidationError({"password": "Password is required when creating a new user."})
        
        if pwd:
            candidate = self.instance or User(**{k: attrs.get(k) for k in ['username', 'email'] if k in attrs})
            validate_password(pwd, candidate)

        return attrs

    def create(self, validated_data: Dict[str, Any]):
        """Create a new user, handling password securely."""
        password = validated_data.pop("password", None)
        user = User.objects.create_user(password, **validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        """Update user fields, handling password securely."""
        password = validated_data.pop("password", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            validate_password(password, instance)
            instance.set_password(password)
        instance.save()
        return instance
