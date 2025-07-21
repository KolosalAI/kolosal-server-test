# Kolosal Server Test

This is the comprehensive test suite for [Kolosal Server](https://github.com/KolosalAI/kolosal-server). It provides extensive testing capabilities for the Kolosal Server's API endpoints, including completion generation, embeddings, document parsing, ingestion, and retrieval functionality.

## Features

- **LLM Completion Testing**: Test basic and streaming completion endpoints with various models
- **Embedding Generation**: Test text embedding generation capabilities  
- **Document Processing**: Test PDF and DOCX parsing functionality
- **Document Ingestion**: Test document ingestion into the server's knowledge base
- **Document Retrieval**: Test document retrieval and search capabilities
- **Concurrent Operations**: Test server performance under concurrent requests

## Prerequisites

- Python 3.7 or higher
- A running instance of [Kolosal Server](https://github.com/KolosalAI/kolosal-server)
- Access to the server's API endpoints (default: `http://localhost:8084`)


## Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd kolosal-server-test
   ```

2. **Install dependencies:**

   You can use [uv](https://github.com/astral-sh/uv) (recommended for speed) or pip:

   ```bash
   uv pip install -r requirements.txt
   ```

   Or using a virtual environment and pip:

   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   pip install -r requirements.txt
   ```

## Configuration

1. **Environment Variables:**

   Copy `.env.template` to `.env` and fill in the required values for your environment:

   ```bash
   copy .env.template .env  # On Windows
   # cp .env.template .env  # On macOS/Linux
   ```

   Edit `.env` to set paths, ports, and other configuration as needed.

2. **(Optional) Launch All Services:**

   You can use the provided batch script to launch Qdrant, Kolosal Server, and the test suite in separate terminals:

   ```bash
   ./launch_all.bat
   ```

   This script loads environment variables from `.env` and starts all required services and tests.

## Usage

### Running All Tests

To run the complete test suite:

```bash
uv run python main.py
```

Or, if not using uv:

```bash
python main.py
```

This will execute all tests in sequence:
1. LLM completion tests (basic and streaming)
2. Embedding generation tests
3. PDF parsing tests
4. DOCX parsing tests  
5. Document ingestion tests
6. Document retrieval tests

## Configuration

Before running tests, ensure your Kolosal Server is running and accessible. The default configuration assumes:

- **Server URL**: `http://localhost:8084`
- **API Key**: `TEST_API_KEY`
- **Default LLM Model**: `qwen3-0.6b`
- **Default Embedding Model**: `text-embedding-3-small`

You can modify these settings in `main.py` or in the individual test classes.

## Usage

### Running All Tests

To run the complete test suite:

```bash
python main.py
```

This will execute all tests in sequence:

1. LLM completion tests (basic and streaming)
2. Embedding generation tests
3. PDF parsing tests
4. DOCX parsing tests  
5. Document ingestion tests
6. Document retrieval tests

### Running Individual Test Categories

You can also run specific test categories by importing and using the individual test classes:

#### Engine Tests (LLM & Embeddings)

```python
from tests.engine_tests.completion_test import CompletionTest
from tests.engine_tests.embedding_test import EmbeddingTest

# Test completions
completion_test = CompletionTest()
completion_test.basic_completion(model_name="qwen3-0.6b", temperature=0.7, max_tokens=128)

# Test embeddings
embedding_test = EmbeddingTest()
embedding_test.basic_embedding(model_name="text-embedding-3-small", input_text="Hello, world!")
```

#### Document Processing Tests

```python
from tests.retrieval_tests.parse_pdf_test import ParsePDFTest
from tests.retrieval_tests.parse_docx_test import ParseDOCXTest

# Test PDF parsing
pdf_test = ParsePDFTest()
pdf_test.test_parse_pdf(path="test_files/test_pdf.pdf")

# Test DOCX parsing
docx_test = ParseDOCXTest()
docx_test.test_parse_docx(path="test_files/test_docx.docx")
```

#### Document Ingestion and Retrieval Tests

```python
from tests.retrieval_tests.document_ingestion_test import DocumentIngestionTest
from tests.retrieval_tests.document_retrieval_test import DocumentRetrievalTest

# Test document ingestion
ingestion_test = DocumentIngestionTest()
ingestion_test.test_ingest_document()

# Test document retrieval
retrieval_test = DocumentRetrievalTest()
retrieval_test.retrieve_documents(query="smartphone", limit=5, score_threshold=0.5)
```

## Test Files

The `test_files/` directory contains sample documents for testing:

- **PDF Files**: `test_pdf.pdf`, `test_pdf1.pdf` through `test_pdf5.pdf`
- **DOCX Files**: `test_docx.docx`, `test_docx1.docx` through `test_docx5.docx`

These files are used for testing document parsing and processing capabilities.

## Customizing Tests

### Changing Server Configuration

To test against a different server instance, modify the base URL and API key:

```python
from tests.kolosal_tests import KolosalTestBase

# Custom server configuration
test_base = KolosalTestBase(
    base_url="http://your-server:8084",
    api_key="your-api-key"
)
```

### Using Different Models

Modify the model names in `main.py` or pass them directly to test methods:

```python
LLM_MODEL = "your-preferred-model"
EMBEDDING_MODEL = "your-embedding-model"
```

## Test Output

The tests provide detailed console output including:

- ✅ Success/failure status
- ⏱️ Response times and performance metrics
- 🔥 Tokens per second for completion tests
- 📄 Document processing results
- 🔍 Retrieval results and scores

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure the Kolosal Server is running and accessible at the configured URL
2. **Authentication Error**: Verify the API key is correct
3. **Model Not Found**: Check that the specified models are available on your server
4. **File Not Found**: Ensure test files exist in the `test_files/` directory

### Debug Mode

For more detailed output, you can add debug prints or modify the test classes to include additional logging.

## Contributing

When adding new tests:

1. Inherit from `KolosalTestBase` for API client setup
2. Follow the existing naming conventions
3. Include comprehensive status reporting
4. Add appropriate error handling
5. Update this README if adding new test categories