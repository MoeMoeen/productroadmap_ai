
"""
Core Utilities for Cognitive Pipeline
-------------------------------------
Includes:
- log_node_io: Decorator for structured logging of node entry/exit/errors.
- handle_errors: Decorator for error handling in nodes/layers.
- get_llm_client: Stub for LLM client integration.
- get_vector_db_client: Stub for vector DB integration.

Example usage:
	@handle_errors(raise_on_error=False)
	@log_node_io(node_name="example_node")
	def example_node(...):
		...

	llm = get_llm_client()
	vectordb = get_vector_db_client()
"""

import logging
import functools
from typing import Callable

logger = logging.getLogger("cognitive_pipeline")

def log_node_io(node_name=None):
	"""
	Decorator for logging entry, exit, and exceptions for cognitive pipeline nodes.
	Logs input/output and errors for observability and debugging.

	Example:
		@log_node_io(node_name="perception_layer")
		def perception_layer(...):
			...
	"""
	def decorator(func: Callable) -> Callable:
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			logger.info(f"[node:{node_name}] Entering node")
			try:
				result = func(*args, **kwargs)
				logger.info(f"[node:{node_name}] Exiting node successfully")
				return result
			except Exception as e:
				logger.error(f"[node:{node_name}] Exception: {e}", exc_info=True)
				raise
		return wrapper
	return decorator

# --- Error Handling Helper ---
def handle_errors(default_return=None, raise_on_error=False):
	"""
	Decorator for error handling in pipeline nodes/layers.
	Logs exceptions and optionally returns a default value or re-raises.

	Example:
		@handle_errors(default_return=None, raise_on_error=False)
		def node(...):
			...
	"""
	def decorator(func: Callable) -> Callable:
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except Exception as e:
				logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
				if raise_on_error:
					raise
				return default_return
		return wrapper
	return decorator

# --- LLM/vector DB helpers (stubs) ---
def get_llm_client():
	"""
	Return a configured LLM client (stub).
	Example:
		llm = get_llm_client()
	"""
	# TODO: Implement real LLM client setup
	return None

def get_vector_db_client():
	"""
	Return a configured vector DB client (stub).
	Example:
		vectordb = get_vector_db_client()
	"""
	# TODO: Implement real vector DB client setup
	return None
