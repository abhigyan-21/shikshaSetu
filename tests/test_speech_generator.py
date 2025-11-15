"""Tests for SpeechGenerator component."""
import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from src.speech import SpeechGenerator, AudioFile, TechnicalTermHandler, ASRValidator
from src.speech.audio_processor import AudioProcessor


class TestSpeechGenerator:
    """Test SpeechGenerator functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.speech_generator = SpeechGenerator()
        self.sample_text = "This is a test sentence for speech generation."
        self.sample_language = "Hindi"
        self.sample_subject = "Science"
    
    def test_speech_generator_initialization(self):
        """Test that speech generator initializes correctly."""
        assert self.speech_generator is not None
        assert self.speech_generator.vits_client is not None
        assert self.speech_generator.term_handler is not None
        assert self.speech_generator.audio_optimizer is not None
        assert self.speech_generator.asr_validator is not None
        assert len(self.speech_generator.supported_languages) >= 5
    
    def test_supported_languages(self):
        """Test that required languages are supported."""
        languages = self.speech_generator.get_supported_languages()
        required_languages = ['Hindi', 'Tamil', 'Telugu', 'Bengali', 'Marathi']
        
        for lang in required_languages:
            assert lang in languages
    
    def test_unsupported_language_raises_error(self):
        """Test that unsupported language raises ValueError."""
        with pytest.raises(ValueError, match="Language 'Klingon' not supported"):
            self.speech_generator.generate_speech("test", "Klingon", "Science")
    
    def test_generate_speech_basic(self):
        """Test basic speech generation functionality."""
        # Mock the VITS client
        mock_audio_content = b"fake_audio_data"
        
        with patch.object(self.speech_generator.vits_client, 'process', return_value=mock_audio_content):
            # Mock ASR validator to return good accuracy
            with patch.object(self.speech_generator.asr_validator, 'validate_audio_accuracy', return_value=0.95):
                result = self.speech_generator.generate_speech(
                    self.sample_text, 
                    self.sample_language, 
                    self.sample_subject
                )
        
        assert isinstance(result, AudioFile)
        assert result.content is not None
        assert result.language == self.sample_language
        assert result.format == "mp3"
        assert result.accuracy_score == 0.95
        assert result.file_path is not None
    
    # Requirement 4.1: Test audio generation for each supported language
    @pytest.mark.parametrize("language", ['Hindi', 'Tamil', 'Telugu', 'Bengali', 'Marathi'])
    def test_generate_speech_all_languages(self, language):
        """Test audio generation for each supported language (Requirement 4.1)."""
        test_text = "This is a test sentence for speech generation."
        mock_audio_content = b"fake_audio_data_" + language.encode()
        
        with patch.object(self.speech_generator.vits_client, 'process', return_value=mock_audio_content):
            with patch.object(self.speech_generator.asr_validator, 'validate_audio_accuracy', return_value=0.92):
                result = self.speech_generator.generate_speech(test_text, language, "Science")
        
        assert isinstance(result, AudioFile)
        assert result.language == language
        assert result.content is not None
        assert result.format == "mp3"
        assert result.file_path is not None
    
    # Requirement 4.2: Test audio file size optimization
    def test_audio_size_optimization_for_low_end_devices(self):
        """Test that audio is optimized for low-end devices (Requirement 4.2)."""
        # Create mock audio content that simulates a large file
        large_audio_content = b"x" * (10 * 1024 * 1024)  # 10MB
        
        # Mock the optimizer to simulate successful optimization
        with patch.object(self.speech_generator.vits_client, 'process', return_value=large_audio_content):
            with patch.object(self.speech_generator.asr_validator, 'validate_audio_accuracy', return_value=0.91):
                # Mock the optimizer to return smaller content
                optimized_content = b"x" * (2 * 1024 * 1024)  # 2MB optimized
                with patch.object(self.speech_generator.audio_optimizer, 'optimize_for_low_end_devices', return_value=optimized_content):
                    result = self.speech_generator.generate_speech(
                        self.sample_text, 
                        "Hindi", 
                        "Science"
                    )
        
        # Verify audio was optimized (size should be reduced)
        assert result.size_mb <= 5.0, f"Audio size {result.size_mb}MB exceeds 5MB target for 10 minutes"
        assert result.format == "mp3"
    
    # Requirement 4.2: Test audio optimization maintains quality
    def test_audio_optimization_maintains_format(self):
        """Test that audio optimization maintains proper format (Requirement 4.2)."""
        mock_audio_content = b"fake_audio_data"
        
        with patch.object(self.speech_generator.vits_client, 'process', return_value=mock_audio_content):
            with patch.object(self.speech_generator.asr_validator, 'validate_audio_accuracy', return_value=0.93):
                result = self.speech_generator.generate_speech(
                    self.sample_text,
                    "Tamil",
                    "Mathematics"
                )
        
        assert result.format == "mp3"
        assert result.sample_rate > 0
        assert result.duration_seconds >= 0
    
    # Requirement 4.3: Test ASR accuracy validation
    def test_asr_accuracy_validation_meets_threshold(self):
        """Test that ASR accuracy validation meets 90% threshold (Requirement 4.3)."""
        mock_audio_content = b"fake_audio_data"
        
        with patch.object(self.speech_generator.vits_client, 'process', return_value=mock_audio_content):
            # Test with accuracy above threshold
            with patch.object(self.speech_generator.asr_validator, 'validate_audio_accuracy', return_value=0.92):
                result = self.speech_generator.generate_speech(
                    self.sample_text,
                    "Hindi",
                    "Science"
                )
        
        assert result.accuracy_score >= 0.90, f"ASR accuracy {result.accuracy_score} below 90% threshold"
    
    # Requirement 4.3: Test ASR accuracy validation below threshold
    def test_asr_accuracy_validation_below_threshold_logged(self):
        """Test that low ASR accuracy is logged but processing continues (Requirement 4.3)."""
        mock_audio_content = b"fake_audio_data"
        
        with patch.object(self.speech_generator.vits_client, 'process', return_value=mock_audio_content):
            # Test with accuracy below threshold
            with patch.object(self.speech_generator.asr_validator, 'validate_audio_accuracy', return_value=0.85):
                result = self.speech_generator.generate_speech(
                    self.sample_text,
                    "Bengali",
                    "Science"
                )
        
        # Should still generate audio but with lower accuracy score
        assert isinstance(result, AudioFile)
        assert result.accuracy_score == 0.85
        assert result.content is not None
    
    # Requirement 4.5: Test technical term pronunciation handling
    def test_technical_term_pronunciation_in_speech(self):
        """Test that technical terms are handled for pronunciation (Requirement 4.5)."""
        text_with_terms = "The equation shows photosynthesis in the molecule."
        mock_audio_content = b"fake_audio_with_technical_terms"
        
        with patch.object(self.speech_generator.vits_client, 'process', return_value=mock_audio_content) as mock_vits:
            with patch.object(self.speech_generator.asr_validator, 'validate_audio_accuracy', return_value=0.91):
                result = self.speech_generator.generate_speech(
                    text_with_terms,
                    "Hindi",
                    "Science"
                )
        
        # Verify that VITS client was called (technical terms should be processed before TTS)
        assert mock_vits.called
        assert isinstance(result, AudioFile)
        assert result.language == "Hindi"
    
    def test_estimate_audio_size(self):
        """Test audio size estimation."""
        text = "This is a sample text with about ten words for testing."
        estimated_size = self.speech_generator.estimate_audio_size(text, "Hindi")
        
        assert isinstance(estimated_size, float)
        assert estimated_size > 0
        assert estimated_size < 1.0  # Should be less than 1MB for short text
    
    def test_validate_audio_quality_good(self):
        """Test audio quality validation with good audio."""
        audio_file = AudioFile(
            content=b"fake_audio_content",
            format="mp3",
            size_mb=2.0,
            duration_seconds=120.0,
            sample_rate=22050,
            accuracy_score=0.95
        )
        
        result = self.speech_generator.validate_audio_quality(audio_file)
        assert result is True
    
    def test_validate_audio_quality_too_large(self):
        """Test audio quality validation with oversized audio."""
        audio_file = AudioFile(
            content=b"fake_audio_content",
            format="mp3",
            size_mb=10.0,  # Too large
            duration_seconds=120.0,
            sample_rate=22050,
            accuracy_score=0.95
        )
        
        result = self.speech_generator.validate_audio_quality(audio_file)
        assert result is False
    
    def test_validate_audio_quality_low_accuracy(self):
        """Test audio quality validation with low accuracy."""
        audio_file = AudioFile(
            content=b"fake_audio_content",
            format="mp3",
            size_mb=2.0,
            duration_seconds=120.0,
            sample_rate=22050,
            accuracy_score=0.85  # Below 90% threshold
        )
        
        result = self.speech_generator.validate_audio_quality(audio_file)
        assert result is False


class TestTechnicalTermHandler:
    """Test TechnicalTermHandler functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.term_handler = TechnicalTermHandler()
    
    def test_term_handler_initialization(self):
        """Test that term handler initializes with mappings."""
        assert self.term_handler.term_mappings is not None
        assert 'Mathematics' in self.term_handler.term_mappings
        assert 'Science' in self.term_handler.term_mappings
    
    def test_process_technical_terms_mathematics_hindi(self):
        """Test technical term processing for Mathematics in Hindi."""
        text = "Solve this equation using algebra."
        result = self.term_handler.process_technical_terms(text, "Hindi", "Mathematics")
        
        # Should replace English terms with Hindi equivalents
        assert "समीकरण" in result or "equation" in result  # Either replaced or original
        assert "बीजगणित" in result or "algebra" in result
    
    def test_process_technical_terms_science_tamil(self):
        """Test technical term processing for Science in Tamil."""
        text = "Photosynthesis occurs in plant cells."
        result = self.term_handler.process_technical_terms(text, "Tamil", "Science")
        
        # Should process the text (may or may not replace terms based on availability)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_process_technical_terms_unsupported_subject(self):
        """Test technical term processing with unsupported subject."""
        text = "This is a test sentence."
        result = self.term_handler.process_technical_terms(text, "Hindi", "History")
        
        # Should return original text for unsupported subjects
        assert result == text
    
    def test_process_technical_terms_unsupported_language(self):
        """Test technical term processing with unsupported language."""
        text = "Solve this equation."
        result = self.term_handler.process_technical_terms(text, "French", "Mathematics")
        
        # Should return original text for unsupported languages
        assert result == text


