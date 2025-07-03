"""Main test script for Kolosal Server."""

from tests.engine_tests.completion_test import CompletionTest

LLM_MODEL = "qwen3-0.6b"  # Default model for testing
# Default embedding model for testing
EMBEDDING_MODEL = "text-embedding-3-small"

# Test engine completion
completion_test = CompletionTest()

# Basic completion test
completion_test.basic_completion(
    model_name=LLM_MODEL,
    temperature=0.7,
    max_tokens=128
)

# Streaming completion test
completion_test.stream_completion(
    model_name=LLM_MODEL,
    temperature=0.7,
    max_tokens=128
)

# Concurrent completion test
completion_test.concurrent_completion(
    model_name=LLM_MODEL,
    temperature=0.7,
    max_tokens=128)
