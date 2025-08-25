# brain/cognitive_pipeline/graph.py

from typing import Dict, Any, Optional
import logging
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from ..models import BrainRun
from .schema import GraphState

from brain.cognitive_pipeline.nodes.perception_node import parse_documents_node
from brain.cognitive_pipeline.layers.entity_extraction_layer import entity_extraction_layer
from brain.cognitive_pipeline.layers.world_model_layer import world_model_layer


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
		# Add nodes for each cognitive layer
		workflow.add_node("parse_documents", self._parse_documents_wrapper)
		workflow.add_node("extract_entities", self._entity_extraction_wrapper)
		workflow.add_node("world_model_update", self._world_model_update_wrapper)

		# TODO: Add more nodes for other cognitive layers
		
		workflow.set_entry_point("parse_documents")
		workflow.add_edge("parse_documents", "extract_entities")
		workflow.add_edge("extract_entities", "world_model_update")
		workflow.add_edge("world_model_update", END)
		return workflow.compile()

	def _parse_documents_wrapper(self, state: GraphState) -> GraphState:
		"""Wrapper for parse_documents_node to handle BrainRun context."""
		run = state.context.get("run") if state.context else None
		if not run:
			raise ValueError("BrainRun instance required in state.context['run']")
		return parse_documents_node(run, state)


	def _entity_extraction_wrapper(self, state: GraphState) -> GraphState:
		"""Wrapper for entity_extraction_layer to handle BrainRun context."""
		run = state.context.get("run") if state.context else None
		return entity_extraction_layer(run, state)

	def _world_model_update_wrapper(self, state: GraphState) -> GraphState:
		"""Wrapper for world_model_layer to handle BrainRun context."""
		run = state.context.get("run") if state.context else None
		return world_model_layer(run, state)

	def run_workflow(self, run: BrainRun, initial_state: GraphState) -> GraphState:
		"""
		Execute the complete workflow for a BrainRun.
		Args:
			run: BrainRun instance for telemetry and tracking
			initial_state: Initial GraphState with input data
		Returns:
			Final GraphState with all processing results
		"""
		from brain.cognitive_pipeline.utils.llm_utils import llm_fn_openai
		try:
			if not initial_state.context:
				initial_state.context = {}
			initial_state.context["run"] = run
			# ✅ Inject the functions directly onto the run object
			initial_state.context["llm_fn"] = llm_fn_openai
			initial_state.context["log_fn"] = logger.info

			# Invoke the graph with the initial state
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
	user_id: Optional[int] = None,
	org: Any = None
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
		org: Optional Organization ORM/model instance for initializing business_profile
	Returns:
		Initialized GraphState ready for workflow execution
	"""
	from brain.cognitive_pipeline.schema import BusinessProfile
	business_profile = None
	if org is not None:
		business_profile = BusinessProfile.from_organization(org)
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
		business_profile=business_profile,
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

