# Monitoring and Logging System

This module provides comprehensive monitoring, logging, and alerting capabilities for the content pipeline.

## Requirements Coverage

- **9.1**: PipelineMetrics data model and logging with metadata (timestamp, language, grade, subject, processing time)
- **9.2**: Success rate tracking for each pipeline stage
- **9.3**: Error tracking and alerting system (alerts when error rate >10% over 1 hour)
- **9.4**: Dashboard metrics collection (throughput, error rates, quality scores)
- **9.5**: Retry attempt tracking

## Components

### 1. MetricsCollector

Collects and aggregates pipeline metrics for monitoring and dashboards.

```python
from src.monitoring import get_metrics_collector, PipelineMetrics

collector = get_metrics_collector()

# Collect a metric
metric = PipelineMetrics(
    stage='translation',
    processing_time_ms=1500,
    success=True,
    retry_count=0,
    metadata={'language': 'Hindi', 'grade': 8}
)
collector.collect_metric(metric)

# Get dashboard metrics
dashboard = collector.get_dashboard_metrics(time_window_hours=24)
print(f"Total requests: {dashboard.total_requests}")
print(f"Error rates: {dashboard.error_rates}")
print(f"Quality scores: {dashboard.quality_scores}")

# Get stage success rate
success_rate = collector.get_stage_success_rate('translation', time_window_hours=1)
print(f"Translation success rate: {success_rate:.1%}")

# Get retry statistics
retry_stats = collector.get_retry_statistics(time_window_hours=24)
print(f"Total retries: {retry_stats['total_retries']}")
```

### 2. PipelineLogger

Enhanced logging with structured metadata for all pipeline operations.

```python
from src.monitoring import get_pipeline_logger

logger = get_pipeline_logger(log_file='logs/pipeline.log')

# Log pipeline start
logger.log_pipeline_start(
    content_id='abc-123',
    language='Hindi',
    grade_level=8,
    subject='Mathematics'
)

# Log stage completion
logger.log_stage_complete(
    stage='translation',
    content_id='abc-123',
    processing_time_ms=1500,
    success=True,
    metadata={'word_count': 250}
)

# Log retry attempt
logger.log_retry_attempt(
    stage='validation',
    content_id='abc-123',
    attempt=2,
    max_attempts=3,
    error='NCERT alignment score below threshold'
)

# Log pipeline completion
logger.log_pipeline_complete(
    content_id='abc-123',
    total_time_ms=5000,
    success=True,
    ncert_score=0.85,
    audio_score=0.92
)
```

### 3. AlertManager

Manages alerts and notifications for pipeline health monitoring.

```python
from src.monitoring import get_alert_manager, console_alert_handler

alert_manager = get_alert_manager()

# Register custom alert handler
def email_alert_handler(alert):
    # Send email notification
    pass

alert_manager.register_alert_handler(email_alert_handler)

# Check error rates (automatically triggers alerts if >10%)
alerts = alert_manager.check_error_rates()

# Check overall error rate
overall_alert = alert_manager.check_overall_error_rate()

# Manually trigger alerts
alert_manager.alert_stage_failure(
    stage='translation',
    content_id='abc-123',
    error_message='API timeout',
    retry_count=3
)

alert_manager.alert_quality_threshold(
    content_id='abc-123',
    metric_name='ncert_alignment',
    score=0.75,
    threshold=0.80
)

# Get recent alerts
recent = alert_manager.get_recent_alerts(hours=24)
for alert in recent:
    print(f"{alert.severity.value}: {alert.message}")
```

### 4. MonitoringService

Comprehensive monitoring service that ties all components together.

```python
from src.monitoring.monitoring_service import get_monitoring_service

service = get_monitoring_service()

# Perform health check
health = service.check_pipeline_health()
print(f"Status: {health['status']}")
print(f"Success rate: {health['success_rate']:.1%}")

# Get dashboard data
dashboard = service.get_dashboard_data(time_window_hours=24)
print(f"Throughput: {dashboard['throughput']}")
print(f"Error rates: {dashboard['error_rates']}")

# Get stage-specific health
stage_health = service.get_stage_health('translation', time_window_hours=1)
print(f"Translation success rate: {stage_health['success_rate']:.1%}")

# Run periodic health checks (every 5 minutes)
service.run_periodic_checks(interval_seconds=300)
```

## Usage in Pipeline

The monitoring system is integrated into the ContentPipelineOrchestrator:

```python
from src.pipeline import ContentPipelineOrchestrator
from src.monitoring import get_metrics_collector, get_alert_manager

orchestrator = ContentPipelineOrchestrator()

# Process content (monitoring happens automatically)
result = orchestrator.process_content(
    input_data="Educational content...",
    target_language="Hindi",
    grade_level=8,
    subject="Mathematics",
    output_format="both"
)

# Metrics are automatically collected and logged
print(f"Processing metrics: {result.metrics}")

# Check for alerts
alert_manager = get_alert_manager()
alerts = alert_manager.check_error_rates()
```

## Alert Thresholds

- **Error Rate Alert**: Triggered when error rate exceeds 10% over a 1-hour window
- **Quality Threshold Alert**: Triggered when NCERT alignment < 80% or audio accuracy < 90%
- **Stage Failure Alert**: Triggered when a stage fails after retries

## Dashboard Metrics

The system collects the following metrics for dashboard display:

1. **Throughput**: Total requests and requests per stage
2. **Error Rates**: Error percentage for each stage and overall
3. **Processing Times**: Average processing time per stage
4. **Quality Scores**: Average NCERT alignment and audio accuracy scores
5. **Retry Statistics**: Total retries and retries per stage
6. **Success Rates**: Success percentage for each stage

## Log Format

Logs include structured metadata:

```
2024-01-15 10:30:45 - pipeline - INFO - Pipeline started | content_id=abc-123 | language=Hindi | grade=8 | subject=Mathematics
2024-01-15 10:30:46 - pipeline - INFO - Stage completed | stage=simplification | content_id=abc-123 | status=SUCCESS | processing_time_ms=1200
2024-01-15 10:30:48 - pipeline - INFO - Stage completed | stage=translation | content_id=abc-123 | status=SUCCESS | processing_time_ms=1500
2024-01-15 10:30:50 - pipeline - ERROR - ALERT [ERROR]: High error rate detected in validation stage: 12.5% (threshold: 10.0%)
```

## Database Schema

Metrics are persisted in the `pipeline_logs` table:

```sql
CREATE TABLE pipeline_logs (
    id UUID PRIMARY KEY,
    content_id UUID REFERENCES processed_content(id),
    stage VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    processing_time_ms INTEGER,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

## Best Practices

1. **Use structured logging**: Always include relevant metadata (content_id, stage, language, etc.)
2. **Monitor error rates**: Set up periodic checks to catch issues early
3. **Register alert handlers**: Implement custom handlers for email, Slack, or other notifications
4. **Review dashboard metrics**: Regularly check throughput, error rates, and quality scores
5. **Track retry patterns**: High retry counts may indicate systemic issues
6. **Set appropriate thresholds**: Adjust alert thresholds based on your requirements

## Example: Complete Monitoring Setup

```python
from src.monitoring import (
    get_metrics_collector,
    get_alert_manager,
    get_pipeline_logger,
    console_alert_handler
)
from src.monitoring.monitoring_service import get_monitoring_service

# Initialize components
logger = get_pipeline_logger(log_file='logs/pipeline.log')
metrics_collector = get_metrics_collector()
alert_manager = get_alert_manager()

# Register alert handlers
alert_manager.register_alert_handler(console_alert_handler)

# Set up monitoring service
monitoring_service = get_monitoring_service()

# Run periodic health checks in background
import threading

def background_monitoring():
    monitoring_service.run_periodic_checks(interval_seconds=300)

monitor_thread = threading.Thread(target=background_monitoring, daemon=True)
monitor_thread.start()

# Your application continues running...
```
