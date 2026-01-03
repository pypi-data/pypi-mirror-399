"""
Risk Scoring with Machine Learning for KRL Defense System.

Week 15: ML-enhanced risk assessment and scoring.
Provides multi-factor risk scoring with ML models.
"""

import hashlib
import logging
import math
import statistics
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from collections import deque
import json

logger = logging.getLogger(__name__)


class RiskCategory(Enum):
    """Categories of risk factors."""
    LICENSE = "license"
    BEHAVIORAL = "behavioral"
    ENVIRONMENTAL = "environmental"
    TEMPORAL = "temporal"
    VOLUMETRIC = "volumetric"
    IDENTITY = "identity"
    NETWORK = "network"
    CONTEXTUAL = "contextual"


class RiskLevel(Enum):
    """Risk severity levels."""
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    @classmethod
    def from_score(cls, score: float) -> 'RiskLevel':
        """Get risk level from numeric score."""
        if score >= 0.9:
            return cls.CRITICAL
        elif score >= 0.7:
            return cls.HIGH
        elif score >= 0.5:
            return cls.MEDIUM
        elif score >= 0.3:
            return cls.LOW
        else:
            return cls.MINIMAL


class RiskTrend(Enum):
    """Risk trend direction."""
    DECREASING = "decreasing"
    STABLE = "stable"
    INCREASING = "increasing"
    SPIKING = "spiking"


@dataclass
class RiskFactor:
    """Individual risk factor."""
    factor_id: str
    category: RiskCategory
    name: str
    description: str
    weight: float  # 0-1, contribution to overall risk
    score: float  # 0-1, current risk score
    confidence: float  # 0-1, confidence in the score
    evidence: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def weighted_score(self) -> float:
        """Get weighted risk score."""
        return self.weight * self.score * self.confidence


@dataclass
class RiskProfile:
    """Risk profile for an entity."""
    entity_id: str
    entity_type: str  # user, license, system
    overall_score: float
    overall_level: RiskLevel
    trend: RiskTrend
    factors: List[RiskFactor]
    last_updated: datetime
    history: List[Tuple[datetime, float]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "overall_score": self.overall_score,
            "overall_level": self.overall_level.value,
            "trend": self.trend.value,
            "factors": [
                {
                    "factor_id": f.factor_id,
                    "category": f.category.value,
                    "name": f.name,
                    "score": f.score,
                    "weight": f.weight,
                    "confidence": f.confidence
                }
                for f in self.factors
            ],
            "last_updated": self.last_updated.isoformat(),
            "history": [(t.isoformat(), s) for t, s in self.history[-10:]]
        }


@dataclass
class RiskEvent:
    """Event that affects risk."""
    event_id: str
    timestamp: datetime
    entity_id: str
    event_type: str
    risk_impact: float  # -1 to 1, negative reduces risk
    category: RiskCategory
    properties: Dict[str, Any] = field(default_factory=dict)


class RiskScorer(ABC):
    """Base class for risk scoring components."""
    
    def __init__(self, category: RiskCategory, weight: float = 1.0):
        self.category = category
        self.weight = weight
    
    @abstractmethod
    def score(self, events: List[RiskEvent], context: Dict[str, Any]) -> RiskFactor:
        """Calculate risk factor from events."""
        pass
    
    @abstractmethod
    def update(self, event: RiskEvent) -> Optional[float]:
        """Update scorer with new event, return impact."""
        pass


