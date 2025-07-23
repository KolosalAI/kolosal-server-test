# Enhanced Endpoint Logging Documentation

## Overview

The Kolosal Server Test Suite now includes comprehensive endpoint logging that tracks every API request and response with detailed information. This enhancement provides complete visibility into:

- **Which endpoint is being tested**
- **Full JSON request payloads**
- **Complete response data**
- **Performance metrics**
- **Error tracking and diagnostics**

## Features

### 🔍 Comprehensive Request Tracking
- Logs all HTTP methods (GET, POST, PUT, DELETE, etc.)
- Captures complete JSON request payloads
- Records URL parameters and headers
- Tracks request size and timing

### 📊 Detailed Response Logging
- Full response JSON data
- HTTP status codes and headers
- Response size and content type
- Error messages and stack traces

### ⚡ Performance Metrics
- Request duration in seconds
- Requests per second calculations
- Performance trending analysis
- Bottleneck identification

### 🛡️ Security & Privacy
- Automatic sanitization of sensitive data (API keys, passwords)
- Configurable data truncation for large payloads
- Safe logging of authentication headers

## Quick Start

### 1. Basic Usage

All existing tests now automatically include enhanced logging. Simply run any test:

```bash
python main.py
```

### 2. Enhanced Test Runner

Use the new enhanced test runner for focused endpoint testing:

```bash
# Quick endpoint tests with detailed logging
python test_runner_enhanced.py --quick

# Test endpoint connectivity only
python test_runner_enhanced.py --endpoints-only

# Full comprehensive testing
python test_runner_enhanced.py
```

### 3. Viewing Logs

Logs are automatically saved to the `logs/` directory:

```bash
# View detailed endpoint logs
cat logs/endpoint_tests.log

# Monitor logs in real-time
tail -f logs/endpoint_tests.log
```

## Log Output Examples

### Console Output
```
[✅ PASS] Document Upload and Indexing - POST /api/v1/documents | Request: 1024B | Response: 200 (256B) | Duration: 0.123s
📤 Request Payload:
{
  "documents": [
    {
      "text": "AI is transforming healthcare...",
      "metadata": {
        "source": "ai_healthcare.txt",
        "category": "healthcare"
      }
    }
  ],
  "collection_name": "test_rag_collection",
  "auto_index": true
}
📥 Response Data:
{
  "success": true,
  "data": {
    "indexed_count": 3,
    "collection_name": "test_rag_collection"
  }
}
```

### File Log Entry
```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "test_name": "Document Upload and Indexing",
  "endpoint": "/api/v1/documents",
  "method": "POST",
  "success": true,
  "request": {
    "payload": {
      "documents": [...],
      "collection_name": "test_rag_collection",
      "auto_index": true
    },
    "size_bytes": 1024
  },
  "response": {
    "status_code": 200,
    "headers": {...},
    "data": {...},
    "size_bytes": 256
  },
  "performance": {
    "duration_seconds": 0.123,
    "requests_per_second": 8.13
  }
}
```

## API Reference

### RequestTracker Class

Use the `RequestTracker` context manager for automatic request logging:

```python
from logging_utils import RequestTracker

with RequestTracker(
    test_name="My API Test",
    endpoint="/api/v1/test",
    method="POST",
    request_data={"key": "value"},
    metadata={"category": "test"}
) as tracker:
    response = requests.post(url, json=data)
    tracker.set_response(response)
```

### KolosalTestBase Enhanced Methods

The base test class now includes enhanced methods:

```python
# Make tracked requests with automatic logging
response = self.make_tracked_request(
    test_name="API Test",
    method="POST",
    endpoint="/api/v1/endpoint",
    json_data={"data": "value"},
    metadata={"category": "test"}
)

# Log test suite start/end
self.log_test_start("Test Suite Name", "Description")
self.log_test_end("Test Suite Name", {"results": "summary"})
```

## Configuration

### Customizing Log Output

Modify the `logging_utils.py` configuration:

```python
# Change log file location
endpoint_logger = EndpointLogger("custom_log.log")

# Adjust truncation limits
def _sanitize_data(self, data):
    # Modify truncation logic here
    pass
```

### Environment Variables

Set environment variables to control logging behavior:

```bash
# Set custom log directory
export KOLOSAL_LOG_DIR="/custom/log/path"

# Control log level
export KOLOSAL_LOG_LEVEL="DEBUG"
```

## Integration with Existing Tests

### Automatic Integration

