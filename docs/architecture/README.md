# FarmFactory Architecture Overview

This document provides a high-level overview of the FarmFactory system architecture.

---

## System Architecture

FarmFactory follows a modern three-tier architecture with microservices principles:

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │  Web Browser   │  │  Mobile App    │  │   API        │  │
│  │   (React)      │  │  (Future)      │  │   Clients    │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              FastAPI Backend (Python)                 │  │
│  │  ┌────────┐  ┌────────┐  ┌─────────┐  ┌──────────┐  │  │
│  │  │  API   │  │ Business│  │  Tasks  │  │  Alerts  │  │  │
│  │  │ Layer  │  │  Logic  │  │ (Celery)│  │  Service │  │  │
│  │  └────────┘  └────────┘  └─────────┘  └──────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       Data Layer                             │
│  ┌──────────────────┐  ┌────────────┐  ┌────────────────┐  │
│  │   PostgreSQL     │  │   Redis    │  │  File Storage  │  │
│  │  + TimescaleDB   │  │  (Cache/   │  │    (MinIO/     │  │
│  │   + PostGIS      │  │   Queue)   │  │     S3)        │  │
│  └──────────────────┘  └────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Frontend (React + TypeScript)

**Purpose**: User interface for farm management and data visualization

**Key Features**:
- Responsive dashboard
- Real-time data visualization
- Interactive forms and data import
- Alert notifications

**Technology Stack**:
- React 18 with TypeScript
- Material-UI components
- Recharts for visualization
- React Query for data management
- React Leaflet for mapping

**Location**: `/frontend`

### 2. Backend API (FastAPI)

**Purpose**: RESTful API for all business logic and data operations

**Key Features**:
- CRUD operations for all entities
- Data validation and transformation
- Authentication and authorization
- Real-time data streaming
- File upload processing

**Technology Stack**:
- FastAPI (Python 3.11+)
- SQLAlchemy ORM
- Pydantic for validation
- JWT authentication

**Location**: `/backend/app`

### 3. Database (PostgreSQL + Extensions)

**Purpose**: Persistent data storage with time-series and spatial capabilities

**Components**:
- **PostgreSQL 14+**: Primary relational database
- **TimescaleDB**: Time-series data optimization
- **PostGIS**: Spatial data support (farm/plot locations)

**Key Tables**:
- Farm management: `farms`, `plots`, `crops`, `plantings`
- Time-series: `irrigation_events`, `nutrient_applications`, `environmental_readings`
- Analytics: `alerts`, `predictions`, `recommendations`

**Location**: Database schema in `/backend/app/models`

### 4. Cache & Message Queue (Redis)

**Purpose**: Performance optimization and asynchronous task management

**Use Cases**:
- **Caching**: Dashboard data, frequently accessed queries
- **Session Management**: User sessions
- **Task Queue**: Celery message broker
- **Real-time Updates**: Pub/Sub for live notifications

### 5. Task Queue (Celery)

**Purpose**: Asynchronous processing of long-running tasks

**Tasks**:
- CSV/Excel file import processing
- Data validation and transformation
- Alert evaluation
- Report generation
- Analytics calculations

**Configuration**: `/backend/app/tasks`

### 6. File Storage

**Purpose**: Store uploaded files and generated reports

**Options**:
- **Local Development**: Local filesystem
- **Production**: MinIO (S3-compatible) or cloud storage (AWS S3, GCS)

**Stored Files**:
- Uploaded CSV/Excel files
- Generated reports (PDF, CSV)
- User-uploaded images
- Export files

---

## Data Flow

### Data Import Flow

```
User uploads CSV
    │
    ▼
Frontend validates file
    │
    ▼
POST /api/v1/import/upload
    │
    ▼
Backend stores file temporarily
    │
    ▼
Celery task created
    │
    ▼
Task processes file in batches
    │
    ├─→ Parse CSV
    ├─→ Validate data
    ├─→ Transform units
    └─→ Insert to database
    │
    ▼
Update import status
    │
    ▼
Notify frontend (WebSocket or polling)
    │
    ▼
User views import report
```

### Real-time Monitoring Flow

```
Sensor data arrives (IoT/Manual entry)
    │
    ▼
POST /api/v1/environmental-readings
    │
    ▼
Backend validates and stores
    │
    ▼
TimescaleDB inserts time-series data
    │
    ▼
Alert service checks thresholds
    │
    ├─→ Threshold exceeded?
    │   │
    │   ▼ Yes
    │   Create alert
    │   │
    │   ▼
    │   Send notification (email/SMS)
    │
    ▼
Update dashboard cache (Redis)
    │
    ▼
Frontend polls or receives WebSocket update
    │
    ▼
Dashboard displays new data
```

