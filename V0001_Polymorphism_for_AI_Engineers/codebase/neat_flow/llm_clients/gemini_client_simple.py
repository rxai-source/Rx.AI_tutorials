# gemini_client_simple.py

from utils.config import GEMINI_API_KEY
from typing import Optional, Any, Type
from google import genai
from google.genai import types
import json

class GeminiClient:
    def __init__(self, model_id: str = "gemini-2.0-flash", api_key: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found.")
        
        self.client = genai.Client(api_key=self.api_key)
        self.default_text_model = model_id

    # ---------------------------------------------------------
    # 1. TEXT GENERATION
    # ---------------------------------------------------------
    async def generate_text(self, prompt: str, model: Optional[str] = None) -> str:
        target_model = model or self.default_text_model
        try:
            response = await self.client.aio.models.generate_content(
                model=target_model,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Error generating text: {str(e)}"

    # ---------------------------------------------------------
    # 2. STRUCTURED OUTPUT (JSON)
    # ---------------------------------------------------------
    async def generate_structured(self, prompt: str, response_schema: Type[Any], model: Optional[str] = None) -> Any:
        target_model = model or self.default_text_model
        try:
            response = await self.client.aio.models.generate_content(
                model=target_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Structured Generation Error: {e}")
            return None