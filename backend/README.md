# FarmFactory Backend API

FastAPI-based REST API for the FarmFactory farm optimization and management system.

## Features

- **FastAPI Framework**: High-performance async API with automatic OpenAPI documentation
- **PostgreSQL + TimescaleDB**: Robust relational database with time-series optimization
- **Pydantic Validation**: Strong typing and data validation
- **CORS Support**: Configurable cross-origin resource sharing
- **Comprehensive Error Handling**: Standardized error responses
- **Health Check Endpoints**: System status monitoring

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/     # API endpoint handlers
│   │       │   ├── farms.py
│   │       │   ├── plots.py
│   │       │   └── health.py
│   │       └── router.py      # Main API router
│   ├── core/
│   │   ├── config.py          # Application configuration
│   │   ├── database.py        # Database connection
│   │   ├── deps.py            # Dependency injection
│   │   └── security.py        # Authentication utilities
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic layer
│   └── utils/                 # Utility functions
├── requirements.txt           # Python dependencies
└── main.py                    # Application entry point
```

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ with TimescaleDB extension
- Redis (optional, for caching)

### Setup

1. **Clone the repository**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb farmfactory

   # Install TimescaleDB extension
   psql -d farmfactory -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"
   ```

6. **Run migrations** (when Alembic is set up)
   ```bash
   alembic upgrade head
   ```

## Running the Application

### Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or using Python directly:

```bash
python -m app.main
```

### Access the API

- **API Documentation (Swagger)**: http://localhost:8000/api/docs
- **Alternative Documentation (ReDoc)**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json
- **Health Check**: http://localhost:8000/api/v1/health

## API Endpoints

### Health & Status

- `GET /api/v1/health` - Health check
- `GET /api/v1/status` - Detailed system status
- `GET /api/v1/ping` - Simple ping endpoint

### Farms

- `POST /api/v1/farms` - Create a new farm
- `GET /api/v1/farms` - List all farms (paginated)
- `GET /api/v1/farms/{farm_id}` - Get farm by ID
- `PUT /api/v1/farms/{farm_id}` - Update farm
- `DELETE /api/v1/farms/{farm_id}` - Delete farm

### Plots

- `POST /api/v1/plots` - Create a new plot
- `GET /api/v1/plots` - List all plots (paginated, filterable by farm)
- `GET /api/v1/plots/{plot_id}` - Get plot by ID
- `PUT /api/v1/plots/{plot_id}` - Update plot
- `DELETE /api/v1/plots/{plot_id}` - Delete plot

## Example Usage

### Create a Farm

```bash
curl -X POST "http://localhost:8000/api/v1/farms" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Green Valley Farm",
    "address": "123 Farm Road, Rural County, State 12345",
    "latitude": 34.0522,
    "longitude": -118.2437,
    "total_area_hectares": 50.5,
    "timezone": "America/Los_Angeles"
  }'
```

### List Farms

```bash
curl -X GET "http://localhost:8000/api/v1/farms?page=1&page_size=20"
```

### Create a Plot

```bash
curl -X POST "http://localhost:8000/api/v1/plots" \
  -H "Content-Type: application/json" \
  -d '{
    "farm_id": "YOUR_FARM_ID_HERE",
    "name": "North Field",
    "plot_number": "NF-01",
    "area_hectares": 2.5,
    "elevation_meters": 150.0,
    "slope_degrees": 5.2
  }'
```

## Configuration

Key configuration options in `.env`:

- `DATABASE_URL`: PostgreSQL connection string
- `CORS_ORIGINS`: Allowed frontend origins (comma-separated)
- `SECRET_KEY`: Secret key for JWT tokens
- `DEBUG`: Enable/disable debug mode
- `ENVIRONMENT`: Environment name (development/staging/production)

## Development

### Code Style

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app tests/
```

## Database Models

- **Farm**: Farm entity with geographic coordinates
- **Plot**: Individual fields/plots within a farm
- **Crop**: Crop master data
- **Planting**: Planting records
- **IrrigationEvent**: Irrigation events (time-series)
- **NutrientApplication**: Nutrient applications (time-series)
- **And more...**

## Error Handling

All endpoints return standardized error responses:

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "errors": []
}
```

## Authentication

Authentication is currently a placeholder. JWT-based authentication will be implemented in future updates.

## License

Proprietary - All rights reserved

## Support

For issues or questions, please contact the development team.
