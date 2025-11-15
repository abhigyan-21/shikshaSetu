# Multilingual Education Content Pipeline

AI-powered educational content pipeline that creates accessible learning materials in multiple Indian languages.

## Features

- **Text Simplification**: Grade-level content adaptation (5-12) using Flan-T5
- **Translation**: Multi-language support (Hindi, Tamil, Telugu, Bengali, Marathi) via IndicTrans2
- **Validation**: NCERT curriculum alignment and quality checks using BERT
- **Speech Generation**: Text-to-speech in multiple Indian languages using VITS/Bhashini

## Project Structure

```
src/
├── api/              # Flask and FastAPI applications
├── pipeline/         # Pipeline orchestrator and model clients
├── simplifier/       # Text simplification component
├── translator/       # Translation engine
├── validator/        # Validation module
├── speech/           # Speech generation
├── repository/       # Database models and storage
└── monitoring/       # Logging and metrics

alembic/              # Database migrations
tests/                # Test suite
data/                 # Data storage
```

## Quick Start with Docker 🐳

The easiest way to run the application is using Docker:

```bash
# 1. Setup environment
make setup

# 2. Edit .env and add your API keys
# HUGGINGFACE_API_KEY=your_key_here

# 3. Start all services
make up

# 4. Check health
make health
```

That's it! The API will be available at http://localhost:5000

For detailed Docker instructions, see [README.docker.md](README.docker.md)

## Manual Setup (Without Docker)

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Hugging Face API key
- FFmpeg (for audio processing)

### Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Set up the database:
   ```bash
   # Create PostgreSQL database
   createdb education_content
   
   # Run initialization script
   psql -U postgres -d education_content -f init-db.sql
   ```

## Running the Application

### With Docker (Recommended)

```bash
# Development mode with hot-reload
make up-dev

# Production mode
make up-prod

# View logs
make logs

# Run tests
make test
```

### Without Docker

#### Flask API (Port 5000)
```bash
python src/api/flask_app.py
```

#### FastAPI (Port 8000)
```bash
python src/api/fastapi_app.py
```

## API Endpoints

### Flask Endpoints
- `GET /health` - Health check
- `POST /api/process-content` - Process content through pipeline
- `GET /api/content/<id>` - Retrieve processed content
- `POST /api/batch-download` - Create offline content package
- `GET /api/content/search` - Search content with filters

### FastAPI Endpoints
- `GET /health` - Health check
- `POST /api/v1/process-content` - Process content through pipeline
- `GET /api/v1/content/<id>` - Retrieve processed content
- `POST /api/v1/batch-download` - Create offline content package
- `GET /api/v1/content/search` - Search content with filters

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## Docker Commands

Common Docker commands (using Makefile):

```bash
make help           # Show all available commands
make up             # Start services
make down           # Stop services
make logs           # View logs
make shell          # Open shell in container
make test           # Run tests
make db-backup      # Backup database
make clean          # Clean up Docker resources
```

For more Docker commands, run `make help` or see [README.docker.md](README.docker.md)

## Testing

### With Docker
```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific tests
make test-speech
```

### Without Docker
```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html
```

## Development Status

This project is currently in active development. Core infrastructure is complete:
- ✅ Database schema and models
- ✅ Hugging Face model clients
- ✅ Flask and FastAPI applications
- ✅ Docker containerization
- ✅ Pipeline orchestrator
- ✅ Text Simplifier component
- ✅ Translation Engine component
- ✅ Validation Module component
- ✅ Speech Generator component
- ⏳ Frontend UI (planned)
- ⏳ Additional features (in progress)

## License

[Add your license here]