### Analytics Flow

```
User requests analytics
    │
    ▼
GET /api/v1/plots/{id}/analytics/yield-trends
    │
    ▼
Backend checks cache
    │
    ├─→ Cache hit → Return cached result
    │
    └─→ Cache miss
        │
        ▼
        Query TimescaleDB for historical data
        │
        ▼
        Apply analytics algorithms
        │
        ▼
        Generate predictions (ML models)
        │
        ▼
        Store result in cache (TTL: 1 hour)
        │
        ▼
        Return to frontend
        │
        ▼
        Display charts and insights
```

---

## Security Architecture

### Authentication Flow

```
1. User Login
   POST /api/v1/auth/login
   {email, password}
   │
   ▼
2. Verify credentials (bcrypt)
   │
   ▼
3. Generate JWT token
   {user_id, permissions, exp}
   │
   ▼
4. Return token to client
   │
   ▼
5. Client stores token (localStorage/cookie)
   │
   ▼
6. Include in subsequent requests
   Authorization: Bearer {token}
   │
   ▼
7. Backend validates token
   │
   ├─→ Valid → Process request
   └─→ Invalid → 401 Unauthorized
```

### Authorization Layers

1. **Route-level**: FastAPI dependencies check authentication
2. **Resource-level**: Verify user owns the farm/plot
3. **Role-based**: Admin, Manager, Viewer permissions

### Data Protection

- **In Transit**: HTTPS/TLS encryption
- **At Rest**: Database encryption
- **Secrets**: Environment variables, never committed
- **Input Validation**: Pydantic schemas
- **SQL Injection**: ORM parameterization
- **XSS**: React auto-escaping

---

## Scalability Considerations

### Horizontal Scaling

```
Load Balancer (NGINX)
    │
    ├─→ API Server 1
    ├─→ API Server 2
    └─→ API Server N
    │
    ▼
Database (with read replicas)
    │
    ├─→ Primary (writes)
    └─→ Replicas (reads)
```

### Performance Optimizations

1. **Database**:
   - TimescaleDB automatic partitioning
   - Indexing on frequently queried columns
   - Connection pooling (pgBouncer)
   - Query optimization

2. **Caching**:
   - Redis for hot data
   - HTTP caching headers
   - CDN for static assets

3. **API**:
   - Async request handling (FastAPI)
   - Pagination for large datasets
   - Lazy loading
   - Rate limiting

4. **Frontend**:
   - Code splitting
   - Lazy component loading
   - Memoization (React.memo)
   - Virtual scrolling for large lists

---

## Monitoring & Observability

### Metrics to Track

- **Application**: Response times, error rates, throughput
- **Database**: Query performance, connection pool usage
- **Infrastructure**: CPU, memory, disk I/O
- **Business**: Active users, data import volume, alert frequency

### Logging Strategy

```
Application Logs
    │
    ▼
Structured JSON format
    │
    ▼
Log aggregation (ELK Stack / Grafana Loki)
    │
    ▼
Dashboards and alerts
```

### Health Checks

- `GET /health` - Basic health check
- `GET /health/db` - Database connectivity
- `GET /health/redis` - Redis connectivity
- `GET /health/detailed` - Full system status

---

## Deployment Architecture

### Development

```
Docker Compose
├── postgres (TimescaleDB)
├── redis
├── backend (FastAPI)
├── celery_worker
└── frontend (React dev server)
```

### Production (Kubernetes)

```
Ingress (NGINX)
    │
    ├─→ Frontend (Static files + CDN)
    │
    └─→ Backend API
        ├─→ Pod 1
        ├─→ Pod 2
        └─→ Pod N
    │
    ├─→ Celery Workers
    │   ├─→ Worker 1
    │   └─→ Worker 2
    │
    ├─→ PostgreSQL (Managed service)
    │
    ├─→ Redis (Managed service)
    │
    └─→ Object Storage (S3/GCS)
```

---

## Related Documentation

- [Component Diagram](./components.md) - Detailed component interactions
- [Data Flow](./data-flow.md) - Data flow diagrams
- [Database Schema](./database-schema.md) - ER diagrams
- [API Architecture](./api-architecture.md) - API design patterns
- [Infrastructure](./infrastructure.md) - Deployment details
- [Security Model](./security.md) - Security architecture

---

## Technology Decisions

See [PROJECT_STATUS.md](../../PROJECT_STATUS.md) for rationale behind technology choices.

---

**Last Updated**: 2025-11-16
**Version**: 1.0.0
**Maintained By**: Architecture Team
