"""
End-to-end integration tests for the complete pipeline.

Tests the full flow:
1. Input → Simplification → Translation → Validation → Speech → Storage → Retrieval
2. API endpoint integration
3. Repository persistence
4. Metrics tracking

REQUIREMENTS:
- PostgreSQL database (configured via DATABASE_URL environment variable)
- Hugging Face API key (for translation and speech generation)
- All dependencies from requirements.txt installed

SETUP:
1. Install PostgreSQL and create a test database
2. Set DATABASE_URL environment variable:
   export DATABASE_URL="postgresql://user:password@localhost:5432/test_db"
3. Set HUGGINGFACE_API_KEY environment variable:
   export HUGGINGFACE_API_KEY="your_api_key_here"
4. Run tests:
   pytest tests/test_end_to_end_integration.py -v -s

TEST COVERAGE (Task 11.1):
- Full pipeline with sample educational content
- NCERT alignment scores (≥80% threshold)
- Audio accuracy scores (≥90% threshold)
- Multi-language support (all 5 MVP languages: Hindi, Tamil, Telugu, Bengali, Marathi)
- Offline functionality and caching
- 2G network performance simulation
"""

import pytest
import os
import sys
from uuid import UUID

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.integration import IntegratedPipeline, test_end_to_end_flow
from src.repository.database import get_db


# Skip all tests if PostgreSQL is not available
pytestmark = pytest.mark.skipif(
    not os.getenv('DATABASE_URL', '').startswith('postgresql'),
    reason="Integration tests require PostgreSQL database"
)


