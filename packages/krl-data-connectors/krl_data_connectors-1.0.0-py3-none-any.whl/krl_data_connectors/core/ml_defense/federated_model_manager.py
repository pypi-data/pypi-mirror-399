# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Federated Model Manager - Phase 3 Week 20

Merges Federated Learning + Multi-Model Versioning with Tiered ML Governance.

ML Governance by Tier:
- Community: Static models only (no updates, no federation)
- Pro: Hybrid (scheduled updates, federated aggregation, manual rollback)
- Enterprise: Full Adaptive (real-time learning, auto-rollback, drift detection)

Key Features:
- Model versioning with semantic versioning
- Federated learning coordination
- Tier-based model access control
- Automatic drift detection and rollback
- Model registry with health monitoring
"""

from __future__ import annotations

import hashlib
import logging
import statistics
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Protocol,
    Set,
    Tuple,
    TypeVar,
)
from collections import deque

logger = logging.getLogger(__name__)


# =============================================================================
# Type Variables
# =============================================================================

T = TypeVar("T")
ModelT = TypeVar("ModelT")


# =============================================================================
# Enums
# =============================================================================

class ModelTier(Enum):
    """Model access tiers."""
    COMMUNITY = "community"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class ModelState(Enum):
    """Model lifecycle states."""
    DRAFT = "draft"
    TRAINING = "training"
    VALIDATING = "validating"
    STAGED = "staged"
    ACTIVE = "active"
    DEGRADED = "degraded"
    DEPRECATED = "deprecated"
    ROLLED_BACK = "rolled_back"
    ARCHIVED = "archived"


class GovernanceMode(Enum):
    """ML governance modes by tier."""
    STATIC = "static"           # Community: No updates
    HYBRID = "hybrid"           # Pro: Scheduled updates
    ADAPTIVE = "adaptive"       # Enterprise: Real-time learning


class FederatedRole(Enum):
    """Roles in federated learning."""
    COORDINATOR = "coordinator"
    PARTICIPANT = "participant"
    OBSERVER = "observer"


class UpdateStrategy(Enum):
    """Model update strategies."""
    NONE = "none"               # Community
    SCHEDULED = "scheduled"     # Pro
    REAL_TIME = "real_time"     # Enterprise
    ON_DEMAND = "on_demand"     # All tiers (manual)


class AggregationMethod(Enum):
    """Federated aggregation methods."""
    FED_AVG = "fed_avg"                 # Federated Averaging
    FED_PROX = "fed_prox"               # Federated Proximal
    FED_ADAM = "fed_adam"               # Federated Adam
    WEIGHTED_AVERAGE = "weighted_avg"   # Weight by sample count
    SECURE_AGG = "secure_agg"           # Secure aggregation


class DriftSeverity(Enum):
    """Model drift severity levels."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass(frozen=True)
class SemanticVersion:
    """Semantic version for models."""
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None
    
    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build:
            version += f"+{self.build}"
        return version
    
    def __lt__(self, other: "SemanticVersion") -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
    
    def __le__(self, other: "SemanticVersion") -> bool:
        return (self.major, self.minor, self.patch) <= (other.major, other.minor, other.patch)
    
    def bump_major(self) -> "SemanticVersion":
        return SemanticVersion(self.major + 1, 0, 0)
    
    def bump_minor(self) -> "SemanticVersion":
        return SemanticVersion(self.major, self.minor + 1, 0)
    
    def bump_patch(self) -> "SemanticVersion":
        return SemanticVersion(self.major, self.minor, self.patch + 1)
    
    @classmethod
    def parse(cls, version_str: str) -> "SemanticVersion":
        """Parse version string."""
        parts = version_str.split("-", 1)
        main_version = parts[0]
        prerelease = parts[1].split("+")[0] if len(parts) > 1 else None
        build = parts[1].split("+")[1] if len(parts) > 1 and "+" in parts[1] else None
        
        version_parts = main_version.split(".")
        return cls(
            major=int(version_parts[0]),
            minor=int(version_parts[1]) if len(version_parts) > 1 else 0,
            patch=int(version_parts[2]) if len(version_parts) > 2 else 0,
            prerelease=prerelease,
            build=build,
        )


@dataclass
class ModelMetrics:
    """Model performance metrics."""
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    latency_p50_ms: float = 0.0
    latency_p99_ms: float = 0.0
    throughput_qps: float = 0.0
    memory_mb: float = 0.0
    inference_count: int = 0
    error_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "latency_p50_ms": self.latency_p50_ms,
            "latency_p99_ms": self.latency_p99_ms,
            "throughput_qps": self.throughput_qps,
            "memory_mb": self.memory_mb,
            "inference_count": self.inference_count,
            "error_rate": self.error_rate,
            "last_updated": self.last_updated.isoformat(),
        }


@dataclass
class DriftMetrics:
    """Model drift detection metrics."""
    data_drift_score: float = 0.0         # 0-1, how much input distribution changed
    concept_drift_score: float = 0.0      # 0-1, how much output distribution changed
    feature_drift_scores: Dict[str, float] = field(default_factory=dict)
    prediction_shift: float = 0.0         # Change in prediction distribution
    performance_degradation: float = 0.0  # Drop in accuracy
    severity: DriftSeverity = DriftSeverity.NONE
    detected_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "data_drift_score": self.data_drift_score,
            "concept_drift_score": self.concept_drift_score,
            "feature_drift_scores": self.feature_drift_scores,
            "prediction_shift": self.prediction_shift,
            "performance_degradation": self.performance_degradation,
            "severity": self.severity.value,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
        }
    
    def compute_severity(self) -> DriftSeverity:
        """Compute overall drift severity."""
        max_drift = max(self.data_drift_score, self.concept_drift_score)
        
        if max_drift < 0.1 and self.performance_degradation < 0.05:
            return DriftSeverity.NONE
        elif max_drift < 0.25 or self.performance_degradation < 0.1:
            return DriftSeverity.LOW
        elif max_drift < 0.5 or self.performance_degradation < 0.2:
            return DriftSeverity.MEDIUM
        elif max_drift < 0.75 or self.performance_degradation < 0.3:
            return DriftSeverity.HIGH
        else:
            return DriftSeverity.CRITICAL


