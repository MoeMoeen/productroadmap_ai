

from pydantic import BaseModel
from typing import List, Optional, Any, Dict

from pydantic import BaseModel
from typing import List, Optional, Any, Dict, Literal
from langchain_core.documents import Document
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

# KPI
class KPI(BaseModel):
    id: Optional[str] = None
    name: str
    value: Optional[Any] = None
    unit: Optional[str] = None
    # Add more fields as needed

# Product Initiative (central entity)
class ProductInitiative(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    related_objectives: Optional[List[str]] = None
    type: Optional[str] = "product"  # Always specify type
    # Add more fields as needed


# Roadmap
class Roadmap(BaseModel):
    product_initiatives: List[ProductInitiative]
    timeline: Optional[Dict[str, Any]] = None
    # Add more fields as needed

# Stub: ValidationResult
class ValidationResult(BaseModel):
    step: str
    passed: bool
    issues: Optional[List[str]] = None
    severity: Optional[str] = None  # e.g., "low", "medium", "critical"
    score: Optional[float] = None   # 0 to 1 confidence level


# Pydantic-compatible ParsedDocument for pipeline use
class ParsedDocumentSchema(BaseModel):
    id: Optional[str] = None
    content: str
    metadata: Optional[Dict[str, Any]] = None
    doc_type: Optional[str] = None
    # Add more fields as needed


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
    parsed_documents: Optional[List[ParsedDocumentSchema]] = None  # After parse_documents_node
    business_objectives: Optional[List[BusinessObjective]] = None
    customer_objectives: Optional[List[CustomerObjective]] = None
    kpis: Optional[List[KPI]] = None
    extracted_entities: Optional[List[ExtractedEntity]] = None  # After extract_entities_node
    enhanced_product_initiatives: Optional[List[ProductInitiative]] = None  # After enhance_initiatives_node
    generated_roadmap: Optional[Roadmap] = None  # After generate_roadmap_node
    validation_results: Optional[List[ValidationResult]] = None
    
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