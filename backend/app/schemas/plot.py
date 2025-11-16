"""
Pydantic schemas for Plot entities
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class PlotBase(BaseModel):
    """Base schema for Plot"""
    farm_id: UUID = Field(..., description="ID of the farm this plot belongs to")
    name: str = Field(..., min_length=1, max_length=255, description="Plot name")
    plot_number: Optional[str] = Field(None, max_length=50, description="Plot number/identifier")
    area_hectares: Optional[Decimal] = Field(None, ge=0, description="Plot area in hectares")
    elevation_meters: Optional[Decimal] = Field(None, description="Elevation in meters")
    slope_degrees: Optional[Decimal] = Field(None, ge=0, le=90, description="Slope in degrees")

    @field_validator('area_hectares', 'elevation_meters', 'slope_degrees', mode='before')
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
                "farm_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "North Field",
                "plot_number": "NF-01",
                "area_hectares": 2.5,
                "elevation_meters": 150.0,
                "slope_degrees": 5.2
            }
        }


class PlotCreate(PlotBase):
    """Schema for creating a new plot"""
    pass


class PlotUpdate(BaseModel):
    """Schema for updating an existing plot"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    plot_number: Optional[str] = Field(None, max_length=50)
    area_hectares: Optional[Decimal] = Field(None, ge=0)
    elevation_meters: Optional[Decimal] = None
    slope_degrees: Optional[Decimal] = Field(None, ge=0, le=90)

    @field_validator('area_hectares', 'elevation_meters', 'slope_degrees', mode='before')
    @classmethod
    def validate_decimal(cls, v):
        """Validate and convert to Decimal"""
        if v is not None:
            return Decimal(str(v))
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Plot Name",
                "area_hectares": 3.0
            }
        }


class PlotInDB(PlotBase):
    """Schema for Plot stored in database"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlotResponse(BaseModel):
    """Schema for Plot API response"""
    success: bool = True
    data: PlotInDB

    class Config:
        from_attributes = True


class PlotListItem(BaseModel):
    """Schema for Plot in list responses"""
    id: UUID
    farm_id: UUID
    name: str
    plot_number: Optional[str]
    area_hectares: Optional[Decimal]
    elevation_meters: Optional[Decimal]
    slope_degrees: Optional[Decimal]
    created_at: datetime
    planting_count: int = Field(default=0, description="Number of active plantings")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "223e4567-e89b-12d3-a456-426614174001",
                "farm_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "North Field",
                "plot_number": "NF-01",
                "area_hectares": 2.5,
                "elevation_meters": 150.0,
                "slope_degrees": 5.2,
                "created_at": "2024-01-15T10:30:00Z",
                "planting_count": 2
            }
        }


class PlotWithDetails(PlotInDB):
    """Schema for Plot with additional details"""
    farm_name: str = Field(..., description="Name of the farm")
    soil_type: Optional[str] = Field(None, description="Soil type if available")
    current_crop: Optional[str] = Field(None, description="Currently planted crop")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "223e4567-e89b-12d3-a456-426614174001",
                "farm_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "North Field",
                "plot_number": "NF-01",
                "area_hectares": 2.5,
                "elevation_meters": 150.0,
                "slope_degrees": 5.2,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "farm_name": "Green Valley Farm",
                "soil_type": "Loamy Clay",
                "current_crop": "Tomatoes"
            }
        }
