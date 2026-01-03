"""Logging helpers for LayerCode create app projects."""

from __future__ import annotations

import os
from typing import Any

import logfire
from loguru import logger

from .config import AppSettings


def setup_logging(settings: AppSettings, level: str | None = None) -> None:
    """Configure loguru and Logfire instrumentation."""

    logger.remove()
    log_level_env = os.getenv("LOG_LEVEL")
    log_level = level or log_level_env or "INFO"
    logger.add(
        sink=lambda message: print(message, end=""),
        level=log_level,
        colorize=False,
        backtrace=True,
        diagnose=False,
    )

    # Always configure logfire (auto-disables if no token present)
    logfire.configure(
        scrubbing=False,
        send_to_logfire="if-token-present",
        service_name="server",
        environment=os.getenv("APP_ENV", "development"),
    )

    # Instrument PydanticAI globally - this is enough for all agents
    logfire.instrument_pydantic_ai()


def instrument_fastapi(app: Any, settings: AppSettings) -> None:
    """Instrument FastAPI application with Logfire."""
    logfire.instrument_fastapi(app)
