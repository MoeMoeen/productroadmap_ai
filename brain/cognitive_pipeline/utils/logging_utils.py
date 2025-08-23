# brain/cognitive_pipeline/utils/logging_utils.py

import json
import datetime
from typing import Any, Dict, List

# --- Production log function ---
def log_fn_file(event: Dict[str, Any], log_path: str = "entity_extraction.log"):
    """
    Appends event as JSON line to a log file.
    """
    event = dict(event)
    event["timestamp"] = event.get("timestamp") or datetime.datetime.utcnow().isoformat()
    with open(log_path, "a") as f:
        f.write(json.dumps(event) + "\n")

# --- Example: In-memory log_fn for tests ---
class InMemoryLogger:
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
    def __call__(self, event: Dict[str, Any]):
        self.events.append(dict(event))
