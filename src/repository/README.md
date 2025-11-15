# Content Repository Module

This module provides content storage, retrieval, and offline caching functionality for the multilingual education content pipeline.

## Components

### ContentRepository

Main class for managing educational content storage and retrieval.

**Key Features:**
- Store and retrieve processed content from PostgreSQL database
- Offline content caching with Gzip compression
- Batch download packages (up to 50 items)
- Synchronization for online/offline transitions
- Content compression for low-bandwidth optimization

**Usage Example:**

```python
from src.repository import ContentRepository

# Initialize repository
repo = ContentRepository(cache_dir='data/cache')

# Store content
content = repo.store(
    original_text="Original educational content",
    simplified_text="Simplified version",
    translated_text="Translated version",
    language="Hindi",
    grade_level=8,
    subject="Mathematics",
    ncert_alignment_score=0.85
)

# Retrieve content
retrieved = repo.retrieve(content.id)

# Create batch download package
package_path = repo.batch_download(
    content_ids=[content.id],
    package_name="math_grade8_hindi"
)

# Cache for offline access
cache_result = repo.cache_for_offline(
    content_ids=[content.id]
)
```

### CacheManager

Optimizes content delivery for 2G networks and low-bandwidth scenarios.

**Key Features:**
- Lazy loading for audio files
- Progressive content loading (chunked delivery)
- CDN-style static asset caching
- 2G network performance validation (<5s load time)
- Audio optimization for low-bandwidth
- Compression ratio analysis

**Usage Example:**

```python
from src.repository import CacheManager

# Initialize cache manager
cache_mgr = CacheManager(cache_dir='data/cache')

# Validate 2G performance
validation = cache_mgr.validate_2g_performance(
    content_size_bytes=50000
)
print(f"Meets <5s requirement: {validation['meets_requirement']}")

# Create progressive chunks
chunk_paths = cache_mgr.create_progressive_content(
    content_text=long_content,
    content_id=content_id,
    chunk_size=1000
)

# Compress content
compressed = cache_mgr.compress_for_bandwidth(
    content="Educational content text",
    compression_level=9
)

# Lazy load audio
for chunk in cache_mgr.lazy_load_audio(audio_path):
    # Process audio chunk
    pass
```

## Performance Optimizations

### 2G Network Support

The module implements several optimizations for 2G networks (50 kbps typical speed):

1. **Gzip Compression**: Maximum compression (level 9) for text content
2. **Audio Optimization**: Target bitrate of 32k for audio files
3. **Progressive Loading**: Content split into chunks for faster initial display
4. **Lazy Loading**: Audio files loaded on-demand in chunks
5. **CDN Caching**: Static assets cached with appropriate headers

### Load Time Validation

Content is validated to meet the <5 second load time requirement on 2G networks:

```python
validation = cache_mgr.validate_2g_performance(content_size_bytes)
# Returns: meets_requirement (True/False)
```

## Database Schema

The module uses the following PostgreSQL tables:

- **processed_content**: Stores processed educational materials
- **ncert_standards**: Reference database for curriculum standards
- **student_profiles**: User preferences and offline cache metadata
- **pipeline_logs**: Processing logs and metrics

## Cache Structure

```
data/cache/
├── {content_id}.json.gz          # Compressed content metadata
├── audio/
│   └── {content_id}.audio        # Compressed audio files
├── packages/
│   └── {package_name}.json.gz    # Batch download packages
├── cdn/
│   └── {cache_key}.{ext}         # CDN-cached static assets
└── progressive/
    └── {content_id}_chunk_*.txt  # Progressive loading chunks
```

## Requirements Addressed

This implementation addresses the following requirements:

- **7.1**: Offline content storage and retrieval
- **7.2**: Batch downloads (up to 50 items per package)
- **7.3**: Content compression for low-bandwidth
- **7.4**: <5s load time on 2G networks
- **7.5**: Online/offline synchronization
- **7.6**: Content package creation (text + audio bundles)

## Testing

Run the example script to test functionality:

```bash
python examples/content_repository_example.py
```

## Dependencies

- SQLAlchemy: Database ORM
- PostgreSQL: Database backend
- Gzip: Content compression
- Python 3.8+
