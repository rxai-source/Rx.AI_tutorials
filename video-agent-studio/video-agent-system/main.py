import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import BASE_DIR, WORKSPACE_DIR
from src.core.audio_engine import generate_tts
from src.core.artifacts import validate_artifact_reference, save_artifact
from src.mcp_server.server import mcp

# Initialize FastAPI application
app = FastAPI(
    title="Video Production Agent System API",
    description="REST API for Agent workflow orchestration and FastMCP tool health monitoring.",
    version="0.1.0",
)

STATIC_DIR = BASE_DIR / "src" / "static"
if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

if WORKSPACE_DIR.is_dir():
    app.mount("/workspace", StaticFiles(directory=str(WORKSPACE_DIR)), name="workspace")


@app.get("/", include_in_schema=False)
@app.get("/ui", include_in_schema=False)
async def serve_ui():
    """Serve the modern web dashboard interface."""
    index_path = STATIC_DIR / "index.html"
    if index_path.is_file():
        return FileResponse(str(index_path))
    return {"message": "Video Agent System API is running. Visit /docs for Swagger UI."}


@app.post("/upload_artifact")
async def upload_artifact(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Upload and stage an asset (script, image, audio, video) in the workspace."""
    try:
        content = await file.read()
        saved = save_artifact(file.filename, content, file.content_type)
        return saved
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")



class OrchestratorRequest(BaseModel):
    """Postman request body for a video-production planning run."""

    user_message: str = Field(
        min_length=1,
        examples=["Create a 30-second explainer video about agentic AI."],
    )
    artifacts: list[Dict[str, Any]] = Field(default_factory=list)
    execute_tasks: bool = True


class OrchestratorResponse(BaseModel):
    user_message: str
    tasks: list[Dict[str, Any]]
    task_queue: list[Dict[str, Any]]
    completed_task_ids: list[str]
    results: list[Dict[str, Any]]
    execution_events: list[Dict[str, Any]]
    trace_events: list[Dict[str, Any]]
    status: str
    final_state: Dict[str, Any]


@app.get("/mcp_healthcheck")
async def mcp_healthcheck() -> Dict[str, Any]:
    """
    GET endpoint that connects to the FastMCP media_tools server,
    retrieves all registered tools and metadata, and returns server health status.
    """
    try:
        tools_list = await mcp.list_tools()
        tools_metadata = []

        for t in tools_list:
            mcp_tool = t.to_mcp_tool() if hasattr(t, "to_mcp_tool") else None
            tools_metadata.append(
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": mcp_tool.inputSchema
                    if mcp_tool
                    else getattr(t, "parameters", {}),
                }
            )

        return {
            "status": "healthy",
            "server_name": mcp.name,
            "tools_count": len(tools_metadata),
            "tools": tools_metadata,
            "timestamp": int(time.time()),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "server_name": getattr(mcp, "name", "media_tools"),
            "error": str(e),
            "timestamp": int(time.time()),
        }


@app.post("/run_orchestrator", response_model=OrchestratorResponse)
async def run_orchestrator(request: OrchestratorRequest) -> OrchestratorResponse:
    """Run the LangGraph workflow for a supplied video-production request."""
    from src.agent.graph import build_graph

    try:
        artifacts = [validate_artifact_reference(item) for item in request.artifacts]
        final_state = await build_graph().ainvoke({
            "user_message": request.user_message,
            "artifacts": artifacts,
            "execute_tasks": request.execute_tasks,
        })
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Orchestrator unavailable: {exc}") from exc

    return OrchestratorResponse(
        user_message=final_state["user_message"],
        tasks=final_state.get("tasks", []),
        task_queue=final_state.get("task_queue", []),
        completed_task_ids=final_state.get("completed_task_ids", []),
        results=final_state.get("results", []),
        execution_events=final_state.get("execution_events", []),
        trace_events=final_state.get("trace_events", []),
        status=final_state.get("status", "completed"),
        final_state=final_state,
    )




def run_mcp_healthcheck_cli():
    """Synchronous wrapper to execute mcp_healthcheck for CLI invocation."""
    result = asyncio.run(mcp_healthcheck())
    print(json.dumps(result, indent=2))


def run_agent(args):
    """Entry point for executing the LangGraph multi-agent workflow."""
    print("=" * 60)
    print("  Video Production Agent System")
    print("=" * 60)
    print(f"Prompt        : {args.prompt}")
    print(f"Input Folder  : {args.input_dir or 'workspace/input'}")
    print(f"Output Folder : {args.output_dir or 'workspace/output'}")
    print("\n[INFO] Initializing LangGraph state machine...")

    from src.agent.graph import build_graph

    graph_app = build_graph()
    initial_state = {
        "user_message": args.prompt,
        "artifacts": [],
        "execute_tasks": True,
        "status": "initialized",
    }

    result = asyncio.run(graph_app.ainvoke(initial_state))
    print("\n[SUCCESS] Agent workflow completed.")
    print(f"Final State: {result}")


def run_mcp_server(args):
    """Entry point for starting the FastMCP tool server."""
    print(f"[INFO] Starting FastMCP server 'media_tools' (transport: {args.transport})...")
    mcp.run(transport=args.transport)


def run_api_server(args):
    """Entry point for starting the FastAPI REST server."""
    print(f"[INFO] Starting FastAPI REST server on http://{args.host}:{args.port}...")
    uvicorn.run("main:app", host=args.host, port=args.port, reload=args.reload)


def run_tool(args):
    """Entry point for testing or invoking individual core tools directly."""
    if args.tool_name == "tts":
        print(f"[TOOL] Executing generate_tts(text='{args.text}', model='{args.model}')...")
        res = generate_tts(
            text=args.text or "Testing TTS synthesis.",
            output_path=args.output,
            model_name=args.model,
            voice=args.voice,
            return_bytes=True,
        )
        print(f"  Status      : {res['status']}")
        print(f"  Output Path : {res['output_path']}")
        print(f"  File Size   : {res['file_size_bytes']} bytes")
    elif args.tool_name == "info":
        from src.core.media_info import get_media_info
        print(f"[TOOL] Executing get_media_info('{args.media_path}')...")
        info = get_media_info(args.media_path)
        print(json.dumps(info, indent=2))
    elif args.tool_name == "qc":
        from src.core.video_engine import validate_final_video
        print(f"[TOOL] Executing validate_final_video('{args.media_path}')...")
        qc = validate_final_video(args.media_path)
        print(json.dumps(qc, indent=2))
    else:
        print(f"[ERROR] Unknown tool name: {args.tool_name}")


def main():
    parser = argparse.ArgumentParser(
        description="Video Agent System - Main Application Entrypoint",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # 1. Agent Subcommand (Runs LangGraph Workflow)
    agent_parser = subparsers.add_parser(
        "agent", help="Run the LangGraph video production agent workflow"
    )
    agent_parser.add_argument(
        "--prompt", "-p", type=str, required=True, help="Prompt / topic for video creation"
    )
    agent_parser.add_argument(
        "--input-dir", type=str, default=None, help="Custom input directory"
    )
    agent_parser.add_argument(
        "--output-dir", type=str, default=None, help="Custom output directory"
    )
    agent_parser.set_defaults(func=run_agent)

    # 2. MCP Server Subcommand (Runs FastMCP Tool Server)
    mcp_parser = subparsers.add_parser(
        "mcp", help="Run the FastMCP 'media_tools' server for agent integration"
    )
    mcp_parser.add_argument(
        "--transport",
        type=str,
        default="stdio",
        choices=["stdio", "sse"],
        help="MCP transport mode (stdio or sse)",
    )
    mcp_parser.set_defaults(func=run_mcp_server)

    # 3. API Server Subcommand (Runs FastAPI Server with /mcp_healthcheck)
    api_parser = subparsers.add_parser(
        "api", help="Start the FastAPI REST API server (includes GET /mcp_healthcheck)"
    )
    api_parser.add_argument("--host", type=str, default="127.0.0.1", help="Host IP address")
    api_parser.add_argument("--port", type=int, default=8000, help="Port number")
    api_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    api_parser.set_defaults(func=run_api_server)

    # 4. MCP Healthcheck CLI Subcommand
    health_parser = subparsers.add_parser(
        "healthcheck", help="Run MCP server healthcheck and output tool metadata JSON"
    )
    health_parser.set_defaults(func=lambda args: run_mcp_healthcheck_cli())

    # 5. Tool Direct Invocation Subcommand
    tool_parser = subparsers.add_parser(
        "tool", help="Directly invoke individual core media engine tools"
    )
    tool_parser.add_argument(
        "tool_name", choices=["tts", "info", "qc"], help="Name of the core tool to execute"
    )
    tool_parser.add_argument("--text", type=str, help="Text input for TTS")
    tool_parser.add_argument("--media-path", type=str, default=None, help="Media path for info or qc")
    tool_parser.add_argument("--output", type=str, help="Output file path")
    tool_parser.add_argument("--model", type=str, default="gtts", help="TTS model name")
    tool_parser.add_argument("--voice", type=str, default="en", help="Voice/language code")
    tool_parser.set_defaults(func=run_tool)


    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
