# FarmFactory API Quick Reference - Sprint 3

**Base URL**: `http://localhost:8000/api/v1`

---

## Crops API

```bash
# Create crop
curl -X POST $BASE_URL/crops \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tomato",
    "variety": "Roma",
    "days_to_maturity": 75
  }'

# List crops
curl "$BASE_URL/crops?page=1&page_size=20"

# Get crop
curl "$BASE_URL/crops/{crop_id}"

# Update crop
curl -X PUT "$BASE_URL/crops/{crop_id}" \
  -H "Content-Type: application/json" \
  -d '{"days_to_maturity": 80}'

# Delete crop
curl -X DELETE "$BASE_URL/crops/{crop_id}"
```

---

## Plantings API

```bash
# Create planting
curl -X POST $BASE_URL/plantings \
  -H "Content-Type: application/json" \
  -d '{
    "plot_id": "123e4567-e89b-12d3-a456-426614174000",
    "crop_id": "223e4567-e89b-12d3-a456-426614174001",
    "planting_date": "2024-03-15",
    "status": "planted"
  }'

# List plantings
curl "$BASE_URL/plantings?page=1&page_size=20&status=growing"

# Get planting
curl "$BASE_URL/plantings/{planting_id}"

# Update planting
curl -X PUT "$BASE_URL/plantings/{planting_id}" \
  -H "Content-Type: application/json" \
  -d '{"status": "growing"}'

# Update planting status (quick)
curl -X PATCH "$BASE_URL/plantings/{planting_id}/status?status=harvested"

# Get planting calendar
curl "$BASE_URL/plantings/calendar?year=2024"

# Delete planting
curl -X DELETE "$BASE_URL/plantings/{planting_id}"
```

---

## Irrigation API

```bash
# Create irrigation event
curl -X POST $BASE_URL/irrigation \
  -H "Content-Type: application/json" \
  -d '{
    "plot_id": "123e4567-e89b-12d3-a456-426614174000",
    "time": "2024-11-15T06:00:00Z",
    "method": "drip",
    "duration_minutes": 120,
    "water_volume_liters": 500.0
  }'

# List irrigation events
curl "$BASE_URL/irrigation?plot_id={plot_id}&start_date=2024-11-01T00:00:00Z&end_date=2024-11-30T23:59:59Z"

# Filter by method
curl "$BASE_URL/irrigation?plot_id={plot_id}&method=drip"

# Get specific event (composite key)
curl "$BASE_URL/irrigation/{plot_id}/2024-11-15T06:00:00Z"

# Update irrigation event
curl -X PUT "$BASE_URL/irrigation/{plot_id}/2024-11-15T06:00:00Z" \
  -H "Content-Type: application/json" \
  -d '{"water_volume_liters": 520.0}'

# Get irrigation summary
curl "$BASE_URL/irrigation/summary?plot_id={plot_id}&start_date=2024-11-01T00:00:00Z&end_date=2024-11-30T23:59:59Z"

# Delete irrigation event
curl -X DELETE "$BASE_URL/irrigation/{plot_id}/2024-11-15T06:00:00Z"
```

---

## Aggregations API

```bash
# Daily aggregations
curl "$BASE_URL/aggregations/daily?table=irrigation_events&plot_id={plot_id}&start_date=2024-11-01T00:00:00Z&end_date=2024-11-30T23:59:59Z"

# Weekly aggregations
curl "$BASE_URL/aggregations/weekly?table=environmental_readings&plot_id={plot_id}&start_date=2024-11-01T00:00:00Z&end_date=2024-11-30T23:59:59Z"

# Monthly aggregations
curl "$BASE_URL/aggregations/monthly?table=nutrient_applications&plot_id={plot_id}&start_date=2024-01-01T00:00:00Z&end_date=2024-12-31T23:59:59Z"

# Summary statistics
curl "$BASE_URL/aggregations/summary?table=irrigation_events&plot_id={plot_id}&start_date=2024-11-01T00:00:00Z&end_date=2024-11-30T23:59:59Z"

# Compare periods
curl "$BASE_URL/aggregations/compare?table=irrigation_events&metric=water_volume_liters&plot_id={plot_id}&period1_start=2024-10-01T00:00:00Z&period1_end=2024-10-31T23:59:59Z&period2_start=2024-11-01T00:00:00Z&period2_end=2024-11-30T23:59:59Z"
```

---

## Supported Tables for Aggregations

- `irrigation_events`
- `nutrient_applications`
- `environmental_readings`
- `water_quality`

---

## Common Query Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `page` | int | Page number (1-indexed) | 1 |
| `page_size` | int | Items per page | 20 |
| `plot_id` | UUID | Filter by plot | - |
| `start_date` | datetime | Start of date range | - |
| `end_date` | datetime | End of date range | - |

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## Date Format

All dates should be in ISO 8601 format:
- `2024-11-15` (date only)
- `2024-11-15T06:00:00Z` (datetime with timezone)

---

## Swagger Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Testing

```bash
# Run all integration tests
cd /home/user/FarmFactory/backend
pytest tests/integration/ -v

# Run specific test suite
pytest tests/integration/test_crops_api.py -v
pytest tests/integration/test_irrigation_api.py -v

# Run with coverage
pytest tests/integration/ --cov=app.api.v1.endpoints
```

---

## Example Variables

Replace these placeholders in the examples:

```bash
export BASE_URL="http://localhost:8000/api/v1"
export PLOT_ID="123e4567-e89b-12d3-a456-426614174000"
export CROP_ID="223e4567-e89b-12d3-a456-426614174001"
export PLANTING_ID="323e4567-e89b-12d3-a456-426614174002"
```

Then use in commands:

```bash
curl "$BASE_URL/crops/$CROP_ID"
curl "$BASE_URL/plantings?plot_id=$PLOT_ID"
```
