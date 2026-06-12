# backend/llms/adapters/openrouter.py
"""
OpenRouter LLM adapter — bridges BaseLLM interface to OpenRouterClient.
"""

from typing import Any, Type

from llms.base import BaseLLM
from llm_clients.openrouter_client import OpenRouterClient


class OpenRouterLLM(BaseLLM):
    def __init__(self, model_id: str = "nvidia/nemotron-3-nano-30b-a3b:free"):
        self.client = OpenRouterClient(model_id=model_id)

    async def generate_text(self, prompt: str) -> str:
        return await self.client.generate_text(prompt=prompt)

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[Any],
    ) -> Any:
        return await self.client.generate_structured(
            prompt=prompt,
            json_schema=response_schema,
        )