class LicenseRiskScorer(RiskScorer):
    """Score license-related risks."""
    
    def __init__(self, weight: float = 0.3):
        super().__init__(RiskCategory.LICENSE, weight)
        self.violation_counts: Dict[str, int] = {}
        self.last_validation: Dict[str, datetime] = {}
        self.baseline_features: int = 0
    
    def score(self, events: List[RiskEvent], context: Dict[str, Any]) -> RiskFactor:
        """Calculate license risk."""
        entity_id = context.get("entity_id", "unknown")
        
        # Collect license-related events
        license_events = [e for e in events if e.category == RiskCategory.LICENSE]
        
        if not license_events:
            return RiskFactor(
                factor_id=f"license_{entity_id}",
                category=self.category,
                name="License Risk",
                description="No license events",
                weight=self.weight,
                score=0.1,  # Base risk
                confidence=0.5,
                evidence=["No recent license activity"]
            )
        
        # Calculate violations
        violations = [e for e in license_events if e.risk_impact > 0]
        validation_failures = len([e for e in violations if "validation" in e.event_type.lower()])
        tampering_attempts = len([e for e in violations if "tamper" in e.event_type.lower()])
        expiry_warnings = len([e for e in violations if "expir" in e.event_type.lower()])
        
        # Base score from violations
        base_score = min(1.0, (
            validation_failures * 0.3 +
            tampering_attempts * 0.5 +
            expiry_warnings * 0.2
        ))
        
        # Time decay - recent events matter more
        now = datetime.now()
        recency_factor = 0.0
        for event in violations:
            age_hours = (now - event.timestamp).total_seconds() / 3600
            recency_factor += math.exp(-age_hours / 24)  # Decay over 24 hours
        
        recency_score = min(1.0, recency_factor / max(1, len(violations)))
        
        final_score = (base_score * 0.6 + recency_score * 0.4)
        
        evidence = []
        if validation_failures:
            evidence.append(f"{validation_failures} validation failure(s)")
        if tampering_attempts:
            evidence.append(f"{tampering_attempts} tampering attempt(s)")
        if expiry_warnings:
            evidence.append(f"{expiry_warnings} expiry warning(s)")
        
        return RiskFactor(
            factor_id=f"license_{entity_id}",
            category=self.category,
            name="License Risk",
            description="Risk from license validation and compliance",
            weight=self.weight,
            score=final_score,
            confidence=min(0.95, 0.5 + len(license_events) * 0.05),
            evidence=evidence or ["Normal license activity"],
            metadata={
                "validation_failures": validation_failures,
                "tampering_attempts": tampering_attempts,
                "total_events": len(license_events)
            }
        )
    
    def update(self, event: RiskEvent) -> Optional[float]:
        """Update with new license event."""
        if event.category != RiskCategory.LICENSE:
            return None
        
        self.violation_counts[event.entity_id] = \
            self.violation_counts.get(event.entity_id, 0) + (1 if event.risk_impact > 0 else 0)
        self.last_validation[event.entity_id] = event.timestamp
        
        return event.risk_impact


