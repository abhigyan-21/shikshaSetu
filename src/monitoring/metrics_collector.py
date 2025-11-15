"""Metrics collection system for pipeline monitoring."""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum

from ..repository.database import get_db
from ..repository.models import PipelineLog


logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics collected."""
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    PROCESSING_TIME = "processing_time"
    QUALITY_SCORE = "quality_score"
    RETRY_COUNT = "retry_count"


@dataclass
class PipelineMetrics:
    """
    Data model for tracking pipeline metrics.
    Requirement 9.1: Create PipelineMetrics data model for tracking
    """
    stage: str
    processing_time_ms: int
    success: bool
    error_message: Optional[str] = None
    retry_count: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardMetrics:
    """
    Aggregated metrics for dashboard display.
    Requirement 9.4: Create dashboard metrics collection
    """
    throughput: Dict[str, int]  # Requests per stage
    error_rates: Dict[str, float]  # Error rate per stage
    avg_processing_times: Dict[str, float]  # Average time per stage
    quality_scores: Dict[str, float]  # Average quality scores
    total_requests: int
    successful_requests: int
    failed_requests: int
    time_window: str
    generated_at: datetime = field(default_factory=datetime.utcnow)


class MetricsCollector:
    """
    Collects and aggregates pipeline metrics for monitoring and dashboards.
    
    Requirements:
    - 9.1: Track pipeline metrics with metadata
    - 9.2: Track success rates for each pipeline stage
    - 9.4: Provide dashboard metrics (throughput, error rates, quality scores)
    - 9.5: Track retry attempts
    """
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.in_memory_metrics: List[PipelineMetrics] = []
        logger.info("MetricsCollector initialized")
    
    def collect_metric(self, metric: PipelineMetrics) -> None:
        """
        Collect a single pipeline metric.
        
        Args:
            metric: PipelineMetrics instance to collect
        """
        self.in_memory_metrics.append(metric)
        logger.debug(f"Collected metric for stage {metric.stage}: success={metric.success}")
    
    def get_dashboard_metrics(
        self,
        time_window_hours: int = 24,
        stages: Optional[List[str]] = None
    ) -> DashboardMetrics:
        """
        Get aggregated metrics for dashboard display.
        
        Requirement 9.4: Create dashboard metrics collection
        (throughput, error rates, quality scores)
        
        Args:
            time_window_hours: Time window in hours for metrics aggregation
            stages: Optional list of stages to filter by
        
        Returns:
            DashboardMetrics with aggregated data
        """
        session = get_db().get_session()
        
        try:
            # Calculate time window
            start_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            
            # Query pipeline logs within time window
            query = session.query(PipelineLog).filter(
                PipelineLog.timestamp >= start_time
            )
            
            if stages:
                query = query.filter(PipelineLog.stage.in_(stages))
            
            logs = query.all()
            
            # Aggregate metrics by stage
            throughput = defaultdict(int)
            error_counts = defaultdict(int)
            success_counts = defaultdict(int)
            processing_times = defaultdict(list)
            
            total_requests = 0
            successful_requests = 0
            failed_requests = 0
            
            for log in logs:
                stage = log.stage
                throughput[stage] += 1
                total_requests += 1
                
                if log.status == 'success':
                    success_counts[stage] += 1
                    successful_requests += 1
                else:
                    error_counts[stage] += 1
                    failed_requests += 1
                
                if log.processing_time_ms:
                    processing_times[stage].append(log.processing_time_ms)
            
            # Calculate error rates
            error_rates = {}
            for stage in throughput.keys():
                total = throughput[stage]
                errors = error_counts[stage]
                error_rates[stage] = (errors / total) if total > 0 else 0.0
            
            # Calculate average processing times
            avg_processing_times = {}
            for stage, times in processing_times.items():
                avg_processing_times[stage] = sum(times) / len(times) if times else 0.0
            
            # Get quality scores from processed_content table
            quality_scores = self._get_quality_scores(session, start_time)
            
            logger.info(
                f"Dashboard metrics generated: {total_requests} total requests, "
                f"{successful_requests} successful, {failed_requests} failed"
            )
            
            return DashboardMetrics(
                throughput=dict(throughput),
                error_rates=error_rates,
                avg_processing_times=avg_processing_times,
                quality_scores=quality_scores,
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                time_window=f"{time_window_hours}h"
            )
            
        finally:
            session.close()
    
    def _get_quality_scores(self, session, start_time: datetime) -> Dict[str, float]:
        """
        Get average quality scores from processed content.
        
        Args:
            session: Database session
            start_time: Start of time window
        
        Returns:
            Dictionary of quality score averages
        """
        from ..repository.models import ProcessedContent
        
        contents = session.query(ProcessedContent).filter(
            ProcessedContent.created_at >= start_time
        ).all()
        
        if not contents:
            return {}
        
        ncert_scores = [c.ncert_alignment_score for c in contents if c.ncert_alignment_score]
        audio_scores = [c.audio_accuracy_score for c in contents if c.audio_accuracy_score]
        
        quality_scores = {}
        if ncert_scores:
            quality_scores['ncert_alignment'] = sum(ncert_scores) / len(ncert_scores)
        if audio_scores:
            quality_scores['audio_accuracy'] = sum(audio_scores) / len(audio_scores)
        
        return quality_scores
    
    def get_stage_success_rate(
        self,
        stage: str,
        time_window_hours: int = 1
    ) -> float:
        """
        Get success rate for a specific pipeline stage.
        
        Requirement 9.2: Track success rates for each pipeline stage
        
        Args:
            stage: Pipeline stage name
            time_window_hours: Time window in hours
        
        Returns:
            Success rate as a float between 0 and 1
        """
        session = get_db().get_session()
        
        try:
            start_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            
            logs = session.query(PipelineLog).filter(
                PipelineLog.stage == stage,
                PipelineLog.timestamp >= start_time
            ).all()
            
            if not logs:
                return 1.0  # No data means no failures
            
            successful = sum(1 for log in logs if log.status == 'success')
            total = len(logs)
            
            success_rate = successful / total if total > 0 else 1.0
            
            logger.debug(f"Stage {stage} success rate: {success_rate:.2%} ({successful}/{total})")
            
            return success_rate
            
        finally:
            session.close()
    
    def get_error_rate(
        self,
        stage: Optional[str] = None,
        time_window_hours: int = 1
    ) -> float:
        """
        Get error rate for a stage or overall pipeline.
        
        Args:
            stage: Optional stage name (None for overall)
            time_window_hours: Time window in hours
        
        Returns:
            Error rate as a float between 0 and 1
        """
        session = get_db().get_session()
        
        try:
            start_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            
            query = session.query(PipelineLog).filter(
                PipelineLog.timestamp >= start_time
            )
            
            if stage:
                query = query.filter(PipelineLog.stage == stage)
            
            logs = query.all()
            
            if not logs:
                return 0.0
            
            failed = sum(1 for log in logs if log.status != 'success')
            total = len(logs)
            
            error_rate = failed / total if total > 0 else 0.0
            
            stage_info = f"stage {stage}" if stage else "overall"
            logger.debug(f"Error rate for {stage_info}: {error_rate:.2%} ({failed}/{total})")
            
            return error_rate
            
        finally:
            session.close()
    
    def get_retry_statistics(
        self,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get retry attempt statistics.
        
        Requirement 9.5: Implement retry attempt tracking
        
        Args:
            time_window_hours: Time window in hours
        
        Returns:
            Dictionary with retry statistics
        """
        # Note: Retry tracking is done in the orchestrator's StageMetrics
        # This method provides aggregated view from in-memory metrics
        
        start_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        relevant_metrics = [
            m for m in self.in_memory_metrics
            if m.timestamp >= start_time
        ]
        
        if not relevant_metrics:
            return {
                'total_retries': 0,
                'retries_by_stage': {},
                'avg_retries_per_failure': 0.0
            }
        
        total_retries = sum(m.retry_count for m in relevant_metrics)
        retries_by_stage = defaultdict(int)
        
        for metric in relevant_metrics:
            if metric.retry_count > 0:
                retries_by_stage[metric.stage] += metric.retry_count
        
        failed_metrics = [m for m in relevant_metrics if not m.success]
        avg_retries = (
            total_retries / len(failed_metrics)
            if failed_metrics else 0.0
        )
        
        return {
            'total_retries': total_retries,
            'retries_by_stage': dict(retries_by_stage),
            'avg_retries_per_failure': avg_retries,
            'total_failures': len(failed_metrics)
        }


# Global metrics collector instance
_metrics_collector = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector
