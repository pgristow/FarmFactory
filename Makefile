.PHONY: help up down restart logs logs-backend logs-frontend logs-celery build clean test migrate shell db-shell redis-shell backup restore

# Default target
.DEFAULT_GOAL := help

# Load environment variables
include .env
export

# Colors for output
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ General

help: ## Display this help message
	@echo "$(CYAN)FarmFactory - Farm Optimization System$(NC)"
	@echo "$(CYAN)========================================$(NC)"
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make $(CYAN)<target>$(NC)\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(CYAN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

up: ## Start all services in development mode
	@echo "$(GREEN)Starting FarmFactory development environment...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Services started!$(NC)"
	@echo "$(CYAN)Frontend:$(NC) http://localhost:3000"
	@echo "$(CYAN)Backend API:$(NC) http://localhost:8000"
	@echo "$(CYAN)API Docs:$(NC) http://localhost:8000/docs"

down: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	docker-compose down

restart: ## Restart all services
	@echo "$(YELLOW)Restarting all services...$(NC)"
	docker-compose restart

stop: ## Stop all services without removing containers
	@echo "$(YELLOW)Stopping all services...$(NC)"
	docker-compose stop

start: ## Start stopped services
	@echo "$(GREEN)Starting services...$(NC)"
	docker-compose start

build: ## Build or rebuild services
	@echo "$(CYAN)Building services...$(NC)"
	docker-compose build

rebuild: ## Force rebuild all services without cache
	@echo "$(CYAN)Rebuilding all services from scratch...$(NC)"
	docker-compose build --no-cache

##@ Logs

logs: ## Tail logs from all services
	docker-compose logs -f

logs-backend: ## Tail logs from backend service
	docker-compose logs -f backend

logs-frontend: ## Tail logs from frontend service
	docker-compose logs -f frontend

logs-celery: ## Tail logs from Celery worker
	docker-compose logs -f celery_worker

logs-db: ## Tail logs from PostgreSQL
	docker-compose logs -f postgres

logs-redis: ## Tail logs from Redis
	docker-compose logs -f redis

##@ Database

migrate: ## Run database migrations
	@echo "$(CYAN)Running database migrations...$(NC)"
	docker-compose exec backend alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create name="description")
	@echo "$(CYAN)Creating new migration: $(name)$(NC)"
	docker-compose exec backend alembic revision --autogenerate -m "$(name)"

migrate-down: ## Rollback last migration
	@echo "$(YELLOW)Rolling back last migration...$(NC)"
	docker-compose exec backend alembic downgrade -1

migrate-history: ## Show migration history
	docker-compose exec backend alembic history

db-shell: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

db-reset: ## Reset database (WARNING: destroys all data)
	@echo "$(RED)WARNING: This will destroy all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		docker-compose up -d postgres; \
		sleep 5; \
		docker-compose exec backend alembic upgrade head; \
		echo "$(GREEN)Database reset complete!$(NC)"; \
	fi

##@ Testing

test: ## Run all tests
	@echo "$(CYAN)Running tests...$(NC)"
	docker-compose exec backend pytest

test-backend: ## Run backend tests with coverage
	@echo "$(CYAN)Running backend tests with coverage...$(NC)"
	docker-compose exec backend pytest --cov=app --cov-report=html --cov-report=term

test-frontend: ## Run frontend tests
	@echo "$(CYAN)Running frontend tests...$(NC)"
	docker-compose exec frontend npm test

test-watch: ## Run backend tests in watch mode
	docker-compose exec backend pytest --watch

##@ Code Quality

lint: ## Run linting on all code
	@echo "$(CYAN)Linting backend...$(NC)"
	docker-compose exec backend flake8 app/
	@echo "$(CYAN)Linting frontend...$(NC)"
	docker-compose exec frontend npm run lint

format: ## Format backend code with black
	@echo "$(CYAN)Formatting backend code...$(NC)"
	docker-compose exec backend black app/

type-check: ## Run type checking
	@echo "$(CYAN)Running type checks...$(NC)"
	docker-compose exec backend mypy app/

##@ Shell Access

shell: ## Open Python shell in backend container
	docker-compose exec backend python

backend-shell: ## Open bash shell in backend container
	docker-compose exec backend /bin/bash

frontend-shell: ## Open shell in frontend container
	docker-compose exec frontend /bin/sh

redis-shell: ## Open Redis CLI
	docker-compose exec redis redis-cli -a $(REDIS_PASSWORD)

##@ Monitoring

status: ## Show status of all services
	@echo "$(CYAN)Service Status:$(NC)"
	@docker-compose ps

stats: ## Show resource usage statistics
	docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

health: ## Check health of all services
	@echo "$(CYAN)Checking service health...$(NC)"
	@curl -s http://localhost:8000/health | python -m json.tool || echo "$(RED)Backend unhealthy$(NC)"
	@curl -s http://localhost:3000 > /dev/null && echo "$(GREEN)Frontend healthy$(NC)" || echo "$(RED)Frontend unhealthy$(NC)"

