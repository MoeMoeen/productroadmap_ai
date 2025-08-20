# brain/langgraph_flow/nodes/present_plan_to_user_node.py

from brain.langgraph_flow.schema import GraphState
from brain.models.runs import BrainRun
from brain.langgraph_flow.utils import log_node_io
from brain.cognitive_pipeline.utils import log_node_io

@log_node_io(node_name="present_plan_to_user_node")
def present_plan_to_user_node(run: BrainRun, state: GraphState) -> GraphState:
    """
    Atomic Node: Present Plan to User

    Presents generated plans, profiles, and strategies to the user for review and feedback.
    Updates state with user feedback and approval status.

    TODO:
    - Implement user review and feedback logic
    - Integrate with deliberation_layer
    """
    print("[TODO] Present plan/profile to user and capture feedback")
    # state.user_feedback = ...
    return state
