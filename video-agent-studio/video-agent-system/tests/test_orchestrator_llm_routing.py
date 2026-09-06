"""Orchestrator-level tests for the production LLM failover route."""

import asyncio
from unittest.mock import AsyncMock

from src.agent.orchestrator import Orchestrator
from src.llm_clients.failover_client import DEFAULT_FAILOVER_ORDER, LLMFailoverClient


def test_orchestrator_defaults_to_the_production_failover_client():
    assert isinstance(Orchestrator().llm_client, LLMFailoverClient)


def test_orchestrator_routes_through_every_fallback_before_groq_success():
    """A plan request reaches Groq only after every preceding model has failed."""
    failover_client = LLMFailoverClient()
    groq_plan = (
        '{"tasks": [{"id": "task_1", "tool_name": "generate_tts", '
        '"description": "Create narration", "arguments": {"text": "Hello"}}]}'
    )
    failover_client._generate = AsyncMock(
        side_effect=[
            RuntimeError("Gemini 3.8 429 rate limit"),
            RuntimeError("Gemini 3.7 rate limit"),
            RuntimeError("Gemini 3.6 unavailable"),
            RuntimeError("OpenRouter unavailable"),
            groq_plan,
        ]
    )
    orchestrator = Orchestrator(llm_client=failover_client)
    orchestrator.get_available_mcp_tools = AsyncMock(return_value=[])

    plan = asyncio.run(orchestrator.create_plan("Create a narration"))

    assert plan.tasks == [{
        "id": "task_1",
        "tool_name": "generate_tts",
        "description": "Create narration",
        "arguments": {"text": "Hello"},
    }]
    assert [call.args[0] for call in failover_client._generate.await_args_list] == list(
        DEFAULT_FAILOVER_ORDER
    )
