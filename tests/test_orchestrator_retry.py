"""Tests for ContentPipelineOrchestrator retry logic and metrics tracking."""
import pytest
import sys
import time
from unittest.mock import MagicMock, Mock, patch

# Mock database and model clients before importing
mock_db_module = MagicMock()
mock_db_module.get_db = MagicMock()
sys.modules['src.repository.database'] = mock_db_module
sys.modules['src.repository.models'] = MagicMock()

# Mock model clients
mock_model_clients = MagicMock()
mock_model_clients.FlanT5Client = Mock
mock_model_clients.IndicTrans2Client = Mock
mock_model_clients.BERTClient = Mock
mock_model_clients.VITSClient = Mock
sys.modules['src.pipeline.model_clients'] = mock_model_clients

from src.pipeline.orchestrator import (
    ContentPipelineOrchestrator,
    PipelineStage,
    PipelineStageError,
    StageMetrics
)


class TestRetryLogic:
    """Test retry logic with simulated failures."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = ContentPipelineOrchestrator()
    
    def test_retry_on_first_failure_then_success(self):
        """Test that stage retries once after initial failure and succeeds."""
        call_count = 0
        
        def failing_then_success():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("First attempt fails")
            return "success"
        
        result = self.orchestrator._execute_stage_with_retry(
            PipelineStage.SIMPLIFICATION,
            failing_then_success
        )
        
        assert result == "success"
        assert call_count == 2
        # Should have one successful metric entry
        assert len(self.orchestrator.metrics) == 1
        assert self.orchestrator.metrics[0].success == True
        assert self.orchestrator.metrics[0].retry_count == 1
    
    def test_retry_on_two_failures_then_success(self):
        """Test that stage retries twice after failures and succeeds on third attempt."""
        call_count = 0
        
        def failing_twice_then_success():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise ValueError(f"Attempt {call_count} fails")
            return "success"
        
        result = self.orchestrator._execute_stage_with_retry(
            PipelineStage.TRANSLATION,
            failing_twice_then_success
        )
        
        assert result == "success"
        assert call_count == 3
        assert len(self.orchestrator.metrics) == 1
        assert self.orchestrator.metrics[0].success == True
        assert self.orchestrator.metrics[0].retry_count == 2
    
    def test_retry_exhausted_after_max_attempts(self):
        """Test that stage fails after max retries (3 attempts total)."""
        call_count = 0
        
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError(f"Attempt {call_count} fails")
        
        with pytest.raises(PipelineStageError) as exc_info:
            self.orchestrator._execute_stage_with_retry(
                PipelineStage.VALIDATION,
                always_fails
            )
        
        # Should attempt 4 times total (initial + 3 retries)
        assert call_count == 4
        assert "failed after 4 attempts" in str(exc_info.value)
        
        # Should have one failed metric entry
        assert len(self.orchestrator.metrics) == 1
        assert self.orchestrator.metrics[0].success == False
        assert self.orchestrator.metrics[0].retry_count == 3
        assert self.orchestrator.metrics[0].error_message is not None
    
    def test_retry_with_exponential_backoff(self):
        """Test that retry uses exponential backoff timing."""
        call_count = 0
        call_times = []
        
        def failing_function():
            nonlocal call_count
            call_count += 1
            call_times.append(time.time())
            if call_count <= 2:
                raise ValueError(f"Attempt {call_count} fails")
            return "success"
        
        with patch('time.sleep') as mock_sleep:
            result = self.orchestrator._execute_stage_with_retry(
                PipelineStage.SIMPLIFICATION,
                failing_function
            )
        
        assert result == "success"
        assert call_count == 3
        
        # Verify exponential backoff: 2^0=1s, 2^1=2s
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(1)  # First retry: 2^0 = 1
        mock_sleep.assert_any_call(2)  # Second retry: 2^1 = 2
    
    def test_no_retry_on_immediate_success(self):
        """Test that no retry occurs when stage succeeds immediately."""
        call_count = 0
        
        def immediate_success():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = self.orchestrator._execute_stage_with_retry(
            PipelineStage.SPEECH,
            immediate_success
        )
        
        assert result == "success"
        assert call_count == 1
        assert len(self.orchestrator.metrics) == 1
        assert self.orchestrator.metrics[0].success == True
        assert self.orchestrator.metrics[0].retry_count == 0
    
    def test_retry_preserves_error_message(self):
        """Test that final error message is preserved after retries."""
        def always_fails():
            raise ValueError("Specific error message")
        
        with pytest.raises(PipelineStageError) as exc_info:
            self.orchestrator._execute_stage_with_retry(
                PipelineStage.VALIDATION,
                always_fails
            )
        
        assert "Specific error message" in str(exc_info.value)
        assert len(self.orchestrator.metrics) == 1
        assert "Specific error message" in self.orchestrator.metrics[0].error_message
    
    def test_retry_different_exceptions(self):
        """Test retry logic with different exception types."""
        call_count = 0
        
        def different_exceptions():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("ValueError on first attempt")
            elif call_count == 2:
                raise RuntimeError("RuntimeError on second attempt")
            return "success"
        
        result = self.orchestrator._execute_stage_with_retry(
            PipelineStage.TRANSLATION,
            different_exceptions
        )
        
        assert result == "success"
        assert call_count == 3
        assert self.orchestrator.metrics[0].success == True


class TestMetricsTracking:
    """Test metrics tracking functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = ContentPipelineOrchestrator()
    
    def test_track_metrics_records_stage_name(self):
        """Test that track_metrics records the correct stage name."""
        self.orchestrator.track_metrics("simplification", 1500, True)
        
        assert len(self.orchestrator.metrics) == 1
        assert self.orchestrator.metrics[0].stage == "simplification"
    
    def test_track_metrics_records_duration(self):
        """Test that track_metrics records processing duration."""
        self.orchestrator.track_metrics("translation", 2500, True)
        
        assert self.orchestrator.metrics[0].processing_time_ms == 2500
    
    def test_track_metrics_records_success_status(self):
        """Test that track_metrics records success status."""
        self.orchestrator.track_metrics("validation", 1000, True)
        
        assert self.orchestrator.metrics[0].success == True
    
    def test_track_metrics_records_failure_status(self):
        """Test that track_metrics records failure status."""
        self.orchestrator.track_metrics("speech", 500, False)
        
        assert self.orchestrator.metrics[0].success == False
    
    def test_track_multiple_stages(self):
        """Test tracking metrics for multiple pipeline stages."""
        self.orchestrator.track_metrics("simplification", 1500, True)
        self.orchestrator.track_metrics("translation", 2000, True)
        self.orchestrator.track_metrics("validation", 1000, True)
        self.orchestrator.track_metrics("speech", 3000, True)
        
        assert len(self.orchestrator.metrics) == 4
        assert self.orchestrator.metrics[0].stage == "simplification"
        assert self.orchestrator.metrics[1].stage == "translation"
        assert self.orchestrator.metrics[2].stage == "validation"
        assert self.orchestrator.metrics[3].stage == "speech"
    
    def test_metrics_include_timestamp(self):
        """Test that metrics include timestamp."""
        self.orchestrator.track_metrics("simplification", 1500, True)
        
        assert self.orchestrator.metrics[0].timestamp is not None
        assert isinstance(self.orchestrator.metrics[0].timestamp, type(self.orchestrator.metrics[0].timestamp))
    
    def test_metrics_reset_between_runs(self):
        """Test that metrics are reset for each processing run."""
        # First run
        self.orchestrator.track_metrics("simplification", 1500, True)
        assert len(self.orchestrator.metrics) == 1
        
        # Reset metrics (simulating new processing run)
        self.orchestrator.metrics = []
        
        # Second run
        self.orchestrator.track_metrics("translation", 2000, True)
        assert len(self.orchestrator.metrics) == 1
        assert self.orchestrator.metrics[0].stage == "translation"
    
    def test_execute_stage_tracks_processing_time(self):
        """Test that _execute_stage_with_retry tracks actual processing time."""
        def slow_function():
            time.sleep(0.1)  # Sleep for 100ms
            return "success"
        
        self.orchestrator._execute_stage_with_retry(
            PipelineStage.SIMPLIFICATION,
            slow_function
        )
        
        assert len(self.orchestrator.metrics) == 1
        # Processing time should be at least 100ms
        assert self.orchestrator.metrics[0].processing_time_ms >= 100
    
    def test_execute_stage_tracks_retry_count(self):
        """Test that metrics include retry count."""
        call_count = 0
        
        def fails_once():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("First attempt fails")
            return "success"
        
        self.orchestrator._execute_stage_with_retry(
            PipelineStage.TRANSLATION,
            fails_once
        )
        
        assert self.orchestrator.metrics[0].retry_count == 1
    
    def test_failed_stage_includes_error_message(self):
        """Test that failed stage metrics include error message."""
        def always_fails():
            raise ValueError("Test error message")
        
        with pytest.raises(PipelineStageError):
            self.orchestrator._execute_stage_with_retry(
                PipelineStage.VALIDATION,
                always_fails
            )
        
        assert len(self.orchestrator.metrics) == 1
        assert self.orchestrator.metrics[0].success == False
        assert "Test error message" in self.orchestrator.metrics[0].error_message


