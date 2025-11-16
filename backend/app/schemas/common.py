"""
Common Pydantic schemas used across the application
"""
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional, Any
from datetime import datetime
from uuid import UUID


# Generic type for paginated responses
T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema"""
    success: bool = True
    data: List[T]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number", ge=1)
    page_size: int = Field(..., description="Number of items per page", ge=1, le=100)
    total_pages: int = Field(..., description="Total number of pages")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": [],
                "total": 100,
                "page": 1,
                "page_size": 20,
                "total_pages": 5
            }
        }


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str
    data: Optional[Any] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": None
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    message: str
    error_code: str
    errors: Optional[List[dict]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "An error occurred",
                "error_code": "VALIDATION_ERROR",
                "errors": []
            }
        }


class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at timestamps"""
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UUIDMixin(BaseModel):
    """Mixin for UUID primary key"""
    id: UUID

    class Config:
        from_attributes = True


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints"""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: Optional[str] = Field(default="asc", pattern="^(asc|desc)$", description="Sort order")


class HealthCheck(BaseModel):
    """Health check response schema"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Current server time")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment name")
    database: Optional[str] = Field(None, description="Database connection status")
    redis: Optional[str] = Field(None, description="Redis connection status")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-15T10:30:00Z",
                "version": "1.0.0",
                "environment": "development",
                "database": "connected",
                "redis": "connected"
            }
        }