@dataclass
class ModelVersion:
    """
    Immutable model version snapshot.
    
    Represents a specific version of a model with its
    metadata, metrics, and state information.
    """
    model_id: str
    version: SemanticVersion
    state: ModelState
    created_at: datetime
    updated_at: datetime
    min_tier: ModelTier  # Minimum tier required to use this model
    
    # Model data
    weights_hash: str = ""
    config_hash: str = ""
    
    # Training info
    training_samples: int = 0
    training_duration_s: float = 0.0
    training_started: Optional[datetime] = None
    training_completed: Optional[datetime] = None
    
    # Performance
    metrics: ModelMetrics = field(default_factory=ModelMetrics)
    drift: DriftMetrics = field(default_factory=DriftMetrics)
    
    # Lineage
    parent_version: Optional[str] = None
    federation_round: Optional[int] = None
    
    # Metadata
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "version": str(self.version),
            "state": self.state.value,
            "min_tier": self.min_tier.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "weights_hash": self.weights_hash,
            "training_samples": self.training_samples,
            "metrics": self.metrics.to_dict(),
            "drift": self.drift.to_dict(),
            "parent_version": self.parent_version,
            "federation_round": self.federation_round,
            "tags": list(self.tags),
        }


@dataclass
class FederatedUpdate:
    """Update from a federated participant."""
    participant_id: str
    model_id: str
    version: SemanticVersion
    round_number: int
    
    # Gradient/weight updates
    updates: Dict[str, Any]  # Layer name -> update tensor
    sample_count: int
    
    # Quality metrics
    local_loss: float = 0.0
    local_accuracy: float = 0.0
    
    # Timing
    training_time_s: float = 0.0
    submitted_at: datetime = field(default_factory=datetime.now)
    
    # Privacy
    differential_privacy_epsilon: Optional[float] = None
    gradient_clipping_norm: Optional[float] = None


@dataclass
class FederatedRound:
    """Federated learning round state."""
    round_number: int
    model_id: str
    started_at: datetime
    
    # Participation
    expected_participants: Set[str]
    received_updates: Dict[str, FederatedUpdate] = field(default_factory=dict)
    
    # Aggregation
    aggregation_method: AggregationMethod = AggregationMethod.FED_AVG
    aggregated: bool = False
    aggregated_at: Optional[datetime] = None
    
    # Result
    new_version: Optional[SemanticVersion] = None
    global_metrics: Optional[ModelMetrics] = None
    
    @property
    def participation_rate(self) -> float:
        if not self.expected_participants:
            return 0.0
        return len(self.received_updates) / len(self.expected_participants)
    
    @property
    def total_samples(self) -> int:
        return sum(u.sample_count for u in self.received_updates.values())


# =============================================================================
# Tier Governance Configuration
# =============================================================================

@dataclass(frozen=True)
class TierGovernanceConfig:
    """ML governance configuration per tier."""
    tier: ModelTier
    governance_mode: GovernanceMode
    update_strategy: UpdateStrategy
    
    # Model access
    max_concurrent_models: int
    allowed_model_types: Set[str]
    can_access_beta: bool
    can_access_experimental: bool
    
    # Federated learning
    federated_role: FederatedRole
    can_participate_in_training: bool
    can_contribute_updates: bool
    
    # Auto-actions
    auto_rollback_enabled: bool
    auto_drift_detection: bool
    drift_threshold: float
    
    # Update windows
    update_window_hours: Optional[Tuple[int, int]]  # e.g., (2, 6) = 2am-6am
    min_update_interval_hours: int


TIER_GOVERNANCE: Dict[ModelTier, TierGovernanceConfig] = {
    ModelTier.COMMUNITY: TierGovernanceConfig(
        tier=ModelTier.COMMUNITY,
        governance_mode=GovernanceMode.STATIC,
        update_strategy=UpdateStrategy.NONE,
        max_concurrent_models=3,
        allowed_model_types={"anomaly_detection", "risk_scoring"},
        can_access_beta=False,
        can_access_experimental=False,
        federated_role=FederatedRole.OBSERVER,
        can_participate_in_training=False,
        can_contribute_updates=False,
        auto_rollback_enabled=False,
        auto_drift_detection=False,
        drift_threshold=0.5,
        update_window_hours=None,
        min_update_interval_hours=720,  # 30 days
    ),
    ModelTier.PRO: TierGovernanceConfig(
        tier=ModelTier.PRO,
        governance_mode=GovernanceMode.HYBRID,
        update_strategy=UpdateStrategy.SCHEDULED,
        max_concurrent_models=10,
        allowed_model_types={"anomaly_detection", "risk_scoring", "pattern_learning", "predictive"},
        can_access_beta=True,
        can_access_experimental=False,
        federated_role=FederatedRole.PARTICIPANT,
        can_participate_in_training=True,
        can_contribute_updates=True,
        auto_rollback_enabled=False,  # Manual rollback only
        auto_drift_detection=True,
        drift_threshold=0.3,
        update_window_hours=(2, 6),  # 2am-6am
        min_update_interval_hours=168,  # 7 days
    ),
    ModelTier.ENTERPRISE: TierGovernanceConfig(
        tier=ModelTier.ENTERPRISE,
        governance_mode=GovernanceMode.ADAPTIVE,
        update_strategy=UpdateStrategy.REAL_TIME,
        max_concurrent_models=50,
        allowed_model_types={"*"},  # All types
        can_access_beta=True,
        can_access_experimental=True,
        federated_role=FederatedRole.COORDINATOR,
        can_participate_in_training=True,
        can_contribute_updates=True,
        auto_rollback_enabled=True,
        auto_drift_detection=True,
        drift_threshold=0.15,
        update_window_hours=None,  # Any time
        min_update_interval_hours=1,  # Real-time
    ),
}


