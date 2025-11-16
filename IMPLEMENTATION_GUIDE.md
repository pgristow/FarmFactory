# FarmFactory Implementation Guide

## Quick Start for Development

This guide provides step-by-step instructions to implement the FarmFactory system based on the detailed plan.

---

## Phase 1: Foundation Setup (Week 1-2)

### Step 1.1: Project Structure Setup

Create the basic directory structure:

```bash
# Create backend structure
mkdir -p backend/app/{api/v1/endpoints,models,schemas,services,tasks,utils}
mkdir -p backend/alembic/versions
mkdir -p backend/tests/{unit,integration}

# Create frontend structure
mkdir -p frontend/src/{components/{common,farms,plots,dashboard,import,analytics},pages,services,hooks,types,utils}
mkdir -p frontend/public

# Create shared directories
mkdir -p templates/csv
mkdir -p docs/{api,user-guide,developer}
mkdir -p scripts
```

### Step 1.2: Backend Dependencies

Create `backend/requirements.txt`:

```txt
# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
asyncpg==0.29.0

# Time-series
# Note: Install timescaledb on PostgreSQL server

# Data Processing
pandas==2.1.3
openpyxl==3.1.2
numpy==1.26.2
scikit-learn==1.3.2

# Async & Tasks
celery==5.3.4
redis==5.0.1

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0

# Validation
pydantic==2.5.0
pydantic-settings==2.1.0
email-validator==2.1.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
pytest-cov==4.1.0

# Utilities
python-dateutil==2.8.2
pytz==2023.3
```

Install dependencies:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 1.3: Frontend Dependencies

Create `frontend/package.json`:

```json
{
  "name": "farmfactory-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx",
    "test": "vitest"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@tanstack/react-query": "^5.12.0",
    "axios": "^1.6.2",
    "recharts": "^2.10.3",
    "react-leaflet": "^4.2.1",
    "leaflet": "^1.9.4",
    "date-fns": "^2.30.0",
    "@mui/material": "^5.14.20",
    "@mui/icons-material": "^5.14.19",
    "@emotion/react": "^11.11.1",
    "@emotion/styled": "^11.11.0",
    "ag-grid-react": "^31.0.0",
    "ag-grid-community": "^31.0.0",
    "react-dropzone": "^14.2.3",
    "zustand": "^4.4.7"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@types/leaflet": "^1.9.8",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.7",
    "eslint": "^8.55.0",
    "@typescript-eslint/eslint-plugin": "^6.14.0",
    "@typescript-eslint/parser": "^6.14.0",
    "vitest": "^1.0.4"
  }
}
```

Install dependencies:

```bash
cd frontend
npm install
```

### Step 1.4: Docker Configuration

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: timescale/timescaledb:latest-pg14
    container_name: farmfactory_db
    environment:
      POSTGRES_DB: farmfactory
      POSTGRES_USER: farm_user
      POSTGRES_PASSWORD: ${DB_PASSWORD:-farmpass123}
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U farm_user -d farmfactory"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: farmfactory_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: farmfactory_backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app
      - upload_data:/app/uploads
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://farm_user:${DB_PASSWORD:-farmpass123}@postgres:5432/farmfactory
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY:-dev-secret-key-change-in-production}
      ENVIRONMENT: development
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: farmfactory_celery
    command: celery -A app.tasks.celery_app worker --loglevel=info
    volumes:
      - ./backend:/app
      - upload_data:/app/uploads
    environment:
      DATABASE_URL: postgresql://farm_user:${DB_PASSWORD:-farmpass123}@postgres:5432/farmfactory
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY:-dev-secret-key-change-in-production}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: farmfactory_frontend
    command: npm run dev -- --host
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  upload_data:

networks:
  default:
    name: farmfactory_network
```

Create `.env.example`:

```bash
# Database
DB_PASSWORD=farmpass123

# Backend
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Email (for alerts)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL_FROM=noreply@farmfactory.com

# File Upload
MAX_UPLOAD_SIZE_MB=100
UPLOAD_DIR=/app/uploads

