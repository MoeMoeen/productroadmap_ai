from django.db import models
from django.contrib.postgres.fields import JSONField

class WorldModel(models.Model):
    """
    Persistent world model for an organization.
    Stores the latest business profile, entities, and relationships as JSON.
    """
    org_id = models.IntegerField(unique=True, db_index=True)
    data = JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"WorldModel(org_id={self.org_id})"
