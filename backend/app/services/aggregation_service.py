"""
Time-Series Data Aggregation Service

Provides aggregation functions for time-series data using TimescaleDB
and standard PostgreSQL functions for efficient data summarization.
"""
from typing import Any, Optional, List, Dict, Tuple
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func, text, and_
from decimal import Decimal
import logging

from app.models.irrigation import IrrigationEvent
from app.models.nutrient import NutrientApplication
from app.models.environmental import EnvironmentalReading
from app.models.water_quality import WaterQuality

logger = logging.getLogger(__name__)


def aggregate_by_day(
    db: Session,
    table: str,
    plot_id: Any,
    start_date: datetime,
    end_date: datetime,
    aggregation_fields: Optional[Dict[str, str]] = None
) -> List[Dict]:
    """
    Aggregate time-series data by day.

    Args:
        db: Database session
        table: Table name (irrigation_events, nutrient_applications, environmental_readings, water_quality)
        plot_id: Plot ID to filter by
        start_date: Start date for aggregation
        end_date: End date for aggregation
        aggregation_fields: Dict of field names to aggregation functions (SUM, AVG, MIN, MAX, COUNT)

    Returns:
        List of dictionaries with daily aggregated data
    """
    try:
        # Map table names to models
        table_models = {
            'irrigation_events': IrrigationEvent,
            'nutrient_applications': NutrientApplication,
            'environmental_readings': EnvironmentalReading,
            'water_quality': WaterQuality
        }

        if table not in table_models:
            raise ValueError(f"Unknown table: {table}")

        model = table_models[table]

        # Default aggregation fields based on table
        if aggregation_fields is None:
            aggregation_fields = _get_default_aggregation_fields(table)

        # Build query using time_bucket for daily aggregation
        # For standard PostgreSQL, use date_trunc
        query = db.query(
            func.date_trunc('day', model.time).label('day')
        )

        # Add aggregation fields
        for field_name, agg_func in aggregation_fields.items():
            if hasattr(model, field_name):
                field = getattr(model, field_name)
                if agg_func.upper() == 'SUM':
                    query = query.add_columns(func.sum(field).label(f'sum_{field_name}'))
                elif agg_func.upper() == 'AVG':
                    query = query.add_columns(func.avg(field).label(f'avg_{field_name}'))
                elif agg_func.upper() == 'MIN':
                    query = query.add_columns(func.min(field).label(f'min_{field_name}'))
                elif agg_func.upper() == 'MAX':
                    query = query.add_columns(func.max(field).label(f'max_{field_name}'))
                elif agg_func.upper() == 'COUNT':
                    query = query.add_columns(func.count(field).label(f'count_{field_name}'))

        # Apply filters
        query = query.filter(
            and_(
                model.plot_id == plot_id,
                model.time >= start_date,
                model.time <= end_date
            )
        )

        # Group by day
        query = query.group_by(func.date_trunc('day', model.time))
        query = query.order_by(func.date_trunc('day', model.time))

        results = query.all()

        # Convert to list of dictionaries
        return _format_aggregation_results(results)

    except Exception as e:
        logger.error(f"Error in aggregate_by_day: {e}", exc_info=True)
        raise


def aggregate_by_week(
    db: Session,
    table: str,
    plot_id: Any,
    start_date: datetime,
    end_date: datetime,
    aggregation_fields: Optional[Dict[str, str]] = None
) -> List[Dict]:
    """
    Aggregate time-series data by week.

    Args:
        db: Database session
        table: Table name
        plot_id: Plot ID to filter by
        start_date: Start date for aggregation
        end_date: End date for aggregation
        aggregation_fields: Dict of field names to aggregation functions

    Returns:
        List of dictionaries with weekly aggregated data
    """
    try:
        table_models = {
            'irrigation_events': IrrigationEvent,
            'nutrient_applications': NutrientApplication,
            'environmental_readings': EnvironmentalReading,
            'water_quality': WaterQuality
        }

        if table not in table_models:
            raise ValueError(f"Unknown table: {table}")

        model = table_models[table]

        if aggregation_fields is None:
            aggregation_fields = _get_default_aggregation_fields(table)

        # Build query using date_trunc for weekly aggregation
        query = db.query(
            func.date_trunc('week', model.time).label('week')
        )

        # Add aggregation fields
        for field_name, agg_func in aggregation_fields.items():
            if hasattr(model, field_name):
                field = getattr(model, field_name)
                if agg_func.upper() == 'SUM':
                    query = query.add_columns(func.sum(field).label(f'sum_{field_name}'))
                elif agg_func.upper() == 'AVG':
                    query = query.add_columns(func.avg(field).label(f'avg_{field_name}'))
                elif agg_func.upper() == 'MIN':
                    query = query.add_columns(func.min(field).label(f'min_{field_name}'))
                elif agg_func.upper() == 'MAX':
                    query = query.add_columns(func.max(field).label(f'max_{field_name}'))
                elif agg_func.upper() == 'COUNT':
                    query = query.add_columns(func.count(field).label(f'count_{field_name}'))

        # Apply filters
        query = query.filter(
            and_(
                model.plot_id == plot_id,
                model.time >= start_date,
                model.time <= end_date
            )
        )

        # Group by week
        query = query.group_by(func.date_trunc('week', model.time))
        query = query.order_by(func.date_trunc('week', model.time))

        results = query.all()

        return _format_aggregation_results(results)

    except Exception as e:
        logger.error(f"Error in aggregate_by_week: {e}", exc_info=True)
        raise


