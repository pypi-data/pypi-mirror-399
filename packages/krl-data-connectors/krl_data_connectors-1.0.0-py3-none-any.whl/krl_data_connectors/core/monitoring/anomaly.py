"""
Anomaly Detection Module - Phase 2 Week 13

Statistical anomaly detection for usage patterns, API calls,
and license behavior with ML-based scoring.

Copyright 2025 KR-Labs. All rights reserved.
"""

from __future__ import annotations

import hashlib
import math
import statistics
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta, UTC
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


class AnomalyType(Enum):
    """Types of anomalies detected."""
    
    # Usage anomalies
    USAGE_SPIKE = "usage_spike"
    USAGE_DROP = "usage_drop"
    UNUSUAL_PATTERN = "unusual_pattern"
    
    # Authentication anomalies
    AUTH_BRUTE_FORCE = "auth_brute_force"
    AUTH_GEOGRAPHIC = "auth_geographic"
    AUTH_TIME_ANOMALY = "auth_time_anomaly"
    
    # License anomalies
    LICENSE_SHARING = "license_sharing"
    LICENSE_ABUSE = "license_abuse"
    
    # API anomalies
    API_RATE_SPIKE = "api_rate_spike"
    API_ERROR_SPIKE = "api_error_spike"
    API_UNUSUAL_ENDPOINT = "api_unusual_endpoint"
    
    # Security anomalies
    INTEGRITY_VIOLATION = "integrity_violation"
    CHALLENGE_FAILURE_SPIKE = "challenge_failure_spike"
    SESSION_ANOMALY = "session_anomaly"


