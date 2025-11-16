"""
Pydantic schemas for Nutrient Application entities
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class NutrientApplicationBase(BaseModel):
    """Base schema for Nutrient Application"""
    plot_id: UUID = Field(..., description="ID of the plot")
    time: datetime = Field(..., description="Timestamp of nutrient application")
    nutrient_type: str = Field(..., max_length=100, description="Type of nutrient (N, P, K, Compost, etc.)")
    application_method: str = Field(..., max_length=50, description="Application method")
    amount_kg: Decimal = Field(..., ge=0, description="Amount applied in kg")
    npk_ratio: Optional[str] = Field(None, max_length=20, description="NPK ratio (e.g., 10-10-10)")
    nitrogen_kg: Optional[Decimal] = Field(None, ge=0, description="Nitrogen content in kg")
    phosphorus_kg: Optional[Decimal] = Field(None, ge=0, description="Phosphorus content in kg")
    potassium_kg: Optional[Decimal] = Field(None, ge=0, description="Potassium content in kg")
    cost_usd: Optional[Decimal] = Field(None, ge=0, description="Cost in USD")
    notes: Optional[str] = Field(None, description="Additional notes")

    @field_validator('amount_kg', 'nitrogen_kg', 'phosphorus_kg', 'potassium_kg', 'cost_usd', mode='before')
    @classmethod
    def validate_decimal(cls, v):
        """Validate and convert to Decimal"""
        if v is not None:
            return Decimal(str(v))
        return v

    @field_validator('application_method')
    @classmethod
    def validate_method(cls, v):
        """Validate application method"""
        allowed_methods = ["broadcast", "fertigation", "foliar", "banding", "injection", "other"]
        if v.lower() not in allowed_methods:
            raise ValueError(f"Method must be one of: {', '.join(allowed_methods)}")
        return v.lower()

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "plot_id": "223e4567-e89b-12d3-a456-426614174001",
                "time": "2024-01-20T08:00:00Z",
                "nutrient_type": "Compound Fertilizer",
                "application_method": "broadcast",
                "amount_kg": 50.0,
                "npk_ratio": "10-10-10",
                "nitrogen_kg": 5.0,
                "phosphorus_kg": 5.0,
                "potassium_kg": 5.0,
                "cost_usd": 75.00,
                "notes": "Pre-planting fertilization"
            }
        }


class NutrientApplicationCreate(NutrientApplicationBase):
    """Schema for creating a new nutrient application"""
    pass


class NutrientApplicationUpdate(BaseModel):
    """Schema for updating a nutrient application"""
    nutrient_type: Optional[str] = Field(None, max_length=100)
    application_method: Optional[str] = Field(None, max_length=50)
    amount_kg: Optional[Decimal] = Field(None, ge=0)
    npk_ratio: Optional[str] = Field(None, max_length=20)
    nitrogen_kg: Optional[Decimal] = Field(None, ge=0)
    phosphorus_kg: Optional[Decimal] = Field(None, ge=0)
    potassium_kg: Optional[Decimal] = Field(None, ge=0)
    cost_usd: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None


class NutrientApplicationInDB(NutrientApplicationBase):
    """Schema for Nutrient Application stored in database"""

    class Config:
        from_attributes = True


class NutrientSummary(BaseModel):
    """Schema for nutrient application summary statistics"""
    plot_id: UUID
    plot_name: str
    total_applications: int = Field(..., description="Total number of applications")
    total_nitrogen_kg: Decimal = Field(..., description="Total nitrogen applied in kg")
    total_phosphorus_kg: Decimal = Field(..., description="Total phosphorus applied in kg")
    total_potassium_kg: Decimal = Field(..., description="Total potassium applied in kg")
    total_cost_usd: Decimal = Field(..., description="Total cost in USD")
    last_application: Optional[datetime] = Field(None, description="Last application timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "plot_id": "223e4567-e89b-12d3-a456-426614174001",
                "plot_name": "North Field",
                "total_applications": 12,
                "total_nitrogen_kg": 60.0,
                "total_phosphorus_kg": 60.0,
                "total_potassium_kg": 60.0,
                "total_cost_usd": 900.00,
                "last_application": "2024-01-20T08:00:00Z"
            }
        }
