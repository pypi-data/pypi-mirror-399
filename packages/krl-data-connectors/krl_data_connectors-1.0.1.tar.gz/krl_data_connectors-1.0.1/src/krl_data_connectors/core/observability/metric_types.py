# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Metric Types - Phase 3 Week 18

Core metric type implementations for defense observability:
- Counter: Monotonically increasing values (events, requests)
- Gauge: Point-in-time values (active connections, queue size)
- Histogram: Distribution tracking with buckets (latencies)
- Summary: Streaming quantile calculation (percentiles)

These types form the foundation for all defense metrics collection.
"""

from __future__ import annotations

import threading
import time
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Callable
from collections import deque


# =============================================================================
# Label Types
# =============================================================================

@dataclass(frozen=True)
class LabelSet:
    """
    Immutable set of labels for a metric.
    
    Labels provide dimensional data for metrics, allowing filtering
    and aggregation across different dimensions.
    """
    labels: Tuple[Tuple[str, str], ...]
    
    def __init__(self, labels: Optional[Dict[str, str]] = None):
        if labels:
            # Sort for consistent hashing
            sorted_labels = tuple(sorted(labels.items()))
        else:
            sorted_labels = ()
        object.__setattr__(self, 'labels', sorted_labels)
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return dict(self.labels)
    
    def with_labels(self, **kwargs: str) -> "LabelSet":
        """Create new LabelSet with additional labels."""
        combined = dict(self.labels)
        combined.update(kwargs)
        return LabelSet(combined)
    
    def __hash__(self) -> int:
        return hash(self.labels)
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, LabelSet):
            return self.labels == other.labels
        return False


# Backwards-compatible alias
MetricLabels = LabelSet


@dataclass
class MetricValue:
    """
    A metric value with timestamp and labels.
    
    Attributes:
        value: The numeric metric value
        timestamp: Unix timestamp of observation
        labels: Associated labels
    """
    value: float
    timestamp: float
    labels: LabelSet = field(default_factory=LabelSet)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "timestamp": self.timestamp,
            "labels": self.labels.to_dict(),
        }


# =============================================================================
# Base Metric Class
# =============================================================================

class MetricBase(ABC):
    """
    Base class for all metric types.
    
    Provides common functionality for metric registration,
    labeling, and serialization.
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        unit: str = "",
        labels: Optional[List[str]] = None,
    ):
        self.name = name
        self.description = description
        self.unit = unit
        self.label_names = labels or []
        self._lock = threading.RLock()
        self._created_at = time.time()
    
    @abstractmethod
    def collect(self) -> List[MetricValue]:
        """Collect all metric values."""
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset the metric."""
        pass
    
    def _validate_labels(self, labels: Dict[str, str]) -> None:
        """Validate that provided labels match declared label names."""
        provided = set(labels.keys())
        expected = set(self.label_names)
        if provided != expected:
            raise ValueError(
                f"Label mismatch for {self.name}: "
                f"expected {expected}, got {provided}"
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize metric metadata."""
        return {
            "name": self.name,
            "description": self.description,
            "unit": self.unit,
            "labels": self.label_names,
            "type": self.__class__.__name__.lower(),
        }


# =============================================================================
# Counter
# =============================================================================