def get_governance_config(tier: ModelTier) -> TierGovernanceConfig:
    """Get governance configuration for a tier."""
    return TIER_GOVERNANCE[tier]


# =============================================================================
# Protocols
# =============================================================================

class ModelProtocol(Protocol):
    """Protocol for ML models."""
    
    def predict(self, inputs: Any) -> Any:
        """Run inference."""
        ...
    
    def get_weights(self) -> Dict[str, Any]:
        """Get model weights."""
        ...
    
    def set_weights(self, weights: Dict[str, Any]) -> None:
        """Set model weights."""
        ...


class DriftDetectorProtocol(Protocol):
    """Protocol for drift detectors."""
    
    def detect_drift(
        self,
        reference_data: Any,
        current_data: Any,
    ) -> DriftMetrics:
        """Detect drift between reference and current data."""
        ...


# =============================================================================
# Federated Aggregators
# =============================================================================

class FederatedAggregator(ABC):
    """Base class for federated aggregation."""
    
    @abstractmethod
    def aggregate(
        self,
        base_weights: Dict[str, Any],
        updates: List[FederatedUpdate],
    ) -> Dict[str, Any]:
        """Aggregate updates into new weights."""
        pass


class FedAvgAggregator(FederatedAggregator):
    """Federated Averaging aggregator."""
    
    def aggregate(
        self,
        base_weights: Dict[str, Any],
        updates: List[FederatedUpdate],
    ) -> Dict[str, Any]:
        if not updates:
            return base_weights
        
        total_samples = sum(u.sample_count for u in updates)
        if total_samples == 0:
            return base_weights
        
        # Weighted average by sample count
        aggregated: Dict[str, Any] = {}
        
        for layer_name in base_weights:
            weighted_sum = None
            
            for update in updates:
                if layer_name not in update.updates:
                    continue
                
                weight = update.sample_count / total_samples
                layer_update = update.updates[layer_name]
                
                if weighted_sum is None:
                    # Initialize with first update
                    weighted_sum = self._multiply_weights(layer_update, weight)
                else:
                    # Add weighted update
                    weighted_sum = self._add_weights(
                        weighted_sum,
                        self._multiply_weights(layer_update, weight)
                    )
            
            aggregated[layer_name] = weighted_sum if weighted_sum is not None else base_weights[layer_name]
        
        return aggregated
    
    def _multiply_weights(self, weights: Any, scalar: float) -> Any:
        """Multiply weights by scalar (placeholder for actual tensor ops)."""
        if isinstance(weights, (int, float)):
            return weights * scalar
        elif isinstance(weights, list):
            return [self._multiply_weights(w, scalar) for w in weights]
        elif isinstance(weights, dict):
            return {k: self._multiply_weights(v, scalar) for k, v in weights.items()}
        return weights
    
    def _add_weights(self, a: Any, b: Any) -> Any:
        """Add two weight structures (placeholder for actual tensor ops)."""
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return a + b
        elif isinstance(a, list) and isinstance(b, list):
            return [self._add_weights(x, y) for x, y in zip(a, b)]
        elif isinstance(a, dict) and isinstance(b, dict):
            return {k: self._add_weights(a[k], b[k]) for k in a}
        return a


class WeightedAvgAggregator(FederatedAggregator):
    """Weighted average with quality weighting."""
    
    def __init__(self, quality_weight: float = 0.3):
        self.quality_weight = quality_weight
    
    def aggregate(
        self,
        base_weights: Dict[str, Any],
        updates: List[FederatedUpdate],
    ) -> Dict[str, Any]:
        if not updates:
            return base_weights
        
        # Compute weights based on samples and quality
        weights = []
        for update in updates:
            sample_weight = update.sample_count
            quality_weight = update.local_accuracy * self.quality_weight
            combined = sample_weight * (1 + quality_weight)
            weights.append(combined)
        
        total_weight = sum(weights)
        if total_weight == 0:
            return base_weights
        
        # Normalize
        weights = [w / total_weight for w in weights]
        
        # Apply FedAvg with adjusted weights
        aggregated: Dict[str, Any] = {}
        
        for layer_name in base_weights:
            weighted_sum = None
            
            for update, weight in zip(updates, weights):
                if layer_name not in update.updates:
                    continue
                
                layer_update = update.updates[layer_name]
                
                if weighted_sum is None:
                    weighted_sum = self._scale(layer_update, weight)
                else:
                    weighted_sum = self._add(weighted_sum, self._scale(layer_update, weight))
            
            aggregated[layer_name] = weighted_sum if weighted_sum is not None else base_weights[layer_name]
        
        return aggregated
    
    def _scale(self, val: Any, s: float) -> Any:
        if isinstance(val, (int, float)):
            return val * s
        elif isinstance(val, list):
            return [self._scale(v, s) for v in val]
        elif isinstance(val, dict):
            return {k: self._scale(v, s) for k, v in val.items()}
        return val
    
    def _add(self, a: Any, b: Any) -> Any:
        if isinstance(a, (int, float)):
            return a + b
        elif isinstance(a, list):
            return [self._add(x, y) for x, y in zip(a, b)]
        elif isinstance(a, dict):
            return {k: self._add(a[k], b[k]) for k in a}
        return a


