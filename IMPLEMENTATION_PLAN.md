# Implementation Plan – MCP Server

## Overview
Build a production-grade MCP Server that exposes product-search tools for Amazon.in, Flipkart.com, and Myntra.com via the Model Context Protocol over Streamable HTTP transport.

---

## Phase 1: Project Foundation ✅
- [x] Initialize Poetry project with `pyproject.toml`
- [x] Configure dependencies (mcp, fastapi, uvicorn, redis, structlog)
- [x] Create package layout: `src/server/`
- [x] Create `Dockerfile` (two-stage build)
- [x] Create `.gitignore`, `README.md`

## Phase 2: Core Architecture
- [x] `config.py` – Environment-based settings (Redis, host, port)
- [x] `cache.py` – Redis async cache layer with graceful fallback
- [x] `tools.py` – Product search tool implementations with caching
- [x] `main.py` – FastMCP server + FastAPI mount + health endpoint

## Phase 3: Data Models & Validation
- [ ] `models.py` – Pydantic models for `Product`, `SearchRequest`, `SearchResponse`
- [ ] Type-safe tool return values using models
- [ ] Input validation on tool parameters (price > 0, query length limits)

## Phase 4: Scraper / API Integration Layer
- [ ] `scrapers/__init__.py` – Base scraper interface
- [ ] `scrapers/amazon.py` – Amazon product search (httpx + BeautifulSoup)
- [ ] `scrapers/flipkart.py` – Flipkart product search
- [ ] `scrapers/myntra.py` – Myntra product search
- [ ] Feature flag to toggle between mock data and live scrapers
- [ ] Rate limiting and retry logic

## Phase 5: Observability & Resilience
- [ ] Structured logging with `structlog` (JSON output for production)
- [ ] `/health` and `/ready` endpoints
- [ ] Graceful Redis disconnection handling (already started)
- [ ] Request correlation IDs

## Phase 6: Testing
- [ ] `tests/test_tools.py` – Unit tests for tool logic
- [ ] `tests/test_cache.py` – Cache hit/miss/fallback tests
- [ ] `tests/test_api.py` – Integration tests for FastAPI endpoints

## Phase 7: Deployment
- [ ] `docker-compose.yml` (shared across ecosystem)
- [ ] Environment variable documentation
- [ ] CI pipeline skeleton (GitHub Actions)

---

## File Structure (Target)
```
ecommerce-best-products-server/
├── src/
│   └── server/
│       ├── __init__.py
│       ├── main.py          # FastAPI + MCP entry point
│       ├── config.py         # Environment settings
│       ├── cache.py          # Redis cache layer
│       ├── models.py         # Pydantic data models
│       ├── tools.py          # MCP tool implementations
│       └── scrapers/
│           ├── __init__.py   # Base scraper protocol
│           ├── amazon.py
│           ├── flipkart.py
│           └── myntra.py
├── tests/
│   ├── __init__.py
│   ├── test_tools.py
│   ├── test_cache.py
│   └── test_api.py
├── pyproject.toml
├── Dockerfile
├── .gitignore
└── README.md
```
