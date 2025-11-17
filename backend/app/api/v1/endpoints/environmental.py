"""
Environmental Readings API endpoints
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
from app.schemas.environmental import (
    EnvironmentalReadingCreate, EnvironmentalReadingBatchCreate,
    EnvironmentalReadingInDB, EnvironmentalReadingLatest, EnvironmentalAverages
)
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.models.environmental import EnvironmentalReading
from app.models.plot import Plot
from app.utils.query_helpers import (
    apply_pagination, apply_time_series_filters, get_paginated_response, get_total_count
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=EnvironmentalReadingInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create environmental reading",
    tags=["Environmental"]
)
async def create_environmental_reading(
    reading_data: EnvironmentalReadingCreate,
    db: Session = Depends(get_db)
):
    """
    Record a new environmental sensor reading.

    - **plot_id**: ID of the plot (required)
    - **time**: Timestamp of reading (required)
    - **air_temp_celsius**: Air temperature in Celsius
    - **soil_temp_celsius**: Soil temperature in Celsius
    - **humidity_percent**: Relative humidity (0-100)
    - **soil_moisture_percent**: Soil moisture (0-100)
    - **light_intensity_lux**: Light intensity in lux
    - **rainfall_mm**: Rainfall in mm
    - **wind_speed_kmh**: Wind speed in km/h
    - **atmospheric_pressure_hpa**: Atmospheric pressure in hPa
    """
    try:
        # Verify plot exists
        plot = db.query(Plot).filter(Plot.id == reading_data.plot_id).first()
        if not plot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plot with id '{reading_data.plot_id}' not found"
            )

        reading = EnvironmentalReading(**reading_data.model_dump())
        db.add(reading)
        db.commit()
        db.refresh(reading)
        return EnvironmentalReadingInDB.model_validate(reading)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating environmental reading: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating environmental reading: {str(e)}"
        )


@router.post(
    "/batch",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Batch create environmental readings",
    tags=["Environmental"]
)
async def batch_create_environmental_readings(
    batch_data: EnvironmentalReadingBatchCreate,
    db: Session = Depends(get_db)
):
    """
    Batch create multiple environmental readings (e.g., from sensors).

    Accepts up to 1000 readings at once for efficient bulk insertion.
    """
    try:
        readings = []
        for reading_data in batch_data.readings:
            reading = EnvironmentalReading(**reading_data.model_dump())
            readings.append(reading)

        db.bulk_save_objects(readings)
        db.commit()

        return SuccessResponse(
            success=True,
            message=f"Successfully created {len(readings)} environmental readings"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error batch creating environmental readings: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error batch creating environmental readings: {str(e)}"
        )


@router.get(
    "/",
    response_model=PaginatedResponse[EnvironmentalReadingInDB],
    summary="List environmental readings",
    tags=["Environmental"]
)
async def list_environmental_readings(
    pagination: dict = Depends(get_pagination_params),
    plot_id: Optional[UUID] = Query(None, description="Filter by plot ID"),
    start_date: Optional[datetime] = Query(None, description="Start date/time (inclusive)"),
    end_date: Optional[datetime] = Query(None, description="End date/time (inclusive)"),
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of environmental readings with filtering.

    Query parameters:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **plot_id**: Filter by plot ID
    - **start_date**: Start date/time
    - **end_date**: End date/time
    """
    try:
        query = db.query(EnvironmentalReading)

        # Apply time-series filters
        query = apply_time_series_filters(
            query,
            time_field=EnvironmentalReading.time,
            plot_id=plot_id,
            plot_field=EnvironmentalReading.plot_id,
            start_time=start_date,
            end_time=end_date,
            limit=10000
        )

        # Get total count before pagination
        total = get_total_count(query)

        # Apply pagination
        query, skip, limit = apply_pagination(query, pagination["page"], pagination["page_size"])

        readings = query.all()

        return get_paginated_response(
            items=[EnvironmentalReadingInDB.model_validate(reading) for reading in readings],
            total=total,
            page=pagination["page"],
            page_size=pagination["page_size"]
        )
    except Exception as e:
        logger.error(f"Error listing environmental readings: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing environmental readings: {str(e)}"
        )


@router.get(
    "/{plot_id}/{time}",
    response_model=EnvironmentalReadingInDB,
    summary="Get environmental reading",
    tags=["Environmental"]
)
async def get_environmental_reading(
    plot_id: UUID,
    time: datetime,
    db: Session = Depends(get_db)
):
    """Get a specific environmental reading by plot ID and timestamp (composite key)."""
    reading = db.query(EnvironmentalReading).filter(
        EnvironmentalReading.plot_id == plot_id,
        EnvironmentalReading.time == time
    ).first()

    if not reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Environmental reading not found"
        )

    return EnvironmentalReadingInDB.model_validate(reading)


