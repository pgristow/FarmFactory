"""
Import job models for tracking data import operations.

Includes models for import jobs, errors, and templates.
"""
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Text, Index, Enum as SQLEnum, CheckConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID
import uuid
import enum

from app.models.base import Base, TimestampMixin, UUIDMixin


class ImportStatus(str, enum.Enum):
    """Status of an import job"""
    PENDING = "pending"
    UPLOADED = "uploaded"
    PARSING = "parsing"
    MAPPING = "mapping"
    VALIDATING = "validating"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    FAILED_VALIDATION = "failed_validation"
    CANCELLED = "cancelled"


class DataType(str, enum.Enum):
    """Type of data being imported"""
    FARMS_PLOTS = "farms_plots"
    IRRIGATION = "irrigation"
    NUTRIENTS = "nutrients"
    PHENOLOGY = "phenology"
    FINANCIAL = "financial"


class ErrorType(str, enum.Enum):
    """Types of import errors"""
    VALIDATION_ERROR = "validation_error"
    DATA_TYPE_ERROR = "data_type_error"
    RANGE_ERROR = "range_error"
    REQUIRED_FIELD_ERROR = "required_field_error"
    DUPLICATE_ERROR = "duplicate_error"
    REFERENCE_ERROR = "reference_error"
    PARSE_ERROR = "parse_error"
    CONSTRAINT_ERROR = "constraint_error"


