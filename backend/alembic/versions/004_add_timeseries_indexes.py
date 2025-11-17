"""Add optimized time-series indexes for query performance

Revision ID: 004
Revises: 003
Create Date: 2025-11-17

Sprint 3 - Database Architect Task DB-201
Optimizes all time-series tables with proper indexes to achieve <200ms query
performance for 30 days of data.

PERFORMANCE TARGETS:
- 30-day time-series query: <200ms
- 90-day time-series query: <500ms
- Aggregation by day: <300ms
- Filter by plot + date range: <200ms

INDEX STRATEGY:
- BRIN indexes for time columns (efficient for sequential time-series data)
- B-tree indexes for exact lookups and foreign keys
- Composite indexes matching common query patterns
- (plot_id, time DESC) for recent data per plot queries
- (time DESC, plot_id) for time-range queries across plots

TEST QUERIES (run after migration):

-- Test 1: 30-day irrigation for specific plot (Target: <200ms)
EXPLAIN ANALYZE
SELECT * FROM irrigation_events
WHERE plot_id = 'some-uuid'
  AND time >= NOW() - INTERVAL '30 days'
ORDER BY time DESC;

-- Test 2: Daily water usage aggregation (Target: <300ms)
EXPLAIN ANALYZE
SELECT DATE(time) as date, SUM(water_volume_liters) as total
FROM irrigation_events
WHERE time >= NOW() - INTERVAL '90 days'
GROUP BY DATE(time)
ORDER BY date DESC;

-- Test 3: Recent nutrient applications by type (Target: <200ms)
EXPLAIN ANALYZE
SELECT * FROM nutrient_applications
WHERE time >= NOW() - INTERVAL '30 days'
  AND nutrient_type = 'Nitrogen'
ORDER BY time DESC
LIMIT 100;

-- Test 4: Environmental readings with aggregation (Target: <300ms)
EXPLAIN ANALYZE
SELECT DATE(time) as date,
       AVG(air_temp_celsius) as avg_temp,
       AVG(soil_moisture_percent) as avg_moisture
FROM environmental_readings
WHERE plot_id = 'some-uuid'
  AND time >= NOW() - INTERVAL '90 days'
GROUP BY DATE(time)
ORDER BY date DESC;

-- Test 5: Phenology observations timeline (Target: <200ms)
EXPLAIN ANALYZE
SELECT * FROM phenology_observations
WHERE planting_id = 'some-uuid'
  AND observation_date >= CURRENT_DATE - INTERVAL '90 days'
ORDER BY observation_date DESC;

-- Test 6: Input costs by category over time (Target: <200ms)
EXPLAIN ANALYZE
SELECT DATE(cost_date) as date, category, SUM(total_cost) as total
FROM input_costs
WHERE cost_date >= CURRENT_DATE - INTERVAL '90 days'
  AND category IN ('fertilizer', 'water', 'labor')
GROUP BY DATE(cost_date), category
ORDER BY date DESC;

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add optimized indexes for time-series and date-based tables.

    This migration creates indexes to optimize common query patterns:
    1. Time-range queries per plot
    2. Recent data queries (descending time)
    3. Filtered queries by categorical fields
    4. Aggregation queries over time periods
    """

    # =========================================================================
    # TIME-SERIES HYPERTABLES - Optimized for TimescaleDB
    # =========================================================================

    # -------------------------------------------------------------------------
    # 1. IRRIGATION_EVENTS
    # -------------------------------------------------------------------------

    # BRIN index on time column (efficient for time-series, already created by hypertable)
    # TimescaleDB automatically creates a BRIN index on the time column

    # Composite index: (plot_id, time DESC) - Query specific plot's recent irrigation
    # This is already created in the model: ix_irrigation_events_plot_time
    # But we'll ensure it's optimized with DESC ordering
    op.execute("""
        DROP INDEX IF EXISTS ix_irrigation_events_plot_time
    """)
    op.create_index(
        'ix_irrigation_events_plot_time_desc',
        'irrigation_events',
        ['plot_id', sa.text('time DESC')],
        postgresql_using='btree'
    )

    # Composite index: (time DESC, plot_id) - Time-range queries across plots
    op.create_index(
        'ix_irrigation_events_time_desc_plot',
        'irrigation_events',
        [sa.text('time DESC'), 'plot_id'],
        postgresql_using='btree'
    )

    # B-tree index on plot_id alone for filtering (already exists as FK)
    # Index on method field for filtering by irrigation method
    # This already exists: ix_irrigation_events_method

    # B-tree index on water_source for filtering
    op.create_index(
        'ix_irrigation_events_water_source',
        'irrigation_events',
        ['water_source'],
        postgresql_using='btree'
    )

    # -------------------------------------------------------------------------
    # 2. NUTRIENT_APPLICATIONS
    # -------------------------------------------------------------------------

    # Composite index: (plot_id, time DESC) - Query specific plot's recent applications
    op.execute("""
        DROP INDEX IF EXISTS ix_nutrient_applications_plot_time
    """)
    op.create_index(
        'ix_nutrient_applications_plot_time_desc',
        'nutrient_applications',
        ['plot_id', sa.text('time DESC')],
        postgresql_using='btree'
    )

    # Composite index: (time DESC, plot_id) - Time-range queries across plots
    op.create_index(
        'ix_nutrient_applications_time_desc_plot',
        'nutrient_applications',
        [sa.text('time DESC'), 'plot_id'],
        postgresql_using='btree'
    )

    # Indexes on categorical fields already exist:
    # - ix_nutrient_applications_nutrient_type
    # - ix_nutrient_applications_method

    # Composite index: (nutrient_type, time DESC) - Query by nutrient over time
    op.create_index(
        'ix_nutrient_applications_type_time_desc',
        'nutrient_applications',
        ['nutrient_type', sa.text('time DESC')],
        postgresql_using='btree'
    )

    # -------------------------------------------------------------------------
    # 3. WATER_QUALITY
    # -------------------------------------------------------------------------

    # Composite index: (plot_id, time DESC) - Query specific plot's water quality
    op.execute("""
        DROP INDEX IF EXISTS ix_water_quality_plot_time
    """)
    op.create_index(
        'ix_water_quality_plot_time_desc',
        'water_quality',
        ['plot_id', sa.text('time DESC')],
        postgresql_using='btree'
    )

    # Composite index: (time DESC, plot_id) - Time-range queries across plots
    op.create_index(
        'ix_water_quality_time_desc_plot',
        'water_quality',
        [sa.text('time DESC'), 'plot_id'],
        postgresql_using='btree'
    )

    # Index on source field already exists: ix_water_quality_source

    # Composite index: (source, time DESC) - Query by water source over time
    op.create_index(
        'ix_water_quality_source_time_desc',
        'water_quality',
        ['source', sa.text('time DESC')],
        postgresql_using='btree'
    )

    # -------------------------------------------------------------------------
    # 4. ENVIRONMENTAL_READINGS
    # -------------------------------------------------------------------------

    # Composite index: (plot_id, time DESC) - Query specific plot's readings
    op.execute("""
        DROP INDEX IF EXISTS ix_environmental_readings_plot_time
    """)
    op.create_index(
        'ix_environmental_readings_plot_time_desc',
        'environmental_readings',
        ['plot_id', sa.text('time DESC')],
        postgresql_using='btree'
    )

    # Composite index: (time DESC, plot_id) - Time-range queries across plots
    op.create_index(
        'ix_environmental_readings_time_desc_plot',
        'environmental_readings',
        [sa.text('time DESC'), 'plot_id'],
        postgresql_using='btree'
    )

    # Indexes on commonly queried metrics already exist:
    # - ix_environmental_readings_soil_moisture
    # - ix_environmental_readings_air_temp

    # =========================================================================
    # REGULAR DATE-BASED TABLES
    # =========================================================================

    # -------------------------------------------------------------------------
    # 5. PHENOLOGY_OBSERVATIONS
    # -------------------------------------------------------------------------

    # Composite index: (planting_id, observation_date DESC) - Recent observations per planting
    op.execute("""
        DROP INDEX IF EXISTS ix_phenology_planting_observation_date
    """)
    op.create_index(
        'ix_phenology_planting_obs_date_desc',
        'phenology_observations',
        ['planting_id', sa.text('observation_date DESC')],
        postgresql_using='btree'
    )

    # Composite index: (observation_date DESC, planting_id) - Date-range queries
    op.create_index(
        'ix_phenology_obs_date_desc_planting',
        'phenology_observations',
        [sa.text('observation_date DESC'), 'planting_id'],
        postgresql_using='btree'
    )

    # B-tree index on growth_stage for filtering
    op.create_index(
        'ix_phenology_growth_stage',
        'phenology_observations',
        ['growth_stage'],
        postgresql_using='btree'
    )

    # Composite index: (growth_stage, observation_date DESC) - Track stage progression
    op.create_index(
        'ix_phenology_stage_date_desc',
        'phenology_observations',
        ['growth_stage', sa.text('observation_date DESC')],
        postgresql_using='btree'
    )

    # -------------------------------------------------------------------------
    # 6. INPUT_COSTS
    # -------------------------------------------------------------------------

    # Index on cost_date DESC for time-based queries
    op.create_index(
        'ix_input_costs_date_desc',
        'input_costs',
        [sa.text('cost_date DESC')],
        postgresql_using='btree'
    )

    # Composite indexes already exist from the model:
    # - ix_input_costs_plot_cost_date
    # - ix_input_costs_planting_cost_date
    # - ix_input_costs_category_cost_date

    # Drop and recreate with DESC ordering for better recent-data performance
    op.execute("""
        DROP INDEX IF EXISTS ix_input_costs_plot_cost_date
    """)
    op.create_index(
        'ix_input_costs_plot_date_desc',
        'input_costs',
        ['plot_id', sa.text('cost_date DESC')],
        postgresql_using='btree'
    )

    op.execute("""
        DROP INDEX IF EXISTS ix_input_costs_planting_cost_date
    """)
    op.create_index(
        'ix_input_costs_planting_date_desc',
        'input_costs',
        ['planting_id', sa.text('cost_date DESC')],
        postgresql_using='btree'
    )

    op.execute("""
        DROP INDEX IF EXISTS ix_input_costs_category_cost_date
    """)
    op.create_index(
        'ix_input_costs_category_date_desc',
        'input_costs',
        ['category', sa.text('cost_date DESC')],
        postgresql_using='btree'
    )

    # -------------------------------------------------------------------------
    # 7. HARVESTS
    # -------------------------------------------------------------------------

    # Composite indexes already exist from the model:
    # - ix_harvests_planting_harvest_date
    # - ix_harvests_harvest_date

    # Drop and recreate with DESC ordering
    op.execute("""
        DROP INDEX IF EXISTS ix_harvests_planting_harvest_date
    """)
    op.create_index(
        'ix_harvests_planting_date_desc',
        'harvests',
        ['planting_id', sa.text('harvest_date DESC')],
        postgresql_using='btree'
    )

    op.execute("""
        DROP INDEX IF EXISTS ix_harvests_harvest_date
    """)
    op.create_index(
        'ix_harvests_date_desc',
        'harvests',
        [sa.text('harvest_date DESC')],
        postgresql_using='btree'
    )

    # B-tree index on quality_grade for filtering
    op.create_index(
        'ix_harvests_quality_grade',
        'harvests',
        ['quality_grade'],
        postgresql_using='btree'
    )

    # Composite index: (quality_grade, harvest_date DESC) - Quality trends over time
    op.create_index(
        'ix_harvests_quality_date_desc',
        'harvests',
        ['quality_grade', sa.text('harvest_date DESC')],
        postgresql_using='btree'
    )

    # =========================================================================
    # INDEX USAGE MONITORING VIEW
    # =========================================================================

    # Create monitoring view to track index usage and effectiveness
    op.execute("""
        CREATE OR REPLACE VIEW v_index_usage AS
        SELECT
            schemaname,
            tablename,
            indexname,
            idx_scan as scans,
            idx_tup_read as tuples_read,
            idx_tup_fetch as tuples_fetched,
            pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
            CASE
                WHEN idx_scan = 0 THEN 'UNUSED'
                WHEN idx_scan < 100 THEN 'LOW_USAGE'
                WHEN idx_scan < 1000 THEN 'MODERATE_USAGE'
                ELSE 'HIGH_USAGE'
            END as usage_category
        FROM pg_stat_user_indexes
        WHERE schemaname = 'public'
        ORDER BY idx_scan DESC, tablename, indexname;
    """)

    # Grant SELECT on the view to all users
    op.execute("""
        GRANT SELECT ON v_index_usage TO PUBLIC;
    """)

    # Create view for table sizes and statistics
    op.execute("""
        CREATE OR REPLACE VIEW v_table_stats AS
        SELECT
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
            pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as indexes_size,
            n_tup_ins as inserts,
            n_tup_upd as updates,
            n_tup_del as deletes,
            n_live_tup as live_tuples,
            n_dead_tup as dead_tuples,
            last_vacuum,
            last_autovacuum,
            last_analyze,
            last_autoanalyze
        FROM pg_stat_user_tables
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
    """)

    op.execute("""
        GRANT SELECT ON v_table_stats TO PUBLIC;
    """)


