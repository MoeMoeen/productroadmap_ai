# brain/cognitive_pipeline/logic/perception_logic.py

from typing import Dict, Any, List
from ..schema import GraphState, ParsedDocument, DocumentMetadata, DocumentParsingValidationResult, DocumentValidationSummary

# --- Pure logic functions (no Django dependencies) ---

def validate_inputs(state: GraphState):
    if not state.uploaded_files and not state.links:
        raise ValueError("No files or links provided for processing")
    return True


def parse_documents_logic(
    run: Any,  # Should be a context object, not Django-dependent
    state: GraphState,
    select_processor,
    process_files,
    process_links,
    validate_processing_results,
    log_info_event,
    log_validation_event
) -> GraphState:
    """
    Pure logic for document ingestion, LLM usage, and validation summary.
    All dependencies are injected for testability.
    """
    log_info_event(run, "parse_documents", "Starting hybrid document parsing", {
        "file_count": len(state.uploaded_files),
        "link_count": len(state.links),
        "framework": state.framework,
        "hybrid_processing": True
    })
    validate_inputs(state)
    parsed_documents = []
    llm_used = False
    stats = {}
    # Process uploaded files with hybrid approach
    if state.uploaded_files:
        processor, processing_method = select_processor()
        llm_used = processing_method == "hybrid_llm"
        docs, stats = process_files(processor, state.uploaded_files, run, processing_method)
        parsed_documents.extend(docs)
    # Process links
    if state.links:
        parsed_documents.extend(process_links(run, state.links))
    # Validate overall processing results
    validation_summary_dict = validate_processing_results(run, parsed_documents)
    validation_summary = DocumentValidationSummary(
        overall_valid=validation_summary_dict.get("overall_valid", False),
        document_count=validation_summary_dict.get("document_count", 0),
        valid_documents=validation_summary_dict.get("valid_documents", 0),
        file_types=validation_summary_dict.get("file_types", []),
        quality_score=validation_summary_dict.get("quality_score"),
        hybrid_processing=validation_summary_dict.get("hybrid_processing", False)
    )
    # Log processing summary
    log_info_event(run, "parse_documents", "Hybrid document parsing completed", {
        "documents_processed": len(parsed_documents),
        "total_content_length": sum(len(doc.content) for doc in parsed_documents),
        "validation_summary": validation_summary_dict,
        "hybrid_processing_used": True,
        "llm_used": llm_used,
        "processing_stats": stats
    })
    # Update state with parsed documents and new fields
    updated_state = state.model_copy()
    updated_state.parsed_documents = parsed_documents
    updated_state.document_validation_summary = validation_summary
    updated_state.llm_used = llm_used
    updated_state.llm_processing_stats = stats
    return updated_state
