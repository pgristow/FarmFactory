"""
Standard API response formatters
"""
from typing import Any, List, Optional, TypeVar, Generic
from fastapi.responses import JSONResponse
from fastapi import status
from app.schemas.common import PaginatedResponse, SuccessResponse, ErrorResponse
import math

T = TypeVar('T')


def success_response(
    message: str = "Success",
    data: Any = None,
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """
    Create a standard success response

    Args:
        message: Success message
        data: Response data
        status_code: HTTP status code

    Returns:
        JSONResponse with success format
    """
    response = SuccessResponse(
        success=True,
        message=message,
        data=data
    )
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump()
    )


def error_response(
    message: str,
    error_code: str = "ERROR",
    errors: Optional[List[dict]] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> JSONResponse:
    """
    Create a standard error response

    Args:
        message: Error message
        error_code: Error code identifier
        errors: List of detailed errors
        status_code: HTTP status code

    Returns:
        JSONResponse with error format
    """
    response = ErrorResponse(
        success=False,
        message=message,
        error_code=error_code,
        errors=errors
    )
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump()
    )


def paginated_response(
    data: List[Any],
    total: int,
    page: int,
    page_size: int,
    status_code: int = status.HTTP_200_OK
) -> dict:
    """
    Create a paginated response

    Args:
        data: List of items for current page
        total: Total number of items
        page: Current page number
        page_size: Items per page
        status_code: HTTP status code

    Returns:
        Dictionary with paginated response format
    """
    total_pages = math.ceil(total / page_size) if page_size > 0 else 0

    return {
        "success": True,
        "data": data,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


def created_response(
    message: str = "Resource created successfully",
    data: Any = None
) -> JSONResponse:
    """
    Create a 201 Created response

    Args:
        message: Success message
        data: Created resource data

    Returns:
        JSONResponse with 201 status
    """
    return success_response(
        message=message,
        data=data,
        status_code=status.HTTP_201_CREATED
    )


def no_content_response() -> JSONResponse:
    """
    Create a 204 No Content response

    Returns:
        JSONResponse with 204 status
    """
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content=None
    )


def not_found_response(
    resource: str = "Resource",
    resource_id: Any = None
) -> JSONResponse:
    """
    Create a 404 Not Found response

    Args:
        resource: Resource type name
        resource_id: Resource identifier

    Returns:
        JSONResponse with 404 status
    """
    if resource_id:
        message = f"{resource} with id '{resource_id}' not found"
    else:
        message = f"{resource} not found"

    return error_response(
        message=message,
        error_code="NOT_FOUND",
        status_code=status.HTTP_404_NOT_FOUND
    )


def validation_error_response(
    errors: List[dict],
    message: str = "Validation error"
) -> JSONResponse:
    """
    Create a 422 Validation Error response

    Args:
        errors: List of validation errors
        message: Error message

    Returns:
        JSONResponse with 422 status
    """
    return error_response(
        message=message,
        error_code="VALIDATION_ERROR",
        errors=errors,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


def conflict_response(
    message: str = "Resource already exists",
    error_code: str = "CONFLICT"
) -> JSONResponse:
    """
    Create a 409 Conflict response

    Args:
        message: Error message
        error_code: Error code

    Returns:
        JSONResponse with 409 status
    """
    return error_response(
        message=message,
        error_code=error_code,
        status_code=status.HTTP_409_CONFLICT
    )


def internal_error_response(
    message: str = "Internal server error"
) -> JSONResponse:
    """
    Create a 500 Internal Server Error response

    Args:
        message: Error message

    Returns:
        JSONResponse with 500 status
    """
    return error_response(
        message=message,
        error_code="INTERNAL_SERVER_ERROR",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
