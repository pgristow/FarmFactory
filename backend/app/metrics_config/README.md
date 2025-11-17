# FarmFactory Metrics and Aggregation Configuration

This directory contains configuration files for Key Performance Indicators (KPIs), metrics definitions, and data aggregation rules used throughout the FarmFactory platform.

## Overview

The metrics system provides:
- **KPI Definitions**: 16 key performance indicators for farm management
- **Aggregation Rules**: Time-based aggregation strategies for all data types
- **Calculation Formulas**: Documented formulas for all derived metrics
- **Data Quality Settings**: Rules for handling nulls, outliers, and edge cases

## Files

### 1. kpis.json

Defines all Key Performance Indicators (KPIs) with their formulas, targets, and visualization preferences.

**Structure**:
```json
{
  "kpi_name": {
    "name": "Human-readable name",
    "description": "What this KPI measures",
    "formula": "Calculation formula",
    "unit": "Unit of measurement",
    "category": "KPI category",
    "target": "Target values",
    "trend": "Desired trend direction",
    "aggregation": "Aggregation method",
    "data_sources": ["Required data sources"],
    "calculation_period": "When to calculate",
    "visualization": "Recommended chart type"
  }
}
```

### 2. aggregations.json

Defines aggregation rules, time periods, rolling averages, and performance optimization settings.

**Main Sections**:
- `time_periods`: Hourly, daily, weekly, monthly, seasonal
- `aggregation_rules`: Per-data-type aggregation strategies
- `rolling_averages`: 7-day, 30-day, 90-day windows
- `cumulative_calculations`: Rainfall, water usage, costs, revenue
- `special_calculations`: Complex derived metrics
- `performance_optimization`: Caching and indexing strategies

---

## KPI Catalog

### Water Management KPIs

#### 1. Water Use Efficiency
**Formula**: `total_water_liters / total_harvest_kg`
**Unit**: L/kg
**Target**: 50 L/kg (optimal)
**Trend**: Lower is better

Measures how efficiently water is converted into crop yield. Lower values indicate better water management.

**Data Sources**:
- Irrigation events
- Harvest records

**Example Calculation**:
```python
total_water = sum(irrigation_events.water_volume_liters)
total_yield = sum(harvest_records.quantity_kg)
wue = total_water / total_yield
```

**Expected Output**: 45.2 L/kg

---

#### 2. Irrigation Frequency
**Formula**: `total_days / count(irrigation_events)`
**Unit**: days
**Target**: 3 days (optimal)
**Trend**: Range optimal (1-7 days)

Tracks the average number of days between irrigation events.

**Data Sources**:
- Irrigation events

**Example Calculation**:
```sql
SELECT
    EXTRACT(DAY FROM MAX(date) - MIN(date)) / COUNT(*) as irrigation_frequency
FROM irrigation_events
WHERE plot_id = 1
    AND date >= '2025-01-01'
    AND date <= '2025-03-31';
```

**Expected Output**: 2.8 days

---

#### 3. Water Cost Efficiency
**Formula**: `total_water_costs / total_harvest_kg`
**Unit**: USD/kg
**Target**: 0.05 USD/kg (optimal)
**Trend**: Lower is better

Measures the cost of water per kilogram of yield produced.

**Data Sources**:
- Irrigation events (with cost data)
- Input costs
- Harvest records

---

#### 4. Water Quality Index
**Formula**: `weighted_average(ph_score, ec_score, turbidity_score, do_score)`
**Unit**: index (0-100)
**Target**: 85+ (optimal)
**Trend**: Higher is better

Composite score of water quality parameters.

**Weights**:
- pH: 30%
- EC: 25%
- Turbidity: 25%
- Dissolved Oxygen: 20%