class Counter(MetricBase):
    """
    A monotonically increasing counter.
    
    Counters are used for values that only increase, such as:
    - Total requests processed
    - Errors encountered
    - Enforcement actions taken
    
    Example:
        >>> counter = Counter("enforcement_total", labels=["tier", "action"])
        >>> counter.inc(tier="community", action="throttle")
        >>> counter.inc(5, tier="pro", action="warn")
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        unit: str = "",
        labels: Optional[List[str]] = None,
    ):
        super().__init__(name, description, unit, labels)
        self._values: Dict[LabelSet, float] = {}
    
    def inc(self, amount: float = 1.0, **labels: str) -> float:
        """
        Increment the counter.
        
        Args:
            amount: Amount to increment (must be positive)
            **labels: Label values
            
        Returns:
            New counter value
        """
        if amount < 0:
            raise ValueError("Counter increment must be non-negative")
        
        if self.label_names:
            self._validate_labels(labels)
        
        label_set = LabelSet(labels) if labels else LabelSet()
        
        with self._lock:
            current = self._values.get(label_set, 0.0)
            new_value = current + amount
            self._values[label_set] = new_value
            return new_value
    
    def get(self, **labels: str) -> float:
        """Get current counter value for labels."""
        label_set = LabelSet(labels) if labels else LabelSet()
        with self._lock:
            return self._values.get(label_set, 0.0)
    
    def collect(self) -> List[MetricValue]:
        """Collect all counter values."""
        now = time.time()
        with self._lock:
            return [
                MetricValue(value=v, timestamp=now, labels=ls)
                for ls, v in self._values.items()
            ]
    
    def reset(self) -> None:
        """Reset all counter values to zero."""
        with self._lock:
            self._values.clear()


# =============================================================================
# Gauge
# =============================================================================

class Gauge(MetricBase):
    """
    A gauge metric that can go up or down.
    
    Gauges are used for values that can increase or decrease:
    - Active connections
    - Queue depth
    - Memory usage
    - Current risk score
    
    Example:
        >>> gauge = Gauge("active_enforcements", labels=["tier"])
        >>> gauge.set(5, tier="community")
        >>> gauge.inc(tier="community")  # Now 6
        >>> gauge.dec(2, tier="community")  # Now 4
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        unit: str = "",
        labels: Optional[List[str]] = None,
    ):
        super().__init__(name, description, unit, labels)
        self._values: Dict[LabelSet, float] = {}
    
    def set(self, value: float, **labels: str) -> None:
        """Set gauge to a specific value."""
        if self.label_names:
            self._validate_labels(labels)
        
        label_set = LabelSet(labels) if labels else LabelSet()
        
        with self._lock:
            self._values[label_set] = value
    
    def inc(self, amount: float = 1.0, **labels: str) -> float:
        """Increment gauge value."""
        if self.label_names:
            self._validate_labels(labels)
        
        label_set = LabelSet(labels) if labels else LabelSet()
        
        with self._lock:
            current = self._values.get(label_set, 0.0)
            new_value = current + amount
            self._values[label_set] = new_value
            return new_value
    
    def dec(self, amount: float = 1.0, **labels: str) -> float:
        """Decrement gauge value."""
        return self.inc(-amount, **labels)
    
    def get(self, **labels: str) -> float:
        """Get current gauge value."""
        label_set = LabelSet(labels) if labels else LabelSet()
        with self._lock:
            return self._values.get(label_set, 0.0)
    
    def set_to_current_time(self, **labels: str) -> None:
        """Set gauge to current Unix timestamp."""
        self.set(time.time(), **labels)
    
    def track_inprogress(self, **labels: str):
        """Context manager to track in-progress operations."""
        return _GaugeInProgress(self, labels)
    
    def collect(self) -> List[MetricValue]:
        """Collect all gauge values."""
        now = time.time()
        with self._lock:
            return [
                MetricValue(value=v, timestamp=now, labels=ls)
                for ls, v in self._values.items()
            ]
    
    def reset(self) -> None:
        """Reset all gauge values."""
        with self._lock:
            self._values.clear()


class _GaugeInProgress:
    """Context manager for tracking in-progress operations."""
    
    def __init__(self, gauge: Gauge, labels: Dict[str, str]):
        self._gauge = gauge
        self._labels = labels
    
    def __enter__(self):
        self._gauge.inc(**self._labels)
        return self
    
    def __exit__(self, *args):
        self._gauge.dec(**self._labels)


# =============================================================================
# Histogram
# =============================================================================

