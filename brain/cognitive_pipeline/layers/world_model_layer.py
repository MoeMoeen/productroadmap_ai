# brain/cognitive_pipeline/layers/world_model_layer.py

from brain.cognitive_pipeline.schema import GraphState
from brain.models.runs import BrainRun
# TODO: Import or implement WorldModel ORM/model when available
from brain.cognitive_pipeline.utils.utils import log_node_io
from brain.cognitive_pipeline.utils.utils import handle_errors

@handle_errors(raise_on_error=False)
@log_node_io(node_name="world_model_layer")
def world_model_layer(run: BrainRun, state: GraphState) -> GraphState:
	"""
	Cognitive Layer: World Model (Layer 3)

	This layer is responsible for:
	- Updating the internal representation of the current organization context (products, KPIs, goals, etc.)
	- Maintaining a structured, up-to-date snapshot of the business state
	- Integrating new information from parsed documents and extracted entities

	Business Logic Context:
	- Synthesizes org-level metadata, structure, and context
	- Enables downstream layers to reason about the business as a whole
	- Supports strategy, planning, and validation steps

	Architectural Role:
	- Acts as the "world model" for the cognitive pipeline
	- May call atomic nodes for extracting and updating org-level facts
	- Ensures the system has a coherent, up-to-date view of the business

	Usage:
	- Should be run after the memory layer
	- Updates the world model representation in persistent storage or in-memory state

	TODO:
	- Implement logic to update world model from state (e.g., parsed documents, extracted entities)
	- Integrate with WorldModel ORM/model when available
	"""
	# 1. Read extracted_entities and inferred_relationships from state
	extracted_entities = getattr(state, "extracted_entities", None) or []
	inferred_relationships = getattr(state, "inferred_relationships", None) or []

	# 2. Update the world model (in-memory, using BusinessProfile Pydantic model)
	from brain.cognitive_pipeline.schema import BusinessProfile
	bp_data = state.business_profile.model_dump() if state.business_profile else {}


	# --- Mapping from entity_type to BusinessProfile field and summary model ---
	from brain.cognitive_pipeline.schema import (
		ProductSummary, InitiativeSummary, ObjectiveSummary, KpiSummary
	)
	entity_field_map = {
		"ProductKPI": ("product_kpis", KpiSummary),
		"BusinessKPI": ("business_kpis", KpiSummary),
		"ProductInitiative": ("product_initiatives", InitiativeSummary),
		"BusinessInitiative": ("business_initiatives", InitiativeSummary),
		"BusinessObjective": ("business_objectives", ObjectiveSummary),
		"CustomerObjective": ("customer_objectives", ObjectiveSummary),
		"Product": ("products", ProductSummary),
		"CustomerSegment": ("customer_segments", str),
	}

	for ent in extracted_entities:
		etype = ent.entity_type if hasattr(ent, "entity_type") else ent.get("entity_type")
		val = ent.value if hasattr(ent, "value") else ent.get("value")
		if etype in entity_field_map:
			field, summary_model = entity_field_map[etype]
			bp_data.setdefault(field, [])
			# Convert value to the correct summary model
			try:
				if summary_model is str:
					summary_val = str(val)
				elif summary_model is ProductSummary:
					# Try to extract id and name
					if isinstance(val, dict):
						summary_val = ProductSummary(
							id=int(val.get("id", 0)) if val.get("id") is not None else 0,
							name=val.get("name", str(val))
						)
					else:
						summary_val = ProductSummary(id=0, name=str(val))
				elif summary_model is InitiativeSummary:
					if isinstance(val, dict):
						summary_val = InitiativeSummary(
							id=int(val.get("id", 0)) if val.get("id") is not None else 0,
							title=val.get("title") or val.get("name") or str(val),
							description=val.get("description")
						)
					else:
						summary_val = InitiativeSummary(id=0, title=str(val))
				elif summary_model is ObjectiveSummary:
					if isinstance(val, dict):
						summary_val = ObjectiveSummary(
							id=int(val.get("id", 0)) if val.get("id") is not None else 0,
							title=val.get("title") or val.get("name") or str(val)
						)
					else:
						summary_val = ObjectiveSummary(id=0, title=str(val))
				elif summary_model is KpiSummary:
					if isinstance(val, dict):
						summary_val = KpiSummary(
							id=int(val.get("id", 0)) if val.get("id") is not None else 0,
							name=val.get("name") or str(val),
							unit=val.get("unit")
						)
					else:
						summary_val = KpiSummary(id=0, name=str(val))
				else:
					summary_val = val
				# Avoid duplicates
				if summary_val not in bp_data[field]:
					bp_data[field].append(summary_val)
			except Exception:
				# Fallback: store in a generic 'entities' field
				bp_data.setdefault('entities', [])
				bp_data['entities'].append(ent.dict() if hasattr(ent, 'dict') else dict(ent))
		else:
			# Store in a generic 'entities' field
			bp_data.setdefault('entities', [])
			bp_data['entities'].append(ent.dict() if hasattr(ent, 'dict') else dict(ent))

	# Store relationships in a dedicated field
	bp_data['relationships'] = inferred_relationships

	# Update the business_profile in state
	state.business_profile = BusinessProfile(**bp_data)


	# 3. Persist the updated world model 
	log_fn = state.context.get("log_fn") if state.context else None
	try:
		from brain.models.world_model import WorldModel
		org_id = getattr(run, "org_id", None) or getattr(state, "org_id", None)
		if org_id:
			wm_obj, created = WorldModel.objects.update_or_create(
				org_id=org_id,
				defaults={"data": state.business_profile.dict()}
			)
			if log_fn:
				log_fn({
					"event_type": "world_model_persisted",
					"org_id": org_id,
					"created": created,
					"updated_at": str(wm_obj.updated_at)
				})
	except Exception as e:
		if log_fn:
			log_fn({"event_type": "world_model_persist_error", "error": str(e)})

	# 4. Log the update
	if log_fn:
		log_fn({
			"event_type": "world_model_updated",
			"entity_count": len(extracted_entities),
			"relationship_count": len(inferred_relationships)
		})

	return state
# World Model Layer
# TODO: Implement world model logic
