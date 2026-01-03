"""
Security Monitoring - Real-time security event monitoring and alerting.

Week 16: Defense Integration & System Hardening
Provides monitoring, metrics, and alerting for security events.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TypeVar
from collections import defaultdict, deque
import threading
import statistics

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


class MetricType(Enum):
    """Types of metrics."""
    
    COUNTER = auto()
    GAUGE = auto()
    HISTOGRAM = auto()
    RATE = auto()


@dataclass
class Alert:
    """Security alert."""
    
    alert_id: str
    timestamp: datetime
    severity: AlertSeverity
    title: str
    description: str
    source: str
    entity_id: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "alert_id": self.alert_id,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity.name,
            "title": self.title,
            "description": self.description,
            "source": self.source,
            "entity_id": self.entity_id,
            "metadata": self.metadata,
            "acknowledged": self.acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": (
                self.acknowledged_at.isoformat()
                if self.acknowledged_at else None
            ),
            "resolved": self.resolved,
            "resolved_at": (
                self.resolved_at.isoformat()
                if self.resolved_at else None
            ),
        }


@dataclass
class MetricPoint:
    """Single metric data point."""
    
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


class Metric:
    """Metric with time-series data."""
    
    def __init__(
        self,
        name: str,
        metric_type: MetricType,
        description: str = "",
        retention_minutes: int = 60
    ):
        self.name = name
        self.metric_type = metric_type
        self.description = description
        self.retention_minutes = retention_minutes
        
        self.points: deque = deque()
        self._value: float = 0.0
        self._lock = threading.Lock()
    
    def record(self, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Record a metric value."""
        with self._lock:
            point = MetricPoint(
                timestamp=datetime.now(),
                value=value,
                labels=labels or {}
            )
            self.points.append(point)
            
            # Update current value based on type
            if self.metric_type == MetricType.COUNTER:
                self._value += value
            elif self.metric_type == MetricType.GAUGE:
                self._value = value
            
            # Clean old points
            self._clean_old_points()
    
    def _clean_old_points(self) -> None:
        """Remove points older than retention period."""
        cutoff = datetime.now() - timedelta(minutes=self.retention_minutes)
        while self.points and self.points[0].timestamp < cutoff:
            self.points.popleft()
    
    def get_value(self) -> float:
        """Get current metric value."""
        return self._value
    
    def get_rate(self, window_seconds: int = 60) -> float:
        """Calculate rate over window."""
        with self._lock:
            self._clean_old_points()
            
            cutoff = datetime.now() - timedelta(seconds=window_seconds)
            recent_points = [p for p in self.points if p.timestamp >= cutoff]
            
            if len(recent_points) < 2:
                return 0.0
            
            total = sum(p.value for p in recent_points)
            return total / window_seconds
    
    def get_statistics(self) -> Dict[str, float]:
        """Get metric statistics."""
        with self._lock:
            self._clean_old_points()
            
            if not self.points:
                return {
                    "count": 0,
                    "min": 0.0,
                    "max": 0.0,
                    "mean": 0.0,
                    "current": self._value,
                }
            
            values = [p.value for p in self.points]
            
            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
                "current": self._value,
            }


class AlertHandler(ABC):
    """Abstract base for alert handlers."""
    
    @abstractmethod
    async def handle(self, alert: Alert) -> bool:
        """Handle an alert."""
        pass


class LogAlertHandler(AlertHandler):
    """Handler that logs alerts."""
    
    def __init__(self, log_level: int = logging.WARNING):
        self.log_level = log_level
    
    async def handle(self, alert: Alert) -> bool:
        """Log the alert."""
        message = (
            f"[{alert.severity.name}] {alert.title}: {alert.description} "
            f"(source={alert.source}, entity={alert.entity_id})"
        )
        
        logger.log(self.log_level, message)
        return True


