# README.md

Project Overview
Vision & Scope
This project is a multi-tenant AI-powered product roadmap management platform designed for product leaders, strategists, and executives.
Its goal is to bridge the gap between business strategy documents (e.g., business plans, product strategies, competitor analysis) and actionable, prioritized product roadmaps.
At the core is the AI Brain, which can:
Parse business and product strategy documents (uploaded files or URLs).
Extract existing business objectives, business initiatives, product initiatives, and customer objectives.
Suggest improvements or replacements for weak/misaligned initiatives.
Generate new initiatives for missing areas.
Build multiple roadmap versions based on different prioritization frameworks (e.g., RICE, WSJF, MoSCoW).
Reprioritize existing roadmaps using new frameworks.
Support human-in-the-loop feedback at each AI pipeline step.
This makes the system both a strategy extraction engine and a product roadmap generator.

Key Capabilities
Document Ingestion
Accepts multiple file types (PDF, DOCX, XLSX) and URLs (Google Docs, Confluence, Notion).
Entity Extraction
Identifies:
Business Objectives (long-term goals)
Business Initiatives (company-level strategic actions)
Product Initiatives (specific product-related actions)
Customer Objectives (desired customer outcomes)
Initiative Enhancement
Improves and validates existing initiatives, adds new ones where gaps exist.
Roadmap Generation
Links initiatives logically:
Product Initiatives → Customer Objectives (direct)
Product Initiatives → Business Objectives (via Business Initiatives) Creates prioritized roadmap entries with:
is_prioritized flag
prioritization_method field
Multiple Framework Support
Generates or converts roadmaps across multiple prioritization frameworks.
Human-in-the-Loop Feedback
At each AI pipeline node, the user can approve or reject outputs and request refinements.

Current Status
Backend: Django + Django REST Framework + PostgreSQL

AI Brain: LangChain + LangGraph (experimental), Pydantic for schema definitions
Core Models: Fully defined and migrated for all objectives, initiatives, KPIs, and roadmap entries

API: CRUD endpoints for all core entities

AI Flow: Minimal LangGraph pipeline skeleton implemented

Future Scope
Integrate RAG for industry-specific data enrichment
Add competitor intelligence scraping
Build advanced prioritization algorithms
Full UI for interactive AI-human roadmap creation
SaaS multi-tenant deployment with org-based permissions
Do you want me to now move to Step 2: Architecture at a Glance?
That’s where I’ll show the backend–AI–database connections in one diagram and text form.



-------------------------------------------


Architecture at a Glance
┌───────────────┐ REST/JSON ┌───────────────┐ │ Frontend │ <────────────────────> │ Django/DRF │ │(Swagger/UI/FE)│ │ ViewSets/URL │ └──────┬────────┘ └──────┬────────┘ │ serializers <-> models │ │ │ ORM │ ▼ │ ┌───────────────┐ │ │ PostgreSQL │ │ │ (multi-tenant│ │ │ org scoping)│ │ └──────┬────────┘ │ │ │ async/sync calls │ │ │ ▼ ▼ ┌────────────────┐ tools + graph ┌───────────────┐ │ AI “Brain” │ <────────────────────────> │ LangGraph │ │ (brain app) │ (nodes: parse/extract/ │ (State, │ │ utils & nodes │ enhance/generate) │ Nodes, Edges)│ └──────┬─────────┘ └──────┬────────┘ │ LLMs, parsing, RAG │ │ │ ▼ ▼ ┌───────────────┐ embeddings / retrieval ┌───────────────┐ │ File/URL │ ─────────────────────────────> │ Vector Store │ │ Ingestion │ (optional, later) │ (e.g., pgvector│ │ (pdf/doc/xls)│ │ or FAISS) │ └───────────────┘ └───────────────┘ (Optionals) - Celery/Redis for long-running AI jobs - S3-compatible storage for original files 
Main pieces
Django + DRF
ViewSets + Routers expose CRUD APIs.
Serializers control I/O shape and validation.
Models capture your domain (Objectives, Initiatives, KPIs, Roadmaps, RoadmapEntry w/ through models).
Permissions + org scoping to keep tenants separated.
PostgreSQL
System of record for all entities.
Multi-tenant via Organization FK on core rows.
(Later) pgvector if we keep embeddings in Postgres.
AI “Brain” (Django app brain/)
LangGraph state machine orchestrates nodes:
parse_documents → extract_entities → enhance_initiatives → generate_roadmap → output.
LangChain tools (doc loaders, LLM prompts, retrievers).
RAG (optional) for enriching with industry/competitor info.
Ingestion
File upload (PDF/DOCX/XLSX) + URL fetchers (Google Docs, Confluence, Notion links where permitted).
Parsers produce normalized text chunks (tables preserved when possible).
Optional workers
Celery + Redis to run AI graphs asynchronously and stream progress.
S3/MinIO for storing originals; DB stores derived/structured outputs.
High-level request flows
CRUD API flow (e.g., ProductInitiative list):
Client → /api/... → DRF ViewSet → Serializer → ORM (prefetch/select_related) → Serializer → JSON
AI job flow (e.g., “Build roadmap from docs”):
Client → /api/brain/start_job → enqueue/trigger graph → parse → extract → enhance/create → generate → persist in DB → job status + results endpoint
Where code lives (bird’s-eye)
backend/ config/ # Django project settings + root urls accounts/ # Users, Organization, auth common/ # TimeStampedModel, ContributionType, shared utils roadmap/ # Models, serializers, viewsets, admin for roadmapping brain/ langgraph_flow/ state/ # Graph state & Pydantic schemas nodes/ # parse_documents.py, extract_entities.py, ... graph.py # Wiring nodes + edges utils/ # parsers, loaders, scraping/cleaning helpers 