class ImportJob(Base, UUIDMixin, TimestampMixin):
    """
    Import job tracking table.

    Tracks the lifecycle of a data import from upload to completion.
    """

    __tablename__ = "import_jobs"

    # User and file information
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,  # For now, nullable until auth is implemented
        comment="User who initiated the import"
    )

    file_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Original filename of uploaded file"
    )

    file_size: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="File size in bytes"
    )

    file_path: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        comment="Path to stored file"
    )

    file_type: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        comment="File type (csv, xlsx, xls)"
    )

    data_type: Mapped[DataType] = mapped_column(
        SQLEnum(DataType, name="data_type_enum", create_type=True),
        nullable=False,
        index=True,
        comment="Type of data being imported"
    )

    # Status tracking
    status: Mapped[ImportStatus] = mapped_column(
        SQLEnum(ImportStatus, name="import_status_enum", create_type=True),
        nullable=False,
        default=ImportStatus.PENDING,
        index=True,
        comment="Current status of the import"
    )

    # Progress tracking
    total_rows: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Total number of rows in the file"
    )

    processed_rows: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of rows processed so far"
    )

    successful_rows: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of rows successfully imported"
    )

    failed_rows: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of rows that failed validation/import"
    )

    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When processing started"
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When processing completed"
    )

    # Metadata and settings
    metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Additional metadata (file encoding, delimiter, etc.)"
    )

    column_mapping: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Column name mapping from source to target"
    )

    error_summary: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Summary of errors by type"
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="General error message if import failed"
    )

    # Relationships
    errors: Mapped[list["ImportError"]] = relationship(
        "ImportError",
        back_populates="import_job",
        cascade="all, delete-orphan"
    )

    # Indexes and constraints
    __table_args__ = (
        Index("ix_import_jobs_user_id", "user_id"),
        Index("ix_import_jobs_status", "status"),
        Index("ix_import_jobs_data_type", "data_type"),
        Index("ix_import_jobs_created_at", "created_at"),
        Index("ix_import_jobs_status_created_at", "status", "created_at"),
        Index("ix_import_jobs_data_type_status", "data_type", "status"),
        Index("ix_import_jobs_user_id_created_at", "user_id", "created_at"),
        CheckConstraint(
            "processed_rows >= 0",
            name="check_processed_rows_positive"
        ),
        CheckConstraint(
            "successful_rows >= 0",
            name="check_successful_rows_positive"
        ),
        CheckConstraint(
            "failed_rows >= 0",
            name="check_failed_rows_positive"
        ),
        CheckConstraint(
            "processed_rows = successful_rows + failed_rows",
            name="check_row_counts_consistent"
        ),
        CheckConstraint(
            "file_size >= 0 OR file_size IS NULL",
            name="check_file_size_positive"
        ),
        CheckConstraint(
            "total_rows >= 0 OR total_rows IS NULL",
            name="check_total_rows_positive"
        ),
    )

    def __repr__(self):
        return (
            f"<ImportJob(id={self.id}, file='{self.file_name}', "
            f"type={self.data_type.value}, status={self.status.value}, "
            f"rows={self.processed_rows}/{self.total_rows})>"
        )

    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage"""
        if not self.total_rows or self.total_rows == 0:
            return 0.0
        return round((self.processed_rows / self.total_rows) * 100, 2)

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if not self.processed_rows or self.processed_rows == 0:
            return 0.0
        return round((self.successful_rows / self.processed_rows) * 100, 2)


class ImportError(Base, UUIDMixin, TimestampMixin):
    """
    Import error tracking table.

    Stores row-level errors that occurred during import validation or processing.
    """

    __tablename__ = "import_errors"

    # Foreign key to import job
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("import_jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Import job this error belongs to"
    )

    # Error location
    row_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Row number in the source file (1-indexed)"
    )

    column_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Column where error occurred"
    )

    # Error details
    error_type: Mapped[ErrorType] = mapped_column(
        SQLEnum(ErrorType, name="error_type_enum", create_type=True),
        nullable=False,
        index=True,
        comment="Type of error"
    )

    error_message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Human-readable error message"
    )

    invalid_value: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="The invalid value that caused the error"
    )

    suggested_value: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Suggested correction for the error"
    )

    # Additional context
    row_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Full row data for context"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        nullable=False,
        comment="Timestamp when error was recorded"
    )

    # Relationships
    import_job: Mapped["ImportJob"] = relationship(
        "ImportJob",
        back_populates="errors"
    )

    # Indexes and constraints
    __table_args__ = (
        Index("ix_import_errors_job_id", "job_id"),
        Index("ix_import_errors_error_type", "error_type"),
        Index("ix_import_errors_job_id_row_number", "job_id", "row_number"),
        Index("ix_import_errors_job_id_error_type", "job_id", "error_type"),
        Index("ix_import_errors_error_type_created_at", "error_type", "created_at"),
        CheckConstraint(
            "row_number > 0",
            name="check_row_number_positive"
        ),
    )

    def __repr__(self):
        return (
            f"<ImportError(id={self.id}, job_id={self.job_id}, "
            f"row={self.row_number}, type={self.error_type.value}, "
            f"column='{self.column_name}')>"
        )


class ImportTemplate(Base, UUIDMixin, TimestampMixin):
    """
    Import template table.

    Stores reusable column mapping templates for different data types.
    """

    __tablename__ = "import_templates"

    # Template information
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Template name"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Template description"
    )

    data_type: Mapped[DataType] = mapped_column(
        SQLEnum(DataType, name="data_type_enum", create_type=False),
        nullable=False,
        index=True,
        comment="Type of data this template is for"
    )

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="User who created this template (null for system templates)"
    )

    # Column mapping configuration
    column_mappings: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        comment="Column name mapping from source to target columns"
    )

    # Template settings
    is_default: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
        comment="Whether this is a default template"
    )

    is_active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
        comment="Whether this template is active/available"
    )

    # Usage tracking
    use_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of times this template has been used"
    )

    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when template was last used"
    )

    # Validation rules (optional)
    validation_rules: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Custom validation rules for this template"
    )

    # Indexes and constraints
    __table_args__ = (
        Index("ix_import_templates_data_type", "data_type"),
        Index("ix_import_templates_user_id", "user_id"),
        Index("ix_import_templates_is_default", "is_default"),
        Index("ix_import_templates_data_type_active", "data_type", "is_active"),
        Index("ix_import_templates_user_id_data_type", "user_id", "data_type"),
        Index("ix_import_templates_name_data_type", "name", "data_type"),
        CheckConstraint(
            "use_count >= 0",
            name="check_use_count_positive"
        ),
    )

    def __repr__(self):
        return (
            f"<ImportTemplate(id={self.id}, name='{self.name}', "
            f"type={self.data_type.value}, default={self.is_default}, "
            f"uses={self.use_count})>"
        )
