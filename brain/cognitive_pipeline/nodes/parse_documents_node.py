# brain/langgraph_flow/nodes/parse_documents_node.py

from brain.langgraph_flow.schema import GraphState
from brain.models.runs import BrainRun
from brain.langgraph_flow.utils import log_node_io
from brain.cognitive_pipeline.utils import log_node_io

@log_node_io(node_name="parse_documents_node")
def parse_documents_node(run: BrainRun, state: GraphState) -> GraphState:
    """
    Atomic Node: Parse Documents

    Parses and normalizes uploaded documents (PDF, DOCX, PPTX, XLSX, etc.), extracting raw text, tables, and metadata.
    Populates state.parsed_documents for downstream layers.

    TODO:
    - Implement document parsing logic for all supported types
    - Integrate with perception_layer
    """
    print("[TODO] Parse and normalize uploaded documents")
    # state.parsed_documents = ...
    return state
