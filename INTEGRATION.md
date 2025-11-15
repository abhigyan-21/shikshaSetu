# Integration Documentation

## Overview

This document describes how all components of the multilingual education content pipeline are integrated together to provide a complete end-to-end solution.

## Architecture

The system follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│              - Upload Page                                   │
│              - Content Viewer                                │
│              - Offline Content Manager                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   API Layer (Flask/FastAPI)                  │
│              - /api/process-content                          │
│              - /api/content/{id}                             │
│              - /api/batch-download                           │
│              - /api/content/search                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Integrated Pipeline                         │
│              - Orchestrates all components                   │
│              - Manages data flow                             │
│              - Tracks metrics                                │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Orchestrator │ │  Repository  │ │   Metrics    │ │   Database   │
│              │ │              │ │  Collector   │ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│              Pipeline Components                             │
│  - Text Simplifier (Flan-T5)                                │
│  - Translation Engine (IndicTrans2)                          │
│  - Validation Module (BERT)                                  │
│  - Speech Generator (VITS/Bhashini)                          │
└─────────────────────────────────────────────────────────────┘
```

## Component Integration

### 1. Integrated Pipeline (`src/integration.py`)

The `IntegratedPipeline` class serves as the central integration point that connects:

- **Content Pipeline Orchestrator**: Manages the 4-stage processing flow
- **Content Repository**: Handles storage and retrieval
- **Metrics Collector**: Tracks performance and quality metrics
- **Database**: Persists all data

**Key Methods:**
- `process_and_store()`: Complete end-to-end processing
- `retrieve_content()`: Fetch processed content
- `search_content()`: Search with filters
- `create_offline_package()`: Batch download for offline access
- `get_system_health()`: System status monitoring

### 2. API Integration

Both Flask and FastAPI applications use the integrated pipeline:

```python
from src.integration import get_integrated_pipeline

# Initialize integrated pipeline
integrated_pipeline = get_integrated_pipeline()

# Use in endpoints
@app.route('/api/process-content', methods=['POST'])
def process_content():
    result = integrated_pipeline.process_and_store(
        input_data=data['input_data'],
        target_language=data['target_language'],
        grade_level=data['grade_level'],
        subject=data['subject'],
        output_format=data['output_format']
    )
    return jsonify(result)
```

### 3. Frontend Integration

The frontend uses a centralized API utility (`frontend/src/utils/api.js`) that provides:

- `processContent()`: Submit content for processing
- `getContent()`: Retrieve processed content
- `searchContent()`: Search with filters
- `createBatchDownload()`: Create offline packages
- `formatApiError()`: User-friendly error messages

**Example Usage:**
```javascript
import { processContent } from '../utils/api'

const result = await processContent({
  input_data: textContent,
  target_language: 'Hindi',
  grade_level: 8,
  subject: 'Science',
  output_format: 'both'
})
```

### 4. Repository Integration

The Content Repository connects to:

- **Database**: PostgreSQL for persistent storage
- **Cache Manager**: Local caching for offline access
- **File System**: Audio file storage

All components access the repository through the integrated pipeline, ensuring consistent data access patterns.

### 5. Metrics Integration

The Metrics Collector tracks:

- Pipeline execution metrics (processing time, success rate)
- Quality scores (NCERT alignment, audio accuracy)
- Error rates and alerts
- System health status

Metrics are automatically collected during pipeline execution and stored in the database.

## Data Flow

### Complete End-to-End Flow

1. **User Input** (Frontend)
   - User enters content and selects parameters
   - Frontend calls `processContent()` API

2. **API Processing** (Flask/FastAPI)
   - API validates request
   - Calls `integrated_pipeline.process_and_store()`

3. **Pipeline Orchestration** (Orchestrator)
   - Stage 1: Text Simplification (Flan-T5)
   - Stage 2: Translation (IndicTrans2)
   - Stage 3: Validation (BERT)
   - Stage 4: Speech Generation (VITS/Bhashini)

4. **Storage** (Repository)
   - Content stored in PostgreSQL
   - Audio files saved to file system
   - Cache created for offline access

5. **Metrics Tracking** (Metrics Collector)
   - Processing time recorded
   - Quality scores logged
   - Success/failure tracked

6. **Response** (API → Frontend)
   - Processed content returned
   - Frontend displays results
   - User can view/download content

## Testing Integration

### Automated Tests

Run the end-to-end integration tests:

```bash
# Run pytest tests
pytest tests/test_end_to_end_integration.py -v

