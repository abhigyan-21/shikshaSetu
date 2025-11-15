"""Example usage of ContentRepository and CacheManager."""
import os
import sys
from uuid import uuid4

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.repository import ContentRepository, CacheManager


def main():
    """Demonstrate ContentRepository and CacheManager functionality."""
    
    print("=" * 60)
    print("Content Repository & Cache Manager Example")
    print("=" * 60)
    
    # Initialize repository and cache manager
    repo = ContentRepository(cache_dir='data/cache')
    cache_mgr = CacheManager(cache_dir='data/cache')
    
    print("\n1. Storing Content")
    print("-" * 60)
    
    # Store sample content
    content = repo.store(
        original_text="Photosynthesis is the process by which plants make food.",
        simplified_text="Plants make their own food using sunlight.",
        translated_text="पौधे सूर्य के प्रकाश का उपयोग करके अपना भोजन बनाते हैं।",
        language="Hindi",
        grade_level=5,
        subject="Science",
        ncert_alignment_score=0.85,
        metadata={'topic': 'Photosynthesis', 'chapter': 1}
    )
    
    print(f"✓ Stored content with ID: {content.id}")
    print(f"  Language: {content.language}")
    print(f"  Grade: {content.grade_level}")
    print(f"  NCERT Score: {content.ncert_alignment_score}")
    
    print("\n2. Retrieving Content")
    print("-" * 60)
    
    # Retrieve content
    retrieved = repo.retrieve(content.id)
    if retrieved:
        print(f"✓ Retrieved content: {retrieved.id}")
        print(f"  Translated: {retrieved.translated_text[:50]}...")
    
    print("\n3. Batch Download Package")
    print("-" * 60)
    
    # Create batch download package
    package_path = repo.batch_download(
        content_ids=[content.id],
        package_name="science_grade5_hindi"
    )
    print(f"✓ Created package: {package_path}")
    
    # Check package size
    package_size = os.path.getsize(package_path)
    print(f"  Package size: {package_size} bytes ({package_size / 1024:.2f} KB)")
    
    print("\n4. Content Compression")
    print("-" * 60)
    
    # Test compression
    sample_text = "This is a sample educational content for testing compression."
    compressed = cache_mgr.compress_for_bandwidth(sample_text)
    
    original_size = len(sample_text.encode('utf-8'))
    compressed_size = len(compressed)
    ratio = cache_mgr.get_compression_ratio(original_size, compressed_size)
    
    print(f"✓ Original size: {original_size} bytes")
    print(f"  Compressed size: {compressed_size} bytes")
    print(f"  Compression ratio: {ratio:.2%}")
    
    print("\n5. 2G Network Performance Validation")
    print("-" * 60)
    
    # Validate 2G performance
    validation = cache_mgr.validate_2g_performance(
        content_size_bytes=package_size
    )
    
    print(f"✓ Content size: {validation['content_size_kb']} KB")
    print(f"  Estimated load time: {validation['estimated_load_time_seconds']}s")
    print(f"  Meets <5s requirement: {validation['meets_requirement']}")
    
    print("\n6. Progressive Content Loading")
    print("-" * 60)
    
    # Create progressive chunks
    long_content = "Lorem ipsum dolor sit amet. " * 100
    chunk_paths = cache_mgr.create_progressive_content(
        content_text=long_content,
        content_id=content.id,
        chunk_size=500
    )
    
    print(f"✓ Created {len(chunk_paths)} progressive chunks")
    print(f"  First chunk path: {chunk_paths[0]}")
    
    # Retrieve first chunk
    first_chunk = cache_mgr.get_progressive_chunk(content.id, 0)
    if first_chunk:
        print(f"  First chunk preview: {first_chunk[:50]}...")
    
    print("\n7. Cache Statistics")
    print("-" * 60)
    
    # Get cache statistics
    cache_stats = repo.get_cache_size()
    print(f"✓ Total cache size: {cache_stats['total_size_mb']} MB")
    print(f"  Cached files: {cache_stats['file_count']}")
    print(f"  Cache directory: {cache_stats['cache_dir']}")
    
    print("\n8. Offline Caching")
    print("-" * 60)
    
    # Cache for offline access
    cache_result = repo.cache_for_offline(
        content_ids=[content.id]
    )
    
    print(f"✓ Cached {cache_result['cached_count']} items")
    print(f"  Failed: {cache_result['failed_count']}")
    print(f"  Total requested: {cache_result['total_requested']}")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()
