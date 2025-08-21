# brain/cognitive_pipeline/schema.py

from pydantic import BaseModel
from typing import List, Optional, Literal, Any, Dict


# Business Initiative
class BusinessInitiative(BaseModel):
    """A strategic initiative at the business level."""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    owner: Optional[str] = None
    related_objectives: Optional[List[str]] = None
    # Add more business-initiative-specific fields as needed


class BusinessProfile(BaseModel):
    """
    Structured business profile extracted from documents.
    """
    name: Optional[str] = None
    vision: Optional[str] = None
    strategy: Optional[str] = None
    product_model: Optional[str] = None
    kpis: Optional[List[str]] = None
    initiatives: Optional[List[str]] = None
    goals: Optional[List[str]] = None
    # Add more fields as needed



# Renamed for clarity: PlanForStep → StepStrategy
class StepStrategy(BaseModel):
    step_name: str
    strategy: str
    rationale: Optional[str] = None
    risks: Optional[List[str]] = None
    assumptions: Optional[List[str]] = None
    tools_to_use: Optional[List[str]] = None
    user_feedback: Optional[str] = None
    status: Literal["pending", "approved", "rejected"] = "pending"

# Stub: ExtractedEntity
class ExtractedEntity(BaseModel):
    entity_type: str
    value: Any
    confidence: Optional[float] = None
    # For future traceability:
    source_document_id: Optional[str] = None
    source_text_excerpt: Optional[str] = None


# Business Objective
class BusinessObjective(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    owner: Optional[str] = None
    # Add more fields as needed

# Customer Objective
class CustomerObjective(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    segment: Optional[str] = None
    # Add more fields as needed


# Product KPI
class ProductKPI(BaseModel):
    """Key Performance Indicator specific to product outcomes."""
    id: Optional[str] = None
    name: str
    value: Optional[Any] = None
    unit: Optional[str] = None
    product_id: Optional[str] = None
    description: Optional[str] = None
    # Add more product-specific KPI fields as needed

# Business KPI
class BusinessKPI(BaseModel):
    """Key Performance Indicator for overall business performance."""
    id: Optional[str] = None
    name: str
    value: Optional[Any] = None
    unit: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None
    # Add more business-specific KPI fields as needed

# Product Initiative (central entity)
class ProductInitiative(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    related_objectives: Optional[List[str]] = None

    type: Optional[str] = "product"  # Always specify type
    timeline: Optional[dict] = None
    # Add more fields as needed


class Roadmap(BaseModel):
    """
    Represents a strategic roadmap generated from processed documents and extracted entities.
    Contains the list of product initiatives and their corresponding entities.
    """
    initiatives: List[ProductInitiative] = []


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


# --------------------------------
# Memory Serialization Models
# --------------------------------

class MemoryRecord(BaseModel):
    """Pydantic model for persistent memory record (for API serialization)."""
    id: str
    data: Dict[str, Any]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# --------------------------------
# Document Parsing & Validation
# --------------------------------

# Unified ParsedDocument model for pipeline and persistence
class DocumentMetadata(BaseModel):
    """Metadata for processed documents"""
    file_path: str
    file_size: int
    file_type: str
    quality_score: float  # 0.0 to 1.0
    errors: List[str] = []
    warnings: List[str] = []
    details: dict = {}
    processing_method: str = "traditional"  # traditional, hybrid_llm, llm_fallback

class DocumentParsingValidationResult(BaseModel):
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
	validation_result: DocumentParsingValidationResult


#-----GraphState-----



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
    business_objectives: Optional[List[BusinessObjective]] = None
    customer_objectives: Optional[List[CustomerObjective]] = None
    product_kpis: Optional[List[ProductKPI]] = None
    business_kpis: Optional[List[BusinessKPI]] = None
    extracted_entities: Optional[List[ExtractedEntity]] = None  # After extract_entities_node
    enhanced_product_initiatives: Optional[List[ProductInitiative]] = None  # After enhance_initiatives_node
    business_initiatives: Optional[List[BusinessInitiative]] = None  # After business_understanding_layer
    generated_roadmap: Optional[Roadmap] = None  # After generate_roadmap_node
    validation_results: Optional[List[DocumentParsingValidationResult]] = None

    # Context and metadata
    context: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = {}

    # New fields for cognitive architecture
    business_profile: Optional[BusinessProfile] = None
    step_strategy: Optional[StepStrategy] = None  # Renamed from plan_for_step

    # Track current step in the pipeline
    current_step: Optional[str] = None

    # User goal/intent for dynamic flow control
    intent: Optional[str] = None  # e.g., "generate_full_roadmap", "prioritize_existing"

