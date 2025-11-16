"""
Irrigation event model for TimescaleDB time-series data.

IMPORTANT: After migration, convert this table to a TimescaleDB hypertable:
    SELECT create_hypertable('irrigation_events', 'time');
"""
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Numeric, ForeignKey, Integer, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
import uuid

from app.models.base import Base


class IrrigationEvent(Base):
    """
    Time-series irrigation events.

    This table will be converted to a TimescaleDB hypertable partitioned by time.
    Records every irrigation event with water volume, duration, and method.
    """

    __tablename__ = "irrigation_events"

    # Time column (primary partitioning key for TimescaleDB)
    time: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        primary_key=True,
        comment="Timestamp of irrigation event",
    )

    # Foreign Keys (composite primary key with time)
    plot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plots.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
        comment="Reference to the plot",
    )

    # Irrigation Details
    method: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Irrigation method (drip, sprinkler, flood, manual)",
    )

    duration_minutes: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Duration of irrigation in minutes"
    )

    water_volume_liters: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="Total water volume in liters"
    )

    water_source: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="Water source (well, municipal, reservoir, etc.)"
    )

    # Technical Measurements
    flow_rate_lpm: Mapped[Optional[float]] = mapped_column(
        Numeric(8, 2), nullable=True, comment="Flow rate in liters per minute"
    )

    pressure_bar: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2), nullable=True, comment="Water pressure in bar"
    )

    # Additional Information
    notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Additional notes about the irrigation event"
    )

    # Relationships
    plot: Mapped["Plot"] = relationship("Plot", back_populates="irrigation_events")

    # Indexes for TimescaleDB performance
    # TimescaleDB automatically creates indexes on time column
    __table_args__ = (
        Index("ix_irrigation_events_plot_time", "plot_id", "time"),
        Index("ix_irrigation_events_method", "method"),
    )

    def __repr__(self):
        return f"<IrrigationEvent(plot_id={self.plot_id}, time={self.time}, volume={self.water_volume_liters}L)>"
