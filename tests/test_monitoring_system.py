"""
Unit tests for monitoring system components.

Tests cover:
- Metrics collection accuracy (Requirement 9.2)
- Alert triggering logic (Requirement 9.4)
- Error rate calculation (Requirement 9.5)
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.monitoring.metrics_collector import (
    MetricsCollector,
    PipelineMetrics,
    DashboardMetrics,
    MetricType
)
from src.monitoring.alert_manager import (
    AlertManager,
    Alert,
    AlertType,
    AlertSeverity
)
from src.repository.models import PipelineLog, ProcessedContent


class TestMetricsCollector:
    """Test suite for MetricsCollector."""
    
    def test_collect_metric_accuracy(self):
        """Test that metrics are collected accurately."""
        collector = MetricsCollector()
        
        # Create test metric
        metric = PipelineMetrics(
            stage='simplification',
            processing_time_ms=1500,
            success=True,
            retry_count=0
        )
        
        # Collect metric
        collector.collect_metric(metric)
        
        # Verify metric was stored
        assert len(collector.in_memory_metrics) == 1
        assert collector.in_memory_metrics[0].stage == 'simplification'
        assert collector.in_memory_metrics[0].processing_time_ms == 1500
        assert collector.in_memory_metrics[0].success is True
    
    def test_collect_multiple_metrics(self):
        """Test collecting multiple metrics maintains accuracy."""
        collector = MetricsCollector()
        
        # Collect multiple metrics
        stages = ['simplification', 'translation', 'validation', 'speech']
        for i, stage in enumerate(stages):
            metric = PipelineMetrics(
                stage=stage,
                processing_time_ms=1000 + i * 100,
                success=i % 2 == 0,
                retry_count=i
            )
            collector.collect_metric(metric)
        
        # Verify all metrics collected
        assert len(collector.in_memory_metrics) == 4
        assert collector.in_memory_metrics[0].stage == 'simplification'
        assert collector.in_memory_metrics[1].stage == 'translation'
        assert collector.in_memory_metrics[2].stage == 'validation'
        assert collector.in_memory_metrics[3].stage == 'speech'
    
    @patch('src.monitoring.metrics_collector.get_db')
    def test_get_stage_success_rate(self, mock_get_db):
        """Test success rate calculation for a specific stage."""
        # Setup mock database
        mock_session = MagicMock()
        mock_get_db.return_value.get_session.return_value = mock_session
        
        # Create mock logs: 8 successful, 2 failed
        mock_logs = []
        for i in range(10):
            log = Mock(spec=PipelineLog)
            log.stage = 'translation'
            log.status = 'success' if i < 8 else 'failed'
            log.timestamp = datetime.utcnow()
            mock_logs.append(log)
        
        # Setup the query chain: query().filter().all()
        mock_query = MagicMock()
        mock_query.all.return_value = mock_logs
        mock_session.query.return_value.filter.return_value = mock_query
        
        # Test success rate calculation
        collector = MetricsCollector()
        success_rate = collector.get_stage_success_rate('translation', time_window_hours=1)
        
        # Verify: 8/10 = 0.8
        assert success_rate == 0.8
    
    @patch('src.monitoring.metrics_collector.get_db')
    def test_get_stage_success_rate_no_data(self, mock_get_db):
        """Test success rate returns 1.0 when no data exists."""
        # Setup mock database with no logs
        mock_session = MagicMock()
        mock_get_db.return_value.get_session.return_value = mock_session
        
        mock_query = mock_session.query.return_value
        mock_query.filter.return_value.filter.return_value.all.return_value = []
        
        collector = MetricsCollector()
        success_rate = collector.get_stage_success_rate('translation', time_window_hours=1)
        
        # Should return 1.0 (no failures)
        assert success_rate == 1.0
    
    @patch('src.monitoring.metrics_collector.get_db')
    def test_get_error_rate_calculation(self, mock_get_db):
        """Test error rate calculation accuracy."""
        # Setup mock database
        mock_session = MagicMock()
        mock_get_db.return_value.get_session.return_value = mock_session
        
        # Create mock logs: 3 failed out of 10
        mock_logs = []
        for i in range(10):
            log = Mock(spec=PipelineLog)
            log.stage = 'validation'
            log.status = 'failed' if i < 3 else 'success'
            log.timestamp = datetime.utcnow()
            mock_logs.append(log)
        
        mock_query = mock_session.query.return_value
        mock_query.filter.return_value.filter.return_value.all.return_value = mock_logs
        
        # Test error rate calculation
        collector = MetricsCollector()
        error_rate = collector.get_error_rate('validation', time_window_hours=1)
        
        # Verify: 3/10 = 0.3
        assert error_rate == 0.3
    
    @patch('src.monitoring.metrics_collector.get_db')
    def test_get_error_rate_overall(self, mock_get_db):
        """Test overall error rate calculation across all stages."""
        # Setup mock database
        mock_session = MagicMock()
        mock_get_db.return_value.get_session.return_value = mock_session
        
        # Create mock logs across multiple stages
        mock_logs = []
        stages = ['simplification', 'translation', 'validation', 'speech']
        for stage in stages:
            for i in range(5):
                log = Mock(spec=PipelineLog)
                log.stage = stage
                log.status = 'failed' if i == 0 else 'success'  # 1 failure per stage
                log.timestamp = datetime.utcnow()
                mock_logs.append(log)
        
        mock_query = mock_session.query.return_value
        mock_query.filter.return_value.all.return_value = mock_logs
        
        # Test overall error rate
        collector = MetricsCollector()
        error_rate = collector.get_error_rate(stage=None, time_window_hours=1)
        
        # Verify: 4 failures out of 20 = 0.2
        assert error_rate == 0.2
    
    @patch('src.monitoring.metrics_collector.get_db')
    def test_get_dashboard_metrics(self, mock_get_db):
        """Test dashboard metrics aggregation."""
        # Setup mock database
        mock_session = MagicMock()
        mock_get_db.return_value.get_session.return_value = mock_session
        
        # Create mock pipeline logs
        mock_logs = []
        for i in range(20):
            log = Mock(spec=PipelineLog)
            log.stage = 'translation' if i < 10 else 'validation'
            log.status = 'success' if i % 5 != 0 else 'failed'
            log.processing_time_ms = 1000 + i * 100
            log.timestamp = datetime.utcnow()
            mock_logs.append(log)
        
        # Create mock processed content
        mock_contents = []
        for i in range(5):
            content = Mock(spec=ProcessedContent)
            content.ncert_alignment_score = 0.85 + i * 0.02
            content.audio_accuracy_score = 0.90 + i * 0.01
            content.created_at = datetime.utcnow()
            mock_contents.append(content)
        
        # Setup query mocks
        mock_query = mock_session.query.return_value
        mock_query.filter.return_value.all.return_value = mock_logs
        
        # Mock the processed content query
        def query_side_effect(model):
            if model == ProcessedContent:
                mock_content_query = MagicMock()
                mock_content_query.filter.return_value.all.return_value = mock_contents
                return mock_content_query
            return mock_query
        
        mock_session.query.side_effect = query_side_effect
        
        # Test dashboard metrics
        collector = MetricsCollector()
        metrics = collector.get_dashboard_metrics(time_window_hours=24)
        
        # Verify metrics structure
        assert isinstance(metrics, DashboardMetrics)
        assert metrics.total_requests == 20
        assert 'translation' in metrics.throughput
        assert 'validation' in metrics.throughput
        assert 'translation' in metrics.error_rates
        assert 'ncert_alignment' in metrics.quality_scores
    
    def test_get_retry_statistics(self):
        """Test retry statistics calculation."""
        collector = MetricsCollector()
        
        # Add metrics with various retry counts
        metrics_data = [
            ('simplification', True, 0),
            ('simplification', False, 2),
            ('translation', False, 3),
            ('translation', True, 0),
            ('validation', False, 1),
        ]
        
        for stage, success, retry_count in metrics_data:
            metric = PipelineMetrics(
                stage=stage,
                processing_time_ms=1000,
                success=success,
                retry_count=retry_count
            )
            collector.collect_metric(metric)
        
        # Get retry statistics
        stats = collector.get_retry_statistics(time_window_hours=24)
        
        # Verify statistics
        assert stats['total_retries'] == 6  # 2 + 3 + 1
        assert stats['total_failures'] == 3
        assert stats['avg_retries_per_failure'] == 2.0  # 6/3
        assert 'simplification' in stats['retries_by_stage']
        assert stats['retries_by_stage']['simplification'] == 2


class TestAlertManager:
    """Test suite for AlertManager."""
    
    def test_alert_triggering_above_threshold(self):
        """Test that alerts are triggered when error rate exceeds threshold."""
        # Create mock metrics collector
        mock_collector = Mock(spec=MetricsCollector)
        mock_collector.get_error_rate.return_value = 0.15  # 15% > 10% threshold
        
        alert_manager = AlertManager(metrics_collector=mock_collector)
        
        # Check error rates
        alerts = alert_manager.check_error_rates(stages=['translation'])
        
        # Verify alert was triggered
        assert len(alerts) == 1
        assert alerts[0].alert_type == AlertType.HIGH_ERROR_RATE
        assert alerts[0].severity == AlertSeverity.ERROR
        assert alerts[0].stage == 'translation'
        assert alerts[0].metric_value == 0.15
        assert alerts[0].threshold == 0.10
    
    def test_no_alert_below_threshold(self):
        """Test that no alerts are triggered when error rate is below threshold."""
        # Create mock metrics collector
        mock_collector = Mock(spec=MetricsCollector)
        mock_collector.get_error_rate.return_value = 0.05  # 5% < 10% threshold
        
        alert_manager = AlertManager(metrics_collector=mock_collector)
        
        # Check error rates
        alerts = alert_manager.check_error_rates(stages=['translation'])
        
        # Verify no alerts triggered
        assert len(alerts) == 0
    
    def test_alert_triggering_multiple_stages(self):
        """Test alert triggering for multiple stages."""
        # Create mock metrics collector with different error rates per stage
        mock_collector = Mock(spec=MetricsCollector)
        
        def get_error_rate_side_effect(stage, time_window_hours):
            rates = {
                'simplification': 0.05,  # Below threshold
                'translation': 0.12,     # Above threshold
                'validation': 0.08,      # Below threshold
                'speech': 0.15           # Above threshold
            }
            return rates.get(stage, 0.0)
        
        mock_collector.get_error_rate.side_effect = get_error_rate_side_effect
        
        alert_manager = AlertManager(metrics_collector=mock_collector)
        
        # Check all stages
        alerts = alert_manager.check_error_rates()
        
        # Verify only 2 alerts triggered (translation and speech)
        assert len(alerts) == 2
        alert_stages = [alert.stage for alert in alerts]
        assert 'translation' in alert_stages
        assert 'speech' in alert_stages
    
    def test_overall_error_rate_alert(self):
        """Test overall error rate alert triggering."""
        # Create mock metrics collector
        mock_collector = Mock(spec=MetricsCollector)
        mock_collector.get_error_rate.return_value = 0.12  # 12% > 10%
        
        alert_manager = AlertManager(metrics_collector=mock_collector)
        
        # Check overall error rate
        alert = alert_manager.check_overall_error_rate()
        
        # Verify alert
        assert alert is not None
        assert alert.alert_type == AlertType.HIGH_ERROR_RATE
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.metric_value == 0.12
        assert alert.stage is None  # Overall, not stage-specific
    
    def test_alert_handler_registration(self):
        """Test alert handler registration and execution."""
        alert_manager = AlertManager()
        
        # Create mock handler with __name__ attribute
        mock_handler = Mock()
        mock_handler.__name__ = 'mock_handler'
        alert_manager.register_alert_handler(mock_handler)
        
        # Trigger an alert
        alert = alert_manager.alert_stage_failure(
            stage='validation',
            content_id='test-123',
            error_message='Test error',
            retry_count=1
        )
        
        # Verify handler was called
        mock_handler.assert_called_once()
        call_args = mock_handler.call_args[0]
        assert isinstance(call_args[0], Alert)
        assert call_args[0].stage == 'validation'
    
    def test_stage_failure_alert(self):
        """Test stage failure alert creation."""
        alert_manager = AlertManager()
        
        # Trigger stage failure alert
        alert = alert_manager.alert_stage_failure(
            stage='translation',
            content_id='content-456',
            error_message='Translation API timeout',
            retry_count=2
        )
        
        # Verify alert properties
        assert alert.alert_type == AlertType.STAGE_FAILURE
        assert alert.severity == AlertSeverity.WARNING
        assert alert.stage == 'translation'
        assert 'content-456' in alert.message
        assert alert.metadata['retry_count'] == 2
    
    def test_stage_failure_alert_severity_escalation(self):
        """Test that alert severity escalates after max retries."""
        alert_manager = AlertManager()
        
        # Trigger alert with max retries
        alert = alert_manager.alert_stage_failure(
            stage='speech',
            content_id='content-789',
            error_message='TTS generation failed',
            retry_count=3
        )
        
        # Verify severity escalated to ERROR
        assert alert.severity == AlertSeverity.ERROR
    
    def test_quality_threshold_alert(self):
        """Test quality threshold violation alert."""
        alert_manager = AlertManager()
        
        # Trigger quality threshold alert
        alert = alert_manager.alert_quality_threshold(
            content_id='content-999',
            metric_name='ncert_alignment',
            score=0.75,
            threshold=0.80
        )
        
        # Verify alert
        assert alert.alert_type == AlertType.QUALITY_THRESHOLD
        assert alert.severity == AlertSeverity.WARNING
        assert alert.metric_value == 0.75
        assert alert.threshold == 0.80
        assert 'ncert_alignment' in alert.message
    
    def test_get_recent_alerts(self):
        """Test retrieving recent alerts."""
        alert_manager = AlertManager()
        
        # Create several alerts
        for i in range(5):
            alert_manager.alert_stage_failure(
                stage='validation',
                content_id=f'content-{i}',
                error_message=f'Error {i}',
                retry_count=1
            )
        
        # Get recent alerts
        recent = alert_manager.get_recent_alerts(hours=24)
        
        # Verify all alerts retrieved
        assert len(recent) == 5
    
    def test_get_recent_alerts_with_severity_filter(self):
        """Test filtering alerts by severity."""
        alert_manager = AlertManager()
        
        # Create alerts with different severities
        alert_manager.alert_stage_failure('validation', 'c1', 'err', retry_count=1)  # WARNING
        alert_manager.alert_stage_failure('validation', 'c2', 'err', retry_count=3)  # ERROR
        alert_manager.alert_quality_threshold('c3', 'ncert', 0.75, 0.80)  # WARNING
        
        # Filter by WARNING severity
        warnings = alert_manager.get_recent_alerts(hours=24, severity=AlertSeverity.WARNING)
        
        # Verify only warnings retrieved
        assert len(warnings) == 2
        assert all(alert.severity == AlertSeverity.WARNING for alert in warnings)
    
    def test_clear_old_alerts(self):
        """Test clearing old alerts."""
        alert_manager = AlertManager()
        
        # Add some alerts
        for i in range(3):
            alert_manager.alert_stage_failure(
                stage='validation',
                content_id=f'content-{i}',
                error_message=f'Error {i}',
                retry_count=1
            )
        
        # Manually set old timestamps
        old_time = datetime.utcnow() - timedelta(days=10)
        alert_manager.alerts[0].timestamp = old_time
        alert_manager.alerts[1].timestamp = old_time
        
        # Clear old alerts (older than 7 days)
        cleared = alert_manager.clear_old_alerts(hours=168)
        
        # Verify 2 alerts cleared
        assert cleared == 2
        assert len(alert_manager.alerts) == 1
    
    def test_error_rate_calculation_with_time_window(self):
        """Test that error rate calculation respects time window."""
        mock_collector = Mock(spec=MetricsCollector)
        
        # Mock should be called with correct time window
        mock_collector.get_error_rate.return_value = 0.05
        
        alert_manager = AlertManager(metrics_collector=mock_collector)
        alert_manager.check_error_rates(stages=['translation'])
        
        # Verify time window parameter was passed
        mock_collector.get_error_rate.assert_called_with(
            stage='translation',
            time_window_hours=1
        )


class TestMetricsIntegration:
    """Integration tests for metrics and alerts working together."""
    
    @patch('src.monitoring.metrics_collector.get_db')
    def test_metrics_to_alert_flow(self, mock_get_db):
        """Test the flow from metrics collection to alert triggering."""
        # Setup mock database with high error rate
        mock_session = MagicMock()
        mock_get_db.return_value.get_session.return_value = mock_session
        
        # Create logs with 15% error rate (3 failures out of 20)
        mock_logs = []
        for i in range(20):
            log = Mock(spec=PipelineLog)
            log.stage = 'translation'
            log.status = 'failed' if i < 3 else 'success'
            log.timestamp = datetime.utcnow()
            mock_logs.append(log)
        
        mock_query = mock_session.query.return_value
        mock_query.filter.return_value.filter.return_value.all.return_value = mock_logs
        
        # Create collector and alert manager
        collector = MetricsCollector()
        alert_manager = AlertManager(metrics_collector=collector)
        
        # Check error rates (should trigger alert)
        alerts = alert_manager.check_error_rates(stages=['translation'])
        
        # Verify alert was triggered
        assert len(alerts) == 1
        assert alerts[0].metric_value == 0.15
        assert alerts[0].threshold == 0.10
