"""
Pydantic schemas for Environmental Reading entities
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class EnvironmentalReadingBase(BaseModel):
    """Base schema for Environmental Reading"""
    plot_id: UUID = Field(..., description="ID of the plot")
    time: datetime = Field(..., description="Timestamp of reading")
    air_temp_celsius: Optional[Decimal] = Field(None, description="Air temperature in Celsius")
    soil_temp_celsius: Optional[Decimal] = Field(None, description="Soil temperature in Celsius")
    humidity_percent: Optional[Decimal] = Field(None, ge=0, le=100, description="Relative humidity (0-100)")
    soil_moisture_percent: Optional[Decimal] = Field(None, ge=0, le=100, description="Soil moisture (0-100)")
    light_intensity_lux: Optional[Decimal] = Field(None, ge=0, description="Light intensity in lux")
    rainfall_mm: Optional[Decimal] = Field(None, ge=0, description="Rainfall in mm")
    wind_speed_kmh: Optional[Decimal] = Field(None, ge=0, description="Wind speed in km/h")
    atmospheric_pressure_hpa: Optional[Decimal] = Field(None, ge=0, description="Atmospheric pressure in hPa")

    @field_validator('air_temp_celsius', 'soil_temp_celsius', 'humidity_percent',
                     'soil_moisture_percent', 'light_intensity_lux', 'rainfall_mm',
                     'wind_speed_kmh', 'atmospheric_pressure_hpa', mode='before')
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
                "time": "2024-01-15T14:30:00Z",
                "air_temp_celsius": 24.5,
                "soil_temp_celsius": 22.0,
                "humidity_percent": 65.0,
                "soil_moisture_percent": 45.0,
                "light_intensity_lux": 50000.0,
                "rainfall_mm": 0.0,
                "wind_speed_kmh": 12.5,
                "atmospheric_pressure_hpa": 1013.25
            }
        }


class EnvironmentalReadingCreate(EnvironmentalReadingBase):
    """Schema for creating a new environmental reading"""
    pass


class EnvironmentalReadingBatchCreate(BaseModel):
    """Schema for batch creating environmental readings"""
    readings: list[EnvironmentalReadingCreate] = Field(..., min_length=1, max_length=1000)


class EnvironmentalReadingInDB(EnvironmentalReadingBase):
    """Schema for Environmental Reading stored in database"""

    class Config:
        from_attributes = True


class EnvironmentalReadingLatest(BaseModel):
    """Schema for latest environmental readings per plot"""
    plot_id: UUID
    plot_name: str
    latest_reading: Optional[EnvironmentalReadingInDB] = None
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True


class EnvironmentalAverages(BaseModel):
    """Schema for environmental data averages"""
    plot_id: UUID
    plot_name: str
    period_start: datetime
    period_end: datetime
    avg_air_temp: Optional[Decimal] = None
    avg_soil_temp: Optional[Decimal] = None
    avg_humidity: Optional[Decimal] = None
    avg_soil_moisture: Optional[Decimal] = None
    avg_light_intensity: Optional[Decimal] = None
    total_rainfall: Optional[Decimal] = None
    avg_wind_speed: Optional[Decimal] = None
    avg_pressure: Optional[Decimal] = None
    reading_count: int

    class Config:
        from_attributes = True
