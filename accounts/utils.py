# accounts/utils.py
"""
Utility functions for Accounts app.
"""

from typing import Optional
from django.contrib.auth import get_user_model
from accounts.models import Organization

User = get_user_model()


def get_user_org(user) -> Optional[Organization]:
    """
    Return the organization for a given user.

    - Superusers may not belong to an org; returns None in that case.
    - Non-authenticated users also return None.
    """
    if not user or not getattr(user, "is_authenticated", False):
        return None
    return getattr(user, "organization", None)
