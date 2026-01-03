"""Application configuration models."""

from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application configuration derived from environment variables and CLI overrides."""

    host: str = "0.0.0.0"
    port: int = 8000

    agent_route: str = "/api/agent"
    authorize_route: str = "/api/authorize"

    layercode_api_key: str | None = None
    layercode_webhook_secret: str | None = None
    layercode_agent_id: str | None = None

    logfire_token: str | None = None

    cloudflare_bin: str = "cloudflared"

    default_model: str = "openai:gpt-5-nano"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("agent_route", "authorize_route")
    @classmethod
    def validate_route(cls, value: str) -> str:
        """Ensure routes start with a slash for FastAPI compatibility."""
        if not value.startswith("/"):
            msg = "Route paths must start with '/'"
            raise ValueError(msg)
        return value.rstrip("/") or "/"
