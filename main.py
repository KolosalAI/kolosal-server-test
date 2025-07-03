"""Main test script for Kolosal Server."""

from tests.engine_tests.completion_test import CompletionTest
from tests.engine_tests.embedding_test import EmbeddingTest
from tests.retrieval_tests.parse_pdf_test import ParsePDFTest

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

# Test engine embedding
embedding_test = EmbeddingTest()

# Basic embedding test
embedding_test.basic_embedding(
    model_name=EMBEDDING_MODEL,
    input_text="Hello, world!"
)

# Concurrent embedding test
embedding_test.concurrent_embedding(
    model_name=EMBEDDING_MODEL,
    input_texts=[
        "Hello, world!",
        "The quick brown fox jumps over the lazy dog.",
        "Machine learning is transforming technology.",
        "Natural language processing enables computers to understand text.",
        "Embeddings convert text into numerical vectors."
    ]
)

# Test PDF parsing
parse_pdf_test = ParsePDFTest()

# Basic PDF parsing test
parse_pdf_test.test_parse_pdf(
    path="test_files/test_pdf.pdf"
)

# Concurrent PDF parsing test
parse_pdf_test.concurrent_parse_pdf(
    pdf_paths=[
        "test_files/test_pdf1.pdf",
        "test_files/test_pdf2.pdf",
        "test_files/test_pdf3.pdf",
        "test_files/test_pdf4.pdf",
        "test_files/test_pdf5.pdf"
    ]
)