All existing test files are automatically enhanced when they:
- Inherit from `KolosalTestBase`
- Use the `make_tracked_request()` method
- Import the logging utilities

### Manual Integration

For custom test classes:

```python
from logging_utils import endpoint_logger, RequestTracker

class MyCustomTester:
    def test_endpoint(self):
        with RequestTracker("My Test", "/api/endpoint", "POST") as tracker:
            response = requests.post(url, json=data)
            tracker.set_response(response)
```

## Analysis and Monitoring

### Log Analysis

Use standard tools to analyze the JSON logs:

```bash
# Count successful vs failed requests
grep '"success": true' logs/endpoint_tests.log | wc -l
grep '"success": false' logs/endpoint_tests.log | wc -l

# Find slow requests (>5 seconds)
grep '"duration_seconds": [5-9]' logs/endpoint_tests.log

# Extract all tested endpoints
grep '"endpoint":' logs/endpoint_tests.log | sort | uniq
```

### Performance Monitoring

Track performance trends:

```bash
# Average response times by endpoint
grep '"endpoint": "/api/v1/documents"' logs/endpoint_tests.log | \
  grep -o '"duration_seconds": [0-9.]*' | \
  awk '{sum+=$2; count++} END {print "Average:", sum/count}'
```

## Troubleshooting

### Common Issues

1. **Missing logs directory**: The `logs/` directory is created automatically
2. **Permission errors**: Ensure write permissions for the log directory
3. **Large log files**: Logs auto-rotate when they exceed size limits
4. **Missing imports**: Ensure `logging_utils` is properly imported

### Debug Mode

Enable verbose logging for troubleshooting:

```python
import logging
logging.getLogger('endpoint_logger').setLevel(logging.DEBUG)
```

## Best Practices

### 1. Meaningful Test Names
Use descriptive test names that identify the feature being tested:

```python
response = self.make_tracked_request(
    test_name="Document Upload with Metadata Validation",
    # ... other parameters
)
```

### 2. Include Metadata
Add context metadata for better analysis:

```python
metadata = {
    "test_category": "document_management",
    "file_type": "pdf",
    "expected_outcome": "success"
}
```

### 3. Error Handling
Always handle errors gracefully:

```python
try:
    response = self.make_tracked_request(...)
except Exception as e:
    logger.error(f"Test failed: {e}")
```

### 4. Performance Awareness
Monitor request timing and optimize slow tests:

```python
# Add performance expectations to metadata
metadata = {"expected_max_duration": 2.0}
```

## Migration Guide

### From Old to New Logging

Old pattern:
```python
response = requests.post(f"{self.base_url}/api/endpoint", json=data)
```

New pattern:
```python
response = self.make_tracked_request(
    test_name="Endpoint Test",
    method="POST", 
    endpoint="/api/endpoint",
    json_data=data
)
```

### Updating Existing Tests

1. Import logging utilities
2. Replace direct `requests` calls with `make_tracked_request`
3. Add test start/end logging for test suites
4. Include meaningful test names and metadata

## Advanced Features

### Custom Log Formatters

Create custom log formatters for specific needs:

```python
class CustomEndpointLogger(EndpointLogger):
    def _log_to_console(self, log_entry):
        # Custom console output format
        pass
```

### Integration with CI/CD

Parse logs in CI/CD pipelines:

```bash
# Extract test results for CI reporting
python -c "
import json
with open('logs/endpoint_tests.log') as f:
    for line in f:
        if 'ENDPOINT_TEST_ENTRY:' in line:
            entry = json.loads(line.split('ENDPOINT_TEST_ENTRY: ')[1])
            print(f\"{entry['test_name']}: {'PASS' if entry['success'] else 'FAIL'}\")
"
```

### Performance Dashboards

Create dashboards using the JSON log data:

```python
import json
import matplotlib.pyplot as plt

# Load and visualize performance data
performance_data = []
with open('logs/endpoint_tests.log') as f:
    for line in f:
        if 'ENDPOINT_TEST_ENTRY:' in line:
            entry = json.loads(line.split('ENDPOINT_TEST_ENTRY: ')[1])
            if 'performance' in entry:
                performance_data.append(entry['performance']['duration_seconds'])

plt.hist(performance_data, bins=20)
plt.title('Request Duration Distribution')
plt.show()
```

---

This enhanced logging system provides complete visibility into your Kolosal Server testing process, enabling better debugging, performance analysis, and quality assurance.
