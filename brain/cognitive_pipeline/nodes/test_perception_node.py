# brain/cognitive_pipeline/nodes/test_perception_node.py

from unittest.mock import MagicMock
from brain.cognitive_pipeline.logic.perception_logic import parse_documents_logic
from brain.cognitive_pipeline.schema import GraphState

class DummyRun:
    def __init__(self):
        self.failed = False
    def mark_failed(self, code, msg):
        self.failed = True

def make_state(files=None, links=None):
    return GraphState(
        org_id=1,
        user_id=1,
        uploaded_files=files or [],
        links=links or [],
        framework="RICE",
        product_context=""
    )

def test_llm_vs_non_llm():
    run = DummyRun()
    state = make_state(files=["file1.txt"])
    result = parse_documents_logic(
        run,
        state,
        select_processor=lambda: (MagicMock(), "hybrid_llm"),
        process_files=lambda p, f, r, m: ([], {}),
        process_links=lambda r, links: [],
        validate_processing_results=lambda r, d: {"overall_valid": True, "document_count": 0, "valid_documents": 0, "file_types": [], "quality_score": None, "hybrid_processing": True},
        log_info_event=lambda *a, **k: None,
        log_validation_event=lambda *a, **k: None
    )
    assert result.llm_used is True
    assert result.document_validation_summary is not None
    assert result.llm_processing_stats == {}

def test_file_only():
    run = DummyRun()
    state = make_state(files=["file1.txt"])
    result = parse_documents_logic(
        run,
        state,
        select_processor=lambda: (MagicMock(), "traditional_only"),
        process_files=lambda p, f, r, m: ([], {}),
        process_links=lambda r, links: [],
        validate_processing_results=lambda r, d: {"overall_valid": True, "document_count": 0, "valid_documents": 0, "file_types": [], "quality_score": None, "hybrid_processing": False},
        log_info_event=lambda *a, **k: None,
        log_validation_event=lambda *a, **k: None
    )
    assert result.llm_used is False
    assert result.document_validation_summary is not None

def test_links_only():
    run = DummyRun()
    state = make_state(links=["http://example.com"])
    result = parse_documents_logic(
        run,
        state,
        select_processor=lambda: (MagicMock(), "traditional_only"),
        process_files=lambda p, f, r, m: ([], {}),
        process_links=lambda r, links: [],
        validate_processing_results=lambda r, d: {"overall_valid": True, "document_count": 0, "valid_documents": 0, "file_types": [], "quality_score": None, "hybrid_processing": False},
        log_info_event=lambda *a, **k: None,
        log_validation_event=lambda *a, **k: None
    )
    assert result.llm_used is False
    assert result.document_validation_summary is not None
