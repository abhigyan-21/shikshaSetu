# Quick Start Guide - Integrated System

## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL database
- Hugging Face API key (optional for testing)

## Setup

### 1. Install Dependencies

```bash
# Backend dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Configure Environment

Create `.env` file in project root:

```bash
DATABASE_URL=postgresql://user:pass@localhost/education_db
HUGGINGFACE_API_KEY=your_api_key_here
FLASK_SECRET_KEY=your_secret_key
CACHE_DIR=data/cache
```

Create `frontend/.env`:

```bash
VITE_API_URL=http://localhost:5000
```

### 3. Initialize Database

```bash
python -c "from src.repository.database import init_db; init_db()"
```

## Running the System

### Option 1: Run All Components Separately

**Terminal 1 - Backend (Flask)**:
```bash
python -m src.api.flask_app
# Runs on http://localhost:5000
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

### Option 2: Using Docker

```bash
docker-compose up -d
```

## Verify Integration

Run the verification script to ensure everything is connected:

```bash
python verify_integration.py
```

Expected output:
```
✓ Component Imports................ PASSED
✓ Database Connection.............. PASSED
✓ Integrated Pipeline.............. PASSED
✓ End-to-End Flow.................. PASSED
✓ API Endpoints.................... PASSED
✓ Frontend Integration............. PASSED

Total: 6/6 steps passed
```

## Test the Complete Flow

### 1. Access the Application

Open your browser to: http://localhost:5173

### 2. Upload Content

1. Navigate to "Upload" page
2. Enter educational content (or select PDF)
3. Choose:
   - Target Language: Hindi, Tamil, Telugu, Bengali, or Marathi
   - Grade Level: 5-12
   - Subject: Mathematics, Science, Social Studies, etc.
   - Output Format: Text, Audio, or Both
4. Click "Process Content"

### 3. View Results

- Automatically redirected to content viewer
- See simplified and translated text
- Play audio (if generated)
- View quality scores

### 4. Search Content

1. Navigate to "Content" page
2. Use filters to search:
   - Language
   - Grade Level
   - Subject
3. Click on results to view details

### 5. Download for Offline

1. Navigate to "Offline" page
2. Select content items
3. Click "Download Selected"
4. Content available offline

## API Testing

### Using cURL

**Process Content**:
```bash
curl -X POST http://localhost:5000/api/process-content \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": "Photosynthesis is the process by which plants make food.",
    "target_language": "Hindi",
    "grade_level": 8,
    "subject": "Science",
    "output_format": "both"
  }'
```

**Get Content**:
```bash
curl http://localhost:5000/api/content/{content_id}
```

**Search Content**:
```bash
curl "http://localhost:5000/api/content/search?language=Hindi&grade=8&subject=Science"
```

### Using Python

```python
from src.integration import get_integrated_pipeline

# Initialize pipeline
pipeline = get_integrated_pipeline()

# Process content
result = pipeline.process_and_store(
    input_data="Sample educational content",
    target_language='Hindi',
    grade_level=8,
    subject='Science',
    output_format='both'
)

print(f"Content ID: {result['content_id']}")
print(f"NCERT Score: {result['quality_scores']['ncert_alignment_score']:.2%}")

# Retrieve content
content = pipeline.retrieve_content(result['content_id'])
print(f"Translated: {content['translated_text'][:100]}...")

# Search
results = pipeline.search_content(language='Hindi', grade_level=8)
print(f"Found {results['total_count']} items")
```

## Run Tests

### Integration Tests

```bash
pytest tests/test_end_to_end_integration.py -v
```

### All Tests

```bash
pytest tests/ -v
```

## Monitoring

### Check System Health

```bash
curl http://localhost:5000/health
```

### View Logs

```bash
# Docker
docker-compose logs -f

# Local
# Check console output where services are running
```

## Troubleshooting

### Backend Won't Start

1. Check database connection:
   ```bash
   psql $DATABASE_URL -c "SELECT 1"
   ```

2. Verify dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Frontend Can't Connect

1. Check VITE_API_URL in `frontend/.env`
2. Ensure backend is running on correct port
3. Check browser console for CORS errors

### Database Errors

1. Initialize database:
   ```bash
   python -c "from src.repository.database import init_db; init_db()"
   ```

2. Check migrations:
   ```bash
   alembic upgrade head
   ```

### Audio Generation Fails

1. Check cache directory exists:
   ```bash
   mkdir -p data/cache/audio
   ```

2. Verify disk space
3. Check API key for TTS service

## Performance Tips

1. **Enable Caching**: Content is automatically cached for offline d`
NTEGRATION.mee `Ition, sumentaoced dail
For detse
to ud ready tegrated any inlltem is fu**: ✓ Sysustat

**Sation

---heck integr` to cration.pytegrify_in veythonn `p Ruon: Verificatiity
-tionalverify func-v` to ests/ ytest tun `pests: Rtion
- Tled informadetaiON.md` for  `INTEGRATIion: See Documentatrt

-
## Suppos
rnge patteusaased on  brformanceune peimize**: T
4. **Optnglertiing and anitorup mot Ser**: **Monito
3. ironmention envto producty eploale**: DSc**se case
2. our uor yparameters f Modify ize**:*Customeps

1. * St
## Nextt abuse
o prevenically ted automatonfigurg**: CRate Limitiners
4. **ansfcontent trrge ssion for lanable compreon**: E **Compressie items
3.plor multid floabatch downse cessing**: U**Batch Proaccess
2. 