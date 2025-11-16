"""Create TimescaleDB hypertables for time-series data

Revision ID: 002
Revises: 001
Create Date: 2025-11-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Convert time-series tables to TimescaleDB hypertables.

    This enables automatic partitioning by time and provides optimized
    time-series query performance.
    """

    # Convert irrigation_events to hypertable
    # Partitioned by 'time' column with chunks of 7 days
    op.execute("""
        SELECT create_hypertable(
            'irrigation_events',
            'time',
            chunk_time_interval => INTERVAL '7 days',
            if_not_exists => TRUE
        )
    """)

    # Convert nutrient_applications to hypertable
    # Partitioned by 'time' column with chunks of 7 days
    op.execute("""
        SELECT create_hypertable(
            'nutrient_applications',
            'time',
            chunk_time_interval => INTERVAL '7 days',
            if_not_exists => TRUE
        )
    """)

    # Convert water_quality to hypertable
    # Partitioned by 'time' column with chunks of 7 days
    op.execute("""
        SELECT create_hypertable(
            'water_quality',
            'time',
            chunk_time_interval => INTERVAL '7 days',
            if_not_exists => TRUE
        )
    """)

    # Convert environmental_readings to hypertable
    # Partitioned by 'time' column with chunks of 1 day (higher frequency data)
    op.execute("""
        SELECT create_hypertable(
            'environmental_readings',
            'time',
            chunk_time_interval => INTERVAL '1 day',
            if_not_exists => TRUE
        )
    """)

    # Enable compression on hypertables to save storage
    # Compress chunks older than 30 days

    op.execute("""
        ALTER TABLE irrigation_events SET (
            timescaledb.compress,
            timescaledb.compress_segmentby = 'plot_id'
        )
    """)

    op.execute("""
        SELECT add_compression_policy('irrigation_events', INTERVAL '30 days')
    """)

    op.execute("""
        ALTER TABLE nutrient_applications SET (
            timescaledb.compress,
            timescaledb.compress_segmentby = 'plot_id'
        )
    """)

    op.execute("""
        SELECT add_compression_policy('nutrient_applications', INTERVAL '30 days')
    """)

    op.execute("""
        ALTER TABLE water_quality SET (
            timescaledb.compress,
            timescaledb.compress_segmentby = 'plot_id'
        )
    """)

    op.execute("""
        SELECT add_compression_policy('water_quality', INTERVAL '30 days')
    """)

    op.execute("""
        ALTER TABLE environmental_readings SET (
            timescaledb.compress,
            timescaledb.compress_segmentby = 'plot_id'
        )
    """)

    op.execute("""
        SELECT add_compression_policy('environmental_readings', INTERVAL '30 days')
    """)

    # Create continuous aggregates for common queries (optional but recommended)
    # Daily aggregates for environmental readings
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS environmental_readings_daily
        WITH (timescaledb.continuous) AS
        SELECT
            time_bucket('1 day', time) AS day,
            plot_id,
            AVG(air_temp_celsius) as avg_air_temp,
            MIN(air_temp_celsius) as min_air_temp,
            MAX(air_temp_celsius) as max_air_temp,
            AVG(soil_temp_celsius) as avg_soil_temp,
            AVG(humidity_percent) as avg_humidity,
            AVG(soil_moisture_percent) as avg_soil_moisture,
            MIN(soil_moisture_percent) as min_soil_moisture,
            MAX(soil_moisture_percent) as max_soil_moisture,
            SUM(rainfall_mm) as total_rainfall,
            AVG(light_intensity_lux) as avg_light_intensity
        FROM environmental_readings
        GROUP BY day, plot_id
        WITH NO DATA
    """)

    # Add refresh policy for the continuous aggregate
    op.execute("""
        SELECT add_continuous_aggregate_policy('environmental_readings_daily',
            start_offset => INTERVAL '3 days',
            end_offset => INTERVAL '1 hour',
            schedule_interval => INTERVAL '1 hour')
    """)


def downgrade() -> None:
    """
    Remove TimescaleDB hypertable configuration.

    Note: This does not convert the tables back to regular PostgreSQL tables,
    but removes the compression policies and continuous aggregates.
    """

    # Drop continuous aggregate
    op.execute("DROP MATERIALIZED VIEW IF EXISTS environmental_readings_daily CASCADE")

    # Remove compression policies (policies are automatically removed when dropping policies)
    op.execute("""
        SELECT remove_compression_policy('irrigation_events', if_exists => true)
    """)

    op.execute("""
        SELECT remove_compression_policy('nutrient_applications', if_exists => true)
    """)

    op.execute("""
        SELECT remove_compression_policy('water_quality', if_exists => true)
    """)

    op.execute("""
        SELECT remove_compression_policy('environmental_readings', if_exists => true)
    """)

    # Note: To fully revert hypertables to regular tables, you would need to:
    # 1. Create new regular tables
    # 2. Copy data from hypertables
    # 3. Drop hypertables
    # 4. Rename new tables
    # This is complex and usually not needed, so we don't implement full downgrade
