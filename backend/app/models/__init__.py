"""
Models package initialization.

Import all models here to ensure they are registered with SQLAlchemy
before Alembic generates migrations.
"""
from app.models.base import Base, TimestampMixin, UUIDMixin

# Core farm models
from app.models.farm import Farm
from app.models.plot import Plot
from app.models.soil import SoilProfile

# Crop models
from app.models.crop import Crop, Planting
from app.models.phenology import PhenologyObservation

# Time-series models (TimescaleDB hypertables)
from app.models.irrigation import IrrigationEvent
from app.models.nutrient import NutrientApplication
from app.models.water_quality import WaterQuality
from app.models.environmental import EnvironmentalReading

# Financial models
from app.models.financial import InputCost, Harvest

# Alert models
from app.models.alert import AlertThreshold, Alert

# Export all models for easy importing
__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDMixin",
    "Farm",
    "Plot",
    "SoilProfile",
    "Crop",
    "Planting",
    "PhenologyObservation",
    "IrrigationEvent",
    "NutrientApplication",
    "WaterQuality",
    "EnvironmentalReading",
    "InputCost",
    "Harvest",
    "AlertThreshold",
    "Alert",
]
