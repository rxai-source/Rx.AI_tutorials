# backend/tests/test_director_agent.py
"""
Unit tests for DirectorAgent.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from agents.director_agent import DirectorAgent, WritingPlan, AgentTask
from llms.base import BaseLLM


class MockLLM(BaseLLM):
    """Minimal LLM mock for testing."""

    async def generate_text(self, prompt: str) -> str:
        return "mock reasoning text"

    async def generate_structured(self, prompt: str, response_schema):
        return WritingPlan(
            needs_clarification=False,
            topic="Test Topic",
            objective="Write a test article.",
            target_audience="Developers",
            content_type="blog post",
            tone="professional",
            word_count_target=800,
            outline=["Introduction", "Main Content", "Conclusion"],
            tasks=[
                AgentTask(
                    agent="tech_sme",
                    task_description="Research technical details",
                    priority=1,
                ),
                AgentTask(
                    agent="writer",
                    task_description="Draft the article",
                    priority=2,
                    depends_on=["tech_sme"],
                ),
                AgentTask(
                    agent="critic",
                    task_description="Review the draft",
                    priority=3,
                    depends_on=["writer"],
                ),
            ],
            director_notes="Keep it concise.",
        ).model_dump()


@pytest.mark.asyncio
async def test_director_plan_returns_writing_plan():
    """Director.plan() should return a WritingPlan with correct fields."""
    llm = MockLLM()
    director = DirectorAgent(llm=llm)

    plan = await director.plan("Write a blog post about LangGraph agents.")

    assert isinstance(plan, WritingPlan)
    assert plan.needs_clarification is False
    assert plan.topic == "Test Topic"
    assert len(plan.tasks) == 3


@pytest.mark.asyncio
async def test_director_scratchpad_is_not_empty_after_think():
    """Director should have scratchpad entries after think() is called."""
    llm = MockLLM()
    director = DirectorAgent(llm=llm)

    await director.think("Test context")

    assert len(director.get_scratchpad_snapshot()) > 0


@pytest.mark.asyncio
async def test_director_scratchpad_cleared_after_plan():
    """After plan() completes, the scratchpad should be cleared."""
    llm = MockLLM()
    director = DirectorAgent(llm=llm)

    await director.plan("Write a blog post about LangGraph agents.")

    # After respond_structured(), scratchpad is cleared inside BaseAgent
    assert len(director.get_scratchpad_snapshot()) == 0


@pytest.mark.asyncio
async def test_scratchpad_never_in_plan_output():
    """The WritingPlan must not contain any scratchpad content."""
    llm = MockLLM()
    director = DirectorAgent(llm=llm)

    plan = await director.plan("Write something about AI.")
    plan_dict = plan.model_dump()

    # Scratchpad fields must not appear in the plan output
    assert "_scratchpad" not in plan_dict
    assert "reasoning" not in plan_dict
