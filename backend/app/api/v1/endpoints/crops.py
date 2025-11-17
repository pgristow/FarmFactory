"""
Crop and Planting CRUD API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID
from datetime import date
import logging

from app.core.deps import get_db, get_pagination_params
from app.schemas.crop import (
    CropCreate, CropUpdate, CropInDB,
    PlantingCreate, PlantingUpdate, PlantingInDB, PlantingWithDetails
)
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.models.crop import Crop, Planting
from app.models.plot import Plot
from app.utils.query_helpers import (
    apply_pagination, apply_filters, apply_sorting, get_paginated_response, get_total_count
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== CROP ENDPOINTS ====================

@router.post(
    "/crops",
    response_model=CropInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new crop",
    tags=["Crops"]
)
async def create_crop(
    crop_data: CropCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new crop variety.

    - **name**: Crop name (required)
    - **scientific_name**: Scientific name
    - **variety**: Crop variety or cultivar
    - **optimal_temp_min_celsius**: Minimum optimal temperature
    - **optimal_temp_max_celsius**: Maximum optimal temperature
    - **optimal_ph_min**: Minimum optimal soil pH
    - **optimal_ph_max**: Maximum optimal soil pH
    - **days_to_maturity**: Typical days from planting to harvest
    """
    try:
        crop = Crop(**crop_data.model_dump())
        db.add(crop)
        db.commit()
        db.refresh(crop)
        return CropInDB.model_validate(crop)
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating crop: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating crop: {str(e)}"
        )


@router.get(
    "/crops",
    response_model=PaginatedResponse[CropInDB],
    summary="List all crops",
    tags=["Crops"]
)
async def list_crops(
    pagination: dict = Depends(get_pagination_params),
    name: Optional[str] = Query(None, description="Filter by crop name (partial match)"),
    variety: Optional[str] = Query(None, description="Filter by variety"),
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of all crops with optional filtering.

    Query parameters:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **name**: Filter by crop name (partial match)
    - **variety**: Filter by variety
    """
    try:
        query = db.query(Crop)

        # Apply filters
        if name:
            query = query.filter(Crop.name.ilike(f"%{name}%"))
        if variety:
            query = query.filter(Crop.variety.ilike(f"%{variety}%"))

        # Order by name
        query = query.order_by(Crop.name)

        # Get total count before pagination
        total = get_total_count(query)

        # Apply pagination
        query, skip, limit = apply_pagination(query, pagination["page"], pagination["page_size"])

        crops = query.all()

        return get_paginated_response(
            items=[CropInDB.model_validate(crop) for crop in crops],
            total=total,
            page=pagination["page"],
            page_size=pagination["page_size"]
        )
    except Exception as e:
        logger.error(f"Error listing crops: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing crops: {str(e)}"
        )


@router.get(
    "/crops/{crop_id}",
    response_model=CropInDB,
    summary="Get crop by ID",
    tags=["Crops"]
)
async def get_crop(
    crop_id: UUID,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific crop by ID."""
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop with id '{crop_id}' not found"
        )
    return CropInDB.model_validate(crop)


@router.put(
    "/crops/{crop_id}",
    response_model=CropInDB,
    summary="Update crop",
    tags=["Crops"]
)
async def update_crop(
    crop_id: UUID,
    crop_data: CropUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a crop's information.

    Only the fields provided in the request body will be updated.
    """
    try:
        crop = db.query(Crop).filter(Crop.id == crop_id).first()
        if not crop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crop with id '{crop_id}' not found"
            )

        # Update only provided fields
        update_data = crop_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(crop, field, value)

        db.commit()
        db.refresh(crop)
        return CropInDB.model_validate(crop)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating crop: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating crop: {str(e)}"
        )


@router.delete(
    "/crops/{crop_id}",
    response_model=SuccessResponse,
    summary="Delete crop",
    tags=["Crops"]
)
async def delete_crop(
    crop_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a crop.

    Warning: This may fail if there are existing plantings using this crop.
    """
    try:
        crop = db.query(Crop).filter(Crop.id == crop_id).first()
        if not crop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crop with id '{crop_id}' not found"
            )

        db.delete(crop)
        db.commit()

        return SuccessResponse(
            success=True,
            message=f"Crop '{crop.name}' deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting crop: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting crop: {str(e)}"
        )


