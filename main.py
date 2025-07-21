"""Main test script for Kolosal Server.

Enhanced with comprehensive test summary and reporting features:
- Automated test result tracking with timing and status
- Categorized test organization (Engine Tests, Document Processing, etc.)
- Detailed summary with performance analysis and recommendations
- Progress tracking during test execution
- Server status integration with test results
- Failed test diagnostics and error reporting
- Success rate calculation and performance insights
"""

from tests.engine_tests.completion_test import CompletionTest
from tests.engine_tests.embedding_test import EmbeddingTest
from tests.retrieval_tests.parse_pdf_test import ParsePDFTest
from tests.retrieval_tests.parse_docx_test import ParseDOCXTest
from tests.retrieval_tests.document_ingestion_test import DocumentIngestionTest
from tests.retrieval_tests.document_retrieval_test import DocumentRetrievalTest

# Import agent test modules
from tests.agent_tests.test_agent_features import KolosalAgentTester
from tests.agent_tests.test_rag_features import RAGTester
from tests.agent_tests.test_workflows import WorkflowTester

import requests
import json
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class TestResult:
    """Data class to store individual test results."""
    name: str
    category: str
    status: str  # "PASS", "FAIL", "SKIP", "WARNING"
    duration: float
    details: str = ""
    error_message: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))

