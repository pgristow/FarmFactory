# FarmFactory API Reference

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Currently, no authentication is required. JWT authentication will be added in future updates.

---

## Health & Status Endpoints

### Health Check
Check API and system health status.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "environment": "development",
  "database": "connected",
  "redis": "not_configured"
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

### System Status
Get detailed system information.

**Endpoint:** `GET /status`

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/status"
```

### Ping
Simple ping endpoint for uptime monitoring.

**Endpoint:** `GET /ping`

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/ping"
```

---

## Farm Endpoints

### Create Farm
Create a new farm.

**Endpoint:** `POST /farms`

**Request Body:**
```json
{
  "name": "Green Valley Farm",
  "address": "123 Farm Road, Rural County, State 12345",
  "latitude": 34.0522,
  "longitude": -118.2437,
  "total_area_hectares": 50.5,
  "timezone": "America/Los_Angeles"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Green Valley Farm",
    "address": "123 Farm Road, Rural County, State 12345",
    "latitude": 34.0522,
    "longitude": -118.2437,
    "total_area_hectares": 50.5,
    "timezone": "America/Los_Angeles",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

**Example:**
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
Get a paginated list of all farms.

**Endpoint:** `GET /farms`

**Query Parameters:**
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 20, max: 100): Items per page

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "Green Valley Farm",
      "address": "123 Farm Road",
      "latitude": 34.0522,
      "longitude": -118.2437,
      "total_area_hectares": 50.5,
      "timezone": "America/Los_Angeles",
      "created_at": "2024-01-15T10:30:00Z",
      "plot_count": 5
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

**Example:**
```bash
# Get first page with default page size
curl -X GET "http://localhost:8000/api/v1/farms"

# Get second page with 10 items per page
curl -X GET "http://localhost:8000/api/v1/farms?page=2&page_size=10"
```

### Get Farm
Get detailed information about a specific farm.

**Endpoint:** `GET /farms/{farm_id}`

**Path Parameters:**
- `farm_id` (UUID): Farm ID

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Green Valley Farm",
    "address": "123 Farm Road, Rural County, State 12345",
    "latitude": 34.0522,
    "longitude": -118.2437,
    "total_area_hectares": 50.5,
    "timezone": "America/Los_Angeles",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/farms/123e4567-e89b-12d3-a456-426614174000"
```

### Update Farm
Update a farm's information.

**Endpoint:** `PUT /farms/{farm_id}`

**Path Parameters:**
- `farm_id` (UUID): Farm ID

**Request Body (all fields optional):**
```json
{
  "name": "Updated Farm Name",
  "total_area_hectares": 55.0
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Updated Farm Name",
    "address": "123 Farm Road, Rural County, State 12345",
    "latitude": 34.0522,
    "longitude": -118.2437,
    "total_area_hectares": 55.0,
    "timezone": "America/Los_Angeles",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

**Example:**
```bash
curl -X PUT "http://localhost:8000/api/v1/farms/123e4567-e89b-12d3-a456-426614174000" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Farm Name",
    "total_area_hectares": 55.0
  }'
```

### Delete Farm
Delete a farm and all associated plots.

**Endpoint:** `DELETE /farms/{farm_id}`

**Path Parameters:**
- `farm_id` (UUID): Farm ID

**Response:**
```json
{
  "success": true,
  "message": "Farm with id '123e4567-e89b-12d3-a456-426614174000' deleted successfully",
  "data": null
}
```

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/farms/123e4567-e89b-12d3-a456-426614174000"
```

---

## Plot Endpoints

### Create Plot
Create a new plot within a farm.

**Endpoint:** `POST /plots`

**Request Body:**
```json
{
  "farm_id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "North Field",
  "plot_number": "NF-01",
  "area_hectares": 2.5,
  "elevation_meters": 150.0,
  "slope_degrees": 5.2
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "223e4567-e89b-12d3-a456-426614174001",
    "farm_id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "North Field",
    "plot_number": "NF-01",
    "area_hectares": 2.5,
    "elevation_meters": 150.0,
    "slope_degrees": 5.2,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/plots" \
  -H "Content-Type: application/json" \
  -d '{
    "farm_id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "North Field",
    "plot_number": "NF-01",
    "area_hectares": 2.5,
    "elevation_meters": 150.0,
    "slope_degrees": 5.2
  }'
```

### List Plots
Get a paginated list of all plots.

**Endpoint:** `GET /plots`

