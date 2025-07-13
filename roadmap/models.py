from django.db import models
from common.models import TimeStampedModel, ContributionType
from accounts.models import Organization, User


# Create your models here.

class ProductKPI(TimeStampedModel):
    """Represents a KPI or metric used to evaluate product performance."""
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
        related_name='created_kpis', 
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
    status = models.CharField(max_length=50, choices=[
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold')
    ], default='planned')

    kpis = models.ManyToManyField(
        ProductKPI,
        through="ProductInitiativeKPI",
        related_name="initiatives"
    )
    
    
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Product Initiatives'

    
class ProductInitiativeKPI(models.Model):
    """Through model to associate ProductInitiative and ProductKPI."""
    product_initiative = models.ForeignKey(ProductInitiative, on_delete=models.CASCADE)
    product_kpi = models.ForeignKey(ProductKPI, on_delete=models.CASCADE)
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

    product_initiatives = models.ManyToManyField(
        ProductInitiative,
        through="BusinessInitiativeProductInitiative",
        related_name="business_initiatives"
    )

    business_kpis = models.ManyToManyField(
        BusinessKPI,
        through="BusinessInitiativeKPI",
        related_name="business_initiatives"
    )

    business_objectives = models.ManyToManyField(
        'BusinessObjective',
        through='BusinessObjectiveInitiative',
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
        on_delete=models.CASCADE
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


class BusinessInitiativeKPI(models.Model):
    """Metadata for how a BusinessInitiative contributes to a BusinessKPI."""
    business_initiative = models.ForeignKey(BusinessInitiative, on_delete=models.CASCADE)
    business_kpi = models.ForeignKey(BusinessKPI, on_delete=models.CASCADE)
    contribution_weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Relative weight or impact this initiative has on the KPI."
    )
    note = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("business_initiative", "business_kpi")
        ordering = ["business_initiative"]

    def __str__(self):
        return f"{self.business_initiative} → {self.business_kpi} ({self.contribution_weight or '-'}%)"



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

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['priority', 'deadline']
        verbose_name_plural = 'Business Objectives'


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
    product_initiatives = models.ManyToManyField(
        'ProductInitiative',
        through='CustomerObjectiveInitiative',
        related_name='customer_objectives'
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Customer Objective'
        verbose_name_plural = 'Customer Objectives'

class CustomerObjectiveInitiative(models.Model):
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


# roadmap/models.py


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

    prioritization_logic = models.TextField(
        blank=True,
        help_text="Explanation of prioritization logic used (e.g. RICE, Value/Effort)"
    )

    product_initiatives = models.ManyToManyField(
        ProductInitiative,
        blank=True,
        related_name="roadmaps"
    )
    business_initiatives = models.ManyToManyField(
        BusinessInitiative,
        blank=True,
        related_name="roadmaps"
    )
    customer_objectives = models.ManyToManyField(
        'CustomerObjective',
        blank=True,
        related_name="roadmaps"
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.organization.name})"

    class Meta:
        ordering = ['-created_at']


