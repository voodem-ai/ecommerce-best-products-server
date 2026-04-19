"""Product search tools registered with the MCP server.

Each tool delegates to a scraper (Gemini-powered or mock) and caches results.
Products are ranked by: highest rating → lowest price → most buyers.

Scraper mode is controlled by SCRAPER_MODE env var:
  - "gemini" → Real products via Gemini + Google Search grounding
  - "mock"   → Fake data for development (no API key needed)
"""

import json

import structlog

from server.cache import cache_get, cache_set
from server.config import settings
from server.models import Product
from server.scrapers import BaseScraper

log = structlog.get_logger()


def _create_scraper(source: str) -> BaseScraper:
    """Factory: create the right scraper based on SCRAPER_MODE config."""
    if settings.SCRAPER_MODE == "gemini":
        from server.scrapers.gemini_scraper import (
            GeminiAmazonScraper,
            GeminiFlipkartScraper,
            GeminiMyntraScraper,
        )
        scrapers = {
            "amazon": GeminiAmazonScraper(),
            "flipkart": GeminiFlipkartScraper(),
            "myntra": GeminiMyntraScraper(),
        }
    else:
        from server.scrapers.amazon import AmazonScraper
        from server.scrapers.flipkart import FlipkartScraper
        from server.scrapers.myntra import MyntraScraper
        scrapers = {
            "amazon": AmazonScraper(),
            "flipkart": FlipkartScraper(),
            "myntra": MyntraScraper(),
        }

    return scrapers[source]


# Lazy-init scrapers (created on first use)
_scrapers: dict[str, BaseScraper] = {}


def _get_scraper(source: str) -> BaseScraper:
    """Get or create a scraper for the given source."""
    if source not in _scrapers:
        _scrapers[source] = _create_scraper(source)
        log.info(
            "scraper_initialized",
            source=source,
            mode=settings.SCRAPER_MODE,
            type=type(_scrapers[source]).__name__,
        )
    return _scrapers[source]


def _products_to_json(products: list[Product]) -> str:
    """Serialise a list of Product models to a JSON string."""
    return json.dumps([p.model_dump() for p in products], indent=2)


async def search_amazon(query: str, max_price: float | None = None) -> str:
    """Search Amazon.in for top-rated, budget-friendly products with the most buyers.

    Uses Gemini AI with Google Search grounding to find real products
    from Amazon.in, ranked by rating, price, and buyer count.

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

    scraper = _get_scraper("amazon")
    products = await scraper.search(query, max_price)
    await cache_set(cache_key, [p.model_dump() for p in products])
    return _products_to_json(products)


async def search_flipkart(query: str, max_price: float | None = None) -> str:
    """Search Flipkart.com for top-rated, budget-friendly products with the most buyers.

    Uses Gemini AI with Google Search grounding to find real products
    from Flipkart.com, ranked by rating, price, and buyer count.

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

    scraper = _get_scraper("flipkart")
    products = await scraper.search(query, max_price)
    await cache_set(cache_key, [p.model_dump() for p in products])
    return _products_to_json(products)


async def search_myntra(query: str, max_price: float | None = None) -> str:
    """Search Myntra.com for top-rated fashion and lifestyle products with the most buyers.

    Uses Gemini AI with Google Search grounding to find real products
    from Myntra.com, ranked by rating, price, and buyer count.

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

    scraper = _get_scraper("myntra")
    products = await scraper.search(query, max_price)
    await cache_set(cache_key, [p.model_dump() for p in products])
    return _products_to_json(products)
