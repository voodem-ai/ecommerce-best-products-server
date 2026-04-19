"""Myntra.com product scraper (mock implementation)."""

import random

import structlog

from server.models import Product
from server.scrapers import BaseScraper

log = structlog.get_logger()

_MYNTRA_TEMPLATES = [
    {"prefix": "Roadster", "rating_range": (4.3, 4.9), "buyers_range": (10000, 40000)},
    {"prefix": "HRX by Hrithik", "rating_range": (4.5, 5.0), "buyers_range": (8000, 25000)},
    {"prefix": "Mast & Harbour", "suffix": "Classic", "rating_range": (4.2, 4.7), "buyers_range": (15000, 50000)},
    {"prefix": "HERE&NOW", "suffix": "Trendy", "rating_range": (4.0, 4.6), "buyers_range": (12000, 35000)},
    {"prefix": "Anouk", "suffix": "Elegance", "rating_range": (4.4, 4.8), "buyers_range": (6000, 18000)},
]


class MyntraScraper(BaseScraper):
    """Mock Myntra.com scraper."""

    source = "myntra.com"

    async def search(
        self, query: str, max_price: float | None = None, limit: int = 10
    ) -> list[Product]:
        log.info("scraper.myntra.search", query=query, max_price=max_price)

        base_price = max_price if max_price else 1999.0
        products: list[Product] = []

        for i, tmpl in enumerate(_MYNTRA_TEMPLATES[:limit]):
            price_factor = round(random.uniform(0.30, 0.85), 2)
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
                    url=f"https://www.myntra.com/product/MNTMOCK{i:04d}",
                    image_url=f"https://via.placeholder.com/200?text=Myntra+{i}",
                    category=query.split()[0] if query else "Fashion",
                )
            )

        return self.sort_products(products)
