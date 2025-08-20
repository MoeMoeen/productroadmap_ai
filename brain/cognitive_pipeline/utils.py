# TODO: Replace with real telemetry/logging decorator
def log_node_io(node_name=None):
	def decorator(func):
		def wrapper(*args, **kwargs):
			print(f"[TODO] log_node_io: Entering node {node_name}")
			result = func(*args, **kwargs)
			print(f"[TODO] log_node_io: Exiting node {node_name}")
			return result
		return wrapper
	return decorator
