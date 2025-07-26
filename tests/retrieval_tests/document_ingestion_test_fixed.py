"""Document Ingestion tests for the Kolosal server - Fixed version with multiple endpoint testing."""
from typing import List, Optional, Dict
import requests
import json
import time
from tests.kolosal_tests import KolosalTestBase


class DocumentIngestionTest(KolosalTestBase):
    """Test class for document ingestion functionality in Kolosal Server."""

    def test_ingest_document(self, documents: Optional[List[Dict[str, str]]] = None) -> bool:
        """Test ingesting a document into the Kolosal Server with comprehensive logging."""
        # Log test start
        self.log_test_start("Document Ingestion Test", "Testing document upload and indexing")
        
        if documents is None:
            documents = [
                {
                    "text": "This is a test document for debugging.",
                    "metadata": {"title": "Debug Test", "type": "debug"}
                }
            ]

        print("🚀 Testing document ingestion...")
        print("=" * 50)
        
        # Test data following the debug script pattern
        test_data = {
            "documents": documents
        }
        
        # List of potential document ingestion endpoints to test
        endpoints_to_test = [
            ("/add_documents", "Legacy add documents endpoint"),
            ("/ingest", "Alternative ingest endpoint"),
            ("/documents", "V1 documents endpoint"),
            ("/v1/documents", "V1 documents endpoint with prefix"),
            ("/api/v1/documents", "Full V1 API documents endpoint"),
            ("/documents/upload", "Document upload endpoint"),
            ("/api/v1/documents/upload", "V1 document upload endpoint"),
        ]
        
        successful_endpoint = None
        
        for endpoint, description in endpoints_to_test:
            print(f"\n🧪 Testing: POST {endpoint}")
            print(f"   Description: {description}")
            
            try:
                initial_time = time.time()
                
                response = self.make_tracked_request(
                    test_name=f"Document Ingestion - {description}",
                    method="POST",
                    endpoint=endpoint,
                    json_data=test_data,
                    timeout=30,
                    metadata={
                        "document_count": len(documents),
                        "endpoint_tested": endpoint,
                        "description": description
                    }
                )
                elapsed_time = time.time() - initial_time
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ SUCCESS")
                    try:
                        result = response.json()
                        if isinstance(result, dict) and 'data' in result:
                            print(f"   Response keys: {list(result.keys())}")
                        else:
                            print(f"   Response type: {type(result)}")
                        print(f"   Response: {json.dumps(result, indent=2)}")
                    except:
                        print(f"   Response length: {len(response.text)} chars")
                    
                    print(f"   ⏱️ Elapsed time: {elapsed_time:.2f} seconds")
                    successful_endpoint = endpoint
                    
                    # Log test completion
                    self.log_test_end("Document Ingestion Test", {
                        "success": True,
                        "successful_endpoint": endpoint,
                        "document_count": len(documents),
                        "elapsed_time": elapsed_time,
                        "response": result if 'result' in locals() else response.text[:500]
                    })
                    print("\n✅ Document ingestion test: PASS")
                    print(f"📄 Successfully used endpoint: {endpoint}")
                    print("")
                    return True
                else:
                    print("   ❌ FAILED")
                    print(f"   Response: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"   💥 ERROR: {e}")
        
        # If we get here, all endpoints failed
        print(f"\n❌ Document ingestion test: FAIL - All endpoints failed")
        print("Tested endpoints:")
        for endpoint, description in endpoints_to_test:
            print(f"  - {endpoint} ({description})")
        print("")
        
        self.log_test_end("Document Ingestion Test", {
            "success": False,
            "error": "All endpoints failed",
            "tested_endpoints": [ep[0] for ep in endpoints_to_test]
        })
        return False

    def test_ingest_multiple_documents(self, use_large_dataset: bool = False) -> bool:
        """Test ingesting multiple documents with various content types."""
        self.log_test_start("Multiple Document Ingestion Test", "Testing bulk document upload")
        
        if use_large_dataset:
            documents = [
                {
                    "text": "The new smartphone launched today. It features an AI-powered camera. Reviews highlight its speed and design.",
                    "metadata": {
                        "title": "Next-Gen Smartphone Release",
                        "category": "technology",
                        "author": "Tech Reporter",
                        "created_at": "2025-07-04T09:00:00Z"
                    }
                },
                {
                    "text": "The unit moved out at dawn. Their mission was to secure the bridge. Tension filled the silent desert.",
                    "metadata": {
                        "title": "Desert Operation Begins",
                        "category": "military",
                        "location": "Middle East",
                        "created_at": "2025-07-04T05:00:00Z"
                    }
                },
                {
                    "text": "Scientists discovered a new exoplanet. It's roughly the size of Earth. It could hold liquid water.",
                    "metadata": {
                        "title": "New Earth-like Planet Found",
                        "category": "science",
                        "field": "astronomy",
                        "created_at": "2025-07-02T08:30:00Z"
                    }
                },
                {
                    "text": "Students gathered in the lab. Today's lesson was about circuits. They built a simple light sensor.",
                    "metadata": {
                        "title": "Hands-On Circuit Lab",
                        "category": "education",
                        "level": "high_school",
                        "created_at": "2025-07-01T10:15:00Z"
                    }
                },
                {
                    "text": "The startup secured its seed funding. Their platform connects artisans with buyers. Growth projections are promising.",
                    "metadata": {
                        "title": "Startup Raises Seed Round",
                        "category": "business",
                        "industry": "e-commerce",
                        "created_at": "2025-07-03T17:45:00Z"
                    }
                }
            ]
        else:
            documents = [
                {
                    "text": "Test document 1 about artificial intelligence and machine learning.",
                    "metadata": {"title": "AI Test Doc 1", "category": "technology"}
                },
                {
                    "text": "Test document 2 about software development practices.",
                    "metadata": {"title": "Dev Test Doc 2", "category": "programming"}
                },
                {
                    "text": "Test document 3 about data science methodologies.",
                    "metadata": {"title": "Data Science Doc 3", "category": "science"}
                }
            ]
        
        return self.test_ingest_document(documents)