**Example Calculation**:
```python
def calculate_water_quality_index(ph, ec, turbidity, do):
    # Normalize each parameter to 0-10 scale
    ph_score = normalize_ph(ph, optimal=7.0, range=(6.5, 7.5))
    ec_score = normalize_ec(ec, optimal=1.0, range=(0.5, 1.5))
    turbidity_score = normalize_turbidity(turbidity, optimal=1.0, max=5.0)
    do_score = normalize_do(do, optimal=7.5, range=(5.0, 9.0))

    # Calculate weighted average
    wqi = (
        ph_score * 0.30 +
        ec_score * 0.25 +
        turbidity_score * 0.25 +
        do_score * 0.20
    ) * 10  # Scale to 0-100

    return wqi
```

**Expected Output**: 87.3 (Excellent)

---

### Nutrient Management KPIs

#### 5. NPK Balance Ratio
**Formula**: `ratio(sum(total_N), sum(total_P), sum(total_K))`
**Unit**: ratio (N:P:K)
**Target**: 3:1:2 (optimal for most crops)
**Trend**: Balance optimal

Tracks the ratio of nitrogen, phosphorus, and potassium applied.

**Example Calculation**:
```sql
WITH nutrient_totals AS (
    SELECT
        SUM(amount_kg * n_percent / 100) as total_n,
        SUM(amount_kg * p_percent / 100) as total_p,
        SUM(amount_kg * k_percent / 100) as total_k
    FROM nutrient_applications
    WHERE plot_id = 1
        AND date >= '2025-01-01'
        AND date <= '2025-03-31'
)
SELECT
    ROUND(total_n / NULLIF(total_p, 0), 2) as n_to_p_ratio,
    ROUND(total_k / NULLIF(total_p, 0), 2) as k_to_p_ratio
FROM nutrient_totals;
```

**Expected Output**: 3.2:1:1.9

---

#### 6. Fertilizer Use Efficiency
**Formula**: `total_harvest_kg / total_fertilizer_kg`
**Unit**: kg_yield/kg_fertilizer
**Target**: 100+ (optimal)
**Trend**: Higher is better

Measures yield produced per kilogram of fertilizer applied.

**Data Sources**:
- Nutrient applications
- Harvest records

---

### Crop Performance KPIs

#### 7. Crop Health Score
**Formula**: `avg(health_score)`
**Unit**: score (0-10)
**Target**: 9+ (optimal)
**Trend**: Higher is better

Average health score from phenology observations.

**Example Calculation**:
```sql
SELECT
    AVG(health_score) as avg_health_score,
    MIN(health_score) as min_health_score,
    MAX(health_score) as max_health_score,
    STDDEV(health_score) as health_score_stddev
FROM phenology_observations
WHERE planting_id = 1
    AND observation_date >= CURRENT_DATE - INTERVAL '30 days';
```

**Expected Output**: 8.7 (Good)

---

#### 8. Yield per Hectare
**Formula**: `sum(harvest_kg) / sum(plot_area_hectares)`
**Unit**: kg/ha
**Target**: Varies by crop (benchmark: 10,000 kg/ha)
**Trend**: Higher is better

Normalized yield metric for comparing plots of different sizes.

**Example Calculation**:
```sql
SELECT
    p.plot_name,
    SUM(h.quantity_kg) / p.area_hectares as yield_per_hectare
FROM harvest_records h
JOIN plots p ON h.plot_id = p.id
WHERE h.harvest_date >= '2025-01-01'
GROUP BY p.plot_name, p.area_hectares
ORDER BY yield_per_hectare DESC;
```

**Expected Output**: 12,450 kg/ha

---

#### 9. Growth Rate
**Formula**: `(final_height - initial_height) / days_elapsed`
**Unit**: cm/day
**Target**: Varies by crop (benchmark: 1.5 cm/day)
**Trend**: Higher is better

Average daily growth rate during vegetative stage.

**Example Calculation**:
```python
def calculate_growth_rate(observations):
    if len(observations) < 2:
        return None

    observations = sorted(observations, key=lambda x: x['date'])
    first = observations[0]
    last = observations[-1]

    height_change = last['height_cm'] - first['height_cm']
    days_elapsed = (last['date'] - first['date']).days

    return height_change / days_elapsed if days_elapsed > 0 else None
```

**Expected Output**: 1.8 cm/day

