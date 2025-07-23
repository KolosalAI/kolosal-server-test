#!/usr/bin/env python3
"""
RAG and Document Management test suite for Kolosal Server.

This script tests document indexing, retrieval, and RAG functionality including:
- Document upload and indexing
- Vector search and similarity matching
- PDF parsing and text extraction
- Embedding generation
- Context retrieval for agents
- Collection management
- Qdrant integration
- Document metadata handling

Enhanced with comprehensive endpoint logging.

Usage:
    python test_rag_features.py [options]
"""

import requests
import json
import base64
import time
import os
import tempfile
import sys
from typing import Dict, List, Optional, Any
import logging

# Add parent directory to path to import logging utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from logging_utils import endpoint_logger, RequestTracker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGTester:
    def __init__(self, base_url: str = "http://127.0.0.1:8080", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'X-API-Key': api_key
            })
        self.session.headers.update({'Content-Type': 'application/json'})
        self.test_collections = []
        self.test_documents = []
    
    def make_tracked_request(self, test_name: str, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with comprehensive logging."""
        url = f"{self.base_url}{endpoint}"
        json_data = kwargs.get('json', {})
        
        # Log the request details
        logger.info(f"🔄 Making request: {method} {url}")
        if json_data:
            logger.info(f"📤 Request payload: {json.dumps(json_data, indent=2)}")
        
        with RequestTracker(
            test_name=test_name,
            endpoint=endpoint,
            method=method,
            request_data=json_data
        ) as tracker:
            try:
                response = self.session.request(method, url, **kwargs)
                tracker.set_response(response)
                
                # Log the response details
                logger.info(f"📥 Response status: {response.status_code}")
                try:
                    response_json = response.json()
                    logger.info(f"📄 Response content: {json.dumps(response_json, indent=2)}")
                except (json.JSONDecodeError, ValueError):
                    logger.info(f"📄 Response content (text): {response.text[:500]}...")
                
                return response
            except Exception as e:
                tracker.set_error(f"Request failed: {str(e)}")
                logger.error(f"❌ Request failed: {method} {url} - {e}")
                raise

    def create_test_pdf_content(self) -> str:
        """Create a simple test PDF content as base64"""
        # This is a minimal PDF content for testing
        pdf_content = """
        Test Document for RAG System
        
        This is a comprehensive test document for the Kolosal Server RAG system.
        It contains various types of content to test document processing capabilities.
        
        Section 1: Introduction to AI
        Artificial Intelligence (AI) is a field of computer science that aims to create
        intelligent machines that can perform tasks typically requiring human intelligence.
        
        Section 2: Machine Learning
        Machine Learning is a subset of AI that enables computers to learn and improve
        from experience without being explicitly programmed for every task.
        
        Section 3: Deep Learning
        Deep Learning uses neural networks with multiple layers to model and understand
        complex patterns in data, revolutionizing fields like computer vision and NLP.
        
        Section 4: Applications
        AI applications include:
        - Natural Language Processing
        - Computer Vision
        - Robotics
        - Autonomous Vehicles
        - Healthcare Diagnosis
        - Financial Trading
        
        Conclusion:
        The future of AI holds tremendous potential for transforming various industries
        and improving human life through intelligent automation and decision-making.
        """
        return base64.b64encode(pdf_content.encode()).decode()

    def test_document_upload(self):
        """Test document upload and indexing using proper API format"""
        try:
            # Use format from api_test.py reference
            test_content = {
                "content": "This is a test document for the Kolosal Server API testing. It contains information about artificial intelligence and machine learning technologies.",
                "title": "API Test Document",
                "metadata": {
                    "category": "test",
                    "type": "api_test",
                    "created_by": "api_tester"
                }
            }
            
            response = self.make_tracked_request(
                test_name="Document Upload Test",
                method="POST",
                endpoint="/documents",
                json=test_content
            )
            
            if response.status_code == 200:
                result = response.json()
                doc_id = result.get('id') or result.get('document_id')
                if doc_id:
                    self.test_documents.append(doc_id)
                    logger.info(f"✅ Document upload test: PASS - Document ID: {doc_id}")
                    return True
                else:
                    logger.error(f"❌ Document upload test: FAIL - No document ID in response")
                    return False
            else:
                try:
                    error_data = response.json()
                    logger.error(f"❌ Document upload test: FAIL - HTTP {response.status_code}: {json.dumps(error_data)}")
                except:
                    logger.error(f"❌ Document upload test: FAIL - HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Document upload test: FAIL - {str(e)}")
            return False

    def test_document_file_upload(self):
        """Test document file upload"""
        import tempfile
        
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document for file upload. It contains sample content about autonomous vehicles and self-driving technology.")
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as file:
                files = {'file': file}
                data = {'type': 'text'}
                
                response = self.session.post(f"{self.base_url}/documents/upload", files=files, data=data)
                
            if response.status_code == 200:
                result = response.json()
                doc_id = result.get('id') or result.get('document_id')
                if doc_id:
                    self.test_documents.append(doc_id)
                    logger.info(f"✅ File upload test: PASS - Document ID: {doc_id}")
                    success = True
                else:
                    logger.error(f"❌ File upload test: FAIL - No document ID in response")
                    success = False
            else:
                logger.error(f"❌ File upload test: FAIL - HTTP {response.status_code}: {response.text[:200]}")
                success = False
                
        except Exception as e:
            logger.error(f"❌ File upload test failed: {e}")
            success = False
        finally:
            # Clean up temp file
            import os
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
        return success

    def test_document_retrieval(self):
        """Test document search and retrieval using proper API format"""
        try:
            # Use search payload format from api_test.py reference
            search_payload = {
                "query": "artificial intelligence machine learning",
                "limit": 5
            }
            
            response = self.make_tracked_request(
                test_name="Document Search Test",
                method="POST",
                endpoint="/search",
                json=search_payload
            )
            
            if response.status_code == 200:
                search_result = response.json()
                results = search_result.get('results', [])
                logger.info(f"✅ Document search test: PASS - Found {len(results)} results")
                
                # Log some details about the results
                for i, doc in enumerate(results[:2]):  # Show first 2 results
                    score = doc.get('score', 'N/A')
                    title = doc.get('title', doc.get('metadata', {}).get('title', 'Untitled'))
                    logger.info(f"   Result {i+1}: {title} (score: {score})")
                return True
            else:
                try:
                    error_data = response.json()
                    logger.error(f"❌ Document search test: FAIL - HTTP {response.status_code}: {json.dumps(error_data)}")
                except:
                    logger.error(f"❌ Document search test: FAIL - HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Document search test: FAIL - {str(e)}")
            return False

    def test_pdf_parsing(self):
        """Test PDF parsing functionality"""
        try:
            # Create minimal PDF content (following api_test.py pattern)
            minimal_pdf_b64 = "JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKPj4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSA0IDAgUgo+Pgo+PgovQ29udGVudHMgNSAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9iago1IDAgb2JqCjw8Ci9MZW5ndGggNDQKPj4Kc3RyZWFtCkJUCi9GMSA0OCBUZgoyMCA3MjAgVGQKKEhlbGxvIFdvcmxkKSBUagoKRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMTUgMDAwMDAgbiAKMDAwMDAwMDA2NiAwMDAwMCBuIAowMDAwMDAwMTI0IDAwMDAwIG4gCjAwMDAwMDAyNzEgMDAwMDAgbiAKMDAwMDAwMDMzOCAwMDAwMCBuIAp0cmFpbGVyCjw8Ci9TaXplIDYKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjQzMwolJUVPRgo="
            
            payload = {
                "data": minimal_pdf_b64,
                "method": "fast",
                "language": "eng"
            }
            
            response = self.session.post(f"{self.base_url}/parse-pdf", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                extracted_text = result.get('data', {}).get('extracted_text', '')
                pages_processed = result.get('data', {}).get('pages_processed', 0)
                
                logger.info(f"✅ PDF parsing test: PASS - Extracted {len(extracted_text)} characters")
                if pages_processed > 0:
                    logger.info(f"   Pages processed: {pages_processed}")
                return True
            else:
                try:
                    error_data = response.json()
                    logger.error(f"❌ PDF parsing test: FAIL - HTTP {response.status_code}: {json.dumps(error_data)}")
                except:
                    logger.error(f"❌ PDF parsing test: FAIL - HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ PDF parsing test: FAIL - {str(e)}")
            return False

    def test_embedding_generation(self):
        """Test embedding generation"""
        try:
            test_texts = [
                "Machine learning algorithms are revolutionizing data analysis",
                "Deep neural networks enable complex pattern recognition",
                "Natural language processing helps computers understand human language"
            ]
            
            # Use proper OpenAI API format (following api_test.py pattern)
            payload = {
                "model": "text-embedding-3-small",  # Use configured model
                "input": test_texts[0],  # Test with single text first
                "encoding_format": "float"
            }
            
            response = self.session.post(f"{self.base_url}/v1/embeddings", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                embeddings = result.get('data', [])
                
                if embeddings and len(embeddings) > 0:
                    embedding_dim = len(embeddings[0].get('embedding', []))
                    logger.info(f"✅ Embedding generation test: PASS - Generated embedding with {embedding_dim} dimensions")
                    return True
                else:
                    logger.error(f"❌ Embedding generation test: FAIL - No embeddings in response")
                    return False
            else:
                try:
                    error_data = response.json()
                    logger.error(f"❌ Embedding generation test: FAIL - HTTP {response.status_code}: {json.dumps(error_data)}")
                except:
                    logger.error(f"❌ Embedding generation test: FAIL - HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Embedding generation test: FAIL - {str(e)}")
            return False

    def test_collection_management(self):
        """Test collection management operations"""
        collection_name = f"test_collection_{int(time.time())}"
        
        try:
            # Test create collection
            create_payload = {
                "name": collection_name,
                "description": "Test collection for RAG system",
                "metadata": {
                    "created_by": "rag_tester",
                    "purpose": "testing"
                }
            }
            
            response = self.session.post(f"{self.base_url}/api/v1/collections", json=create_payload)
            create_success = response.status_code in [200, 201]
            
            if create_success:
                self.test_collections.append(collection_name)
            
            # Test list collections
            response = self.session.get(f"{self.base_url}/api/v1/collections")
            list_success = response.status_code == 200
            
            collections = []
            if list_success:
                result = response.json()
                collections = result.get('data', {}).get('collections', [])
            
            # Test get collection info
            response = self.session.get(f"{self.base_url}/api/v1/collections/{collection_name}")
            info_success = response.status_code == 200
            
            collection_info = {}
            if info_success:
                collection_info = response.json().get('data', {})
            
            overall_success = create_success and list_success
            logger.info(f"Collection management test: {'PASS' if overall_success else 'FAIL'}")
            logger.info(f"Create: {create_success}, List: {list_success} ({len(collections)} collections), Info: {info_success}")
            
            return overall_success
            
        except Exception as e:
            logger.error(f"Collection management test failed: {e}")
            return False

    def test_vector_search(self):
        """Test vector similarity search"""
        try:
            # Use payload format from api_test.py reference
            payload = {
                "query": "test search query for vector similarity",
                "limit": 5,
                "collection": "default"
            }
            
            response = self.session.post(f"{self.base_url}/vector-search", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                results = result.get('results', [])
                logger.info(f"✅ Vector search test: PASS - Found {len(results)} results")
                return True
            else:
                try:
                    error_data = response.json()
                    logger.error(f"❌ Vector search test: FAIL - HTTP {response.status_code}: {json.dumps(error_data)}")
                except:
                    logger.error(f"❌ Vector search test: FAIL - HTTP {response.status_code}: {response.text}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Vector search test: FAIL - {str(e)}")
            return False

    def test_context_retrieval_for_agents(self):
        """Test context retrieval specifically for agent use"""
        try:
            context_queries = [
                {
                    "query": "How does AI help in healthcare diagnosis?",
                    "context_type": "qa",
                    "max_context_length": 1000,
                    "include_metadata": True,
                    "collection_name": self.test_collections[0] if self.test_collections else "test_rag_collection"
                },
                {
                    "query": "What are the benefits of autonomous vehicles?",
                    "context_type": "informational",
                    "max_context_length": 800,
                    "include_metadata": True,
                    "collection_name": self.test_collections[0] if self.test_collections else "test_rag_collection"
                }
            ]
            
            success_count = 0
            for i, query_data in enumerate(context_queries):
                try:
                    response = self.session.post(f"{self.base_url}/context-retrieval", json=query_data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        context = result.get('data', {}).get('context', '')
                        sources = result.get('data', {}).get('sources', [])
                        
                        if context and len(context) > 50:  # Reasonable context length
                            success_count += 1
                            logger.info(f"Context retrieval {i+1}: PASS - Context length: {len(context)}, sources: {len(sources)}")
                        else:
                            logger.warning(f"Context retrieval {i+1}: PARTIAL - Insufficient context")
                    else:
                        logger.error(f"Context retrieval {i+1}: FAIL - HTTP {response.status_code}")
                        
                except Exception as e:
                    logger.error(f"Context retrieval {i+1} failed: {e}")
            
            overall_success = success_count > 0
            logger.info(f"Context retrieval test: {'PASS' if overall_success else 'FAIL'} - {success_count}/{len(context_queries)} retrievals succeeded")
            return overall_success
            
        except Exception as e:
            logger.error(f"Context retrieval test failed: {e}")
            return False

    def test_document_metadata_filtering(self):
        """Test document filtering by metadata"""
        try:
            filter_queries = [
                {
                    "query": "artificial intelligence",
                    "filters": {
                        "category": "healthcare"
                    },
                    "k": 5,
                    "collection_name": self.test_collections[0] if self.test_collections else "test_rag_collection"
                },
                {
                    "query": "machine learning",
                    "filters": {
                        "keywords": {"$in": ["AI", "diagnostics"]}
                    },
                    "k": 3,
                    "collection_name": self.test_collections[0] if self.test_collections else "test_rag_collection"
                },
                {
                    "query": "technology",
                    "filters": {
                        "date": {"$gte": "2024-01-01"}
                    },
                    "k": 10,
                    "collection_name": self.test_collections[0] if self.test_collections else "test_rag_collection"
                }
            ]
            
            success_count = 0
            for i, filter_data in enumerate(filter_queries):
                try:
                    response = self.session.post(f"{self.base_url}/vector-search", json=filter_data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        documents = result.get('data', {}).get('documents', [])
                        
                        # Check if returned documents match the filter criteria
                        valid_results = True
                        if filter_data['filters'].get('category'):
                            expected_category = filter_data['filters']['category']
                            for doc in documents:
                                doc_category = doc.get('metadata', {}).get('category')
                                if doc_category != expected_category:
                                    valid_results = False
                                    break
                        
                        if valid_results:
                            success_count += 1
                            logger.info(f"Metadata filtering {i+1}: PASS - Found {len(documents)} filtered documents")
                        else:
                            logger.warning(f"Metadata filtering {i+1}: PARTIAL - Filter criteria not properly applied")
                    else:
                        logger.error(f"Metadata filtering {i+1}: FAIL - HTTP {response.status_code}")
                        
                except Exception as e:
                    logger.error(f"Metadata filtering {i+1} failed: {e}")
            
            overall_success = success_count > 0
            logger.info(f"Metadata filtering test: {'PASS' if overall_success else 'FAIL'} - {success_count}/{len(filter_queries)} filters succeeded")
            return overall_success
            
        except Exception as e:
            logger.error(f"Metadata filtering test failed: {e}")
            return False

    def test_bulk_operations(self):
        """Test bulk document operations"""
        try:
            # Test bulk document upload
            bulk_documents = []
            for i in range(10):
                bulk_documents.append({
                    "text": f"Bulk test document {i+1}. This document contains information about topic {i+1} related to artificial intelligence and machine learning applications in various industries.",
                    "metadata": {
                        "source": f"bulk_doc_{i+1}.txt",
                        "batch": "bulk_test",
                        "index": i+1,
                        "category": "bulk_test"
                    }
                })
            
            bulk_payload = {
                "documents": bulk_documents,
                "collection_name": "bulk_test_collection",
                "batch_size": 5,
                "auto_index": True
            }
            
            response = self.session.post(f"{self.base_url}/api/v1/documents/bulk", json=bulk_payload)
            upload_success = response.status_code == 200
            
            if upload_success:
                result = response.json()
                indexed_count = result.get('data', {}).get('indexed_count', 0)
                self.test_collections.append("bulk_test_collection")
                
                # Test bulk retrieval
                bulk_retrieval_payload = {
                    "queries": [
                        "artificial intelligence applications",
                        "machine learning industries",
                        "topic technology systems"
                    ],
                    "k": 3,
                    "collection_name": "bulk_test_collection"
                }
                
                response = self.session.post(f"{self.base_url}/retrieve-bulk", json=bulk_retrieval_payload)
                retrieval_success = response.status_code == 200
                
                success = upload_success and retrieval_success
                logger.info(f"Bulk operations test: {'PASS' if success else 'FAIL'}")
                logger.info(f"Upload: {upload_success} ({indexed_count} docs), Retrieval: {retrieval_success}")
                
                return success
            else:
                logger.error(f"Bulk operations test: FAIL - Upload failed with HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Bulk operations test failed: {e}")
            return False

    def test_qdrant_integration(self):
        """Test Qdrant vector database integration"""
        try:
            # Test Qdrant status
            response = self.session.get(f"{self.base_url}/api/v1/qdrant/status")
            status_success = response.status_code == 200
            
            qdrant_status = {}
            if status_success:
                qdrant_status = response.json().get('data', {})
            elif response.status_code == 404:
                logger.warning("Qdrant status endpoint not implemented")
                status_success = False  # Mark as failed instead of skipped
            
            # Test Qdrant collections
            response = self.session.get(f"{self.base_url}/api/v1/qdrant/collections")
            collections_success = response.status_code == 200
            
            collections_info = {}
            if collections_success:
                collections_info = response.json().get('data', {})
            elif response.status_code == 404:
                logger.warning("Qdrant collections endpoint not implemented")
                collections_success = False  # Mark as failed instead of skipped
            
            # Test Qdrant cluster info
            response = self.session.get(f"{self.base_url}/api/v1/qdrant/cluster/info")
            cluster_success = response.status_code == 200
            
            if cluster_success:
                pass  # Process cluster info if needed
            elif response.status_code == 404:
                logger.warning("Qdrant cluster info endpoint not implemented")
                cluster_success = False  # Mark as failed instead of skipped
            
            # Fail if any endpoints return errors
            success = status_success and collections_success and cluster_success
            logger.info(f"Qdrant integration test: {'PASS' if success else 'FAIL'}")
            logger.info(f"Status: {status_success}, Collections: {collections_success}, Cluster: {cluster_success}")
            
            if status_success:
                logger.info(f"Qdrant version: {qdrant_status.get('version', 'unknown')}")
            
            return success
            
        except Exception as e:
            logger.error(f"Qdrant integration test failed: {e}")
            return False

    def cleanup(self):
        """Clean up test resources"""
        logger.info("Cleaning up RAG test resources...")
        
        # Delete test collections
        for collection_name in self.test_collections:
            try:
                response = self.session.delete(f"{self.base_url}/api/v1/collections/{collection_name}")
                if response.status_code in [200, 204, 404]:
                    logger.info(f"Deleted collection: {collection_name}")
                else:
                    logger.warning(f"Failed to delete collection {collection_name}: {response.status_code}")
            except Exception as e:
                logger.warning(f"Error deleting collection {collection_name}: {e}")

    def run_all_rag_tests(self):
        """Run all RAG and document management tests"""
        logger.info("=" * 60)
        logger.info("Starting Kolosal RAG System Test Suite")
        logger.info("=" * 60)
        
        try:
            test_results = {
                'document_upload': self.test_document_upload(),
                'document_retrieval': self.test_document_retrieval(),
                'pdf_parsing': self.test_pdf_parsing(),
                'embedding_generation': self.test_embedding_generation(),
                'collection_management': self.test_collection_management(),
                'vector_search': self.test_vector_search(),
                'context_retrieval': self.test_context_retrieval_for_agents(),
                'metadata_filtering': self.test_document_metadata_filtering(),
                'bulk_operations': self.test_bulk_operations(),
                'qdrant_integration': self.test_qdrant_integration()
            }
            
            # Print results
            logger.info("\n" + "=" * 60)
            logger.info("RAG SYSTEM TEST RESULTS")
            logger.info("=" * 60)
            
            passed = sum(1 for result in test_results.values() if result)
            total = len(test_results)
            
            for test_name, result in test_results.items():
                status = "PASS" if result else "FAIL"
                logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
            
            logger.info(f"\nPassed: {passed}/{total}")
            logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
            
            # Additional insights
            if test_results.get('qdrant_integration'):
                logger.info("\n✓ Qdrant vector database is properly integrated")
            if test_results.get('embedding_generation'):
                logger.info("✓ Embedding generation is working correctly")
            if test_results.get('document_upload') and test_results.get('document_retrieval'):
                logger.info("✓ End-to-end document workflow is functional")
            
            # Return success based on whether majority of tests passed
            return passed >= total * 0.5  # At least 50% pass rate required
            
        finally:
            self.cleanup()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Kolosal Server RAG System')
    parser.add_argument('--server-url', default='http://127.0.0.1:8080',
                       help='Base URL of the Kolosal Server')
    parser.add_argument('--api-key', help='API key for authentication')
    
    args = parser.parse_args()
    
    tester = RAGTester(args.server_url, args.api_key)
    tester.run_all_rag_tests()


if __name__ == "__main__":
    main()
