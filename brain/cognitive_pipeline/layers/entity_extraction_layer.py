# brain/cognitive_pipeline/layers/entity_extraction_layer.py

from brain.cognitive_pipeline.schema import GraphState
from brain.models.runs import BrainRun
from brain.cognitive_pipeline.utils.utils import log_node_io, handle_errors

@handle_errors(raise_on_error=False)
@log_node_io(node_name="entity_extraction_layer")
def entity_extraction_layer(run: BrainRun, state: GraphState) -> GraphState:
    """
    Cognitive Layer: Entity Extraction (Layer 5)

    This layer is responsible for:
    - Extracting structured entities (objectives, KPIs, initiatives, etc.) from business context
    - Populating the GraphState with concrete, structured items for downstream planning

    Business Logic Context:
    - Pulls out actionable business objectives, customer objectives, KPIs, and more
    - Enables initiative generation and planning to be tightly aligned with business needs

    Architectural Role:
    - Acts as the "structuring" step between business understanding and initiative generation
    - May call atomic nodes like extract_entities_node

    Usage:
    - Should be run after business_understanding_layer
    - Updates state.extracted_entities with structured data

    TODO:
    - Implement logic to extract entities from business context
    - Integrate with atomic entity extraction nodes
    """
    # Call the atomic extract_entities_node
    from brain.cognitive_pipeline.nodes.extract_entities_node import extract_entities_node
    llm_fn = state.context.get("llm_fn") if state.context else None
    log_fn = state.context.get("log_fn") if state.context else None
    # Call the node and return the updated state
    return extract_entities_node(run, state, llm_fn=llm_fn, log_fn=log_fn)
