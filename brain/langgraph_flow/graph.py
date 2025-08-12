# brain/langgraph_flow/graph.py
from typing import Dict, Any
from ..langgraph_flow.schema import GraphState
from ..langgraph_flow.nodes.parse_documents import parse_documents_node

# For Step 1A we won't bring in langgraph yet; just call the node directly
# Later (Step 1C), we’ll wrap this in a LangGraph StateGraph.

def run_parse_documents(files=None, urls=None, approvals=None, metadata=None) -> Dict[str, Any]:
    state = GraphState(
        files=files or [],
        urls=urls or [],
        approvals=approvals or {},
        metadata=metadata or {}
    )
    node_out = parse_documents_node(state)
    # Apply updates to state (the simplest “reducer”)
    for k, v in node_out.updates.items():
        setattr(state, k, v)
    # Attach node note for debugging
    state.metadata["parse_documents_note"] = node_out.notes
    return state.model_dump()