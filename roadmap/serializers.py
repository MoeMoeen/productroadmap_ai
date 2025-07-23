from rest_framework import serializers
from .models import ProductKPI, ProductInitiativeKPI, ProductInitiative
from .models import BusinessInitiative, CustomerObjective

class ProductKPISerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductKPI
        fields = [
            'id',
            'name',
            'description',
            'target_value',
            'current_value',
            'unit',
            'organization',
            'created_by',
        ]
        read_only_fields = ['id', 'created_by', 'organization']

class ProductInitiativeKPISerializer(serializers.ModelSerializer):
    product_kpi = ProductKPISerializer(read_only=True)

    class Meta:
        model = ProductInitiativeKPI
        fields = [
            'id',
            'product_initiative',
            'product_kpi',
            'target_value',
            'current_value',
            'weight',
            'note',
            'unit',
            'created_by',
        ]
        read_only_fields = ['id', 'created_by']


class BusinessInitiativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessInitiative
        fields = [
            'id',
            'title',
            'description',
            'start_date',
            'end_date',
            'status',
            'organization',
            'owner',
        ]
        read_only_fields = ['id', 'owner', 'organization']

class CustomerObjectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerObjective
        fields = [
            'id',
            'name',
            'description',
            'start_date',
            'end_date',
            'status',
            'organization',
            'created_by',
            'metric_name',
            'current_value',
            'target_value',
            'unit',
        ]
        read_only_fields = ['id', 'created_by', 'organization']

class ProductInitiativeSerializer(serializers.ModelSerializer):
    product_kpis = ProductInitiativeKPISerializer(many=True, read_only=True, source='product_initiative_kpi_set')
    business_initiatives = BusinessInitiativeSerializer(read_only=True, many=True, source='business_initiative')

    customer_objectives = CustomerObjectiveSerializer(read_only=True, many=True, source='customer_objective')

    class Meta:
        model = ProductInitiative
        fields = [
            'id',
            'title',
            'description',
            'start_date',
            'end_date',
            'status',
            'organization',
            'owner',
            'product_kpis',
            'business_initiatives',
            'customer_objectives',
        ]
        read_only_fields = ['id', 'owner', 'organization']




#------- Example Output -------
# When GET /product_initiatives/ is called, a record might look like this:

# {
#   "id": 1,
#   "title": "Improve onboarding flow",
#   "description": "Redesign signup",
#   "status": "planned",
#   "start_date": "2025-08-01",
#   "end_date": "2025-10-01",
#   "kpis": [
#     {
#       "product_kpi": {
#         "id": 4,
#         "name": "Signup Conversion Rate",
#         "description": "",
#         "target_value": 0.5,
#         "current_value": 0.3,
#         "unit": "%"
#       },
#       "target_value": 0.5,
#       "current_value": 0.3,
#       "weight": 50.0,
#       "note": ""
#     }
#   ]
# }