@router.delete(
    "/{plot_id}/{time}",
    response_model=SuccessResponse,
    summary="Delete environmental reading",
    tags=["Environmental"]
)
async def delete_environmental_reading(
    plot_id: UUID,
    time: datetime,
    db: Session = Depends(get_db)
):
    """Delete an environmental reading."""
    try:
        reading = db.query(EnvironmentalReading).filter(
            EnvironmentalReading.plot_id == plot_id,
            EnvironmentalReading.time == time
        ).first()

        if not reading:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Environmental reading not found"
            )

        db.delete(reading)
        db.commit()

        return SuccessResponse(
            success=True,
            message=f"Environmental reading deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting environmental reading: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting environmental reading: {str(e)}"
        )


@router.get(
    "/latest",
    response_model=List[EnvironmentalReadingLatest],
    summary="Get latest readings for all plots",
    tags=["Environmental"]
)
async def get_latest_readings(
    db: Session = Depends(get_db)
):
    """
    Get the latest environmental reading for each plot.

    Useful for dashboard displays showing current conditions across all plots.
    """
    try:
        # Get all plots
        plots = db.query(Plot).all()

        results = []
        for plot in plots:
            # Get latest reading for this plot
            latest = db.query(EnvironmentalReading).filter(
                EnvironmentalReading.plot_id == plot.id
            ).order_by(desc(EnvironmentalReading.time)).first()

            results.append(EnvironmentalReadingLatest(
                plot_id=plot.id,
                plot_name=plot.name,
                latest_reading=EnvironmentalReadingInDB.model_validate(latest) if latest else None,
                last_updated=latest.time if latest else None
            ))

        return results
    except Exception as e:
        logger.error(f"Error getting latest readings: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting latest readings: {str(e)}"
        )


@router.get(
    "/averages",
    response_model=EnvironmentalAverages,
    summary="Get period averages",
    tags=["Environmental"]
)
async def get_period_averages(
    plot_id: UUID = Query(..., description="Plot ID"),
    start_date: Optional[datetime] = Query(None, description="Start date/time"),
    end_date: Optional[datetime] = Query(None, description="End date/time"),
    db: Session = Depends(get_db)
):
    """
    Get average environmental values for a specific period.

    Calculates averages for temperature, humidity, moisture, etc.
    """
    try:
        # Verify plot exists
        plot = db.query(Plot).filter(Plot.id == plot_id).first()
        if not plot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plot with id '{plot_id}' not found"
            )

        query = db.query(EnvironmentalReading).filter(EnvironmentalReading.plot_id == plot_id)

        # Apply date range
        if start_date:
            query = query.filter(EnvironmentalReading.time >= start_date)
        if end_date:
            query = query.filter(EnvironmentalReading.time <= end_date)

        # Get count
        reading_count = query.count()

        if reading_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No environmental readings found for the specified period"
            )

        # Calculate averages
        avg_data = db.query(
            func.avg(EnvironmentalReading.air_temp_celsius).label('avg_air_temp'),
            func.avg(EnvironmentalReading.soil_temp_celsius).label('avg_soil_temp'),
            func.avg(EnvironmentalReading.humidity_percent).label('avg_humidity'),
            func.avg(EnvironmentalReading.soil_moisture_percent).label('avg_soil_moisture'),
            func.avg(EnvironmentalReading.light_intensity_lux).label('avg_light'),
            func.sum(EnvironmentalReading.rainfall_mm).label('total_rainfall'),
            func.avg(EnvironmentalReading.wind_speed_kmh).label('avg_wind'),
            func.avg(EnvironmentalReading.atmospheric_pressure_hpa).label('avg_pressure')
        ).filter(EnvironmentalReading.plot_id == plot_id)

        if start_date:
            avg_data = avg_data.filter(EnvironmentalReading.time >= start_date)
        if end_date:
            avg_data = avg_data.filter(EnvironmentalReading.time <= end_date)

        result = avg_data.first()

        return EnvironmentalAverages(
            plot_id=plot_id,
            plot_name=plot.name,
            period_start=start_date or datetime.min,
            period_end=end_date or datetime.now(),
            avg_air_temp=Decimal(str(result.avg_air_temp)) if result.avg_air_temp else None,
            avg_soil_temp=Decimal(str(result.avg_soil_temp)) if result.avg_soil_temp else None,
            avg_humidity=Decimal(str(result.avg_humidity)) if result.avg_humidity else None,
            avg_soil_moisture=Decimal(str(result.avg_soil_moisture)) if result.avg_soil_moisture else None,
            avg_light_intensity=Decimal(str(result.avg_light)) if result.avg_light else None,
            total_rainfall=Decimal(str(result.total_rainfall)) if result.total_rainfall else None,
            avg_wind_speed=Decimal(str(result.avg_wind)) if result.avg_wind else None,
            avg_pressure=Decimal(str(result.avg_pressure)) if result.avg_pressure else None,
            reading_count=reading_count
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting period averages: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting period averages: {str(e)}"
        )
