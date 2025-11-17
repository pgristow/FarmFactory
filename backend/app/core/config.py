"""
Application configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings and configuration"""

    # Application
    APP_NAME: str = "FarmFactory"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Database
    DATABASE_URL: str = "postgresql://farm_user:farm_password@localhost:5432/farmfactory"
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # File Upload & Import
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB for import files
    UPLOAD_DIR: Path = Path("uploads")
    ALLOWED_EXTENSIONS: List[str] = [".csv", ".xlsx", ".xls"]

    # Import settings
    IMPORT_BATCH_SIZE: int = 500  # Number of rows to process per batch
    IMPORT_MAX_ERRORS: int = 100  # Maximum errors to collect during validation
    IMPORT_FILE_RETENTION_DAYS: int = 30  # Days to keep processed import files
    IMPORT_MIN_CONFIDENCE: float = 60.0  # Minimum confidence for auto column mapping (%)

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