------------------------------------------------

Repository Structure (folders & files) with a clean tree and what lives where.

productroadmap_ai/
├─ README.md
├─ manage.py
├─ .env.example
├─ requirements.txt
├─ pyproject.toml            # (optional; if you use poetry/uv)
├─ config/                   # Django project (settings & root urls)
│  ├─ init.py
│  ├─ settings.py
│  ├─ urls.py                # includes app urls (roadmap, brain, swagger)
│  ├─ wsgi.py
│  └─ asgi.py
│
├─ accounts/                 # auth, organizations, users
│  ├─ init.py
│  ├─ apps.py
│  ├─ admin.py
│  ├─ models.py              # Organization, User (with org FK), etc.
│  ├─ serializers.py         # (if exposing user/org APIs)
│  ├─ views.py               # (optional DRF views for accounts)
│  ├─ urls.py                # (optional)
│  └─ migrations/
│
├─ common/                   # shared stuff across apps
│  ├─ init.py
│  ├─ models.py              # TimeStampedModel, ContributionType, mixins
│  ├─ utils.py               # shared helpers
│  └─ admin.py
│
├─ roadmap/                  # product/biz/customer/roadmap domain
│  ├─ init.py
│  ├─ apps.py
│  ├─ admin.py               # inlines for through models, RoadmapEntry inline, etc.
│  ├─ models.py              # ProductInitiative, KPIs, Objectives, Roadmap, RoadmapEntry, through models
│  ├─ serializers.py         # ProductInitiativeSerializer, *Summary serializers, through serializers
│  ├─ views.py               # DRF ViewSets (ProductInitiativeViewSet, ProductInitiativeKPIViewSet, …)
│  ├─ urls.py                # DRF router registrations for roadmap API
│  ├─ pagination.py          # (optional)
│  ├─ permissions.py         # (optional org scoping/custom perms)
│  ├─ filters.py             # (optional django-filters)
│  └─ migrations/
│
├─ brain/                    # AI orchestration (LangGraph + utils)
│  ├─ init.py
│  ├─ apps.py
│  ├─ urls.py                # endpoints to launch/inspect jobs
│  ├─ views.py               # thin API to start/monitor AI flows
│  ├─ admin.py               # (optional: list runs/jobs)
│  │
│  ├─ langgraph_flow/
│  │  ├─ init.py
│  │  ├─ graph.py            # builds & returns the graph (nodes wired together)
│  │  ├─ state/
│  │  │  ├─ init.py
│  │  │  └─ schema.py        # Pydantic: GraphState, NodeOutput, ParsedDoc, Entity types, etc.
│  │  └─ nodes/
│  │     ├─ init.py
│  │     ├─ parse_documents.py     # Node A: ingest files/links → normalized text/chunks
│  │     ├─ extract_entities.py    # Node B: BO/BI/PI/CO extraction (+ merge existing)
│  │     ├─ enhance_initiatives.py # Node C: improve + add new initiatives
│  │     ├─ generate_roadmap.py    # Node D: scoring & RoadmapEntry creation
│  │     └─ output.py              # Node E: finalize payload (ids, counts, messages)
│  │
│  └─ utils/
│     ├─ init.py
│     ├─ file_loaders.py     # PDF/DOCX/XLSX/text loaders; preserve tables where possible
│     ├─ url_fetchers.py     # HTTP fetchers for GDocs/Confluence/Notion (as allowed)
│     ├─ cleaners.py         # dedupe, boilerplate removal, chunking
│     ├─ llm.py              # prompt runners, model configs (OpenAI, etc.)
│     ├─ rag.py              # (optional) retrievers/vector-store adapters
│     └─ mapping.py          # map extracted entities -> ORM instances
│
├─ static/                   # (if needed)
├─ media/                    # user-uploaded files (dev)
└─ scripts/                  # convenience scripts (db reset, demo seeding, etc.)

