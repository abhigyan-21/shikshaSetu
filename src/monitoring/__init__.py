"""
Monitoring and logging module for pipeline operations.

This module provides comprehensive monitoring capabilities including:
- Metrics collection and aggregation
- Enhanced logging with metadata
- Error tracking and alerting
- Dashboard metrics generation
- Retry attempt tracking

Requirements covered:
- 9.1: PipelineMetrics data model and logging with metadata
- 9.2: Success rate tracking for each pipeline stage
- 9.3: Error tracking and alerting (>10% error rate over 1 hour)
- 9.4: Dashboard metrics collection (throughput, error rates, quality scores)
- 9.5: Retry attempt tracking
"""

from .metrics_collector import (
    MetricsCollector,
    PipelineMetrics,
    DashboardMetrics,
    MetricType,
    get_metrics_collector
)
from .logger import (
    PipelineLogger,
    get_pipeline_logger
)
from .alert_manager import (
    AlertManager,
    Alert,
    AlertType,
    AlertSeverity,
    get_alert_manager,
    console_alert_handler
)
from .monitoring_service import (
    MonitoringService,
    get_monitoring_service
)

__all__ = [
    # Metrics
    'MetricsCollector',
    'PipelineMetrics',
    'DashboardMetrics',
    'MetricType',
    'get_metrics_collector',
    
    # Logging
    'PipelineLogger',
    'get_pipeline_logger',
    
    # Alerting
    'AlertManager',
    'Alert',
    'AlertType',
    'AlertSeverity',
    'get_alert_manager',
    'console_alert_handler',
    
    # Monitoring Service
    'MonitoringService',
    'get_monitoring_service',
]
