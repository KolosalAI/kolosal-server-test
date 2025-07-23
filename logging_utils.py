"""
Enhanced logging utility for Kolosal Server Test Suite.

This module provides comprehensive logging capabilities that track:
- Which endpoint is being tested
- JSON request payloads
- Response data and status codes
- Performance metrics
- Error details

All logs are written to both console and log files for comprehensive tracking.
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
import requests


def extract_id_from_response(response_data: Dict[str, Any], id_field_name: str = "id") -> Optional[str]:
    """
    Extract ID from response data, handling various response structures.
    
    This function checks multiple possible locations for IDs in API responses:
    - data.{id_field_name}
    - data.{id_field_name}_id (e.g., data.agent_id for agent)
    - {id_field_name}
    - {id_field_name}_id
    - data.id (fallback)
    - id (fallback)
    
    Args:
        response_data: The parsed JSON response data
        id_field_name: The base name for the ID field (e.g., "agent", "workflow", "job")
        
    Returns:
        The extracted ID string, or None if not found
    """
    if not isinstance(response_data, dict):
        return None
    
    # List of possible ID field locations to check
    possible_locations = [
        # Check data.{field}_id first (e.g., data.agent_id)
        ("data", f"{id_field_name}_id"),
        # Check data.{field} (e.g., data.agent)
        ("data", id_field_name),
        # Check data.id (common fallback)
        ("data", "id"),
        # Check root level {field}_id (e.g., agent_id)
        (None, f"{id_field_name}_id"),
        # Check root level {field} (e.g., agent)
        (None, id_field_name),
        # Check root level id (final fallback)
        (None, "id")
    ]
    
    for container, field in possible_locations:
        if container:
            # Check inside a container (e.g., data.agent_id)
            value = response_data.get(container, {}).get(field)
        else:
            # Check at root level (e.g., agent_id)
            value = response_data.get(field)
        
        if value and isinstance(value, str):
            return value
    
    return None


class EndpointLogger:
    """Enhanced logger for tracking endpoint testing details."""
    
    def __init__(self, log_file: str = "endpoint_tests.log"):
        """Initialize the endpoint logger."""
        self.log_file = log_file
        self.setup_logging()
        
    def setup_logging(self):
        """Set up logging configuration."""
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Set up file handler
        self.file_handler = logging.FileHandler(log_dir / self.log_file, mode='a', encoding='utf-8')
        self.file_handler.setLevel(logging.INFO)
        
        # Set up console handler
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        self.file_handler.setFormatter(formatter)
        self.console_handler.setFormatter(formatter)
        
        # Set up logger
        self.logger = logging.getLogger('endpoint_logger')
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Add handlers
        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.console_handler)
        
    def log_endpoint_test(
        self,
        test_name: str,
        endpoint: str,
        method: str,
        request_data: Optional[Dict[str, Any]] = None,
        response: Optional[requests.Response] = None,
        response_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        duration: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log comprehensive endpoint test details.
        
        Args:
            test_name: Name of the test being performed
            endpoint: The API endpoint being tested
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            request_data: JSON request payload
            response: Response object from requests
            response_data: Parsed response JSON data
            error: Error message if test failed
            duration: Request duration in seconds
            metadata: Additional test metadata
        """
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "test_name": test_name,
            "endpoint": endpoint,
            "method": method.upper(),
            "success": error is None and (response is None or response.status_code < 400),
        }
        
        # Add request details
        if request_data is not None:
            log_entry["request"] = {
                "payload": self._sanitize_data(request_data),
                "size_bytes": len(json.dumps(request_data).encode('utf-8'))
            }
        
        # Add response details
        if response is not None:
            log_entry["response"] = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "size_bytes": len(response.content) if response.content else 0
            }
            
            # Add response data if provided
            if response_data is not None:
                log_entry["response"]["data"] = self._sanitize_data(response_data)
        
        # Add performance metrics
        if duration is not None:
            log_entry["performance"] = {
                "duration_seconds": round(duration, 3),
                "requests_per_second": round(1.0 / duration, 2) if duration > 0 else 0
            }
        
        # Add error details
        if error:
            log_entry["error"] = error
        
        # Add metadata
        if metadata:
            log_entry["metadata"] = metadata
        
        # Log to console with formatted output
        self._log_to_console(log_entry)
        
        # Log to file with full JSON
        self._log_to_file(log_entry)
    
    def _log_to_console(self, log_entry: Dict[str, Any]):
        """Log formatted output to console."""
        status = "✅ PASS" if log_entry["success"] else "❌ FAIL"
        endpoint_info = f"{log_entry['method']} {log_entry['endpoint']}"
        
        message = f"[{status}] {log_entry['test_name']} - {endpoint_info}"
        
        # Add request size info
        if "request" in log_entry:
            req_size = log_entry["request"]["size_bytes"]
            message += f" | Request: {req_size}B"
        
        # Add response info
        if "response" in log_entry:
            resp_code = log_entry["response"]["status_code"]
            resp_size = log_entry["response"]["size_bytes"]
            message += f" | Response: {resp_code} ({resp_size}B)"
        
        # Add performance info
        if "performance" in log_entry:
            duration = log_entry["performance"]["duration_seconds"]
            message += f" | Duration: {duration}s"
        
        # Add error info
        if "error" in log_entry:
            message += f" | Error: {log_entry['error']}"
        
        self.logger.info(message)
        
        # Log request payload if present
        if "request" in log_entry and log_entry["request"]["payload"]:
            payload_str = json.dumps(log_entry["request"]["payload"], indent=2)
            self.logger.info(f"📤 Request Payload:\n{payload_str}")
        
        # Log response data if present (both success and failure for debugging)
        if ("response" in log_entry and 
            "data" in log_entry["response"]):
            response_str = json.dumps(log_entry["response"]["data"], indent=2)
            # Truncate very long responses
            if len(response_str) > 1000:
                response_str = response_str[:1000] + "... [truncated]"
            
            if log_entry["success"]:
                self.logger.info(f"📥 Response Data:\n{response_str}")
            else:
                self.logger.info(f"📥 Error Response Data:\n{response_str}")
        
        # Log error response even if no structured data
        elif not log_entry["success"] and "response" in log_entry:
            resp_code = log_entry["response"]["status_code"]
            self.logger.info(f"📥 HTTP {resp_code} Response (no JSON data available)")
    
    def _log_to_file(self, log_entry: Dict[str, Any]):
        """Log full JSON entry to file."""
        json_str = json.dumps(log_entry, indent=2, ensure_ascii=False)
        self.logger.info(f"ENDPOINT_TEST_ENTRY: {json_str}")
    
    def _sanitize_data(self, data: Any) -> Any:
        """Sanitize data for logging (remove sensitive information)."""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                # Hide sensitive data
                if key.lower() in ['password', 'api_key', 'token', 'secret', 'auth']:
                    sanitized[key] = "[HIDDEN]"
                elif isinstance(value, (dict, list)):
                    sanitized[key] = self._sanitize_data(value)
                elif isinstance(value, str) and len(value) > 1000:
                    # Truncate very long strings (like base64 data)
                    sanitized[key] = value[:100] + f"... [truncated {len(value)} chars]"
                else:
                    sanitized[key] = value
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        else:
            return data
    
    def log_test_start(self, test_suite: str, description: str = ""):
        """Log the start of a test suite."""
        separator = "=" * 80
        self.logger.info(f"\n{separator}")
        self.logger.info(f"🚀 STARTING TEST SUITE: {test_suite}")
        if description:
            self.logger.info(f"📝 Description: {description}")
        self.logger.info(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(separator)
    
    def log_test_end(self, test_suite: str, summary: Optional[Dict[str, Any]] = None):
        """Log the end of a test suite."""
        separator = "=" * 80
        self.logger.info(separator)
        self.logger.info(f"🏁 COMPLETED TEST SUITE: {test_suite}")
        if summary:
            # Enhanced summary logging with failure analysis
            total = summary.get("total_tests", 0)
            passed = summary.get("passed", 0)
            failed = summary.get("failed", 0)
            skipped = summary.get("skipped", 0)
            warnings = summary.get("warnings", 0)
            
            # Calculate additional metrics
            if total > 0:
                success_rate = (passed / total) * 100
                failure_rate = (failed / total) * 100
                
                # Log summary with insights
                summary_log = {
                    "overview": {
                        "total_tests": total,
                        "passed": passed,
                        "failed": failed,
                        "skipped": skipped,
                        "warnings": warnings,
                        "success_rate": f"{success_rate:.1f}%",
                        "failure_rate": f"{failure_rate:.1f}%"
                    },
                    "insights": []
                }
                
                # Add performance insights
                if failed > passed:
                    summary_log["insights"].append("⚠️ More tests failed than passed - system may have significant issues")
                elif failed > 0:
                    summary_log["insights"].append(f"⚠️ {failed} test(s) failed - check individual test logs for details")
                elif passed == total:
                    summary_log["insights"].append("✅ All tests passed successfully")
                    
                if skipped > 0:
                    summary_log["insights"].append(f"ℹ️ {skipped} test(s) were skipped")
                if warnings > 0:
                    summary_log["insights"].append(f"⚠️ {warnings} test(s) had warnings")
                
                # Add the original summary data
                summary_log.update(summary)
                
                self.logger.info(f"📊 Summary: {json.dumps(summary_log, indent=2)}")
            else:
                self.logger.info(f"📊 Summary: {json.dumps(summary, indent=2)}")
        self.logger.info(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(separator)


# Global logger instance
endpoint_logger = EndpointLogger()


class RequestTracker:
    """Context manager for tracking HTTP requests with automatic logging."""
    
    def __init__(
        self,
        test_name: str,
        endpoint: str,
        method: str,
        request_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.test_name = test_name
        self.endpoint = endpoint
        self.method = method
        self.request_data = request_data
        self.metadata = metadata
        self.start_time = None
        self.response = None
        self.error = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time if self.start_time else None
        
        # Handle exceptions
        if exc_type is not None:
            self.error = str(exc_val)
        
        # Parse response data if available
        response_data = None
        if self.response:
            try:
                response_data = self.response.json()
            except (ValueError, json.JSONDecodeError):
                response_data = {"raw_content": self.response.text[:500]}
        
        # Log the request
        endpoint_logger.log_endpoint_test(
            test_name=self.test_name,
            endpoint=self.endpoint,
            method=self.method,
            request_data=self.request_data,
            response=self.response,
            response_data=response_data,
            error=self.error,
            duration=duration,
            metadata=self.metadata
        )
    
    def set_response(self, response: requests.Response):
        """Set the response object."""
        self.response = response
    
    def set_error(self, error: str):
        """Set an error message."""
        self.error = error
