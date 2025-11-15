# Makefile for Multilingual Education Content Pipeline
# Simplifies Docker and development commands

.PHONY: help build up down restart logs shell test clean

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Multilingual Education Content Pipeline - Docker Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ============================================
# Setup Commands
# ============================================

setup: ## Initial setup - copy .env.example to .env
	@echo "$(BLUE)Setting up environment...$(NC)"
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✓ Created .env file from .env.example$(NC)"; \
		echo "$(YELLOW)⚠ Please edit .env and add your API keys$(NC)"; \
	else \
		echo "$(YELLOW)⚠ .env file already exists$(NC)"; \
	fi

init: setup ## Initialize project (setup + create directories)
	@echo "$(BLUE)Initializing project...$(NC)"
	@mkdir -p data/audio data/cache data/curriculum logs
	@echo "$(GREEN)✓ Created data directories$(NC)"

# ============================================
# Docker Build Commands
# ============================================

build: ## Build all Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose build
	@echo "$(GREEN)✓ Build complete$(NC)"

build-no-cache: ## Build Docker images without cache
	@echo "$(BLUE)Building Docker images (no cache)...$(NC)"
	docker-compose build --no-cache
	@echo "$(GREEN)✓ Build complete$(NC)"

# ============================================
# Docker Run Commands
# ============================================

up: ## Start all services in detached mode
	@echo "$(BLUE)Starting services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo "$(YELLOW)Run 'make logs' to view logs$(NC)"

up-dev: ## Start services in development mode with hot-reload
	@echo "$(BLUE)Starting services in development mode...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "$(GREEN)✓ Development services started$(NC)"

up-prod: ## Start services in production mode
	@echo "$(BLUE)Starting services in production mode...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "$(GREEN)✓ Production services started$(NC)"

up-admin: ## Start services with PgAdmin
	@echo "$(BLUE)Starting services with PgAdmin...$(NC)"
	docker-compose --profile admin up -d
	@echo "$(GREEN)✓ Services started with PgAdmin at http://localhost:5050$(NC)"

down: ## Stop and remove all containers
	@echo "$(BLUE)Stopping services...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

down-v: ## Stop and remove all containers and volumes (⚠️ deletes data)
	@echo "$(RED)⚠️  WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		echo "$(GREEN)✓ Services and volumes removed$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

restart: ## Restart all services
	@echo "$(BLUE)Restarting services...$(NC)"
	docker-compose restart
	@echo "$(GREEN)✓ Services restarted$(NC)"

restart-api: ## Restart only the Flask API service
	@echo "$(BLUE)Restarting Flask API...$(NC)"
	docker-compose restart flask_api
	@echo "$(GREEN)✓ Flask API restarted$(NC)"

# ============================================
# Monitoring Commands
# ============================================

logs: ## View logs from all services
	docker-compose logs -f

logs-api: ## View logs from Flask API
	docker-compose logs -f flask_api

logs-db: ## View logs from PostgreSQL
	docker-compose logs -f postgres

ps: ## Show running containers
	docker-compose ps

stats: ## Show container resource usage
	docker stats

health: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@docker-compose ps
	@echo ""
	@echo "$(BLUE)API Health Check:$(NC)"
	@curl -s http://localhost:5000/health | python -m json.tool || echo "$(RED)✗ API not responding$(NC)"

# ============================================
# Shell Access Commands
# ============================================

shell: ## Open bash shell in Flask API container
	docker-compose exec flask_api bash

shell-db: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U postgres -d education_content

python: ## Open Python shell in Flask API container
	docker-compose exec flask_api python

# ============================================
# Testing Commands
# ============================================

test: ## Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	docker-compose exec flask_api pytest tests/ -v
	@echo "$(GREEN)✓ Tests complete$(NC)"

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	docker-compose exec flask_api pytest tests/ -v --cov=src --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/$(NC)"

test-speech: ## Run speech generator tests only
	docker-compose exec flask_api pytest tests/test_speech_generator.py -v

test-integration: ## Run integration tests only
	docker-compose exec flask_api pytest tests/test_speech_integration.py -v

# ============================================
# Database Commands
# ============================================

db-migrate: ## Run database migrations
	docker-compose exec flask_api alembic upgrade head

db-backup: ## Create database backup
	@echo "$(BLUE)Creating database backup...$(NC)"
	@mkdir -p backups
	@docker-compose exec -T postgres pg_dump -U postgres education_content > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Backup created in backups/$(NC)"

db-restore: ## Restore database from backup (usage: make db-restore FILE=backup.sql)
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)Error: Please specify FILE=backup.sql$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Restoring database from $(FILE)...$(NC)"
	@docker-compose exec -T postgres psql -U postgres education_content < $(FILE)
	@echo "$(GREEN)✓ Database restored$(NC)"

db-reset: ## Reset database (⚠️ deletes all data)
	@echo "$(RED)⚠️  WARNING: This will delete all database data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose exec postgres psql -U postgres -c "DROP DATABASE IF EXISTS education_content;"; \
		docker-compose exec postgres psql -U postgres -c "CREATE DATABASE education_content;"; \
		docker-compose exec -T postgres psql -U postgres education_content < init-db.sql; \
		echo "$(GREEN)✓ Database reset complete$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

# ============================================
# Cleanup Commands
# ============================================

clean: ## Remove stopped containers and unused images
	@echo "$(BLUE)Cleaning up Docker resources...$(NC)"
	docker-compose down --remove-orphans
	docker system prune -f
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-all: ## Remove all containers, images, and volumes (⚠️ nuclear option)
	@echo "$(RED)⚠️  WARNING: This will remove ALL Docker resources!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v --rmi all; \
		docker system prune -af --volumes; \
		echo "$(GREEN)✓ All Docker resources removed$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

# ============================================
# Development Commands
# ============================================

dev: up-dev logs ## Start development environment and show logs

format: ## Format code with black
	docker-compose exec flask_api black src/ tests/

lint: ## Run linting checks
	docker-compose exec flask_api flake8 src/ tests/

type-check: ## Run type checking with mypy
	docker-compose exec flask_api mypy src/

# ============================================
# Quick Commands
# ============================================

quick-start: init build up health ## Quick start: setup, build, and run
	@echo "$(GREEN)✓ Application is ready!$(NC)"
	@echo "$(BLUE)API available at: http://localhost:5000$(NC)"
	@echo "$(BLUE)Health check: http://localhost:5000/health$(NC)"

quick-test: up test ## Quick test: start services and run tests

# ============================================
# Information Commands
# ============================================

info: ## Show project information
	@echo "$(BLUE)Project Information$(NC)"
	@echo "$(GREEN)Services:$(NC)"
	@echo "  - Flask API: http://localhost:5000"
	@echo "  - PostgreSQL: localhost:5432"
	@echo "  - PgAdmin: http://localhost:5050 (with --profile admin)"
	@echo ""
	@echo "$(GREEN)Useful commands:$(NC)"
	@echo "  make up          - Start services"
	@echo "  make logs        - View logs"
	@echo "  make test        - Run tests"
	@echo "  make shell       - Open shell in container"
	@echo "  make help        - Show all commands"

version: ## Show Docker and Docker Compose versions
	@echo "$(BLUE)Docker Version:$(NC)"
	@docker --version
	@echo ""
	@echo "$(BLUE)Docker Compose Version:$(NC)"
	@docker-compose --version
