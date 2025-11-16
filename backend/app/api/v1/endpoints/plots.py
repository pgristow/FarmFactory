"""
Plot CRUD API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import logging

from app.core.deps import get_db, get_pagination_params
from app.schemas.plot import PlotCreate, PlotUpdate, PlotInDB, PlotResponse, PlotListItem
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.services.plot_service import PlotService
from app.services.farm_service import FarmService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=PlotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new plot",
    tags=["Plots"]
)
async def create_plot(
    plot_data: PlotCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new plot within a farm with the following information:

    - **farm_id**: ID of the parent farm (required)
    - **name**: Plot name (required)
    - **plot_number**: Plot number or identifier
    - **area_hectares**: Plot area in hectares
    - **elevation_meters**: Elevation above sea level
    - **slope_degrees**: Slope in degrees (0-90)
    """
    try:
        # Verify farm exists
        if not FarmService.farm_exists(db, plot_data.farm_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm with id '{plot_data.farm_id}' not found"
            )

        plot = PlotService.create_plot(db, plot_data)
        return PlotResponse(success=True, data=PlotInDB.model_validate(plot))
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating plot: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating plot: {str(e)}"
        )


@router.get(
    "/",
    response_model=PaginatedResponse[PlotListItem],
    summary="List all plots",
    tags=["Plots"]
)
async def list_plots(
    farm_id: Optional[UUID] = Query(None, description="Filter by farm ID"),
    pagination: dict = Depends(get_pagination_params),
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of all plots.

    Query parameters:
    - **farm_id**: Filter plots by farm ID (optional)
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    """
    try:
        plots, total = PlotService.get_plots(
            db,
            farm_id=farm_id,
            skip=pagination["skip"],
            limit=pagination["limit"]
        )

        return {
            "success": True,
            "data": [plot.model_dump() for plot in plots],
            "total": total,
            "page": pagination["page"],
            "page_size": pagination["page_size"],
            "total_pages": (total + pagination["page_size"] - 1) // pagination["page_size"]
        }
    except Exception as e:
        logger.error(f"Error listing plots: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing plots: {str(e)}"
        )


@router.get(
    "/{plot_id}",
    response_model=PlotResponse,
    summary="Get plot by ID",
    tags=["Plots"]
)
async def get_plot(
    plot_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific plot by ID.
    """
    plot = PlotService.get_plot(db, plot_id)
    if not plot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plot with id '{plot_id}' not found"
        )

    return PlotResponse(success=True, data=PlotInDB.model_validate(plot))


@router.put(
    "/{plot_id}",
    response_model=PlotResponse,
    summary="Update plot",
    tags=["Plots"]
)
async def update_plot(
    plot_id: UUID,
    plot_data: PlotUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a plot's information.

    Only the fields provided in the request body will be updated.
    """
    plot = PlotService.update_plot(db, plot_id, plot_data)
    if not plot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plot with id '{plot_id}' not found"
        )

    return PlotResponse(success=True, data=PlotInDB.model_validate(plot))


@router.delete(
    "/{plot_id}",
    response_model=SuccessResponse,
    summary="Delete plot",
    tags=["Plots"]
)
async def delete_plot(
    plot_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a plot and all associated data.

    Warning: This action cannot be undone and will delete all data
    associated with this plot (plantings, irrigation events, etc.).
    """
    deleted = PlotService.delete_plot(db, plot_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plot with id '{plot_id}' not found"
        )

    return SuccessResponse(
        success=True,
        message=f"Plot with id '{plot_id}' deleted successfully"
    )
