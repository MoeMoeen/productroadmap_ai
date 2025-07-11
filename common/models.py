from django.db import models

# Create your models here.

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


    