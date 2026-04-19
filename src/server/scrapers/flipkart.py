"""Flipkart.com product scraper (mock implementation)."""

import random

import structlog

from server.models import Product
from server.scrapers import BaseScraper

log = structlog.get_logger()

_FLIPKART_TEMPLATES = [
    {"prefix": "Flipkart SmartBuy", "rating_range": (4.2, 4.8), "buyers_range": (12000, 55000)},
    {"prefix": "MarQ by Flipkart", "suffix": "Edition", "rating_range": (4.4, 4.9), "buyers_range": (5000, 20000)},
    {"prefix": "Perfect Homes", "suffix": "Ultra", "rating_range": (4.0, 4.5), "buyers_range": (20000, 70000)},
    {"prefix": "SmartBuy", "suffix": "Essential", "rating_range": (4.3, 4.7), "buyers_range": (8000, 35000)},
]


class FlipkartScraper(BaseScraper):
    """Mock Flipkart.com scraper."""

    source = "flipkart.com"

    async def search(
        self, query: str, max_price: float | None = None, limit: int = 10
    ) -> list[Product]:
        log.info("scraper.flipkart.search", query=query, max_price=max_price)

        base_price = max_price if max_price else 2499.0
        products: list[Product] = []

        for i, tmpl in enumerate(_FLIPKART_TEMPLATES[:limit]):
            price_factor = round(random.uniform(0.30, 0.90), 2)
            rating = round(random.uniform(*tmpl["rating_range"]), 1)
            buyers = random.randint(*tmpl["buyers_range"])

            name_parts = [tmpl["prefix"], query]
            if "suffix" in tmpl:
                name_parts.append(tmpl["suffix"])

            products.append(
                Product(
                    name=" ".join(name_parts),
                    price=round(base_price * price_factor, 2),
                    rating=rating,
                    buyers=buyers,
                    source=self.source,
                    url=f"https://www.flipkart.com/product/FKMOCK{i:04d}",
                    image_url=f"https://via.placeholder.com/200?text=Flipkart+{i}",
                    category=query.split()[0] if query else "General",
                )
            )

        return self.sort_products(products)
