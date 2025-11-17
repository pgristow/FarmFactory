"""
Nutrient Applications API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
import logging

from app.core.deps import get_db, get_pagination_params
from app.schemas.nutrient import (
    NutrientApplicationCreate, NutrientApplicationUpdate,
    NutrientApplicationInDB, NutrientSummary
)
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.models.nutrient import NutrientApplication
from app.models.plot import Plot
from app.utils.query_helpers import (
    apply_pagination, apply_time_series_filters, get_paginated_response, get_total_count
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=NutrientApplicationInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create nutrient application",
    tags=["Nutrients"]
)
async def create_nutrient_application(
    application_data: NutrientApplicationCreate,
    db: Session = Depends(get_db)
):
    """
    Log a new nutrient application event.

    - **plot_id**: ID of the plot (required)
    - **time**: Timestamp of application (required)
    - **nutrient_type**: Type of nutrient (N, P, K, Compost, etc.)
    - **application_method**: Application method (broadcast, fertigation, foliar, etc.)
    - **amount_kg**: Amount applied in kg
    - **npk_ratio**: NPK ratio (e.g., '10-10-10')
    - **nitrogen_kg**: Nitrogen content in kg
    - **phosphorus_kg**: Phosphorus content in kg
    - **potassium_kg**: Potassium content in kg
    - **cost_usd**: Cost in USD
    - **notes**: Additional notes
    """
    try:
        # Verify plot exists
        plot = db.query(Plot).filter(Plot.id == application_data.plot_id).first()
        if not plot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plot with id '{application_data.plot_id}' not found"
            )

        application = NutrientApplication(**application_data.model_dump())
        db.add(application)
        db.commit()
        db.refresh(application)
        return NutrientApplicationInDB.model_validate(application)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating nutrient application: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating nutrient application: {str(e)}"
        )


@router.get(
    "/",
    response_model=PaginatedResponse[NutrientApplicationInDB],
    summary="List nutrient applications",
    tags=["Nutrients"]
)
async def list_nutrient_applications(
    pagination: dict = Depends(get_pagination_params),
    plot_id: Optional[UUID] = Query(None, description="Filter by plot ID"),
    start_date: Optional[datetime] = Query(None, description="Start date/time (inclusive)"),
    end_date: Optional[datetime] = Query(None, description="End date/time (inclusive)"),
    nutrient_type: Optional[str] = Query(None, description="Filter by nutrient type"),
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of nutrient applications with filtering.

    Query parameters:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **plot_id**: Filter by plot ID
    - **start_date**: Start date/time
    - **end_date**: End date/time
    - **nutrient_type**: Filter by nutrient type
    """
    try:
        query = db.query(NutrientApplication)

        # Apply time-series filters
        query = apply_time_series_filters(
            query,
            time_field=NutrientApplication.time,
            plot_id=plot_id,
            plot_field=NutrientApplication.plot_id,
            start_time=start_date,
            end_time=end_date,
            limit=10000
        )

        # Apply nutrient type filter
        if nutrient_type:
            query = query.filter(NutrientApplication.nutrient_type.ilike(f"%{nutrient_type}%"))

        # Get total count before pagination
        total = get_total_count(query)

        # Apply pagination
        query, skip, limit = apply_pagination(query, pagination["page"], pagination["page_size"])

        applications = query.all()

        return get_paginated_response(
            items=[NutrientApplicationInDB.model_validate(app) for app in applications],
            total=total,
            page=pagination["page"],
            page_size=pagination["page_size"]
        )
    except Exception as e:
        logger.error(f"Error listing nutrient applications: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing nutrient applications: {str(e)}"
        )


@router.get(
    "/{plot_id}/{time}",
    response_model=NutrientApplicationInDB,
    summary="Get nutrient application",
    tags=["Nutrients"]
)
async def get_nutrient_application(
    plot_id: UUID,
    time: datetime,
    db: Session = Depends(get_db)
):
    """Get a specific nutrient application by plot ID and timestamp (composite key)."""
    application = db.query(NutrientApplication).filter(
        NutrientApplication.plot_id == plot_id,
        NutrientApplication.time == time
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nutrient application not found"
        )

    return NutrientApplicationInDB.model_validate(application)


@router.put(
    "/{plot_id}/{time}",
    response_model=NutrientApplicationInDB,
    summary="Update nutrient application",
    tags=["Nutrients"]
)
async def update_nutrient_application(
    plot_id: UUID,
    time: datetime,
    application_data: NutrientApplicationUpdate,
    db: Session = Depends(get_db)
):
    """Update a nutrient application."""
    try:
        application = db.query(NutrientApplication).filter(
            NutrientApplication.plot_id == plot_id,
            NutrientApplication.time == time
        ).first()

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Nutrient application not found"
            )

        # Update only provided fields
        update_data = application_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(application, field, value)

        db.commit()
        db.refresh(application)
        return NutrientApplicationInDB.model_validate(application)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating nutrient application: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating nutrient application: {str(e)}"
        )


