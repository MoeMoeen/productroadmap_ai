from rest_framework.routers import DefaultRouter
from .views import ProductInitiativeViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'product-initiatives', ProductInitiativeViewSet, basename='product-initiative')

urlpatterns = [
    path('', include(router.urls)),
]