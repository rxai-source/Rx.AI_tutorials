# backend/agents/base_agent.py
"""
BaseAgent — foundational class for all AI Boardroom personas.

Extends the codebase's Agent template with:
  - Named persona identity
  - System prompt injection
  - ISOLATED private scratchpad (never exposed to the group chat)
  - Structured LangChain message building
"""

from __future__ import annotations

from typing import Any, Optional, Type, Dict
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from llms.base import BaseLLM


class BaseAgent:
    """
    Base class for all boardroom AI personas.

    Isolation rule
    --------------
    Each agent has a private `_scratchpad` list that accumulates intermediate
    reasoning steps.  This scratchpad is NEVER forwarded to the shared group
    chat or returned to the user.  Only the final answer — explicitly produced
    by calling `respond()` — is eligible to enter the shared context.
    """

    def __init__(
        self,
        name: str,
        persona: str,
        llm: BaseLLM,
        system_prompt: str,
        max_argument_quota: int = 3,
        synthesize_json_template: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.persona = persona
        self.llm = llm
        self.system_prompt = system_prompt
        self.max_argument_quota = max_argument_quota
        self.synthesize_json_template = synthesize_json_template

        # ------------------------------------------------------------------ #
        # PRIVATE SCRATCHPAD — isolation boundary                             #
        # RULE: This list must NEVER be serialised into the shared group chat #
        # ------------------------------------------------------------------ #
        self._scratchpad: list[dict[str, str]] = []

    # ------------------------------------------------------------------
    # Scratchpad helpers (private reasoning — isolated)
    # ------------------------------------------------------------------

    def _scratch_append(self, role: str, content: str) -> None:
        """Append a private reasoning step to the scratchpad."""
        self._scratchpad.append({"role": role, "content": content, "agent": self.name})

    def _scratch_clear(self) -> None:
        """Clear the scratchpad after completing a reasoning cycle."""
        self._scratchpad.clear()

    def get_scratchpad_snapshot(self) -> list[dict[str, str]]:
        """
        Read-only view of the scratchpad for debugging / logging.
        MUST NOT be sent to any user-facing channel or group chat state.
        """
        return list(self._scratchpad)

    # ------------------------------------------------------------------
    # Core interaction methods
    # ------------------------------------------------------------------

    async def think(self, context: str) -> str:
        """
        Private reasoning step — result stays in the scratchpad.
        Returns the raw reasoning text (for internal use only).
        """
        reasoning_prompt = (
            f"[PRIVATE REASONING — NOT FOR PUBLICATION]\n\n"
            f"System: {self.system_prompt}\n\n"
            f"Context:\n{context}\n\n"
            f"Think step-by-step about your response. "
            f"This output is private and will NOT be shown to the user."
        )
        reasoning = await self.llm.generate_text(reasoning_prompt)
        self._scratch_append("reasoning", reasoning)
        return reasoning

    async def respond(self, prompt: str) -> str:
        """
        Generate the agent's final, publishable response.
        This is the ONLY output allowed into the shared group chat.
        """
        full_prompt = f"System: {self.system_prompt}\n\nUser: {prompt}"
        response = await self.llm.generate_text(full_prompt)
        self._scratch_clear()
        return response

    async def respond_structured(
        self,
        prompt: str,
        response_schema: Type[Any],
    ) -> Any:
        """
        Generate a structured (JSON) response conforming to response_schema.
        This is the ONLY structured output allowed into the shared group chat.
        """
        full_prompt = f"System: {self.system_prompt}\n\nUser: {prompt}"
        result = await self.llm.generate_structured(full_prompt, response_schema)
        self._scratch_clear()
        return result

    async def run(self, prompt: str) -> None:
        """
        Simple run method — matches the codebase agent.py template interface.
        Prints the agent's response (for CLI usage / quick testing).
        """
        response = await self.respond(prompt)
        print(f"[{self.name}]: {response}")
