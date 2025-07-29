Product Initiative List
Full CRUD operations for ProductInitiative.

GET /api/roadmap/product-initiatives/
HTTP 200 OK
Allow: GET, POST, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept


BEFORE

[
    {
        "id": 5,
        "title": "[SWAGGER] Develop Group Shopping Functionality",
        "description": "[SWAGGER] Develop Group Shopping Functionality\n[[SWAGGER] Develop Group Shopping Functionality",
        "start_date": "2025-11-27",
        "end_date": "2025-12-27",
        "status": "planned",
        "organization": 1,
        "owner": 1,
        "product_kpis": [],
        "business_initiatives": [],
        "customer_objectives": [],
        "business_objectives": []
    },
    {
        "id": 4,
        "title": "[SWAGGER] Launch Livestreaming shopping",
        "description": "[SWAGGER] Launch Livestreaming shopping\n[SWAGGER] Launch Livestreaming shopping",
        "start_date": "2025-08-27",
        "end_date": "2025-10-27",
        "status": "planned",
        "organization": null,
        "owner": 1,
        "product_kpis": [],
        "business_initiatives": [],
        "customer_objectives": [],
        "business_objectives": []
    },
    {
        "id": 3,
        "title": "[SWAGGER] Implement the A/B testing engine.",
        "description": "[SWAGGER] Implement the A/B testing engine.\n[SWAGGER] Implement the A/B testing engine.",
        "start_date": "2025-07-27",
        "end_date": "2025-09-27",
        "status": "planned",
        "organization": null,
        "owner": null,
        "product_kpis": [],
        "business_initiatives": [],
        "customer_objectives": [],
        "business_objectives": []
    },
    {
        "id": 2,
        "title": "Introduce local (UAE) payment methods to the app",
        "description": "Introduce local (UAE) payment methods to the app\r\nIntroduce local (UAE) payment methods to the app",
        "start_date": "2025-07-21",
        "end_date": "2025-08-25",
        "status": "in_progress",
        "organization": 1,
        "owner": 2,
        "product_kpis": [
            {
                "id": 3,
                "product_kpi": {
                    "id": 3,
                    "name": "New Payment method (X) Relative Adoption rate",
                    "description": "New Payment method (X) Relative Adoption rate\r\nNew Payment method (X) Relative Adoption rate",
                    "target_value": 30.0,
                    "current_value": 0.0,
                    "unit": "%",
                    "organization": 1,
                    "created_by": 2
                },
                "target_value": 30.0,
                "weight": "40.00",
                "note": "This will measure how much users will use this new advanced payment method compared to other options."
            }
        ],
        "business_initiatives": [
            {
                "id": 2,
                "title": "Market Expansion to UAE",
                "description": "Market Expansion to UAE\r\nMarket Expansion to UAE",
                "start_date": "2025-09-11",
                "end_date": "2025-10-31",
                "status": "planned",
                "organization": 1,
                "owner": 2
            }
        ],
        "customer_objectives": [
            {
                "id": 1,
                "name": "Complete the purchase as fast as possible",
                "metric_name": "Purchase Completion Time",
                "current_value": 10.0,
                "target_value": 2.0,
                "unit": "minute"
            }
        ],
        "business_objectives": []
    },
    {
        "id": 1,
        "title": "Redesign of UX for checkout",
        "description": "Redesign of UX for checkout\r\nRedesign of UX for checkout",
        "start_date": "2025-07-30",
        "end_date": "2025-08-14",
        "status": "planned",
        "organization": 1,
        "owner": 2,
        "product_kpis": [
            {
                "id": 1,
                "product_kpi": {
                    "id": 1,
                    "name": "Checkout Page Load Time",
                    "description": "Checkout Page Load Time\r\nCheckout Page Load Time",
                    "target_value": 1.0,
                    "current_value": 3.0,
                    "unit": "seconds",
                    "organization": 1,
                    "created_by": 2
                },
                "target_value": 1.0,
                "weight": "30.00",
                "note": "The redesign must reduce this product kpi from 2 seconds to 1 second"
            },
            {
                "id": 2,
                "product_kpi": {
                    "id": 2,
                    "name": "Checkout Page Drop Rate",
                    "description": "Checkout Page Drop Rate\r\nCheckout Page Drop Rate",
                    "target_value": 10.0,
                    "current_value": 20.0,
                    "unit": "%",
                    "organization": 1,
                    "created_by": 3
                },
                "target_value": 10.0,
                "weight": "10.00",
                "note": "Drop rate is a good measure of how good the UX redesign is."
            }
        ],
        "business_initiatives": [
            {
                "id": 1,
                "title": "Marketplace app Growth Business Initiative",
                "description": "Marketplace app Growth Business Initiative\r\nMarketplace app Growth Business Initiative",
                "start_date": "2025-09-02",
                "end_date": "2025-10-25",
                "status": "active",
                "organization": 1,
                "owner": 2
            }
        ],
        "customer_objectives": [
            {
                "id": 1,
                "name": "Complete the purchase as fast as possible",
                "metric_name": "Purchase Completion Time",
                "current_value": 10.0,
                "target_value": 2.0,
                "unit": "minute"
            }
        ],
        "business_objectives": [
            {
                "id": 1,
                "title": "Increase revenue by 20%",
                "description": "Increase revenue by 20%\r\nIncrease revenue by 20%",
                "deadline": "2025-11-30",
                "priority": 1,
                "organization": 1,
                "created_by": 2
            }
        ]
    }
]

AFTER

class ProductInitiativeKPISerializer(serializers.ModelSerializer):
    product_kpi = ProductKPISerializer(read_only=True) # just for experimination purposes I decided to use read_only=True and not PrimaryKeyRelatedField
    product_initiative = serializers.PrimaryKeyRelatedField(queryset=ProductInitiative.objects.all()) # Just for experimentation purposes I decided to use PrimaryKeyRelatedField


