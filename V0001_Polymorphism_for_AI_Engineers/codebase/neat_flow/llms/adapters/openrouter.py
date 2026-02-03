# neat_flow/llms/adapters/openrouter.py

from llms.base import BaseLLM
from llm_clients.openrouter_client_simple import OpenRouterClient
from typing import Any, Type

class OpenRouterLLM(BaseLLM):
    def __init__(self):
        self.client = OpenRouterClient()

    async def generate_text(self, prompt: str) -> str:
        return await self.client.generate_text(prompt=prompt)

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[Any]
    ) -> Any:
        return await self.client.generate_structured(
            prompt=prompt,
            json_schema=response_schema
        )