"""
Pydantic schemas for Phenology Observation entities
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal


class PhenologyObservationBase(BaseModel):
    """Base schema for Phenology Observation"""
    planting_id: UUID = Field(..., description="ID of the planting")
    observation_date: date = Field(..., description="Date of observation")
    growth_stage: Optional[str] = Field(None, max_length=100, description="Growth stage")
    bbch_code: Optional[int] = Field(None, ge=0, le=99, description="BBCH phenological scale code")
    height_cm: Optional[Decimal] = Field(None, ge=0, description="Plant height in cm")
    canopy_cover_percent: Optional[Decimal] = Field(None, ge=0, le=100, description="Canopy cover (0-100)")
    health_score: Optional[int] = Field(None, ge=1, le=10, description="Health score (1-10)")
    notes: Optional[str] = Field(None, description="Observation notes")
    photos: Optional[dict] = Field(None, description="Photo URLs and metadata")

    @field_validator('height_cm', 'canopy_cover_percent', mode='before')
    @classmethod
    def validate_decimal(cls, v):
        """Validate and convert to Decimal"""
        if v is not None:
            return Decimal(str(v))
        return v

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "planting_id": "323e4567-e89b-12d3-a456-426614174002",
                "observation_date": "2024-01-15",
                "growth_stage": "vegetative",
                "bbch_code": 15,
                "height_cm": 25.5,
                "canopy_cover_percent": 30.0,
                "health_score": 8,
                "notes": "Strong growth, healthy leaves",
                "photos": {"urls": ["photo1.jpg", "photo2.jpg"]}
            }
        }


class PhenologyObservationCreate(PhenologyObservationBase):
    """Schema for creating a new phenology observation"""
    pass


class PhenologyObservationUpdate(BaseModel):
    """Schema for updating a phenology observation"""
    growth_stage: Optional[str] = Field(None, max_length=100)
    bbch_code: Optional[int] = Field(None, ge=0, le=99)
    height_cm: Optional[Decimal] = Field(None, ge=0)
    canopy_cover_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    health_score: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None
    photos: Optional[dict] = None


class PhenologyObservationInDB(PhenologyObservationBase):
    """Schema for Phenology Observation stored in database"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class PhenologyTimeline(BaseModel):
    """Schema for growth timeline of a planting"""
    planting_id: UUID
    planting_date: date
    observations: list[PhenologyObservationInDB]
    days_since_planting: int
    current_growth_stage: Optional[str] = None
    latest_health_score: Optional[int] = None

    class Config:
        from_attributes = True
