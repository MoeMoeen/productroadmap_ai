# accounts/urls.py

"""
accounts/urls.py

URL routing for the Accounts app API endpoints.
- /api/accounts/organizations/
- /api/accounts/users/
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import OrganizationViewSet, UserViewSet

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
