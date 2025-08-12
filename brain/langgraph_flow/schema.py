from pydantic import BaseModel
from typing import List, Optional, Any
from langchain_core.documents import Document


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
    State container that flows between LangGraph nodes.
    """
    input: IngestionInput
    raw_docs: Optional[List[Document]] = None  # After parse_documents_node
    extracted_entities: Optional[dict] = None  # After extract_entities_node
    enhanced_initiatives: Optional[List[dict]] = None  # After enhance_initiatives_node
    roadmap: Optional[dict] = None  # After generate_roadmap_node