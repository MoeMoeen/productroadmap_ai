from rest_framework.routers import DefaultRouter
from .views import ProductInitiativeViewSet, ProductInitiativeKPIViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'product-initiatives', ProductInitiativeViewSet, basename='product-initiative')
router.register(r'product-initiative-kpis', ProductInitiativeKPIViewSet, basename='product-initiative-kpi')

urlpatterns = [
    path('', include(router.urls)),
]