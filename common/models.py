from django.db import models
from django.apps import apps

# Create your models here.


def get_organization_model():
    return apps.get_model('accounts', 'Organization')

class TimeStampedModel(models.Model):
    """
    Abstract base model with created_at and updated_at fields.
    Inherit from this in any model where you want automatic timestamps.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # This model won't create a table in the database
        ordering = ['-created_at']  # Default ordering by created_at descending 



class ContributionType(models.Model):
    """Model representing a type of contribution to a business objective. 
    Dynamic model for storing reusable types (like "Conversion", "Discovery", etc.)
    """
    # Use the dynamic function to get the Organization model
    organization = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.CASCADE,
        related_name="contribution_types"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ("organization", "name")
        ordering = ["name"]

