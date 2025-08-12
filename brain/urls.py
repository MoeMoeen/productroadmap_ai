from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BrainRunViewSet, BrainRunEventViewSet
from .api.ai_job_endpoints import ai_job_urlpatterns

router = DefaultRouter()
router.register(r"runs", BrainRunViewSet, basename="brain-run")
router.register(r"events", BrainRunEventViewSet, basename="brain-run-event")

urlpatterns = [
    # DRF ViewSets
    path('', include(router.urls)),
    
    # AI Job API endpoints
    path('', include(ai_job_urlpatterns)),
]
