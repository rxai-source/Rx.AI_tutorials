from typing import Any, TypedDict, List, Dict, Optional

class Task(TypedDict):
    id: str 
    tool_name: str
    description: str
    arguments: Dict[str, Any]

class AgentState(TypedDict, total=False):
    """
    Defines the Agents Communication bus
    """
    user_message: str
    tasks: List[Task]
    results: List[Dict[str, Any]]
    error: Optional[str]




