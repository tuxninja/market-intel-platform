"""
Configuration management for Market Intelligence Platform.

Uses pydantic-settings for environment variable management with validation.
"""

from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Market Intelligence Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS (comma-separated string)
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # Database
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # Email (for notifications and daily digest)
    EMAIL_FROM: str = "noreply@marketintel.com"
    EMAIL_FROM_NAME: str = "Market Intelligence Platform"
    EMAIL_PASSWORD: Optional[str] = None
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True

    # News APIs
    NEWSAPI_KEY: Optional[str] = None
    ALPHA_VANTAGE_API_KEY: Optional[str] = None

    # ML Models
    ML_MODEL_PATH: str = "models"
    ENABLE_ML_ENHANCEMENT: bool = True

    # Digest Settings
    MAX_DIGEST_ITEMS: int = 20
    HOURS_LOOKBACK: int = 24

    # Stripe (for subscriptions)
    STRIPE_API_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # Cache
    REDIS_URL: Optional[str] = None
    CACHE_TTL_SECONDS: int = 3600

    def get_cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
