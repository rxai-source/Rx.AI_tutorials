# backend/agents/__init__.py
"""
AI Boardroom agents package.

Agents:
  - DirectorAgent  : orchestrator — understands requirements, plans, assigns tasks
  - TechSMEAgent   : subject matter expert — research, facts, citations
  - WriterAgent    : content drafter — produces the actual writing
  - CriticAgent    : quality gatekeeper — reviews and approves/rejects drafts

Isolation rule (enforced across all agents):
  Each agent maintains a private _scratchpad for intermediate reasoning.
  This scratchpad is NEVER forwarded to the shared group chat or the user.
  Only the final structured output of each agent enters the shared state.
"""

from agents.base_agent import BaseAgent
from agents.director_agent import DirectorAgent, WritingPlan, AgentTask
from agents.tech_sme_agent import TechSMEAgent, SMEReport
from agents.writer_agent import WriterAgent, WriterDraft
from agents.critic_agent import CriticAgent, CriticReport

__all__ = [
    "BaseAgent",
    "DirectorAgent",
    "WritingPlan",
    "AgentTask",
    "TechSMEAgent",
    "SMEReport",
    "WriterAgent",
    "WriterDraft",
    "CriticAgent",
    "CriticReport",
]
