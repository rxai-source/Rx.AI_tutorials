# backend/api/routes/writer_room.py
"""
AI Writer Room routes.

POST /ai_writer_room
  — Calls the DirectorAgent (always).
  — Optionally runs the full LangGraph pipeline.
  — Returns structured JSON.

WebSocket /ws/boardroom/{session_id}
  — Authenticated via JWT in the Sec-WebSocket-Protocol header.
  — Streams agent updates in real time.
"""

from __future__ import annotations

import json
import uuid
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from langchain_core.messages import AIMessage

from api.schemas import WriterRoomRequest, WriterRoomResponse, WSMessage
from core.security import decode_access_token, validate_ws_token
from agents.director_agent import DirectorAgent
from graph.boardroom_graph import boardroom_graph
from graph.state import BoardroomState
from llms.registry import get_llm

router = APIRouter(tags=["AI Writer Room"])
bearer_scheme = HTTPBearer()


# ---------------------------------------------------------------------------
# Dependency: Validate HTTP Bearer JWT
# ---------------------------------------------------------------------------

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """Validate the Bearer JWT and return the decoded payload."""
    return decode_access_token(credentials.credentials)


# ---------------------------------------------------------------------------
# POST /ai_writer_room
# ---------------------------------------------------------------------------

@router.post(
    "/ai_writer_room",
    response_model=WriterRoomResponse,
    summary="Submit a writing request to the AI Boardroom",
    description=(
        "The DirectorAgent always runs first: it understands the request, "
        "asks clarifying questions if needed, and produces a structured WritingPlan. "
        "If `run_full_pipeline=True`, the full LangGraph graph executes "
        "(Director → Tech SME → Writer → Critic)."
    ),
)
async def ai_writer_room(
    payload: WriterRoomRequest,
    current_user: dict = Depends(get_current_user),
) -> WriterRoomResponse:
    """Main AI Writer Room endpoint."""

    session_id = str(uuid.uuid4())

    try:
        if not payload.run_full_pipeline:
            # ----------------------------------------------------------------
            # Director-only mode (default)
            # ----------------------------------------------------------------
            llm = get_llm(payload.llm_provider)
            director = DirectorAgent(llm=llm)
            plan = await director.plan(payload.user_request)

            status_str = "clarifying" if plan.needs_clarification else "planned"
            return WriterRoomResponse(
                session_id=session_id,
                status=status_str,
                writing_plan=plan.model_dump(),
                messages=[
                    {
                        "agent": "director",
                        "content": (
                            "Clarification needed:\n"
                            + "\n".join(f"• {q}" for q in plan.clarification_questions)
                        )
                        if plan.needs_clarification
                        else f"Plan ready for: {plan.topic}",
                    }
                ],
            )

        else:
            # ----------------------------------------------------------------
            # Full LangGraph pipeline mode
            # ----------------------------------------------------------------
            initial_state: BoardroomState = {
                "user_request": payload.user_request,
                "writing_plan": None,
                "sme_report": None,
                "writer_draft": None,
                "critic_report": None,
                "final_output": None,
                "messages": [],
                "status": "starting",
                "error": None,
                "revision_count": 0,
            }

            final_state: BoardroomState = await boardroom_graph.ainvoke(initial_state)

            # Serialise messages for the response
            messages_out = []
            for msg in final_state.get("messages", []):
                if isinstance(msg, AIMessage):
                    messages_out.append({
                        "agent": getattr(msg, "name", "unknown"),
                        "content": msg.content,
                    })

            return WriterRoomResponse(
                session_id=session_id,
                status=final_state.get("status", "done"),
                writing_plan=final_state["writing_plan"].model_dump()
                if final_state.get("writing_plan") else None,
                sme_report=final_state["sme_report"].model_dump()
                if final_state.get("sme_report") else None,
                writer_draft=final_state["writer_draft"].model_dump()
                if final_state.get("writer_draft") else None,
                critic_report=final_state["critic_report"].model_dump()
                if final_state.get("critic_report") else None,
                final_output=final_state.get("final_output"),
                messages=messages_out,
                error=final_state.get("error"),
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Boardroom pipeline error: {str(e)}",
        )


