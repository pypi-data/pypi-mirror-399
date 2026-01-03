# layercode-create-app

[![CI](https://github.com/svilupp/layercode-create-app/actions/workflows/ci.yml/badge.svg)](https://github.com/svilupp/layercode-create-app/actions/workflows/ci.yml)
[![Docs](https://github.com/svilupp/layercode-create-app/actions/workflows/docs.yml/badge.svg)](https://github.com/svilupp/layercode-create-app/actions/workflows/docs.yml)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://svilupp.github.io/layercode-create-app)

**Unofficial quick-starter template for [LayerCode.com](https://layercode.com) voice agent platform**

`layercode-create-app` is a lightweight toolkit for spinning up LayerCode-compatible FastAPI backends with a single command. It packages:

- **Typed LayerCode SDK primitives** for webhook payloads, signature verification, and SSE streaming
- **Ready-to-run agents** (echo, starter, bakery, outdoor_shop, slow_agent) powered by [PydanticAI](https://ai.pydantic.dev/)
- **Observability hooks** for Logfire + Loguru
- **Built-in Cloudflare tunneling** for instant public webhook URLs
- **An ergonomic CLI** for zero-config development

The goal is to give teams an opinionated but hackable starting point for building LayerCode voice agents.

---

## Quick Start

Run from anywhere with `uvx` (no installation required):

```bash
uvx layercode-create-app run --tunnel
```

This command will:
1. Start a FastAPI server with the default agent
2. Launch a Cloudflare tunnel and display your public webhook URL
3. Show you exactly where to paste the URL in your LayerCode dashboard (if you didn't use `--unsafe-update-webhook`)

> **Tip:** Add `--unsafe-update-webhook` to skip manual webhook setting in Layercode dashboard (see [Auto-Update Webhook](#auto-update-webhook-quick-testing)).

### Example Output

```
2025-11-02 17:06:57.571 | INFO | Starting Cloudflare tunnel...
2025-11-02 17:06:57.571 | INFO | Tunnel logs: /path/to/cloudflare_tunnel_20251102_170657.log
INFO:     Started server process [82911]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
2025-11-02 17:06:58.123 | INFO | Tunnel established successfully
2025-11-02 17:06:58.123 | INFO | Webhook URL: https://apache-lake-soviet-infrastructure.trycloudflare.com/api/agent

======================================================================
======================================================================
  ✓ CLOUDFLARE TUNNEL ESTABLISHED
======================================================================

  Webhook URL: https://apache-lake-soviet-infrastructure.trycloudflare.com/api/agent

======================================================================
  IMPORTANT: Add this webhook URL to your LayerCode agent:
  https://dash.layercode.com/
======================================================================
======================================================================

INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## Environment Setup

Create a `.env` file with your credentials:

```bash
# Required - Get these from https://dash.layercode.com/
LAYERCODE_API_KEY=...
LAYERCODE_WEBHOOK_SECRET=...

# Required - Your AI provider API key
OPENAI_API_KEY=sk-...
# OR for Google models:
# GOOGLE_GENERATIVEAI_API_KEY=...

# Optional
LOGFIRE_TOKEN=pylf_...
```

The CLI automatically loads `.env` from the current directory. Use `--env-file` to specify a different path.

---

## CLI Usage

Get help on available commands:

```bash
uvx layercode-create-app run -h
```

### Available Commands

**List available agents:**
```bash
uvx layercode-create-app list-agents
```

**Run a specific agent:**
```bash
uvx layercode-create-app run --agent starter --port 8005
```

**Run with Cloudflare tunnel (recommended):**
```bash
uvx layercode-create-app run --agent bakery --tunnel
```

### CLI Options

| Option | Default | Description |
| --- | --- | --- |
| `--agent` | `starter` | Which built-in agent to run (`echo`, `starter`, `bakery`, `outdoor_shop`, `slow_agent`) |
| `--model` | env `DEFAULT_MODEL` | Model identifier passed to PydanticAI |
| `--host` | `0.0.0.0` | Server host binding |
| `--port` | `8000` | Server port |
| `--agent-route` | `/api/agent` | Webhook route path |
| `--authorize-route` | `/api/authorize` | Authorization route path |
| `--tunnel` | `False` | Launch a Cloudflare quick tunnel for public access |
| `--agent-id` | env `LAYERCODE_AGENT_ID` | Agent ID for webhook auto-update |
| `--unsafe-update-webhook` | `False` | Auto-update agent webhook URL to tunnel URL (requires `--tunnel`) |
| `--env-file` | `.env` | Path to environment file to load before running |
| `--verbose`, `-v` | `False` | Enable DEBUG logging for detailed request traces |

---

## Built-in Agents

- **echo** – Deterministic welcome + echo responses (no LLMs required)
- **starter** – Concise general-purpose assistant with progressive disclosure and automatic transcription cleanup
- **bakery** – Bakery persona demonstrating simple tool calls for menu lookup, order placement, and reservations
- **outdoor_shop** – Customer service agent for "Nimbus Gear" outdoor equipment store with complex tool responses and structured data payloads
- **slow_agent** – Testing agent that responds in 3 parts over ~10 seconds; ideal for testing wait/timeout handling in layercode-gym

All prompts live under `src/layercode_create_app/agents/prompts/`. Edit them or add new agents by following the `BaseLayercodeAgent` interface.

---

## Webhook Events

The SDK handles all LayerCode webhook event types:

| Event | Description | Agent Method |
|-------|-------------|--------------|
| `session.start` | New session begins | `handle_session_start()` |
| `message` | User speech transcribed | `handle_message()` |
| `data` | Client-sent structured JSON | `handle_data()` |
| `session.update` | Recording completed/failed | `handle_session_update()` |
| `session.end` | Session finished with transcript | `handle_session_end()` |

Override these methods in your agent to handle each event type. See the [SDK documentation](https://svilupp.github.io/layercode-create-app/api/sdk/) for payload schemas.

---

## Cloudflare Tunnel

When you use the `--tunnel` flag:

- **All tunnel debug logs** are written to a timestamped file (e.g., `cloudflare_tunnel_20251102_170657.log`)
- **The webhook URL** is displayed prominently with instructions
- **No tunnel output** clutters your main application logs
- **The server waits** for the tunnel to be ready before accepting requests

This makes it trivial to develop and test voice agents without deploying to production infrastructure.

### Auto-Update Webhook (Quick Testing)

For rapid iteration, use `--unsafe-update-webhook` to automatically update your LayerCode agent's webhook URL to the tunnel URL:

```bash
# Set your agent ID in .env
LAYERCODE_AGENT_ID=agent_...

# Run with auto-update
uvx layercode-create-app run --tunnel --unsafe-update-webhook
```

This will:
1. Start the tunnel and get a public URL
2. Fetch the current webhook URL from your agent (and save it)
3. Update your agent's webhook to the new tunnel URL
4. On shutdown, restore the previous webhook URL

> **WARNING: This flag modifies your LayerCode agent's webhook configuration via the API. Do NOT use this with production agents—it will disrupt live traffic. Only use with dedicated development/test agents.**

---

## Logging & Observability

If `LOGFIRE_TOKEN` is defined, Logfire instrumentation is activated for FastAPI and any PydanticAI agents. Loguru handles structured console output by default.

---

## Project Structure

```
layercode-create-app/
├── src/
│   └── layercode_create_app/
│       ├── agents/          # Agent implementations
│       │   ├── prompts/     # System prompts for each agent
│       │   ├── base.py
│       │   ├── echo.py
│       │   ├── starter.py
│       │   ├── bakery.py
│       │   ├── outdoor_shop.py
│       │   └── slow_agent.py
│       ├── sdk/             # LayerCode SDK primitives
│       ├── server/          # FastAPI app and routing
│       ├── cli.py           # CLI entry point
│       ├── config.py        # Settings management
│       ├── logging.py       # Observability setup
│       └── tunnel.py        # Cloudflare tunnel launcher
├── tests/
├── .env.example
└── pyproject.toml
```

---

## Extending

1. Create a new prompt in `src/layercode_create_app/agents/prompts/`
2. Implement an agent subclass in `src/layercode_create_app/agents/` and decorate it with `@agent("name")`
3. Register custom routes or middleware by wrapping `create_app(settings, agent)`
4. Add Makefile/CLI targets as needed

---

## Development

For local development with the full repository:

```bash
# Clone and sync dependencies
git clone https://github.com/svilupp/layercode-create-app.git
cd layercode-create-app
uv sync --group dev

# Run commands
uv run layercode-create-app run --tunnel
```

### Make Targets

```bash
make format    # Format code with ruff
make lint      # Lint code with ruff
make typecheck # Type check with mypy
make test      # Run pytest tests
make check     # Run all checks (format, lint, typecheck, test)
make docs      # Install docs dependencies and serve locally
make build     # Clean dist/ and build package
make publish   # Build and publish to PyPI
```

---

## Documentation

Full documentation is available at [https://svilupp.github.io/layercode-create-app](https://svilupp.github.io/layercode-create-app)

To build and serve documentation locally:

```bash
make docs        # Install docs dependencies and serve
make docs-serve  # Serve docs at http://127.0.0.1:8000
make docs-build  # Build static site to site/
```

---

## Troubleshooting

1. **Tunnel not connecting?** Check the log file path shown when the tunnel starts. It contains full debug output from cloudflared.
2. **Webhook URL not working?** Verify the URL in your LayerCode dashboard matches exactly what's displayed in the banner.
3. **Missing environment variables?** Ensure your `.env` file contains `LAYERCODE_API_KEY`, `LAYERCODE_WEBHOOK_SECRET`, and your AI provider API key.
4. **Agent errors?** Run with `-v` flag to enable DEBUG logging: `uvx layercode-create-app run --tunnel -v`

---

## Related Projects

- **[layercode-gym](https://github.com/svilupp/layercode-gym)** - LayerCode gym for evaluating your Layercode-based agents
- **[layercode-examples](https://github.com/svilupp/layercode-examples)** - Agent patterns and integration recipes


---

## License

MIT
