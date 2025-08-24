# brain/cognitive_pipeline/nodes/extract_entities_node.py

from brain.cognitive_pipeline.schema import GraphState
from brain.models.runs import BrainRun
from brain.cognitive_pipeline.utils.utils import log_node_io, handle_errors

@handle_errors(raise_on_error=False)
@log_node_io(node_name="save_outputs_node")
def save_outputs_node(run: BrainRun, state: GraphState) -> GraphState:
    """
    Atomic Node: Save Outputs

    Persists the final roadmap, initiatives, and links into the database.
    Updates persistent storage with all final outputs.

    TODO:
    - Implement output persistence logic
    - Integrate with execution_layer
    """
    print("[TODO] Persist roadmap, initiatives, and links to DB")
    # Save outputs to DB
    return state