---

#### 10. Canopy Development Rate
**Formula**: `(current_canopy_percent - previous_canopy_percent) / weeks_elapsed`
**Unit**: %/week
**Target**: 8%/week during vegetative stage
**Trend**: Higher is better

Rate of canopy cover increase.

---

#### 11. Crop Cycle Duration
**Formula**: `harvest_date - planting_date`
**Unit**: days
**Target**: Varies by crop (±10% acceptable)
**Trend**: On-target optimal

Actual days from planting to harvest compared to expected duration.

---

### Financial KPIs

#### 12. Profit Margin
**Formula**: `((revenue - costs) / revenue) * 100`
**Unit**: %
**Target**: 40%+ (optimal)
**Trend**: Higher is better

Net profit as a percentage of revenue.

**Example Calculation**:
```sql
WITH financial_summary AS (
    SELECT
        SUM(h.quantity_kg * h.price_per_kg) as total_revenue,
        SUM(c.amount_usd) as total_costs
    FROM harvest_records h
    CROSS JOIN input_costs c
    WHERE h.plot_id = c.plot_id
        AND h.harvest_date >= '2025-01-01'
        AND c.date >= '2025-01-01'
)
SELECT
    total_revenue,
    total_costs,
    total_revenue - total_costs as net_profit,
    ROUND(((total_revenue - total_costs) / total_revenue * 100), 2) as profit_margin_percent
FROM financial_summary;
```

**Expected Output**: 43.5%

---

#### 13. Return on Investment (ROI)
**Formula**: `((revenue - costs) / costs) * 100`
**Unit**: %
**Target**: 150%+ (optimal)
**Trend**: Higher is better

Percentage return on total input costs.

**Example Calculation**:
```python
revenue = 50000  # USD
costs = 20000    # USD
roi = ((revenue - costs) / costs) * 100
# roi = 150%
```

**Expected Output**: 150%

---

#### 14. Cost per Hectare
**Formula**: `sum(input_costs) / sum(plot_area_hectares)`
**Unit**: USD/ha
**Target**: Varies by crop (benchmark: $5,000/ha)
**Trend**: Lower is better

Normalized cost metric for comparing operations.

---

### Operational KPIs

#### 15. Labor Efficiency
**Formula**: `total_harvest_kg / total_labor_hours`
**Unit**: kg/hour
**Target**: Varies by operation (benchmark: 50 kg/hour)
**Trend**: Higher is better

Yield produced per labor hour.

---

#### 16. Pest Pressure Index
**Formula**: `weighted_score(health_score_decline, intervention_frequency)`
**Unit**: index (0-10)
**Target**: < 3 (optimal)
**Trend**: Lower is better

Indicator of pest and disease pressure.

**Example Calculation**:
```python
def calculate_pest_pressure(health_scores, interventions):
    # Health score decline component
    if len(health_scores) >= 2:
        recent_avg = mean(health_scores[-3:])
        previous_avg = mean(health_scores[:-3])
        decline = max(0, previous_avg - recent_avg)
    else:
        decline = 0

    # Intervention frequency component
    intervention_rate = len(interventions) / 4  # per month

    # Weighted score (0-10 scale)
    pest_pressure = (decline * 3 + intervention_rate * 2)
    return min(10, pest_pressure)
```

**Expected Output**: 2.3 (Low pressure)

---

## Aggregation Strategies

### Time-Based Aggregation

#### Hourly Aggregation
**Best for**: Environmental sensor data, real-time monitoring

```sql
SELECT
    DATE_TRUNC('hour', timestamp) as hour,
    plot_id,
    AVG(temperature_c) as avg_temperature,
    MIN(temperature_c) as min_temperature,
    MAX(temperature_c) as max_temperature,
    AVG(humidity_percent) as avg_humidity,
    AVG(soil_moisture_percent) as avg_soil_moisture,
    SUM(rainfall_mm) as total_rainfall
FROM environmental_readings
WHERE timestamp >= '2025-01-01'
    AND timestamp < '2025-01-02'
GROUP BY DATE_TRUNC('hour', timestamp), plot_id
ORDER BY hour;
```

