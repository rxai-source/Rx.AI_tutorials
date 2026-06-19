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


@pytest.mark.asyncio
async def test_director_agent_methods():
    """Verify all methods for the Director persona loaded from writers_room.yaml."""
    from core.templates.loader import load_template
    import os

    template_path = os.path.join("backend", "core", "templates", "writers_room.yaml")
    template = load_template(template_path)
    director_config = next(p for p in template.personas if p.id == "director")

    print("\n[DEBUG] --- DIRECTOR PERSONA INITIALIZATION ---")
    print(f"[DEBUG] Display Name: {director_config.display_name}")
    print(f"[DEBUG] Role: {director_config.role}")
    print(f"[DEBUG] Description: {director_config.description}")
    print(f"[DEBUG] Tools: {director_config.tools}")
    print(f"[DEBUG] Max Argument Quota: {director_config.max_argument_quota}")
    print(f"[DEBUG] JSON Synthesis Template: {director_config.synthesize_json_template}")

    llm = MockLLM()
    director_agent = DynamicAgent(persona_config=director_config, llm=llm)

    print("\n[DEBUG] --- SYSTEM PROMPT ---")
    print(director_agent.system_prompt)

    # 1. Test configuration absorption
    assert director_agent.name == "director"
    assert director_agent.persona == "Orchestrator"
    assert director_agent.max_argument_quota == 10
    assert "You are Director." in director_agent.system_prompt
    assert "Your Role: Orchestrator" in director_agent.system_prompt
    assert "tools" in dir(director_agent)

    # 2. Test think() method (private reasoning)
    print("\n[DEBUG] --- TESTING think() ---")
    reasoning = await director_agent.think("Develop an outline for Sherlock Holmes AI story.")
    print(f"[DEBUG] Private Reasoning Output: {reasoning}")
    scratchpad = director_agent.get_scratchpad_snapshot()
    print(f"[DEBUG] Scratchpad Snapshot: {scratchpad}")
    assert len(scratchpad) == 1
    assert scratchpad[0]["role"] == "reasoning"
    assert scratchpad[0]["content"] == "mock final response"
    assert scratchpad[0]["agent"] == "director"

    # 3. Test respond() method (public final text response)
    print("\n[DEBUG] --- TESTING respond() ---")
    response = await director_agent.respond("Finalize script outline.")
    print(f"[DEBUG] Public Response: {response}")
    scratchpad_after = director_agent.get_scratchpad_snapshot()
    print(f"[DEBUG] Scratchpad After respond(): {scratchpad_after}")
    assert response == "mock final response"
    assert len(scratchpad_after) == 0

    # 4. Test respond_structured() method (JSON/Schema response)
    print("\n[DEBUG] --- TESTING respond_structured() ---")
    # Repopulate scratchpad to verify it gets cleared
    await director_agent.think("Some intermediate thoughts.")
    assert len(director_agent.get_scratchpad_snapshot()) == 1

    from pydantic import BaseModel
    class DummySchema(BaseModel):
        mock_key: str

    structured_response = await director_agent.respond_structured("Format output in schema.", DummySchema)
    print(f"[DEBUG] Structured Response: {structured_response}")
    scratchpad_after_structured = director_agent.get_scratchpad_snapshot()
    print(f"[DEBUG] Scratchpad After respond_structured(): {scratchpad_after_structured}")
    assert structured_response == {"mock_key": "mock_value"}
    assert len(scratchpad_after_structured) == 0

    # 5. Test execute() method (dynamic stage node execution flow)
    print("\n[DEBUG] --- TESTING execute() ---")
    from graph.state import DynamicRoomState
    state: DynamicRoomState = {
        "user_request": "Sherlock Holmes AI Story",
        "messages": [],
        "current_stage": "roundtable_review",
        "status": "active",
        "error": None,
        "shared_data": {}
    }

    result = await director_agent.execute(state, "Writer's draft is ready for review.")
    print(f"[DEBUG] Execute Result: {result}")
    scratchpad_after_execute = director_agent.get_scratchpad_snapshot()
    print(f"[DEBUG] Scratchpad After execute(): {scratchpad_after_execute}")
    assert result["output"] == "mock final response"
    assert result["agent"] == "director"
    assert len(scratchpad_after_execute) == 0

