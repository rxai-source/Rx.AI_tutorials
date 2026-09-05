from typing import Any, Dict, List, Optional, TypedDict

class Task(TypedDict):
    id: str 
    tool_name: str
    description: str
    arguments: Dict[str, Any]


class Artifact(TypedDict):
    id: str
    filename: str
    path: str
    media_type: str

class AgentState(TypedDict, total=False):
    """
    Defines the Agents Communication bus
    """
    user_message: str
    artifacts: List[Artifact]
    execute_tasks: bool
    tasks: List[Task]
    task_queue: List[Task]
    completed_task_ids: List[str]
    results: List[Dict[str, Any]]
    execution_events: List[Dict[str, Any]]
    trace_events: List[Dict[str, Any]]
    status: str
    error: Optional[str]


