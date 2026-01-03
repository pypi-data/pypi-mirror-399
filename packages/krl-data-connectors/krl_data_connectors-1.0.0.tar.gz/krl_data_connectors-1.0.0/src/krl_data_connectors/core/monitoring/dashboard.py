"""
Monitoring Dashboard - Phase 2 Week 13

Real-time security monitoring dashboard with metrics collection,
aggregation, and visualization support.

Copyright 2025 KR-Labs. All rights reserved.
"""

from __future__ import annotations

import asyncio
import json
import statistics
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta, UTC
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
import hashlib


class MetricType(Enum):
    """Types of metrics collected."""
    
    # Counters (monotonically increasing)
    COUNTER = "counter"
    
    # Gauges (point-in-time values)
    GAUGE = "gauge"
    
    # Histograms (distribution of values)
    HISTOGRAM = "histogram"
    
    # Summary (quantiles)
    SUMMARY = "summary"
    
    # Rate (per-second calculations)
    RATE = "rate"


class TimeRange(Enum):
    """Time ranges for dashboard queries."""
    
    LAST_MINUTE = 60
    LAST_5_MINUTES = 300
    LAST_15_MINUTES = 900
    LAST_HOUR = 3600
    LAST_6_HOURS = 21600
    LAST_24_HOURS = 86400
    LAST_7_DAYS = 604800
    LAST_30_DAYS = 2592000


@dataclass
class MetricPoint:
    """A single metric data point."""
    
    name: str
    value: float
    timestamp: float
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp,
            "labels": self.labels,
            "type": self.metric_type.value,
        }


@dataclass
class MetricSeries:
    """Time series of metric points."""
    
    name: str
    labels: Dict[str, str]
    metric_type: MetricType
    points: deque = field(default_factory=lambda: deque(maxlen=10000))
    
    def add_point(self, value: float, timestamp: float | None = None) -> None:
        """Add a data point to the series."""
        ts = timestamp or time.time()
        self.points.append((ts, value))
    
    def get_points(
        self,
        start_time: float | None = None,
        end_time: float | None = None
    ) -> List[Tuple[float, float]]:
        """Get points within time range."""
        result = []
        for ts, value in self.points:
            if start_time and ts < start_time:
                continue
            if end_time and ts > end_time:
                continue
            result.append((ts, value))
        return result
    
    def get_latest(self) -> Tuple[float, float] | None:
        """Get the most recent point."""
        if self.points:
            return self.points[-1]
        return None
    
    def calculate_rate(self, window_seconds: float = 60.0) -> float:
        """Calculate rate of change over window."""
        now = time.time()
        start = now - window_seconds
        points = self.get_points(start_time=start)
        
        if len(points) < 2:
            return 0.0
        
        first_ts, first_val = points[0]
        last_ts, last_val = points[-1]
        
        time_diff = last_ts - first_ts
        if time_diff <= 0:
            return 0.0
        
        return (last_val - first_val) / time_diff
    
    def calculate_statistics(
        self,
        window_seconds: float = 300.0
    ) -> Dict[str, float]:
        """Calculate statistics over window."""
        now = time.time()
        start = now - window_seconds
        points = self.get_points(start_time=start)
        
        if not points:
            return {
                "count": 0,
                "min": 0.0,
                "max": 0.0,
                "mean": 0.0,
                "median": 0.0,
                "stddev": 0.0,
            }
        
        values = [v for _, v in points]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "stddev": statistics.stdev(values) if len(values) > 1 else 0.0,
        }


@dataclass
class DashboardConfig:
    """Configuration for the monitoring dashboard."""
    
    # Data retention
    max_points_per_series: int = 10000
    retention_seconds: int = 86400 * 7  # 7 days
    
    # Collection
    collection_interval_seconds: float = 10.0
    aggregation_interval_seconds: float = 60.0
    
    # Alerting thresholds
    error_rate_threshold: float = 0.05  # 5%
    latency_p99_threshold_ms: float = 1000.0
    anomaly_score_threshold: float = 0.8
    
    # Dashboard
    refresh_interval_seconds: float = 30.0
    default_time_range: TimeRange = TimeRange.LAST_HOUR


