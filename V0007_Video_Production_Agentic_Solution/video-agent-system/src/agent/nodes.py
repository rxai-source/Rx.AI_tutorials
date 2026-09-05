from src.agent.state import AgentState
from src.agent.orchestrator import Orchestrator
from src.agent.executor import Executor

class AgentNodes:
    def __init__(self, orchestrator: Orchestrator, executor: Executor):
        self.orchestrator = orchestrator
        self.executor = executor

    async def orchestrator_node(self, state: AgentState):
        """Create the plan and initialize the state-backed execution queue."""
        artifacts = list(state.get("artifacts", []))
        artifact_context = "\n".join(f"- {item['filename']}: {item['path']}" for item in artifacts)
        user_input = state.get("user_message", "missing user_message")
        if artifact_context:
            user_input = f"{user_input}\n\nATTACHED ARTIFACTS:\n{artifact_context}"
        plan = await self.orchestrator.create_plan(user_input=user_input)
        trace_events = [
            {"event": "request_received", "artifact_count": len(artifacts)},
            *self.orchestrator.last_trace_events,
        ]
        return {
            "tasks": plan.tasks,
            "task_queue": list(plan.tasks),
            "completed_task_ids": [],
            "results": [],
            "execution_events": [{"event": "plan_created", "task_count": len(plan.tasks)}],
            "trace_events": trace_events,
            "status": "queued" if state.get("execute_tasks", True) and plan.tasks else "planned",
            "error": None,
        }

    async def executor_node(self, state: AgentState):
        """Dequeue and execute one task, then write its progress back to state."""
        task_queue = list(state.get("task_queue", []))
        if not task_queue:
            return {"status": "completed"}

        task = task_queue.pop(0)
        result = await self.executor.execute_task(task)
        results = [*state.get("results", []), result]
        completed_task_ids = [*state.get("completed_task_ids", []), task["id"]]
        events = [
            *state.get("execution_events", []),
            {"event": "task_finished", "task_id": task["id"], "status": result["status"]},
        ]
        trace_events = [
            *state.get("trace_events", []),
            {"event": "tool_finished", "task_id": task["id"], "tool_name": task["tool_name"], "status": result["status"]},
        ]
        return {
            "task_queue": task_queue,
            "results": results,
            "completed_task_ids": completed_task_ids,
            "execution_events": events,
            "trace_events": trace_events,
            "status": "executing" if task_queue else "completed",
        }
