# backend/api/schemas.py
"""
Pydantic request/response schemas for the FastAPI endpoints.
"""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Auth schemas
# ---------------------------------------------------------------------------

class TokenRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------------------------------------------------------------------------
# AI Writer Room schemas
# ---------------------------------------------------------------------------

class WriterRoomRequest(BaseModel):
    """Request body for POST /ai_writer_room."""
    user_request: str = Field(
        description="The user's content creation request.",
        min_length=10,
        max_length=5000,
    )
    llm_provider: str = Field(
        default="gemini",
        description="LLM provider to use: 'gemini' or 'openrouter'.",
    )
    run_full_pipeline: bool = Field(
        default=False,
        description=(
            "If False (default), only the director agent runs and returns a WritingPlan. "
            "If True, the full LangGraph pipeline executes (director → sme → writer → critic)."
        ),
    )


class WriterRoomResponse(BaseModel):
    """Response from POST /ai_writer_room."""
    session_id: str = Field(description="Unique session identifier for WebSocket streaming.")
    status: str = Field(description="Current workflow status.")
    writing_plan: Optional[Any] = Field(
        default=None,
        description="Director's structured WritingPlan (always present).",
    )
    sme_report: Optional[Any] = Field(
        default=None,
        description="Tech SME research report (present if run_full_pipeline=True).",
    )
    writer_draft: Optional[Any] = Field(
        default=None,
        description="Writer's content draft (present if run_full_pipeline=True).",
    )
    critic_report: Optional[Any] = Field(
        default=None,
        description="Critic's review report (present if run_full_pipeline=True).",
    )
    final_output: Optional[str] = Field(
        default=None,
        description="Final approved content (present if run_full_pipeline=True and approved).",
    )
    messages: list[dict] = Field(
        default_factory=list,
        description="User-facing conversation log from the boardroom agents.",
    )
    error: Optional[str] = Field(default=None, description="Error message if something failed.")


# ---------------------------------------------------------------------------
# WebSocket message schemas
# ---------------------------------------------------------------------------

class WSMessage(BaseModel):
    """Generic WebSocket message envelope."""
    type: str = Field(description="Message type: 'status', 'agent_message', 'result', 'error'.")
    agent: Optional[str] = Field(default=None, description="Originating agent name.")
    content: Any = Field(description="Message payload.")
