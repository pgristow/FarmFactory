"""Initial database schema with all tables

Revision ID: 001
Revises:
Create Date: 2025-11-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable PostGIS extension
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')

    # Enable TimescaleDB extension
    op.execute('CREATE EXTENSION IF NOT EXISTS timescaledb')

    # Create farms table
    op.create_table(
        'farms',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique identifier (UUID v4)'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Farm name'),
        sa.Column('address', sa.String(), nullable=True, comment='Physical address of the farm'),
        sa.Column('location', geoalchemy2.Geography(geometry_type='POINT', srid=4326, from_text='ST_GeogFromText', name='geography'), nullable=True, comment='Geographic coordinates (lat/lon) of farm center'),
        sa.Column('total_area_hectares', sa.Numeric(precision=10, scale=2), nullable=True, comment='Total farm area in hectares'),
        sa.Column('timezone', sa.String(length=50), nullable=True, comment="Timezone for the farm (e.g., 'America/Los_Angeles')"),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_farms_location', 'farms', ['location'], postgresql_using='gist')
    op.create_index('ix_farms_name', 'farms', ['name'])

    # Create plots table
    op.create_table(
        'plots',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique identifier (UUID v4)'),
        sa.Column('farm_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Reference to parent farm'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Plot name or identifier'),
        sa.Column('plot_number', sa.String(length=50), nullable=True, comment='Plot number or code for reference'),
        sa.Column('location', geoalchemy2.Geography(geometry_type='POLYGON', srid=4326, from_text='ST_GeogFromText', name='geography'), nullable=True, comment='Geographic boundaries of the plot (polygon)'),
        sa.Column('area_hectares', sa.Numeric(precision=10, scale=2), nullable=True, comment='Plot area in hectares'),
        sa.Column('elevation_meters', sa.Numeric(precision=6, scale=2), nullable=True, comment='Average elevation above sea level in meters'),
        sa.Column('slope_degrees', sa.Numeric(precision=4, scale=2), nullable=True, comment='Average slope in degrees'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_plots_farm_id', 'plots', ['farm_id'])
    op.create_index('ix_plots_location', 'plots', ['location'], postgresql_using='gist')
    op.create_index('ix_plots_name', 'plots', ['name'])
    op.create_index('ix_plots_farm_id_name', 'plots', ['farm_id', 'name'])

    # Create soil_profiles table
    op.create_table(
        'soil_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique identifier (UUID v4)'),
        sa.Column('plot_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Reference to the plot'),
        sa.Column('soil_type', sa.String(length=100), nullable=True, comment='Soil type (e.g., Clay, Sandy, Loam, Silt)'),
        sa.Column('texture', sa.String(length=50), nullable=True, comment='Soil texture classification'),
        sa.Column('drainage_class', sa.String(length=50), nullable=True, comment='Drainage classification (e.g., well-drained, poorly-drained)'),
        sa.Column('ph_level', sa.Numeric(precision=3, scale=1), nullable=True, comment='Soil pH level (0-14 scale)'),
        sa.Column('organic_matter_percent', sa.Numeric(precision=4, scale=2), nullable=True, comment='Organic matter content as percentage'),
        sa.Column('cec_meq_per_100g', sa.Numeric(precision=5, scale=2), nullable=True, comment='Cation Exchange Capacity in meq/100g'),
        sa.Column('bulk_density', sa.Numeric(precision=4, scale=2), nullable=True, comment='Bulk density in g/cm³'),
        sa.Column('porosity_percent', sa.Numeric(precision=4, scale=2), nullable=True, comment='Soil porosity as percentage'),
        sa.Column('test_date', sa.Date(), nullable=True, comment='Date when soil test was conducted'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Additional notes about the soil profile'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['plot_id'], ['plots.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_soil_profiles_plot_id', 'soil_profiles', ['plot_id'])
    op.create_index('ix_soil_profiles_plot_test_date', 'soil_profiles', ['plot_id', 'test_date'])

    # Create crops table
    op.create_table(
        'crops',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique identifier (UUID v4)'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Common crop name'),
        sa.Column('scientific_name', sa.String(length=255), nullable=True, comment='Scientific name (binomial nomenclature)'),
        sa.Column('variety', sa.String(length=255), nullable=True, comment='Crop variety or cultivar'),
        sa.Column('optimal_temp_min_celsius', sa.Numeric(precision=4, scale=1), nullable=True, comment='Minimum optimal temperature in Celsius'),
        sa.Column('optimal_temp_max_celsius', sa.Numeric(precision=4, scale=1), nullable=True, comment='Maximum optimal temperature in Celsius'),
        sa.Column('optimal_ph_min', sa.Numeric(precision=3, scale=1), nullable=True, comment='Minimum optimal soil pH'),
        sa.Column('optimal_ph_max', sa.Numeric(precision=3, scale=1), nullable=True, comment='Maximum optimal soil pH'),
        sa.Column('days_to_maturity', sa.Integer(), nullable=True, comment='Typical days from planting to harvest'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_crops_name', 'crops', ['name'])

    # Create plantings table
    op.create_table(
        'plantings',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique identifier (UUID v4)'),
        sa.Column('plot_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Reference to the plot'),
        sa.Column('crop_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Reference to the crop'),
        sa.Column('planting_date', sa.Date(), nullable=False, comment='Date when crop was planted'),
        sa.Column('expected_harvest_date', sa.Date(), nullable=True, comment='Expected harvest date'),
        sa.Column('actual_harvest_date', sa.Date(), nullable=True, comment='Actual harvest date'),
        sa.Column('plant_population', sa.Integer(), nullable=True, comment='Number of plants'),
        sa.Column('row_spacing_cm', sa.Numeric(precision=5, scale=2), nullable=True, comment='Row spacing in centimeters'),
        sa.Column('plant_spacing_cm', sa.Numeric(precision=5, scale=2), nullable=True, comment='Plant spacing within row in centimeters'),
        sa.Column('status', sa.String(length=50), nullable=True, comment='Current status: planted, growing, harvested, failed'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['crop_id'], ['crops.id']),
        sa.ForeignKeyConstraint(['plot_id'], ['plots.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_plantings_crop_id', 'plantings', ['crop_id'])
    op.create_index('ix_plantings_planting_date', 'plantings', ['planting_date'])
    op.create_index('ix_plantings_plot_id', 'plantings', ['plot_id'])
    op.create_index('ix_plantings_status', 'plantings', ['status'])
    op.create_index('ix_plantings_plot_planting_date', 'plantings', ['plot_id', 'planting_date'])

    # Create phenology_observations table
    op.create_table(
        'phenology_observations',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique identifier (UUID v4)'),
        sa.Column('planting_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Reference to the planting'),
        sa.Column('observation_date', sa.Date(), nullable=False, comment='Date of observation'),
        sa.Column('growth_stage', sa.String(length=100), nullable=True, comment='Growth stage (e.g., germination, vegetative, flowering, fruiting, maturity)'),
        sa.Column('bbch_code', sa.Integer(), nullable=True, comment='BBCH phenological scale code (standard international scale)'),
        sa.Column('height_cm', sa.Numeric(precision=6, scale=2), nullable=True, comment='Plant height in centimeters'),
        sa.Column('canopy_cover_percent', sa.Numeric(precision=4, scale=1), nullable=True, comment='Canopy cover percentage (0-100)'),
        sa.Column('health_score', sa.Integer(), nullable=True, comment='Health score from 1 (poor) to 10 (excellent)'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Observation notes and details'),
        sa.Column('photos', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Array of photo URLs or metadata in JSON format'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.CheckConstraint('health_score >= 1 AND health_score <= 10', name='check_health_score_range'),
        sa.CheckConstraint('canopy_cover_percent >= 0 AND canopy_cover_percent <= 100', name='check_canopy_cover_range'),
        sa.ForeignKeyConstraint(['planting_id'], ['plantings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_phenology_observations_observation_date', 'phenology_observations', ['observation_date'])
    op.create_index('ix_phenology_observations_planting_id', 'phenology_observations', ['planting_id'])
    op.create_index('ix_phenology_planting_observation_date', 'phenology_observations', ['planting_id', 'observation_date'])

    # Create time-series tables (will be converted to hypertables in next migration)

    # Create irrigation_events table
    op.create_table(
        'irrigation_events',
        sa.Column('time', postgresql.TIMESTAMP(timezone=True), nullable=False, comment='Timestamp of irrigation event'),
        sa.Column('plot_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Reference to the plot'),
        sa.Column('method', sa.String(length=50), nullable=True, comment='Irrigation method (drip, sprinkler, flood, manual)'),
        sa.Column('duration_minutes', sa.Integer(), nullable=True, comment='Duration of irrigation in minutes'),
        sa.Column('water_volume_liters', sa.Numeric(precision=10, scale=2), nullable=True, comment='Total water volume in liters'),
        sa.Column('water_source', sa.String(length=100), nullable=True, comment='Water source (well, municipal, reservoir, etc.)'),
        sa.Column('flow_rate_lpm', sa.Numeric(precision=8, scale=2), nullable=True, comment='Flow rate in liters per minute'),
        sa.Column('pressure_bar', sa.Numeric(precision=5, scale=2), nullable=True, comment='Water pressure in bar'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Additional notes about the irrigation event'),
        sa.ForeignKeyConstraint(['plot_id'], ['plots.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('time', 'plot_id')
    )
    op.create_index('ix_irrigation_events_method', 'irrigation_events', ['method'])
    op.create_index('ix_irrigation_events_plot_time', 'irrigation_events', ['plot_id', 'time'])

    # Create nutrient_applications table
    op.create_table(
        'nutrient_applications',
        sa.Column('time', postgresql.TIMESTAMP(timezone=True), nullable=False, comment='Timestamp of nutrient application'),
        sa.Column('plot_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Reference to the plot'),
        sa.Column('nutrient_type', sa.String(length=100), nullable=True, comment='Type of nutrient (N, P, K, Micronutrients, Compost, Organic, etc.)'),
        sa.Column('application_method', sa.String(length=50), nullable=True, comment='Application method (broadcast, fertigation, foliar, side-dress, etc.)'),
        sa.Column('amount_kg', sa.Numeric(precision=10, scale=3), nullable=True, comment='Total amount applied in kilograms'),
        sa.Column('npk_ratio', sa.String(length=20), nullable=True, comment="NPK ratio (e.g., '10-10-10', '20-5-10')"),
        sa.Column('nitrogen_kg', sa.Numeric(precision=10, scale=3), nullable=True, comment='Nitrogen content in kilograms'),
        sa.Column('phosphorus_kg', sa.Numeric(precision=10, scale=3), nullable=True, comment='Phosphorus content in kilograms'),
        sa.Column('potassium_kg', sa.Numeric(precision=10, scale=3), nullable=True, comment='Potassium content in kilograms'),
        sa.Column('cost_usd', sa.Numeric(precision=10, scale=2), nullable=True, comment='Cost of application in USD'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Additional notes about the application'),
        sa.ForeignKeyConstraint(['plot_id'], ['plots.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('time', 'plot_id')
    )
    op.create_index('ix_nutrient_applications_method', 'nutrient_applications', ['application_method'])
    op.create_index('ix_nutrient_applications_nutrient_type', 'nutrient_applications', ['nutrient_type'])
    op.create_index('ix_nutrient_applications_plot_time', 'nutrient_applications', ['plot_id', 'time'])

    # Create water_quality table
    op.create_table(
        'water_quality',
        sa.Column('time', postgresql.TIMESTAMP(timezone=True), nullable=False, comment='Timestamp of water quality measurement'),
        sa.Column('plot_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Reference to the plot'),
        sa.Column('source', sa.String(length=100), nullable=True, comment='Water source (well, municipal, reservoir, river, etc.)'),
        sa.Column('ph_level', sa.Numeric(precision=3, scale=1), nullable=True, comment='pH level (0-14 scale)'),
        sa.Column('ec_ds_per_m', sa.Numeric(precision=6, scale=3), nullable=True, comment='Electrical conductivity in dS/m (deciSiemens per meter)'),
        sa.Column('tds_ppm', sa.Numeric(precision=8, scale=2), nullable=True, comment='Total dissolved solids in parts per million (ppm)'),
        sa.Column('temperature_celsius', sa.Numeric(precision=4, scale=1), nullable=True, comment='Water temperature in Celsius'),
        sa.Column('dissolved_oxygen_ppm', sa.Numeric(precision=5, scale=2), nullable=True, comment='Dissolved oxygen content in parts per million'),
        sa.Column('turbidity_ntu', sa.Numeric(precision=6, scale=2), nullable=True, comment='Turbidity in Nephelometric Turbidity Units (NTU)'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Additional notes about the measurement'),
        sa.ForeignKeyConstraint(['plot_id'], ['plots.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('time', 'plot_id')
    )
    op.create_index('ix_water_quality_plot_time', 'water_quality', ['plot_id', 'time'])
    op.create_index('ix_water_quality_source', 'water_quality', ['source'])

    # Create environmental_readings table
    op.create_table(
        'environmental_readings',
        sa.Column('time', postgresql.TIMESTAMP(timezone=True), nullable=False, comment='Timestamp of environmental reading'),
        sa.Column('plot_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Reference to the plot'),
        sa.Column('air_temp_celsius', sa.Numeric(precision=4, scale=1), nullable=True, comment='Air temperature in Celsius'),
        sa.Column('soil_temp_celsius', sa.Numeric(precision=4, scale=1), nullable=True, comment='Soil temperature in Celsius'),
        sa.Column('humidity_percent', sa.Numeric(precision=4, scale=1), nullable=True, comment='Relative air humidity percentage (0-100)'),
        sa.Column('soil_moisture_percent', sa.Numeric(precision=4, scale=1), nullable=True, comment='Soil moisture percentage (0-100)'),
        sa.Column('light_intensity_lux', sa.Numeric(precision=10, scale=2), nullable=True, comment='Light intensity in lux'),
        sa.Column('rainfall_mm', sa.Numeric(precision=6, scale=2), nullable=True, comment='Rainfall amount in millimeters'),
        sa.Column('wind_speed_kmh', sa.Numeric(precision=5, scale=2), nullable=True, comment='Wind speed in kilometers per hour'),
        sa.Column('atmospheric_pressure_hpa', sa.Numeric(precision=6, scale=1), nullable=True, comment='Atmospheric pressure in hectopascals (hPa)'),
        sa.ForeignKeyConstraint(['plot_id'], ['plots.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('time', 'plot_id')
    )
    op.create_index('ix_environmental_readings_air_temp', 'environmental_readings', ['air_temp_celsius'])
    op.create_index('ix_environmental_readings_plot_time', 'environmental_readings', ['plot_id', 'time'])
    op.create_index('ix_environmental_readings_soil_moisture', 'environmental_readings', ['soil_moisture_percent'])

    # Create financial tables

    # Create input_costs table
    op.create_table(
        'input_costs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique identifier (UUID v4)'),
        sa.Column('plot_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Reference to the plot (optional)'),
        sa.Column('planting_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Reference to the planting (optional)'),
        sa.Column('cost_date', sa.Date(), nullable=False, comment='Date when cost was incurred'),
        sa.Column('category', sa.String(length=100), nullable=True, comment='Cost category (seeds, fertilizer, water, labor, equipment, pesticide, etc.)'),
        sa.Column('description', sa.Text(), nullable=True, comment='Detailed description of the cost'),
        sa.Column('quantity', sa.Numeric(precision=10, scale=3), nullable=True, comment='Quantity purchased/used'),
        sa.Column('unit', sa.String(length=50), nullable=True, comment='Unit of measurement (kg, liters, hours, etc.)'),
        sa.Column('unit_cost', sa.Numeric(precision=10, scale=2), nullable=True, comment='Cost per unit'),
        sa.Column('total_cost', sa.Numeric(precision=12, scale=2), nullable=False, comment='Total cost amount'),
        sa.Column('currency', sa.String(length=3), nullable=False, comment='Currency code (ISO 4217)'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['planting_id'], ['plantings.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['plot_id'], ['plots.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_input_costs_category', 'input_costs', ['category'])
    op.create_index('ix_input_costs_cost_date', 'input_costs', ['cost_date'])
    op.create_index('ix_input_costs_planting_id', 'input_costs', ['planting_id'])
    op.create_index('ix_input_costs_plot_id', 'input_costs', ['plot_id'])
    op.create_index('ix_input_costs_category_cost_date', 'input_costs', ['category', 'cost_date'])
    op.create_index('ix_input_costs_planting_cost_date', 'input_costs', ['planting_id', 'cost_date'])
    op.create_index('ix_input_costs_plot_cost_date', 'input_costs', ['plot_id', 'cost_date'])

    # Create harvests table
    op.create_table(
        'harvests',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique identifier (UUID v4)'),
        sa.Column('planting_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Reference to the planting'),
        sa.Column('harvest_date', sa.Date(), nullable=False, comment='Date of harvest'),
        sa.Column('quantity_kg', sa.Numeric(precision=10, scale=2), nullable=True, comment='Harvested quantity in kilograms'),
        sa.Column('quality_grade', sa.String(length=50), nullable=True, comment='Quality grade (A, B, C, Premium, Standard, etc.)'),
        sa.Column('revenue_usd', sa.Numeric(precision=12, scale=2), nullable=True, comment='Revenue from harvest in USD'),
        sa.Column('market', sa.String(length=100), nullable=True, comment='Market where produce was sold (farmers market, wholesale, direct, etc.)'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Additional notes about the harvest'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.ForeignKeyConstraint(['planting_id'], ['plantings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_harvests_harvest_date', 'harvests', ['harvest_date'])
    op.create_index('ix_harvests_planting_id', 'harvests', ['planting_id'])
    op.create_index('ix_harvests_planting_harvest_date', 'harvests', ['planting_id', 'harvest_date'])

    # Create alert tables

    # Create alert_thresholds table
    op.create_table(
        'alert_thresholds',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique identifier (UUID v4)'),
        sa.Column('plot_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Reference to the plot (null for global thresholds)'),
        sa.Column('parameter', sa.String(length=100), nullable=False, comment='Parameter to monitor (soil_moisture, ph, ec, temperature, etc.)'),
        sa.Column('min_value', sa.Numeric(precision=10, scale=3), nullable=True, comment='Minimum acceptable value'),
        sa.Column('max_value', sa.Numeric(precision=10, scale=3), nullable=True, comment='Maximum acceptable value'),
        sa.Column('severity', sa.String(length=20), nullable=False, comment='Alert severity (info, warning, critical)'),
        sa.Column('active', sa.Boolean(), nullable=False, comment='Whether this threshold is active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.CheckConstraint("severity IN ('info', 'warning', 'critical')", name='check_severity_values'),
        sa.ForeignKeyConstraint(['plot_id'], ['plots.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_alert_thresholds_active', 'alert_thresholds', ['active'])
    op.create_index('ix_alert_thresholds_parameter', 'alert_thresholds', ['parameter'])
    op.create_index('ix_alert_thresholds_plot_id', 'alert_thresholds', ['plot_id'])
    op.create_index('ix_alert_thresholds_plot_parameter', 'alert_thresholds', ['plot_id', 'parameter'])

    # Create alerts table
    op.create_table(
        'alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Unique identifier (UUID v4)'),
        sa.Column('plot_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Reference to the plot'),
        sa.Column('alert_threshold_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Reference to the threshold configuration'),
        sa.Column('triggered_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False, comment='When the alert was triggered'),
        sa.Column('parameter', sa.String(length=100), nullable=False, comment='Parameter that triggered the alert'),
        sa.Column('current_value', sa.Numeric(precision=10, scale=3), nullable=True, comment='Current value that triggered the alert'),
        sa.Column('threshold_min', sa.Numeric(precision=10, scale=3), nullable=True, comment='Minimum threshold value at time of alert'),
        sa.Column('threshold_max', sa.Numeric(precision=10, scale=3), nullable=True, comment='Maximum threshold value at time of alert'),
        sa.Column('severity', sa.String(length=20), nullable=False, comment='Alert severity (info, warning, critical)'),
        sa.Column('message', sa.Text(), nullable=True, comment='Human-readable alert message'),
        sa.Column('acknowledged', sa.Boolean(), nullable=False, comment='Whether alert has been acknowledged'),
        sa.Column('acknowledged_at', postgresql.TIMESTAMP(timezone=True), nullable=True, comment='When the alert was acknowledged'),
        sa.Column('resolved', sa.Boolean(), nullable=False, comment='Whether the alert has been resolved'),
        sa.Column('resolved_at', postgresql.TIMESTAMP(timezone=True), nullable=True, comment='When the alert was resolved'),
        sa.CheckConstraint("severity IN ('info', 'warning', 'critical')", name='check_alert_severity_values'),
        sa.ForeignKeyConstraint(['alert_threshold_id'], ['alert_thresholds.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['plot_id'], ['plots.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_alerts_acknowledged', 'alerts', ['acknowledged'])
    op.create_index('ix_alerts_active', 'alerts', ['acknowledged', 'resolved'])
    op.create_index('ix_alerts_alert_threshold_id', 'alerts', ['alert_threshold_id'])
    op.create_index('ix_alerts_plot_id', 'alerts', ['plot_id'])
    op.create_index('ix_alerts_resolved', 'alerts', ['resolved'])
    op.create_index('ix_alerts_severity', 'alerts', ['severity'])
    op.create_index('ix_alerts_triggered_at', 'alerts', ['triggered_at'])
    op.create_index('ix_alerts_plot_triggered_at', 'alerts', ['plot_id', 'triggered_at'])


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_table('alerts')
    op.drop_table('alert_thresholds')
    op.drop_table('harvests')
    op.drop_table('input_costs')
    op.drop_table('environmental_readings')
    op.drop_table('water_quality')
    op.drop_table('nutrient_applications')
    op.drop_table('irrigation_events')
    op.drop_table('phenology_observations')
    op.drop_table('plantings')
    op.drop_table('crops')
    op.drop_table('soil_profiles')
    op.drop_table('plots')
    op.drop_table('farms')

    # Drop extensions
    op.execute('DROP EXTENSION IF EXISTS timescaledb')
    op.execute('DROP EXTENSION IF EXISTS postgis')
