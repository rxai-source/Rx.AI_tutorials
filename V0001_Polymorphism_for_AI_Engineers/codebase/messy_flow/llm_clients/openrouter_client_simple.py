import json
from typing import Optional, Any, Dict, List, Type
import httpx

from utils.config import OPENROUTER_API_KEY

class OpenRouterClient:
    """
    A clean async client for Nemotron via OpenRouter.
    Mirrors the structure of GeminiClient for consistency.
    """

    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, 
                model_id: str = "nvidia/nemotron-3-nano-30b-a3b:free",
                api_key: Optional[str] = None):
        
        self.api_key = api_key or OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found.")

        self.default_model = model_id

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    # ---------------------------------------------------------
    # 1. BASIC TEXT GENERATION (NO REASONING)
    # ---------------------------------------------------------
    async def generate_text(self, prompt: str, model: Optional[str] = None) -> str:
        target_model = model or self.default_model

        payload = {
            "model": target_model,
            "messages": [{"role": "user", "content": prompt}]
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.BASE_URL, headers=self.headers, json=payload
                )
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                return f"OpenRouter text generation error: {str(e)}"

    # ---------------------------------------------------------
    # 2. ENABLE REASONING MODE (Nemotron)
    # ---------------------------------------------------------
    async def generate_reasoning(
        self,
        prompt: str,
        model: Optional[str] = None,
        enable_reasoning: bool = True
    ) -> Dict[str, Any]:
        
        target_model = model or self.default_model

        payload = {
            "model": target_model,
            "messages": [{"role": "user", "content": prompt}],
            "reasoning": {"enabled": enable_reasoning}
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.BASE_URL, headers=self.headers, json=payload
                )
                data = response.json()
                return data["choices"][0]["message"]
            except Exception as e:
                return {"error": f"OpenRouter reasoning error: {str(e)}"}

    # ---------------------------------------------------------
    # 3. CONTINUE REASONING SESSION (Two-step reasoning)
    # ---------------------------------------------------------
    async def continue_reasoning(
        self,
        previous_messages: List[Dict[str, Any]],
        model: Optional[str] = None
    ) -> Dict[str, Any]:

        target_model = model or self.default_model
        
        payload = {
            "model": target_model,
            "messages": previous_messages,
            "reasoning": {"enabled": True}
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.BASE_URL, headers=self.headers, json=payload
                )
                return response.json()["choices"][0]["message"]
            except Exception as e:
                return {"error": f"Continuation reasoning error: {str(e)}"}

    # ---------------------------------------------------------
    # 4. STRUCTURED OUTPUT (Nemotron JSON responses)
    # ---------------------------------------------------------
    async def generate_structured(
        self,
        prompt: str,
        json_schema: Type[Any],
        model: Optional[str] = None
    ) -> Any:

        target_model = model or self.default_model

        payload = {
            "model": target_model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object", "schema": json_schema}
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.BASE_URL, headers=self.headers, json=payload
                )
                return json.loads(
                    response.json()["choices"][0]["message"]["content"]
                )
            except Exception as e:
                print(f"Nemotron Structured Output Error: {e}")
                return None
