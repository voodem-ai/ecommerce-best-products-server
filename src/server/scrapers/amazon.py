"""Amazon.in product scraper (mock implementation).

Replace the mock data with real httpx + BeautifulSoup scraping or
Amazon Product Advertising API calls when ready.
"""

import random

import structlog

from server.models import Product
from server.scrapers import BaseScraper

log = structlog.get_logger()

# Realistic mock product templates
_AMAZON_TEMPLATES = [
    {"prefix": "Amazon Basics", "rating_range": (4.3, 4.9), "buyers_range": (8000, 45000)},
    {"prefix": "Premium", "suffix": "Pro", "rating_range": (4.5, 5.0), "buyers_range": (3000, 15000)},
    {"prefix": "Budget", "suffix": "Lite", "rating_range": (4.0, 4.6), "buyers_range": (15000, 60000)},
    {"prefix": "Top Seller", "suffix": "Edition", "rating_range": (4.4, 4.8), "buyers_range": (10000, 30000)},
    {"prefix": "Choice", "suffix": "Plus", "rating_range": (4.2, 4.7), "buyers_range": (5000, 25000)},
]


class AmazonScraper(BaseScraper):
    """Mock Amazon.in scraper."""

    source = "amazon.in"

    async def search(
        self, query: str, max_price: float | None = None, limit: int = 10
    ) -> list[Product]:
        log.info("scraper.amazon.search", query=query, max_price=max_price)

        base_price = max_price if max_price else 2999.0
        products: list[Product] = []

        for i, tmpl in enumerate(_AMAZON_TEMPLATES[:limit]):
            price_factor = round(random.uniform(0.35, 0.95), 2)
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
                    url=f"https://www.amazon.in/dp/B0MOCK{i:04d}",
                    image_url=f"https://via.placeholder.com/200?text=Amazon+{i}",
                    category=query.split()[0] if query else "General",
                )
            )

        return self.sort_products(products)