Notes & conventions

Each app has its own urls.py; config/urls.py includes them with prefixes (e.g., /api/roadmap/, /api/brain/).

roadmap is your authoritative domain layer: all models + admin + CRUD APIs.

brain never edits raw DB tables directly from nodes; it calls small mapping helpers in brain/utils/mapping.py (and/or dedicated services) so the flow logic stays clean.

langgraph_flow/state/schema.py centralizes Pydantic types used by nodes and the shared GraphState.

langgraph_flow/graph.py wires nodes and returns a runnable graph; views call into it.

utils/ keeps I/O boundaries clean (file parsing, URL fetching, RAG, LLM runners).

-------------------------------------------------------------

Data Model Map (ER-style summary). Here’s a clear, compact view of your domain and how things link together.


Entities & relationships (high‑level)
Organization 1─* User Organization 1─* ProductKPI Organization 1─* CustomerSegment Organization 1─* CustomerObjective Organization 1─* BusinessKPI Organization 1─* BusinessObjective Organization 1─* BusinessInitiative Organization 1─* ProductInitiative Organization 1─* Roadmap User 1─* ProductInitiative (owner) User 1─* BusinessInitiative (owner) User 1─* [created_* fields across entities] 
Product side
ProductInitiative (TimeStamped)
FK organization, FK owner
Fields: title, description, start_date, end_date, status
M2M via through: 
↔️ ProductKPI through ProductInitiativeKPI
↔️ CustomerObjective through CustomerObjectiveProductInitiitive
↔️ BusinessInitiative through BusinessInitiativeProductInitiative (the initiative-centric link that ties into business side)
Included in roadmaps via RoadmapEntry (through model)
ProductKPI (TimeStamped)
FK organization, FK created_by
Fields: name, description, target_value, current_value, unit
Reverse: 
.product_initiatives (through ProductInitiativeKPI)
ProductInitiativeKPI (through)
FK product_initiative (related_name: product_initiative_kpis)
FK product_kpi (related_name: product_initiative_kpis)
Fields: target_value, current_value, weight, note
Unique: (product_initiative, product_kpi)
Customer side
CustomerSegment (TimeStamped)
FK organization, FK created_by
Fields: name, description, size_count, size_value, strategic_importance
CustomerObjective (TimeStamped)
FK organization, FK created_by
Fields: name, description, metric_name, current_value, target_value, unit
M2M: 
↔️ CustomerSegment (simple M2M)
↔️ ProductInitiative through CustomerObjectiveProductInitiative
CustomerObjectiveProductInitiative (through)
FK customer_objective (related_name: customer_objective_product_initiatives)
FK product_initiative (related_name: customer_objective_product_initiatives)
FK contribution_type (to ContributionType)
Fields: confidence, note
Unique: (customer_objective, product_initiative)
Business side
BusinessInitiative (TimeStamped)
FK organization, FK owner
Fields: title, description, status, start_date, end_date
M2M: 
↔️ BusinessObjective through BusinessObjectiveInitiative
↔️ ProductInitiative through BusinessInitiativeProductInitiative
BusinessObjective (TimeStamped)
FK organization, FK created_by
Fields: title, description, deadline, priority
M2M: 
↔️ BusinessKPI through **BusinessObjectiveKPI
↔️ BusinessInitiative through **BusinessObjectiveInitiative (reverse)
BusinessKPI (TimeStamped)
FK organization, FK created_by
Fields: name, description, target_value, current_value, unit, priority
BusinessObjectiveInitiative (through)
FK business_objective
FK business_initiative
Fields: priority, contribution_type (FK ContributionType), confidence_level, note
Unique: (business_objective, business_initiative)
Ordering: priority
BusinessObjectiveKPI (through)
FK business_objective (related_name: business_objective_kpis)
FK business_kpi (related_name: business_objective_kpis)
Fields: target_value, current_value, weight, note
Unique: (business_objective, business_kpi)
BusinessInitiativeProductInitiative (through)
FK business_initiative (related_name: business_initiative_product_initiatives)
FK product_initiative
Fields: contribution_weight, note
Unique: (business_initiative, product_initiative)
Roadmap layer
Roadmap (TimeStamped)
FK organization, FK created_by
Fields: name, description, start_date, end_date, prioritization_logic (text), time_horizon (enum), is_active
M2M: 
↔️ ProductInitiative through RoadmapEntry
RoadmapEntry (through)
FK roadmap (related_name: roadmap_entries)
FK product_initiative (related_name: roadmap_entries)
Fields: priority_score, priority_rank, note