class TestStageMetricsDataclass:
    """Test StageMetrics dataclass functionality."""
    
    def test_stage_metrics_creation(self):
        """Test creating StageMetrics instance."""
        metrics = StageMetrics(
            stage="simplification",
            processing_time_ms=1500,
            success=True
        )
        
        assert metrics.stage == "simplification"
        assert metrics.processing_time_ms == 1500
        assert metrics.success == True
        assert metrics.error_message is None
        assert metrics.retry_count == 0
        assert metrics.timestamp is not None
    
    def test_stage_metrics_with_error(self):
        """Test creating StageMetrics with error message."""
        metrics = StageMetrics(
            stage="validation",
            processing_time_ms=500,
            success=False,
            error_message="Validation failed",
            retry_count=3
        )
        
        assert metrics.success == False
        assert metrics.error_message == "Validation failed"
        assert metrics.retry_count == 3
    
    def test_stage_metrics_default_values(self):
        """Test StageMetrics default values."""
        metrics = StageMetrics(
            stage="translation",
            processing_time_ms=2000,
            success=True
        )
        
        assert metrics.error_message is None
        assert metrics.retry_count == 0
        assert metrics.timestamp is not None


class TestRetryConfiguration:
    """Test retry configuration constants."""
    
    def test_max_retries_constant(self):
        """Test that MAX_RETRIES is set correctly."""
        orchestrator = ContentPipelineOrchestrator()
        assert orchestrator.MAX_RETRIES == 3
    
    def test_retry_backoff_base_constant(self):
        """Test that RETRY_BACKOFF_BASE is set correctly."""
        orchestrator = ContentPipelineOrchestrator()
        assert orchestrator.RETRY_BACKOFF_BASE == 2
    
    def test_retry_attempts_total(self):
        """Test that total retry attempts equals MAX_RETRIES + 1."""
        orchestrator = ContentPipelineOrchestrator()
        call_count = 0
        
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")
        
        with pytest.raises(PipelineStageError):
            orchestrator._execute_stage_with_retry(
                PipelineStage.SIMPLIFICATION,
                always_fails
            )
        
        # Should attempt initial + MAX_RETRIES times
        expected_attempts = orchestrator.MAX_RETRIES + 1
        assert call_count == expected_attempts
