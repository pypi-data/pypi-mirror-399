"""Echo agent implementation."""

from __future__ import annotations

from pydantic_ai.messages import ModelMessage

from ..sdk.events import MessagePayload, SessionEndPayload, SessionStartPayload
from ..sdk.stream import StreamHelper
from .base import BaseLayercodeAgent, agent


@agent("echo")
class EchoAgent(BaseLayercodeAgent):
    """A minimal agent that echoes user input."""

    name = "echo"
    description = "Simple echo agent"

    def __init__(self, model: str) -> None:  # noqa: D401 - docstring inherited
        super().__init__(model)
        self._welcome = "Welcome to the Echo Agent!"

    async def handle_session_start(
        self, payload: SessionStartPayload, stream: StreamHelper
    ) -> None:
        stream.tts(self._welcome)
        stream.end()

    async def handle_message(
        self,
        payload: MessagePayload,
        stream: StreamHelper,
        history: list[ModelMessage],
    ) -> list[ModelMessage]:
        text = payload.text or ""
        stream.tts(f"You said: {text}")
        stream.end()
        return []

    async def handle_session_end(self, payload: SessionEndPayload) -> None:  # noqa: D401
        return None
