"""Typed LayerCode event models."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class LayercodeEventType(str, Enum):
    """Supported inbound LayerCode webhook events."""

    SESSION_START = "session.start"
    MESSAGE = "message"
    DATA = "data"
    SESSION_END = "session.end"
    SESSION_UPDATE = "session.update"


class BaseWebhookPayload(BaseModel):
    """Shared attributes for all webhook events (no turn_id)."""

    type: LayercodeEventType
    session_id: str = Field(..., alias="session_id")
    conversation_id: str = Field(..., alias="conversation_id")
    metadata: dict[str, Any] | None = None
    from_phone_number: str | None = Field(default=None, alias="from_phone_number")
    to_phone_number: str | None = Field(default=None, alias="to_phone_number")

    model_config = ConfigDict(populate_by_name=True)


class TurnBasedPayload(BaseWebhookPayload):
    """Base for events that occur within a conversation turn (includes turn_id)."""

    turn_id: str = Field(..., alias="turn_id")


class SessionStartPayload(TurnBasedPayload):
    """Payload for `session.start` events."""

    type: Literal[LayercodeEventType.SESSION_START]
    text: str | None = None


class MessagePayload(TurnBasedPayload):
    """Payload for `message` events."""

    type: Literal[LayercodeEventType.MESSAGE]
    text: str | None = None
    recording_url: str | None = Field(default=None, alias="recording_url")
    recording_status: str | None = Field(default=None, alias="recording_status")
    transcript: str | None = None
    usage: dict[str, Any] | None = None


class DataPayload(TurnBasedPayload):
    """Payload for `data` events (client-sent structured JSON)."""

    type: Literal[LayercodeEventType.DATA]
    data: dict[str, Any] = Field(default_factory=dict)


class TranscriptItem(BaseModel):
    """A single item in the session transcript."""

    role: str
    text: str
    timestamp: int | str | None = None  # Unix ms (int) or ISO string

    model_config = ConfigDict(extra="allow")


class SessionEndPayload(BaseWebhookPayload):
    """Payload for `session.end` events (no turn_id)."""

    type: Literal[LayercodeEventType.SESSION_END]
    agent_id: str | None = None
    started_at: str | None = None
    ended_at: str | None = None
    duration: int | None = None  # milliseconds
    transcription_duration_seconds: float | None = None
    tts_duration_seconds: float | None = None
    latency: float | None = None
    ip_address: str | None = None
    country_code: str | None = None
    recording_status: str | None = None  # "enabled" | "disabled"
    transcript: list[TranscriptItem] | None = None


class SessionUpdatePayload(BaseWebhookPayload):
    """Payload for `session.update` events (no turn_id)."""

    type: Literal[LayercodeEventType.SESSION_UPDATE]
    recording_status: str | None = None  # "completed" | "failed"
    recording_url: str | None = Field(default=None, alias="recording_url")
    recording_duration: float | None = Field(default=None, alias="recording_duration")
    error_message: str | None = Field(default=None, alias="error_message")


WebhookPayload = (
    SessionStartPayload | MessagePayload | DataPayload | SessionEndPayload | SessionUpdatePayload
)


_WEBHOOK_PAYLOAD_ADAPTER: TypeAdapter[WebhookPayload] = TypeAdapter(WebhookPayload)


def parse_webhook_payload(data: dict[str, Any]) -> WebhookPayload:
    """Validate raw webhook payload into the appropriate typed model."""

    return _WEBHOOK_PAYLOAD_ADAPTER.validate_python(data)
