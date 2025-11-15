"""FastAPI application for high-performance endpoints."""
from fastapi import FastAPI, HTTPException, Query, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
import os
import logging
import io
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from ..pipeline.orchestrator import ContentPipelineOrchestrator, PipelineValidationError, PipelineStageError
from ..repository.database import get_db
from ..repository.models import ProcessedContent
from ..repository.cache_manager import CacheManager
from ..integration import get_integrated_pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Education Content API",
    description="AI-powered multilingual education content pipeline",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize integrated pipeline (connects all components)
integrated_pipeline = get_integrated_pipeline()
cache_manager = CacheManager()


# Request/Response Models
class ContentRequest(BaseModel):
    """Request model for content processing."""
    input_data: str = Field(..., description="Text or PDF content to process", min_length=1)
    target_language: str = Field(..., description="Target Indian language")
    grade_level: int = Field(..., ge=5, le=12, description="Grade level (5-12)")
    subject: str = Field(..., description="Subject area")
    output_format: str = Field(..., description="Output format: text, audio, or both")
    
    @validator('target_language')
    def validate_language(cls, v):
        supported = ['Hindi', 'Tamil', 'Telugu', 'Bengali', 'Marathi']
        if v not in supported:
            raise ValueError(f'Language must be one of {supported}')
        return v
    
    @validator('subject')
    def validate_subject(cls, v):
        supported = ['Mathematics', 'Science', 'Social Studies', 'English', 'History', 'Geography']
        if v not in supported:
            raise ValueError(f'Subject must be one of {supported}')
        return v
    
    @validator('output_format')
    def validate_format(cls, v):
        supported = ['text', 'audio', 'both']
        if v not in supported:
            raise ValueError(f'Output format must be one of {supported}')
        return v


class ContentResponse(BaseModel):
    """Response model for processed content."""
    id: str
    simplified_text: str
    translated_text: str
    language: str
    grade_level: int
    subject: str
    audio_url: Optional[str]
    ncert_alignment_score: float
    audio_accuracy_score: Optional[float]
    validation_status: str
    created_at: str
    metadata: Dict[str, Any]


class ContentDetail(BaseModel):
    """Detailed content model for retrieval."""
    id: str
    original_text: str
    simplified_text: str
    translated_text: str
    language: str
    grade_level: int
    subject: str
    audio_url: Optional[str]
    ncert_alignment_score: float
    audio_accuracy_score: Optional[float]
    created_at: str
    metadata: Optional[Dict[str, Any]]


class BatchDownloadRequest(BaseModel):
    """Request model for batch download."""
    content_ids: List[str] = Field(..., description="List of content IDs", max_items=50)
    include_audio: bool = Field(True, description="Include audio files in package")


class BatchDownloadResponse(BaseModel):
    """Response model for batch download."""
    package_id: str
    item_count: int
    include_audio: bool
    total_size_bytes: int
    total_size_mb: float
    performance: Dict[str, Any]
    contents: List[Dict[str, Any]]


class SearchResult(BaseModel):
    """Search result item."""
    id: str
    language: str
    grade_level: int
    subject: str
    translated_text_preview: str
    ncert_alignment_score: float
    audio_available: bool
    created_at: str


class SearchResponse(BaseModel):
    """Response model for search."""
    total_count: int
    limit: int
    offset: int
    results: List[SearchResult]
    filters: Dict[str, Any]


# Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Education Content API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "education-content-api"}


