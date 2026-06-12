# backend/main.py
"""
AI Boardroom — FastAPI application entry point.

Mounts:
  /auth          — JWT authentication
  /ai_writer_room — POST endpoint (director + optional full pipeline)
  /ws/boardroom  — WebSocket streaming (JWT via Sec-WebSocket-Protocol)
  /docs          — Swagger UI (development only)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from api.routes.auth import router as auth_router
from api.routes.writer_room import router as writer_room_router

settings = get_settings()


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    print(f"🎬 AI Boardroom starting — env: {settings.app_env}")
    yield
    print("🎬 AI Boardroom shutting down.")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Boardroom",
        description=(
            "Agentic AI writing boardroom powered by LangGraph. "
            "Orchestrates Director, Tech SME, Writer, and Critic agents."
        ),
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.app_env == "development" else None,
        redoc_url="/redoc" if settings.app_env == "development" else None,
    )

    # --- CORS ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Routers ---
    app.include_router(auth_router)
    app.include_router(writer_room_router)

    # --- Health check ---
    @app.get("/health", tags=["System"])
    async def health():
        return {"status": "ok", "service": "ai-boardroom"}

    return app


app = create_app()


# ---------------------------------------------------------------------------
# Dev server entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env == "development",
    )
