# brain/cognitive_pipeline/nodes/extract_entities_node.py

from brain.cognitive_pipeline.schema import GraphState
from brain.models.runs import BrainRun
from brain.cognitive_pipeline.utils.utils import log_node_io, handle_errors

@handle_errors(raise_on_error=False)
@log_node_io(node_name="extract_entities_node")
def extract_entities_node(run: BrainRun, state: GraphState, llm_fn = None) -> GraphState:
    """
    Atomic Node: Extract Entities

    Extracts structured entities (objectives, KPIs, etc.) from business context and parsed documents.
    Populates state.extracted_entities for downstream layers.

    TODO:
    - Integrate with entity_extraction_layer
    """

    from brain.cognitive_pipeline.logic.entity_extraction_logic import (
        entity_extraction_logic,
        keyword_extract_entities,
        llm_extract_entities,
        deduplicate_entities,
        enrich_entities,
        log_extraction_event
    )
    from brain.cognitive_pipeline.schema import ExtractedEntity

    # Allow for dependency injection (for prod/tests)
    # llm_fn = getattr(run, "llm_fn", None)
    if llm_fn is None:
        raise ValueError("llm_fn must be provided on BrainRun for entity extraction")

    log_fn = getattr(run, "log_fn", None)

    # Prepare memory
    semantic_memory = getattr(state, "extracted_entities", None) or []
    episodic_memory = getattr(state, "episodic_memory", None) or []
    world_model = getattr(state, "business_profile", None) or {}
    parsed_documents = getattr(state, "parsed_documents", None) or []

    # Wrap LLM extraction to ensure robust parsing/validation
    def safe_llm_extract(parsed_docs, world_model, prior_entities):
        raw = llm_extract_entities(parsed_docs, world_model, prior_entities, llm_fn)
        # Validate and coerce to ExtractedEntity list
        results = []
        for ent in raw:
            if isinstance(ent, ExtractedEntity):
                results.append(ent)
            elif isinstance(ent, dict) and ent.get("entity_type") and ent.get("value"):
                try:
                    results.append(ExtractedEntity(**ent))
                except Exception:
                    continue
        return results

    # Log batch start
    if log_fn:
        log_fn({"event_type": "entity_extraction_batch_start", "count": len(parsed_documents)})

    # Run extraction logic (now returns both entities and relationships)
    extracted_entities, inferred_relationships = entity_extraction_logic(
        parsed_documents=parsed_documents,
        world_model=world_model,
        semantic_memory=semantic_memory,
        episodic_memory=episodic_memory,
        keyword_extract_fn=keyword_extract_entities,
        llm_extract_fn=safe_llm_extract,
        deduplicate_fn=deduplicate_entities,
        enrich_fn=enrich_entities,
        log_event_fn=(lambda ent: log_extraction_event(ent, run_id=getattr(run, "id", None), log_fn=log_fn)) if log_fn else None
    )
    if log_fn:
        log_fn({"event_type": "relationship_inference_batch_end", "count": len(inferred_relationships)})
    state.extracted_entities = extracted_entities
    state.inferred_relationships = inferred_relationships
    return state
