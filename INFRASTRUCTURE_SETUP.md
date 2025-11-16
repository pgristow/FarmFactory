# FarmFactory Infrastructure Setup - Complete Guide

## Overview

This document provides a complete guide for the DevOps infrastructure that has been set up for the FarmFactory project.

## Files Created

### Core Docker Files
1. **docker-compose.yml** - Development environment configuration
2. **docker-compose.prod.yml** - Production environment configuration
3. **backend/Dockerfile** - Multi-stage Dockerfile for FastAPI application
4. **frontend/Dockerfile.dev** - Development Dockerfile for React
5. **frontend/Dockerfile.prod** - Production Dockerfile for React with Nginx
6. **frontend/nginx.conf** - Nginx configuration for serving React app

### Database & Scripts
7. **scripts/init-db.sql** - PostgreSQL initialization script with extensions
8. **.env.example** - Environment variables template (comprehensive)

### Automation & Tools
9. **Makefile** - 50+ commands for development workflows
10. **.dockerignore** - Docker build optimization

### Monitoring Stack
11. **monitoring/docker-compose.monitoring.yml** - Prometheus + Grafana setup
12. **monitoring/prometheus/prometheus.yml** - Prometheus configuration
13. **monitoring/prometheus/alerts.yml** - Alert rules
14. **monitoring/alertmanager/config.yml** - Alert routing configuration
15. **monitoring/grafana/provisioning/datasources/datasource.yml** - Grafana datasource
16. **monitoring/grafana/provisioning/dashboards/dashboard.yml** - Dashboard provisioning

### Documentation
17. **README.md** - Complete project documentation with quick start guide

---

## Quick Start Instructions

### Prerequisites

Ensure you have installed:
- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- Make (optional but recommended)
- At least 4GB RAM available
- Ports available: 3000, 8000, 5432, 6379

### Step 1: Initial Setup

```bash
# Navigate to project directory
cd /home/user/FarmFactory

# Create environment file
cp .env.example .env

# (Optional) Edit .env file with your preferences
nano .env
```

### Step 2: Start Development Environment

**Option A: Using Makefile (Recommended)**

```bash
# Initialize and start everything
make init
```

This single command will:
- Create `.env` from template if not exists
- Build all Docker images
- Start all services (PostgreSQL, Redis, Backend, Celery, Frontend)
- Wait for services to be healthy
- Run database migrations
- Show access URLs

**Option B: Manual Docker Compose**

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Wait for services to start (about 10-15 seconds)
sleep 15

# Run migrations
docker-compose exec backend alembic upgrade head
```

### Step 3: Verify Installation

```bash
# Check service status
make status

# Or manually
docker-compose ps

# Check health
make health
```

### Step 4: Access the Application

Once all services are running:

- **Frontend (React)**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **API Documentation (ReDoc)**: http://localhost:8000/redoc

---

## Architecture Overview

### Services in Development Environment

| Service | Container Name | Port | Description |
|---------|----------------|------|-------------|
| PostgreSQL | farmfactory_db | 5432 | TimescaleDB + PostGIS database |
| Redis | farmfactory_redis | 6379 | Cache and message broker |
| Backend | farmfactory_backend | 8000 | FastAPI application |
| Celery Worker | farmfactory_celery_worker | - | Async task processor |
| Celery Beat | farmfactory_celery_beat | - | Periodic task scheduler |
| Frontend | farmfactory_frontend | 3000 | React development server |

### Key Features

#### Docker Compose (Development)
- Health checks for all services
- Automatic service dependencies
- Volume persistence for data
- Hot-reload for backend and frontend
- Isolated network

#### Backend Dockerfile
- Multi-stage build (development & production targets)
- Python 3.11-slim base
- System dependencies (gcc, postgresql-client)
- Development tools in dev stage
- Non-root user in production
- Health check endpoint

#### Database Initialization
- UUID extension
- PostGIS for spatial data
- TimescaleDB for time-series data
- Custom types (alert_severity, planting_status, irrigation_method)
- Helper functions
- Proper permissions

#### Environment Configuration
- 80+ environment variables documented
- Separate sections for each component
- Production settings commented out
- Feature flags
- Performance tuning options

---

## Development Workflow

### Daily Development

```bash
# Start the day
make up

# View logs
make logs

# View specific service logs
make logs-backend
make logs-frontend

# Run tests
make test

# Stop at end of day
make down
```

### Database Operations

```bash
# Create a migration after model changes
make migrate-create name="add_new_field"

# Run migrations
make migrate

# Access database shell
make db-shell

# Create backup
make backup

# View migration history
make migrate-history
```

### Code Quality

```bash
# Run linting
make lint

# Format code
make format

# Type checking
make type-check
```

### Debugging

```bash
# Access Python shell
make shell

