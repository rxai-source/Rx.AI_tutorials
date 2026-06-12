# backend/graph/state.py
"""
LangGraph shared state for the AI Boardroom workflow.

ISOLATION ARCHITECTURE
======================
The BoardroomState is the SHARED GROUP CHAT state — it flows through every
node in the LangGraph graph.  The following fields are STRICTLY PUBLIC and
visible to all agents and the user-facing API:

  - user_request
  - writing_plan
  - sme_report
  - writer_draft
  - critic_report
  - final_output
  - messages  (user-facing conversation log)
  - status / error

Fields that MUST NEVER appear in BoardroomState:
  - Any agent's _scratchpad contents
  - Partial or intermediate reasoning steps
  - Raw chain-of-thought text

Each agent is responsible for enforcing its own isolation boundary by only
writing its final structured output into these fields.
"""

from __future__ import annotations

from typing import Annotated, Any, Optional, Dict
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

from agents.director_agent import WritingPlan
from agents.tech_sme_agent import SMEReport
from agents.writer_agent import WriterDraft
from agents.critic_agent import CriticReport


class BoardroomState(TypedDict):
    """
    The SHARED GROUP CHAT state — all fields are PUBLIC.

    ┌─────────────────────────────────────────────────────────────────┐
    │  PUBLIC SHARED STATE (group chat)                                │
    │  ✓ user_request   ✓ writing_plan   ✓ sme_report                 │
    │  ✓ writer_draft   ✓ critic_report  ✓ final_output               │
    │  ✓ messages       ✓ status         ✓ error                      │
    └─────────────────────────────────────────────────────────────────┘
    ┌─────────────────────────────────────────────────────────────────┐
    │  PRIVATE SCRATCHPADS (per-agent, NEVER in this state)           │
    │  ✗ director._scratchpad                                          │
    │  ✗ tech_sme._scratchpad                                          │
    │  ✗ writer._scratchpad                                            │
    │  ✗ critic._scratchpad                                            │
    └─────────────────────────────────────────────────────────────────┘
    """

    # --- Input ---
    user_request: str

    # --- Agent outputs (structured, PUBLIC) ---
    writing_plan: Optional[WritingPlan]
    sme_report: Optional[SMEReport]
    writer_draft: Optional[WriterDraft]
    critic_report: Optional[CriticReport]

    # --- Final content delivered to the user ---
    final_output: Optional[str]

    # --- User-facing conversation log ---
    # Uses LangGraph's add_messages reducer so messages accumulate correctly
    messages: Annotated[list[BaseMessage], add_messages]

    # --- Workflow control ---
    status: str          # e.g. "planning", "researching", "drafting", "reviewing", "done"
    error: Optional[str] # populated if a node fails
    revision_count: int  # tracks how many critic revision cycles have occurred


class DynamicRoomState(TypedDict):
    """
    The DYNAMIC SHARED GROUP CHAT state for Configuration-Driven templates.
    All fields are PUBLIC and synchronized to clients via WebSockets.

    Memory Isolation Guardrail:
    - THIS STATE MUST NEVER INGEST OR LEAK `_scratchpad` REASONING DATA.
    - Each agent is explicitly responsible for wiping its scratchpad and
      only contributing final, structured responses to `shared_data` or `messages`.
    """

    # --- Input ---
    user_request: str

    # --- User-facing conversation log ---
    # Accumulates messages correctly over the graph execution
    messages: Annotated[list[BaseMessage], add_messages]

    # --- Workflow control ---
    current_stage: str       # e.g., "requirements", "drafting"
    status: str              # e.g., "active", "done", "error"
    error: Optional[str]     # populated if a node fails

    # --- Flexible structured output ---
    # Stores domain-specific data such as ScriptDraft, JSON Prototypes, or DealOffers
    shared_data: Dict[str, Any]
