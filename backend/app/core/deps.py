"""
Dependency injection for FastAPI endpoints
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
import logging

logger = logging.getLogger(__name__)


def get_db() -> Generator:
    """
    Database session dependency
    Yields a database session and ensures it's closed after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pagination dependencies
def get_pagination_params(
    page: int = 1,
    page_size: int = 20
) -> dict:
    """
    Get pagination parameters with validation

    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Dictionary with validated pagination parameters
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page number must be >= 1"
        )

    if page_size < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page size must be >= 1"
        )

    if page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page size cannot exceed 100"
        )

    return {
        "page": page,
        "page_size": page_size,
        "skip": (page - 1) * page_size,
        "limit": page_size
    }


# Optional: Authentication dependency (placeholder for future implementation)
async def get_current_user(
    # token: str = Depends(oauth2_scheme)  # Uncomment when implementing auth
) -> Optional[dict]:
    """
    Get current authenticated user
    Placeholder for future authentication implementation

    Returns:
        User information dictionary or None
    """
    # TODO: Implement JWT token validation
    # For now, return None to indicate no authentication
    return None


async def get_current_active_user(
    current_user: Optional[dict] = Depends(get_current_user)
) -> Optional[dict]:
    """
    Get current active user
    Placeholder for future authentication implementation

    Args:
        current_user: Current user from authentication

    Returns:
        Active user information or None
    """
    # TODO: Implement user active status check
    return current_user
