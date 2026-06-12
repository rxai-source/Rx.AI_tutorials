Here is the updated project plan, refactored to transition from a hardcoded "Writer's Room" to a highly extensible, **Configuration-Driven Architecture**. This will allow you to instantly spin up an Agentic Group Chat, a Shark Tank, or a Drug Design lab simply by swapping out a configuration file.

# AI Boardroom — Project Plan

> **Status**: ✅ Core backend scaffolded. 🔄 Refactoring for Extensibility (Phase 2 active)
> **Last Updated**: 2026-06-10

---

## Project Overview

A highly scalable, multi-workflow orchestration platform. By utilizing **Room Templates**, the system dynamically instantiates specialized AI personas, custom state machines, and dynamic action tools to simulate any collaborative environment (Writer's Room, Shark Tank, Drug Design Lab, etc.). Orchestrated via LangGraph on a FastAPI backend with WebSocket streaming.

---

## Architecture (Configuration-Driven)

```text
POST /ai_room/create
        │ Loads JSON/YAML Room Template (e.g., shark_tank.yaml)
        ▼
  [Initialization]
  System dynamically provisions Personas, Tools, and Stage Logic
        │
        ▼
  [Continuous Loop / Dynamic Stages]
  Client ──── WS Stream ───► Orchestrator Agent (Silent Semantic Router)
                                │
                                ├── intent_analysis?
                                ├── tool_routing?
                                │
                                ▼
  [Agent Action Space]
  Dynamic Agent A (e.g., Investor) ──► Uses Tool (e.g., make_offer())
  Dynamic Agent B (e.g., SME)      ──► Processes silently in isolated scratchpad
                                │
                                ▼
  Orchestrator Agent ──► Synthesizes actions ──► Updates Synchronized Shared Memory
                                │
                                ▼
  [Dynamic UI Rendering]
  FastAPI pushes UI Layout Frames (e.g., {"layout": "split_screen_deal_tracker"}) alongside tokens

```

---

## Technology Stack

| Layer | Technology |
| --- | --- |
| Backend API | Python FastAPI |
| Configuration | YAML / JSON (Room Templates) |
| Streaming | WebSockets (FastAPI native) |
| Agent Orchestration | LangChain + LangGraph (Dynamic Graph Building) |
| LLM Clients | Google Gemini (genai), OpenRouter |
| Auth | JWT (python-jose) via `Sec-WebSocket-Protocol` header |
| Frontend | React + Vite + TypeScript + Zustand (Componentized UI) |
| Validation | Pydantic v2 |

---

## Isolation Rules (Enforced)

| Role | Private Scratchpad | Public Group Chat Output |
| --- | --- | --- |
| **Orchestrator** | Intent analysis, routing decisions, tool evaluation | UI Layout frames, synthesized summaries, turn handoffs |
| **Dynamic Agent** | Intermediate reasoning, domain-specific calculations | Final structured output (e.g., `DealOffer`, `MolecularStructure`, `ScriptDraft`) |

**Enforcement mechanism:**

* Each agent holds `_scratchpad: list[dict]` — a private instance variable.


* Scratchpad is populated by `agent.think()` (private reasoning).


* Scratchpad is **cleared** by `agent.respond()` after producing the public output.
* 
`RoomSharedState` (the LangGraph shared state) **never contains scratchpad data**.


* The Orchestrator manages these scratchpads to let agents formulate thoughts before speaking.



---

## Repository Structure

```text
V0005_Extensible_AI_Boardroom/
├── backend/
│   ├── main.py                          ✅ FastAPI app factory
│   ├── requirements.txt
│   ├── .env.example
│   │
│   ├── core/
│   │   ├── config.py                    ✅ Pydantic-settings
│   │   ├── security.py                  ✅ JWT via WS protocol
│   │   └── templates/                   🔄 NEW: Room Configurations
│   │       ├── writers_room.yaml
│   │       ├── shark_tank.yaml
│   │       └── drug_design.yaml
│   │
│   ├── agents/
│   │   ├── base_agent.py                ✅ BaseAgent with isolated _scratchpad
│   │   ├── orchestrator.py              🔄 NEW: Silent semantic router
│   │   ├── dynamic_agent.py             🔄 NEW: Instantiated via Room Template
│   │   └── tools/                       🔄 NEW: Dynamic Tool Registry
│   │       ├── script_tools.py
│   │       ├── investor_tools.py        (e.g., make_offer)
│   │       └── biotech_tools.py
│   │
│   ├── graph/
│   │   ├── state.py                     ✅ RoomSharedState TypedDict
│   │   ├── nodes.py                     ✅ Generic node execution functions
│   │   └── dynamic_graph_builder.py     🔄 NEW: Compiles LangGraph dynamically from template stages
│   │
│   ├── llm_clients/                     ✅ (Untouched) Gemini & OpenRouter clients
│   ├── api/
│   │   ├── schemas.py                   ✅ Pydantic request/response models
│   │   └── routes/
│   │       ├── auth.py
│   │       └── room_manager.py          🔄 NEW: Handles template loading and WS /ws/room/{id}
│   │
│   └── tests/
│
├── frontend/
│   ├── package.json
│   └── src/
│       ├── api/
│       ├── store/
│       └── components/                  🔄 NEW: Pluggable UI widgets
│           ├── layouts/                 (ChatOnly, SplitScreen, Canvas)
│           └── widgets/                 (DealTracker, ScriptSidebar, MoleculeViewer)
└── plan.md

```

---

## Phase Roadmap

### ✅ Phase 1 — Core Infrastructure (DONE)

* Backend FastAPI application factory & JWT security.
* BaseAgent with isolated private scratchpad.


* LangGraph shared state documented isolation boundary.


* `WS /ws/boardroom/{session_id}` with JWT via `Sec-WebSocket-Protocol`.

### 🔄 Phase 2 — Configuration-Driven Refactoring (Current)

* [x] Implement `Room Templates` loader (parse YAML/JSON configs for personas and stages).


* [x] Build the `dynamic_graph_builder.py` to compile LangGraph state machines based on the loaded template's stages.


* [x] Replace hardcoded Director/Writer with a generic `DynamicAgent` class that absorbs a persona from the config.

* [ ] Finalize the user journey for the writers' room flow - what is the steps happening in each stage, and what are the parameters which decide the completion of the stage, and what is the conversation, etc within each step of each stage. 

* [ ] Implement the silent `Orchestrator` agent to handle routing and turn-taking.


* [ ] Build the `Tool Registry` to assign environment-specific action spaces (e.g., `make_offer` tool for Shark Tank).


* [ ] Create the end-to-end flow from the FastAPI endpoint for the `writers_room` flow for the different stages implementation and responses from each of the agents.


* [ ] Do the backend testing for the end-to-end `writers_room` flow for 5 different test scenarios.

### 🔲 Phase 3 — Componentized Frontend UI

* [ ] Setup Zustand store to interpret UI Layout frames pushed by the FastAPI backend.


* [ ] Build pluggable layout containers that mount/unmount seamlessly without interrupting the WebSocket token stream.


* [ ] Develop domain-specific widgets (e.g., "Deal Tracker" for Shark Tank, "Review Sidebar" for Writer's Room).



### 🔲 Phase 4 — Testing & Production Hardening

* [ ] Integration tests for template loading and dynamic graph building.
* [ ] Test the Orchestrator's ability to isolate scratchpads across different dynamic agents.
* [ ] Replace stub user store with PostgreSQL/NeonDB.
* [ ] Docker Compose (backend + frontend) & CI/CD pipeline.

---

## Key Design Decisions

1. 
**Room Templates (YAML/JSON)**: Moving away from hardcoded logic, the application flow is now entirely dictated by config files defining the roster, the stages (e.g., `["pitch", "q_and_a", "bidding"]`), and the required tools.


2. **The Silent Orchestrator**: The "Director" is replaced by a background Semantic Router. It analyzes user intent and dictates which agent acts, removing the reliance on a visible "boss" agent for casual group chats or adversarial formats like a Shark Tank.


3. **Dynamic UI Rendering**: The frontend no longer follows a linear progression. The backend pushes UI layout frames (e.g., `{"layout": "split_screen_deal_tracker"}`). The React client intercepts these frames and mounts widgets dynamically, allowing a single frontend to support entirely different use cases.


4. **Environment Action Spaces (Tools)**: Agents are granted specific capabilities based on the active template. A Shark Tank investor agent can execute a `make_offer()` function, which the backend routes directly to the frontend's Deal Tracker UI.


## FAQs

1. Explain all the key python scripts - what are they for, what they do, etc.