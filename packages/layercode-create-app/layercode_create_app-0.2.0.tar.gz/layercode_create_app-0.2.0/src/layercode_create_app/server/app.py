"""FastAPI application factory for LayerCode backends."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, cast

import httpx
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse, Response
from loguru import logger
from pydantic_ai.messages import ModelMessage

from ..agents.base import BaseLayercodeAgent
from ..config import AppSettings
from ..logging import instrument_fastapi
from ..sdk import (
    InvalidSignatureError,
    parse_webhook_payload,
    stream_response,
    verify_signature,
)
from ..sdk.events import (
    DataPayload,
    LayercodeEventType,
    MessagePayload,
    SessionEndPayload,
    SessionStartPayload,
    SessionUpdatePayload,
)
from ..sdk.stream import StreamHelper
from .conversation import ConversationStore

AUTH_ENDPOINT = "https://api.layercode.com/v1/agents/web/authorize_session"


def create_app(settings: AppSettings, agent: BaseLayercodeAgent) -> FastAPI:
    """Create a configured FastAPI application."""

    conversation_store = ConversationStore()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        client = httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=5.0))
        app.state.http_client = client
        logger.info(f"FastAPI application starting on {settings.host}:{settings.port}")
        yield
        await client.aclose()
        logger.info("FastAPI application shutdown")

    app = FastAPI(title="LayerCode Voice Backend", lifespan=lifespan)

    instrument_fastapi(app, settings)

    app.state.settings = settings
    app.state.agent = agent

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    async def authorize_payload(request: Request) -> dict[str, Any]:
        try:
            data = await request.json()
        except json.JSONDecodeError as exc:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid JSON body") from exc

        if not isinstance(data, dict):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid JSON body")

        return cast(dict[str, Any], data)

    @app.post(settings.authorize_route)
    async def authorize_endpoint(request: Request) -> Response:
        body = await authorize_payload(request)
        api_key = settings.layercode_api_key
        if not api_key:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "LAYERCODE_API_KEY is not configured",
            )
        client: httpx.AsyncClient = app.state.http_client

        try:
            response = await client.post(
                AUTH_ENDPOINT,
                json=body,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(f"LayerCode API error {exc.response.status_code}")
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=exc.response.text or exc.response.reason_phrase,
            ) from exc
        except httpx.RequestError as exc:
            logger.error(f"Failed to reach LayerCode API: {exc}")
            raise HTTPException(status.HTTP_502_BAD_GATEWAY, "LayerCode API unreachable") from exc

        logger.info("Session authorized for agent")
        return JSONResponse(status_code=status.HTTP_200_OK, content=response.json())

    @app.post(settings.agent_route)
    async def agent_webhook(request: Request) -> Response:
        signature = request.headers.get("layercode-signature")
        if not signature:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing signature header")

        body_bytes = await request.body()
        body_str = body_bytes.decode("utf-8")

        secret = settings.layercode_webhook_secret
        if not secret:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "LAYERCODE_WEBHOOK_SECRET is not configured",
            )

        try:
            verify_signature(body_str, signature, secret)
        except InvalidSignatureError as exc:
            logger.warning(f"Invalid signature: {exc}")
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc

        try:
            payload_dict: dict[str, Any] = json.loads(body_str)
        except json.JSONDecodeError as exc:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid JSON body") from exc

        try:
            payload = parse_webhook_payload(payload_dict)
        except Exception as exc:
            logger.error(f"Payload validation failed: {exc}")
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid payload schema") from exc

        logger.info(f"Webhook received: type={payload.type} conversation={payload.conversation_id}")

        await conversation_store.acquire_lock(payload.conversation_id)
        try:
            if payload.type == LayercodeEventType.SESSION_START:
                return await _handle_session_start(
                    payload_dict,
                    cast(SessionStartPayload, payload),
                    agent,
                )
            if payload.type == LayercodeEventType.MESSAGE:
                history = conversation_store.get(payload.conversation_id)
                response, new_messages = await _handle_message(
                    payload_dict,
                    cast(MessagePayload, payload),
                    history,
                    agent,
                )
                conversation_store.append(payload.conversation_id, new_messages)
                return response
            if payload.type == LayercodeEventType.DATA:
                return await _handle_data(cast(DataPayload, payload), agent)
            if payload.type == LayercodeEventType.SESSION_UPDATE:
                return await _handle_session_update(cast(SessionUpdatePayload, payload), agent)
            if payload.type == LayercodeEventType.SESSION_END:
                return await _handle_session_end(cast(SessionEndPayload, payload), agent)

            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unsupported event type")
        finally:
            conversation_store.release_lock(payload.conversation_id)

    return app


async def _handle_session_start(
    payload_dict: dict[str, Any],
    payload: SessionStartPayload,
    agent: BaseLayercodeAgent,
) -> Response:
    async def handler(stream: StreamHelper) -> None:
        await agent.handle_session_start(payload, stream)

    return await stream_response(payload_dict, handler)


async def _handle_message(
    payload_dict: dict[str, Any],
    payload: MessagePayload,
    history: list[ModelMessage],
    agent: BaseLayercodeAgent,
) -> tuple[Response, list[ModelMessage]]:
    new_messages: list[ModelMessage] = []

    async def handler(stream: StreamHelper) -> None:
        nonlocal new_messages
        new_messages = await agent.handle_message(payload, stream, history)

    response = await stream_response(payload_dict, handler)
    return response, new_messages


async def _handle_data(
    payload: DataPayload,
    agent: BaseLayercodeAgent,
) -> Response:
    data_keys = list(payload.data.keys()) if payload.data else []
    logger.info(f"Data event received: session={payload.session_id} keys={data_keys}")
    response_data = await agent.handle_data(payload)
    return JSONResponse(response_data or {"status": "ok"})


async def _handle_session_update(
    payload: SessionUpdatePayload,
    agent: BaseLayercodeAgent,
) -> Response:
    logger.info(
        f"Session update: session={payload.session_id} "
        f"recording_status={payload.recording_status} duration={payload.recording_duration}"
    )
    await agent.handle_session_update(payload)
    return JSONResponse({"status": "ok"})


async def _handle_session_end(
    payload: SessionEndPayload,
    agent: BaseLayercodeAgent,
) -> Response:
    transcript_count = len(payload.transcript) if payload.transcript else 0
    logger.info(
        f"Session ended: session={payload.session_id} "
        f"duration={payload.duration}ms transcript_items={transcript_count}"
    )
    await agent.handle_session_end(payload)
    return JSONResponse({"status": "ok"})
