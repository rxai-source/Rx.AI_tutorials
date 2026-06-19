from __future__ import annotations
from pydantic import BaseModel
from agents.base_agent import BaseAgent

class CriticReport(BaseModel):
    verdict: str
    feedback: str

class CriticAgent(BaseAgent):
    def __init__(self, llm=None, name="critic", persona="Devil's Advocate", system_prompt=""):
        super().__init__(
            name=name,
            persona=persona,
            llm=llm,
            system_prompt=system_prompt
        )
