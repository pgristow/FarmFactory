"""
API v1 Router
Includes all endpoint routers for API version 1
"""
from fastapi import APIRouter
from app.api.v1.endpoints import health, farms, plots, import_api

# Create main API router
api_router = APIRouter()

# Include health check endpoints
api_router.include_router(
    health.router,
    tags=["Health"]
)

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

# Include import endpoints
api_router.include_router(
    import_api.router,
    prefix="/import",
    tags=["Import"]
)

# TODO: Add more endpoint routers as they are implemented:
# - /crops
# - /plantings
# - /irrigation
# - /nutrients
# - /analytics
# - /alerts