# ==================== PLANTING ENDPOINTS ====================

@router.post(
    "/plantings",
    response_model=PlantingInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new planting",
    tags=["Plantings"]
)
async def create_planting(
    planting_data: PlantingCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new planting record.

    - **plot_id**: ID of the plot (required)
    - **crop_id**: ID of the crop (required)
    - **planting_date**: Date when crop was planted (required)
    - **expected_harvest_date**: Expected harvest date
    - **actual_harvest_date**: Actual harvest date
    - **plant_population**: Number of plants
    - **row_spacing_cm**: Row spacing in centimeters
    - **plant_spacing_cm**: Plant spacing in centimeters
    - **status**: Status (planted, growing, harvested, failed)
    """
    try:
        # Verify plot exists
        plot = db.query(Plot).filter(Plot.id == planting_data.plot_id).first()
        if not plot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plot with id '{planting_data.plot_id}' not found"
            )

        # Verify crop exists
        crop = db.query(Crop).filter(Crop.id == planting_data.crop_id).first()
        if not crop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crop with id '{planting_data.crop_id}' not found"
            )

        planting = Planting(**planting_data.model_dump())
        db.add(planting)
        db.commit()
        db.refresh(planting)
        return PlantingInDB.model_validate(planting)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating planting: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating planting: {str(e)}"
        )


@router.get(
    "/plantings",
    response_model=PaginatedResponse[PlantingInDB],
    summary="List plantings",
    tags=["Plantings"]
)
async def list_plantings(
    pagination: dict = Depends(get_pagination_params),
    plot_id: Optional[UUID] = Query(None, description="Filter by plot ID"),
    crop_id: Optional[UUID] = Query(None, description="Filter by crop ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of plantings with optional filtering.

    Query parameters:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **plot_id**: Filter by plot ID
    - **crop_id**: Filter by crop ID
    - **status**: Filter by status (planted, growing, harvested, failed)
    """
    try:
        query = db.query(Planting)

        # Apply filters
        if plot_id:
            query = query.filter(Planting.plot_id == plot_id)
        if crop_id:
            query = query.filter(Planting.crop_id == crop_id)
        if status:
            query = query.filter(Planting.status == status)

        # Order by planting date descending (most recent first)
        query = query.order_by(Planting.planting_date.desc())

        # Get total count before pagination
        total = get_total_count(query)

        # Apply pagination
        query, skip, limit = apply_pagination(query, pagination["page"], pagination["page_size"])

        plantings = query.all()

        return get_paginated_response(
            items=[PlantingInDB.model_validate(planting) for planting in plantings],
            total=total,
            page=pagination["page"],
            page_size=pagination["page_size"]
        )
    except Exception as e:
        logger.error(f"Error listing plantings: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing plantings: {str(e)}"
        )


@router.get(
    "/plantings/{planting_id}",
    response_model=PlantingInDB,
    summary="Get planting by ID",
    tags=["Plantings"]
)
async def get_planting(
    planting_id: UUID,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific planting including phenology observations."""
    planting = db.query(Planting).filter(Planting.id == planting_id).first()
    if not planting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Planting with id '{planting_id}' not found"
        )
    return PlantingInDB.model_validate(planting)


@router.put(
    "/plantings/{planting_id}",
    response_model=PlantingInDB,
    summary="Update planting",
    tags=["Plantings"]
)
async def update_planting(
    planting_id: UUID,
    planting_data: PlantingUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a planting's information.

    Only the fields provided in the request body will be updated.
    """
    try:
        planting = db.query(Planting).filter(Planting.id == planting_id).first()
        if not planting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planting with id '{planting_id}' not found"
            )

        # Update only provided fields
        update_data = planting_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(planting, field, value)

        db.commit()
        db.refresh(planting)
        return PlantingInDB.model_validate(planting)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating planting: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating planting: {str(e)}"
        )