# Run integration verification script
python verify_integration.py
```

### Manual Testing

1. **Start Backend:**
   ```bash
   # Flask
   python -m src.api.flask_app
   
   # FastAPI
   python -m src.api.fastapi_app
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test Flow:**
   - Navigate to http://localhost:5173
   - Upload content on Upload page
   - View processed content on Content page
   - Download for offline on Offline page

### Integration Verification

The `verify_integration.py` script checks:

1. ✓ Component imports
2. ✓ Database connection
3. ✓ Integrated pipeline initialization
4. ✓ End-to-end flow execution
5. ✓ API endpoint configuration
6. ✓ Frontend integration

Run it to verify everything is connected:

```bash
python verify_integration.py
```

## API Endpoints

### Flask API (Port 5000)

- `POST /api/process-content` - Process educational content
- `GET /api/content/{id}` - Retrieve content by ID
- `GET /api/content/{id}/audio` - Get audio file
- `POST /api/batch-download` - Create offline package
- `GET /api/content/search` - Search content with filters
- `GET /health` - Health check

### FastAPI (Port 8000)

- `POST /api/v1/process-content` - Process educational content
- `GET /api/v1/content/{id}` - Retrieve content by ID
- `GET /api/v1/content/{id}/audio` - Get audio file
- `POST /api/v1/batch-download` - Create offline package
- `GET /api/v1/content/search` - Search content with filters
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/education_db

# API Keys
HUGGINGFACE_API_KEY=your_api_key_here

# Flask
FLASK_SECRET_KEY=your_secret_key
FLASK_DEBUG=false
FLASK_PORT=5000

# FastAPI
FASTAPI_PORT=8000

# Cache
CACHE_DIR=data/cache

# Redis (for rate limiting)
REDIS_URL=redis://localhost:6379
```

### Frontend Configuration

Create `frontend/.env`:

```bash
VITE_API_URL=http://localhost:5000
```

## Deployment

### Production Deployment

1. **Database Setup:**
   ```bash
   # Initialize database
   python -m src.repository.database
   ```

2. **Start Backend:**
   ```bash
   # Using gunicorn for Flask
   gunicorn -w 4 -b 0.0.0.0:5000 src.api.flask_app:app
   
   # Using uvicorn for FastAPI
   uvicorn src.api.fastapi_app:app --host 0.0.0.0 --port 8000 --workers 4
   ```

3. **Build Frontend:**
   ```bash
   cd frontend
   npm run build
   ```

4. **Serve Frontend:**
   ```bash
   # Using nginx or serve
   npx serve -s dist -p 3000
   ```

### Docker Deployment

Use the provided Docker configuration:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Monitoring

### Health Checks

Check system health:

```bash
# Flask
curl http://localhost:5000/health

# FastAPI
curl http://localhost:8000/health
```

### Metrics Dashboard

Access metrics through the integrated pipeline:

```python
from src.integration import get_integrated_pipeline

pipeline = get_integrated_pipeline()
health = pipeline.get_system_health()

print(health['status'])
print(health['metrics'])
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check DATABASE_URL environment variable
   - Ensure PostgreSQL is running
   - Verify database exists

2. **API Key Errors**
   - Set HUGGINGFACE_API_KEY environment variable
   - Verify API key is valid

3. **Frontend Can't Connect to Backend**
   - Check VITE_API_URL in frontend/.env
   - Ensure backend is running
   - Verify CORS is enabled

4. **Audio Generation Fails**
   - Check audio cache directory exists
   - Verify VITS/Bhashini API access
   - Check disk space for audio files

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Optimization

### Caching

- Content cached locally for offline access
- Audio files compressed for bandwidth optimization
- Database queries optimized with indexes

### Rate Limiting

- API endpoints rate-limited to prevent abuse
- Configurable limits per endpoint

### Batch Processing

- Support for batch downloads (up to 50 items)
- Optimized for 2G network performance

## Security

### Input Validation

- All inputs validated before processing
- SQL injection prevention
- XSS protection

### Authentication

- API key authentication for model access
- Rate limiting per IP address
- CORS configured for frontend access

### Data Privacy

- User data encrypted at rest
- Secure database connections
- No PII stored without consent

## Next Steps

1. **Scale Testing**: Test with larger datasets
2. **Performance Tuning**: Optimize processing times
3. **Monitoring**: Set up production monitoring
4. **Documentation**: Add API documentation
5. **Testing**: Expand test coverage

## Support

For issues or questions:
- Check logs: `docker-compose logs`
- Run verification: `python verify_integration.py`
- Review test results: `pytest tests/ -v`

---

**Integration Status**: ✓ Complete

All components are integrated and tested. The system is ready for deployment.
