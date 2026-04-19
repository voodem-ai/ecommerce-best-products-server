"""Product search tools registered with the MCP server.

Each tool returns a list of products sorted by:
   1. Highest rating
   2. Lowest price
   3. Most buyers

Currently using mock data. Replace the `_fetch_*` helpers with
real scraper / API calls when ready.
"""

import json
from typing import Any

import structlog

from server.cache import cache_get, cache_set

log = structlog.get_logger()


# ---------------------------------------------------------------------------
# Mock data generators (replace with real API / scraper calls)
# ---------------------------------------------------------------------------

def _mock_amazon(query: str, max_price: float | None) -> list[dict[str, Any]]:
    """Generate mock Amazon product results."""
    base_price = max_price if max_price else 2999.0
    return [
        {
            "name": f"Amazon Basics {query}",
            "price": round(base_price * 0.65, 2),
            "rating": 4.8,
            "buyers": 15_420,
            "source": "amazon.in",
            "url": "https://www.amazon.in/dp/B0EXAMPLE1",
        },
        {
            "name": f"Premium {query} Pro",
            "price": round(base_price * 0.90, 2),
            "rating": 4.9,
            "buyers": 8_320,
            "source": "amazon.in",
            "url": "https://www.amazon.in/dp/B0EXAMPLE2",
        },
        {
            "name": f"Budget {query} Lite",
            "price": round(base_price * 0.40, 2),
            "rating": 4.5,
            "buyers": 22_100,
            "source": "amazon.in",
            "url": "https://www.amazon.in/dp/B0EXAMPLE3",
        },
    ]


def _mock_flipkart(query: str, max_price: float | None) -> list[dict[str, Any]]:
    """Generate mock Flipkart product results."""
    base_price = max_price if max_price else 2499.0
    return [
        {
            "name": f"Flipkart SmartBuy {query}",
            "price": round(base_price * 0.60, 2),
            "rating": 4.6,
            "buyers": 31_200,
            "source": "flipkart.com",
            "url": "https://www.flipkart.com/product/FKEXAMPLE1",
        },
        {
            "name": f"MarQ {query} Edition",
            "price": round(base_price * 0.85, 2),
            "rating": 4.7,
            "buyers": 11_050,
            "source": "flipkart.com",
            "url": "https://www.flipkart.com/product/FKEXAMPLE2",
        },
    ]


def _mock_myntra(query: str, max_price: float | None) -> list[dict[str, Any]]:
    """Generate mock Myntra product results."""
    base_price = max_price if max_price else 1999.0
    return [
        {
            "name": f"Roadster {query}",
            "price": round(base_price * 0.55, 2),
            "rating": 4.7,
            "buyers": 18_600,
            "source": "myntra.com",
            "url": "https://www.myntra.com/product/MNTEXAMPLE1",
        },
        {
            "name": f"HRX by Hrithik {query}",
            "price": round(base_price * 0.70, 2),
            "rating": 4.8,
            "buyers": 14_320,
            "source": "myntra.com",
            "url": "https://www.myntra.com/product/MNTEXAMPLE2",
        },
    ]


def _sort_products(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort by highest rating → lowest price → most buyers."""
    return sorted(products, key=lambda p: (-p["rating"], p["price"], -p["buyers"]))


# ---------------------------------------------------------------------------
# MCP Tool implementations (called by the server)
# ---------------------------------------------------------------------------

async def search_amazon(query: str, max_price: float | None = None) -> str:
    """Search Amazon.in for top-rated, budget-friendly products with the most buyers.

    Args:
        query: Product search term (e.g. "wireless earbuds").
        max_price: Optional maximum price in INR.

    Returns:
        JSON array of product objects sorted by best value.
    """
    log.info("tool.search_amazon", query=query, max_price=max_price)

    cache_key = f"amazon:{query}:{max_price}"
    cached = await cache_get(cache_key)
    if cached is not None:
        return json.dumps(cached)

    products = _sort_products(_mock_amazon(query, max_price))
    await cache_set(cache_key, products)
    return json.dumps(products)


async def search_flipkart(query: str, max_price: float | None = None) -> str:
    """Search Flipkart.com for top-rated, budget-friendly products with the most buyers.

    Args:
        query: Product search term (e.g. "mechanical keyboard").
        max_price: Optional maximum price in INR.

    Returns:
        JSON array of product objects sorted by best value.
    """
    log.info("tool.search_flipkart", query=query, max_price=max_price)

    cache_key = f"flipkart:{query}:{max_price}"
    cached = await cache_get(cache_key)
    if cached is not None:
        return json.dumps(cached)

    products = _sort_products(_mock_flipkart(query, max_price))
    await cache_set(cache_key, products)
    return json.dumps(products)


async def search_myntra(query: str, max_price: float | None = None) -> str:
    """Search Myntra.com for top-rated fashion and lifestyle products with the most buyers.

    Args:
        query: Product search term (e.g. "running shoes").
        max_price: Optional maximum price in INR.

    Returns:
        JSON array of product objects sorted by best value.
    """
    log.info("tool.search_myntra", query=query, max_price=max_price)

    cache_key = f"myntra:{query}:{max_price}"
    cached = await cache_get(cache_key)
    if cached is not None:
        return json.dumps(cached)

    products = _sort_products(_mock_myntra(query, max_price))
    await cache_set(cache_key, products)
    return json.dumps(products)
