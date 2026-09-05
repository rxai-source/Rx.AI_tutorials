"""Minimal developer console for the real /run_orchestrator endpoint."""

import os

import httpx
import streamlit as st

from src.core.artifacts import SUPPORTED_ARTIFACT_EXTENSIONS, save_artifact


API_URL = os.getenv("ORCHESTRATOR_API_URL", "http://127.0.0.1:8000").rstrip("/")


def _trace_label(event: dict) -> str:
    event_name = event.get("event", "trace")
    status = event.get("status")
    subject = event.get("tool_name") or event.get("model") or event.get("task_id")
    return " · ".join(str(part) for part in (event_name, subject, status) if part)


def main() -> None:
    st.set_page_config(page_title="Video Agent Developer Console", layout="wide")
    st.title("Video Agent Developer Console")
    st.caption(f"Using the real orchestrator endpoint: `{API_URL}/run_orchestrator`")

    if st.button("Start another request"):
        for key in ("last_response", "attached_artifacts", "instruction"):
            st.session_state.pop(key, None)
        st.rerun()

    with st.form("orchestrator_request"):
        instruction = st.text_area(
            "Instruction",
            placeholder="Describe the video you want to produce",
            key="instruction",
        )
        uploads = st.file_uploader(
            "Attach artifacts (optional)",
            type=[suffix.removeprefix(".") for suffix in sorted(SUPPORTED_ARTIFACT_EXTENSIONS)],
            accept_multiple_files=True,
        )
        execute_tasks = st.checkbox("Execute planned tools", value=True)
        submitted = st.form_submit_button("Run orchestrator", type="primary")

    if submitted:
        if not instruction.strip():
            st.error("Enter an instruction before running the orchestrator.")
            return
        try:
            artifact_references = [
                save_artifact(upload.name, upload.getvalue(), upload.type)
                for upload in uploads or []
            ]
            st.session_state.attached_artifacts = artifact_references
            response = httpx.post(
                f"{API_URL}/run_orchestrator",
                json={
                    "user_message": instruction,
                    "artifacts": artifact_references,
                    "execute_tasks": execute_tasks,
                },
                timeout=120.0,
            )
            response.raise_for_status()
            st.session_state.last_response = response.json()
        except (httpx.HTTPError, OSError, ValueError) as exc:
            st.error(f"Request failed: {exc}")

    if st.session_state.get("attached_artifacts"):
        st.subheader("Attached artifacts")
        for artifact in st.session_state.attached_artifacts:
            st.code(f"{artifact['filename']}  →  {artifact['path']}")

    result = st.session_state.get("last_response")
    if not result:
        return
    with st.chat_message("user"):
        st.write(result.get("user_message", ""))
    st.subheader("Final response")
    st.json({
        "status": result.get("status"),
        "tasks": result.get("tasks", []),
        "results": result.get("results", []),
    })

    st.subheader("Actual execution trace")
    traces = result.get("trace_events", [])
    if not traces:
        st.info("The backend did not expose trace events for this run.")
    for event in traces:
        with st.expander(_trace_label(event), expanded=False):
            st.json(event)


if __name__ == "__main__":
    main()
