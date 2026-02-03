# neat_flow/llms/registry.py

from llms.adapters.gemini import GeminiLLM
from llms.adapters.openrouter import OpenRouterLLM
from llms.base import BaseLLM

def get_llm(name: str) -> BaseLLM:
    registry = {
        "gemini": GeminiLLM,
        "openrouter": OpenRouterLLM,
    }

    if name not in registry:
        raise ValueError(f"Unknown LLM: {name}")

    return registry[name]()