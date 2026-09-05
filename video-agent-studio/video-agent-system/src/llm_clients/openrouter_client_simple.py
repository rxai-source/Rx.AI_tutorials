"""Async OpenRouter chat-completions client with reasoning support."""

import json
import os
from typing import Any, Dict, List, Optional, Type

import httpx
from dotenv import load_dotenv

load_dotenv()


class OpenRouterError(RuntimeError):
    """Raised when OpenRouter cannot complete a chat request."""


class OpenRouterClient:
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(
        self,
        model_id: str = "openrouter/free",
        api_key: Optional[str] = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found.")
        self.default_model = model_id
        self.transport = transport
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        enable_reasoning: bool = True,
    ) -> str:
        """Generate text using OpenRouter; reasoning is enabled by default."""
        message = await self.generate_message(
            [{"role": "user", "content": prompt}], model=model, enable_reasoning=enable_reasoning
        )
        content = message.get("content")
        if not isinstance(content, str) or not content:
            raise OpenRouterError(f"OpenRouter returned no assistant content for {model or self.default_model}")
        return content

    async def generate_message(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        enable_reasoning: bool = True,
    ) -> Dict[str, Any]:
        """Return the assistant message, retaining OpenRouter reasoning details."""
        payload: Dict[str, Any] = {"model": model or self.default_model, "messages": messages}
        if enable_reasoning:
            payload["reasoning"] = {"enabled": True}
        data = await self._post(payload)
        choices = data.get("choices", [])
        if not choices or not isinstance(choices[0].get("message"), dict):
            raise OpenRouterError(f"OpenRouter returned no choices: {data}")
        return choices[0]["message"]

    async def generate_reasoning(
        self, prompt: str, model: Optional[str] = None, enable_reasoning: bool = True
    ) -> Dict[str, Any]:
        return await self.generate_message(
            [{"role": "user", "content": prompt}], model=model, enable_reasoning=enable_reasoning
        )

    async def continue_reasoning(
        self, previous_messages: List[Dict[str, Any]], model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Continue a conversation without stripping assistant reasoning_details."""
        return await self.generate_message(previous_messages, model=model, enable_reasoning=True)

    async def generate_structured(
        self, prompt: str, json_schema: Optional[Type[Any]] = None, model: Optional[str] = None
    ) -> Any:
        payload: Dict[str, Any] = {
            "model": model or self.default_model,
            "messages": [{"role": "user", "content": prompt}],
            "reasoning": {"enabled": True},
            "response_format": {"type": "json_object"},
        }
        if json_schema:
            payload["response_format"]["schema"] = json_schema
        message = (await self._post(payload)).get("choices", [{}])[0].get("message", {})
        try:
            return json.loads(message["content"])
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            raise OpenRouterError("OpenRouter returned invalid structured content") from exc

    async def _post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=60.0, transport=self.transport) as client:
                response = await client.post(self.BASE_URL, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            model = payload.get("model", self.default_model)
            raise OpenRouterError(f"OpenRouter request failed for {model}: {exc}") from exc
