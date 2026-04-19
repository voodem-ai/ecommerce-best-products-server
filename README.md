# E-Commerce Best Products – MCP Server

An MCP (Model Context Protocol) server that exposes product search tools for **Amazon.in**, **Flipkart.com**, and **Myntra.com**. Products are ranked by **top-rated → lowest price → most buyers**.

## Architecture

```
┌────────────────────┐    Streamable HTTP / SSE     ┌─────────────────────────────┐
│   MCP Client       │ ──────────────────────────▶  │  MCP Server (this repo)     │
│  (Gemini Agent)    │                              │   ├─ search_amazon           │
└────────────────────┘                              │   ├─ search_flipkart         │
                                                    │   ├─ search_myntra           │
                                                    │   └─ Redis Cache ↕           │
                                                    └─────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| Build Tool | Poetry |
| MCP | FastMCP (official Python SDK) |
| Web Framework | FastAPI + Uvicorn |
| Data Models | Pydantic v2 |
| Caching | Redis (async, graceful fallback) |
| Scraping | Gemini AI + Google Search grounding (`google-genai`) with mock fallback |
| Logging | structlog (structured JSON) |
| Config | python-dotenv + environment variables |
| Container | Docker (multi-stage) |

## Quick Start

### 1. Clone & Configure
```bash
git clone https://github.com/voodem-ai/ecommerce-best-products-server.git
cd ecommerce-best-products-server
cp .env.example .env
# Edit .env with your values
```

### 2. Install & Run
```bash
poetry install
poetry run uvicorn server.main:app --reload --port 8000
```

### 3. Docker
```bash
docker build -t mcp-server .
docker run -p 8000:8000 --env-file .env mcp-server
```

## Environment Variables (`.env`)

| Variable | Default | Required | Description |
|---|---|---|---|
| `SCRAPER_MODE` | `gemini` | No | `gemini` (real) or `mock` (fake data) |
| `GEMINI_API_KEY` | – | **Yes** (if mode is gemini)| Gemini API key for search grounding |
| `REDIS_HOST` | `localhost` | No | Redis hostname |
| `REDIS_PORT` | `6379` | No | Redis port |
| `REDIS_TTL` | `3600` | No | Cache TTL (seconds) |
| `SERVER_HOST` | `0.0.0.0` | No | Bind address |
| `SERVER_PORT` | `8000` | No | Bind port |
| `GOOGLE_APPLICATION_CREDENTIALS` | – | No | GCP service account JSON (for Vertex AI) |
| `GOOGLE_CLOUD_PROJECT` | – | No | GCP project ID (for Vertex AI) |

## MCP Tools

| Tool | Description | Parameters |
|---|---|---|
| `search_amazon` | Search Amazon.in | `query` (str), `max_price` (float, optional) |
| `search_flipkart` | Search Flipkart.com | `query` (str), `max_price` (float, optional) |
| `search_myntra` | Search Myntra.com | `query` (str), `max_price` (float, optional) |

Each tool returns a JSON array of products sorted by: **rating (desc) → price (asc) → buyers (desc)**.

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness probe |
| * | `/mcp/*` | MCP Streamable HTTP transport |

## Project Structure

```
src/server/
├── __init__.py
├── main.py          # FastAPI + MCP entry point
├── config.py        # .env + environment settings
├── cache.py         # Redis async cache layer
├── models.py        # Pydantic data models
├── tools.py         # MCP tool implementations
└── scrapers/
    ├── __init__.py      # BaseScraper ABC
    ├── gemini_scraper.py# Real scraper using Google Search grounding
    ├── amazon.py        # Amazon scraper (mock fallback)
    ├── flipkart.py      # Flipkart scraper (mock fallback)
    └── myntra.py        # Myntra scraper (mock fallback)
```

## Testing

```bash
poetry run pytest tests/ -v
```

## License
MIT
