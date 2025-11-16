"""
Health check and system status endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.core.deps import get_db
from app.core.config import settings
from app.schemas.common import HealthCheck
from app.core.database import get_db_connection

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint
    Returns system status and component health
    """
    # Check database connection
    db_status = "connected" if get_db_connection() else "disconnected"

    # TODO: Add Redis health check when Redis is configured
    redis_status = "not_configured"

    health_data = HealthCheck(
        status="healthy" if db_status == "connected" else "unhealthy",
        timestamp=datetime.utcnow(),
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database=db_status,
        redis=redis_status
    )

    return health_data


@router.get("/status", tags=["Health"])
async def system_status():
    """
    Detailed system status endpoint
    Returns comprehensive system information
    """
    return {
        "success": True,
        "data": {
            "application": {
                "name": settings.APP_NAME,
                "version": settings.VERSION,
                "environment": settings.ENVIRONMENT
            },
            "database": {
                "connected": get_db_connection(),
                "url_masked": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "not_configured"
            },
            "api": {
                "prefix": settings.API_V1_PREFIX,
                "docs_url": "/api/docs",
                "cors_enabled": True,
                "cors_origins": settings.CORS_ORIGINS
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    }


@router.get("/ping", tags=["Health"])
async def ping():
    """
    Simple ping endpoint for uptime monitoring
    """
    return {
        "success": True,
        "message": "pong",
        "timestamp": datetime.utcnow().isoformat()
    }
