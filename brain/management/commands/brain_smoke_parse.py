from django.core.management.base import BaseCommand
from pathlib import Path

# ✅ Import from schema.py inside langgraph_flow
from brain.langgraph_flow.schema import IngestionInput, GraphState

# ✅ Import the parse_documents_node from nodes folder inside langgraph_flow
from brain.langgraph_flow.nodes.parse_documents import parse_documents_node


class Command(BaseCommand):
    help = "Smoke test for parse_documents node"

    def handle(self, *args, **options):
        # Build input: one local file + one URL
        input_payload = IngestionInput(
            org_id=1,
            user_id=1,
            file_paths=[str(Path("/tmp/brain_smoke_test.txt"))],  # Example local file
            links=["https://example.com/"]
        )

        # Create initial graph state
        state = GraphState(input=input_payload)

        # Run the parse_documents node
        out_state = parse_documents_node(state)

        # Show some debug output
        docs = out_state.raw_docs or []
        self.stdout.write(f"✅ parse_documents produced {len(docs)} documents")

        for i, d in enumerate(docs[:3], 1):
            text_preview = (d[:120] + "...") if len(d) > 120 else d
            self.stdout.write(f"{i}. {text_preview}")