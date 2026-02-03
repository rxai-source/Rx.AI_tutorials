# neat_flow/llms/base.py

from abc import ABC, abstractmethod
from typing import Any, Type

class BaseLLM(ABC):

    @abstractmethod
    async def generate_text(self, prompt: str) -> str:
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[Any]
    ) -> Any:
        pass
