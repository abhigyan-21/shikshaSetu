# Frontend-Backend Integration Guide

This document describes how the React frontend integrates with the Python backend API.

## API Configuration

### Development
The frontend is configured to proxy API requests to `http://localhost:5000` in development mode.

**Configuration**: `vite.config.js`
```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true
    }
  }
}
```

### Production
In production, configure the API base URL via environment variable:

```bash
VITE_API_BASE_URL=https://your-api-domain.com
```

## API Endpoints

### 1. Process Content
**Endpoint**: `POST /api/process-content`

**Request**:
```javascript
const formData = new FormData()
formData.append('input_data', textContent) // or PDF file
formData.append('target_language', 'Hindi')
formData.append('grade_level', 8)
formData.append('subject', 'Mathematics')
formData.append('output_format', 'both') // 'text', 'audio', or 'both'

const response = await axios.post('/api/process-content', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
```

**Response**:
```json
{
  "id": "uuid",
  "simplified_text": "...",
  "translated_text": "...",
  "language": "Hindi",
  "grade_level": 8,
  "subject": "Mathematics",
  "audio_file_path": "/audio/uuid.mp3",
  "ncert_alignment_score": 0.85,
  "audio_accuracy_score": 0.92,
  "metadata": {}
}
```

**Used in**: `src/pages/UploadPage.jsx`

### 2. Get Content by ID
**Endpoint**: `GET /api/content/:id`

**Request**:
```javascript
const response = await axios.get(`/api/content/${contentId}`)
```

**Response**: Same as Process Content response

**Used in**: `src/pages/ContentViewerPage.jsx`

### 3. Search Content
**Endpoint**: `GET /api/content/search`

**Request**:
```javascript
const params = new URLSearchParams({
  language: 'Hindi',
  grade: '8',
  subject: 'Mathematics'
})
const response = await axios.get(`/api/content/search?${params}`)
```

**Response**:
```json
[
  {
    "id": "uuid",
    "simplified_text": "...",
    "language": "Hindi",
    "grade_level": 8,
    "subject": "Mathematics",
    ...
  }
]
```

**Used in**: `src/pages/ContentViewerPage.jsx`

### 4. Batch Download
**Endpoint**: `POST /api/batch-download`

**Request**:
```javascript
const response = await axios.post('/api/batch-download', {
  content_ids: ['uuid1', 'uuid2', 'uuid3']
})
```

**Response**:
```json
[
  {
    "id": "uuid1",
    "simplified_text": "...",
    "translated_text": "...",
    ...
  }
]
```

**Used in**: `src/pages/OfflineContentPage.jsx`

## Error Handling

### Frontend Error Handling
```javascript
try {
  const response = await axios.post('/api/process-content', formData)
  setResult(response.data)
} catch (err) {
  setError(err.response?.data?.message || err.message || 'An error occurred')
}
```

### Expected Error Responses
```json
{
  "error": "Error message",
  "message": "Detailed error description",
  "status": 400
}
```

## Data Flow

### Content Processing Flow
```
User Input (UploadPage)
  ↓
POST /api/process-content
  ↓
Backend Pipeline Processing
  ↓
Response with processed content
  ↓
Display success message
  ↓
Redirect to ContentViewerPage
```

### Offline Content Flow
```
User selects content (OfflineContentPage)
  ↓
POST /api/batch-download
  ↓
Backend retrieves content
  ↓
Response with content array
  ↓
Store in localStorage
  ↓
Display in offline content list
```

## Local Storage

### Stored Data
```javascript
// Accessibility preferences
localStorage.setItem('dyslexicFont', 'true')
localStorage.setItem('fontSize', 'large')
localStorage.setItem('highContrast', 'true')

// Offline content
localStorage.setItem('offlineContent', JSON.stringify([...]))
```

### Data Structure
```javascript
// Offline content array
[
  {
    id: 'uuid',
    simplified_text: '...',
    translated_text: '...',
    language: 'Hindi',
    grade_level: 8,
    subject: 'Mathematics',
    audio_file_path: '/audio/uuid.mp3',
    ncert_alignment_score: 0.85,
    audio_accuracy_score: 0.92
  }
]
```

## Audio Handling

### Audio Playback
```javascript
const audioRef = useRef(null)

const toggleAudio = () => {
  if (audioRef.current) {
    if (isPlaying) {
      audioRef.current.pause()
    } else {
      audioRef.current.play()
    }
  }
}

<audio
  ref={audioRef}
  src={content.audio_file_path}
  onEnded={() => setIsPlaying(false)}
/>
```

### Audio File Paths
- Development: Proxied through Vite dev server
- Production: Served from CDN or static file server

## Network Status Detection

### Online/Offline Detection
```javascript
const [isOnline, setIsOnline] = useState(navigator.onLine)

useEffect(() => {
  const handleOnline = () => setIsOnline(true)
  const handleOffline = () => setIsOnline(false)
  
  window.addEventListener('online', handleOnline)
  window.addEventListener('offline', handleOffline)
  
  return () => {
    window.removeEventListener('online', handleOnline)
    window.removeEventListener('offline', handleOffline)
  }
}, [])
```

## Performance Optimization

### Request Optimization
- Use FormData for file uploads
- Implement request cancellation for search
- Cache API responses where appropriate
- Lazy load audio files

### Loading States
```javascript
const [isLoading, setIsLoading] = useState(false)

// Show loading indicator
{isLoading && (
  <div role="status" aria-live="polite">
    Loading...
  </div>
)}
```

## Testing Integration

### Mock API for Development
Create a mock API server for frontend development:

```javascript
// mock-api.js
import express from 'express'
const app = express()

app.post('/api/process-content', (req, res) => {
  res.json({
    id: 'mock-uuid',
    simplified_text: 'Mock simplified text',
    translated_text: 'Mock translated text',
    // ...
  })
})

app.listen(5000)
```

### Integration Tests
Test API integration with actual backend:

```javascript
describe('API Integration', () => {
  it('should process content successfully', async () => {
    const formData = new FormData()
    formData.append('input_data', 'Test content')
    formData.append('target_language', 'Hindi')
    formData.append('grade_level', 8)
    formData.append('subject', 'Mathematics')
    formData.append('output_format', 'both')

    const response = await axios.post('/api/process-content', formData)
    expect(response.status).toBe(200)
    expect(response.data).toHaveProperty('id')
  })
})
```

## Deployment Considerations

### Environment Variables
```bash
# .env.production
VITE_API_BASE_URL=https://api.yourdomain.com
```

### CORS Configuration
Backend must allow requests from frontend domain:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['https://yourdomain.com'])
```

### Static File Serving
Configure backend to serve audio files:

```python
@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory('audio', filename)
```

## Troubleshooting

### Issue: API requests failing
**Check**:
1. Backend server is running on port 5000
2. CORS is configured correctly
3. API endpoints match frontend expectations

### Issue: Audio not playing
**Check**:
1. Audio file path is correct
2. Audio file is accessible
3. Browser supports audio format
4. CORS allows audio file access

### Issue: Offline content not persisting
**Check**:
1. localStorage is enabled in browser
2. Storage quota not exceeded
3. Data is being serialized correctly

## Security Considerations

### Input Validation
- Validate file types on frontend before upload
- Limit file sizes (e.g., max 10MB for PDFs)
- Sanitize user input

### Authentication (Future)
When implementing authentication:
```javascript
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
```

### HTTPS
Always use HTTPS in production for:
- API requests
- Audio file delivery
- Static assets
