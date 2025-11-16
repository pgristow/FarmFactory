"""
Farm model with PostGIS spatial support.
Represents a farm location with geographic coordinates.
"""
from typing import Optional, List
from sqlalchemy import String, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geography

from app.models.base import Base, TimestampMixin, UUIDMixin


class Farm(Base, UUIDMixin, TimestampMixin):
    """
    Farm entity representing a farm location.

    A farm can contain multiple plots/fields and has geographic coordinates
    for mapping and spatial analysis.
    """

    __tablename__ = "farms"

    # Basic Information
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="Farm name"
    )

    address: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, comment="Physical address of the farm"
    )

    # Geographic Information (PostGIS)
    # GEOGRAPHY type uses lat/lon in WGS84 (SRID 4326)
    # Stores as POINT(longitude latitude)
    location: Mapped[Optional[Geography]] = mapped_column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=True,
        comment="Geographic coordinates (lat/lon) of farm center",
    )

    # Farm Metrics
    total_area_hectares: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="Total farm area in hectares"
    )

    timezone: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default="UTC",
        comment="Timezone for the farm (e.g., 'America/Los_Angeles')",
    )

    # Relationships
    plots: Mapped[List["Plot"]] = relationship(
        "Plot", back_populates="farm", cascade="all, delete-orphan"
    )

    # Indexes for performance
    __table_args__ = (
        Index("ix_farms_location", "location", postgresql_using="gist"),
    )

    def __repr__(self):
        return f"<Farm(id={self.id}, name='{self.name}', area={self.total_area_hectares}ha)>"
