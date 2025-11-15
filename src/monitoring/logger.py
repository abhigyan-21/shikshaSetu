"""Enhanced logging system for pipeline monitoring."""
import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


class PipelineLogger:
    """
    Enhanced logger for pipeline operations.
    
    Requirement 9.1: Implement logging for all pipeline stages with metadata
    (timestamp, language, grade, subject, processing time)
    """
    
    def __init__(self, name: str, log_file: Optional[str] = None):
        """
        Initialize the pipeline logger.
        
        Args:
            name: Logger name
            log_file: Optional log file path
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (if specified)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def log_pipeline_start(
        self,
        content_id: str,
        language: str,
        grade_level: int,
        subject: str
    ) -> None:
        """
        Log the start of pipeline processing.
        
        Requirement 9.1: Log with metadata (timestamp, language, grade, subject)
        
        Args:
            content_id: Content identifier
            language: Target language
            grade_level: Grade level
            subject: Subject area
        """
        self.logger.info(
            f"Pipeline started | content_id={content_id} | "
            f"language={language} | grade={grade_level} | subject={subject}"
        )
    
    def log_stage_start(self, stage: str, content_id: str) -> None:
        """
        Log the start of a pipeline stage.
        
        Args:
            stage: Stage name
            content_id: Content identifier
        """
        self.logger.info(f"Stage started | stage={stage} | content_id={content_id}")
    
    def log_stage_complete(
        self,
        stage: str,
        content_id: str,
        processing_time_ms: int,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log the completion of a pipeline stage.
        
        Requirement 9.1: Log with metadata including processing time
        
        Args:
            stage: Stage name
            content_id: Content identifier
            processing_time_ms: Processing time in milliseconds
            success: Whether the stage succeeded
            metadata: Optional additional metadata
        """
        status = "SUCCESS" if success else "FAILED"
        log_msg = (
            f"Stage completed | stage={stage} | content_id={content_id} | "
            f"status={status} | processing_time_ms={processing_time_ms}"
        )
        
        if metadata:
            metadata_str = " | ".join(f"{k}={v}" for k, v in metadata.items())
            log_msg += f" | {metadata_str}"
        
        if success:
            self.logger.info(log_msg)
        else:
            self.logger.error(log_msg)
    
    def log_retry_attempt(
        self,
        stage: str,
        content_id: str,
        attempt: int,
        max_attempts: int,
        error: str
    ) -> None:
        """
        Log a retry attempt.
        
        Requirement 9.3: Log retry attempts
        
        Args:
            stage: Stage name
            content_id: Content identifier
            attempt: Current attempt number
            max_attempts: Maximum attempts allowed
            error: Error message
        """
        self.logger.warning(
            f"Retry attempt | stage={stage} | content_id={content_id} | "
            f"attempt={attempt}/{max_attempts} | error={error}"
        )
    
    def log_pipeline_complete(
        self,
        content_id: str,
        total_time_ms: int,
        success: bool,
        ncert_score: Optional[float] = None,
        audio_score: Optional[float] = None
    ) -> None:
        """
        Log the completion of the entire pipeline.
        
        Args:
            content_id: Content identifier
            total_time_ms: Total processing time
            success: Whether pipeline succeeded
            ncert_score: NCERT alignment score
            audio_score: Audio accuracy score
        """
        status = "SUCCESS" if success else "FAILED"
        log_msg = (
            f"Pipeline completed | content_id={content_id} | "
            f"status={status} | total_time_ms={total_time_ms}"
        )
        
        if ncert_score is not None:
            log_msg += f" | ncert_score={ncert_score:.2f}"
        if audio_score is not None:
            log_msg += f" | audio_score={audio_score:.2f}"
        
        if success:
            self.logger.info(log_msg)
        else:
            self.logger.error(log_msg)
    
    def log_error(
        self,
        stage: str,
        content_id: str,
        error: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an error with context.
        
        Requirement 9.3: Build error tracking system
        
        Args:
            stage: Stage where error occurred
            content_id: Content identifier
            error: Error message
            metadata: Optional additional metadata
        """
        log_msg = f"Error | stage={stage} | content_id={content_id} | error={error}"
        
        if metadata:
            metadata_str = " | ".join(f"{k}={v}" for k, v in metadata.items())
            log_msg += f" | {metadata_str}"
        
        self.logger.error(log_msg)
    
    def log_validation_failure(
        self,
        content_id: str,
        reason: str,
        score: float,
        threshold: float
    ) -> None:
        """
        Log a validation failure.
        
        Args:
            content_id: Content identifier
            reason: Reason for failure
            score: Actual score
            threshold: Required threshold
        """
        self.logger.warning(
            f"Validation failed | content_id={content_id} | "
            f"reason={reason} | score={score:.2f} | threshold={threshold:.2f}"
        )


# Global logger instance
_pipeline_logger = None


def get_pipeline_logger(log_file: Optional[str] = None) -> PipelineLogger:
    """
    Get the global pipeline logger instance.
    
    Args:
        log_file: Optional log file path
    
    Returns:
        PipelineLogger instance
    """
    global _pipeline_logger
    if _pipeline_logger is None:
        _pipeline_logger = PipelineLogger('pipeline', log_file)
    return _pipeline_logger
