from brain.cognitive_pipeline.utils.llm_utils import llm_fn_openai, llm_fn_dummy
from brain.cognitive_pipeline.utils.logging_utils import log_fn_file, InMemoryLogger

# Example usage in a pipeline setup or test:
#
# run = BrainRun(
#     ...,
#     llm_fn=llm_fn_openai,  # For production
#     log_fn=log_fn_file     # For production
# )
#
# # For testing:
# test_logger = InMemoryLogger()
# run = BrainRun(
#     ...,
#     llm_fn=llm_fn_dummy,
#     log_fn=test_logger
# )