class BehavioralRiskScorer(RiskScorer):
    """Score behavioral risks using statistical analysis."""
    
    def __init__(self, weight: float = 0.25):
        super().__init__(RiskCategory.BEHAVIORAL, weight)
        self.baseline_metrics: Dict[str, Dict[str, float]] = {}
        self.recent_metrics: Dict[str, deque] = {}
        self.window_size = 100
    
    def _calculate_deviation(self, entity_id: str, metric: str, value: float) -> float:
        """Calculate deviation from baseline."""
        if entity_id not in self.baseline_metrics or metric not in self.baseline_metrics[entity_id]:
            return 0.0
        
        baseline = self.baseline_metrics[entity_id]
        mean = baseline.get(f"{metric}_mean", value)
        std = baseline.get(f"{metric}_std", 1.0)
        
        if std == 0:
            return 0.0
        
        z_score = abs(value - mean) / std
        return min(1.0, z_score / 3)  # Cap at 3 standard deviations
    
    def score(self, events: List[RiskEvent], context: Dict[str, Any]) -> RiskFactor:
        """Calculate behavioral risk."""
        entity_id = context.get("entity_id", "unknown")
        
        behavioral_events = [e for e in events if e.category == RiskCategory.BEHAVIORAL]
        
        if not behavioral_events:
            return RiskFactor(
                factor_id=f"behavioral_{entity_id}",
                category=self.category,
                name="Behavioral Risk",
                description="No behavioral events",
                weight=self.weight,
                score=0.0,
                confidence=0.3,
                evidence=["No behavioral data"]
            )
        
        # Extract metrics from events
        deviations = []
        anomaly_count = 0
        
        for event in behavioral_events:
            for metric, value in event.properties.items():
                if isinstance(value, (int, float)):
                    dev = self._calculate_deviation(entity_id, metric, value)
                    deviations.append(dev)
                    if dev > 0.7:
                        anomaly_count += 1
        
        if not deviations:
            avg_deviation = 0.0
        else:
            avg_deviation = statistics.mean(deviations)
        
        # Risk from anomalies
        anomaly_risk = min(1.0, anomaly_count / max(1, len(behavioral_events)))
        
        final_score = (avg_deviation * 0.5 + anomaly_risk * 0.5)
        
        evidence = []
        if anomaly_count > 0:
            evidence.append(f"{anomaly_count} behavioral anomalies detected")
        if avg_deviation > 0.5:
            evidence.append(f"High deviation from baseline: {avg_deviation:.2f}")
        
        return RiskFactor(
            factor_id=f"behavioral_{entity_id}",
            category=self.category,
            name="Behavioral Risk",
            description="Risk from behavioral deviation",
            weight=self.weight,
            score=final_score,
            confidence=min(0.9, 0.3 + len(behavioral_events) * 0.05),
            evidence=evidence or ["Normal behavior"],
            metadata={
                "avg_deviation": avg_deviation,
                "anomaly_count": anomaly_count,
                "events_analyzed": len(behavioral_events)
            }
        )
    
    def update(self, event: RiskEvent) -> Optional[float]:
        """Update behavioral baseline."""
        if event.category != RiskCategory.BEHAVIORAL:
            return None
        
        entity_id = event.entity_id
        
        if entity_id not in self.recent_metrics:
            self.recent_metrics[entity_id] = deque(maxlen=self.window_size)
        
        self.recent_metrics[entity_id].append(event.properties)
        
        # Periodically update baseline
        if len(self.recent_metrics[entity_id]) >= self.window_size:
            self._update_baseline(entity_id)
        
        return event.risk_impact
    
    def _update_baseline(self, entity_id: str) -> None:
        """Recalculate baseline from recent metrics."""
        metrics = list(self.recent_metrics[entity_id])
        
        if not metrics:
            return
        
        # Aggregate by metric name
        aggregated: Dict[str, List[float]] = {}
        for m in metrics:
            for key, value in m.items():
                if isinstance(value, (int, float)):
                    if key not in aggregated:
                        aggregated[key] = []
                    aggregated[key].append(value)
        
        baseline: Dict[str, float] = {}
        for key, values in aggregated.items():
            if values:
                baseline[f"{key}_mean"] = statistics.mean(values)
                baseline[f"{key}_std"] = statistics.stdev(values) if len(values) > 1 else 1.0
        
        self.baseline_metrics[entity_id] = baseline


class EnvironmentalRiskScorer(RiskScorer):
    """Score environment-related risks."""
    
    def __init__(self, weight: float = 0.15):
        super().__init__(RiskCategory.ENVIRONMENTAL, weight)
        self.known_environments: Dict[str, Set[str]] = {}
        self.suspicious_indicators: List[str] = [
            "vm_detected", "debugger_attached", "sandbox",
            "unusual_timezone", "vpn_detected", "emulator"
        ]
    
    def score(self, events: List[RiskEvent], context: Dict[str, Any]) -> RiskFactor:
        """Calculate environmental risk."""
        entity_id = context.get("entity_id", "unknown")
        
        env_events = [e for e in events if e.category == RiskCategory.ENVIRONMENTAL]
        
        if not env_events:
            return RiskFactor(
                factor_id=f"environmental_{entity_id}",
                category=self.category,
                name="Environmental Risk",
                description="No environmental data",
                weight=self.weight,
                score=0.2,  # Slight risk from unknown environment
                confidence=0.3,
                evidence=["Environment not verified"]
            )
        
        suspicious_count = 0
        new_environment = False
        evidence = []
        
        for event in env_events:
            # Check for suspicious indicators
            for indicator in self.suspicious_indicators:
                if event.properties.get(indicator):
                    suspicious_count += 1
                    evidence.append(f"Detected: {indicator}")
            
            # Check for new/unknown environment
            env_hash = event.properties.get("environment_hash")
            if env_hash:
                if entity_id not in self.known_environments:
                    self.known_environments[entity_id] = set()
                
                if env_hash not in self.known_environments[entity_id]:
                    new_environment = True
                    evidence.append("New environment detected")
        
        # Calculate score
        suspicious_score = min(1.0, suspicious_count * 0.25)
        new_env_score = 0.3 if new_environment else 0.0
        
        final_score = min(1.0, suspicious_score + new_env_score)
        
        return RiskFactor(
            factor_id=f"environmental_{entity_id}",
            category=self.category,
            name="Environmental Risk",
            description="Risk from execution environment",
            weight=self.weight,
            score=final_score,
            confidence=min(0.9, 0.4 + len(env_events) * 0.1),
            evidence=evidence or ["Normal environment"],
            metadata={
                "suspicious_indicators": suspicious_count,
                "new_environment": new_environment
            }
        )
    
    def update(self, event: RiskEvent) -> Optional[float]:
        """Update known environments."""
        if event.category != RiskCategory.ENVIRONMENTAL:
            return None
        
        env_hash = event.properties.get("environment_hash")
        if env_hash and event.entity_id:
            if event.entity_id not in self.known_environments:
                self.known_environments[event.entity_id] = set()
            self.known_environments[event.entity_id].add(env_hash)
        
        return event.risk_impact


