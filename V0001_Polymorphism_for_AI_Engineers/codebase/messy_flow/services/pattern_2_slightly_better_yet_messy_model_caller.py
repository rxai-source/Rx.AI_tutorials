# pattern_2_factory_function.py
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from llm_clients
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_clients.openai_client_simple import OpenAIClient
from llm_clients.gemini_client_simple import GeminiClient

def get_llm_client(model_name: str):
    """Factory pattern — better, but still not ideal."""
    mapping = {
        "openai": lambda: OpenAIClient(api_key="OPENAI_KEY"),
        "gemini": lambda: GeminiClient(api_key="GEMINI_KEY"),
        # In reality, more models = more complexity here
    }

    if model_name not in mapping:
        raise ValueError(f"Unknown model: {model_name}")

    return mapping[model_name]()

# Agent code
def main():
    client = get_llm_client("gemini")
    print(client.generate("Explain transformers."))

if __name__ == "__main__":
    main()