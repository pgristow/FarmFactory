# FarmFactory Developer Guide

Welcome to the FarmFactory developer documentation. This guide will help you set up your development environment and contribute to the project.

---

## Prerequisites

### Required Software

- **Git** (latest version)
- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Python** 3.11+ (for local backend development)
- **Node.js** 18+ and **npm** (for local frontend development)
- **PostgreSQL** 14+ (via Docker recommended)
- **Code Editor** (VS Code, PyCharm, or your preference)

### Recommended Tools

- **Postman** or **Insomnia** - API testing
- **DBeaver** or **pgAdmin** - Database management
- **Redis Desktop Manager** - Redis inspection
- **GitHub CLI** - GitHub operations

---

## Quick Setup (Docker - Recommended)

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_ORG/FarmFactory.git
cd FarmFactory
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# Minimum required: DB_PASSWORD, SECRET_KEY
```

### 3. Start Development Environment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 4. Initialize Database

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# (Optional) Load sample data
docker-compose exec backend python scripts/seed_data.py
```

### 5. Verify Setup

```bash
# Backend health check
curl http://localhost:8000/health

# Frontend
open http://localhost:3000

# API docs
open http://localhost:8000/docs
```

---

## Local Development Setup (Without Docker)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with local PostgreSQL and Redis URLs

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Set up environment
cp .env.example .env.local
# Edit VITE_API_URL if needed

# Start development server
npm run dev
```

### Database Setup (Local PostgreSQL)

```bash
# Install PostgreSQL 14+ and TimescaleDB extension

# Create database
createdb farmfactory

# Enable extensions
psql farmfactory -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"
psql farmfactory -c "CREATE EXTENSION IF NOT EXISTS postgis;"
psql farmfactory -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
```

### Redis Setup

```bash
# Install Redis
# Ubuntu: sudo apt install redis-server
# macOS: brew install redis

# Start Redis
redis-server
```

---

## Project Structure

```
FarmFactory/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/v1/            # API routes
│   │   │   └── endpoints/     # Endpoint handlers
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   ├── tasks/             # Celery tasks
│   │   ├── utils/             # Utilities
│   │   ├── config.py          # Configuration
│   │   ├── database.py        # Database setup
│   │   └── main.py            # FastAPI app
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Test suite
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── common/
│   │   │   ├── farms/
│   │   │   ├── plots/
│   │   │   ├── dashboard/
│   │   │   └── analytics/
│   │   ├── pages/             # Page components
│   │   ├── services/          # API client
│   │   ├── hooks/             # Custom hooks
│   │   ├── types/             # TypeScript types
│   │   ├── utils/             # Utilities
│   │   └── App.tsx
│   ├── tests/
│   ├── package.json
│   └── Dockerfile.dev
│
├── docs/                       # Documentation
├── templates/                  # CSV templates
├── scripts/                    # Utility scripts
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Edit code, add features, fix bugs...

### 3. Write Tests

```bash
# Backend tests
cd backend
pytest tests/unit/test_your_feature.py

# Frontend tests
cd frontend
npm test
```

### 4. Run Linters

```bash
# Backend
cd backend
black app/ tests/
flake8 app/ tests/

# Frontend
cd frontend
npm run lint
npm run format
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat(farms): add irrigation efficiency calculation"
```

Follow [Conventional Commits](https://www.conventionalcommits.org/) format.

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
# Create Pull Request on GitHub
```

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for detailed contribution guidelines.

---

## Key Technologies

### Backend Stack

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **Celery** - Task queue
- **Redis** - Caching and message broker
- **pytest** - Testing framework

### Frontend Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router** - Routing
- **React Query** - Data fetching
- **Material-UI** - Component library
- **Recharts** - Charts
- **Vitest** - Testing framework

### Database

- **PostgreSQL 14+** - Primary database
- **TimescaleDB** - Time-series extension
- **PostGIS** - Spatial data support

---

## Common Development Tasks

### Running Migrations

```bash
# Create migration
alembic revision --autogenerate -m "add irrigation table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Running Tests

```bash
# Backend - all tests
pytest

# Backend - specific test
pytest tests/unit/test_farms.py::test_create_farm

# Backend - with coverage
pytest --cov=app --cov-report=html

# Frontend - all tests
npm test

# Frontend - watch mode
npm run test:watch
```

### Debugging

#### Backend Debugging

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use IDE debugger
# VS Code: Set breakpoint, press F5
```

#### Frontend Debugging

```typescript
// Browser DevTools
debugger;

// Console logging
console.log('Debug:', { data });

// React DevTools (browser extension)
```

### Database Access

```bash
# Using Docker
docker-compose exec postgres psql -U farm_user -d farmfactory

# List tables
\dt

# Describe table
\d farms

# Query data
SELECT * FROM farms LIMIT 10;
```

---

## API Development

### Creating a New Endpoint

1. **Define Pydantic Schema** (`app/schemas/`)

```python
# app/schemas/irrigation.py
from pydantic import BaseModel
from datetime import datetime

class IrrigationCreate(BaseModel):
    plot_id: UUID
    time: datetime
    method: str
    duration_minutes: int
    water_volume_liters: float
```

2. **Create Database Model** (`app/models/`)

```python
# app/models/irrigation.py
from sqlalchemy import Column, DateTime, Integer, Float
from app.database import Base

class Irrigation(Base):
    __tablename__ = "irrigation_events"
    # ... columns
```

3. **Implement Service Logic** (`app/services/`)

```python
# app/services/irrigation_service.py
def create_irrigation_event(db: Session, data: IrrigationCreate):
    event = Irrigation(**data.dict())
    db.add(event)
    db.commit()
    return event
```

4. **Create API Endpoint** (`app/api/v1/endpoints/`)

```python
# app/api/v1/endpoints/irrigation.py
from fastapi import APIRouter, Depends

router = APIRouter()

@router.post("/irrigation", response_model=IrrigationInDB)
def create_irrigation(
    data: IrrigationCreate,
    db: Session = Depends(get_db)
):
    return irrigation_service.create_irrigation_event(db, data)
```

5. **Add Tests**

```python
# tests/unit/test_irrigation.py
def test_create_irrigation(db_session):
    data = IrrigationCreate(...)
    result = create_irrigation_event(db_session, data)
    assert result.id is not None
```

---

## Environment Variables

Key environment variables (see `.env.example`):

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/farmfactory

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:3000

# File Upload
MAX_UPLOAD_SIZE_MB=100
UPLOAD_DIR=/app/uploads

# Email (for alerts)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## Additional Resources

- [Architecture Overview](./architecture.md)
- [Backend Development Guide](./backend.md)
- [Frontend Development Guide](./frontend.md)
- [Database Schema](./database.md)
- [Testing Guide](./testing.md)
- [Deployment Guide](./deployment.md)

---

## Getting Help

- **GitHub Issues**: [Report bugs](https://github.com/YOUR_ORG/FarmFactory/issues)
- **Discussions**: [Ask questions](https://github.com/YOUR_ORG/FarmFactory/discussions)
- **Contributing**: See [CONTRIBUTING.md](../../CONTRIBUTING.md)

---

**Last Updated**: 2025-11-16
**Version**: 1.0.0
