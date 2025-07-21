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

Usage:
    python test_rag_features.py [options]
"""

import requests
import json
import base64
import time
import os
import tempfile
from typing import Dict, List, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGTester:
    def __init__(self, base_url: str = "http://localhost:8080", api_key: Optional[str] = None):
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
        """Test document upload and indexing"""
        test_documents = [
            {
                "text": "Artificial Intelligence is transforming the healthcare industry through advanced diagnostic tools, personalized treatment plans, and predictive analytics. Machine learning algorithms can analyze medical images, detect patterns in patient data, and assist doctors in making more accurate diagnoses.",
                "metadata": {
                    "source": "ai_healthcare.txt",
                    "category": "healthcare",
                    "author": "AI Research Team",
                    "date": "2024-01-15",
                    "keywords": ["AI", "healthcare", "machine learning", "diagnostics"]
                }
            },
            {
                "text": "The automotive industry is experiencing a revolution with the development of autonomous vehicles. Self-driving cars use computer vision, sensor fusion, and deep learning to navigate roads safely. This technology promises to reduce accidents, improve traffic flow, and provide mobility solutions for people with disabilities.",
                "metadata": {
                    "source": "autonomous_vehicles.txt", 
                    "category": "automotive",
                    "author": "Tech Innovation Lab",
                    "date": "2024-01-20",
                    "keywords": ["autonomous vehicles", "computer vision", "safety", "transportation"]
                }
            },
            {
                "text": "Financial institutions are leveraging artificial intelligence for fraud detection, algorithmic trading, and risk assessment. AI systems can analyze transaction patterns in real-time, identify suspicious activities, and make trading decisions faster than human traders. This technology is reshaping the finance industry landscape.",
                "metadata": {
                    "source": "ai_finance.txt",
                    "category": "finance", 
                    "author": "FinTech Research",
                    "date": "2024-01-25",
                    "keywords": ["finance", "fraud detection", "algorithmic trading", "risk assessment"]
                }
            }
        ]
        
        try:
            payload = {
                "documents": test_documents,
                "collection_name": "test_rag_collection",
                "auto_index": True,
                "embedding_model": "default"
            }
            
            response = self.session.post(f"{self.base_url}/api/v1/documents", json=payload)
            success = response.status_code == 200
            
            if success:
                result = response.json()
                indexed_count = result.get('data', {}).get('indexed_count', 0)
                collection_name = result.get('data', {}).get('collection_name')
                
                if collection_name:
                    self.test_collections.append(collection_name)
                
                logger.info(f"Document upload test: PASS - Indexed {indexed_count} documents")
                return True
            else:
                logger.error(f"Document upload test: FAIL - HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Document upload test failed: {e}")
            return False

    def test_document_retrieval(self):
        """Test document retrieval and search"""
        retrieval_queries = [
            {
                "query": "healthcare AI machine learning diagnostics",
                "k": 3,
                "score_threshold": 0.5,
                "collection_name": "test_rag_collection"
            },
            {
                "query": "autonomous vehicles self-driving cars computer vision",
                "k": 2,
                "score_threshold": 0.6,
                "collection_name": "test_rag_collection"
            },
            {
                "query": "financial fraud detection algorithmic trading",
                "k": 2,
                "score_threshold": 0.5,
                "collection_name": "test_rag_collection"
            }
        ]
        
        success_count = 0
        for i, query_data in enumerate(retrieval_queries):
            try:
                response = self.session.post(f"{self.base_url}/retrieve", json=query_data)
                
                if response.status_code == 200:
                    result = response.json()
                    documents = result.get('data', {}).get('documents', [])
                    scores = [doc.get('score', 0) for doc in documents]
                    
                    if documents and len(documents) > 0:
                        success_count += 1
                        logger.info(f"Retrieval query {i+1}: PASS - Found {len(documents)} documents, avg score: {sum(scores)/len(scores):.3f}")
                    else:
                        logger.warning(f"Retrieval query {i+1}: PARTIAL - No documents found")
                else:
                    logger.error(f"Retrieval query {i+1}: FAIL - HTTP {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Retrieval query {i+1} failed: {e}")
        
        overall_success = success_count >= len(retrieval_queries) // 2
        logger.info(f"Document retrieval test: {'PASS' if overall_success else 'FAIL'} - {success_count}/{len(retrieval_queries)} queries succeeded")
        return overall_success

    def test_pdf_parsing(self):
        """Test PDF parsing functionality"""
        try:
            pdf_data = self.create_test_pdf_content()
            
            payload = {
                "pdf_data": pdf_data,
                "method": "fast",
                "auto_index": True,
                "collection_name": "test_pdf_collection",
                "metadata": {
                    "source": "test_ai_document.pdf",
                    "type": "educational",
                    "topic": "artificial_intelligence"
                }
            }
            
            response = self.session.post(f"{self.base_url}/parse-pdf", json=payload)
            success = response.status_code == 200
            
            if success:
                result = response.json()
                extracted_text = result.get('data', {}).get('extracted_text', '')
                pages_processed = result.get('data', {}).get('pages_processed', 0)
                indexed = result.get('data', {}).get('indexed', False)
                
                if "test_pdf_collection" not in self.test_collections:
                    self.test_collections.append("test_pdf_collection")
                
                logger.info(f"PDF parsing test: PASS - Extracted {len(extracted_text)} characters, {pages_processed} pages, indexed: {indexed}")
                return True
            else:
                logger.error(f"PDF parsing test: FAIL - HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"PDF parsing test failed: {e}")
            return False

    def test_embedding_generation(self):
        """Test embedding generation"""
        try:
            test_texts = [
                "Machine learning algorithms are revolutionizing data analysis",
                "Deep neural networks enable complex pattern recognition",
                "Natural language processing helps computers understand human language"
            ]
            
            payload = {
                "texts": test_texts,
                "model": "default",
                "normalize": True
            }
            
            response = self.session.post(f"{self.base_url}/embeddings", json=payload)
            success = response.status_code == 200
            
            if success:
                result = response.json()
                embeddings = result.get('data', {}).get('embeddings', [])
                
                if embeddings and len(embeddings) == len(test_texts):
                    # Check if embeddings have reasonable dimensions
                    first_embedding = embeddings[0]
                    embedding_dim = len(first_embedding) if isinstance(first_embedding, list) else 0
                    
                    logger.info(f"Embedding generation test: PASS - Generated {len(embeddings)} embeddings, dimension: {embedding_dim}")
                    return True
                else:
                    logger.error(f"Embedding generation test: FAIL - Expected {len(test_texts)} embeddings, got {len(embeddings)}")
                    return False
            else:
                logger.error(f"Embedding generation test: FAIL - HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Embedding generation test failed: {e}")
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
            # First, ensure we have some documents
            if not self.test_collections:
                logger.warning("No test collections available for vector search")
                return False
            
            search_queries = [
                {
                    "vector": None,  # Will be generated from text
                    "text": "artificial intelligence healthcare applications",
                    "k": 5,
                    "collection_name": self.test_collections[0] if self.test_collections else "test_rag_collection"
                },
                {
                    "vector": None,
                    "text": "machine learning financial fraud detection",
                    "k": 3,
                    "collection_name": self.test_collections[0] if self.test_collections else "test_rag_collection"
                }
            ]
            
            success_count = 0
            for i, search_data in enumerate(search_queries):
                try:
                    response = self.session.post(f"{self.base_url}/vector-search", json=search_data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        matches = result.get('data', {}).get('matches', [])
                        
                        if matches:
                            success_count += 1
                            avg_score = sum(match.get('score', 0) for match in matches) / len(matches)
                            logger.info(f"Vector search {i+1}: PASS - Found {len(matches)} matches, avg score: {avg_score:.3f}")
                        else:
                            logger.warning(f"Vector search {i+1}: PARTIAL - No matches found")
                    else:
                        logger.error(f"Vector search {i+1}: FAIL - HTTP {response.status_code}")
                        
                except Exception as e:
                    logger.error(f"Vector search {i+1} failed: {e}")
            
            overall_success = success_count > 0
            logger.info(f"Vector search test: {'PASS' if overall_success else 'FAIL'} - {success_count}/{len(search_queries)} searches succeeded")
            return overall_success
            
        except Exception as e:
            logger.error(f"Vector search test failed: {e}")
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
                    response = self.session.post(f"{self.base_url}/retrieve-filtered", json=filter_data)
                    
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
            
            # Test Qdrant collections
            response = self.session.get(f"{self.base_url}/api/v1/qdrant/collections")
            collections_success = response.status_code == 200
            
            collections_info = {}
            if collections_success:
                collections_info = response.json().get('data', {})
            
            # Test Qdrant cluster info
            response = self.session.get(f"{self.base_url}/api/v1/qdrant/cluster/info")
            cluster_success = response.status_code == 200
            
            success = status_success and collections_success
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
            
        finally:
            self.cleanup()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Kolosal Server RAG System')
    parser.add_argument('--server-url', default='http://localhost:8080',
                       help='Base URL of the Kolosal Server')
    parser.add_argument('--api-key', help='API key for authentication')
    
    args = parser.parse_args()
    
    tester = RAGTester(args.server_url, args.api_key)
    tester.run_all_rag_tests()


if __name__ == "__main__":
    main()
