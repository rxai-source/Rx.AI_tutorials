"""Ordered LLM failover used by the video-production agents."""

import time
from dataclasses import dataclass
from typing import Any

from src.llm_clients.gemini_client_simple import GeminiClient
from src.llm_clients.groq_client import GroqClient
from src.llm_clients.openrouter_client_simple import OpenRouterClient


@dataclass(frozen=True)
class LLMTarget:
    provider: str
    model: str


DEFAULT_FAILOVER_ORDER = (
    LLMTarget("gemini", "gemini-3.8-flash"),
    LLMTarget("gemini", "gemini-3.7-flash"),
    LLMTarget("gemini", "gemini-3.6-flash"),
    LLMTarget("openrouter", "openrouter/free"),
    LLMTarget("groq", "openai/gpt-oss-120b"),
)


class LLMFailoverClient:
    """Tries preferred models in order, including quota/rate-limit failures."""

    def __init__(self, targets: tuple[LLMTarget, ...] = DEFAULT_FAILOVER_ORDER) -> None:
        self.targets = targets
        self.last_attempts: list[dict[str, Any]] = []

    async def generate_text(self, prompt: str, model: str | None = None) -> str:
        """Generate using the ordered chain, or a caller-selected target model.

        The optional ``model`` argument preserves the common LLM-client interface
        used by the orchestrator.  Normal orchestration omits it and therefore
        always starts at Gemini 3.7 Flash.
        """
        targets = self.targets if model is None else (self._resolve_explicit_model(model),)
        errors: list[str] = []
        self.last_attempts = []
        for target in targets:
            started_at = time.time()
            try:
                result = await self._generate(target, prompt)
                self.last_attempts.append({
                    "provider": target.provider,
                    "model": target.model,
                    "status": "completed",
                    "duration_ms": round((time.time() - started_at) * 1000),
                })
                return result
            except Exception as exc:
                message = f"{target.provider}/{target.model}: {exc}"
                errors.append(message)
                self.last_attempts.append({
                    "provider": target.provider,
                    "model": target.model,
                    "status": "failed",
                    "error": str(exc),
                    "duration_ms": round((time.time() - started_at) * 1000),
                })
        raise RuntimeError("All configured LLM providers failed: " + " | ".join(errors))

    def _resolve_explicit_model(self, model: str) -> LLMTarget:
        for target in self.targets:
            if target.model == model:
                return target
        if model.startswith("gemini-"):
            return LLMTarget("gemini", model)
        if model.startswith("openai/gpt-oss"):
            return LLMTarget("groq", model)
        return LLMTarget("openrouter", model)

    async def _generate(self, target: LLMTarget, prompt: str) -> str:
        if target.provider == "gemini":
            client = GeminiClient(model_id=target.model)
        elif target.provider == "openrouter":
            client = OpenRouterClient(model_id=target.model)
        elif target.provider == "groq":
            client = GroqClient(model_id=target.model)
        else:
            raise ValueError(f"Unsupported LLM provider: {target.provider}")
        result = await client.generate_text(prompt)
        if not result or "error" in result.lower():
            raise RuntimeError(result or "Empty response")
        return result
