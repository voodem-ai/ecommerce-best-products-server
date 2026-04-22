# Implementation Plan – MCP Server

## Overview
Build a production-grade MCP Server that exposes product-search tools for Amazon.in, Flipkart.com, and Myntra.com via the Model Context Protocol over **SSE transport**. Products are sourced in real-time using Gemini AI + Google Search grounding.

---

## Phase 1: Project Foundation ✅
- [x] Initialize Poetry project with `pyproject.toml`
- [x] Configure dependencies (mcp, fastapi, uvicorn, redis, structlog, python-dotenv, google-genai)
- [x] Create package layout: `src/server/`
- [x] Create `Dockerfile` (two-stage build)
- [x] Create `.gitignore`, `README.md`

## Phase 2: Core Architecture ✅
- [x] `config.py` – Environment-based settings with `.env` file support via python-dotenv
- [x] `cache.py` – Redis async cache layer with graceful no-Redis fallback
- [x] `tools.py` – Product search tools with scraper factory (`SCRAPER_MODE` toggle) and caching
- [x] `main.py` – FastMCP server mounted via `mcp.sse_app()` on FastAPI at `/mcp`
- [x] Health endpoint at `/health`

## Phase 3: Data Models & Validation ✅
- [x] `models.py` – Pydantic models for `Product`, `SearchRequest`, `SearchResponse`
- [x] Type-safe tool return values (JSON-serialised product lists)
- [x] Input validation on tool parameters (price > 0, query length limits)

## Phase 4: Scraper / API Integration Layer ✅
- [x] `scrapers/__init__.py` – `BaseScraper` ABC with `search()` and `sort_products()` contracts
- [x] `scrapers/gemini_scraper.py` – Real-time Gemini + Google Search grounding scraper
  - [x] Natural-language queries (not fragile `site:` filters) for reliable product discovery
  - [x] Blocking Gemini API calls offloaded to `asyncio.run_in_executor` for true parallelism
  - [x] 3-stage JSON extraction: direct parse → strip markdown fences → regex `\[.*\]` fallback
  - [x] Robust price/string cleaning (handles `"₹1,999"` → `1999.0`)
  - [x] Per-retailer classes: `GeminiAmazonScraper`, `GeminiFlipkartScraper`, `GeminiMyntraScraper`
- [x] `scrapers/amazon.py` – Mock fallback scraper
- [x] `scrapers/flipkart.py` – Mock fallback scraper
- [x] `scrapers/myntra.py` – Mock fallback scraper
- [x] `SCRAPER_MODE=gemini|mock` feature flag

## Phase 5: MCP Transport & Connectivity ✅
- [x] SSE transport mounted at `/mcp` using `mcp.sse_app()` (exposes `/mcp/sse` + `/mcp/messages`)
- [x] Fixed mount from `streamable_http_app()` → `sse_app()` to resolve 404 errors on client connection
- [x] Verified SSE stream returns `event: endpoint` with session URL correctly
- [x] Tools registered: `search_amazon`, `search_flipkart`, `search_myntra`

## Phase 6: Environment & Google Access ✅
- [x] `.env.example` – Template with all environment variables documented
- [x] `GEMINI_API_KEY` prioritised over Vertex AI to avoid GCP billing conflicts
- [x] `GOOGLE_CLOUD_PROJECT` / `GOOGLE_APPLICATION_CREDENTIALS` – optional Vertex AI support
- [x] `SKILLS.md` – Skills documentation

## Phase 7: Testing ✅
- [x] `tests/test_tools.py` – Unit tests for tool logic (5 tests)
- [ ] `tests/test_cache.py` – Cache hit/miss/fallback tests
- [ ] `tests/test_api.py` – Integration tests for FastAPI endpoints

## Phase 8: Deployment ✅
- [x] `docker-compose.yml` (shared across ecosystem)
- [x] Environment variable documentation in README
- [x] GitHub Actions CI pipeline with Helm deployment (`helm/ecommerce-server/`)
- [x] Internal Networking (ClusterIP) to ensure the server is isolated from public internet

---

## File Structure
```
ecommerce-best-products-server/
├── src/server/
│   ├── __init__.py
│   ├── main.py              ← FastAPI + FastMCP (sse_app mount)
│   ├── config.py            ← .env loading via python-dotenv
│   ├── cache.py             ← Redis with graceful fallback
│   ├── models.py            ← Pydantic data models
│   ├── tools.py             ← MCP tool implementations
│   └── scrapers/
│       ├── __init__.py      ← BaseScraper ABC
│       ├── gemini_scraper.py← Gemini Google Search grounding (real data)
│       ├── amazon.py        ← Mock fallback
│       ├── flipkart.py      ← Mock fallback
│       └── myntra.py        ← Mock fallback
├── tests/
│   ├── __init__.py
│   └── test_tools.py
├── helm/
│   └── ecommerce-server/    ← Helm chart deployment files
├── .env                     ← Local config (not committed)
├── .env.example             ← Template
├── SKILLS.md
├── IMPLEMENTATION_PLAN.md
├── pyproject.toml
├── Dockerfile
├── .gitignore
└── README.md
```
