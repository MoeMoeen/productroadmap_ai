# Week 1: Perception Layer Implementation Plan

**Date:** August 12, 2025  
**Status:** ✅ COMPLETED - Hybrid LLM + Traditional Architecture Implemented  
**Target:** Robust Document Processing with Quality Validation

## Implementation Overview

### **Goal**
Build the **Perception Layer** - the foundation of our cognitive AI system that processes and validates input documents (PDF, DOCX, XLSX) to extract structured information for roadmap generation.

### **Architecture Context**
```
Layer 9: Learning Loop (Future)
Layer 8: Execution Monitor (Future) 
Layer 7: Tool/Action Executor (Future)
Layer 6: Reasoning Engine (Future)
Layer 5: Planner (Future)
Layer 4: Goal & Intent Manager (Future)
Layer 3: World Model (Future)
Layer 2: Memory Layer (Future)
Layer 1: Perception Layer 🎯 CURRENT FOCUS
------------------------------------
Foundation: Observability System ✅ COMPLETE
```

## **Week 1 Deliverables**

### 1. **Document Processing Service** 
**File**: `brain/services/document_processor.py`
- **PDF Processing**: Extract text, tables, metadata using pdfplumber
- **DOCX Processing**: Extract structured content using python-docx
- **XLSX Processing**: Parse spreadsheets with openpyxl
- **Unified Output**: `ParsedDocument` schema with source metadata
- **Error Handling**: Comprehensive validation and error capture

### 2. **Perception Layer Node**
**File**: `brain/langgraph_flow/nodes/perception.py`
- **Integration**: Use telemetry decorators for full observability
- **Multi-Document**: Process multiple files in single run
- **Quality Gates**: File validation, format checking, content sanity
- **Output Schema**: Structured `PerceptionOutput` with validation

### 3. **Enhanced Schema Models**
**File**: `brain/langgraph_flow/schema.py`
- **ParsedDocument**: Rich document representation with metadata
- **PerceptionOutput**: Standardized perception layer output
- **DocumentMetadata**: Source tracking, file info, processing stats
- **ValidationResult**: Quality check results with error details

### 4. **AI Job API Integration**
**Files**: `brain/views.py`, `brain/serializers.py`
- **Start Job Endpoint**: `POST /api/brain/start_job/` with files + framework selection
- **Status Endpoint**: `GET /api/brain/jobs/{run_id}/` for job status
- **Trace Endpoint**: `GET /api/brain/jobs/{run_id}/trace/` for full event trace
- **Storage**: Secure file handling in media directory
- **LangGraph Integration**: Launch complete AI workflow (sync initially)
- **Status Tracking**: Real-time processing status via telemetry

### 5. **Quality Validation Framework**
**File**: `brain/services/validators.py`
- **File Format Validation**: MIME type checking, file integrity
- **Content Validation**: Text extraction success, table detection
- **Schema Validation**: Pydantic models with comprehensive error messages
- **Auto-Repair Logic**: Simple fixes for common parsing issues

## **Technical Implementation**

### **Core Components**

#### **1. Document Processor Architecture**
```python
# brain/services/document_processor.py
class DocumentProcessor:
    def process_files(self, file_paths: List[str]) -> List[ParsedDocument]:
        """Process multiple files with error handling"""
        
    def process_pdf(self, file_path: str) -> ParsedDocument:
        """Extract text, tables, metadata from PDF"""
        
    def process_docx(self, file_path: str) -> ParsedDocument:
        """Extract structured content from Word document"""
        
    def process_xlsx(self, file_path: str) -> ParsedDocument:
        """Parse spreadsheet data with sheet detection"""
```

#### **2. Perception Node Integration**
```python
# brain/langgraph_flow/nodes/perception.py
@log_node_io(node_name="parse_documents")
def parse_documents_node(run: BrainRun, state: GraphState) -> GraphState:
    """
    Layer 1: Document parsing with quality validation
    Input: File paths + framework from GraphState
    Output: Updated GraphState with parsed_documents
    """
```

#### **3. Schema-First Design**
```python
# brain/langgraph_flow/schema.py
class GraphState(BaseModel):
    org_id: int
    uploaded_files: List[str] = []
    links: List[str] = []
    framework: str = "RICE"
    parsed_documents: Optional[List[ParsedDocument]] = None
    # Future nodes will add their outputs here

class ParsedDocument(BaseModel):
    file_path: str
    file_type: str
    content: str
    tables: Optional[List[dict]] = None
    metadata: DocumentMetadata
    validation_result: ValidationResult

class PerceptionOutput(BaseModel):
    documents: List[ParsedDocument]
    processing_stats: dict
    quality_score: float
    validation_summary: dict
```

### **Integration Points**

#### **AI Job Flow**
1. **API Request**: `POST /api/brain/start_job/` with files + framework selection
2. **BrainRun Creation**: Status PENDING with job metadata in database
3. **LangGraph Launch**: Start complete AI workflow (sync initially, async later)
4. **Node Execution**: `parse_documents` → (future: extract_entities → enhance_initiatives → generate_roadmap)
5. **Status Updates**: Real-time progress via RunEvent system
6. **Result Access**: Job status and trace available via API endpoints

