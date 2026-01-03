"""
Metrics Module - Phase 2 Week 13

Prometheus and OpenTelemetry metric exporters for
observability platform integration.

Copyright 2025 KR-Labs. All rights reserved.
"""

from __future__ import annotations

import http.server
import json
import socketserver
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
import hashlib


class MetricType(Enum):
    """Types of metrics."""
    
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class MetricPoint:
    """A single metric observation."""
    
    name: str
    value: float
    timestamp: float
    metric_type: MetricType
    labels: Dict[str, str] = field(default_factory=dict)
    unit: str = ""
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp,
            "type": self.metric_type.value,
            "labels": self.labels,
            "unit": self.unit,
            "description": self.description,
        }


@dataclass
class HistogramBucket:
    """A histogram bucket."""
    
    le: float  # Upper bound (less than or equal)
    count: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {"le": self.le, "count": self.count}


@dataclass
class HistogramMetric:
    """Histogram metric with buckets."""
    
    name: str
    labels: Dict[str, str]
    buckets: List[HistogramBucket]
    sum_value: float
    count: int
    
    DEFAULT_BUCKETS = [0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]


@dataclass
class SummaryMetric:
    """Summary metric with quantiles."""
    
    name: str
    labels: Dict[str, str]
    quantiles: Dict[float, float]  # quantile -> value
    sum_value: float
    count: int