AGGREGATORS: Dict[AggregationMethod, FederatedAggregator] = {
    AggregationMethod.FED_AVG: FedAvgAggregator(),
    AggregationMethod.WEIGHTED_AVERAGE: WeightedAvgAggregator(),
}


# =============================================================================
# Model Registry
# =============================================================================

class VersionedModelRegistry:
    """
    Model registry with versioning support.
    
    Manages model versions, their state transitions,
    and rollback capabilities.
    """
    
    def __init__(self, max_versions_per_model: int = 10):
        self._models: Dict[str, Dict[str, ModelVersion]] = {}  # model_id -> version_str -> version
        self._active_versions: Dict[str, str] = {}  # model_id -> active version_str
        self._model_weights: Dict[str, Dict[str, Any]] = {}  # model_id:version -> weights
        self._max_versions = max_versions_per_model
        self._lock = threading.RLock()
        self._listeners: List[Callable[[str, ModelVersion, str], None]] = []
    
    def register_model(
        self,
        model_id: str,
        version: SemanticVersion,
        min_tier: ModelTier = ModelTier.COMMUNITY,
        weights: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ModelVersion:
        """Register a new model version."""
        with self._lock:
            now = datetime.now()
            
            # Create version
            model_version = ModelVersion(
                model_id=model_id,
                version=version,
                state=ModelState.DRAFT,
                created_at=now,
                updated_at=now,
                min_tier=min_tier,
                weights_hash=self._compute_hash(weights) if weights else "",
                metadata=metadata or {},
            )
            
            # Store
            if model_id not in self._models:
                self._models[model_id] = {}
            
            version_str = str(version)
            self._models[model_id][version_str] = model_version
            
            if weights:
                key = f"{model_id}:{version_str}"
                self._model_weights[key] = weights
            
            # Cleanup old versions
            self._cleanup_old_versions(model_id)
            
            logger.info(f"Registered model {model_id} version {version_str}")
            self._notify_listeners(model_id, model_version, "registered")
            
            return model_version
    
    def activate_version(self, model_id: str, version_str: str) -> bool:
        """Activate a specific version."""
        with self._lock:
            if model_id not in self._models:
                return False
            if version_str not in self._models[model_id]:
                return False
            
            # Deactivate current
            if model_id in self._active_versions:
                old_version = self._active_versions[model_id]
                if old_version in self._models[model_id]:
                    self._models[model_id][old_version].state = ModelState.DEPRECATED
            
            # Activate new
            self._models[model_id][version_str].state = ModelState.ACTIVE
            self._models[model_id][version_str].updated_at = datetime.now()
            self._active_versions[model_id] = version_str
            
            logger.info(f"Activated {model_id} version {version_str}")
            self._notify_listeners(model_id, self._models[model_id][version_str], "activated")
            
            return True
    
    def get_active_version(self, model_id: str) -> Optional[ModelVersion]:
        """Get the active version of a model."""
        with self._lock:
            if model_id not in self._active_versions:
                return None
            
            version_str = self._active_versions[model_id]
            return self._models.get(model_id, {}).get(version_str)
    
    def get_version(self, model_id: str, version_str: str) -> Optional[ModelVersion]:
        """Get a specific version."""
        with self._lock:
            return self._models.get(model_id, {}).get(version_str)
    
    def get_all_versions(self, model_id: str) -> List[ModelVersion]:
        """Get all versions of a model."""
        with self._lock:
            return list(self._models.get(model_id, {}).values())
    
    def get_weights(self, model_id: str, version_str: str) -> Optional[Dict[str, Any]]:
        """Get model weights for a version."""
        key = f"{model_id}:{version_str}"
        return self._model_weights.get(key)
    
    def update_weights(
        self,
        model_id: str,
        version_str: str,
        weights: Dict[str, Any],
    ) -> bool:
        """Update weights for a version."""
        with self._lock:
            if model_id not in self._models:
                return False
            if version_str not in self._models[model_id]:
                return False
            
            key = f"{model_id}:{version_str}"
            self._model_weights[key] = weights
            self._models[model_id][version_str].weights_hash = self._compute_hash(weights)
            self._models[model_id][version_str].updated_at = datetime.now()
            
            return True
    
    def update_metrics(
        self,
        model_id: str,
        version_str: str,
        metrics: ModelMetrics,
    ) -> bool:
        """Update metrics for a version."""
        with self._lock:
            if model_id not in self._models:
                return False
            if version_str not in self._models[model_id]:
                return False
            
            self._models[model_id][version_str].metrics = metrics
            self._models[model_id][version_str].updated_at = datetime.now()
            
            return True
    
    def update_drift(
        self,
        model_id: str,
        version_str: str,
        drift: DriftMetrics,
    ) -> bool:
        """Update drift metrics for a version."""
        with self._lock:
            if model_id not in self._models:
                return False
            if version_str not in self._models[model_id]:
                return False
            
            self._models[model_id][version_str].drift = drift
            self._models[model_id][version_str].updated_at = datetime.now()
            
            return True
    
    def update_state(
        self,
        model_id: str,
        version_str: str,
        state: ModelState,
    ) -> bool:
        """Update state for a version."""
        with self._lock:
            if model_id not in self._models:
                return False
            if version_str not in self._models[model_id]:
                return False
            
            self._models[model_id][version_str].state = state
            self._models[model_id][version_str].updated_at = datetime.now()
            
            self._notify_listeners(
                model_id,
                self._models[model_id][version_str],
                f"state_changed:{state.value}"
            )
            
            return True
    
    def rollback(self, model_id: str, to_version: Optional[str] = None) -> Optional[str]:
        """
        Rollback to a previous version.
        
        If to_version is None, rolls back to the previous version.
        Returns the version rolled back to, or None on failure.
        """
        with self._lock:
            if model_id not in self._models:
                return None
            
            versions = sorted(
                self._models[model_id].items(),
                key=lambda x: SemanticVersion.parse(x[0]),
                reverse=True
            )
            
            if not versions:
                return None
            
            current = self._active_versions.get(model_id)
            
            if to_version:
                # Rollback to specific version
                if to_version not in self._models[model_id]:
                    return None
                target = to_version
            else:
                # Find previous version
                target = None
                found_current = False
                
                for v_str, v in versions:
                    if v_str == current:
                        found_current = True
                        continue
                    if found_current and v.state not in [ModelState.ARCHIVED, ModelState.ROLLED_BACK]:
                        target = v_str
                        break
                
                if not target:
                    return None
            
            # Mark current as rolled back
            if current and current in self._models[model_id]:
                self._models[model_id][current].state = ModelState.ROLLED_BACK
            
            # Activate target
            self.activate_version(model_id, target)
            
            logger.warning(f"Rolled back {model_id} from {current} to {target}")
            
            return target
    
    def add_listener(self, listener: Callable[[str, ModelVersion, str], None]) -> None:
        """Add a version change listener."""
        self._listeners.append(listener)
    
    def _notify_listeners(self, model_id: str, version: ModelVersion, event: str) -> None:
        for listener in self._listeners:
            try:
                listener(model_id, version, event)
            except Exception as e:
                logger.warning(f"Listener error: {e}")
    
    def _compute_hash(self, obj: Any) -> str:
        """Compute hash of object."""
        import json
        data = json.dumps(obj, sort_keys=True, default=str)
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _cleanup_old_versions(self, model_id: str) -> None:
        """Remove old versions exceeding max_versions."""
        if model_id not in self._models:
            return
        
        versions = self._models[model_id]
        if len(versions) <= self._max_versions:
            return
        
        # Sort by version (oldest first)
        sorted_versions = sorted(
            versions.items(),
            key=lambda x: SemanticVersion.parse(x[0])
        )
        
        # Keep active and newest versions
        active = self._active_versions.get(model_id)
        to_remove = []
        
        for v_str, v in sorted_versions:
            if len(versions) - len(to_remove) <= self._max_versions:
                break
            if v_str == active:
                continue
            if v.state in [ModelState.ARCHIVED, ModelState.ROLLED_BACK]:
                to_remove.append(v_str)
        
        for v_str in to_remove:
            del self._models[model_id][v_str]
            key = f"{model_id}:{v_str}"
            if key in self._model_weights:
                del self._model_weights[key]


# =============================================================================
# Federated Model Manager
# =============================================================================

class FederatedModelManager:
    """
    Central manager for federated learning and model governance.
    
    Coordinates:
    - Model versioning and registry
    - Federated learning rounds
    - Tier-based access control
    - Drift detection and auto-rollback
    - Update scheduling
    """
    
    def __init__(
        self,
        tier: ModelTier = ModelTier.PRO,
        participant_id: Optional[str] = None,
    ):
        self._tier = tier
        self._config = TIER_GOVERNANCE[tier]
        self._participant_id = participant_id or self._generate_id()
        
        self._registry = VersionedModelRegistry()
        self._models: Dict[str, Any] = {}  # model_id -> actual model object
        
        # Federated state
        self._current_rounds: Dict[str, FederatedRound] = {}  # model_id -> active round
        self._round_history: Dict[str, List[FederatedRound]] = {}  # model_id -> past rounds
        self._aggregators = AGGREGATORS.copy()
        
        # Scheduling
        self._last_updates: Dict[str, datetime] = {}  # model_id -> last update time
        self._scheduled_updates: Dict[str, datetime] = {}  # model_id -> next update time
        
        # Drift detection
        self._drift_detectors: Dict[str, DriftDetectorProtocol] = {}
        self._reference_data: Dict[str, Any] = {}
        
        # Callbacks
        self._on_version_change: List[Callable[[str, ModelVersion], None]] = []
        self._on_drift_detected: List[Callable[[str, DriftMetrics], None]] = []
        self._on_rollback: List[Callable[[str, str, str], None]] = []
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Register for version changes
        self._registry.add_listener(self._on_registry_change)
    
    @property
    def tier(self) -> ModelTier:
        return self._tier
    
    @property
    def governance_config(self) -> TierGovernanceConfig:
        return self._config
    
    @property
    def participant_id(self) -> str:
        return self._participant_id
    
    @property
    def registry(self) -> VersionedModelRegistry:
        return self._registry
    
    # =========================================================================
    # Model Management
    # =========================================================================
    
    def register_model(
        self,
        model_id: str,
        model: Any,
        version: SemanticVersion,
        model_type: str = "generic",
        min_tier: ModelTier = ModelTier.COMMUNITY,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[ModelVersion]:
        """
        Register a model with version.
        
        Enforces tier-based model type restrictions.
        """
        with self._lock:
            # Check model type restrictions
            if "*" not in self._config.allowed_model_types:
                if model_type not in self._config.allowed_model_types:
                    logger.warning(
                        f"Model type {model_type} not allowed for tier {self._tier.value}"
                    )
                    return None
            
            # Check concurrent model limit
            if len(self._models) >= self._config.max_concurrent_models:
                logger.warning(
                    f"Max concurrent models ({self._config.max_concurrent_models}) "
                    f"reached for tier {self._tier.value}"
                )
                return None
            
            # Get weights if model supports it
            weights = None
            if hasattr(model, "get_weights"):
                try:
                    weights = model.get_weights()
                except Exception as e:
                    logger.warning(f"Could not get weights: {e}")
            
            # Register version
            meta = metadata or {}
            meta["model_type"] = model_type
            meta["registered_by"] = self._participant_id
            
            version_obj = self._registry.register_model(
                model_id=model_id,
                version=version,
                min_tier=min_tier,
                weights=weights,
                metadata=meta,
            )
            
            # Store model object
            self._models[model_id] = model
            
            # Activate if first version
            if len(self._registry.get_all_versions(model_id)) == 1:
                self._registry.activate_version(model_id, str(version))
            
            return version_obj
    
    def get_model(
        self,
        model_id: str,
        requester_tier: Optional[ModelTier] = None,
    ) -> Optional[Any]:
        """
        Get a model, enforcing tier access control.
        """
        requester = requester_tier or self._tier
        
        active = self._registry.get_active_version(model_id)
        if not active:
            return None
        
        # Check tier access
        tier_order = [ModelTier.COMMUNITY, ModelTier.PRO, ModelTier.ENTERPRISE]
        requester_level = tier_order.index(requester)
        required_level = tier_order.index(active.min_tier)
        
        if requester_level < required_level:
            logger.warning(
                f"Tier {requester.value} cannot access model requiring {active.min_tier.value}"
            )
            return None
        
        return self._models.get(model_id)
    
    def can_access_model(
        self,
        model_id: str,
        requester_tier: ModelTier,
    ) -> bool:
        """Check if a tier can access a model."""
        active = self._registry.get_active_version(model_id)
        if not active:
            return False
        
        tier_order = [ModelTier.COMMUNITY, ModelTier.PRO, ModelTier.ENTERPRISE]
        return tier_order.index(requester_tier) >= tier_order.index(active.min_tier)
    
    # =========================================================================
    # Model Updates
    # =========================================================================
    
    def can_update_model(self, model_id: str) -> Tuple[bool, str]:
        """Check if model can be updated based on governance."""
        if self._config.update_strategy == UpdateStrategy.NONE:
            return False, "Updates disabled for tier"
        
        # Check update interval
        last = self._last_updates.get(model_id)
        if last:
            min_interval = timedelta(hours=self._config.min_update_interval_hours)
            if datetime.now() - last < min_interval:
                return False, f"Min interval not met (requires {min_interval})"
        
        # Check update window
        if self._config.update_window_hours:
            now = datetime.now()
            start, end = self._config.update_window_hours
            current_hour = now.hour
            
            if not (start <= current_hour < end):
                return False, f"Outside update window ({start}:00-{end}:00)"
        
        return True, "Update allowed"
    
    def update_model(
        self,
        model_id: str,
        new_weights: Dict[str, Any],
        new_version: Optional[SemanticVersion] = None,
        training_info: Optional[Dict[str, Any]] = None,
    ) -> Optional[ModelVersion]:
        """
        Update a model with new weights.
        
        Creates a new version and activates it.
        """
        can_update, reason = self.can_update_model(model_id)
        if not can_update:
            logger.warning(f"Cannot update {model_id}: {reason}")
            return None
        
        with self._lock:
            current = self._registry.get_active_version(model_id)
            if not current:
                logger.warning(f"No active version for {model_id}")
                return None
            
            # Compute new version
            if new_version is None:
                new_version = current.version.bump_patch()
            
            # Apply weights to model
            model = self._models.get(model_id)
            if model and hasattr(model, "set_weights"):
                try:
                    model.set_weights(new_weights)
                except Exception as e:
                    logger.error(f"Failed to set weights: {e}")
                    return None
            
            # Register new version
            meta = current.metadata.copy()
            meta["parent_version"] = str(current.version)
            if training_info:
                meta["training_info"] = training_info
            
            new_ver = self._registry.register_model(
                model_id=model_id,
                version=new_version,
                min_tier=current.min_tier,
                weights=new_weights,
                metadata=meta,
            )
            
            if new_ver:
                new_ver.parent_version = str(current.version)
                self._registry.activate_version(model_id, str(new_version))
                self._last_updates[model_id] = datetime.now()
            
            return new_ver
    
    # =========================================================================
    # Federated Learning
    # =========================================================================
    
    def start_federated_round(
        self,
        model_id: str,
        expected_participants: Set[str],
        aggregation_method: AggregationMethod = AggregationMethod.FED_AVG,
    ) -> Optional[FederatedRound]:
        """
        Start a new federated learning round.
        
        Only coordinators can start rounds.
        """
        if self._config.federated_role != FederatedRole.COORDINATOR:
            logger.warning(
                f"Only coordinators can start rounds, current role: {self._config.federated_role.value}"
            )
            return None
        
        with self._lock:
            # Get current round number
            history = self._round_history.get(model_id, [])
            round_number = len(history) + 1
            
            # Create round
            round_obj = FederatedRound(
                round_number=round_number,
                model_id=model_id,
                started_at=datetime.now(),
                expected_participants=expected_participants,
                aggregation_method=aggregation_method,
            )
            
            self._current_rounds[model_id] = round_obj
            
            logger.info(
                f"Started federated round {round_number} for {model_id} "
                f"with {len(expected_participants)} expected participants"
            )
            
            return round_obj
    
    def submit_update(
        self,
        model_id: str,
        updates: Dict[str, Any],
        sample_count: int,
        local_metrics: Optional[Dict[str, float]] = None,
    ) -> bool:
        """
        Submit an update to a federated round.
        
        Requires participant or coordinator role.
        """
        if not self._config.can_contribute_updates:
            logger.warning(f"Tier {self._tier.value} cannot contribute updates")
            return False
        
        with self._lock:
            round_obj = self._current_rounds.get(model_id)
            if not round_obj:
                logger.warning(f"No active round for {model_id}")
                return False
            
            current = self._registry.get_active_version(model_id)
            if not current:
                return False
            
            # Create update
            update = FederatedUpdate(
                participant_id=self._participant_id,
                model_id=model_id,
                version=current.version,
                round_number=round_obj.round_number,
                updates=updates,
                sample_count=sample_count,
                local_loss=local_metrics.get("loss", 0.0) if local_metrics else 0.0,
                local_accuracy=local_metrics.get("accuracy", 0.0) if local_metrics else 0.0,
            )
            
            round_obj.received_updates[self._participant_id] = update
            
            logger.info(
                f"Submitted update to round {round_obj.round_number} for {model_id} "
                f"(samples: {sample_count})"
            )
            
            return True
    
    def aggregate_round(self, model_id: str) -> Optional[ModelVersion]:
        """
        Aggregate updates and create new version.
        
        Only coordinators can aggregate.
        """
        if self._config.federated_role != FederatedRole.COORDINATOR:
            logger.warning("Only coordinators can aggregate rounds")
            return None
        
        with self._lock:
            round_obj = self._current_rounds.get(model_id)
            if not round_obj:
                return None
            
            if round_obj.aggregated:
                logger.warning(f"Round {round_obj.round_number} already aggregated")
                return None
            
            if not round_obj.received_updates:
                logger.warning("No updates received for aggregation")
                return None
            
            # Get aggregator
            aggregator = self._aggregators.get(
                round_obj.aggregation_method,
                self._aggregators[AggregationMethod.FED_AVG]
            )
            
            # Get base weights
            current = self._registry.get_active_version(model_id)
            if not current:
                return None
            
            base_weights = self._registry.get_weights(model_id, str(current.version))
            if not base_weights:
                logger.warning("No base weights found")
                return None
            
            # Aggregate
            updates = list(round_obj.received_updates.values())
            new_weights = aggregator.aggregate(base_weights, updates)
            
            # Create new version
            new_version = current.version.bump_minor()
            new_ver = self.update_model(
                model_id=model_id,
                new_weights=new_weights,
                new_version=new_version,
                training_info={
                    "federation_round": round_obj.round_number,
                    "participants": len(updates),
                    "total_samples": round_obj.total_samples,
                    "aggregation_method": round_obj.aggregation_method.value,
                },
            )
            
            if new_ver:
                new_ver.federation_round = round_obj.round_number
                round_obj.aggregated = True
                round_obj.aggregated_at = datetime.now()
                round_obj.new_version = new_version
                
                # Move to history
                if model_id not in self._round_history:
                    self._round_history[model_id] = []
                self._round_history[model_id].append(round_obj)
                del self._current_rounds[model_id]
                
                logger.info(
                    f"Aggregated round {round_obj.round_number} for {model_id} -> {new_version}"
                )
            
            return new_ver
    
    # =========================================================================
    # Drift Detection
    # =========================================================================
    
    def register_drift_detector(
        self,
        model_id: str,
        detector: DriftDetectorProtocol,
        reference_data: Any,
    ) -> None:
        """Register a drift detector for a model."""
        self._drift_detectors[model_id] = detector
        self._reference_data[model_id] = reference_data
    
    def check_drift(
        self,
        model_id: str,
        current_data: Any,
    ) -> Optional[DriftMetrics]:
        """
        Check for model drift.
        
        Returns drift metrics if drift is detected.
        """
        if not self._config.auto_drift_detection:
            return None
        
        detector = self._drift_detectors.get(model_id)
        reference = self._reference_data.get(model_id)
        
        if not detector or reference is None:
            return None
        
        try:
            drift = detector.detect_drift(reference, current_data)
            drift.severity = drift.compute_severity()
            drift.detected_at = datetime.now()
            
            # Update registry
            active = self._registry.get_active_version(model_id)
            if active:
                self._registry.update_drift(model_id, str(active.version), drift)
            
            # Check threshold
            max_drift = max(drift.data_drift_score, drift.concept_drift_score)
            if max_drift >= self._config.drift_threshold:
                logger.warning(
                    f"Drift detected for {model_id}: {drift.severity.value} "
                    f"(data: {drift.data_drift_score:.3f}, concept: {drift.concept_drift_score:.3f})"
                )
                
                # Notify
                for cb in self._on_drift_detected:
                    try:
                        cb(model_id, drift)
                    except Exception as e:
                        logger.warning(f"Drift callback error: {e}")
                
                # Auto-rollback for enterprise
                if self._config.auto_rollback_enabled:
                    if drift.severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]:
                        self._handle_auto_rollback(model_id, drift)
            
            return drift
            
        except Exception as e:
            logger.error(f"Drift detection failed for {model_id}: {e}")
            return None
    
    def _handle_auto_rollback(self, model_id: str, drift: DriftMetrics) -> None:
        """Handle automatic rollback on severe drift."""
        current = self._registry.get_active_version(model_id)
        if not current:
            return
        
        previous = self._registry.rollback(model_id)
        if previous:
            logger.warning(
                f"Auto-rollback triggered for {model_id}: "
                f"{current.version} -> {previous} due to {drift.severity.value} drift"
            )
            
            for cb in self._on_rollback:
                try:
                    cb(model_id, str(current.version), previous)
                except Exception as e:
                    logger.warning(f"Rollback callback error: {e}")
    
    # =========================================================================
    # Callbacks
    # =========================================================================
    
    def on_version_change(self, callback: Callable[[str, ModelVersion], None]) -> None:
        """Register version change callback."""
        self._on_version_change.append(callback)
    
    def on_drift_detected(self, callback: Callable[[str, DriftMetrics], None]) -> None:
        """Register drift detection callback."""
        self._on_drift_detected.append(callback)
    
    def on_rollback(self, callback: Callable[[str, str, str], None]) -> None:
        """Register rollback callback (model_id, from_version, to_version)."""
        self._on_rollback.append(callback)
    
    def _on_registry_change(
        self,
        model_id: str,
        version: ModelVersion,
        event: str,
    ) -> None:
        """Handle registry version changes."""
        if event in ["activated", "registered"]:
            for cb in self._on_version_change:
                try:
                    cb(model_id, version)
                except Exception as e:
                    logger.warning(f"Version change callback error: {e}")
    
    # =========================================================================
    # Status & Reporting
    # =========================================================================
    
    def get_model_status(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive model status."""
        active = self._registry.get_active_version(model_id)
        if not active:
            return None
        
        return {
            "model_id": model_id,
            "active_version": str(active.version),
            "state": active.state.value,
            "min_tier": active.min_tier.value,
            "metrics": active.metrics.to_dict(),
            "drift": active.drift.to_dict(),
            "last_updated": active.updated_at.isoformat(),
            "version_count": len(self._registry.get_all_versions(model_id)),
            "can_update": self.can_update_model(model_id)[0],
        }
    
    def get_federation_status(self) -> Dict[str, Any]:
        """Get federated learning status."""
        return {
            "role": self._config.federated_role.value,
            "can_participate": self._config.can_participate_in_training,
            "can_contribute": self._config.can_contribute_updates,
            "active_rounds": {
                model_id: {
                    "round": r.round_number,
                    "participants": len(r.received_updates),
                    "expected": len(r.expected_participants),
                    "started_at": r.started_at.isoformat(),
                }
                for model_id, r in self._current_rounds.items()
            },
            "total_rounds_completed": sum(
                len(h) for h in self._round_history.values()
            ),
        }
    
    def get_governance_status(self) -> Dict[str, Any]:
        """Get governance configuration status."""
        return {
            "tier": self._tier.value,
            "governance_mode": self._config.governance_mode.value,
            "update_strategy": self._config.update_strategy.value,
            "max_models": self._config.max_concurrent_models,
            "current_models": len(self._models),
            "auto_rollback": self._config.auto_rollback_enabled,
            "auto_drift_detection": self._config.auto_drift_detection,
            "drift_threshold": self._config.drift_threshold,
            "update_window": self._config.update_window_hours,
            "min_update_interval_hours": self._config.min_update_interval_hours,
        }
    
    def _generate_id(self) -> str:
        """Generate a unique participant ID."""
        import uuid
        return f"participant-{uuid.uuid4().hex[:8]}"


# =============================================================================
# Factory Functions
# =============================================================================

def create_model_manager(
    tier: str = "pro",
    participant_id: Optional[str] = None,
) -> FederatedModelManager:
    """Create a FederatedModelManager with the specified tier."""
    tier_enum = ModelTier(tier.lower())
    return FederatedModelManager(tier=tier_enum, participant_id=participant_id)


def create_community_manager(participant_id: Optional[str] = None) -> FederatedModelManager:
    """Create a Community tier model manager (static models only)."""
    return FederatedModelManager(tier=ModelTier.COMMUNITY, participant_id=participant_id)


def create_pro_manager(participant_id: Optional[str] = None) -> FederatedModelManager:
    """Create a Pro tier model manager (hybrid governance)."""
    return FederatedModelManager(tier=ModelTier.PRO, participant_id=participant_id)


def create_enterprise_manager(participant_id: Optional[str] = None) -> FederatedModelManager:
    """Create an Enterprise tier model manager (full adaptive)."""
    return FederatedModelManager(tier=ModelTier.ENTERPRISE, participant_id=participant_id)


# =============================================================================
# Convenience Exports
# =============================================================================

__all__ = [
    # Enums
    "ModelTier",
    "ModelState",
    "GovernanceMode",
    "FederatedRole",
    "UpdateStrategy",
    "AggregationMethod",
    "DriftSeverity",
    # Data Classes
    "SemanticVersion",
    "ModelMetrics",
    "DriftMetrics",
    "ModelVersion",
    "FederatedUpdate",
    "FederatedRound",
    "TierGovernanceConfig",
    # Constants
    "TIER_GOVERNANCE",
    # Protocols
    "ModelProtocol",
    "DriftDetectorProtocol",
    # Aggregators
    "FederatedAggregator",
    "FedAvgAggregator",
    "WeightedAvgAggregator",
    "AGGREGATORS",
    # Registry
    "VersionedModelRegistry",
    # Manager
    "FederatedModelManager",
    # Factories
    "create_model_manager",
    "create_community_manager",
    "create_pro_manager",
    "create_enterprise_manager",
    # Functions
    "get_governance_config",
]
