# brain/langgraph_flow/nodes/extract_entities_node.py

from brain.cognitive_pipeline.schema import GraphState
from brain.models.runs import BrainRun
from brain.cognitive_pipeline.utils import log_node_io, handle_errors

@handle_errors(raise_on_error=False)
@log_node_io(node_name="extract_entities_node")
def extract_entities_node(run: BrainRun, state: GraphState) -> GraphState:
    """
    Atomic Node: Extract Entities

    Extracts structured entities (objectives, KPIs, etc.) from business context and parsed documents.
    Populates state.extracted_entities for downstream layers.

    TODO:
    - Implement entity extraction logic
    - Integrate with entity_extraction_layer
    """
    print("[TODO] Extract structured entities from business context")
    # state.extracted_entities = ...
    return state