@router.delete(
    "/{plot_id}/{time}",
    response_model=SuccessResponse,
    summary="Delete nutrient application",
    tags=["Nutrients"]
)
async def delete_nutrient_application(
    plot_id: UUID,
    time: datetime,
    db: Session = Depends(get_db)
):
    """Delete a nutrient application."""
    try:
        application = db.query(NutrientApplication).filter(
            NutrientApplication.plot_id == plot_id,
            NutrientApplication.time == time
        ).first()

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Nutrient application not found"
            )

        db.delete(application)
        db.commit()

        return SuccessResponse(
            success=True,
            message=f"Nutrient application deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting nutrient application: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting nutrient application: {str(e)}"
        )


@router.get(
    "/npk-balance",
    response_model=NutrientSummary,
    summary="Get NPK balance",
    tags=["Nutrients"]
)
async def get_npk_balance(
    plot_id: UUID = Query(..., description="Plot ID"),
    start_date: Optional[datetime] = Query(None, description="Start date/time"),
    end_date: Optional[datetime] = Query(None, description="End date/time"),
    db: Session = Depends(get_db)
):
    """
    Get NPK balance and nutrient summary for a plot.

    Returns total applications, total NPK amounts, and costs.
    """
    try:
        # Verify plot exists
        plot = db.query(Plot).filter(Plot.id == plot_id).first()
        if not plot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plot with id '{plot_id}' not found"
            )

        query = db.query(NutrientApplication).filter(NutrientApplication.plot_id == plot_id)

        # Apply date range
        if start_date:
            query = query.filter(NutrientApplication.time >= start_date)
        if end_date:
            query = query.filter(NutrientApplication.time <= end_date)

        # Calculate statistics
        total_applications = query.count()

        if total_applications == 0:
            return NutrientSummary(
                plot_id=plot_id,
                plot_name=plot.name,
                total_applications=0,
                total_nitrogen_kg=Decimal("0.00"),
                total_phosphorus_kg=Decimal("0.00"),
                total_potassium_kg=Decimal("0.00"),
                total_cost_usd=Decimal("0.00"),
                last_application=None
            )

        # Sum NPK values
        total_n = db.query(func.sum(NutrientApplication.nitrogen_kg)).filter(
            NutrientApplication.plot_id == plot_id
        )
        if start_date:
            total_n = total_n.filter(NutrientApplication.time >= start_date)
        if end_date:
            total_n = total_n.filter(NutrientApplication.time <= end_date)
        total_n = total_n.scalar() or Decimal("0.00")

        total_p = db.query(func.sum(NutrientApplication.phosphorus_kg)).filter(
            NutrientApplication.plot_id == plot_id
        )
        if start_date:
            total_p = total_p.filter(NutrientApplication.time >= start_date)
        if end_date:
            total_p = total_p.filter(NutrientApplication.time <= end_date)
        total_p = total_p.scalar() or Decimal("0.00")

        total_k = db.query(func.sum(NutrientApplication.potassium_kg)).filter(
            NutrientApplication.plot_id == plot_id
        )
        if start_date:
            total_k = total_k.filter(NutrientApplication.time >= start_date)
        if end_date:
            total_k = total_k.filter(NutrientApplication.time <= end_date)
        total_k = total_k.scalar() or Decimal("0.00")

        # Sum costs
        total_cost = db.query(func.sum(NutrientApplication.cost_usd)).filter(
            NutrientApplication.plot_id == plot_id
        )
        if start_date:
            total_cost = total_cost.filter(NutrientApplication.time >= start_date)
        if end_date:
            total_cost = total_cost.filter(NutrientApplication.time <= end_date)
        total_cost = total_cost.scalar() or Decimal("0.00")

        # Get last application
        last_application_query = db.query(NutrientApplication).filter(
            NutrientApplication.plot_id == plot_id
        ).order_by(desc(NutrientApplication.time))
        if end_date:
            last_application_query = last_application_query.filter(NutrientApplication.time <= end_date)

        last_application = last_application_query.first()
        last_application_time = last_application.time if last_application else None

        return NutrientSummary(
            plot_id=plot_id,
            plot_name=plot.name,
            total_applications=total_applications,
            total_nitrogen_kg=Decimal(str(total_n)),
            total_phosphorus_kg=Decimal(str(total_p)),
            total_potassium_kg=Decimal(str(total_k)),
            total_cost_usd=Decimal(str(total_cost)),
            last_application=last_application_time
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting NPK balance: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting NPK balance: {str(e)}"
        )
