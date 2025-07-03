"""OpenAI API Compatible Tests for Completion Endpoints."""
import time
import asyncio
from typing import Optional

import tiktoken

from tests.kolosal_tests import KolosalTestBase


encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")


class CompletionTest(KolosalTestBase):
    """Test class for OpenAI API compatible completion endpoints."""

    def basic_completion(self,
                         model_name="gpt-3.5-turbo",
                         temperature: Optional[float] = 0.7,
                         max_tokens: Optional[int] = 128) -> None:
        """Test creating a completion."""
        # Status Report
        print(f"🚀 Testing chat completion with model: {model_name}")
        print("⏳ Sending request...")

        initial_time = time.time()
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Hello!"}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        elapsed_time = time.time() - initial_time

        # Status Report
        print(f"✅ Response received!")
        print(f"Response: {response.choices[0].message.content}")
        print(f"⏱️ Elapsed time: {elapsed_time:.2f} seconds")
        print(
            f"🔥 Tokens per second: {len(encoding.encode(response.choices[0].message.content)) / elapsed_time:.2f}")
        print("")

    def stream_completion(self,
                          model_name="gpt-3.5-turbo",
                          temperature: Optional[float] = 0.7,
                          max_tokens: Optional[int] = 128) -> None:
        """Test streaming a completion."""
        # Status Report
        print(f"🚀 Testing chat completion streaming with model: {model_name}")
        print("⏳ Sending request...")

        initial_time = time.time()
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Hello!"}],
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True
        )

        first_token_time = None
        response_text = ""

        for chunk in response:
            if chunk.choices[0].delta.content:
                if first_token_time is None:
                    first_token_time = time.time()
                response_text += chunk.choices[0].delta.content
                print(chunk.choices[0].delta.content, end="", flush=True)

        elapsed_time = time.time() - initial_time
        time_to_first_token = first_token_time - \
            initial_time if first_token_time else 0

        print(response)
        # Status Report
        print("\n✅ Response received!")
        print(f"⏱️ Time to first token: {time_to_first_token:.2f} seconds")
        print(f"⏱️ Total elapsed time: {elapsed_time:.2f} seconds")
        if len(encoding.encode(response_text)) > 0:
            print(
                f"🔥 Tokens per second: {len(encoding.encode(response_text)) / elapsed_time:.2f}")
        print("")

    def concurrent_completion(self,
                              model_name="gpt-3.5-turbo",
                              temperature: Optional[float] = 0.7,
                              max_tokens: Optional[int] = 128,
                              messages: Optional[list] = None) -> None:
        """Test concurrent completion requests using asyncio."""

        if messages is None:
            messages = [
                "Hello! How are you today?",
                "What's the weather like?",
                "Tell me a short joke.",
                "Explain quantum physics briefly.",
                "What's your favorite color?"
            ]

        print(
            f"🚀 Testing {len(messages)} concurrent chat completions with model: {model_name}")
        print("⏳ Sending concurrent requests...")

        async def single_request(message, request_id):
            start_time = time.time()
            response = await self.async_client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": message}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            elapsed_time = time.time() - start_time
            content = response.choices[0].message.content
            output_tokens = response.usage.completion_tokens if response.usage else len(
                encoding.encode(content))
            tokens_per_second = output_tokens / elapsed_time if elapsed_time > 0 else 0
            return request_id, elapsed_time, tokens_per_second, output_tokens, content

        async def run_concurrent_requests():
            start_time = time.time()
            results = await asyncio.gather(*[single_request(msg, i+1) for i, msg in enumerate(messages)])
            total_time = time.time() - start_time
            return results, total_time

        results, total_time = asyncio.run(run_concurrent_requests())

        results.sort(key=lambda x: x[0])

        print("✅ All responses received!")
        total_tokens = 0
        for request_id, elapsed_time, tokens_per_second, output_tokens, content in results:
            print(
                f"Request {request_id}: ⏱️ {elapsed_time:.2f}s, 🔥 {tokens_per_second:.2f} tokens/sec, 📝 {output_tokens} tokens")
            print(f"Response: {content}")
            print("")
            total_tokens += output_tokens

        print(
            f"📊 Average tokens per second per request: {sum(result[2] for result in results) / len(results):.2f}")
        print(
            f"📊 Overall tokens per second: {total_tokens / total_time if total_time > 0 else 0:.2f}")
        print(f"📊 Total concurrent execution time: {total_time:.2f} seconds")
        print(f"📊 Total tokens generated: {total_tokens}")
        print("")
