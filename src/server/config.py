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

    # --- Redis Cache ---
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_TTL: int = int(os.getenv("REDIS_TTL", "3600"))  # 1 hour default

    # --- Server ---
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))

    # --- Google Cloud (for future real scraper auth) ---
    GOOGLE_APPLICATION_CREDENTIALS: str | None = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    GOOGLE_CLOUD_PROJECT: str | None = os.getenv("GOOGLE_CLOUD_PROJECT")


settings = Settings()
