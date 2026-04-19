"""Gemini-powered product scraper using Google Search grounding.

Strategy: Ask Gemini to search broadly for products on a specific retailer
WITHOUT the `site:` filter restriction that prevents Google from returning
real product listings. Instead we use natural-language queries mentioning
the retailer by name – the same way a human would search.
"""

import asyncio
import json
import re

import structlog
from google import genai
from google.genai import types

from server.config import settings
from server.models import Product
from server.scrapers import BaseScraper

log = structlog.get_logger()


# ---------------------------------------------------------------------------
# Helper: build the Gemini client (called once per scraper instance)
# ---------------------------------------------------------------------------

def _make_client() -> genai.Client:
    """Create a Gemini client preferring API key over Vertex AI."""
    api_key = getattr(settings, "GEMINI_API_KEY", None)
    if api_key and api_key not in ("", "your-gemini-api-key-here"):
        return genai.Client(api_key=api_key)

    project = getattr(settings, "GOOGLE_CLOUD_PROJECT", None)
    if project:
        location = getattr(settings, "GOOGLE_CLOUD_LOCATION", "us-central1")
        return genai.Client(vertexai=True, project=project, location=location)

    return genai.Client()  # ADC fallback


# ---------------------------------------------------------------------------
# Core scraper
# ---------------------------------------------------------------------------

class GeminiScraper(BaseScraper):
    """Scrapes real product data using Gemini + Google Search grounding.

    Uses natural-language search queries like a human would type into
    Google, rather than `site:` restrictions which block product listings.
    """

    def __init__(self, source: str, retailer_name: str):
        """
        Args:
            source:        Short identifier shown in Product.source (e.g. "amazon.in")
            retailer_name: How the retailer is mentioned in search queries
                           (e.g. "Amazon India", "Flipkart", "Myntra")
        """
        self.source = source
        self.retailer_name = retailer_name
        self._client = _make_client()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def search(
        self, query: str, max_price: float | None = None, limit: int = 5
    ) -> list[Product]:
        """Search for products via Gemini Google-Search grounding."""
        log.info("gemini_scraper.search", source=self.source, query=query, max_price=max_price)

        # Run the (synchronous) Gemini API call in an executor so it
        # does not block the event loop when called with asyncio.gather
        loop = asyncio.get_event_loop()
        products = await loop.run_in_executor(
            None, self._sync_search, query, max_price, limit
        )
        return products

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_prompt(self, query: str, max_price: float | None, limit: int) -> str:
        price_clause = f" under ₹{int(max_price)}" if max_price else ""
        return f"""Search the web and find the top {limit} "{query}"{price_clause} products currently listed on {self.retailer_name} in India.

YOU MUST respond with a raw JSON array ONLY. No prose, no markdown, no explanation before or after. Start your response with `[` and end with `]`.

Each element in the array must have these exact keys:
  "name"      – full product title (string)
  "price"     – price in INR as a number (no currency symbols or commas)
  "rating"    – star rating 0-5 as a decimal (use 4.0 if unknown)
  "buyers"    – integer count of reviews/ratings (use 500 if unknown)  
  "url"       – full direct product URL on {self.retailer_name}
  "image_url" – product image URL string or null
  "category"  – category string

Rules:
- Only include products from {self.retailer_name}. Do NOT mix retailers.
- Prioritise: highest rating → lowest price → most buyers.
- You MUST find and include REAL products currently available.
- Output ONLY the JSON array. No text before or after the array.

Example of the EXACT format required:
[{{"name":"Product Name","price":1999,"rating":4.3,"buyers":2500,"url":"https://example.com/product","image_url":null,"category":"Shoes"}}]"""

    def _sync_search(self, query: str, max_price: float | None, limit: int) -> list[Product]:
        prompt = self._build_prompt(query, max_price, limit)

        try:
            response = self._client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.1,
                ),
            )
            raw = (response.text or "").strip()
            log.debug("gemini_scraper.raw_response", source=self.source, raw=raw[:500])

            products_data = self._extract_json(raw)
            return self._parse_products(products_data, limit)

        except Exception as e:
            log.error("gemini_scraper.error", source=self.source, error=str(e))
            return []

    @staticmethod
    def _extract_json(text: str) -> list[dict]:
        """Robustly extract a JSON array from Gemini's response text."""
        # 1. Try direct parse first
        try:
            data = json.loads(text)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

        # 2. Strip markdown code fences  ```json ... ```
        fenced = re.sub(r"^```[a-z]*\n?", "", text, flags=re.MULTILINE)
        fenced = re.sub(r"\n?```$", "", fenced, flags=re.MULTILINE).strip()
        try:
            data = json.loads(fenced)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

        # 3. Regex – grab the first [...] block (handles trailing prose)
        match = re.search(r"\[[\s\S]*?\](?=\s*$|\s*\n[^[\]]*$|\s*```)", text)
        if not match:
            match = re.search(r"\[[\s\S]*\]", text)  # greedy fallback
        if match:
            try:
                data = json.loads(match.group(0))
                if isinstance(data, list):
                    return data
            except json.JSONDecodeError:
                pass

        log.warning("gemini_scraper.no_json_found", text_preview=text[:300])
        return []

    def _parse_products(self, items: list[dict], limit: int) -> list[Product]:
        products: list[Product] = []
        for item in items[:limit]:
            try:
                price_raw = item.get("price", 0)
                # Handle strings like "1,999" or "₹999"
                if isinstance(price_raw, str):
                    price_raw = re.sub(r"[^\d.]", "", price_raw) or "0"

                products.append(Product(
                    name=str(item.get("name", "Unknown")),
                    price=float(price_raw),
                    rating=min(float(item.get("rating", 4.0)), 5.0),
                    buyers=int(str(item.get("buyers", 500)).replace(",", "")),
                    source=self.source,
                    url=str(item.get("url", f"https://{self.source}")),
                    image_url=item.get("image_url"),
                    category=item.get("category"),
                ))
            except (ValueError, TypeError) as e:
                log.warning("gemini_scraper.parse_item_error", error=str(e), item=item)

        log.info("gemini_scraper.results", source=self.source, count=len(products))
        return self.sort_products(products)


# ---------------------------------------------------------------------------
# Pre-configured scrapers – one per retailer
# ---------------------------------------------------------------------------

class GeminiAmazonScraper(GeminiScraper):
    """Gemini-powered Amazon India scraper."""
    def __init__(self):
        super().__init__(source="amazon.in", retailer_name="Amazon India (amazon.in)")


class GeminiFlipkartScraper(GeminiScraper):
    """Gemini-powered Flipkart scraper."""
    def __init__(self):
        super().__init__(source="flipkart.com", retailer_name="Flipkart (flipkart.com)")


class GeminiMyntraScraper(GeminiScraper):
    """Gemini-powered Myntra scraper."""
    def __init__(self):
        super().__init__(source="myntra.com", retailer_name="Myntra (myntra.com)")
