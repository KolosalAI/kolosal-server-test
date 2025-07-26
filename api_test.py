#!/usr/bin/env python3
"""
Enhanced API test script for Kolosal Server
Integrates with the existing test infrastructure and follows codebase patterns.
"""

import requests
import json
import base64
import time
import os
from datetime import datetime
from typing import Optional, Dict, List, Any

# Import from existing codebase
from config import SERVER_CONFIG, MODELS, ENDPOINTS, get_full_url
from logging_utils import endpoint_logger


class KolosalServerTester:
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or SERVER_CONFIG["base_url"]
        self.api_key = api_key or SERVER_CONFIG.get("api_key")
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'KolosalServerTester/1.0'
        })
        
        # Add authentication if required
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'X-API-Key': self.api_key
            })

    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} - {level} - {message}")

    def make_tracked_request(self, method: str, endpoint: str, test_name: str, **kwargs) -> requests.Response:
        """Make a request with endpoint tracking"""
        url = f"{self.base_url}{endpoint}"
        
        # Use endpoint logger for comprehensive tracking
        return endpoint_logger.make_request(
            test_name=test_name,
            method=method,
            url=url,
            session=self.session,
            **kwargs
        )

    def test_health(self) -> bool:
        """Test server health endpoint"""
        try:
            response = self.make_tracked_request(
                method="GET",
                endpoint="/health",
                test_name="Health Check",
                timeout=10
            )
            
            if response.status_code == 200:
                self.log("Health check: PASS")
                return True
            else:
                self.log(f"Health check: FAIL - HTTP {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Health check: FAIL - {str(e)}", "ERROR")
            return False

    def test_pdf_parsing(self) -> bool:
        """Test PDF parsing endpoint using existing test files"""
        try:
            # Try to use existing test files first
            test_pdf_path = "test_files/test_pdf.pdf"
            pdf_data_b64 = None
            
            if os.path.exists(test_pdf_path):
                with open(test_pdf_path, 'rb') as f:
                    pdf_data = f.read()
                pdf_data_b64 = base64.b64encode(pdf_data).decode('utf-8')
                self.log(f"Using test file: {test_pdf_path}")
            else:
                # Fallback to minimal PDF content
                pdf_data_b64 = self._create_minimal_pdf_b64()
                self.log("Using generated minimal PDF content")
            
            payload = {
                "data": pdf_data_b64,
                "method": "fast",
                "language": "eng"
            }
            
            response = self.make_tracked_request(
                method="POST",
                endpoint="/parse-pdf",
                test_name="PDF Parsing Test",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                extracted_text = result.get('data', {}).get('extracted_text', '')
                self.log(f"PDF parsing test: PASS - Extracted {len(extracted_text)} characters")
                return True
            else:
                try:
                    error_data = response.json()
                    self.log(f"PDF parsing test: FAIL - HTTP {response.status_code}: {json.dumps(error_data)}", "ERROR")
                except:
                    self.log(f"PDF parsing test: FAIL - HTTP {response.status_code}: {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"PDF parsing test: FAIL - {str(e)}", "ERROR")
            return False

    def test_embedding_generation(self) -> bool:
        """Test embedding generation endpoint"""
        try:
            # Use configured embedding model
            embedding_model = MODELS.get("embedding_small", "text-embedding-3-small")
            
            payload = {
                "model": embedding_model,
                "input": "This is a test sentence for embedding generation.",
                "encoding_format": "float"
            }
            
            response = self.make_tracked_request(
                method="POST",
                endpoint="/v1/embeddings",
                test_name="Embedding Generation Test",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                embeddings = result.get('data', [])
                if embeddings and len(embeddings) > 0:
                    embedding_dim = len(embeddings[0].get('embedding', []))
                    self.log(f"Embedding generation test: PASS - Generated embedding with {embedding_dim} dimensions")
                    return True
                else:
                    self.log("Embedding generation test: FAIL - No embeddings in response", "ERROR")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log(f"Embedding generation test: FAIL - HTTP {response.status_code}: {json.dumps(error_data)}", "ERROR")
                except:
                    self.log(f"Embedding generation test: FAIL - HTTP {response.status_code}: {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Embedding generation test: FAIL - {str(e)}", "ERROR")
            return False

    def test_chat_completion(self) -> bool:
        """Test chat completion endpoint"""
        try:
            # Use configured LLM model
            llm_model = MODELS.get("primary_llm", "qwen3-0.6b")
            
            payload = {
                "model": llm_model,
                "messages": [
                    {"role": "user", "content": "Hello! Please respond with a simple greeting."}
                ],
                "max_tokens": 50,
                "temperature": 0.7
            }
            
            response = self.make_tracked_request(
                method="POST",
                endpoint="/v1/chat/completions",
                test_name="Chat Completion Test",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                choices = result.get('choices', [])
                if choices and len(choices) > 0:
                    content = choices[0].get('message', {}).get('content', '')
                    self.log(f"Chat completion test: PASS - Generated {len(content)} characters")
                    return True
                else:
                    self.log("Chat completion test: FAIL - No choices in response", "ERROR")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log(f"Chat completion test: FAIL - HTTP {response.status_code}: {json.dumps(error_data)}", "ERROR")
                except:
                    self.log(f"Chat completion test: FAIL - HTTP {response.status_code}: {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Chat completion test: FAIL - {str(e)}", "ERROR")
            return False

    def test_document_management(self) -> bool:
        """Test document upload and search"""
        try:
            # Test document upload
            test_content = {
                "content": "This is a test document for the Kolosal Server API testing. It contains information about artificial intelligence and machine learning technologies.",
                "title": "API Test Document",
                "metadata": {
                    "category": "test",
                    "type": "api_test",
                    "created_by": "api_tester"
                }
            }
            
            # Upload document
            upload_response = self.make_tracked_request(
                method="POST",
                endpoint="/documents",
                test_name="Document Upload Test",
                json=test_content,
                timeout=30
            )
            
            upload_success = upload_response.status_code == 200
            doc_id = None
            
            if upload_success:
                upload_result = upload_response.json()
                doc_id = upload_result.get('id') or upload_result.get('document_id')
                self.log(f"Document upload: PASS - Document ID: {doc_id}")
            else:
                self.log(f"Document upload: FAIL - HTTP {upload_response.status_code}", "ERROR")
            
            # Test document search
            search_payload = {
                "query": "artificial intelligence machine learning",
                "limit": 5
            }
            
            search_response = self.make_tracked_request(
                method="POST",
                endpoint="/search",
                test_name="Document Search Test",
                json=search_payload,
                timeout=30
            )
            
            search_success = search_response.status_code == 200
            
            if search_success:
                search_result = search_response.json()
                results = search_result.get('results', [])
                self.log(f"Document search: PASS - Found {len(results)} results")
            else:
                self.log(f"Document search: FAIL - HTTP {search_response.status_code}", "ERROR")
            
            return upload_success and search_success
            
        except Exception as e:
            self.log(f"Document management test: FAIL - {str(e)}", "ERROR")
            return False

    def test_vector_search(self) -> bool:
        """Test vector search endpoints"""
        try:
            # Test text-based vector search
            payload = {
                "query": "test search query for vector similarity",
                "limit": 5,
                "collection": "default"
            }
            
            response = self.make_tracked_request(
                method="POST",
                endpoint="/vector-search",
                test_name="Vector Search Test",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                results = result.get('results', [])
                self.log(f"Vector search test: PASS - Found {len(results)} results")
                return True
            else:
                try:
                    error_data = response.json()
                    self.log(f"Vector search test: FAIL - HTTP {response.status_code}: {json.dumps(error_data)}", "ERROR")
                except:
                    self.log(f"Vector search test: FAIL - HTTP {response.status_code}: {response.text}", "ERROR")
                return False
            
        except Exception as e:
            self.log(f"Vector search test: FAIL - {str(e)}", "ERROR")
            return False

    def _create_minimal_pdf_b64(self) -> str:
        """Create minimal valid PDF content as base64"""
        minimal_pdf = "JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSA0IDAgUgo+Pgo+PgovQ29udGVudHMgNSAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9iago1IDAgb2JqCjw8Ci9MZW5ndGggNDQKPj4Kc3RyZWFtCkJUCi9GMSA0OCBUZgoyMCA3MjAgVGQKKEhlbGxvIFdvcmxkKSBUagoKRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMTUgMDAwMDAgbiAKMDAwMDAwMDA2NiAwMDAwMCBuIAowMDAwMDAwMTI0IDAwMDAwIG4gCjAwMDAwMDAyNzEgMDAwMDAgbiAKMDAwMDAwMDMzOCAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDYKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjQzMwolJUVPRgo="
        return minimal_pdf

    def run_all_tests(self) -> bool:
        """Run all tests and return overall success"""
        self.log("=" * 50)
        self.log("STARTING KOLOSAL SERVER API TESTS")
        self.log("=" * 50)
        
        # Start comprehensive endpoint logging
        endpoint_logger.log_test_start("Kolosal Server API Test Suite", {
            "base_url": self.base_url,
            "timestamp": datetime.now().isoformat()
        })
        
        tests = [
            ("Health Check", self.test_health),
            ("Chat Completion", self.test_chat_completion),
            ("Embedding Generation", self.test_embedding_generation),
            ("PDF Parsing", self.test_pdf_parsing),
            ("Document Management", self.test_document_management),
            ("Vector Search", self.test_vector_search)
        ]
        
        results = {}
        for test_name, test_func in tests:
            self.log(f"Running {test_name} test...")
            try:
                start_time = time.time()
                result = test_func()
                elapsed_time = time.time() - start_time
                results[test_name] = result
                
                # Log individual test completion
                endpoint_logger.log_test_end(f"{test_name} Test", {
                    "success": result,
                    "elapsed_time": elapsed_time
                })
                
            except Exception as e:
                self.log(f"{test_name} test failed with exception: {str(e)}", "ERROR")
                results[test_name] = False
                
                # Log test failure
                endpoint_logger.log_test_end(f"{test_name} Test", {
                    "success": False,
                    "error": str(e)
                })
            
            time.sleep(1)  # Brief pause between tests
        
        # Summary
        self.log("=" * 50)
        self.log("TEST RESULTS SUMMARY")
        self.log("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            status_symbol = "✅" if result else "❌"
            self.log(f"{status_symbol} {test_name}: {status}")
            if result:
                passed += 1
        
        success_rate = (passed / total) * 100
        self.log("=" * 50)
        self.log(f"OVERALL RESULT: {passed}/{total} tests passed ({success_rate:.1f}%)")
        
        # End comprehensive endpoint logging
        endpoint_logger.log_test_end("Kolosal Server API Test Suite", {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": success_rate,
            "completion_time": datetime.now().isoformat()
        })
        
        overall_success = passed == total
        if overall_success:
            self.log("🎉 ALL TESTS PASSED!")
        else:
            self.log(f"⚠️  {total - passed} TEST(S) FAILED")
        
        self.log("=" * 50)
        
        return overall_success


def main():
    """Main function to run the API tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Kolosal Server API Test Suite')
    parser.add_argument('--base-url', default=None, 
                       help=f'Server base URL (default: {SERVER_CONFIG["base_url"]})')
    parser.add_argument('--api-key', default=None,
                       help='API key for authentication (if required)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Initialize tester
    tester = KolosalServerTester(
        base_url=args.base_url,
        api_key=args.api_key
    )
    
    # Run tests
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