Unique: (roadmap, product_initiative)
Shared / Common
ContributionType (in common)
Drives typed links (direct/indirect/enabling, etc.) in through models.
TimeStampedModel (in common)
Provides created_at, updated_at across entities.
Key reverse accessors (handy ones)
pi.product_initiative_kpis.all() → rows in the through table with weights/notes
pi.product_kpis.all() → plain list of KPIs (DRF uses this for simple nesting)
pi.customer_objective_product_initiatives.all() → CO↔️PI link rows
pi.business_initiatives.all() → linked business initiatives
initiative.business_objectives.all() (via BOI through)
roadmap.roadmap_entries.all() and pi.roadmap_entries.all()
Serializer/viewset snapshot (current)
roadmap/serializers.py 
ProductInitiativeSerializer (+ business_objectives computed)
ProductInitiativeKPISerializer (CRUD; writes via PK for initiative/KPI if desired)
ProductKPISerializer
CustomerObjectiveSummarySerializer (+ full CustomerObjectiveSerializer)
BusinessInitiativeSerializer
Through serializers where needed (lightweight)
roadmap/views.py 
ProductInitiativeViewSet (full CRUD, prefetches related)
ProductInitiativeKPIViewSet (CRUD)
(others as you’ve added)
Org/ownership guardrails (recommended)
In each ViewSet: 
Filter by request.user.organization
On create: set organization and owner from request context
In serializers: 
Keep organization, owner read-only; populate in create()/update() from context.


----------------------------------------------------------

API surface (what exists + what we’ll add next). I’m keeping it crisp but concrete so the frontend/brain can integrate right away.

Base

Base URL: /api/roadmap/

Auth: DRF Session or Token (TBD). All list endpoints are org‑scoped in the viewsets.

Pagination: DRF default (page/size).

Formats: JSON.


Product Initiatives

Collection

GET /product-initiatives/

Query params: search (title/description), status, ordering (e.g., -created_at), start_dategte, end_datelte

Response item (abridged):

{
  "id": 1, "title": "...", "status": "planned",
  "organization": 1, "owner": 2,
  "product_kpis": [...through rows...],
  "business_initiatives": [...],
  "customer_objectives": [...summary...],
  "business_objectives": [...]  // computed, optional
}


POST /product-initiatives/

Body:

{
  "title": "Implement A/B engine",
  "description": "...",
  "start_date": "2025-08-01",
  "end_date": "2025-09-30",
  "status": "planned"
}

Notes: organization & owner auto-set from request.



Detail

GET /product-initiatives/{id}/

PUT /product-initiatives/{id}/ | PATCH /product-initiatives/{id}/

Only base fields (we’re not doing nested writes here).


DELETE /product-initiatives/{id}/


Product Initiative ↔️ KPI (through)

Collection

GET /product-initiative-kpis/

Supports product_initiative, product_kpi filters.


POST /product-initiative-kpis/

Body (PK style):

{
  "product_initiative": 1,
  "product_kpi": 3,
  "target_value": 30.0,
  "weight": "40.00",
  "note": "Key target for launch"
}



Detail

GET /product-initiative-kpis/{id}/

PUT/PATCH /product-initiative-kpis/{id}/

DELETE /product-initiative-kpis/{id}/


Product KPIs

GET /product-kpis/ (filter by name, ordering=priority if added)

POST /product-kpis/

{"name":"Checkout Latency","description":"...","target_value":1.0,"current_value":3.0,"unit":"s"}

GET/PUT/PATCH/DELETE /product-kpis/{id}/


Business Initiatives

GET /business-initiatives/ (filters: status, date range)

POST /business-initiatives/ (org/owner auto-set)

GET/PUT/PATCH/DELETE /business-initiatives/{id}/


Customer Objectives

GET /customer-objectives/ (filters: name, maybe segment)

POST /customer-objectives/

GET/PUT/PATCH/DELETE /customer-objectives/{id}/


Business Objective links (optional near‑term)

GET/POST /business-objective-kpis/ (through)

GET/POST /business-objective-initiatives/ (through)


Roadmaps

GET /roadmaps/ (filters: is_active, time_horizon)

POST /roadmaps/

{
  "name":"H2 Growth",
  "description":"...",
  "start_date":"2025-07-01",
  "end_date":"2025-12-31",
  "time_horizon":"medium_term",
  "prioritization_logic":"RICE"
}

