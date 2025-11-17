"""
Data Aggregation Logic for Time-Series Data

This module provides functions for aggregating time-series farm data
by different time periods (hour, day, week, month) and calculating
KPIs and metrics for dashboards.

Author: Data Engineer
Created: 2025-11-17
Sprint: 3
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Literal
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
import pandas as pd
import json


AggregationPeriod = Literal['hour', 'day', 'week', 'month', 'year']
AggregationType = Literal['sum', 'avg', 'min', 'max', 'count', 'cumulative_sum']


def aggregate_by_period(
    data: List[Dict[str, Any]],
    time_field: str,
    value_fields: List[str],
    period: AggregationPeriod = 'day',
    aggregation_type: AggregationType = 'sum'
) -> List[Dict[str, Any]]:
    """
    Aggregate time-series data by specified period.

    Args:
        data: List of data dictionaries with timestamp and values
        time_field: Name of the timestamp field
        value_fields: List of field names to aggregate
        period: Time period for aggregation ('hour', 'day', 'week', 'month', 'year')
        aggregation_type: Type of aggregation ('sum', 'avg', 'min', 'max', 'count', 'cumulative_sum')

    Returns:
        List of aggregated data dictionaries

    Example:
        >>> data = [
        ...     {'date': '2025-11-01', 'volume': 100},
        ...     {'date': '2025-11-01', 'volume': 150},
        ...     {'date': '2025-11-02', 'volume': 200}
        ... ]
        >>> aggregate_by_period(data, 'date', ['volume'], 'day', 'sum')
        [{'date': '2025-11-01', 'volume': 250}, {'date': '2025-11-02', 'volume': 200}]
    """
    if not data:
        return []

    # Convert to pandas DataFrame for easier aggregation
    df = pd.DataFrame(data)

    # Convert time field to datetime
    df[time_field] = pd.to_datetime(df[time_field])

    # Set up period grouping
    period_map = {
        'hour': 'H',
        'day': 'D',
        'week': 'W',
        'month': 'M',
        'year': 'Y'
    }

    freq = period_map.get(period, 'D')

    # Group by period
    grouped = df.groupby(pd.Grouper(key=time_field, freq=freq))

    # Apply aggregation
    if aggregation_type == 'sum':
        aggregated = grouped[value_fields].sum()
    elif aggregation_type == 'avg':
        aggregated = grouped[value_fields].mean()
    elif aggregation_type == 'min':
        aggregated = grouped[value_fields].min()
    elif aggregation_type == 'max':
        aggregated = grouped[value_fields].max()
    elif aggregation_type == 'count':
        aggregated = grouped[value_fields].count()
    elif aggregation_type == 'cumulative_sum':
        aggregated = df[value_fields].cumsum()
        aggregated[time_field] = df[time_field]
        return aggregated.to_dict('records')
    else:
        raise ValueError(f"Unknown aggregation type: {aggregation_type}")

    # Reset index and convert back to list of dicts
    aggregated = aggregated.reset_index()

    return aggregated.to_dict('records')


def calculate_daily_summary(
    db: Session,
    table_model: Any,
    date_field: str,
    value_fields: Dict[str, str],
    date_range: tuple[datetime, datetime],
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Calculate daily summaries for dashboard metrics.

    Args:
        db: Database session
        table_model: SQLAlchemy model class
        date_field: Name of the date/datetime field in the model
        value_fields: Dict mapping field names to aggregation types
                     e.g., {'volume_liters': 'sum', 'temperature': 'avg'}
        date_range: Tuple of (start_date, end_date)
        filters: Optional additional filters as field: value dict

    Returns:
        List of daily summary dictionaries

    Example:
        >>> calculate_daily_summary(
        ...     db, IrrigationEvent, 'event_date',
        ...     {'volume_liters': 'sum', 'duration_hours': 'avg'},
        ...     (datetime(2025, 11, 1), datetime(2025, 11, 30)),
        ...     {'plot_id': 101}
        ... )
    """
    start_date, end_date = date_range

    # Build base query
    query = db.query(
        func.date_trunc('day', getattr(table_model, date_field)).label('date')
    )

    # Add aggregation fields
    for field_name, agg_type in value_fields.items():
        field = getattr(table_model, field_name)
        if agg_type == 'sum':
            query = query.add_columns(func.sum(field).label(f'{field_name}_sum'))
        elif agg_type == 'avg':
            query = query.add_columns(func.avg(field).label(f'{field_name}_avg'))
        elif agg_type == 'min':
            query = query.add_columns(func.min(field).label(f'{field_name}_min'))
        elif agg_type == 'max':
            query = query.add_columns(func.max(field).label(f'{field_name}_max'))
        elif agg_type == 'count':
            query = query.add_columns(func.count(field).label(f'{field_name}_count'))

    # Apply date range filter
    date_column = getattr(table_model, date_field)
    query = query.filter(and_(
        date_column >= start_date,
        date_column <= end_date
    ))

    # Apply additional filters
    if filters:
        for field_name, value in filters.items():
            query = query.filter(getattr(table_model, field_name) == value)

    # Group by date
    query = query.group_by(func.date_trunc('day', getattr(table_model, date_field)))
    query = query.order_by('date')

    # Execute and return results
    results = query.all()

    return [
        {
            'date': row.date,
            **{col: getattr(row, col) for col in row._fields if col != 'date'}
        }
        for row in results
    ]


