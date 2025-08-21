# brain/models/memory.py

from django.db import models

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

