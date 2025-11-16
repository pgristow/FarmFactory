# FarmFactory Database Models Documentation

This document describes the database schema for the FarmFactory farm optimization system.

## Overview

The database is built on PostgreSQL 14+ with the following extensions:
- **PostGIS**: For geographic/spatial data (farm and plot locations)
- **TimescaleDB**: For optimized time-series data storage and queries

## Technology Stack

- **SQLAlchemy 2.0**: ORM with modern async support
- **GeoAlchemy2**: PostGIS integration for spatial queries
- **Alembic**: Database migration management
- **Pydantic**: Configuration and settings management

## Database Architecture

### Core Entities

#### 1. Farm Management

**`farms`** - Farm locations and basic information
- Primary spatial entity using PostGIS POINT geography
- Contains farm-level metadata (name, address, total area, timezone)
- One-to-many relationship with plots

**`plots`** - Individual fields/plots within farms
- Uses PostGIS POLYGON geography for boundaries
- Tracks physical characteristics (area, elevation, slope)
- Central entity linking to most other tables
- One-to-many relationships with plantings, soil profiles, and time-series data

**`soil_profiles`** - Soil characteristics and test results
- Tracks soil chemistry (pH, organic matter, CEC)
- Tracks soil physics (texture, bulk density, porosity)
- Multiple profiles per plot to track changes over time

#### 2. Crop Management

**`crops`** - Master crop catalog
- Reference table for crop types and varieties
- Stores optimal growing conditions
- Includes growth characteristics (days to maturity)

**`plantings`** - Specific crop plantings in plots
- Links crops to plots with temporal data
- Tracks planting and harvest dates
- Records planting density and spacing
- Status tracking (planted, growing, harvested, failed)

**`phenology_observations`** - Growth stage observations
- Periodic observations of crop development
- BBCH scale support for standardized growth staging
- Health scoring (1-10 scale)
- Photo documentation support (JSONB)

#### 3. Time-Series Data (TimescaleDB Hypertables)

All time-series tables use composite primary keys (time, plot_id) and are converted to TimescaleDB hypertables for optimal performance.

**`irrigation_events`** - Irrigation tracking
- Records water application events
- Tracks volume, duration, method, and source
- Technical measurements (flow rate, pressure)
- Compressed after 30 days, 7-day chunks

**`nutrient_applications`** - Fertilizer/nutrient tracking
- Records all nutrient applications
- NPK ratios and individual nutrient quantities
- Application method and cost tracking
- Compressed after 30 days, 7-day chunks

**`water_quality`** - Water quality measurements
- pH, EC, TDS, temperature
- Dissolved oxygen and turbidity
- Source tracking
- Compressed after 30 days, 7-day chunks

**`environmental_readings`** - Environmental sensor data
- Air and soil temperature
- Humidity and soil moisture
- Light intensity, rainfall, wind speed
- Atmospheric pressure
- Compressed after 30 days, 1-day chunks (high frequency)
- Daily aggregates available via continuous aggregate view

#### 4. Financial Tracking

**`input_costs`** - Farm input costs
- Tracks all expenses (seeds, fertilizer, water, labor, equipment)
- Can be linked to specific plots or plantings
- Category-based organization
- Unit cost and total cost tracking

**`harvests`** - Harvest records and revenue
- Yield data (quantity, quality grade)
- Revenue and market information
- Linked to plantings for ROI analysis

#### 5. Alert System

**`alert_thresholds`** - Alert configuration
- Defines monitoring thresholds for parameters
- Plot-specific or global thresholds
- Severity levels (info, warning, critical)
- Active/inactive status

**`alerts`** - Alert history
- Records triggered alerts
- Tracks acknowledgment and resolution
- Stores threshold values at time of alert
- Indexed for quick retrieval of active alerts

## Model Mixins

### `UUIDMixin`
Provides UUID primary key using PostgreSQL's `gen_random_uuid()`.

### `TimestampMixin`
Adds `created_at` and `updated_at` timestamp columns with automatic management.

## Indexes and Performance

### Spatial Indexes
- GiST indexes on all geography columns for spatial queries
- Enables efficient location-based queries and proximity searches

