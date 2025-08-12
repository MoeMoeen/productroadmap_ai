from rest_framework.routers import DefaultRouter
from .views import (
    ProductInitiativeViewSet, 
    ProductInitiativeKPIViewSet,
    ProductKPIViewSet,
    BusinessInitiativeViewSet,
    CustomerObjectiveViewSet,
    BusinessObjectiveViewSet,
    BusinessKPIViewSet,
    CustomerSegmentViewSet,
    RoadmapViewSet,
    RoadmapEntryViewSet,
)
from django.urls import path, include

router = DefaultRouter()
router.register(r'product-initiatives', ProductInitiativeViewSet, basename='product-initiative')
router.register(r'product-initiative-kpis', ProductInitiativeKPIViewSet, basename='product-initiative-kpi')
router.register(r'product-kpis', ProductKPIViewSet, basename='product-kpi')
router.register(r'business-initiatives', BusinessInitiativeViewSet, basename='business-initiative')
router.register(r'customer-objectives', CustomerObjectiveViewSet, basename='customer-objective')
router.register(r'business-objectives', BusinessObjectiveViewSet, basename='business-objective')
router.register(r'business-kpis', BusinessKPIViewSet, basename='business-kpi')
router.register(r'customer-segments', CustomerSegmentViewSet, basename='customer-segment')
router.register(r'roadmaps', RoadmapViewSet, basename='roadmap')
router.register(r'roadmap-entries', RoadmapEntryViewSet, basename='roadmap-entry')

urlpatterns = [
    path('', include(router.urls)),
]