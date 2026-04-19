"""Tests for product search tools."""

import json
import pytest
from unittest.mock import AsyncMock, patch

from server.tools import search_amazon, search_flipkart, search_myntra


@pytest.mark.asyncio
async def test_search_amazon_returns_valid_json():
    """search_amazon should return a valid JSON array of products."""
    with patch("server.tools.cache_get", new_callable=AsyncMock, return_value=None), \
         patch("server.tools.cache_set", new_callable=AsyncMock):
        result = await search_amazon("wireless earbuds", max_price=2000)
        products = json.loads(result)

        assert isinstance(products, list)
        assert len(products) > 0
        for p in products:
            assert "name" in p
            assert "price" in p
            assert "rating" in p
            assert "buyers" in p
            assert p["source"] == "amazon.in"
            assert p["price"] <= 2000


@pytest.mark.asyncio
async def test_search_flipkart_returns_valid_json():
    """search_flipkart should return a valid JSON array of products."""
    with patch("server.tools.cache_get", new_callable=AsyncMock, return_value=None), \
         patch("server.tools.cache_set", new_callable=AsyncMock):
        result = await search_flipkart("laptop stand")
        products = json.loads(result)

        assert isinstance(products, list)
        assert len(products) > 0
        for p in products:
            assert p["source"] == "flipkart.com"


@pytest.mark.asyncio
async def test_search_myntra_returns_valid_json():
    """search_myntra should return a valid JSON array of products."""
    with patch("server.tools.cache_get", new_callable=AsyncMock, return_value=None), \
         patch("server.tools.cache_set", new_callable=AsyncMock):
        result = await search_myntra("running shoes", max_price=3000)
        products = json.loads(result)

        assert isinstance(products, list)
        assert len(products) > 0
        for p in products:
            assert p["source"] == "myntra.com"


@pytest.mark.asyncio
async def test_products_sorted_by_rating_desc():
    """Products should be sorted by rating descending."""
    with patch("server.tools.cache_get", new_callable=AsyncMock, return_value=None), \
         patch("server.tools.cache_set", new_callable=AsyncMock):
        result = await search_amazon("headphones")
        products = json.loads(result)

        ratings = [p["rating"] for p in products]
        assert ratings == sorted(ratings, reverse=True)


@pytest.mark.asyncio
async def test_cache_hit_skips_scraper():
    """When cache has data, scraper should not be called."""
    cached_data = [{"name": "Cached Product", "price": 100, "rating": 5.0,
                     "buyers": 999, "source": "amazon.in", "url": "http://example.com"}]

    with patch("server.tools.cache_get", new_callable=AsyncMock, return_value=cached_data):
        result = await search_amazon("test")
        products = json.loads(result)
        assert products[0]["name"] == "Cached Product"
