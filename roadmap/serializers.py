from rest_framework import serializers
from .models import ProductKPI, ProductInitiativeKPI, ProductInitiative
from .models import BusinessInitiative, CustomerObjective, BusinessInitiativeProductInitiative, CustomerObjectiveProductInitiative
from .models import CustomerSegment
from .models import BusinessObjective


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
    product_kpi = ProductKPISerializer(read_only=True) # just for experimination purposes I decided to use read_only=True and not PrimaryKeyRelatedField
    product_kpi_id = serializers.PrimaryKeyRelatedField(
        source='product_kpi',
        queryset=ProductKPI.objects.all(),
        write_only=True
    ) # this is for post/patch requests to set the product_kpi
    product_initiative = serializers.PrimaryKeyRelatedField(queryset=ProductInitiative.objects.all()) # Just for experimentation purposes I decided to use PrimaryKeyRelatedField

    class Meta:
        model = ProductInitiativeKPI
        fields = [
            'id',
            'product_kpi',
            'product_kpi_id',
            'product_initiative',
            'target_value',
            # 'current_value',
            'weight',
            'note',
            'organization',
            'owner',
        ]
        read_only_fields = ['id', 'owner', 'organization']

    def create(self, validated_data):
        """
        Create a new ProductInitiativeKPI instance. Overrides the create method to set the owner and organization.
        """
        user = self.context['request'].user
        organization = getattr(user, 'organization', None)
        validated_data['owner'] = user
        validated_data['organization'] = organization
        return super().create(validated_data)


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


class BusinessObjectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessObjective
        fields = [
            'id',
            'title',
            'description',
            'deadline',
            'priority',
            'organization',
            'created_by',
        ]
        read_only_fields = ['id', 'created_by', 'organization']

class ProductInitiativeSerializer(serializers.ModelSerializer):
    product_kpis = ProductInitiativeKPISerializer(many=True, read_only=True, source='product_initiative_kpis')
    business_initiatives = BusinessInitiativeSerializer(read_only=True, many=True)
    customer_objectives = CustomerObjectiveSummarySerializer(read_only=True, many=True)
    business_objectives = serializers.SerializerMethodField()

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
            'business_objectives',
        ]
        read_only_fields = ['id', 'owner', 'organization']

    def create(self, validated_data):
        user = self.context['request'].user
        organization = getattr(user, 'organization', None)
        validated_data['owner'] = user
        validated_data['organization'] = organization
        return super().create(validated_data)

    def get_business_objectives(self, obj):
        # business_objectives = obj.business_initiatives.values_list('business_objective', flat=True)
        business_objectives = set()
        for initiative in obj.business_initiatives.all():
            for objective in initiative.business_objectives.all():
                business_objectives.add(objective)
        return BusinessObjectiveSerializer(business_objectives, many=True, read_only=True).data if business_objectives else []




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