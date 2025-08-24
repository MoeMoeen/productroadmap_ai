# brain/cognitive_pipeline/nodes/extract_entities_node.py

from brain.cognitive_pipeline.schema import GraphState
from brain.models.runs import BrainRun
from brain.cognitive_pipeline.utils.utils import log_node_io, handle_errors

@handle_errors(raise_on_error=False)
@log_node_io(node_name="capture_feedback_loop_node")
def capture_feedback_loop_node(run: BrainRun, state: GraphState) -> GraphState:
    """
    Atomic Node: Capture Feedback Loop

    Captures user feedback, edits, or rejections to improve future extractions and outputs.
    Updates state and/or persistent storage with learning signals.

    TODO:
    - Implement feedback capture and learning logic
    - Integrate with learning_layer
    """
    print("[TODO] Capture user feedback and update learning signals")
    # state.learning_signals = ...
    return state
