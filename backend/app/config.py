"""
Configuration management using Pydantic Settings.
Loads environment variables for database, Redis, and application settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "FarmFactory"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://farm_user:farmpass@localhost:5432/farmfactory"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_ECHO: bool = False  # Set to True for SQL query logging

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    # File Upload
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_EXTENSIONS: set = {".csv", ".xlsx", ".xls"}

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 1000

    # Time series data retention (days)
    ENVIRONMENTAL_DATA_RETENTION_DAYS: int = 365
    IRRIGATION_DATA_RETENTION_DAYS: int = 730
    NUTRIENT_DATA_RETENTION_DAYS: int = 730
    WATER_QUALITY_DATA_RETENTION_DAYS: int = 365

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create a global settings instance
settings = Settings()
