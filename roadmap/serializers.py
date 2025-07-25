from rest_framework import serializers
from .models import ProductKPI, ProductInitiativeKPI, ProductInitiative
from .models import BusinessInitiative, CustomerObjective, BusinessInitiativeProductInitiative, CustomerObjectiveProductInitiative
from .models import CustomerSegment


class CustomerObjectiveSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerObjective
        fields = ['id', 'name', 'metric_name', 'current_value', 'target_value', 'unit']
        read_only_fields = ['id']

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
            'product_kpi',
            'target_value',
            # 'current_value',
            'weight',
            'note',
        ]
        read_only_fields = ['id',]

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

class CustomerSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerSegment
        fields = [
            'id',
            'name',
            'description',
            'organization',
            'created_by',
            'size_count',
            'size_value',
            'strategic_importance',
        ]
        read_only_fields = ['id', 'created_by', 'organization']

class CustomerObjectiveSerializer(serializers.ModelSerializer):
    customer_segments = CustomerSegmentSerializer(read_only=False, many=True)

    class Meta:
        model = CustomerObjective
        fields = [
            'id',
            'name',
            'description',
            'organization',
            'created_by',
            'metric_name',
            'current_value',
            'target_value',
            'unit',
            'customer_segments',
        ]
        read_only_fields = ['id', 'created_by', 'organization']


class BusinessInitiativeProductInitiativeSerializer(serializers.ModelSerializer):
    business_initiative = BusinessInitiativeSerializer(read_only=True, many=True)
    # product_initiative = serializers.SerializerMethodField()

    class Meta:
        model = BusinessInitiativeProductInitiative
        fields = [
            'id',
            'business_initiative',
            # 'product_initiative',
            'note',
            'contribution_weight',
        ]
        read_only_fields = ['id',]

    # def get_product_initiative(self, obj):
    #     from .serializers import ProductInitiativeSerializer
    #     return ProductInitiativeSerializer(obj.product_initiative, read_only=True).data if obj.product_initiative else None

class CustomerObjectiveProductInitiativeSerializer(serializers.ModelSerializer):
    customer_objective = CustomerObjectiveSerializer(read_only=True)
    product_initiative = serializers.SerializerMethodField()

    class Meta:
        model = CustomerObjectiveProductInitiative
        fields = [
            'id',
            'customer_objective',
            'product_initiative',
            'note',
            'confidence',
            'contribution_type',

        ]
        read_only_fields = ['id',]

    def get_product_initiative(self, obj):
        from .serializers import ProductInitiativeSerializer
        return ProductInitiativeSerializer(obj.product_initiative, read_only=True).data if obj.product_initiative else None

class ProductInitiativeSerializer(serializers.ModelSerializer):
    product_kpis = ProductInitiativeKPISerializer(many=True, read_only=True, source='product_initiative_kpis')
    business_initiatives = BusinessInitiativeSerializer(read_only=True, many=True)
    customer_objectives = CustomerObjectiveSummarySerializer(read_only=True, many=True)

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