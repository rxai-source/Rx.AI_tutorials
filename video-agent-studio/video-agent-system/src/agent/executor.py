"""Asynchronous, queue-based executor for planned media tasks."""

import asyncio
import inspect
import time
from collections.abc import Callable
from typing import Any, Dict, List

from src.agent.state import Task
from src.mcp_server.server import TOOL_REGISTRY


class Executor:
    """Executes one queued task at a time without blocking the event loop."""

    def __init__(self, tool_registry: Dict[str, Callable[..., Any]] | None = None):
        self.tool_registry = dict(tool_registry) if tool_registry is not None else dict(TOOL_REGISTRY)


    async def execute(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        """Execute independent tasks concurrently when the caller wants a batch."""
        async with asyncio.TaskGroup() as group:
            running = [group.create_task(self.execute_task(task)) for task in tasks]
        return [task.result() for task in running]

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        """Run one task and return a serializable state update result."""
        started_at = time.time()
        tool = self.tool_registry.get(task["tool_name"])
        if tool is None:
            return {
                "task_id": task["id"],
                "tool_name": task["tool_name"],
                "status": "failed",
                "error": f"Unsupported tool: {task['tool_name']}",
                "started_at": started_at,
                "completed_at": time.time(),
            }

        try:
            if inspect.iscoroutinefunction(tool):
                output = await tool(**task["arguments"])
            else:
                output = await asyncio.to_thread(tool, **task["arguments"])
            return {
                "task_id": task["id"],
                "tool_name": task["tool_name"],
                "status": "completed",
                "output": output,
                "started_at": started_at,
                "completed_at": time.time(),
            }
        except Exception as exc:
            return {
                "task_id": task["id"],
                "tool_name": task["tool_name"],
                "status": "failed",
                "error": str(exc),
                "started_at": started_at,
                "completed_at": time.time(),
            }