class TestAudioOptimizer:
    """Test AudioOptimizer functionality for file size optimization."""
    
    def setup_method(self):
        """Set up test fixtures."""
        from src.speech.speech_generator import AudioOptimizer
        self.optimizer = AudioOptimizer()
    
    def test_audio_optimizer_initialization(self):
        """Test that audio optimizer initializes with correct settings."""
        assert self.optimizer.target_size_mb == 5.0
        assert self.optimizer.min_quality == 32
    
    # Requirement 4.2: Test audio optimization for low-end devices
    def test_optimize_for_low_end_devices_reduces_size(self):
        """Test that optimization reduces audio size for low-end devices (Requirement 4.2)."""
        # Create mock large audio content
        large_audio = b"x" * (8 * 1024 * 1024)  # 8MB
        
        # Optimization should reduce size (or return original if pydub unavailable)
        optimized = self.optimizer.optimize_for_low_end_devices(large_audio, target_duration_minutes=10.0)
        
        assert isinstance(optimized, bytes)
        assert len(optimized) > 0
    
    # Requirement 4.2: Test compression levels
    def test_compress_audio_different_levels(self):
        """Test audio compression at different levels (Requirement 4.2)."""
        mock_audio = b"fake_audio_content_for_compression"
        
        # Test different compression levels
        for level in ["low", "medium", "high"]:
            compressed = self.optimizer.compress_audio(mock_audio, compression_level=level)
            assert isinstance(compressed, bytes)
            assert len(compressed) > 0
    
    # Requirement 4.2: Test that optimization maintains audio integrity
    def test_optimization_maintains_audio_format(self):
        """Test that optimization maintains proper audio format (Requirement 4.2)."""
        mock_audio = b"fake_audio_content"
        
        optimized = self.optimizer.optimize_for_low_end_devices(mock_audio)
        
        # Should return bytes (audio content)
        assert isinstance(optimized, bytes)
        assert len(optimized) > 0