Product Initiative List
Full CRUD operations for ProductInitiative.

GET /api/roadmap/product-initiatives/
HTTP 200 OK
Allow: GET, POST, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

[
    {
        "id": 5,
        "title": "[SWAGGER] Develop Group Shopping Functionality",
        "description": "[SWAGGER] Develop Group Shopping Functionality\n[[SWAGGER] Develop Group Shopping Functionality",
        "start_date": "2025-11-27",
        "end_date": "2025-12-27",
        "status": "planned",
        "organization": 1,
        "owner": 1,
        "product_kpis": [],
        "business_initiatives": [],
        "customer_objectives": [],
        "business_objectives": []
    },
    {
        "id": 4,
        "title": "[SWAGGER] Launch Livestreaming shopping",
        "description": "[SWAGGER] Launch Livestreaming shopping\n[SWAGGER] Launch Livestreaming shopping",
        "start_date": "2025-08-27",
        "end_date": "2025-10-27",
        "status": "planned",
        "organization": null,
        "owner": 1,
        "product_kpis": [],
        "business_initiatives": [],
        "customer_objectives": [],
        "business_objectives": []
    },
    {
        "id": 3,
        "title": "[SWAGGER] Implement the A/B testing engine.",
        "description": "[SWAGGER] Implement the A/B testing engine.\n[SWAGGER] Implement the A/B testing engine.",
        "start_date": "2025-07-27",
        "end_date": "2025-09-27",
        "status": "planned",
        "organization": null,
        "owner": null,
        "product_kpis": [],
        "business_initiatives": [],
        "customer_objectives": [],
        "business_objectives": []
    },
    {
        "id": 2,
        "title": "Introduce local (UAE) payment methods to the app",
        "description": "Introduce local (UAE) payment methods to the app\r\nIntroduce local (UAE) payment methods to the app",
        "start_date": "2025-07-21",
        "end_date": "2025-08-25",
        "status": "in_progress",
        "organization": 1,
        "owner": 2,
        "product_kpis": [
            {
                "id": 3,
                "product_kpi": {
                    "id": 3,
                    "name": "New Payment method (X) Relative Adoption rate",
                    "description": "New Payment method (X) Relative Adoption rate\r\nNew Payment method (X) Relative Adoption rate",
                    "target_value": 30.0,
                    "current_value": 0.0,
                    "unit": "%",
                    "organization": 1,
                    "created_by": 2
                },
                "product_initiative": 2,
                "target_value": 30.0,
                "weight": "40.00",
                "note": "This will measure how much users will use this new advanced payment method compared to other options."
            }
        ],
        "business_initiatives": [
            {
                "id": 2,
                "title": "Market Expansion to UAE",
                "description": "Market Expansion to UAE\r\nMarket Expansion to UAE",
                "start_date": "2025-09-11",
                "end_date": "2025-10-31",
                "status": "planned",
                "organization": 1,
                "owner": 2
            }
        ],
        "customer_objectives": [
            {
                "id": 1,
                "name": "Complete the purchase as fast as possible",
                "metric_name": "Purchase Completion Time",
                "current_value": 10.0,
                "target_value": 2.0,
                "unit": "minute"
            }
        ],
        "business_objectives": []
    },
    {
        "id": 1,
        "title": "Redesign of UX for checkout",
        "description": "Redesign of UX for checkout\r\nRedesign of UX for checkout",
        "start_date": "2025-07-30",
        "end_date": "2025-08-14",
        "status": "planned",
        "organization": 1,
        "owner": 2,
        "product_kpis": [
            {
                "id": 1,
                "product_kpi": {
                    "id": 1,
                    "name": "Checkout Page Load Time",
                    "description": "Checkout Page Load Time\r\nCheckout Page Load Time",
                    "target_value": 1.0,
                    "current_value": 3.0,
                    "unit": "seconds",
                    "organization": 1,
                    "created_by": 2
                },
                "product_initiative": 1,
                "target_value": 1.0,
                "weight": "30.00",
                "note": "The redesign must reduce this product kpi from 2 seconds to 1 second"
            },
            {
                "id": 2,
                "product_kpi": {
                    "id": 2,
                    "name": "Checkout Page Drop Rate",
                    "description": "Checkout Page Drop Rate\r\nCheckout Page Drop Rate",
                    "target_value": 10.0,
                    "current_value": 20.0,
                    "unit": "%",
                    "organization": 1,
                    "created_by": 3
                },
                "product_initiative": 1,
                "target_value": 10.0,
                "weight": "10.00",
                "note": "Drop rate is a good measure of how good the UX redesign is."
            }
        ],
        "business_initiatives": [
            {
                "id": 1,
                "title": "Marketplace app Growth Business Initiative",
                "description": "Marketplace app Growth Business Initiative\r\nMarketplace app Growth Business Initiative",
                "start_date": "2025-09-02",
                "end_date": "2025-10-25",
                "status": "active",
                "organization": 1,
                "owner": 2
            }
        ],
        "customer_objectives": [
            {
                "id": 1,
                "name": "Complete the purchase as fast as possible",
                "metric_name": "Purchase Completion Time",
                "current_value": 10.0,
                "target_value": 2.0,
                "unit": "minute"
            }
        ],
        "business_objectives": [
            {
                "id": 1,
                "title": "Increase revenue by 20%",
                "description": "Increase revenue by 20%\r\nIncrease revenue by 20%",
                "deadline": "2025-11-30",
                "priority": 1,
                "organization": 1,
                "created_by": 2
            }
        ]
    }
]