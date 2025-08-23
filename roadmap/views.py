from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import (
    BusinessInitiative,
    CustomerObjective,
    ProductKPI,
    ProductInitiativeKPI,
    ProductInitiative,
    BusinessObjective,
    BusinessKPI,
    CustomerSegment,
    Roadmap,
    RoadmapEntry,
)
from .serializers import (
    ProductKPISerializer,
    ProductInitiativeKPISerializer,
    BusinessInitiativeSerializer,
    CustomerObjectiveSerializer,
    ProductInitiativeSerializer,
    BusinessObjectiveSerializer,
    BusinessKPISerializer,
    CustomerSegmentSerializer,
    RoadmapSerializer,
    RoadmapEntrySerializer,
)
from .permissions import IsOrganizationMember


# Create your views here.

class ProductKPIViewSet(ModelViewSet):
    serializer_class = ProductKPISerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        user = self.request.user
        organization = getattr(user, 'organization', None)
        if not organization:
            return ProductKPI.objects.none()
        return ProductKPI.objects.filter(organization=organization)


class ProductInitiativeKPIViewSet(ModelViewSet):
    serializer_class = ProductInitiativeKPISerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        user = self.request.user
        organization = getattr(user, 'organization', None)
        if not organization:
            return ProductInitiativeKPI.objects.none()
        return ProductInitiativeKPI.objects.filter(organization=organization)


class BusinessInitiativeViewSet(ModelViewSet):
    serializer_class = BusinessInitiativeSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        user = self.request.user
        organization = getattr(user, 'organization', None)
        if not organization:
            return BusinessInitiative.objects.none()
        return BusinessInitiative.objects.filter(organization=organization)


class CustomerObjectiveViewSet(ModelViewSet):
    serializer_class = CustomerObjectiveSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        user = self.request.user
        organization = getattr(user, 'organization', None)
        if not organization:
            return CustomerObjective.objects.none()
        return CustomerObjective.objects.filter(organization=organization)


class ProductInitiativeViewSet(ModelViewSet):
    """
    Full CRUD operations for ProductInitiative.
    """
    serializer_class = ProductInitiativeSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_fields = ["product"]  # enables ?product=1 filter
    
    def get_queryset(self):
        user = self.request.user
        organization = getattr(user, 'organization', None)
        if not organization:
            return ProductInitiative.objects.none()
        return ProductInitiative.objects.filter(
            organization=organization
        ).prefetch_related(
            'product_kpis',
            'business_initiatives',
            'customer_objectives',
            'owner',
            'organization',
            'product_initiative_kpis',
            'business_initiatives__business_objectives',
        )


class BusinessObjectiveViewSet(ModelViewSet):
    """
    Full CRUD operations for BusinessObjective.
    """
    serializer_class = BusinessObjectiveSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        user = self.request.user
        organization = getattr(user, 'organization', None)
        if not organization:
            return BusinessObjective.objects.none()
        return BusinessObjective.objects.filter(
            organization=organization
        ).prefetch_related(
            'organization',
            'created_by',
            'business_kpis',
            'business_initiatives',
        )


class BusinessKPIViewSet(ModelViewSet):
    """
    Full CRUD operations for BusinessKPI.
    """
    serializer_class = BusinessKPISerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        user = self.request.user
        organization = getattr(user, 'organization', None)
        if not organization:
            return BusinessKPI.objects.none()
        return BusinessKPI.objects.filter(
            organization=organization
        ).prefetch_related(
            'organization',
            'created_by',
        )


class CustomerSegmentViewSet(ModelViewSet):
    """
    Full CRUD operations for CustomerSegment.
    """
    serializer_class = CustomerSegmentSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        user = self.request.user
        organization = getattr(user, 'organization', None)
        if not organization:
            return CustomerSegment.objects.none()
        return CustomerSegment.objects.filter(
            organization=organization
        ).prefetch_related(
            'organization',
            'created_by',
            'customer_objectives',
        )


class RoadmapViewSet(ModelViewSet):
    """
    Full CRUD operations for Roadmap.
    """
    serializer_class = RoadmapSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        user = self.request.user
        organization = getattr(user, 'organization', None)
        if not organization:
            return Roadmap.objects.none()
        return Roadmap.objects.filter(
            organization=organization
        ).prefetch_related(
            'organization',
            'created_by',
            'product_initiatives',
            'roadmap_entries',
            'roadmap_entries__product_initiative',
        )


class RoadmapEntryViewSet(ModelViewSet):
    """
    Full CRUD operations for RoadmapEntry.
    """
    serializer_class = RoadmapEntrySerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        user = self.request.user
        organization = getattr(user, 'organization', None)
        if not organization:
            return RoadmapEntry.objects.none()
        return RoadmapEntry.objects.filter(
            roadmap__organization=organization
        ).prefetch_related(
            'roadmap',
            'product_initiative',
            'roadmap__organization',
        )
