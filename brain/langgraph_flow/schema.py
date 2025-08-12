from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from langchain_core.documents import Document


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


class ParsedDocument(BaseModel):
    """Processed document with extracted content and metadata"""
    file_path: str
    file_type: str
    content: str
    tables: List[Dict[str, Any]] = []
    metadata: DocumentMetadata
    validation_result: ValidationResult


class IngestionInput(BaseModel):
    """
    Represents the input data to the AI brain pipeline before parsing.
    Can include file paths and/or URLs to online docs.
    """
    org_id: int
    user_id: int
    file_paths: Optional[List[str]] = None
    links: Optional[List[str]] = None


class NodeOutput(BaseModel):
    """
    Standard structure for all LangGraph node outputs.
    This way, every node returns consistent metadata + payload.
    """
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None


class GraphState(BaseModel):
    """
    Enhanced state container that flows between LangGraph nodes.
    """
    # Job configuration
    org_id: int
    user_id: int
    uploaded_files: List[str] = []
    links: List[str] = []
    framework: str = "RICE"  # RICE, WSJF, MoSCoW
    product_context: str = ""
    
    # Node outputs
    parsed_documents: Optional[List[ParsedDocument]] = None  # After parse_documents_node
    extracted_entities: Optional[Dict[str, Any]] = None  # After extract_entities_node
    enhanced_initiatives: Optional[List[Dict[str, Any]]] = None  # After enhance_initiatives_node
    generated_roadmap: Optional[Dict[str, Any]] = None  # After generate_roadmap_node
    
    # Context and metadata
    context: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = {}
    
    # Legacy support for existing code
    input: Optional[IngestionInput] = None
    raw_docs: Optional[List[Document]] = None