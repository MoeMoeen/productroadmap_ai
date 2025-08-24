# brain/langgraph_flow/layers/memory_layer.py

from brain.cognitive_pipeline.schema import GraphState
from brain.models.runs import BrainRun
from brain.cognitive_pipeline.utils.utils import log_node_io, handle_errors

@handle_errors(raise_on_error=False)
@log_node_io(node_name="memory_layer")
def memory_layer(run: BrainRun, state: GraphState) -> GraphState:
	"""
	Cognitive Layer: Memory (Layer 2)

	This layer captures episodic and semantic memory for each run and persists them using ORM models.
	"""
	from brain.models.memory import EpisodicMemoryEntry, SemanticMemoryEntry

	# Persist episodic memory for each parsed document
	if state.parsed_documents:
		for doc in state.parsed_documents:
			EpisodicMemoryEntry.objects.create(
				run=run,
				event_type="document_parsed",
				content=doc.content,
				step="perception_layer"
			)

	# Persist semantic memory for each extracted entity
	if state.extracted_entities:
		for entity in state.extracted_entities:
			SemanticMemoryEntry.objects.create(
				run=run,
				entity_type=getattr(entity, 'entity_type', 'unknown'),
				value=str(entity),
				step="entity_extraction_layer"
			)

	# (Optional) Integrate with vector DB or knowledge store here

	return state