#### **Enhanced Integration Points**
- **Complete Job API**: Start, status, and trace endpoints
- **Framework Selection**: RICE/WSJF/MoSCoW from job creation
- **GraphState Flow**: State management between cognitive layers
- **Sync → Async Ready**: Easy transition to Celery background jobs

#### **Observability Integration**
- **Every Step Logged**: File processing, validation, errors
- **Performance Metrics**: Processing time per document type
- **Quality Metrics**: Extraction success rates, validation results
- **Debug Information**: Full processing trace for troubleshooting

## **Success Criteria**

### **Functional Requirements**
- ✅ **Multi-Format Support**: PDF, DOCX, XLSX processing
- ✅ **Quality Validation**: Comprehensive error handling + reporting
- ✅ **Observability**: Complete processing audit trail
- ✅ **AI Job API**: Start job → status → trace workflow
- ✅ **Framework Selection**: Support RICE/WSJF/MoSCoW from job creation
- ✅ **GraphState Management**: Proper state flow between cognitive layers
- ✅ **Error Recovery**: Graceful handling of corrupt/invalid files

### **Performance Targets**
- **PDF Processing**: <30 seconds per 10MB file
- **DOCX Processing**: <10 seconds per 5MB file  
- **XLSX Processing**: <15 seconds per 100 sheet file
- **Quality Score**: >95% successful processing rate
- **Error Handling**: <5% silent failures (everything logged)

### **Quality Gates**
- **Schema Validation**: 100% of outputs conform to Pydantic models
- **File Format Support**: Handle 90% of common business document formats
- **Error Transparency**: Every failure has actionable error message
- **Regression Testing**: Golden file tests for each document type

## **Implementation Steps**

### **Step 1: Document Processing Service** (Day 1-2)
1. Create `brain/services/document_processor.py`
2. Implement PDF extraction with pdfplumber
3. Implement DOCX extraction with python-docx
4. Implement XLSX parsing with openpyxl
5. Add comprehensive error handling + logging

### **Step 2: Enhanced Schema & GraphState** (Day 2)
1. Extend `brain/langgraph_flow/schema.py`
2. Add enhanced `GraphState` with framework selection
3. Add `ParsedDocument`, `DocumentMetadata`, `ValidationResult` models
4. Create validation utilities and error handling schemas

### **Step 3: Perception Node & LangGraph Integration** (Day 3)
1. Implement `brain/langgraph_flow/nodes/perception.py` (parse_documents_node)
2. Integrate with telemetry system using existing decorators
3. Add quality validation gates and error handling
4. Create basic LangGraph workflow with single node
5. Test with multiple document types

### **Step 4: AI Job API Implementation** (Day 4)
1. Implement `start_job` endpoint in `brain/views.py`
2. Add job status and trace endpoints
3. Update `brain/serializers.py` for job requests and file handling
4. Integrate LangGraph execution with API (sync execution)
5. Test complete workflow: start job → process documents → get status/trace

### **Step 5: Testing & Validation** (Day 5)
1. Create test document suite (PDF, DOCX, XLSX)
2. Build comprehensive test cases
3. Performance testing + optimization
4. Integration testing with observability system

## **File Structure After Week 1**
```
brain/
├── services/
│   ├── __init__.py
│   ├── document_processor.py    # NEW: Core document processing
│   └── validators.py            # NEW: Quality validation logic
├── langgraph_flow/
│   ├── graph.py                 # ENHANCED: Basic workflow with perception node
│   ├── nodes/
│   │   ├── perception.py        # NEW: parse_documents_node implementation
│   │   └── ...
│   └── schema.py                # ENHANCED: GraphState + document schemas
├── models.py                    # ✅ Complete (observability)
├── views.py                     # ENHANCED: AI job API endpoints
├── serializers.py               # ENHANCED: Job + file handling
└── utils/
    └── telemetry.py             # ✅ Complete
```

## **Dependencies & Prerequisites**

### **Python Packages** (Already Installed ✅)
- `pdfplumber==0.11.7` - PDF text + table extraction
- `python-docx==1.2.0` - Word document processing  
- `openpyxl==3.1.5` - Excel spreadsheet parsing
- `pillow==11.3.0` - Image processing support

### **Django Configuration**
- File upload settings in `settings.py`
- Media directory configuration
- File size limits and security

### **Testing Requirements**
- Sample documents for each format
- Golden file test suite
- Performance benchmarking

## **Next Week Preview: Memory Layer**
After completing the Perception Layer, Week 2 will focus on:
- **Memory Layer**: Context retention across document chunks
- **World Model**: Organization strategy comprehension using existing Django models
- **API Completion**: Any missing org-scoped endpoints

---

**Ready to begin Week 1 implementation! The observability foundation is solid and the architecture is well-defined.** 🚀
