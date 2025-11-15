"""Content Repository for storing and retrieving processed educational content."""
import gzip
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from uuid import UUID
import hashlib

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .database import get_db
from .models import ProcessedContent, StudentProfile


class ContentRepository:
    """Manages storage, retrieval, and offline caching of educational content."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the content repository.
        
        Args:
            cache_dir: Directory for offline content cache (default: data/cache)
        """
        self.db = get_db()
        self.cache_dir = Path(cache_dir or os.getenv('CACHE_DIR', 'data/cache'))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Audio cache directory
        self.audio_cache_dir = self.cache_dir / 'audio'
        self.audio_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Package cache directory
        self.package_cache_dir = self.cache_dir / 'packages'
        self.package_cache_dir.mkdir(parents=True, exist_ok=True)
    
    def store(
        self,
        original_text: str,
        simplified_text: str,
        translated_text: str,
        language: str,
        grade_level: int,
        subject: str,
        audio_file_path: Optional[str] = None,
        ncert_alignment_score: Optional[float] = None,
        audio_accuracy_score: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProcessedContent:
        """
        Store processed content in the database.
        
        Args:
            original_text: Original educational content
            simplified_text: Grade-level simplified text
            translated_text: Translated text in target language
            language: Target language code
            grade_level: Grade level (5-12)
            subject: Subject area
            audio_file_path: Path to generated audio file
            ncert_alignment_score: NCERT curriculum alignment score
            audio_accuracy_score: ASR validation score
            metadata: Additional metadata
            
        Returns:
            ProcessedContent: Stored content object
        """
        session = self.db.get_session()
        
        try:
            content = ProcessedContent(
                original_text=original_text,
                simplified_text=simplified_text,
                translated_text=translated_text,
                language=language,
                grade_level=grade_level,
                subject=subject,
                audio_file_path=audio_file_path,
                ncert_alignment_score=ncert_alignment_score,
                audio_accuracy_score=audio_accuracy_score,
                content_metadata=metadata or {}
            )
            
            session.add(content)
            session.commit()
            session.refresh(content)
            
            return content
            
        except Exception as e:
            session.rollback()
            raise Exception(f"Failed to store content: {str(e)}")
        finally:
            session.close()
    
    def retrieve(
        self,
        content_id: UUID,
        use_cache: bool = True
    ) -> Optional[ProcessedContent]:
        """
        Retrieve content by ID, checking cache first if offline.
        
        Args:
            content_id: UUID of the content
            use_cache: Whether to check offline cache first
            
        Returns:
            ProcessedContent or None if not found
        """
        # Try cache first if requested
        if use_cache:
            cached_content = self._retrieve_from_cache(content_id)
            if cached_content:
                return cached_content
        
        # Retrieve from database
        session = self.db.get_session()
        
        try:
            content = session.query(ProcessedContent).filter(
                ProcessedContent.id == content_id
            ).first()
            
            # Cache for offline access
            if content and use_cache:
                self._cache_content(content)
            
            return content
            
        finally:
            session.close()
    
    def retrieve_by_filters(
        self,
        language: Optional[str] = None,
        grade_level: Optional[int] = None,
        subject: Optional[str] = None,
        limit: int = 50
    ) -> List[ProcessedContent]:
        """
        Retrieve content by filters.
        
        Args:
            language: Filter by language
            grade_level: Filter by grade level
            subject: Filter by subject
            limit: Maximum number of results
            
        Returns:
            List of ProcessedContent objects
        """
        session = self.db.get_session()
        
        try:
            query = session.query(ProcessedContent)
            
            if language:
                query = query.filter(ProcessedContent.language == language)
            if grade_level:
                query = query.filter(ProcessedContent.grade_level == grade_level)
            if subject:
                query = query.filter(ProcessedContent.subject == subject)
            
            return query.limit(limit).all()
            
        finally:
            session.close()

    def batch_download(
        self,
        content_ids: List[UUID],
        package_name: Optional[str] = None
    ) -> str:
        """
        Create a downloadable package with multiple content items (up to 50).
        
        Args:
            content_ids: List of content UUIDs (max 50)
            package_name: Optional name for the package
            
        Returns:
            Path to the created package file
        """
        if len(content_ids) > 50:
            raise ValueError("Batch download limited to 50 items per package")
        
        session = self.db.get_session()
        
        try:
            # Retrieve all content items
            contents = session.query(ProcessedContent).filter(
                ProcessedContent.id.in_(content_ids)
            ).all()
            
            if not contents:
                raise ValueError("No content found for provided IDs")
            
            # Generate package name
            if not package_name:
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                package_name = f"content_package_{timestamp}"
            
            package_path = self.package_cache_dir / f"{package_name}.json.gz"
            
            # Prepare package data
            package_data = {
                'created_at': datetime.utcnow().isoformat(),
                'content_count': len(contents),
                'contents': []
            }
            
            for content in contents:
                content_data = {
                    'id': str(content.id),
                    'original_text': content.original_text,
                    'simplified_text': content.simplified_text,
                    'translated_text': content.translated_text,
                    'language': content.language,
                    'grade_level': content.grade_level,
                    'subject': content.subject,
                    'audio_file_path': content.audio_file_path,
                    'ncert_alignment_score': content.ncert_alignment_score,
                    'audio_accuracy_score': content.audio_accuracy_score,
                    'metadata': content.content_metadata
                }
                
                # Include audio data if available
                if content.audio_file_path and os.path.exists(content.audio_file_path):
                    with open(content.audio_file_path, 'rb') as audio_file:
                        import base64
                        content_data['audio_data'] = base64.b64encode(audio_file.read()).decode('utf-8')
                
                package_data['contents'].append(content_data)
            
            # Compress and save package
            with gzip.open(package_path, 'wt', encoding='utf-8') as f:
                json.dump(package_data, f)
            
            return str(package_path)
            
        finally:
            session.close()
    
    def cache_for_offline(
        self,
        content_ids: List[UUID],
        student_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Cache content for offline access.
        
        Args:
            content_ids: List of content UUIDs to cache
            student_id: Optional student profile ID to update cache metadata
            
        Returns:
            Dictionary with cache statistics
        """
        session = self.db.get_session()
        cached_count = 0
        failed_count = 0
        
        try:
            contents = session.query(ProcessedContent).filter(
                ProcessedContent.id.in_(content_ids)
            ).all()
            
            for content in contents:
                try:
                    self._cache_content(content)
                    cached_count += 1
                except Exception:
                    failed_count += 1
            
            # Update student profile cache metadata
            if student_id:
                student = session.query(StudentProfile).filter(
                    StudentProfile.id == student_id
                ).first()
                
                if student:
                    cache_metadata = student.offline_content_cache or {}
                    cache_metadata['cached_content_ids'] = [str(cid) for cid in content_ids]
                    cache_metadata['last_sync'] = datetime.utcnow().isoformat()
                    cache_metadata['cached_count'] = cached_count
                    
                    student.offline_content_cache = cache_metadata
                    session.commit()
            
            return {
                'cached_count': cached_count,
                'failed_count': failed_count,
                'total_requested': len(content_ids)
            }
            
        finally:
            session.close()
    
    def sync_when_online(
        self,
        student_id: UUID
    ) -> Dict[str, Any]:
        """
        Synchronize cached content when connectivity is restored.
        
        Args:
            student_id: Student profile ID
            
        Returns:
            Dictionary with sync statistics
        """
        session = self.db.get_session()
        
        try:
            student = session.query(StudentProfile).filter(
                StudentProfile.id == student_id
            ).first()
            
            if not student or not student.offline_content_cache:
                return {'synced_count': 0, 'message': 'No cache to sync'}
            
            cache_metadata = student.offline_content_cache
            cached_ids = cache_metadata.get('cached_content_ids', [])
            
            # Check for updates to cached content
            synced_count = 0
            for content_id_str in cached_ids:
                try:
                    content_id = UUID(content_id_str)
                    content = session.query(ProcessedContent).filter(
                        ProcessedContent.id == content_id
                    ).first()
                    
                    if content:
                        self._cache_content(content)
                        synced_count += 1
                except Exception:
                    continue
            
            # Update sync timestamp
            cache_metadata['last_sync'] = datetime.utcnow().isoformat()
            student.offline_content_cache = cache_metadata
            session.commit()
            
            return {
                'synced_count': synced_count,
                'total_cached': len(cached_ids),
                'last_sync': cache_metadata['last_sync']
            }
            
        finally:
            session.close()

    def _cache_content(self, content: ProcessedContent) -> None:
        """
        Cache content to local storage for offline access.
        
        Args:
            content: ProcessedContent object to cache
        """
        cache_file = self.cache_dir / f"{content.id}.json.gz"
        
        content_data = {
            'id': str(content.id),
            'original_text': content.original_text,
            'simplified_text': content.simplified_text,
            'translated_text': content.translated_text,
            'language': content.language,
            'grade_level': content.grade_level,
            'subject': content.subject,
            'audio_file_path': content.audio_file_path,
            'ncert_alignment_score': content.ncert_alignment_score,
            'audio_accuracy_score': content.audio_accuracy_score,
            'metadata': content.content_metadata,
            'cached_at': datetime.utcnow().isoformat()
        }
        
        # Cache audio file separately if available
        if content.audio_file_path and os.path.exists(content.audio_file_path):
            audio_cache_path = self.audio_cache_dir / f"{content.id}.audio"
            
            # Copy and compress audio file
            with open(content.audio_file_path, 'rb') as src:
                with gzip.open(audio_cache_path, 'wb') as dst:
                    dst.write(src.read())
            
            content_data['cached_audio_path'] = str(audio_cache_path)
        
        # Compress and save content metadata
        with gzip.open(cache_file, 'wt', encoding='utf-8') as f:
            json.dump(content_data, f)
    
    def _retrieve_from_cache(self, content_id: UUID) -> Optional[ProcessedContent]:
        """
        Retrieve content from local cache.
        
        Args:
            content_id: UUID of the content
            
        Returns:
            ProcessedContent object or None if not cached
        """
        cache_file = self.cache_dir / f"{content_id}.json.gz"
        
        if not cache_file.exists():
            return None
        
        try:
            with gzip.open(cache_file, 'rt', encoding='utf-8') as f:
                content_data = json.load(f)
            
            # Reconstruct ProcessedContent object
            content = ProcessedContent(
                id=UUID(content_data['id']),
                original_text=content_data['original_text'],
                simplified_text=content_data['simplified_text'],
                translated_text=content_data['translated_text'],
                language=content_data['language'],
                grade_level=content_data['grade_level'],
                subject=content_data['subject'],
                audio_file_path=content_data.get('cached_audio_path') or content_data.get('audio_file_path'),
                ncert_alignment_score=content_data.get('ncert_alignment_score'),
                audio_accuracy_score=content_data.get('audio_accuracy_score'),
                content_metadata=content_data.get('metadata', {})
            )
            
            return content
            
        except Exception:
            return None
    
    def compress_content(
        self,
        text: str,
        compression_level: int = 6
    ) -> bytes:
        """
        Compress text content using Gzip.
        
        Args:
            text: Text content to compress
            compression_level: Compression level (1-9, default 6)
            
        Returns:
            Compressed bytes
        """
        return gzip.compress(text.encode('utf-8'), compresslevel=compression_level)
    
    def decompress_content(self, compressed_data: bytes) -> str:
        """
        Decompress Gzip-compressed content.
        
        Args:
            compressed_data: Compressed bytes
            
        Returns:
            Decompressed text
        """
        return gzip.decompress(compressed_data).decode('utf-8')
    
    def get_cache_size(self) -> Dict[str, Any]:
        """
        Get statistics about cached content.
        
        Returns:
            Dictionary with cache size information
        """
        total_size = 0
        file_count = 0
        
        for cache_file in self.cache_dir.rglob('*'):
            if cache_file.is_file():
                total_size += cache_file.stat().st_size
                file_count += 1
        
        return {
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'file_count': file_count,
            'cache_dir': str(self.cache_dir)
        }
    
    def clear_cache(self, content_id: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Clear cached content.
        
        Args:
            content_id: Optional specific content ID to clear, or None to clear all
            
        Returns:
            Dictionary with cleared cache statistics
        """
        if content_id:
            # Clear specific content
            cache_file = self.cache_dir / f"{content_id}.json.gz"
            audio_cache_file = self.audio_cache_dir / f"{content_id}.audio"
            
            cleared_count = 0
            if cache_file.exists():
                cache_file.unlink()
                cleared_count += 1
            if audio_cache_file.exists():
                audio_cache_file.unlink()
                cleared_count += 1
            
            return {'cleared_count': cleared_count, 'content_id': str(content_id)}
        else:
            # Clear all cache
            import shutil
            cleared_count = len(list(self.cache_dir.rglob('*')))
            
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.audio_cache_dir.mkdir(parents=True, exist_ok=True)
            self.package_cache_dir.mkdir(parents=True, exist_ok=True)
            
            return {'cleared_count': cleared_count, 'message': 'All cache cleared'}
