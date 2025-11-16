# FarmFactory API Documentation

Welcome to the FarmFactory REST API documentation. This API provides programmatic access to all farm optimization features.

---

## Base URL

```
Production: https://api.farmfactory.example.com/api/v1
Development: http://localhost:8000/api/v1
```

---

## Interactive Documentation

When the backend is running, you can access interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## API Overview

The FarmFactory API is organized around REST principles. It accepts JSON-encoded requests and returns JSON-encoded responses.

### Key Features

- 🔐 **JWT-based Authentication** - Secure token-based auth
- 📊 **Comprehensive Data Access** - Farm, plot, crop, and sensor data
- 📈 **Analytics Endpoints** - Yield prediction and optimization
- 🔔 **Alert Management** - Configure and manage alerts
- 📤 **Bulk Import** - Upload CSV/Excel files
- 📥 **Export Capabilities** - Download data in various formats

---

## Authentication

See [Authentication Guide](./authentication.md) for details.

Quick example:

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}

# Use token in requests
curl -X GET http://localhost:8000/api/v1/farms \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Endpoint Categories

### Farm Management
- `GET /farms` - List all farms
- `POST /farms` - Create new farm
- `GET /farms/{id}` - Get farm details
- `PUT /farms/{id}` - Update farm
- `DELETE /farms/{id}` - Delete farm

### Plot Management
- `GET /farms/{farm_id}/plots` - List plots
- `POST /farms/{farm_id}/plots` - Create plot
- `GET /plots/{id}` - Get plot details
- `PUT /plots/{id}` - Update plot
- `DELETE /plots/{id}` - Delete plot

### Data Import
- `POST /import/upload` - Upload file
- `POST /import/preview` - Preview data
- `POST /import/process` - Process import
- `GET /import/status/{job_id}` - Check import status

### Time-Series Data
- `GET /plots/{id}/irrigation` - Get irrigation data
- `GET /plots/{id}/nutrients` - Get nutrient data
- `GET /plots/{id}/water-quality` - Get water quality data
- `GET /plots/{id}/environmental` - Get environmental data

### Analytics
- `GET /plots/{id}/analytics/yield-trends` - Yield trends
- `GET /plots/{id}/analytics/input-efficiency` - Input efficiency
- `GET /plots/{id}/analytics/cost-analysis` - Cost analysis
- `GET /plots/{id}/analytics/recommendations` - Optimization recommendations

### Alerts
- `GET /alerts` - List alerts
- `POST /alerts` - Create alert threshold
- `GET /alerts/{id}` - Get alert details
- `POST /alerts/{id}/acknowledge` - Acknowledge alert

See [Endpoints Reference](./endpoints.md) for complete documentation.

---

## Request Format

### Headers

```
Content-Type: application/json
Authorization: Bearer {access_token}
```

### Pagination

List endpoints support pagination:

```bash
GET /api/v1/farms?page=1&page_size=20
```

### Filtering

Most list endpoints support filtering:

```bash
GET /api/v1/plots/{id}/irrigation?start_date=2024-01-01&end_date=2024-12-31
```

### Sorting

```bash
GET /api/v1/farms?sort_by=name&order=asc
```

---

## Response Format

### Success Response

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Green Valley Farm",
  "total_area_hectares": 25.5,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### List Response

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

### Error Response

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Farm not found",
    "details": {
      "farm_id": "invalid-id"
    }
  }
}
```

See [Error Handling](./errors.md) for complete error reference.

---

## Rate Limiting

API requests are rate limited to ensure fair usage. See [Rate Limiting](./rate-limiting.md) for details.

Default limits:
- **Authenticated requests**: 1000 requests/hour
- **Unauthenticated requests**: 100 requests/hour

Rate limit headers:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1699876543
```

---

## Webhooks

Configure webhooks to receive real-time notifications for events. See [Webhooks Guide](./webhooks.md).

---

## SDKs and Client Libraries

### Official SDKs (Coming Soon)
- Python SDK
- JavaScript/TypeScript SDK
- Go SDK

### Community SDKs
- Contributions welcome!

---

## Examples

### Create a Farm

```bash
curl -X POST http://localhost:8000/api/v1/farms \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "name": "Sunny Acres Farm",
    "address": "123 Farm Road, Rural County",
    "total_area_hectares": 50.0,
    "latitude": 34.0522,
    "longitude": -118.2437,
    "timezone": "America/Los_Angeles"
  }'
```

### Get Irrigation Data

```bash
curl -X GET "http://localhost:8000/api/v1/plots/{plot_id}/irrigation?start_date=2024-01-01&end_date=2024-01-31" \
  -H "Authorization: Bearer {token}"
```

### Upload CSV Data

```bash
curl -X POST http://localhost:8000/api/v1/import/upload \
  -H "Authorization: Bearer {token}" \
  -F "file=@irrigation_data.csv" \
  -F "data_type=irrigation"
```

---

## Best Practices

1. **Use HTTPS** in production
2. **Implement exponential backoff** for retries
3. **Cache responses** when appropriate
4. **Handle rate limits** gracefully
5. **Validate input data** before sending
6. **Use pagination** for large datasets
7. **Monitor API usage** and errors

---

## Changelog

API versioning follows semantic versioning. See [CHANGELOG.md](../../CHANGELOG.md) for version history.

Current API version: **v1.0.0**

---

## Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_ORG/FarmFactory/issues)
- **Documentation**: This guide
- **Email**: api-support@farmfactory.example.com

---

**Last Updated**: 2025-11-16
**API Version**: v1.0.0
