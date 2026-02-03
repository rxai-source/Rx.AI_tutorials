# openai_client_simple.py

from openai import OpenAI
from utils.config import OPENAI_API_KEY

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def generate(self, prompt: str) -> str:
        """Unstructured text response"""
        resp = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message["content"]

    def generate_structured(self, prompt: str, schema: dict):
        """Return JSON-by-schema output"""
        resp = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_schema", "json_schema": schema},
        )
        return resp.choices[0].message["content"]