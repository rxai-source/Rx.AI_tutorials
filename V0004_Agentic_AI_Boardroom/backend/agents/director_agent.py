from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field
from agents.base_agent import BaseAgent

class AgentTask(BaseModel):
    agent_id: str
    task_description: str

class WritingPlan(BaseModel):
    topic: str
    needs_clarification: bool = False
    clarification_questions: List[str] = Field(default_factory=list)
    tasks: List[AgentTask] = Field(default_factory=list)

class DirectorAgent(BaseAgent):
    def __init__(self, llm=None, name="director", persona="Orchestrator", system_prompt=""):
        super().__init__(
            name=name,
            persona=persona,
            llm=llm,
            system_prompt=system_prompt
        )

    async def plan(self, user_request: str) -> WritingPlan:
        return WritingPlan(topic=user_request)
