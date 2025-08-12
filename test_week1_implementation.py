# test_week1_implementation.py

"""
Test script for Week 1 Perception Layer implementation.

This script validates that all components work together:
1. Document processing service
2. Validation framework  
3. Enhanced schema models
4. Perception node with telemetry
5. API endpoints

Run this after completing Week 1 implementation.
"""

import os
import sys
import django
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Now import Django-dependent modules
from brain.models import BrainRun
from brain.services.document_processor import DocumentProcessor
from brain.services.validators import FileValidator, ContentValidator
from brain.langgraph_flow.week1_workflow import run_parse_documents_enhanced, create_ai_job_workflow


def test_document_processor():
    """Test the DocumentProcessor service."""
    print("🔍 Testing DocumentProcessor...")
    
    # Test with a simple text file
    test_content = "This is a test document for product roadmap.\n\nFeatures:\n- Authentication\n- Dashboard\n- Analytics"
    test_file = "test_document.txt"
    
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    try:
        processor = DocumentProcessor()
        documents = processor.process_files([test_file])
        
        assert len(documents) == 1
        assert documents[0].content == test_content
        assert documents[0].file_type == "txt"
        assert documents[0].validation_result.is_valid
        
        print("✅ DocumentProcessor test passed")
        return True
        
    except Exception as e:
        print(f"❌ DocumentProcessor test failed: {e}")
        return False
        
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_validators():
    """Test the validation framework."""
    print("🔍 Testing Validators...")
    
    try:
        # Test file path validation
        result = FileValidator.validate_file_paths(["nonexistent.txt"])
        assert not result.is_valid
        assert "does not exist" in result.errors[0]
        
        # Test content validation 
        content_result = ContentValidator.validate_content("Short")
        assert content_result.warnings  # Should warn about short content
        
        print("✅ Validators test passed")
        return True
        
    except Exception as e:
        print(f"❌ Validators test failed: {e}")
        return False


def test_enhanced_workflow():
    """Test the enhanced workflow with telemetry."""
    print("🔍 Testing Enhanced Workflow...")
    
    # Create test file
    test_content = """Product Requirements Document

## Core Features
1. User Authentication System
   - Email/password login
   - OAuth integration
   - Multi-factor authentication

2. Dashboard Analytics
   - Real-time metrics
   - Custom reports
   - Data visualization

## Performance Requirements
- Page load time < 2 seconds
- 99.9% uptime
- Support 10,000 concurrent users

## Technical Stack
- Frontend: React.js
- Backend: Django
- Database: PostgreSQL
- Cache: Redis
"""
    
    test_file = "test_prd.txt"
    
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    try:
        # Create a test organization and user if needed
        from accounts.models import Organization  
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Get or create test organization and user
        org, _ = Organization.objects.get_or_create(
            name="Test Organization",
            defaults={"slug": "test-org"}
        )
        
        user, _ = User.objects.get_or_create(
            username="testuser",
            defaults={"email": "test@example.com"}
        )
        
        # Create a BrainRun
        run = BrainRun.objects.create(
            status='running',
            organization=org,
            created_by=user,
            meta={'test': True}
        )
        
        # Run enhanced workflow
        result = run_parse_documents_enhanced(
            run=run,
            uploaded_files=[test_file],
            links=["https://example.com/api-docs"],
            framework="RICE",
            product_context="SaaS product for small businesses"
        )
        
        # Validate results
        assert 'parsed_documents' in result
        assert len(result['parsed_documents']) == 2  # 1 file + 1 URL placeholder
        
        # Check that file was processed correctly
        file_doc = next(doc for doc in result['parsed_documents'] if doc['file_type'] == 'txt')
        assert file_doc['validation_result']['is_valid']
        assert len(file_doc['content']) > 100
        
        # Check that URL placeholder was created
        url_doc = next(doc for doc in result['parsed_documents'] if doc['file_type'] == 'url')
        assert not url_doc['validation_result']['is_valid']  # Placeholder
        assert "PLACEHOLDER" in url_doc['content']
        
        print("✅ Enhanced Workflow test passed")
        print(f"   - Processed {len(result['parsed_documents'])} documents")
        print(f"   - Run ID: {run.id}")
        print(f"   - Status: {run.status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_schema_models():
    """Test the enhanced schema models."""
    print("🔍 Testing Schema Models...")
    
    try:
        # Test GraphState creation
        state = create_ai_job_workflow(
            uploaded_files=["test.pdf"],
            links=["https://example.com"],
            framework="WSJF",
            product_context="Mobile app for fitness tracking"
        )
        
        assert state.framework == "WSJF"
        assert len(state.uploaded_files) == 1
        assert len(state.links) == 1
        assert state.product_context == "Mobile app for fitness tracking"
        assert state.parsed_documents == []  # Initially empty
        
        print("✅ Schema Models test passed")
        return True
        
    except Exception as e:
        print(f"❌ Schema Models test failed: {e}")
        return False


def run_all_tests():
    """Run all Week 1 tests."""
    print("🚀 Running Week 1 Perception Layer Tests...\n")
    
    tests = [
        test_document_processor,
        test_validators,
        test_schema_models,
        test_enhanced_workflow
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Empty line between tests
    
    print("📊 Test Results:")
    print(f"   Passed: {passed}/{total}")
    print(f"   Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All tests passed! Week 1 implementation is ready.")
        print("\n📋 Next Steps:")
        print("   1. Install missing dependencies: pip install langgraph pdfplumber python-docx openpyxl")
        print("   2. Run migrations: python manage.py migrate")
        print("   3. Test API endpoints with curl or Postman")
        print("   4. Proceed to Week 2: Comprehension Layer")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please fix issues before proceeding.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
