#!/usr/bin/env python3
"""
Demonstration script for Enhanced Endpoint Logging

This script shows how the enhanced logging system captures:
- Endpoint being tested
- JSON request payloads  
- Response data
- Performance metrics
- Error handling

Run this to see the logging in action without running the full test suite.
"""

import time
import json
from datetime import datetime

# Import our enhanced logging system
from logging_utils import endpoint_logger, RequestTracker
from config import SERVER_CONFIG


def demo_basic_logging():
    """Demonstrate basic endpoint logging features."""
    print("🎯 Demo: Basic Endpoint Logging")
    print("-" * 40)
    
    # Simulate testing a health check endpoint
    with RequestTracker(
        test_name="Health Check Demo",
        endpoint="/health",
        method="GET",
        metadata={"demo": True, "category": "connectivity"}
    ) as tracker:
        # Simulate API response
        time.sleep(0.1)  # Simulate network delay
        
        # Create a mock response
        class MockResponse:
            def __init__(self, status_code, json_data):
                self.status_code = status_code
                self.headers = {"Content-Type": "application/json"}
                self.content = json.dumps(json_data).encode()
            
            def json(self):
                return json.loads(self.content.decode())
        
        mock_response = MockResponse(200, {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        })
        
        tracker.set_response(mock_response)
    
    print("✅ Health check demo completed\n")


def demo_document_upload():
    """Demonstrate document upload logging."""
    print("📄 Demo: Document Upload Endpoint Logging")
    print("-" * 40)
    
    # Simulate document upload request
    upload_payload = {
        "documents": [
            {
                "text": "This is a test document for the enhanced logging demonstration. It contains sample text to show how document uploads are tracked.",
                "metadata": {
                    "source": "demo_document.txt",
                    "category": "demo",
                    "author": "Test System",
                    "date": "2024-01-15"
                }
            }
        ],
        "collection_name": "demo_collection",
        "auto_index": True,
        "embedding_model": "default"
    }
    
    with RequestTracker(
        test_name="Document Upload Demo",
        endpoint="/api/v1/documents",
        method="POST",
        request_data=upload_payload,
        metadata={"demo": True, "test_type": "document_management"}
    ) as tracker:
        # Simulate processing time
        time.sleep(0.2)
        
        # Mock successful response
        class MockResponse:
            def __init__(self, status_code, json_data):
                self.status_code = status_code
                self.headers = {"Content-Type": "application/json"}
                self.content = json.dumps(json_data).encode()
            
            def json(self):
                return json.loads(self.content.decode())
        
        mock_response = MockResponse(200, {
            "success": True,
            "data": {
                "indexed_count": 1,
                "collection_name": "demo_collection",
                "processing_time": 0.15,
                "document_ids": ["doc_12345"]
            },
            "message": "Documents successfully uploaded and indexed"
        })
        
        tracker.set_response(mock_response)
    
    print("✅ Document upload demo completed\n")


def demo_retrieval_query():
    """Demonstrate document retrieval logging."""
    print("🔍 Demo: Document Retrieval Endpoint Logging")
    print("-" * 40)
    
    # Simulate retrieval query
    query_payload = {
        "query": "artificial intelligence machine learning",
        "k": 5,
        "score_threshold": 0.7,
        "collection_name": "demo_collection",
        "include_metadata": True
    }
    
    with RequestTracker(
        test_name="Document Retrieval Demo",
        endpoint="/api/v1/retrieve",
        method="POST",
        request_data=query_payload,
        metadata={"demo": True, "test_type": "information_retrieval"}
    ) as tracker:
        # Simulate retrieval processing
        time.sleep(0.3)
        
        # Mock retrieval response
        class MockResponse:
            def __init__(self, status_code, json_data):
                self.status_code = status_code
                self.headers = {"Content-Type": "application/json"}
                self.content = json.dumps(json_data).encode()
            
            def json(self):
                return json.loads(self.content.decode())
        
        mock_response = MockResponse(200, {
            "success": True,
            "data": {
                "documents": [
                    {
                        "text": "Artificial intelligence is transforming industries...",
                        "score": 0.95,
                        "metadata": {
                            "source": "ai_overview.txt",
                            "category": "technology"
                        }
                    },
                    {
                        "text": "Machine learning algorithms are being used...",
                        "score": 0.87,
                        "metadata": {
                            "source": "ml_applications.txt", 
                            "category": "technology"
                        }
                    }
                ],
                "total_results": 2,
                "query_time": 0.25
            }
        })
        
        tracker.set_response(mock_response)
    
    print("✅ Document retrieval demo completed\n")


def demo_error_handling():
    """Demonstrate error logging."""
    print("❌ Demo: Error Handling and Logging")
    print("-" * 40)
    
    with RequestTracker(
        test_name="Error Handling Demo",
        endpoint="/api/v1/nonexistent",
        method="GET",
        metadata={"demo": True, "expected_outcome": "error"}
    ) as tracker:
        # Simulate error
        time.sleep(0.05)
        
        # Mock error response
        class MockResponse:
            def __init__(self, status_code, json_data):
                self.status_code = status_code
                self.headers = {"Content-Type": "application/json"}
                self.content = json.dumps(json_data).encode()
            
            def json(self):
                return json.loads(self.content.decode())
        
        mock_response = MockResponse(404, {
            "error": True,
            "message": "Endpoint not found",
            "code": "ENDPOINT_NOT_FOUND",
            "timestamp": datetime.now().isoformat()
        })
        
        tracker.set_response(mock_response)
    
    print("✅ Error handling demo completed\n")


def main():
    """Run the logging demonstration."""
    print("🌟 ENHANCED ENDPOINT LOGGING DEMONSTRATION")
    print("=" * 60)
    print(f"Server: {SERVER_CONFIG['base_url']}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Start comprehensive logging
    endpoint_logger.log_test_start(
        "Enhanced Logging Demonstration",
        "Showcasing endpoint request/response tracking capabilities"
    )
    
    try:
        # Run demonstrations
        demo_basic_logging()
        demo_document_upload()
        demo_retrieval_query()
        demo_error_handling()
        
        print("🎉 All demonstrations completed successfully!")
        print("\n📊 Summary of logged features:")
        print("  ✓ Request methods and endpoints")
        print("  ✓ JSON request payloads")
        print("  ✓ Response data and status codes")
        print("  ✓ Performance timing metrics")
        print("  ✓ Error handling and tracking")
        print("  ✓ Metadata and categorization")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
    
    finally:
        # End logging
        endpoint_logger.log_test_end(
            "Enhanced Logging Demonstration",
            {
                "demos_completed": 4,
                "features_demonstrated": [
                    "basic_logging",
                    "document_upload",
                    "retrieval_query", 
                    "error_handling"
                ],
                "completion_time": datetime.now().isoformat()
            }
        )
        
        print(f"\n📁 Detailed logs saved to: logs/endpoint_tests.log")
        print("🔍 Check the log file to see the complete JSON entries")
        print("\nTo view logs:")
        print("  cat logs/endpoint_tests.log")
        print("  tail -f logs/endpoint_tests.log")


if __name__ == "__main__":
    main()
