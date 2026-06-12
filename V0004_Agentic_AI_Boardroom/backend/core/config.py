# backend/core/config.py
"""
Central application configuration using pydantic-settings.
Loads from environment variables / .env file.
"""

import os
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_env: str = Field(default="development")
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000)
    allowed_origins: str = Field(default="http://localhost:3000")

    # --- JWT ---
    jwt_secret_key: str = Field(default="change_me_in_production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=60)

    # --- LLM API Keys ---
    gemini_api_key: str = Field(default="")
    openrouter_api_key: str = Field(default="")
    openai_api_key: str = Field(default="")
    deepseek_api_key: str = Field(default="")

    # --- Ollama (local) ---
    ollama_host: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="llama3")

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache()
def get_settings() -> Settings:
    """Return cached Settings singleton."""
    return Settings()
