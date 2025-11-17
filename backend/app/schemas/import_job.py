"""
Pydantic schemas for import job entities.

Provides validation and serialization for import API endpoints.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from enum import Enum


class ImportStatus(str, Enum):
    """Status of an import job"""
    UPLOADED = "uploaded"
    PARSING = "parsing"
    MAPPING = "mapping"
    VALIDATING = "validating"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    FAILED_VALIDATION = "failed_validation"
    CANCELLED = "cancelled"


class DataType(str, Enum):
    """Type of data being imported"""
    FARMS_PLOTS = "farms_plots"
    IRRIGATION = "irrigation"
    NUTRIENTS = "nutrients"
    PHENOLOGY = "phenology"
    FINANCIAL = "financial"


# ============================================================================
# Import Job Schemas
# ============================================================================

class ImportJobCreate(BaseModel):
    """Schema for creating a new import job"""
    filename: str = Field(..., min_length=1, max_length=500, description="Original filename")
    file_path: str = Field(..., description="Path to stored file")
    file_type: str = Field(..., pattern="^(csv|xlsx|xls)$", description="File type")
    data_type: DataType = Field(..., description="Type of data being imported")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "filename": "irrigation_data.csv",
                "file_path": "/uploads/2024/01/abc123.csv",
                "file_type": "csv",
                "data_type": "irrigation",
                "metadata": {
                    "file_size": 1024000,
                    "encoding": "utf-8"
                }
            }
        }


class ImportJobUpdate(BaseModel):
    """Schema for updating an import job"""
    status: Optional[ImportStatus] = None
    total_rows: Optional[int] = Field(None, ge=0)
    processed_rows: Optional[int] = Field(None, ge=0)
    error_count: Optional[int] = Field(None, ge=0)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    column_mapping: Optional[Dict[str, str]] = None
    validation_summary: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "processing",
                "processed_rows": 500,
                "error_count": 5
            }
        }


class ImportJobInDB(BaseModel):
    """Schema for import job stored in database"""
    id: UUID
    user_id: Optional[UUID]
    filename: str
    file_path: str
    file_type: str
    data_type: DataType
    status: ImportStatus
    total_rows: Optional[int]
    processed_rows: int
    error_count: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    metadata: Optional[Dict[str, Any]]
    column_mapping: Optional[Dict[str, str]]
    validation_summary: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ImportJobResponse(BaseModel):
    """Schema for import job API response"""
    success: bool = True
    data: ImportJobInDB

    class Config:
        from_attributes = True


class ImportJobListItem(BaseModel):
    """Schema for import job in list responses"""
    id: UUID
    filename: str
    file_type: str
    data_type: DataType
    status: ImportStatus
    total_rows: Optional[int]
    processed_rows: int
    error_count: int
    created_at: datetime
    completed_at: Optional[datetime]
    progress_percent: Optional[float] = Field(None, description="Progress percentage (0-100)")

    @field_validator('progress_percent', mode='before')
    @classmethod
    def calculate_progress(cls, v, info):
        """Calculate progress percentage"""
        if 'total_rows' in info.data and 'processed_rows' in info.data:
            total = info.data.get('total_rows')
            processed = info.data.get('processed_rows', 0)
            if total and total > 0:
                return round((processed / total) * 100, 2)
        return None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "filename": "irrigation_data.csv",
                "file_type": "csv",
                "data_type": "irrigation",
                "status": "completed",
                "total_rows": 1000,
                "processed_rows": 1000,
                "error_count": 5,
                "progress_percent": 100.0,
                "created_at": "2024-01-15T10:30:00Z",
                "completed_at": "2024-01-15T10:32:00Z"
            }
        }


# ============================================================================
# Import Error Schemas
# ============================================================================

class ImportErrorResponse(BaseModel):
    """Schema for import error"""
    id: UUID
    import_job_id: UUID
    row_number: int
    column_name: Optional[str]
    error_type: str
    error_message: str
    row_data: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "import_job_id": "123e4567-e89b-12d3-a456-426614174000",
                "row_number": 42,
                "column_name": "irrigation_date",
                "error_type": "validation",
                "error_message": "Invalid date format. Expected YYYY-MM-DD",
                "row_data": {
                    "farm_name": "Green Valley Farm",
                    "irrigation_date": "01/15/2024"
                },
                "created_at": "2024-01-15T10:31:00Z"
            }
        }


# ============================================================================
# Import Template Schemas
# ============================================================================

class ImportTemplateCreate(BaseModel):
    """Schema for creating an import template"""
    name: str = Field(..., min_length=1, max_length=255)
    data_type: DataType
    column_mapping: Dict[str, str] = Field(..., description="Mapping from source to target columns")
    is_default: bool = Field(False, description="Whether this is the default template")
    description: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Standard Irrigation Import",
                "data_type": "irrigation",
                "column_mapping": {
                    "Farm Name": "farm_name",
                    "Date": "irrigation_date",
                    "Amount (gallons)": "amount_gallons"
                },
                "is_default": True,
                "description": "Standard template for irrigation data imports"
            }
        }


class ImportTemplateInDB(BaseModel):
    """Schema for import template stored in database"""
    id: UUID
    name: str
    data_type: DataType
    column_mapping: Dict[str, str]
    is_default: bool
    user_id: Optional[UUID]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ImportTemplateResponse(BaseModel):
    """Schema for import template API response"""
    success: bool = True
    data: ImportTemplateInDB

    class Config:
        from_attributes = True


# ============================================================================
# Column Mapping Schemas
# ============================================================================

class ColumnMappingSuggestion(BaseModel):
    """Suggested column mapping with confidence score"""
    source_column: str
    target_column: Optional[str]
    confidence: float = Field(..., ge=0, le=100, description="Confidence score (0-100)")
    alternatives: List[Dict[str, Any]] = Field(default_factory=list, description="Alternative mappings")

    class Config:
        json_schema_extra = {
            "example": {
                "source_column": "Farm Name",
                "target_column": "farm_name",
                "confidence": 95.5,
                "alternatives": [
                    {"target_column": "farm_id", "confidence": 45.0}
                ]
            }
        }


class ColumnMappingRequest(BaseModel):
    """Request for column mapping"""
    job_id: UUID
    manual_mappings: Optional[Dict[str, str]] = Field(None, description="Manual column mappings to override auto-detection")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "manual_mappings": {
                    "Farm": "farm_name",
                    "Date": "irrigation_date"
                }
            }
        }


class ColumnMappingResponse(BaseModel):
    """Response with column mapping suggestions"""
    success: bool = True
    job_id: UUID
    mappings: List[ColumnMappingSuggestion]
    unmapped_columns: List[str] = Field(default_factory=list, description="Source columns that couldn't be mapped")
    required_columns_missing: List[str] = Field(default_factory=list, description="Required target columns not mapped")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "mappings": [
                    {
                        "source_column": "Farm Name",
                        "target_column": "farm_name",
                        "confidence": 95.5,
                        "alternatives": []
                    }
                ],
                "unmapped_columns": ["Notes", "Comments"],
                "required_columns_missing": []
            }
        }


# ============================================================================
# Validation Schemas
# ============================================================================

class ValidationError(BaseModel):
    """Individual validation error"""
    row_number: int
    column_name: Optional[str]
    error_type: str
    error_message: str
    value: Optional[Any]

    class Config:
        json_schema_extra = {
            "example": {
                "row_number": 42,
                "column_name": "irrigation_date",
                "error_type": "invalid_date",
                "error_message": "Date is in the future",
                "value": "2025-12-31"
            }
        }


class ValidationResultResponse(BaseModel):
    """Response with validation results"""
    success: bool = True
    job_id: UUID
    is_valid: bool
    total_rows: int
    valid_rows: int
    error_count: int
    errors: List[ValidationError]
    error_summary: Dict[str, int] = Field(default_factory=dict, description="Count of errors by type")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "is_valid": False,
                "total_rows": 1000,
                "valid_rows": 995,
                "error_count": 5,
                "errors": [
                    {
                        "row_number": 42,
                        "column_name": "irrigation_date",
                        "error_type": "invalid_date",
                        "error_message": "Date is in the future",
                        "value": "2025-12-31"
                    }
                ],
                "error_summary": {
                    "invalid_date": 3,
                    "missing_required": 2
                }
            }
        }


# ============================================================================
# File Upload Schemas
# ============================================================================

class FileUploadResponse(BaseModel):
    """Response after file upload"""
    success: bool = True
    job_id: UUID
    filename: str
    file_size: int
    file_type: str
    message: str = "File uploaded successfully"

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "filename": "irrigation_data.csv",
                "file_size": 1024000,
                "file_type": "csv",
                "message": "File uploaded successfully"
            }
        }


class DataPreviewResponse(BaseModel):
    """Response with data preview"""
    success: bool = True
    job_id: UUID
    columns: List[str]
    preview_data: List[Dict[str, Any]]
    total_rows: int
    data_types: Dict[str, str] = Field(default_factory=dict, description="Detected data types for each column")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "columns": ["Farm Name", "Date", "Amount"],
                "preview_data": [
                    {"Farm Name": "Green Valley Farm", "Date": "2024-01-15", "Amount": "1000"}
                ],
                "total_rows": 1000,
                "data_types": {
                    "Farm Name": "string",
                    "Date": "date",
                    "Amount": "numeric"
                }
            }
        }
