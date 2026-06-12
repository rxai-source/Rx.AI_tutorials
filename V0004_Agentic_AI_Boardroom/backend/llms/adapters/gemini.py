# backend/llms/adapters/gemini.py
"""
Gemini LLM adapter — bridges BaseLLM interface to GeminiClient.
"""

from typing import Any, Type

from llms.base import BaseLLM
from llm_clients.gemini_client import GeminiClient


class GeminiLLM(BaseLLM):
    def __init__(self, model_id: str = "gemini-2.0-flash"):
        self.client = GeminiClient(model_id=model_id)

    async def generate_text(self, prompt: str) -> str:
        return await self.client.generate_text(prompt=prompt)

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[Any],
    ) -> Any:
        return await self.client.generate_structured(
            prompt=prompt,
            response_schema=response_schema,
        )