@router.delete(
    "/plantings/{planting_id}",
    response_model=SuccessResponse,
    summary="Delete planting",
    tags=["Plantings"]
)
async def delete_planting(
    planting_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a planting and all associated records (phenology observations, harvests, costs).

    Warning: This action cannot be undone.
    """
    try:
        planting = db.query(Planting).filter(Planting.id == planting_id).first()
        if not planting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planting with id '{planting_id}' not found"
            )

        db.delete(planting)
        db.commit()

        return SuccessResponse(
            success=True,
            message=f"Planting deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting planting: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting planting: {str(e)}"
        )


@router.patch(
    "/plantings/{planting_id}/status",
    response_model=PlantingInDB,
    summary="Update planting status",
    tags=["Plantings"]
)
async def update_planting_status(
    planting_id: UUID,
    status: str = Query(..., description="New status (planted, growing, harvested, failed)"),
    db: Session = Depends(get_db)
):
    """
    Update only the status of a planting.

    Valid statuses: planted, growing, harvested, failed
    """
    try:
        # Validate status
        allowed_statuses = ["planted", "growing", "harvested", "failed"]
        if status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(allowed_statuses)}"
            )

        planting = db.query(Planting).filter(Planting.id == planting_id).first()
        if not planting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planting with id '{planting_id}' not found"
            )

        planting.status = status
        db.commit()
        db.refresh(planting)
        return PlantingInDB.model_validate(planting)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating planting status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating planting status: {str(e)}"
        )


@router.get(
    "/plantings/calendar",
    summary="Get planting calendar",
    tags=["Plantings"]
)
async def get_planting_calendar(
    year: Optional[int] = Query(None, description="Filter by year"),
    plot_id: Optional[UUID] = Query(None, description="Filter by plot ID"),
    db: Session = Depends(get_db)
):
    """
    Get planting calendar grouped by month with crop details.

    Returns plantings organized by month, showing what crops were planted when.
    Useful for planning and visualizing the planting schedule.

    Query parameters:
    - **year**: Filter plantings by year (default: all years)
    - **plot_id**: Filter by specific plot (default: all plots)
    """
    try:
        query = db.query(Planting).join(Crop)

        # Apply filters
        if plot_id:
            query = query.filter(Planting.plot_id == plot_id)
        if year:
            query = query.filter(func.extract('year', Planting.planting_date) == year)

        # Order by planting date
        query = query.order_by(Planting.planting_date)

        plantings = query.all()

        # Group by month
        calendar = {}
        for planting in plantings:
            month_key = planting.planting_date.strftime('%Y-%m')
            month_name = planting.planting_date.strftime('%B %Y')

            if month_key not in calendar:
                calendar[month_key] = {
                    'month': month_name,
                    'year': planting.planting_date.year,
                    'month_number': planting.planting_date.month,
                    'plantings': []
                }

            calendar[month_key]['plantings'].append({
                'id': str(planting.id),
                'plot_id': str(planting.plot_id),
                'crop_id': str(planting.crop_id),
                'crop_name': planting.crop.name,
                'crop_variety': planting.crop.variety,
                'planting_date': planting.planting_date.isoformat(),
                'expected_harvest_date': planting.expected_harvest_date.isoformat() if planting.expected_harvest_date else None,
                'status': planting.status,
                'plant_population': planting.plant_population
            })

        # Convert to list and sort by month
        calendar_list = sorted(calendar.values(), key=lambda x: f"{x['year']}-{x['month_number']:02d}")

        return {
            'success': True,
            'year': year,
            'plot_id': str(plot_id) if plot_id else None,
            'total_months': len(calendar_list),
            'total_plantings': len(plantings),
            'calendar': calendar_list
        }
    except Exception as e:
        logger.error(f"Error getting planting calendar: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting planting calendar: {str(e)}"
        )
