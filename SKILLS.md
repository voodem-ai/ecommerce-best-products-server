# Skills – MCP Server

Technical skills and competencies required to develop, maintain, and extend this project.

---

## Core Skills

### Python Development
- **Python 3.12+** – Modern Python with type hints, union types (`X | None`), and async/await
- **Poetry** – Dependency management, virtual environments, build system
- **Pydantic v2** – Data validation, serialization, and settings management

### MCP (Model Context Protocol)
- **FastMCP SDK** – Tool registration, schema generation, and server lifecycle
- **Streamable HTTP Transport** – Exposing MCP tools over HTTP/SSE for remote clients
- **Tool Design** – Writing descriptive tool schemas that LLMs can reliably invoke

### Web Framework
- **FastAPI** – REST API design, dependency injection, middleware, lifespan events
- **Uvicorn** – ASGI server configuration, worker management
- **SSE (Server-Sent Events)** – Real-time streaming protocol for MCP communication

### Caching
- **Redis** – Async client (`redis.asyncio`), key design, TTL-based expiration
- **Cache-aside pattern** – Check cache → miss → compute → store → return
- **Graceful degradation** – App continues to work when Redis is unavailable

### Web Scraping (Future)
- **httpx** – Async HTTP client for API calls
- **BeautifulSoup4** – HTML parsing and data extraction
- **Rate limiting & Retry** – Polite scraping with exponential backoff

---

## Google & Cloud Skills

### Google Cloud Platform (Future)
- **Service Account Authentication** – `GOOGLE_APPLICATION_CREDENTIALS` for GCP services
- **GCP Project Configuration** – `GOOGLE_CLOUD_PROJECT` environment binding

### Environment Configuration
- **python-dotenv** – Loading `.env` files for local development
- **12-Factor App** – Configuration via environment variables

---

## DevOps & Infrastructure

### Docker
- **Multi-stage builds** – Separate builder and runtime stages for smaller images
- **Poetry in Docker** – Installing Poetry, caching dependency layers
- **Health checks** – Liveness/readiness probes

### Docker Compose
- **Service orchestration** – Multi-container setup with dependencies
- **Health check conditions** – `condition: service_healthy`
- **Volume management** – Persistent Redis data

### Version Control
- **Git** – Branching, committing, pushing
- **GitHub** – Organization repositories, CI/CD (future)

---

## Testing

- **pytest** – Test runner and fixtures
- **pytest-asyncio** – Testing async functions
- **unittest.mock** – `AsyncMock`, `patch` for isolating dependencies
- **Test patterns** – Unit tests for tools, cache, and API integration

---

## Architecture Patterns

| Pattern | Usage |
|---|---|
| **Strategy Pattern** | `BaseScraper` ABC with `AmazonScraper`, `FlipkartScraper`, `MyntraScraper` |
| **Cache-Aside** | Check Redis → compute on miss → store result |
| **Singleton** | Global scraper and Redis connection instances |
| **Dependency Injection** | FastAPI lifespan for resource management |
| **12-Factor Config** | All config via env vars + `.env` file |