class WebhookAlertHandler(AlertHandler):
    """Handler that sends alerts to a webhook."""
    
    def __init__(
        self,
        webhook_url: str,
        timeout_seconds: int = 10,
        include_metadata: bool = True
    ):
        self.webhook_url = webhook_url
        self.timeout_seconds = timeout_seconds
        self.include_metadata = include_metadata
    
    async def handle(self, alert: Alert) -> bool:
        """Send alert to webhook."""
        payload = alert.to_dict()
        
        if not self.include_metadata:
            payload.pop("metadata", None)
        
        # In production, this would use aiohttp or similar
        logger.info(f"Would send webhook to {self.webhook_url}: {alert.title}")
        return True


class CallbackAlertHandler(AlertHandler):
    """Handler that calls a callback function."""
    
    def __init__(self, callback: Callable[[Alert], bool]):
        self.callback = callback
    
    async def handle(self, alert: Alert) -> bool:
        """Call the callback."""
        return self.callback(alert)


@dataclass
class AlertRule:
    """Rule for generating alerts."""
    
    rule_id: str
    name: str
    metric_name: str
    condition: str  # "gt", "lt", "eq", "gte", "lte"
    threshold: float
    severity: AlertSeverity
    window_seconds: int = 60
    cooldown_seconds: int = 300
    enabled: bool = True
    
    last_triggered: Optional[datetime] = None
    
    def evaluate(self, value: float) -> bool:
        """Evaluate if rule should trigger."""
        if not self.enabled:
            return False
        
        # Check cooldown
        if self.last_triggered:
            cooldown_until = self.last_triggered + timedelta(
                seconds=self.cooldown_seconds
            )
            if datetime.now() < cooldown_until:
                return False
        
        # Evaluate condition
        conditions = {
            "gt": lambda v, t: v > t,
            "lt": lambda v, t: v < t,
            "eq": lambda v, t: abs(v - t) < 0.001,
            "gte": lambda v, t: v >= t,
            "lte": lambda v, t: v <= t,
        }
        
        check = conditions.get(self.condition, lambda v, t: False)
        return check(value, self.threshold)


