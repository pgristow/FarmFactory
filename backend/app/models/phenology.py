"""
Phenology observation model for tracking crop growth stages.
"""
from typing import Optional
from datetime import date
from sqlalchemy import String, Numeric, ForeignKey, Date, Text, Integer, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.models.base import Base, TimestampMixin, UUIDMixin


class PhenologyObservation(Base, UUIDMixin, TimestampMixin):
    """
    Phenology observations tracking crop growth stages over time.

    Records periodic observations of plant growth, development stages,
    and overall health throughout the growing season.
    """

    __tablename__ = "phenology_observations"

    # Foreign Keys
    planting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plantings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Reference to the planting",
    )

    # Observation Information
    observation_date: Mapped[date] = mapped_column(
        Date, nullable=False, index=True, comment="Date of observation"
    )

    # Growth Stage
    growth_stage: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Growth stage (e.g., germination, vegetative, flowering, fruiting, maturity)",
    )

    bbch_code: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="BBCH phenological scale code (standard international scale)",
    )

    # Physical Measurements
    height_cm: Mapped[Optional[float]] = mapped_column(
        Numeric(6, 2), nullable=True, comment="Plant height in centimeters"
    )

    canopy_cover_percent: Mapped[Optional[float]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
        comment="Canopy cover percentage (0-100)",
    )

    # Health Assessment
    health_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Health score from 1 (poor) to 10 (excellent)",
    )

    # Additional Information
    notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Observation notes and details"
    )

    # Photo Documentation
    photos: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Array of photo URLs or metadata in JSON format",
    )

    # Relationships
    planting: Mapped["Planting"] = relationship(
        "Planting", back_populates="phenology_observations"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "health_score >= 1 AND health_score <= 10",
            name="check_health_score_range",
        ),
        CheckConstraint(
            "canopy_cover_percent >= 0 AND canopy_cover_percent <= 100",
            name="check_canopy_cover_range",
        ),
        Index(
            "ix_phenology_planting_observation_date",
            "planting_id",
            "observation_date",
        ),
    )

    def __repr__(self):
        return f"<PhenologyObservation(id={self.id}, date={self.observation_date}, stage='{self.growth_stage}', health={self.health_score})>"
