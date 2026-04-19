# E-Commerce Best Products – MCP Server

An MCP (Model Context Protocol) server that exposes product search tools for **Amazon.in**, **Flipkart.com**, and **Myntra.com**.

## Architecture

```
┌────────────────────┐       SSE / Streamable HTTP
│   MCP Client       │ ──────────────────────────────▶ │ MCP Server (this repo) │
│  (Gemini Agent)    │                                  │  ├─ search_amazon       │
└────────────────────┘                                  │  ├─ search_flipkart     │
                                                        │  └─ search_myntra      │
                                                        │       ↕  Redis Cache   │
                                                        └────────────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.12+
- Poetry
- Redis (optional – the server degrades gracefully without it)

### Install & Run
```bash
poetry install
poetry run uvicorn server.main:app --reload --port 8000
```

### Docker
```bash
docker build -t mcp-server .
docker run -p 8000:8000 mcp-server
```

### Environment Variables
| Variable | Default | Description |
|---|---|---|
| `REDIS_HOST` | `localhost` | Redis hostname |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_TTL` | `3600` | Cache TTL in seconds |
| `SERVER_HOST` | `0.0.0.0` | Bind address |
| `SERVER_PORT` | `8000` | Bind port |

## MCP Tools

| Tool | Description |
|---|---|
| `search_amazon` | Searches Amazon.in – returns top-rated, lowest-price, highest-buyer products |
| `search_flipkart` | Searches Flipkart.com – same ranking criteria |
| `search_myntra` | Searches Myntra.com – same ranking criteria |

## License
MIT
