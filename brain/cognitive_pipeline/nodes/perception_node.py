# brain/langgraph_flow/nodes/perception.py

from typing import Dict, Any
import logging

from ...models.runs import BrainRun
from ...utils.telemetry import log_info_event, log_validation_event
from ...services.document_processor import DocumentProcessor, DocumentProcessingError
from ...services.llm_document_processor import LLMDocumentProcessor
from ...services.validators import FileValidator
from ..schema import GraphState, ParsedDocumentSchema

logger = logging.getLogger(__name__)


def parse_documents_node(run: BrainRun, state: GraphState) -> GraphState:
    """
    Layer 1: Perception Layer - Hybrid document parsing with LLM enhancement
    
    This node processes uploaded documents and URLs using a hybrid approach:
    1. Traditional parsing (fast, reliable) - Primary
    2. LLM enhancement (intelligent understanding) - Enhancement  
    3. LLM fallback (complex/corrupted files) - Backup
    
    Args:
        run: BrainRun instance for telemetry and error tracking
        state: GraphState containing file paths and processing configuration
        
    Returns:
        Updated GraphState with parsed_documents populated
    """
    try:
        log_info_event(run, "parse_documents", "Starting hybrid document parsing", {
            "file_count": len(state.uploaded_files),
            "link_count": len(state.links),
            "framework": state.framework,
            "hybrid_processing": True
        })
        
        # Validate input files
        if not state.uploaded_files and not state.links:
            raise DocumentProcessingError("No files or links provided for processing")
        
        parsed_documents = []
        
        # Process uploaded files with hybrid approach
        if state.uploaded_files:
            parsed_documents.extend(_process_uploaded_files_hybrid(run, state.uploaded_files))
        
        # Process links (placeholder for now)
        if state.links:
            parsed_documents.extend(_process_links(run, state.links))
        
        # Validate overall processing results
        validation_summary = _validate_processing_results(run, parsed_documents)
        
        # Log processing summary
        log_info_event(run, "parse_documents", "Hybrid document parsing completed", {
            "documents_processed": len(parsed_documents),
            "total_content_length": sum(len(doc.content) for doc in parsed_documents),
            "validation_summary": validation_summary,
            "hybrid_processing_used": True
        })
        
        # Update state with parsed documents
        updated_state = state.model_copy()
        updated_state.parsed_documents = parsed_documents
        
        return updated_state
        
    except Exception as e:
        error_msg = f"Hybrid document parsing failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # Update run status to failed
        run.mark_failed("parse_documents_error", error_msg)
        
        # Re-raise to be handled by telemetry decorator
        raise


def _process_uploaded_files_hybrid(run: BrainRun, file_paths: list[str]) -> list[ParsedDocumentSchema]:
    """Process uploaded files using hybrid LLM + traditional approach."""
    # Validate file paths first
    validation_result = FileValidator.validate_file_paths(file_paths)
    
    log_validation_event(run, "parse_documents", {
        "is_valid": validation_result.is_valid,
        "errors": validation_result.errors,
        "warnings": validation_result.warnings,
        "details": validation_result.details,
        "processing_method": "hybrid"
    })
    
    if not validation_result.is_valid:
        raise DocumentProcessingError(f"File validation failed: {'; '.join(validation_result.errors)}")
    
    # Initialize hybrid processor with proper environment loading
    from decouple import config
    from typing import Optional
    
    try:
        anthropic_key_raw = str(config('ANTHROPIC_API_KEY', default=''))
        openai_key_raw = str(config('OPENAI_API_KEY', default=''))
        # Convert empty strings to None
        anthropic_key: Optional[str] = anthropic_key_raw if anthropic_key_raw else None
        openai_key: Optional[str] = openai_key_raw if openai_key_raw else None
    except Exception:
        anthropic_key = None
        openai_key = None
    
    if anthropic_key or openai_key:
        processor = LLMDocumentProcessor(
            anthropic_api_key=anthropic_key,
            openai_api_key=openai_key
        )
        processing_method = "hybrid_llm"
    else:
        # Fallback to traditional processing if no LLM keys
        processor = DocumentProcessor()
        processing_method = "traditional_only"
        logger.warning("No LLM API keys found, using traditional processing only")
    
    log_info_event(run, "parse_documents", "Starting file processing", {
        "file_count": len(file_paths),
        "validation_score": validation_result.quality_score,
        "processing_method": processing_method
    })
    
    try:
        documents = processor.process_files(file_paths)
        # Convert to ParsedDocumentSchema if needed
        parsed_documents = []
        for doc in documents:
            if isinstance(doc, ParsedDocumentSchema):
                parsed_documents.append(doc)
            elif isinstance(doc, dict):
                parsed_documents.append(ParsedDocumentSchema(**doc))
            else:
                # Fallback: try to extract fields
                parsed_documents.append(ParsedDocumentSchema(
                    id=getattr(doc, 'id', None),
                    content=getattr(doc, 'content', ''),
                    metadata=getattr(doc, 'metadata', None),
                    doc_type=getattr(doc, 'doc_type', None)
                ))
        # Log processing statistics
        stats = processor.get_processing_stats()
        log_info_event(run, "parse_documents", "File processing completed", {
            "processing_stats": stats,
            "documents_created": len(parsed_documents),
            "processing_method": processing_method
        })
        return parsed_documents
        
    except Exception as e:
        raise DocumentProcessingError(f"Hybrid file processing failed: {e}")


def _process_links(run: BrainRun, links: list[str]) -> list[ParsedDocumentSchema]:
    """Process web links (enhanced placeholder for Week 1)."""
    log_info_event(run, "parse_documents", "Processing links (enhanced placeholder)", {
        "link_count": len(links),
        "status": "placeholder_with_llm_ready"
    })
    
    # TODO: Implement link processing with LLM analysis in Week 2
    # For now, create enhanced placeholder documents
    placeholder_documents = []
    
    for i, link in enumerate(links):
        placeholder_doc = ParsedDocumentSchema(
            id=f"url_{i}",
            content=f"[ENHANCED PLACEHOLDER] URL content from: {link}\n\nThis will be processed with LLM-based web scraping in Week 2.",
            metadata={
                "file_path": link,
                "file_type": "url",
                "placeholder": True,
                "llm_ready": True,
                "enhancement_planned": "Week 2"
            },
            doc_type="url"
        )
        placeholder_documents.append(placeholder_doc)
    
    return placeholder_documents


def _validate_processing_results(run: BrainRun, documents: list[ParsedDocumentSchema]) -> Dict[str, Any]:
    """Validate the overall processing results with hybrid metrics."""
    if not documents:
        validation_summary = {
            "overall_valid": False,
            "error": "No documents were processed",
            "document_count": 0,
            "valid_documents": 0,
            "quality_score": 0.0,
            "hybrid_processing": False
        }
    else:
        # No validation_result, tables, or file_type in ParsedDocumentSchema
        validation_summary = {
            "overall_valid": len(documents) > 0,
            "document_count": len(documents),
            "valid_documents": len(documents),
            "quality_score": None,
            "total_content_length": sum(len(doc.content) for doc in documents),
            "total_tables": None,
            "file_types": list(set(doc.metadata.get("file_type", "unknown") for doc in documents if doc.metadata)),
            "hybrid_processing": True,
            "llm_enhanced_count": None,
            "llm_fallback_count": None,
            "enhancement_rate": None
        }
    
    # Log validation summary
    log_validation_event(run, "parse_documents", validation_summary)
    
    return validation_summary