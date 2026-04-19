"""Application configuration loaded from .env file and environment variables."""

import os

from dotenv import load_dotenv

# Load .env file from project root (auto-discovers .env in CWD or parents)
load_dotenv()


class Settings:
    """Server configuration.

    Values are read from environment variables. Place a `.env` file in the
    project root for local development (see `.env.example`).
    """

    # --- Gemini AI (REQUIRED – used for scraping products) ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # --- Scraper Mode ---
    # "gemini" → Uses Gemini + Google Search grounding (requires GEMINI_API_KEY)
    # "mock"   → Uses mock/fake data (no API key needed, for development)
    SCRAPER_MODE: str = os.getenv("SCRAPER_MODE", "gemini")

    # --- Redis Cache ---
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_TTL: int = int(os.getenv("REDIS_TTL", "3600"))  # 1 hour default

    # --- Server ---
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))

    # --- Google Cloud (optional – for Vertex AI) ---
    GOOGLE_APPLICATION_CREDENTIALS: str | None = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    GOOGLE_CLOUD_PROJECT: str | None = os.getenv("GOOGLE_CLOUD_PROJECT")


settings = Settings()
