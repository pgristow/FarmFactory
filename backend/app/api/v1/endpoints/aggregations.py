"""
Time-Series Aggregation API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, List
from uuid import UUID
from datetime import datetime
import logging

from app.core.deps import get_db
from app.services.aggregation_service import (
    aggregate_by_day, aggregate_by_week, aggregate_by_month,
    calculate_summary_stats, calculate_moving_average, compare_periods
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/daily",
    summary="Get daily aggregations",
    tags=["Aggregations"]
)
async def get_daily_aggregations(
    table: str = Query(..., description="Table name (irrigation_events, nutrient_applications, environmental_readings, water_quality)"),
    plot_id: UUID = Query(..., description="Plot ID"),
    start_date: datetime = Query(..., description="Start date/time"),
    end_date: datetime = Query(..., description="End date/time"),
    db: Session = Depends(get_db)
):
    """
    Get daily aggregated data for time-series tables.

    Returns aggregated values grouped by day for the specified date range.

    Example:
    - `table=irrigation_events` returns daily water volume totals
    - `table=environmental_readings` returns daily temperature/humidity averages
    """
    try:
        results = aggregate_by_day(
            db=db,
            table=table,
            plot_id=plot_id,
            start_date=start_date,
            end_date=end_date
        )

        return {
            "success": True,
            "table": table,
            "plot_id": str(plot_id),
            "aggregation": "daily",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "data": results
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting daily aggregations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting daily aggregations: {str(e)}"
        )


@router.get(
    "/weekly",
    summary="Get weekly aggregations",
    tags=["Aggregations"]
)
async def get_weekly_aggregations(
    table: str = Query(..., description="Table name"),
    plot_id: UUID = Query(..., description="Plot ID"),
    start_date: datetime = Query(..., description="Start date/time"),
    end_date: datetime = Query(..., description="End date/time"),
    db: Session = Depends(get_db)
):
    """
    Get weekly aggregated data for time-series tables.

    Returns aggregated values grouped by week for the specified date range.
    """
    try:
        results = aggregate_by_week(
            db=db,
            table=table,
            plot_id=plot_id,
            start_date=start_date,
            end_date=end_date
        )

        return {
            "success": True,
            "table": table,
            "plot_id": str(plot_id),
            "aggregation": "weekly",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "data": results
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting weekly aggregations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting weekly aggregations: {str(e)}"
        )


@router.get(
    "/monthly",
    summary="Get monthly aggregations",
    tags=["Aggregations"]
)
async def get_monthly_aggregations(
    table: str = Query(..., description="Table name"),
    plot_id: UUID = Query(..., description="Plot ID"),
    start_date: datetime = Query(..., description="Start date/time"),
    end_date: datetime = Query(..., description="End date/time"),
    db: Session = Depends(get_db)
):
    """
    Get monthly aggregated data for time-series tables.

    Returns aggregated values grouped by month for the specified date range.
    """
    try:
        results = aggregate_by_month(
            db=db,
            table=table,
            plot_id=plot_id,
            start_date=start_date,
            end_date=end_date
        )

        return {
            "success": True,
            "table": table,
            "plot_id": str(plot_id),
            "aggregation": "monthly",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "data": results
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting monthly aggregations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting monthly aggregations: {str(e)}"
        )


@router.get(
    "/summary",
    summary="Get summary statistics",
    tags=["Aggregations"]
)
async def get_summary_statistics(
    table: str = Query(..., description="Table name"),
    plot_id: UUID = Query(..., description="Plot ID"),
    start_date: datetime = Query(..., description="Start date/time"),
    end_date: datetime = Query(..., description="End date/time"),
    db: Session = Depends(get_db)
):
    """
    Get summary statistics (count, sum, avg, min, max) for all numeric fields.

    Useful for dashboard widgets and overview displays.
    """
    try:
        results = calculate_summary_stats(
            db=db,
            table=table,
            plot_id=plot_id,
            date_range=(start_date, end_date)
        )

        return {
            "success": True,
            "table": table,
            "plot_id": str(plot_id),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "statistics": results
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting summary statistics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting summary statistics: {str(e)}"
        )


@router.get(
    "/compare",
    summary="Compare two time periods",
    tags=["Aggregations"]
)
async def compare_time_periods(
    table: str = Query(..., description="Table name"),
    metric: str = Query(..., description="Metric field name to compare"),
    plot_id: UUID = Query(..., description="Plot ID"),
    period1_start: datetime = Query(..., description="Period 1 start date/time"),
    period1_end: datetime = Query(..., description="Period 1 end date/time"),
    period2_start: datetime = Query(..., description="Period 2 start date/time"),
    period2_end: datetime = Query(..., description="Period 2 end date/time"),
    db: Session = Depends(get_db)
):
    """
    Compare a metric between two time periods.

    Returns statistics for both periods and the percent change.

    Example: Compare average soil moisture between last week and this week.
    """
    try:
        results = compare_periods(
            db=db,
            table=table,
            metric=metric,
            plot_id=plot_id,
            period1=(period1_start, period1_end),
            period2=(period2_start, period2_end)
        )

        return {
            "success": True,
            "comparison": results
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error comparing periods: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error comparing periods: {str(e)}"
        )
