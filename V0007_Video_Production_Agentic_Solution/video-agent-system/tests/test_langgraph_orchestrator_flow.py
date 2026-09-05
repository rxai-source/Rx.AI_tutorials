"""Integration test for graph -> nodes -> orchestrator_node -> orchestrator."""

import asyncio
from unittest.mock import AsyncMock, patch

from src.agent.executor import Executor
from src.agent.graph import build_graph
from src.agent.orchestrator import Orchestrator
from src.llm_clients.failover_client import LLMFailoverClient


USER_MESSAGE = "Create an engaging 30-second narration about agentic video generation."
LLM_PLAN = (
    '{"tasks": [{"id": "task_1", "tool_name": "generate_tts", '
    '"description": "Generate the narration", '
    '"arguments": {"text": "Agentic video generation is here."}}]}'
)


def test_langgraph_queues_and_executes_each_planned_task_through_state():
    """Run graph -> nodes -> orchestrator -> state queue -> executor -> final state."""
    executor = Executor()
    executor.execute_task = AsyncMock(return_value={"task_id": "task_1", "status": "completed"})
    generate_text = AsyncMock(return_value=LLM_PLAN)

    with (
        patch.object(LLMFailoverClient, "generate_text", generate_text),
        patch.object(Orchestrator, "get_available_mcp_tools", AsyncMock(return_value=[])),
    ):
        final_state = asyncio.run(build_graph(executor=executor).ainvoke({"user_message": USER_MESSAGE}))

    assert USER_MESSAGE in generate_text.await_args.args[0]
    assert final_state["user_message"] == USER_MESSAGE
    assert final_state["tasks"] == [{
        "id": "task_1",
        "tool_name": "generate_tts",
        "description": "Generate the narration",
        "arguments": {"text": "Agentic video generation is here."},
    }]
    assert final_state["task_queue"] == []
    assert final_state["completed_task_ids"] == ["task_1"]
    assert final_state["results"] == [{"task_id": "task_1", "status": "completed"}]
    assert final_state["execution_events"][-1] == {
        "event": "task_finished", "task_id": "task_1", "status": "completed"
    }
    assert final_state["status"] == "completed"


def test_langgraph_drains_a_multi_task_queue_in_order():
    """Each executor-node pass removes one item and appends one state result."""
    two_task_plan = (
        '{"tasks": ['
        '{"id": "task_1", "tool_name": "generate_tts", "description": "First", "arguments": {}}, '
        '{"id": "task_2", "tool_name": "generate_tts", "description": "Second", "arguments": {}}'
        ']}'
    )
    executor = Executor()
    executor.execute_task = AsyncMock(side_effect=[
        {"task_id": "task_1", "status": "completed"},
        {"task_id": "task_2", "status": "completed"},
    ])

    with (
        patch.object(LLMFailoverClient, "generate_text", AsyncMock(return_value=two_task_plan)),
        patch.object(Orchestrator, "get_available_mcp_tools", AsyncMock(return_value=[])),
    ):
        final_state = asyncio.run(build_graph(executor=executor).ainvoke({"user_message": USER_MESSAGE}))

    assert [call.args[0]["id"] for call in executor.execute_task.await_args_list] == ["task_1", "task_2"]
    assert final_state["task_queue"] == []
    assert final_state["completed_task_ids"] == ["task_1", "task_2"]
    assert [result["task_id"] for result in final_state["results"]] == ["task_1", "task_2"]
    assert [event["task_id"] for event in final_state["execution_events"][1:]] == ["task_1", "task_2"]


def test_langgraph_executes_real_media_tools_workflow():
    """Execute a realistic multi-step pipeline (image format -> text overlay -> QC) with real executor tools."""
    import shutil
    import uuid
    from PIL import Image
    from src.config import TEMP_DIR

    test_dir = TEMP_DIR / f"langgraph_exec_test_{uuid.uuid4().hex}"
    test_dir.mkdir(parents=True, exist_ok=True)
    try:
        raw_img = test_dir / "raw.png"
        Image.new("RGB", (200, 200), "purple").save(raw_img)

        plan_json = f"""{{
            "tasks": [
                {{
                    "id": "task_1",
                    "tool_name": "format_image_aspect_ratio",
                    "description": "Letterbox input image to 16:9 canvas",
                    "arguments": {{
                        "image_path": "{raw_img.as_posix()}",
                        "output_path": "{(test_dir / 'formatted.png').as_posix()}",
                        "aspect_ratio": "16:9"
                    }}
                }},
                {{
                    "id": "task_2",
                    "tool_name": "add_text_overlay",
                    "description": "Add banner text",
                    "arguments": {{
                        "image_path": "{(test_dir / 'formatted.png').as_posix()}",
                        "output_path": "{(test_dir / 'titled.png').as_posix()}",
                        "text": "Production Video Pipeline",
                        "position": "center"
                    }}
                }}
            ]
        }}"""

        executor = Executor()
        with (
            patch.object(LLMFailoverClient, "generate_text", AsyncMock(return_value=plan_json)),
            patch.object(Orchestrator, "get_available_mcp_tools", AsyncMock(return_value=[])),
        ):
            final_state = asyncio.run(build_graph(executor=executor).ainvoke({"user_message": "Make a video title card."}))

        assert final_state["status"] == "completed"
        assert len(final_state["results"]) == 2
        assert all(r["status"] == "completed" for r in final_state["results"])
        assert (test_dir / "titled.png").is_file()
        assert (test_dir / "titled.png").stat().st_size > 0
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)

