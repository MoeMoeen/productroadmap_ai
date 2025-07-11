from django.db import models
from common.models import TimeStampedModel
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