##@ Backup & Restore

backup: ## Backup database
	@echo "$(CYAN)Creating database backup...$(NC)"
	@mkdir -p ./backups
	@docker-compose exec -T postgres pg_dump -U $(POSTGRES_USER) $(POSTGRES_DB) > ./backups/farmfactory_backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Backup created in ./backups/$(NC)"

restore: ## Restore database from latest backup (usage: make restore file=backup.sql)
	@echo "$(YELLOW)Restoring database from $(file)...$(NC)"
	@docker-compose exec -T postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) < ./backups/$(file)
	@echo "$(GREEN)Database restored!$(NC)"

##@ Production

prod-up: ## Start production environment
	@echo "$(GREEN)Starting production environment...$(NC)"
	docker-compose -f docker-compose.prod.yml up -d

prod-down: ## Stop production environment
	@echo "$(YELLOW)Stopping production environment...$(NC)"
	docker-compose -f docker-compose.prod.yml down

prod-logs: ## View production logs
	docker-compose -f docker-compose.prod.yml logs -f

prod-deploy: ## Deploy to production (build and start)
	@echo "$(CYAN)Deploying to production...$(NC)"
	docker-compose -f docker-compose.prod.yml build
	docker-compose -f docker-compose.prod.yml up -d
	@echo "$(GREEN)Production deployment complete!$(NC)"

##@ Monitoring Stack

monitoring-up: ## Start monitoring stack (Prometheus + Grafana)
	@echo "$(GREEN)Starting monitoring stack...$(NC)"
	docker-compose -f monitoring/docker-compose.monitoring.yml up -d
	@echo "$(GREEN)Monitoring services started!$(NC)"
	@echo "$(CYAN)Grafana:$(NC) http://localhost:3001 (admin/admin123)"
	@echo "$(CYAN)Prometheus:$(NC) http://localhost:9090"

monitoring-down: ## Stop monitoring stack
	docker-compose -f monitoring/docker-compose.monitoring.yml down

##@ Cleanup

clean: ## Remove all containers, volumes, and images
	@echo "$(RED)WARNING: This will remove all containers, volumes, and images!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v --rmi all; \
		echo "$(GREEN)Cleanup complete!$(NC)"; \
	fi

clean-volumes: ## Remove all volumes (WARNING: destroys all data)
	@echo "$(RED)WARNING: This will destroy all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		echo "$(GREEN)Volumes removed!$(NC)"; \
	fi

clean-images: ## Remove all images
	docker-compose down --rmi all

prune: ## Remove unused Docker resources
	@echo "$(YELLOW)Pruning unused Docker resources...$(NC)"
	docker system prune -f
	@echo "$(GREEN)Prune complete!$(NC)"

##@ Utilities

seed: ## Seed database with sample data
	@echo "$(CYAN)Seeding database with sample data...$(NC)"
	docker-compose exec backend python -m app.scripts.seed_data

install-backend: ## Install backend dependencies
	docker-compose exec backend pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	docker-compose exec frontend npm install

requirements: ## Update Python requirements
	docker-compose exec backend pip freeze > requirements.txt

npm-update: ## Update npm packages
	docker-compose exec frontend npm update

##@ Celery & Task Management

celery-status: ## Check Celery worker status
	@echo "$(CYAN)Celery Worker Status:$(NC)"
	docker-compose exec celery_worker celery -A app.tasks.celery_app inspect active

celery-stats: ## Show Celery worker statistics
	@echo "$(CYAN)Celery Worker Statistics:$(NC)"
	docker-compose exec celery_worker celery -A app.tasks.celery_app inspect stats

celery-tasks: ## List registered Celery tasks
	@echo "$(CYAN)Registered Celery Tasks:$(NC)"
	docker-compose exec celery_worker celery -A app.tasks.celery_app inspect registered

celery-queues: ## Show Celery queue status
	@echo "$(CYAN)Celery Queue Status:$(NC)"
	docker-compose exec celery_worker celery -A app.tasks.celery_app inspect active_queues

celery-purge: ## Purge all tasks from queues (WARNING: removes all pending tasks)
	@echo "$(RED)WARNING: This will remove all pending tasks!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose exec celery_worker celery -A app.tasks.celery_app purge -f; \
		echo "$(GREEN)All tasks purged!$(NC)"; \
	fi

flower-open: ## Open Flower monitoring UI in browser
	@echo "$(CYAN)Opening Flower UI...$(NC)"
	@echo "$(CYAN)Flower:$(NC) http://localhost:5555"
	@echo "$(CYAN)Credentials:$(NC) admin / admin123"

logs-flower: ## Tail logs from Flower
	docker-compose logs -f flower

logs-beat: ## Tail logs from Celery beat scheduler
	docker-compose logs -f celery_beat

##@ Import & Storage

storage-stats: ## Show file storage statistics
	@echo "$(CYAN)File Storage Statistics:$(NC)"
	docker-compose exec backend python -c "from app.core.storage import storage_service; import json; print(json.dumps(storage_service.get_storage_stats(), indent=2))"

