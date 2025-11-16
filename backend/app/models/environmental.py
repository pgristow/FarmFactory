"""
Environmental reading model for TimescaleDB time-series data.

IMPORTANT: After migration, convert this table to a TimescaleDB hypertable:
    SELECT create_hypertable('environmental_readings', 'time');
"""
from typing import Optional
from datetime import datetime
from sqlalchemy import Numeric, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
import uuid

from app.models.base import Base


class EnvironmentalReading(Base):
    """
    Time-series environmental sensor readings.

    This table will be converted to a TimescaleDB hypertable partitioned by time.
    Captures environmental conditions including temperature, humidity, and soil moisture.
    """

    __tablename__ = "environmental_readings"

    # Time column (primary partitioning key for TimescaleDB)
    time: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        primary_key=True,
        comment="Timestamp of environmental reading",
    )

    # Foreign Keys (composite primary key with time)
    plot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plots.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
        comment="Reference to the plot",
    )

    # Temperature Measurements
    air_temp_celsius: Mapped[Optional[float]] = mapped_column(
        Numeric(4, 1), nullable=True, comment="Air temperature in Celsius"
    )

    soil_temp_celsius: Mapped[Optional[float]] = mapped_column(
        Numeric(4, 1), nullable=True, comment="Soil temperature in Celsius"
    )

    # Humidity and Moisture
    humidity_percent: Mapped[Optional[float]] = mapped_column(
        Numeric(4, 1), nullable=True, comment="Relative air humidity percentage (0-100)"
    )

    soil_moisture_percent: Mapped[Optional[float]] = mapped_column(
        Numeric(4, 1), nullable=True, comment="Soil moisture percentage (0-100)"
    )

    # Light and Precipitation
    light_intensity_lux: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="Light intensity in lux"
    )

    rainfall_mm: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 2), nullable=True, comment="Rainfall amount in millimeters"
    )

    # Wind and Atmospheric Pressure
    wind_speed_kmh: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2), nullable=True, comment="Wind speed in kilometers per hour"
    )

    atmospheric_pressure_hpa: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 1), nullable=True, comment="Atmospheric pressure in hectopascals (hPa)"
    )

    # Relationships
    plot: Mapped["Plot"] = relationship("Plot", back_populates="environmental_readings")

    # Indexes for TimescaleDB performance
    # Create indexes on commonly queried columns
    __table_args__ = (
        Index("ix_environmental_readings_plot_time", "plot_id", "time"),
        Index("ix_environmental_readings_soil_moisture", "soil_moisture_percent"),
        Index("ix_environmental_readings_air_temp", "air_temp_celsius"),
    )

    def __repr__(self):
        return f"<EnvironmentalReading(plot_id={self.plot_id}, time={self.time}, temp={self.air_temp_celsius}°C, moisture={self.soil_moisture_percent}%)>"
