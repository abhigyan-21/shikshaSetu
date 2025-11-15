# Docker Setup Guide

This guide explains how to run the Multilingual Education Content Pipeline using Docker.

## Prerequisites

- Docker Engine 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose 2.0+ ([Install Docker Compose](https://docs.docker.com/compose/install/))
- At least 4GB of available RAM
- 10GB of free disk space

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd shiksha_setu
```

### 2. Configure Environment Variables

Copy the example environment file and update with your values:

```bash
cp .env.example .env
```

Edit `.env` and set:
- `POSTGRES_PASSWORD` - Secure database password
- `FLASK_SECRET_KEY` - Secure secret key for Flask
- `HUGGINGFACE_API_KEY` - Your Hugging Face API key (get from https://huggingface.co/settings/tokens)
- `BHASHINI_API_KEY` - (Optional) Your Bhashini API key

### 3. Start the Services

**Development Mode:**
```bash
docker-compose up -d
```

**With Development Features (hot-reload):**
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

**Production Mode:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 4. Verify Services are Running

```bash
docker-compose ps
```

Check health status:
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{"status": "healthy", "service": "education-content-api"}
```

## Service URLs

- **Flask API**: http://localhost:5000
- **FastAPI** (optional): http://localhost:8000
- **PostgreSQL**: localhost:5432
- **PgAdmin** (optional): http://localhost:5050

## Common Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f flask_api
docker-compose logs -f postgres
```

### Stop Services

```bash
docker-compose down
```

### Stop and Remove Volumes (⚠️ deletes all data)

```bash
docker-compose down -v
```

### Restart a Service

```bash
docker-compose restart flask_api
```

### Execute Commands in Container

```bash
# Open shell in Flask API container
docker-compose exec flask_api bash

# Run Python shell
docker-compose exec flask_api python

# Run tests
docker-compose exec flask_api pytest tests/ -v
```

### Database Operations

```bash
# Access PostgreSQL CLI
docker-compose exec postgres psql -U postgres -d education_content

# Run database migrations
docker-compose exec flask_api alembic upgrade head

# Create database backup
docker-compose exec postgres pg_dump -U postgres education_content > backup.sql

# Restore database backup
docker-compose exec -T postgres psql -U postgres education_content < backup.sql
```

## Running Tests

### Run All Tests

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --profile test up test_runner
```

### Run Specific Tests

```bash
docker-compose exec flask_api pytest tests/test_speech_generator.py -v
```

### Run Tests with Coverage

```bash
docker-compose exec flask_api pytest tests/ --cov=src --cov-report=html
```

## Optional Services

### Start with PgAdmin (Database Management UI)

```bash
docker-compose --profile admin up -d
```

Access PgAdmin at http://localhost:5050
- Email: admin@example.com (or value from .env)
- Password: admin (or value from .env)

### Start with FastAPI

```bash
docker-compose --profile fastapi up -d
```

## Building Images

### Build All Images

```bash
docker-compose build
```

### Build Specific Service

```bash
docker-compose build flask_api
```

### Build Without Cache

```bash
docker-compose build --no-cache
```

## Troubleshooting

### Port Already in Use

If you get "port already allocated" error:

```bash
# Check what's using the port
lsof -i :5000  # On macOS/Linux
netstat -ano | findstr :5000  # On Windows

# Change port in .env file
FLASK_PORT=5001
```

### Database Connection Issues

```bash
# Check if PostgreSQL is healthy
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Out of Memory

If containers are killed due to memory:

```bash
# Check Docker memory allocation
docker stats

# Increase Docker Desktop memory limit in settings
# Or reduce worker count in production config
```

### Permission Issues

```bash
# Fix data directory permissions
sudo chown -R $USER:$USER data/ logs/

# Or run with sudo (not recommended)
sudo docker-compose up -d
```

### Clean Start (Reset Everything)

```bash
# Stop all containers
docker-compose down

# Remove all volumes (⚠️ deletes data)
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Rebuild and start fresh
docker-compose build --no-cache
docker-compose up -d
```

## Production Deployment

### 1. Update Environment Variables

```bash
# Set production values in .env
FLASK_DEBUG=false
POSTGRES_PASSWORD=<strong-password>
FLASK_SECRET_KEY=<strong-secret-key>
BUILD_TARGET=production
```

### 2. Configure SSL (Optional)

Place SSL certificates in `./ssl/` directory:
- `./ssl/cert.pem`
- `./ssl/key.pem`

### 3. Start Production Stack

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 4. Monitor Services

```bash
# Check resource usage
docker stats

# View logs
docker-compose logs -f --tail=100

# Check health
curl http://localhost/health
```

## Performance Optimization

### Adjust Worker Count

Edit `docker-compose.prod.yml`:

```yaml
command: gunicorn --bind 0.0.0.0:5000 --workers 8 --timeout 120 ...
```

Rule of thumb: `workers = (2 × CPU cores) + 1`

### Database Connection Pool

Edit `.env`:

```bash
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
```

### Resource Limits

Edit `docker-compose.prod.yml` to adjust CPU and memory limits.

## Backup and Restore

### Automated Backups

Create a backup script:

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U postgres education_content > "backup_${DATE}.sql"
```

### Restore from Backup

```bash
docker-compose exec -T postgres psql -U postgres education_content < backup_20240101_120000.sql
```

## Monitoring

### Health Checks

```bash
# Check all services
docker-compose ps

# Check specific service health
docker inspect --format='{{.State.Health.Status}}' education_content_api
```

### Resource Usage

```bash
# Real-time stats
docker stats

# Container logs
docker-compose logs -f --tail=100
```

## Support

For issues and questions:
- Check logs: `docker-compose logs -f`
- Review environment variables in `.env`
- Ensure all required ports are available
- Verify Docker has sufficient resources allocated

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Python Docker Best Practices](https://docs.docker.com/language/python/)