@app.post("/api/v1/process-content", response_model=ContentResponse, status_code=201)
@limiter.limit("10/minute")
async def process_content(request: ContentRequest, response: Response):
    """
    Process educational content through the pipeline.
    
    This endpoint processes content through four stages:
    1. Simplification (Flan-T5)
    2. Translation (IndicTrans2)
    3. Validation (BERT)
    4. Speech Generation (VITS/Bhashini)
    
    Rate limit: 10 requests per minute
    """
    try:
        logger.info(f"Processing content: language={request.target_language}, grade={request.grade_level}")
        
        # Process through integrated pipeline (orchestrator + repository + metrics)
        result = integrated_pipeline.process_and_store(
            input_data=request.input_data,
            target_language=request.target_language,
            grade_level=request.grade_level,
            subject=request.subject,
            output_format=request.output_format
        )
        
        # Build response from integrated result
        content_response = ContentResponse(
            id=result['content_id'],
            simplified_text=result['content']['simplified_text'],
            translated_text=result['content']['translated_text'],
            language=result['content']['language'],
            grade_level=result['content']['grade_level'],
            subject=result['content']['subject'],
            audio_url=result['content']['audio_url'],
            ncert_alignment_score=result['quality_scores']['ncert_alignment_score'],
            audio_accuracy_score=result['quality_scores']['audio_accuracy_score'],
            validation_status=result['quality_scores']['validation_status'],
            created_at='',  # Will be set from metadata
            metadata=result['metadata']
        )
        
        logger.info(f"Content processed successfully: content_id={result['content_id']}")
        
        return content_response
        
    except PipelineValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")
        
    except PipelineStageError as e:
        logger.error(f"Pipeline stage error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/v1/content/{content_id}", response_model=ContentDetail)