class MetricRegistry:
    """Registry for managing metric series."""
    
    def __init__(self, config: DashboardConfig):
        self.config = config
        self._series: Dict[str, MetricSeries] = {}
        self._lock = threading.RLock()
    
    def _make_key(self, name: str, labels: Dict[str, str]) -> str:
        """Create unique key for metric series."""
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}:{label_str}"
    
    def get_or_create(
        self,
        name: str,
        labels: Dict[str, str],
        metric_type: MetricType = MetricType.GAUGE
    ) -> MetricSeries:
        """Get existing series or create new one."""
        key = self._make_key(name, labels)
        
        with self._lock:
            if key not in self._series:
                self._series[key] = MetricSeries(
                    name=name,
                    labels=labels,
                    metric_type=metric_type,
                    points=deque(maxlen=self.config.max_points_per_series)
                )
            return self._series[key]
    
    def record(
        self,
        name: str,
        value: float,
        labels: Dict[str, str] | None = None,
        metric_type: MetricType = MetricType.GAUGE,
        timestamp: float | None = None
    ) -> None:
        """Record a metric value."""
        labels = labels or {}
        series = self.get_or_create(name, labels, metric_type)
        series.add_point(value, timestamp)
    
    def get_series(self, name: str, labels: Dict[str, str] | None = None) -> List[MetricSeries]:
        """Get all series matching name and optional labels."""
        results = []
        with self._lock:
            for key, series in self._series.items():
                if series.name != name:
                    continue
                if labels:
                    if all(series.labels.get(k) == v for k, v in labels.items()):
                        results.append(series)
                else:
                    results.append(series)
        return results
    
    def get_all_names(self) -> List[str]:
        """Get all unique metric names."""
        with self._lock:
            return list(set(s.name for s in self._series.values()))
    
    def cleanup_old_data(self) -> int:
        """Remove data older than retention period."""
        cutoff = time.time() - self.config.retention_seconds
        removed = 0
        
        with self._lock:
            for series in self._series.values():
                while series.points and series.points[0][0] < cutoff:
                    series.points.popleft()
                    removed += 1
        
        return removed


@dataclass
class DashboardPanel:
    """A panel in the monitoring dashboard."""
    
    id: str
    title: str
    metric_name: str
    panel_type: str = "line_chart"  # line_chart, gauge, stat, table
    labels_filter: Dict[str, str] = field(default_factory=dict)
    aggregation: str = "none"  # none, sum, avg, max, min
    time_range: TimeRange = TimeRange.LAST_HOUR
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "metric_name": self.metric_name,
            "panel_type": self.panel_type,
            "labels_filter": self.labels_filter,
            "aggregation": self.aggregation,
            "time_range": self.time_range.value,
        }


