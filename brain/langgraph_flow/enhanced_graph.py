# brain/langgraph_flow/enhanced_graph.py

from typing import Dict, Any, Optional
import logging
from langgraph.graph import StateGraph, END

from ..models import BrainRun
from .schema import GraphState
from .nodes.perception_enhanced import parse_documents_node

logger = logging.getLogger(__name__)


class ProductRoadmapGraph:
    """
    LangGraph-based workflow for product roadmap generation using cognitive AI architecture.
    
    This graph orchestrates the 9-layer cognitive AI system for processing documents,
    extracting insights, and generating strategic roadmaps.
    """
    
    def __init__(self):
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph."""
        workflow = StateGraph(GraphState)
        
        # Add nodes for each cognitive layer
        workflow.add_node("parse_documents", self._parse_documents_wrapper)
        # TODO: Add more nodes for other cognitive layers
        
        # Define the workflow
        workflow.set_entry_point("parse_documents")
        workflow.add_edge("parse_documents", END)
        
        return workflow.compile()
    
    def _parse_documents_wrapper(self, state: GraphState) -> GraphState:
        """Wrapper for parse_documents_node to handle BrainRun context."""
        # Get BrainRun from state context
        run = state.context.get("run") if state.context else None
        if not run:
            raise ValueError("BrainRun instance required in state.context['run']")
        
        return parse_documents_node(run, state)
    
    def run_workflow(self, run: BrainRun, initial_state: GraphState) -> GraphState:
        """
        Execute the complete workflow for a BrainRun.
        
        Args:
            run: BrainRun instance for telemetry and tracking
            initial_state: Initial GraphState with input data
            
        Returns:
            Final GraphState with all processing results
        """
        try:
            # Add run to state context
            if not initial_state.context:
                initial_state.context = {}
            initial_state.context["run"] = run
            
            # Execute the graph
            final_state = self.graph.invoke(initial_state)
            
            logger.info(f"Workflow completed successfully for run {run.id}")
            return final_state
            
        except Exception as e:
            logger.error(f"Workflow failed for run {run.id}: {e}", exc_info=True)
            run.mark_failed("workflow_error", str(e))
            raise


def create_ai_job_workflow(
    uploaded_files: list[str],
    links: list[str] = None,
    framework: str = "RICE",
    product_context: str = "",
    organization_id: Optional[int] = None
) -> GraphState:
    """
    Create initial GraphState for AI job workflow.
    
    Args:
        uploaded_files: List of file paths to process
        links: Optional list of URLs to process
        framework: Prioritization framework (RICE, WSJF, MoSCoW)
        product_context: Additional context about the product
        organization_id: Optional organization ID for multi-tenant support
        
    Returns:
        Initialized GraphState ready for workflow execution
    """
    return GraphState(
        # Input data
        uploaded_files=uploaded_files or [],
        links=links or [],
        framework=framework,
        product_context=product_context,
        
        # Processing results (empty initially)
        parsed_documents=[],
        extracted_entities=[],
        enhanced_initiatives=[],
        generated_roadmap={},
        
        # Metadata and context
        context={
            "organization_id": organization_id,
            "processing_start_time": None,
            "processing_end_time": None,
            "total_processing_time_ms": 0
        },
        metadata={}
    )


# Convenience functions for backward compatibility and testing
def run_parse_documents_enhanced(
    run: BrainRun,
    uploaded_files: list[str] = None,
    links: list[str] = None,
    framework: str = "RICE",
    product_context: str = "",
    organization_id: Optional[int] = None
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
        organization_id=organization_id
    )
    
    # Run just the parse_documents node
    final_state = parse_documents_node(run, initial_state)
    
    return final_state.model_dump()


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
        organization_id=None
    )
