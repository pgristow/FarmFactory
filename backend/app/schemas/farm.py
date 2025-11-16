"""
Pydantic schemas for Farm entities
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class FarmBase(BaseModel):
    """Base schema for Farm"""
    name: str = Field(..., min_length=1, max_length=255, description="Farm name")
    address: Optional[str] = Field(None, description="Farm address")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude coordinate")
    total_area_hectares: Optional[Decimal] = Field(None, ge=0, description="Total farm area in hectares")
    timezone: Optional[str] = Field(default="UTC", description="Farm timezone")

    @field_validator('total_area_hectares', mode='before')
    @classmethod
    def validate_area(cls, v):
        """Validate and convert area to Decimal"""
        if v is not None:
            return Decimal(str(v))
        return v

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "name": "Green Valley Farm",
                "address": "123 Farm Road, Rural County, State 12345",
                "latitude": 34.0522,
                "longitude": -118.2437,
                "total_area_hectares": 50.5,
                "timezone": "America/Los_Angeles"
            }
        }


class FarmCreate(FarmBase):
    """Schema for creating a new farm"""
    pass


class FarmUpdate(BaseModel):
    """Schema for updating an existing farm"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    total_area_hectares: Optional[Decimal] = Field(None, ge=0)
    timezone: Optional[str] = None

    @field_validator('total_area_hectares', mode='before')
    @classmethod
    def validate_area(cls, v):
        """Validate and convert area to Decimal"""
        if v is not None:
            return Decimal(str(v))
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Farm Name",
                "total_area_hectares": 55.0
            }
        }


class FarmInDB(FarmBase):
    """Schema for Farm stored in database"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FarmResponse(BaseModel):
    """Schema for Farm API response"""
    success: bool = True
    data: FarmInDB

    class Config:
        from_attributes = True


class FarmListItem(BaseModel):
    """Schema for Farm in list responses"""
    id: UUID
    name: str
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    total_area_hectares: Optional[Decimal]
    timezone: str
    created_at: datetime
    plot_count: int = Field(default=0, description="Number of plots in this farm")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Green Valley Farm",
                "address": "123 Farm Road",
                "latitude": 34.0522,
                "longitude": -118.2437,
                "total_area_hectares": 50.5,
                "timezone": "America/Los_Angeles",
                "created_at": "2024-01-15T10:30:00Z",
                "plot_count": 5
            }
        }
