"""
Behavioral Analysis Module - Phase 2 Week 14

User and entity behavior profiling with deviation detection.

Copyright 2025 KR-Labs. All rights reserved.
"""

import hashlib
import json
import logging
import math
import statistics
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level classifications."""
    
    MINIMAL = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


class BehaviorCategory(Enum):
    """Categories of behaviors to track."""
    
    AUTHENTICATION = "authentication"
    API_USAGE = "api_usage"
    DATA_ACCESS = "data_access"
    LICENSE_USAGE = "license_usage"
    SESSION = "session"
    NETWORK = "network"
    TEMPORAL = "temporal"
    GEOGRAPHIC = "geographic"


@dataclass
class BehaviorEvent:
    """A single behavior event."""
    
    id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    timestamp: datetime = field(default_factory=datetime.now)
    entity_id: str = ""
    entity_type: str = ""  # user, license, session, ip
    category: BehaviorCategory = BehaviorCategory.API_USAGE
    action: str = ""
    resource: str = ""
    value: float = 1.0  # Quantifiable metric
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "category": self.category.value,
            "action": self.action,
            "resource": self.resource,
            "value": self.value,
            "metadata": self.metadata,
            "source_ip": self.source_ip,
            "session_id": self.session_id,
        }


@dataclass
class BehaviorMetric:
    """A metric derived from behavior events."""
    
    name: str
    category: BehaviorCategory
    aggregation: str  # count, sum, avg, max, min, rate
    window_seconds: int = 3600  # 1 hour default
    values: List[Tuple[datetime, float]] = field(default_factory=list)
    
    def add_value(self, value: float, timestamp: Optional[datetime] = None) -> None:
        """Add a value to the metric."""
        ts = timestamp or datetime.now()
        self.values.append((ts, value))
        
        # Prune old values
        cutoff = datetime.now() - timedelta(seconds=self.window_seconds * 2)
        self.values = [(t, v) for t, v in self.values if t > cutoff]
    
    def get_value(self, window_seconds: Optional[int] = None) -> Optional[float]:
        """Get aggregated value for the window."""
        window = window_seconds or self.window_seconds
        cutoff = datetime.now() - timedelta(seconds=window)
        
        window_values = [v for t, v in self.values if t > cutoff]
        
        if not window_values:
            return None
        
        if self.aggregation == "count":
            return float(len(window_values))
        elif self.aggregation == "sum":
            return sum(window_values)
        elif self.aggregation == "avg":
            return statistics.mean(window_values)
        elif self.aggregation == "max":
            return max(window_values)
        elif self.aggregation == "min":
            return min(window_values)
        elif self.aggregation == "rate":
            return len(window_values) / (window / 60.0)  # per minute
        
        return None


@dataclass
class BehaviorBaseline:
    """Baseline profile for an entity's behavior."""
    
    entity_id: str = ""
    entity_type: str = ""
    metrics: Dict[str, Dict[str, float]] = field(default_factory=dict)
    # metric_name -> {mean, std, min, max, count}
    patterns: Dict[str, Any] = field(default_factory=dict)
    # hour_distribution, day_distribution, etc.
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    sample_count: int = 0
    
    def update_metric(self, name: str, value: float) -> None:
        """Update a metric in the baseline using online algorithm."""
        if name not in self.metrics:
            self.metrics[name] = {
                "mean": value,
                "variance": 0.0,
                "min": value,
                "max": value,
                "count": 1,
            }
        else:
            m = self.metrics[name]
            n = m["count"] + 1
            
            # Welford's online algorithm for variance
            delta = value - m["mean"]
            m["mean"] += delta / n
            m["variance"] += delta * (value - m["mean"])
            
            m["min"] = min(m["min"], value)
            m["max"] = max(m["max"], value)
            m["count"] = n
        
        self.sample_count += 1
        self.updated_at = datetime.now()
    
    def get_std(self, metric_name: str) -> float:
        """Get standard deviation for a metric."""
        if metric_name not in self.metrics:
            return 0.0
        
        m = self.metrics[metric_name]
        if m["count"] < 2:
            return 0.0
        
        return math.sqrt(m["variance"] / (m["count"] - 1))
    
    def update_pattern(self, pattern_name: str, key: str, value: float = 1.0) -> None:
        """Update a pattern distribution."""
        if pattern_name not in self.patterns:
            self.patterns[pattern_name] = {}
        
        if key not in self.patterns[pattern_name]:
            self.patterns[pattern_name][key] = 0.0
        
        self.patterns[pattern_name][key] += value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "metrics": self.metrics,
            "patterns": self.patterns,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "sample_count": self.sample_count,
        }


