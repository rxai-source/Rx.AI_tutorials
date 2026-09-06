"""Live, opt-in connectivity checks for each configured LLM endpoint.

Run with ``pytest -m connectivity``. Missing credentials skip only that
provider; credentials that are present but rejected cause a visible failure.
"""

import asyncio
import os

import pytest

from src.llm_clients.gemini_client_simple import GeminiClient
from src.llm_clients.groq_client import GroqClient
from src.llm_clients.openrouter_client_simple import OpenRouterClient


PROMPT = "Reply with exactly: OK"


def _run(coro):
    return asyncio.run(coro)


@pytest.mark.connectivity
@pytest.mark.parametrize("model", ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash"])
def test_gemini_model_connectivity(model: str):
    """Probe each Gemini tier independently, rather than using failover."""
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY is not configured")
    response = _run(GeminiClient(model_id=model).generate_text(PROMPT))
    assert response and not response.startswith("Error generating text:"), response


@pytest.mark.connectivity
def test_openrouter_free_connectivity():
    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip("OPENROUTER_API_KEY is not configured")
    response = _run(OpenRouterClient(model_id="openrouter/free").generate_text(PROMPT))
    assert response


@pytest.mark.connectivity
def test_groq_gpt_oss_connectivity():
    """Groq is optional until GROQ_API_KEY is added to .env."""
    if not os.getenv("GROQ_API_KEY"):
        pytest.skip("GROQ_API_KEY is not configured")
    response = _run(GroqClient(model_id="openai/gpt-oss-120b").generate_text(PROMPT))
    assert response
