# brain/cognitive_pipeline/logic/entity_extraction_logic.py

from typing import List, Any, Dict, Optional
from ..schema import GraphState, ExtractedEntity
from difflib import SequenceMatcher
import datetime
import re
import json
import os
import yaml

# --- Step 5: Episodic Memory Logging ---
def log_extraction_event(entity, run_id=None, log_fn=None):
    """
    Log an extraction event to episodic memory. Optionally use a provided log_fn for persistence.
    """
    event = {
        "event_type": "extracted_entity",
        "content": f"{entity.entity_type}: {entity.value}",
        "step": entity.step or "entity_extraction",
        "entity_type": entity.entity_type,
        "value": entity.value,
        "confidence": entity.confidence,
        "extraction_method": entity.extraction_method,
        "relationships": entity.relationships,
        "run_id": run_id,
        "timestamp": entity.created_at,
    }
    if log_fn:
        log_fn(event)
    return event

# --- Final Pipeline Wiring Example ---
def run_entity_extraction_pipeline(
    parsed_documents,
    world_model,
    semantic_memory,
    episodic_memory,
    llm_fn,
    run_id=None,
    log_fn=None
):
    """
    Full pipeline: keyword + LLM extraction, deduplication, enrichment, and episodic memory logging.
    Returns list of enriched ExtractedEntity.
    """
    # 1. Keyword extraction
    keyword_entities = keyword_extract_entities(parsed_documents, world_model, semantic_memory)
    # 2. LLM extraction
    llm_entities = llm_extract_entities(parsed_documents, world_model, semantic_memory, llm_fn)
    # 3. Combine and deduplicate
    all_entities = keyword_entities + llm_entities
    deduped_entities = deduplicate_entities(all_entities, semantic_memory, episodic_memory, log_fn=log_fn)
    # 4. Enrich
    enriched_entities = enrich_entities(deduped_entities, world_model, semantic_memory)
    # 5. Log to episodic memory
    for ent in enriched_entities:
        log_extraction_event(ent, run_id=run_id, log_fn=log_fn)
    return enriched_entities




# --- Step 4: LLM-Based Extraction Logic ---

LLM_EXTRACTION_PROMPT = """
You are an expert business analyst. Given the following context, extract all business entities and organizational facts of the following types: BusinessObjective, BusinessInitiative, CustomerObjective, CustomerSegment, ProductInitiative, ProductKPI, BusinessKPI, Product, Vision, Strategy, Market, Department, Headcount, and any relationships between them. Avoid duplicates with prior entities and enrich ambiguous facts using the world model.

World Model (current org facts):
{world_model}

Prior Entities (semantic memory):
{prior_entities}

Document:
{document}
"""

def llm_extract_entities(parsed_documents, world_model, prior_entities, llm_fn, max_tokens=2048):
    """
    Use an LLM to extract entities from parsed documents. Handles prompt construction, output validation, and error handling.
    llm_fn: function that takes a prompt and returns a string (LLM output)
    """
    results = []
    world_model_str = json.dumps(world_model, default=str) if world_model else "{}"
    prior_entities_str = json.dumps([
        {"entity_type": e.entity_type, "value": e.value} for e in (prior_entities or [])
    ], default=str)
    # Accept log_fn as kwarg for error logging
    log_fn = None
    if 'log_fn' in locals():
        log_fn = locals()['log_fn']
    for doc in parsed_documents:
        text = doc.content if hasattr(doc, "content") else str(doc)
        prompt = LLM_EXTRACTION_PROMPT.format(
            world_model=world_model_str,
            prior_entities=prior_entities_str,
            document=text[:max_tokens]
        )
        try:
            llm_output = llm_fn(prompt)
            entities = json.loads(llm_output)
            if not isinstance(entities, list):
                continue
            for ent in entities:
                if not ent.get("entity_type") or not ent.get("value"):
                    continue
                entity = ExtractedEntity(
                    entity_type=ent["entity_type"],
                    value=ent["value"],
                    confidence=ent.get("confidence", 0.85),
                    extraction_method="llm",
                    step="entity_extraction",
                    relationships=ent.get("relationships"),
                    source_document_id=getattr(doc, "file_path", None),
                    source_text_excerpt=text[:200],
                    origin=ent.get("origin", None)
                )
                results.append(entity)
        except Exception as e:
            # Log LLM/JSON errors for later inspection
            if log_fn:
                log_fn({
                    "event_type": "llm_extraction_error",
                    "error": str(e),
                    "prompt_excerpt": prompt[:200],
                    "doc_id": getattr(doc, "file_path", None)
                })
            continue
    return results
# --- Step 2: Deduplication Logic (Semantic & Episodic Memory aware) ---

def is_duplicate_entity(new_entity, prior_entity, threshold=0.85):
    """
    Fuzzy match on entity_type and value. Returns True if duplicate.
    Fuzzy match means allowing for slight variations in wording or phrasing.
    """
    if new_entity.entity_type != prior_entity.entity_type:
        return False
    # Use SequenceMatcher for fuzzy string matching
    val1 = str(new_entity.value).lower()
    val2 = str(prior_entity.value).lower()
    ratio = SequenceMatcher(None, val1, val2).ratio()
    return ratio >= threshold

