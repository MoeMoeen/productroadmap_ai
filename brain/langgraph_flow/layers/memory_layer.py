# brain/langgraph_flow/layers/memory_layer.py

from brain.langgraph_flow.schema import GraphState
from brain.models.runs import BrainRun
from brain.models.memory import SemanticMemoryEntry, EpisodicMemoryEntry
from brain.langgraph_flow.utils import log_node_io

@log_node_io(node_name="memory_layer")
def memory_layer(run: BrainRun, state: GraphState) -> GraphState:
	"""
	Cognitive Layer: Memory (Layer 2)

	This layer is responsible for:
	- Capturing episodic memory (steps, documents, results) for each run
	- Updating semantic memory (facts, entities, insights)
	- Persisting to memory models (e.g., SemanticMemoryEntry, EpisodicMemoryEntry)
	- Optionally, integrating with a vector DB or knowledge store (mocked for now)

	Business Logic Context:
	- Stores normalized documents and extracted entities for long-term reference
	- Enables the system to recall past facts, context, and results across runs
	- Supports downstream reasoning, validation, and learning layers

	Architectural Role:
	- Acts as the "memory bank" for the cognitive pipeline
	- Ensures all key information is persisted and available for future steps
	- May call atomic nodes for granular memory operations

	Usage:
	- Should be run after the perception layer
	- Updates persistent storage with new documents and entities

	TODO:
	- Implement real ORM/model persistence for memory entries
	- Integrate with vector DB or knowledge store as needed
	"""
	# Capture episodic memory (documents, steps, results)
	if state.parsed_documents:
		for doc in state.parsed_documents:
			EpisodicMemoryEntry.objects.create(
				run=run,
				document_id=getattr(doc, 'id', None),
				content=getattr(doc, 'content', None),
				metadata=getattr(doc, 'metadata', {}),
				step="perception"
			)
	# Capture semantic memory (entities, facts)
	if state.extracted_entities:
		for entity_type, entities in state.extracted_entities.items():
			for entity in entities:
				SemanticMemoryEntry.objects.create(
					run=run,
					entity_type=entity_type,
					value=entity
				)
	# (Optional) Persist to vector DB or knowledge store (mocked)
	# vector_db.save(state.parsed_documents + state.extracted_entities)

	return state
# Memory Layer
# TODO: Implement memory layer logic
