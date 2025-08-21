# brain/services/llm_document_processor.py

"""
Hybrid LLM + Traditional Document Processing Service

This service combines traditional document parsing libraries with LLM-based 
content understanding for enhanced document processing capabilities.

Architecture:
1. Traditional parsing (fast, reliable) - Primary
2. LLM post-processing (intelligent understanding) - Enhancement  
3. LLM fallback (complex/corrupted files) - Backup
"""

import logging
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from anthropic import Anthropic
from openai import OpenAI

from .document_processor import DocumentProcessor, DocumentProcessingError
from brain.cognitive_pipeline.schema import ParsedDocument, DocumentMetadata, DocumentParsingValidationResult

logger = logging.getLogger(__name__)


class LLMDocumentProcessor(DocumentProcessor):
    """
    Hybrid document processor combining traditional parsing with LLM intelligence.
    """
    
    def __init__(self, anthropic_api_key: Optional[str] = None, openai_api_key: Optional[str] = None):
        super().__init__()
        self.traditional_processor = DocumentProcessor()
        
        # Initialize LLM clients
        self.anthropic_client = None
        self.openai_client = None
        
        if anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=anthropic_api_key)
        if openai_api_key:
            self.openai_client = OpenAI(api_key=openai_api_key)
        
        # Processing statistics
        self.stats = {
            "traditional_success": 0,
            "traditional_failures": 0,
            "llm_enhancements": 0,
            "llm_fallbacks": 0,
            "total_processing_time_ms": 0.0
        }
    
    def process_files(self, file_paths: List[str]) -> List[ParsedDocument]:
        """
        Process multiple files using hybrid approach.
        
        Strategy:
        1. Try traditional parsing first
        2. Enhance successful results with LLM
        3. Use LLM fallback for failures
        """
        start_time = time.time()
        documents = []
        
        for file_path in file_paths:
            try:
                doc = self._process_single_file(file_path)
                documents.append(doc)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                # Create error document
                error_doc = self._create_error_document(file_path, str(e))
                documents.append(error_doc)
        
        # Update stats
        processing_time = (time.time() - start_time) * 1000
        self.stats["total_processing_time_ms"] += processing_time
        
        return documents
    
    def _process_single_file(self, file_path: str) -> ParsedDocument:
        """Process a single file using hybrid approach."""
        # Step 1: Try traditional parsing
        try:
            traditional_doc = self.traditional_processor.process_files([file_path])[0]
            self.stats["traditional_success"] += 1
            
            # Step 2: Enhance with LLM if available and content is complex
            if self._should_enhance_with_llm(traditional_doc):
                enhanced_doc = self._enhance_with_llm(traditional_doc)
                if enhanced_doc:
                    self.stats["llm_enhancements"] += 1
                    return enhanced_doc
            
            return traditional_doc
            
        except DocumentProcessingError as e:
            self.stats["traditional_failures"] += 1
            logger.warning(f"Traditional parsing failed for {file_path}: {e}")
            
            # Step 3: LLM fallback for failed traditional parsing
            if self._has_llm_capability():
                fallback_doc = self._llm_fallback_processing(file_path)
                if fallback_doc:
                    self.stats["llm_fallbacks"] += 1
                    return fallback_doc
            
            # If all else fails, re-raise the error
            raise
    
    def _should_enhance_with_llm(self, doc: ParsedDocument) -> bool:
        """Determine if document should be enhanced with LLM processing."""
        # Enhance if:
        # 1. Document has complex tables
        # 2. Content suggests strategic/planning information
        # 3. Traditional parsing had low confidence
        
        if not self._has_llm_capability():
            return False
        
        # Check for complex content indicators
        content_lower = doc.content.lower()
        strategic_keywords = [
            'roadmap', 'strategy', 'goals', 'objectives', 'priorities',
            'initiatives', 'requirements', 'features', 'product',
            'stakeholder', 'timeline', 'milestone', 'budget'
        ]
        
        keyword_count = sum(1 for keyword in strategic_keywords if keyword in content_lower)
        
        return (
            len(doc.tables) > 2 or  # Multiple tables
            keyword_count >= 3 or  # Strategic content
            doc.validation_result.quality_score < 0.8  # Low traditional confidence
        )
    
    def _enhance_with_llm(self, doc: ParsedDocument) -> Optional[ParsedDocument]:
        """Enhance traditional parsing results with LLM understanding."""
        try:
            # Prepare content for LLM
            content_summary = self._prepare_content_for_llm(doc)
            
            # Get LLM enhancement
            enhancement = self._get_llm_content_analysis(content_summary, doc.file_type)
            
            if enhancement:
                # Create enhanced document
                enhanced_doc = self._apply_llm_enhancement(doc, enhancement)
                return enhanced_doc
            
        except Exception as e:
            logger.error(f"LLM enhancement failed for {doc.file_path}: {e}")
        
        return None
    
    def _llm_fallback_processing(self, file_path: str) -> Optional[ParsedDocument]:
        """Use LLM as fallback when traditional parsing fails."""
        try:
            # For now, focus on text-based analysis
            # In production, could use vision models for images/PDFs
            
            file_path_obj = Path(file_path)
            
            # Read raw file content if possible
            try:
                if file_path_obj.suffix.lower() == '.txt':
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        raw_content = f.read()
                else:
                    # For non-text files, create a placeholder
                    raw_content = f"[LLM FALLBACK] Unable to parse {file_path_obj.name} with traditional methods."
            except Exception:
                raw_content = f"[LLM FALLBACK] File access failed for {file_path_obj.name}"
            
            # Get LLM analysis
            llm_analysis = self._get_llm_fallback_analysis(raw_content, file_path_obj.suffix)
            
            if llm_analysis:
                return self._create_llm_fallback_document(file_path, raw_content, llm_analysis)
                
        except Exception as e:
            logger.error(f"LLM fallback failed for {file_path}: {e}")
        
        return None
    
    def _prepare_content_for_llm(self, doc: ParsedDocument) -> str:
        """Prepare document content for LLM analysis."""
        content_parts = [
            f"Document: {doc.file_path}",
            f"Type: {doc.file_type}",
            f"Content:\n{doc.content[:2000]}..."  # Limit content size
        ]
        
        if doc.tables:
            content_parts.append(f"\nTables ({len(doc.tables)}):")
            for i, table in enumerate(doc.tables[:3]):  # Limit to first 3 tables
                content_parts.append(f"Table {i+1}: {str(table)[:500]}...")
        
        return "\n".join(content_parts)
    
    def _get_llm_content_analysis(self, content: str, file_type: str) -> Optional[Dict[str, Any]]:
        """Get LLM analysis of document content."""
        prompt = f"""
Analyze this {file_type} document content for product roadmap planning:

{content}

Please provide a JSON analysis with:
1. "content_summary": Brief summary of the document
2. "strategic_elements": List of strategic planning elements found
3. "key_entities": Important entities (features, stakeholders, timelines)
4. "document_structure": Assessment of how well-structured the content is
5. "quality_indicators": Factors affecting document quality
6. "recommendations": Suggestions for better roadmap planning

Respond with valid JSON only.
"""
        
        try:
            if self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                # Handle Anthropic response format with safe attribute access
                response_content = response.content[0]
                content = getattr(response_content, 'text', str(response_content))
                return json.loads(content)
            
            elif self.openai_client:
                response = self.openai_client.chat.completions.create(  # type: ignore
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000
                )
                # OpenAI Python SDK is dynamic; suppress mypy type errors
                message_content = response.choices[0].message.content  # type: ignore
                if message_content is None:
                    raise ValueError("OpenAI returned empty response")
                return json.loads(message_content)
                
        except Exception as e:
            logger.error(f"LLM content analysis failed: {e}")
        
        return None
    
    def _get_llm_fallback_analysis(self, content: str, file_extension: str) -> Optional[Dict[str, Any]]:
        """Get LLM analysis as fallback for failed traditional parsing."""
        prompt = f"""
This {file_extension} file failed traditional parsing. Please extract any useful information for product roadmap planning:

{content[:1500]}

Provide a JSON response with:
1. "extracted_content": Any readable content you can identify
2. "potential_structure": Guessed document structure
3. "confidence_level": Your confidence in the extraction (0.0-1.0)
4. "recommendations": What would help parse this better

Respond with valid JSON only.
"""
        
        try:
            if self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=800,
                    messages=[{"role": "user", "content": prompt}]
                )
                # Handle Anthropic response format with safe attribute access
                response_content = response.content[0]
                content = getattr(response_content, 'text', str(response_content))
                return json.loads(content)
                
        except Exception as e:
            logger.error(f"LLM fallback analysis failed: {e}")
        
        return None
    
    def _apply_llm_enhancement(self, original_doc: ParsedDocument, enhancement: Dict[str, Any]) -> ParsedDocument:
        """Apply LLM enhancement to traditional parsing results."""
        # Create enhanced metadata
        enhanced_metadata = DocumentMetadata(
            file_path=original_doc.metadata.file_path,
            file_size=original_doc.metadata.file_size,
            file_type=original_doc.metadata.file_type,
            quality_score=original_doc.metadata.quality_score if hasattr(original_doc.metadata, "quality_score") else 1.0
        )
        
        # Enhanced validation with LLM insights
        enhanced_validation = DocumentParsingValidationResult(
            is_valid=original_doc.validation_result.is_valid,
            quality_score=min(original_doc.validation_result.quality_score + 0.1, 1.0),  # Slight boost
            errors=original_doc.validation_result.errors,
            warnings=original_doc.validation_result.warnings,
            processing_method="hybrid_llm_enhanced",
            details={
                **original_doc.validation_result.details,
                "llm_enhancement": enhancement,
                "enhancement_applied": True
            }
        )
        
        # Enhanced content (could append LLM insights)
        enhanced_content = original_doc.content
        if enhancement.get("content_summary"):
            enhanced_content += f"\n\n[LLM ANALYSIS SUMMARY]\n{enhancement['content_summary']}"
        
        return ParsedDocument(
            file_path=original_doc.file_path,
            file_type=original_doc.file_type,
            content=enhanced_content,
            tables=original_doc.tables,
            metadata=enhanced_metadata,
            validation_result=enhanced_validation
        )
    
    def _create_llm_fallback_document(self, file_path: str, raw_content: str, analysis: Dict[str, Any]) -> ParsedDocument:
        """Create document from LLM fallback analysis."""
        file_path_obj = Path(file_path)
        
        # Create metadata
        metadata = DocumentMetadata(
            file_path=file_path,
            file_size=file_path_obj.stat().st_size if file_path_obj.exists() else 0,
            file_type=file_path_obj.suffix.lstrip('.').lower(),
            quality_score=analysis.get("confidence_level", 0.3)
        )
        
        # Create validation result
        confidence = analysis.get("confidence_level", 0.3)
        validation = DocumentParsingValidationResult(
            is_valid=confidence > 0.5,
            quality_score=confidence,
            errors=[] if confidence > 0.5 else ["Traditional parsing failed, using LLM fallback"],
            warnings=["LLM fallback used - results may be less reliable"],
            processing_method="llm_fallback",
            details={
                "llm_fallback": True,
                "llm_analysis": analysis,
                "confidence_level": confidence
            }
        )
        
        # Extract content
        content = analysis.get("extracted_content", raw_content)
        
        return ParsedDocument(
            file_path=file_path,
            file_type=metadata.file_type,
            content=content,
            tables=[],
            metadata=metadata,
            validation_result=validation
        )
    
    def _create_error_document(self, file_path: str, error_message: str) -> ParsedDocument:
        """Create error document for completely failed processing."""
        file_path_obj = Path(file_path)
        
        metadata = DocumentMetadata(
            file_path=file_path,
            file_size=file_path_obj.stat().st_size if file_path_obj.exists() else 0,
            file_type=file_path_obj.suffix.lstrip('.').lower(),
            quality_score=0.0
        )
        
        validation = DocumentParsingValidationResult(
            is_valid=False,
            quality_score=0.0,
            errors=[f"Processing failed: {error_message}"],
            warnings=[],
            processing_method="failed",
            details={"processing_failed": True, "error_message": error_message}
        )
        
        return ParsedDocument(
            file_path=file_path,
            file_type=metadata.file_type,
            content=f"[ERROR] Failed to process file: {error_message}",
            tables=[],
            metadata=metadata,
            validation_result=validation
        )
    
    def _has_llm_capability(self) -> bool:
        """Check if LLM processing is available."""
        return self.anthropic_client is not None or self.openai_client is not None
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        total_processed = self.stats["traditional_success"] + self.stats["traditional_failures"]
        
        return {
            **self.stats,
            "total_files_processed": total_processed,
            "traditional_success_rate": self.stats["traditional_success"] / max(total_processed, 1),
            "enhancement_rate": self.stats["llm_enhancements"] / max(self.stats["traditional_success"], 1),
            "fallback_rate": self.stats["llm_fallbacks"] / max(self.stats["traditional_failures"], 1),
            "average_processing_time_ms": self.stats["total_processing_time_ms"] / max(total_processed, 1)
        }
