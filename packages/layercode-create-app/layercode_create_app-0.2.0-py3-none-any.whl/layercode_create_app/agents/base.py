"""Base classes and registry for LayerCode agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, TypeVar

from pydantic_ai.messages import ModelMessage

from ..sdk.events import (
    DataPayload,
    MessagePayload,
    SessionEndPayload,
    SessionStartPayload,
    SessionUpdatePayload,
)
from ..sdk.stream import StreamHelper


class BaseLayercodeAgent(ABC):
    """Base class for agents handling LayerCode webhook events."""

    name: str
    description: str

    def __init__(self, model: str) -> None:
        self.model = model

    @abstractmethod
    async def handle_session_start(
        self, payload: SessionStartPayload, stream: StreamHelper
    ) -> None:
        """Handle `session.start` events."""

    @abstractmethod
    async def handle_message(
        self,
        payload: MessagePayload,
        stream: StreamHelper,
        history: list[ModelMessage],
    ) -> list[ModelMessage]:
        """Handle `message` events and return messages to append to history."""

    async def handle_session_end(self, payload: SessionEndPayload) -> None:
        """Handle `session.end` events.

        Override to perform cleanup, persist transcripts, or log analytics.
        """

        return None

    async def handle_session_update(self, payload: SessionUpdatePayload) -> None:
        """Handle `session.update` events (e.g., recording completed).

        Override to process recording URLs, handle recording failures, etc.
        """

        return None

    async def handle_data(self, payload: DataPayload) -> dict[str, Any] | None:
        """Handle `data` events (client-sent structured JSON).

        Override to process client-side data payloads. Return a dict to send
        a JSON response, or None for a default {"status": "ok"} response.
        """

        return None

    @classmethod
    def display_name(cls) -> str:
        return getattr(cls, "name", cls.__name__.lower())

    def pydantic_agent(self) -> object | None:
        """Return the underlying PydanticAI agent if applicable."""

        return None


AgentFactory = Callable[[str], BaseLayercodeAgent]


_REGISTRY: dict[str, AgentFactory] = {}


def register_agent(name: str, factory: AgentFactory) -> None:
    """Register an agent factory under a given name."""

    key = name.lower()
    _REGISTRY[key] = factory


def create_agent(name: str, model: str) -> BaseLayercodeAgent:
    """Instantiate an agent by registry name."""

    key = name.lower()
    if key not in _REGISTRY:
        raise ValueError(f"Unknown agent '{name}'. Available: {', '.join(sorted(_REGISTRY))}")
    return _REGISTRY[key](model)


TAgent = TypeVar("TAgent", bound=BaseLayercodeAgent)


def agent(name: str) -> Callable[[Callable[[str], TAgent]], Callable[[str], TAgent]]:
    """Decorator to register agent factories."""

    def decorator(factory: Callable[[str], TAgent]) -> Callable[[str], TAgent]:
        register_agent(name, factory)
        return factory

    return decorator


def available_agents() -> dict[str, AgentFactory]:
    """Return a copy of the registered agent mapping."""

    return dict(_REGISTRY)
