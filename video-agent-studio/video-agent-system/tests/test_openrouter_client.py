"""Unit tests for the OpenRouter reasoning request/response contract."""

import asyncio
import json

import httpx

from src.llm_clients.openrouter_client_simple import OpenRouterClient


def test_reasoning_requests_use_openrouter_free_and_preserve_reasoning_details():
    requests: list[dict] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(json.loads(request.content))
        return httpx.Response(200, json={
            "choices": [{"message": {
                "role": "assistant",
                "content": "First answer",
                "reasoning_details": [{"type": "reasoning.encrypted", "data": "opaque"}],
            }}]
        })

    client = OpenRouterClient(
        api_key="test-key",
        transport=httpx.MockTransport(handler),
    )
    assistant_message = asyncio.run(client.generate_reasoning("Solve this"))
    asyncio.run(client.continue_reasoning([
        {"role": "user", "content": "Solve this"},
        assistant_message,
        {"role": "user", "content": "Continue"},
    ]))

    assert requests[0]["model"] == "openrouter/free"
    assert requests[0]["reasoning"] == {"enabled": True}
    assert requests[1]["messages"][1]["reasoning_details"] == assistant_message["reasoning_details"]
