"""
API v1 Router
Includes all endpoint routers for API version 1
"""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    health, farms, plots, import_api,
    crops, irrigation, nutrients, environmental,
    water_quality, phenology, financial, aggregations
)

# Create main API router
api_router = APIRouter()

# ==================== SYSTEM ENDPOINTS ====================

# Include health check endpoints
api_router.include_router(
    health.router,
    tags=["Health"]
)

# ==================== FARM MANAGEMENT ENDPOINTS ====================

# Include farm endpoints
api_router.include_router(
    farms.router,
    prefix="/farms",
    tags=["Farms"]
)

# Include plot endpoints
api_router.include_router(
    plots.router,
    prefix="/plots",
    tags=["Plots"]
)

# ==================== CROP MANAGEMENT ENDPOINTS ====================

# Include crop and planting endpoints
api_router.include_router(
    crops.router,
    tags=["Crops", "Plantings"]
)

# ==================== OPERATIONAL DATA ENDPOINTS ====================

# Include irrigation endpoints
api_router.include_router(
    irrigation.router,
    prefix="/irrigation",
    tags=["Irrigation"]
)

# Include nutrient application endpoints
api_router.include_router(
    nutrients.router,
    prefix="/nutrients",
    tags=["Nutrients"]
)

# ==================== MONITORING ENDPOINTS ====================

# Include environmental monitoring endpoints
api_router.include_router(
    environmental.router,
    prefix="/environmental",
    tags=["Environmental"]
)

# Include water quality endpoints
api_router.include_router(
    water_quality.router,
    prefix="/water-quality",
    tags=["Water Quality"]
)

# Include phenology observation endpoints
api_router.include_router(
    phenology.router,
    prefix="/phenology",
    tags=["Phenology"]
)

# ==================== FINANCIAL ENDPOINTS ====================

# Include financial tracking endpoints (costs and harvests)
api_router.include_router(
    financial.router,
    prefix="/financial",
    tags=["Financial"]
)

# ==================== DATA AGGREGATION ENDPOINTS ====================

# Include time-series aggregation endpoints
api_router.include_router(
    aggregations.router,
    prefix="/aggregations",
    tags=["Aggregations"]
)

# ==================== DATA IMPORT ENDPOINTS ====================

# Include import endpoints
api_router.include_router(
    import_api.router,
    prefix="/import",
    tags=["Import"]
)

# TODO: Future endpoints to be implemented:
# - /alerts - Alert threshold configuration and notifications
# - /analytics - Advanced analytics and predictions
# - /reports - Report generation and exports
