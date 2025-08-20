# brain/langgraph_flow/nodes/generate_roadmap_node.py

from brain.cognitive_pipeline.schema import GraphState
from brain.models.runs import BrainRun
from brain.cognitive_pipeline.utils import log_node_io, handle_errors

@handle_errors(raise_on_error=False)
@log_node_io(node_name="generate_roadmap_node")
def generate_roadmap_node(run: BrainRun, state: GraphState) -> GraphState:
    """
    Atomic Node: Generate Roadmap

    Constructs and prioritizes roadmaps using selected frameworks (RICE, WSJF, etc.).
    Populates state.generated_roadmap for downstream review and execution.

    TODO:
    - Implement roadmap generation and prioritization logic
    - Integrate with planner_layer
    """
    print("[TODO] Generate and prioritize roadmap based on business context")
    # state.generated_roadmap = ...
    return state
