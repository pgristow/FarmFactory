"""
Water Quality API endpoints
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
from app.schemas.water_quality import (
    WaterQualityCreate, WaterQualityUpdate, WaterQualityInDB, WaterQualityTrends
)
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.models.water_quality import WaterQuality
from app.models.plot import Plot
from app.utils.query_helpers import (
    apply_pagination, apply_time_series_filters, get_paginated_response, get_total_count
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=WaterQualityInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create water quality test",
    tags=["Water Quality"]
)
async def create_water_quality_test(
    test_data: WaterQualityCreate,
    db: Session = Depends(get_db)
):
    """
    Record a new water quality test.

    - **plot_id**: ID of the plot (required)
    - **time**: Timestamp of test (required)
    - **source**: Water source (well, municipal, reservoir, etc.)
    - **ph_level**: pH level (0-14)
    - **ec_ds_per_m**: Electrical conductivity in dS/m
    - **tds_ppm**: Total dissolved solids in ppm
    - **temperature_celsius**: Water temperature in Celsius
    - **dissolved_oxygen_ppm**: Dissolved oxygen in ppm
    - **turbidity_ntu**: Turbidity in NTU
    - **notes**: Additional notes
    """
    try:
        # Verify plot exists
        plot = db.query(Plot).filter(Plot.id == test_data.plot_id).first()
        if not plot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plot with id '{test_data.plot_id}' not found"
            )

        test = WaterQuality(**test_data.model_dump())
        db.add(test)
        db.commit()
        db.refresh(test)
        return WaterQualityInDB.model_validate(test)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating water quality test: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating water quality test: {str(e)}"
        )


@router.get(
    "/",
    response_model=PaginatedResponse[WaterQualityInDB],
    summary="List water quality tests",
    tags=["Water Quality"]
)
async def list_water_quality_tests(
    pagination: dict = Depends(get_pagination_params),
    plot_id: Optional[UUID] = Query(None, description="Filter by plot ID"),
    start_date: Optional[datetime] = Query(None, description="Start date/time (inclusive)"),
    end_date: Optional[datetime] = Query(None, description="End date/time (inclusive)"),
    source: Optional[str] = Query(None, description="Filter by water source"),
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of water quality tests with filtering.

    Query parameters:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **plot_id**: Filter by plot ID
    - **start_date**: Start date/time
    - **end_date**: End date/time
    - **source**: Filter by water source
    """
    try:
        query = db.query(WaterQuality)

        # Apply time-series filters
        query = apply_time_series_filters(
            query,
            time_field=WaterQuality.time,
            plot_id=plot_id,
            plot_field=WaterQuality.plot_id,
            start_time=start_date,
            end_time=end_date,
            limit=10000
        )

        # Apply source filter
        if source:
            query = query.filter(WaterQuality.source.ilike(f"%{source}%"))

        # Get total count before pagination
        total = get_total_count(query)

        # Apply pagination
        query, skip, limit = apply_pagination(query, pagination["page"], pagination["page_size"])

        tests = query.all()

        return get_paginated_response(
            items=[WaterQualityInDB.model_validate(test) for test in tests],
            total=total,
            page=pagination["page"],
            page_size=pagination["page_size"]
        )
    except Exception as e:
        logger.error(f"Error listing water quality tests: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing water quality tests: {str(e)}"
        )


@router.get(
    "/{plot_id}/{time}",
    response_model=WaterQualityInDB,
    summary="Get water quality test",
    tags=["Water Quality"]
)
async def get_water_quality_test(
    plot_id: UUID,
    time: datetime,
    db: Session = Depends(get_db)
):
    """Get a specific water quality test by plot ID and timestamp (composite key)."""
    test = db.query(WaterQuality).filter(
        WaterQuality.plot_id == plot_id,
        WaterQuality.time == time
    ).first()

    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Water quality test not found"
        )

    return WaterQualityInDB.model_validate(test)


