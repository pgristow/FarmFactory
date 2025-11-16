"""
Base model and mixins for all database models.
Uses SQLAlchemy 2.0 declarative base with UUID primary keys and timestamps.
"""
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at timestamp columns.

    Automatically sets created_at on insert and updated_at on update.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the record was created",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when the record was last updated",
    )


class UUIDMixin:
    """
    Mixin that adds a UUID primary key.

    Uses PostgreSQL's gen_random_uuid() function for server-side generation.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        comment="Unique identifier (UUID v4)",
    )