def deduplicate_entities(all_entities, prior_entities, episodic_memory=None, log_fn=None):
    """
    Remove duplicates using prior (semantic) memory and current batch. Avoids entities marked obsolete in episodic memory.
    """
    deduped = []
    seen = set()
    obsolete = set()
    if episodic_memory:
        for event in episodic_memory:
            if getattr(event, 'event_type', None) == 'removed_entity':
                obsolete.add((getattr(event, 'entity_type', None), str(getattr(event, 'value', None)).lower()))
    for ent in all_entities:
        key = (ent.entity_type, str(ent.value).lower())
        if key in seen or key in obsolete:
            if log_fn:
                log_fn({"event_type": "deduplication_skipped", "entity_type": ent.entity_type, "value": ent.value, "reason": "duplicate or obsolete"})
            continue
        duplicate = False
        for prior in prior_entities:
            if is_duplicate_entity(ent, prior):
                duplicate = True
                break
        if not duplicate:
            deduped.append(ent)
            seen.add(key)
        else:
            if log_fn:
                log_fn({"event_type": "deduplication_skipped", "entity_type": ent.entity_type, "value": ent.value, "reason": "fuzzy duplicate"})
    return deduped

# --- Step 3: Enrichment Logic (World Model & Semantic Memory aware) ---
def enrich_entities(entities, world_model, prior_entities):
    """
    Enrich entities with missing context using world model and prior entities.
    Fills missing fields, links related entities, adds timestamps.
    """
    now = datetime.datetime.utcnow().isoformat()
    enriched = []
    for ent in entities:
        # Fill missing fields from world model or prior entities
        if not ent.confidence:
            ent.confidence = 0.8  # Default if not set
        if not ent.created_at:
            ent.created_at = now
        if not ent.step:
            ent.step = "entity_extraction"
        # Example: link to related ProductInitiative if entity is BusinessObjective
        if ent.entity_type == "BusinessObjective" and world_model:
            related = [pi for pi in world_model.get("ProductInitiative", []) if ent.value.lower() in str(pi).lower()]
            if related:
                ent.relationships = ent.relationships or {}
                ent.relationships["related_initiatives"] = related
        # Example: enrich with prior entity context
        for prior in prior_entities:
            if ent.entity_type == prior.entity_type and str(ent.value).lower() == str(prior.value).lower():
                if prior.relationships:
                    ent.relationships = ent.relationships or {}
                    ent.relationships.update(prior.relationships)
        enriched.append(ent)
    return enriched

# --- Step 1: Robust Keyword/Heuristic Extraction ---


# --- Load ENTITY_PATTERNS from YAML config ---

def load_entity_patterns():
    config_path = os.path.join(os.path.dirname(__file__), "entity_patterns.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
ENTITY_PATTERNS = load_entity_patterns()

def keyword_extract_entities(parsed_documents, world_model, prior_entities):
    """
    Extract entities from parsed documents using keyword and regex patterns.
    Returns a list of ExtractedEntity with confidence and traceability.
    """
    results = []
    for doc in parsed_documents:
        text = doc.content if hasattr(doc, "content") else str(doc)
        for entity_type, patterns in ENTITY_PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    value = match.group(1).strip()
                    if value:
                        entity = ExtractedEntity(
                            entity_type=entity_type,
                            value=value,
                            confidence=0.7,  # Heuristic: keyword matches are medium confidence
                            extraction_method="keyword",
                            step="entity_extraction",
                            source_document_id=getattr(doc, "file_path", None),
                            source_text_excerpt=text[max(0, match.start()-40):match.end()+40],
                            origin=getattr(doc, "origin", None)
                        )
                        results.append(entity)
    return results


# --- Pure logic for entity extraction (memory-aware, hybrid) ---

def entity_extraction_logic(
    parsed_documents: List[Any],
    world_model: Optional[Dict[str, Any]],
    semantic_memory: Optional[List[Any]],
    episodic_memory: Optional[List[Any]],
    keyword_extract_fn,
    llm_extract_fn,
    deduplicate_fn,
    enrich_fn,
    log_event_fn=None
) -> List[ExtractedEntity]:
    """
    Extracts entities from parsed documents, using both keyword/heuristic and LLM-based methods.
    Incorporates semantic and episodic memory for continuity and enrichment.
    Returns a list of ExtractedEntity.
    """
    # 1. Read from semantic memory to prevent duplicates and enrich context
    prior_entities = semantic_memory or []
    # 2. Run keyword/heuristic extraction
    keyword_entities = keyword_extract_fn(parsed_documents, world_model, prior_entities)
    # 3. Run LLM-based extraction
    llm_entities = llm_extract_fn(parsed_documents, world_model, prior_entities)
    # 4. Combine and deduplicate
    all_entities = keyword_entities + llm_entities
    deduped_entities = deduplicate_fn(all_entities, prior_entities)
    # 5. Enrich ambiguous or partial entities
    enriched_entities = enrich_fn(deduped_entities, world_model, prior_entities)
    # 6. Optionally log extraction events to episodic memory
    if log_event_fn:
        for ent in enriched_entities:
            log_event_fn(ent)
    return enriched_entities
