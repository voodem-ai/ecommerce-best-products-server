"""Gemini-powered product scraper using Google Search grounding.

This scraper uses Gemini AI with Google Search to find REAL product data
from e-commerce websites. Gemini searches the web, extracts product info,
and returns structured JSON.
"""

import json

import structlog
from google import genai
from google.genai import types

from server.config import settings
from server.models import Product
from server.scrapers import BaseScraper

log = structlog.get_logger()


class GeminiScraper(BaseScraper):
    """Scrapes real product data using Gemini + Google Search grounding.

    Instead of manually scraping HTML (which is fragile and blocked by
    anti-bot systems), we ask Gemini to search the web with Google Search
    grounding and return structured product data.
    """

    def __init__(self, source: str, site_domain: str):
        """
        Args:
            source: Display name for the source (e.g. "amazon.in")
            site_domain: Domain to restrict search to (e.g. "amazon.in")
        """
        self.source = source
        self.site_domain = site_domain
        
        # Support both Google AI Studio (API Key) and Vertex AI (GCP)
        if hasattr(settings, "GOOGLE_CLOUD_PROJECT") and settings.GOOGLE_CLOUD_PROJECT:
            self._client = genai.Client(
                vertexai=True, project=settings.GOOGLE_CLOUD_PROJECT
            )
        elif settings.GEMINI_API_KEY:
            self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        else:
            # Fallback to auto-discovery
            self._client = genai.Client()

    async def search(
        self, query: str, max_price: float | None = None, limit: int = 5
    ) -> list[Product]:
        """Search for products using Gemini with Google Search grounding.

        Gemini will search the web (restricted to the site domain) and return
        structured product data.
        """
        log.info(
            "gemini_scraper.search",
            source=self.source,
            query=query,
            max_price=max_price,
        )

        price_constraint = ""
        if max_price:
            price_constraint = f" under ₹{max_price}"

        prompt = f"""Search {self.site_domain} for "{query}"{price_constraint}.

Find the top {limit} best products. For EACH product, extract:
- name: Full product title
- price: Price in INR (number only, no currency symbol)
- rating: Star rating out of 5 (e.g. 4.3)
- buyers: Approximate number of ratings/reviews/buyers (number only)
- url: Direct product URL on {self.site_domain}
- image_url: Product image URL if available (or null)
- category: Product category

IMPORTANT:
- Only include products actually available on {self.site_domain}
- Prioritize: highest rated, lowest price, most buyers
- Return ONLY valid JSON, no markdown, no explanation

Return a JSON array like:
[
  {{"name": "...", "price": 999, "rating": 4.5, "buyers": 12000, "url": "https://...", "image_url": "https://...", "category": "..."}},
  ...
]"""

        try:
            response = self._client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.1,  # Low creativity for factual data
                ),
            )

            # Extract text and parse JSON
            raw_text = response.text.strip()

            # Strip markdown code fences if present
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[1]  # Remove first line
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                raw_text = raw_text.strip()

            products_data = json.loads(raw_text)

            products: list[Product] = []
            for item in products_data[:limit]:
                try:
                    products.append(
                        Product(
                            name=str(item.get("name", "Unknown")),
                            price=float(item.get("price", 0)),
                            rating=min(float(item.get("rating", 0)), 5.0),
                            buyers=int(item.get("buyers", 0)),
                            source=self.source,
                            url=str(item.get("url", f"https://{self.site_domain}")),
                            image_url=item.get("image_url"),
                            category=item.get("category"),
                        )
                    )
                except (ValueError, TypeError) as e:
                    log.warning("gemini_scraper.parse_item_error", error=str(e), item=item)
                    continue

            log.info(
                "gemini_scraper.results",
                source=self.source,
                count=len(products),
            )

            return self.sort_products(products)

        except json.JSONDecodeError as e:
            log.error("gemini_scraper.json_error", source=self.source, error=str(e))
            return []
        except Exception as e:
            log.error("gemini_scraper.error", source=self.source, error=str(e))
            return []


# Pre-configured scrapers for each e-commerce site
class GeminiAmazonScraper(GeminiScraper):
    """Gemini-powered Amazon.in scraper."""

    def __init__(self):
        super().__init__(source="amazon.in", site_domain="amazon.in")


class GeminiFlipkartScraper(GeminiScraper):
    """Gemini-powered Flipkart.com scraper."""

    def __init__(self):
        super().__init__(source="flipkart.com", site_domain="flipkart.com")


class GeminiMyntraScraper(GeminiScraper):
    """Gemini-powered Myntra.com scraper."""

    def __init__(self):
        super().__init__(source="myntra.com", site_domain="myntra.com")
