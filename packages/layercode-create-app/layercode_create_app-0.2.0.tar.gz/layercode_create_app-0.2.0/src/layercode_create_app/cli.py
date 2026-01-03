"""Simple CLI for running LayerCode scaffolding servers."""

from __future__ import annotations

import argparse
import asyncio
import sys

import uvicorn
from dotenv import load_dotenv
from loguru import logger
from pydantic import ValidationError

from .agents import available_agents, create_agent
from .agents import bakery as _bakery  # noqa: F401
from .agents import echo as _echo  # noqa: F401
from .agents import outdoor_shop as _outdoor_shop  # noqa: F401
from .agents import slow_agent as _slow_agent  # noqa: F401
from .agents import starter as _starter  # noqa: F401
from .config import AppSettings
from .logging import setup_logging
from .server.app import create_app
from .tunnel import CloudflareTunnelLauncher


def list_agents() -> None:
    """List available built-in agents."""
    print("Available agents:")
    for name in sorted(available_agents()):
        print(f"  {name}")


def run(
    agent: str,
    model: str,
    host: str,
    port: int,
    agent_route: str,
    authorize_route: str,
    tunnel: bool,
    verbose: bool,
    env_file: str,
    agent_id: str | None,
    unsafe_update_webhook: bool,
) -> None:
    """Start the FastAPI server with optional Cloudflare tunnel."""

    load_dotenv(env_file, override=False)

    try:
        base_settings = AppSettings()
    except ValidationError as exc:
        print(f"Configuration error: {exc}")
        sys.exit(1)

    overrides = {
        "host": host,
        "port": port,
        "agent_route": agent_route,
        "authorize_route": authorize_route,
    }

    if agent_id:
        overrides["layercode_agent_id"] = agent_id

    settings = base_settings.model_copy(update=overrides)

    if not settings.layercode_api_key:
        print("Error: Missing LAYERCODE_API_KEY in environment or overrides.")
        sys.exit(1)

    if not settings.layercode_webhook_secret:
        print("Error: Missing LAYERCODE_WEBHOOK_SECRET in environment or overrides.")
        sys.exit(1)

    # Validate unsafe_update_webhook requirements
    if unsafe_update_webhook:
        if not tunnel:
            print("Error: --unsafe-update-webhook requires --tunnel flag")
            sys.exit(1)
        if not settings.layercode_agent_id:
            print(
                "Error: --unsafe-update-webhook requires LAYERCODE_AGENT_ID "
                "env var or --agent-id argument"
            )
            sys.exit(1)

    chosen_model = model if model else settings.default_model

    try:
        agent_instance = create_agent(agent, chosen_model)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    log_level = "DEBUG" if verbose else None
    setup_logging(settings, level=log_level)

    fastapi_app = create_app(settings, agent_instance)

    async def serve() -> None:
        config = uvicorn.Config(
            fastapi_app,
            host=settings.host,
            port=settings.port,
            log_level="info",
        )
        server = uvicorn.Server(config)

        if not tunnel:
            await server.serve()
            return

        launcher = CloudflareTunnelLauncher(
            settings.host,
            settings.port,
            settings.agent_route,
            settings.cloudflare_bin,
            settings.layercode_agent_id,
            settings.layercode_api_key,
            unsafe_update_webhook,
        )

        async def run_server() -> None:
            await server.serve()

        server_task = asyncio.create_task(run_server())

        try:
            try:
                await launcher.start()
            except RuntimeError as exc:
                logger.error(f"Tunnel error: {exc}")
                server.should_exit = True
                raise
            await server_task
        finally:
            await launcher.stop()

    try:
        asyncio.run(serve())
    except KeyboardInterrupt:  # pragma: no cover - handled during manual runs
        print("\nShutting down...")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Scaffold and run LayerCode-ready FastAPI backends.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list-agents command
    _ = subparsers.add_parser("list-agents", help="List available built-in agents")

    # run command
    run_parser = subparsers.add_parser("run", help="Start the FastAPI server")
    run_parser.add_argument(
        "--agent",
        default="starter",
        help=(
            "Agent to run (default: starter). Options: "
            "echo (simple echo), starter (general assistant), bakery (tool demo), "
            "outdoor_shop (e-commerce demo), slow_agent (test agent, ~10s response in 3 parts)"
        ),
    )
    run_parser.add_argument(
        "--model",
        default="",
        help="LLM model identifier (e.g., openai:gpt-4o-mini)",
    )
    run_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host address for the server (default: 0.0.0.0)",
    )
    run_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for the server (default: 8000)",
    )
    run_parser.add_argument(
        "--agent-route",
        default="/api/agent",
        help="Webhook route path (default: /api/agent)",
    )
    run_parser.add_argument(
        "--authorize-route",
        default="/api/authorize",
        help="Authorize route path (default: /api/authorize)",
    )
    run_parser.add_argument(
        "--tunnel",
        action="store_true",
        help="Launch a Cloudflare tunnel alongside the server",
    )
    run_parser.add_argument(
        "--agent-id",
        default=None,
        help="Agent ID for webhook updates (overrides LAYERCODE_AGENT_ID env var)",
    )
    run_parser.add_argument(
        "--unsafe-update-webhook",
        action="store_true",
        help=(
            "Automatically update agent webhook URL when using --tunnel "
            "(requires --agent-id or LAYERCODE_AGENT_ID)"
        ),
    )
    run_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose (DEBUG) logging output",
    )
    run_parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to environment file (default: .env)",
    )

    args = parser.parse_args()

    if args.command == "list-agents":
        list_agents()
    elif args.command == "run":
        run(
            agent=args.agent,
            model=args.model,
            host=args.host,
            port=args.port,
            agent_route=args.agent_route,
            authorize_route=args.authorize_route,
            tunnel=args.tunnel,
            verbose=args.verbose,
            env_file=args.env_file,
            agent_id=args.agent_id,
            unsafe_update_webhook=args.unsafe_update_webhook,
        )
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
