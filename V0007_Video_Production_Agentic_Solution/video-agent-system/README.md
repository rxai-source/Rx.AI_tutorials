# Video Agent System — Production Agentic Video Generation

An agentic video production solution powered by LangGraph state machines, FastMCP tools, and python media engines.

```text
┌──────────────────────────────────────────────────────────┐
│                   LangGraph Orchestrator                 │
│              (Plan · Execute · Validate · Retry)         │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│               FastMCP Server (media_tools)               │
│        Atomic, Sandbox-Safe Tool Exposure Layer          │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│                  Core Media Engines                      │
│     FFmpeg · Pillow · gTTS / edge-tts · Whisper ASR      │
│  (audio_engine · video_engine · image_engine · subtitle) │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│                   Workspace Sandbox                      │
│     workspace/input/ · workspace/temp/ · workspace/output│
└──────────────────────────────────────────────────────────┘
```

---

## Production Pipeline Flow

The LangGraph orchestrator drives the stateful media creation workflow:

```text
Plan
  ↓
Inspect Media (get_media_info)
  ↓
Process Audio (generate_tts / merge_audio_tracks / adjust_audio_volume)
  ↓
Format Visuals (format_image_aspect_ratio / add_text_overlay)
  ↓
Render Video Clips (create_video_from_image_audio / concatenate_video_clips)
  ↓
Subtitles & Mix (generate_and_burn_subtitles / replace_video_audio)
  ↓
Validate Render (validate_final_video QC)
  ↓
Valid? ─── No ───► Retry / Correct
  │
 Yes
  ▼
Final Output
```

---

## MCP Tools Reference

All tools are registered on the FastMCP `media_tools` server and sandboxed inside `workspace/`:

| Tool Name | Purpose | Key Inputs | Expected Output |
|---|---|---|---|
| `get_media_info` | Inspect media metadata (duration, resolution, aspect ratio, codecs, streams) | `media_path` | Dictionary with `duration_seconds`, `width`, `height`, `aspect_ratio_str`, `video_codec`, `audio_codec`, `media_type` |
| `generate_tts` | Synthesize voiceover audio from text script | `text`, `output_path`, `model_name` (`gtts`, `edge-tts`, `pyttsx3`), `voice` | Dictionary with `status`, `output_path`, `file_size_bytes`, `format` |
| `merge_audio_tracks` | Combine voiceover and background music with ducking | `voiceover_path`, `background_music_path`, `output_path`, `background_volume`, `ducking_ratio` | Dictionary with `status`, `output_path`, `ducking`, `background_volume` |
| `extract_audio` | Extract audio stream from input video | `video_path`, `output_path` (`.mp3`, `.aac`, `.wav`, `.m4a`) | Dictionary with `status`, `output_path`, `audio_codec` |
| `format_image_aspect_ratio` | Letterbox image to canvas (16:9, 9:16, 1:1, 4:5, 4:3, 21:9) | `image_path`, `output_path`, `aspect_ratio` | Dictionary with `status`, `output_path`, `width`, `height`, `aspect_ratio` |
| `add_text_overlay` | Add title, caption, or lower-third overlay to image | `image_path`, `output_path`, `text`, `position` (`top`, `center`, `bottom`, `lower_third`), `font_size`, `color` | Dictionary with `status`, `output_path`, `text`, `position` |
| `create_video_from_image_audio` | Render H.264/AAC MP4 clip from image + audio matching audio duration | `image_path`, `audio_path`, `output_path`, `width`, `height`, `fps` | Dictionary with `status`, `output_path`, `media_info` |
| `concatenate_video_clips` | Join multiple clips sequentially with auto-normalization for differing resolutions | `input_clips` (list), `output_path`, `auto_normalize` | Dictionary with `status`, `output_path`, `clip_count`, `media_info` |
| `replace_video_audio` | Replace video audio track with supplied audio file | `video_path`, `audio_path`, `output_path` | Dictionary with `status`, `output_path`, `media_info` |
| `generate_and_burn_subtitles` | Generate/burn subtitles from SRT, transcript text, or Whisper ASR | `video_path`, `output_path`, `subtitle_path`, `transcript`, `font_size`, `font_color` | Dictionary with `status`, `output_path`, `subtitle_path`, `media_info` |
| `validate_final_video` | Automated QC check (duration, readable, resolution, audio/video streams) | `video_path`, `expected_width`, `expected_height`, `require_audio` | Structured QC dict: `valid`, `checks`, `errors`, `warnings`, `media_info` |
| `trim_media` | Precision trimming of video/audio clip | `media_path`, `output_path`, `start_time`, `end_time`, `duration` | Dictionary with `status`, `output_path`, `media_info` |
| `adjust_audio_volume` | Adjust audio volume/gain multiplier | `audio_path`, `output_path`, `volume` (e.g. 0.5, 1.5) | Dictionary with `status`, `output_path`, `volume`, `media_info` |
| `generate_thumbnail` | Extract poster frame at timestamp | `video_path`, `output_path`, `timestamp_seconds`, `width`, `height` | Dictionary with `status`, `output_path`, `timestamp_seconds` |

---

## Environment & Dependency Management

