# AI Boardroom

> Agentic AI writing boardroom powered by **FastAPI**, **LangGraph**, and **React**.

## Architecture

```
Director ──► Tech SME ──► Writer ──► Critic
   │                                    │
   └── Needs clarification? ──► END     └── Approved? ──► END
                                             │
                                     revision_required ──► Writer (max 2x)
```

## Project Structure

```
V0004_Agentic_AI_Boardroom/
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── requirements.txt
│   ├── .env.example
│   ├── core/
│   │   ├── config.py              # Settings (pydantic-settings)
│   │   └── security.py            # JWT + WebSocket auth
│   ├── agents/
│   │   ├── base_agent.py          # Base class with isolated scratchpad
│   │   ├── director_agent.py      # Planner / orchestrator
│   │   ├── tech_sme_agent.py      # Domain researcher
│   │   ├── writer_agent.py        # Content drafter
│   │   └── critic_agent.py        # Quality reviewer
│   ├── graph/
│   │   ├── state.py               # LangGraph BoardroomState (shared group chat)
│   │   ├── nodes.py               # Node functions (one per agent)
│   │   └── boardroom_graph.py     # Compiled StateGraph
│   ├── llms/
│   │   ├── base.py                # BaseLLM abstract class
│   │   ├── registry.py            # Provider factory
│   │   └── adapters/
│   │       ├── gemini.py
│   │       └── openrouter.py
│   ├── llm_clients/
│   │   ├── gemini_client.py
│   │   └── openrouter_client.py
│   ├── api/
│   │   ├── schemas.py             # Pydantic request/response models
│   │   └── routes/
│   │       ├── auth.py            # POST /auth/token
│   │       └── writer_room.py     # POST /ai_writer_room + WS /ws/boardroom/{id}
│   └── tests/
│       ├── test_director_agent.py
│       └── test_security.py
├── frontend/
│   ├── package.json               # React + Vite + TypeScript + Zustand
│   └── src/
│       ├── api/boardroom.ts       # REST + WebSocket client
│       └── store/boardroom.store.ts  # Zustand global state
├── codebase/                      # Reference implementations
├── plan.md
├── .gitignore
└── README.md
```

## Isolation Rules

| Layer | Private (scratchpad) | Public (group chat) |
|---|---|---|
| Director | Reasoning about the request | `WritingPlan` JSON |
| Tech SME | Research steps, draft notes | `SMEReport` JSON |
| Writer | Draft iterations, self-corrections | `WriterDraft` JSON |
| Critic | Annotation passes, comparison steps | `CriticReport` JSON |

**Rule**: `BoardroomState` (LangGraph shared state) NEVER contains scratchpad data.

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env        # Fill in your API keys
python main.py
```

### API Docs

Open http://localhost:8000/docs

### WebSocket Authentication

```javascript
// Client sends JWT via Sec-WebSocket-Protocol header
const ws = new WebSocket(
  "ws://localhost:8000/ws/boardroom/<session_id>",
  ["bearer", "<your_jwt_token>"]
);
```

### POST /ai_writer_room (Director-only, default)

```bash
curl -X POST http://localhost:8000/ai_writer_room \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"user_request": "Write a blog post about LangGraph multi-agent systems."}'
```

### POST /ai_writer_room (Full pipeline)

```bash
curl -X POST http://localhost:8000/ai_writer_room \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"user_request": "...", "run_full_pipeline": true}'
```