class Histogram(MetricBase):
    """
    A histogram for tracking distributions of values.
    
    Histograms are ideal for measuring latencies and request sizes.
    Values are placed into configurable buckets for efficient
    aggregation and percentile approximation.
    
    Default buckets are optimized for latency measurement in seconds.
    
    Example:
        >>> hist = Histogram(
        ...     "enforcement_duration_seconds",
        ...     buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
        ...     labels=["tier"]
        ... )
        >>> hist.observe(0.023, tier="pro")
    """
    
    # Default buckets for latency in seconds (5ms to 10s)
    DEFAULT_BUCKETS = (
        0.001, 0.0025, 0.005, 0.0075, 0.01, 0.025, 0.05, 0.075,
        0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, float("inf")
    )
    
    # Buckets optimized for ML inference (sub-millisecond to 100ms)
    ML_INFERENCE_BUCKETS = (
        0.0001, 0.0005, 0.001, 0.002, 0.003, 0.004, 0.005,
        0.0075, 0.01, 0.025, 0.05, 0.1, float("inf")
    )
    
    def __init__(
        self,
        name: str,
        description: str = "",
        unit: str = "seconds",
        labels: Optional[List[str]] = None,
        buckets: Optional[Tuple[float, ...]] = None,
    ):
        super().__init__(name, description, unit, labels)
        self._buckets = buckets or self.DEFAULT_BUCKETS
        
        # Ensure buckets are sorted and include +Inf
        bucket_list = list(self._buckets)
        if float("inf") not in bucket_list:
            bucket_list.append(float("inf"))
        self._buckets = tuple(sorted(bucket_list))
        
        # Per-label-set data: (bucket_counts, sum, count)
        self._data: Dict[LabelSet, Tuple[List[int], float, int]] = {}
    
    def _init_buckets(self) -> Tuple[List[int], float, int]:
        """Initialize bucket data structure."""
        return ([0] * len(self._buckets), 0.0, 0)
    
    def observe(self, value: float, **labels: str) -> None:
        """
        Record an observation.
        
        Args:
            value: The observed value
            **labels: Label values
        """
        if self.label_names:
            self._validate_labels(labels)
        
        label_set = LabelSet(labels) if labels else LabelSet()
        
        with self._lock:
            if label_set not in self._data:
                self._data[label_set] = self._init_buckets()
            
            bucket_counts, sum_value, count = self._data[label_set]
            
            # Update buckets
            for i, bound in enumerate(self._buckets):
                if value <= bound:
                    bucket_counts[i] += 1
            
            # Update sum and count
            self._data[label_set] = (
                bucket_counts,
                sum_value + value,
                count + 1
            )
    
    def time(self, **labels: str):
        """
        Context manager for timing operations.
        
        Example:
            >>> with hist.time(tier="pro"):
            ...     do_operation()
        """
        return _HistogramTimer(self, labels)
    
    def get_bucket_counts(self, **labels: str) -> Dict[float, int]:
        """Get bucket counts for labels."""
        label_set = LabelSet(labels) if labels else LabelSet()
        with self._lock:
            if label_set not in self._data:
                return {b: 0 for b in self._buckets}
            bucket_counts, _, _ = self._data[label_set]
            return dict(zip(self._buckets, bucket_counts))
    
    def get_sum(self, **labels: str) -> float:
        """Get sum of all observations."""
        label_set = LabelSet(labels) if labels else LabelSet()
        with self._lock:
            if label_set not in self._data:
                return 0.0
            _, sum_value, _ = self._data[label_set]
            return sum_value
    
    def get_count(self, **labels: str) -> int:
        """Get count of observations."""
        label_set = LabelSet(labels) if labels else LabelSet()
        with self._lock:
            if label_set not in self._data:
                return 0
            _, _, count = self._data[label_set]
            return count
    
    def collect(self) -> List[MetricValue]:
        """Collect histogram data as metric values."""
        now = time.time()
        values = []
        
        with self._lock:
            for label_set, (bucket_counts, sum_value, count) in self._data.items():
                # Emit bucket counts
                for bound, bucket_count in zip(self._buckets, bucket_counts):
                    bucket_labels = label_set.with_labels(le=str(bound))
                    values.append(MetricValue(
                        value=bucket_count,
                        timestamp=now,
                        labels=bucket_labels,
                    ))
                
                # Emit sum
                sum_labels = label_set.with_labels(aggregation="sum")
                values.append(MetricValue(
                    value=sum_value,
                    timestamp=now,
                    labels=sum_labels,
                ))
                
                # Emit count
                count_labels = label_set.with_labels(aggregation="count")
                values.append(MetricValue(
                    value=count,
                    timestamp=now,
                    labels=count_labels,
                ))
        
        return values
    
    def reset(self) -> None:
        """Reset histogram."""
        with self._lock:
            self._data.clear()


class _HistogramTimer:
    """Context manager for timing histogram observations."""
    
    def __init__(self, histogram: Histogram, labels: Dict[str, str]):
        self._histogram = histogram
        self._labels = labels
        self._start: float = 0
    
    def __enter__(self):
        self._start = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        duration = time.perf_counter() - self._start
        self._histogram.observe(duration, **self._labels)


# =============================================================================
# Summary
# =============================================================================

