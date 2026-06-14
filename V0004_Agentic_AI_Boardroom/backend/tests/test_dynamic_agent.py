# backend/tests/test_dynamic_agent.py
"""
Unit tests for DynamicAgent.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from core.templates.loader import Persona
from agents.dynamic_agent import DynamicAgent
from llms.base import BaseLLM


class MockLLM(BaseLLM):
    """Minimal LLM mock for testing."""

    async def generate_text(self, prompt: str) -> str:
        return "mock final response"

    async def generate_structured(self, prompt: str, response_schema):
        return {"mock_key": "mock_value"}


def test_dynamic_agent_initialization():
    """Verify that DynamicAgent correctly absorbs configurations from Persona."""
    persona = Persona(
        id="test_agent",
        display_name="Test Agent",
        role="Tester",
        tools=["test_tool"],
        description="A test persona.",
        max_argument_quota=6,
        synthesize_json_template={"output_format": "json"}
    )
    llm = MockLLM()
    agent = DynamicAgent(persona_config=persona, llm=llm)

    assert agent.name == "test_agent"
    assert agent.persona == "Tester"
    assert agent.max_argument_quota == 6
    assert agent.synthesize_json_template == {"output_format": "json"}
    assert "You are Test Agent." in agent.system_prompt
    assert "Your Role: Tester" in agent.system_prompt
    assert "A test persona." in agent.system_prompt
    assert agent.tools == ["test_tool"]


@pytest.mark.asyncio
async def test_dynamic_agent_scratchpad_isolation():
    """Verify that execution uses and isolates scratchpad reasoning."""
    persona = Persona(
        id="test_agent",
        display_name="Test Agent",
        role="Tester",
        tools=[],
        description="A test persona.",
        max_argument_quota=3,
        synthesize_json_template=None
    )
    llm = MockLLM()
    agent = DynamicAgent(persona_config=persona, llm=llm)

    # Before execute, scratchpad should be empty
    assert len(agent.get_scratchpad_snapshot()) == 0

    from graph.state import DynamicRoomState
    state: DynamicRoomState = {
        "user_request": "Test request",
        "messages": [],
        "current_stage": "test_stage",
        "status": "active",
        "error": None,
        "shared_data": {}
    }

    result = await agent.execute(state, "Test context info")

    # The returned result should contain final public output
    assert result["output"] == "mock final response"
    assert result["agent"] == "test_agent"

    # Execution should clean up scratchpad internally via respond()
    assert len(agent.get_scratchpad_snapshot()) == 0
