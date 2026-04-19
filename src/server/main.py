"""FastAPI + MCP Server entry-point.

Starts an MCP server over SSE transport, exposing three product search
tools: search_amazon, search_flipkart, search_myntra.
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

from server.cache import close_redis
from server.config import settings
from server import tools  # noqa: F401 – registers tools

log = structlog.get_logger()

# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "ecommerce-products-server",
    instructions=(
        "You are an e-commerce product search assistant. "
        "Use the available tools to find top-rated, "
        "budget-friendly products with the most buyers "
        "across Amazon, Flipkart, and Myntra."
    ),
)


# Register tools with the MCP server
@mcp.tool()
async def search_amazon(query: str, max_price: float | None = None) -> str:
    """Search Amazon.in for top-rated, budget-friendly products with the most buyers.

    Args:
        query: Product search term (e.g. "wireless earbuds").
        max_price: Optional maximum price in INR.
    """
    return await tools.search_amazon(query, max_price)


@mcp.tool()
async def search_flipkart(query: str, max_price: float | None = None) -> str:
    """Search Flipkart.com for top-rated, budget-friendly products with the most buyers.

    Args:
        query: Product search term (e.g. "mechanical keyboard").
        max_price: Optional maximum price in INR.
    """
    return await tools.search_flipkart(query, max_price)


@mcp.tool()
async def search_myntra(query: str, max_price: float | None = None) -> str:
    """Search Myntra.com for top-rated fashion and lifestyle products with the most buyers.

    Args:
        query: Product search term (e.g. "running shoes").
        max_price: Optional maximum price in INR.
    """
    return await tools.search_myntra(query, max_price)


# ---------------------------------------------------------------------------
# FastAPI wrapper (provides health-check + hosts the MCP SSE transport)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(application: FastAPI):
    """Application startup / shutdown hooks."""
    log.info("server_starting", host=settings.SERVER_HOST, port=settings.SERVER_PORT)
    yield
    await close_redis()
    log.info("server_stopped")


app = FastAPI(
    title="E-Commerce Best Products – MCP Server",
    version="0.1.0",
    lifespan=lifespan,
)

# Mount the MCP SSE transport under the FastAPI app
app.mount("/mcp", mcp.sse_app())


@app.get("/health")
async def health():
    """Simple liveness probe."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Run directly: python -m server.main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True,
    )
