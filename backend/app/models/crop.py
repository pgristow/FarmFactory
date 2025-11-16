"""
Crop and Planting models for tracking crops and their lifecycle.
"""
from typing import Optional, List
from datetime import date
from sqlalchemy import String, Numeric, ForeignKey, Date, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import Base, TimestampMixin, UUIDMixin


class Crop(Base, UUIDMixin, TimestampMixin):
    """
    Crop master table containing crop varieties and their characteristics.

    This is a reference table for crop types that can be planted.
    """

    __tablename__ = "crops"

    # Basic Information
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="Common crop name"
    )

    scientific_name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="Scientific name (binomial nomenclature)"
    )

    variety: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="Crop variety or cultivar"
    )

    # Optimal Growing Conditions
    optimal_temp_min_celsius: Mapped[Optional[float]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
        comment="Minimum optimal temperature in Celsius",
    )

    optimal_temp_max_celsius: Mapped[Optional[float]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
        comment="Maximum optimal temperature in Celsius",
    )

    optimal_ph_min: Mapped[Optional[float]] = mapped_column(
        Numeric(3, 1), nullable=True, comment="Minimum optimal soil pH"
    )

    optimal_ph_max: Mapped[Optional[float]] = mapped_column(
        Numeric(3, 1), nullable=True, comment="Maximum optimal soil pH"
    )

    # Growth Characteristics
    days_to_maturity: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Typical days from planting to harvest"
    )

    # Relationships
    plantings: Mapped[List["Planting"]] = relationship(
        "Planting", back_populates="crop"
    )

    def __repr__(self):
        return f"<Crop(id={self.id}, name='{self.name}', variety='{self.variety}')>"


class Planting(Base, UUIDMixin, TimestampMixin):
    """
    Planting records tracking specific crop plantings in plots.

    Each planting represents a specific crop grown in a specific plot
    during a specific time period.
    """

    __tablename__ = "plantings"

    # Foreign Keys
    plot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to the plot",
    )

    crop_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crops.id"),
        nullable=False,
        index=True,
        comment="Reference to the crop",
    )

    # Planting Dates
    planting_date: Mapped[date] = mapped_column(
        Date, nullable=False, index=True, comment="Date when crop was planted"
    )

    expected_harvest_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="Expected harvest date"
    )

    actual_harvest_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="Actual harvest date"
    )

    # Planting Details
    plant_population: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Number of plants"
    )

    row_spacing_cm: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2), nullable=True, comment="Row spacing in centimeters"
    )

    plant_spacing_cm: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2), nullable=True, comment="Plant spacing within row in centimeters"
    )

    # Status Tracking
    status: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default="planted",
        comment="Current status: planted, growing, harvested, failed",
    )

    # Relationships
    plot: Mapped["Plot"] = relationship("Plot", back_populates="plantings")
    crop: Mapped["Crop"] = relationship("Crop", back_populates="plantings")

    phenology_observations: Mapped[List["PhenologyObservation"]] = relationship(
        "PhenologyObservation", back_populates="planting", cascade="all, delete-orphan"
    )

    harvests: Mapped[List["Harvest"]] = relationship(
        "Harvest", back_populates="planting", cascade="all, delete-orphan"
    )

    input_costs: Mapped[List["InputCost"]] = relationship(
        "InputCost", back_populates="planting", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("ix_plantings_plot_planting_date", "plot_id", "planting_date"),
        Index("ix_plantings_status", "status"),
    )

    def __repr__(self):
        return f"<Planting(id={self.id}, crop_id={self.crop_id}, date={self.planting_date}, status='{self.status}')>"
