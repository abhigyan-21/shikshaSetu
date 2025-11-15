# Multi-stage Dockerfile for Multilingual Education Content Pipeline
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libsndfile1 \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/audio data/cache data/curriculum logs

# Set proper permissions
RUN chmod -R 755 /app

# Expose ports
EXPOSE 5000 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Default command (can be overridden in docker-compose)
CMD ["python", "-m", "src.api.flask_app"]


# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest==7.4.3 \
    pytest-cov==4.1.0 \
    pytest-mock==3.12.0 \
    black==23.11.0 \
    flake8==6.1.0 \
    mypy==1.7.1

# Set development environment
ENV FLASK_DEBUG=true

CMD ["python", "-m", "src.api.flask_app"]


# Production stage
FROM base as production

# Remove unnecessary files
RUN rm -rf tests/ examples/ .git/ .pytest_cache/ __pycache__/

# Use non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Production command with gunicorn
RUN pip install --no-cache-dir gunicorn==21.2.0

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "src.api.flask_app:app"]