class TestSummary:
    """Test summary tracker and reporter."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = time.time()
        self.server_status = None
        self.server_info = {}
        
    def add_result(self, name: str, category: str, status: str, duration: float, 
                   details: str = "", error_message: str = ""):
        """Add a test result to the summary."""
        result = TestResult(
            name=name,
            category=category,
            status=status,
            duration=duration,
            details=details,
            error_message=error_message
        )
        self.results.append(result)
        
    def set_server_status(self, status: bool, info: Dict[str, Any] = None):
        """Set server status information."""
        self.server_status = status
        self.server_info = info or {}
        
    def run_test(self, test_name: str, category: str, test_func, *args, **kwargs):
        """Run a test function and automatically track its result."""
        print(f"\n🧪 Running: {test_name}")
        start_time = time.time()
        
        try:
            result = test_func(*args, **kwargs)
            duration = time.time() - start_time
            
            if result is False:
                self.add_result(test_name, category, "FAIL", duration, 
                              details="Test function returned False")
                print(f"❌ {test_name} - FAILED ({duration:.2f}s)")
                return False
            else:
                self.add_result(test_name, category, "PASS", duration,
                              details="Test completed successfully")
                print(f"✅ {test_name} - PASSED ({duration:.2f}s)")
                return True
                
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            self.add_result(test_name, category, "FAIL", duration,
                          error_message=error_msg)
            print(f"❌ {test_name} - FAILED ({duration:.2f}s)")
            print(f"   Error: {error_msg}")
            return False
    
    def run_test_manual(self, test_name: str, category: str, test_func, *args, **kwargs):
        """Run a test function and track its result based on return value and exceptions.
        
        This method handles tests that:
        - Return True/False to indicate success/failure
        - Use assert statements that raise AssertionError on failure  
        - Complete without exceptions (assumed success)
        - Raise other exceptions (treated as failure)
        """
        print(f"\n🧪 Running: {test_name}")
        start_time = time.time()
        
        try:
            result = test_func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Check if the test function returned a boolean result
            if result is False:
                self.add_result(test_name, category, "FAIL", duration,
                              details="Test function returned False")
                print(f"❌ {test_name} - FAILED ({duration:.2f}s)")
                return False
            elif result is True:
                self.add_result(test_name, category, "PASS", duration,
                              details="Test function returned True")
                print(f"✅ {test_name} - PASSED ({duration:.2f}s)")
                return True
            else:
                # If no clear boolean result, assume success if no exception was thrown
                self.add_result(test_name, category, "PASS", duration,
                              details="Test completed without exceptions")
                print(f"✅ {test_name} - COMPLETED ({duration:.2f}s)")
                return True
        except AssertionError as e:
            duration = time.time() - start_time
            error_msg = str(e)
            self.add_result(test_name, category, "FAIL", duration,
                          error_message=f"Assertion failed: {error_msg}")
            print(f"❌ {test_name} - FAILED ({duration:.2f}s)")
            print(f"   Assertion Error: {error_msg}")
            return False
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            self.add_result(test_name, category, "FAIL", duration,
                          error_message=error_msg)
            print(f"❌ {test_name} - FAILED ({duration:.2f}s)")
            print(f"   Error: {error_msg}")
            return False
            
    def add_manual_result(self, name: str, category: str, status: str, duration: float = 0.0, 
                         details: str = "", error_message: str = ""):
        """Manually add a test result (for tests run outside the framework)."""
        self.add_result(name, category, status, duration, details, error_message)
        
    def get_category_summary(self, category: str) -> Dict[str, Any]:
        """Get summary statistics for a specific test category."""
        category_results = [r for r in self.results if r.category == category]
        
        if not category_results:
            return {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "warnings": 0}
            
        return {
            "total": len(category_results),
            "passed": len([r for r in category_results if r.status == "PASS"]),
            "failed": len([r for r in category_results if r.status == "FAIL"]),
            "skipped": len([r for r in category_results if r.status == "SKIP"]),
            "warnings": len([r for r in category_results if r.status == "WARNING"]),
            "avg_duration": sum(r.duration for r in category_results) / len(category_results),
            "total_duration": sum(r.duration for r in category_results)
        }
        
    def print_quick_summary(self):
        """Print a quick summary during test execution."""
        total_tests = len(self.results)
        passed = len([r for r in self.results if r.status == "PASS"])
        failed = len([r for r in self.results if r.status == "FAIL"])
        
        print(f"\n📊 Quick Summary: {passed}/{total_tests} tests passed, {failed} failed")
        
    def get_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        # Server connectivity recommendations
        if self.server_status is False:
            recommendations.append("🔧 Server is not responding. Check if Kolosal Server is running on localhost:8080")
        elif not self.server_info:
            recommendations.append("⚠️ Server status unclear. Consider implementing health check endpoints")
            
        # Performance recommendations
        if self.results:
            slow_tests = [r for r in self.results if r.duration > 30.0]  # Tests taking more than 30s
            if slow_tests:
                recommendations.append(f"⏱️ {len(slow_tests)} tests are running slowly (>30s). Consider optimization")
                
        # Failure pattern recommendations
        failed_tests = [r for r in self.results if r.status == "FAIL"]
        if failed_tests:
            categories_with_failures = set(r.category for r in failed_tests)
            if "Engine Tests" in categories_with_failures:
                recommendations.append("🤖 Engine test failures detected. Check model availability and server configuration")
            if "Document Processing" in categories_with_failures:
                recommendations.append("📄 Document processing issues. Verify test files exist and are accessible")
            if "Agent System" in categories_with_failures:
                recommendations.append("🤖 Agent system failures. Check API compatibility and authentication")
        
        # Success rate recommendations
        total_tests = len(self.results)
        passed = len([r for r in self.results if r.status == "PASS"])
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        
        if success_rate < 50:
            recommendations.append("🚨 Low success rate (<50%). Review server setup and test configuration")
        elif success_rate < 80:
            recommendations.append("⚠️ Moderate success rate (<80%). Some components may need attention")
        elif success_rate >= 95:
            recommendations.append("🎉 Excellent success rate! System appears to be functioning well")
            
        return recommendations
        
    def print_detailed_summary(self):
        """Print a comprehensive test summary."""
        total_duration = time.time() - self.start_time
        
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("="*80)
        
        # Server Status Summary
        print("\n🖥️  SERVER STATUS:")
        if self.server_status is True:
            print("   ✅ Server is responding")
            if self.server_info:
                for key, value in self.server_info.items():
                    print(f"   • {key}: {value}")
        elif self.server_status is False:
            print("   ❌ Server is not responding")
        else:
            print("   ❓ Server status unknown")
            
        # Overall Statistics
        total_tests = len(self.results)
        passed = len([r for r in self.results if r.status == "PASS"])
        failed = len([r for r in self.results if r.status == "FAIL"])
        skipped = len([r for r in self.results if r.status == "SKIP"])
        warnings = len([r for r in self.results if r.status == "WARNING"])
        
        print(f"\n📈 OVERALL STATISTICS:")
        print(f"   • Total Tests: {total_tests}")
        print(f"   • Passed: {passed} ({passed/total_tests*100:.1f}%)" if total_tests > 0 else "   • Passed: 0")
        print(f"   • Failed: {failed} ({failed/total_tests*100:.1f}%)" if total_tests > 0 else "   • Failed: 0")
        print(f"   • Skipped: {skipped} ({skipped/total_tests*100:.1f}%)" if total_tests > 0 else "   • Skipped: 0")
        print(f"   • Warnings: {warnings} ({warnings/total_tests*100:.1f}%)" if total_tests > 0 else "   • Warnings: 0")
        print(f"   • Total Duration: {total_duration:.2f}s")
        print(f"   • Average Test Duration: {sum(r.duration for r in self.results)/total_tests:.2f}s" if total_tests > 0 else "   • Average Test Duration: 0s")
        
        # Category Breakdown
        categories = list(set(r.category for r in self.results))
        if categories:
            print(f"\n📋 CATEGORY BREAKDOWN:")
            for category in sorted(categories):
                summary = self.get_category_summary(category)
                print(f"\n   {category.upper()}:")
                print(f"     • Tests: {summary['total']}")
                print(f"     • Passed: {summary['passed']} | Failed: {summary['failed']} | Skipped: {summary['skipped']} | Warnings: {summary['warnings']}")
                print(f"     • Duration: {summary['total_duration']:.2f}s (avg: {summary['avg_duration']:.2f}s)")
                
                # Show status for each test in category
                category_results = [r for r in self.results if r.category == category]
                for result in category_results:
                    status_emoji = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️", "WARNING": "⚠️"}.get(result.status, "❓")
                    print(f"       {status_emoji} {result.name} ({result.duration:.2f}s)")
                    if result.error_message:
                        print(f"         └─ Error: {result.error_message[:100]}...")
        
        # Failed Tests Detail
        failed_tests = [r for r in self.results if r.status == "FAIL"]
        if failed_tests:
            print(f"\n❌ FAILED TESTS DETAIL:")
            for i, result in enumerate(failed_tests, 1):
                print(f"\n   {i}. {result.name} ({result.category})")
                print(f"      Time: {result.timestamp} | Duration: {result.duration:.2f}s")
                if result.error_message:
                    print(f"      Error: {result.error_message}")
                if result.details:
                    print(f"      Details: {result.details}")
        
        # Performance Analysis
        if self.results:
            slowest_tests = sorted(self.results, key=lambda x: x.duration, reverse=True)[:5]
            print(f"\n⏱️  SLOWEST TESTS:")
            for i, result in enumerate(slowest_tests, 1):
                print(f"   {i}. {result.name}: {result.duration:.2f}s ({result.category})")
        
        # Final Status
        print(f"\n🎯 FINAL RESULT:")
        if failed == 0 and total_tests > 0:
            print("   🎉 ALL TESTS PASSED!")
        elif failed > 0:
            print(f"   ⚠️  {failed} TEST(S) FAILED")
        else:
            print("   ❓ NO TESTS WERE RUN")
            
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        print(f"   📊 Success Rate: {success_rate:.1f}%")
        
        # Recommendations
        recommendations = self.get_recommendations()
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        print("="*80)

def check_server_status(test_summary: TestSummary):
    """Check server status and available models"""
    # Try different common endpoints to check server availability
    endpoints_to_try = [
        "http://localhost:8080/status",
        "http://localhost:8080/api/status", 
        "http://localhost:8080/health",
        "http://localhost:8080/api/health",
        "http://localhost:8080/v1/models",
        "http://localhost:8080/api/v1/models"
    ]
    
    server_info = {}
    
    for endpoint in endpoints_to_try:
        try:
            print(f"Trying endpoint: {endpoint}")
            response = requests.get(endpoint, timeout=10)
            if response.status_code == 200:
                print(f"✅ Server is responding at: {endpoint}")
                try:
                    data = response.json()
                    print("\nServer Status:")
                    if "engines" in data:
                        print("  Available Engines:")
                        server_info["available_engines"] = len(data["engines"])
                        for engine in data["engines"]:
                            print(f"    - {engine['engine_id']}: {engine['status']}")
                    if "node_manager" in data:
                        nm = data["node_manager"]
                        print(f"  Node Manager: {nm.get('autoscaling', 'unknown')} autoscaling")
                        print(f"  Loaded Engines: {nm.get('loaded_engines', 0)}")
                        print(f"  Total Engines: {nm.get('total_engines', 0)}")
                        server_info["loaded_engines"] = nm.get('loaded_engines', 0)
                        server_info["total_engines"] = nm.get('total_engines', 0)
                    if "data" in data:  # For models endpoint
                        print("  Available Models:")
                        server_info["available_models"] = len(data["data"])
                        for model in data["data"]:
                            print(f"    - {model.get('id', 'unknown')}")
                    print(f"Response content: {data}")
                    server_info["responding_endpoint"] = endpoint
                except json.JSONDecodeError:
                    print(f"Response (non-JSON): {response.text[:200]}")
                test_summary.set_server_status(True, server_info)
                return True
            else:
                print(f"❌ {endpoint} returned: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} failed: {e}")
    
    # If no status endpoint works, try a simple connection test
    try:
        print("Trying basic connection test...")
        response = requests.get("http://localhost:8080/", timeout=10)
        if response.status_code in [200, 404, 405]:  # Server is responding
            print(f"✅ Server is running (returned {response.status_code})")
            print("⚠️  No status endpoint found, but server appears to be running")
            server_info["basic_connection"] = True
            server_info["status_code"] = response.status_code
            test_summary.set_server_status(True, server_info)
            return True
    except Exception as e:
        print(f"❌ Basic connection failed: {e}")
    
    print("❌ Server is not available or not responding to any known endpoints")
    test_summary.set_server_status(False)
    return False

# Initialize test summary system
test_summary = TestSummary()

print("="*80)
print("KOLOSAL SERVER TEST SUITE")
print("="*80)

# Check server status first
server_available = check_server_status(test_summary)

print("\nConfiguration:")
print("  Server: http://localhost:8080")
print("  Authentication: Enabled (API Key: Not Required)")  
print("  Rate Limiting: 100 requests/60s")
print("  Testing multiple endpoints to determine server capabilities...")
print("="*80)

# Model configuration based on actual server response
LLM_MODEL = "qwen3-0.6b"  # Only available LLM model
# Note: These models may not be available on current server instance
LLM_MODEL_ALT = "gpt-3.5-turbo"  # Alternative LLM model (may not be available)
EMBEDDING_MODEL = "text-embedding-3-small"  # Small embedding model (may not be available)
EMBEDDING_MODEL_LARGE = "text-embedding-3-large"  # Large embedding model (may not be available)

if not server_available:
    print("\n⚠️  Server status check failed, but server might still be running.")
    print("The server may not have a status endpoint, but other API endpoints might work.")
    print("Proceeding with tests... (tests may fail if server is actually down)")
    print("="*80)

print("\n" + "="*60)
print("ENGINE TESTS")
print("="*60)

# Test engine completion
completion_test = CompletionTest()

print("\n--- Testing Primary LLM Model (qwen3-0.6b) ---")
# Basic completion test
test_summary.run_test(
    "Basic Completion (qwen3-0.6b)", 
    "Engine Tests",
    completion_test.basic_completion,
    model_name=LLM_MODEL,
    temperature=0.7,
    max_tokens=128
)

# Streaming completion test
test_summary.run_test(
    "Streaming Completion (qwen3-0.6b)", 
    "Engine Tests",
    completion_test.stream_completion,
    model_name=LLM_MODEL,
    temperature=0.7,
    max_tokens=128
)

# Check if streaming test failed and run diagnostic
streaming_test_result = next((r for r in test_summary.results if r.name == "Streaming Completion (qwen3-0.6b)"), None)
if streaming_test_result and streaming_test_result.status == "FAIL":
    print("\n⚠️  Streaming test failed. Running diagnostic tests...")
    
    # Test if non-streaming works with same parameters
    print("🔍 Testing non-streaming completion with same parameters...")
    diagnostic_result = test_summary.run_test(
        "Diagnostic: Non-streaming with same params", 
        "Engine Tests",
        completion_test.basic_completion,
        model_name=LLM_MODEL,
        temperature=0.7,
        max_tokens=128
    )
    
    if diagnostic_result:
        print("✅ Non-streaming works - issue is specifically with streaming implementation")
        test_summary.add_manual_result(
            "Streaming Diagnosis", 
            "Engine Tests", 
            "WARNING", 
            0.0,
            "Streaming failed but non-streaming works - server streaming issue"
        )
    else:
        print("❌ Both streaming and non-streaming failed - broader model/server issue")
        test_summary.add_manual_result(
            "Streaming Diagnosis", 
            "Engine Tests", 
            "FAIL", 
            0.0,
            "Both streaming and non-streaming failed"
        )

# Concurrent completion test
test_summary.run_test(
    "Concurrent Completion (qwen3-0.6b)", 
    "Engine Tests",
    completion_test.concurrent_completion,
    model_name=LLM_MODEL,
    temperature=0.7,
    max_tokens=128
)

# Test engine embedding
embedding_test = EmbeddingTest()

print("\n--- Testing Small Embedding Model (text-embedding-3-small) ---")
print("Warning: This model may not be available on current server instance")
# Basic embedding test
test_summary.run_test(
    "Basic Embedding (text-embedding-3-small)", 
    "Engine Tests",
    embedding_test.basic_embedding,
    model_name=EMBEDDING_MODEL,
    input_text="Hello, world!"
)

# Concurrent embedding test
test_summary.run_test(
    "Concurrent Embedding (text-embedding-3-small)", 
    "Engine Tests",
    embedding_test.concurrent_embedding,
    model_name=EMBEDDING_MODEL,
    input_texts=[
        "Hello, world!",
        "The quick brown fox jumps over the lazy dog.",
        "Machine learning is transforming technology.",
        "Natural language processing enables computers to understand text.",
        "Embeddings convert text into numerical vectors."
    ]
)

# Test large embedding model
print("\n--- Testing Large Embedding Model (text-embedding-3-large) ---")
print("Warning: This model may not be available on current server instance")
test_summary.run_test(
    "Basic Embedding (text-embedding-3-large)", 
    "Engine Tests",
    embedding_test.basic_embedding,
    model_name=EMBEDDING_MODEL_LARGE,
    input_text="Testing large embedding model with Kolosal Server."
)

# Show progress summary after engine tests
test_summary.print_quick_summary()

# Test alternative LLM model
print("\n--- Testing Alternative LLM Model (gpt-3.5-turbo) ---")
print("Warning: This model may not be available on current server instance")
test_summary.run_test(
    "Basic Completion (gpt-3.5-turbo)", 
    "Engine Tests",
    completion_test.basic_completion,
    model_name=LLM_MODEL_ALT,
    temperature=0.7,
    max_tokens=128
)

print("\n" + "="*60)
print("DOCUMENT PROCESSING TESTS")
print("="*60)

# Test PDF parsing
parse_pdf_test = ParsePDFTest()

# Basic PDF parsing test
test_summary.run_test_manual(
    "Basic PDF Parsing", 
    "Document Processing",
    parse_pdf_test.test_parse_pdf,
    path="test_files/test_pdf.pdf"
)

# Concurrent PDF parsing test
test_summary.run_test_manual(
    "Concurrent PDF Parsing", 
    "Document Processing",
    parse_pdf_test.concurrent_parse_pdf,
    pdf_paths=[
        "test_files/test_pdf1.pdf",
        "test_files/test_pdf2.pdf",
        "test_files/test_pdf3.pdf",
        "test_files/test_pdf4.pdf",
        "test_files/test_pdf5.pdf"
    ]
)

# Test DOCX parsing
parse_docx_test = ParseDOCXTest()

# Basic DOCX parsing test
test_summary.run_test_manual(
    "Basic DOCX Parsing", 
    "Document Processing",
    parse_docx_test.test_parse_docx,
    path="test_files/test_docx.docx"
)

# Concurrent DOCX parsing test
test_summary.run_test_manual(
    "Concurrent DOCX Parsing", 
    "Document Processing",
    parse_docx_test.concurrent_parse_docx,
    docx_paths=[
        "test_files/test_docx1.docx",
        "test_files/test_docx2.docx",
        "test_files/test_docx3.docx",
        "test_files/test_docx4.docx",
        "test_files/test_docx5.docx"
    ]
)

# Show progress summary after document processing tests
test_summary.print_quick_summary()

print("\n" + "="*60)
print("DOCUMENT INGESTION & RETRIEVAL TESTS")
print("="*60)

# Test document ingestion
document_ingestion_test = DocumentIngestionTest()

test_summary.run_test_manual(
    "Document Ingestion", 
    "Document Management",
    document_ingestion_test.test_ingest_document
)

# Test document retrieval
document_retrieval_test = DocumentRetrievalTest()

# Basic document retrieval test
test_summary.run_test_manual(
    "Basic Document Retrieval", 
    "Document Management",
    document_retrieval_test.retrieve_documents,
    query="smartphone",
    limit=5,
    score_threshold=0.5
)

# Concurrent document retrieval test
test_summary.run_test_manual(
    "Concurrent Document Retrieval", 
    "Document Management",
    document_retrieval_test.concurrent_retrieve_documents
)

# Custom concurrent retrieval test
test_summary.run_test_manual(
    "Custom Concurrent Retrieval", 
    "Document Management",
    document_retrieval_test.custom_concurrent_retrieve
)

# Show progress summary after document management tests
test_summary.print_quick_summary()

print("\n" + "="*60)
print("AGENT SYSTEM TESTS")
print("="*60)

# Server configuration matching Kolosal Server setup
SERVER_CONFIG = {
    "url": "http://localhost:8080",  # Kolosal Server host and port
    "api_key": None,  # API key not required based on config
    "timeout": 300,   # Match idle timeout
    "auth_enabled": True,  # Auth is enabled
    "rate_limit": {
        "max_requests": 100,
        "window": 60
    }
}

# Initialize agent testers with server configuration
SERVER_URL = SERVER_CONFIG["url"]
API_KEY = SERVER_CONFIG["api_key"]

# Test Agent Features
print("\n--- Testing Agent Features ---")
agent_tester = KolosalAgentTester(base_url=SERVER_URL, api_key=API_KEY)

test_summary.run_test_manual(
    "Agent Features Test", 
    "Agent System",
    agent_tester.run_all_tests,
    skip_auth=True, 
    skip_rag=False
)

# Test RAG Features
print("\n--- Testing RAG Features ---")
rag_tester = RAGTester(base_url=SERVER_URL, api_key=API_KEY)

test_summary.run_test_manual(
    "RAG Features Test", 
    "Agent System",
    rag_tester.run_all_rag_tests
)

# Test Workflow Features
print("\n--- Testing Workflow Features ---")
workflow_tester = WorkflowTester(base_url=SERVER_URL, api_key=API_KEY)

test_summary.run_test_manual(
    "Workflow Features Test", 
    "Agent System",
    workflow_tester.run_all_workflow_tests
)

# Generate and display comprehensive test summary
test_summary.print_detailed_summary()

print("\n" + "="*60)
print("ALL TESTS COMPLETED")
print("="*60)