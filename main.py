"""Main test script for Kolosal Server.

Enhanced with comprehensive test summary and reporting features:
- Automated test result tracking with timing and status
- Categorized test organization (Engine Tests, Document Processing, etc.)
- Detailed summary with performance analysis and recommendations
- Progress tracking during test execution
- Server status integration with test results
- Failed test diagnostics and error reporting
- Success rate calculation and performance insights
- Aligned with actual Kolosal Server configuration
- Comprehensive endpoint logging with request/response tracking
- Dual logging to both terminal and tests.log file
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

# Import configuration and logging
from config import SERVER_CONFIG, MODELS, ENDPOINTS, get_full_url, get_model_config
from logging_utils import endpoint_logger

import requests
import json
import time
import logging
import sys
import io
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path

class TestLogger:
    """Dual logging class that writes to both terminal and tests.log file.
    
    Also captures stdout to ensure all print statements are logged.
    """
    
    def __init__(self, log_file: str = "tests.log"):
        self.log_file = log_file
        self.original_stdout = sys.stdout
        self.setup_file_logging()
        self.setup_stdout_capture()
        
    def setup_file_logging(self):
        """Setup file logging configuration."""
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Setup file logger
        self.file_logger = logging.getLogger("test_logger")
        self.file_logger.setLevel(logging.INFO)
        
        # Remove any existing handlers to avoid duplicates
        self.file_logger.handlers.clear()
        
        # Create file handler
        file_handler = logging.FileHandler(self.log_file, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.file_logger.addHandler(file_handler)
        
    def setup_stdout_capture(self):
        """Setup stdout capture to log all print statements."""
        class StdoutCapture:
            def __init__(self, logger_instance):
                self.logger_instance = logger_instance
                self.original_stdout = logger_instance.original_stdout
                
            def write(self, text):
                # Write to original stdout (terminal)
                self.original_stdout.write(text)
                self.original_stdout.flush()
                
                # Write to log file (skip empty lines and whitespace-only content)
                if text.strip():
                    # Remove newlines for logging since the logger adds its own
                    clean_text = text.rstrip('\n\r')
                    if clean_text:
                        self.logger_instance.file_logger.info(clean_text)
                        
            def flush(self):
                self.original_stdout.flush()
                
        # Replace stdout with our capture
        sys.stdout = StdoutCapture(self)
        
    def restore_stdout(self):
        """Restore original stdout."""
        sys.stdout = self.original_stdout
        
    def print_and_log(self, message: str, level: str = "INFO"):
        """Print message to terminal and write to log file."""
        # Print to terminal (will be captured by stdout capture)
        print(message)
    
    def log_separator(self, char: str = "=", length: int = 80):
        """Log a separator line to both terminal and file."""
        separator = char * length
        self.print_and_log(separator)
    
    def log_section(self, title: str, char: str = "=", length: int = 80):
        """Log a section header to both terminal and file."""
        separator = char * length
        self.print_and_log(separator)
        self.print_and_log(title)
        self.print_and_log(separator)

# Initialize dual logger
test_logger = TestLogger()

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
        test_logger.print_and_log(f"\n🧪 Running: {test_name}")
        start_time = time.time()
        
        try:
            result = test_func(*args, **kwargs)
            duration = time.time() - start_time
            
            if result is False:
                self.add_result(test_name, category, "FAIL", duration, 
                              details="Test function returned False")
                test_logger.print_and_log(f"❌ {test_name} - FAILED ({duration:.2f}s)", "ERROR")
                return False
            else:
                self.add_result(test_name, category, "PASS", duration,
                              details="Test completed successfully")
                test_logger.print_and_log(f"✅ {test_name} - PASSED ({duration:.2f}s)")
                return True
                
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            self.add_result(test_name, category, "FAIL", duration,
                          error_message=error_msg)
            test_logger.print_and_log(f"❌ {test_name} - FAILED ({duration:.2f}s)", "ERROR")
            test_logger.print_and_log(f"   Error: {error_msg}", "ERROR")
            return False
    
    def run_test_manual(self, test_name: str, category: str, test_func, *args, **kwargs):
        """Run a test function and track its result based on return value and exceptions.
        
        This method handles tests that:
        - Return True/False to indicate success/failure
        - Use assert statements that raise AssertionError on failure  
        - Complete without exceptions (assumed success)
        - Raise other exceptions (treated as failure)
        """
        test_logger.print_and_log(f"\n🧪 Running: {test_name}")
        start_time = time.time()
        
        try:
            result = test_func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Check if the test function returned a boolean result
            if result is False:
                self.add_result(test_name, category, "FAIL", duration,
                              details="Test function returned False")
                test_logger.print_and_log(f"❌ {test_name} - FAILED ({duration:.2f}s)", "ERROR")
                return False
            elif result is True:
                self.add_result(test_name, category, "PASS", duration,
                              details="Test function returned True")
                test_logger.print_and_log(f"✅ {test_name} - PASSED ({duration:.2f}s)")
                return True
            else:
                # If no clear boolean result, assume success if no exception was thrown
                self.add_result(test_name, category, "PASS", duration,
                              details="Test completed without exceptions")
                test_logger.print_and_log(f"✅ {test_name} - COMPLETED ({duration:.2f}s)")
                return True
        except AssertionError as e:
            duration = time.time() - start_time
            error_msg = str(e)
            self.add_result(test_name, category, "FAIL", duration,
                          error_message=f"Assertion failed: {error_msg}")
            test_logger.print_and_log(f"❌ {test_name} - FAILED ({duration:.2f}s)", "ERROR")
            test_logger.print_and_log(f"   Assertion Error: {error_msg}", "ERROR")
            return False
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            self.add_result(test_name, category, "FAIL", duration,
                          error_message=error_msg)
            test_logger.print_and_log(f"❌ {test_name} - FAILED ({duration:.2f}s)", "ERROR")
            test_logger.print_and_log(f"   Error: {error_msg}", "ERROR")
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
        
        test_logger.print_and_log(f"\n📊 Quick Summary: {passed}/{total_tests} tests passed, {failed} failed")
        
    def get_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        # Server connectivity recommendations
        if self.server_status is False:
            recommendations.append("🔧 Server is not responding. Check if Kolosal Server is running on 127.0.0.1:8080")
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
        
        test_logger.print_and_log("\n" + "="*80)
        test_logger.print_and_log("📊 COMPREHENSIVE TEST SUMMARY")
        test_logger.print_and_log("="*80)
        
        # Server Status Summary
        test_logger.print_and_log("\n🖥️  SERVER STATUS:")
        if self.server_status is True:
            test_logger.print_and_log("   ✅ Server is responding")
            if self.server_info:
                for key, value in self.server_info.items():
                    test_logger.print_and_log(f"   • {key}: {value}")
        elif self.server_status is False:
            test_logger.print_and_log("   ❌ Server is not responding")
        else:
            test_logger.print_and_log("   ❓ Server status unknown")
            
        # Overall Statistics
        total_tests = len(self.results)
        passed = len([r for r in self.results if r.status == "PASS"])
        failed = len([r for r in self.results if r.status == "FAIL"])
        skipped = len([r for r in self.results if r.status == "SKIP"])
        warnings = len([r for r in self.results if r.status == "WARNING"])
        
        test_logger.print_and_log(f"\n📈 OVERALL STATISTICS:")
        test_logger.print_and_log(f"   • Total Tests: {total_tests}")
        test_logger.print_and_log(f"   • Passed: {passed} ({passed/total_tests*100:.1f}%)" if total_tests > 0 else "   • Passed: 0")
        test_logger.print_and_log(f"   • Failed: {failed} ({failed/total_tests*100:.1f}%)" if total_tests > 0 else "   • Failed: 0")
        test_logger.print_and_log(f"   • Skipped: {skipped} ({skipped/total_tests*100:.1f}%)" if total_tests > 0 else "   • Skipped: 0")
        test_logger.print_and_log(f"   • Warnings: {warnings} ({warnings/total_tests*100:.1f}%)" if total_tests > 0 else "   • Warnings: 0")
        test_logger.print_and_log(f"   • Total Duration: {total_duration:.2f}s")
        test_logger.print_and_log(f"   • Average Test Duration: {sum(r.duration for r in self.results)/total_tests:.2f}s" if total_tests > 0 else "   • Average Test Duration: 0s")
        
        # Category Breakdown
        categories = list(set(r.category for r in self.results))
        if categories:
            test_logger.print_and_log(f"\n📋 CATEGORY BREAKDOWN:")
            for category in sorted(categories):
                summary = self.get_category_summary(category)
                test_logger.print_and_log(f"\n   {category.upper()}:")
                test_logger.print_and_log(f"     • Tests: {summary['total']}")
                test_logger.print_and_log(f"     • Passed: {summary['passed']} | Failed: {summary['failed']} | Skipped: {summary['skipped']} | Warnings: {summary['warnings']}")
                test_logger.print_and_log(f"     • Duration: {summary['total_duration']:.2f}s (avg: {summary['avg_duration']:.2f}s)")
                
                # Show status for each test in category
                category_results = [r for r in self.results if r.category == category]
                for result in category_results:
                    status_emoji = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️", "WARNING": "⚠️"}.get(result.status, "❓")
                    test_logger.print_and_log(f"       {status_emoji} {result.name} ({result.duration:.2f}s)")
                    if result.error_message:
                        test_logger.print_and_log(f"         └─ Error: {result.error_message[:100]}...")
        
        # Failed Tests Detail
        failed_tests = [r for r in self.results if r.status == "FAIL"]
        if failed_tests:
            test_logger.print_and_log(f"\n❌ FAILED TESTS DETAIL:")
            for i, result in enumerate(failed_tests, 1):
                test_logger.print_and_log(f"\n   {i}. {result.name} ({result.category})")
                test_logger.print_and_log(f"      Time: {result.timestamp} | Duration: {result.duration:.2f}s")
                if result.error_message:
                    test_logger.print_and_log(f"      Error: {result.error_message}")
                if result.details:
                    test_logger.print_and_log(f"      Details: {result.details}")
        
        # Performance Analysis
        if self.results:
            slowest_tests = sorted(self.results, key=lambda x: x.duration, reverse=True)[:5]
            test_logger.print_and_log(f"\n⏱️  SLOWEST TESTS:")
            for i, result in enumerate(slowest_tests, 1):
                test_logger.print_and_log(f"   {i}. {result.name}: {result.duration:.2f}s ({result.category})")
        
        # Final Status
        test_logger.print_and_log(f"\n🎯 FINAL RESULT:")
        if failed == 0 and total_tests > 0:
            test_logger.print_and_log("   🎉 ALL TESTS PASSED!")
        elif failed > 0:
            test_logger.print_and_log(f"   ⚠️  {failed} TEST(S) FAILED", "WARNING")
        else:
            test_logger.print_and_log("   ❓ NO TESTS WERE RUN")
            
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        test_logger.print_and_log(f"   📊 Success Rate: {success_rate:.1f}%")
        
        # Recommendations
        recommendations = self.get_recommendations()
        if recommendations:
            test_logger.print_and_log(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                test_logger.print_and_log(f"   {i}. {rec}")
        
        test_logger.print_and_log("="*80)

def check_server_status(test_summary: TestSummary):
    """Check server status and available models - Updated for Kolosal Server configuration"""
    # Based on server log, use actual Kolosal Server endpoints
    endpoints_to_try = [
        get_full_url("health"),
        get_full_url("models"),
        get_full_url("engines"), 
        get_full_url("metrics"),
        get_full_url("agents_health")
    ]
    
    server_info = {}
    
    for endpoint in endpoints_to_try:
        try:
            test_logger.print_and_log(f"Trying endpoint: {endpoint}")
            response = requests.get(endpoint, timeout=SERVER_CONFIG["request_timeout"])
            if response.status_code == 200:
                test_logger.print_and_log(f"✅ Server is responding at: {endpoint}")
                try:
                    data = response.json()
                    test_logger.print_and_log("\nServer Status:")
                    if "engines" in data:
                        test_logger.print_and_log("  Available Engines:")
                        server_info["available_engines"] = len(data["engines"])
                        for engine in data["engines"]:
                            test_logger.print_and_log(f"    - {engine['engine_id']}: {engine['status']}")
                    if "node_manager" in data:
                        nm = data["node_manager"]
                        test_logger.print_and_log(f"  Node Manager: {nm.get('autoscaling', 'unknown')} autoscaling")
                        test_logger.print_and_log(f"  Loaded Engines: {nm.get('loaded_engines', 0)}")
                        test_logger.print_and_log(f"  Total Engines: {nm.get('total_engines', 0)}")
                        server_info["loaded_engines"] = nm.get('loaded_engines', 0)
                        server_info["total_engines"] = nm.get('total_engines', 0)
                    if "data" in data:  # For models endpoint
                        test_logger.print_and_log("  Available Models:")
                        server_info["available_models"] = len(data["data"])
                        for model in data["data"]:
                            test_logger.print_and_log(f"    - {model.get('id', 'unknown')}")
                    if "status" in data:  # For health endpoint
                        test_logger.print_and_log(f"  Health Status: {data.get('status', 'unknown')}")
                        server_info["health_status"] = data.get('status')
                    test_logger.print_and_log(f"Response content: {data}")
                    server_info["responding_endpoint"] = endpoint
                except json.JSONDecodeError:
                    test_logger.print_and_log(f"Response (non-JSON): {response.text[:200]}")
                test_summary.set_server_status(True, server_info)
                return True
            else:
                test_logger.print_and_log(f"❌ {endpoint} returned: {response.status_code}")
        except Exception as e:
            test_logger.print_and_log(f"❌ {endpoint} failed: {e}")
    
    # If no status endpoint works, try a simple connection test
    try:
        test_logger.print_and_log("Trying basic connection test...")
        response = requests.get(SERVER_CONFIG["base_url"], timeout=SERVER_CONFIG["request_timeout"])
        if response.status_code in [200, 404, 405]:  # Server is responding
            test_logger.print_and_log(f"✅ Server is running (returned {response.status_code})")
            test_logger.print_and_log("⚠️  No status endpoint found, but server appears to be running")
            server_info["basic_connection"] = True
            server_info["status_code"] = response.status_code
            test_summary.set_server_status(True, server_info)
            return True
    except Exception as e:
        test_logger.print_and_log(f"❌ Basic connection failed: {e}")
    
    test_logger.print_and_log("❌ Server is not available or not responding to any known endpoints")
    test_summary.set_server_status(False)
    return False

# Initialize test summary system
test_summary = TestSummary()

try:
    # Start comprehensive endpoint logging
    endpoint_logger.log_test_start(
        "Kolosal Server Complete Test Suite",
        "Comprehensive testing of all server endpoints with detailed request/response logging"
    )

    test_logger.log_section("KOLOSAL SERVER TEST SUITE")

    # Check server status first
    server_available = check_server_status(test_summary)

    test_logger.print_and_log("\nConfiguration:")
    test_logger.print_and_log(f"  Server: {SERVER_CONFIG['base_url']}")
    test_logger.print_and_log(f"  Authentication: Enabled (API Key: {'Required' if SERVER_CONFIG['api_key'] else 'Not Required'})")  
    test_logger.print_and_log(f"  Rate Limiting: {SERVER_CONFIG['rate_limit']['max_requests']} requests/{SERVER_CONFIG['rate_limit']['window_seconds']}s")
    test_logger.print_and_log("  Testing multiple endpoints to determine server capabilities...")
    test_logger.print_and_log("  Enhanced logging: Capturing all endpoint requests and responses")
    test_logger.print_and_log("  Dual logging: Writing to both terminal and tests.log file")
    test_logger.log_separator()

    # Model configuration based on actual server response from server log
    LLM_MODEL = MODELS["primary_llm"]  # qwen3-0.6b - Primary available LLM model
    LLM_MODEL_ALT = MODELS["alt_llm"]  # gpt-3.5-turbo - Alternative LLM model (same file)
    EMBEDDING_MODEL = MODELS["embedding_small"]  # text-embedding-3-small 
    EMBEDDING_MODEL_LARGE = MODELS["embedding_large"]  # text-embedding-3-large

    if not server_available:
        test_logger.print_and_log("\n⚠️  Server status check failed, but server might still be running.", "WARNING")
        test_logger.print_and_log("The server may not have a status endpoint, but other API endpoints might work.")
        test_logger.print_and_log("Proceeding with tests... (tests may fail if server is actually down)")
        test_logger.log_separator()

    test_logger.log_section("ENGINE TESTS", "=", 60)

    # Test engine completion
    completion_test = CompletionTest()

    test_logger.print_and_log("\n--- Testing Primary LLM Model (qwen3-0.6b) ---")
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
        test_logger.print_and_log("\n⚠️  Streaming test failed. Running diagnostic tests...", "WARNING")
        
        # Test if non-streaming works with same parameters
        test_logger.print_and_log("🔍 Testing non-streaming completion with same parameters...")
        diagnostic_result = test_summary.run_test(
            "Diagnostic: Non-streaming with same params", 
            "Engine Tests",
            completion_test.basic_completion,
            model_name=LLM_MODEL,
            temperature=0.7,
            max_tokens=128
        )
        
        if diagnostic_result:
            test_logger.print_and_log("✅ Non-streaming works - issue is specifically with streaming implementation")
            test_summary.add_manual_result(
                "Streaming Diagnosis", 
                "Engine Tests", 
                "WARNING", 
                0.0,
                "Streaming failed but non-streaming works - server streaming issue"
            )
        else:
            test_logger.print_and_log("❌ Both streaming and non-streaming failed - broader model/server issue")
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

    test_logger.print_and_log("\n--- Testing Small Embedding Model (text-embedding-3-small) ---")
    test_logger.print_and_log("Warning: This model may not be available on current server instance", "WARNING")
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
    test_logger.print_and_log("\n--- Testing Large Embedding Model (text-embedding-3-large) ---")
    test_logger.print_and_log("Warning: This model may not be available on current server instance", "WARNING")
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
    test_logger.print_and_log("\n--- Testing Alternative LLM Model (gpt-3.5-turbo) ---")
    test_logger.print_and_log("Warning: This model may not be available on current server instance", "WARNING")
    test_summary.run_test(
        "Basic Completion (gpt-3.5-turbo)", 
        "Engine Tests",
        completion_test.basic_completion,
        model_name=LLM_MODEL_ALT,
        temperature=0.7,
        max_tokens=128
    )

    test_logger.log_section("DOCUMENT PROCESSING TESTS", "=", 60)

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

    test_logger.log_section("DOCUMENT INGESTION & RETRIEVAL TESTS", "=", 60)

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

    test_logger.log_section("AGENT SYSTEM TESTS", "=", 60)

    # Initialize agent testers with server configuration from config.py
    SERVER_URL = SERVER_CONFIG["base_url"]
    API_KEY = SERVER_CONFIG["api_key"]

    # Test Agent Features
    test_logger.print_and_log("\n--- Testing Agent Features ---")
    agent_tester = KolosalAgentTester(base_url=SERVER_URL, api_key=API_KEY)

    test_summary.run_test_manual(
        "Agent Features Test", 
        "Agent System",
        agent_tester.run_all_tests
    )

    # Test RAG Features
    test_logger.print_and_log("\n--- Testing RAG Features ---")
    rag_tester = RAGTester(base_url=SERVER_URL, api_key=API_KEY)

    test_summary.run_test_manual(
        "RAG Features Test", 
        "Agent System",
        rag_tester.run_all_rag_tests
    )

    # Test Workflow Features
    test_logger.print_and_log("\n--- Testing Workflow Features ---")
    workflow_tester = WorkflowTester(base_url=SERVER_URL, api_key=API_KEY)

    test_summary.run_test_manual(
        "Workflow Features Test", 
        "Agent System",
        workflow_tester.run_all_workflow_tests
    )

    # Generate and display comprehensive test summary
    test_summary.print_detailed_summary()

    # End comprehensive endpoint logging
    endpoint_logger.log_test_end(
        "Kolosal Server Complete Test Suite",
        {
            "total_tests": len(test_summary.results),
            "passed": sum(1 for test in test_summary.results if test.status == "PASS"),
            "failed": sum(1 for test in test_summary.results if test.status == "FAIL"),
            "skipped": sum(1 for test in test_summary.results if test.status == "SKIP"),
            "warnings": sum(1 for test in test_summary.results if test.status == "WARNING"),
            "completion_time": datetime.now().isoformat()
        }
    )

    test_logger.log_section("ALL TESTS COMPLETED", "=", 60)
    test_logger.print_and_log("Enhanced logging complete - check logs/ directory for detailed endpoint logs")
    test_logger.print_and_log("Test results logged to tests.log file")
    test_logger.log_separator()
    
finally:
    # Restore original stdout
    test_logger.restore_stdout()