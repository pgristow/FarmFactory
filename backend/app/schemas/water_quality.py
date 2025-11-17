"""
Pydantic schemas for Water Quality entities
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class WaterQualityBase(BaseModel):
    """Base schema for Water Quality measurement"""
    plot_id: UUID = Field(..., description="ID of the plot")
    time: datetime = Field(..., description="Timestamp of measurement")
    source: Optional[str] = Field(None, max_length=100, description="Water source (well, municipal, reservoir, etc.)")
    ph_level: Optional[Decimal] = Field(None, ge=0, le=14, description="pH level (0-14)")
    ec_ds_per_m: Optional[Decimal] = Field(None, ge=0, description="Electrical conductivity in dS/m")
    tds_ppm: Optional[Decimal] = Field(None, ge=0, description="Total dissolved solids in ppm")
    temperature_celsius: Optional[Decimal] = Field(None, description="Water temperature in Celsius")
    dissolved_oxygen_ppm: Optional[Decimal] = Field(None, ge=0, description="Dissolved oxygen in ppm")
    turbidity_ntu: Optional[Decimal] = Field(None, ge=0, description="Turbidity in NTU")
    notes: Optional[str] = Field(None, description="Additional notes")

    @field_validator('ph_level', 'ec_ds_per_m', 'tds_ppm', 'temperature_celsius',
                     'dissolved_oxygen_ppm', 'turbidity_ntu', mode='before')
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
                "plot_id": "223e4567-e89b-12d3-a456-426614174001",
                "time": "2024-01-15T09:00:00Z",
                "source": "Well #1",
                "ph_level": 7.2,
                "ec_ds_per_m": 0.8,
                "tds_ppm": 450.0,
                "temperature_celsius": 18.5,
                "dissolved_oxygen_ppm": 8.5,
                "turbidity_ntu": 2.1,
                "notes": "Weekly water quality test"
            }
        }


class WaterQualityCreate(WaterQualityBase):
    """Schema for creating a new water quality measurement"""
    pass


class WaterQualityUpdate(BaseModel):
    """Schema for updating a water quality measurement"""
    source: Optional[str] = Field(None, max_length=100)
    ph_level: Optional[Decimal] = Field(None, ge=0, le=14)
    ec_ds_per_m: Optional[Decimal] = Field(None, ge=0)
    tds_ppm: Optional[Decimal] = Field(None, ge=0)
    temperature_celsius: Optional[Decimal] = None
    dissolved_oxygen_ppm: Optional[Decimal] = Field(None, ge=0)
    turbidity_ntu: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None


class WaterQualityInDB(WaterQualityBase):
    """Schema for Water Quality stored in database"""

    class Config:
        from_attributes = True


class WaterQualityTrends(BaseModel):
    """Schema for water quality parameter trends"""
    plot_id: UUID
    plot_name: str
    parameter: str
    period_start: datetime
    period_end: datetime
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    avg_value: Optional[Decimal] = None
    measurement_count: int

    class Config:
        from_attributes = True
