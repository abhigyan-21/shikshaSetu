"""Example demonstrating pipeline integration with monitoring system."""
import sys
import os

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


def simulate_pipeline_with_monitoring():
    """
    Simulate pipeline processing with monitoring integration.
    
    This demonstrates how the monitoring system tracks:
    - Pipeline metrics (Requirement 9.1)
    - Success rates per stage (Requirement 9.2)
    - Error tracking and alerting (Requirement 9.3)
    - Dashboard metrics (Requirement 9.4)
    - Retry attempts (Requirement 9.5)
    """
    print("=" * 70)
    print("Pipeline Processing with Monitoring Integration")
    print("=" * 70)
    
    # Initialize monitoring components
    logger = get_pipeline_logger()
    metrics_collector = get_metrics_collector()
    alert_manager = get_alert_manager()
    monitoring_service = get_monitoring_service()
    
    # Register alert handler
    alert_manager.register_alert_handler(console_alert_handler)
    
    # Simulate processing multiple content items
    content_items = [
        {"id": "content-001", "language": "Hindi", "grade": 8, "subject": "Mathematics"},
        {"id": "content-002", "language": "Tamil", "grade": 10, "subject": "Science"},
        {"id": "content-003", "language": "Telugu", "grade": 7, "subject": "Social Studies"},
        {"id": "content-004", "language": "Bengali", "grade": 9, "subject": "Mathematics"},
        {"id": "content-005", "language": "Marathi", "grade": 11, "subject": "Science"},
    ]
    
    stages = ["simplification", "translation", "validation", "speech"]
    
    print("\nProcessing content items with monitoring...\n")
    
    for item in content_items:
        content_id = item["id"]
        
        # Log pipeline start (Requirement 9.1: metadata logging)
        logger.log_pipeline_start(
            content_id=content_id,
            language=item["language"],
            grade_level=item["grade"],
            subject=item["subject"]
        )
        
        total_time = 0
        pipeline_success = True
        
        # Process through each stage
        for stage_idx, stage in enumerate(stages):
            logger.log_stage_start(stage, content_id)
            
            # Simulate processing time
            processing_time = 1000 + stage_idx * 500
            total_time += processing_time
            
            # Simulate occasional failures (for demonstration)
            import random
            success = random.random() > 0.15  # 85% success rate
            retry_count = 0 if success else random.randint(1, 2)
            
            if not success:
                pipeline_success = False
                # Log retry attempts (Requirement 9.5)
                for attempt in range(1, retry_count + 1):
                    logger.log_retry_attempt(
                        stage=stage,
                        content_id=content_id,
                        attempt=attempt,
                        max_attempts=3,
                        error=f"Simulated {stage} error"
                    )
            
            # Log stage completion
            logger.log_stage_complete(
                stage=stage,
                content_id=content_id,
                processing_time_ms=processing_time,
                success=success,
                metadata={
                    "language": item["language"],
                    "grade": item["grade"],
                    "subject": item["subject"]
                }
            )
            
            # Collect metrics (Requirement 9.1: PipelineMetrics data model)
            metric = PipelineMetrics(
                stage=stage,
                processing_time_ms=processing_time,
                success=success,
                error_message=f"Simulated {stage} error" if not success else None,
                retry_count=retry_count,
                metadata={
                    "content_id": content_id,
                    "language": item["language"],
                    "grade": item["grade"],
                    "subject": item["subject"]
                }
            )
            metrics_collector.collect_metric(metric)
            
            # Trigger alerts for failures (Requirement 9.3)
            if not success:
                alert_manager.alert_stage_failure(
                    stage=stage,
                    content_id=content_id,
                    error_message=f"Simulated {stage} error",
                    retry_count=retry_count
                )
        
        # Log pipeline completion
        logger.log_pipeline_complete(
            content_id=content_id,
            total_time_ms=total_time,
            success=pipeline_success,
            ncert_score=0.85 if pipeline_success else 0.70,
            audio_score=0.92 if pipeline_success else None
        )
    
    print("\n" + "=" * 70)
    print("Monitoring Summary")
    print("=" * 70)
    
    # Display metrics summary (Requirement 9.4: Dashboard metrics)
    print("\n1. Collected Metrics:")
    print(f"   Total metrics collected: {len(metrics_collector.in_memory_metrics)}")
    
    successful = sum(1 for m in metrics_collector.in_memory_metrics if m.success)
    failed = len(metrics_collector.in_memory_metrics) - successful
    print(f"   Successful stages: {successful}")
    print(f"   Failed stages: {failed}")
    print(f"   Overall success rate: {successful / len(metrics_collector.in_memory_metrics):.1%}")
    
    # Display retry statistics (Requirement 9.5)
    print("\n2. Retry Statistics:")
    retry_stats = metrics_collector.get_retry_statistics(time_window_hours=24)
    print(f"   Total retries: {retry_stats['total_retries']}")
    print(f"   Retries by stage: {retry_stats['retries_by_stage']}")
    print(f"   Average retries per failure: {retry_stats['avg_retries_per_failure']:.2f}")
    
    # Display stage success rates (Requirement 9.2)
    print("\n3. Stage Success Rates:")
    for stage in stages:
        stage_metrics = [m for m in metrics_collector.in_memory_metrics if m.stage == stage]
        if stage_metrics:
            stage_success = sum(1 for m in stage_metrics if m.success)
            stage_rate = stage_success / len(stage_metrics)
            print(f"   {stage}: {stage_rate:.1%} ({stage_success}/{len(stage_metrics)})")
    
    # Display alerts (Requirement 9.3)
    print("\n4. Alerts Triggered:")
    recent_alerts = alert_manager.get_recent_alerts(hours=1)
    print(f"   Total alerts: {len(recent_alerts)}")
    
    alert_by_severity = {}
    for alert in recent_alerts:
        severity = alert.severity.value
        alert_by_severity[severity] = alert_by_severity.get(severity, 0) + 1
    
    for severity, count in alert_by_severity.items():
        print(f"   {severity.upper()}: {count}")
    
    # Check for high error rates (Requirement 9.3: >10% error rate alert)
    print("\n5. Error Rate Check (>10% threshold):")
    try:
        error_alerts = alert_manager.check_error_rates(stages)
        if error_alerts:
            print(f"   ⚠️  {len(error_alerts)} stage(s) exceeded error rate threshold!")
            for alert in error_alerts:
                print(f"      - {alert.stage}: {alert.metric_value:.1%}")
        else:
            print("   ✓ All stages within acceptable error rates")
    except Exception as e:
        print(f"   ℹ️  Database-based error rate check requires database connection")
        print(f"      (In-memory metrics show {failed}/{len(metrics_collector.in_memory_metrics)} failures = {failed/len(metrics_collector.in_memory_metrics):.1%} error rate)")
    
    print("\n" + "=" * 70)
    print("Monitoring Integration Complete")
    print("=" * 70)
    print("\nThe monitoring system successfully tracked:")
    print("  ✓ Pipeline metrics with metadata (Req 9.1)")
    print("  ✓ Success rates for each stage (Req 9.2)")
    print("  ✓ Error tracking and alerting (Req 9.3)")
    print("  ✓ Dashboard metrics collection (Req 9.4)")
    print("  ✓ Retry attempt tracking (Req 9.5)")
    print("=" * 70)


if __name__ == "__main__":
    simulate_pipeline_with_monitoring()