def calculate_kpi(
    db: Session,
    kpi_name: str,
    plot_id: Optional[int] = None,
    date_range: Optional[tuple[datetime, datetime]] = None,
    kpi_definitions_path: str = '/home/user/FarmFactory/backend/app/metrics_config/kpi_definitions.json'
) -> Dict[str, Any]:
    """
    Calculate specific KPI value based on KPI definitions.

    Args:
        db: Database session
        kpi_name: Name of the KPI to calculate (from kpi_definitions.json)
        plot_id: Optional plot ID to filter by
        date_range: Optional date range tuple (start_date, end_date)
        kpi_definitions_path: Path to KPI definitions JSON file

    Returns:
        Dictionary with KPI value, unit, and metadata

    Example:
        >>> calculate_kpi(db, 'total_water_used_30d', plot_id=101)
        {
            'name': 'Total Water Used (30 Days)',
            'value': 45000,
            'unit': 'liters',
            'threshold_status': 'good',
            'color': '#4CAF50'
        }
    """
    # Load KPI definitions
    with open(kpi_definitions_path, 'r') as f:
        kpi_config = json.load(f)

    # Find the KPI definition
    kpi_def = None
    for category, kpis in kpi_config['kpis'].items():
        if kpi_name in kpis:
            kpi_def = kpis[kpi_name]
            break

    if not kpi_def:
        raise ValueError(f"KPI '{kpi_name}' not found in definitions")

    # Note: Actual implementation would execute the formula
    # This is a placeholder that returns structure
    result = {
        'name': kpi_def['name'],
        'value': None,  # Would be calculated from formula
        'unit': kpi_def['unit'],
        'display_format': kpi_def['display_format'],
        'target_value': kpi_def.get('target_value'),
        'threshold_status': None,  # Would be determined from thresholds
        'color': None  # Would be determined from thresholds
    }

    return result


def compare_periods(
    current_data: List[Dict[str, Any]],
    previous_data: List[Dict[str, Any]],
    metric_field: str
) -> Dict[str, Any]:
    """
    Compare current period vs previous period for a metric.

    Args:
        current_data: Data for current period
        previous_data: Data for previous period
        metric_field: Name of the metric field to compare

    Returns:
        Dictionary with comparison metrics (change, percent_change, trend)

    Example:
        >>> compare_periods(
        ...     [{'volume': 100}, {'volume': 150}],
        ...     [{'volume': 80}, {'volume': 120}],
        ...     'volume'
        ... )
        {
            'current_total': 250,
            'previous_total': 200,
            'change': 50,
            'percent_change': 25.0,
            'trend': 'up'
        }
    """
    # Calculate totals
    current_total = sum(row.get(metric_field, 0) for row in current_data)
    previous_total = sum(row.get(metric_field, 0) for row in previous_data)

    # Calculate change
    change = current_total - previous_total

    # Calculate percent change
    if previous_total != 0:
        percent_change = (change / previous_total) * 100
    else:
        percent_change = 0 if current_total == 0 else 100

    # Determine trend
    if change > 0:
        trend = 'up'
    elif change < 0:
        trend = 'down'
    else:
        trend = 'stable'

    return {
        'current_total': current_total,
        'previous_total': previous_total,
        'change': change,
        'percent_change': round(percent_change, 2),
        'trend': trend,
        'current_average': current_total / len(current_data) if current_data else 0,
        'previous_average': previous_total / len(previous_data) if previous_data else 0
    }


