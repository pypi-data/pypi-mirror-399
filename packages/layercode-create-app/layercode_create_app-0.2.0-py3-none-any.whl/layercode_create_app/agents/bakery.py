"""Bakery assistant agent with simple tool examples."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pydantic_ai import Agent as PydanticAgent
from pydantic_ai import RunContext
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models.openai import OpenAIChatModelSettings
from textprompts import load_prompt

from ..sdk.events import MessagePayload, SessionEndPayload, SessionStartPayload
from ..sdk.stream import StreamHelper
from .base import BaseLayercodeAgent, agent

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


@agent("bakery")
class BakeryAgent(BaseLayercodeAgent):
    """Bakery shop assistant demonstrating PydanticAI tool usage."""

    name = "bakery"
    description = "Bakery assistant with ordering tools"

    def __init__(self, model: str) -> None:
        super().__init__(model)

        self._menu: dict[str, float] = {
            "croissant": 3.50,
            "baguette": 2.25,
            "chocolate cake": 18.00,
            "sourdough": 6.00,
        }
        self._orders: list[dict[str, Any]] = []
        self._reservations: list[dict[str, Any]] = []

        prompt = load_prompt(PROMPTS_DIR / "bakery.txt", meta="strict")
        system_prompt = str(prompt.prompt)

        model_settings = None
        # Configure model settings for OpenAI GPT-5-nano to be even faster
        if model == "openai:gpt-5-nano":
            model_settings = OpenAIChatModelSettings(openai_reasoning_effort="minimal")
        self._agent = PydanticAgent(
            model,
            system_prompt=system_prompt,
            deps_type=StreamHelper,
            model_settings=model_settings,
        )

        @self._agent.tool
        async def list_menu(ctx: RunContext[StreamHelper]) -> Mapping[str, float]:
            stream = ctx.deps
            stream.data({"tool": "list_menu", "status": "called"})
            return self._menu

        @self._agent.tool
        async def make_order(
            ctx: RunContext[StreamHelper],
            item: str,
            quantity: int,
        ) -> str:
            stream = ctx.deps
            normalized = item.lower()
            if normalized not in self._menu:
                result = f"Sorry, we do not have {item} today."
            else:
                total = self._menu[normalized] * quantity
                order = {"item": normalized, "quantity": quantity, "total": total}
                self._orders.append(order)
                result = f"Order confirmed: {quantity} x {normalized} for ${total:.2f}."
            stream.data(
                {
                    "tool": "make_order",
                    "args": {"item": item, "quantity": quantity},
                    "result": result,
                }
            )
            return result

        @self._agent.tool
        async def book_table(
            ctx: RunContext[StreamHelper],
            name: str,
            time: str,
            guests: int,
        ) -> str:
            stream = ctx.deps
            reservation = {"name": name, "time": time, "guests": guests}
            self._reservations.append(reservation)
            result = f"Reservation booked for {name} at {time} for {guests} guests."
            stream.data(
                {
                    "tool": "book_table",
                    "args": reservation,
                    "result": result,
                }
            )
            return result

    def pydantic_agent(self) -> object | None:
        return self._agent

    async def handle_session_start(
        self, payload: SessionStartPayload, stream: StreamHelper
    ) -> None:
        stream.tts("Welcome to Sunrise Bakery! What can I get started for you?")
        stream.end()

    async def handle_message(
        self,
        payload: MessagePayload,
        stream: StreamHelper,
        history: list[ModelMessage],
    ) -> list[ModelMessage]:
        user_text = payload.text or ""

        async with self._agent.run_stream(user_text, deps=stream, message_history=history) as run:
            streamed = False
            async for chunk in run.stream_text(delta=True):
                if chunk:
                    streamed = True
                    stream.tts(chunk)

            final_text = await run.get_output()
            if final_text and not streamed:
                stream.tts(final_text)

            new_messages = list(run.new_messages())

        stream.end()
        return new_messages

    async def handle_session_end(self, payload: SessionEndPayload) -> None:
        self._orders.clear()
        self._reservations.clear()