class TemporalRiskScorer(RiskScorer):
    """Score time-based risks."""
    
    def __init__(self, weight: float = 0.1):
        super().__init__(RiskCategory.TEMPORAL, weight)
        self.normal_hours: Set[int] = set(range(6, 22))  # 6 AM to 10 PM
        self.normal_days: Set[int] = set(range(0, 5))  # Monday to Friday
        self.access_patterns: Dict[str, Dict[int, int]] = {}
    
    def score(self, events: List[RiskEvent], context: Dict[str, Any]) -> RiskFactor:
        """Calculate temporal risk."""
        entity_id = context.get("entity_id", "unknown")
        
        if not events:
            return RiskFactor(
                factor_id=f"temporal_{entity_id}",
                category=self.category,
                name="Temporal Risk",
                description="No temporal data",
                weight=self.weight,
                score=0.0,
                confidence=0.3,
                evidence=["No activity data"]
            )
        
        off_hours_count = 0
        weekend_count = 0
        unusual_pattern_count = 0
        evidence = []
        
        for event in events:
            hour = event.timestamp.hour
            day = event.timestamp.weekday()
            
            if hour not in self.normal_hours:
                off_hours_count += 1
            
            if day not in self.normal_days:
                weekend_count += 1
            
            # Check against learned patterns
            if entity_id in self.access_patterns:
                pattern = self.access_patterns[entity_id]
                if hour in pattern and pattern[hour] < 3:  # Unusual hour
                    unusual_pattern_count += 1
        
        total = len(events)
        
        off_hours_ratio = off_hours_count / total if total > 0 else 0
        weekend_ratio = weekend_count / total if total > 0 else 0
        unusual_ratio = unusual_pattern_count / total if total > 0 else 0
        
        if off_hours_ratio > 0.3:
            evidence.append(f"{off_hours_count} events during off-hours")
        if weekend_ratio > 0.3:
            evidence.append(f"{weekend_count} events on weekends")
        if unusual_ratio > 0.2:
            evidence.append(f"{unusual_pattern_count} events at unusual times")
        
        final_score = min(1.0, off_hours_ratio * 0.3 + weekend_ratio * 0.2 + unusual_ratio * 0.5)
        
        return RiskFactor(
            factor_id=f"temporal_{entity_id}",
            category=self.category,
            name="Temporal Risk",
            description="Risk from access timing",
            weight=self.weight,
            score=final_score,
            confidence=min(0.9, 0.4 + total * 0.02),
            evidence=evidence or ["Normal access times"],
            metadata={
                "off_hours_ratio": off_hours_ratio,
                "weekend_ratio": weekend_ratio,
                "unusual_pattern_ratio": unusual_ratio
            }
        )
    
    def update(self, event: RiskEvent) -> Optional[float]:
        """Update access patterns."""
        entity_id = event.entity_id
        hour = event.timestamp.hour
        
        if entity_id not in self.access_patterns:
            self.access_patterns[entity_id] = {}
        
        self.access_patterns[entity_id][hour] = \
            self.access_patterns[entity_id].get(hour, 0) + 1
        
        return event.risk_impact