@dataclass
class DeviationScore:
    """Score indicating deviation from baseline behavior."""
    
    entity_id: str = ""
    entity_type: str = ""
    score: float = 0.0  # 0-100, higher = more anomalous
    risk_level: RiskLevel = RiskLevel.MINIMAL
    deviations: List[Dict[str, Any]] = field(default_factory=list)
    contributing_factors: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    confidence: float = 0.0
    
    @classmethod
    def calculate_risk_level(cls, score: float) -> RiskLevel:
        """Calculate risk level from score."""
        if score >= 80:
            return RiskLevel.CRITICAL
        elif score >= 60:
            return RiskLevel.HIGH
        elif score >= 40:
            return RiskLevel.MEDIUM
        elif score >= 20:
            return RiskLevel.LOW
        return RiskLevel.MINIMAL
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "score": self.score,
            "risk_level": self.risk_level.value,
            "deviations": self.deviations,
            "contributing_factors": self.contributing_factors,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence,
        }


@dataclass
class UserProfile:
    """Behavior profile for a user entity."""
    
    user_id: str = ""
    baseline: BehaviorBaseline = field(default_factory=BehaviorBaseline)
    recent_events: List[BehaviorEvent] = field(default_factory=list)
    active_sessions: Set[str] = field(default_factory=set)
    typical_hours: List[int] = field(default_factory=list)  # 0-23
    typical_days: List[int] = field(default_factory=list)  # 0-6 (Mon-Sun)
    known_ips: Set[str] = field(default_factory=set)
    known_locations: Set[str] = field(default_factory=set)
    known_devices: Set[str] = field(default_factory=set)
    risk_score_history: List[Tuple[datetime, float]] = field(default_factory=list)
    last_activity: Optional[datetime] = None
    
    def add_event(self, event: BehaviorEvent) -> None:
        """Add an event to the profile."""
        self.recent_events.append(event)
        self.last_activity = event.timestamp
        
        # Prune old events (keep last 24 hours)
        cutoff = datetime.now() - timedelta(hours=24)
        self.recent_events = [e for e in self.recent_events if e.timestamp > cutoff]
        
        # Update known attributes
        if event.source_ip:
            self.known_ips.add(event.source_ip)
        if event.session_id:
            self.active_sessions.add(event.session_id)
        
        # Update temporal patterns
        hour = event.timestamp.hour
        if hour not in self.typical_hours and len(self.typical_hours) < 24:
            self.typical_hours.append(hour)
        
        day = event.timestamp.weekday()
        if day not in self.typical_days and len(self.typical_days) < 7:
            self.typical_days.append(day)
    
    def get_event_rate(self, category: Optional[BehaviorCategory] = None) -> float:
        """Get events per minute in recent window."""
        window_minutes = 60
        cutoff = datetime.now() - timedelta(minutes=window_minutes)
        
        events = [e for e in self.recent_events if e.timestamp > cutoff]
        if category:
            events = [e for e in events if e.category == category]
        
        return len(events) / window_minutes


@dataclass
class EntityProfile:
    """Generic entity behavior profile."""
    
    entity_id: str = ""
    entity_type: str = ""
    baseline: BehaviorBaseline = field(default_factory=BehaviorBaseline)
    metrics: Dict[str, BehaviorMetric] = field(default_factory=dict)
    recent_events: List[BehaviorEvent] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    event_count: int = 0
    
    def add_event(self, event: BehaviorEvent) -> None:
        """Add an event to the profile."""
        self.recent_events.append(event)
        self.last_seen = event.timestamp
        self.event_count += 1
        
        # Prune old events
        cutoff = datetime.now() - timedelta(hours=6)
        self.recent_events = [e for e in self.recent_events if e.timestamp > cutoff]


@dataclass
class BehaviorConfig:
    """Configuration for behavior analyzer."""
    
    enabled: bool = True
    baseline_min_samples: int = 100
    deviation_threshold: float = 2.5  # Standard deviations
    high_risk_threshold: float = 60.0
    event_retention_hours: int = 24
    baseline_update_interval: int = 300  # seconds
    enable_realtime_analysis: bool = True
    analysis_window_seconds: int = 3600
    
    # Weights for different behavior categories
    category_weights: Dict[str, float] = field(default_factory=lambda: {
        "authentication": 1.5,
        "api_usage": 1.0,
        "data_access": 1.2,
        "license_usage": 1.3,
        "session": 0.8,
        "network": 1.0,
        "temporal": 0.9,
        "geographic": 1.1,
    })


