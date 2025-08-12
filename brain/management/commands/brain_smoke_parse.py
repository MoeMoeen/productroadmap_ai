from django.core.management.base import BaseCommand
from pathlib import Path

# Import from correct location after file renaming
from brain.langgraph_flow.schema import IngestionInput, GraphState
from brain.langgraph_flow.nodes.perception import parse_documents_node
from brain.models import BrainRun


class Command(BaseCommand):
    help = "Smoke test for parse_documents node"

    def handle(self, *args, **options):
        # Create a test BrainRun
        run = BrainRun.objects.create(
            status="running",
            organization_id=1,
            metadata={"test": True}
        )
        
        # Build input: one local file + one URL
        input_payload = IngestionInput(
            org_id=1,
            user_id=1,
            file_paths=[str(Path("/tmp/brain_smoke_test.txt"))],  # Example local file
            links=["https://example.com/"]
        )

        # Create initial graph state with required fields
        state = GraphState(
            org_id=1,
            user_id=1,
            uploaded_files=[str(Path("/tmp/brain_smoke_test.txt"))],
            links=["https://example.com/"],
            framework="RICE",
            input=input_payload
        )

        # Run the parse_documents node
        out_state = parse_documents_node(run, state)

        # Show some debug output
        docs = out_state.parsed_documents or []
        self.stdout.write(f"✅ parse_documents produced {len(docs)} documents")

        for i, doc in enumerate(docs[:3], 1):
            content_preview = (doc.content[:120] + "...") if len(doc.content) > 120 else doc.content
            self.stdout.write(f"{i}. {doc.file_path}: {content_preview}")
            
        # Clean up test run
        run.delete()