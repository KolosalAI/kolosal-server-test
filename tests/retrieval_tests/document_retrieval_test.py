"""Document retrieval test module for the Kolosal server."""
import time
import asyncio
from typing import List, Optional
import requests
import aiohttp
from tests.kolosal_tests import KolosalTestBase


class DocumentRetrievalTest(KolosalTestBase):
    """Test class for document retrieval functionality in Kolosal Server."""

    def retrieve_documents(self,
                           query: Optional[str] = "smartphone",
                           limit: Optional[int] = 10,
                           score_threshold: Optional[float] = 0.0) -> None:
        """Test retrieving documents based on a query."""
        print(f"🚀 Testing document retrieval with query: {query}")
        print("⏳ Sending request...")

        start_time = time.time()

        api_url = f"{self.client.base_url}/retrieve"
        payload = {
            "query": query,
            "limit": limit,
            "score_threshold": score_threshold
        }

        response = requests.post(api_url, json=payload, timeout=30)
        elapsed_time = time.time() - start_time

        assert response.status_code == 200, "Failed to retrieve documents."

        result = response.json()
        documents = result.get('documents', [])

        print("✅ Document retrieval completed!")
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

    def concurrent_retrieve_documents(self,
                                      queries: Optional[List[str]] = None,
                                      limit: Optional[int] = 10,
                                      score_threshold: Optional[float] = 0.0) -> None:
        """Test concurrent document retrieval requests with different queries."""

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

        async def single_request(query: str, request_id: int):
            start_time = time.time()

            api_url = f"{self.client.base_url}/retrieve"
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

        # Sort results by request ID to maintain order
        results.sort(key=lambda x: x[0])

        print("✅ All document retrieval requests completed!")

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

        print("📊 SUMMARY STATISTICS:")
        print(f"📊 Average response time: {avg_response_time:.2f}s")
        print(f"📊 Average documents per query: {avg_documents_per_query:.2f}")
        print(f"📊 Total concurrent execution time: {total_time:.2f} seconds")
        print("")

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

            api_url = f"{self.client.base_url}/retrieve"
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