"""
Irrigation Events API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from app.core.deps import get_db, get_pagination_params
from app.schemas.irrigation import (
    IrrigationEventCreate, IrrigationEventUpdate, IrrigationEventInDB, IrrigationSummary
)
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.models.irrigation import IrrigationEvent
from app.models.plot import Plot
from app.utils.query_helpers import (
    apply_pagination, apply_time_series_filters, get_paginated_response, get_total_count
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=IrrigationEventInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create irrigation event",
    tags=["Irrigation"]
)
async def create_irrigation_event(
    event_data: IrrigationEventCreate,
    db: Session = Depends(get_db)
):
    """
    Log a new irrigation event.

    - **plot_id**: ID of the plot (required)
    - **time**: Timestamp of irrigation (required)
    - **method**: Irrigation method (drip, sprinkler, flood, manual)
    - **duration_minutes**: Duration in minutes
    - **water_volume_liters**: Total water volume in liters
    - **water_source**: Water source
    - **flow_rate_lpm**: Flow rate in liters per minute
    - **pressure_bar**: Water pressure in bar
    - **notes**: Additional notes
    """
    try:
        # Verify plot exists
        plot = db.query(Plot).filter(Plot.id == event_data.plot_id).first()
        if not plot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plot with id '{event_data.plot_id}' not found"
            )

        event = IrrigationEvent(**event_data.model_dump())
        db.add(event)
        db.commit()
        db.refresh(event)
        return IrrigationEventInDB.model_validate(event)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating irrigation event: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating irrigation event: {str(e)}"
        )


@router.get(
    "/",
    response_model=PaginatedResponse[IrrigationEventInDB],
    summary="List irrigation events",
    tags=["Irrigation"]
)
async def list_irrigation_events(
    pagination: dict = Depends(get_pagination_params),
    plot_id: Optional[UUID] = Query(None, description="Filter by plot ID"),
    start_date: Optional[datetime] = Query(None, description="Start date/time (inclusive)"),
    end_date: Optional[datetime] = Query(None, description="End date/time (inclusive)"),
    method: Optional[str] = Query(None, description="Filter by irrigation method"),
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of irrigation events with filtering.

    Query parameters:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **plot_id**: Filter by plot ID
    - **start_date**: Start date/time
    - **end_date**: End date/time
    - **method**: Filter by irrigation method
    """
    try:
        query = db.query(IrrigationEvent)

        # Apply time-series filters
        query = apply_time_series_filters(
            query,
            time_field=IrrigationEvent.time,
            plot_id=plot_id,
            plot_field=IrrigationEvent.plot_id,
            start_time=start_date,
            end_time=end_date,
            limit=10000  # Will be overridden by pagination
        )

        # Apply method filter
        if method:
            query = query.filter(IrrigationEvent.method == method.lower())

        # Get total count before pagination
        total = get_total_count(query)

        # Apply pagination
        query, skip, limit = apply_pagination(query, pagination["page"], pagination["page_size"])

        events = query.all()

        return get_paginated_response(
            items=[IrrigationEventInDB.model_validate(event) for event in events],
            total=total,
            page=pagination["page"],
            page_size=pagination["page_size"]
        )
    except Exception as e:
        logger.error(f"Error listing irrigation events: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing irrigation events: {str(e)}"
        )


@router.get(
    "/{plot_id}/{time}",
    response_model=IrrigationEventInDB,
    summary="Get irrigation event",
    tags=["Irrigation"]
)
async def get_irrigation_event(
    plot_id: UUID,
    time: datetime,
    db: Session = Depends(get_db)
):
    """Get a specific irrigation event by plot ID and timestamp (composite key)."""
    event = db.query(IrrigationEvent).filter(
        IrrigationEvent.plot_id == plot_id,
        IrrigationEvent.time == time
    ).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Irrigation event not found"
        )

    return IrrigationEventInDB.model_validate(event)


