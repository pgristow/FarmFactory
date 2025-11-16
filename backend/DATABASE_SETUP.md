# Database Setup and Migration Guide

This guide explains how to set up the FarmFactory database and run migrations.

## Prerequisites

1. **PostgreSQL 14+** installed and running
2. **PostGIS extension** available
3. **TimescaleDB extension** available
4. **Python 3.11+** with pip

## Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Step 2: Configure Database Connection

Copy the example environment file and update with your database credentials:

```bash
cp .env.example .env
```

Edit `.env` and update the `DATABASE_URL`:

```
DATABASE_URL=postgresql://username:password@localhost:5432/farmfactory
```

## Step 3: Create Database

Create the PostgreSQL database:

```bash
# Using psql
createdb farmfactory

# Or using SQL
psql -U postgres -c "CREATE DATABASE farmfactory;"
```

## Step 4: Enable Extensions

Connect to the database and enable required extensions:

```bash
psql -U postgres -d farmfactory
```

```sql
-- Enable PostGIS for spatial data
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enable TimescaleDB for time-series data
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Exit psql
\q
```

**Note**: The migrations will also attempt to enable these extensions automatically.

## Step 5: Run Migrations

Run all migrations to create the database schema:

```bash
cd backend

# Upgrade to latest version
alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial database schema with all tables
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, Create TimescaleDB hypertables for time-series data
```

## Step 6: Verify Installation

Check that all tables were created:

```bash
psql -U postgres -d farmfactory -c "\dt"
```

Expected tables:
- farms
- plots
- soil_profiles
- crops
- plantings
- phenology_observations
- irrigation_events (hypertable)
- nutrient_applications (hypertable)
- water_quality (hypertable)
- environmental_readings (hypertable)
- input_costs
- harvests
- alert_thresholds
- alerts

## Migration Commands Reference

### Check Current Version

```bash
alembic current
```

### View Migration History

```bash
alembic history --verbose
```

### Upgrade to Specific Version

```bash
alembic upgrade <revision>
```

### Downgrade One Version

```bash
alembic downgrade -1
```

### Downgrade to Specific Version

```bash
alembic downgrade <revision>
```

### Generate New Migration (Auto-detect Changes)

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Generate Empty Migration

```bash
alembic revision -m "Description of changes"
```

## Database Schema Overview

### Core Tables (Standard PostgreSQL)

1. **farms** - Farm locations with PostGIS POINT geography
2. **plots** - Field/plot boundaries with PostGIS POLYGON geography
3. **soil_profiles** - Soil characteristics and test results
4. **crops** - Crop master data
5. **plantings** - Crop planting records
6. **phenology_observations** - Growth stage observations

### Time-Series Tables (TimescaleDB Hypertables)

7. **irrigation_events** - Irrigation tracking
8. **nutrient_applications** - Fertilizer applications
9. **water_quality** - Water quality measurements
10. **environmental_readings** - Environmental sensor data

### Financial Tables

11. **input_costs** - Farm expenses tracking
12. **harvests** - Harvest yield and revenue

### Alert Tables

13. **alert_thresholds** - Alert configuration
14. **alerts** - Alert history

## TimescaleDB Features

### Hypertables

Time-series tables are automatically partitioned by time:
- **irrigation_events**: 7-day chunks
- **nutrient_applications**: 7-day chunks
- **water_quality**: 7-day chunks
- **environmental_readings**: 1-day chunks

### Compression

Data older than 30 days is automatically compressed to save storage.

### Continuous Aggregates

Daily aggregates for environmental readings are available in the `environmental_readings_daily` materialized view.

## Troubleshooting

### Extension Not Available

If you get "extension not available" errors:

```bash
# Install PostGIS
sudo apt-get install postgresql-14-postgis-3

# Install TimescaleDB
sudo add-apt-repository ppa:timescale/timescaledb-ppa
sudo apt-get update
sudo apt-get install timescaledb-postgresql-14
```

### Permission Errors

Ensure your database user has sufficient permissions:

```sql
GRANT ALL PRIVILEGES ON DATABASE farmfactory TO your_user;
ALTER USER your_user WITH SUPERUSER;  -- For extension creation
```

### Migration Conflicts

If migrations are out of sync:

```bash
# Check current version
alembic current

# Force to specific version (use with caution)
alembic stamp <revision>
```

## Development Workflow

### Making Schema Changes

1. Modify the SQLAlchemy models in `app/models/`
2. Generate migration:
   ```bash
   alembic revision --autogenerate -m "Add new field to farms table"
   ```
3. Review the generated migration in `alembic/versions/`
4. Edit if necessary (autogenerate isn't perfect)
5. Test the migration:
   ```bash
   alembic upgrade head
   ```
6. If issues occur, rollback:
   ```bash
   alembic downgrade -1
   ```

### Best Practices

1. **Always review** autogenerated migrations before running
2. **Test migrations** on development database first
3. **Backup production** database before running migrations
4. **Keep migrations small** - one logical change per migration
5. **Never edit** applied migrations - create a new one instead
6. **Document** complex migrations with comments

## Database Backup

### Backup Command

```bash
pg_dump -U postgres -d farmfactory -F c -f farmfactory_backup.dump
```

### Restore Command

```bash
pg_restore -U postgres -d farmfactory -c farmfactory_backup.dump
```

## Performance Optimization

### Analyze Tables

After loading data, update statistics:

```sql
ANALYZE farms;
ANALYZE plots;
-- etc.
```

### Vacuum

Regular maintenance:

```sql
VACUUM ANALYZE;
```

### Check Hypertable Status

```sql
SELECT * FROM timescaledb_information.hypertables;
SELECT * FROM timescaledb_information.chunks;
SELECT * FROM timescaledb_information.continuous_aggregates;
```

## Next Steps

After database setup:

1. Review the model documentation in `app/models/README.md`
2. Set up the FastAPI application
3. Create Pydantic schemas for API validation
4. Implement API endpoints
5. Add sample data for testing

## Additional Resources

- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [PostGIS Documentation](https://postgis.net/documentation/)
