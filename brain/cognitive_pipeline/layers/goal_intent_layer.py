# brain/cognitive_pipeline/layers/goal_intent_layer.py

from brain.cognitive_pipeline.schema import GraphState
from brain.models.runs import BrainRun
from brain.cognitive_pipeline.utils import log_node_io, handle_errors

@handle_errors(raise_on_error=False)
@log_node_io(node_name="goal_intent_layer")
def goal_intent_layer(run: BrainRun, state: GraphState) -> GraphState:
    """
    Cognitive Layer: Goal & Intent (Layer 0)

    This layer is responsible for:
    - Interpreting the user's goal or intent (e.g., "generate_full_roadmap", "prioritize_existing", "suggest_new_initiatives", etc.)
    - Configuring the downstream pipeline dynamically based on the detected intent
    - Acting as the entry point for all AI jobs, ensuring the right sequence of cognitive layers and nodes is activated for each business scenario

    Business Logic Context:
    - The system supports multiple types of AI jobs, each with a different user goal and requiring a different sequence of layers and nodes
    - Example goals: full roadmap generation, prioritization, initiative suggestion, business objective extraction, strategy comparison, etc.
    - This layer enables dynamic flow control, so the LangGraph DAG can route to different subflows based on the user's intent
    - Without this layer, the pipeline would be static and less flexible

    Architectural Role:
    - Goal formation is a distinct phase of cognition in agentic systems
    - It governs which mental resources (layers/nodes) are activated
    - It defines the plan for the plan, similar to a human deciding "what am I trying to do?"
    - Enables pluggable, composable flows and easy UX integration (e.g., user clicks "Enhance Roadmap" → system starts at that goal)

    Usage:
    - This should be the first layer in the LangGraph pipeline
    - Sets `state.intent` to a string representing the user's goal
    - Downstream layers and nodes can branch or skip steps based on this intent

    TODO:
    - Implement logic to infer user intent from state/input
    - Example: state.intent = "generate_full_roadmap" or "prioritize_existing"
    """
    print("[TODO] Infer and set user goal/intent in GraphState")
    # state.intent = ...
    return state
