"""Monitoring service for continuous pipeline health checks."""
import logging
import time
from typing import Optional, List
from datetime import datetime

from .metrics_collector import MetricsCollector, get_metrics_collector
from .alert_manager import AlertManager, get_alert_manager, console_alert_handler
from .logger import PipelineLogger, get_pipeline_logger


logger = logging.getLogger(__name__)


class MonitoringService:
    """
    Continuous monitoring service for pipeline health.
    
    This service provides:
    - Periodic error rate checks
    - Dashboard metrics generation
    - Alert management
    - Health status reporting
    """
    
    def __init__(
        self,
        metrics_collector: Optional[MetricsCollector] = None,
        alert_manager: Optional[AlertManager] = None,
        pipeline_logger: Optional[PipelineLogger] = None
    ):
        """
        Initialize the monitoring service.
        
        Args:
            metrics_collector: Optional MetricsCollector instance
            alert_manager: Optional AlertManager instance
            pipeline_logger: Optional PipelineLogger instance
        """
        self.metrics_collector = metrics_collector or get_metrics_collector()
        self.alert_manager = alert_manager or get_alert_manager()
        self.pipeline_logger = pipeline_logger or get_pipeline_logger()
        
        # Register default alert handler
        self.alert_manager.register_alert_handler(console_alert_handler)
        
        logger.info("MonitoringService initialized")
    
    def check_pipeline_health(self) -> dict:
        """
        Perform a comprehensive health check of the pipeline.
        
        Returns:
            Dictionary with health status and metrics
        """
        logger.info("Performing pipeline health check...")
        
        # Check error rates for all stages
        error_alerts = self.alert_manager.check_error_rates()
        
        # Check overall error rate
        overall_alert = self.alert_manager.check_overall_error_rate()
        
        # Get dashboard metrics
        dashboard_metrics = self.metrics_collector.get_dashboard_metrics(
            time_window_hours=1
        )
        
        # Get retry statistics
        retry_stats = self.metrics_collector.get_retry_statistics(
            time_window_hours=24
        )
        
        # Determine overall health status
        health_status = "healthy"
        if overall_alert or len(error_alerts) > 2:
            health_status = "critical"
        elif len(error_alerts) > 0:
            health_status = "degraded"
        
        health_report = {
            'status': health_status,
            'timestamp': datetime.utcnow().isoformat(),
            'error_alerts': len(error_alerts),
            'overall_error_rate': dashboard_metrics.error_rates,
            'throughput': dashboard_metrics.total_requests,
            'success_rate': (
                dashboard_metrics.successful_requests / dashboard_metrics.total_requests
                if dashboard_metrics.total_requests > 0 else 1.0
            ),
            'retry_stats': retry_stats,
            'quality_scores': dashboard_metrics.quality_scores
        }
        
        logger.info(f"Health check complete: status={health_status}")
        
        return health_report
    
    def get_dashboard_data(self, time_window_hours: int = 24) -> dict:
        """
        Get comprehensive dashboard data.
        
        Requirement 9.4: Create dashboard metrics collection
        
        Args:
            time_window_hours: Time window for metrics
        
        Returns:
            Dictionary with dashboard data
        """
        dashboard_metrics = self.metrics_collector.get_dashboard_metrics(
            time_window_hours=time_window_hours
        )
        
        retry_stats = self.metrics_collector.get_retry_statistics(
            time_window_hours=time_window_hours
        )
        
        recent_alerts = self.alert_manager.get_recent_alerts(
            hours=time_window_hours
        )
        
        return {
            'time_window': f"{time_window_hours}h",
            'generated_at': datetime.utcnow().isoformat(),
            'throughput': {
                'total_requests': dashboard_metrics.total_requests,
                'successful_requests': dashboard_metrics.successful_requests,
                'failed_requests': dashboard_metrics.failed_requests,
                'by_stage': dashboard_metrics.throughput
            },
            'error_rates': dashboard_metrics.error_rates,
            'processing_times': dashboard_metrics.avg_processing_times,
            'quality_scores': dashboard_metrics.quality_scores,
            'retry_statistics': retry_stats,
            'recent_alerts': [
                {
                    'type': alert.alert_type.value,
                    'severity': alert.severity.value,
                    'message': alert.message,
                    'stage': alert.stage,
                    'timestamp': alert.timestamp.isoformat()
                }
                for alert in recent_alerts
            ]
        }
    
    def get_stage_health(self, stage: str, time_window_hours: int = 1) -> dict:
        """
        Get health metrics for a specific pipeline stage.
        
        Args:
            stage: Stage name
            time_window_hours: Time window for metrics
        
        Returns:
            Dictionary with stage health data
        """
        success_rate = self.metrics_collector.get_stage_success_rate(
            stage=stage,
            time_window_hours=time_window_hours
        )
        
        error_rate = self.metrics_collector.get_error_rate(
            stage=stage,
            time_window_hours=time_window_hours
        )
        
        dashboard_metrics = self.metrics_collector.get_dashboard_metrics(
            time_window_hours=time_window_hours,
            stages=[stage]
        )
        
        avg_processing_time = dashboard_metrics.avg_processing_times.get(stage, 0.0)
        throughput = dashboard_metrics.throughput.get(stage, 0)
        
        return {
            'stage': stage,
            'success_rate': success_rate,
            'error_rate': error_rate,
            'avg_processing_time_ms': avg_processing_time,
            'throughput': throughput,
            'time_window': f"{time_window_hours}h",
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def run_periodic_checks(
        self,
        interval_seconds: int = 300,
        duration_seconds: Optional[int] = None
    ) -> None:
        """
        Run periodic health checks.
        
        Args:
            interval_seconds: Interval between checks (default 5 minutes)
            duration_seconds: Optional duration to run (None for indefinite)
        """
        logger.info(
            f"Starting periodic health checks every {interval_seconds}s"
            + (f" for {duration_seconds}s" if duration_seconds else " (indefinite)")
        )
        
        start_time = time.time()
        
        try:
            while True:
                # Perform health check
                health_report = self.check_pipeline_health()
                
                # Log summary
                logger.info(
                    f"Health: {health_report['status']} | "
                    f"Throughput: {health_report['throughput']} | "
                    f"Success Rate: {health_report['success_rate']:.1%}"
                )
                
                # Check if duration limit reached
                if duration_seconds:
                    elapsed = time.time() - start_time
                    if elapsed >= duration_seconds:
                        logger.info("Periodic checks duration limit reached")
                        break
                
                # Wait for next check
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            logger.info("Periodic checks stopped by user")
        except Exception as e:
            logger.error(f"Error in periodic checks: {str(e)}")
            raise


# Global monitoring service instance
_monitoring_service = None


def get_monitoring_service() -> MonitoringService:
    """Get the global monitoring service instance."""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
    return _monitoring_service
