# backend/llms/registry.py
"""
LLM registry — resolves a provider name string to a concrete BaseLLM instance.
Mirrors the codebase reference implementation.
"""

from llms.base import BaseLLM
from llms.adapters.gemini import GeminiLLM
from llms.adapters.openrouter import OpenRouterLLM


def get_llm(name: str) -> BaseLLM:
    """
    Factory function: returns an LLM instance by provider name.

    Supported names:
        "gemini"      -> GeminiLLM (google-genai)
        "openrouter"  -> OpenRouterLLM (Nemotron / other OpenRouter models)
    """
    registry: dict[str, type[BaseLLM]] = {
        "gemini": GeminiLLM,
        "openrouter": OpenRouterLLM,
    }

    if name not in registry:
        raise ValueError(
            f"Unknown LLM provider: '{name}'. Available: {list(registry.keys())}"
        )

    return registry[name]()
