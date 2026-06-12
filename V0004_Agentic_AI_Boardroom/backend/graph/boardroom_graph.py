# backend/graph/boardroom_graph.py
"""
AI Boardroom LangGraph workflow definition.

Graph topology:
  START
    │
    ▼
  director  ──── needs_clarification? ────► END (return clarification Q's)
    │
    ▼ (plan ready)
  tech_sme
    │
    ▼
  writer
    │
    ▼
  critic ──── revision_required? ──► writer (up to MAX_REVISIONS)
    │
    ▼ (approved or max revisions hit)
  END
"""

from __future__ import annotations

from langgraph.graph import StateGraph, START, END

from graph.state import BoardroomState
from graph.nodes import director_node, sme_node, writer_node, critic_node

# Maximum critic → writer revision cycles before forcing completion
MAX_REVISIONS = 2


# ---------------------------------------------------------------------------
# Conditional edge: should we go to SME or stop for clarification?
# ---------------------------------------------------------------------------

def route_after_director(state: BoardroomState) -> str:
    """Route after the director node."""
    plan = state.get("writing_plan")
    if plan is None or plan.needs_clarification:
        return END          # Return clarification questions to caller
    return "tech_sme"


# ---------------------------------------------------------------------------
# Conditional edge: should the critic send the draft back to the writer?
# ---------------------------------------------------------------------------

def route_after_critic(state: BoardroomState) -> str:
    """Route after the critic node."""
    report = state.get("critic_report")
    revision_count = state.get("revision_count", 0)

    if report is None:
        return END

    if report.verdict == "approved":
        return END

    if revision_count >= MAX_REVISIONS:
        # Force completion even without approval — surface the best draft
        return END

    return "writer"     # Send back for revision


# ---------------------------------------------------------------------------
# Build the compiled graph
# ---------------------------------------------------------------------------

def build_boardroom_graph() -> StateGraph:
    """Construct and compile the AI Boardroom StateGraph."""

    builder = StateGraph(BoardroomState)

    # Add nodes
    builder.add_node("director", director_node)
    builder.add_node("tech_sme", sme_node)
    builder.add_node("writer", writer_node)
    builder.add_node("critic", critic_node)

    # Entry point
    builder.add_edge(START, "director")

    # Director → SME or END (clarification)
    builder.add_conditional_edges("director", route_after_director)

    # Linear flow: SME → Writer → Critic
    builder.add_edge("tech_sme", "writer")
    builder.add_edge("writer", "critic")

    # Critic → Writer (revision) or END (approved / max revisions)
    builder.add_conditional_edges("critic", route_after_critic)

    return builder.compile()


# Singleton compiled graph — import and use directly
boardroom_graph = build_boardroom_graph()
