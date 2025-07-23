"""Base Class for Kolosal Server API Test"""
import json
import time
import requests
from typing import Optional, Dict, Any, Union
from openai import OpenAI, AsyncOpenAI
from logging_utils import endpoint_logger, RequestTracker


class KolosalTestBase():
    """Base Class for Kolosal Server API Test with Enhanced Logging"""

    client: OpenAI
    async_client: AsyncOpenAI

    def __init__(self, base_url: Optional[str] = "http://127.0.0.1:8080",
                 api_key: Optional[str] = None) -> None:
        """Initialize the KolosalTestBase with optional base URL and API key.
        
        Default configuration aligns with Kolosal Server:
        - Host: 127.0.0.1:8080 (localhost only as per server config)
        - API Key: None (not required as per server config)
        """
        # Set default API key if none provided (OpenAI client requires one)
        if api_key is None:
            api_key = "not-required"
            
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        self.async_client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key
        )
        
        # Store base configuration for logging
        self.base_url = base_url
        self.api_key = api_key
        
        # Set up requests session for HTTP testing
        self.session = requests.Session()
        if api_key and api_key != "not-required":
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'X-API-Key': api_key
            })
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'KolosalTestSuite/1.0'
        })
    
    def make_tracked_request(
        self,
        test_name: str,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = 30.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """
        Make an HTTP request with comprehensive logging.
        
        Args:
            test_name: Name of the test being performed
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (with or without leading slash)
            json_data: JSON payload to send
            params: URL parameters
            headers: Additional headers
            timeout: Request timeout in seconds
            metadata: Additional metadata for logging
            
        Returns:
            requests.Response object
        """
        # Normalize endpoint
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        
        # Construct full URL
        url = f"{self.base_url.rstrip('/')}{endpoint}"
        
        # Prepare request data for logging
        request_data = {}
        if json_data:
            request_data.update(json_data)
        if params:
            request_data["_url_params"] = params
        
        # Use request tracker for automatic logging
        with RequestTracker(
            test_name=test_name,
            endpoint=endpoint,
            method=method,
            request_data=request_data,
            metadata=metadata
        ) as tracker:
            try:
                # Merge headers
                request_headers = self.session.headers.copy()
                if headers:
                    request_headers.update(headers)
                
                # Make the request
                response = self.session.request(
                    method=method.upper(),
                    url=url,
                    json=json_data,
                    params=params,
                    headers=request_headers,
                    timeout=timeout
                )
                
                # Set response in tracker
                tracker.set_response(response)
                
                return response
                
            except requests.exceptions.RequestException as e:
                tracker.set_error(f"Request failed: {str(e)}")
                raise
            except Exception as e:
                tracker.set_error(f"Unexpected error: {str(e)}")
                raise
    
    def log_test_start(self, test_name: str, description: str = ""):
        """Log the start of a test."""
        endpoint_logger.log_test_start(test_name, description)
    
    def log_test_end(self, test_name: str, summary: Optional[Dict[str, Any]] = None):
        """Log the end of a test."""
        endpoint_logger.log_test_end(test_name, summary)
