# backend/llms/base.py
"""
Abstract base class for all LLM adapters.
Mirrors the codebase reference implementation.
"""

from abc import ABC, abstractmethod
from typing import Any, Type


class BaseLLM(ABC):
    """Every LLM adapter must implement these two methods."""

    @abstractmethod
    async def generate_text(self, prompt: str) -> str:
        """Generate plain text from a prompt."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[Any],
    ) -> Any:
        """Generate structured (JSON) output conforming to response_schema."""
        pass
