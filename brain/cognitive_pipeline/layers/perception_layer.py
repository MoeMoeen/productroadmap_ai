# brain/cognitive_pipeline/layers/perception_layer.py

from brain.cognitive_pipeline.schema import GraphState
from brain.models.runs import BrainRun
from brain.cognitive_pipeline.utils import log_node_io
from brain.cognitive_pipeline.utils import handle_errors
from brain.cognitive_pipeline.nodes.perception_node import parse_documents_node

@handle_errors(raise_on_error=False)
@log_node_io(node_name="perception_layer")
def perception_layer(run: BrainRun, state: GraphState) -> GraphState:
	"""
	Cognitive Layer: Perception (Layer 1)

	This layer is responsible for:
	- Parsing and normalizing all uploaded documents (PDF, DOCX, PPTX, XLSX, etc.)
	- Extracting raw text, tables, and metadata from each document
	- Identifying the type of each document (e.g., business plan, financial model, strategy deck)
	- Populating the `parsed_documents` field in GraphState for downstream layers

	Business Logic Context:
	- This is the first step after goal/intent detection
	- Ensures all content is in a consistent, machine-readable format
	- Enables downstream layers to reason about the business context, strategy, and objectives

	Architectural Role:
	- Acts as the "sensory input" for the cognitive pipeline
	- Converts unstructured files into structured representations
	- May call atomic nodes like `parse_documents_node` for granular parsing logic

	Usage:
	- Should be run after the goal_intent_layer
	- Updates `state.parsed_documents` with a list of ParsedDocument objects

	TODO:
	- Implement logic to parse and normalize all supported document types
	- Integrate with atomic parsing nodes as needed
	"""
	# Perception layer: simply delegates to the atomic node for document parsing
	return parse_documents_node(run, state)
# Perception Layer
# TODO: Move perception logic here from nodes/perception.py