class Summary(MetricBase):
    """
    A summary metric for streaming quantile calculation.
    
    Summaries calculate quantiles (e.g., P50, P95, P99) over a
    sliding time window. Unlike histograms, quantiles are
    calculated client-side.
    
    Note: Summaries are more expensive than histograms and
    should be used when precise quantiles are required.
    
    Example:
        >>> summary = Summary(
        ...     "request_latency",
        ...     quantiles=[0.5, 0.9, 0.95, 0.99],
        ...     max_age_seconds=60
        ... )
        >>> summary.observe(0.023)
    """
    
    DEFAULT_QUANTILES = (0.5, 0.9, 0.95, 0.99)
    
    def __init__(
        self,
        name: str,
        description: str = "",
        unit: str = "seconds",
        labels: Optional[List[str]] = None,
        quantiles: Optional[Tuple[float, ...]] = None,
        max_age_seconds: float = 60.0,
        max_size: int = 1000,
    ):
        super().__init__(name, description, unit, labels)
        self._quantiles = quantiles or self.DEFAULT_QUANTILES
        self._max_age = max_age_seconds
        self._max_size = max_size
        
        # Per-label-set: deque of (timestamp, value)
        self._observations: Dict[LabelSet, deque] = {}
    
    def observe(self, value: float, **labels: str) -> None:
        """Record an observation."""
        if self.label_names:
            self._validate_labels(labels)
        
        label_set = LabelSet(labels) if labels else LabelSet()
        now = time.time()
        
        with self._lock:
            if label_set not in self._observations:
                self._observations[label_set] = deque(maxlen=self._max_size)
            
            obs = self._observations[label_set]
            obs.append((now, value))
            
            # Expire old observations
            cutoff = now - self._max_age
            while obs and obs[0][0] < cutoff:
                obs.popleft()
    
    def get_quantiles(self, **labels: str) -> Dict[float, float]:
        """Calculate quantiles for current observations."""
        label_set = LabelSet(labels) if labels else LabelSet()
        now = time.time()
        cutoff = now - self._max_age
        
        with self._lock:
            if label_set not in self._observations:
                return {q: 0.0 for q in self._quantiles}
            
            # Filter to valid observations
            values = sorted([
                v for ts, v in self._observations[label_set]
                if ts >= cutoff
            ])
            
            if not values:
                return {q: 0.0 for q in self._quantiles}
            
            result = {}
            for q in self._quantiles:
                idx = int(q * (len(values) - 1))
                result[q] = values[idx]
            
            return result
    
    def get_sum(self, **labels: str) -> float:
        """Get sum of current observations."""
        label_set = LabelSet(labels) if labels else LabelSet()
        now = time.time()
        cutoff = now - self._max_age
        
        with self._lock:
            if label_set not in self._observations:
                return 0.0
            return sum(
                v for ts, v in self._observations[label_set]
                if ts >= cutoff
            )
    
    def get_count(self, **labels: str) -> int:
        """Get count of current observations."""
        label_set = LabelSet(labels) if labels else LabelSet()
        now = time.time()
        cutoff = now - self._max_age
        
        with self._lock:
            if label_set not in self._observations:
                return 0
            return sum(
                1 for ts, _ in self._observations[label_set]
                if ts >= cutoff
            )
    
    def collect(self) -> List[MetricValue]:
        """Collect summary data as metric values."""
        now = time.time()
        values = []
        
        with self._lock:
            for label_set in self._observations:
                # Emit quantiles
                quantiles = self.get_quantiles(**label_set.to_dict())
                for q, v in quantiles.items():
                    q_labels = label_set.with_labels(quantile=str(q))
                    values.append(MetricValue(
                        value=v,
                        timestamp=now,
                        labels=q_labels,
                    ))
                
                # Emit sum
                sum_labels = label_set.with_labels(aggregation="sum")
                values.append(MetricValue(
                    value=self.get_sum(**label_set.to_dict()),
                    timestamp=now,
                    labels=sum_labels,
                ))
                
                # Emit count
                count_labels = label_set.with_labels(aggregation="count")
                values.append(MetricValue(
                    value=self.get_count(**label_set.to_dict()),
                    timestamp=now,
                    labels=count_labels,
                ))
        
        return values
    
    def reset(self) -> None:
        """Reset summary."""
        with self._lock:
            self._observations.clear()