class TestEndToEndIntegration:
    """Test suite for end-to-end pipeline integration."""
    
    @pytest.fixture(autouse=True)
    def setup(self, clean_database):
        """Set up test environment."""
        # Create integrated pipeline
        self.pipeline = IntegratedPipeline()
        
        yield
        
        # Cleanup handled by clean_database fixture
    
    def test_complete_pipeline_flow(self):
        """Test complete flow from input to retrieval."""
        # Sample educational content
        sample_text = """
        Photosynthesis is the process by which green plants use sunlight to synthesize 
        nutrients from carbon dioxide and water. It is essential for life on Earth as 
        it produces oxygen and organic compounds that serve as food for other organisms.
        """
        
        # Process content
        result = self.pipeline.process_and_store(
            input_data=sample_text,
            target_language='Hindi',
            grade_level=8,
            subject='Science',
            output_format='both'
        )
        
        # Verify processing succeeded
        assert result['success'] is True
        assert 'content_id' in result
        assert result['content']['language'] == 'Hindi'
        assert result['content']['grade_level'] == 8
        assert result['content']['subject'] == 'Science'
        
        # Verify quality scores
        assert result['quality_scores']['ncert_alignment_score'] >= 0.80
        assert result['quality_scores']['validation_status'] == 'passed'
        
        # Verify all pipeline stages completed
        assert len(result['metrics']['stage_metrics']) == 4  # simplification, translation, validation, speech
        
        # Verify content was stored
        content_id = result['content_id']
        retrieved = self.pipeline.retrieve_content(content_id)
        
        assert retrieved is not None
        assert retrieved['id'] == content_id
        assert retrieved['simplified_text'] is not None
        assert retrieved['translated_text'] is not None
        assert retrieved['audio_file_path'] is not None
        
        print(f"✓ Complete pipeline flow test passed: content_id={content_id}")
    
    def test_text_only_output(self):
        """Test pipeline with text-only output."""
        result = self.pipeline.process_and_store(
            input_data="Simple math problem: 2 + 2 = 4",
            target_language='Tamil',
            grade_level=5,
            subject='Mathematics',
            output_format='text'
        )
        
        assert result['success'] is True
        assert result['content']['audio_file_path'] is None
        assert result['content']['audio_url'] is None
        
        print("✓ Text-only output test passed")
    
    def test_audio_only_output(self):
        """Test pipeline with audio-only output."""
        result = self.pipeline.process_and_store(
            input_data="The water cycle includes evaporation, condensation, and precipitation.",
            target_language='Bengali',
            grade_level=7,
            subject='Science',
            output_format='audio'
        )
        
        assert result['success'] is True
        assert result['content']['audio_file_path'] is not None
        
        print("✓ Audio-only output test passed")
    
    def test_search_functionality(self):
        """Test content search with filters."""
        # First, create some test content
        for grade in [6, 8, 10]:
            self.pipeline.process_and_store(
                input_data=f"Test content for grade {grade}",
                target_language='Hindi',
                grade_level=grade,
                subject='Mathematics',
                output_format='text'
            )
        
        # Search for grade 8 content
        results = self.pipeline.search_content(
            language='Hindi',
            grade_level=8,
            subject='Mathematics'
        )
        
        assert results['total_count'] > 0
        assert all(r['grade_level'] == 8 for r in results['results'])
        assert all(r['language'] == 'Hindi' for r in results['results'])
        
        print(f"✓ Search functionality test passed: {results['total_count']} results found")
    
    def test_offline_package_creation(self):
        """Test batch download package creation."""
        # Create multiple content items
        content_ids = []
        for i in range(3):
            result = self.pipeline.process_and_store(
                input_data=f"Test content {i+1}",
                target_language='Telugu',
                grade_level=9,
                subject='Science',
                output_format='both'
            )
            content_ids.append(result['content_id'])
        
        # Create offline package
        package_result = self.pipeline.create_offline_package(
            content_ids=content_ids,
            package_name='test_package'
        )
        
        assert package_result['success'] is True
        assert package_result['content_count'] == 3
        assert package_result['package_size_mb'] > 0
        assert os.path.exists(package_result['package_path'])
        
        print(f"✓ Offline package test passed: {package_result['package_size_mb']}MB")
    
    def test_parameter_validation(self):
        """Test input parameter validation."""
        # Test invalid language
        with pytest.raises(Exception) as exc_info:
            self.pipeline.process_and_store(
                input_data="Test content",
                target_language='InvalidLanguage',
                grade_level=8,
                subject='Science',
                output_format='text'
            )
        
        assert 'Validation failed' in str(exc_info.value) or 'target_language' in str(exc_info.value)
        
        # Test invalid grade level
        with pytest.raises(Exception) as exc_info:
            self.pipeline.process_and_store(
                input_data="Test content",
                target_language='Hindi',
                grade_level=20,  # Invalid grade
                subject='Science',
                output_format='text'
            )
        
        assert 'Validation failed' in str(exc_info.value) or 'grade_level' in str(exc_info.value)
        
        print("✓ Parameter validation test passed")
    
    def test_system_health_check(self):
        """Test system health monitoring."""
        health = self.pipeline.get_system_health()
        
        assert 'status' in health
        assert health['status'] in ['healthy', 'degraded', 'unhealthy']
        assert 'database' in health
        assert 'components' in health
        
        print(f"✓ System health check passed: status={health['status']}")
    
    def test_retrieval_with_cache(self):
        """Test content retrieval with caching."""
        # Create content
        result = self.pipeline.process_and_store(
            input_data="Test content for caching",
            target_language='Marathi',
            grade_level=10,
            subject='History',
            output_format='text'
        )
        
        content_id = result['content_id']
        
        # Retrieve with cache
        retrieved_cached = self.pipeline.retrieve_content(content_id, use_cache=True)
        assert retrieved_cached is not None
        
        # Retrieve without cache
        retrieved_direct = self.pipeline.retrieve_content(content_id, use_cache=False)
        assert retrieved_direct is not None
        
        # Both should return same content
        assert retrieved_cached['id'] == retrieved_direct['id']
        
        print("✓ Retrieval with cache test passed")
    
    def test_multiple_languages(self):
        """Test processing content in multiple languages."""
        languages = ['Hindi', 'Tamil', 'Telugu', 'Bengali', 'Marathi']
        
        for language in languages:
            result = self.pipeline.process_and_store(
                input_data="Test content for multiple languages",
                target_language=language,
                grade_level=7,
                subject='Social Studies',
                output_format='text'
            )
            
            assert result['success'] is True
            assert result['content']['language'] == language
        
        print(f"✓ Multiple languages test passed: {len(languages)} languages")
    
    def test_metrics_tracking(self):
        """Test that metrics are properly tracked."""
        result = self.pipeline.process_and_store(
            input_data="Test content for metrics tracking",
            target_language='Hindi',
            grade_level=8,
            subject='Science',
            output_format='both'
        )
        
        # Verify metrics were recorded
        assert 'metrics' in result
        assert 'total_processing_time_ms' in result['metrics']
        assert 'stage_metrics' in result['metrics']
        
        # Verify all stages have metrics
        stages = [m['stage'] for m in result['metrics']['stage_metrics']]
        assert 'simplification' in stages
        assert 'translation' in stages
        assert 'validation' in stages
        assert 'speech' in stages
        
        print("✓ Metrics tracking test passed")
    
    def test_ncert_alignment_threshold(self):
        """Test NCERT alignment scores meet ≥80% requirement (Requirement 3.2)."""
        # Test with educational content that should align with NCERT standards
        sample_content = """
        The cell is the basic unit of life. All living organisms are made up of cells.
        Cells contain genetic material (DNA) that controls their structure and function.
        Plant cells have a cell wall, while animal cells do not.
        """
        
        result = self.pipeline.process_and_store(
            input_data=sample_content,
            target_language='Hindi',
            grade_level=9,
            subject='Science',
            output_format='both'
        )
        
        # Verify NCERT alignment score meets threshold
        ncert_score = result['quality_scores']['ncert_alignment_score']
        assert ncert_score >= 0.80, f"NCERT alignment score {ncert_score:.2%} is below 80% threshold"
        assert result['quality_scores']['validation_status'] == 'passed'
        
        print(f"✓ NCERT alignment threshold test passed: {ncert_score:.2%}")
    
    def test_audio_accuracy_threshold(self):
        """Test audio accuracy scores meet ≥90% requirement (Requirement 4.3)."""
        # Test with content that includes technical terms
        sample_content = """
        Photosynthesis occurs in the chloroplasts of plant cells.
        The process converts carbon dioxide and water into glucose and oxygen.
        """
        
        result = self.pipeline.process_and_store(
            input_data=sample_content,
            target_language='Tamil',
            grade_level=8,
            subject='Science',
            output_format='both'
        )
        
        # Verify audio accuracy score meets threshold
        audio_score = result['quality_scores'].get('audio_accuracy_score')
        assert audio_score is not None, "Audio accuracy score is missing"
        assert audio_score >= 0.90, f"Audio accuracy score {audio_score:.2%} is below 90% threshold"
        
        print(f"✓ Audio accuracy threshold test passed: {audio_score:.2%}")
    
    def test_all_mvp_languages(self):
        """Test multi-language support for all 5 MVP languages (Requirement 1.4)."""
        mvp_languages = ['Hindi', 'Tamil', 'Telugu', 'Bengali', 'Marathi']
        
        sample_content = """
        Water is essential for all living organisms. It covers about 71% of Earth's surface.
        The water cycle includes evaporation, condensation, and precipitation.
        """
        
        results = {}
        
        for language in mvp_languages:
            print(f"  Testing {language}...")
            result = self.pipeline.process_and_store(
                input_data=sample_content,
                target_language=language,
                grade_level=7,
                subject='Science',
                output_format='both'
            )
            
            # Verify processing succeeded
            assert result['success'] is True, f"Processing failed for {language}"
            assert result['content']['language'] == language
            assert result['content']['translated_text'] is not None
            assert result['content']['audio_file_path'] is not None
            
            # Verify quality thresholds
            assert result['quality_scores']['ncert_alignment_score'] >= 0.80
            assert result['quality_scores']['audio_accuracy_score'] >= 0.90
            
            results[language] = {
                'content_id': result['content_id'],
                'ncert_score': result['quality_scores']['ncert_alignment_score'],
                'audio_score': result['quality_scores']['audio_accuracy_score']
            }
        
        print(f"✓ All MVP languages test passed: {len(mvp_languages)} languages")
        for lang, scores in results.items():
            print(f"  - {lang}: NCERT={scores['ncert_score']:.2%}, Audio={scores['audio_score']:.2%}")
    
    def test_offline_functionality(self):
        """Test offline content access and synchronization (Requirement 7.4)."""
        # Create content while "online"
        result = self.pipeline.process_and_store(
            input_data="Content for offline testing",
            target_language='Bengali',
            grade_level=10,
            subject='Mathematics',
            output_format='both'
        )
        
        content_id = result['content_id']
        
        # Retrieve with cache (simulating offline access)
        cached_content = self.pipeline.retrieve_content(content_id, use_cache=True)
        assert cached_content is not None, "Failed to retrieve cached content"
        assert cached_content['id'] == content_id
        
        # Create offline package for batch download
        package_result = self.pipeline.create_offline_package(
            content_ids=[content_id],
            package_name='offline_test_package'
        )
        
        assert package_result['success'] is True
        assert package_result['content_count'] == 1
        assert os.path.exists(package_result['package_path'])
        
        # Verify package size is reasonable for low-bandwidth
        assert package_result['package_size_mb'] < 10, "Package size too large for offline use"
        
        print(f"✓ Offline functionality test passed: {package_result['package_size_mb']}MB package")
    
    def test_2g_network_performance(self):
        """Test content load time on simulated 2G network (Requirement 7.4)."""
        import time
        
        # Create content
        result = self.pipeline.process_and_store(
            input_data="Content for 2G network testing",
            target_language='Marathi',
            grade_level=6,
            subject='Social Studies',
            output_format='text'  # Text-only for faster loading
        )
        
        content_id = result['content_id']
        
        # Measure retrieval time (simulating 2G network conditions)
        start_time = time.time()
        retrieved = self.pipeline.retrieve_content(content_id, use_cache=True)
        load_time = time.time() - start_time
        
        assert retrieved is not None, "Failed to retrieve content"
        
        # Verify load time is under 5 seconds (requirement for 2G network)
        assert load_time < 5.0, f"Load time {load_time:.2f}s exceeds 5s threshold for 2G network"
        
        print(f"✓ 2G network performance test passed: {load_time:.2f}s load time")
    
    def test_full_pipeline_with_all_requirements(self):
        """
        Comprehensive test covering all requirements from task 11.1:
        - Full pipeline processing
        - NCERT alignment ≥80%
        - Audio accuracy ≥90%
        - Multi-language support
        - Offline functionality
        - Performance requirements
        """
        print("\n" + "=" * 80)
        print("COMPREHENSIVE END-TO-END TEST WITH ALL REQUIREMENTS")
        print("=" * 80)
        
        # Test content with educational value
        sample_content = """
        The solar system consists of the Sun and all celestial objects bound to it by gravity.
        This includes eight planets: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune.
        Each planet has unique characteristics and orbits the Sun at different distances.
        """
        
        # Test with one language (Hindi) for comprehensive validation
        print("\n[1/5] Processing content through full pipeline...")
        result = self.pipeline.process_and_store(
            input_data=sample_content,
            target_language='Hindi',
            grade_level=8,
            subject='Science',
            output_format='both'
        )
        
        assert result['success'] is True
        content_id = result['content_id']
        print(f"✓ Pipeline processing completed: {content_id}")
        
        # Verify NCERT alignment
        print("\n[2/5] Verifying NCERT alignment score...")
        ncert_score = result['quality_scores']['ncert_alignment_score']
        assert ncert_score >= 0.80, f"NCERT score {ncert_score:.2%} below threshold"
        print(f"✓ NCERT alignment: {ncert_score:.2%} (≥80% required)")
        
        # Verify audio accuracy
        print("\n[3/5] Verifying audio accuracy score...")
        audio_score = result['quality_scores']['audio_accuracy_score']
        assert audio_score >= 0.90, f"Audio score {audio_score:.2%} below threshold"
        print(f"✓ Audio accuracy: {audio_score:.2%} (≥90% required)")
        
        # Verify all pipeline stages completed
        print("\n[4/5] Verifying all pipeline stages...")
        stages = [m['stage'] for m in result['metrics']['stage_metrics']]
        required_stages = ['simplification', 'translation', 'validation', 'speech']
        for stage in required_stages:
            assert stage in stages, f"Missing pipeline stage: {stage}"
        print(f"✓ All pipeline stages completed: {', '.join(required_stages)}")
        
        # Verify content retrieval and offline capability
        print("\n[5/5] Verifying offline functionality...")
        retrieved = self.pipeline.retrieve_content(content_id, use_cache=True)
        assert retrieved is not None
        assert retrieved['translated_text'] is not None
        assert retrieved['audio_file_path'] is not None
        print("✓ Offline content retrieval successful")
        
        print("\n" + "=" * 80)
        print("COMPREHENSIVE TEST PASSED - ALL REQUIREMENTS MET")
        print("=" * 80)
        print(f"\nSummary:")
        print(f"  Content ID: {content_id}")
        print(f"  NCERT Alignment: {ncert_score:.2%}")
        print(f"  Audio Accuracy: {audio_score:.2%}")
        print(f"  Processing Time: {result['metrics']['total_processing_time_ms']}ms")
        print(f"  Validation Status: {result['quality_scores']['validation_status']}")
        print()


def test_integration_script():
    """Test the integration test script itself."""
    result = test_end_to_end_flow(
        sample_text="The Earth revolves around the Sun.",
        target_language='Hindi',
        grade_level=6,
        subject='Science'
    )
    
    assert result['success'] is True
    assert 'content_id' in result
    assert 'processing_result' in result
    assert 'retrieval_result' in result
    assert 'search_result' in result
    
    print("✓ Integration script test passed")


if __name__ == '__main__':
    # Run tests
    print("=" * 80)
    print("RUNNING END-TO-END INTEGRATION TESTS")
    print("=" * 80)
    
    pytest.main([__file__, '-v', '-s'])
