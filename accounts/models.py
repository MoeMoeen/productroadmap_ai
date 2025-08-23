from django.db import models
from common.models import TimeStampedModel  # Assuming TimeStampedModel is in common/models.py
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.name

class Organization(TimeStampedModel):
    name = models.CharField(max_length=255)
    vision = models.TextField(null=True, blank=True)
    markets = models.CharField(max_length=512, null=True, blank=True, help_text="Comma-separated list of markets")
    headcount = models.IntegerField(null=True, blank=True)
    departments = models.CharField(max_length=512, null=True, blank=True, help_text="Comma-separated list of departments")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class User(AbstractUser):
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='users',
        null=True, 
        blank=True    
    )
    #required fields for django to identify the user model
    # USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS = ['email']