storage-cleanup: ## Clean up old upload files (>30 days)
	@echo "$(CYAN)Cleaning up old files...$(NC)"
	docker-compose exec backend python -c "from app.core.storage import storage_service; import json; print(json.dumps(storage_service.cleanup_old_files(), indent=2))"

backup-uploads: ## Backup upload files
	@echo "$(CYAN)Backing up upload files...$(NC)"
	@./scripts/backup-imports.sh

##@ Database Performance

db-tune: ## Apply TimescaleDB performance tuning
	@echo "$(CYAN)Applying TimescaleDB performance tuning...$(NC)"
	@docker-compose exec -T postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -f /scripts/tune-timescaledb.sql
	@echo "$(GREEN)TimescaleDB tuning applied!$(NC)"

db-stats: ## Show database statistics
	@echo "$(CYAN)Database Statistics:$(NC)"
	@docker-compose exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c "\
		SELECT schemaname, tablename, \
		       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size, \
		       n_tup_ins AS inserts, n_tup_upd AS updates, n_tup_del AS deletes \
		FROM pg_stat_user_tables ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 10;"

db-vacuum: ## Manual VACUUM ANALYZE
	@echo "$(CYAN)Running VACUUM ANALYZE...$(NC)"
	@docker-compose exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c "VACUUM ANALYZE;"
	@echo "$(GREEN)VACUUM ANALYZE complete!$(NC)"

db-reindex: ## Reindex all indexes
	@echo "$(CYAN)Reindexing database...$(NC)"
	@docker-compose exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c "REINDEX DATABASE $(POSTGRES_DB);"
	@echo "$(GREEN)Reindex complete!$(NC)"

db-bloat: ## Show table bloat statistics
	@echo "$(CYAN)Table Bloat Statistics:$(NC)"
	@docker-compose exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c "SELECT * FROM v_table_bloat;"

db-cache: ## Show cache hit ratio (should be >95%)
	@echo "$(CYAN)Cache Hit Ratio:$(NC)"
	@docker-compose exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c "SELECT * FROM v_cache_hit_ratio;"

db-connections: ## Show connection statistics
	@echo "$(CYAN)Connection Statistics:$(NC)"
	@docker-compose exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c "SELECT * FROM v_connection_stats;"

db-chunks: ## Show TimescaleDB chunk statistics
	@echo "$(CYAN)TimescaleDB Chunk Statistics:$(NC)"
	@docker-compose exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c "SELECT * FROM v_chunk_stats;"

db-compression: ## Show compression statistics and savings
	@echo "$(CYAN)Compression Statistics:$(NC)"
	@docker-compose exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c "SELECT * FROM v_compression_stats;"

db-performance: ## Show comprehensive performance report
	@echo "$(CYAN)Database Performance Report$(NC)"
	@echo "$(CYAN)=============================$(NC)"
	@docker-compose exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -f /scripts/performance-monitoring.sql

db-summary: ## Show quick performance summary
	@echo "$(CYAN)Quick Performance Summary:$(NC)"
	@docker-compose exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c "SELECT * FROM performance_summary();"

db-index-usage: ## Show index usage statistics
	@echo "$(CYAN)Index Usage Statistics:$(NC)"
	@docker-compose exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c "SELECT * FROM v_index_usage WHERE usage_status LIKE '%UNUSED%' OR usage_status = 'Low usage';"

db-apply-timescale-config: ## Apply TimescaleDB compression and retention policies
	@echo "$(CYAN)Applying TimescaleDB configuration...$(NC)"
	@docker-compose exec postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -f /infrastructure/database/timescaledb.conf
	@echo "$(GREEN)TimescaleDB configuration applied!$(NC)"

##@ Monitoring & Performance

monitoring-urls: ## Display monitoring service URLs
	@echo "$(CYAN)Monitoring Services:$(NC)"
	@echo "  Flower (Celery): http://localhost:5555 (admin/admin123)"
	@echo "  Grafana:         http://localhost:3001 (admin/admin123)"
	@echo "  Prometheus:      http://localhost:9090"
	@echo "  Backend API:     http://localhost:8000/docs"
	@echo "  PostgreSQL Exp:  http://localhost:9187/metrics"

init: ## Initialize project (first time setup)
	@echo "$(CYAN)Initializing FarmFactory...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Creating .env file from .env.example...$(NC)"; \
		cp .env.example .env; \
	fi
	@echo "$(GREEN)Building services...$(NC)"
	docker-compose build
	@echo "$(GREEN)Starting services...$(NC)"
	docker-compose up -d
	@echo "$(YELLOW)Waiting for database to be ready...$(NC)"
	@sleep 10
	@echo "$(GREEN)Running migrations...$(NC)"
	docker-compose exec backend alembic upgrade head
	@echo "$(GREEN)✓ FarmFactory is ready!$(NC)"
	@echo ""
	@echo "$(CYAN)Access the application:$(NC)"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend:  http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"
