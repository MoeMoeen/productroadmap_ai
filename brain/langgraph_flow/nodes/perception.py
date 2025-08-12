# brain/langgraph_flow/nodes/perception.py

from typing import Dict, Any
import logging
import os

from ...models import BrainRun
from ...utils.telemetry import log_info_event, log_validation_event
from ...services.document_processor import DocumentProcessor, DocumentProcessingError
from ...services.llm_document_processor import LLMDocumentProcessor
from ...services.validators import FileValidator
from ..schema import GraphState, ParsedDocument, DocumentMetadata, ValidationResult

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
            "successful_documents": sum(1 for doc in parsed_documents if doc.validation_result.is_valid),
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


def _process_uploaded_files_hybrid(run: BrainRun, file_paths: list[str]) -> list[ParsedDocument]:
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
    
    # Initialize hybrid processor
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
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
        
        # Log processing statistics
        stats = processor.get_processing_stats()
        log_info_event(run, "parse_documents", "File processing completed", {
            "processing_stats": stats,
            "documents_created": len(documents),
            "processing_method": processing_method
        })
        
        return documents
        
    except Exception as e:
        raise DocumentProcessingError(f"Hybrid file processing failed: {e}")


def _process_links(run: BrainRun, links: list[str]) -> list[ParsedDocument]:
    """Process web links (enhanced placeholder for Week 1)."""
    log_info_event(run, "parse_documents", "Processing links (enhanced placeholder)", {
        "link_count": len(links),
        "status": "placeholder_with_llm_ready"
    })
    
    # TODO: Implement link processing with LLM analysis in Week 2
    # For now, create enhanced placeholder documents
    placeholder_documents = []
    
    for i, link in enumerate(links):
        placeholder_doc = ParsedDocument(
            file_path=link,
            file_type="url",
            content=f"[ENHANCED PLACEHOLDER] URL content from: {link}\n\nThis will be processed with LLM-based web scraping in Week 2.",
            tables=[],
            metadata=DocumentMetadata(
                file_path=link,
                file_size=0,
                file_type="url", 
                page_count=1,
                table_count=0,
                processing_time_ms=0,
                extracted_text_length=len(f"Enhanced placeholder for: {link}")
            ),
            validation_result=ValidationResult(
                is_valid=False,
                quality_score=0.0,
                errors=["URL processing not yet implemented"],
                warnings=["Enhanced placeholder - LLM web scraping coming in Week 2"],
                details={
                    "placeholder": True, 
                    "url": link,
                    "llm_ready": True,
                    "enhancement_planned": "Week 2"
                }
            )
        )
        placeholder_documents.append(placeholder_doc)
    
    return placeholder_documents


def _validate_processing_results(run: BrainRun, documents: list[ParsedDocument]) -> Dict[str, Any]:
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
        valid_docs = [doc for doc in documents if doc.validation_result.is_valid]
        total_quality = sum(doc.validation_result.quality_score for doc in documents)
        avg_quality = total_quality / len(documents)
        
        # Check for LLM enhancement usage
        llm_enhanced = sum(1 for doc in documents 
                          if doc.validation_result.details.get("enhancement_applied", False))
        llm_fallbacks = sum(1 for doc in documents 
                           if doc.validation_result.details.get("llm_fallback", False))
        
        validation_summary = {
            "overall_valid": len(valid_docs) > 0,
            "document_count": len(documents),
            "valid_documents": len(valid_docs),
            "quality_score": avg_quality,
            "total_content_length": sum(len(doc.content) for doc in documents),
            "total_tables": sum(len(doc.tables) for doc in documents),
            "file_types": list(set(doc.file_type for doc in documents)),
            "hybrid_processing": True,
            "llm_enhanced_count": llm_enhanced,
            "llm_fallback_count": llm_fallbacks,
            "enhancement_rate": llm_enhanced / len(documents) if documents else 0
        }
    
    # Log validation summary
    log_validation_event(run, "parse_documents", validation_summary)
    
    return validation_summary