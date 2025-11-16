"""
Financial tracking models for input costs and harvest revenue.
"""
from typing import Optional
from datetime import date
from sqlalchemy import String, Numeric, ForeignKey, Date, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import Base, TimestampMixin, UUIDMixin


class InputCost(Base, UUIDMixin, TimestampMixin):
    """
    Input costs tracking all farm expenses.

    Tracks costs for seeds, fertilizer, water, labor, equipment, and other inputs
    associated with specific plots or plantings.
    """

    __tablename__ = "input_costs"

    # Foreign Keys (nullable to allow farm-wide costs)
    plot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plots.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Reference to the plot (optional)",
    )

    planting_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plantings.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Reference to the planting (optional)",
    )

    # Cost Information
    cost_date: Mapped[date] = mapped_column(
        Date, nullable=False, index=True, comment="Date when cost was incurred"
    )

    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Cost category (seeds, fertilizer, water, labor, equipment, pesticide, etc.)",
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Detailed description of the cost"
    )

    # Quantity and Pricing
    quantity: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 3), nullable=True, comment="Quantity purchased/used"
    )

    unit: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="Unit of measurement (kg, liters, hours, etc.)"
    )

    unit_cost: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="Cost per unit"
    )

    total_cost: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False, comment="Total cost amount"
    )

    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="USD", comment="Currency code (ISO 4217)"
    )

    # Relationships
    plot: Mapped[Optional["Plot"]] = relationship("Plot", back_populates="input_costs")
    planting: Mapped[Optional["Planting"]] = relationship(
        "Planting", back_populates="input_costs"
    )

    # Indexes
    __table_args__ = (
        Index("ix_input_costs_plot_cost_date", "plot_id", "cost_date"),
        Index("ix_input_costs_planting_cost_date", "planting_id", "cost_date"),
        Index("ix_input_costs_category_cost_date", "category", "cost_date"),
    )

    def __repr__(self):
        return f"<InputCost(id={self.id}, category='{self.category}', amount={self.total_cost} {self.currency})>"


class Harvest(Base, UUIDMixin, TimestampMixin):
    """
    Harvest records tracking yield and revenue.

    Records harvest events including quantity, quality, and revenue
    for each planting.
    """

    __tablename__ = "harvests"

    # Foreign Keys
    planting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plantings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to the planting",
    )

    # Harvest Information
    harvest_date: Mapped[date] = mapped_column(
        Date, nullable=False, index=True, comment="Date of harvest"
    )

    # Yield Data
    quantity_kg: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="Harvested quantity in kilograms"
    )

    quality_grade: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Quality grade (A, B, C, Premium, Standard, etc.)",
    )

    # Revenue Data
    revenue_usd: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="Revenue from harvest in USD"
    )

    market: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Market where produce was sold (farmers market, wholesale, direct, etc.)",
    )

    # Additional Information
    notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Additional notes about the harvest"
    )

    # Relationships
    planting: Mapped["Planting"] = relationship("Planting", back_populates="harvests")

    # Indexes
    __table_args__ = (
        Index("ix_harvests_planting_harvest_date", "planting_id", "harvest_date"),
        Index("ix_harvests_harvest_date", "harvest_date"),
    )

    def __repr__(self):
        return f"<Harvest(id={self.id}, date={self.harvest_date}, quantity={self.quantity_kg}kg, revenue={self.revenue_usd} USD)>"