def aggregate_by_month(
    db: Session,
    table: str,
    plot_id: Any,
    start_date: datetime,
    end_date: datetime,
    aggregation_fields: Optional[Dict[str, str]] = None
) -> List[Dict]:
    """
    Aggregate time-series data by month.

    Args:
        db: Database session
        table: Table name
        plot_id: Plot ID to filter by
        start_date: Start date for aggregation
        end_date: End date for aggregation
        aggregation_fields: Dict of field names to aggregation functions

    Returns:
        List of dictionaries with monthly aggregated data
    """
    try:
        table_models = {
            'irrigation_events': IrrigationEvent,
            'nutrient_applications': NutrientApplication,
            'environmental_readings': EnvironmentalReading,
            'water_quality': WaterQuality
        }

        if table not in table_models:
            raise ValueError(f"Unknown table: {table}")

        model = table_models[table]

        if aggregation_fields is None:
            aggregation_fields = _get_default_aggregation_fields(table)

        # Build query using date_trunc for monthly aggregation
        query = db.query(
            func.date_trunc('month', model.time).label('month')
        )

        # Add aggregation fields
        for field_name, agg_func in aggregation_fields.items():
            if hasattr(model, field_name):
                field = getattr(model, field_name)
                if agg_func.upper() == 'SUM':
                    query = query.add_columns(func.sum(field).label(f'sum_{field_name}'))
                elif agg_func.upper() == 'AVG':
                    query = query.add_columns(func.avg(field).label(f'avg_{field_name}'))
                elif agg_func.upper() == 'MIN':
                    query = query.add_columns(func.min(field).label(f'min_{field_name}'))
                elif agg_func.upper() == 'MAX':
                    query = query.add_columns(func.max(field).label(f'max_{field_name}'))
                elif agg_func.upper() == 'COUNT':
                    query = query.add_columns(func.count(field).label(f'count_{field_name}'))

        # Apply filters
        query = query.filter(
            and_(
                model.plot_id == plot_id,
                model.time >= start_date,
                model.time <= end_date
            )
        )

        # Group by month
        query = query.group_by(func.date_trunc('month', model.time))
        query = query.order_by(func.date_trunc('month', model.time))

        results = query.all()

        return _format_aggregation_results(results)

    except Exception as e:
        logger.error(f"Error in aggregate_by_month: {e}", exc_info=True)
        raise