class VolumetricRiskScorer(RiskScorer):
    """Score volume/rate-based risks."""
    
    def __init__(self, weight: float = 0.1):
        super().__init__(RiskCategory.VOLUMETRIC, weight)
        self.rate_baselines: Dict[str, Dict[str, float]] = {}
        self.window_events: Dict[str, deque] = {}
        self.window_minutes = 60
    
    def score(self, events: List[RiskEvent], context: Dict[str, Any]) -> RiskFactor:
        """Calculate volumetric risk."""
        entity_id = context.get("entity_id", "unknown")
        
        if not events:
            return RiskFactor(
                factor_id=f"volumetric_{entity_id}",
                category=self.category,
                name="Volumetric Risk",
                description="No volume data",
                weight=self.weight,
                score=0.0,
                confidence=0.3,
                evidence=["No activity data"]
            )
        
        # Calculate current rate
        now = datetime.now()
        window = timedelta(minutes=self.window_minutes)
        recent = [e for e in events if now - e.timestamp <= window]
        
        current_rate = len(recent)
        
        # Compare to baseline
        baseline = self.rate_baselines.get(entity_id, {})
        baseline_mean = baseline.get("mean", current_rate)
        baseline_std = baseline.get("std", max(1, current_rate * 0.5))
        
        # Z-score for rate
        if baseline_std > 0:
            z_score = (current_rate - baseline_mean) / baseline_std
        else:
            z_score = 0
        
        evidence = []
        
        # High volume check
        if z_score > 2:
            evidence.append(f"High activity: {current_rate} events in {self.window_minutes}min")
        
        # Burst detection
        if current_rate > baseline_mean * 3:
            evidence.append("Burst activity detected")
        
        # Score based on deviation
        final_score = min(1.0, max(0, z_score / 3))
        
        return RiskFactor(
            factor_id=f"volumetric_{entity_id}",
            category=self.category,
            name="Volumetric Risk",
            description="Risk from activity volume",
            weight=self.weight,
            score=final_score,
            confidence=min(0.9, 0.4 + len(events) * 0.01),
            evidence=evidence or ["Normal activity volume"],
            metadata={
                "current_rate": current_rate,
                "baseline_mean": baseline_mean,
                "baseline_std": baseline_std,
                "z_score": z_score
            }
        )
    
    def update(self, event: RiskEvent) -> Optional[float]:
        """Update rate baselines."""
        entity_id = event.entity_id
        
        if entity_id not in self.window_events:
            self.window_events[entity_id] = deque(maxlen=1000)
        
        self.window_events[entity_id].append(event.timestamp)
        
        # Recalculate baseline periodically
        if len(self.window_events[entity_id]) >= 100:
            self._update_baseline(entity_id)
        
        return event.risk_impact
    
    def _update_baseline(self, entity_id: str) -> None:
        """Update rate baseline."""
        timestamps = list(self.window_events[entity_id])
        
        if len(timestamps) < 10:
            return
        
        # Calculate events per window
        window = timedelta(minutes=self.window_minutes)
        rates = []
        
        for i in range(len(timestamps) - 1):
            count = sum(1 for t in timestamps if timestamps[i] <= t < timestamps[i] + window)
            rates.append(count)
        
        if rates:
            self.rate_baselines[entity_id] = {
                "mean": statistics.mean(rates),
                "std": statistics.stdev(rates) if len(rates) > 1 else 1.0
            }


class IdentityRiskScorer(RiskScorer):
    """Score identity-related risks."""
    
    def __init__(self, weight: float = 0.1):
        super().__init__(RiskCategory.IDENTITY, weight)
        self.known_identities: Dict[str, Set[str]] = {}
        self.credential_events: Dict[str, List[datetime]] = {}
    
    def score(self, events: List[RiskEvent], context: Dict[str, Any]) -> RiskFactor:
        """Calculate identity risk."""
        entity_id = context.get("entity_id", "unknown")
        
        identity_events = [e for e in events if e.category == RiskCategory.IDENTITY]
        
        if not identity_events:
            return RiskFactor(
                factor_id=f"identity_{entity_id}",
                category=self.category,
                name="Identity Risk",
                description="No identity events",
                weight=self.weight,
                score=0.1,  # Unknown identity has slight risk
                confidence=0.3,
                evidence=["Identity not verified"]
            )
        
        auth_failures = 0
        credential_changes = 0
        new_identities = 0
        evidence = []
        
        for event in identity_events:
            if "auth_failure" in event.event_type.lower():
                auth_failures += 1
            if "credential_change" in event.event_type.lower():
                credential_changes += 1
            if "new_identity" in event.event_type.lower():
                new_identities += 1
        
        if auth_failures > 3:
            evidence.append(f"{auth_failures} authentication failures")
        if credential_changes > 1:
            evidence.append(f"{credential_changes} credential changes")
        if new_identities > 0:
            evidence.append(f"{new_identities} new identities")
        
        # Score components
        auth_score = min(1.0, auth_failures * 0.2)
        cred_score = min(1.0, credential_changes * 0.3)
        identity_score = min(0.5, new_identities * 0.25)
        
        final_score = min(1.0, auth_score + cred_score + identity_score)
        
        return RiskFactor(
            factor_id=f"identity_{entity_id}",
            category=self.category,
            name="Identity Risk",
            description="Risk from identity/authentication",
            weight=self.weight,
            score=final_score,
            confidence=min(0.9, 0.4 + len(identity_events) * 0.1),
            evidence=evidence or ["Normal identity activity"],
            metadata={
                "auth_failures": auth_failures,
                "credential_changes": credential_changes,
                "new_identities": new_identities
            }
        )
    
    def update(self, event: RiskEvent) -> Optional[float]:
        """Update identity tracking."""
        if event.category != RiskCategory.IDENTITY:
            return None
        
        identity = event.properties.get("identity")
        if identity and event.entity_id:
            if event.entity_id not in self.known_identities:
                self.known_identities[event.entity_id] = set()
            self.known_identities[event.entity_id].add(identity)
        
        return event.risk_impact


