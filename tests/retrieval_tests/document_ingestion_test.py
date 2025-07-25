"""Document Ingestion tests for the Kolosal server."""
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
                    "text": "The mayor held a press conference. She addressed rising fuel prices. Reforms were promised in the coming weeks.",
                    "metadata": {
                        "title": "City Hall Responds to Crisis",
                        "category": "politics",
                        "region": "North America",
                        "created_at": "2025-07-03T14:00:00Z"
                    }
                },
                {
                    "text": "The dragon soared over the hills. Villagers watched in awe and fear. A hero was needed once more.",
                    "metadata": {
                        "title": "The Awakening of the Dragon",
                        "category": "fiction",
                        "genre": "fantasy",
                        "author": "A. Storyteller"
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
                    "text": "They landed in Tokyo just before noon. Neon signs lit up the streets. Sushi was their first stop.",
                    "metadata": {
                        "title": "First Impressions of Tokyo",
                        "category": "travel",
                        "location": "Japan",
                        "tags": ["tokyo", "sushi", "asia"]
                    }
                },
                {
                    "text": "She started her morning with yoga. A balanced diet followed. Her health journey was finally on track.",
                    "metadata": {
                        "title": "Morning Wellness Routine",
                        "category": "health",
                        "type": "lifestyle",
                        "created_at": "2025-07-04T06:30:00Z"
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
                },
                {
                    "text": "The forest was alive with sound. Leaves rustled and streams flowed. It was untouched and peaceful.",
                    "metadata": {
                        "title": "Symphony of the Forest",
                        "category": "nature",
                        "location": "Pacific Northwest",
                        "tags": ["forest", "peace", "wildlife"]
                    }
                }
            ]

        print("🚀 Testing document ingestion...")
        print("⏳ Sending request...")

        try:
            initial_time = time.time()
            
            # Use the enhanced request tracking method
            response = self.make_tracked_request(
                test_name="Document Ingestion",
                method="POST",
                endpoint="/add-documents",
                json_data={"documents": documents},
                timeout=30,
                metadata={
                    "document_count": len(documents),
                    "categories": list(set(doc['metadata'].get('category', 'unknown') for doc in documents))
                }
            )
            elapsed_time = time.time() - initial_time

            if response.status_code == 200:
                result = response.json()
                print("✅ Document ingestion test: PASS")
                print(f"� Response: {json.dumps(result, indent=2)}")
                print(f"⏱️ Elapsed time: {elapsed_time:.2f} seconds")
                print("")
                
                # Log test completion
                self.log_test_end("Document Ingestion Test", {
                    "success": True,
                    "document_count": len(documents),
                    "elapsed_time": elapsed_time,
                    "response": result
                })
                return True
            else:
                try:
                    error_data = response.json()
                    print(f"❌ Document ingestion test: FAIL - HTTP {response.status_code}: {json.dumps(error_data)}")
                except:
                    print(f"❌ Document ingestion test: FAIL - HTTP {response.status_code}: {response.text}")
                print("")
                
                self.log_test_end("Document Ingestion Test", {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "response": response.text[:500]
                })
                return False
                
        except Exception as e:
            print(f"❌ Document ingestion test: FAIL - {str(e)}")
            print("")
            self.log_test_end("Document Ingestion Test", {
                "success": False,
                "error": str(e)
            })
            return False