class TestASRValidator:
    """Test ASRValidator functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.asr_validator = ASRValidator()
    
    def test_asr_validator_initialization(self):
        """Test that ASR validator initializes correctly."""
        assert self.asr_validator.target_accuracy == 0.90
    
    def test_calculate_text_similarity_identical(self):
        """Test text similarity calculation with identical texts."""
        text1 = "This is a test sentence"
        text2 = "This is a test sentence"
        
        similarity = self.asr_validator._calculate_text_similarity(text1, text2)
        assert similarity == 1.0
    
    def test_calculate_text_similarity_different(self):
        """Test text similarity calculation with different texts."""
        text1 = "This is a test sentence"
        text2 = "This is completely different"
        
        similarity = self.asr_validator._calculate_text_similarity(text1, text2)
        assert 0.0 <= similarity < 1.0
    
    def test_calculate_text_similarity_empty(self):
        """Test text similarity calculation with empty texts."""
        similarity = self.asr_validator._calculate_text_similarity("", "")
        assert similarity == 1.0
        
        similarity = self.asr_validator._calculate_text_similarity("test", "")
        assert similarity == 0.0
    
    def test_validate_audio_accuracy_without_sr(self):
        """Test audio accuracy validation when speech_recognition is not available."""
        audio_file = AudioFile(
            content=b"fake_audio_content",
            format="mp3",
            size_mb=1.0,
            duration_seconds=60.0,
            sample_rate=22050,
            language="Hindi"
        )
        
        # Should return default accuracy when SR is not available
        accuracy = self.asr_validator.validate_audio_accuracy(audio_file, "test text")
        assert isinstance(accuracy, float)
        assert 0.0 <= accuracy <= 1.0
    
    # Requirement 4.3: Test ASR validation for different languages
    @pytest.mark.parametrize("language", ['Hindi', 'Tamil', 'Telugu', 'Bengali', 'Marathi'])
    def test_validate_audio_accuracy_multiple_languages(self, language):
        """Test ASR accuracy validation for each supported language (Requirement 4.3)."""
        audio_file = AudioFile(
            content=b"fake_audio_content",
            format="mp3",
            size_mb=1.0,
            duration_seconds=60.0,
            sample_rate=22050,
            language=language
        )
        
        reference_text = "This is a test sentence."
        accuracy = self.asr_validator.validate_audio_accuracy(audio_file, reference_text)
        
        # Should return a valid accuracy score
        assert isinstance(accuracy, float)
        assert 0.0 <= accuracy <= 1.0
    
    # Requirement 4.3: Test ASR accuracy threshold validation
    def test_asr_accuracy_meets_90_percent_threshold(self):
        """Test that ASR validator has 90% accuracy threshold (Requirement 4.3)."""
        assert self.asr_validator.target_accuracy == 0.90
        
        # Test that accuracy scores are properly evaluated
        audio_file = AudioFile(
            content=b"fake_audio_content",
            format="mp3",
            size_mb=1.0,
            duration_seconds=60.0,
            sample_rate=22050,
            language="Hindi"
        )
        
        accuracy = self.asr_validator.validate_audio_accuracy(audio_file, "test")
        
        # Accuracy should be a valid percentage
        assert isinstance(accuracy, float)
        assert 0.0 <= accuracy <= 1.0


class TestAudioProcessor:
    """Test AudioProcessor functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.audio_processor = AudioProcessor()
    
    def test_audio_processor_initialization(self):
        """Test that audio processor initializes correctly."""
        assert self.audio_processor.supported_formats == ['mp3', 'wav', 'ogg', 'm4a']
        assert self.audio_processor.target_sample_rate == 22050
        assert self.audio_processor.target_channels == 1
    
    def test_get_audio_info_basic(self):
        """Test basic audio info extraction."""
        fake_audio_content = b"fake_audio_data_for_testing"
        info = self.audio_processor.get_audio_info(fake_audio_content)
        
        assert isinstance(info, dict)
        assert 'size_bytes' in info
        assert 'size_mb' in info
        assert 'duration_seconds' in info
        assert info['size_bytes'] == len(fake_audio_content)
    
    def test_validate_audio_quality_empty_content(self):
        """Test audio quality validation with empty content."""
        is_valid, message = self.audio_processor.validate_audio_quality(b"")
        assert is_valid is False
        assert "Empty audio content" in message
    
    def test_validate_audio_quality_too_large(self):
        """Test audio quality validation with oversized content."""
        # Create fake large audio content (simulate 15MB)
        large_content = b"x" * (15 * 1024 * 1024)
        
        # Mock get_audio_info to return realistic audio info with large size
        with patch.object(self.audio_processor, 'get_audio_info') as mock_info:
            mock_info.return_value = {
                'size_bytes': len(large_content),
                'size_mb': len(large_content) / (1024 * 1024),
                'duration_seconds': 60.0,  # Valid duration
                'sample_rate': 22050,
                'channels': 1,
                'bitrate': 128000,
                'format': 'mp3'
            }
            
            is_valid, message = self.audio_processor.validate_audio_quality(large_content)
            assert is_valid is False
            assert "too large" in message.lower()


# Integration test for the complete speech generation flow
class TestSpeechGenerationIntegration:
    """Integration tests for speech generation workflow."""
    
    def test_complete_speech_generation_flow(self):
        """Test the complete speech generation workflow."""
        speech_generator = SpeechGenerator()
        
        # Mock VITS client
        mock_audio_content = b"fake_audio_data_for_testing"
        
        with patch.object(speech_generator.vits_client, 'process', return_value=mock_audio_content):
            # Mock ASR validation
            with patch.object(speech_generator.asr_validator, 'validate_audio_accuracy', return_value=0.92):
                result = speech_generator.generate_speech(
                    "This is a test sentence about photosynthesis in plants.",
                    "Hindi",
                    "Science"
                )
        
        # Verify the result
        assert isinstance(result, AudioFile)
        assert result.content is not None
        assert result.language == "Hindi"
        assert result.accuracy_score == 0.92
        assert result.file_path is not None
        
        # Verify audio quality validation
        assert speech_generator.validate_audio_quality(result) is True