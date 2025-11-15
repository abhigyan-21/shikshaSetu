"""Alert management system for pipeline monitoring."""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

from .metrics_collector import MetricsCollector, get_metrics_collector


logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(Enum):
    """Types of alerts."""
    HIGH_ERROR_RATE = "high_error_rate"
    STAGE_FAILURE = "stage_failure"
    QUALITY_THRESHOLD = "quality_threshold"
    PROCESSING_TIMEOUT = "processing_timeout"


@dataclass
class Alert:
    """Alert data model."""
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    stage: Optional[str] = None
    metric_value: Optional[float] = None
    threshold: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AlertManager:
    """
    Manages alerts and notifications for pipeline monitoring.
    
    Requirement 9.3: Build error tracking and alerting system
    (alert when error rate >10% over 1 hour)
    """
    
    # Alert thresholds
    ERROR_RATE_THRESHOLD = 0.10  # 10%
    ERROR_RATE_WINDOW_HOURS = 1
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        """
        Initialize the alert manager.
        
        Args:
            metrics_collector: Optional MetricsCollector instance
        """
        self.metrics_collector = metrics_collector or get_metrics_collector()
        self.alerts: List[Alert] = []
        self.alert_handlers: List[Callable[[Alert], None]] = []
        logger.info("AlertManager initialized")
    
    def register_alert_handler(self, handler: Callable[[Alert], None]) -> None:
        """
        Register a handler function to be called when alerts are triggered.
        
        Args:
            handler: Function that takes an Alert and handles it
        """
        self.alert_handlers.append(handler)
        logger.info(f"Registered alert handler: {handler.__name__}")
    
    def check_error_rates(self, stages: Optional[List[str]] = None) -> List[Alert]:
        """
        Check error rates for pipeline stages and trigger alerts if needed.
        
        Requirement 9.3: Alert when error rate >10% over 1 hour
        
        Args:
            stages: Optional list of stages to check (None for all)
        
        Returns:
            List of triggered alerts
        """
        triggered_alerts = []
        
        # Define stages to check
        if stages is None:
            stages = ['simplification', 'translation', 'validation', 'speech']
        
        for stage in stages:
            error_rate = self.metrics_collector.get_error_rate(
                stage=stage,
                time_window_hours=self.ERROR_RATE_WINDOW_HOURS
            )
            
            if error_rate > self.ERROR_RATE_THRESHOLD:
                alert = Alert(
                    alert_type=AlertType.HIGH_ERROR_RATE,
                    severity=AlertSeverity.ERROR,
                    message=(
                        f"High error rate detected in {stage} stage: "
                        f"{error_rate:.1%} (threshold: {self.ERROR_RATE_THRESHOLD:.1%})"
                    ),
                    stage=stage,
                    metric_value=error_rate,
                    threshold=self.ERROR_RATE_THRESHOLD,
                    metadata={
                        'time_window_hours': self.ERROR_RATE_WINDOW_HOURS
                    }
                )
                
                triggered_alerts.append(alert)
                self._trigger_alert(alert)
        
        return triggered_alerts
    
    def check_overall_error_rate(self) -> Optional[Alert]:
        """
        Check overall pipeline error rate.
        
        Returns:
            Alert if error rate exceeds threshold, None otherwise
        """
        error_rate = self.metrics_collector.get_error_rate(
            stage=None,
            time_window_hours=self.ERROR_RATE_WINDOW_HOURS
        )
        
        if error_rate > self.ERROR_RATE_THRESHOLD:
            alert = Alert(
                alert_type=AlertType.HIGH_ERROR_RATE,
                severity=AlertSeverity.CRITICAL,
                message=(
                    f"High overall error rate detected: "
                    f"{error_rate:.1%} (threshold: {self.ERROR_RATE_THRESHOLD:.1%})"
                ),
                metric_value=error_rate,
                threshold=self.ERROR_RATE_THRESHOLD,
                metadata={
                    'time_window_hours': self.ERROR_RATE_WINDOW_HOURS
                }
            )
            
            self._trigger_alert(alert)
            return alert
        
        return None
    
    def alert_stage_failure(
        self,
        stage: str,
        content_id: str,
        error_message: str,
        retry_count: int
    ) -> Alert:
        """
        Trigger an alert for a stage failure.
        
        Args:
            stage: Stage that failed
            content_id: Content identifier
            error_message: Error message
            retry_count: Number of retry attempts
        
        Returns:
            Created alert
        """
        alert = Alert(
            alert_type=AlertType.STAGE_FAILURE,
            severity=AlertSeverity.WARNING if retry_count < 3 else AlertSeverity.ERROR,
            message=f"Stage {stage} failed for content {content_id}: {error_message}",
            stage=stage,
            metadata={
                'content_id': content_id,
                'error_message': error_message,
                'retry_count': retry_count
            }
        )
        
        self._trigger_alert(alert)
        return alert
    
    def alert_quality_threshold(
        self,
        content_id: str,
        metric_name: str,
        score: float,
        threshold: float
    ) -> Alert:
        """
        Trigger an alert for quality threshold violation.
        
        Args:
            content_id: Content identifier
            metric_name: Name of quality metric
            score: Actual score
            threshold: Required threshold
        
        Returns:
            Created alert
        """
        alert = Alert(
            alert_type=AlertType.QUALITY_THRESHOLD,
            severity=AlertSeverity.WARNING,
            message=(
                f"Quality threshold not met for content {content_id}: "
                f"{metric_name}={score:.2f} (threshold: {threshold:.2f})"
            ),
            metric_value=score,
            threshold=threshold,
            metadata={
                'content_id': content_id,
                'metric_name': metric_name
            }
        )
        
        self._trigger_alert(alert)
        return alert
    
    def _trigger_alert(self, alert: Alert) -> None:
        """
        Trigger an alert by calling all registered handlers.
        
        Args:
            alert: Alert to trigger
        """
        self.alerts.append(alert)
        
        # Log the alert
        log_level = {
            AlertSeverity.INFO: logging.INFO,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.ERROR: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL
        }.get(alert.severity, logging.INFO)
        
        logger.log(log_level, f"ALERT [{alert.severity.value.upper()}]: {alert.message}")
        
        # Call registered handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Error in alert handler {handler.__name__}: {str(e)}")
    
    def get_recent_alerts(
        self,
        hours: int = 24,
        severity: Optional[AlertSeverity] = None
    ) -> List[Alert]:
        """
        Get recent alerts within a time window.
        
        Args:
            hours: Time window in hours
            severity: Optional severity filter
        
        Returns:
            List of alerts
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        alerts = [
            alert for alert in self.alerts
            if alert.timestamp >= cutoff_time
        ]
        
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        return alerts
    
    def clear_old_alerts(self, hours: int = 168) -> int:
        """
        Clear alerts older than specified hours (default 7 days).
        
        Args:
            hours: Age threshold in hours
        
        Returns:
            Number of alerts cleared
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        old_count = len(self.alerts)
        self.alerts = [
            alert for alert in self.alerts
            if alert.timestamp >= cutoff_time
        ]
        
        cleared = old_count - len(self.alerts)
        if cleared > 0:
            logger.info(f"Cleared {cleared} old alerts")
        
        return cleared


# Global alert manager instance
_alert_manager = None


def get_alert_manager() -> AlertManager:
    """Get the global alert manager instance."""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager


# Default alert handlers
def console_alert_handler(alert: Alert) -> None:
    """
    Default console alert handler.
    
    Args:
        alert: Alert to handle
    """
    print(f"\n{'='*60}")
    print(f"ALERT: {alert.severity.value.upper()}")
    print(f"Type: {alert.alert_type.value}")
    print(f"Message: {alert.message}")
    if alert.stage:
        print(f"Stage: {alert.stage}")
    if alert.metric_value is not None:
        print(f"Metric Value: {alert.metric_value}")
    if alert.threshold is not None:
        print(f"Threshold: {alert.threshold}")
    print(f"Timestamp: {alert.timestamp}")
    print(f"{'='*60}\n")