class BehaviorAnalyzer:
    """
    Behavioral Analysis Engine.
    
    Profiles user and entity behavior, detects deviations,
    and calculates risk scores.
    """
    
    def __init__(self, config: Optional[BehaviorConfig] = None):
        self.config = config or BehaviorConfig()
        self.user_profiles: Dict[str, UserProfile] = {}
        self.entity_profiles: Dict[str, EntityProfile] = {}
        self.deviation_history: List[DeviationScore] = []
        self._subscribers: List[Callable[[DeviationScore], None]] = []
        self._lock = threading.Lock()
    
    def record_event(self, event: BehaviorEvent) -> Optional[DeviationScore]:
        """Record a behavior event and optionally analyze it."""
        # Get or create profile
        if event.entity_type == "user":
            profile = self._get_or_create_user_profile(event.entity_id)
            profile.add_event(event)
            profile.baseline.entity_id = event.entity_id
            profile.baseline.entity_type = "user"
        else:
            profile = self._get_or_create_entity_profile(
                event.entity_id,
                event.entity_type,
            )
            profile.add_event(event)
        
        # Update baseline
        self._update_baseline(profile.baseline, event)
        
        # Real-time analysis if enabled
        if self.config.enable_realtime_analysis:
            return self.analyze_entity(event.entity_id, event.entity_type)
        
        return None
    
    def analyze_entity(
        self,
        entity_id: str,
        entity_type: str,
    ) -> DeviationScore:
        """Analyze an entity's recent behavior against baseline."""
        if entity_type == "user":
            profile = self.user_profiles.get(entity_id)
            if not profile:
                return DeviationScore(
                    entity_id=entity_id,
                    entity_type=entity_type,
                    score=0.0,
                    risk_level=RiskLevel.MINIMAL,
                    confidence=0.0,
                )
            baseline = profile.baseline
            recent_events = profile.recent_events
        else:
            key = f"{entity_type}:{entity_id}"
            profile = self.entity_profiles.get(key)
            if not profile:
                return DeviationScore(
                    entity_id=entity_id,
                    entity_type=entity_type,
                    score=0.0,
                    risk_level=RiskLevel.MINIMAL,
                    confidence=0.0,
                )
            baseline = profile.baseline
            recent_events = profile.recent_events
        
        # Calculate deviation score
        deviation = DeviationScore(
            entity_id=entity_id,
            entity_type=entity_type,
        )
        
        if baseline.sample_count < self.config.baseline_min_samples:
            deviation.confidence = baseline.sample_count / self.config.baseline_min_samples
            deviation.score = 0.0
            deviation.risk_level = RiskLevel.MINIMAL
            return deviation
        
        # Analyze different aspects
        factors: Dict[str, float] = {}
        deviations_list: List[Dict[str, Any]] = []
        
        # 1. Activity rate deviation
        rate_score = self._analyze_activity_rate(recent_events, baseline)
        if rate_score > 0:
            factors["activity_rate"] = rate_score
            if rate_score > 30:
                deviations_list.append({
                    "type": "activity_rate",
                    "description": "Unusual activity rate",
                    "severity": rate_score,
                })
        
        # 2. Temporal deviation
        temporal_score = self._analyze_temporal_patterns(recent_events, baseline)
        if temporal_score > 0:
            factors["temporal_pattern"] = temporal_score
            if temporal_score > 30:
                deviations_list.append({
                    "type": "temporal_pattern",
                    "description": "Activity at unusual times",
                    "severity": temporal_score,
                })
        
        # 3. Resource access deviation
        resource_score = self._analyze_resource_access(recent_events, baseline)
        if resource_score > 0:
            factors["resource_access"] = resource_score
            if resource_score > 30:
                deviations_list.append({
                    "type": "resource_access",
                    "description": "Unusual resource access pattern",
                    "severity": resource_score,
                })
        
        # 4. User-specific analysis
        if entity_type == "user" and isinstance(profile, UserProfile):
            # IP analysis
            ip_score = self._analyze_ip_patterns(profile)
            if ip_score > 0:
                factors["ip_pattern"] = ip_score
                if ip_score > 30:
                    deviations_list.append({
                        "type": "ip_pattern",
                        "description": "Connection from unusual IP",
                        "severity": ip_score,
                    })
        
        # Calculate weighted score
        total_weight = 0.0
        weighted_sum = 0.0
        
        for factor, score in factors.items():
            category = self._factor_to_category(factor)
            weight = self.config.category_weights.get(category, 1.0)
            weighted_sum += score * weight
            total_weight += weight
        
        if total_weight > 0:
            deviation.score = weighted_sum / total_weight
        
        deviation.score = min(100, max(0, deviation.score))
        deviation.risk_level = DeviationScore.calculate_risk_level(deviation.score)
        deviation.contributing_factors = factors
        deviation.deviations = deviations_list
        deviation.confidence = min(1.0, baseline.sample_count / (self.config.baseline_min_samples * 2))
        
        # Store in history
        self.deviation_history.append(deviation)
        
        # Notify subscribers if high risk
        if deviation.risk_level.value >= RiskLevel.HIGH.value:
            for subscriber in self._subscribers:
                try:
                    subscriber(deviation)
                except Exception as e:
                    logger.error(f"Error notifying subscriber: {e}")
        
        return deviation
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get a user's behavior profile."""
        return self.user_profiles.get(user_id)
    
    def get_entity_profile(
        self,
        entity_id: str,
        entity_type: str,
    ) -> Optional[EntityProfile]:
        """Get an entity's behavior profile."""
        key = f"{entity_type}:{entity_id}"
        return self.entity_profiles.get(key)
    
    def get_risk_score(
        self,
        entity_id: str,
        entity_type: str,
    ) -> float:
        """Get current risk score for an entity."""
        deviation = self.analyze_entity(entity_id, entity_type)
        return deviation.score
    
    def get_high_risk_entities(
        self,
        threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Get entities with high risk scores."""
        threshold = threshold or self.config.high_risk_threshold
        high_risk = []
        
        # Check user profiles
        for user_id, profile in self.user_profiles.items():
            deviation = self.analyze_entity(user_id, "user")
            if deviation.score >= threshold:
                high_risk.append({
                    "entity_id": user_id,
                    "entity_type": "user",
                    "score": deviation.score,
                    "risk_level": deviation.risk_level.value,
                })
        
        # Check entity profiles
        for key, profile in self.entity_profiles.items():
            deviation = self.analyze_entity(profile.entity_id, profile.entity_type)
            if deviation.score >= threshold:
                high_risk.append({
                    "entity_id": profile.entity_id,
                    "entity_type": profile.entity_type,
                    "score": deviation.score,
                    "risk_level": deviation.risk_level.value,
                })
        
        high_risk.sort(key=lambda x: x["score"], reverse=True)
        return high_risk
    
    def subscribe(self, callback: Callable[[DeviationScore], None]) -> None:
        """Subscribe to high-risk deviation notifications."""
        self._subscribers.append(callback)
    
    def reset_baseline(
        self,
        entity_id: str,
        entity_type: str,
    ) -> bool:
        """Reset the baseline for an entity."""
        if entity_type == "user":
            if entity_id in self.user_profiles:
                self.user_profiles[entity_id].baseline = BehaviorBaseline(
                    entity_id=entity_id,
                    entity_type="user",
                )
                return True
        else:
            key = f"{entity_type}:{entity_id}"
            if key in self.entity_profiles:
                self.entity_profiles[key].baseline = BehaviorBaseline(
                    entity_id=entity_id,
                    entity_type=entity_type,
                )
                return True
        
        return False
    
    def export_profile(
        self,
        entity_id: str,
        entity_type: str,
    ) -> Optional[Dict[str, Any]]:
        """Export a profile for backup or analysis."""
        if entity_type == "user":
            profile = self.user_profiles.get(entity_id)
            if profile:
                return {
                    "user_id": profile.user_id,
                    "baseline": profile.baseline.to_dict(),
                    "typical_hours": profile.typical_hours,
                    "typical_days": profile.typical_days,
                    "known_ips": list(profile.known_ips),
                    "event_count": len(profile.recent_events),
                }
        else:
            key = f"{entity_type}:{entity_id}"
            profile = self.entity_profiles.get(key)
            if profile:
                return {
                    "entity_id": profile.entity_id,
                    "entity_type": profile.entity_type,
                    "baseline": profile.baseline.to_dict(),
                    "event_count": profile.event_count,
                    "first_seen": profile.first_seen.isoformat(),
                    "last_seen": profile.last_seen.isoformat(),
                }
        
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get behavior analysis statistics."""
        return {
            "user_profiles": len(self.user_profiles),
            "entity_profiles": len(self.entity_profiles),
            "total_deviations_recorded": len(self.deviation_history),
            "high_risk_users": len([
                p for p in self.user_profiles.values()
                if self.analyze_entity(p.user_id, "user").score >= self.config.high_risk_threshold
            ]),
            "config": {
                "baseline_min_samples": self.config.baseline_min_samples,
                "deviation_threshold": self.config.deviation_threshold,
                "high_risk_threshold": self.config.high_risk_threshold,
            },
        }
    
    def _get_or_create_user_profile(self, user_id: str) -> UserProfile:
        """Get or create a user profile."""
        with self._lock:
            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = UserProfile(user_id=user_id)
            return self.user_profiles[user_id]
    
    def _get_or_create_entity_profile(
        self,
        entity_id: str,
        entity_type: str,
    ) -> EntityProfile:
        """Get or create an entity profile."""
        key = f"{entity_type}:{entity_id}"
        
        with self._lock:
            if key not in self.entity_profiles:
                self.entity_profiles[key] = EntityProfile(
                    entity_id=entity_id,
                    entity_type=entity_type,
                )
            return self.entity_profiles[key]
    
    def _update_baseline(
        self,
        baseline: BehaviorBaseline,
        event: BehaviorEvent,
    ) -> None:
        """Update baseline with new event."""
        # Update category-specific metrics
        metric_name = f"{event.category.value}_count"
        baseline.update_metric(metric_name, 1.0)
        
        if event.value:
            value_metric = f"{event.category.value}_value"
            baseline.update_metric(value_metric, event.value)
        
        # Update temporal patterns
        hour = event.timestamp.hour
        baseline.update_pattern("hour_distribution", str(hour))
        
        day = event.timestamp.weekday()
        baseline.update_pattern("day_distribution", str(day))
    
    def _analyze_activity_rate(
        self,
        events: List[BehaviorEvent],
        baseline: BehaviorBaseline,
    ) -> float:
        """Analyze activity rate deviation."""
        if not events:
            return 0.0
        
        # Calculate current rate (events per hour)
        window_hours = 1
        cutoff = datetime.now() - timedelta(hours=window_hours)
        recent = [e for e in events if e.timestamp > cutoff]
        current_rate = len(recent) / window_hours
        
        # Get baseline rate
        for category in BehaviorCategory:
            metric_name = f"{category.value}_count"
            if metric_name in baseline.metrics:
                baseline_rate = baseline.metrics[metric_name].get("mean", 0)
                baseline_std = baseline.get_std(metric_name)
                
                if baseline_std > 0:
                    z_score = abs(current_rate - baseline_rate) / baseline_std
                    if z_score > self.config.deviation_threshold:
                        return min(100, z_score * 20)
        
        return 0.0
    
    def _analyze_temporal_patterns(
        self,
        events: List[BehaviorEvent],
        baseline: BehaviorBaseline,
    ) -> float:
        """Analyze temporal pattern deviation."""
        if not events or "hour_distribution" not in baseline.patterns:
            return 0.0
        
        hour_dist = baseline.patterns["hour_distribution"]
        total_events = sum(hour_dist.values())
        
        if total_events < 10:
            return 0.0
        
        unusual_count = 0
        for event in events[-10:]:  # Check last 10 events
            hour = str(event.timestamp.hour)
            hour_freq = hour_dist.get(hour, 0) / total_events
            
            if hour_freq < 0.01:  # Less than 1% of events
                unusual_count += 1
        
        return min(100, unusual_count * 10)
    
    def _analyze_resource_access(
        self,
        events: List[BehaviorEvent],
        baseline: BehaviorBaseline,
    ) -> float:
        """Analyze resource access pattern deviation."""
        if not events:
            return 0.0
        
        # Track resources accessed
        resources = set(e.resource for e in events if e.resource)
        
        # Check for unusual resource types
        unusual_count = 0
        resource_pattern = baseline.patterns.get("resource_distribution", {})
        total_resources = sum(resource_pattern.values()) if resource_pattern else 0
        
        if total_resources > 10:
            for resource in resources:
                if resource_pattern.get(resource, 0) / total_resources < 0.005:
                    unusual_count += 1
        
        return min(100, unusual_count * 15)
    
    def _analyze_ip_patterns(self, profile: UserProfile) -> float:
        """Analyze IP access patterns for users."""
        if not profile.recent_events:
            return 0.0
        
        recent_ips = set()
        for event in profile.recent_events[-20:]:
            if event.source_ip:
                recent_ips.add(event.source_ip)
        
        new_ips = recent_ips - profile.known_ips
        
        if len(profile.known_ips) < 3:
            return 0.0  # Not enough history
        
        new_ip_ratio = len(new_ips) / max(1, len(recent_ips))
        
        if new_ip_ratio > 0.5:
            return min(100, new_ip_ratio * 80)
        
        return 0.0
    
    def _factor_to_category(self, factor: str) -> str:
        """Map factor name to behavior category."""
        mapping = {
            "activity_rate": "api_usage",
            "temporal_pattern": "temporal",
            "resource_access": "data_access",
            "ip_pattern": "network",
        }
        return mapping.get(factor, "api_usage")