def calculate_summary_stats(
    db: Session,
    table: str,
    plot_id: Any,
    date_range: Tuple[datetime, datetime],
    fields: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Calculate summary statistics for specified fields.

    Args:
        db: Database session
        table: Table name
        plot_id: Plot ID to filter by
        date_range: Tuple of (start_date, end_date)
        fields: List of field names to calculate stats for

    Returns:
        Dictionary with summary statistics (count, sum, avg, min, max) for each field
    """
    try:
        table_models = {
            'irrigation_events': IrrigationEvent,
            'nutrient_applications': NutrientApplication,
            'environmental_readings': EnvironmentalReading,
            'water_quality': WaterQuality
        }

        if table not in table_models:
            raise ValueError(f"Unknown table: {table}")

        model = table_models[table]
        start_date, end_date = date_range

        if fields is None:
            fields = _get_numeric_fields(table)

        stats = {}

        for field_name in fields:
            if hasattr(model, field_name):
                field = getattr(model, field_name)

                # Calculate statistics
                result = db.query(
                    func.count(field).label('count'),
                    func.sum(field).label('sum'),
                    func.avg(field).label('avg'),
                    func.min(field).label('min'),
                    func.max(field).label('max')
                ).filter(
                    and_(
                        model.plot_id == plot_id,
                        model.time >= start_date,
                        model.time <= end_date
                    )
                ).first()

                stats[field_name] = {
                    'count': result.count if result else 0,
                    'sum': float(result.sum) if result.sum is not None else None,
                    'avg': float(result.avg) if result.avg is not None else None,
                    'min': float(result.min) if result.min is not None else None,
                    'max': float(result.max) if result.max is not None else None
                }

        return stats

    except Exception as e:
        logger.error(f"Error calculating summary stats: {e}", exc_info=True)
        raise


def calculate_moving_average(
    data: List[Dict],
    window_days: int,
    field_name: str
) -> List[Dict]:
    """
    Calculate moving average for a time-series dataset.

    Args:
        data: List of data points with 'time' and field values
        window_days: Number of days for the moving average window
        field_name: Name of the field to calculate moving average for

    Returns:
        List of data points with added moving average field
    """
    try:
        if not data or len(data) < window_days:
            return data

        result = []
        for i, point in enumerate(data):
            # Calculate average of current point and previous (window_days - 1) points
            start_idx = max(0, i - window_days + 1)
            window_data = data[start_idx:i+1]

            values = [p.get(field_name) for p in window_data if p.get(field_name) is not None]
            if values:
                moving_avg = sum(values) / len(values)
            else:
                moving_avg = None

            result_point = point.copy()
            result_point[f'{field_name}_ma{window_days}'] = moving_avg
            result.append(result_point)

        return result

    except Exception as e:
        logger.error(f"Error calculating moving average: {e}", exc_info=True)
        raise


def compare_periods(
    db: Session,
    table: str,
    metric: str,
    plot_id: Any,
    period1: Tuple[datetime, datetime],
    period2: Tuple[datetime, datetime]
) -> Dict[str, Any]:
    """
    Compare a metric between two time periods.

    Args:
        db: Database session
        table: Table name
        metric: Metric field name to compare
        plot_id: Plot ID to filter by
        period1: First period (start_date, end_date)
        period2: Second period (start_date, end_date)

    Returns:
        Dictionary with comparison statistics and percent change
    """
    try:
        # Get stats for period 1
        stats1 = calculate_summary_stats(db, table, plot_id, period1, [metric])

        # Get stats for period 2
        stats2 = calculate_summary_stats(db, table, plot_id, period2, [metric])

        # Calculate percent change
        percent_change = None
        if stats1[metric]['avg'] is not None and stats2[metric]['avg'] is not None:
            if stats1[metric]['avg'] != 0:
                percent_change = ((stats2[metric]['avg'] - stats1[metric]['avg']) /
                                stats1[metric]['avg']) * 100

        return {
            'metric': metric,
            'period1': {
                'start': period1[0],
                'end': period1[1],
                'stats': stats1[metric]
            },
            'period2': {
                'start': period2[0],
                'end': period2[1],
                'stats': stats2[metric]
            },
            'percent_change': percent_change
        }

    except Exception as e:
        logger.error(f"Error comparing periods: {e}", exc_info=True)
        raise


# Helper functions

def _get_default_aggregation_fields(table: str) -> Dict[str, str]:
    """Get default aggregation fields for a table."""
    defaults = {
        'irrigation_events': {
            'water_volume_liters': 'SUM',
            'duration_minutes': 'AVG'
        },
        'nutrient_applications': {
            'nitrogen_kg': 'SUM',
            'phosphorus_kg': 'SUM',
            'potassium_kg': 'SUM',
            'cost_usd': 'SUM'
        },
        'environmental_readings': {
            'air_temp_celsius': 'AVG',
            'soil_temp_celsius': 'AVG',
            'humidity_percent': 'AVG',
            'soil_moisture_percent': 'AVG',
            'rainfall_mm': 'SUM'
        },
        'water_quality': {
            'ph_level': 'AVG',
            'ec_ds_per_m': 'AVG',
            'tds_ppm': 'AVG'
        }
    }
    return defaults.get(table, {})


def _get_numeric_fields(table: str) -> List[str]:
    """Get numeric fields for a table."""
    fields = {
        'irrigation_events': ['water_volume_liters', 'duration_minutes', 'flow_rate_lpm', 'pressure_bar'],
        'nutrient_applications': ['amount_kg', 'nitrogen_kg', 'phosphorus_kg', 'potassium_kg', 'cost_usd'],
        'environmental_readings': ['air_temp_celsius', 'soil_temp_celsius', 'humidity_percent',
                                  'soil_moisture_percent', 'light_intensity_lux', 'rainfall_mm',
                                  'wind_speed_kmh', 'atmospheric_pressure_hpa'],
        'water_quality': ['ph_level', 'ec_ds_per_m', 'tds_ppm', 'temperature_celsius',
                         'dissolved_oxygen_ppm', 'turbidity_ntu']
    }
    return fields.get(table, [])


def _format_aggregation_results(results: List[Any]) -> List[Dict]:
    """Format SQLAlchemy result rows to dictionaries."""
    formatted = []
    for row in results:
        row_dict = {}
        for key, value in row._mapping.items():
            if isinstance(value, Decimal):
                row_dict[key] = float(value)
            elif isinstance(value, (datetime, date)):
                row_dict[key] = value.isoformat()
            else:
                row_dict[key] = value
        formatted.append(row_dict)
    return formatted