class MonitoringDashboard:
    """
    Real-time security monitoring dashboard.
    
    Provides:
    - Metric collection and aggregation
    - Real-time data streaming
    - Panel-based visualization
    - Alert status integration
    """
    
    # Pre-defined security metrics
    SECURITY_METRICS = {
        "auth_attempts": MetricType.COUNTER,
        "auth_failures": MetricType.COUNTER,
        "auth_success": MetricType.COUNTER,
        "challenge_requests": MetricType.COUNTER,
        "challenge_failures": MetricType.COUNTER,
        "integrity_checks": MetricType.COUNTER,
        "integrity_failures": MetricType.COUNTER,
        "license_validations": MetricType.COUNTER,
        "license_rejections": MetricType.COUNTER,
        "api_requests": MetricType.COUNTER,
        "api_errors": MetricType.COUNTER,
        "api_latency_ms": MetricType.HISTOGRAM,
        "active_sessions": MetricType.GAUGE,
        "blocked_ips": MetricType.GAUGE,
        "anomaly_score": MetricType.GAUGE,
        "failsafe_mode": MetricType.GAUGE,
    }
    
    def __init__(self, config: DashboardConfig | None = None):
        self.config = config or DashboardConfig()
        self.registry = MetricRegistry(self.config)
        self.panels: Dict[str, DashboardPanel] = {}
        self._subscribers: List[Callable[[MetricPoint], None]] = []
        self._running = False
        self._cleanup_thread: threading.Thread | None = None
        self._lock = threading.RLock()
        
        # Initialize default panels
        self._setup_default_panels()
    
    def _setup_default_panels(self) -> None:
        """Set up default dashboard panels."""
        default_panels = [
            DashboardPanel(
                id="auth_overview",
                title="Authentication Overview",
                metric_name="auth_attempts",
                panel_type="line_chart",
            ),
            DashboardPanel(
                id="error_rate",
                title="Error Rate",
                metric_name="api_errors",
                panel_type="gauge",
                aggregation="rate",
            ),
            DashboardPanel(
                id="active_sessions",
                title="Active Sessions",
                metric_name="active_sessions",
                panel_type="stat",
            ),
            DashboardPanel(
                id="latency_p99",
                title="API Latency (p99)",
                metric_name="api_latency_ms",
                panel_type="line_chart",
                aggregation="p99",
            ),
            DashboardPanel(
                id="integrity_status",
                title="Integrity Check Status",
                metric_name="integrity_checks",
                panel_type="line_chart",
            ),
            DashboardPanel(
                id="anomaly_score",
                title="Anomaly Detection Score",
                metric_name="anomaly_score",
                panel_type="gauge",
            ),
        ]
        
        for panel in default_panels:
            self.panels[panel.id] = panel
    
    def record_metric(
        self,
        name: str,
        value: float,
        labels: Dict[str, str] | None = None,
        metric_type: MetricType | None = None
    ) -> None:
        """Record a metric value."""
        # Use pre-defined type if available
        if metric_type is None:
            metric_type = self.SECURITY_METRICS.get(name, MetricType.GAUGE)
        
        self.registry.record(name, value, labels, metric_type)
        
        # Notify subscribers
        point = MetricPoint(
            name=name,
            value=value,
            timestamp=time.time(),
            labels=labels or {},
            metric_type=metric_type,
        )
        self._notify_subscribers(point)
    
    def increment(
        self,
        name: str,
        amount: float = 1.0,
        labels: Dict[str, str] | None = None
    ) -> None:
        """Increment a counter metric."""
        labels = labels or {}
        series_list = self.registry.get_series(name, labels)
        
        if series_list:
            series = series_list[0]
            latest = series.get_latest()
            current = latest[1] if latest else 0.0
        else:
            current = 0.0
        
        self.record_metric(name, current + amount, labels, MetricType.COUNTER)
    
    def set_gauge(
        self,
        name: str,
        value: float,
        labels: Dict[str, str] | None = None
    ) -> None:
        """Set a gauge metric."""
        self.record_metric(name, value, labels, MetricType.GAUGE)
    
    def observe_latency(
        self,
        name: str,
        latency_ms: float,
        labels: Dict[str, str] | None = None
    ) -> None:
        """Record a latency observation."""
        self.record_metric(name, latency_ms, labels, MetricType.HISTOGRAM)
    
    def subscribe(self, callback: Callable[[MetricPoint], None]) -> None:
        """Subscribe to metric updates."""
        with self._lock:
            self._subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable[[MetricPoint], None]) -> None:
        """Unsubscribe from metric updates."""
        with self._lock:
            if callback in self._subscribers:
                self._subscribers.remove(callback)
    
    def _notify_subscribers(self, point: MetricPoint) -> None:
        """Notify all subscribers of new metric."""
        with self._lock:
            for callback in self._subscribers:
                try:
                    callback(point)
                except Exception:
                    pass  # Don't let subscriber errors affect monitoring
    
    def get_panel_data(
        self,
        panel_id: str,
        time_range: TimeRange | None = None
    ) -> Dict[str, Any]:
        """Get data for a specific panel."""
        if panel_id not in self.panels:
            return {"error": f"Panel not found: {panel_id}"}
        
        panel = self.panels[panel_id]
        tr = time_range or panel.time_range
        
        # Get time range
        end_time = time.time()
        start_time = end_time - tr.value
        
        # Get series
        series_list = self.registry.get_series(
            panel.metric_name,
            panel.labels_filter or None
        )
        
        data = {
            "panel": panel.to_dict(),
            "time_range": {"start": start_time, "end": end_time},
            "series": [],
        }
        
        for series in series_list:
            points = series.get_points(start_time, end_time)
            stats = series.calculate_statistics(tr.value)
            
            series_data = {
                "labels": series.labels,
                "points": points,
                "stats": stats,
            }
            
            # Calculate aggregations
            if panel.aggregation == "rate":
                series_data["rate"] = series.calculate_rate(tr.value)
            
            data["series"].append(series_data)
        
        return data
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get summary of all dashboard metrics."""
        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "panels": {},
            "health": "healthy",
            "alerts": [],
        }
        
        for panel_id, panel in self.panels.items():
            panel_data = self.get_panel_data(panel_id)
            
            # Extract current value
            current_value = 0.0
            if panel_data.get("series"):
                for s in panel_data["series"]:
                    if s.get("points"):
                        current_value = s["points"][-1][1]
                        break
            
            summary["panels"][panel_id] = {
                "title": panel.title,
                "current_value": current_value,
                "metric_name": panel.metric_name,
            }
        
        # Check health thresholds
        error_rate = self._calculate_error_rate()
        if error_rate > self.config.error_rate_threshold:
            summary["health"] = "degraded"
            summary["alerts"].append({
                "type": "error_rate",
                "message": f"Error rate {error_rate:.2%} exceeds threshold",
            })
        
        return summary
    
    def _calculate_error_rate(self) -> float:
        """Calculate current error rate."""
        total_series = self.registry.get_series("api_requests")
        error_series = self.registry.get_series("api_errors")
        
        total = 0.0
        errors = 0.0
        
        for s in total_series:
            latest = s.get_latest()
            if latest:
                total += latest[1]
        
        for s in error_series:
            latest = s.get_latest()
            if latest:
                errors += latest[1]
        
        if total == 0:
            return 0.0
        
        return errors / total
    
    def add_panel(self, panel: DashboardPanel) -> None:
        """Add a new panel to the dashboard."""
        with self._lock:
            self.panels[panel.id] = panel
    
    def remove_panel(self, panel_id: str) -> bool:
        """Remove a panel from the dashboard."""
        with self._lock:
            if panel_id in self.panels:
                del self.panels[panel_id]
                return True
            return False
    
    def start(self) -> None:
        """Start the dashboard background tasks."""
        if self._running:
            return
        
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True
        )
        self._cleanup_thread.start()
    
    def stop(self) -> None:
        """Stop the dashboard background tasks."""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5.0)
            self._cleanup_thread = None
    
    def _cleanup_loop(self) -> None:
        """Background loop for data cleanup."""
        while self._running:
            try:
                removed = self.registry.cleanup_old_data()
                if removed > 0:
                    pass  # Could log this
            except Exception:
                pass
            
            time.sleep(300)  # Cleanup every 5 minutes
    
    def export_metrics(self, format: str = "json") -> str:
        """Export all metrics in specified format."""
        if format == "json":
            return self._export_json()
        elif format == "prometheus":
            return self._export_prometheus()
        else:
            raise ValueError(f"Unknown export format: {format}")
    
    def _export_json(self) -> str:
        """Export metrics as JSON."""
        data = {
            "timestamp": time.time(),
            "metrics": {},
        }
        
        for name in self.registry.get_all_names():
            series_list = self.registry.get_series(name)
            data["metrics"][name] = []
            
            for series in series_list:
                latest = series.get_latest()
                if latest:
                    data["metrics"][name].append({
                        "labels": series.labels,
                        "value": latest[1],
                        "timestamp": latest[0],
                    })
        
        return json.dumps(data, indent=2)
    
    def _export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        for name in self.registry.get_all_names():
            series_list = self.registry.get_series(name)
            
            for series in series_list:
                latest = series.get_latest()
                if latest:
                    labels_str = ",".join(
                        f'{k}="{v}"' for k, v in series.labels.items()
                    )
                    if labels_str:
                        lines.append(f"{name}{{{labels_str}}} {latest[1]}")
                    else:
                        lines.append(f"{name} {latest[1]}")
        
        return "\n".join(lines)
    
    def __enter__(self) -> "MonitoringDashboard":
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop()


# Convenience functions for global dashboard
_global_dashboard: MonitoringDashboard | None = None


def get_dashboard() -> MonitoringDashboard:
    """Get or create the global dashboard instance."""
    global _global_dashboard
    if _global_dashboard is None:
        _global_dashboard = MonitoringDashboard()
    return _global_dashboard


def record_security_event(
    event_type: str,
    success: bool = True,
    labels: Dict[str, str] | None = None
) -> None:
    """Record a security event to the global dashboard."""
    dashboard = get_dashboard()
    
    metric_name = f"{event_type}_{'success' if success else 'failures'}"
    dashboard.increment(metric_name, labels=labels)
    
    # Also increment the total counter
    dashboard.increment(f"{event_type}_total", labels=labels)
