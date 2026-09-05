"""Opt-in real endpoint smoke test; never runs in the ordinary unit-test suite."""

import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from main import app


@pytest.mark.integration
def test_run_orchestrator_live_smoke():
    load_dotenv()
    if os.getenv("RUN_LIVE_ENDPOINT_TEST") != "1":
        pytest.skip("Set RUN_LIVE_ENDPOINT_TEST=1 to call configured external LLM providers")
    if not any(os.getenv(key) for key in ("GEMINI_API_KEY", "OPENROUTER_API_KEY", "GROQ_API_KEY")):
        pytest.fail("A provider key is required: GEMINI_API_KEY, OPENROUTER_API_KEY, or GROQ_API_KEY")

    response = TestClient(app).post("/run_orchestrator", json={
        "user_message": "Create a concise plan for a 10-second AI video.",
        "execute_tasks": False,
    })

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["tasks"], body
    assert body["status"] == "planned", body
    assert any(event["event"] == "orchestrator_started" for event in body["trace_events"]), body
