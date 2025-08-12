# brain/langgraph_flow/nodes/perception_enhanced.py

from typing import Dict, Any
import logging

from ...models import BrainRun
from ...utils.telemetry import log_node_io, log_info_event, log_validation_event
from ...services.document_processor import DocumentProcessor, DocumentProcessingError
from ...services.validators import FileValidator
from ..schema import GraphState, ParsedDocument

logger = logging.getLogger(__name__)


@log_node_io(node_name="parse_documents")
def parse_documents_node(run: BrainRun, state: GraphState) -> GraphState:
    """
    Layer 1: Perception Layer - Document parsing with quality validation
    
    This node processes uploaded documents and URLs to extract structured content.
    It validates files, processes them based on type (PDF, DOCX, XLSX), and 
    returns structured ParsedDocument objects with metadata and quality scores.
    
    Args:
        run: BrainRun instance for telemetry and error tracking
        state: GraphState containing file paths and processing configuration
        
    Returns:
        Updated GraphState with parsed_documents populated
    """
    try:
        log_info_event(run, "parse_documents", "Starting document parsing", {
            "file_count": len(state.uploaded_files),
            "link_count": len(state.links),
            "framework": state.framework
        })
        
        # Validate input files
        if not state.uploaded_files and not state.links:
            raise DocumentProcessingError("No files or links provided for processing")
        
        parsed_documents = []
        
        # Process uploaded files
        if state.uploaded_files:
            parsed_documents.extend(_process_uploaded_files(run, state.uploaded_files))
        
        # Process links (placeholder for now)
        if state.links:
            parsed_documents.extend(_process_links(run, state.links))
        
        # Validate overall processing results
        validation_summary = _validate_processing_results(run, parsed_documents)
        
        # Log processing summary
        log_info_event(run, "parse_documents", "Document parsing completed", {
            "documents_processed": len(parsed_documents),
            "successful_documents": sum(1 for doc in parsed_documents if doc.validation_result.is_valid),
            "total_content_length": sum(len(doc.content) for doc in parsed_documents),
            "validation_summary": validation_summary
        })
        
        # Update state with parsed documents
        updated_state = state.model_copy()
        updated_state.parsed_documents = parsed_documents
        
        return updated_state
        
    except Exception as e:
        error_msg = f"Document parsing failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # Update run status to failed
        run.mark_failed("parse_documents_error", error_msg)
        
        # Re-raise to be handled by telemetry decorator
        raise


def _process_uploaded_files(run: BrainRun, file_paths: list[str]) -> list[ParsedDocument]:
    """Process uploaded files using DocumentProcessor."""
    # Validate file paths first
    validation_result = FileValidator.validate_file_paths(file_paths)
    
    log_validation_event(run, "parse_documents", {
        "is_valid": validation_result.is_valid,
        "errors": validation_result.errors,
        "warnings": validation_result.warnings,
        "details": validation_result.details
    })
    
    if not validation_result.is_valid:
        raise DocumentProcessingError(f"File validation failed: {'; '.join(validation_result.errors)}")
    
    # Process files
    processor = DocumentProcessor()
    
    log_info_event(run, "parse_documents", "Starting file processing", {
        "file_count": len(file_paths),
        "validation_score": validation_result.quality_score
    })
    
    try:
        documents = processor.process_files(file_paths)
        
        # Log processing statistics
        stats = processor.get_processing_stats()
        log_info_event(run, "parse_documents", "File processing completed", {
            "processing_stats": stats,
            "documents_created": len(documents)
        })
        
        return documents
        
    except Exception as e:
        raise DocumentProcessingError(f"File processing failed: {e}")


def _process_links(run: BrainRun, links: list[str]) -> list[ParsedDocument]:
    """Process web links (placeholder implementation for Week 1)."""
    log_info_event(run, "parse_documents", "Processing links (placeholder)", {
        "link_count": len(links),
        "status": "not_implemented"
    })
    
    # TODO: Implement link processing in future weeks
    # For now, create placeholder documents
    placeholder_documents = []
    
    for i, link in enumerate(links):
        placeholder_doc = ParsedDocument(
            file_path=link,
            file_type="url",
            content=f"[PLACEHOLDER] Content from: {link}",
            tables=[],
            metadata={
                "file_path": link,
                "file_size": 0,
                "file_type": "url", 
                "page_count": 1,
                "table_count": 0,
                "processing_time_ms": 0,
                "extracted_text_length": len(f"[PLACEHOLDER] Content from: {link}")
            },
            validation_result={
                "is_valid": False,
                "quality_score": 0.0,
                "errors": ["URL processing not yet implemented"],
                "warnings": ["This is a placeholder for future URL processing"],
                "details": {"placeholder": True, "url": link}
            }
        )
        placeholder_documents.append(placeholder_doc)
    
    return placeholder_documents


def _validate_processing_results(run: BrainRun, documents: list[ParsedDocument]) -> Dict[str, Any]:
    """Validate the overall processing results and create summary."""
    if not documents:
        validation_summary = {
            "overall_valid": False,
            "error": "No documents were processed",
            "document_count": 0,
            "valid_documents": 0,
            "quality_score": 0.0
        }
    else:
        valid_docs = [doc for doc in documents if doc.validation_result.is_valid]
        total_quality = sum(doc.validation_result.quality_score for doc in documents)
        avg_quality = total_quality / len(documents)
        
        validation_summary = {
            "overall_valid": len(valid_docs) > 0,
            "document_count": len(documents),
            "valid_documents": len(valid_docs),
            "quality_score": avg_quality,
            "total_content_length": sum(len(doc.content) for doc in documents),
            "total_tables": sum(len(doc.tables) for doc in documents),
            "file_types": list(set(doc.file_type for doc in documents))
        }
    
    # Log validation summary
    log_validation_event(run, "parse_documents", validation_summary)
    
    return validation_summary
