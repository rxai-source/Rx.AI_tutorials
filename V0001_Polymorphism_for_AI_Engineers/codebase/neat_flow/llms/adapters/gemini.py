# neat_flow/llms/adapters/gemini.py

from llms.base import BaseLLM
from llm_clients.gemini_client_simple import GeminiClient
from typing import Any, Type

class GeminiLLM(BaseLLM):
    def __init__(self):
        self.client = GeminiClient()

    async def generate_text(self, prompt: str) -> str:
        return await self.client.generate_text(prompt=prompt)

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[Any]
    ) -> Any:
        return await self.client.generate_structured(
            prompt=prompt,
            response_schema=response_schema
        )