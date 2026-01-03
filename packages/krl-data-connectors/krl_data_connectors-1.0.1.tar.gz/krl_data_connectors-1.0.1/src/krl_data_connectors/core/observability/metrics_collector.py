# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Defense Metrics Collector - Phase 3 Week 18

Centralized metrics collection for all defense subsystems.
Provides a unified interface for:
- Registering and collecting metrics
- Buffered collection with flush
- Adaptive sampling for high-volume metrics
- Export to Prometheus, StatsD, OpenTelemetry

Defense Metrics Catalog (20+ metrics):
- Enforcement: events, duration, active count
- ML: inference duration, budget violations, anomaly scores
- License: refresh, validation, active count
- Policy: updates, delivery duration, success rate
- Revenue: protection events, prevented leakage
"""

from __future__ import annotations

import asyncio
import logging
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from contextlib import contextmanager

from .metric_types import (
    MetricBase,
    Counter,
    Gauge,
    Histogram,
    Summary,
    MetricValue,
    LabelSet,
)

logger = logging.getLogger("krl.observability.metrics")


# =============================================================================
# Sampling Strategies
# =============================================================================

class SamplingStrategy(Enum):
    """Sampling strategies for high-volume metrics."""
    
    NONE = auto()           # No sampling, collect all
    RANDOM = auto()         # Random sampling
    RATE_LIMIT = auto()     # Rate-limited sampling
    ADAPTIVE = auto()       # Adaptive based on volume


@dataclass
class SamplingConfig:
    """Configuration for metric sampling."""
    
    strategy: SamplingStrategy = SamplingStrategy.NONE
    sample_rate: float = 1.0       # 0.0 to 1.0 for random sampling
    max_per_second: float = 1000   # For rate limiting
    adaptive_threshold: int = 100  # Volume threshold for adaptive
    
    def should_sample(self, current_rate: float) -> bool:
        """Determine if current observation should be sampled."""
        if self.strategy == SamplingStrategy.NONE:
            return True
        
        if self.strategy == SamplingStrategy.RANDOM:
            import random
            return random.random() < self.sample_rate
        
        if self.strategy == SamplingStrategy.RATE_LIMIT:
            return current_rate < self.max_per_second
        
        if self.strategy == SamplingStrategy.ADAPTIVE:
            if current_rate < self.adaptive_threshold:
                return True
            # Reduce sampling as rate increases
            return (self.adaptive_threshold / current_rate) > 0.1
        
        return True


# =============================================================================
# Metric Buffer
# =============================================================================

@dataclass
class BufferedMetric:
    """A metric value waiting to be flushed."""
    
    metric_name: str
    value: float
    timestamp: float
    labels: Dict[str, str]
    metric_type: str


class MetricBuffer:
    """
    Buffer for metric observations before flush.
    
    Collects metrics in memory and periodically flushes
    to configured exporters. Reduces overhead for high-volume
    metric collection.
    """
    
    def __init__(
        self,
        max_size: int = 10000,
        flush_interval: float = 10.0,
        auto_flush: bool = True,
    ):
        self._buffer: List[BufferedMetric] = []
        self._lock = threading.Lock()
        self._max_size = max_size
        self._flush_interval = flush_interval
        self._auto_flush = auto_flush
        self._flush_callbacks: List[Callable[[List[BufferedMetric]], None]] = []
        self._last_flush = time.time()
        
        if auto_flush:
            self._start_flush_thread()
    
    def _start_flush_thread(self) -> None:
        """Start background flush thread."""
        def flush_loop():
            while self._auto_flush:
                time.sleep(self._flush_interval)
                self.flush()
        
        thread = threading.Thread(target=flush_loop, daemon=True)
        thread.start()
    
    def add(self, metric: BufferedMetric) -> None:
        """Add a metric to the buffer."""
        with self._lock:
            self._buffer.append(metric)
            
            # Auto-flush if buffer is full
            if len(self._buffer) >= self._max_size:
                self._flush_internal()
    
    def flush(self) -> List[BufferedMetric]:
        """Flush buffer and return metrics."""
        with self._lock:
            return self._flush_internal()
    
    def _flush_internal(self) -> List[BufferedMetric]:
        """Internal flush without lock."""
        metrics = self._buffer
        self._buffer = []
        self._last_flush = time.time()
        
        # Call flush callbacks
        for callback in self._flush_callbacks:
            try:
                callback(metrics)
            except Exception as e:
                logger.error(f"Flush callback error: {e}")
        
        return metrics
    
    def on_flush(self, callback: Callable[[List[BufferedMetric]], None]) -> None:
        """Register a callback for flush events."""
        self._flush_callbacks.append(callback)
    
    def size(self) -> int:
        """Get current buffer size."""
        with self._lock:
            return len(self._buffer)
    
    def stop(self) -> None:
        """Stop auto-flush."""
        self._auto_flush = False


# =============================================================================
# Defense Metrics Collector
# =============================================================================

class DefenseMetricsCollector:
    """
    Centralized collector for all defense metrics.
    
    Provides a unified interface for registering, collecting,
    and exporting defense metrics across all subsystems.
    
    Usage:
        >>> collector = DefenseMetricsCollector()
        >>> 
        >>> # Record enforcement
        >>> collector.record_enforcement(tier="warn", action="throttle")
        >>> 
        >>> # Time ML inference
        >>> with collector.time_ml_inference(model="anomaly"):
        ...     result = model.predict(features)
        >>> 
        >>> # Export metrics
        >>> metrics = collector.collect_all()
    """
    
    def __init__(
        self,
        prefix: str = "krl",
        buffer: Optional[MetricBuffer] = None,
        sampling: Optional[SamplingConfig] = None,
    ):
        self._prefix = prefix
        self._buffer = buffer or MetricBuffer()
        self._sampling = sampling or SamplingConfig()
        self._lock = threading.RLock()
        
        # Rate tracking for sampling
        self._rate_tracker: Dict[str, List[float]] = defaultdict(list)
        self._rate_window = 1.0  # 1 second window
        
        # Initialize all defense metrics
        self._init_metrics()
    
    def _init_metrics(self) -> None:
        """Initialize all defense metrics."""
        
        # =================================================================
        # Enforcement Metrics
        # =================================================================
        
        self.enforcement_total = Counter(
            name=f"{self._prefix}_enforcement_events_total",
            description="Total enforcement events",
            labels=["tier", "action", "reason"],
        )
        
        self.enforcement_duration = Histogram(
            name=f"{self._prefix}_enforcement_duration_seconds",
            description="Enforcement action duration",
            labels=["tier"],
            buckets=Histogram.DEFAULT_BUCKETS,
        )
        
        self.active_enforcements = Gauge(
            name=f"{self._prefix}_active_enforcements",
            description="Currently active enforcements",
            labels=["tier"],
        )
        
        self.enforcement_escalations = Counter(
            name=f"{self._prefix}_enforcement_escalations_total",
            description="Enforcement tier escalations",
            labels=["from_tier", "to_tier"],
        )
        
        self.enforcement_deescalations = Counter(
            name=f"{self._prefix}_enforcement_deescalations_total",
            description="Enforcement tier de-escalations",
            labels=["from_tier", "to_tier"],
        )
        
        # =================================================================
        # ML Metrics
        # =================================================================
        
        self.ml_inference_duration = Histogram(
            name=f"{self._prefix}_ml_inference_duration_seconds",
            description="ML model inference duration",
            labels=["model"],
            buckets=Histogram.ML_INFERENCE_BUCKETS,
        )
        
        self.ml_budget_violations = Counter(
            name=f"{self._prefix}_ml_budget_violations_total",
            description="ML inference budget violations",
            labels=["model", "severity"],
        )
        
        self.ml_predictions = Counter(
            name=f"{self._prefix}_ml_predictions_total",
            description="Total ML predictions",
            labels=["model", "result"],
        )
        
        self.anomaly_score = Histogram(
            name=f"{self._prefix}_anomaly_score_distribution",
            description="Distribution of anomaly scores",
            labels=["model"],
            buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
        )
        
        self.model_drift = Gauge(
            name=f"{self._prefix}_model_drift_score",
            description="Current model drift score",
            labels=["model"],
        )
        
        # =================================================================
        # License Metrics
        # =================================================================
        
        self.token_refresh_total = Counter(
            name=f"{self._prefix}_token_refresh_total",
            description="Total token refresh attempts",
            labels=["status", "tier"],
        )
        
        self.token_validation_duration = Histogram(
            name=f"{self._prefix}_token_validation_duration_seconds",
            description="Token validation duration",
            labels=["tier"],
        )
        
        self.active_licenses = Gauge(
            name=f"{self._prefix}_active_licenses",
            description="Currently active licenses",
            labels=["tier"],
        )
        
        self.license_anomalies = Counter(
            name=f"{self._prefix}_license_anomalies_total",
            description="License anomalies detected",
            labels=["type"],
        )
        
        # =================================================================
        # Policy Metrics
        # =================================================================
        
        self.policy_updates = Counter(
            name=f"{self._prefix}_policy_updates_total",
            description="Total policy updates received",
            labels=["type", "status"],
        )
        
        self.policy_delivery_duration = Histogram(
            name=f"{self._prefix}_policy_delivery_duration_seconds",
            description="Policy delivery duration",
            labels=["channel"],
        )
        
        self.policy_delivery_success = Gauge(
            name=f"{self._prefix}_policy_delivery_success_rate",
            description="Policy delivery success rate",
            labels=["channel"],
        )
        
        self.policy_version = Gauge(
            name=f"{self._prefix}_policy_version_current",
            description="Current policy version",
            labels=["policy_type"],
        )
        
        # =================================================================
        # Revenue Protection Metrics
        # =================================================================
        
        self.revenue_protection_events = Counter(
            name=f"{self._prefix}_revenue_protection_events_total",
            description="Revenue protection events",
            labels=["type", "tier"],
        )
        
        self.prevented_leakage = Gauge(
            name=f"{self._prefix}_prevented_leakage_value",
            description="Estimated revenue leakage prevented",
            unit="usd",
        )
        
        self.upgrade_opportunities = Counter(
            name=f"{self._prefix}_upgrade_opportunities_total",
            description="Upgrade opportunities identified",
            labels=["from_tier", "trigger"],
        )
        
        # =================================================================
        # Telemetry Metrics
        # =================================================================
        
        self.telemetry_events = Counter(
            name=f"{self._prefix}_telemetry_events_total",
            description="Telemetry events received",
            labels=["type"],
        )
        
        self.telemetry_ingestion_duration = Histogram(
            name=f"{self._prefix}_telemetry_ingestion_duration_seconds",
            description="Telemetry ingestion duration",
        )
        
        # =================================================================
        # Defense Liveness Score Components
        # =================================================================
        
        self.detection_accuracy = Gauge(
            name=f"{self._prefix}_detection_accuracy",
            description="Detection accuracy (true positive rate)",
        )
        
        self.false_positive_rate = Gauge(
            name=f"{self._prefix}_false_positive_rate",
            description="Current false positive rate",
        )
        
        self.drift_rate = Gauge(
            name=f"{self._prefix}_drift_rate",
            description="Overall drift rate across models",
        )
        
        # =================================================================
        # Performance Budget Metrics
        # =================================================================
        
        self.budget_status = Gauge(
            name=f"{self._prefix}_budget_status",
            description="Performance budget status (1=ok, 0=violated)",
            labels=["component"],
        )
        
        self.budget_utilization = Gauge(
            name=f"{self._prefix}_budget_utilization_ratio",
            description="Budget utilization ratio",
            labels=["component"],
        )
        
        # Store all metrics for collection
        self._all_metrics: List[MetricBase] = [
            self.enforcement_total,
            self.enforcement_duration,
            self.active_enforcements,
            self.enforcement_escalations,
            self.enforcement_deescalations,
            self.ml_inference_duration,
            self.ml_budget_violations,
            self.ml_predictions,
            self.anomaly_score,
            self.model_drift,
            self.token_refresh_total,
            self.token_validation_duration,
            self.active_licenses,
            self.license_anomalies,
            self.policy_updates,
            self.policy_delivery_duration,
            self.policy_delivery_success,
            self.policy_version,
            self.revenue_protection_events,
            self.prevented_leakage,
            self.upgrade_opportunities,
            self.telemetry_events,
            self.telemetry_ingestion_duration,
            self.detection_accuracy,
            self.false_positive_rate,
            self.drift_rate,
            self.budget_status,
            self.budget_utilization,
        ]
    
    # =========================================================================
    # Convenience Methods for Recording
    # =========================================================================
    
    def record_enforcement(
        self,
        tier: str,
        action: str,
        reason: str = "unknown",
        duration: Optional[float] = None,
    ) -> None:
        """Record an enforcement event."""
        self.enforcement_total.inc(tier=tier, action=action, reason=reason)
        if duration is not None:
            self.enforcement_duration.observe(duration, tier=tier)
    
    def record_escalation(self, from_tier: str, to_tier: str) -> None:
        """Record enforcement escalation."""
        self.enforcement_escalations.inc(from_tier=from_tier, to_tier=to_tier)
    
    def record_deescalation(self, from_tier: str, to_tier: str) -> None:
        """Record enforcement de-escalation."""
        self.enforcement_deescalations.inc(from_tier=from_tier, to_tier=to_tier)
    
    @contextmanager
    def time_ml_inference(self, model: str):
        """Context manager for timing ML inference."""
        start = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start
            self.ml_inference_duration.observe(duration, model=model)
    
    def record_ml_prediction(
        self,
        model: str,
        result: str,
        score: Optional[float] = None,
    ) -> None:
        """Record ML prediction."""
        self.ml_predictions.inc(model=model, result=result)
        if score is not None:
            self.anomaly_score.observe(score, model=model)
    
    def record_budget_violation(
        self,
        model: str,
        severity: str = "warning",
    ) -> None:
        """Record ML budget violation."""
        self.ml_budget_violations.inc(model=model, severity=severity)
    
    def record_token_refresh(
        self,
        status: str,
        tier: str,
        duration: Optional[float] = None,
    ) -> None:
        """Record token refresh attempt."""
        self.token_refresh_total.inc(status=status, tier=tier)
        if duration is not None:
            self.token_validation_duration.observe(duration, tier=tier)
    
    def record_policy_update(
        self,
        policy_type: str,
        status: str,
        duration: Optional[float] = None,
        channel: str = "pull",
    ) -> None:
        """Record policy update."""
        self.policy_updates.inc(type=policy_type, status=status)
        if duration is not None:
            self.policy_delivery_duration.observe(duration, channel=channel)
    
    def record_revenue_protection(
        self,
        event_type: str,
        tier: str,
        value: Optional[float] = None,
    ) -> None:
        """Record revenue protection event."""
        self.revenue_protection_events.inc(type=event_type, tier=tier)
        if value is not None:
            current = self.prevented_leakage.get()
            self.prevented_leakage.set(current + value)
    
    def record_telemetry(self, event_type: str) -> None:
        """Record telemetry event."""
        self.telemetry_events.inc(type=event_type)
    
    @contextmanager
    def time_telemetry_ingestion(self):
        """Context manager for timing telemetry ingestion."""
        start = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start
            self.telemetry_ingestion_duration.observe(duration)
    
    def update_liveness_components(
        self,
        detection_accuracy: Optional[float] = None,
        false_positive_rate: Optional[float] = None,
        drift_rate: Optional[float] = None,
    ) -> None:
        """Update Defense Liveness Score components."""
        if detection_accuracy is not None:
            self.detection_accuracy.set(detection_accuracy)
        if false_positive_rate is not None:
            self.false_positive_rate.set(false_positive_rate)
        if drift_rate is not None:
            self.drift_rate.set(drift_rate)
    
    def update_budget_status(
        self,
        component: str,
        within_budget: bool,
        utilization: float,
    ) -> None:
        """Update performance budget status."""
        self.budget_status.set(1.0 if within_budget else 0.0, component=component)
        self.budget_utilization.set(utilization, component=component)
    
    # =========================================================================
    # Collection and Export
    # =========================================================================
    
    def collect_all(self) -> List[MetricValue]:
        """Collect all metric values."""
        all_values = []
        for metric in self._all_metrics:
            all_values.extend(metric.collect())
        return all_values
    
    def to_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        for metric in self._all_metrics:
            # Add HELP and TYPE
            lines.append(f"# HELP {metric.name} {metric.description}")
            lines.append(f"# TYPE {metric.name} {metric.__class__.__name__.lower()}")
            
            for value in metric.collect():
                labels_str = ""
                if value.labels.labels:
                    label_pairs = [f'{k}="{v}"' for k, v in value.labels.labels]
                    labels_str = "{" + ",".join(label_pairs) + "}"
                
                lines.append(f"{metric.name}{labels_str} {value.value}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export metrics as dictionary."""
        result = {}
        for metric in self._all_metrics:
            metric_data = metric.to_dict()
            metric_data["values"] = [v.to_dict() for v in metric.collect()]
            result[metric.name] = metric_data
        return result
    
    def reset_all(self) -> None:
        """Reset all metrics."""
        for metric in self._all_metrics:
            metric.reset()


# =============================================================================
# Global Collector Instance
# =============================================================================

_global_collector: Optional[DefenseMetricsCollector] = None


def get_metrics_collector() -> DefenseMetricsCollector:
    """Get or create the global metrics collector."""
    global _global_collector
    if _global_collector is None:
        _global_collector = DefenseMetricsCollector()
    return _global_collector


def set_metrics_collector(collector: DefenseMetricsCollector) -> None:
    """Set the global metrics collector."""
    global _global_collector
    _global_collector = collector


# Backwards-compatible alias
DefenseMetrics = DefenseMetricsCollector