---

#### Daily Aggregation
**Best for**: Irrigation events, water quality, phenology, general operations

```sql
-- Irrigation daily summary
SELECT
    DATE(date) as day,
    plot_id,
    COUNT(*) as irrigation_count,
    SUM(water_volume_liters) as total_water,
    AVG(duration_minutes) as avg_duration,
    AVG(efficiency_rating) as avg_efficiency
FROM irrigation_events
WHERE date >= '2025-01-01'
GROUP BY DATE(date), plot_id
ORDER BY day;
```

---

#### Weekly Aggregation
**Best for**: Nutrient applications, crop health trends, performance reports

```sql
-- Nutrient weekly summary
SELECT
    DATE_TRUNC('week', date) as week,
    plot_id,
    COUNT(*) as application_count,
    SUM(amount_kg * n_percent / 100) as total_n_kg,
    SUM(amount_kg * p_percent / 100) as total_p_kg,
    SUM(amount_kg * k_percent / 100) as total_k_kg,
    SUM(cost_usd) as total_cost
FROM nutrient_applications
WHERE date >= '2025-01-01'
GROUP BY DATE_TRUNC('week', date), plot_id
ORDER BY week;
```

---

#### Monthly Aggregation
**Best for**: Financial summaries, KPI dashboards, strategic planning

```sql
-- Financial monthly summary
SELECT
    TO_CHAR(date, 'YYYY-MM') as month,
    SUM(CASE WHEN category = 'fertilizer' THEN amount_usd ELSE 0 END) as fertilizer_costs,
    SUM(CASE WHEN category = 'water' THEN amount_usd ELSE 0 END) as water_costs,
    SUM(CASE WHEN category = 'labor' THEN amount_usd ELSE 0 END) as labor_costs,
    SUM(amount_usd) as total_costs
FROM input_costs
WHERE date >= '2025-01-01'
GROUP BY TO_CHAR(date, 'YYYY-MM')
ORDER BY month;
```

---

### Rolling Averages

#### 7-Day Moving Average

```sql
SELECT
    observation_date,
    planting_id,
    health_score,
    AVG(health_score) OVER (
        PARTITION BY planting_id
        ORDER BY observation_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as health_score_7day_avg
FROM phenology_observations
ORDER BY planting_id, observation_date;
```

---

#### 30-Day Moving Average

```sql
SELECT
    DATE(timestamp) as date,
    plot_id,
    AVG(temperature_c) as daily_avg_temp,
    AVG(AVG(temperature_c)) OVER (
        PARTITION BY plot_id
        ORDER BY DATE(timestamp)
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) as temp_30day_avg
FROM environmental_readings
GROUP BY DATE(timestamp), plot_id
ORDER BY plot_id, date;
```

---

### Cumulative Calculations

#### Cumulative Rainfall

```sql
SELECT
    DATE(timestamp) as date,
    plot_id,
    SUM(rainfall_mm) as daily_rainfall,
    SUM(SUM(rainfall_mm)) OVER (
        PARTITION BY plot_id, DATE_TRUNC('month', timestamp)
        ORDER BY DATE(timestamp)
    ) as cumulative_monthly_rainfall
FROM environmental_readings
GROUP BY DATE(timestamp), plot_id, DATE_TRUNC('month', timestamp)
ORDER BY plot_id, date;
```

---

#### Cumulative Costs

```sql
SELECT
    date,
    category,
    amount_usd,
    SUM(amount_usd) OVER (
        PARTITION BY category
        ORDER BY date
    ) as cumulative_cost
FROM input_costs
WHERE date >= '2025-01-01'
ORDER BY category, date;
```

---

## Performance Optimization

### Materialized Views

Create materialized views for commonly accessed aggregations:

```sql
-- Daily irrigation summary (materialized view)
CREATE MATERIALIZED VIEW mv_irrigation_daily AS
SELECT
    DATE(date) as day,
    plot_id,
    COUNT(*) as event_count,
    SUM(water_volume_liters) as total_water,
    AVG(efficiency_rating) as avg_efficiency
FROM irrigation_events
GROUP BY DATE(date), plot_id;

-- Refresh schedule: Daily at 2 AM
CREATE INDEX idx_mv_irrigation_daily ON mv_irrigation_daily(plot_id, day);
```

---

### TimescaleDB Continuous Aggregates

For high-frequency time-series data:

```sql
-- Hourly environmental averages (continuous aggregate)
CREATE MATERIALIZED VIEW cagg_environmental_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', timestamp) as hour,
    plot_id,
    AVG(temperature_c) as avg_temperature,
    MIN(temperature_c) as min_temperature,
    MAX(temperature_c) as max_temperature,
    AVG(humidity_percent) as avg_humidity,
    AVG(soil_moisture_percent) as avg_soil_moisture
FROM environmental_readings
GROUP BY time_bucket('1 hour', timestamp), plot_id;

-- Automatic refresh policy
SELECT add_continuous_aggregate_policy('cagg_environmental_hourly',
    start_offset => INTERVAL '1 week',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');
```

---

### Indexing Strategy

**Recommended indexes for time-series queries**:

```sql
-- Irrigation events
CREATE INDEX idx_irrigation_plot_date ON irrigation_events(plot_id, date DESC);
CREATE INDEX idx_irrigation_date ON irrigation_events(date);

-- Nutrient applications
CREATE INDEX idx_nutrients_plot_date ON nutrient_applications(plot_id, date DESC);
CREATE INDEX idx_nutrients_planting ON nutrient_applications(planting_id, date DESC);

-- Environmental readings
CREATE INDEX idx_environmental_plot_timestamp ON environmental_readings(plot_id, timestamp DESC);

-- Phenology observations
CREATE INDEX idx_phenology_planting_date ON phenology_observations(planting_id, observation_date DESC);

-- Water quality
CREATE INDEX idx_water_quality_plot_date ON water_quality_tests(plot_id, date DESC);
```

---

## Data Quality

### Handling Null Values

**Strategy**: Exclude from calculations by default

```sql
-- Example: Calculate average excluding nulls
SELECT
    AVG(health_score) as avg_health  -- Automatically excludes NULLs
FROM phenology_observations
WHERE planting_id = 1;
```

---

### Outlier Detection

**Method**: Interquartile Range (IQR)

```python
def detect_outliers_iqr(data, threshold=1.5):
    """Detect outliers using IQR method"""
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1

    lower_bound = q1 - (threshold * iqr)
    upper_bound = q3 + (threshold * iqr)

    outliers = [x for x in data if x < lower_bound or x > upper_bound]
    return outliers, lower_bound, upper_bound
```

---

### Minimum Data Points

Required minimum data points for valid aggregations:
- **Daily**: 1 data point
- **Weekly**: 3 data points
- **Monthly**: 10 data points

If minimum not met, return NULL or flag as insufficient data.

---

## Usage Examples

### Backend Service Implementation