This project uses [`uv`](https://github.com/astral-sh/uv) or standard Python virtual environments.

### Prerequisites

- **Python 3.10+** (tested on Python 3.13)
- **FFmpeg**: Bundled automatically via `imageio-ffmpeg` or detected from system `PATH`.
- Install `uv` (recommended):
  ```bash
  pip install uv
  ```

### Setup Virtual Environment & Install Dependencies

```bash
# Sync dependencies and create virtual environment (.venv)
uv sync
```

Or using standard pip:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## LLM & API Configuration

Create a local `.env` file in the root or `video-agent-system` directory:

```env
# Primary LLM Providers (for orchestrator planning)
GEMINI_API_KEY=your_gemini_api_key
OPENROUTER_API_KEY=your_openrouter_key
GROQ_API_KEY=your_groq_key

# Optional TTS & Transcription
DEFAULT_TTS_MODEL=gtts
DEFAULT_TTS_VOICE=en
```

The orchestrator utilizes automatic failover across models:
**Gemini 3.7 Flash → Gemini 3.6 Flash → OpenRouter Free → Groq GPT-OSS**.

---

## Quick Command Reference

| Purpose | Command (with `.venv` activated) | Command (without activating `.venv`) |
|---|---|---|
| **Run Web Studio & REST API** | `python main.py api --port 8000` | `uv run python main.py api --port 8000` |
| **Run FastMCP Tool Server** | `python main.py mcp` | `uv run python main.py mcp` |
| **Run MCP Healthcheck CLI** | `python main.py healthcheck` | `uv run python main.py healthcheck` |
| **Run Streamlit Dev Console** | `streamlit run streamlit_app.py` | `uv run streamlit run streamlit_app.py` |
| **Run LangGraph Agent Workflow** | `python main.py agent --prompt "..."` | `uv run python main.py agent --prompt "..."` |
| **Direct Tool Execution** | `python main.py tool tts --text "Hello"` | `uv run python main.py tool tts --text "Hello"` |
| **Inspect Media directly** | `python main.py tool info --media-path "workspace/output/clip.mp4"` | `uv run python main.py tool info --media-path "..."` |
| **Validate Media QC directly** | `python main.py tool qc --media-path "workspace/output/clip.mp4"` | `uv run python main.py tool qc --media-path "..."` |
| **Run Full Test Suite** | `pytest -v` | `uv run pytest -v` |
| **Run Media Pipeline Tests** | `pytest tests/test_mcp_media_pipeline.py -v` | `uv run pytest tests/test_mcp_media_pipeline.py -v` |
| **Run Live Smoke Test** | `$env:RUN_LIVE_ENDPOINT_TEST="1"; pytest tests/test_endpoint_smoke.py -m integration -v` | `uv run pytest tests/test_endpoint_smoke.py -m integration -v` |

---

## Web Studio Dashboard

Starting the server with `python main.py api --port 8000` automatically serves the modern web studio:
- **Web UI**: Open `http://127.0.0.1:8000` or `http://127.0.0.1:8000/ui` in your browser.
- **Interactive Swagger Docs**: Open `http://127.0.0.1:8000/docs`.

---

## Docker & Cloud Deployment

### 1. Run with Docker Locally
```bash
# Build the production container
docker build -t video-agent-studio -f Dockerfile .

# Run with environment keys
docker run -d -p 8000:8000 --env-file ../.env video-agent-studio
```

### 2. Deploy to Cloud (Render / Railway / Fly.io)
- **Render**: Connect repository and select `render.yaml` Blueprint or create a Web Service pointing to `V0007_Video_Production_Agentic_Solution/video-agent-system/Dockerfile`.
- **Railway / Dokku / PaaS**: Auto-detects the provided `Procfile` and `Dockerfile`.

---

## Directory Structure

```text
video-agent-system/
├── workspace/                  # Sandboxed input, output & temp files
│   ├── input/
│   ├── temp/
│   └── output/
├── src/
│   ├── core/                   # Raw Python media engines (audio, video, image, subtitles)
│   │   ├── audio_engine.py     # TTS synthesis (gTTS, edge-tts, pyttsx3)
│   │   ├── image_engine.py     # Canvas formatting & text overlay
│   │   ├── media_info.py       # FFmpeg stream inspection & metadata
│   │   ├── media_utils.py      # FFmpeg runner, workspace sandboxing
│   │   ├── subtitle_engine.py  # SRT generation, Whisper ASR, subtitle burn-in
│   │   ├── video_engine.py     # Clips, concatenation, audio mix/ducking, trim, volume, QC
│   │   └── artifacts.py        # File staging and upload validation
│   ├── mcp_server/             # FastMCP server exposing media tools
│   │   └── server.py           # FastMCP tool registrations & TOOL_REGISTRY
│   ├── agent/                  # LangGraph multi-agent orchestration
│   │   ├── graph.py            # LangGraph state machine definition
│   │   ├── nodes.py            # Orchestrator and Executor nodes
│   │   ├── orchestrator.py     # LLM tool-calling & planning agent
│   │   ├── executor.py         # Async task executor
│   │   ├── state.py            # TypedDict state communication bus
│   │   ├── schemas.py          # LLM output schemas
│   │   └── planner.py          # Planning utilities
│   ├── llm_clients/            # LLM provider abstractions & failover chain
│   └── config.py               # Path and default configuration
├── tests/                      # Comprehensive test suite
│   ├── test_mcp_media_pipeline.py         # Real FFmpeg/Pillow media pipeline integration tests
│   ├── test_langgraph_orchestrator_flow.py # LangGraph workflow execution tests
│   ├── test_orchestrator_endpoint.py      # FastAPI /run_orchestrator and /mcp_healthcheck tests
│   ├── test_audio_engine.py               # TTS synthesis unit tests
│   ├── test_artifacts_and_executor.py     # Artifact sandboxing & executor batch tests
│   ├── test_llm_failover.py               # LLM failover fallback tests
│   ├── test_openrouter_client.py          # OpenRouter client tests
│   ├── test_orchestrator_llm_routing.py   # Model routing tests
│   └── test_endpoint_smoke.py             # Opt-in live smoke test
├── pyproject.toml              # Project configuration and dependencies
├── uv.lock                     # Lockfile generated by uv
├── requirements.txt            # Python requirements
├── streamlit_app.py            # Developer UI console
└── main.py                     # CLI & FastAPI application entrypoint
```

