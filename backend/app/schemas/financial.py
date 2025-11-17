"""
Pydantic schemas for Financial entities (Input Costs and Harvests)
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal


# Input Cost Schemas
class InputCostBase(BaseModel):
    """Base schema for Input Cost"""
    plot_id: Optional[UUID] = Field(None, description="ID of the plot (optional)")
    planting_id: Optional[UUID] = Field(None, description="ID of the planting (optional)")
    cost_date: date = Field(..., description="Date when cost was incurred")
    category: str = Field(..., max_length=100, description="Cost category (seeds, fertilizer, water, labor, etc.)")
    description: Optional[str] = Field(None, description="Detailed description")
    quantity: Optional[Decimal] = Field(None, ge=0, description="Quantity purchased/used")
    unit: Optional[str] = Field(None, max_length=50, description="Unit of measurement")
    unit_cost: Optional[Decimal] = Field(None, ge=0, description="Cost per unit")
    total_cost: Decimal = Field(..., ge=0, description="Total cost amount")
    currency: str = Field(default="USD", max_length=3, description="Currency code (ISO 4217)")

    @field_validator('quantity', 'unit_cost', 'total_cost', mode='before')
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
                "planting_id": "323e4567-e89b-12d3-a456-426614174002",
                "cost_date": "2024-01-10",
                "category": "seeds",
                "description": "Tomato seeds - Roma variety",
                "quantity": 5.0,
                "unit": "kg",
                "unit_cost": 25.00,
                "total_cost": 125.00,
                "currency": "USD"
            }
        }


class InputCostCreate(InputCostBase):
    """Schema for creating a new input cost"""
    pass


class InputCostUpdate(BaseModel):
    """Schema for updating an input cost"""
    cost_date: Optional[date] = None
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    quantity: Optional[Decimal] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=50)
    unit_cost: Optional[Decimal] = Field(None, ge=0)
    total_cost: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)


class InputCostInDB(InputCostBase):
    """Schema for Input Cost stored in database"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Harvest Schemas
class HarvestBase(BaseModel):
    """Base schema for Harvest"""
    planting_id: UUID = Field(..., description="ID of the planting")
    harvest_date: date = Field(..., description="Date of harvest")
    quantity_kg: Optional[Decimal] = Field(None, ge=0, description="Harvested quantity in kg")
    quality_grade: Optional[str] = Field(None, max_length=50, description="Quality grade")
    revenue_usd: Optional[Decimal] = Field(None, ge=0, description="Revenue from harvest in USD")
    market: Optional[str] = Field(None, max_length=100, description="Market where sold")
    notes: Optional[str] = Field(None, description="Additional notes")

    @field_validator('quantity_kg', 'revenue_usd', mode='before')
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
                "harvest_date": "2024-04-15",
                "quantity_kg": 250.5,
                "quality_grade": "A",
                "revenue_usd": 875.00,
                "market": "Farmers Market",
                "notes": "Excellent quality tomatoes"
            }
        }


class HarvestCreate(HarvestBase):
    """Schema for creating a new harvest"""
    pass


class HarvestUpdate(BaseModel):
    """Schema for updating a harvest"""
    harvest_date: Optional[date] = None
    quantity_kg: Optional[Decimal] = Field(None, ge=0)
    quality_grade: Optional[str] = Field(None, max_length=50)
    revenue_usd: Optional[Decimal] = Field(None, ge=0)
    market: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class HarvestInDB(HarvestBase):
    """Schema for Harvest stored in database"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Financial Summary Schemas
class ProfitLossSummary(BaseModel):
    """Schema for Profit & Loss summary"""
    plot_id: Optional[UUID] = None
    plot_name: Optional[str] = None
    period_start: date
    period_end: date
    total_revenue: Decimal = Field(default=Decimal("0.00"), description="Total revenue")
    total_costs: Decimal = Field(default=Decimal("0.00"), description="Total costs")
    profit: Decimal = Field(default=Decimal("0.00"), description="Profit (revenue - costs)")
    profit_margin: Optional[Decimal] = Field(None, description="Profit margin percentage")
    cost_breakdown: dict = Field(default_factory=dict, description="Costs by category")

    class Config:
        from_attributes = True


class ROISummary(BaseModel):
    """Schema for ROI summary"""
    plot_id: Optional[UUID] = None
    plot_name: Optional[str] = None
    crop_id: Optional[UUID] = None
    crop_name: Optional[str] = None
    total_investment: Decimal = Field(default=Decimal("0.00"))
    total_return: Decimal = Field(default=Decimal("0.00"))
    roi_percentage: Optional[Decimal] = Field(None, description="ROI as percentage")
    payback_period_days: Optional[int] = None

    class Config:
        from_attributes = True
