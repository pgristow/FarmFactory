"""
Import API endpoints for data import functionality.

Provides REST API for file upload, parsing, mapping, validation, and processing.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import logging
from pathlib import Path
import shutil
import uuid as uuid_lib

from app.core.deps import get_db, get_pagination_params
from app.core.config import settings
from app.schemas.import_job import (
    FileUploadResponse,
    DataPreviewResponse,
    ColumnMappingResponse,
    ColumnMappingRequest,
    ValidationResultResponse,
    ImportJobResponse,
    ImportJobListItem,
    ImportErrorResponse,
    DataType,
)
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.services.import_service import ImportService, ImportServiceError
from app.services.csv_parser import CSVParser
from app.services.excel_parser import ExcelParser
from app.tasks.import_tasks import process_import

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload file for import",
    tags=["Import"]
)
async def upload_file(
    file: UploadFile = File(...),
    data_type: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Upload a CSV or Excel file for import.

    - **file**: CSV or Excel file (max 100MB)
    - **data_type**: Type of data (farms_plots, irrigation, nutrients, phenology, financial)

    Returns file metadata and job_id for tracking.
    """
    try:
        # Validate data type
        try:
            DataType(data_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid data_type. Must be one of: {', '.join([dt.value for dt in DataType])}"
            )

        # Validate file type
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

        # Create upload directory if it doesn't exist
        upload_dir = settings.UPLOAD_DIR
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        unique_filename = f"{uuid_lib.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = file_path.stat().st_size

        # Validate file size
        if file_size > settings.MAX_UPLOAD_SIZE:
            file_path.unlink()  # Delete file
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / (1024*1024):.0f}MB"
            )

        # Validate file structure
        file_type = file_extension[1:]  # Remove dot
        if file_type == 'csv':
            is_valid, error_msg = CSVParser.validate_csv_structure(str(file_path))
        else:
            is_valid, error_msg = ExcelParser.validate_excel_structure(str(file_path))

        if not is_valid:
            file_path.unlink()  # Delete file
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file: {error_msg}"
            )

        # Create import job
        import_service = ImportService(db)
        job = import_service.create_import_job(
            filename=file.filename,
            file_path=str(file_path),
            file_type=file_type,
            data_type=data_type,
            file_size=file_size
        )

        logger.info(f"File uploaded successfully: {file.filename} -> {job.id}")

        return FileUploadResponse(
            success=True,
            job_id=job.id,
            filename=file.filename,
            file_size=file_size,
            file_type=file_type
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )


@router.post(
    "/preview",
    response_model=DataPreviewResponse,
    summary="Preview uploaded data with column mapping",
    tags=["Import"]
)
async def preview_data(
    job_id: UUID,
    preview_rows: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get preview of uploaded data with auto-detected column mappings.

    - **job_id**: Import job ID
    - **preview_rows**: Number of rows to preview (1-100)

    Returns preview data, columns, and mapping suggestions.
    """
    try:
        import_service = ImportService(db)
        job = import_service.get_import_job(job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Import job {job_id} not found"
            )

        # Parse file
        df, metadata = import_service.parse_file(job_id, preview_rows)

        # Auto-map columns
        mapping_result = import_service.auto_map_columns(
            job_id,
            metadata['columns']
        )

        # Get preview
        if job.file_type == 'csv':
            preview_data = CSVParser.get_preview(df, preview_rows)
        else:
            preview_data = ExcelParser.get_preview(df, preview_rows)

        return DataPreviewResponse(
            success=True,
            job_id=job_id,
            columns=metadata['columns'],
            preview_data=preview_data,
            total_rows=metadata['total_rows'],
            data_types=metadata['data_types']
        )

    except ImportServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error previewing data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error previewing data: {str(e)}"
        )


@router.post(
    "/map",
    response_model=ColumnMappingResponse,
    summary="Map columns with optional manual overrides",
    tags=["Import"]
)
async def map_columns(
    request: ColumnMappingRequest,
    db: Session = Depends(get_db)
):
    """
    Auto-map columns or apply manual mapping overrides.

    - **job_id**: Import job ID
    - **manual_mappings**: Optional dictionary of manual column mappings

    Returns column mappings with confidence scores.
    """
    try:
        import_service = ImportService(db)
        job = import_service.get_import_job(request.job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Import job {request.job_id} not found"
            )

        # Get metadata
        if not job.metadata or 'columns' not in job.metadata:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File has not been parsed yet. Call /preview first."
            )

        # Auto-map columns with optional manual overrides
        mapping_result = import_service.auto_map_columns(
            request.job_id,
            job.metadata['columns'],
            request.manual_mappings
        )

        # Convert to response format
        mappings = [
            {
                'source_column': m['source_column'],
                'target_column': m['target_column'],
                'confidence': m['confidence'],
                'alternatives': m.get('alternatives', [])
            }
            for m in mapping_result['mappings']
        ]

        return ColumnMappingResponse(
            success=True,
            job_id=request.job_id,
            mappings=mappings,
            unmapped_columns=mapping_result['unmapped_columns'],
            required_columns_missing=mapping_result['required_columns_missing']
        )

    except ImportServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error mapping columns: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error mapping columns: {str(e)}"
        )


@router.post(
    "/validate",
    response_model=ValidationResultResponse,
    summary="Validate import data",
    tags=["Import"]
)
async def validate_data(
    job_id: UUID,
    max_errors: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Validate imported data against schema rules.

    - **job_id**: Import job ID
    - **max_errors**: Maximum number of errors to return (1-1000)

    Returns validation results with error details.
    """
    try:
        import_service = ImportService(db)
        job = import_service.get_import_job(job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Import job {job_id} not found"
            )

        # Check if column mapping exists
        if not job.column_mapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Columns have not been mapped yet. Call /map first."
            )

        # Parse file
        df, _ = import_service.parse_file(job_id)

        # Validate data
        validation_result = import_service.validate_data(
            job_id,
            df,
            job.column_mapping,
            max_errors
        )

        return ValidationResultResponse(
            success=True,
            job_id=job_id,
            is_valid=validation_result['is_valid'],
            total_rows=validation_result['total_rows'],
            valid_rows=validation_result['valid_rows'],
            error_count=validation_result['error_count'],
            errors=validation_result['errors'],
            error_summary=validation_result['error_summary']
        )

    except ImportServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating data: {str(e)}"
        )


