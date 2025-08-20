# Migration Note: Cognitive AI Architecture Refactor (August 2025)

## Summary

In August 2025, the codebase was refactored to implement a modular, cognitive-layer-based architecture for the product roadmap AI system. This migration brings the following key changes:

### 1. Layer-Based Structure
- Each cognitive function (perception, memory, world model, goal, planner, reasoning, execution, monitor, learning, business understanding, deliberation) now has its own file in `brain/langgraph_flow/layers/`.
- Atomic, reusable logic remains in `brain/langgraph_flow/nodes/`.

### 2. Centralized Graph Wiring
- The orchestration logic is now in `brain/langgraph_flow/graph.py` (formerly `langgraph_workflow.py`).

### 3. Models Refactor
- `brain/models.py` was split into a package: `brain/models/` with `runs.py`, `memory.py`, `documents.py`, etc.

### 4. Schema Updates
- `brain/langgraph_flow/schema.py` now includes `BusinessProfile` and `PlanForStep` models.
- `GraphState` includes `business_profile` and `plan_for_step` fields for richer state management.

### 5. API & Services
- API and service layers remain unchanged for now, but are ready for future modularization.

## Rationale
- Improves modularity, clarity, and extensibility of the codebase.
- Enables new cognitive layers and human-in-the-loop planning.
- Supports future observability, auditability, and explainability.

## Action Items
- Update all imports to use the new structure.
- Remove any legacy files or references (e.g., `langgraph_workflow.py`).
- See `docs/project-restructuring-2025-08-20.md.md` for full details and rationale.

---

_This note documents the August 2025 migration to a cognitive, modular architecture._
