"""Basic tests for ContentPipelineOrchestrator parameter validation."""
import pytest
import sys
import os

# Mock the database module before importing orchestrator
from unittest.mock import MagicMock
sys.modules['src.repository.database'] = MagicMock()

from src.pipeline.orchestrator import (
    ContentPipelineOrchestrator,
    PipelineValidationError
)


class TestParameterValidation:
    """Test parameter validation in ContentPipelineOrchestrator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = ContentPipelineOrchestrator()
    
    def test_valid_parameters(self):
        """Test that valid parameters pass validation."""
        # Should not raise any exception
        self.orchestrator.validate_parameters(
            input_data="Sample educational content about mathematics",
            target_language="Hindi",
            grade_level=8,
            subject="Mathematics",
            output_format="text"
        )
    
    def test_empty_input_data(self):
        """Test that empty input_data raises validation error."""
        with pytest.raises(PipelineValidationError) as exc_info:
            self.orchestrator.validate_parameters(
                input_data="",
                target_language="Hindi",
                grade_level=8,
                subject="Mathematics",
                output_format="text"
            )
        assert "input_data cannot be empty" in str(exc_info.value)
    
    def test_invalid_language(self):
        """Test that unsupported language raises validation error."""
        with pytest.raises(PipelineValidationError) as exc_info:
            self.orchestrator.validate_parameters(
                input_data="Sample content",
                target_language="French",
                grade_level=8,
                subject="Mathematics",
                output_format="text"
            )
        assert "target_language must be one of" in str(exc_info.value)
    
    def test_invalid_grade_level_too_low(self):
        """Test that grade level below minimum raises validation error."""
        with pytest.raises(PipelineValidationError) as exc_info:
            self.orchestrator.validate_parameters(
                input_data="Sample content",
                target_language="Hindi",
                grade_level=3,
                subject="Mathematics",
                output_format="text"
            )
        assert "grade_level must be between" in str(exc_info.value)
    
    def test_invalid_grade_level_too_high(self):
        """Test that grade level above maximum raises validation error."""
        with pytest.raises(PipelineValidationError) as exc_info:
            self.orchestrator.validate_parameters(
                input_data="Sample content",
                target_language="Hindi",
                grade_level=15,
                subject="Mathematics",
                output_format="text"
            )
        assert "grade_level must be between" in str(exc_info.value)
    
    def test_invalid_grade_level_type(self):
        """Test that non-integer grade level raises validation error."""
        with pytest.raises(PipelineValidationError) as exc_info:
            self.orchestrator.validate_parameters(
                input_data="Sample content",
                target_language="Hindi",
                grade_level="8",
                subject="Mathematics",
                output_format="text"
            )
        assert "grade_level must be an integer" in str(exc_info.value)
    
    def test_invalid_subject(self):
        """Test that unsupported subject raises validation error."""
        with pytest.raises(PipelineValidationError) as exc_info:
            self.orchestrator.validate_parameters(
                input_data="Sample content",
                target_language="Hindi",
                grade_level=8,
                subject="Art",
                output_format="text"
            )
        assert "subject must be one of" in str(exc_info.value)
    
    def test_invalid_output_format(self):
        """Test that unsupported output format raises validation error."""
        with pytest.raises(PipelineValidationError) as exc_info:
            self.orchestrator.validate_parameters(
                input_data="Sample content",
                target_language="Hindi",
                grade_level=8,
                subject="Mathematics",
                output_format="video"
            )
        assert "output_format must be one of" in str(exc_info.value)
    
    def test_multiple_validation_errors(self):
        """Test that multiple validation errors are reported together."""
        with pytest.raises(PipelineValidationError) as exc_info:
            self.orchestrator.validate_parameters(
                input_data="",
                target_language="French",
                grade_level=20,
                subject="Art",
                output_format="video"
            )
        error_message = str(exc_info.value)
        assert "input_data cannot be empty" in error_message
        assert "target_language must be one of" in error_message
        assert "grade_level must be between" in error_message
        assert "subject must be one of" in error_message
        assert "output_format must be one of" in error_message
    
    def test_all_supported_languages(self):
        """Test that all supported languages pass validation."""
        for language in self.orchestrator.SUPPORTED_LANGUAGES:
            self.orchestrator.validate_parameters(
                input_data="Sample content",
                target_language=language,
                grade_level=8,
                subject="Mathematics",
                output_format="text"
            )
    
    def test_all_supported_subjects(self):
        """Test that all supported subjects pass validation."""
        for subject in self.orchestrator.SUPPORTED_SUBJECTS:
            self.orchestrator.validate_parameters(
                input_data="Sample content",
                target_language="Hindi",
                grade_level=8,
                subject=subject,
                output_format="text"
            )
    
    def test_all_supported_formats(self):
        """Test that all supported output formats pass validation."""
        for output_format in self.orchestrator.SUPPORTED_FORMATS:
            self.orchestrator.validate_parameters(
                input_data="Sample content",
                target_language="Hindi",
                grade_level=8,
                subject="Mathematics",
                output_format=output_format
            )
    
    def test_all_grade_levels(self):
        """Test that all grade levels in range pass validation."""
        for grade in range(5, 13):  # 5 to 12 inclusive
            self.orchestrator.validate_parameters(
                input_data="Sample content",
                target_language="Hindi",
                grade_level=grade,
                subject="Mathematics",
                output_format="text"
            )


class TestOrchestratorInitialization:
    """Test ContentPipelineOrchestrator initialization."""
    
    def test_orchestrator_creates_clients(self):
        """Test that orchestrator initializes all model clients."""
        orchestrator = ContentPipelineOrchestrator()
        
        assert orchestrator.flant5_client is not None
        assert orchestrator.indictrans2_client is not None
        assert orchestrator.bert_client is not None
        assert orchestrator.vits_client is not None
    
    def test_orchestrator_initializes_metrics(self):
        """Test that orchestrator initializes empty metrics list."""
        orchestrator = ContentPipelineOrchestrator()
        
        assert orchestrator.metrics == []
    
    def test_orchestrator_constants(self):
        """Test that orchestrator has correct constants."""
        orchestrator = ContentPipelineOrchestrator()
        
        assert orchestrator.MIN_GRADE == 5
        assert orchestrator.MAX_GRADE == 12
        assert orchestrator.MAX_RETRIES == 3
        assert orchestrator.RETRY_BACKOFF_BASE == 2
        assert orchestrator.NCERT_ALIGNMENT_THRESHOLD == 0.80
        assert len(orchestrator.SUPPORTED_LANGUAGES) == 5
        assert len(orchestrator.SUPPORTED_SUBJECTS) == 6
        assert len(orchestrator.SUPPORTED_FORMATS) == 3
