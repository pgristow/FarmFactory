# Quick Test Guide - FarmFactory API

## Start the Server

```bash
cd /home/user/FarmFactory/backend

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at: **http://localhost:8000**

---

## Test the API

### 1. Health Check
```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

Expected output:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "environment": "development",
  "database": "connected"
}
```

---

### 2. Create a Farm
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

**Save the farm ID from the response! You'll need it for the next steps.**

---

### 3. List All Farms
```bash
curl -X GET "http://localhost:8000/api/v1/farms?page=1&page_size=20"
```

---

### 4. Get Farm by ID
```bash
# Replace {FARM_ID} with the actual farm ID from step 2
curl -X GET "http://localhost:8000/api/v1/farms/{FARM_ID}"
```

---

### 5. Update Farm
```bash
# Replace {FARM_ID} with the actual farm ID
curl -X PUT "http://localhost:8000/api/v1/farms/{FARM_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Green Valley Farm - Updated",
    "total_area_hectares": 55.0
  }'
```

---

### 6. Create a Plot
```bash
# Replace {FARM_ID} with the actual farm ID
curl -X POST "http://localhost:8000/api/v1/plots" \
  -H "Content-Type: application/json" \
  -d '{
    "farm_id": "{FARM_ID}",
    "name": "North Field",
    "plot_number": "NF-01",
    "area_hectares": 2.5,
    "elevation_meters": 150.0,
    "slope_degrees": 5.2
  }'
```

**Save the plot ID from the response!**

---

### 7. List All Plots
```bash
curl -X GET "http://localhost:8000/api/v1/plots?page=1&page_size=20"
```

---

### 8. List Plots by Farm
```bash
# Replace {FARM_ID} with the actual farm ID
curl -X GET "http://localhost:8000/api/v1/plots?farm_id={FARM_ID}"
```

---

### 9. Get Plot by ID
```bash
# Replace {PLOT_ID} with the actual plot ID
curl -X GET "http://localhost:8000/api/v1/plots/{PLOT_ID}"
```

---

### 10. Update Plot
```bash
# Replace {PLOT_ID} with the actual plot ID
curl -X PUT "http://localhost:8000/api/v1/plots/{PLOT_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "North Field - Updated",
    "area_hectares": 3.0
  }'
```

---

### 11. Delete Plot
```bash
# Replace {PLOT_ID} with the actual plot ID
curl -X DELETE "http://localhost:8000/api/v1/plots/{PLOT_ID}"
```

---

### 12. Delete Farm
```bash
# Replace {FARM_ID} with the actual farm ID
curl -X DELETE "http://localhost:8000/api/v1/farms/{FARM_ID}"
```

---

## Alternative: Use the Test Script

```bash
# Make sure the server is running first
cd /home/user/FarmFactory/backend
python test_api.py
```

This will automatically test all endpoints and clean up after itself.

---

## Alternative: Use Swagger UI

1. Start the server
2. Open: http://localhost:8000/api/docs
3. Click "Try it out" on any endpoint
4. Fill in the parameters
5. Click "Execute"

---

## Complete Test Flow Example

Here's a complete test flow with actual commands:

```bash
# 1. Health check
curl -X GET "http://localhost:8000/api/v1/health"

# 2. Create a farm and save the ID
FARM_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/farms" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Farm",
    "latitude": 34.0522,
    "longitude": -118.2437,
    "total_area_hectares": 50.5
  }')

# Extract farm ID (requires jq)
FARM_ID=$(echo $FARM_RESPONSE | jq -r '.data.id')
echo "Created farm: $FARM_ID"

# 3. Create a plot
PLOT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/plots" \
  -H "Content-Type: application/json" \
  -d "{
    \"farm_id\": \"$FARM_ID\",
    \"name\": \"Test Plot\",
    \"area_hectares\": 2.5
  }")

PLOT_ID=$(echo $PLOT_RESPONSE | jq -r '.data.id')
echo "Created plot: $PLOT_ID"

# 4. List farms
curl -X GET "http://localhost:8000/api/v1/farms"

# 5. List plots for this farm
curl -X GET "http://localhost:8000/api/v1/plots?farm_id=$FARM_ID"

# 6. Update the farm
curl -X PUT "http://localhost:8000/api/v1/farms/$FARM_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Farm - Updated"
  }'

# 7. Cleanup
curl -X DELETE "http://localhost:8000/api/v1/plots/$PLOT_ID"
curl -X DELETE "http://localhost:8000/api/v1/farms/$FARM_ID"
```

---

## Troubleshooting

### Server won't start
- Check if port 8000 is already in use: `lsof -i :8000`
- Make sure PostgreSQL is running
- Check DATABASE_URL in .env file

### Connection refused
- Ensure the server is running: `curl http://localhost:8000/api/v1/health`
- Check firewall settings

### Module not found errors
- Install dependencies: `pip install -r requirements.txt`
- Activate virtual environment if using one

### Database errors
- Ensure PostgreSQL is running
- Check database connection string in .env
- Run migrations if needed: `alembic upgrade head`

---

## API Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

See `API_REFERENCE.md` for complete API documentation.
