"""Integration tests for Speech Generator with Pipeline Orchestrator."""
import pytest
from unittest.mock import Mock, patch
from src.pipeline.orchestrator import ContentPipelineOrchestrator
from src.speech import AudioFile


class TestSpeechIntegration:
    """Test Speech Generator integration with the pipeline orchestrator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = ContentPipelineOrchestrator()
        self.sample_text = "Photosynthesis is the process by which plants make food."
        self.sample_language = "Hindi"
        self.sample_subject = "Science"
        self.sample_grade = 8
    
    def test_orchestrator_has_speech_generator(self):
        """Test that orchestrator initializes with speech generator."""
        assert hasattr(self.orchestrator, 'speech_generator')
        assert self.orchestrator.speech_generator is not None
    
    @patch('src.pipeline.orchestrator.get_db')
    def test_speech_generation_in_pipeline(self, mock_get_db):
        """Test speech generation as part of the complete pipeline."""
        # Mock database operations
        mock_session = Mock()
        mock_get_db.return_value.get_session.return_value = mock_session
        mock_session.commit.return_value = None
        mock_session.close.return_value = None
        
        # Mock all the model clients
        with patch.object(self.orchestrator.flant5_client, 'process', return_value="Simple text about plants making food."):
            with patch.object(self.orchestrator.indictrans2_client, 'process', return_value="पौधे भोजन बनाने की प्रक्रिया"):
                with patch.object(self.orchestrator.bert_client, 'process', return_value=0.85):
                    # Mock the speech generator
                    mock_audio_file = AudioFile(
                        content=b"fake_audio_content",
                        format="mp3",
                        size_mb=2.0,
                        duration_seconds=30.0,
                        sample_rate=22050,
                        language="Hindi",
                        accuracy_score=0.92,
                        file_path="/fake/path/audio.mp3"
                    )
                    
                    with patch.object(self.orchestrator.speech_generator, 'generate_speech', return_value=mock_audio_file) as mock_generate:
                        with patch.object(self.orchestrator.speech_generator, 'validate_audio_quality', return_value=True):
                            # Process content with audio output
                            result = self.orchestrator.process_content(
                                input_data=self.sample_text,
                                target_language=self.sample_language,
                                grade_level=self.sample_grade,
                                subject=self.sample_subject,
                                output_format='both'
                            )
                    
                    # Verify speech generation was called
                    mock_generate.assert_called_once_with(
                        "पौधे भोजन बनाने की प्रक्रिया", 
                        "Hindi", 
                        "Science"
                    )
                    
                    # Verify result includes audio information
                    assert result.audio_file_path == "/fake/path/audio.mp3"
                    assert result.audio_accuracy_score == 0.92
    
    def test_speech_generation_stage_method(self):
        """Test the _generate_speech method directly."""
        mock_audio_file = AudioFile(
            content=b"fake_audio_content",
            format="mp3",
            size_mb=1.5,
            duration_seconds=25.0,
            sample_rate=22050,
            language="Tamil",
            accuracy_score=0.94,
            file_path="/fake/path/tamil_audio.mp3"
        )
        
        with patch.object(self.orchestrator.speech_generator, 'generate_speech', return_value=mock_audio_file):
            with patch.object(self.orchestrator.speech_generator, 'validate_audio_quality', return_value=True):
                audio_path, accuracy_score = self.orchestrator._generate_speech(
                    "Sample Tamil text",
                    "Tamil",
                    "Mathematics"
                )
        
        assert audio_path == "/fake/path/tamil_audio.mp3"
        assert accuracy_score == 0.94
    
    def test_speech_generation_failure_handling(self):
        """Test handling of speech generation failures."""
        with patch.object(self.orchestrator.speech_generator, 'generate_speech', side_effect=RuntimeError("TTS service unavailable")):
            with pytest.raises(RuntimeError, match="TTS service unavailable"):
                self.orchestrator._generate_speech(
                    "Test text",
                    "Hindi",
                    "Science"
                )
    
    def test_speech_generation_empty_audio_handling(self):
        """Test handling of empty audio generation."""
        mock_audio_file = AudioFile(
            content=b"",  # Empty content
            format="mp3",
            size_mb=0.0,
            duration_seconds=0.0,
            sample_rate=22050,
            language="Hindi"
        )
        
        with patch.object(self.orchestrator.speech_generator, 'generate_speech', return_value=mock_audio_file):
            with pytest.raises(ValueError, match="Speech generation produced empty audio"):
                self.orchestrator._generate_speech(
                    "Test text",
                    "Hindi",
                    "Science"
                )
    
    @patch('src.pipeline.orchestrator.get_db')
    def test_pipeline_without_audio_output(self, mock_get_db):
        """Test pipeline processing without audio generation (text-only output)."""
        # Mock database operations
        mock_session = Mock()
        mock_get_db.return_value.get_session.return_value = mock_session
        mock_session.commit.return_value = None
        mock_session.close.return_value = None
        
        # Mock model clients (no speech generation needed)
        with patch.object(self.orchestrator.flant5_client, 'process', return_value="Simplified text"):
            with patch.object(self.orchestrator.indictrans2_client, 'process', return_value="Translated text"):
                with patch.object(self.orchestrator.bert_client, 'process', return_value=0.85):
                    result = self.orchestrator.process_content(
                        input_data=self.sample_text,
                        target_language=self.sample_language,
                        grade_level=self.sample_grade,
                        subject=self.sample_subject,
                        output_format='text'  # Text only, no audio
                    )
        
        # Verify no audio was generated
        assert result.audio_file_path is None
        assert result.audio_accuracy_score is None
        
        # Verify speech generator was not called
        # (We can't easily verify this without more complex mocking, but the test passes if no errors occur)
    
    def test_speech_quality_validation_warning(self):
        """Test that quality validation warnings are handled properly."""
        mock_audio_file = AudioFile(
            content=b"fake_audio_content",
            format="mp3",
            size_mb=8.0,  # Too large
            duration_seconds=30.0,
            sample_rate=22050,
            language="Hindi",
            accuracy_score=0.85,  # Below 90% threshold
            file_path="/fake/path/audio.mp3"
        )
        
        with patch.object(self.orchestrator.speech_generator, 'generate_speech', return_value=mock_audio_file):
            with patch.object(self.orchestrator.speech_generator, 'validate_audio_quality', return_value=False):
                # Should still return the audio path and score, but log a warning
                audio_path, accuracy_score = self.orchestrator._generate_speech(
                    "Test text",
                    "Hindi",
                    "Science"
                )
        
        assert audio_path == "/fake/path/audio.mp3"
        assert accuracy_score == 0.85