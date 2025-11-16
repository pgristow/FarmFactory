"""
Farm CRUD API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import logging

from app.core.deps import get_db, get_pagination_params
from app.schemas.farm import FarmCreate, FarmUpdate, FarmInDB, FarmResponse, FarmListItem
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.services.farm_service import FarmService
from app.utils.responses import paginated_response, not_found_response

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=FarmResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new farm",
    tags=["Farms"]
)
async def create_farm(
    farm_data: FarmCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new farm with the following information:

    - **name**: Farm name (required)
    - **address**: Physical address
    - **latitude**: Geographic latitude (-90 to 90)
    - **longitude**: Geographic longitude (-180 to 180)
    - **total_area_hectares**: Total farm area in hectares
    - **timezone**: Timezone (e.g., "America/Los_Angeles")
    """
    try:
        farm = FarmService.create_farm(db, farm_data)
        return FarmResponse(success=True, data=FarmInDB.model_validate(farm))
    except Exception as e:
        logger.error(f"Error creating farm: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating farm: {str(e)}"
        )


@router.get(
    "/",
    response_model=PaginatedResponse[FarmListItem],
    summary="List all farms",
    tags=["Farms"]
)
async def list_farms(
    pagination: dict = Depends(get_pagination_params),
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of all farms.

    Query parameters:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    """
    try:
        farms, total = FarmService.get_farms(
            db,
            skip=pagination["skip"],
            limit=pagination["limit"]
        )

        return paginated_response(
            data=[farm.model_dump() for farm in farms],
            total=total,
            page=pagination["page"],
            page_size=pagination["page_size"]
        )
    except Exception as e:
        logger.error(f"Error listing farms: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing farms: {str(e)}"
        )


@router.get(
    "/{farm_id}",
    response_model=FarmResponse,
    summary="Get farm by ID",
    tags=["Farms"]
)
async def get_farm(
    farm_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific farm by ID.
    """
    farm = FarmService.get_farm(db, farm_id)
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with id '{farm_id}' not found"
        )

    return FarmResponse(success=True, data=FarmInDB.model_validate(farm))


@router.put(
    "/{farm_id}",
    response_model=FarmResponse,
    summary="Update farm",
    tags=["Farms"]
)
async def update_farm(
    farm_id: UUID,
    farm_data: FarmUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a farm's information.

    Only the fields provided in the request body will be updated.
    """
    farm = FarmService.update_farm(db, farm_id, farm_data)
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with id '{farm_id}' not found"
        )

    return FarmResponse(success=True, data=FarmInDB.model_validate(farm))


@router.delete(
    "/{farm_id}",
    response_model=SuccessResponse,
    summary="Delete farm",
    tags=["Farms"]
)
async def delete_farm(
    farm_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a farm and all associated plots.

    Warning: This action cannot be undone and will delete all plots
    associated with this farm.
    """
    deleted = FarmService.delete_farm(db, farm_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with id '{farm_id}' not found"
        )

    return SuccessResponse(
        success=True,
        message=f"Farm with id '{farm_id}' deleted successfully"
    )
