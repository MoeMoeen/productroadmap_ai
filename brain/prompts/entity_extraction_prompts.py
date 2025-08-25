# brain/prompts/entity_extraction_prompts.py

"""
Centralized prompts for entity extraction and related LLM tasks.
Each prompt should be documented and parameterized as needed.
"""


import yaml
import os

def load_relationship_schema(schema_path=None):
	"""
	Loads and formats the relationship schema YAML for prompt injection.
	Returns a string summary of relationship types, descriptions, and examples.
	"""
	if schema_path is None:
		schema_path = os.path.join(os.path.dirname(__file__), "relationship_schema.yaml")
	try:
		with open(schema_path, "r") as f:
			data = yaml.safe_load(f)
		rels = data.get("relationships", [])
		lines = []
		for rel in rels:
			lines.append(f"- {rel['type']}: {rel['description']}")
			if 'example' in rel:
				src = rel['example'].get('source_entity', {})
				tgt = rel['example'].get('target_entity', {})
				lines.append(f"    Example: {src.get('type')} ('{src.get('value')}') -> {rel['relationship_type']} -> {tgt.get('type')} ('{tgt.get('value')}')")
		return "\n".join(lines)
	except Exception:
		return ""

ENTITY_EXTRACTION_PROMPT = """
You are an expert business analyst. Given the following context, extract all business entities and organizational facts of the following types: BusinessObjective, BusinessInitiative, CustomerObjective, CustomerSegment, ProductInitiative, ProductKPI, BusinessKPI, Product, Vision, Strategy, Market, Department, Headcount, and any relationships between them. Avoid duplicates with prior entities and enrich ambiguous facts using the world model.

Relationship Schema (typical relationships to look for):
{relationship_schema}

World Model (current org facts):
{world_model}

Prior Entities (semantic memory):
{prior_entities}

Document:
{document}
"""
