from django.db import models
from common.models import TimeStampedModel, ContributionType
from accounts.models import Organization, User


# Create your models here.

class ProductKPI(TimeStampedModel):
    """Represents a KPI or metric used to evaluate product performance. It's 
    typically used in product initiatives to track progress against specific customer objectives 
    and/or business priority."""
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE,
        related_name='product_kpis',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    target_value = models.FloatField()
    current_value = models.FloatField()
    unit = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        related_name='created_product_kpis', 
        null=True
    )
    
    def __str__(self):
        return f"{self.name} - {self.current_value} {self.unit if self.unit else ''}"

    class Meta:
        ordering = ['-created_at']


class ProductInitiative(TimeStampedModel):
    """Represents a specific product-related initiative or project."""
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE,
        related_name='product_initiatives',
        null=True,
        blank=True
    )
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='owned_product_initiatives',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(blank=True, null=True)
    # status options must be dynamically defined and updated #LATER
    status = models.CharField(max_length=50, choices=[ 
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold')
    ], default='planned') 

    product_kpis = models.ManyToManyField(
        ProductKPI,
        through="ProductInitiativeKPI",
        related_name="product_initiatives"
    )
    
    customer_objectives = models.ManyToManyField(
        'CustomerObjective',
        through='CustomerObjectiveProductInitiative',
        related_name='linked_product_initiatives'
    )

    business_initiatives = models.ManyToManyField(
        'BusinessInitiative',
        through='BusinessInitiativeProductInitiative',
        related_name='linked_product_initiatives'
    )
    
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Product Initiatives'

    
class ProductInitiativeKPI(models.Model):
    """Through model to associate ProductInitiative and ProductKPI."""
    product_initiative = models.ForeignKey(ProductInitiative, on_delete=models.CASCADE, related_name='product_initiative_kpis')
    product_kpi = models.ForeignKey(ProductKPI, on_delete=models.CASCADE, related_name='product_initiative_kpis')
    target_value = models.FloatField()
    current_value = models.FloatField()
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Relative weight or contribution % of this initiative toward this KPI."
    )
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.product_initiative.title} - {self.product_kpi.name}"

    class Meta:
        unique_together = ('product_initiative', 'product_kpi')

    
class BusinessObjectiveInitiative(models.Model):
    """Captures how a Business Initiative contributes to a Business Objective."""
    business_objective = models.ForeignKey(
        'BusinessObjective', on_delete=models.CASCADE
    )
    business_initiative = models.ForeignKey(
        'BusinessInitiative', on_delete=models.CASCADE
    )
    priority = models.PositiveSmallIntegerField(
        default=1,
        help_text="Lower number = higher priority for this objective"
    )
    # type_of_contribution = models.CharField(
    #     max_length=50,
    #     choices=[
    #         ('direct', 'Direct'),
    #         ('indirect', 'Indirect'),
    #         ('enabling', 'Enabling'),
    #     ],
    #     default='direct'
    # )

    contribution_type = models.ForeignKey(
    ContributionType,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="contributions"
    )

    confidence_level = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Confidence in this initiative’s impact on the objective (e.g., 90%)"
    )
    note = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('business_objective', 'business_initiative')
        ordering = ['priority']

    def __str__(self):
        return f"{self.business_initiative.title} ↔ {self.business_objective.title} ({self.contribution_type})"


class BusinessInitiative(TimeStampedModel):
    """Represents a cross-functional business initiative or theme."""
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="business_initiatives",
        null=True,
        blank=True
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="owned_business_initiatives",
        null=True,
        blank=True
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ("planned", "Planned"),
            ("active", "Active"),
            ("completed", "Completed"),
            ("on_hold", "On Hold")
        ],
        default="planned"
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    business_objectives = models.ManyToManyField(
        'BusinessObjective',
        through=BusinessObjectiveInitiative,
        related_name='business_initiatives',
        blank=True,
        help_text="Business objectives this initiative contributes to.",
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Business Initiatives"


class BusinessInitiativeProductInitiative(models.Model):
    """Through model linking BusinessInitiatives and ProductInitiatives with metadata."""
    business_initiative = models.ForeignKey(
        BusinessInitiative,
        on_delete=models.CASCADE, related_name='business_initiative_product_initiatives'
    )
    product_initiative = models.ForeignKey(
        ProductInitiative,
        on_delete=models.CASCADE
    )
    contribution_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="How much this product initiative contributes to the business initiative."
    )
    note = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("business_initiative", "product_initiative")
        ordering = ["business_initiative"]

    def __str__(self):
        return f"{self.product_initiative} → {self.business_initiative} ({self.contribution_weight or '-'}%)"


class BusinessKPI(TimeStampedModel):
    """Represents a business-level Key Performance Indicator (KPI)."""
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='business_kpis',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    target_value = models.FloatField()
    current_value = models.FloatField()
    unit = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_business_kpis'
    )
    priority = models.PositiveSmallIntegerField(
        default=1,
        help_text="Lower number = higher priority (e.g. 1 is highest)"
    )

    def __str__(self):
        return f"{self.name} - {self.current_value} {self.unit or ''}"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Business KPIs'


