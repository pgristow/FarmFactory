# FarmFactory - Quick Start Guide

## 1. First Time Setup (5 minutes)

```bash
# Clone repository (if not already done)
cd /home/user/FarmFactory

# Initialize everything
make init
```

That's it! The `make init` command will:
- Create `.env` file from template
- Build all Docker images (~2-3 minutes)
- Start all services
- Run database migrations
- Show you the access URLs

## 2. Access the Application

After `make init` completes, access:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 3. Essential Daily Commands

```bash
# Start services
make up

# View logs
make logs

# Stop services
make down

# Restart services
make restart

# See all available commands
make help
```

## 4. Database Commands

```bash
# Run migrations
make migrate

# Create new migration
make migrate-create name="your_description"

# Access database
make db-shell

# Backup database
make backup
```

## 5. Development Tools

```bash
# Run tests
make test

# Python shell
make shell

# Backend bash shell
make backend-shell

# Check service health
make health
```

## 6. Monitoring (Optional)

```bash
# Start monitoring stack
make monitoring-up

# Access Grafana: http://localhost:3001
# Username: admin
# Password: admin123
```

## 7. Troubleshooting

### Services won't start?
```bash
make down
make up
make logs
```

### Need fresh start?
```bash
make clean    # WARNING: Deletes all data!
make init     # Reinitialize
```

### Port conflicts?
Edit `.env` file and change ports:
```bash
FRONTEND_PORT=3001
BACKEND_PORT=8001
POSTGRES_PORT=5433
```

## 8. Production Deployment

```bash
# 1. Create production env file
cp .env.example .env.production

# 2. Edit with production values (IMPORTANT!)
nano .env.production

# 3. Deploy
make prod-deploy
```

## Common Issues

| Problem | Solution |
|---------|----------|
| Port already in use | Edit `.env` and change ports |
| Database won't connect | `make db-reset` (destroys data!) |
| Services unhealthy | `make down && make up` |
| Out of memory | Increase Docker memory to 6GB+ |
| Permission errors | `sudo chown -R $USER:$USER .` |

## File Structure

```
FarmFactory/
├── docker-compose.yml           # Dev environment
├── docker-compose.prod.yml      # Production environment
├── Makefile                     # All commands
├── .env.example                 # Config template
├── backend/
│   ├── Dockerfile              # Backend container
│   └── app/                    # FastAPI code
├── frontend/
│   ├── Dockerfile.dev          # Frontend dev container
│   ├── Dockerfile.prod         # Frontend prod container
│   └── src/                    # React code
├── scripts/
│   └── init-db.sql             # DB initialization
└── monitoring/                  # Prometheus + Grafana
```

## Help & Documentation

- **All commands**: `make help`
- **Full guide**: [INFRASTRUCTURE_SETUP.md](INFRASTRUCTURE_SETUP.md)
- **Deployment summary**: [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)
- **Planning docs**: [FARM_OPTIMIZATION_PLAN.md](FARM_OPTIMIZATION_PLAN.md)

## Quick Checklist

Before starting development:
- [ ] Run `make init`
- [ ] Verify all services: `make status`
- [ ] Check API docs: http://localhost:8000/docs
- [ ] Check frontend: http://localhost:3000
- [ ] Review `.env` file

Before production:
- [ ] Update all passwords in `.env.production`
- [ ] Generate new `SECRET_KEY`
- [ ] Set `DEBUG=false`
- [ ] Configure real SMTP
- [ ] Set up SSL certificates
- [ ] Enable monitoring
- [ ] Set up backups

---

**Need Help?** Run `make help` or check [INFRASTRUCTURE_SETUP.md](INFRASTRUCTURE_SETUP.md)

**Ready to start?** Run: `make init`
