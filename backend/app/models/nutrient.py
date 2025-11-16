"""
Nutrient application model for TimescaleDB time-series data.

IMPORTANT: After migration, convert this table to a TimescaleDB hypertable:
    SELECT create_hypertable('nutrient_applications', 'time');
"""
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Numeric, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
import uuid

from app.models.base import Base


class NutrientApplication(Base):
    """
    Time-series nutrient/fertilizer applications.

    This table will be converted to a TimescaleDB hypertable partitioned by time.
    Tracks all nutrient applications including NPK ratios and costs.
    """

    __tablename__ = "nutrient_applications"

    # Time column (primary partitioning key for TimescaleDB)
    time: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        primary_key=True,
        comment="Timestamp of nutrient application",
    )

    # Foreign Keys (composite primary key with time)
    plot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plots.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
        comment="Reference to the plot",
    )

    # Nutrient Type and Method
    nutrient_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Type of nutrient (N, P, K, Micronutrients, Compost, Organic, etc.)",
    )

    application_method: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Application method (broadcast, fertigation, foliar, side-dress, etc.)",
    )

    # Application Amounts
    amount_kg: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 3), nullable=True, comment="Total amount applied in kilograms"
    )

    npk_ratio: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="NPK ratio (e.g., '10-10-10', '20-5-10')"
    )

    # Individual Nutrient Quantities
    nitrogen_kg: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 3), nullable=True, comment="Nitrogen content in kilograms"
    )

    phosphorus_kg: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 3), nullable=True, comment="Phosphorus content in kilograms"
    )

    potassium_kg: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 3), nullable=True, comment="Potassium content in kilograms"
    )

    # Cost Tracking
    cost_usd: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="Cost of application in USD"
    )

    # Additional Information
    notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Additional notes about the application"
    )

    # Relationships
    plot: Mapped["Plot"] = relationship("Plot", back_populates="nutrient_applications")

    # Indexes for TimescaleDB performance
    __table_args__ = (
        Index("ix_nutrient_applications_plot_time", "plot_id", "time"),
        Index("ix_nutrient_applications_nutrient_type", "nutrient_type"),
        Index("ix_nutrient_applications_method", "application_method"),
    )

    def __repr__(self):
        return f"<NutrientApplication(plot_id={self.plot_id}, time={self.time}, type='{self.nutrient_type}', amount={self.amount_kg}kg)>"