# Access backend container bash
make backend-shell

# Access Redis CLI
make redis-shell

# View resource usage
make stats
```

---

## Production Deployment

### Pre-deployment Checklist

1. **Update `.env.production`**:
   ```bash
   # Copy template
   cp .env.example .env.production

   # Edit with production values
   nano .env.production
   ```

2. **Critical Production Settings**:
   ```bash
   ENVIRONMENT=production
   DEBUG=false

   # Generate secure secret key
   SECRET_KEY=$(openssl rand -hex 32)

   # Use strong passwords
   POSTGRES_PASSWORD=<strong-password>
   REDIS_PASSWORD=<strong-password>

   # Update CORS
   ALLOWED_ORIGINS=https://yourdomain.com

   # Configure real SMTP
   SMTP_HOST=smtp.yourprovider.com
   SMTP_USER=your-email@domain.com
   SMTP_PASSWORD=your-password
   ```

3. **SSL Certificates** (if using HTTPS):
   - Place SSL certificates in appropriate directory
   - Update Nginx configuration if needed

### Deploy to Production

```bash
# Build and deploy
make prod-deploy

# Or manually
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
make prod-logs
```

### Production Features

- **Optimized Images**: Multi-stage builds, minimal size
- **Security**: Non-root users, no debug mode
- **Performance**: Multiple Uvicorn workers, connection pooling
- **Reliability**: Health checks, restart policies
- **Resource Limits**: CPU and memory constraints
- **Monitoring**: Ready for Prometheus integration

---

## Monitoring Setup

### Start Monitoring Stack

```bash
# Start Prometheus + Grafana
make monitoring-up
```

This starts:
- **Prometheus** (port 9090): Metrics collection
- **Grafana** (port 3001): Dashboards and visualization
- **Node Exporter** (port 9100): System metrics
- **PostgreSQL Exporter** (port 9187): Database metrics
- **Redis Exporter** (port 9121): Cache metrics
- **cAdvisor** (port 8080): Container metrics
- **AlertManager** (port 9093): Alert routing

### Access Monitoring

- **Grafana**: http://localhost:3001
  - Username: `admin`
  - Password: `admin123` (change in `.env`)

- **Prometheus**: http://localhost:9090

### Default Alerts Configured

1. **Service Health**:
   - Service down for >1 minute

2. **Database**:
   - PostgreSQL down
   - High connection count (>80)
   - Slow queries

3. **Redis**:
   - Redis down
   - High memory usage (>90%)

4. **System Resources**:
   - High CPU usage (>80%)
   - High memory usage (>90%)
   - High disk usage (>85%)

5. **Containers**:
   - Container high CPU (>80%)
   - Container high memory (>90%)

### Alert Routing

Alerts are sent via:
- Email (critical and warning)
- Webhook (all alerts)
- Slack (commented out, ready to enable)

---

## Makefile Commands Reference

### General
- `make help` - Display all available commands
- `make up` - Start development environment
- `make down` - Stop all services
- `make restart` - Restart all services
- `make build` - Build/rebuild services
- `make status` - Show service status

### Logs
- `make logs` - Tail all logs
- `make logs-backend` - Backend logs only
- `make logs-frontend` - Frontend logs only
- `make logs-celery` - Celery worker logs
- `make logs-db` - PostgreSQL logs

### Database
- `make migrate` - Run migrations
- `make migrate-create name="desc"` - Create migration
- `make migrate-down` - Rollback migration
- `make db-shell` - PostgreSQL shell
- `make db-reset` - Reset database (destroys data!)
- `make backup` - Create database backup
- `make restore file=backup.sql` - Restore backup

### Testing
- `make test` - Run all tests
- `make test-backend` - Backend tests with coverage
- `make test-frontend` - Frontend tests
- `make test-watch` - Tests in watch mode

### Code Quality
- `make lint` - Run linting
- `make format` - Format code
- `make type-check` - Type checking

### Shell Access
- `make shell` - Python shell
- `make backend-shell` - Backend bash
- `make frontend-shell` - Frontend shell
- `make redis-shell` - Redis CLI

### Monitoring
- `make monitoring-up` - Start monitoring stack
- `make monitoring-down` - Stop monitoring
- `make health` - Check service health
- `make stats` - Resource usage

### Production
- `make prod-up` - Start production
- `make prod-down` - Stop production
- `make prod-deploy` - Build and deploy
- `make prod-logs` - Production logs

### Cleanup
- `make clean` - Remove everything
- `make clean-volumes` - Remove volumes (data!)
- `make prune` - Clean unused resources

### Utilities
- `make init` - First-time setup
- `make seed` - Seed sample data
- `make celery-flower` - Start Celery monitoring

---

## Troubleshooting

### Services Won't Start

```bash
# Check what's running
docker-compose ps

