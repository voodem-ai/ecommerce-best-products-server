"""Base scraper protocol and shared utilities."""

from abc import ABC, abstractmethod

from server.models import Product


class BaseScraper(ABC):
    """Abstract base class for all e-commerce scrapers."""

    source: str = ""

    @abstractmethod
    async def search(
        self, query: str, max_price: float | None = None, limit: int = 10
    ) -> list[Product]:
        """Search for products matching the query.

        Args:
            query: Search term.
            max_price: Optional price ceiling in INR.
            limit: Maximum results to return.

        Returns:
            List of Product objects sorted by rating desc, price asc, buyers desc.
        """
        ...

    @staticmethod
    def sort_products(products: list[Product]) -> list[Product]:
        """Sort by highest rating → lowest price → most buyers."""
        return sorted(
            products,
            key=lambda p: (-p.rating, p.price, -p.buyers),
        )
