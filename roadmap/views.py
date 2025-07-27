from django.shortcuts import render
from .models import (
    BusinessInitiative,
    CustomerObjective,
    ProductKPI,
    ProductInitiativeKPI,
    ProductInitiative,
)
from rest_framework.viewsets import ModelViewSet
from .serializers import (
    ProductKPISerializer,
    ProductInitiativeKPISerializer,
    BusinessInitiativeSerializer,
    CustomerObjectiveSerializer,
    ProductInitiativeSerializer,
)

# Create your views here.

class ProductKPIViewSet(ModelViewSet):
    queryset = ProductKPI.objects.all()
    serializer_class = ProductKPISerializer

class ProductInitiativeKPIViewSet(ModelViewSet):
    queryset = ProductInitiativeKPI.objects.all()
    serializer_class = ProductInitiativeKPISerializer

class BusinessInitiativeViewSet(ModelViewSet):
    queryset = BusinessInitiative.objects.all()
    serializer_class = BusinessInitiativeSerializer

class CustomerObjectiveViewSet(ModelViewSet):
    queryset = CustomerObjective.objects.all()
    serializer_class = CustomerObjectiveSerializer

class ProductInitiativeViewSet(ModelViewSet):
    """
    Full CRUD operations for ProductInitiative.
    """
    serializer_class = ProductInitiativeSerializer
    
    queryset = ProductInitiative.objects.all().prefetch_related(
        'product_kpis',
        'business_initiatives',
        'customer_objectives',
        'owner',
        'organization',
        'product_initiative_kpis',
        'business_initiatives__business_objective',
    )