def calculate_moving_average(
    data: List[Dict[str, Any]],
    time_field: str,
    value_field: str,
    window_days: int = 7
) -> List[Dict[str, Any]]:
    """
    Calculate moving average for time-series data.

    Args:
        data: List of data dictionaries
        time_field: Name of the timestamp field
        value_field: Name of the value field to average
        window_days: Number of days in the moving average window

    Returns:
        List of dictionaries with original data plus moving average

    Example:
        >>> data = [
        ...     {'date': '2025-11-01', 'temp': 20},
        ...     {'date': '2025-11-02', 'temp': 22},
        ...     {'date': '2025-11-03', 'temp': 21},
        ... ]
        >>> calculate_moving_average(data, 'date', 'temp', window_days=2)
        [
            {'date': '2025-11-01', 'temp': 20, 'temp_ma': 20},
            {'date': '2025-11-02', 'temp': 22, 'temp_ma': 21},
            {'date': '2025-11-03', 'temp': 21, 'temp_ma': 21.5}
        ]
    """
    if not data:
        return []

    # Convert to pandas DataFrame
    df = pd.DataFrame(data)

    # Ensure time field is datetime and sort
    df[time_field] = pd.to_datetime(df[time_field])
    df = df.sort_values(time_field)

    # Calculate moving average
    df[f'{value_field}_ma'] = df[value_field].rolling(
        window=window_days,
        min_periods=1
    ).mean()

    # Round the moving average
    df[f'{value_field}_ma'] = df[f'{value_field}_ma'].round(2)

    return df.to_dict('records')


def aggregate_multi_metric(
    data: List[Dict[str, Any]],
    time_field: str,
    metric_configs: List[Dict[str, str]],
    period: AggregationPeriod = 'day'
) -> List[Dict[str, Any]]:
    """
    Aggregate multiple metrics with different aggregation types.

    Args:
        data: List of data dictionaries
        time_field: Name of the timestamp field
        metric_configs: List of metric configurations, each with 'field' and 'agg_type'
                       e.g., [{'field': 'temp', 'agg_type': 'avg'}, {'field': 'rain', 'agg_type': 'sum'}]
        period: Time period for aggregation

    Returns:
        List of aggregated data dictionaries

    Example:
        >>> data = [
        ...     {'time': '2025-11-01 08:00', 'temp': 20, 'rain': 5},
        ...     {'time': '2025-11-01 14:00', 'temp': 25, 'rain': 0},
        ...     {'time': '2025-11-02 08:00', 'temp': 18, 'rain': 10}
        ... ]
        >>> aggregate_multi_metric(
        ...     data, 'time',
        ...     [{'field': 'temp', 'agg_type': 'avg'}, {'field': 'rain', 'agg_type': 'sum'}],
        ...     'day'
        ... )
        [
            {'time': '2025-11-01', 'temp_avg': 22.5, 'rain_sum': 5},
            {'time': '2025-11-02', 'temp_avg': 18.0, 'rain_sum': 10}
        ]
    """
    if not data:
        return []

    # Convert to pandas DataFrame
    df = pd.DataFrame(data)
    df[time_field] = pd.to_datetime(df[time_field])

    # Set up period grouping
    period_map = {
        'hour': 'H',
        'day': 'D',
        'week': 'W',
        'month': 'M',
        'year': 'Y'
    }
    freq = period_map.get(period, 'D')

    # Group by period
    grouped = df.groupby(pd.Grouper(key=time_field, freq=freq))

    # Build aggregation dict
    agg_dict = {}
    for config in metric_configs:
        field = config['field']
        agg_type = config['agg_type']

        if agg_type == 'sum':
            agg_dict[field] = 'sum'
        elif agg_type == 'avg':
            agg_dict[field] = 'mean'
        elif agg_type == 'min':
            agg_dict[field] = 'min'
        elif agg_type == 'max':
            agg_dict[field] = 'max'
        elif agg_type == 'count':
            agg_dict[field] = 'count'

    # Apply aggregations
    result = grouped.agg(agg_dict).reset_index()

    # Rename columns to include aggregation type
    rename_map = {time_field: time_field}
    for config in metric_configs:
        field = config['field']
        agg_type = config['agg_type']
        rename_map[field] = f"{field}_{agg_type}"

    result = result.rename(columns=rename_map)

    return result.to_dict('records')


