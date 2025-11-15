"""Cache manager for optimizing content delivery on low-bandwidth networks."""
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from uuid import UUID
import hashlib
import mimetypes


class CacheManager:
    """Manages content caching strategies for 2G network optimization."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory for cache storage
        """
        self.cache_dir = Path(cache_dir or os.getenv('CACHE_DIR', 'data/cache'))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # CDN cache directory for static assets
        self.cdn_cache_dir = self.cache_dir / 'cdn'
        self.cdn_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Progressive loading cache
        self.progressive_cache_dir = self.cache_dir / 'progressive'
        self.progressive_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache metadata
        self.metadata_file = self.cache_dir / 'cache_metadata.json'
    
    def lazy_load_audio(
        self,
        audio_path: str,
        chunk_size: int = 8192
    ) -> bytes:
        """
        Lazy load audio file in chunks for memory efficiency.
        
        Args:
            audio_path: Path to audio file
            chunk_size: Size of chunks to read (default 8KB)
            
        Yields:
            Audio data chunks
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        with open(audio_path, 'rb') as audio_file:
            while True:
                chunk = audio_file.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    
    def create_progressive_content(
        self,
        content_text: str,
        content_id: UUID,
        chunk_size: int = 1000
    ) -> List[str]:
        """
        Split large content into progressive chunks for faster initial load.
        
        Args:
            content_text: Full content text
            content_id: Content UUID
            chunk_size: Characters per chunk
            
        Returns:
            List of chunk file paths
        """
        chunks = []
        chunk_paths = []
        
        # Split content into chunks
        for i in range(0, len(content_text), chunk_size):
            chunk = content_text[i:i + chunk_size]
            chunks.append(chunk)
        
        # Save chunks
        for idx, chunk in enumerate(chunks):
            chunk_file = self.progressive_cache_dir / f"{content_id}_chunk_{idx}.txt"
            with open(chunk_file, 'w', encoding='utf-8') as f:
                f.write(chunk)
            chunk_paths.append(str(chunk_file))
        
        return chunk_paths
    
    def get_progressive_chunk(
        self,
        content_id: UUID,
        chunk_index: int
    ) -> Optional[str]:
        """
        Retrieve a specific progressive content chunk.
        
        Args:
            content_id: Content UUID
            chunk_index: Index of the chunk to retrieve
            
        Returns:
            Chunk content or None if not found
        """
        chunk_file = self.progressive_cache_dir / f"{content_id}_chunk_{chunk_index}.txt"
        
        if not chunk_file.exists():
            return None
        
        with open(chunk_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def cache_static_asset(
        self,
        asset_path: str,
        asset_type: str = 'auto'
    ) -> Dict[str, Any]:
        """
        Cache static assets with CDN-style optimization.
        
        Args:
            asset_path: Path to the asset file
            asset_type: Type of asset (auto-detect if 'auto')
            
        Returns:
            Dictionary with cache information
        """
        if not os.path.exists(asset_path):
            raise FileNotFoundError(f"Asset not found: {asset_path}")
        
        # Generate cache key based on file content
        with open(asset_path, 'rb') as f:
            content = f.read()
            cache_key = hashlib.md5(content).hexdigest()
        
        # Detect asset type
        if asset_type == 'auto':
            mime_type, _ = mimetypes.guess_type(asset_path)
            asset_type = mime_type or 'application/octet-stream'
        
        # Create cached asset path
        file_ext = Path(asset_path).suffix
        cached_asset_path = self.cdn_cache_dir / f"{cache_key}{file_ext}"
        
        # Copy to cache if not already cached
        if not cached_asset_path.exists():
            import shutil
            shutil.copy2(asset_path, cached_asset_path)
        
        return {
            'cache_key': cache_key,
            'cached_path': str(cached_asset_path),
            'asset_type': asset_type,
            'size_bytes': len(content),
            'cache_hit': cached_asset_path.exists()
        }
    
    def get_cached_asset(self, cache_key: str) -> Optional[str]:
        """
        Retrieve cached asset by cache key.
        
        Args:
            cache_key: MD5 hash of the asset
            
        Returns:
            Path to cached asset or None if not found
        """
        # Search for file with matching cache key
        for cached_file in self.cdn_cache_dir.glob(f"{cache_key}.*"):
            return str(cached_file)
        
        return None

    def optimize_audio_for_2g(
        self,
        audio_path: str,
        target_bitrate: str = '32k',
        target_format: str = 'mp3'
    ) -> str:
        """
        Optimize audio file for 2G network delivery.
        
        Args:
            audio_path: Path to original audio file
            target_bitrate: Target bitrate (default 32k for 2G)
            target_format: Target format (mp3 or ogg)
            
        Returns:
            Path to optimized audio file
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Generate optimized file path
        audio_file = Path(audio_path)
        optimized_path = self.cache_dir / f"{audio_file.stem}_optimized.{target_format}"
        
        # Note: In production, this would use ffmpeg or similar tool
        # For now, we'll create a placeholder that copies the file
        # Real implementation would be:
        # ffmpeg -i input.wav -b:a 32k -ar 22050 output.mp3
        
        import shutil
        shutil.copy2(audio_path, optimized_path)
        
        return str(optimized_path)
    
    def estimate_load_time(
        self,
        content_size_bytes: int,
        network_speed_kbps: int = 50  # 2G typical speed
    ) -> float:
        """
        Estimate content load time on 2G network.
        
        Args:
            content_size_bytes: Size of content in bytes
            network_speed_kbps: Network speed in kbps (default 50 for 2G)
            
        Returns:
            Estimated load time in seconds
        """
        # Convert bytes to kilobits
        content_size_kb = (content_size_bytes * 8) / 1024
        
        # Calculate load time
        load_time = content_size_kb / network_speed_kbps
        
        return load_time
    
    def validate_2g_performance(
        self,
        content_size_bytes: int,
        max_load_time_seconds: float = 5.0
    ) -> Dict[str, Any]:
        """
        Validate if content meets 2G performance requirements (<5s load time).
        
        Args:
            content_size_bytes: Size of content in bytes
            max_load_time_seconds: Maximum acceptable load time
            
        Returns:
            Dictionary with validation results
        """
        estimated_time = self.estimate_load_time(content_size_bytes)
        
        return {
            'content_size_bytes': content_size_bytes,
            'content_size_kb': round(content_size_bytes / 1024, 2),
            'estimated_load_time_seconds': round(estimated_time, 2),
            'max_load_time_seconds': max_load_time_seconds,
            'meets_requirement': estimated_time <= max_load_time_seconds,
            'network_speed_kbps': 50  # 2G speed
        }
    
    def compress_for_bandwidth(
        self,
        content: str,
        compression_level: int = 9
    ) -> bytes:
        """
        Compress content with maximum compression for low bandwidth.
        
        Args:
            content: Text content to compress
            compression_level: Gzip compression level (1-9, 9 is maximum)
            
        Returns:
            Compressed bytes
        """
        import gzip
        return gzip.compress(content.encode('utf-8'), compresslevel=compression_level)
    
    def get_compression_ratio(
        self,
        original_size: int,
        compressed_size: int
    ) -> float:
        """
        Calculate compression ratio.
        
        Args:
            original_size: Original content size in bytes
            compressed_size: Compressed content size in bytes
            
        Returns:
            Compression ratio (e.g., 0.3 means 30% of original size)
        """
        if original_size == 0:
            return 0.0
        
        return compressed_size / original_size
    
    def create_cdn_cache_headers(
        self,
        asset_type: str,
        max_age_seconds: int = 86400  # 24 hours default
    ) -> Dict[str, str]:
        """
        Generate CDN cache headers for static assets.
        
        Args:
            asset_type: MIME type of the asset
            max_age_seconds: Cache duration in seconds
            
        Returns:
            Dictionary of cache headers
        """
        return {
            'Cache-Control': f'public, max-age={max_age_seconds}',
            'Content-Type': asset_type,
            'ETag': hashlib.md5(str(time.time()).encode()).hexdigest(),
            'Vary': 'Accept-Encoding'
        }
    
    def simulate_2g_network(
        self,
        content_path: str,
        simulate: bool = True
    ) -> Dict[str, Any]:
        """
        Simulate 2G network conditions for testing.
        
        Args:
            content_path: Path to content file
            simulate: Whether to actually simulate delay
            
        Returns:
            Dictionary with simulation results
        """
        if not os.path.exists(content_path):
            raise FileNotFoundError(f"Content not found: {content_path}")
        
        file_size = os.path.getsize(content_path)
        estimated_time = self.estimate_load_time(file_size)
        
        if simulate:
            # Simulate network delay
            time.sleep(estimated_time)
        
        return {
            'file_size_bytes': file_size,
            'estimated_load_time': round(estimated_time, 2),
            'simulated': simulate,
            'meets_5s_requirement': estimated_time <= 5.0
        }
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_size = 0
        file_count = 0
        cache_types = {
            'cdn': 0,
            'progressive': 0,
            'other': 0
        }
        
        for cache_file in self.cache_dir.rglob('*'):
            if cache_file.is_file():
                total_size += cache_file.stat().st_size
                file_count += 1
                
                # Categorize by cache type
                if 'cdn' in str(cache_file):
                    cache_types['cdn'] += 1
                elif 'progressive' in str(cache_file):
                    cache_types['progressive'] += 1
                else:
                    cache_types['other'] += 1
        
        return {
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'file_count': file_count,
            'cache_types': cache_types,
            'cache_dir': str(self.cache_dir)
        }
