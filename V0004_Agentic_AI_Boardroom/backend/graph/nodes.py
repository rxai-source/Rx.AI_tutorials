# backend/graph/nodes.py
"""
LangGraph node functions for the AI Boardroom workflow.

Each node function:
  1. Receives the current BoardroomState (shared group chat).
  2. Calls the appropriate agent's public method.
  3. Returns a PARTIAL state update containing ONLY the public output.

ISOLATION GUARANTEE:
  Node functions receive NO agent scratchpad data.
  They call agent methods which internally use scratchpads, then return
  only the final structured result. The scratchpad is cleared inside
  the agent after each completed reasoning cycle.
"""

from __future__ import annotations

import json
from langchain_core.messages import AIMessage

from graph.state import BoardroomState
from agents.director_agent import DirectorAgent
from agents.tech_sme_agent import TechSMEAgent
from agents.writer_agent import WriterAgent
from agents.critic_agent import CriticAgent
from llms.registry import get_llm


# ---------------------------------------------------------------------------
# Node: Director (Planning)
# ---------------------------------------------------------------------------

async def director_node(state: BoardroomState) -> dict:
    """
    Node 1 — Director plans the writing task.

    Input  : state["user_request"]
    Output : state["writing_plan"], state["status"], state["messages"]
    """
    llm = get_llm("gemini")
    director = DirectorAgent(llm=llm)

    plan = await director.plan(state["user_request"])

    status = "clarifying" if plan.needs_clarification else "researching"
    summary = (
        f"Director needs clarification:\n"
        + "\n".join(f"  - {q}" for q in plan.clarification_questions)
        if plan.needs_clarification
        else f"Director has created a plan for: '{plan.topic}'"
    )

    return {
        "writing_plan": plan,
        "status": status,
        "messages": [AIMessage(content=summary, name="director")],
    }


# ---------------------------------------------------------------------------
# Node: Tech SME (Research)
# ---------------------------------------------------------------------------

async def sme_node(state: BoardroomState) -> dict:
    """
    Node 2 — Tech SME conducts research.

    Input  : state["writing_plan"]
    Output : state["sme_report"], state["status"], state["messages"]
    """
    plan = state["writing_plan"]
    if plan is None:
        return {"error": "No writing plan available for SME research.", "status": "error"}

    # Find the SME task from the plan
    sme_task = next(
        (t for t in plan.tasks if t.agent == "tech_sme"),
        None,
    )
    task_description = sme_task.task_description if sme_task else plan.objective

    llm = get_llm("gemini")
    sme = TechSMEAgent(llm=llm)

    report = await sme.research(
        topic=plan.topic,
        task_description=task_description,
    )

    return {
        "sme_report": report,
        "status": "drafting",
        "messages": [
            AIMessage(
                content=f"Tech SME research complete. Domain: {report.domain}. "
                        f"{len(report.key_facts)} key facts compiled.",
                name="tech_sme",
            )
        ],
    }


# ---------------------------------------------------------------------------
# Node: Writer (Drafting)
# ---------------------------------------------------------------------------

async def writer_node(state: BoardroomState) -> dict:
    """
    Node 3 — Writer drafts the content.

    Input  : state["writing_plan"], state["sme_report"]
    Output : state["writer_draft"], state["status"], state["messages"]
    """
    plan = state["writing_plan"]
    sme_report = state["sme_report"]

    if plan is None:
        return {"error": "No writing plan for writer.", "status": "error"}

    # Serialise plan and SME report as context strings
    plan_context = (
        f"Objective: {plan.objective}\n"
        f"Outline:\n" + "\n".join(f"  {i+1}. {s}" for i, s in enumerate(plan.outline)) +
        f"\nDirector Notes: {plan.director_notes}"
    )
    sme_context = (
        json.dumps(sme_report.model_dump(), indent=2)
        if sme_report else "No SME research provided."
    )

    llm = get_llm("gemini")
    writer = WriterAgent(llm=llm)

    draft = await writer.draft(
        topic=plan.topic,
        plan_context=plan_context,
        sme_context=sme_context,
        tone=plan.tone,
        content_type=plan.content_type,
        target_audience=plan.target_audience,
        word_count_target=plan.word_count_target,
    )

    return {
        "writer_draft": draft,
        "status": "reviewing",
        "messages": [
            AIMessage(
                content=f"Writer has completed the draft: '{draft.title}' "
                        f"({draft.word_count} words).",
                name="writer",
            )
        ],
    }


# ---------------------------------------------------------------------------
# Node: Critic (Review)
# ---------------------------------------------------------------------------

async def critic_node(state: BoardroomState) -> dict:
    """
    Node 4 — Critic reviews the draft.

    Input  : state["writing_plan"], state["sme_report"], state["writer_draft"]
    Output : state["critic_report"], state["status"], state["messages"]
    """
    plan = state["writing_plan"]
    sme_report = state["sme_report"]
    draft = state["writer_draft"]

    if plan is None or draft is None:
        return {"error": "Missing plan or draft for critic review.", "status": "error"}

    plan_context = (
        f"Objective: {plan.objective}\n"
        f"Outline:\n" + "\n".join(f"  {i+1}. {s}" for i, s in enumerate(plan.outline))
    )
    sme_context = (
        json.dumps(sme_report.model_dump(), indent=2)
        if sme_report else "No SME research provided."
    )

    llm = get_llm("gemini")
    critic = CriticAgent(llm=llm)

    report = await critic.review(
        draft_content=draft.content,
        plan_context=plan_context,
        sme_context=sme_context,
        tone=plan.tone,
        target_audience=plan.target_audience,
        word_count_target=plan.word_count_target,
    )

    status = "done" if report.verdict == "approved" else "revision_required"
    revision_count = state.get("revision_count", 0) + 1

    return {
        "critic_report": report,
        "status": status,
        "revision_count": revision_count,
        "final_output": draft.content if report.verdict == "approved" else None,
        "messages": [
            AIMessage(
                content=(
                    f"Critic verdict: {report.verdict.upper()}. "
                    f"Overall score: {report.overall_score}/10. "
                    + (
                        f"Issues: {'; '.join(report.issues[:2])}"
                        if report.issues else "No blocking issues."
                    )
                ),
                name="critic",
            )
        ],
    }
