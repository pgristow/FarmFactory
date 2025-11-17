"""
Phenology Observations API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date
import logging

from app.core.deps import get_db, get_pagination_params
from app.schemas.phenology import (
    PhenologyObservationCreate, PhenologyObservationUpdate,
    PhenologyObservationInDB, PhenologyTimeline
)
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.models.phenology import PhenologyObservation
from app.models.crop import Planting
from app.utils.query_helpers import (
    apply_pagination, apply_date_range_filter, get_paginated_response, get_total_count
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=PhenologyObservationInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create phenology observation",
    tags=["Phenology"]
)
async def create_phenology_observation(
    observation_data: PhenologyObservationCreate,
    db: Session = Depends(get_db)
):
    """
    Record a new phenology observation.

    - **planting_id**: ID of the planting (required)
    - **observation_date**: Date of observation (required)
    - **growth_stage**: Growth stage (germination, vegetative, flowering, etc.)
    - **bbch_code**: BBCH phenological scale code (0-99)
    - **height_cm**: Plant height in cm
    - **canopy_cover_percent**: Canopy cover (0-100)
    - **health_score**: Health score (1-10)
    - **notes**: Observation notes
    - **photos**: Photo URLs and metadata
    """
    try:
        # Verify planting exists
        planting = db.query(Planting).filter(Planting.id == observation_data.planting_id).first()
        if not planting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planting with id '{observation_data.planting_id}' not found"
            )

        observation = PhenologyObservation(**observation_data.model_dump())
        db.add(observation)
        db.commit()
        db.refresh(observation)
        return PhenologyObservationInDB.model_validate(observation)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating phenology observation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating phenology observation: {str(e)}"
        )


@router.get(
    "/",
    response_model=PaginatedResponse[PhenologyObservationInDB],
    summary="List phenology observations",
    tags=["Phenology"]
)
async def list_phenology_observations(
    pagination: dict = Depends(get_pagination_params),
    planting_id: Optional[UUID] = Query(None, description="Filter by planting ID"),
    start_date: Optional[date] = Query(None, description="Start date (inclusive)"),
    end_date: Optional[date] = Query(None, description="End date (inclusive)"),
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of phenology observations with filtering.

    Query parameters:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **planting_id**: Filter by planting ID
    - **start_date**: Start date
    - **end_date**: End date
    """
    try:
        query = db.query(PhenologyObservation)

        # Apply filters
        if planting_id:
            query = query.filter(PhenologyObservation.planting_id == planting_id)

        # Apply date range filter
        query = apply_date_range_filter(
            query,
            PhenologyObservation.observation_date,
            start_date,
            end_date
        )

        # Order by observation date descending
        query = query.order_by(desc(PhenologyObservation.observation_date))

        # Get total count before pagination
        total = get_total_count(query)

        # Apply pagination
        query, skip, limit = apply_pagination(query, pagination["page"], pagination["page_size"])

        observations = query.all()

        return get_paginated_response(
            items=[PhenologyObservationInDB.model_validate(obs) for obs in observations],
            total=total,
            page=pagination["page"],
            page_size=pagination["page_size"]
        )
    except Exception as e:
        logger.error(f"Error listing phenology observations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing phenology observations: {str(e)}"
        )


@router.get(
    "/{observation_id}",
    response_model=PhenologyObservationInDB,
    summary="Get phenology observation",
    tags=["Phenology"]
)
async def get_phenology_observation(
    observation_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific phenology observation by ID."""
    observation = db.query(PhenologyObservation).filter(
        PhenologyObservation.id == observation_id
    ).first()

    if not observation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Phenology observation not found"
        )

    return PhenologyObservationInDB.model_validate(observation)


@router.put(
    "/{observation_id}",
    response_model=PhenologyObservationInDB,
    summary="Update phenology observation",
    tags=["Phenology"]
)
async def update_phenology_observation(
    observation_id: UUID,
    observation_data: PhenologyObservationUpdate,
    db: Session = Depends(get_db)
):
    """Update a phenology observation."""
    try:
        observation = db.query(PhenologyObservation).filter(
            PhenologyObservation.id == observation_id
        ).first()

        if not observation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Phenology observation not found"
            )

        # Update only provided fields
        update_data = observation_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(observation, field, value)

        db.commit()
        db.refresh(observation)
        return PhenologyObservationInDB.model_validate(observation)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating phenology observation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating phenology observation: {str(e)}"
        )


@router.delete(
    "/{observation_id}",
    response_model=SuccessResponse,
    summary="Delete phenology observation",
    tags=["Phenology"]
)
async def delete_phenology_observation(
    observation_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a phenology observation."""
    try:
        observation = db.query(PhenologyObservation).filter(
            PhenologyObservation.id == observation_id
        ).first()

        if not observation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Phenology observation not found"
            )

        db.delete(observation)
        db.commit()

        return SuccessResponse(
            success=True,
            message=f"Phenology observation deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting phenology observation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting phenology observation: {str(e)}"
        )


@router.post(
    "/{observation_id}/photos",
    response_model=PhenologyObservationInDB,
    summary="Upload photos to observation",
    tags=["Phenology"]
)
async def upload_observation_photos(
    observation_id: UUID,
    photos: dict = Query(..., description="Photo URLs and metadata"),
    db: Session = Depends(get_db)
):
    """
    Upload/attach photos to a phenology observation.

    This is a simplified endpoint. In production, this would handle actual file uploads.
    """
    try:
        observation = db.query(PhenologyObservation).filter(
            PhenologyObservation.id == observation_id
        ).first()

        if not observation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Phenology observation not found"
            )

        # Update photos field
        observation.photos = photos
        db.commit()
        db.refresh(observation)

        return PhenologyObservationInDB.model_validate(observation)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error uploading photos: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading photos: {str(e)}"
        )


@router.get(
    "/timeline/{planting_id}",
    response_model=PhenologyTimeline,
    summary="Get growth timeline for planting",
    tags=["Phenology"]
)
async def get_growth_timeline(
    planting_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get the complete growth timeline for a planting.

    Returns all observations ordered chronologically with planting details.
    """
    try:
        # Verify planting exists
        planting = db.query(Planting).filter(Planting.id == planting_id).first()
        if not planting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planting with id '{planting_id}' not found"
            )

        # Get all observations for this planting
        observations = db.query(PhenologyObservation).filter(
            PhenologyObservation.planting_id == planting_id
        ).order_by(PhenologyObservation.observation_date).all()

        # Calculate days since planting
        from datetime import date as dt_date
        today = dt_date.today()
        days_since_planting = (today - planting.planting_date).days

        # Get current growth stage and latest health score
        latest_obs = db.query(PhenologyObservation).filter(
            PhenologyObservation.planting_id == planting_id
        ).order_by(desc(PhenologyObservation.observation_date)).first()

        current_growth_stage = latest_obs.growth_stage if latest_obs else None
        latest_health_score = latest_obs.health_score if latest_obs else None

        return PhenologyTimeline(
            planting_id=planting_id,
            planting_date=planting.planting_date,
            observations=[PhenologyObservationInDB.model_validate(obs) for obs in observations],
            days_since_planting=days_since_planting,
            current_growth_stage=current_growth_stage,
            latest_health_score=latest_health_score
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting growth timeline: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting growth timeline: {str(e)}"
        )
