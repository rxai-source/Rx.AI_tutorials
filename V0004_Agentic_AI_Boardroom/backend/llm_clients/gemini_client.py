# backend/llm_clients/gemini_client.py
"""
Async Gemini LLM client — mirrors and extends the codebase reference implementation.
"""

import json
from typing import Any, Optional, Type

from google import genai
from google.genai import types

from core.config import get_settings

settings = get_settings()


class GeminiClient:
    def __init__(
        self,
        model_id: str = "gemini-2.0-flash",
        api_key: Optional[str] = None,
    ):
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured.")

        self.client = genai.Client(api_key=self.api_key)
        self.default_text_model = model_id

    # ------------------------------------------------------------------
    # 1. TEXT GENERATION
    # ------------------------------------------------------------------
    async def generate_text(self, prompt: str, model: Optional[str] = None) -> str:
        target_model = model or self.default_text_model
        try:
            response = await self.client.aio.models.generate_content(
                model=target_model,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            return f"[GeminiClient] Text generation error: {e}"

    # ------------------------------------------------------------------
    # 2. STRUCTURED OUTPUT (JSON schema enforced)
    # ------------------------------------------------------------------
    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[Any],
        model: Optional[str] = None,
    ) -> Any:
        target_model = model or self.default_text_model
        try:
            response = await self.client.aio.models.generate_content(
                model=target_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"[GeminiClient] Structured generation error: {e}")
            return None