@dataclass
class MetricsConfig:
    """Configuration for metrics collection."""
    
    # General
    enabled: bool = True
    prefix: str = "krl"
    
    # Collection
    collection_interval_seconds: float = 15.0
    
    # Prometheus
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    prometheus_path: str = "/metrics"
    
    # OpenTelemetry
    otlp_enabled: bool = False
    otlp_endpoint: str = "http://localhost:4317"
    otlp_headers: Dict[str, str] = field(default_factory=dict)
    
    # Histogram buckets
    latency_buckets: List[float] = field(
        default_factory=lambda: [0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
    )


class MetricRegistry:
    """Registry for collecting and storing metrics."""
    
    def __init__(self, prefix: str = "krl"):
        self.prefix = prefix
        self._counters: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self._gauges: Dict[str, Dict[str, float]] = defaultdict(dict)
        self._histograms: Dict[str, Dict[str, HistogramMetric]] = defaultdict(dict)
        self._summaries: Dict[str, Dict[str, SummaryMetric]] = defaultdict(dict)
        self._descriptions: Dict[str, str] = {}
        self._lock = threading.RLock()
    
    def _make_label_key(self, labels: Dict[str, str]) -> str:
        """Create key from labels for storage."""
        return ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
    
    def _full_name(self, name: str) -> str:
        """Get full metric name with prefix."""
        if self.prefix:
            return f"{self.prefix}_{name}"
        return name
    
    def describe(self, name: str, description: str) -> None:
        """Add description for a metric."""
        self._descriptions[self._full_name(name)] = description
    
    def counter_inc(
        self,
        name: str,
        amount: float = 1.0,
        labels: Dict[str, str] | None = None
    ) -> float:
        """Increment a counter."""
        full_name = self._full_name(name)
        label_key = self._make_label_key(labels or {})
        
        with self._lock:
            self._counters[full_name][label_key] += amount
            return self._counters[full_name][label_key]
    
    def gauge_set(
        self,
        name: str,
        value: float,
        labels: Dict[str, str] | None = None
    ) -> None:
        """Set a gauge value."""
        full_name = self._full_name(name)
        label_key = self._make_label_key(labels or {})
        
        with self._lock:
            self._gauges[full_name][label_key] = value
    
    def gauge_inc(
        self,
        name: str,
        amount: float = 1.0,
        labels: Dict[str, str] | None = None
    ) -> float:
        """Increment a gauge."""
        full_name = self._full_name(name)
        label_key = self._make_label_key(labels or {})
        
        with self._lock:
            current = self._gauges[full_name].get(label_key, 0.0)
            self._gauges[full_name][label_key] = current + amount
            return self._gauges[full_name][label_key]
    
    def gauge_dec(
        self,
        name: str,
        amount: float = 1.0,
        labels: Dict[str, str] | None = None
    ) -> float:
        """Decrement a gauge."""
        return self.gauge_inc(name, -amount, labels)
    
    def histogram_observe(
        self,
        name: str,
        value: float,
        labels: Dict[str, str] | None = None,
        buckets: List[float] | None = None
    ) -> None:
        """Record a histogram observation."""
        full_name = self._full_name(name)
        label_key = self._make_label_key(labels or {})
        bucket_bounds = buckets or HistogramMetric.DEFAULT_BUCKETS
        
        with self._lock:
            if label_key not in self._histograms[full_name]:
                self._histograms[full_name][label_key] = HistogramMetric(
                    name=full_name,
                    labels=labels or {},
                    buckets=[HistogramBucket(le=b, count=0) for b in bucket_bounds] + [HistogramBucket(le=float('inf'), count=0)],
                    sum_value=0.0,
                    count=0
                )
            
            hist = self._histograms[full_name][label_key]
            hist.sum_value += value
            hist.count += 1
            
            for bucket in hist.buckets:
                if value <= bucket.le:
                    bucket.count += 1
    
    def get_all_metrics(self) -> List[MetricPoint]:
        """Get all metrics as MetricPoints."""
        points = []
        
        with self._lock:
            # Counters
            for name, label_values in self._counters.items():
                for label_key, value in label_values.items():
                    labels = dict(item.split("=") for item in label_key.split(",") if "=" in item) if label_key else {}
                    points.append(MetricPoint(
                        name=name,
                        value=value,
                        timestamp=time.time(),
                        metric_type=MetricType.COUNTER,
                        labels=labels,
                        description=self._descriptions.get(name, "")
                    ))
            
            # Gauges
            for name, label_values in self._gauges.items():
                for label_key, value in label_values.items():
                    labels = dict(item.split("=") for item in label_key.split(",") if "=" in item) if label_key else {}
                    points.append(MetricPoint(
                        name=name,
                        value=value,
                        timestamp=time.time(),
                        metric_type=MetricType.GAUGE,
                        labels=labels,
                        description=self._descriptions.get(name, "")
                    ))
        
        return points


class MetricsCollector:
    """
    Collects and manages application metrics.
    
    Provides convenient API for recording metrics and
    supports multiple export formats.
    """
    
    def __init__(self, config: MetricsConfig | None = None):
        self.config = config or MetricsConfig()
        self.registry = MetricRegistry(self.config.prefix)
        self._collectors: List[Callable[[], List[MetricPoint]]] = []
        self._lock = threading.RLock()
    
    def inc(
        self,
        name: str,
        amount: float = 1.0,
        labels: Dict[str, str] | None = None
    ) -> None:
        """Increment a counter."""
        self.registry.counter_inc(name, amount, labels)
    
    def set(
        self,
        name: str,
        value: float,
        labels: Dict[str, str] | None = None
    ) -> None:
        """Set a gauge value."""
        self.registry.gauge_set(name, value, labels)
    
    def observe(
        self,
        name: str,
        value: float,
        labels: Dict[str, str] | None = None
    ) -> None:
        """Record a histogram observation."""
        self.registry.histogram_observe(name, value, labels, self.config.latency_buckets)
    
    def timer(self, name: str, labels: Dict[str, str] | None = None):
        """Context manager for timing operations."""
        return TimerContext(self, name, labels)
    
    def describe(self, name: str, description: str) -> None:
        """Add description for a metric."""
        self.registry.describe(name, description)
    
    def register_collector(self, collector: Callable[[], List[MetricPoint]]) -> None:
        """Register a custom metric collector."""
        with self._lock:
            self._collectors.append(collector)
    
    def collect(self) -> List[MetricPoint]:
        """Collect all metrics."""
        points = self.registry.get_all_metrics()
        
        # Run custom collectors
        for collector in self._collectors:
            try:
                points.extend(collector())
            except Exception:
                pass
        
        return points


class TimerContext:
    """Context manager for timing operations."""
    
    def __init__(
        self,
        collector: MetricsCollector,
        name: str,
        labels: Dict[str, str] | None
    ):
        self.collector = collector
        self.name = name
        self.labels = labels
        self.start_time: float = 0
    
    def __enter__(self) -> "TimerContext":
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        duration = time.time() - self.start_time
        self.collector.observe(self.name, duration, self.labels)


class PrometheusExporter:
    """
    Exports metrics in Prometheus format.
    
    Provides HTTP endpoint for Prometheus scraping.
    """
    
    def __init__(
        self,
        collector: MetricsCollector,
        port: int = 9090,
        path: str = "/metrics"
    ):
        self.collector = collector
        self.port = port
        self.path = path
        self._server: socketserver.TCPServer | None = None
        self._thread: threading.Thread | None = None
    
    def format_metrics(self) -> str:
        """Format metrics in Prometheus text format."""
        lines = []
        points = self.collector.collect()
        
        # Group by name
        by_name: Dict[str, List[MetricPoint]] = defaultdict(list)
        for point in points:
            by_name[point.name].append(point)
        
        for name, metric_points in sorted(by_name.items()):
            # Add HELP and TYPE if available
            if metric_points:
                first = metric_points[0]
                if first.description:
                    lines.append(f"# HELP {name} {first.description}")
                lines.append(f"# TYPE {name} {first.metric_type.value}")
            
            # Add metric values
            for point in metric_points:
                if point.labels:
                    labels_str = ",".join(f'{k}="{v}"' for k, v in point.labels.items())
                    lines.append(f"{name}{{{labels_str}}} {point.value}")
                else:
                    lines.append(f"{name} {point.value}")
        
        return "\n".join(lines) + "\n"
    
    def start(self) -> None:
        """Start the HTTP server."""
        exporter = self
        
        class MetricsHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == exporter.path:
                    content = exporter.format_metrics().encode()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.send_header("Content-Length", len(content))
                    self.end_headers()
                    self.wfile.write(content)
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                pass  # Suppress logging
        
        self._server = socketserver.TCPServer(("", self.port), MetricsHandler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        """Stop the HTTP server."""
        if self._server:
            self._server.shutdown()
            self._server = None
        if self._thread:
            self._thread.join(timeout=5.0)
            self._thread = None


class OpenTelemetryExporter:
    """
    Exports metrics in OpenTelemetry format.
    
    Sends metrics to OTLP endpoint.
    """
    
    def __init__(
        self,
        collector: MetricsCollector,
        endpoint: str = "http://localhost:4317",
        headers: Dict[str, str] | None = None
    ):
        self.collector = collector
        self.endpoint = endpoint
        self.headers = headers or {}
        self._running = False
        self._thread: threading.Thread | None = None
        self._interval = 15.0
    
    def format_otlp(self) -> Dict[str, Any]:
        """Format metrics in OTLP JSON format."""
        points = self.collector.collect()
        
        # Build OTLP structure
        resource_metrics = {
            "resourceMetrics": [{
                "resource": {
                    "attributes": [
                        {"key": "service.name", "value": {"stringValue": "krl-data-connectors"}},
                    ]
                },
                "scopeMetrics": [{
                    "scope": {
                        "name": "krl.metrics",
                        "version": "1.0.0"
                    },
                    "metrics": []
                }]
            }]
        }
        
        metrics = resource_metrics["resourceMetrics"][0]["scopeMetrics"][0]["metrics"]
        
        for point in points:
            metric = {
                "name": point.name,
                "description": point.description,
            }
            
            if point.metric_type == MetricType.COUNTER:
                metric["sum"] = {
                    "dataPoints": [{
                        "asDouble": point.value,
                        "timeUnixNano": int(point.timestamp * 1e9),
                        "attributes": [{"key": k, "value": {"stringValue": v}} for k, v in point.labels.items()]
                    }],
                    "aggregationTemporality": 2,  # CUMULATIVE
                    "isMonotonic": True
                }
            elif point.metric_type == MetricType.GAUGE:
                metric["gauge"] = {
                    "dataPoints": [{
                        "asDouble": point.value,
                        "timeUnixNano": int(point.timestamp * 1e9),
                        "attributes": [{"key": k, "value": {"stringValue": v}} for k, v in point.labels.items()]
                    }]
                }
            
            metrics.append(metric)
        
        return resource_metrics
    
    def export(self) -> bool:
        """Export metrics to OTLP endpoint."""
        import urllib.request
        import urllib.error
        
        try:
            data = json.dumps(self.format_otlp()).encode()
            
            headers = {
                "Content-Type": "application/json",
                **self.headers
            }
            
            req = urllib.request.Request(
                f"{self.endpoint}/v1/metrics",
                data=data,
                headers=headers,
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                return 200 <= response.status < 300
        except Exception:
            return False
    
    def start(self, interval: float = 15.0) -> None:
        """Start periodic export."""
        self._interval = interval
        self._running = True
        self._thread = threading.Thread(target=self._export_loop, daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        """Stop periodic export."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
            self._thread = None
    
    def _export_loop(self) -> None:
        """Background export loop."""
        while self._running:
            try:
                self.export()
            except Exception:
                pass
            time.sleep(self._interval)


# Pre-defined metrics for KRL security monitoring
class SecurityMetrics:
    """Pre-defined security metrics."""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self._setup_metrics()
    
    def _setup_metrics(self) -> None:
        """Set up metric descriptions."""
        descriptions = {
            "auth_attempts_total": "Total authentication attempts",
            "auth_failures_total": "Total authentication failures",
            "license_validations_total": "Total license validations",
            "license_rejections_total": "Total license rejections",
            "api_requests_total": "Total API requests",
            "api_errors_total": "Total API errors",
            "api_latency_seconds": "API request latency in seconds",
            "active_sessions": "Number of active sessions",
            "integrity_checks_total": "Total integrity checks",
            "integrity_failures_total": "Total integrity check failures",
            "challenge_requests_total": "Total challenge-response requests",
            "challenge_failures_total": "Total challenge-response failures",
            "anomaly_score": "Current anomaly detection score",
            "failsafe_mode": "Current failsafe mode (0=normal, 1=degraded, 2=blocked)",
        }
        
        for name, desc in descriptions.items():
            self.collector.describe(name, desc)
    
    def record_auth_attempt(self, success: bool, method: str = "api_key") -> None:
        """Record authentication attempt."""
        labels = {"method": method}
        self.collector.inc("auth_attempts_total", labels=labels)
        if not success:
            self.collector.inc("auth_failures_total", labels=labels)
    
    def record_license_validation(self, valid: bool, tier: str = "unknown") -> None:
        """Record license validation."""
        labels = {"tier": tier}
        self.collector.inc("license_validations_total", labels=labels)
        if not valid:
            self.collector.inc("license_rejections_total", labels=labels)
    
    def record_api_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        latency_seconds: float
    ) -> None:
        """Record API request."""
        labels = {"endpoint": endpoint, "method": method, "status": str(status_code)}
        self.collector.inc("api_requests_total", labels=labels)
        
        if status_code >= 400:
            self.collector.inc("api_errors_total", labels=labels)
        
        self.collector.observe("api_latency_seconds", latency_seconds, labels={"endpoint": endpoint})
    
    def set_active_sessions(self, count: int) -> None:
        """Set active sessions count."""
        self.collector.set("active_sessions", count)
    
    def record_integrity_check(self, passed: bool) -> None:
        """Record integrity check."""
        self.collector.inc("integrity_checks_total")
        if not passed:
            self.collector.inc("integrity_failures_total")
    
    def record_challenge(self, success: bool) -> None:
        """Record challenge-response."""
        self.collector.inc("challenge_requests_total")
        if not success:
            self.collector.inc("challenge_failures_total")
    
    def set_anomaly_score(self, score: float) -> None:
        """Set current anomaly score."""
        self.collector.set("anomaly_score", score)
    
    def set_failsafe_mode(self, mode: int) -> None:
        """Set failsafe mode (0=normal, 1=degraded, 2=blocked)."""
        self.collector.set("failsafe_mode", mode)


# Global instance
_global_collector: MetricsCollector | None = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector."""
    global _global_collector
    if _global_collector is None:
        _global_collector = MetricsCollector()
    return _global_collector
