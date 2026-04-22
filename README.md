# E-Commerce Best Products – MCP Server

An MCP (Model Context Protocol) server that exposes product search tools for **Amazon.in**, **Flipkart.com**, and **Myntra.com**. Products are sourced in real-time using **Gemini AI + Google Search grounding** and ranked by **top-rated → lowest price → most buyers**.

---

## Architecture

### High-Level System Flow
```
React UI (port 3000)
     │  POST /recommend {"prompt": "..."}
     ▼
MCP Client (port 8001)  ──SSE──▶  MCP Server (port 8000)
     │                                     │
     │  Gemini Agentic Loop                │  Gemini Scraper
     │  (google-genai SDK)                 │  (google-genai + Google Search)
     └─────────────────────────────────────┘
```

### Low-Level Request Flow (Server)

```
Incoming MCP Tool Call: search_amazon(query, max_price)
         │
         ▼
  tools.py :: search_amazon()
         │
         ├──► cache.py :: cache_get("amazon:{query}:{price}")
         │         └─► Redis HIT → return cached JSON immediately
         │
         ▼ (cache miss)
  tools.py :: _get_scraper("amazon")
         │
         ├─► SCRAPER_MODE == "gemini"
         │         └─► GeminiAmazonScraper (gemini_scraper.py)
         │                    │
         │                    ▼
         │         asyncio.run_in_executor(None, _sync_search)
         │                    │  (offloaded to thread pool - non-blocking)
         │                    │
         │                    ▼
         │         Gemini API: generate_content()
         │           model: gemini-2.5-flash
         │           tool:  GoogleSearch (grounding)
         │           prompt: "Find top 5 '{query}' on Amazon India..."
         │                    │
         │                    ▼
         │         Google Search (grounded)
         │           Searches: "{query} Amazon India"
         │           Reads product listings, review pages, comparison sites
         │                    │
         │                    ▼
         │         Gemini returns raw text with product data
         │                    │
         │         _extract_json() [3-stage fallback]
         │           Stage 1: json.loads(raw_text)
         │           Stage 2: strip ```json fences, then json.loads()
         │           Stage 3: regex \[.*\] extraction, then json.loads()
         │                    │
         │                    ▼
         │         _parse_products() → list[Product]
         │           Cleans "₹1,999" → 1999.0
         │           Validates rating 0-5, buyers as int
         │           Falls back to defaults if fields missing
         │
         ├─► SCRAPER_MODE == "mock"
         │         └─► AmazonScraper (deterministic fake data)
         │
         ▼
  sort_products() → sorted by: rating DESC, price ASC, buyers DESC
         │
         ▼
  cache.py :: cache_set("amazon:{query}:{price}", products, TTL=3600s)
         │
         ▼
  Return JSON string to MCP Client
```

### MCP SSE Transport Internals
```
FastAPI app (uvicorn, port 8000)
  │
  ├── GET  /health          → {"status": "ok", "scraper_mode": "gemini"}
  │
  └── /mcp  ← FastMCP mounted via mcp.sse_app()
        │
        ├── GET  /mcp/sse      → Opens SSE stream, sends session endpoint URL
        │                        event: endpoint
        │                        data: /mcp/messages/?session_id=<uuid>
        │
        └── POST /mcp/messages → Receives JSON-RPC 2.0 messages
              Handles: initialize, tools/list, tools/call
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| Build Tool | Poetry |
| MCP | FastMCP (official Python SDK) |
| MCP Transport | SSE (`mcp.sse_app()`) |
| Web Framework | FastAPI + Uvicorn |
| Data Models | Pydantic v2 |
| Caching | Redis (async, graceful no-Redis fallback) |
| Scraping | Gemini AI + Google Search grounding (`google-genai`) with mock fallback |
| Logging | structlog (structured JSON) |
| Config | python-dotenv + environment variables |
| Container | Docker (multi-stage) |
| Deployment | Helm chart with internal ClusterIP Service |

---

## Quick Start

### 1. Clone & Configure
```bash
git clone https://github.com/voodem-ai/ecommerce-best-products-server.git
cd ecommerce-best-products-server
cp .env.example .env
# Edit .env: set GEMINI_API_KEY and SCRAPER_MODE=gemini
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

---

## Environment Variables (`.env`)

| Variable | Default | Required | Description |
|---|---|---|---|
| `SCRAPER_MODE` | `gemini` | No | `gemini` (real) or `mock` (fake data) |
| `GEMINI_API_KEY` | – | **Yes** (if mode is gemini) | Google AI Studio API key |
| `GEMINI_MODEL` | `gemini-2.5-flash` | No | Gemini model ID |
| `REDIS_HOST` | `localhost` | No | Redis hostname |
| `REDIS_PORT` | `6379` | No | Redis port |
| `REDIS_TTL` | `3600` | No | Cache TTL in seconds |
| `SERVER_HOST` | `0.0.0.0` | No | Bind address |
| `SERVER_PORT` | `8000` | No | Bind port |
| `GOOGLE_APPLICATION_CREDENTIALS` | – | No | GCP service account JSON (Vertex AI only) |
| `GOOGLE_CLOUD_PROJECT` | – | No | GCP project ID (Vertex AI only) |

> **Note:** `GEMINI_API_KEY` is always used if present. Vertex AI is a fallback only when no API key is set.

---

## MCP Tools

| Tool | Description | Parameters |
|---|---|---|
| `search_amazon` | Search Amazon.in | `query` (str), `max_price` (float, optional) |
| `search_flipkart` | Search Flipkart.com | `query` (str), `max_price` (float, optional) |
| `search_myntra` | Search Myntra.com | `query` (str), `max_price` (float, optional) |

Each tool returns a JSON array of products sorted by: **rating (desc) → price (asc) → buyers (desc)**.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness probe |
| GET | `/mcp/sse` | MCP Server-Sent Events stream connection |
| POST | `/mcp/messages` | MCP JSON-RPC 2.0 messages endpoint |

---

## Project Structure

```
src/server/
├── __init__.py
├── main.py              # FastAPI + FastMCP entry point (sse_app mount)
├── config.py            # .env + environment settings
├── cache.py             # Redis async cache with graceful fallback
├── models.py            # Pydantic data models
├── tools.py             # MCP tool implementations + scraper factory
└── scrapers/
    ├── __init__.py      # BaseScraper ABC
    ├── gemini_scraper.py# Real-time Gemini Google Search scraper
    ├── amazon.py        # Mock fallback scraper
    ├── flipkart.py      # Mock fallback scraper
    └── myntra.py        # Mock fallback scraper
helm/
└── ecommerce-server/    # Helm chart deployment files
```

---

## Testing

```bash
poetry run pytest tests/ -v
```

## License
MIT
