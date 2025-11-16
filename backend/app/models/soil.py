"""
Soil profile model for storing soil characteristics and test results.
"""
from typing import Optional
from datetime import date
from sqlalchemy import String, Numeric, ForeignKey, Date, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import Base, TimestampMixin, UUIDMixin


class SoilProfile(Base, UUIDMixin, TimestampMixin):
    """
    Soil profile information for a plot.

    Stores soil characteristics and test results over time.
    Multiple profiles can exist for a plot to track changes.
    """

    __tablename__ = "soil_profiles"

    # Foreign Keys
    plot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to the plot",
    )

    # Soil Classification
    soil_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Soil type (e.g., Clay, Sandy, Loam, Silt)",
    )

    texture: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Soil texture classification",
    )

    drainage_class: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Drainage classification (e.g., well-drained, poorly-drained)",
    )

    # Chemical Properties
    ph_level: Mapped[Optional[float]] = mapped_column(
        Numeric(3, 1),
        nullable=True,
        comment="Soil pH level (0-14 scale)",
    )

    organic_matter_percent: Mapped[Optional[float]] = mapped_column(
        Numeric(4, 2),
        nullable=True,
        comment="Organic matter content as percentage",
    )

    cec_meq_per_100g: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Cation Exchange Capacity in meq/100g",
    )

    # Physical Properties
    bulk_density: Mapped[Optional[float]] = mapped_column(
        Numeric(4, 2),
        nullable=True,
        comment="Bulk density in g/cm³",
    )

    porosity_percent: Mapped[Optional[float]] = mapped_column(
        Numeric(4, 2),
        nullable=True,
        comment="Soil porosity as percentage",
    )

    # Test Information
    test_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="Date when soil test was conducted"
    )

    notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Additional notes about the soil profile"
    )

    # Relationships
    plot: Mapped["Plot"] = relationship("Plot", back_populates="soil_profiles")

    # Indexes
    __table_args__ = (Index("ix_soil_profiles_plot_test_date", "plot_id", "test_date"),)

    def __repr__(self):
        return f"<SoilProfile(id={self.id}, type='{self.soil_type}', ph={self.ph_level})>"