# Check logs for errors
docker-compose logs

# Restart specific service
docker-compose restart backend

# Rebuild if needed
docker-compose up -d --build backend
```

### Database Connection Errors

```bash
# Check if PostgreSQL is ready
docker-compose exec postgres pg_isready -U farm_user

# Check if extensions are loaded
docker-compose exec postgres psql -U farm_user -d farmfactory -c "SELECT * FROM pg_extension;"

# Reset database (WARNING: destroys data)
make db-reset
```

### Port Already in Use

Edit `.env` file:
```bash
FRONTEND_PORT=3001
BACKEND_PORT=8001
POSTGRES_PORT=5433
REDIS_PORT=6380
```

### Out of Memory

Increase Docker memory:
- Docker Desktop: Settings → Resources → Memory (increase to 6GB+)
- Linux: Ensure sufficient system memory

Or reduce resource usage:
```bash
# Reduce Celery workers
CELERY_CONCURRENCY=2

# Reduce database pool
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
```

### Permission Errors

```bash
# Fix ownership (Linux/Mac)
sudo chown -R $USER:$USER .

# Fix uploads directory
docker-compose exec backend mkdir -p /app/uploads
docker-compose exec backend chmod 777 /app/uploads
```

### Clear Everything and Start Fresh

```bash
# Stop and remove everything
make clean

# Reinitialize
make init
```

---

## Security Best Practices

### Development
- Don't commit `.env` file
- Use default passwords only in development
- Keep Docker images updated

### Production
1. **Use strong passwords** for all services
2. **Generate unique SECRET_KEY**: `openssl rand -hex 32`
3. **Enable HTTPS** with SSL certificates
4. **Restrict CORS** to your domain only
5. **Set DEBUG=false**
6. **Use environment variables** for secrets
7. **Regular backups** of database
8. **Update dependencies** regularly
9. **Monitor logs** for suspicious activity
10. **Limit exposed ports** (use firewall)

---

## Performance Tuning

### Database
```bash
# Increase connection pool
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# PostgreSQL tuning (in docker-compose)
- shared_buffers=256MB
- effective_cache_size=1GB
```

### Backend
```bash
# More Uvicorn workers (in production)
--workers 4  # (2 x CPU cores) + 1

# More Celery workers
CELERY_CONCURRENCY=8
```

### Redis
```bash
# Increase max memory
maxmemory 512mb
maxmemory-policy allkeys-lru
```

### Frontend
- Enable gzip compression (already in nginx.conf)
- Use CDN for static assets (production)
- Lazy load components
- Implement code splitting

---

## Backup Strategy

### Automated Backups

Create a cron job:
```bash
# Daily backup at 2 AM
0 2 * * * cd /path/to/FarmFactory && make backup
```

### Manual Backup

```bash
# Create backup
make backup

# Files are saved to ./backups/
# farmfactory_backup_YYYYMMDD_HHMMSS.sql
```

### Restore

```bash
make restore file=farmfactory_backup_20240101_120000.sql
```

### Backup Retention

Set in `.env`:
```bash
BACKUP_RETENTION_DAYS=30
```

---

## Next Steps

1. **Review Environment Variables**: Update `.env` with your specific configuration
2. **Start Development**: Run `make init` to begin
3. **Implement Backend Models**: See `IMPLEMENTATION_GUIDE.md`
4. **Create API Endpoints**: Follow the REST API design in planning docs
5. **Build Frontend Components**: Start with dashboard layout
6. **Configure Monitoring**: Customize Grafana dashboards
7. **Set Up CI/CD**: Add GitHub Actions or GitLab CI
8. **Production Deployment**: Follow production checklist above

---

## Support & Resources

- **Planning Document**: `FARM_OPTIMIZATION_PLAN.md`
- **Implementation Guide**: `IMPLEMENTATION_GUIDE.md`
- **API Documentation**: http://localhost:8000/docs (when running)
- **Make Help**: `make help`

---

## Summary

You now have a complete, production-ready infrastructure for FarmFactory with:

✅ Docker Compose for development and production
✅ Multi-stage Dockerfiles optimized for each service
✅ PostgreSQL with TimescaleDB and PostGIS
✅ Redis for caching and task queue
✅ Celery for background processing
✅ Complete monitoring stack with Prometheus and Grafana
✅ Comprehensive Makefile with 50+ commands
✅ Environment configuration with 80+ documented variables
✅ Health checks and auto-restart policies
✅ Database initialization and migrations
✅ Backup and restore capabilities
✅ Production deployment configuration
✅ Security best practices
✅ Performance tuning options

**Ready to start developing!** Run `make init` to begin.

---

**Last Updated**: 2025-11-16
**Version**: 1.0
**Status**: Ready for Development
