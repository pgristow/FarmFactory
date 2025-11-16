"""
Water quality measurement model for TimescaleDB time-series data.

IMPORTANT: After migration, convert this table to a TimescaleDB hypertable:
    SELECT create_hypertable('water_quality', 'time');
"""
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Numeric, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
import uuid

from app.models.base import Base


class WaterQuality(Base):
    """
    Time-series water quality measurements.

    This table will be converted to a TimescaleDB hypertable partitioned by time.
    Tracks water quality parameters for irrigation sources.
    """

    __tablename__ = "water_quality"

    # Time column (primary partitioning key for TimescaleDB)
    time: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        primary_key=True,
        comment="Timestamp of water quality measurement",
    )

    # Foreign Keys (composite primary key with time)
    plot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plots.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
        comment="Reference to the plot",
    )

    # Water Source
    source: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Water source (well, municipal, reservoir, river, etc.)",
    )

    # Chemical Parameters
    ph_level: Mapped[Optional[float]] = mapped_column(
        Numeric(3, 1), nullable=True, comment="pH level (0-14 scale)"
    )

    ec_ds_per_m: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 3),
        nullable=True,
        comment="Electrical conductivity in dS/m (deciSiemens per meter)",
    )

    tds_ppm: Mapped[Optional[float]] = mapped_column(
        Numeric(8, 2),
        nullable=True,
        comment="Total dissolved solids in parts per million (ppm)",
    )

    # Physical Parameters
    temperature_celsius: Mapped[Optional[float]] = mapped_column(
        Numeric(4, 1), nullable=True, comment="Water temperature in Celsius"
    )

    dissolved_oxygen_ppm: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Dissolved oxygen content in parts per million",
    )

    turbidity_ntu: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 2),
        nullable=True,
        comment="Turbidity in Nephelometric Turbidity Units (NTU)",
    )

    # Additional Information
    notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Additional notes about the measurement"
    )

    # Relationships
    plot: Mapped["Plot"] = relationship("Plot", back_populates="water_quality_readings")

    # Indexes for TimescaleDB performance
    __table_args__ = (
        Index("ix_water_quality_plot_time", "plot_id", "time"),
        Index("ix_water_quality_source", "source"),
    )

    def __repr__(self):
        return f"<WaterQuality(plot_id={self.plot_id}, time={self.time}, ph={self.ph_level}, ec={self.ec_ds_per_m})>"