**Query Parameters:**
- `farm_id` (UUID, optional): Filter by farm ID
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 20, max: 100): Items per page

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "223e4567-e89b-12d3-a456-426614174001",
      "farm_id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "North Field",
      "plot_number": "NF-01",
      "area_hectares": 2.5,
      "elevation_meters": 150.0,
      "slope_degrees": 5.2,
      "created_at": "2024-01-15T10:30:00Z",
      "planting_count": 2
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

**Examples:**
```bash
# Get all plots
curl -X GET "http://localhost:8000/api/v1/plots"

# Get plots for a specific farm
curl -X GET "http://localhost:8000/api/v1/plots?farm_id=123e4567-e89b-12d3-a456-426614174000"

# Get second page with 10 items per page
curl -X GET "http://localhost:8000/api/v1/plots?page=2&page_size=10"
```

### Get Plot
Get detailed information about a specific plot.

**Endpoint:** `GET /plots/{plot_id}`

**Path Parameters:**
- `plot_id` (UUID): Plot ID

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "223e4567-e89b-12d3-a456-426614174001",
    "farm_id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "North Field",
    "plot_number": "NF-01",
    "area_hectares": 2.5,
    "elevation_meters": 150.0,
    "slope_degrees": 5.2,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/plots/223e4567-e89b-12d3-a456-426614174001"
```

### Update Plot
Update a plot's information.

**Endpoint:** `PUT /plots/{plot_id}`

**Path Parameters:**
- `plot_id` (UUID): Plot ID

**Request Body (all fields optional):**
```json
{
  "name": "Updated Plot Name",
  "area_hectares": 3.0
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "223e4567-e89b-12d3-a456-426614174001",
    "farm_id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Updated Plot Name",
    "plot_number": "NF-01",
    "area_hectares": 3.0,
    "elevation_meters": 150.0,
    "slope_degrees": 5.2,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

**Example:**
```bash
curl -X PUT "http://localhost:8000/api/v1/plots/223e4567-e89b-12d3-a456-426614174001" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Plot Name",
    "area_hectares": 3.0
  }'
```

### Delete Plot
Delete a plot and all associated data.

**Endpoint:** `DELETE /plots/{plot_id}`

**Path Parameters:**
- `plot_id` (UUID): Plot ID

**Response:**
```json
{
  "success": true,
  "message": "Plot with id '223e4567-e89b-12d3-a456-426614174001' deleted successfully",
  "data": null
}
```

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/plots/223e4567-e89b-12d3-a456-426614174001"
```

---

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "errors": []
}
```

### Common Error Codes

- `VALIDATION_ERROR` (422): Request validation failed
- `NOT_FOUND` (404): Resource not found
- `INTERNAL_SERVER_ERROR` (500): Internal server error
- `HTTP_400` (400): Bad request
- `HTTP_401` (401): Unauthorized
- `HTTP_403` (403): Forbidden

### Example Error Response

```json
{
  "success": false,
  "message": "Farm with id '123e4567-e89b-12d3-a456-426614174000' not found",
  "error_code": "NOT_FOUND",
  "path": "/api/v1/farms/123e4567-e89b-12d3-a456-426614174000"
}
```

---

## Testing the API

### Using the Test Script

Run the included test script:

```bash
# Make sure the API is running first
uvicorn app.main:app --reload

# In another terminal, run the test script
python test_api.py
```

### Using Swagger UI

Access the interactive API documentation:

```
http://localhost:8000/api/docs
```

### Using Python Requests

```python
import requests

# Create a farm
response = requests.post(
    "http://localhost:8000/api/v1/farms",
    json={
        "name": "My Farm",
        "total_area_hectares": 100.0
    }
)
farm = response.json()["data"]
print(f"Created farm: {farm['id']}")

# List farms
response = requests.get("http://localhost:8000/api/v1/farms")
farms = response.json()["data"]
print(f"Total farms: {response.json()['total']}")
```

---

## Rate Limiting

Currently, no rate limiting is implemented. This will be added in future updates.

## Pagination

All list endpoints support pagination with the following parameters:

- `page`: Page number (1-indexed, default: 1)
- `page_size`: Items per page (default: 20, max: 100)

Response includes:
- `data`: Array of items
- `total`: Total number of items
- `page`: Current page
- `page_size`: Items per page
- `total_pages`: Total number of pages

---

## API Versioning

The API uses URL versioning with the prefix `/api/v1`. Future versions will use `/api/v2`, etc.

## Support

For issues or questions, please refer to the main README.md or contact the development team.
