# backend/agents/dynamic_agent.py
"""
DynamicAgent — Configuration-driven agent persona.

Replaces the hardcoded Director/Writer/Critic/SME agents. It dynamically absorbs 
its identity, role, and capabilities from a `Persona` configuration block.

Isolation Guarantee:
- Uses the private `_scratchpad` for intermediate reasoning via `think()`.
- Public execution methods (`execute()`) must output to the group chat using 
  `respond()` or `respond_structured()`, which explicitly clear the scratchpad.
"""

from __future__ import annotations
from typing import Any, Dict

from agents.base_agent import BaseAgent
from core.templates.loader import Persona
from llms.base import BaseLLM
from graph.state import DynamicRoomState


class DynamicAgent(BaseAgent):
    """
    A generic agent class that dynamically configures its system prompt and tools 
    based on a Persona defined in the YAML/JSON Room Template.
    """

    def __init__(self, persona_config: Persona, llm: BaseLLM):
        # Build the dynamic system prompt
        system_prompt = (
            f"You are {persona_config.display_name or persona_config.id}.\n"
            f"Your Role: {persona_config.role}\n"
            f"Description: {persona_config.description or 'No specific description provided.'}\n\n"
            f"Follow all instructions and stay in character. Provide structured and concise outputs."
        )

        super().__init__(
            name=persona_config.id,
            persona=persona_config.role,
            llm=llm,
            system_prompt=system_prompt,
            max_argument_quota=persona_config.max_argument_quota if persona_config.max_argument_quota is not None else 3,
            synthesize_json_template=persona_config.synthesize_json_template,
        )

        # Placeholder for Tool Registry integration
        # Will dynamically bind environment-specific action spaces later.
        self.tools = persona_config.tools or []

    async def execute(self, state: DynamicRoomState, stage_context: str) -> Dict[str, Any]:
        """
        Executes a task for the current stage.
        
        ISOLATION ENFORCEMENT:
        1. Uses `think()` which appends to the private `_scratchpad`.
        2. Uses `respond()` which generates the final output AND clears the `_scratchpad`.
        3. Returns a state update dict; `DynamicRoomState` NEVER ingests `_scratchpad` data.
        """
        # Step 1: Private Reasoning (Scratchpad isolated)
        reasoning_context = (
            f"Current Stage: {state['current_stage']}\n"
            f"User Request: {state['user_request']}\n"
            f"Context: {stage_context}\n"
            f"Plan your approach."
        )
        await self.think(reasoning_context)
        
        # Step 2: Public Response (Clears scratchpad internally)
        action_prompt = (
            f"Based on your reasoning, provide your final public output for the stage '{state['current_stage']}'.\n"
            f"Address the user's overall goal: {state['user_request']}"
        )
        final_output = await self.respond(action_prompt)
        
        # Return partial state update without any scratchpad leaks
        return {
            "output": final_output,
            "agent": self.name
        }
