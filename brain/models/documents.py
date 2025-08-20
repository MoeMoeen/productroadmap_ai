
from pydantic import BaseModel
from typing import List, Any, Dict

class DocumentMetadata(BaseModel):
	"""Metadata for processed documents"""
	file_path: str
	file_size: int
	file_type: str
	page_count: int
	table_count: int
	processing_time_ms: int
	extracted_text_length: int

class ValidationResult(BaseModel):
	"""Validation results for document processing"""
	is_valid: bool
	quality_score: float  # 0.0 to 1.0
	errors: List[str] = []
	warnings: List[str] = []
	details: Dict[str, Any] = {}
	processing_method: str = "traditional"  # traditional, hybrid_llm, llm_fallback

class ParsedDocument(BaseModel):
	"""Processed document with extracted content and metadata"""
	file_path: str
	file_type: str
	content: str
	tables: List[Dict[str, Any]] = []
	metadata: DocumentMetadata
	validation_result: ValidationResult
