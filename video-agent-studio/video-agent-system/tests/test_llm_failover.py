"""Pure unit tests for LLM provider ordering; these do not call external APIs."""

import asyncio
from unittest.mock import AsyncMock

from src.llm_clients.failover_client import DEFAULT_FAILOVER_ORDER, LLMFailoverClient, LLMTarget


def test_failover_uses_the_next_model_after_a_provider_error():
    targets = (LLMTarget("gemini", "first"), LLMTarget("openrouter", "second"))
    client = LLMFailoverClient(targets=targets)
    client._generate = AsyncMock(side_effect=[RuntimeError("quota exceeded"), "OK"])

    assert asyncio.run(client.generate_text("ping")) == "OK"
    assert client._generate.await_count == 2
    assert client._generate.await_args_list[0].args[0] == targets[0]
    assert client._generate.await_args_list[1].args[0] == targets[1]
    assert client.last_attempts[-1]["status"] == "completed"


def test_failover_reports_all_provider_errors():
    targets = (LLMTarget("gemini", "first"), LLMTarget("groq", "second"))
    client = LLMFailoverClient(targets=targets)
    client._generate = AsyncMock(side_effect=[RuntimeError("quota"), RuntimeError("unavailable")])

    try:
        asyncio.run(client.generate_text("ping"))
    except RuntimeError as exc:
        assert "gemini/first: quota" in str(exc)
        assert "groq/second: unavailable" in str(exc)
    else:
        raise AssertionError("Expected an error after every provider failed")


def test_default_order_uses_openrouter_free_then_groq():
    assert [(target.provider, target.model) for target in DEFAULT_FAILOVER_ORDER] == [
        ("gemini", "gemini-3.8-flash"),
        ("gemini", "gemini-3.7-flash"),
        ("gemini", "gemini-3.6-flash"),
        ("openrouter", "openrouter/free"),
        ("groq", "openai/gpt-oss-120b"),
    ]


def test_explicit_model_selection_bypasses_the_default_chain():
    client = LLMFailoverClient()
    client._generate = AsyncMock(return_value="OK")

    assert asyncio.run(client.generate_text("ping", model="gemini-3.5-flash")) == "OK"
    assert client._generate.await_args.args[0] == LLMTarget("gemini", "gemini-3.5-flash")