def fill_missing_dates(
    data: List[Dict[str, Any]],
    time_field: str,
    start_date: datetime,
    end_date: datetime,
    fill_value: Any = 0,
    freq: str = 'D'
) -> List[Dict[str, Any]]:
    """
    Fill in missing dates in time-series data.

    Args:
        data: List of data dictionaries
        time_field: Name of the timestamp field
        start_date: Start of the date range
        end_date: End of the date range
        fill_value: Value to use for missing data points
        freq: Frequency ('D' for daily, 'H' for hourly, etc.)

    Returns:
        List of data dictionaries with filled dates
    """
    if not data:
        # Create empty data for the entire range
        date_range = pd.date_range(start=start_date, end=end_date, freq=freq)
        return [{time_field: date, 'value': fill_value} for date in date_range]

    # Convert to DataFrame
    df = pd.DataFrame(data)
    df[time_field] = pd.to_datetime(df[time_field])

    # Create complete date range
    complete_range = pd.date_range(start=start_date, end=end_date, freq=freq)

    # Reindex to include all dates
    df = df.set_index(time_field)
    df = df.reindex(complete_range, fill_value=fill_value)
    df = df.reset_index()
    df = df.rename(columns={'index': time_field})

    return df.to_dict('records')


# Utility functions for common calculations

def calculate_water_use_efficiency(
    total_water_liters: float,
    total_yield_kg: float
) -> float:
    """Calculate water use efficiency (liters per kg of yield)."""
    if total_yield_kg == 0:
        return 0
    return round(total_water_liters / total_yield_kg, 2)


def calculate_nutrient_use_efficiency(
    total_fertilizer_kg: float,
    total_yield_kg: float
) -> float:
    """Calculate nutrient use efficiency (kg yield per kg fertilizer)."""
    if total_fertilizer_kg == 0:
        return 0
    return round(total_yield_kg / total_fertilizer_kg, 2)


def calculate_profit_margin(
    total_revenue: float,
    total_costs: float
) -> float:
    """Calculate profit margin percentage."""
    if total_revenue == 0:
        return 0
    return round(((total_revenue - total_costs) / total_revenue) * 100, 2)


def calculate_roi(
    total_revenue: float,
    total_costs: float
) -> float:
    """Calculate return on investment percentage."""
    if total_costs == 0:
        return 0
    return round(((total_revenue - total_costs) / total_costs) * 100, 2)


def calculate_growing_degree_days(
    temp_max: float,
    temp_min: float,
    base_temp: float = 10.0
) -> float:
    """
    Calculate growing degree days (GDD).

    Args:
        temp_max: Maximum temperature for the day (°C)
        temp_min: Minimum temperature for the day (°C)
        base_temp: Base temperature for crop growth (default 10°C)

    Returns:
        GDD value for the day
    """
    avg_temp = (temp_max + temp_min) / 2
    gdd = max(0, avg_temp - base_temp)
    return round(gdd, 2)
