"""Base Class for Kolosal Server API Test"""
from typing import Optional
from openai import OpenAI, AsyncOpenAI


class KolosalTestBase():
    """Base Class for Kolosal Server API Test"""

    client: OpenAI
    async_client: AsyncOpenAI

    def __init__(self, base_url: Optional[str] = "http://localhost:8084",
                 api_key: Optional[str] = "TEST_API_KEY") -> None:
        """Initialize the KolosalTestBase with optional base URL and API key."""
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        self.async_client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key
        )
