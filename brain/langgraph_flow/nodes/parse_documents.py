# brain/langgraph_flow/nodes/parse_documents.py
from typing import List
from ..schema import GraphState, NodeOutput

def _read_txt_files(paths: List[str]) -> List[str]:
    texts = []
    for p in paths:
        if p.lower().endswith(".txt"):
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    texts.append(f.read())
            except Exception as e:
                texts.append(f"[ERROR reading {p}: {e}]")
        else:
            # Step 1A is deliberately minimal; we’ll add proper loaders in Step 1B
            texts.append(f"[Step 1A placeholder: {p} (non-.txt not parsed yet)]")
    return texts

def parse_documents_node(state: GraphState) -> NodeOutput:
    """
    Step 1A: minimal parser
    - Reads .txt files locally (placeholder for real loaders)
    - For URLs, stores a placeholder line (real fetching in Step 1B)
    - Concats everything into parsed_text
    """
    raw_docs = []

    # Files (only .txt truly parsed in 1A)
    if state.files:
        raw_docs += _read_txt_files(state.files)

    # URLs (placeholder only in 1A)
    if state.urls:
        for u in state.urls:
            raw_docs.append(f"[Step 1A placeholder URL: {u}]")

    parsed = "\n\n---\n\n".join(raw_docs).strip()

    return NodeOutput(
        updates={
            "raw_documents": raw_docs,
            "parsed_text": parsed
        },
        notes="Step 1A minimal parse: .txt files read, others/URLs are placeholders."
    )