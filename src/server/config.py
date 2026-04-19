"""Application configuration loaded from environment variables."""

import os


class Settings:
    """Server configuration."""

    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_TTL: int = int(os.getenv("REDIS_TTL", "3600"))  # 1 hour default
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))


settings = Settings()
