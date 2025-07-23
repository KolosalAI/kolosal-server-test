"""OpenAI API Compatible Tests for Embedding Endpoints."""
import time
import asyncio
from typing import Optional, List

from tests.kolosal_tests import KolosalTestBase


class EmbeddingTest(KolosalTestBase):
    """Test class for OpenAI API compatible embedding endpoints."""

    def basic_embedding(self,
                        model_name="text-embedding-ada-002",
                        input_text: Optional[str] = "Hello, world!") -> bool:
        """Test creating an embedding."""
        # Status Report
        print(f"🚀 Testing embedding with model: {model_name}")
        print("⏳ Sending request...")

        try:
            initial_time = time.time()
            response = self.client.embeddings.create(
                model=model_name,
                input=input_text
            )
            elapsed_time = time.time() - initial_time

            # Validate response structure (following api_test.py pattern)
            if response.data and len(response.data) > 0 and response.data[0].embedding:
                embedding_dim = len(response.data[0].embedding)
                print(f"✅ Embedding generation test: PASS - Generated embedding with {embedding_dim} dimensions")
                print(f"Input text: {input_text}")
                print(f"⏱️ Elapsed time: {elapsed_time:.2f} seconds")
                if hasattr(response, 'usage') and response.usage:
                    print(f"📊 Usage: {response.usage.total_tokens} tokens")
                print("")
                return True
            else:
                print(f"❌ Embedding generation test: FAIL - No embeddings in response")
                print("")
                return False
            
        except Exception as e:
            print(f"❌ Embedding generation test: FAIL - {str(e)}")
            print("")
            return False

    def concurrent_embedding(self,
                             model_name="text-embedding-ada-002",
                             input_texts: Optional[List[str]] = None) -> bool:
        """Test concurrent embedding requests using asyncio."""

        if input_texts is None:
            input_texts = [
                "Hello, world!",
                "The quick brown fox jumps over the lazy dog.",
                "Machine learning is transforming technology.",
                "Natural language processing enables computers to understand text.",
                "Embeddings convert text into numerical vectors."
            ]

        print(
            f"🚀 Testing {len(input_texts)} concurrent embeddings with model: {model_name}")
        print("⏳ Sending concurrent requests...")

        try:
            async def single_request(text, request_id):
                start_time = time.time()
                response = await self.async_client.embeddings.create(
                    model=model_name,
                    input=text
                )
                elapsed_time = time.time() - start_time
                embedding_dims = len(response.data[0].embedding)
                total_tokens = response.usage.total_tokens if response.usage else 0
                return request_id, elapsed_time, embedding_dims, total_tokens, text

            async def run_concurrent_requests():
                start_time = time.time()
                results = await asyncio.gather(*[single_request(text, i+1) for i, text in enumerate(input_texts)])
                total_time = time.time() - start_time
                return results, total_time

            results, total_time = asyncio.run(run_concurrent_requests())

            results.sort(key=lambda x: x[0])

            print("✅ All responses received!")
            total_tokens = 0
            successful_requests = 0
            
            for request_id, elapsed_time, embedding_dims, tokens, text in results:
                print(
                    f"Request {request_id}: ⏱️ {elapsed_time:.2f}s, 📏 {embedding_dims} dims, 📊 {tokens} tokens")
                print(f"Input: {text}")
                print("")
                total_tokens += tokens
                if embedding_dims > 0:  # Count successful embeddings
                    successful_requests += 1

            print(
                f"📊 Average time per request: {sum(result[1] for result in results) / len(results):.2f}s")
            print(
                f"📊 Total concurrent execution time: {total_time:.2f} seconds")
            print(f"📊 Total tokens processed: {total_tokens}")
            print(f"📊 Successful requests: {successful_requests}/{len(input_texts)}")
            print("")
            
            # Return True if at least 80% of requests succeeded
            success_rate = successful_requests / len(input_texts)
            return success_rate >= 0.8
            
        except Exception as e:
            print(f"❌ Concurrent embedding failed: {str(e)}")
            print("")
            return False
