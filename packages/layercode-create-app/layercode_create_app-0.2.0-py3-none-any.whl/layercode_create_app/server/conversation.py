"""In-memory conversation state management."""

from __future__ import annotations

import asyncio
from collections import defaultdict

from pydantic_ai.messages import ModelMessage


class ConversationStore:
    """Tracks per-conversation message history with concurrency protection."""

    def __init__(self) -> None:
        self._histories: defaultdict[str, list[ModelMessage]] = defaultdict(list)
        self._locks: dict[str, asyncio.Lock] = {}
        self._registry_lock = asyncio.Lock()

    async def acquire_lock(self, conversation_id: str) -> asyncio.Lock:
        """Acquire a lock specific to the conversation id."""

        async with self._registry_lock:
            lock = self._locks.get(conversation_id)
            if lock is None:
                lock = asyncio.Lock()
                self._locks[conversation_id] = lock
        await lock.acquire()
        return lock

    def release_lock(self, conversation_id: str) -> None:
        """Release the lock for a conversation if it exists."""

        lock = self._locks.get(conversation_id)
        if lock and lock.locked():
            lock.release()

    def append(self, conversation_id: str, messages: list[ModelMessage]) -> None:
        """Append messages to a conversation history."""

        if messages:
            self._histories[conversation_id].extend(messages)

    def get(self, conversation_id: str) -> list[ModelMessage]:
        """Return history for a conversation id."""

        return list(self._histories.get(conversation_id, []))