# Environment
ENVIRONMENT=development
DEBUG=true
```

### Step 1.5: Backend Core Files

Create `backend/app/config.py`:

```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 100
    UPLOAD_DIR: str = "/app/uploads"

    # Email
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    ALERT_EMAIL_FROM: str = ""

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
```

Create `backend/app/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Create `backend/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api.v1 import router as api_router

app = FastAPI(
    title="FarmFactory API",
    description="Farm Optimization System API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "FarmFactory API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Step 1.6: Database Initialization

Create `scripts/init-db.sql`:

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- Create initial database schema will be handled by Alembic migrations
```

Create `backend/alembic.ini`:

```ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

sqlalchemy.url = postgresql://farm_user:farmpass123@localhost:5432/farmfactory

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
```

Create `backend/alembic/env.py`:

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import Base
from app.models import *  # Import all models
from app.config import settings

config = context.config

# Override sqlalchemy.url from environment
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Step 1.7: Frontend Core Files

Create `frontend/vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 3000,
    watch: {
      usePolling: true
    }
  }
})
```

Create `frontend/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

Create `frontend/src/main.tsx`:

```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

Create `frontend/src/App.tsx`:

```typescript
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'

const queryClient = new QueryClient()

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2e7d32', // Green for agriculture
    },
    secondary: {
      main: '#1976d2',
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <div className="App">
            <h1>FarmFactory</h1>
            <p>Farm Optimization System</p>
            {/* Routes will be added here */}
          </div>
        </Router>
      </ThemeProvider>
    </QueryClient Provider>
  )
}

export default App
```

---

## Phase 2: Database Models (Week 2)

### Step 2.1: Create Base Models

Create `backend/app/models/base.py`:

```python
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
from app.database import Base

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Step 2.2: Create Farm Models

See the detailed schema in `FARM_OPTIMIZATION_PLAN.md` Section 2.

Create models in:
- `backend/app/models/farm.py`
- `backend/app/models/plot.py`
- `backend/app/models/soil.py`
- `backend/app/models/crop.py`
- `backend/app/models/planting.py`
- `backend/app/models/irrigation.py`
- `backend/app/models/nutrient.py`
- `backend/app/models/water_quality.py`
- `backend/app/models/environmental.py`
- `backend/app/models/financial.py`
- `backend/app/models/alert.py`

### Step 2.3: Create Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

---

## Phase 3: API Development (Week 3-4)

### Step 3.1: Create Pydantic Schemas

Create validation schemas for all models in `backend/app/schemas/`.

Example `backend/app/schemas/farm.py`:

```python
from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

class FarmBase(BaseModel):
    name: str
    address: Optional[str] = None
    total_area_hectares: Optional[float] = None
    timezone: Optional[str] = "UTC"

class FarmCreate(FarmBase):
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class FarmUpdate(FarmBase):
    name: Optional[str] = None

class FarmInDB(FarmBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
```

### Step 3.2: Create API Endpoints

See `FARM_OPTIMIZATION_PLAN.md` Section 4 for complete API design.

Create endpoints in `backend/app/api/v1/endpoints/`.

### Step 3.3: Create Service Layer

Implement business logic in `backend/app/services/`.

---

## Phase 4-7: Continue with Plan

Follow the detailed implementation steps in `FARM_OPTIMIZATION_PLAN.md` for:

- Phase 4: Data Import System
- Phase 5: Dashboard Development
- Phase 6: Analytics & Alerts
- Phase 7: Testing & Deployment

---

## Quick Commands Reference

### Start Development Environment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

### Database Operations

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U farm_user -d farmfactory

# Create migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Rollback migration
docker-compose exec backend alembic downgrade -1
```

### Testing

```bash
# Backend tests
docker-compose exec backend pytest

# Frontend tests
docker-compose exec frontend npm test
```

### Code Quality

```bash
# Backend linting
docker-compose exec backend flake8 app/

# Frontend linting
docker-compose exec frontend npm run lint
```

---

## Next Steps

1. Review this implementation guide
2. Set up your local development environment
3. Follow Phase 1 steps to create the foundation
4. Proceed with subsequent phases as outlined in the main plan

For detailed architecture and feature specifications, refer to `FARM_OPTIMIZATION_PLAN.md`.