@router.post(
    "/process",
    response_model=SuccessResponse,
    summary="Start import processing",
    tags=["Import"]
)
async def start_import_processing(
    job_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Start asynchronous import processing with Celery.

    - **job_id**: Import job ID

    Returns success message. Use /status endpoint to track progress.
    """
    try:
        import_service = ImportService(db)
        job = import_service.get_import_job(job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Import job {job_id} not found"
            )

        # Check if job is ready for processing
        if not job.column_mapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Columns have not been mapped yet."
            )

        # Trigger Celery task
        task = process_import.delay(str(job_id))

        logger.info(f"Started import processing for job {job_id}, task {task.id}")

        return SuccessResponse(
            success=True,
            message=f"Import processing started. Task ID: {task.id}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting import processing: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting import processing: {str(e)}"
        )


@router.get(
    "/status/{job_id}",
    response_model=ImportJobResponse,
    summary="Get import job status",
    tags=["Import"]
)
async def get_import_status(
    job_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get the status and progress of an import job.

    - **job_id**: Import job ID

    Returns job status, progress, and metadata.
    """
    try:
        import_service = ImportService(db)
        job = import_service.get_import_job(job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Import job {job_id} not found"
            )

        return ImportJobResponse(
            success=True,
            data=job
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting import status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting import status: {str(e)}"
        )


@router.get(
    "/history",
    response_model=PaginatedResponse[ImportJobListItem],
    summary="Get import history",
    tags=["Import"]
)
async def get_import_history(
    pagination: dict = Depends(get_pagination_params),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    data_type: Optional[str] = Query(None, description="Filter by data type"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of import jobs.

    Query parameters:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **status_filter**: Filter by status
    - **data_type**: Filter by data type

    Returns paginated list of import jobs.
    """
    try:
        import_service = ImportService(db)
        jobs, total = import_service.get_import_history(
            limit=pagination["limit"],
            offset=pagination["skip"],
            status=status_filter,
            data_type=data_type
        )

        # Convert to list items
        job_items = []
        for job in jobs:
            progress_percent = None
            if job.total_rows and job.total_rows > 0:
                progress_percent = round((job.processed_rows / job.total_rows) * 100, 2)

            job_items.append(ImportJobListItem(
                id=job.id,
                filename=job.file_name,
                file_type=job.file_type,
                data_type=job.data_type,
                status=job.status,
                total_rows=job.total_rows,
                processed_rows=job.processed_rows,
                error_count=job.failed_rows,
                created_at=job.created_at,
                completed_at=job.completed_at,
                progress_percent=progress_percent
            ))

        from app.utils.responses import paginated_response
        return paginated_response(
            data=[item.model_dump() for item in job_items],
            total=total,
            page=pagination["page"],
            page_size=pagination["page_size"]
        )

    except Exception as e:
        logger.error(f"Error getting import history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting import history: {str(e)}"
        )


@router.get(
    "/{job_id}/errors",
    response_model=PaginatedResponse[ImportErrorResponse],
    summary="Get import errors",
    tags=["Import"]
)
async def get_import_errors(
    job_id: UUID,
    pagination: dict = Depends(get_pagination_params),
    db: Session = Depends(get_db)
):
    """
    Get validation/processing errors for an import job.

    - **job_id**: Import job ID

    Returns paginated list of errors.
    """
    try:
        import_service = ImportService(db)
        errors, total = import_service.get_validation_errors(
            job_id,
            limit=pagination["limit"],
            offset=pagination["skip"]
        )

        from app.utils.responses import paginated_response
        return paginated_response(
            data=[ImportErrorResponse.model_validate(error).model_dump() for error in errors],
            total=total,
            page=pagination["page"],
            page_size=pagination["page_size"]
        )

    except Exception as e:
        logger.error(f"Error getting import errors: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting import errors: {str(e)}"
        )


@router.delete(
    "/{job_id}",
    response_model=SuccessResponse,
    summary="Delete import job",
    tags=["Import"]
)
async def delete_import(
    job_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete an import job and its associated errors.

    - **job_id**: Import job ID

    Returns success message.
    """
    try:
        import_service = ImportService(db)
        deleted = import_service.delete_import(job_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Import job {job_id} not found"
            )

        return SuccessResponse(
            success=True,
            message=f"Import job {job_id} deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting import: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting import: {str(e)}"
        )


@router.post(
    "/{job_id}/cancel",
    response_model=SuccessResponse,
    summary="Cancel import job",
    tags=["Import"]
)
async def cancel_import(
    job_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Cancel an in-progress import job.

    - **job_id**: Import job ID

    Returns success message.
    """
    try:
        import_service = ImportService(db)
        cancelled = import_service.cancel_import(job_id)

        if not cancelled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Import job cannot be cancelled (not found or already completed)"
            )

        return SuccessResponse(
            success=True,
            message=f"Import job {job_id} cancelled successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling import: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelling import: {str(e)}"
        )
