"""Unit tests for the shared artifact staging and async executor batch API."""

import asyncio
import time

from src.agent.executor import Executor
from src.core import artifacts


def test_save_and_validate_artifact_reference(tmp_path, monkeypatch):
    monkeypatch.setattr(artifacts, "INPUT_DIR", tmp_path)
    saved = artifacts.save_artifact("outline.txt", b"video outline", "text/plain")

    assert saved["filename"] == "outline.txt"
    assert saved["path"].startswith(str(tmp_path))
    assert artifacts.validate_artifact_reference(saved) == saved


def test_executor_batch_api_uses_concurrent_tasks():
    async def slow_tool(delay: float) -> dict:
        await asyncio.sleep(delay)
        return {"delay": delay}

    executor = Executor(tool_registry={"slow_tool": slow_tool})
    tasks = [
        {"id": "task_1", "tool_name": "slow_tool", "description": "first", "arguments": {"delay": 0.05}},
        {"id": "task_2", "tool_name": "slow_tool", "description": "second", "arguments": {"delay": 0.05}},
    ]
    started_at = time.perf_counter()
    results = asyncio.run(executor.execute(tasks))

    assert time.perf_counter() - started_at < 0.09
    assert [result["task_id"] for result in results] == ["task_1", "task_2"]
    assert all(result["status"] == "completed" for result in results)
