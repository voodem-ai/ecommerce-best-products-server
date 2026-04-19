"""Product search tools registered with the MCP server.

Each tool delegates to a scraper and caches results.
Products are ranked by: highest rating → lowest price → most buyers.
"""

import json

import structlog

from server.cache import cache_get, cache_set
from server.models import Product
from server.scrapers.amazon import AmazonScraper
from server.scrapers.flipkart import FlipkartScraper
from server.scrapers.myntra import MyntraScraper

log = structlog.get_logger()

# Scraper singletons
_amazon = AmazonScraper()
_flipkart = FlipkartScraper()
_myntra = MyntraScraper()


def _products_to_json(products: list[Product]) -> str:
    """Serialise a list of Product models to a JSON string."""
    return json.dumps([p.model_dump() for p in products], indent=2)


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

    products = await _amazon.search(query, max_price)
    await cache_set(cache_key, [p.model_dump() for p in products])
    return _products_to_json(products)


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

    products = await _flipkart.search(query, max_price)
    await cache_set(cache_key, [p.model_dump() for p in products])
    return _products_to_json(products)


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

    products = await _myntra.search(query, max_price)
    await cache_set(cache_key, [p.model_dump() for p in products])
    return _products_to_json(products)
