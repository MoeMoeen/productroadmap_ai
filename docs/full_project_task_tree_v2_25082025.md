
# PROJECT_TASKS.md — Full Task Tree (Numbered Index)

---

## 1. ACCOUNTS APP

### 1.1 Implemented
- 1.1.1 Organization model with fields like vision, departments, headcount  
- 1.1.2 User model extending AbstractUser and linked to Organization  
- 1.1.3 Admin model registration is working  

### 1.2 Gaps / Recommendations
- 1.2.1 Create serializers.py (OrganizationSerializer, UserSerializer)  
- 1.2.2 Create views.py with OrganizationViewSet and optional UserViewSet  
- 1.2.3 Create urls.py for /api/accounts/  
- 1.2.4 Add permissions.py for org-based access (e.g., IsOrgMember)  
- 1.2.5 Add get_user_org() utility for consistent org scoping  
- 1.2.6 Add tests.py with tests for user/org creation, auth, and org scoping  
- 1.2.7 Improve admin.py with filters and inlines  

---

## 2. ROADMAP APP

### 2.1 Implemented
- 2.1.1 Relational models: ProductInitiative, ProductKPI, CustomerObjective, BusinessObjective, Roadmap  
- 2.1.2 Through-models with metadata (confidence, weight, priority)  
- 2.1.3 Admin interface with inlines and filters  
- 2.1.4 DRF serializers (support for through-models, nested reads)  
- 2.1.5 ViewSets: ProductInitiative, ProductKPI, ProductInitiativeKPI  

### 2.2 Gaps / Recommendations
- 2.2.1 Add ViewSets for:
  - 2.2.1.1 CustomerObjective  
  - 2.2.1.2 BusinessObjective  
  - 2.2.1.3 Roadmap  
  - 2.2.1.4 RoadmapEntry  
- 2.2.2 Enforce request.user.organization filtering in all ViewSets  
- 2.2.3 Add filtering/search (status, segment, date, priority, etc.)  
- 2.2.4 Add summary serializers for lightweight responses  
- 2.2.5 Add unit tests for model creation, update, through-model connections  

---

## 3. BRAIN APP (LangGraph Cognitive Pipeline)

### 3.1 Implemented
- 3.1.1 LangGraph DAG in graph.py  
- 3.1.2 Pydantic schema: GraphState, ParsedDocument, ExtractedEntity  
- 3.1.3 Nodes:
  - 3.1.3.1 perception_node.py  
  - 3.1.3.2 extract_entities_node.py  
- 3.1.4 Layer: world_model_layer.py  
- 3.1.5 Logic:
  - 3.1.5.1 entity_extraction_logic.py  
  - 3.1.5.2 perception_logic.py  
- 3.1.6 LLM utils: document_processor.py, llm_document_processor.py, llm_utils.py  
- 3.1.7 DRF views: BrainRunViewSet, BrainRunEventViewSet  
- 3.1.8 Prompt templates grouped by function  

### 3.2 Gaps / Recommendations

#### 3.2.1 Nodes to Implement
- 3.2.1.1 enhance_initiatives_node.py  
- 3.2.1.2 generate_product_initiatives_node.py  
- 3.2.1.3 generate_roadmap_node.py  
- 3.2.1.4 validate_alignment_node.py  
- 3.2.1.5 present_plan_to_user_node.py  
- 3.2.1.6 save_outputs_node.py  
- 3.2.1.7 quality_gate_node.py  
- 3.2.1.8 capture_feedback_loop_node.py  
- 3.2.1.9 output_node.py  

#### 3.2.2 Layers to Flesh Out
- 3.2.2.1 memory_layer.py  
- 3.2.2.2 planner_layer.py  
- 3.2.2.3 reasoning_layer.py  
- 3.2.2.4 execution_layer.py  
- 3.2.2.5 learning_layer.py  
- 3.2.2.6 monitor_layer.py  
- 3.2.2.7 deliberation_layer.py  
- 3.2.2.8 goal_manager_layer.py  
- 3.2.2.9 initiative_layer.py  
- 3.2.2.10 product_initiative_layer.py  
- 3.2.2.11 business_understanding_layer.py  
- 3.2.2.12 perception_layer.py  
- 3.2.2.13 entity_extraction_layer.py  

#### 3.2.3 API Integration
- 3.2.3.1 /start-job/ endpoint  
- 3.2.3.2 /status/ endpoint  
- 3.2.3.3 /result/ endpoint  
- 3.2.3.4 /feedback/ endpoint  
- 3.2.3.5 Add ingestion config parsing and validation  
- 3.2.3.6 Upload handling (PDF, DOCX, XLSX)  
- 3.2.3.7 Integrate LangGraph runner with BrainRun  
- 3.2.3.8 Add org/user permission enforcement  

#### 3.2.4 Observability
- 3.2.4.1 Log BrainRun events step-by-step  
- 3.2.4.2 Emit telemetry per node  
- 3.2.4.3 Export GraphState changes to JSONL for debugging  

#### 3.2.5 Testing
- 3.2.5.1 Unit tests per node (perception, extraction, world model)  
- 3.2.5.2 Integration test: perception → extraction → world model  
- 3.2.5.3 End-to-end test: upload → LLM → roadmap  
- 3.2.5.4 Regression tests for enrichment, alignment, deduplication  

---

## 4. PROJECT-WIDE INFRASTRUCTURE

### 4.1 Implemented
- 4.1.1 Models use organization scoping
- 4.1.2 Admin working across apps

### 4.2 Gaps / Recommendations

#### 4.2.1 Auth & Security
- 4.2.1.1 Add JWT or session-based authentication  
- 4.2.1.2 Enforce org scoping in all views, queries, serializers  

#### 4.2.2 Async + Storage
- 4.2.2.1 Add Celery + Redis for async pipeline jobs  
- 4.2.2.2 Add S3 or MinIO for uploaded files  

#### 4.2.3 DevOps + Logging
- 4.2.3.1 Add central logging (structured logs, file JSONL dumps)  
- 4.2.3.2 Add GitHub Actions for CI/CD  
- 4.2.3.3 Dockerize local + staging environments  

#### 4.2.4 Documentation
- 4.2.4.1 Add DRF Spectacular tags per ViewSet  
- 4.2.4.2 Expand README and internal docstrings  
