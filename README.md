# Kolosal Server Test Suite

A comprehensive test suite for [Kolosal Server](https://github.com/KolosalAI/kolosal-server) that provides extensive testing capabilities for LLM completions, embeddings, document processing, and RAG functionality.

## 🆕 New YAML Configuration System

This test suite now uses **YAML-based configuration** for better maintainability and alignment with Kolosal Server's configuration format:

- **`config/config.yaml`** - Main server and model configuration
- **`config/agents.yaml`** - Agent system configuration  
- **`config/sequential_workflows.yaml`** - Workflow definitions

✅ **Fully backwards compatible** - existing code continues to work!

📖 See [YAML_MIGRATION_GUIDE.md](YAML_MIGRATION_GUIDE.md) for detailed migration information.

🧪 **Test the configuration**: `python test_yaml_config.py`

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- A running instance of [Kolosal Server](https://github.com/KolosalAI/kolosal-server)
- Access to the server's API endpoints (configured in `config/config.yaml`)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd kolosal-server-test
   ```

2. **Install dependencies:**
   ```bash
   # Using uv (recommended)
   uv pip install -r requirements.txt
   
   # Or using pip with virtual environment
   python -m venv venv
   venv\Scripts\activate  # On Windows
   pip install -r requirements.txt
   
   # Install PyYAML for configuration
   pip install PyYAML
   ```

### Quick Test
```bash
# Test YAML configuration
python test_yaml_config.py

# Test server connectivity
python basic_test.py

# Run full test suite
python main.py

# Run specific test categories
python scripts/launcher.py --test-endpoints
python scripts/launcher.py --run-tests
```

## 📋 Features

### Core Testing Capabilities
- **🤖 LLM Completion Testing**: Basic and streaming completion endpoints
- **🔢 Embedding Generation**: Text embedding capabilities testing
- **📄 Document Processing**: PDF and DOCX parsing functionality
- **📚 Document Management**: Ingestion and retrieval testing
- **🔍 Vector Search**: Document search and retrieval capabilities
- **🔄 RAG Features**: Retrieval Augmented Generation testing
- **⚡ Concurrent Operations**: Performance testing under load
- **🛠️ Agent System**: Workflow and agent functionality testing

### Enhanced Features
- **📊 Comprehensive Logging**: Detailed request/response tracking
- **⚡ Performance Metrics**: Response time and throughput analysis
- **🔍 Endpoint Discovery**: Automatic endpoint availability testing
- **🛡️ Error Handling**: Robust error detection and reporting
- **📈 Test Reporting**: Detailed success/failure analytics

## 🏗️ Project Structure

```
kolosal-server-test/
├── main.py                    # Main test runner with comprehensive reporting
├── config.py                  # Centralized configuration management
├── logging_utils.py          # Enhanced logging and request tracking
├── quick_start_demo.py       # Interactive API demo
├── run_api_tests.py          # Reference API test runner
├── requirements.txt          # Python dependencies
├── scripts/                  # Launcher and utility scripts
│   ├── launcher.py           # Enhanced test launcher with validation
│   ├── launch_all.bat       # Windows batch launcher
│   ├── launch_tests.ps1     # PowerShell launcher
│   └── kill_test.bat        # Stop all test processes
├── utils/                    # Utility modules
│   ├── endpoint_tester.py   # Comprehensive endpoint testing
│   ├── demo_enhanced_logging.py # Logging demonstration
│   └── fix_id_extractions.py   # ID extraction utilities
├── tests/                   # Test modules organized by category
│   ├── engine_tests/        # LLM and embedding tests
│   │   ├── completion_test.py
│   │   └── embedding_test.py
│   ├── retrieval_tests/     # Document processing tests
│   │   ├── parse_pdf_test.py
│   │   ├── parse_docx_test.py
│   │   ├── document_ingestion_test.py
│   │   └── document_retrieval_test.py
│   └── agent_tests/         # Agent and RAG tests
│       ├── test_agent_features.py
│       ├── test_rag_features.py
│       └── test_workflows.py
├── test_files/              # Sample test documents
├── logs/                    # Test execution logs
└── backup/                  # Backup of original documentation
```

## ⚙️ Configuration

### Server Configuration
The test suite is configured to work with Kolosal Server's actual deployment settings:

```python
# Server settings (config.py)
SERVER_CONFIG = {
    "base_url": "http://127.0.0.1:8080",  # Default server URL
    "api_key": None,                      # No API key required
    "rate_limit": {
        "max_requests": 100,              # Rate limiting
        "window_seconds": 60
    }
}
```

### Model Configuration
Configured for standard Kolosal Server models:
- **Primary LLM**: `qwen3-0.6b`
- **Alternative LLM**: `gpt-3.5-turbo` 
- **Embeddings**: `text-embedding-3-small`, `text-embedding-3-large`

### Endpoint Mapping
All 25+ server endpoints are mapped and tested:
- Health: `/health`
- Models: `/models`, `/engines`
- OpenAI Compatible: `/v1/chat/completions`, `/v1/embeddings`
- Document Processing: `/parse-pdf`, `/parse-docx`
- Vector Search: `/vector-search`
- Workflows: `/sequential-workflows`
- Agent System: `/agents/*`
- Metrics: `/metrics`

## 🧪 Running Tests

### 1. Basic Connectivity Test
```bash
python basic_test.py
```
Verifies server accessibility and basic functionality.

### 2. Endpoint Testing
```bash
python utils/endpoint_tester.py
```
Tests all 25+ endpoints for availability and response.

### 3. Comprehensive Test Suite
```bash
python main.py
```
Runs the complete test suite with detailed reporting:
- LLM completion tests (basic and streaming)
- Embedding generation tests
- PDF and DOCX parsing tests
- Document ingestion and retrieval tests
- Agent system tests
- RAG feature tests
- Workflow tests
- Reference API tests

### 4. Enhanced Test Launcher
```bash
# Test with prerequisites checking
python scripts/launcher.py --run-tests

# Test endpoints only
python scripts/launcher.py --test-endpoints

# Windows PowerShell
.\scripts\launch_tests.ps1 -RunTests
```

### 5. Quick Start Demo
```bash
python quick_start_demo.py
```
Interactive demo following the API guide examples.

## 📊 Test Categories

### Engine Tests
- **Completion Test**: Basic and streaming LLM completions
- **Embedding Test**: Text embedding generation and validation

### Document Processing Tests  
- **PDF Parsing**: Extract text and metadata from PDF files
- **DOCX Parsing**: Process Word documents
- **Document Ingestion**: Add documents to knowledge base
- **Document Retrieval**: Search and retrieve documents

### Agent System Tests
- **Agent Features**: Agent creation and management
- **RAG Features**: Retrieval Augmented Generation
- **Workflows**: Multi-step workflow execution

## 🔍 Enhanced Logging

The test suite includes comprehensive endpoint logging that tracks:

### Request Tracking
- HTTP methods and URLs
- Complete JSON payloads
- Request size and timing
- Headers and parameters

### Response Analysis
- HTTP status codes
- Response JSON data
- Response size and headers
- Success/failure status

### Performance Metrics
- Request duration
- Requests per second
- Performance trending
- Bottleneck identification

### Log Outputs
- **Console**: Real-time formatted output with ✅/❌ indicators
- **File Logs**: `logs/endpoint_tests.log` - Structured JSON data
- **Test Logs**: `tests.log` - Complete test execution log

Example log output:
```
[✅ PASS] Document Upload - POST /api/v1/documents | Request: 1024B | Response: 200 (256B) | Duration: 0.123s
📤 Request Payload: {"documents": [...], "collection_name": "test_collection"}
📥 Response Data: {"success": true, "indexed_count": 3}
```

## 🛠️ API Fixes and Improvements

### Key Issues Resolved

#### 1. Consistent Error Handling
- **Before**: Mixed error handling patterns, crashes on assertions
- **After**: Standardized try-catch blocks with proper logging

#### 2. Response Validation
- **Before**: Poor response validation, unclear failure reasons  
- **After**: Proper response structure validation and detailed error reporting

#### 3. Endpoint Format Standardization
- **Before**: Inconsistent API endpoint formats
- **After**: Aligned with actual Kolosal Server API endpoints

#### 4. Fallback Mechanisms
- **Before**: Tests failed on missing files
- **After**: Graceful fallback to minimal content when test files unavailable

#### 5. Improved Status Reporting
- **Before**: Inconsistent logging across tests
- **After**: Standardized logging with clear PASS/FAIL indicators

### Fixed Endpoint URLs
- PDF Parsing: `/parse_pdf` → `/parse-pdf`
- DOCX Parsing: `/parse_docx` → `/parse-docx`
- Document Retrieval: `/retrieve` → `/vector-search`
- Embeddings: `/embeddings` → `/v1/embeddings`
- Chat: `/chat` → `/v1/chat/completions`

## 🚨 Troubleshooting

### Common Issues

#### Server Connection
```bash
# Test basic connectivity
python basic_test.py

# Check if server is running
curl http://127.0.0.1:8080/health
```

#### Missing Test Files
- PDF and DOCX tests include fallback content
- Files automatically created if missing
- Check `test_files/` directory for sample files

#### API Key Issues
- No API key required for default configuration
- Set `api_key=None` in config.py
- Server configured with "API Key Required: No"

#### Rate Limiting
- Default: 100 requests per 60 seconds
- Tests include automatic rate limiting handling
- Configurable in `config.py`

### Server-Side Issues Identified

#### Chat Template Errors
```
Failed to format chat templates: Unknown method: startswith
```
**Resolution**: Fix Jinja2 template syntax in server configuration

#### JSON Parsing Errors
```
JSON parsing error: incomplete UTF-8 string
```
**Resolution**: Server-side JSON parsing improvement needed

## 📈 Performance Monitoring

### Metrics Tracked
- Request/response timing
- Success/failure rates
- Error categorization
- Performance trending
- Resource utilization

### Performance Analysis
Tests provide detailed performance insights:
- Average response times per endpoint
- Requests per second calculations
- Error rate analysis
- Performance recommendations

## 🔧 Development

### Adding New Tests
1. Create test file in appropriate directory (`tests/`)
2. Inherit from `KolosalTestBase` for logging integration
3. Use `make_tracked_request()` for automatic logging
4. Follow standardized error handling patterns

### Configuration Updates
- Modify `config.py` for server/model settings
- Update endpoint mappings as needed
- Adjust rate limiting and timeouts

### Extending Logging
- Use `EndpointLogger` for custom request tracking
- Implement `RequestTracker` context manager
- Add custom metadata fields as needed

## 📝 Change History

### Latest Updates
- ✅ **API Fixes Applied**: Standardized error handling and response validation
- ✅ **Configuration Alignment**: Updated to match actual server deployment  
- ✅ **Enhanced Logging**: Comprehensive request/response tracking
- ✅ **Endpoint Fixes**: Corrected all endpoint URLs to match server implementation
- ✅ **Documentation Consolidation**: Merged all documentation into single README
- ✅ **Test Reliability**: Added fallback mechanisms and robust error handling
- ✅ **Performance Monitoring**: Detailed metrics and analysis capabilities

### Migration Notes
- All configuration centralized in `config.py`
- Logging enhanced with detailed request tracking
- Test files reorganized by category
- Endpoint URLs updated to match server implementation
- Error handling standardized across all tests

## 🤝 Contributing

1. Follow existing code patterns and error handling
2. Use the centralized configuration system
3. Include comprehensive logging for new endpoints
4. Add appropriate test categories and documentation
5. Ensure backward compatibility with existing tests

## 📄 License

This project is part of the Kolosal Server ecosystem. Please refer to the main project for licensing information.

---

**Note**: This test suite has been restructured and enhanced to align with the actual Kolosal Server deployment. All previous documentation has been consolidated into this comprehensive README for easier maintenance and reference.