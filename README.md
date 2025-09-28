## Omni Agent — Deep Research Orchestrator

Omni Agent is a modular, production-ready research agent that performs end‑to‑end deep research: analysis, strategy formation, parallelized web research, and evidence‑driven synthesis. It exposes an HTTP agent API, a scraping microservice powered by Playwright, and an MCP server to integrate into compatible clients.

### Highlights

- Orchestrated multi‑stage pipeline: Analysis → Research → Synthesis
- Playwright scraping via Lightpanda remote browser/CDP
- Clean API surface: FastAPI microservice for scraping, ADK tool exposure, MCP stdio server
- Dockerized with `uv` for fast, reproducible Python 3.13 environments

---

## Technologies Used

### Primary technologies (called out explicitly)

- **OpenAI**: Accessed via LiteLLM with model IDs like `openai/gpt-5-nano-2025-08-07` and `openai/gpt-5-mini-2025-08-07`.
- **Playwright**: Headless browser automation for web scraping, connected to Lightpanda over CDP.

### Other frameworks, libraries, and tools

- **Google ADK** (`google-adk`): Agent framework used for orchestration and tool exposure
- **A2A / a2a-sdk**: Agent runtime and HTTP server integration
- **FastAPI** and **Uvicorn**: HTTP API for the scraping microservice
- **LiteLLM**: Unified LLM client (OpenAI, Groq, and others)
- **Groq SDK**: Optional LLM provider integration
- **MCP (Model Context Protocol)**: Stdio server to expose the ADK tool to MCP clients
- **structlog**: Structured logging
- **Pydantic / pydantic-settings / python-dotenv**: Typed settings and `.env` loading
- **Docker** and **Docker Compose**: Containerized local development and deployment
- **Astral UV**: Fast Python package manager used in Docker builds

---

## Repository layout

```
omni_agent/
  agent.py                         # Root agent entry
  adk_mcp_server.py                # MCP stdio server exposing ADK tool
  playwright_lightpanda_service.py # FastAPI scraping service
  agents/                          # Analysis, research, synthesis agents
  core/                            # Settings, logging, models
Dockerfile
docker-compose.yml
pyproject.toml
LICENSE
```

Key orchestrator composition is defined in `omni_agent/agents/deep_research_orchestrator.py` and wired as `root_agent` in `omni_agent/agent.py`.

---

## Architecture

The pipeline is built with `google.adk.agents.SequentialAgent`:

- **Stage 1 — Analysis & Strategy**: `claim_structuring_agent` → `gap_identification_agent`
- **Stage 2 — Research (parallelized)**: `research_orchestrator_agent`
- **Stage 3 — Synthesis & Verification**: `evidence_adjudicator_agent`

Scraping is offloaded to a lightweight FastAPI service backed by **Playwright** connected over CDP to **Lightpanda** for reliable, headless browsing at scale.

An **MCP stdio server** (`omni_agent/adk_mcp_server.py`) exposes the ADK tool so MCP‑compatible clients can discover and call the agent via stdio.

---

## Requirements

- Python ≥ 3.13 (project targets `py313`)
- Docker and Docker Compose (recommended for quickest start)
- A `.env` file with required tokens/keys (see below)

---

## Configuration (.env)

The application reads settings via `pydantic-settings` and `dotenv`. Create a `.env` at the repository root with the following keys as needed:

```
# LLM providers
OPENAI_API_KEY=sk-...            # Required if using OpenAI via LiteLLM
GROQ_API_KEY=...                 # Optional, enable Groq via LiteLLM

# Web scraping / Lightpanda (required for scraping)
LIGHTPANDA_TOKEN=...             # Required to connect to Lightpanda
LIGHTPANDA_WS_BASE=wss://cloud.lightpanda.io/ws  # Default OK

# External scraping helper
SCRAPE_DO_TOKEN=...              # Optional scrape.do key if used elsewhere

# App knobs (optional overrides)
APP_NAME=Omni Agent
DEBUG=false
LOG_LEVEL=INFO
DEFAULT_TIMEOUT=60.0
MAX_RETRIES=3
MAX_CONTENT_LENGTH=10000
```

All of the above map to fields in `omni_agent/core/settings.py` and can be overridden via environment variables.

---

## Quickstart

### Option A — Docker Compose (recommended)

1. Create `.env` as described above.
2. Start services:

```bash
docker compose up -d
```

This will start:

- `omni-agent` on `http://localhost:8001` (ADK agent API server)
- `playwright-lightpanda` on `http://localhost:8003` (scraping service)

3. Verify the scraping API:

```bash
curl -X POST http://localhost:8003/scrape \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com"]}'
```

### Option B — Local dev with UV

Ensure Python 3.13 is active, then install:

```bash
uv sync
```

Run the ADK agent API server (hot‑reload):

```bash
uv run adk web --port 8001 --host 0.0.0.0 --a2a --reload
```

Run the Playwright scraping service:

```bash
uv run uvicorn omni_agent.playwright_lightpanda_service:app --host 0.0.0.0 --port 8003 --reload
```

Run the MCP stdio server that exposes the ADK tool:

```bash
uv run python omni_agent.adk_mcp_server
```

---

## HTTP APIs

### Scraping Service (FastAPI)

- **Endpoint**: `POST /scrape`
- **Body**:

```json
{ "urls": ["https://example.com", "https://news.ycombinator.com/"] }
```

- **Response**:

```json
{
  "status": "success",
  "combined_content": "# Content from https://example.com\n..."
}
```

Notes:

- Requires `LIGHTPANDA_TOKEN` set in the environment.
- The service connects to Lightpanda via CDP using Playwright for robust page loads.

### ADK Agent API

The ADK runner (`adk web`/`adk api_server`) exposes the `root_agent` defined in `omni_agent/agent.py` (wired to `DeepResearchOrchestrator`). Refer to Google ADK docs for available HTTP routes in the chosen runner mode.

---

## Development

### Code style & tooling

This repo uses `ruff` and `mypy` (configured for `py313`). Common commands:

```bash
uv run ruff format .
uv run ruff check --fix .
uv run mypy .
```

### Project decisions

- Sequential/parallel agent composition is explicit in `omni_agent/agents/deep_research_orchestrator.py`.
- Settings are centralized in `omni_agent/core/settings.py` and loaded from `.env`.
- Playwright scraping is separated as a microservice for performance and isolation.

---

## License

Licensed under the terms of the LICENSE file included in this repository.

---

## Acknowledgements

- Google ADK and A2A
- Playwright team & Lightpanda
- LiteLLM and Groq
- FastAPI & Uvicorn
- Structlog, Pydantic, and Astral UV
