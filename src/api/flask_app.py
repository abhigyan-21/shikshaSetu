"""Flask application for content processing API."""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import BadRequest
import os
import logging
from uuid import UUID
from typing import Optional
import gzip
import io

from ..pipeline.orchestrator import ContentPipelineOrchestrator, PipelineValidationError, PipelineStageError
from ..repository.database import get_db
from ..repository.models import ProcessedContent
from ..repository.cache_manager import CacheManager
from ..integration import get_integrated_pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size

# Enable CORS for frontend access
CORS(app)

# Rate limiting to prevent API abuse
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.getenv('REDIS_URL', 'memory://')
)

# Initialize integrated pipeline (connects all components)
integrated_pipeline = get_integrated_pipeline()
cache_manager = CacheManager()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'education-content-api'}), 200


@app.route('/api/process-content', methods=['POST'])
@limiter.limit("10 per minute")
def process_content():
    """
    Process educational content through the pipeline.
    
    Request Body:
        {
            "input_data": "Text content to process",
            "target_language": "Hindi",
            "grade_level": 8,
            "subject": "Mathematics",
            "output_format": "both"
        }
    
    Returns:
        Processed content with ID, translations, audio, and quality scores
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        # Validate required parameters
        required_fields = ['input_data', 'target_language', 'grade_level', 'subject', 'output_format']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing': missing_fields
            }), 400
        
        # Extract parameters
        input_data = data['input_data']
        target_language = data['target_language']
        grade_level = data['grade_level']
        subject = data['subject']
        output_format = data['output_format']
        
        logger.info(f"Processing content request: language={target_language}, grade={grade_level}, subject={subject}")
        
        # Process through integrated pipeline (orchestrator + repository + metrics)
        result = integrated_pipeline.process_and_store(
            input_data=input_data,
            target_language=target_language,
            grade_level=grade_level,
            subject=subject,
            output_format=output_format
        )
        
        # Build response from integrated result
        response = {
            'id': result['content_id'],
            'simplified_text': result['content']['simplified_text'],
            'translated_text': result['content']['translated_text'],
            'language': result['content']['language'],
            'grade_level': result['content']['grade_level'],
            'subject': result['content']['subject'],
            'audio_url': result['content']['audio_url'],
            'ncert_alignment_score': result['quality_scores']['ncert_alignment_score'],
            'audio_accuracy_score': result['quality_scores']['audio_accuracy_score'],
            'validation_status': result['quality_scores']['validation_status'],
            'metadata': result['metadata']
        }
        
        logger.info(f"Content processed successfully: content_id={result['content_id']}")
        
        return jsonify(response), 201
        
    except PipelineValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        return jsonify({'error': 'Validation failed', 'details': str(e)}), 400
        
    except PipelineStageError as e:
        logger.error(f"Pipeline stage error: {str(e)}")
        return jsonify({'error': 'Processing failed', 'details': str(e)}), 500
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@app.route('/api/content/<content_id>', methods=['GET'])
@limiter.limit("100 per minute")
def get_content(content_id: str):
    """
    Retrieve processed content by ID.
    
    Args:
        content_id: UUID of the processed content
    
    Query Parameters:
        compress: If 'true', return gzip-compressed content for bandwidth optimization
    
    Returns:
        Processed content with all translations and metadata
    """
    try:
        # Validate UUID format
        try:
            content_uuid = UUID(content_id)
        except ValueError:
            return jsonify({'error': 'Invalid content ID format'}), 400
        
        # Retrieve from database
        session = get_db().get_session()
        
        try:
            content = session.query(ProcessedContent).filter_by(id=content_uuid).first()
            
            if not content:
                return jsonify({'error': 'Content not found'}), 404
            
            # Build response
            response = {
                'id': str(content.id),
                'original_text': content.original_text,
                'simplified_text': content.simplified_text,
                'translated_text': content.translated_text,
                'language': content.language,
                'grade_level': content.grade_level,
                'subject': content.subject,
                'audio_url': f"/api/content/{content.id}/audio" if content.audio_file_path else None,
                'ncert_alignment_score': content.ncert_alignment_score,
                'audio_accuracy_score': content.audio_accuracy_score,
                'created_at': content.created_at.isoformat(),
                'metadata': content.content_metadata
            }
            
            # Check if compression is requested
            compress = request.args.get('compress', 'false').lower() == 'true'
            
            if compress:
                # Compress response for bandwidth optimization
                compressed_data = cache_manager.compress_for_bandwidth(
                    str(response),
                    compression_level=9
                )
                
                return send_file(
                    io.BytesIO(compressed_data),
                    mimetype='application/gzip',
                    as_attachment=True,
                    download_name=f'content_{content_id}.json.gz'
                )
            
            logger.info(f"Content retrieved: content_id={content_id}")
            
            return jsonify(response), 200
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error retrieving content: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve content', 'details': str(e)}), 500


@app.route('/api/content/<content_id>/audio', methods=['GET'])
@limiter.limit("50 per minute")
def get_content_audio(content_id: str):
    """
    Retrieve audio file for processed content.
    
    Args:
        content_id: UUID of the processed content
    
    Returns:
        Audio file (MP3/OGG format)
    """
    try:
        # Validate UUID format
        try:
            content_uuid = UUID(content_id)
        except ValueError:
            return jsonify({'error': 'Invalid content ID format'}), 400
        
        # Retrieve from database
        session = get_db().get_session()
        
        try:
            content = session.query(ProcessedContent).filter_by(id=content_uuid).first()
            
            if not content:
                return jsonify({'error': 'Content not found'}), 404
            
            if not content.audio_file_path:
                return jsonify({'error': 'Audio not available for this content'}), 404
            
            # Check if audio file exists
            if not os.path.exists(content.audio_file_path):
                logger.error(f"Audio file not found: {content.audio_file_path}")
                return jsonify({'error': 'Audio file not found'}), 404
            
            # Return audio file
            return send_file(
                content.audio_file_path,
                mimetype='audio/mpeg',
                as_attachment=False
            )
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error retrieving audio: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve audio', 'details': str(e)}), 500


@app.route('/api/batch-download', methods=['POST'])
@limiter.limit("5 per minute")
def batch_download():
    """
    Create batch download package for offline access.
    
    Request Body:
        {
            "content_ids": ["uuid1", "uuid2", ...],
            "include_audio": true
        }
    
    Returns:
        Compressed package with up to 50 content items
    """
    try:
        data = request.get_json()
        
        if not data or 'content_ids' not in data:
            return jsonify({'error': 'Missing required field: content_ids'}), 400
        
        content_ids = data['content_ids']
        include_audio = data.get('include_audio', True)
        
        # Validate batch size (max 50 items)
        if len(content_ids) > 50:
            return jsonify({
                'error': 'Batch size exceeds maximum',
                'max_items': 50,
                'requested': len(content_ids)
            }), 400
        
        # Validate UUIDs
        valid_uuids = []
        for content_id in content_ids:
            try:
                valid_uuids.append(UUID(content_id))
            except ValueError:
                return jsonify({'error': f'Invalid content ID format: {content_id}'}), 400
        
        # Retrieve content from database
        session = get_db().get_session()
        
        try:
            contents = session.query(ProcessedContent).filter(
                ProcessedContent.id.in_(valid_uuids)
            ).all()
            
            if not contents:
                return jsonify({'error': 'No content found for provided IDs'}), 404
            
            # Build batch package
            package = {
                'package_id': f"batch_{len(contents)}_items",
                'item_count': len(contents),
                'include_audio': include_audio,
                'contents': []
            }
            
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
                    item['audio_url'] = f"/api/content/{content.id}/audio"
                    if os.path.exists(content.audio_file_path):
                        total_size += os.path.getsize(content.audio_file_path)
                
                # Add text size estimate
                text_size = len(content.translated_text.encode('utf-8'))
                total_size += text_size
                
                package['contents'].append(item)
            
            # Add package metadata
            package['total_size_bytes'] = total_size
            package['total_size_mb'] = round(total_size / (1024 * 1024), 2)
            
            # Validate 2G performance
            performance = cache_manager.validate_2g_performance(total_size)
            package['performance'] = performance
            
            logger.info(f"Batch package created: {len(contents)} items, {package['total_size_mb']}MB")
            
            return jsonify(package), 200
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error creating batch download: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to create batch download', 'details': str(e)}), 500


@app.route('/api/content/search', methods=['GET'])
@limiter.limit("100 per minute")
def search_content():
    """
    Search content with filters.
    
    Query Parameters:
        language: Filter by language (e.g., Hindi, Tamil)
        grade: Filter by grade level (5-12)
        subject: Filter by subject (e.g., Mathematics, Science)
        limit: Maximum number of results (default 20, max 100)
        offset: Pagination offset (default 0)
    
    Returns:
        List of matching content items with metadata
    """
    try:
        # Extract query parameters
        language = request.args.get('language')
        grade = request.args.get('grade', type=int)
        subject = request.args.get('subject')
        limit = min(request.args.get('limit', 20, type=int), 100)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        session = get_db().get_session()
        
        try:
            query = session.query(ProcessedContent)
            
            # Apply filters
            if language:
                query = query.filter(ProcessedContent.language == language)
            
            if grade:
                # Validate grade range
                if grade < 5 or grade > 12:
                    return jsonify({'error': 'Grade must be between 5 and 12'}), 400
                query = query.filter(ProcessedContent.grade_level == grade)
            
            if subject:
                query = query.filter(ProcessedContent.subject == subject)
            
            # Get total count
            total_count = query.count()
            
            # Apply pagination
            contents = query.order_by(ProcessedContent.created_at.desc()).offset(offset).limit(limit).all()
            
            # Build response
            results = []
            for content in contents:
                results.append({
                    'id': str(content.id),
                    'language': content.language,
                    'grade_level': content.grade_level,
                    'subject': content.subject,
                    'translated_text_preview': content.translated_text[:200] + '...' if len(content.translated_text) > 200 else content.translated_text,
                    'ncert_alignment_score': content.ncert_alignment_score,
                    'audio_available': content.audio_file_path is not None,
                    'created_at': content.created_at.isoformat()
                })
            
            response = {
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'results': results,
                'filters': {
                    'language': language,
                    'grade': grade,
                    'subject': subject
                }
            }
            
            logger.info(f"Search completed: {len(results)} results, filters={response['filters']}")
            
            return jsonify(response), 200
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error searching content: {str(e)}", exc_info=True)
        return jsonify({'error': 'Search failed', 'details': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(429)
def rate_limit_exceeded(error):
    """Handle rate limit errors."""
    return jsonify({'error': 'Rate limit exceeded', 'details': str(error)}), 429


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