@dataclass
class RiskScoringConfig:
    """Configuration for risk scoring system."""
    enabled: bool = True
    # Scorer weights
    license_weight: float = 0.3
    behavioral_weight: float = 0.25
    environmental_weight: float = 0.15
    temporal_weight: float = 0.1
    volumetric_weight: float = 0.1
    identity_weight: float = 0.1
    # Thresholds
    alert_threshold: float = 0.7
    critical_threshold: float = 0.9
    # History
    history_window_hours: int = 24
    max_history_entries: int = 1000
    # Trend detection
    trend_window_entries: int = 10
    trend_increase_threshold: float = 0.2


class RiskScoringEngine:
    """Main engine for ML-enhanced risk scoring."""
    
    def __init__(self, config: Optional[RiskScoringConfig] = None):
        self.config = config or RiskScoringConfig()
        self.scorers: Dict[RiskCategory, RiskScorer] = {}
        self.profiles: Dict[str, RiskProfile] = {}
        self.event_history: Dict[str, List[RiskEvent]] = {}
        self._initialize_scorers()
    
    def _initialize_scorers(self) -> None:
        """Initialize risk scorers."""
        self.scorers = {
            RiskCategory.LICENSE: LicenseRiskScorer(self.config.license_weight),
            RiskCategory.BEHAVIORAL: BehavioralRiskScorer(self.config.behavioral_weight),
            RiskCategory.ENVIRONMENTAL: EnvironmentalRiskScorer(self.config.environmental_weight),
            RiskCategory.TEMPORAL: TemporalRiskScorer(self.config.temporal_weight),
            RiskCategory.VOLUMETRIC: VolumetricRiskScorer(self.config.volumetric_weight),
            RiskCategory.IDENTITY: IdentityRiskScorer(self.config.identity_weight)
        }
    
    def score_entity(
        self,
        entity_id: str,
        entity_type: str = "license",
        events: Optional[List[RiskEvent]] = None
    ) -> RiskProfile:
        """Calculate comprehensive risk score for entity."""
        if not self.config.enabled:
            return self._empty_profile(entity_id, entity_type)
        
        # Get events from history if not provided
        if events is None:
            events = self._get_recent_events(entity_id)
        
        context = {"entity_id": entity_id, "entity_type": entity_type}
        
        # Score each category
        factors = []
        for category, scorer in self.scorers.items():
            try:
                factor = scorer.score(events, context)
                factors.append(factor)
            except Exception as e:
                logger.warning(f"Scoring failed for {category.value}: {e}")
        
        # Calculate overall score
        if factors:
            total_weight = sum(f.weight * f.confidence for f in factors)
            if total_weight > 0:
                overall_score = sum(f.weighted_score for f in factors) / total_weight
            else:
                overall_score = 0.0
        else:
            overall_score = 0.0
        
        overall_level = RiskLevel.from_score(overall_score)
        
        # Calculate trend
        trend = self._calculate_trend(entity_id, overall_score)
        
        # Create profile
        profile = RiskProfile(
            entity_id=entity_id,
            entity_type=entity_type,
            overall_score=overall_score,
            overall_level=overall_level,
            trend=trend,
            factors=factors,
            last_updated=datetime.now()
        )
        
        # Update history
        profile.history = self._get_score_history(entity_id)
        profile.history.append((datetime.now(), overall_score))
        
        # Store profile
        self.profiles[entity_id] = profile
        
        logger.debug(f"Risk score for {entity_id}: {overall_score:.3f} ({overall_level.value})")
        
        return profile
    
    def _empty_profile(self, entity_id: str, entity_type: str) -> RiskProfile:
        """Create empty risk profile."""
        return RiskProfile(
            entity_id=entity_id,
            entity_type=entity_type,
            overall_score=0.0,
            overall_level=RiskLevel.MINIMAL,
            trend=RiskTrend.STABLE,
            factors=[],
            last_updated=datetime.now()
        )
    
    def _get_recent_events(self, entity_id: str) -> List[RiskEvent]:
        """Get recent events from history."""
        if entity_id not in self.event_history:
            return []
        
        cutoff = datetime.now() - timedelta(hours=self.config.history_window_hours)
        return [e for e in self.event_history[entity_id] if e.timestamp >= cutoff]
    
    def _get_score_history(self, entity_id: str) -> List[Tuple[datetime, float]]:
        """Get score history for entity."""
        if entity_id in self.profiles:
            return self.profiles[entity_id].history[-self.config.max_history_entries:]
        return []
    
    def _calculate_trend(self, entity_id: str, current_score: float) -> RiskTrend:
        """Calculate risk trend."""
        history = self._get_score_history(entity_id)
        
        if len(history) < self.config.trend_window_entries:
            return RiskTrend.STABLE
        
        recent = [s for _, s in history[-self.config.trend_window_entries:]]
        
        if not recent:
            return RiskTrend.STABLE
        
        avg_past = statistics.mean(recent[:-1]) if len(recent) > 1 else recent[0]
        
        change = current_score - avg_past
        
        if change > self.config.trend_increase_threshold:
            if change > 0.5:
                return RiskTrend.SPIKING
            return RiskTrend.INCREASING
        elif change < -self.config.trend_increase_threshold:
            return RiskTrend.DECREASING
        else:
            return RiskTrend.STABLE
    
    def process_event(self, event: RiskEvent) -> Optional[RiskProfile]:
        """Process new risk event."""
        if not self.config.enabled:
            return None
        
        # Store in history
        if event.entity_id not in self.event_history:
            self.event_history[event.entity_id] = []
        
        self.event_history[event.entity_id].append(event)
        
        # Trim history
        cutoff = datetime.now() - timedelta(hours=self.config.history_window_hours * 2)
        self.event_history[event.entity_id] = [
            e for e in self.event_history[event.entity_id] if e.timestamp >= cutoff
        ]
        
        # Update relevant scorer
        scorer = self.scorers.get(event.category)
        if scorer:
            scorer.update(event)
        
        # Rescore entity
        return self.score_entity(event.entity_id)
    
    def get_high_risk_entities(self, threshold: Optional[float] = None) -> List[RiskProfile]:
        """Get entities above risk threshold."""
        threshold = threshold or self.config.alert_threshold
        
        return [
            profile for profile in self.profiles.values()
            if profile.overall_score >= threshold
        ]
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """Get summary of risk across all entities."""
        if not self.profiles:
            return {"total_entities": 0}
        
        scores = [p.overall_score for p in self.profiles.values()]
        
        by_level = {}
        for profile in self.profiles.values():
            level = profile.overall_level.value
            by_level[level] = by_level.get(level, 0) + 1
        
        by_trend = {}
        for profile in self.profiles.values():
            trend = profile.trend.value
            by_trend[trend] = by_trend.get(trend, 0) + 1
        
        return {
            "total_entities": len(self.profiles),
            "avg_risk": statistics.mean(scores),
            "max_risk": max(scores),
            "min_risk": min(scores),
            "by_level": by_level,
            "by_trend": by_trend,
            "high_risk_count": len(self.get_high_risk_entities())
        }
    
    def export_profiles(self) -> Dict[str, Any]:
        """Export all risk profiles."""
        return {
            "profiles": {
                entity_id: profile.to_dict()
                for entity_id, profile in self.profiles.items()
            },
            "summary": self.get_risk_summary(),
            "exported_at": datetime.now().isoformat()
        }
