"""
Import orchestration service.

Coordinates the entire import workflow from file parsing to validation.
"""
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID
import logging

from app.models.import_job import ImportJob, ImportError, ImportStatus, DataType
from app.services.csv_parser import CSVParser, CSVParseError
from app.services.excel_parser import ExcelParser, ExcelParseError
from app.services.column_mapper import ColumnMapper
from app.services.data_validator import DataValidator

logger = logging.getLogger(__name__)


class ImportServiceError(Exception):
    """Exception raised when import service encounters an error"""
    pass


class ImportService:
    """
    Orchestrates the entire import workflow.

    Workflow:
    1. Parse file (CSV or Excel)
    2. Auto-map columns
    3. Validate data
    4. Save validation errors
    5. Update import job status
    """

    def __init__(self, db: Session):
        """Initialize import service with database session"""
        self.db = db

    def get_import_job(self, job_id: UUID) -> Optional[ImportJob]:
        """Get import job by ID"""
        return self.db.query(ImportJob).filter(ImportJob.id == job_id).first()

    def create_import_job(
        self,
        filename: str,
        file_path: str,
        file_type: str,
        data_type: str,
        file_size: int,
        user_id: Optional[UUID] = None
    ) -> ImportJob:
        """
        Create a new import job record.

        Args:
            filename: Original filename
            file_path: Path to stored file
            file_type: File type (csv, xlsx, xls)
            data_type: Type of data being imported
            file_size: File size in bytes
            user_id: ID of user who initiated import

        Returns:
            Created ImportJob instance
        """
        job = ImportJob(
            user_id=user_id,
            file_name=filename,
            file_path=file_path,
            file_type=file_type,
            data_type=DataType(data_type),
            file_size=file_size,
            status=ImportStatus.UPLOADED,
            processed_rows=0,
            successful_rows=0,
            failed_rows=0,
        )

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        logger.info(f"Created import job {job.id} for file '{filename}'")
        return job

    def parse_file(
        self,
        job_id: UUID,
        preview_rows: int = 100
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Parse uploaded file and extract metadata.

        Args:
            job_id: Import job ID
            preview_rows: Number of rows to parse for preview

        Returns:
            Tuple of (DataFrame, metadata dict)

        Raises:
            ImportServiceError: If parsing fails
        """
        job = self.get_import_job(job_id)
        if not job:
            raise ImportServiceError(f"Import job {job_id} not found")

        # Update status
        job.status = ImportStatus.PARSING
        self.db.commit()

        try:
            file_path = job.file_path

            # Parse based on file type
            if job.file_type == 'csv':
                df, metadata = CSVParser.parse_csv(file_path)
            elif job.file_type in ['xlsx', 'xls']:
                df, metadata = ExcelParser.parse_excel(file_path)
            else:
                raise ImportServiceError(f"Unsupported file type: {job.file_type}")

            # Update job with metadata
            job.total_rows = len(df)
            job.metadata = metadata
            job.status = ImportStatus.UPLOADED  # Reset to uploaded after successful parse
            self.db.commit()

            logger.info(f"Parsed file for job {job_id}: {len(df)} rows")
            return df, metadata

        except (CSVParseError, ExcelParseError) as e:
            job.status = ImportStatus.FAILED
            job.error_message = str(e)
            self.db.commit()
            raise ImportServiceError(f"Failed to parse file: {str(e)}")

    def auto_map_columns(
        self,
        job_id: UUID,
        source_columns: List[str],
        manual_overrides: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Auto-map source columns to target schema.

        Args:
            job_id: Import job ID
            source_columns: List of column names from file
            manual_overrides: Optional manual column mappings

        Returns:
            Mapping result dictionary

        Raises:
            ImportServiceError: If mapping fails
        """
        job = self.get_import_job(job_id)
        if not job:
            raise ImportServiceError(f"Import job {job_id} not found")

        job.status = ImportStatus.MAPPING
        self.db.commit()

        try:
            # Auto-map columns
            mapping_result = ColumnMapper.auto_map_columns(
                source_columns,
                job.data_type.value
            )

            # Apply manual overrides if provided
            if manual_overrides:
                mapping_result = ColumnMapper.apply_manual_mapping(
                    mapping_result,
                    manual_overrides
                )

            # Extract simple mapping dict
            column_mapping = ColumnMapper.get_mapping_dict(mapping_result)

            # Save mapping to job
            job.column_mapping = column_mapping
            job.status = ImportStatus.UPLOADED  # Reset after mapping
            self.db.commit()

            logger.info(
                f"Mapped columns for job {job_id}: "
                f"{len(column_mapping)} columns mapped"
            )

            return mapping_result

        except Exception as e:
            job.status = ImportStatus.FAILED
            job.error_message = str(e)
            self.db.commit()
            raise ImportServiceError(f"Failed to map columns: {str(e)}")

    def validate_data(
        self,
        job_id: UUID,
        df: pd.DataFrame,
        column_mapping: Dict[str, str],
        max_errors: int = 100
    ) -> Dict[str, Any]:
        """
        Validate DataFrame data.

        Args:
            job_id: Import job ID
            df: DataFrame to validate
            column_mapping: Column name mapping
            max_errors: Maximum number of errors to collect

        Returns:
            Validation result dictionary

        Raises:
            ImportServiceError: If validation fails
        """
        job = self.get_import_job(job_id)
        if not job:
            raise ImportServiceError(f"Import job {job_id} not found")

        job.status = ImportStatus.VALIDATING
        self.db.commit()

        try:
            validator = DataValidator(self.db)
            is_valid, errors, error_summary = validator.validate_dataframe(
                df,
                job.data_type.value,
                column_mapping,
                max_errors
            )

            # Save errors to database
            if errors:
                self._save_validation_errors(job_id, errors)

            # Update job
            job.failed_rows = len(errors)
            job.error_summary = error_summary

            if is_valid:
                job.status = ImportStatus.UPLOADED  # Ready for processing
            else:
                job.status = ImportStatus.FAILED_VALIDATION

            self.db.commit()

            result = {
                'is_valid': is_valid,
                'total_rows': len(df),
                'valid_rows': len(df) - len(errors),
                'error_count': len(errors),
                'errors': [e.to_dict() for e in errors[:max_errors]],
                'error_summary': error_summary
            }

            logger.info(
                f"Validated data for job {job_id}: "
                f"{len(errors)} errors found, valid={is_valid}"
            )

            return result

        except Exception as e:
            job.status = ImportStatus.FAILED
            job.error_message = str(e)
            self.db.commit()
            raise ImportServiceError(f"Validation failed: {str(e)}")

    def _save_validation_errors(
        self,
        job_id: UUID,
        errors: List[Any]
    ):
        """Save validation errors to database"""
        # Clear existing errors
        self.db.query(ImportError).filter(
            ImportError.import_job_id == job_id
        ).delete()

        # Add new errors
        for error in errors:
            db_error = ImportError(
                import_job_id=job_id,
                row_number=error.row_number,
                column_name=error.column_name,
                error_type=error.error_type,
                error_message=error.error_message,
                row_data={'value': str(error.value)} if error.value is not None else None
            )
            self.db.add(db_error)

        self.db.commit()

    def get_validation_errors(
        self,
        job_id: UUID,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[ImportError], int]:
        """
        Get validation errors for a job.

        Args:
            job_id: Import job ID
            limit: Maximum number of errors to return
            offset: Number of errors to skip

        Returns:
            Tuple of (errors list, total count)
        """
        query = self.db.query(ImportError).filter(
            ImportError.import_job_id == job_id
        )

        total = query.count()
        errors = query.order_by(ImportError.row_number).limit(limit).offset(offset).all()

        return errors, total

    def get_import_history(
        self,
        limit: int = 20,
        offset: int = 0,
        status: Optional[str] = None,
        data_type: Optional[str] = None
    ) -> Tuple[List[ImportJob], int]:
        """
        Get import job history.

        Args:
            limit: Maximum number of jobs to return
            offset: Number of jobs to skip
            status: Optional status filter
            data_type: Optional data type filter

        Returns:
            Tuple of (jobs list, total count)
        """
        query = self.db.query(ImportJob)

        if status:
            query = query.filter(ImportJob.status == ImportStatus(status))

        if data_type:
            query = query.filter(ImportJob.data_type == DataType(data_type))

        total = query.count()
        jobs = query.order_by(ImportJob.created_at.desc()).limit(limit).offset(offset).all()

        return jobs, total

    def cancel_import(self, job_id: UUID) -> bool:
        """
        Cancel an import job.

        Args:
            job_id: Import job ID

        Returns:
            True if cancelled, False if not found or already completed
        """
        job = self.get_import_job(job_id)
        if not job:
            return False

        # Can only cancel jobs that are in progress
        if job.status in [ImportStatus.COMPLETED, ImportStatus.FAILED, ImportStatus.CANCELLED]:
            return False

        job.status = ImportStatus.CANCELLED
        self.db.commit()

        logger.info(f"Cancelled import job {job_id}")
        return True

    def delete_import(self, job_id: UUID) -> bool:
        """
        Delete an import job and its errors.

        Args:
            job_id: Import job ID

        Returns:
            True if deleted, False if not found
        """
        job = self.get_import_job(job_id)
        if not job:
            return False

        # Delete the file if it exists
        if job.file_path and Path(job.file_path).exists():
            try:
                Path(job.file_path).unlink()
            except Exception as e:
                logger.warning(f"Failed to delete file {job.file_path}: {e}")

        # Delete job (errors will be cascade deleted)
        self.db.delete(job)
        self.db.commit()

        logger.info(f"Deleted import job {job_id}")
        return True

    def get_preview_with_mapping(
        self,
        job_id: UUID,
        preview_rows: int = 10
    ) -> Dict[str, Any]:
        """
        Get data preview with auto-mapped columns.

        Args:
            job_id: Import job ID
            preview_rows: Number of rows to include in preview

        Returns:
            Dictionary with preview data and mapping suggestions
        """
        # Parse file
        df, metadata = self.parse_file(job_id)

        # Auto-map columns
        mapping_result = self.auto_map_columns(
            job_id,
            metadata['columns']
        )

        # Get preview
        if df is not None:
            if job_id.hex[:3] == 'csv':  # Check file type
                preview_data = CSVParser.get_preview(df, preview_rows)
            else:
                preview_data = ExcelParser.get_preview(df, preview_rows)
        else:
            preview_data = []

        return {
            'preview_data': preview_data,
            'columns': metadata['columns'],
            'total_rows': metadata['total_rows'],
            'data_types': metadata['data_types'],
            'mapping': mapping_result
        }