class BusinessObjectiveKPI(models.Model):
    """Through model to associate BusinessObjective and BusinessKPI."""
    business_objective = models.ForeignKey('BusinessObjective', on_delete=models.CASCADE, related_name='business_objective_kpis')
    business_kpi = models.ForeignKey(BusinessKPI, on_delete=models.CASCADE, related_name='business_objective_kpis')
    target_value = models.FloatField()
    current_value = models.FloatField()
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Relative weight or contribution % of this objective toward this KPI."
    )
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.business_objective.title} - {self.business_kpi.name}"

    class Meta:
        unique_together = ('business_objective', 'business_kpi')
        ordering = ['business_objective', 'business_kpi']


class BusinessObjective(TimeStampedModel):
    """Represents a strategic business objective or long-term goal."""
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='business_objectives',
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_business_objectives'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    priority = models.PositiveSmallIntegerField(
        default=1,
        help_text="Lower number = higher priority (e.g. 1 is highest)"
    )

    business_kpis = models.ManyToManyField(
        'BusinessKPI',
        through='BusinessObjectiveKPI',
        related_name="business_objectives"
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['priority', 'deadline']
        verbose_name_plural = 'Business Objectives'


class CustomerSegment(TimeStampedModel):
    """Represents a specific customer segment or persona."""
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='customer_segments',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_customer_segments'
    )
    size_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Estimated number of customers in this segment"
    )
    size_value = models.FloatField(
        null=True,
        blank=True,
        help_text="Estimated total value of this customer segment"
    )
    # strategic importance must be dynamically calculated, defined, and updated through a function or AI # LATER
    strategic_importance = models.CharField(
        max_length=50,
        choices=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical")
        ],
        default='medium',
        help_text="Strategic importance of this segment to the organization"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Customer Segment'
        verbose_name_plural = 'Customer Segments'

class CustomerObjective(TimeStampedModel):
    """Represents a key goal or outcome customers aim to achieve."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    metric_name = models.CharField(max_length=255, blank=True, null=True)
    current_value = models.FloatField(null=True, blank=True)
    target_value = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='customer_objectives',
        null=True,
        blank=True
    )
    customer_segments = models.ManyToManyField(
        'CustomerSegment',
        related_name='customer_objectives',
        blank=True
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_customer_objectives'
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Customer Objective'
        verbose_name_plural = 'Customer Objectives'

class CustomerObjectiveProductInitiative(models.Model):
    customer_objective = models.ForeignKey("CustomerObjective", on_delete=models.CASCADE)
    product_initiative = models.ForeignKey("ProductInitiative", on_delete=models.CASCADE)
    
    # contribution_type = models.CharField(
    #     max_length=50,
    #     choices=[
    #         ("discovery", "Discovery"),
    #         ("conversion", "Conversion"),
    #         ("retention", "Retention"),
    #         ("satisfaction", "Satisfaction"),
    #     ],
    #     default="discovery"
    # )

    contribution_type = models.ForeignKey(
        ContributionType,
        on_delete=models.CASCADE,
        related_name='customer_objective_initiatives'
    )
    
    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Confidence (%) that this initiative contributes to the objective"
    )
    
    note = models.TextField(blank=True)

    class Meta:
        unique_together = ("customer_objective", "product_initiative")

    def __str__(self):
        return f"{self.product_initiative} → {self.customer_objective} ({self.contribution_type})"


class Roadmap(TimeStampedModel):
    """
    A strategic roadmap that links together product, business, and customer objectives/initiatives.
    """
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="roadmaps"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_roadmaps"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    # prioritization_logic must be dynamically defined and updated #LATER
    prioritization_logic = models.TextField(
        blank=True,
        help_text="Explanation of prioritization logic used (e.g. RICE, Value/Effort, WSJF, etc.)"
    )

    product_initiatives = models.ManyToManyField(
        ProductInitiative,
        through="RoadmapEntry",
        related_name="included_in_roadmaps"
    )
    
    time_horizon = models.CharField(
        max_length=100,
        choices=[
            ("short_term", "Short Term (0-3 months)"),
            ("medium_term", "Medium Term (3-6 months)"),
            ("long_term", "Long Term (6+ months)")
        ],
        default="short_term",
        help_text="Time horizon this roadmap covers"
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.organization.name})"

    class Meta:
        ordering = ['-created_at']


class RoadmapEntry(models.Model):
    """
    Defines how a specific ProductInitiative is represented in a Roadmap.
    """
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name="roadmap_entries")
    product_initiative = models.ForeignKey(
        ProductInitiative, on_delete=models.CASCADE, null=True, blank=True, related_name="roadmap_entries"
    )
    priority_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Calculated priority score for this initiative in this specific roadmap."
    )
    priority_rank = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Rank of this initiative within the roadmap (1 = highest priority), based on priority_score."
    )
    note = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('roadmap', 'product_initiative')
        ordering = ['priority_rank', 'priority_score']

    def __str__(self):
        initiative_title = self.product_initiative.title if self.product_initiative else "No Initiative"
        roadmap_name = self.roadmap.name if self.roadmap else "No Roadmap"
        return f"{initiative_title} in {roadmap_name} (Rank: {self.priority_rank})"

