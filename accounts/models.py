from django.db import models
from common.models import TimeStampedModel  # Assuming TimeStampedModel is in common/models.py

# Create your models here.

class Organization(TimeStampedModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