GET/PUT/PATCH/DELETE /roadmaps/{id}/


Roadmap Entries (through PI in a roadmap)

GET /roadmap-entries/?roadmap=1 (or product_initiative=ID)

POST /roadmap-entries/

{
  "roadmap": 1,
  "product_initiative": 3,
  "priority_score": 12.5,
  "priority_rank": 2,
  "note":"High RICE"
}

GET/PUT/PATCH/DELETE /roadmap-entries/{id}/


Common patterns & responses

Errors: DRF standard (400 with field errors, 403 unauthorized, 404 not found).

Org/owner: auto-populated in create(); lists filtered by request.user.organization.

Nested reads: returned as we’ve wired (KPIs via through rows; BI & CO as summaries).


What’s next (API)

1. Add viewsets/routes for:

BusinessObjective, BusinessObjectiveKPI, BusinessObjectiveInitiative



2. Filters/search:

Consistent filtering across lists (status, date range, free‑text search)



3. Permissions:

Per‑org + object‑level (owner can edit, others read)



4. Slim/summary variants:

?view=summary returns lighter payloads (use dedicated serializers)


------------------------------------------------------------



Alright — continuing the README with Step 6: AI Integration Overview.

6. AI Integration Overview

The Brain app is the AI orchestration layer. It ingests company context (docs, links, existing DB records), extracts structured entities (objectives, initiatives, KPIs), and proposes/updates roadmaps using chosen prioritization frameworks. We use:

LangGraph for stateful, branching workflows (graphs of nodes with memory, retries, human-in-the-loop).

LangChain utilities for LLM calls, parsing, and tool use (scraping, loaders, structured output).

(Optionally later) a vector store for retrieval over large corpora.


6.1 What the AI does (at a glance)

Parse inputs (PDF/DOCX/URLs) → normalized chunks + metadata.

Extract entities → Business Objectives, Business Initiatives, Customer Objectives, (candidate) Product Initiatives, KPIs.

Reconcile → keep/improve existing records from DB; propose new ones where gaps exist.

Generate roadmaps → create/update ProductInitiatives and RoadmapEntries; attach KPIs/links.

Prioritize → compute scores per framework (RICE, WSJF, Value/Effort, custom).

Human-in-the-loop → users can approve/request changes at node-level; graph resumes with feedback.


6.2 Core scenarios (what graphs cover)

1. Greenfield generation from uploaded/linked docs.


2. Augment + reconcile using existing DB records and new materials.


3. Re-prioritize an existing roadmap under a different framework.


4. End-to-end autopilot: ingest → extract → propose/merge → prioritize → produce roadmap variants.



6.3 High-level architecture

Django: source of truth (models, auth, org boundaries, audit).

Brain (LangGraph): long-running workflows; persists state; calls Django services.

Services layer (brain/services/*): pure Python utilities for extraction, scoring, reconciliation.

Adapters (brain/adapters/*): file loaders, web fetchers, chunkers, structured parsers.

Storage: Postgres (canonical data), optional vector store (RAG), S3-like file bucket.


6.4 State & node model (minimal)

State (Pydantic model): holds input config, extracted entities, decisions, and artifacts (errors, warnings, logs).

Nodes (pure functions): parse_documents → extract_entities → enhance_initiatives → generate_roadmap → prioritize → output.

Control: conditional edges (e.g., if missing objectives, fallback to assumptions), retries with backoff, and human approval hooks.


6.5 Human-in-the-loop

Each node can emit status="needs_review" + a preview payload.

Frontend posts approved or changes_requested with comments.

Graph resumes with feedback merged into state (tracked as deltas).


6.6 Prioritization frameworks (pluggable)

RICE (Reach, Impact, Confidence, Effort)

WSJF (Cost of Delay / Job Size)

Value/Effort (simple)

Custom (org-defined weights + formula)
All live in brain/services/prioritization.py as interchangeable scorers.


6.7 Org and security considerations

Every graph run is scoped to an Organization (org_id in state).

Node utilities must enforce org filtering when reading/writing DB.

Audit fields (created_by, organization) set from the request context.


6.8 Persistence & idempotency

Graph runs get a run_id with checkpoints after each node.

If a node crashes, resume from last checkpoint.

Writes to DB are made via service functions with idempotent keys when possible (e.g., hash of source snippet).


6.9 Extensibility points

Add loaders for new sources (Confluence, Notion, Google Drive).

Add new prioritization methods.

Slot in a vector store-backed RAG retriever for large corpora.

Add new “explainability” nodes (e.g., rationales per score).



---------------------------------------------------------