@limiter.limit("100/minute")
async def get_content(
    content_id: str,
    response: Response,
    compress: bool = Query(False, description="Return gzip-compressed content")
):
    """
    Retrieve processed content by ID.
    
    Args:
        content_id: UUID of the processed content
        compress: If true, return gzip-compressed content for bandwidth optimization
    
    Rate limit: 100 requests per minute
    """
    try:
        # Validate UUID format
        try:
            content_uuid = UUID(content_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid content ID format")
        
        # Retrieve from database
        session = get_db().get_session()
        
        try:
            content = session.query(ProcessedContent).filter_by(id=content_uuid).first()
            
            if not content:
                raise HTTPException(status_code=404, detail="Content not found")
            
            # Build response
            content_detail = ContentDetail(
                id=str(content.id),
                original_text=content.original_text,
                simplified_text=content.simplified_text,
                translated_text=content.translated_text,
                language=content.language,
                grade_level=content.grade_level,
                subject=content.subject,
                audio_url=f"/api/v1/content/{content.id}/audio" if content.audio_file_path else None,
                ncert_alignment_score=content.ncert_alignment_score,
                audio_accuracy_score=content.audio_accuracy_score,
                created_at=content.created_at.isoformat(),
                metadata=content.content_metadata
            )
            
            if compress:
                # Compress response for bandwidth optimization
                import json
                json_data = json.dumps(content_detail.dict())
                compressed_data = cache_manager.compress_for_bandwidth(json_data, compression_level=9)
                
                return StreamingResponse(
                    io.BytesIO(compressed_data),
                    media_type="application/gzip",
                    headers={"Content-Disposition": f"attachment; filename=content_{content_id}.json.gz"}
                )
            
            logger.info(f"Content retrieved: content_id={content_id}")
            
            return content_detail
            
        finally:
            session.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving content: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve content: {str(e)}")


@app.get("/api/v1/content/{content_id}/audio")
@limiter.limit("50/minute")
async def get_content_audio(content_id: str, response: Response):
    """
    Retrieve audio file for processed content.
    
    Args:
        content_id: UUID of the processed content
    
    Returns:
        Audio file (MP3/OGG format)
    
    Rate limit: 50 requests per minute
    """
    try:
        # Validate UUID format
        try:
            content_uuid = UUID(content_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid content ID format")
        
        # Retrieve from database
        session = get_db().get_session()
        
        try:
            content = session.query(ProcessedContent).filter_by(id=content_uuid).first()
            
            if not content:
                raise HTTPException(status_code=404, detail="Content not found")
            
            if not content.audio_file_path:
                raise HTTPException(status_code=404, detail="Audio not available for this content")
            
            # Check if audio file exists
            if not os.path.exists(content.audio_file_path):
                logger.error(f"Audio file not found: {content.audio_file_path}")
                raise HTTPException(status_code=404, detail="Audio file not found")
            
            # Return audio file
            return FileResponse(
                content.audio_file_path,
                media_type="audio/mpeg",
                filename=f"content_{content_id}.mp3"
            )
            
        finally:
            session.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving audio: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve audio: {str(e)}")


@app.post("/api/v1/batch-download", response_model=BatchDownloadResponse)
@limiter.limit("5/minute")
async def batch_download(request: BatchDownloadRequest, response: Response):
    """
    Create batch download package for offline access.
    
    Supports up to 50 content items per package.
    
    Rate limit: 5 requests per minute
    """
    try:
        content_ids = request.content_ids
        include_audio = request.include_audio
        
        # Validate UUIDs
        valid_uuids = []
        for content_id in content_ids:
            try:
                valid_uuids.append(UUID(content_id))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid content ID format: {content_id}")
        
        # Retrieve content from database
        session = get_db().get_session()
        
        try:
            contents = session.query(ProcessedContent).filter(
                ProcessedContent.id.in_(valid_uuids)
            ).all()
            
            if not contents:
                raise HTTPException(status_code=404, detail="No content found for provided IDs")
            
            # Build batch package
            package_contents = []
            total_size = 0
            
            for content in contents:
                item = {
                    'id': str(content.id),
                    'simplified_text': content.simplified_text,
                    'translated_text': content.translated_text,
                    'language': content.language,
                    'grade_level': content.grade_level,
                    'subject': content.subject,
                    'ncert_alignment_score': content.ncert_alignment_score,
                    'metadata': content.content_metadata
                }
                
                if include_audio and content.audio_file_path:
                    item['audio_url'] = f"/api/v1/content/{content.id}/audio"
                    if os.path.exists(content.audio_file_path):
                        total_size += os.path.getsize(content.audio_file_path)
                
                # Add text size estimate
                text_size = len(content.translated_text.encode('utf-8'))
                total_size += text_size
                
                package_contents.append(item)
            
            # Validate 2G performance
            performance = cache_manager.validate_2g_performance(total_size)
            
            batch_response = BatchDownloadResponse(
                package_id=f"batch_{len(contents)}_items",
                item_count=len(contents),
                include_audio=include_audio,
                total_size_bytes=total_size,
                total_size_mb=round(total_size / (1024 * 1024), 2),
                performance=performance,
                contents=package_contents
            )
            
            logger.info(f"Batch package created: {len(contents)} items, {batch_response.total_size_mb}MB")
            
            return batch_response
            
        finally:
            session.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating batch download: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create batch download: {str(e)}")


@app.get("/api/v1/content/search", response_model=SearchResponse)
@limiter.limit("100/minute")
async def search_content(
    response: Response,
    language: Optional[str] = Query(None, description="Filter by language"),
    grade: Optional[int] = Query(None, ge=5, le=12, description="Filter by grade (5-12)"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results (max 100)"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """
    Search content with filters.
    
    Supports filtering by language, grade level, and subject.
    Results are paginated with a maximum of 100 items per request.
    
    Rate limit: 100 requests per minute
    """
    try:
        # Build query
        session = get_db().get_session()
        
        try:
            query = session.query(ProcessedContent)
            
            # Apply filters
            if language:
                query = query.filter(ProcessedContent.language == language)
            
            if grade:
                query = query.filter(ProcessedContent.grade_level == grade)
            
            if subject:
                query = query.filter(ProcessedContent.subject == subject)
            
            # Get total count
            total_count = query.count()
            
            # Apply pagination
            contents = query.order_by(ProcessedContent.created_at.desc()).offset(offset).limit(limit).all()
            
            # Build results
            results = []
            for content in contents:
                preview = content.translated_text[:200] + '...' if len(content.translated_text) > 200 else content.translated_text
                
                results.append(SearchResult(
                    id=str(content.id),
                    language=content.language,
                    grade_level=content.grade_level,
                    subject=content.subject,
                    translated_text_preview=preview,
                    ncert_alignment_score=content.ncert_alignment_score,
                    audio_available=content.audio_file_path is not None,
                    created_at=content.created_at.isoformat()
                ))
            
            search_response = SearchResponse(
                total_count=total_count,
                limit=limit,
                offset=offset,
                results=results,
                filters={
                    'language': language,
                    'grade': grade,
                    'subject': subject
                }
            )
            
            logger.info(f"Search completed: {len(results)} results")
            
            return search_response
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error searching content: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('FASTAPI_PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
