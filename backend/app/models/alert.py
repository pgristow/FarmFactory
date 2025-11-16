"""
Alert and alert threshold models for monitoring and notifications.
"""
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Numeric, ForeignKey, Boolean, Text, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
import uuid

from app.models.base import Base, TimestampMixin, UUIDMixin


class AlertThreshold(Base, UUIDMixin, TimestampMixin):
    """
    Alert threshold configuration.

    Defines thresholds for various parameters that trigger alerts
    when measurements fall outside acceptable ranges.
    """

    __tablename__ = "alert_thresholds"

    # Foreign Keys (nullable for global thresholds)
    plot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plots.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Reference to the plot (null for global thresholds)",
    )

    # Threshold Configuration
    parameter: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Parameter to monitor (soil_moisture, ph, ec, temperature, etc.)",
    )

    min_value: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 3), nullable=True, comment="Minimum acceptable value"
    )

    max_value: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 3), nullable=True, comment="Maximum acceptable value"
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="warning",
        comment="Alert severity (info, warning, critical)",
    )

    # Status
    active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, comment="Whether this threshold is active"
    )

    # Relationships
    plot: Mapped[Optional["Plot"]] = relationship(
        "Plot", back_populates="alert_thresholds"
    )

    alerts: Mapped[list["Alert"]] = relationship(
        "Alert", back_populates="alert_threshold", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("ix_alert_thresholds_plot_parameter", "plot_id", "parameter"),
        Index("ix_alert_thresholds_active", "active"),
        CheckConstraint(
            "severity IN ('info', 'warning', 'critical')",
            name="check_severity_values",
        ),
    )

    def __repr__(self):
        return f"<AlertThreshold(id={self.id}, parameter='{self.parameter}', severity='{self.severity}')>"


class Alert(Base, UUIDMixin):
    """
    Alert history tracking triggered alerts.

    Records when thresholds are exceeded and tracks acknowledgment
    and resolution status.
    """

    __tablename__ = "alerts"

    # Foreign Keys
    plot_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plots.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Reference to the plot",
    )

    alert_threshold_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("alert_thresholds.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Reference to the threshold configuration",
    )

    # Alert Information
    triggered_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default="NOW()",
        index=True,
        comment="When the alert was triggered",
    )

    parameter: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Parameter that triggered the alert"
    )

    current_value: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 3), nullable=True, comment="Current value that triggered the alert"
    )

    threshold_min: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 3), nullable=True, comment="Minimum threshold value at time of alert"
    )

    threshold_max: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 3), nullable=True, comment="Maximum threshold value at time of alert"
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Alert severity (info, warning, critical)",
    )

    message: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Human-readable alert message"
    )

    # Status Tracking
    acknowledged: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Whether alert has been acknowledged"
    )

    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, comment="When the alert was acknowledged"
    )

    resolved: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="Whether the alert has been resolved"
    )

    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, comment="When the alert was resolved"
    )

    # Relationships
    plot: Mapped[Optional["Plot"]] = relationship("Plot", back_populates="alerts")
    alert_threshold: Mapped[Optional["AlertThreshold"]] = relationship(
        "AlertThreshold", back_populates="alerts"
    )

    # Indexes
    __table_args__ = (
        Index("ix_alerts_plot_triggered_at", "plot_id", "triggered_at"),
        Index("ix_alerts_severity", "severity"),
        Index("ix_alerts_acknowledged", "acknowledged"),
        Index("ix_alerts_resolved", "resolved"),
        Index("ix_alerts_active", "acknowledged", "resolved"),
        CheckConstraint(
            "severity IN ('info', 'warning', 'critical')",
            name="check_alert_severity_values",
        ),
    )

    def __repr__(self):
        return f"<Alert(id={self.id}, parameter='{self.parameter}', severity='{self.severity}', triggered_at={self.triggered_at})>"
