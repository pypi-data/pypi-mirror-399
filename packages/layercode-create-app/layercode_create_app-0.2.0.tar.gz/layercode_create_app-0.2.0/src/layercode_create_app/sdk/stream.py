"""Streaming helpers for LayerCode SSE responses."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any, Protocol

from fastapi.responses import StreamingResponse


class Encoder(Protocol):
    """Protocol describing an encoder interface."""

    def encode(self, text: str) -> bytes: ...


class Controller(Protocol):
    """Protocol describing a streaming controller."""

    def enqueue(self, data: bytes) -> None: ...

    def close(self) -> None: ...


class StreamHelper:
    """Utility for writing SSE payloads matching LayerCode expectations."""

    def __init__(self, turn_id: str, encoder: Encoder, controller: Controller) -> None:
        self._turn_id = turn_id
        self._encoder = encoder
        self._controller = controller
        self._closed = False

    def _emit(self, event_type: str, content: dict[str, Any]) -> None:
        payload = {"type": event_type, "turn_id": self._turn_id, **content}
        data = f"data: {json.dumps(payload, separators=(',', ':'))}\n\n"
        self._controller.enqueue(self._encoder.encode(data))

    def tts(self, content: str) -> None:
        """Emit a TTS chunk."""

        self._emit("response.tts", {"content": content})

    def data(self, content: dict[str, Any]) -> None:
        """Emit a data payload (tool calls, metadata, etc.)."""

        self._emit("response.data", {"content": content})

    def end(self) -> None:
        """Signal the end of the stream."""

        if not self._closed:
            self._emit("response.end", {})
            self._controller.close()
            self._closed = True


async def stream_response(
    request_body: dict[str, Any],
    handler: Callable[[StreamHelper], Awaitable[None]],
) -> StreamingResponse:
    """Create a FastAPI StreamingResponse compatible with LayerCode SSE."""

    turn_id = str(request_body.get("turn_id", ""))

    class UTF8Encoder:
        def encode(self, text: str) -> bytes:
            return text.encode("utf-8")

    encoder = UTF8Encoder()

    queue: asyncio.Queue[bytes] = asyncio.Queue()

    class QueueController:
        def __init__(self) -> None:
            self._closed = False

        def enqueue(self, data: bytes) -> None:
            if not self._closed:
                queue.put_nowait(data)

        def close(self) -> None:
            self._closed = True
            queue.put_nowait(b"")

    controller = QueueController()
    stream = StreamHelper(turn_id, encoder, controller)

    async def producer() -> None:
        try:
            await handler(stream)
        except Exception as exc:  # pragma: no cover - defensive logging hook
            stream.data({"error": str(exc)})
        finally:
            stream.end()

    async def generator() -> AsyncIterator[bytes]:
        producer_task = asyncio.create_task(producer())
        try:
            while True:
                chunk = await queue.get()
                if chunk == b"":
                    break
                yield chunk
        finally:
            await producer_task

    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache, no-transform",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }

    return StreamingResponse(generator(), headers=headers, media_type="text/event-stream")