```python
# backend/app/services/aggregation_service.py

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func

class AggregationService:
    """Service for calculating time-series aggregations and KPIs"""

    def get_daily_irrigation_summary(
        self,
        plot_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Get daily irrigation summary for a plot"""
        query = (
            db.session.query(
                func.date(IrrigationEvent.date).label('day'),
                func.count().label('event_count'),
                func.sum(IrrigationEvent.water_volume_liters).label('total_water'),
                func.avg(IrrigationEvent.efficiency_rating).label('avg_efficiency')
            )
            .filter(
                IrrigationEvent.plot_id == plot_id,
                IrrigationEvent.date >= start_date,
                IrrigationEvent.date <= end_date
            )
            .group_by(func.date(IrrigationEvent.date))
            .order_by(func.date(IrrigationEvent.date))
        )

        return [
            {
                'day': row.day,
                'event_count': row.event_count,
                'total_water': float(row.total_water),
                'avg_efficiency': float(row.avg_efficiency)
            }
            for row in query.all()
        ]

    def calculate_water_use_efficiency(
        self,
        plot_id: int,
        crop_cycle_start: datetime,
        crop_cycle_end: datetime
    ) -> Optional[float]:
        """Calculate water use efficiency for a crop cycle"""
        # Get total water used
        total_water = (
            db.session.query(func.sum(IrrigationEvent.water_volume_liters))
            .filter(
                IrrigationEvent.plot_id == plot_id,
                IrrigationEvent.date >= crop_cycle_start,
                IrrigationEvent.date <= crop_cycle_end
            )
            .scalar()
        )

        # Get total harvest
        total_harvest = (
            db.session.query(func.sum(Harvest.quantity_kg))
            .filter(
                Harvest.plot_id == plot_id,
                Harvest.harvest_date >= crop_cycle_start,
                Harvest.harvest_date <= crop_cycle_end
            )
            .scalar()
        )

        if total_water and total_harvest and total_harvest > 0:
            return total_water / total_harvest
        return None
```

---

### Frontend Chart Integration

```typescript
// frontend/src/services/aggregationService.ts

export interface DailyWaterSummary {
  day: string;
  eventCount: number;
  totalWater: number;
  avgEfficiency: number;
}

export class AggregationService {
  async getDailyWaterUsage(
    plotId: number,
    startDate: Date,
    endDate: Date
  ): Promise<DailyWaterSummary[]> {
    const response = await api.get(`/api/v1/plots/${plotId}/irrigation/summary`, {
      params: {
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
        aggregation: 'daily'
      }
    });

    return response.data;
  }

  async getWaterUseEfficiency(
    plotId: number,
    cropCycleId: number
  ): Promise<number> {
    const response = await api.get(`/api/v1/kpis/water-use-efficiency`, {
      params: {
        plot_id: plotId,
        crop_cycle_id: cropCycleId
      }
    });

    return response.data.value;
  }
}
```

---

## Testing Aggregations

### Unit Tests

```python
# backend/tests/unit/test_aggregation_service.py

def test_daily_irrigation_summary():
    """Test daily irrigation aggregation"""
    service = AggregationService()

    # Create test data
    plot = create_test_plot()
    create_irrigation_event(plot.id, date='2025-01-01', water_liters=500)
    create_irrigation_event(plot.id, date='2025-01-01', water_liters=300)
    create_irrigation_event(plot.id, date='2025-01-02', water_liters=400)

    # Get summary
    summary = service.get_daily_irrigation_summary(
        plot_id=plot.id,
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 1, 2)
    )

    # Assertions
    assert len(summary) == 2
    assert summary[0]['event_count'] == 2
    assert summary[0]['total_water'] == 800
    assert summary[1]['event_count'] == 1
    assert summary[1]['total_water'] == 400
```

---

## Best Practices

1. **Use appropriate time granularity**
   - Hourly for real-time sensor data
   - Daily for operational events
   - Weekly/monthly for reports and KPIs

2. **Cache aggregated data**
   - Use materialized views for frequently accessed aggregations
   - Implement refresh schedules during off-peak hours
   - Consider TimescaleDB continuous aggregates for high-frequency data

3. **Handle edge cases**
   - Check for null values before calculations
   - Validate minimum data points
   - Handle division by zero

4. **Optimize queries**
   - Use appropriate indexes
   - Limit date ranges to reasonable periods
   - Consider pre-aggregation for large datasets

5. **Document assumptions**
   - Clearly document calculation formulas
   - Specify target values and benchmarks
   - Note crop-specific variations

---

## Support

For questions or issues with metrics and aggregations:

1. Review this documentation
2. Check `kpis.json` and `aggregations.json` for configuration
3. Consult Sprint 3 plan: `/home/user/FarmFactory/SPRINT_3_PLAN.md`
4. Review database indexes: `backend/alembic/versions/004_add_timeseries_indexes.py`

---

**Version**: 1.0
**Last Updated**: 2025-11-17
**Maintained by**: Data Engineering Team