class AnomalySeverity(Enum):
    """Severity levels for anomalies."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AnomalyEvent:
    """An anomaly event detected by the system."""
    
    anomaly_id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    score: float  # 0.0 to 1.0
    timestamp: float
    entity_id: str  # user_id, session_id, etc.
    entity_type: str
    description: str
    context: Dict[str, Any] = field(default_factory=dict)
    baseline: Dict[str, float] = field(default_factory=dict)
    observed: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "anomaly_id": self.anomaly_id,
            "anomaly_type": self.anomaly_type.value,
            "severity": self.severity.value,
            "score": self.score,
            "timestamp": self.timestamp,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "description": self.description,
            "context": self.context,
            "baseline": self.baseline,
            "observed": self.observed,
        }


@dataclass
class AnomalyConfig:
    """Configuration for anomaly detection."""
    
    # Sensitivity (0.0 = very sensitive, 1.0 = very lenient)
    sensitivity: float = 0.5
    
    # Z-score thresholds
    zscore_threshold_low: float = 2.0
    zscore_threshold_medium: float = 3.0
    zscore_threshold_high: float = 4.0
    zscore_threshold_critical: float = 5.0
    
    # Baseline window
    baseline_window_seconds: int = 3600 * 24  # 24 hours
    min_samples_for_baseline: int = 30
    
    # Rate limits
    max_events_per_entity: int = 100
    event_cooldown_seconds: float = 60.0
    
    # Detection toggles
    detect_usage_anomalies: bool = True
    detect_auth_anomalies: bool = True
    detect_license_anomalies: bool = True
    detect_api_anomalies: bool = True
    detect_security_anomalies: bool = True


@dataclass
class EntityBaseline:
    """Baseline statistics for an entity."""
    
    entity_id: str
    entity_type: str
    metrics: Dict[str, deque] = field(default_factory=dict)
    last_updated: float = 0.0
    
    def add_sample(self, metric: str, value: float) -> None:
        """Add a sample to the baseline."""
        if metric not in self.metrics:
            self.metrics[metric] = deque(maxlen=1000)
        self.metrics[metric].append((time.time(), value))
        self.last_updated = time.time()
    
    def get_statistics(self, metric: str) -> Dict[str, float]:
        """Get baseline statistics for a metric."""
        if metric not in self.metrics or len(self.metrics[metric]) < 2:
            return {"mean": 0.0, "stddev": 0.0, "count": 0}
        
        values = [v for _, v in self.metrics[metric]]
        
        return {
            "mean": statistics.mean(values),
            "stddev": statistics.stdev(values) if len(values) > 1 else 0.0,
            "count": len(values),
            "min": min(values),
            "max": max(values),
        }
    
    def calculate_zscore(self, metric: str, value: float) -> float:
        """Calculate Z-score for a value."""
        stats = self.get_statistics(metric)
        
        if stats["stddev"] == 0 or stats["count"] < 2:
            return 0.0
        
        return abs(value - stats["mean"]) / stats["stddev"]


class StatisticalDetector:
    """Statistical anomaly detection using Z-scores and IQR."""
    
    def __init__(self, config: AnomalyConfig):
        self.config = config
    
    def detect_zscore_anomaly(
        self,
        value: float,
        baseline: EntityBaseline,
        metric: str
    ) -> Tuple[bool, float, AnomalySeverity]:
        """Detect anomaly using Z-score method."""
        zscore = baseline.calculate_zscore(metric, value)
        
        # Adjust for sensitivity
        adjusted_zscore = zscore * (1.0 + (0.5 - self.config.sensitivity))
        
        if adjusted_zscore >= self.config.zscore_threshold_critical:
            return True, min(zscore / self.config.zscore_threshold_critical, 1.0), AnomalySeverity.CRITICAL
        elif adjusted_zscore >= self.config.zscore_threshold_high:
            return True, zscore / self.config.zscore_threshold_critical, AnomalySeverity.HIGH
        elif adjusted_zscore >= self.config.zscore_threshold_medium:
            return True, zscore / self.config.zscore_threshold_critical, AnomalySeverity.MEDIUM
        elif adjusted_zscore >= self.config.zscore_threshold_low:
            return True, zscore / self.config.zscore_threshold_critical, AnomalySeverity.LOW
        
        return False, zscore / self.config.zscore_threshold_critical, AnomalySeverity.LOW
    
    def detect_iqr_anomaly(
        self,
        value: float,
        values: List[float],
        multiplier: float = 1.5
    ) -> Tuple[bool, float]:
        """Detect anomaly using IQR method."""
        if len(values) < 4:
            return False, 0.0
        
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        
        q1 = sorted_vals[n // 4]
        q3 = sorted_vals[3 * n // 4]
        iqr = q3 - q1
        
        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr
        
        if value < lower_bound or value > upper_bound:
            # Calculate how far outside bounds
            if value < lower_bound:
                distance = (lower_bound - value) / iqr if iqr > 0 else 0
            else:
                distance = (value - upper_bound) / iqr if iqr > 0 else 0
            
            score = min(distance / 3.0, 1.0)  # Normalize to 0-1
            return True, score
        
        return False, 0.0


class PatternDetector:
    """Pattern-based anomaly detection."""
    
    def __init__(self, config: AnomalyConfig):
        self.config = config
        self._patterns: Dict[str, List[float]] = defaultdict(list)
    
    def detect_rate_anomaly(
        self,
        entity_id: str,
        events: List[float],  # List of timestamps
        window_seconds: float = 60.0
    ) -> Tuple[bool, float, str]:
        """Detect unusual rate of events."""
        if len(events) < 2:
            return False, 0.0, ""
        
        now = time.time()
        recent = [e for e in events if now - e <= window_seconds]
        
        rate = len(recent) / window_seconds
        
        # Check historical rate
        key = f"{entity_id}:rate"
        self._patterns[key].append(rate)
        
        if len(self._patterns[key]) < 10:
            return False, 0.0, ""
        
        historical_rates = self._patterns[key][-100:]
        mean_rate = statistics.mean(historical_rates)
        stddev = statistics.stdev(historical_rates) if len(historical_rates) > 1 else 0
        
        if stddev > 0:
            zscore = (rate - mean_rate) / stddev
            if zscore > 3.0:
                return True, min(zscore / 5.0, 1.0), f"Rate spike: {rate:.2f}/s vs baseline {mean_rate:.2f}/s"
        
        return False, 0.0, ""
    
    def detect_time_pattern_anomaly(
        self,
        entity_id: str,
        timestamp: float
    ) -> Tuple[bool, float, str]:
        """Detect activity outside normal time patterns."""
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        hour = dt.hour
        day_of_week = dt.weekday()
        
        # Track hour patterns
        key = f"{entity_id}:hours"
        if key not in self._patterns:
            self._patterns[key] = [0] * 24
        
        # Simple heuristic: unusual hours (late night/early morning)
        if hour >= 1 and hour <= 5:
            # Check if this is normal for the entity
            hour_count = self._patterns[key][hour]
            total_count = sum(self._patterns[key])
            
            if total_count > 20:
                hour_ratio = hour_count / total_count
                if hour_ratio < 0.05:  # Less than 5% of activity at this hour
                    return True, 0.6, f"Unusual activity time: {hour:02d}:00 UTC"
        
        # Update pattern
        self._patterns[key][hour] += 1
        
        return False, 0.0, ""


class AnomalyDetector:
    """
    Main anomaly detection engine.
    
    Combines multiple detection methods:
    - Statistical (Z-score, IQR)
    - Pattern-based (rate, time)
    - Rule-based (thresholds)
    """
    
    def __init__(self, config: AnomalyConfig | None = None):
        self.config = config or AnomalyConfig()
        self._baselines: Dict[str, EntityBaseline] = {}
        self._events: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._cooldowns: Dict[str, float] = {}
        self._callbacks: List[Callable[[AnomalyEvent], None]] = []
        self._lock = threading.RLock()
        
        # Sub-detectors
        self._statistical = StatisticalDetector(self.config)
        self._pattern = PatternDetector(self.config)
        
        # Event counter
        self._event_counter = 0
    
    def _get_baseline(self, entity_id: str, entity_type: str) -> EntityBaseline:
        """Get or create baseline for entity."""
        key = f"{entity_type}:{entity_id}"
        
        if key not in self._baselines:
            self._baselines[key] = EntityBaseline(
                entity_id=entity_id,
                entity_type=entity_type
            )
        
        return self._baselines[key]
    
    def _generate_anomaly_id(self) -> str:
        """Generate unique anomaly ID."""
        self._event_counter += 1
        data = f"{time.time()}-{self._event_counter}".encode()
        return hashlib.sha256(data).hexdigest()[:16]
    
    def _check_cooldown(self, entity_id: str, anomaly_type: AnomalyType) -> bool:
        """Check if anomaly type is in cooldown for entity."""
        key = f"{entity_id}:{anomaly_type.value}"
        
        if key in self._cooldowns:
            if time.time() - self._cooldowns[key] < self.config.event_cooldown_seconds:
                return True
        
        return False
    
    def _set_cooldown(self, entity_id: str, anomaly_type: AnomalyType) -> None:
        """Set cooldown for anomaly type."""
        key = f"{entity_id}:{anomaly_type.value}"
        self._cooldowns[key] = time.time()
    
    def record_metric(
        self,
        entity_id: str,
        entity_type: str,
        metric: str,
        value: float
    ) -> Optional[AnomalyEvent]:
        """Record a metric and check for anomalies."""
        with self._lock:
            baseline = self._get_baseline(entity_id, entity_type)
            
            # Check for anomaly before updating baseline
            event = None
            
            if baseline.get_statistics(metric)["count"] >= self.config.min_samples_for_baseline:
                is_anomaly, score, severity = self._statistical.detect_zscore_anomaly(
                    value, baseline, metric
                )
                
                if is_anomaly:
                    anomaly_type = self._classify_metric_anomaly(metric, value, baseline)
                    
                    if not self._check_cooldown(entity_id, anomaly_type):
                        event = AnomalyEvent(
                            anomaly_id=self._generate_anomaly_id(),
                            anomaly_type=anomaly_type,
                            severity=severity,
                            score=score,
                            timestamp=time.time(),
                            entity_id=entity_id,
                            entity_type=entity_type,
                            description=f"Anomalous {metric}: {value}",
                            baseline=baseline.get_statistics(metric),
                            observed={"value": value},
                        )
                        self._set_cooldown(entity_id, anomaly_type)
                        self._emit_event(event)
            
            # Update baseline
            baseline.add_sample(metric, value)
            
            return event
    
    def _classify_metric_anomaly(
        self,
        metric: str,
        value: float,
        baseline: EntityBaseline
    ) -> AnomalyType:
        """Classify the type of metric anomaly."""
        stats = baseline.get_statistics(metric)
        
        if "rate" in metric or "count" in metric:
            if value > stats["mean"]:
                return AnomalyType.USAGE_SPIKE
            else:
                return AnomalyType.USAGE_DROP
        
        if "auth" in metric:
            return AnomalyType.AUTH_BRUTE_FORCE
        
        if "error" in metric:
            return AnomalyType.API_ERROR_SPIKE
        
        if "integrity" in metric:
            return AnomalyType.INTEGRITY_VIOLATION
        
        return AnomalyType.UNUSUAL_PATTERN
    
    def record_event(
        self,
        entity_id: str,
        entity_type: str,
        event_type: str,
        context: Dict[str, Any] | None = None
    ) -> Optional[AnomalyEvent]:
        """Record an event and check for rate anomalies."""
        with self._lock:
            key = f"{entity_type}:{entity_id}:{event_type}"
            
            now = time.time()
            self._events[key].append(now)
            
            # Check for rate anomaly
            is_anomaly, score, description = self._pattern.detect_rate_anomaly(
                key,
                list(self._events[key]),
            )
            
            if is_anomaly:
                anomaly_type = self._classify_event_anomaly(event_type)
                
                if not self._check_cooldown(entity_id, anomaly_type):
                    event = AnomalyEvent(
                        anomaly_id=self._generate_anomaly_id(),
                        anomaly_type=anomaly_type,
                        severity=AnomalySeverity.MEDIUM if score < 0.7 else AnomalySeverity.HIGH,
                        score=score,
                        timestamp=now,
                        entity_id=entity_id,
                        entity_type=entity_type,
                        description=description,
                        context=context or {},
                    )
                    self._set_cooldown(entity_id, anomaly_type)
                    self._emit_event(event)
                    return event
            
            # Check time pattern
            is_time_anomaly, time_score, time_desc = self._pattern.detect_time_pattern_anomaly(
                entity_id, now
            )
            
            if is_time_anomaly:
                if not self._check_cooldown(entity_id, AnomalyType.AUTH_TIME_ANOMALY):
                    event = AnomalyEvent(
                        anomaly_id=self._generate_anomaly_id(),
                        anomaly_type=AnomalyType.AUTH_TIME_ANOMALY,
                        severity=AnomalySeverity.LOW,
                        score=time_score,
                        timestamp=now,
                        entity_id=entity_id,
                        entity_type=entity_type,
                        description=time_desc,
                        context=context or {},
                    )
                    self._set_cooldown(entity_id, AnomalyType.AUTH_TIME_ANOMALY)
                    self._emit_event(event)
                    return event
            
            return None
    
    def _classify_event_anomaly(self, event_type: str) -> AnomalyType:
        """Classify event-based anomaly."""
        event_lower = event_type.lower()
        
        if "auth" in event_lower or "login" in event_lower:
            return AnomalyType.AUTH_BRUTE_FORCE
        
        if "api" in event_lower:
            return AnomalyType.API_RATE_SPIKE
        
        if "license" in event_lower:
            return AnomalyType.LICENSE_ABUSE
        
        if "challenge" in event_lower:
            return AnomalyType.CHALLENGE_FAILURE_SPIKE
        
        return AnomalyType.UNUSUAL_PATTERN
    
    def detect_license_sharing(
        self,
        license_id: str,
        ip_addresses: List[str],
        window_seconds: float = 3600.0
    ) -> Optional[AnomalyEvent]:
        """Detect potential license sharing based on IP diversity."""
        unique_ips = set(ip_addresses)
        
        # Threshold: more than 3 unique IPs in an hour suggests sharing
        if len(unique_ips) > 3:
            score = min((len(unique_ips) - 3) / 5.0, 1.0)
            severity = (
                AnomalySeverity.CRITICAL if len(unique_ips) > 10
                else AnomalySeverity.HIGH if len(unique_ips) > 5
                else AnomalySeverity.MEDIUM
            )
            
            if not self._check_cooldown(license_id, AnomalyType.LICENSE_SHARING):
                event = AnomalyEvent(
                    anomaly_id=self._generate_anomaly_id(),
                    anomaly_type=AnomalyType.LICENSE_SHARING,
                    severity=severity,
                    score=score,
                    timestamp=time.time(),
                    entity_id=license_id,
                    entity_type="license",
                    description=f"License used from {len(unique_ips)} unique IPs in {window_seconds}s",
                    context={"unique_ips": list(unique_ips)},
                )
                self._set_cooldown(license_id, AnomalyType.LICENSE_SHARING)
                self._emit_event(event)
                return event
        
        return None
    
    def detect_geographic_anomaly(
        self,
        entity_id: str,
        current_location: Tuple[float, float],  # (lat, lon)
        previous_location: Tuple[float, float],
        time_delta_seconds: float
    ) -> Optional[AnomalyEvent]:
        """Detect impossible travel (geographic anomaly)."""
        # Calculate distance using Haversine formula
        lat1, lon1 = current_location
        lat2, lon2 = previous_location
        
        R = 6371  # Earth's radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (
            math.sin(dlat / 2) ** 2 +
            math.cos(math.radians(lat1)) *
            math.cos(math.radians(lat2)) *
            math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance_km = R * c
        
        # Calculate required speed
        hours = time_delta_seconds / 3600
        if hours > 0:
            speed_kmh = distance_km / hours
        else:
            speed_kmh = float('inf')
        
        # Flag if speed exceeds 900 km/h (faster than commercial aircraft)
        if speed_kmh > 900:
            score = min(speed_kmh / 1500, 1.0)
            
            if not self._check_cooldown(entity_id, AnomalyType.AUTH_GEOGRAPHIC):
                event = AnomalyEvent(
                    anomaly_id=self._generate_anomaly_id(),
                    anomaly_type=AnomalyType.AUTH_GEOGRAPHIC,
                    severity=AnomalySeverity.HIGH,
                    score=score,
                    timestamp=time.time(),
                    entity_id=entity_id,
                    entity_type="user",
                    description=f"Impossible travel detected: {distance_km:.0f}km in {time_delta_seconds:.0f}s",
                    context={
                        "distance_km": distance_km,
                        "time_seconds": time_delta_seconds,
                        "speed_kmh": speed_kmh,
                        "current_location": current_location,
                        "previous_location": previous_location,
                    },
                )
                self._set_cooldown(entity_id, AnomalyType.AUTH_GEOGRAPHIC)
                self._emit_event(event)
                return event
        
        return None
    
    def subscribe(self, callback: Callable[[AnomalyEvent], None]) -> None:
        """Subscribe to anomaly events."""
        with self._lock:
            self._callbacks.append(callback)
    
    def unsubscribe(self, callback: Callable[[AnomalyEvent], None]) -> None:
        """Unsubscribe from anomaly events."""
        with self._lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)
    
    def _emit_event(self, event: AnomalyEvent) -> None:
        """Emit anomaly event to all subscribers."""
        for callback in self._callbacks:
            try:
                callback(event)
            except Exception:
                pass  # Don't let callback errors affect detection
    
    def get_recent_anomalies(
        self,
        entity_id: str | None = None,
        anomaly_type: AnomalyType | None = None,
        min_severity: AnomalySeverity | None = None,
        limit: int = 100
    ) -> List[AnomalyEvent]:
        """Get recent anomalies matching criteria."""
        # This would typically query a persistent store
        # For now, return empty list as events are emitted in real-time
        return []
    
    def get_entity_risk_score(self, entity_id: str, entity_type: str) -> float:
        """Calculate overall risk score for an entity."""
        baseline = self._get_baseline(entity_id, entity_type)
        
        # Simple risk calculation based on baseline volatility
        total_stddev = 0.0
        metric_count = 0
        
        for metric, samples in baseline.metrics.items():
            stats = baseline.get_statistics(metric)
            if stats["count"] > 0 and stats["mean"] > 0:
                cv = stats["stddev"] / stats["mean"]  # Coefficient of variation
                total_stddev += cv
                metric_count += 1
        
        if metric_count == 0:
            return 0.0
        
        avg_cv = total_stddev / metric_count
        return min(avg_cv, 1.0)
    
    def reset_baseline(self, entity_id: str, entity_type: str) -> None:
        """Reset baseline for an entity."""
        key = f"{entity_type}:{entity_id}"
        with self._lock:
            if key in self._baselines:
                del self._baselines[key]