def downgrade() -> None:
    """
    Remove optimized indexes and monitoring views.

    This will revert to the original indexes from the models.
    """

    # Drop monitoring views
    op.execute("DROP VIEW IF EXISTS v_index_usage")
    op.execute("DROP VIEW IF EXISTS v_table_stats")

    # =========================================================================
    # DROP TIME-SERIES INDEXES (and restore originals)
    # =========================================================================

    # IRRIGATION_EVENTS - Restore original indexes
    op.execute("DROP INDEX IF EXISTS ix_irrigation_events_plot_time_desc")
    op.execute("DROP INDEX IF EXISTS ix_irrigation_events_time_desc_plot")
    op.execute("DROP INDEX IF EXISTS ix_irrigation_events_water_source")

    # Restore original from model
    op.create_index(
        'ix_irrigation_events_plot_time',
        'irrigation_events',
        ['plot_id', 'time']
    )

    # NUTRIENT_APPLICATIONS - Restore original indexes
    op.execute("DROP INDEX IF EXISTS ix_nutrient_applications_plot_time_desc")
    op.execute("DROP INDEX IF EXISTS ix_nutrient_applications_time_desc_plot")
    op.execute("DROP INDEX IF EXISTS ix_nutrient_applications_type_time_desc")

    # Restore original from model
    op.create_index(
        'ix_nutrient_applications_plot_time',
        'nutrient_applications',
        ['plot_id', 'time']
    )

    # WATER_QUALITY - Restore original indexes
    op.execute("DROP INDEX IF EXISTS ix_water_quality_plot_time_desc")
    op.execute("DROP INDEX IF EXISTS ix_water_quality_time_desc_plot")
    op.execute("DROP INDEX IF EXISTS ix_water_quality_source_time_desc")

    # Restore original from model
    op.create_index(
        'ix_water_quality_plot_time',
        'water_quality',
        ['plot_id', 'time']
    )

    # ENVIRONMENTAL_READINGS - Restore original indexes
    op.execute("DROP INDEX IF EXISTS ix_environmental_readings_plot_time_desc")
    op.execute("DROP INDEX IF EXISTS ix_environmental_readings_time_desc_plot")

    # Restore original from model
    op.create_index(
        'ix_environmental_readings_plot_time',
        'environmental_readings',
        ['plot_id', 'time']
    )

    # =========================================================================
    # DROP REGULAR TABLE INDEXES (and restore originals)
    # =========================================================================

    # PHENOLOGY_OBSERVATIONS - Restore original indexes
    op.execute("DROP INDEX IF EXISTS ix_phenology_planting_obs_date_desc")
    op.execute("DROP INDEX IF EXISTS ix_phenology_obs_date_desc_planting")
    op.execute("DROP INDEX IF EXISTS ix_phenology_growth_stage")
    op.execute("DROP INDEX IF EXISTS ix_phenology_stage_date_desc")

    # Restore original from model
    op.create_index(
        'ix_phenology_planting_observation_date',
        'phenology_observations',
        ['planting_id', 'observation_date']
    )

    # INPUT_COSTS - Restore original indexes
    op.execute("DROP INDEX IF EXISTS ix_input_costs_date_desc")
    op.execute("DROP INDEX IF EXISTS ix_input_costs_plot_date_desc")
    op.execute("DROP INDEX IF EXISTS ix_input_costs_planting_date_desc")
    op.execute("DROP INDEX IF EXISTS ix_input_costs_category_date_desc")

    # Restore originals from model
    op.create_index(
        'ix_input_costs_plot_cost_date',
        'input_costs',
        ['plot_id', 'cost_date']
    )
    op.create_index(
        'ix_input_costs_planting_cost_date',
        'input_costs',
        ['planting_id', 'cost_date']
    )
    op.create_index(
        'ix_input_costs_category_cost_date',
        'input_costs',
        ['category', 'cost_date']
    )

    # HARVESTS - Restore original indexes
    op.execute("DROP INDEX IF EXISTS ix_harvests_planting_date_desc")
    op.execute("DROP INDEX IF EXISTS ix_harvests_date_desc")
    op.execute("DROP INDEX IF EXISTS ix_harvests_quality_grade")
    op.execute("DROP INDEX IF EXISTS ix_harvests_quality_date_desc")

    # Restore originals from model
    op.create_index(
        'ix_harvests_planting_harvest_date',
        'harvests',
        ['planting_id', 'harvest_date']
    )
    op.create_index(
        'ix_harvests_harvest_date',
        'harvests',
        ['harvest_date']
    )
