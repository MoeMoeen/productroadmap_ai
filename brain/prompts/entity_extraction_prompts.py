# brain/prompts/entity_extraction_prompts.py

"""
Centralized prompts for entity extraction and related LLM tasks.
Each prompt should be documented and parameterized as needed.
"""

ENTITY_EXTRACTION_PROMPT = """
You are an expert business analyst. Given the following context, extract all business entities and organizational facts of the following types: BusinessObjective, BusinessInitiative, CustomerObjective, CustomerSegment, ProductInitiative, ProductKPI, BusinessKPI, Product, Vision, Strategy, Market, Department, Headcount, and any relationships between them. Avoid duplicates with prior entities and enrich ambiguous facts using the world model.

World Model (current org facts):
{world_model}

Prior Entities (semantic memory):
{prior_entities}

Document:
{document}
"""
