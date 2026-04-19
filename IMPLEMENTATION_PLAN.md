# Implementation Plan – MCP Server

## Overview
Build a production-grade MCP Server that exposes product-search tools for Amazon.in, Flipkart.com, and Myntra.com via the Model Context Protocol over Streamable HTTP transport.

---

## Phase 1: Project Foundation ✅
- [x] Initialize Poetry project with `pyproject.toml`
- [x] Configure dependencies (mcp, fastapi, uvicorn, redis, structlog, python-dotenv)
- [x] Create package layout: `src/server/`
- [x] Create `Dockerfile` (two-stage build)
- [x] Create `.gitignore`, `README.md`

## Phase 2: Core Architecture ✅
- [x] `config.py` – Environment-based settings with `.env` file support via python-dotenv
- [x] `cache.py` – Redis async cache layer with graceful fallback
- [x] `tools.py` – Product search tool implementations with caching
- [x] `main.py` – FastMCP server + FastAPI mount + health endpoint

## Phase 3: Data Models & Validation ✅
- [x] `models.py` – Pydantic models for `Product`, `SearchRequest`, `SearchResponse`
- [x] Type-safe tool return values using models
- [x] Input validation on tool parameters (price > 0, query length limits)

## Phase 4: Scraper / API Integration Layer ✅
- [x] `scrapers/__init__.py` – Base scraper interface (`BaseScraper` ABC)
- [x] `scrapers/amazon.py` – Amazon product search (mock implementation)
- [x] `scrapers/flipkart.py` – Flipkart product search (mock implementation)
- [x] `scrapers/myntra.py` – Myntra product search (mock implementation)
- [ ] Feature flag to toggle between mock data and live scrapers
- [ ] Rate limiting and retry logic for live scrapers

## Phase 5: Environment & Google Access ✅
- [x] `.env.example` – Template with all environment variables
- [x] `python-dotenv` integration – Auto-loads `.env` on startup
- [x] Google Cloud config fields – `GOOGLE_APPLICATION_CREDENTIALS`, `GOOGLE_CLOUD_PROJECT`
- [x] `SKILLS.md` – Complete skills documentation

## Phase 6: Testing ✅
- [x] `tests/test_tools.py` – Unit tests for tool logic (5 tests)
- [ ] `tests/test_cache.py` – Cache hit/miss/fallback tests
- [ ] `tests/test_api.py` – Integration tests for FastAPI endpoints

## Phase 7: Deployment ✅
- [x] `docker-compose.yml` (shared across ecosystem)
- [x] Environment variable documentation in README
- [ ] CI pipeline skeleton (GitHub Actions)

---

## File Structure
```
ecommerce-best-products-server/
├── src/server/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py        ← .env loading via python-dotenv
│   ├── cache.py
│   ├── models.py
│   ├── tools.py
│   └── scrapers/
│       ├── __init__.py
│       ├── amazon.py
│       ├── flipkart.py
│       └── myntra.py
├── tests/
│   ├── __init__.py
│   └── test_tools.py
├── .env.example         ← NEW: env template
├── SKILLS.md            ← NEW: skills documentation
├── IMPLEMENTATION_PLAN.md
├── pyproject.toml
├── Dockerfile
├── .gitignore
└── README.md
```
