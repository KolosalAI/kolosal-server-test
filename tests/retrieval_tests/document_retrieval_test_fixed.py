"""Document retrieval test module for the Kolosal server - Fixed version with multiple endpoint testing."""
import time
import asyncio
import json
from typing import List, Optional
import requests
import aiohttp
from tests.kolosal_tests import KolosalTestBase


class DocumentRetrievalTest(KolosalTestBase):
    """Test class for document retrieval functionality in Kolosal Server."""

    def retrieve_documents(self,
                           query: Optional[str] = "test document",
                           limit: Optional[int] = 5,
                           score_threshold: Optional[float] = 0.0) -> bool:
        """Test retrieving documents based on a query with comprehensive logging."""
        # Log test start
        self.log_test_start("Document Retrieval Test", f"Query: {query}")
        
        print(f"🚀 Testing document retrieval with query: {query}")
        print("=" * 50)
        
        # Test retrieval data following the debug script pattern
        retrieval_data = {
            "query": query,
            "limit": limit
        }
        
        # Add score_threshold if provided and not default
        if score_threshold > 0.0:
            retrieval_data["score_threshold"] = score_threshold
        
        # List of potential document retrieval endpoints to test
        retrieval_endpoints = [
            ("/retrieve", "Legacy retrieve endpoint"),
            ("/vector-search", "Vector search endpoint"),
            ("/v1/rag/search", "V1 RAG search endpoint"),
            ("/search", "Basic search endpoint"),
            ("/api/v1/search", "V1 API search endpoint"),
            ("/documents/search", "Documents search endpoint"),
        ]
        
        successful_endpoint = None
        
        for endpoint, description in retrieval_endpoints:
            print(f"\n🧪 Testing: POST {endpoint}")
            print(f"   Description: {description}")
            
            try:
                start_time = time.time()

                response = self.make_tracked_request(
                    test_name=f"Document Retrieval - {description}",
                    method="POST",
                    endpoint=endpoint,
                    json_data=retrieval_data,
                    timeout=30,
                    metadata={
                        "query": query,
                        "limit": limit,
                        "score_threshold": score_threshold,
                        "endpoint_tested": endpoint,
                        "description": description
                    }
                )
                elapsed_time = time.time() - start_time
                
                print(f"   Status: {response.status_code}")

                if response.status_code == 200:
                    print("   ✅ SUCCESS")
                    try:
                        result = response.json()
                        if isinstance(result, dict):
                            print(f"   Response keys: {list(result.keys())}")
                            
                            # Try to extract documents from different possible structures
                            documents = []
                            if 'documents' in result:
                                documents = result['documents']
                            elif 'results' in result:
                                documents = result['results']
                            elif 'data' in result:
                                if isinstance(result['data'], list):
                                    documents = result['data']
                                elif isinstance(result['data'], dict) and 'documents' in result['data']:
                                    documents = result['data']['documents']
                                elif isinstance(result['data'], dict) and 'results' in result['data']:
                                    documents = result['data']['results']
                            
                            print(f"   Found {len(documents)} documents")
                            
                            # Print first document if available
                            if documents and len(documents) > 0:
                                first_doc = documents[0]
                                print(f"   First result preview:")
                                if isinstance(first_doc, dict):
                                    if 'title' in first_doc:
                                        print(f"     Title: {first_doc['title']}")
                                    elif 'metadata' in first_doc and isinstance(first_doc['metadata'], dict) and 'title' in first_doc['metadata']:
                                        print(f"     Title: {first_doc['metadata']['title']}")
                                    if 'score' in first_doc:
                                        print(f"     Score: {first_doc['score']}")
                                    if 'text' in first_doc:
                                        preview_text = first_doc['text'][:100] + "..." if len(first_doc['text']) > 100 else first_doc['text']
                                        print(f"     Text: {preview_text}")
                        else:
                            print(f"   Response type: {type(result)}")
                    except:
                        print(f"   Response length: {len(response.text)} chars")
                    
                    print(f"   ⏱️ Elapsed time: {elapsed_time:.2f} seconds")
                    successful_endpoint = endpoint
                    
                    # Log test completion
                    self.log_test_end("Document Retrieval Test", {
                        "success": True,
                        "successful_endpoint": endpoint,
                        "documents_count": len(documents) if 'documents' in locals() else 0,
                        "elapsed_time": elapsed_time,
                        "query": query,
                        "score_threshold": score_threshold
                    })
                    print(f"\n✅ Document retrieval test: PASS")
                    print(f"📄 Successfully used endpoint: {endpoint}")
                    print(f"🔍 Query: {query}")
                    if 'documents' in locals():
                        print(f"📄 Retrieved documents count: {len(documents)}")
                    print("")
                    return True
                else:
                    print("   ❌ FAILED")
                    print(f"   Response: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"   💥 ERROR: {e}")
        
        # If we get here, all endpoints failed
        print(f"\n❌ Document retrieval test: FAIL - All endpoints failed")
        print("Tested endpoints:")
        for endpoint, description in retrieval_endpoints:
            print(f"  - {endpoint} ({description})")
        print("")
        
        self.log_test_end("Document Retrieval Test", {
            "success": False,
            "error": "All endpoints failed",
            "tested_endpoints": [ep[0] for ep in retrieval_endpoints],
            "query": query,
            "score_threshold": score_threshold
        })
        return False

    def test_multiple_queries(self) -> bool:
        """Test document retrieval with multiple different queries."""
        self.log_test_start("Multiple Query Test", "Testing various search queries")
        
        test_queries = [
            "artificial intelligence",
            "machine learning",
            "test document",
            "technology",
            "debug"
        ]
        
        successful_queries = 0
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            if self.retrieve_documents(query=query, limit=3):
                successful_queries += 1
            else:
                print(f"   Query '{query}' failed")
        
        success_rate = successful_queries / len(test_queries)
        overall_success = success_rate >= 0.5  # At least 50% should succeed
        
        print(f"\n📊 Query Test Summary:")
        print(f"   Successful queries: {successful_queries}/{len(test_queries)}")
        print(f"   Success rate: {success_rate:.2%}")
        print(f"   Overall result: {'✅ PASS' if overall_success else '❌ FAIL'}")
        
        self.log_test_end("Multiple Query Test", {
            "success": overall_success,
            "successful_queries": successful_queries,
            "total_queries": len(test_queries),
            "success_rate": success_rate
        })
        
        return overall_success

    def concurrent_retrieve_documents(self,
                                      queries: Optional[List[str]] = None,
                                      limit: Optional[int] = 5,
                                      score_threshold: Optional[float] = 0.0) -> bool:
        """Test concurrent document retrieval requests with different queries."""
        # Log test start
        self.log_test_start("Concurrent Document Retrieval Test", f"Multiple concurrent queries")

        if queries is None:
            queries = [
                "test document artificial intelligence",
                "machine learning technology",
                "debug information",
                "software development",
                "data science"
            ]

        print(f"🚀 Testing {len(queries)} concurrent document retrieval requests")
        print("⏳ Sending concurrent requests...")
        
        # First, find a working endpoint by testing the first query
        print("🔍 Finding working endpoint...")
        working_endpoint = None
        test_query = queries[0]
        
        retrieval_endpoints = [
            "/retrieve",
            "/vector-search", 
            "/v1/rag/search",
            "/search",
            "/api/v1/search"
        ]
        
        for endpoint in retrieval_endpoints:
            try:
                test_data = {"query": test_query, "limit": limit}
                if score_threshold > 0.0:
                    test_data["score_threshold"] = score_threshold
                response = requests.post(f"{self.client.base_url}{endpoint}", 
                                       json=test_data, timeout=10)
                if response.status_code == 200:
                    working_endpoint = endpoint
                    print(f"   ✅ Found working endpoint: {endpoint}")
                    break
            except:
                continue
        
        if not working_endpoint:
            print("   ❌ No working endpoint found for concurrent testing")
            self.log_test_end("Concurrent Document Retrieval Test", {
                "success": False,
                "error": "No working endpoint found",
                "score_threshold": score_threshold
            })
            return False
        
        # Log request details
        request_config = {
            "concurrent_requests": len(queries),
            "queries": queries,
            "limit": limit,
            "score_threshold": score_threshold,
            "endpoint": working_endpoint
        }
        print(f"📤 Request configuration: {json.dumps(request_config, indent=2)}")

        async def single_request(query: str, request_id: int):
            start_time = time.time()

            api_url = f"{self.client.base_url}{working_endpoint}"
            payload = {
                "query": query,
                "limit": limit
            }
            
            # Add score_threshold if provided and not default
            if score_threshold > 0.0:
                payload["score_threshold"] = score_threshold

            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload) as response:
                    elapsed_time = time.time() - start_time

                    if response.status != 200:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=f"Failed to retrieve documents for query: {query}"
                        )

                    result = await response.json()
                    
                    # Extract documents from various possible response structures
                    documents = []
                    if 'documents' in result:
                        documents = result['documents']
                    elif 'results' in result:
                        documents = result['results']
                    elif 'data' in result:
                        if isinstance(result['data'], list):
                            documents = result['data']
                        elif isinstance(result['data'], dict):
                            if 'documents' in result['data']:
                                documents = result['data']['documents']
                            elif 'results' in result['data']:
                                documents = result['data']['results']
                    
                    document_count = len(documents)

                    return request_id, elapsed_time, document_count, query, documents

        async def run_concurrent_requests():
            start_time = time.time()
            results = await asyncio.gather(*[single_request(query, i+1) for i, query in enumerate(queries)])
            total_time = time.time() - start_time
            return results, total_time

        try:
            results, total_time = asyncio.run(run_concurrent_requests())

            # Sort results by request ID to maintain order
            results.sort(key=lambda x: x[0])
        
            # Log response summary
            response_summary = {
                "total_requests": len(queries),
                "total_time": total_time,
                "endpoint_used": working_endpoint,
                "results": [
                    {
                        "request_id": result[0],
                        "elapsed_time": result[1],
                        "document_count": result[2],
                        "query": result[3]
                    } for result in results
                ]
            }
            print(f"📥 Concurrent requests summary: {json.dumps(response_summary, indent=2)}")

            print("✅ All document retrieval requests completed!")

            successful_requests = 0
            total_documents = 0
            for request_id, elapsed_time, document_count, query, documents in results:
                print(f"Request {request_id}: ⏱️ {elapsed_time:.2f}s, 📄 {document_count} docs")
                print(f"🔍 Query: {query}")
                print("")
                total_documents += document_count
                if document_count > 0:
                    successful_requests += 1

            avg_time = sum(result[1] for result in results) / len(results)
            success_rate = successful_requests / len(results)

            print(f"📊 Average time per request: {avg_time:.2f}s")
            print(f"📊 Total concurrent execution time: {total_time:.2f} seconds")
            print(f"📊 Total documents retrieved: {total_documents}")
            print(f"📊 Successful requests: {successful_requests}/{len(queries)}")
            print(f"📊 Success rate: {success_rate:.2%}")
            print("")
            
            overall_success = success_rate >= 0.8  # 80% success rate required
            
            # Log test completion
            self.log_test_end("Concurrent Document Retrieval Test", {
                "success": overall_success,
                "success_rate": success_rate,
                "total_requests": len(queries),
                "successful_requests": successful_requests,
                "total_time": total_time,
                "total_documents": total_documents,
                "score_threshold": score_threshold,
                "endpoint_used": working_endpoint
            })
            
            result_msg = "✅ PASS" if overall_success else "❌ FAIL"
            print(f"🏁 Concurrent retrieval test: {result_msg}")
            print("")
            
            return overall_success
            
        except Exception as e:
            print(f"❌ Concurrent document retrieval failed: {str(e)}")
            print("")
            self.log_test_end("Concurrent Document Retrieval Test", {
                "success": False,
                "error": str(e),
                "score_threshold": score_threshold
            })
            return False

    def custom_concurrent_retrieve(self,
                                   queries: Optional[List[str]] = None,
                                   limit: Optional[int] = 10,
                                   score_threshold: Optional[float] = 0.0) -> bool:
        """Test concurrent document retrieval with custom query list - improved version."""
        # Log test start
        self.log_test_start("Custom Concurrent Document Retrieval Test", "Custom query list")

        if queries is None:
            queries = [
                "python programming",
                "javascript frameworks", 
                "react development",
                "nodejs backend",
                "database optimization",
            ]

        print(f"🚀 Testing {len(queries)} custom concurrent document retrieval requests")
        print("⏳ Sending concurrent requests...")
        
        # First, find a working endpoint by testing the first query
        print("🔍 Finding working endpoint...")
        working_endpoint = None
        test_query = queries[0]
        
        retrieval_endpoints = [
            "/retrieve",
            "/vector-search", 
            "/v1/rag/search",
            "/search",
            "/api/v1/search"
        ]
        
        for endpoint in retrieval_endpoints:
            try:
                test_data = {"query": test_query, "limit": limit}
                if score_threshold > 0.0:
                    test_data["score_threshold"] = score_threshold
                response = requests.post(f"{self.client.base_url}{endpoint}", 
                                       json=test_data, timeout=10)
                if response.status_code == 200:
                    working_endpoint = endpoint
                    print(f"   ✅ Found working endpoint: {endpoint}")
                    break
            except:
                continue
        
        if not working_endpoint:
            print("   ❌ No working endpoint found for custom concurrent testing")
            self.log_test_end("Custom Concurrent Document Retrieval Test", {
                "success": False,
                "error": "No working endpoint found",
                "score_threshold": score_threshold
            })
            return False

        # Log request details
        request_config = {
            "concurrent_requests": len(queries),
            "queries": queries,
            "limit": limit,
            "score_threshold": score_threshold,
            "endpoint": working_endpoint
        }
        print(f"📤 Request configuration: {json.dumps(request_config, indent=2)}")

        async def single_request(query: str, request_id: int):
            start_time = time.time()

            api_url = f"{self.client.base_url}{working_endpoint}"
            payload = {
                "query": query,
                "limit": limit
            }
            
            # Add score_threshold if provided and not default
            if score_threshold > 0.0:
                payload["score_threshold"] = score_threshold

            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json=payload) as response:
                    elapsed_time = time.time() - start_time

                    if response.status != 200:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=f"Failed to retrieve documents for query: {query}"
                        )

                    result = await response.json()
                    
                    # Extract documents from various possible response structures
                    documents = []
                    if 'documents' in result:
                        documents = result['documents']
                    elif 'results' in result:
                        documents = result['results']
                    elif 'data' in result:
                        if isinstance(result['data'], list):
                            documents = result['data']
                        elif isinstance(result['data'], dict):
                            if 'documents' in result['data']:
                                documents = result['data']['documents']
                            elif 'results' in result['data']:
                                documents = result['data']['results']
                    
                    document_count = len(documents)

                    return request_id, elapsed_time, document_count, query, documents

        async def run_concurrent_requests():
            start_time = time.time()
            results = await asyncio.gather(*[single_request(query, i+1) for i, query in enumerate(queries)])
            total_time = time.time() - start_time
            return results, total_time

        try:
            results, total_time = asyncio.run(run_concurrent_requests())

            # Sort results by request ID
            results.sort(key=lambda x: x[0])

            print("✅ All custom document retrieval requests completed!")

            successful_requests = 0
            total_documents = 0
            
            for request_id, elapsed_time, document_count, query, documents in results:
                print(f"Request {request_id}: ⏱️ {elapsed_time:.2f}s, 📄 {document_count} docs")
                print(f"🔍 Query: {query}")
                
                # Print the first document for each query
                if documents and len(documents) > 0:
                    first_doc = documents[0]
                    title = "N/A"
                    score = "N/A"
                    
                    if isinstance(first_doc, dict):
                        if 'title' in first_doc:
                            title = first_doc['title']
                        elif 'metadata' in first_doc and isinstance(first_doc['metadata'], dict) and 'title' in first_doc['metadata']:
                            title = first_doc['metadata']['title']
                        
                        if 'score' in first_doc:
                            score = first_doc['score']
                    
                    print(f"   📋 First doc: {title} (Score: {score})")
                    successful_requests += 1
                else:
                    print("   ⚠️ No documents found")
                print("")
                
                total_documents += document_count

            # Summary statistics
            avg_response_time = sum(result[1] for result in results) / len(results)
            avg_documents_per_query = total_documents / len(results) if len(results) > 0 else 0
            success_rate = successful_requests / len(results)

            print("📊 CUSTOM QUERY SUMMARY:")
            print(f"📊 Average response time: {avg_response_time:.2f}s")
            print(f"📊 Average documents per query: {avg_documents_per_query:.2f}")
            print(f"📊 Total execution time: {total_time:.2f} seconds")
            print(f"📊 Success rate: {success_rate:.2%}")
            print("")
            
            overall_success = success_rate >= 0.6  # 60% success rate for custom queries
            
            # Log test completion
            self.log_test_end("Custom Concurrent Document Retrieval Test", {
                "success": overall_success,
                "success_rate": success_rate,
                "total_requests": len(queries),
                "successful_requests": successful_requests,
                "total_time": total_time,
                "total_documents": total_documents,
                "avg_response_time": avg_response_time,
                "endpoint_used": working_endpoint,
                "score_threshold": score_threshold
            })
            
            result_msg = "✅ PASS" if overall_success else "❌ FAIL"
            print(f"🏁 Custom concurrent retrieval test: {result_msg}")
            print("")
            
            return overall_success
            
        except Exception as e:
            print(f"❌ Custom concurrent document retrieval failed: {str(e)}")
            print("")
            self.log_test_end("Custom Concurrent Document Retrieval Test", {
                "success": False,
                "error": str(e),
                "score_threshold": score_threshold
            })
            return False
