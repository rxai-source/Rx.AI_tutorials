"""HTTP contract test for POST /run_orchestrator."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from main import app


def test_run_orchestrator_uses_the_compiled_langgraph():
    graph = type("FakeGraph", (), {})()
    graph.ainvoke = AsyncMock(return_value={
        "user_message": "Make a test video",
        "tasks": [{"id": "task_1", "tool_name": "generate_tts", "description": "Narrate", "arguments": {}}],
        "task_queue": [],
        "completed_task_ids": ["task_1"],
        "results": [{"task_id": "task_1", "status": "completed"}],
        "execution_events": [{"event": "task_finished", "task_id": "task_1", "status": "completed"}],
        "status": "completed",
    })

    with patch("src.agent.graph.build_graph", return_value=graph):
        response = TestClient(app).post("/run_orchestrator", json={"user_message": "Make a test video"})

    assert response.status_code == 200
    assert response.json()["tasks"][0]["tool_name"] == "generate_tts"
    assert response.json()["task_queue"] == []
    assert response.json()["completed_task_ids"] == ["task_1"]
    assert response.json()["results"][0]["status"] == "completed"
    assert response.json()["final_state"]["status"] == "completed"
    graph.ainvoke.assert_awaited_once_with({
        "user_message": "Make a test video",
        "artifacts": [],
        "execute_tasks": True,
    })


def test_run_orchestrator_rejects_an_empty_message():
    response = TestClient(app).post("/run_orchestrator", json={"user_message": ""})
    assert response.status_code == 422


def test_mcp_healthcheck_endpoint_returns_all_registered_tools():
    response = TestClient(app).get("/mcp_healthcheck")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["tools_count"] >= 11
    tool_names = {tool["name"] for tool in data["tools"]}
    assert {
        "get_media_info",
        "generate_tts",
        "merge_audio_tracks",
        "extract_audio",
        "format_image_aspect_ratio",
        "add_text_overlay",
        "create_video_from_image_audio",
        "concatenate_video_clips",
        "replace_video_audio",
        "generate_and_burn_subtitles",
        "validate_final_video",
    } <= tool_names

