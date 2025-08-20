from typing import Dict, Any, Optional
import logging
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from ..models import BrainRun
from .schema import GraphState
from brain.cognitive_pipeline.nodes.perception_node import parse_documents_node

logger = logging.getLogger(__name__)

class ProductRoadmapGraph:
	"""
	LangGraph-based workflow for product roadmap generation using cognitive AI architecture.
	This graph orchestrates the cognitive AI system for processing documents,
	extracting insights, and generating strategic roadmaps.
	"""
	def __init__(self):
		self.graph = self._build_graph()

	def _build_graph(self) -> CompiledStateGraph:
		"""Build the LangGraph state graph."""
		workflow = StateGraph(GraphState)
		# Add nodes for each cognitive layer (currently only parse_documents)
		workflow.add_node("parse_documents", self._parse_documents_wrapper)
		# TODO: Add more nodes for other cognitive layers
		workflow.set_entry_point("parse_documents")
		workflow.add_edge("parse_documents", END)
		return workflow.compile()

	def _parse_documents_wrapper(self, state: GraphState) -> GraphState:
		"""Wrapper for parse_documents_node to handle BrainRun context."""
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
			if not initial_state.context:
				initial_state.context = {}
			initial_state.context["run"] = run
			final_state = self.graph.invoke(initial_state)
			logger.info(f"Workflow completed successfully for run {run.id}")
			return GraphState(**final_state) if isinstance(final_state, dict) else final_state
		except Exception as e:
			logger.error(f"Workflow failed for run {run.id}: {e}", exc_info=True)
			run.mark_failed("workflow_error", str(e))
			raise

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
		org_id=organization_id or 0,
		user_id=user_id or 0,
		uploaded_files=uploaded_files or [],
		links=links or [],
		framework=framework,
		product_context=product_context,
		parsed_documents=[],
		extracted_entities=None,
		generated_roadmap=None,
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
	organization_id: Optional[int] = None
) -> Dict[str, Any]:
	"""
	Enhanced document parsing with full observability and validation.
	This function creates a minimal workflow that just runs the perception layer
	for testing and development purposes.
	"""
	initial_state = create_ai_job_workflow(
	uploaded_files=uploaded_files or [],
	links=links or [],
	framework=framework,
	product_context=product_context,
	organization_id=organization_id,
	user_id=getattr(run, 'user_id', None)
	)
	final_state = parse_documents_node(run, initial_state)
	return final_state.model_dump()

def run_parse_documents(files=None, urls=None, approvals=None, metadata=None) -> Dict[str, Any]:
	"""
	Legacy function for backward compatibility.
	Note: This creates a minimal BrainRun for compatibility but won't persist telemetry.
	Use run_parse_documents_enhanced for full functionality.
	"""
	from ..models import BrainRun
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
