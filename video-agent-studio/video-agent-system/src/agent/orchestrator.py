import json
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from src.agent.state import Task
from src.llm_clients.failover_client import LLMFailoverClient
from src.mcp_server.server import mcp


@dataclass
class Plan:
    """
    Plan wrapper holding the list of Task objects.
    Supports both dot notation (plan.tasks) and dictionary access (plan["tasks"]).
    """
    tasks: List[Task] = field(default_factory=list)

    def __getitem__(self, item: str) -> Any:
        if item == "tasks":
            return self.tasks
        raise KeyError(f"Plan object has no item '{item}'")


class Orchestrator:
    """
    Orchestrator agent responsible for creating execution plans for media workflows.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """Create an orchestrator backed by the production failover chain by default."""
        self.llm_client = llm_client or LLMFailoverClient()
        self.last_trace_events: List[Dict[str, Any]] = []

    # ---------------------------------------------------------
    # 1. LLM CALL FUNCTION
    # ---------------------------------------------------------
    async def call_llm(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Routes through Gemini 3.7 → 3.6 → 3.5 → OpenRouter Nemotron → Groq
        GPT-OSS when no client override is supplied.
        """
        return await self.llm_client.generate_text(prompt, model=model)

    # ---------------------------------------------------------
    # 2. CREATE PLAN FUNCTION
    # ---------------------------------------------------------
    async def get_available_mcp_tools(self) -> List[Dict[str, Any]]:
        """
        Retrieves list of registered MCP tools and their parameter schemas.
        """
        tools_info = []
        try:
            tools = await mcp.list_tools()
            for tool in tools:
                mcp_tool = tool.to_mcp_tool() if hasattr(tool, "to_mcp_tool") else None
                args_schema = (
                    (mcp_tool.inputSchema if mcp_tool else None)
                    or getattr(tool, "parameters", None)
                    or getattr(tool, "args_schema", None)
                    or getattr(tool, "parameters_schema", {})
                )
                tools_info.append({
                    "name": tool.name,
                    "description": tool.description,
                    "arguments_schema": args_schema
                })
        except Exception as e:
            print(f"Error fetching MCP tools: {e}")
        return tools_info

    async def create_plan(self, user_input: str) -> Plan:
        """
        Takes user_input, fetches all registered MCP tools, constructs a detailed prompt
        including the tools and their argument schemas, calls the LLM, and returns a Plan
        containing a list of Task items as defined in state.py.
        """
        started_at = time.time()
        self.last_trace_events = [{"event": "orchestrator_started", "timestamp": started_at}]
        # Retrieve list of available MCP tools
        tools_info = await self.get_available_mcp_tools()
        tools_json = json.dumps(tools_info, indent=2)

        detailed_prompt = f"""
You are an expert Video Production Orchestrator AI.
Your goal is to break down the user's request into a sequence of executable tasks using the available MCP tools.

AVAILABLE MCP TOOLS:
{tools_json}

USER REQUEST:
{user_input}

INSTRUCTIONS:
1. Analyze the user request and select the required tool(s) from the AVAILABLE MCP TOOLS list.
2. Formulate a list of tasks where each task specifies:
   - "id": A unique string identifier for the task (e.g. "task_1", "task_2")
   - "tool_name": The exact tool name from the available tools list
   - "description": A concise explanation of what this step does
   - "arguments": A dictionary of exact arguments to pass to the tool matching its schema
3. Output MUST be valid JSON strictly adhering to the following structure:

```json
{{
  "tasks": [
    {{
      "id": "task_1",
      "tool_name": "generate_tts",
      "description": "Generate audio speech for script",
      "arguments": {{
        "text": "Hello world",
        "output_path": "workspace/output/audio.mp3",
        "model_name": "gtts"
      }}
    }}
  ]
}}
```
Do NOT include any explanation outside the JSON block. Return ONLY the JSON object.
"""

        response_text = await self.call_llm(detailed_prompt)
        for attempt in getattr(self.llm_client, "last_attempts", []):
            self.last_trace_events.append({"event": "llm_attempt", **attempt})

        tasks_list: List[Task] = []
        try:
            clean_text = response_text.strip()
            if clean_text.startswith("```"):
                clean_text = clean_text.split("```")[1]
                if clean_text.startswith("json"):
                    clean_text = clean_text[4:]
                clean_text = clean_text.strip()

            parsed = json.loads(clean_text)
            raw_tasks = parsed.get("tasks", [])

            for idx, raw_task in enumerate(raw_tasks, start=1):
                task: Task = {
                    "id": str(raw_task.get("id", f"task_{idx}")),
                    "tool_name": str(raw_task.get("tool_name", "")),
                    "description": str(raw_task.get("description", "")),
                    "arguments": dict(raw_task.get("arguments", {}))
                }
                tasks_list.append(task)
        except Exception as e:
            print(f"Error parsing LLM plan JSON: {e}. Raw response: {response_text}")
            self.last_trace_events.append({"event": "plan_parse_failed", "error": str(e)})
            fallback_task: Task = {
                "id": "task_1",
                "tool_name": "generate_tts",
                "description": "Generate speech audio for user prompt",
                "arguments": {
                    "text": user_input,
                    "output_path": "workspace/output/speech.mp3"
                }
            }
            tasks_list.append(fallback_task)

        self.last_trace_events.append({
            "event": "plan_created",
            "task_count": len(tasks_list),
            "duration_ms": round((time.time() - started_at) * 1000),
        })

        return Plan(tasks=tasks_list)
