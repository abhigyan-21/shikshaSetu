"""Example demonstrating the monitoring and logging system."""
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.monitoring import (
    get_metrics_collector,
    get_alert_manager,
    get_pipeline_logger,
    PipelineMetrics,
    console_alert_handler
)
from src.monitoring.monitoring_service import get_monitoring_service


def main():
    """Demonstrate monitoring system capabilities."""
    print("=" * 60)
    print("Monitoring System Example")
    print("=" * 60)
    
    # Initialize components
    logger = get_pipeline_logger()
    metrics_collector = get_metrics_collector()
    alert_manager = get_alert_manager()
    monitoring_service = get_monitoring_service()
    
    # Register alert handler
    alert_manager.register_alert_handler(console_alert_handler)
    
    print("\n1. Logging Pipeline Operations")
    print("-" * 60)
    
    # Log pipeline start
    content_id = "example-123"
    logger.log_pipeline_start(
        content_id=content_id,
        language="Hindi",
        grade_level=8,
        subject="Mathematics"
    )
    
    # Log stage operations
    logger.log_stage_start("simplification", content_id)
    logger.log_stage_complete(
        stage="simplification",
        content_id=content_id,
        processing_time_ms=1200,
        success=True,
        metadata={"complexity_score": 0.65}
    )
    
    logger.log_stage_start("translation", content_id)
    logger.log_stage_complete(
        stage="translation",
        content_id=content_id,
        processing_time_ms=1500,
        success=True,
        metadata={"word_count": 250}
    )
    
    # Log pipeline completion
    logger.log_pipeline_complete(
        content_id=content_id,
        total_time_ms=5000,
        success=True,
        ncert_score=0.85,
        audio_score=0.92
    )
    
    print("\n2. Collecting Metrics")
    print("-" * 60)
    
    # Collect some metrics
    for i in range(5):
        metric = PipelineMetrics(
            stage="translation",
            processing_time_ms=1500 + i * 100,
            success=True,
            retry_count=0,
            metadata={"language": "Hindi", "grade": 8}
        )
        metrics_collector.collect_metric(metric)
    
    # Add a failed metric
    failed_metric = PipelineMetrics(
        stage="validation",
        processing_time_ms=2000,
        success=False,
        error_message="NCERT alignment below threshold",
        retry_count=2
    )
    metrics_collector.collect_metric(failed_metric)
    
    print(f"Collected {len(metrics_collector.in_memory_metrics)} metrics")
    
    # Get retry statistics
    retry_stats = metrics_collector.get_retry_statistics(time_window_hours=24)
    print(f"\nRetry Statistics:")
    print(f"  Total retries: {retry_stats['total_retries']}")
    print(f"  Retries by stage: {retry_stats['retries_by_stage']}")
    print(f"  Average retries per failure: {retry_stats['avg_retries_per_failure']:.2f}")
    
    print("\n3. Alert Management")
    print("-" * 60)
    
    # Trigger a stage failure alert
    alert_manager.alert_stage_failure(
        stage="validation",
        content_id=content_id,
        error_message="NCERT alignment score below threshold",
        retry_count=2
    )
    
    # Trigger a quality threshold alert
    alert_manager.alert_quality_threshold(
        content_id=content_id,
        metric_name="ncert_alignment",
        score=0.75,
        threshold=0.80
    )
    
    # Get recent alerts
    recent_alerts = alert_manager.get_recent_alerts(hours=1)
    print(f"\nRecent alerts: {len(recent_alerts)}")
    for alert in recent_alerts:
        print(f"  - [{alert.severity.value}] {alert.message}")
    
    print("\n4. Health Check")
    print("-" * 60)
    
    # Note: Health check requires database connection
    # This is a demonstration of the API
    print("Health check API available:")
    print("  - monitoring_service.check_pipeline_health()")
    print("  - monitoring_service.get_dashboard_data(time_window_hours=24)")
    print("  - monitoring_service.get_stage_health('translation', time_window_hours=1)")
    
    print("\n5. Dashboard Metrics")
    print("-" * 60)
    print("Dashboard metrics API available:")
    print("  - metrics_collector.get_dashboard_metrics(time_window_hours=24)")
    print("  - metrics_collector.get_stage_success_rate('translation', time_window_hours=1)")
    print("  - metrics_collector.get_error_rate(stage='validation', time_window_hours=1)")
    
    print("\n" + "=" * 60)
    print("Monitoring System Example Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