# ---------------------------------------------------------------------------
# WebSocket /ws/boardroom/{session_id}
# ---------------------------------------------------------------------------

@router.websocket("/ws/boardroom/{session_id}")
async def boardroom_websocket(
    websocket: WebSocket,
    session_id: str,
) -> None:
    """
    Authenticated WebSocket endpoint for streaming boardroom updates.

    Authentication
    --------------
    JWT must be passed in the Sec-WebSocket-Protocol header:
        Sec-WebSocket-Protocol: bearer, <jwt_token>

    The server accepts the connection only if the JWT is valid,
    then echoes "bearer" as the accepted sub-protocol.

    Message flow
    ------------
    Client → Server : { "user_request": "...", "run_full_pipeline": bool }
    Server → Client : WSMessage envelopes for each agent step
    """
    # --- Validate JWT from Sec-WebSocket-Protocol header ---
    protocols: list[str] = websocket.headers.get("sec-websocket-protocol", "").split(",")
    protocols = [p.strip() for p in protocols if p.strip()]

    try:
        user_payload = validate_ws_token(protocols)
    except HTTPException:
        await websocket.close(code=4001, reason="Unauthorized: invalid or missing JWT")
        return

    # Accept connection, echo "bearer" as the selected sub-protocol
    await websocket.accept(subprotocol="bearer")

    try:
        # Receive the initial request from the client
        raw = await websocket.receive_text()
        request_data = json.loads(raw)
        user_request = request_data.get("user_request", "")
        run_full_pipeline = request_data.get("run_full_pipeline", False)

        if not user_request:
            await websocket.send_text(
                WSMessage(
                    type="error",
                    content="user_request is required",
                ).model_dump_json()
            )
            return

        # --- Stream status updates ---
        async def send_status(msg: str, agent: str | None = None) -> None:
            await websocket.send_text(
                WSMessage(type="status", agent=agent, content=msg).model_dump_json()
            )

        await send_status("Boardroom session started", "system")

        if not run_full_pipeline:
            # Director-only streaming
            await send_status("Director is analysing your request...", "director")
            llm = get_llm("gemini")
            director = DirectorAgent(llm=llm)
            plan = await director.plan(user_request)

            await websocket.send_text(
                WSMessage(
                    type="result",
                    agent="director",
                    content=plan.model_dump(),
                ).model_dump_json()
            )

        else:
            # Full pipeline streaming via LangGraph stream
            initial_state: BoardroomState = {
                "user_request": user_request,
                "writing_plan": None,
                "sme_report": None,
                "writer_draft": None,
                "critic_report": None,
                "final_output": None,
                "messages": [],
                "status": "starting",
                "error": None,
                "revision_count": 0,
            }

            async for chunk in boardroom_graph.astream(
                initial_state, stream_mode="updates"
            ):
                for node_name, node_output in chunk.items():
                    # Stream each agent's public output to the client
                    # NOTE: scratchpads are never in node_output
                    await websocket.send_text(
                        WSMessage(
                            type="agent_message",
                            agent=node_name,
                            content=_serialise_node_output(node_output),
                        ).model_dump_json()
                    )

            await send_status("Boardroom session complete", "system")

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(
                WSMessage(type="error", content=str(e)).model_dump_json()
            )
        except Exception:
            pass


def _serialise_node_output(output: dict) -> dict:
    """Convert LangGraph node output to a JSON-serialisable dict."""
    result = {}
    for key, value in output.items():
        if key == "messages":
            result[key] = [
                {"agent": getattr(m, "name", "unknown"), "content": m.content}
                for m in (value or [])
                if isinstance(m, AIMessage)
            ]
        elif hasattr(value, "model_dump"):
            result[key] = value.model_dump()
        else:
            result[key] = value
    return result
