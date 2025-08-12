#!/usr/bin/env python
"""
Simple test for Week 1 implementation components.
Tests core functionality without complex Django setup.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_imports():
    """Test that we can import our core modules."""
    print("🔍 Testing imports...")
    
    try:
        # Test basic imports
        from brain.services.document_processor import DocumentProcessor
        from brain.services.validators import FileValidator, ContentValidator
        from brain.langgraph_flow.schema import GraphState, ParsedDocument
        
        print("✅ All imports successful")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_document_processor_basic():
    """Test DocumentProcessor without Django."""
    print("🔍 Testing DocumentProcessor basic functionality...")
    
    try:
        from brain.services.document_processor import DocumentProcessor
        
        # Create a test file
        test_content = "This is a test document.\n\nIt contains some product requirements."
        test_file = "test_basic.txt"
        
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        # Test processor
        processor = DocumentProcessor()
        assert hasattr(processor, 'process_files')
        assert hasattr(processor, 'get_processing_stats')
        
        # Test file processing
        documents = processor.process_files([test_file])
        assert len(documents) == 1
        assert documents[0].content == test_content
        assert documents[0].file_type == "txt"
        
        # Cleanup
        os.remove(test_file)
        
        print("✅ DocumentProcessor test passed")
        return True
        
    except Exception as e:
        print(f"❌ DocumentProcessor test failed: {e}")
        if os.path.exists(test_file):
            os.remove(test_file)
        return False


def test_validators_basic():
    """Test validators without Django."""
    print("🔍 Testing validators basic functionality...")
    
    try:
        from brain.services.validators import FileValidator, ContentValidator
        
        # Test FileValidator
        assert hasattr(FileValidator, 'validate_file_paths')
        assert hasattr(FileValidator, 'validate_uploaded_files')
        
        # Test with non-existent file
        result = FileValidator.validate_file_paths(["nonexistent.txt"])
        assert not result.is_valid
        assert "does not exist" in result.errors[0]
        
        # Test ContentValidator
        assert hasattr(ContentValidator, 'validate_processed_content')
        
        # Test content validation with minimal content
        content_result = ContentValidator.validate_processed_content("Short", "txt")
        assert hasattr(content_result, 'is_valid')
        
        print("✅ Validators test passed")
        return True
        
    except Exception as e:
        print(f"❌ Validators test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_schema_models():
    """Test Pydantic schema models."""
    print("🔍 Testing schema models...")
    
    try:
        from brain.langgraph_flow.schema import GraphState, ParsedDocument, DocumentMetadata, ValidationResult
        
        # Test ValidationResult
        validation = ValidationResult(
            is_valid=True,
            quality_score=0.9,
            errors=[],
            warnings=["Test warning"]
        )
        assert validation.is_valid
        assert validation.quality_score == 0.9
        
        # Test DocumentMetadata
        metadata = DocumentMetadata(
            file_path="test.txt",
            file_size=100,
            file_type="txt",
            page_count=1,
            table_count=0,
            processing_time_ms=50,
            extracted_text_length=100
        )
        assert metadata.file_type == "txt"
        
        # Test ParsedDocument
        doc = ParsedDocument(
            file_path="test.txt",
            file_type="txt",
            content="Test content",
            tables=[],
            metadata=metadata,
            validation_result=validation
        )
        assert doc.content == "Test content"
        
        # Test GraphState
        state = GraphState(
            org_id=1,
            user_id=1,
            uploaded_files=["test.txt"],
            links=["https://example.com"],
            framework="RICE"
        )
        assert state.framework == "RICE"
        assert len(state.uploaded_files) == 1
        
        print("✅ Schema models test passed")
        return True
        
    except Exception as e:
        print(f"❌ Schema models test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_basic_tests():
    """Run basic tests without Django setup."""
    print("🚀 Running Basic Week 1 Tests...\n")
    
    tests = [
        test_imports,
        test_document_processor_basic,
        test_validators_basic,
        test_schema_models
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Empty line between tests
    
    print("📊 Basic Test Results:")
    print(f"   Passed: {passed}/{total}")
    print(f"   Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All basic tests passed! Core components are working.")
        print("\n📋 Next Steps:")
        print("   1. Install dependencies: pip install langgraph pdfplumber python-docx openpyxl")
        print("   2. Run full Django tests with: python test_week1_implementation.py")
        print("   3. Test API endpoints")
        print("   4. Proceed to Week 2")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please fix core issues first.")
    
    return passed == total


if __name__ == "__main__":
    success = run_basic_tests()
    sys.exit(0 if success else 1)
