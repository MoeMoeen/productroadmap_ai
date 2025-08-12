# brain/langgraph_flow/simple_workflow.py

"""
Simplified workflow for Week 1 implementation.
This avoids complex LangGraph setup while providing the core functionality.
"""

from typing import Dict, Any, Optional
import logging

from ..models import BrainRun
from .schema import GraphState
from .nodes.perception import parse_documents_node

logger = logging.getLogger(__name__)


def create_ai_job_workflow(
    uploaded_files: list[str],
    links: Optional[list[str]] = None,
    framework: str = "RICE",
    product_context: str = "",
    organization_id: Optional[int] = None,
    user_id: Optional[int] = None
) -> GraphState:
    """
    Create initial GraphState for AI job workflow.
    
    Args:
        uploaded_files: List of file paths to process
        links: Optional list of URLs to process
        framework: Prioritization framework (RICE, WSJF, MoSCoW)
        product_context: Additional context about the product
        organization_id: Optional organization ID for multi-tenant support
        user_id: Optional user ID
        
    Returns:
        Initialized GraphState ready for workflow execution
    """
    return GraphState(
        # Required fields
        org_id=organization_id or 0,
        user_id=user_id or 0,
        
        # Input data
        uploaded_files=uploaded_files or [],
        links=links or [],
        framework=framework,
        product_context=product_context,
        
        # Processing results (empty initially)
        parsed_documents=None,
        extracted_entities=None,
        enhanced_initiatives=None,
        generated_roadmap=None,
        
        # Metadata and context
        context={
            "organization_id": organization_id,
            "processing_start_time": None,
            "processing_end_time": None,
            "total_processing_time_ms": 0
        },
        metadata={}
    )


def run_parse_documents_enhanced(
    run: BrainRun,
    uploaded_files: Optional[list[str]] = None,
    links: Optional[list[str]] = None,
    framework: str = "RICE",
    product_context: str = "",
    organization_id: Optional[int] = None,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Enhanced document parsing with full observability and validation.
    
    This function creates a minimal workflow that just runs the perception layer
    for testing and development purposes.
    """
    # Create initial state
    initial_state = create_ai_job_workflow(
        uploaded_files=uploaded_files or [],
        links=links or [],
        framework=framework,
        product_context=product_context,
        organization_id=organization_id,
        user_id=user_id
    )
    
    # Add run to state context
    if not initial_state.context:
        initial_state.context = {}
    initial_state.context["run"] = run
    
    # Run just the parse_documents node
    final_state = parse_documents_node(run, initial_state)
    
    return final_state.model_dump()


def run_simple_workflow(run: BrainRun, initial_state: GraphState) -> GraphState:
    """
    Run a simplified workflow for Week 1.
    
    This just runs the perception layer for now. In future weeks,
    we'll add more cognitive layers.
    """
    try:
        # Add run to state context
        if not initial_state.context:
            initial_state.context = {}
        initial_state.context["run"] = run
        
        # Run perception layer
        final_state = parse_documents_node(run, initial_state)
        
        logger.info(f"Simple workflow completed successfully for run {run.id}")
        return final_state
        
    except Exception as e:
        logger.error(f"Simple workflow failed for run {run.id}: {e}", exc_info=True)
        run.mark_failed("workflow_error", str(e))
        raise


# Legacy compatibility function
def run_parse_documents(files=None, urls=None, approvals=None, metadata=None) -> Dict[str, Any]:
    """
    Legacy function for backward compatibility.
    
    Note: This creates a minimal BrainRun for compatibility but won't persist telemetry.
    Use run_parse_documents_enhanced for full functionality.
    """
    from ..models import BrainRun
    
    # Create a temporary run (won't be saved without proper context)
    run = BrainRun(
        status="running",
        organization_id=None,
        metadata=metadata or {}
    )
    
    return run_parse_documents_enhanced(
        run=run,
        uploaded_files=files or [],
        links=urls or [],
        framework="RICE",
        product_context="",
        organization_id=None,
        user_id=None
    )
