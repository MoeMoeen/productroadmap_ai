# brain/utils/telemetry.py

"""
Telemetry module for logging and tracking events within the Brain application.
"""

import time
from typing import Callable, Any, Dict, List, Optional
from django.db import transaction
from ..models import BrainRun, BrainRunEvent

def _next_seq(run: BrainRun) -> int:
    # Lightweight way to get next sequence; safe under transaction
    last = BrainRunEvent.objects.filter(run=run).order_by("-seq").values_list("seq", flat=True).first()
    return (last or 0) + 1

@transaction.atomic
def emit_event(run: BrainRun, node_name: str, event_type: str, payload: Dict[str, Any], duration_ms: Optional[int] = None) -> int:
    seq = _next_seq(run)
    BrainRunEvent.objects.create(
        run=run, 
        seq=seq, 
        node_name=node_name, 
        event_type=event_type, 
        payload=payload or {},
        duration_ms=duration_ms
    )
    return seq

@transaction.atomic
def emit_events_batch(run: BrainRun, events: List[Dict]) -> List[int]:
    """Bulk create events for high-throughput scenarios"""
    start_seq = _next_seq(run)
    event_objects = []
    
    for i, event_data in enumerate(events):
        event_objects.append(BrainRunEvent(
            run=run,
            seq=start_seq + i,
            node_name=event_data["node_name"],
            event_type=event_data["event_type"],
            payload=event_data.get("payload", {}),
            duration_ms=event_data.get("duration_ms")
        ))
    
    BrainRunEvent.objects.bulk_create(event_objects)
    return list(range(start_seq, start_seq + len(events)))

def log_node_io(node_name: str):
    """
    Decorator for node functions: logs INPUT and OUTPUT events automatically.
    Node signature: func(run: BrainRun, state: dict) -> dict
    """
    def _wrap(func: Callable[[BrainRun, dict], dict]):
        def _inner(run: BrainRun, state: dict) -> dict:
            start_time = time.perf_counter()
            
            emit_event(run, node_name, BrainRunEvent.EventType.INPUT, {"state": state})
            
            try:
                # Update current node in run
                run.current_node = node_name
                run.save(update_fields=["current_node", "updated_at"])
                
                result = func(run, state)
                
                duration_ms = int((time.perf_counter() - start_time) * 1000)
                emit_event(run, node_name, BrainRunEvent.EventType.OUTPUT, {"state": result}, duration_ms=duration_ms)
                
                return result
            except Exception as exc:
                duration_ms = int((time.perf_counter() - start_time) * 1000)
                emit_event(run, node_name, BrainRunEvent.EventType.ERROR, {"message": str(exc)}, duration_ms=duration_ms)
                run.mark_failed(code=f"{node_name}_error", message=str(exc))
                raise
        return _inner
    return _wrap

def log_validation_event(run: BrainRun, node_name: str, validation_result: Dict[str, Any]):
    """Helper to log validation events with standardized format"""
    emit_event(
        run, 
        node_name, 
        BrainRunEvent.EventType.VALIDATION, 
        {
            "is_valid": validation_result.get("is_valid", False),
            "errors": validation_result.get("errors", []),
            "warnings": validation_result.get("warnings", []),
            "details": validation_result.get("details", {})
        }
    )

def log_info_event(run: BrainRun, node_name: str, message: str, details: Optional[Dict[str, Any]] = None):
    """Helper to log informational events"""
    payload: Dict[str, Any] = {"message": message}
    if details:
        payload["details"] = details
    emit_event(run, node_name, BrainRunEvent.EventType.INFO, payload)
