from django.db import models
from common.models import TimeStampedModel  # Assuming TimeStampedModel is in common/models.py
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Organization(TimeStampedModel):
    name = models.CharField(max_length=255)

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