@router.put(
    "/{plot_id}/{time}",
    response_model=WaterQualityInDB,
    summary="Update water quality test",
    tags=["Water Quality"]
)
async def update_water_quality_test(
    plot_id: UUID,
    time: datetime,
    test_data: WaterQualityUpdate,
    db: Session = Depends(get_db)
):
    """Update a water quality test."""
    try:
        test = db.query(WaterQuality).filter(
            WaterQuality.plot_id == plot_id,
            WaterQuality.time == time
        ).first()

        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Water quality test not found"
            )

        # Update only provided fields
        update_data = test_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(test, field, value)

        db.commit()
        db.refresh(test)
        return WaterQualityInDB.model_validate(test)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating water quality test: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating water quality test: {str(e)}"
        )


@router.delete(
    "/{plot_id}/{time}",
    response_model=SuccessResponse,
    summary="Delete water quality test",
    tags=["Water Quality"]
)
async def delete_water_quality_test(
    plot_id: UUID,
    time: datetime,
    db: Session = Depends(get_db)
):
    """Delete a water quality test."""
    try:
        test = db.query(WaterQuality).filter(
            WaterQuality.plot_id == plot_id,
            WaterQuality.time == time
        ).first()

        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Water quality test not found"
            )

        db.delete(test)
        db.commit()

        return SuccessResponse(
            success=True,
            message=f"Water quality test deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting water quality test: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting water quality test: {str(e)}"
        )


@router.get(
    "/trends",
    response_model=WaterQualityTrends,
    summary="Get water quality trends",
    tags=["Water Quality"]
)
async def get_water_quality_trends(
    plot_id: UUID = Query(..., description="Plot ID"),
    parameter: str = Query(..., description="Parameter to analyze (ph_level, ec_ds_per_m, tds_ppm, etc.)"),
    start_date: Optional[datetime] = Query(None, description="Start date/time"),
    end_date: Optional[datetime] = Query(None, description="End date/time"),
    db: Session = Depends(get_db)
):
    """
    Get trends for a specific water quality parameter over time.

    Returns min, max, and average values for the specified parameter.
    """
    try:
        # Verify plot exists
        plot = db.query(Plot).filter(Plot.id == plot_id).first()
        if not plot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plot with id '{plot_id}' not found"
            )

        # Validate parameter
        valid_parameters = ['ph_level', 'ec_ds_per_m', 'tds_ppm', 'temperature_celsius',
                           'dissolved_oxygen_ppm', 'turbidity_ntu']
        if parameter not in valid_parameters:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid parameter. Must be one of: {', '.join(valid_parameters)}"
            )

        query = db.query(WaterQuality).filter(WaterQuality.plot_id == plot_id)

        # Apply date range
        if start_date:
            query = query.filter(WaterQuality.time >= start_date)
        if end_date:
            query = query.filter(WaterQuality.time <= end_date)

        measurement_count = query.count()

        if measurement_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No water quality measurements found for the specified period"
            )

        # Get field to analyze
        field = getattr(WaterQuality, parameter)

        # Calculate statistics
        stats = db.query(
            func.min(field).label('min_value'),
            func.max(field).label('max_value'),
            func.avg(field).label('avg_value')
        ).filter(WaterQuality.plot_id == plot_id)

        if start_date:
            stats = stats.filter(WaterQuality.time >= start_date)
        if end_date:
            stats = stats.filter(WaterQuality.time <= end_date)

        result = stats.first()

        return WaterQualityTrends(
            plot_id=plot_id,
            plot_name=plot.name,
            parameter=parameter,
            period_start=start_date or datetime.min,
            period_end=end_date or datetime.now(),
            min_value=Decimal(str(result.min_value)) if result.min_value is not None else None,
            max_value=Decimal(str(result.max_value)) if result.max_value is not None else None,
            avg_value=Decimal(str(result.avg_value)) if result.avg_value is not None else None,
            measurement_count=measurement_count
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting water quality trends: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting water quality trends: {str(e)}"
        )
