"""Async Groq client used as the final LLM failover provider."""

import os
from typing import Optional

from dotenv import load_dotenv
import httpx

load_dotenv()


class GroqClient:
    """Minimal OpenAI-compatible client for GPT-OSS models served by Groq."""

    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, model_id: str = "openai/gpt-oss-120b", api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.default_model = model_id
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found.")

    async def generate_text(self, prompt: str, model: Optional[str] = None) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model or self.default_model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 32,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.BASE_URL, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
