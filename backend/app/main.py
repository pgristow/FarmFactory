"""
FastAPI main application for FarmFactory
Provides REST API for farm optimization and management
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
from typing import Dict, Any

from app.api.v1.router import api_router
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# OpenAPI Tags Metadata
tags_metadata = [
    {
        "name": "Health",
        "description": "Health check and system status endpoints"
    },
    {
        "name": "Farms",
        "description": "Farm management operations - create, read, update, delete farms"
    },
    {
        "name": "Plots",
        "description": "Plot management operations - manage farm plots and their properties"
    },
    {
        "name": "Crops",
        "description": "Crop variety management - manage crop types and their characteristics"
    },
    {
        "name": "Plantings",
        "description": "Planting operations - track crop plantings, growth cycles, and harvests"
    },
    {
        "name": "Irrigation",
        "description": "Irrigation event tracking - log and analyze water usage across plots"
    },
    {
        "name": "Nutrients",
        "description": "Nutrient application tracking - manage fertilizer applications and NPK balance"
    },
    {
        "name": "Environmental",
        "description": "Environmental monitoring - track temperature, humidity, soil moisture, and weather data"
    },
    {
        "name": "Water Quality",
        "description": "Water quality monitoring - track pH, EC, TDS, and other water parameters"
    },
    {
        "name": "Phenology",
        "description": "Phenology observations - track plant growth stages, height, health, and photos"
    },
    {
        "name": "Financial",
        "description": "Financial tracking - manage input costs, harvest revenue, and profitability analysis"
    },
    {
        "name": "Aggregations",
        "description": "Time-series data aggregations - daily, weekly, monthly summaries and statistics"
    },
    {
        "name": "Import",
        "description": "Data import operations - bulk import data from CSV and Excel files"
    }
]

# Create FastAPI application
app = FastAPI(
    title="FarmFactory API",
    description="""
## Farm Optimization and Management System API

FarmFactory provides a comprehensive REST API for modern farm management, optimization, and data-driven decision making.

### Features

- **Farm & Plot Management**: Organize your farm structure with plots and boundaries
- **Crop Management**: Track crop varieties, plantings, and growth cycles
- **Irrigation Tracking**: Monitor water usage and optimize irrigation schedules
- **Nutrient Management**: Track fertilizer applications and NPK balance
- **Environmental Monitoring**: Real-time sensor data for temperature, humidity, soil moisture, and more
- **Water Quality**: Monitor irrigation water quality parameters
- **Phenology Tracking**: Document plant growth stages with photos and observations
- **Financial Analytics**: Track costs, revenue, and calculate ROI
- **Time-Series Aggregations**: Daily, weekly, and monthly data summaries
- **Data Import**: Bulk import historical data from CSV and Excel files

### Authentication

Authentication is currently not required. Future versions will implement JWT-based authentication.

### Rate Limiting

No rate limiting is currently enforced. Production deployments should implement rate limiting.

### Support

For issues or questions, contact support or visit our documentation.
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    openapi_tags=tags_metadata,
    contact={
        "name": "FarmFactory Support",
        "email": "support@farmfactory.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions with consistent JSON response"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": f"HTTP_{exc.status_code}",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors with detailed error messages"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "errors": errors,
            "path": str(request.url.path)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_SERVER_ERROR",
            "path": str(request.url.path)
        }
    )


# Startup and Shutdown Events
@app.on_event("startup")
async def startup_event():
    """Execute on application startup"""
    logger.info("Starting FarmFactory API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"CORS Origins: {settings.CORS_ORIGINS}")


@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown"""
    logger.info("Shutting down FarmFactory API...")


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """Root endpoint - API information"""
    return {
        "success": True,
        "message": "Welcome to FarmFactory API",
        "version": "1.0.0",
        "docs_url": "/api/docs",
        "health_check": "/api/v1/health"
    }


# Include API router
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
