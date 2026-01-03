"""Slow agent for testing wait/timeout handling in layercode-gym.

This agent responds in 3 parts over ~10 seconds total, with 5-second gaps
between response parts. This stress-tests the 3-second idle timeout in
layercode-gym, making it ideal for validating wait handling and timeout logic.

Response pattern:
1. "Processing..." + data(status=loading, progress=0)
2. [5 second delay]
3. "Still working..." + data(status=processing, progress=50)
4. [5 second delay]
5. "Done!" + data(status=complete, progress=100)

Run with:
    uv run layercode-create-app run --agent slow_agent --tunnel --unsafe-update-webhook
"""

from __future__ import annotations

import asyncio

from pydantic_ai.messages import ModelMessage

from ..sdk.events import MessagePayload, SessionEndPayload, SessionStartPayload
from ..sdk.stream import StreamHelper
from .base import BaseLayercodeAgent, agent


@agent("slow_agent")
class SlowAgent(BaseLayercodeAgent):
    """Testing agent that responds in 3 parts over ~10 seconds for wait/timeout testing."""

    name = "slow_agent"
    description = (
        "Testing agent that responds in 3 parts over ~10 seconds (for wait/timeout testing)"
    )

    def __init__(self, model: str) -> None:
        super().__init__(model)

    async def handle_session_start(
        self, payload: SessionStartPayload, stream: StreamHelper
    ) -> None:
        stream.tts(
            "Welcome! I'm a slow agent. "
            "Every response takes a bit longer than usual with updates along the way."
        )
        stream.end()

    async def handle_message(
        self,
        payload: MessagePayload,
        stream: StreamHelper,
        history: list[ModelMessage],
    ) -> list[ModelMessage]:
        # Part 1: Acknowledge and start loading
        stream.tts("Processing your request now. Please wait 5 seconds.")
        stream.data({"status": "loading", "progress": 0})

        await asyncio.sleep(5)

        # Part 2: Progress update
        stream.tts(" Still working. Please wait 5 more seconds.")
        stream.data({"status": "processing", "progress": 50})

        await asyncio.sleep(5)

        # Part 3: Complete
        stream.tts(" Done! Your request has been processed successfully.")
        stream.data({"status": "complete", "progress": 100})
        stream.end()

        return []

    async def handle_session_end(self, payload: SessionEndPayload) -> None:
        return None
