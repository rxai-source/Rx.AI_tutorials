import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI
import uvicorn

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.core.audio_engine import generate_tts
from src.mcp_server.server import mcp

# Initialize FastAPI application
app = FastAPI(
    title="Video Production Agent System API",
    description="REST API for Agent workflow orchestration and FastMCP tool health monitoring.",
    version="0.1.0",
)


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


@app.post("/run-video-gen-orchestrator",response_model=VidOrchResponse)
async def run_video_gen_orchestrator():
    #Take the user's message and send it to orchestrator


    #Take the result from the orchestrator & then run the agents based on that.


    #Take the final results and send to the consolidation agent

    #Send the final response to the user




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

    from src.agent.graph import compile_graph

    graph_app = compile_graph()
    initial_state = {
        "prompt": args.prompt,
        "input_dir": args.input_dir,
        "output_dir": args.output_dir,
        "status": "initialized",
    }

    result = graph_app.invoke(initial_state)
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
            text=args.text,
            output_path=args.output,
            model_name=args.model,
            voice=args.voice,
            return_bytes=True,
        )
        print(f"  Status      : {res['status']}")
        print(f"  Output Path : {res['output_path']}")
        print(f"  File Size   : {res['file_size_bytes']} bytes")
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
        "tool_name", choices=["tts"], help="Name of the core tool to execute"
    )
    tool_parser.add_argument("--text", type=str, help="Text input for TTS")
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
