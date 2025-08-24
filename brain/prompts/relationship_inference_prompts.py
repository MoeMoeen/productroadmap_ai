# brain/prompts/relationship_inference_prompts.py
"""
Centralized prompts for LLM-based relationship inference between extracted entities.
"""

RELATIONSHIP_INFERENCE_PROMPT = """
You are an expert in business knowledge graphs. Given the following extracted entities from a document, infer all meaningful relationships between them. 

Entities (JSON):
{entities_json}

World Model (optional, JSON):
{world_model_json}

Instructions:
- Identify links such as: which ProductInitiative supports which BusinessObjective through which BusinessInitiative, 
which BusinessKPI measures which BusinessObjective, which ProductInitiative supports which CustomerObjective, which CustomerSegment is targeted by which ProductInitiative and which Product, etc.
- Use both explicit and implicit clues (co-location, shared terms, prior knowledge).
- Output a JSON list of relationships, each with:
  - source_entity (type & value)
  - target_entity (type & value)
  - relationship_type (e.g., supports, measures, targets)
  - confidence (0.0-1.0)
  - rationale (short explanation)

Respond with valid JSON only.
"""
