Here’s the updated plan for the world_model_layer.py and related modeling, incorporating your direction to add only the most stable, essential org facts (e.g., name, vision, markets) to the `Organization` model now:

---

## 🚦 World Model Layer: Finalized Implementation Plan

### 1. **Purpose**
- Aggregate all extracted org facts (from hybrid document parsing and entity extraction).
- Map these facts into the exact core entities defined in models.py (no generic fields).
- Build and persist a `WorldModel` instance, scoped per run and per organization.
- Update the pipeline `GraphState` with the new world model (mandatory).

---

### 2. **Inputs**
- `run: BrainRun` (with `.organization`)
- `state: GraphState` (must include `parsed_documents`, `extracted_entities`, and optionally memory for enrichment)

---

### 3. **Key Entities (from your models)**
- `BusinessObjective`
- `BusinessInitiative` (↔ `BusinessObjective` via `BusinessObjectiveInitiative`)
- `ProductInitiative` (↔ `BusinessInitiative`, `CustomerObjective`, `ProductKPI`)
- `CustomerObjective` (↔ `CustomerSegment`)
- `CustomerSegment`
- `BusinessKPI` (↔ `BusinessObjective` via `BusinessObjectiveKPI`)
- `ProductKPI` (↔ `ProductInitiative` via `ProductInitiativeKPI`)
- (Optionally: `Product`, `OrganizationFact` for org name, vision, markets, headcount, etc.)

---

### 4. **Stable Org Facts in Organization Model**
- **Action:** Add only the most stable, essential org facts (e.g., name, vision, markets) to the `Organization` model in models.py now.
- More dynamic or experimental fields (e.g., extracted product portfolio, headcount, etc.) will remain in the `WorldModel` or a related model for now.

---

### 5. **Data Flow**
1. **Hybrid Document Parsing** (traditional + LLM) → `parsed_documents`
2. **Entity Extraction** (keyword/heuristics + LLM) → `extracted_entities`
3. **Aggregate Facts** (from `parsed_documents`, `extracted_entities`, and memory if relevant)
4. **Map to World Model** (using a mapping utility, e.g., `map_extracted_facts_to_world_model`)
5. **Persist World Model** (per run + org, update or create as needed)
6. **Update Pipeline State** (`state.world_model = ...`)

---

### 6. **Implementation Steps**
1. **Import/Define WorldModel**
   - Use the actual `WorldModel` ORM/model, with all relationships to the above entities.
   - If not present, define it with the correct fields and relationships.

2. **Mapping Utility**
   - Implement `map_extracted_facts_to_world_model(facts, run)` in `brain/utils/mapping.py`.
   - This function:
     - Accepts a list of `ExtractedEntity` and the current `BrainRun`.
     - Looks up or creates all related entities (using your models).
     - Aggregates them into a `WorldModel` instance.
     - Persists the world model (scoped per run + org).
     - Returns a Pydantic/dict representation for pipeline state.

3. **Layer Logic**
   - In world_model_layer.py:
     - Call the mapping utility with all extracted facts.
     - Persist the result.
     - Update `state.world_model` with the new model.

4. **Additional Org Facts**
   - Always attempt to extract and include: organization name, vision, markets, product portfolio (with a `Product` entity if needed), headcount, key stakeholders, etc.
   - Use LLM to complement extraction where heuristics/keywords are insufficient.
   - Only persist the most stable facts (name, vision, markets) in the `Organization` model for now.

5. **Strict Domain Alignment**
   - Only use entities and relationships defined in your models.
   - No generic or invented fields.

6. **Persistence**
   - Always persist the world model per run and per organization.
   - Ensure all relationships are set according to your schema.

7. **Pipeline State**
   - Always update `state.world_model` (never optional).

---

### 7. **Layer Relationships**
- **Entity Extraction Layer:** May further refine or validate entities in the world model.
- **Business Understanding Layer:** Consumes the world model to build a business profile (using heuristics + LLM).
- **Deliberation Layer:** Consults the world model for ambiguity resolution or user feedback.

---

### Immediate Actions:

Here’s the immediate execution plan:

1. **Confirm/finish any model changes** in models.py and models.py (stable org facts, WorldModel, relationships).
2. **Run Django migrations** if any model fields were added/changed.
3. **Update schema.py** to define `WorldModelSchema` for use in `GraphState` and serialization.
4. **Implement `map_extracted_facts_to_world_model()`** in `utils/mapping.py` to aggregate, persist, and return the world model.
5. **Refactor world_model_layer.py** to use the mapping function, persist, and update state.
6. **Test the full data flow** with sample data to ensure correct extraction, mapping, persistence, and state update.
7. **Document all changes** (docstrings, README, architecture docs).

