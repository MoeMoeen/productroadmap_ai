# brain/models/memory.py


# Episodic memory event model for logging extracted entities and events
from django.db import models
from brain.models.runs import BrainRun

class EpisodicMemoryEvent(models.Model):
	run = models.ForeignKey(BrainRun, on_delete=models.CASCADE, related_name="episodic_memory")
	timestamp = models.DateTimeField(auto_now_add=True)
	event_type = models.CharField(max_length=100)
	step = models.CharField(max_length=100, null=True, blank=True)
	entity_type = models.CharField(max_length=100, null=True, blank=True)
	value = models.TextField(null=True, blank=True)
	confidence = models.FloatField(null=True, blank=True)
	extraction_method = models.CharField(max_length=100, null=True, blank=True)
	relationships = models.JSONField(null=True, blank=True)
	raw_data = models.JSONField(null=True, blank=True)  # fallback full log

	class Meta:
		ordering = ['-timestamp']


class SemanticMemoryEntry(models.Model):
	"""Persistent semantic memory entry for storing extracted knowledge."""
	run = models.ForeignKey('runs.BrainRun', on_delete=models.CASCADE, related_name='semantic_memories')
	entity_type = models.CharField(max_length=100)
	value = models.TextField()
	step = models.CharField(max_length=100, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"SemanticMemoryEntry({self.entity_type}: {self.value[:30]})"


class EpisodicMemoryEntry(models.Model):
	"""Persistent episodic memory entry for storing event-based memory."""
	run = models.ForeignKey('runs.BrainRun', on_delete=models.CASCADE, related_name='episodic_memories')
	event_type = models.CharField(max_length=100)
	content = models.TextField()
	step = models.CharField(max_length=100, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"EpisodicMemoryEntry({self.event_type}: {self.content[:30]})"

