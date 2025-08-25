# brain/cognitive_pipeline/nodes/perception_node.py

from typing import Dict, Any
import logging


from ...models.runs import BrainRun
from ...utils.telemetry import log_info_event, log_validation_event
from ..utils.document_processor import DocumentProcessor, DocumentProcessingError
from ..utils.llm_document_processor import LLMDocumentProcessor
from ..utils.file_validators import FileValidator
from ..schema import GraphState, ParsedDocument, DocumentMetadata, DocumentParsingValidationResult
from ..logic.perception_logic import parse_documents_logic

logger = logging.getLogger(__name__)


def _select_processor():
    from decouple import config
    from typing import Optional
    anthropic_key_raw = str(config('ANTHROPIC_API_KEY', default=''))
    openai_key_raw = str(config('OPENAI_API_KEY', default=''))
    anthropic_key: Optional[str] = anthropic_key_raw if anthropic_key_raw else None
    openai_key: Optional[str] = openai_key_raw if openai_key_raw else None
    if anthropic_key or openai_key:
        return LLMDocumentProcessor(
            anthropic_api_key=anthropic_key,
            openai_api_key=openai_key
        ), "hybrid_llm"
    else:
        logger.warning("No LLM API keys found, using traditional processing only")
        return DocumentProcessor(), "traditional_only"


def _process_files(processor : DocumentProcessor | LLMDocumentProcessor, file_paths : list[str], run : BrainRun, processing_method : str):
    validation_result = FileValidator.validate_file_paths(file_paths)
    log_validation_event(run, "parse_documents", {
        "is_valid": validation_result.is_valid,
        "errors": validation_result.errors,
        "warnings": validation_result.warnings,
        "details": validation_result.details,
        "processing_method": processing_method
    })
    if not validation_result.is_valid:
        raise DocumentProcessingError(f"File validation failed: {'; '.join(validation_result.errors)}")
    documents = processor.process_files(file_paths)
    parsed_documents = []
    for doc in documents:
        if isinstance(doc, ParsedDocument):
            parsed_documents.append(doc)
        elif isinstance(doc, dict):
            parsed_documents.append(ParsedDocument(**doc))
        else:
            parsed_documents.append(ParsedDocument(
                file_path=getattr(doc, 'file_path', '') or '',
                content=getattr(doc, 'content', ''),
                metadata=getattr(doc, 'metadata', None) or DocumentMetadata(
                    file_path=getattr(doc, 'file_path', '') or '',
                    file_size=getattr(doc, 'file_size', 0) or 0,
                    file_type=getattr(doc, 'file_type', '') or '',
                    quality_score=getattr(doc, 'quality_score', 0.0) or 0.0
                ),
                file_type=getattr(doc, 'file_type', '') or '',
                validation_result=getattr(doc, 'validation_result', None) or DocumentParsingValidationResult(is_valid=True, quality_score=0.0)
            ))
    stats = processor.get_processing_stats()
    log_info_event(run, "parse_documents", "File processing completed", {
        "processing_stats": stats,
        "documents_created": len(parsed_documents),
        "processing_method": processing_method
    })
    return parsed_documents, stats


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
    # Thin wrapper: delegate to pure logic, passing all dependencies
    try:
        return parse_documents_logic(
            run,
            state,
            select_processor=_select_processor,
            process_files=_process_files,
            process_links=_process_links,
            validate_processing_results=_validate_processing_results,
            log_info_event=log_info_event,
            log_validation_event=log_validation_event
        )
    except Exception as e:
        error_msg = f"Hybrid document parsing failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        run.mark_failed("parse_documents_error", error_msg)
        raise




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
            content=f"[ENHANCED PLACEHOLDER] URL content from: {link}\n\nThis will be processed with LLM-based web scraping in Week 2.",
            metadata=DocumentMetadata(
                file_path=link,
                file_size=0,
                file_type="url",
                quality_score=0.0
            ),
            file_type="url",
            validation_result=DocumentParsingValidationResult(is_valid=True, quality_score=0.0)
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
        # No validation_result, tables, or file_type in ParsedDocumentSchema
        validation_summary = {
            "overall_valid": len(documents) > 0,
            "document_count": len(documents),
            "valid_documents": len(documents),
            "quality_score": None,
            "total_content_length": sum(len(doc.content) for doc in documents),
            "total_tables": None,
            "file_types": list(set(getattr(doc.metadata, "file_type", "unknown") for doc in documents if doc.metadata)),
            "hybrid_processing": True,
            "llm_enhanced_count": None,
            "llm_fallback_count": None,
            "enhancement_rate": None
        }
    
    # Log validation summary
    log_validation_event(run, "parse_documents", validation_summary)
    
    return validation_summary