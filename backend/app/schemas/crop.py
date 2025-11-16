"""
Pydantic schemas for Crop and Planting entities
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal


class CropBase(BaseModel):
    """Base schema for Crop"""
    name: str = Field(..., min_length=1, max_length=255, description="Crop name")
    scientific_name: Optional[str] = Field(None, max_length=255, description="Scientific name")
    variety: Optional[str] = Field(None, max_length=255, description="Crop variety")
    optimal_temp_min_celsius: Optional[Decimal] = Field(None, description="Minimum optimal temperature")
    optimal_temp_max_celsius: Optional[Decimal] = Field(None, description="Maximum optimal temperature")
    optimal_ph_min: Optional[Decimal] = Field(None, ge=0, le=14, description="Minimum optimal pH")
    optimal_ph_max: Optional[Decimal] = Field(None, ge=0, le=14, description="Maximum optimal pH")
    days_to_maturity: Optional[int] = Field(None, ge=0, description="Days to maturity")

    @field_validator('optimal_temp_min_celsius', 'optimal_temp_max_celsius', 'optimal_ph_min', 'optimal_ph_max', mode='before')
    @classmethod
    def validate_decimal(cls, v):
        """Validate and convert to Decimal"""
        if v is not None:
            return Decimal(str(v))
        return v

    class Config:
        from_attributes = True


class CropCreate(CropBase):
    """Schema for creating a new crop"""
    pass


class CropUpdate(BaseModel):
    """Schema for updating a crop"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    scientific_name: Optional[str] = Field(None, max_length=255)
    variety: Optional[str] = Field(None, max_length=255)
    optimal_temp_min_celsius: Optional[Decimal] = None
    optimal_temp_max_celsius: Optional[Decimal] = None
    optimal_ph_min: Optional[Decimal] = Field(None, ge=0, le=14)
    optimal_ph_max: Optional[Decimal] = Field(None, ge=0, le=14)
    days_to_maturity: Optional[int] = Field(None, ge=0)


class CropInDB(CropBase):
    """Schema for Crop stored in database"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Planting schemas
class PlantingBase(BaseModel):
    """Base schema for Planting"""
    plot_id: UUID = Field(..., description="ID of the plot")
    crop_id: UUID = Field(..., description="ID of the crop")
    planting_date: date = Field(..., description="Date of planting")
    expected_harvest_date: Optional[date] = Field(None, description="Expected harvest date")
    actual_harvest_date: Optional[date] = Field(None, description="Actual harvest date")
    plant_population: Optional[int] = Field(None, ge=0, description="Number of plants")
    row_spacing_cm: Optional[Decimal] = Field(None, ge=0, description="Row spacing in cm")
    plant_spacing_cm: Optional[Decimal] = Field(None, ge=0, description="Plant spacing in cm")
    status: str = Field(default="planted", description="Status: planted, growing, harvested, failed")

    @field_validator('row_spacing_cm', 'plant_spacing_cm', mode='before')
    @classmethod
    def validate_decimal(cls, v):
        """Validate and convert to Decimal"""
        if v is not None:
            return Decimal(str(v))
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        """Validate status value"""
        allowed_statuses = ["planted", "growing", "harvested", "failed"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v

    class Config:
        from_attributes = True


class PlantingCreate(PlantingBase):
    """Schema for creating a new planting"""
    pass


class PlantingUpdate(BaseModel):
    """Schema for updating a planting"""
    expected_harvest_date: Optional[date] = None
    actual_harvest_date: Optional[date] = None
    plant_population: Optional[int] = Field(None, ge=0)
    row_spacing_cm: Optional[Decimal] = Field(None, ge=0)
    plant_spacing_cm: Optional[Decimal] = Field(None, ge=0)
    status: Optional[str] = None

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        """Validate status value"""
        if v is not None:
            allowed_statuses = ["planted", "growing", "harvested", "failed"]
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v


class PlantingInDB(PlantingBase):
    """Schema for Planting stored in database"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class PlantingWithDetails(PlantingInDB):
    """Schema for Planting with crop and plot details"""
    crop_name: str
    plot_name: str

    class Config:
        from_attributes = True
