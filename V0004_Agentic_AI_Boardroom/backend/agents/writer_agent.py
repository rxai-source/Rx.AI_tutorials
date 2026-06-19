from __future__ import annotations
from pydantic import BaseModel
from agents.base_agent import BaseAgent

class WriterDraft(BaseModel):
    draft_content: str

class WriterAgent(BaseAgent):
    def __init__(self, llm=None, name="writer", persona="Creative Copywriter", system_prompt=""):
        super().__init__(
            name=name,
            persona=persona,
            llm=llm,
            system_prompt=system_prompt
        )
