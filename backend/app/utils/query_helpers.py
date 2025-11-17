"""
Query helper utilities for filtering, pagination, and query manipulation.

Provides reusable functions for applying filters, pagination, and other
common query operations across all API endpoints.
"""
from typing import Any, Dict, List, Optional, TypeVar
from datetime import datetime, date
from sqlalchemy.orm import Query
from sqlalchemy import desc, asc, and_, or_
from app.schemas.common import PaginatedResponse
import math

T = TypeVar("T")


def apply_date_range_filter(
    query: Query,
    date_field: Any,
    start_date: Optional[datetime | date] = None,
    end_date: Optional[datetime | date] = None
) -> Query:
    """
    Apply date range filter to a SQLAlchemy query.

    Args:
        query: SQLAlchemy query object
        date_field: The date/datetime column to filter on
        start_date: Start date/datetime (inclusive)
        end_date: End date/datetime (inclusive)

    Returns:
        Modified query with date range filter applied
    """
    if start_date is not None:
        query = query.filter(date_field >= start_date)

    if end_date is not None:
        query = query.filter(date_field <= end_date)

    return query


def apply_pagination(
    query: Query,
    page: int = 1,
    page_size: int = 20
) -> tuple[Query, int, int]:
    """
    Apply offset-based pagination to a query.

    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (paginated query, skip offset, limit)
    """
    # Ensure page and page_size are valid
    page = max(1, page)
    page_size = min(max(1, page_size), 100)  # Cap at 100 items per page

    skip = (page - 1) * page_size
    limit = page_size

    return query.offset(skip).limit(limit), skip, limit


def apply_cursor_pagination(
    query: Query,
    cursor: Optional[datetime] = None,
    limit: int = 100,
    time_field: Any = None
) -> Query:
    """
    Apply cursor-based pagination for time-series data.

    Cursor pagination is more efficient for time-series data than offset pagination.

    Args:
        query: SQLAlchemy query object
        cursor: Timestamp cursor (returns records after this time)
        limit: Maximum number of records to return
        time_field: The time column to use for cursor pagination

    Returns:
        Modified query with cursor pagination applied
    """
    if cursor is not None and time_field is not None:
        query = query.filter(time_field > cursor)

    # Cap limit at 1000 for time-series queries
    limit = min(max(1, limit), 1000)
    query = query.limit(limit)

    return query


def apply_filters(
    query: Query,
    model: Any,
    filters: Dict[str, Any]
) -> Query:
    """
    Apply dynamic filters from query parameters.

    Args:
        query: SQLAlchemy query object
        model: SQLAlchemy model class
        filters: Dictionary of field names and their filter values

    Returns:
        Modified query with filters applied

    Example:
        filters = {"status": "active", "plot_id": uuid_value}
        query = apply_filters(query, Planting, filters)
    """
    for field_name, value in filters.items():
        if value is not None and hasattr(model, field_name):
            field = getattr(model, field_name)
            query = query.filter(field == value)

    return query


def apply_sorting(
    query: Query,
    model: Any,
    sort_by: Optional[str] = None,
    sort_order: str = "asc"
) -> Query:
    """
    Apply sorting to a query.

    Args:
        query: SQLAlchemy query object
        model: SQLAlchemy model class
        sort_by: Field name to sort by
        sort_order: Sort order ("asc" or "desc")

    Returns:
        Modified query with sorting applied
    """
    if sort_by and hasattr(model, sort_by):
        field = getattr(model, sort_by)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(field))
        else:
            query = query.order_by(asc(field))

    return query


def get_paginated_response(
    items: List[T],
    total: int,
    page: int,
    page_size: int
) -> PaginatedResponse[T]:
    """
    Create a standardized paginated response.

    Args:
        items: List of items for current page
        total: Total number of items across all pages
        page: Current page number
        page_size: Number of items per page

    Returns:
        PaginatedResponse object with metadata
    """
    total_pages = math.ceil(total / page_size) if page_size > 0 else 0

    return PaginatedResponse(
        success=True,
        data=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


def apply_time_series_filters(
    query: Query,
    time_field: Any,
    plot_id: Optional[Any] = None,
    plot_field: Optional[Any] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 1000
) -> Query:
    """
    Apply common filters for time-series queries.

    Args:
        query: SQLAlchemy query object
        time_field: The time column
        plot_id: Optional plot ID to filter by
        plot_field: The plot_id column
        start_time: Start time (inclusive)
        end_time: End time (inclusive)
        limit: Maximum number of records

    Returns:
        Modified query with time-series filters applied
    """
    # Apply plot filter
    if plot_id is not None and plot_field is not None:
        query = query.filter(plot_field == plot_id)

    # Apply date range filter
    query = apply_date_range_filter(query, time_field, start_time, end_time)

    # Order by time descending (most recent first)
    query = query.order_by(desc(time_field))

    # Apply limit
    limit = min(max(1, limit), 10000)  # Cap at 10k records
    query = query.limit(limit)

    return query


def get_total_count(query: Query) -> int:
    """
    Get the total count of items in a query without pagination.

    Args:
        query: SQLAlchemy query object

    Returns:
        Total count of items
    """
    return query.count()