class SecurityMonitor:
    """Central security monitoring system."""
    
    def __init__(
        self,
        metrics_retention_minutes: int = 60,
        max_alerts: int = 10000
    ):
        self.metrics_retention_minutes = metrics_retention_minutes
        self.max_alerts = max_alerts
        
        # Metrics
        self.metrics: Dict[str, Metric] = {}
        
        # Alerts
        self.alerts: List[Alert] = []
        self.active_alerts: Dict[str, Alert] = {}
        
        # Handlers and rules
        self.handlers: List[AlertHandler] = []
        self.rules: Dict[str, AlertRule] = {}
        
        # State
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._lock = threading.Lock()
        
        # Default metrics
        self._setup_default_metrics()
    
    def _setup_default_metrics(self) -> None:
        """Set up default security metrics."""
        default_metrics = [
            ("security.events.total", MetricType.COUNTER, "Total security events"),
            ("security.events.blocked", MetricType.COUNTER, "Blocked events"),
            ("security.events.allowed", MetricType.COUNTER, "Allowed events"),
            ("security.threats.active", MetricType.GAUGE, "Active threats"),
            ("security.defense_level", MetricType.GAUGE, "Current defense level"),
            ("security.response_time_ms", MetricType.HISTOGRAM, "Response time"),
            ("security.rate_limits.triggered", MetricType.COUNTER, "Rate limits triggered"),
            ("security.injections.detected", MetricType.COUNTER, "Injection attempts"),
            ("security.api.requests", MetricType.COUNTER, "API requests"),
            ("security.api.errors", MetricType.COUNTER, "API errors"),
        ]
        
        for name, metric_type, description in default_metrics:
            self.register_metric(name, metric_type, description)
    
    def register_metric(
        self,
        name: str,
        metric_type: MetricType,
        description: str = ""
    ) -> Metric:
        """Register a new metric."""
        metric = Metric(
            name=name,
            metric_type=metric_type,
            description=description,
            retention_minutes=self.metrics_retention_minutes
        )
        self.metrics[name] = metric
        return metric
    
    def record_metric(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a metric value."""
        if name not in self.metrics:
            # Auto-create as counter
            self.register_metric(name, MetricType.COUNTER)
        
        self.metrics[name].record(value, labels)
        
        # Check alert rules
        self._check_rules(name)
    
    def increment(
        self,
        name: str,
        amount: float = 1.0,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Increment a counter metric."""
        self.record_metric(name, amount, labels)
    
    def set_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Set a gauge metric."""
        if name not in self.metrics:
            self.register_metric(name, MetricType.GAUGE)
        
        self.metrics[name].record(value, labels)
    
    def add_handler(self, handler: AlertHandler) -> None:
        """Add an alert handler."""
        self.handlers.append(handler)
    
    def add_rule(self, rule: AlertRule) -> None:
        """Add an alert rule."""
        self.rules[rule.rule_id] = rule
    
    def _check_rules(self, metric_name: str) -> None:
        """Check alert rules for a metric."""
        for rule in self.rules.values():
            if rule.metric_name != metric_name:
                continue
            
            metric = self.metrics.get(metric_name)
            if not metric:
                continue
            
            value = metric.get_value()
            
            if rule.evaluate(value):
                self._trigger_alert(rule, value)
    
    def _trigger_alert(self, rule: AlertRule, value: float) -> None:
        """Trigger an alert from a rule."""
        import uuid
        
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            severity=rule.severity,
            title=f"Alert: {rule.name}",
            description=(
                f"Metric {rule.metric_name} {rule.condition} {rule.threshold} "
                f"(current value: {value})"
            ),
            source=f"rule:{rule.rule_id}",
            entity_id=None,
            metadata={
                "rule_id": rule.rule_id,
                "metric_name": rule.metric_name,
                "threshold": rule.threshold,
                "current_value": value,
            }
        )
        
        rule.last_triggered = datetime.now()
        
        asyncio.create_task(self.emit_alert(alert))
    
    async def emit_alert(self, alert: Alert) -> None:
        """Emit an alert through all handlers."""
        with self._lock:
            self.alerts.append(alert)
            
            if not alert.resolved:
                self.active_alerts[alert.alert_id] = alert
            
            # Trim old alerts
            if len(self.alerts) > self.max_alerts:
                self.alerts = self.alerts[-self.max_alerts:]
        
        # Send to handlers
        for handler in self.handlers:
            try:
                await handler.handle(alert)
            except Exception as e:
                logger.error(f"Alert handler error: {e}")
    
    def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str
    ) -> bool:
        """Acknowledge an alert."""
        with self._lock:
            if alert_id not in self.active_alerts:
                return False
            
            alert = self.active_alerts[alert_id]
            alert.acknowledged = True
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.now()
            
            return True
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        with self._lock:
            if alert_id not in self.active_alerts:
                return False
            
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = datetime.now()
            
            del self.active_alerts[alert_id]
            
            return True
    
    def get_active_alerts(
        self,
        severity: Optional[AlertSeverity] = None
    ) -> List[Alert]:
        """Get active alerts."""
        with self._lock:
            alerts = list(self.active_alerts.values())
            
            if severity:
                alerts = [a for a in alerts if a.severity == severity]
            
            return sorted(alerts, key=lambda a: a.timestamp, reverse=True)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        return {
            name: metric.get_statistics()
            for name, metric in self.metrics.items()
        }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for security dashboard."""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        recent_alerts = [
            a for a in self.alerts
            if a.timestamp >= hour_ago
        ]
        
        return {
            "timestamp": now.isoformat(),
            "metrics": self.get_metrics_summary(),
            "alerts": {
                "active_count": len(self.active_alerts),
                "recent_count": len(recent_alerts),
                "by_severity": {
                    severity.name: len([
                        a for a in self.active_alerts.values()
                        if a.severity == severity
                    ])
                    for severity in AlertSeverity
                },
            },
            "health": self._calculate_health_score(),
        }
    
    def _calculate_health_score(self) -> Dict[str, Any]:
        """Calculate overall security health score."""
        # Simple health calculation
        critical_alerts = len([
            a for a in self.active_alerts.values()
            if a.severity == AlertSeverity.CRITICAL
        ])
        error_alerts = len([
            a for a in self.active_alerts.values()
            if a.severity == AlertSeverity.ERROR
        ])
        
        # Start at 100, deduct for issues
        score = 100
        score -= critical_alerts * 20
        score -= error_alerts * 10
        
        # Get metrics impact
        events_metric = self.metrics.get("security.events.blocked")
        if events_metric:
            stats = events_metric.get_statistics()
            if stats["count"] > 100:
                score -= 10
        
        score = max(0, min(100, score))
        
        status = "healthy"
        if score < 50:
            status = "critical"
        elif score < 70:
            status = "degraded"
        elif score < 90:
            status = "warning"
        
        return {
            "score": score,
            "status": status,
            "factors": {
                "critical_alerts": critical_alerts,
                "error_alerts": error_alerts,
            }
        }
    
    async def start_monitoring(self, interval_seconds: int = 30) -> None:
        """Start background monitoring."""
        self._running = True
        
        async def monitor_loop():
            while self._running:
                try:
                    # Check all rules
                    for metric_name in self.metrics:
                        self._check_rules(metric_name)
                    
                    await asyncio.sleep(interval_seconds)
                except Exception as e:
                    logger.error(f"Monitor loop error: {e}")
        
        self._monitor_task = asyncio.create_task(monitor_loop())
    
    async def stop_monitoring(self) -> None:
        """Stop background monitoring."""
        self._running = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass


class SecurityDashboard:
    """Security dashboard for visualization."""
    
    def __init__(self, monitor: SecurityMonitor):
        self.monitor = monitor
    
    def get_overview(self) -> Dict[str, Any]:
        """Get dashboard overview."""
        return self.monitor.get_dashboard_data()
    
    def get_metric_history(
        self,
        metric_name: str,
        duration_minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """Get metric history for charting."""
        metric = self.monitor.metrics.get(metric_name)
        if not metric:
            return []
        
        cutoff = datetime.now() - timedelta(minutes=duration_minutes)
        
        return [
            {
                "timestamp": p.timestamp.isoformat(),
                "value": p.value,
                "labels": p.labels,
            }
            for p in metric.points
            if p.timestamp >= cutoff
        ]
    
    def get_alert_timeline(
        self,
        duration_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get alert timeline."""
        cutoff = datetime.now() - timedelta(hours=duration_hours)
        
        return [
            alert.to_dict()
            for alert in self.monitor.alerts
            if alert.timestamp >= cutoff
        ]
    
    def get_threat_distribution(self) -> Dict[str, int]:
        """Get distribution of threats by source."""
        distribution: Dict[str, int] = defaultdict(int)
        
        for alert in self.monitor.active_alerts.values():
            source = alert.source.split(":")[0]
            distribution[source] += 1
        
        return dict(distribution)


# Factory functions
def create_monitor(
    enable_default_handlers: bool = True
) -> SecurityMonitor:
    """Create a configured security monitor."""
    monitor = SecurityMonitor()
    
    if enable_default_handlers:
        monitor.add_handler(LogAlertHandler())
    
    # Add default rules
    default_rules = [
        AlertRule(
            rule_id="high_blocked_events",
            name="High Blocked Events",
            metric_name="security.events.blocked",
            condition="gte",
            threshold=100,
            severity=AlertSeverity.WARNING,
            window_seconds=300,
        ),
        AlertRule(
            rule_id="injection_attempts",
            name="Injection Attempts Detected",
            metric_name="security.injections.detected",
            condition="gte",
            threshold=5,
            severity=AlertSeverity.ERROR,
            window_seconds=60,
        ),
        AlertRule(
            rule_id="critical_defense_level",
            name="Critical Defense Level",
            metric_name="security.defense_level",
            condition="gte",
            threshold=4,
            severity=AlertSeverity.CRITICAL,
            window_seconds=0,
        ),
    ]
    
    for rule in default_rules:
        monitor.add_rule(rule)
    
    return monitor