### Time-Series Optimizations
- TimescaleDB automatic partitioning by time
- Compression policies for data older than 30 days
- Continuous aggregates for common query patterns
- Efficient time-range queries

### Standard Indexes
- Foreign keys are automatically indexed
- Composite indexes on frequently queried column combinations
- Status and category fields indexed for filtering

## Database Migrations

### Running Migrations

```bash
# Navigate to backend directory
cd backend

# Create a new migration (auto-generate from model changes)
alembic revision --autogenerate -m "description of changes"

# Run all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current migration version
alembic current

# Show migration history
alembic history
```

### Initial Setup

1. **Migration 001**: Creates all base tables and indexes
   - Enables PostGIS and TimescaleDB extensions
   - Creates all standard tables
   - Creates time-series tables (not yet hypertables)
   - Sets up all indexes and constraints

2. **Migration 002**: Converts time-series tables to hypertables
   - Creates TimescaleDB hypertables
   - Sets up compression policies
   - Creates continuous aggregates
   - Configures refresh policies

## Relationships

### One-to-Many
- Farm → Plots
- Plot → Soil Profiles, Plantings, Time-series data
- Crop → Plantings
- Planting → Phenology Observations, Harvests, Input Costs
- AlertThreshold → Alerts

### Many-to-One
- All child entities reference their parents via UUID foreign keys
- Cascading deletes configured where appropriate

## Constraints and Validation

### Check Constraints
- Health score: 1-10 range
- Canopy cover: 0-100% range
- Alert severity: enum ('info', 'warning', 'critical')

### Foreign Key Constraints
- ON DELETE CASCADE: Child records deleted with parent
- ON DELETE SET NULL: Reference nullified (for optional relationships)

## Spatial Data

### Coordinate System
All spatial data uses WGS84 (SRID 4326):
- Latitude/Longitude coordinates
- PostGIS GEOGRAPHY type for accurate distance calculations
- POINT for farm locations
- POLYGON for plot boundaries

### Spatial Queries Example
```python
# Find plots within 1km of a point
from geoalchemy2.functions import ST_DWithin, ST_MakePoint

nearby_plots = session.query(Plot).filter(
    ST_DWithin(
        Plot.location,
        ST_MakePoint(longitude, latitude),
        1000  # meters
    )
).all()
```

## Time-Series Queries

### Basic Time-Range Query
```python
from datetime import datetime, timedelta

# Get last 7 days of environmental data
end_time = datetime.now()
start_time = end_time - timedelta(days=7)

readings = session.query(EnvironmentalReading).filter(
    EnvironmentalReading.plot_id == plot_id,
    EnvironmentalReading.time >= start_time,
    EnvironmentalReading.time < end_time
).order_by(EnvironmentalReading.time).all()
```

### Using Continuous Aggregates
```python
# Query daily environmental aggregates (much faster)
from sqlalchemy import text

result = session.execute(
    text("""
        SELECT day, avg_air_temp, avg_soil_moisture, total_rainfall
        FROM environmental_readings_daily
        WHERE plot_id = :plot_id
        AND day >= :start_day
        ORDER BY day
    """),
    {"plot_id": plot_id, "start_day": start_day}
)
```

## Data Retention

Configured in `config.py`:
- Environmental data: 365 days
- Irrigation data: 730 days (2 years)
- Nutrient data: 730 days (2 years)
- Water quality: 365 days

Older data is automatically compressed by TimescaleDB to save storage.

## Best Practices

1. **Use async sessions** for FastAPI endpoints
2. **Use sync sessions** for Celery tasks
3. **Batch inserts** for time-series data
4. **Use continuous aggregates** for dashboard queries
5. **Index new query patterns** as needed
6. **Monitor query performance** with EXPLAIN ANALYZE
7. **Regular VACUUM** for PostgreSQL maintenance
8. **Backup strategy** for critical data

## Future Enhancements

- Partitioning for large non-time-series tables
- Read replicas for analytics workload
- Full-text search on notes fields
- Audit logging table
- User and permissions tables
- Data versioning for critical records

## Support and Documentation

- SQLAlchemy 2.0: https://docs.sqlalchemy.org/en/20/
- TimescaleDB: https://docs.timescale.com/
- PostGIS: https://postgis.net/documentation/
- Alembic: https://alembic.sqlalchemy.org/
