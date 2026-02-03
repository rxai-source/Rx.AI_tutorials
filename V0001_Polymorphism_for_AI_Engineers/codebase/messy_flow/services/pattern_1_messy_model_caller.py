# pattern_1_messy_model_caller.py

import sys
from pathlib import Path

# Add the parent directory to the path so we can import from llm_clients
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_clients.openai_client_simple import OpenAIClient
from llm_clients.gemini_client_simple import GeminiClient
from llm_clients.openrouter_client_simple import OpenRouterClient

async def call_llm(model_name: str, prompt: str):
    if model_name == "gemini":
        client = GeminiClient()
        return await client.generate_text(prompt=prompt)
    elif model_name == "openrouter":
        client = OpenRouterClient()
        return await client.generate_text(prompt=prompt)
    elif model_name == "openai":
        client = OpenAIClient()
        return client.generate(prompt)
    else:
        raise ValueError("Unknown model!")

# Your agent loop
async def main():
    #model = "openai"   # switching this breaks multiple files
    print("Testing with Gemini model...")
    model = "gemini"
    response = await call_llm(model, "Multi-agentic Solutions are great! I am going to use this topic for my Rx.AI channel Youtube video.. How does this sound? Tell me in brief.")
    print(response)
    print("****************************************")
    print("Testing with OpenRouter model...")
    model = "openrouter"
    response = await call_llm(model, "Multi-agentic Solutions are great! I am going to use this topic for my Rx.AI channel Youtube video.. How does this sound? Tell me in brief.")
    print(response)
    print("****************************************")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())