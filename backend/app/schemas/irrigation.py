"""
Pydantic schemas for Irrigation entities
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class IrrigationEventBase(BaseModel):
    """Base schema for Irrigation Event"""
    plot_id: UUID = Field(..., description="ID of the plot")
    time: datetime = Field(..., description="Timestamp of irrigation event")
    method: str = Field(..., description="Irrigation method: drip, sprinkler, flood, manual")
    duration_minutes: Optional[int] = Field(None, ge=0, description="Duration in minutes")
    water_volume_liters: Optional[Decimal] = Field(None, ge=0, description="Water volume in liters")
    water_source: Optional[str] = Field(None, max_length=100, description="Water source")
    flow_rate_lpm: Optional[Decimal] = Field(None, ge=0, description="Flow rate in liters per minute")
    pressure_bar: Optional[Decimal] = Field(None, ge=0, description="Water pressure in bar")
    notes: Optional[str] = Field(None, description="Additional notes")

    @field_validator('water_volume_liters', 'flow_rate_lpm', 'pressure_bar', mode='before')
    @classmethod
    def validate_decimal(cls, v):
        """Validate and convert to Decimal"""
        if v is not None:
            return Decimal(str(v))
        return v

    @field_validator('method')
    @classmethod
    def validate_method(cls, v):
        """Validate irrigation method"""
        allowed_methods = ["drip", "sprinkler", "flood", "manual", "other"]
        if v.lower() not in allowed_methods:
            raise ValueError(f"Method must be one of: {', '.join(allowed_methods)}")
        return v.lower()

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "plot_id": "223e4567-e89b-12d3-a456-426614174001",
                "time": "2024-01-15T06:00:00Z",
                "method": "drip",
                "duration_minutes": 120,
                "water_volume_liters": 500.0,
                "water_source": "Well",
                "flow_rate_lpm": 4.17,
                "pressure_bar": 2.5,
                "notes": "Morning irrigation cycle"
            }
        }


class IrrigationEventCreate(IrrigationEventBase):
    """Schema for creating a new irrigation event"""
    pass


class IrrigationEventUpdate(BaseModel):
    """Schema for updating an irrigation event"""
    method: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    water_volume_liters: Optional[Decimal] = Field(None, ge=0)
    water_source: Optional[str] = Field(None, max_length=100)
    flow_rate_lpm: Optional[Decimal] = Field(None, ge=0)
    pressure_bar: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None


class IrrigationEventInDB(IrrigationEventBase):
    """Schema for Irrigation Event stored in database"""

    class Config:
        from_attributes = True


class IrrigationSummary(BaseModel):
    """Schema for irrigation summary statistics"""
    plot_id: UUID
    plot_name: str
    total_events: int = Field(..., description="Total number of irrigation events")
    total_water_liters: Decimal = Field(..., description="Total water used in liters")
    average_duration_minutes: Optional[Decimal] = Field(None, description="Average duration per event")
    most_common_method: Optional[str] = Field(None, description="Most commonly used method")
    last_irrigation: Optional[datetime] = Field(None, description="Last irrigation timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "plot_id": "223e4567-e89b-12d3-a456-426614174001",
                "plot_name": "North Field",
                "total_events": 45,
                "total_water_liters": 22500.0,
                "average_duration_minutes": 120.0,
                "most_common_method": "drip",
                "last_irrigation": "2024-01-15T06:00:00Z"
            }
        }