@router.put(
    "/{plot_id}/{time}",
    response_model=IrrigationEventInDB,
    summary="Update irrigation event",
    tags=["Irrigation"]
)
async def update_irrigation_event(
    plot_id: UUID,
    time: datetime,
    event_data: IrrigationEventUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an irrigation event.

    Only the fields provided in the request body will be updated.
    """
    try:
        event = db.query(IrrigationEvent).filter(
            IrrigationEvent.plot_id == plot_id,
            IrrigationEvent.time == time
        ).first()

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Irrigation event not found"
            )

        # Update only provided fields
        update_data = event_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(event, field, value)

        db.commit()
        db.refresh(event)
        return IrrigationEventInDB.model_validate(event)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating irrigation event: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating irrigation event: {str(e)}"
        )


@router.delete(
    "/{plot_id}/{time}",
    response_model=SuccessResponse,
    summary="Delete irrigation event",
    tags=["Irrigation"]
)
async def delete_irrigation_event(
    plot_id: UUID,
    time: datetime,
    db: Session = Depends(get_db)
):
    """Delete an irrigation event."""
    try:
        event = db.query(IrrigationEvent).filter(
            IrrigationEvent.plot_id == plot_id,
            IrrigationEvent.time == time
        ).first()

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Irrigation event not found"
            )

        db.delete(event)
        db.commit()

        return SuccessResponse(
            success=True,
            message=f"Irrigation event deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting irrigation event: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting irrigation event: {str(e)}"
        )


@router.get(
    "/summary",
    response_model=IrrigationSummary,
    summary="Get irrigation summary",
    tags=["Irrigation"]
)
async def get_irrigation_summary(
    plot_id: UUID = Query(..., description="Plot ID"),
    start_date: Optional[datetime] = Query(None, description="Start date/time"),
    end_date: Optional[datetime] = Query(None, description="End date/time"),
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for irrigation events.

    Returns total events, total water volume, average duration, most common method, etc.
    """
    try:
        # Verify plot exists
        plot = db.query(Plot).filter(Plot.id == plot_id).first()
        if not plot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plot with id '{plot_id}' not found"
            )

        query = db.query(IrrigationEvent).filter(IrrigationEvent.plot_id == plot_id)

        # Apply date range
        if start_date:
            query = query.filter(IrrigationEvent.time >= start_date)
        if end_date:
            query = query.filter(IrrigationEvent.time <= end_date)

        # Calculate statistics
        total_events = query.count()

        if total_events == 0:
            return IrrigationSummary(
                plot_id=plot_id,
                plot_name=plot.name,
                total_events=0,
                total_water_liters=Decimal("0.00"),
                average_duration_minutes=None,
                most_common_method=None,
                last_irrigation=None
            )

        total_water = db.query(func.sum(IrrigationEvent.water_volume_liters)).filter(
            IrrigationEvent.plot_id == plot_id
        )
        if start_date:
            total_water = total_water.filter(IrrigationEvent.time >= start_date)
        if end_date:
            total_water = total_water.filter(IrrigationEvent.time <= end_date)
        total_water = total_water.scalar() or Decimal("0.00")

        avg_duration = db.query(func.avg(IrrigationEvent.duration_minutes)).filter(
            IrrigationEvent.plot_id == plot_id
        )
        if start_date:
            avg_duration = avg_duration.filter(IrrigationEvent.time >= start_date)
        if end_date:
            avg_duration = avg_duration.filter(IrrigationEvent.time <= end_date)
        avg_duration = avg_duration.scalar()

        # Get most common method
        method_query = db.query(
            IrrigationEvent.method,
            func.count(IrrigationEvent.method).label('count')
        ).filter(IrrigationEvent.plot_id == plot_id)
        if start_date:
            method_query = method_query.filter(IrrigationEvent.time >= start_date)
        if end_date:
            method_query = method_query.filter(IrrigationEvent.time <= end_date)

        most_common = method_query.group_by(IrrigationEvent.method).order_by(
            desc('count')
        ).first()

        most_common_method = most_common[0] if most_common else None

        # Get last irrigation
        last_irrigation_query = db.query(IrrigationEvent).filter(
            IrrigationEvent.plot_id == plot_id
        ).order_by(desc(IrrigationEvent.time))
        if end_date:
            last_irrigation_query = last_irrigation_query.filter(IrrigationEvent.time <= end_date)

        last_irrigation = last_irrigation_query.first()
        last_irrigation_time = last_irrigation.time if last_irrigation else None

        return IrrigationSummary(
            plot_id=plot_id,
            plot_name=plot.name,
            total_events=total_events,
            total_water_liters=Decimal(str(total_water)),
            average_duration_minutes=Decimal(str(avg_duration)) if avg_duration else None,
            most_common_method=most_common_method,
            last_irrigation=last_irrigation_time
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting irrigation summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting irrigation summary: {str(e)}"
        )
