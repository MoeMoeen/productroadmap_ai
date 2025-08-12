# brain/langgraph_flow/graph.py
from typing import Dict, Any
from .schema import GraphState
from .nodes.perception import parse_documents_node
from ..models import BrainRun

# Simple wrapper for backward compatibility
def run_parse_documents(files=None, urls=None, approvals=None, metadata=None) -> Dict[str, Any]:
    # Create a temporary run for legacy compatibility
    run = BrainRun(
        status="running", 
        organization_id=1,
        metadata=metadata or {}
    )
    
    state = GraphState(
        org_id=1,
        user_id=1,
        uploaded_files=files or [],
        links=urls or [],
        framework="RICE",
        product_context="",
        metadata=metadata or {}
    )
    
    # Run the node
    result_state = parse_documents_node(run, state)
    
    return result_state.model_dump()