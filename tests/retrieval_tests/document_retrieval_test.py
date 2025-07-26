"""Document retrieval test module for the Kolosal server."""
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
                           query: Optional[str] = "smartphone",
                           limit: Optional[int] = 10,
                           score_threshold: Optional[float] = 0.0) -> bool:
        """Test retrieving documents based on a query with comprehensive logging."""
        # Log test start
        self.log_test_start("Document Retrieval Test", f"Query: {query}")
        
        print(f"🚀 Testing document retrieval with query: {query}")
        print("⏳ Sending request...")

        try:
            start_time = time.time()

            # Use the enhanced request tracking method
            response = self.make_tracked_request(
                test_name="Document Retrieval",
                method="POST",
                endpoint="/vector-search",
                json_data={
                    "query": query,
                    "limit": limit,
                    "score_threshold": score_threshold
                },
                timeout=30,
                metadata={
                    "query": query,
                    "limit": limit,
                    "score_threshold": score_threshold
                }
            )
            elapsed_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                documents = result.get('documents', [])

                print("✅ Document retrieval test: PASS")
                print(f"📄 Retrieved documents count: {len(documents)}")
                print(f"⏱️ Response time: {elapsed_time:.2f} seconds")
                print(f"🔍 Query: {query}")
                
                # Print the first document if available
                if documents:
                    first_doc = documents[0]
                    print("\n📋 FIRST DOCUMENT RETRIEVED:")
                    print(f"   ID: {first_doc.get('id', 'N/A')}")
                    print(f"   Title: {first_doc.get('metadata', {}).get('title', 'N/A')}")
                    print(f"   Score: {first_doc.get('score', 'N/A')}")
                    print(f"   Text: {first_doc.get('text', 'N/A')}")
                    print(f"   Metadata: {first_doc.get('metadata', {})}")
                else:
                    print("\n⚠️ No documents found in the response.")
                
                print("")
                
                # Log test completion
                self.log_test_end("Document Retrieval Test", {
                    "success": True,
                    "documents_count": len(documents),
                    "elapsed_time": elapsed_time,
                    "query": query
                })
                return True
            else:
                try:
                    error_data = response.json()
                    print(f"❌ Document retrieval test: FAIL - HTTP {response.status_code}: {json.dumps(error_data)}")
                except:
                    print(f"❌ Document retrieval test: FAIL - HTTP {response.status_code}: {response.text}")
                print("")
                
                self.log_test_end("Document Retrieval Test", {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "query": query
                })
                return False
                
        except Exception as e:
            print(f"❌ Document retrieval test: FAIL - {str(e)}")
            print("")
            self.log_test_end("Document Retrieval Test", {
                "success": False,
                "error": str(e),
                "query": query
            })
            return False

    def concurrent_retrieve_documents(self,
                                      queries: Optional[List[str]] = None,
                                      limit: Optional[int] = 10,
                                      score_threshold: Optional[float] = 0.0) -> bool:
        """Test concurrent document retrieval requests with different queries with comprehensive logging."""
        # Log test start
        self.log_test_start("Concurrent Document Retrieval Test", f"Multiple queries")

        if queries is None:
            queries = [
                "smartphone technology",
                "artificial intelligence",
                "machine learning algorithms",
                "data science methods",
                "cloud computing services",
                "cybersecurity best practices",
                "software development",
                "web development frameworks",
                "mobile app development",
                "database management"
            ]

        print(
            f"🚀 Testing {len(queries)} concurrent document retrieval requests")
        print("⏳ Sending concurrent requests...")
        
        # Log request details
        request_config = {
            "concurrent_requests": len(queries),
            "queries": queries,
            "limit": limit,
            "score_threshold": score_threshold
        }
        print(f"📤 Request configuration: {json.dumps(request_config, indent=2)}")

        async def single_request(query: str, request_id: int):
            start_time = time.time()

            api_url = f"{self.client.base_url}/vector-search"
            payload = {
                "query": query,
                "limit": limit,
                "score_threshold": score_threshold
            }

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
                    documents = result.get('documents', [])
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
            for request_id, elapsed_time, document_count, query, documents in results:
                print(
                    f"Request {request_id}: ⏱️ {elapsed_time:.2f}s, 📄 {document_count} docs")
                print(f"🔍 Query: {query}")
                
                # Print the first document for each query
                if documents:
                    first_doc = documents[0]
                    print(f"   📋 First doc: {first_doc.get('metadata', {}).get('title', 'N/A')} (Score: {first_doc.get('score', 'N/A')})")
                    successful_requests += 1
                else:
                    print("   ⚠️ No documents found")
                print("")

            # Summary statistics
            avg_response_time = sum(result[1] for result in results) / len(results)
            avg_documents_per_query = sum(result[2] for result in results) / len(results)

            print("📊 SUMMARY STATISTICS:")
            print(f"📊 Average response time: {avg_response_time:.2f}s")
            print(f"📊 Average documents per query: {avg_documents_per_query:.2f}")
            print(f"📊 Total concurrent execution time: {total_time:.2f} seconds")
            print(f"📊 Successful requests: {successful_requests}/{len(queries)}")
            print("")
            
            # Log test completion
            success_rate = successful_requests / len(queries)
            self.log_test_end("Concurrent Document Retrieval Test", {
                "success": success_rate >= 0.8,
                "success_rate": success_rate,
                "total_requests": len(queries),
                "successful_requests": successful_requests,
                "total_time": total_time,
                "avg_response_time": avg_response_time
            })
            
            return success_rate >= 0.8
            
        except Exception as e:
            print(f"❌ Concurrent document retrieval test: FAIL - {str(e)}")
            print("")
            self.log_test_end("Concurrent Document Retrieval Test", {
                "success": False,
                "error": str(e)
            })
            return False

    def custom_concurrent_retrieve(self,
                                   queries: Optional[List[str]] = None,
                                   limit: Optional[int] = 10,
                                   score_threshold: Optional[float] = 0.0) -> None:
        """Test concurrent document retrieval with custom query list."""

        if queries is None:
            queries = [
                "python programming",
                "javascript frameworks",
                "react development",
                "nodejs backend",
                "database optimization",
            ]

        print(
            f"🚀 Testing {len(queries)} custom concurrent document retrieval requests")
        print("⏳ Sending concurrent requests...")

        async def single_request(query: str, request_id: int):
            start_time = time.time()

            api_url = f"{self.client.base_url}/vector-search"
            payload = {
                "query": query,
                "limit": limit,
                "score_threshold": score_threshold
            }

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
                    documents = result.get('documents', [])
                    document_count = len(documents)

                    return request_id, elapsed_time, document_count, query, documents

        async def run_concurrent_requests():
            start_time = time.time()
            results = await asyncio.gather(*[single_request(query, i+1) for i, query in enumerate(queries)])
            total_time = time.time() - start_time
            return results, total_time

        results, total_time = asyncio.run(run_concurrent_requests())

        # Sort results by request ID
        results.sort(key=lambda x: x[0])

        print("✅ All custom document retrieval requests completed!")

        for request_id, elapsed_time, document_count, query, documents in results:
            print(
                f"Request {request_id}: ⏱️ {elapsed_time:.2f}s, 📄 {document_count} docs")
            print(f"🔍 Query: {query}")
            
            # Print the first document for each query
            if documents:
                first_doc = documents[0]
                print(f"   📋 First doc: {first_doc.get('metadata', {}).get('title', 'N/A')} (Score: {first_doc.get('score', 'N/A')})")
            else:
                print("   ⚠️ No documents found")
            print("")

        # Summary statistics
        avg_response_time = sum(result[1] for result in results) / len(results)
        avg_documents_per_query = sum(result[2]
                                      for result in results) / len(results)

        print("📊 CUSTOM QUERY SUMMARY:")
        print(f"📊 Average response time: {avg_response_time:.2f}s")
        print(f"📊 Average documents per query: {avg_documents_per_query:.2f}")
        print(f"📊 Total execution time: {total_time:.2f} seconds")
        print("")