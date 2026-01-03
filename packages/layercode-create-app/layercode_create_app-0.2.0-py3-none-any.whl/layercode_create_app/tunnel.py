"""Cloudflare tunnel launcher utility."""

from __future__ import annotations

import asyncio
import contextlib
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import httpx
from loguru import logger

TUNNEL_PATTERN = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com", re.IGNORECASE)
LAYERCODE_API_BASE = "https://api.layercode.com/v1"


class CloudflareTunnelLauncher:
    """Launches a Cloudflare quick tunnel and surfaces the webhook URL."""

    def __init__(
        self,
        host: str,
        port: int,
        agent_route: str,
        binary: str = "cloudflared",
        agent_id: str | None = None,
        api_key: str | None = None,
        update_webhook: bool = False,
    ) -> None:
        self.host = host
        self.port = port
        self.agent_route = agent_route
        self.binary = binary
        self.agent_id = agent_id
        self.api_key = api_key
        self.update_webhook = update_webhook
        self.process: asyncio.subprocess.Process | None = None
        self._stdout_task: asyncio.Task[None] | None = None
        self._stderr_task: asyncio.Task[None] | None = None
        self._tunnel_url: str | None = None
        self._log_file_handle: Any | None = None
        self._previous_webhook_url: str | None = None
        self._http_client: httpx.AsyncClient | None = None

        # Create log file for tunnel output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file_path = Path(f"cloudflare_tunnel_{timestamp}.log")

    async def _get_agent_details(self) -> dict[str, Any] | None:
        """Fetch current agent details from Layercode API."""
        if not self.agent_id or not self.api_key:
            return None

        if not self._http_client:
            self._http_client = httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=5.0))

        try:
            response = await self._http_client.get(
                f"{LAYERCODE_API_BASE}/agents/{self.agent_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            response.raise_for_status()
            return cast(dict[str, Any], response.json())
        except httpx.HTTPStatusError as exc:
            logger.warning(
                f"Failed to fetch agent details (status {exc.response.status_code}): "
                f"{exc.response.text}"
            )
            return None
        except httpx.RequestError as exc:
            logger.warning(f"Failed to reach Layercode API: {exc}")
            return None

    async def _update_agent_webhook(self, webhook_url: str) -> bool:
        """Update agent webhook URL via Layercode API."""
        if not self.agent_id or not self.api_key:
            return False

        if not self._http_client:
            self._http_client = httpx.AsyncClient(timeout=httpx.Timeout(15.0, connect=5.0))

        try:
            response = await self._http_client.post(
                f"{LAYERCODE_API_BASE}/agents/{self.agent_id}",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={"webhook_url": webhook_url},
            )
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as exc:
            logger.error(
                f"Failed to update webhook (status {exc.response.status_code}): {exc.response.text}"
            )
            return False
        except httpx.RequestError as exc:
            logger.error(f"Failed to reach Layercode API: {exc}")
            return False

    async def start(self, timeout_seconds: float = 30.0) -> str:
        """Start the tunnel and return the webhook URL."""

        if shutil.which(self.binary) is None:
            raise RuntimeError(
                "cloudflared binary not found. Install it from https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/"
            )

        # Open log file for writing (line-buffered for immediate output)
        self._log_file_handle = open(  # noqa: ASYNC230
            self.log_file_path, "w", encoding="utf-8", buffering=1
        )
        self._log_file_handle.write(
            f"=== Cloudflare Tunnel Log - {datetime.now().isoformat()} ===\n"
        )
        self._log_file_handle.write(f"Target: http://{self.host}:{self.port}\n")
        self._log_file_handle.write(f"Agent route: {self.agent_route}\n")
        self._log_file_handle.write("=" * 60 + "\n\n")
        self._log_file_handle.flush()

        target_host = "localhost" if self.host in {"0.0.0.0", ""} else self.host
        target = f"http://{target_host}:{self.port}"

        logger.info("Starting Cloudflare tunnel...")
        logger.info(f"Tunnel logs: {self.log_file_path.absolute()}")

        self.process = await asyncio.create_subprocess_exec(
            self.binary,
            "tunnel",
            "--url",
            target,
            "--loglevel",
            "debug",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        assert self.process.stdout is not None
        assert self.process.stderr is not None

        # Cloudflared outputs the URL to stderr, so we need to monitor both streams
        url_future: asyncio.Future[str] = asyncio.Future()

        # Store references for type checking
        stdout = self.process.stdout
        stderr = self.process.stderr

        async def monitor_streams() -> None:
            """Monitor both stdout and stderr for the tunnel URL."""
            stdout_task = asyncio.create_task(self._scan_for_url(stdout, "stdout", url_future))
            stderr_task = asyncio.create_task(self._scan_for_url(stderr, "stderr", url_future))

            # Wait for either task to find the URL
            done, pending = await asyncio.wait(
                {stdout_task, stderr_task}, return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel the other task
            for task in pending:
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task

        try:
            # Start monitoring both streams
            monitor_task = asyncio.create_task(monitor_streams())
            tunnel_url = await asyncio.wait_for(url_future, timeout=timeout_seconds)
            await monitor_task
        except TimeoutError as exc:
            await self.stop()
            raise RuntimeError("Timed out waiting for Cloudflare tunnel URL") from exc

        self._stdout_task = asyncio.create_task(self._drain_stream(self.process.stdout, "stdout"))
        self._stderr_task = asyncio.create_task(self._drain_stream(self.process.stderr, "stderr"))

        self._tunnel_url = tunnel_url
        webhook_path = self.agent_route.lstrip("/")
        webhook_url = f"{tunnel_url}/{webhook_path}" if webhook_path else tunnel_url

        logger.info("Tunnel established successfully")
        logger.info(f"Webhook URL: {webhook_url}")

        # Update webhook if requested
        if self.update_webhook and self.agent_id:
            logger.info(f"Fetching current webhook for agent {self.agent_id}...")
            agent_details = await self._get_agent_details()
            if agent_details:
                self._previous_webhook_url = agent_details.get("webhook_url")
                if self._previous_webhook_url:
                    logger.warning(
                        f"⚠️  Updating webhook from {self._previous_webhook_url} to {webhook_url}"
                    )
                else:
                    logger.info(f"Agent has no previous webhook, setting to {webhook_url}")

                success = await self._update_agent_webhook(webhook_url)
                if success:
                    logger.info("✓ Webhook updated successfully")
                else:
                    logger.error("✗ Failed to update webhook - continuing with tunnel anyway")
            else:
                logger.warning("Could not fetch agent details - skipping webhook update")

        _print_banner(tunnel_url, webhook_url, self.update_webhook)
        return webhook_url

    async def _scan_for_url(
        self, stream: asyncio.StreamReader, stream_name: str, url_future: asyncio.Future[str]
    ) -> None:
        """Scan a stream for the tunnel URL and log all output to file only."""
        try:
            while True:
                line = await stream.readline()
                if not line:
                    break
                decoded = line.decode("utf-8", errors="ignore")

                # Write to log file only (not to console)
                if self._log_file_handle:
                    self._log_file_handle.write(f"[{stream_name}] {decoded}")
                    self._log_file_handle.flush()

                # Check if this line contains the tunnel URL
                match = TUNNEL_PATTERN.search(decoded)
                if match and not url_future.done():
                    url = match.group(0)
                    url_future.set_result(url)
                    return
        except asyncio.CancelledError:
            # This is expected when the URL is found in the other stream
            pass

    async def _drain_stream(self, stream: asyncio.StreamReader, stream_name: str) -> None:
        """Drain output from tunnel process and write to log file only."""
        while True:
            line = await stream.readline()
            if not line:
                break
            decoded = line.decode("utf-8", errors="ignore")

            # Write to log file only (not to console)
            if self._log_file_handle:
                self._log_file_handle.write(f"[{stream_name}] {decoded}")
                self._log_file_handle.flush()

    async def stop(self) -> None:
        """Stop the tunnel process and clean up resources."""
        # Restore webhook if it was updated and hasn't been changed by someone else
        if self.update_webhook and self.agent_id and self._tunnel_url:
            logger.info("Checking if webhook should be restored...")
            agent_details = await self._get_agent_details()
            if agent_details:
                current_webhook = agent_details.get("webhook_url")
                webhook_path = self.agent_route.lstrip("/")
                our_webhook = (
                    f"{self._tunnel_url}/{webhook_path}" if webhook_path else self._tunnel_url
                )

                if current_webhook == our_webhook:
                    # Webhook is still ours, restore the previous one
                    if self._previous_webhook_url:
                        logger.info(f"Restoring webhook to {self._previous_webhook_url}")
                        success = await self._update_agent_webhook(self._previous_webhook_url)
                        if success:
                            logger.info("✓ Webhook restored successfully")
                        else:
                            logger.warning("✗ Failed to restore webhook")
                    elif self._previous_webhook_url is None:
                        # There was no previous webhook, clear it
                        logger.info("Clearing webhook (no previous webhook existed)")
                        success = await self._update_agent_webhook("")
                        if success:
                            logger.info("✓ Webhook cleared successfully")
                        else:
                            logger.warning("✗ Failed to clear webhook")
                else:
                    logger.info(f"Webhook has been changed to {current_webhook}, leaving it as is")
            else:
                logger.warning("Could not fetch agent details - skipping webhook restore")

        # Close HTTP client
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

        if self.process and self.process.returncode is None:
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=5)
            except TimeoutError:
                self.process.kill()
                await self.process.wait()

        for task in (self._stdout_task, self._stderr_task):
            if task:
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task

        # Close log file
        if self._log_file_handle:
            self._log_file_handle.write(
                f"\n=== Tunnel stopped at {datetime.now().isoformat()} ===\n"
            )
            self._log_file_handle.close()
            self._log_file_handle = None
            logger.info(f"Tunnel logs saved to: {self.log_file_path.absolute()}")


def _print_banner(tunnel_url: str, webhook_url: str, webhook_updated: bool = False) -> None:
    """Print a prominent banner with tunnel URLs."""
    border = "=" * 70

    if webhook_updated:
        message = (
            f"\n\n{border}\n"
            f"{border}\n"
            "  ✓ CLOUDFLARE TUNNEL ESTABLISHED\n"
            f"{border}\n\n"
            f"  Webhook URL: {webhook_url}\n"
            "  Status: ✓ Webhook automatically updated\n\n"
            f"{border}\n"
            f"{border}\n\n"
        )
    else:
        message = (
            f"\n\n{border}\n"
            f"{border}\n"
            "  ✓ CLOUDFLARE TUNNEL ESTABLISHED\n"
            f"{border}\n\n"
            f"  Webhook URL: {webhook_url}\n\n"
            f"{border}\n"
            "  IMPORTANT: Add this webhook URL to your LayerCode agent:\n"
            "  https://dash.layercode.com/\n\n"
            "  💡 TIP: Use --unsafe-update-webhook to automatically update\n"
            "         the webhook for your agent (requires LAYERCODE_AGENT_ID)\n"
            f"{border}\n"
            f"{border}\n\n"
        )
    print(message, flush=True)
