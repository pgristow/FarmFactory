"""
Plot (field) model with PostGIS polygon support.
Represents individual fields/plots within a farm.
"""
from typing import Optional, List
from sqlalchemy import String, Numeric, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
import uuid

from app.models.base import Base, TimestampMixin, UUIDMixin


class Plot(Base, UUIDMixin, TimestampMixin):
    """
    Plot/Field entity representing a subdivision of a farm.

    Each plot has its own geographic boundaries (polygon), soil profile,
    and can have multiple plantings over time.
    """

    __tablename__ = "plots"

    # Foreign Keys
    farm_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("farms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to parent farm",
    )

    # Basic Information
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="Plot name or identifier"
    )

    plot_number: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="Plot number or code for reference"
    )

    # Geographic Information (PostGIS)
    # POLYGON stores the plot boundaries in WGS84 (SRID 4326)
    location: Mapped[Optional[Geography]] = mapped_column(
        Geography(geometry_type="POLYGON", srid=4326),
        nullable=True,
        comment="Geographic boundaries of the plot (polygon)",
    )

    # Plot Metrics
    area_hectares: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="Plot area in hectares"
    )

    elevation_meters: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 2), nullable=True, comment="Average elevation above sea level in meters"
    )

    slope_degrees: Mapped[Optional[float]] = mapped_column(
        Numeric(4, 2), nullable=True, comment="Average slope in degrees"
    )

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm", back_populates="plots")

    soil_profiles: Mapped[List["SoilProfile"]] = relationship(
        "SoilProfile", back_populates="plot", cascade="all, delete-orphan"
    )

    plantings: Mapped[List["Planting"]] = relationship(
        "Planting", back_populates="plot", cascade="all, delete-orphan"
    )

    irrigation_events: Mapped[List["IrrigationEvent"]] = relationship(
        "IrrigationEvent", back_populates="plot", cascade="all, delete-orphan"
    )

    nutrient_applications: Mapped[List["NutrientApplication"]] = relationship(
        "NutrientApplication", back_populates="plot", cascade="all, delete-orphan"
    )

    water_quality_readings: Mapped[List["WaterQuality"]] = relationship(
        "WaterQuality", back_populates="plot", cascade="all, delete-orphan"
    )

    environmental_readings: Mapped[List["EnvironmentalReading"]] = relationship(
        "EnvironmentalReading", back_populates="plot", cascade="all, delete-orphan"
    )

    input_costs: Mapped[List["InputCost"]] = relationship(
        "InputCost", back_populates="plot", cascade="all, delete-orphan"
    )

    alert_thresholds: Mapped[List["AlertThreshold"]] = relationship(
        "AlertThreshold", back_populates="plot", cascade="all, delete-orphan"
    )

    alerts: Mapped[List["Alert"]] = relationship(
        "Alert", back_populates="plot", cascade="all, delete-orphan"
    )

    # Indexes for performance
    __table_args__ = (
        Index("ix_plots_location", "location", postgresql_using="gist"),
        Index("ix_plots_farm_id_name", "farm_id", "name"),
    )

    def __repr__(self):
        return f"<Plot(id={self.id}, name='{self.name}', area={self.area_hectares}ha)>"
