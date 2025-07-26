"""OpenAI API Compatible Tests for Embedding Endpoints."""
import time
import asyncio
import json
from typing import Optional, List

from tests.kolosal_tests import KolosalTestBase


class EmbeddingTest(KolosalTestBase):
    """Test class for OpenAI API compatible embedding endpoints."""

    def basic_embedding(self,
                        model_name="text-embedding-ada-002",
                        input_text: Optional[str] = "Hello, world!") -> bool:
        """Test creating an embedding with comprehensive logging."""
        # Log test start
        self.log_test_start("Basic Embedding Test", f"Model: {model_name}")
        
        # Status Report
        print(f"🚀 Testing embedding with model: {model_name}")
        print("⏳ Sending request...")

        try:
            initial_time = time.time()
            
            # Prepare request data for logging
            request_data = {
                "model": model_name,
                "input": input_text
            }
            
            # Log the request details
            print(f"📤 Request URL: {self.client.base_url}/v1/embeddings")
            print(f"📦 Request payload: {json.dumps(request_data, indent=2)}")
            print(f"📊 Request details:")
            print(f"   - Model: {model_name}")
            print(f"   - Input text: {input_text}")
            print(f"   - Input length: {len(input_text)} characters")
            
            response = self.client.embeddings.create(
                model=model_name,
                input=input_text
            )
            elapsed_time = time.time() - initial_time
            
            # Log response details
            print(f"📥 Response received in {elapsed_time:.2f} seconds")
            if response.data and len(response.data) > 0:
                embedding_dim = len(response.data[0].embedding)
                response_data = {
                    "data": [
                        {
                            "embedding_dimensions": embedding_dim,
                            "embedding_preview": response.data[0].embedding[:5] if embedding_dim >= 5 else response.data[0].embedding
                        }
                    ],
                    "model": getattr(response, 'model', model_name),
                    "usage": {
                        "prompt_tokens": getattr(response.usage, 'prompt_tokens', 0) if hasattr(response, 'usage') and response.usage else 0,
                        "total_tokens": getattr(response.usage, 'total_tokens', 0) if hasattr(response, 'usage') and response.usage else 0
                    }
                }
                print(f"📄 Response content: {json.dumps(response_data, indent=2)}")
            else:
                print(f"📄 Response: No embedding data received")

            # Validate response structure (following api_test.py pattern)
            if response.data and len(response.data) > 0 and response.data[0].embedding:
                embedding_dim = len(response.data[0].embedding)
                print(f"✅ Embedding generation test: PASS - Generated embedding with {embedding_dim} dimensions")
                print(f"Input text: {input_text}")
                print(f"⏱️ Elapsed time: {elapsed_time:.2f} seconds")
                if hasattr(response, 'usage') and response.usage:
                    print(f"📊 Usage: {response.usage.total_tokens} tokens")
                print("")
                
                # Log test completion
                self.log_test_end("Basic Embedding Test", {
                    "success": True,
                    "embedding_dimensions": embedding_dim,
                    "elapsed_time": elapsed_time,
                    "input_length": len(input_text),
                    "model": model_name
                })
                return True
            else:
                print(f"❌ Embedding generation test: FAIL - No embeddings in response")
                print("")
                self.log_test_end("Basic Embedding Test", {
                    "success": False,
                    "error": "No embeddings in response",
                    "model": model_name
                })
                return False
            
        except Exception as e:
            print(f"❌ Embedding generation test: FAIL - {str(e)}")
            print("")
            self.log_test_end("Basic Embedding Test", {
                "success": False,
                "error": str(e),
                "model": model_name
            })
            return False

    def concurrent_embedding(self,
                             model_name="text-embedding-ada-002",
                             input_texts: Optional[List[str]] = None) -> bool:
        """Test concurrent embedding requests using asyncio with comprehensive logging."""
        # Log test start
        self.log_test_start("Concurrent Embedding Test", f"Model: {model_name}")

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
        
        # Log request details
        request_config = {
            "model": model_name,
            "concurrent_requests": len(input_texts),
            "input_texts": input_texts
        }
        print(f"📤 Request configuration: {json.dumps(request_config, indent=2)}")

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
            
            # Log response summary
            response_summary = {
                "total_requests": len(input_texts),
                "total_time": total_time,
                "results": [
                    {
                        "request_id": result[0],
                        "elapsed_time": result[1],
                        "embedding_dimensions": result[2],
                        "tokens": result[3],
                        "input_text": result[4][:50] + "..." if len(result[4]) > 50 else result[4]
                    } for result in results
                ]
            }
            print(f"📥 Concurrent requests summary: {json.dumps(response_summary, indent=2)}")

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
            
            # Log test completion
            self.log_test_end("Concurrent Embedding Test", {
                "success": success_rate >= 0.8,
                "success_rate": success_rate,
                "total_requests": len(input_texts),
                "successful_requests": successful_requests,
                "total_time": total_time,
                "total_tokens": total_tokens,
                "model": model_name
            })
            
            return success_rate >= 0.8
            
        except Exception as e:
            print(f"❌ Concurrent embedding failed: {str(e)}")
            print("")
            self.log_test_end("Concurrent Embedding Test", {
                "success": False,
                "error": str(e),
                "model": model_name
            })
            return False
