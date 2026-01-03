"""
ML Enforcement Loop - Automated ML-driven Enforcement and Self-Healing.

Week 17: Explicit closed-loop pipeline that:
1. Subscribes to ML anomaly detection events
2. Automatically triggers graduated enforcement actions
3. Monitors for threat resolution
4. Executes self-healing (rollback, recovery, de-escalation)

This module completes the "final layer of behavioral defense" by making
the ML→Enforcement→Self-Healing pipeline explicit and maintainable.
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TypeVar
from collections import defaultdict
import threading
import uuid
import weakref

logger = logging.getLogger(__name__)


# =============================================================================
# Enums and Constants
# =============================================================================

class EnforcementState(Enum):
    """State of enforcement action."""
    
    PENDING = auto()       # Enforcement queued
    ACTIVE = auto()        # Enforcement in effect
    MONITORING = auto()    # Watching for resolution
    HEALING = auto()       # Self-healing in progress
    RESOLVED = auto()      # Threat resolved, enforcement lifted
    ESCALATED = auto()     # Escalated to higher severity
    FAILED = auto()        # Enforcement failed


class HealingStrategy(Enum):
    """Self-healing strategies."""
    
    AUTO_EXPIRE = auto()       # Let enforcement expire naturally
    GRADUAL_RELEASE = auto()   # Gradually reduce restrictions
    IMMEDIATE_RELEASE = auto() # Immediately lift enforcement
    CONDITIONAL = auto()       # Release based on conditions
    MANUAL_ONLY = auto()       # Requires manual intervention


class ThreatResolutionCriteria(Enum):
    """Criteria for determining threat resolution."""
    
    TIME_BASED = auto()        # Resolved after time period
    METRIC_BASED = auto()      # Resolved when metrics normalize
    BEHAVIORAL = auto()        # Resolved when behavior normalizes
    EXTERNAL_SIGNAL = auto()   # Resolved by external system
    COMBINED = auto()          # Multiple criteria must be met


class EnforcementTier(Enum):
    """Graduated enforcement tiers."""
    
    OBSERVE = 1        # Log and monitor only
    WARN = 2           # Send alerts, no restrictions
    THROTTLE = 3       # Rate limit the entity
    RESTRICT = 4       # Restrict specific capabilities
    BLOCK = 5          # Block entity temporarily
    QUARANTINE = 6     # Full isolation
    REVOKE = 7         # Permanent revocation


# Tier escalation mapping
TIER_ESCALATION: Dict[EnforcementTier, EnforcementTier] = {
    EnforcementTier.OBSERVE: EnforcementTier.WARN,
    EnforcementTier.WARN: EnforcementTier.THROTTLE,
    EnforcementTier.THROTTLE: EnforcementTier.RESTRICT,
    EnforcementTier.RESTRICT: EnforcementTier.BLOCK,
    EnforcementTier.BLOCK: EnforcementTier.QUARANTINE,
    EnforcementTier.QUARANTINE: EnforcementTier.REVOKE,
    EnforcementTier.REVOKE: EnforcementTier.REVOKE,  # Max tier
}

# Tier de-escalation mapping
TIER_DEESCALATION: Dict[EnforcementTier, EnforcementTier] = {
    EnforcementTier.OBSERVE: EnforcementTier.OBSERVE,  # Min tier
    EnforcementTier.WARN: EnforcementTier.OBSERVE,
    EnforcementTier.THROTTLE: EnforcementTier.WARN,
    EnforcementTier.RESTRICT: EnforcementTier.THROTTLE,
    EnforcementTier.BLOCK: EnforcementTier.RESTRICT,
    EnforcementTier.QUARANTINE: EnforcementTier.BLOCK,
    EnforcementTier.REVOKE: EnforcementTier.QUARANTINE,
}


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class MLSignal:
    """Signal from ML detection systems."""
    
    signal_id: str = field(default_factory=lambda: f"sig_{uuid.uuid4().hex[:12]}")
    timestamp: datetime = field(default_factory=datetime.now)
    source_model: str = ""  # Which ML model generated this
    entity_id: str = ""
    signal_type: str = ""  # anomaly, prediction, pattern, risk
    
    # Scores and confidence
    anomaly_score: float = 0.0  # 0.0-1.0
    risk_score: float = 0.0     # 0.0-1.0
    confidence: float = 0.0     # 0.0-1.0
    
    # Context
    features: Dict[str, float] = field(default_factory=dict)
    evidence: Dict[str, Any] = field(default_factory=dict)
    prediction: Optional[str] = None
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "signal_id": self.signal_id,
            "timestamp": self.timestamp.isoformat(),
            "source_model": self.source_model,
            "entity_id": self.entity_id,
            "signal_type": self.signal_type,
            "anomaly_score": self.anomaly_score,
            "risk_score": self.risk_score,
            "confidence": self.confidence,
            "features": self.features,
            "evidence": self.evidence,
            "prediction": self.prediction,
            "tags": self.tags,
            "correlation_id": self.correlation_id,
        }
    
    @property
    def combined_threat_score(self) -> float:
        """Calculate combined threat score."""
        # Weighted combination of anomaly and risk scores
        base_score = (self.anomaly_score * 0.4 + self.risk_score * 0.6)
        # Adjust by confidence
        return base_score * (0.5 + self.confidence * 0.5)


@dataclass
class EnforcementAction:
    """An enforcement action triggered by ML signals."""
    
    action_id: str = field(default_factory=lambda: f"enf_{uuid.uuid4().hex[:12]}")
    created_at: datetime = field(default_factory=datetime.now)
    entity_id: str = ""
    tier: EnforcementTier = EnforcementTier.OBSERVE
    state: EnforcementState = EnforcementState.PENDING
    
    # Trigger information
    trigger_signals: List[str] = field(default_factory=list)  # Signal IDs
    trigger_score: float = 0.0
    trigger_reason: str = ""
    
    # Timing
    activated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    last_evaluation: Optional[datetime] = None
    
    # Self-healing configuration
    healing_strategy: HealingStrategy = HealingStrategy.AUTO_EXPIRE
    resolution_criteria: ThreatResolutionCriteria = ThreatResolutionCriteria.TIME_BASED
    resolution_conditions: Dict[str, Any] = field(default_factory=dict)
    
    # State tracking
    state_before: Dict[str, Any] = field(default_factory=dict)
    state_during: Dict[str, Any] = field(default_factory=dict)
    escalation_count: int = 0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "action_id": self.action_id,
            "created_at": self.created_at.isoformat(),
            "entity_id": self.entity_id,
            "tier": self.tier.name,
            "state": self.state.name,
            "trigger_signals": self.trigger_signals,
            "trigger_score": self.trigger_score,
            "trigger_reason": self.trigger_reason,
            "activated_at": self.activated_at.isoformat() if self.activated_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "healing_strategy": self.healing_strategy.name,
            "resolution_criteria": self.resolution_criteria.name,
            "escalation_count": self.escalation_count,
        }


@dataclass
class HealingRecord:
    """Record of a self-healing operation."""
    
    record_id: str = field(default_factory=lambda: f"heal_{uuid.uuid4().hex[:12]}")
    action_id: str = ""
    entity_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Healing details
    strategy_used: HealingStrategy = HealingStrategy.AUTO_EXPIRE
    previous_tier: EnforcementTier = EnforcementTier.OBSERVE
    new_tier: Optional[EnforcementTier] = None  # None if fully resolved
    
    # Resolution
    resolution_reason: str = ""
    resolution_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Rollback information
    rollback_performed: bool = False
    rollback_details: Dict[str, Any] = field(default_factory=dict)
    
    # Success
    success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "record_id": self.record_id,
            "action_id": self.action_id,
            "entity_id": self.entity_id,
            "timestamp": self.timestamp.isoformat(),
            "strategy_used": self.strategy_used.name,
            "previous_tier": self.previous_tier.name,
            "new_tier": self.new_tier.name if self.new_tier else None,
            "resolution_reason": self.resolution_reason,
            "rollback_performed": self.rollback_performed,
            "success": self.success,
            "error_message": self.error_message,
        }


@dataclass
class LoopMetrics:
    """Metrics for the ML enforcement loop."""
    
    signals_received: int = 0
    signals_processed: int = 0
    enforcements_triggered: int = 0
    enforcements_active: int = 0
    escalations: int = 0
    de_escalations: int = 0
    healings_performed: int = 0
    healings_successful: int = 0
    false_positives: int = 0  # Enforcements that were later deemed unnecessary
    
    # Timing metrics
    avg_signal_to_enforcement_ms: float = 0.0
    avg_healing_time_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "signals_received": self.signals_received,
            "signals_processed": self.signals_processed,
            "enforcements_triggered": self.enforcements_triggered,
            "enforcements_active": self.enforcements_active,
            "escalations": self.escalations,
            "de_escalations": self.de_escalations,
            "healings_performed": self.healings_performed,
            "healings_successful": self.healings_successful,
            "false_positives": self.false_positives,
            "avg_signal_to_enforcement_ms": self.avg_signal_to_enforcement_ms,
            "avg_healing_time_seconds": self.avg_healing_time_seconds,
        }


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class EnforcementLoopConfig:
    """Configuration for the ML enforcement loop."""
    
    # Thresholds for triggering enforcement tiers
    tier_thresholds: Dict[EnforcementTier, float] = field(default_factory=lambda: {
        EnforcementTier.OBSERVE: 0.0,
        EnforcementTier.WARN: 0.3,
        EnforcementTier.THROTTLE: 0.5,
        EnforcementTier.RESTRICT: 0.65,
        EnforcementTier.BLOCK: 0.75,
        EnforcementTier.QUARANTINE: 0.85,
        EnforcementTier.REVOKE: 0.95,
    })
    
    # Default durations for each tier
    tier_durations: Dict[EnforcementTier, timedelta] = field(default_factory=lambda: {
        EnforcementTier.OBSERVE: timedelta(minutes=5),
        EnforcementTier.WARN: timedelta(minutes=15),
        EnforcementTier.THROTTLE: timedelta(minutes=30),
        EnforcementTier.RESTRICT: timedelta(hours=1),
        EnforcementTier.BLOCK: timedelta(hours=4),
        EnforcementTier.QUARANTINE: timedelta(hours=24),
        EnforcementTier.REVOKE: timedelta(days=30),  # Long duration, manual review recommended
    })
    
    # Escalation settings
    escalation_threshold: float = 0.1  # Score increase that triggers escalation
    max_escalations: int = 3
    escalation_cooldown: timedelta = timedelta(minutes=5)
    
    # De-escalation settings
    de_escalation_threshold: float = 0.15  # Score decrease for de-escalation
    min_time_for_de_escalation: timedelta = timedelta(minutes=10)
    
    # Self-healing settings
    default_healing_strategy: HealingStrategy = HealingStrategy.GRADUAL_RELEASE
    healing_check_interval: timedelta = timedelta(minutes=1)
    max_healing_attempts: int = 3
    
    # Signal aggregation
    signal_aggregation_window: timedelta = timedelta(seconds=30)
    min_signals_for_enforcement: int = 1
    
    # Feature flags
    enable_auto_escalation: bool = True
    enable_auto_de_escalation: bool = True
    enable_auto_healing: bool = True
    enable_rollback: bool = True
    
    # Confidence requirements
    min_confidence_for_enforcement: float = 0.6
    min_confidence_for_revoke: float = 0.85


# =============================================================================
# Signal Processing
# =============================================================================

class SignalAggregator:
    """Aggregates ML signals for an entity within a time window."""
    
    def __init__(
        self,
        aggregation_window: timedelta = timedelta(seconds=30)
    ):
        self.aggregation_window = aggregation_window
        self.signals: Dict[str, List[MLSignal]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def add_signal(self, signal: MLSignal) -> None:
        """Add a signal to the aggregator."""
        with self._lock:
            self._cleanup_old_signals(signal.entity_id)
            self.signals[signal.entity_id].append(signal)
    
    def _cleanup_old_signals(self, entity_id: str) -> None:
        """Remove signals outside the aggregation window."""
        cutoff = datetime.now() - self.aggregation_window
        self.signals[entity_id] = [
            s for s in self.signals[entity_id]
            if s.timestamp > cutoff
        ]
    
    def get_aggregated_score(self, entity_id: str) -> Tuple[float, float, int]:
        """
        Get aggregated threat score for an entity.
        
        Returns: (aggregated_score, max_confidence, signal_count)
        """
        with self._lock:
            self._cleanup_old_signals(entity_id)
            signals = self.signals[entity_id]
            
            if not signals:
                return 0.0, 0.0, 0
            
            # Calculate weighted average score
            total_weight = 0.0
            weighted_sum = 0.0
            max_confidence = 0.0
            
            for signal in signals:
                weight = signal.confidence
                weighted_sum += signal.combined_threat_score * weight
                total_weight += weight
                max_confidence = max(max_confidence, signal.confidence)
            
            if total_weight > 0:
                aggregated_score = weighted_sum / total_weight
            else:
                aggregated_score = sum(
                    s.combined_threat_score for s in signals
                ) / len(signals)
            
            return aggregated_score, max_confidence, len(signals)
    
    def get_recent_signals(self, entity_id: str) -> List[MLSignal]:
        """Get recent signals for an entity."""
        with self._lock:
            self._cleanup_old_signals(entity_id)
            return self.signals[entity_id].copy()
    
    def clear_entity(self, entity_id: str) -> None:
        """Clear all signals for an entity."""
        with self._lock:
            if entity_id in self.signals:
                del self.signals[entity_id]


class TierResolver:
    """Resolves ML signals to enforcement tiers."""
    
    def __init__(self, config: EnforcementLoopConfig):
        self.config = config
    
    def resolve_tier(
        self,
        aggregated_score: float,
        confidence: float,
        current_tier: Optional[EnforcementTier] = None
    ) -> Tuple[EnforcementTier, str]:
        """
        Resolve aggregated score to an enforcement tier.
        
        Returns: (tier, reason)
        """
        # Check confidence threshold
        if confidence < self.config.min_confidence_for_enforcement:
            return EnforcementTier.OBSERVE, "Confidence below threshold"
        
        # Special check for REVOKE tier
        if aggregated_score >= self.config.tier_thresholds[EnforcementTier.REVOKE]:
            if confidence >= self.config.min_confidence_for_revoke:
                return EnforcementTier.REVOKE, f"Critical threat score: {aggregated_score:.3f}"
        
        # Find appropriate tier based on thresholds
        resolved_tier = EnforcementTier.OBSERVE
        
        for tier in sorted(self.config.tier_thresholds.keys(), key=lambda t: t.value, reverse=True):
            if aggregated_score >= self.config.tier_thresholds[tier]:
                # Skip REVOKE if confidence insufficient
                if tier == EnforcementTier.REVOKE and confidence < self.config.min_confidence_for_revoke:
                    continue
                resolved_tier = tier
                break
        
        reason = f"Score {aggregated_score:.3f} maps to {resolved_tier.name}"
        
        # Consider current tier for hysteresis
        if current_tier:
            score_diff = aggregated_score - self.config.tier_thresholds.get(current_tier, 0)
            if abs(score_diff) < 0.05:  # Within hysteresis band
                reason = f"Maintaining {current_tier.name} (hysteresis)"
                return current_tier, reason
        
        return resolved_tier, reason


# =============================================================================
# Enforcement Execution
# =============================================================================

class EnforcementExecutor(ABC):
    """Abstract base for enforcement executors."""
    
    @abstractmethod
    async def execute(
        self,
        action: EnforcementAction,
        tier: EnforcementTier
    ) -> bool:
        """Execute enforcement at the specified tier."""
        pass
    
    @abstractmethod
    async def rollback(
        self,
        action: EnforcementAction
    ) -> bool:
        """Rollback an enforcement action."""
        pass
    
    @abstractmethod
    async def modify(
        self,
        action: EnforcementAction,
        new_tier: EnforcementTier
    ) -> bool:
        """Modify enforcement to a new tier (escalate/de-escalate)."""
        pass


class DefaultEnforcementExecutor(EnforcementExecutor):
    """Default implementation of enforcement executor."""
    
    def __init__(self):
        self.active_enforcements: Dict[str, EnforcementAction] = {}
        self.tier_handlers: Dict[EnforcementTier, List[Callable]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def register_tier_handler(
        self,
        tier: EnforcementTier,
        handler: Callable[[EnforcementAction], bool]
    ) -> None:
        """Register a handler for a specific tier."""
        self.tier_handlers[tier].append(handler)
    
    async def execute(
        self,
        action: EnforcementAction,
        tier: EnforcementTier
    ) -> bool:
        """Execute enforcement at the specified tier."""
        with self._lock:
            self.active_enforcements[action.action_id] = action
        
        action.tier = tier
        action.state = EnforcementState.ACTIVE
        action.activated_at = datetime.now()
        
        # Execute tier-specific handlers
        handlers = self.tier_handlers.get(tier, [])
        success = True
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(action)
                else:
                    result = handler(action)
                
                if not result:
                    success = False
            except Exception as e:
                logger.error(f"Tier handler error for {tier.name}: {e}")
                success = False
        
        if not success:
            action.state = EnforcementState.FAILED
        
        logger.info(
            f"Enforcement {action.action_id} executed at tier {tier.name} "
            f"for entity {action.entity_id}: {'success' if success else 'failed'}"
        )
        
        return success
    
    async def rollback(self, action: EnforcementAction) -> bool:
        """Rollback an enforcement action."""
        with self._lock:
            if action.action_id in self.active_enforcements:
                del self.active_enforcements[action.action_id]
        
        action.state = EnforcementState.RESOLVED
        
        logger.info(
            f"Enforcement {action.action_id} rolled back for entity {action.entity_id}"
        )
        
        return True
    
    async def modify(
        self,
        action: EnforcementAction,
        new_tier: EnforcementTier
    ) -> bool:
        """Modify enforcement to a new tier."""
        old_tier = action.tier
        
        # Execute new tier handlers
        success = await self.execute(action, new_tier)
        
        if success:
            logger.info(
                f"Enforcement {action.action_id} modified: "
                f"{old_tier.name} -> {new_tier.name}"
            )
        
        return success
    
    def get_active_for_entity(self, entity_id: str) -> List[EnforcementAction]:
        """Get active enforcements for an entity."""
        with self._lock:
            return [
                action for action in self.active_enforcements.values()
                if action.entity_id == entity_id
            ]


# =============================================================================
# Self-Healing System
# =============================================================================

class ResolutionEvaluator:
    """Evaluates whether a threat has been resolved."""
    
    def __init__(self, config: EnforcementLoopConfig):
        self.config = config
    
    async def evaluate(
        self,
        action: EnforcementAction,
        current_score: float,
        signal_count: int
    ) -> Tuple[bool, str]:
        """
        Evaluate if the threat is resolved.
        
        Returns: (is_resolved, reason)
        """
        criteria = action.resolution_criteria
        conditions = action.resolution_conditions
        
        if criteria == ThreatResolutionCriteria.TIME_BASED:
            return await self._evaluate_time_based(action, conditions)
        
        elif criteria == ThreatResolutionCriteria.METRIC_BASED:
            return await self._evaluate_metric_based(
                action, current_score, conditions
            )
        
        elif criteria == ThreatResolutionCriteria.BEHAVIORAL:
            return await self._evaluate_behavioral(
                action, current_score, signal_count, conditions
            )
        
        elif criteria == ThreatResolutionCriteria.EXTERNAL_SIGNAL:
            return await self._evaluate_external(action, conditions)
        
        elif criteria == ThreatResolutionCriteria.COMBINED:
            return await self._evaluate_combined(
                action, current_score, signal_count, conditions
            )
        
        return False, "Unknown criteria"
    
    async def _evaluate_time_based(
        self,
        action: EnforcementAction,
        conditions: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Evaluate time-based resolution."""
        if action.expires_at and datetime.now() >= action.expires_at:
            return True, "Enforcement duration expired"
        
        min_duration = conditions.get("min_duration_seconds", 60)
        if action.activated_at:
            elapsed = (datetime.now() - action.activated_at).total_seconds()
            if elapsed >= min_duration:
                # Also check if no new signals
                quiet_period = conditions.get("quiet_period_seconds", 30)
                if action.last_evaluation:
                    since_eval = (datetime.now() - action.last_evaluation).total_seconds()
                    if since_eval >= quiet_period:
                        return True, f"Quiet period ({quiet_period}s) with no new threats"
        
        return False, "Time-based criteria not met"
    
    async def _evaluate_metric_based(
        self,
        action: EnforcementAction,
        current_score: float,
        conditions: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Evaluate metric-based resolution."""
        threshold = conditions.get("score_threshold", 0.3)
        
        if current_score < threshold:
            return True, f"Score ({current_score:.3f}) below threshold ({threshold})"
        
        # Check for significant score drop
        score_drop = action.trigger_score - current_score
        drop_threshold = conditions.get("score_drop_threshold", 0.3)
        
        if score_drop >= drop_threshold:
            return True, f"Significant score drop: {score_drop:.3f}"
        
        return False, f"Current score ({current_score:.3f}) still elevated"
    
    async def _evaluate_behavioral(
        self,
        action: EnforcementAction,
        current_score: float,
        signal_count: int,
        conditions: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Evaluate behavioral resolution."""
        # Check signal frequency
        max_signals = conditions.get("max_signals_in_window", 2)
        if signal_count <= max_signals:
            # Also check score
            score_threshold = conditions.get("score_threshold", 0.4)
            if current_score < score_threshold:
                return True, f"Behavior normalized: {signal_count} signals, score {current_score:.3f}"
        
        return False, f"Behavioral anomaly continues: {signal_count} signals"
    
    async def _evaluate_external(
        self,
        action: EnforcementAction,
        conditions: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Evaluate external signal resolution."""
        # Check for external resolution flag
        if conditions.get("resolved_externally"):
            return True, conditions.get("resolution_source", "External system")
        
        return False, "Awaiting external resolution signal"
    
    async def _evaluate_combined(
        self,
        action: EnforcementAction,
        current_score: float,
        signal_count: int,
        conditions: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Evaluate combined criteria resolution."""
        required_criteria = conditions.get("required_criteria", [])
        met_criteria = []
        
        # Check time
        if "time" in required_criteria:
            time_met, _ = await self._evaluate_time_based(
                action, conditions.get("time_conditions", {})
            )
            if time_met:
                met_criteria.append("time")
        
        # Check metrics
        if "metrics" in required_criteria:
            metric_met, _ = await self._evaluate_metric_based(
                action, current_score, conditions.get("metric_conditions", {})
            )
            if metric_met:
                met_criteria.append("metrics")
        
        # Check behavior
        if "behavior" in required_criteria:
            behavior_met, _ = await self._evaluate_behavioral(
                action, current_score, signal_count,
                conditions.get("behavior_conditions", {})
            )
            if behavior_met:
                met_criteria.append("behavior")
        
        # Determine if enough criteria are met
        min_required = conditions.get("min_criteria_count", len(required_criteria))
        
        if len(met_criteria) >= min_required:
            return True, f"Combined criteria met: {', '.join(met_criteria)}"
        
        return False, f"Combined criteria not met: {len(met_criteria)}/{min_required}"


class SelfHealingEngine:
    """Executes self-healing operations."""
    
    def __init__(
        self,
        config: EnforcementLoopConfig,
        executor: EnforcementExecutor
    ):
        self.config = config
        self.executor = executor
        self.resolution_evaluator = ResolutionEvaluator(config)
        self.healing_history: List[HealingRecord] = []
        self._lock = threading.Lock()
    
    async def attempt_healing(
        self,
        action: EnforcementAction,
        current_score: float,
        signal_count: int
    ) -> Optional[HealingRecord]:
        """
        Attempt to heal/resolve an enforcement action.
        
        Returns: HealingRecord if healing was performed, None otherwise
        """
        # Check if healing is appropriate
        is_resolved, resolution_reason = await self.resolution_evaluator.evaluate(
            action, current_score, signal_count
        )
        
        if not is_resolved:
            # Check for de-escalation opportunity
            if self.config.enable_auto_de_escalation:
                return await self._attempt_de_escalation(
                    action, current_score, signal_count
                )
            return None
        
        # Perform healing based on strategy
        strategy = action.healing_strategy
        
        if strategy == HealingStrategy.AUTO_EXPIRE:
            return await self._heal_auto_expire(action, resolution_reason)
        
        elif strategy == HealingStrategy.GRADUAL_RELEASE:
            return await self._heal_gradual_release(
                action, current_score, resolution_reason
            )
        
        elif strategy == HealingStrategy.IMMEDIATE_RELEASE:
            return await self._heal_immediate_release(action, resolution_reason)
        
        elif strategy == HealingStrategy.CONDITIONAL:
            return await self._heal_conditional(
                action, current_score, signal_count, resolution_reason
            )
        
        elif strategy == HealingStrategy.MANUAL_ONLY:
            logger.info(
                f"Action {action.action_id} requires manual healing. "
                f"Resolution: {resolution_reason}"
            )
            return None
        
        return None
    
    async def _attempt_de_escalation(
        self,
        action: EnforcementAction,
        current_score: float,
        signal_count: int
    ) -> Optional[HealingRecord]:
        """Attempt to de-escalate enforcement tier."""
        # Check minimum time
        if action.activated_at:
            elapsed = datetime.now() - action.activated_at
            if elapsed < self.config.min_time_for_de_escalation:
                return None
        
        # Check score improvement
        score_improvement = action.trigger_score - current_score
        if score_improvement < self.config.de_escalation_threshold:
            return None
        
        # Get lower tier
        new_tier = TIER_DEESCALATION.get(action.tier)
        if not new_tier or new_tier == action.tier:
            return None
        
        # Perform de-escalation
        record = HealingRecord(
            action_id=action.action_id,
            entity_id=action.entity_id,
            strategy_used=HealingStrategy.GRADUAL_RELEASE,
            previous_tier=action.tier,
            new_tier=new_tier,
            resolution_reason=f"Score improved by {score_improvement:.3f}",
            resolution_metrics={
                "original_score": action.trigger_score,
                "current_score": current_score,
                "improvement": score_improvement,
            }
        )
        
        try:
            success = await self.executor.modify(action, new_tier)
            record.success = success
            
            if success:
                action.state = EnforcementState.HEALING
                logger.info(
                    f"De-escalated {action.action_id}: "
                    f"{action.tier.name} -> {new_tier.name}"
                )
        except Exception as e:
            record.success = False
            record.error_message = str(e)
            logger.error(f"De-escalation failed: {e}")
        
        with self._lock:
            self.healing_history.append(record)
        
        return record
    
    async def _heal_auto_expire(
        self,
        action: EnforcementAction,
        reason: str
    ) -> HealingRecord:
        """Heal by letting enforcement expire."""
        record = HealingRecord(
            action_id=action.action_id,
            entity_id=action.entity_id,
            strategy_used=HealingStrategy.AUTO_EXPIRE,
            previous_tier=action.tier,
            new_tier=None,
            resolution_reason=reason,
        )
        
        try:
            success = await self.executor.rollback(action)
            record.success = success
            record.rollback_performed = True
            
            if success:
                action.state = EnforcementState.RESOLVED
                logger.info(
                    f"Auto-expired enforcement {action.action_id}: {reason}"
                )
        except Exception as e:
            record.success = False
            record.error_message = str(e)
        
        with self._lock:
            self.healing_history.append(record)
        
        return record
    
    async def _heal_gradual_release(
        self,
        action: EnforcementAction,
        current_score: float,
        reason: str
    ) -> HealingRecord:
        """Heal by gradually releasing restrictions."""
        new_tier = TIER_DEESCALATION.get(action.tier)
        
        record = HealingRecord(
            action_id=action.action_id,
            entity_id=action.entity_id,
            strategy_used=HealingStrategy.GRADUAL_RELEASE,
            previous_tier=action.tier,
            new_tier=new_tier,
            resolution_reason=reason,
            resolution_metrics={"current_score": current_score},
        )
        
        try:
            if new_tier and new_tier != EnforcementTier.OBSERVE:
                # Step down one tier
                success = await self.executor.modify(action, new_tier)
                record.new_tier = new_tier
            else:
                # Fully release
                success = await self.executor.rollback(action)
                record.new_tier = None
                record.rollback_performed = True
            
            record.success = success
            
            if success:
                if record.new_tier:
                    action.state = EnforcementState.HEALING
                else:
                    action.state = EnforcementState.RESOLVED
                
                logger.info(
                    f"Gradual release for {action.action_id}: "
                    f"{action.tier.name} -> {new_tier.name if new_tier else 'RESOLVED'}"
                )
        except Exception as e:
            record.success = False
            record.error_message = str(e)
        
        with self._lock:
            self.healing_history.append(record)
        
        return record
    
    async def _heal_immediate_release(
        self,
        action: EnforcementAction,
        reason: str
    ) -> HealingRecord:
        """Heal by immediately releasing all restrictions."""
        record = HealingRecord(
            action_id=action.action_id,
            entity_id=action.entity_id,
            strategy_used=HealingStrategy.IMMEDIATE_RELEASE,
            previous_tier=action.tier,
            new_tier=None,
            resolution_reason=reason,
            rollback_performed=True,
        )
        
        try:
            success = await self.executor.rollback(action)
            record.success = success
            
            if success:
                action.state = EnforcementState.RESOLVED
                logger.info(
                    f"Immediate release for {action.action_id}: {reason}"
                )
        except Exception as e:
            record.success = False
            record.error_message = str(e)
        
        with self._lock:
            self.healing_history.append(record)
        
        return record
    
    async def _heal_conditional(
        self,
        action: EnforcementAction,
        current_score: float,
        signal_count: int,
        reason: str
    ) -> HealingRecord:
        """Heal based on conditions."""
        conditions = action.resolution_conditions
        
        # Determine release level based on conditions
        if current_score < 0.2 and signal_count == 0:
            # Full release
            return await self._heal_immediate_release(action, reason)
        elif current_score < 0.4:
            # Gradual release
            return await self._heal_gradual_release(action, current_score, reason)
        else:
            # Just de-escalate one tier
            return await self._attempt_de_escalation(
                action, current_score, signal_count
            ) or HealingRecord(
                action_id=action.action_id,
                entity_id=action.entity_id,
                strategy_used=HealingStrategy.CONDITIONAL,
                previous_tier=action.tier,
                new_tier=action.tier,
                resolution_reason="Conditions not favorable for release",
                success=True,
            )
    
    def get_healing_history(
        self,
        entity_id: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> List[HealingRecord]:
        """Get healing history."""
        with self._lock:
            records = self.healing_history.copy()
        
        if entity_id:
            records = [r for r in records if r.entity_id == entity_id]
        
        if since:
            records = [r for r in records if r.timestamp >= since]
        
        return records


# =============================================================================
# Main Enforcement Loop
# =============================================================================

class MLEnforcementLoop:
    """
    Complete ML-driven Enforcement and Self-Healing Loop.
    
    This is the main class that orchestrates:
    1. ML signal reception and aggregation
    2. Automated enforcement tier resolution
    3. Enforcement execution
    4. Continuous monitoring
    5. Self-healing and recovery
    """
    
    def __init__(
        self,
        config: Optional[EnforcementLoopConfig] = None,
        executor: Optional[EnforcementExecutor] = None
    ):
        self.config = config or EnforcementLoopConfig()
        self.executor = executor or DefaultEnforcementExecutor()
        
        # Core components
        self.signal_aggregator = SignalAggregator(
            aggregation_window=self.config.signal_aggregation_window
        )
        self.tier_resolver = TierResolver(self.config)
        self.healing_engine = SelfHealingEngine(self.config, self.executor)
        
        # State tracking
        self.active_actions: Dict[str, EnforcementAction] = {}
        self.entity_actions: Dict[str, List[str]] = defaultdict(list)
        self.metrics = LoopMetrics()
        
        # Control
        self._running = False
        self._monitoring_task: Optional[asyncio.Task] = None
        self._lock = threading.Lock()
        
        # Callbacks
        self._signal_callbacks: List[Callable[[MLSignal], None]] = []
        self._enforcement_callbacks: List[Callable[[EnforcementAction], None]] = []
        self._healing_callbacks: List[Callable[[HealingRecord], None]] = []
    
    # -------------------------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------------------------
    
    async def start(self) -> None:
        """Start the enforcement loop."""
        if self._running:
            return
        
        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("ML Enforcement Loop started")
    
    async def stop(self) -> None:
        """Stop the enforcement loop."""
        self._running = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("ML Enforcement Loop stopped")
    
    # -------------------------------------------------------------------------
    # Signal Processing
    # -------------------------------------------------------------------------
    
    async def process_signal(self, signal: MLSignal) -> Optional[EnforcementAction]:
        """
        Process an ML signal through the enforcement loop.
        
        This is the main entry point for ML signals.
        """
        self.metrics.signals_received += 1
        
        # Notify callbacks
        for callback in self._signal_callbacks:
            try:
                callback(signal)
            except Exception as e:
                logger.error(f"Signal callback error: {e}")
        
        # Add to aggregator
        self.signal_aggregator.add_signal(signal)
        
        # Get aggregated score
        aggregated_score, confidence, signal_count = \
            self.signal_aggregator.get_aggregated_score(signal.entity_id)
        
        # Check if we have enough signals
        if signal_count < self.config.min_signals_for_enforcement:
            return None
        
        self.metrics.signals_processed += 1
        
        # Check for existing enforcement
        existing_action = self._get_active_action(signal.entity_id)
        
        if existing_action:
            # Handle existing enforcement
            return await self._handle_existing_enforcement(
                existing_action, signal, aggregated_score, confidence
            )
        else:
            # Potentially create new enforcement
            return await self._handle_new_signal(
                signal, aggregated_score, confidence, signal_count
            )
    
    async def _handle_new_signal(
        self,
        signal: MLSignal,
        aggregated_score: float,
        confidence: float,
        signal_count: int
    ) -> Optional[EnforcementAction]:
        """Handle a signal when no enforcement exists for the entity."""
        # Resolve to tier
        tier, reason = self.tier_resolver.resolve_tier(
            aggregated_score, confidence
        )
        
        # Only create enforcement if tier is above OBSERVE
        if tier == EnforcementTier.OBSERVE:
            return None
        
        # Create enforcement action
        action = EnforcementAction(
            entity_id=signal.entity_id,
            tier=tier,
            trigger_signals=[signal.signal_id],
            trigger_score=aggregated_score,
            trigger_reason=reason,
            expires_at=datetime.now() + self.config.tier_durations.get(
                tier, timedelta(hours=1)
            ),
            healing_strategy=self.config.default_healing_strategy,
            resolution_criteria=ThreatResolutionCriteria.BEHAVIORAL,
            resolution_conditions={
                "score_threshold": self.config.tier_thresholds.get(
                    EnforcementTier.WARN, 0.3
                ),
                "max_signals_in_window": 2,
            },
            state_before=signal.evidence.copy(),
        )
        
        # Execute enforcement
        success = await self.executor.execute(action, tier)
        
        if success:
            self._register_action(action)
            self.metrics.enforcements_triggered += 1
            self.metrics.enforcements_active += 1
            
            # Notify callbacks
            for callback in self._enforcement_callbacks:
                try:
                    callback(action)
                except Exception as e:
                    logger.error(f"Enforcement callback error: {e}")
            
            logger.info(
                f"New enforcement triggered: {action.action_id} "
                f"tier={tier.name} entity={signal.entity_id} "
                f"score={aggregated_score:.3f}"
            )
            
            return action
        
        return None
    
    async def _handle_existing_enforcement(
        self,
        action: EnforcementAction,
        signal: MLSignal,
        aggregated_score: float,
        confidence: float
    ) -> Optional[EnforcementAction]:
        """Handle a signal when enforcement already exists."""
        # Update action with new signal
        action.trigger_signals.append(signal.signal_id)
        action.last_evaluation = datetime.now()
        
        # Resolve new tier
        new_tier, reason = self.tier_resolver.resolve_tier(
            aggregated_score, confidence, action.tier
        )
        
        # Check for escalation
        if new_tier.value > action.tier.value:
            if self.config.enable_auto_escalation:
                if action.escalation_count < self.config.max_escalations:
                    await self._escalate_action(action, new_tier, reason)
        
        # Check for de-escalation (handled by healing engine)
        elif new_tier.value < action.tier.value:
            action.trigger_score = aggregated_score  # Update for healing evaluation
        
        return action
    
    async def _escalate_action(
        self,
        action: EnforcementAction,
        new_tier: EnforcementTier,
        reason: str
    ) -> bool:
        """Escalate an enforcement action."""
        old_tier = action.tier
        
        success = await self.executor.modify(action, new_tier)
        
        if success:
            action.escalation_count += 1
            action.state = EnforcementState.ESCALATED
            
            # Extend expiration
            action.expires_at = datetime.now() + self.config.tier_durations.get(
                new_tier, timedelta(hours=1)
            )
            
            self.metrics.escalations += 1
            
            logger.info(
                f"Escalated {action.action_id}: {old_tier.name} -> {new_tier.name}. "
                f"Reason: {reason}"
            )
        
        return success
    
    # -------------------------------------------------------------------------
    # Monitoring Loop
    # -------------------------------------------------------------------------
    
    async def _monitoring_loop(self) -> None:
        """Background loop for monitoring and healing."""
        while self._running:
            try:
                await self._check_all_actions()
                await asyncio.sleep(
                    self.config.healing_check_interval.total_seconds()
                )
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
    
    async def _check_all_actions(self) -> None:
        """Check all active actions for healing opportunities."""
        if not self.config.enable_auto_healing:
            return
        
        with self._lock:
            actions = list(self.active_actions.values())
        
        for action in actions:
            if action.state in [EnforcementState.RESOLVED, EnforcementState.FAILED]:
                continue
            
            # Get current threat level
            score, confidence, signal_count = \
                self.signal_aggregator.get_aggregated_score(action.entity_id)
            
            # Attempt healing
            record = await self.healing_engine.attempt_healing(
                action, score, signal_count
            )
            
            if record:
                self.metrics.healings_performed += 1
                
                if record.success:
                    self.metrics.healings_successful += 1
                    
                    if record.new_tier is None:
                        # Fully resolved
                        self._unregister_action(action)
                        self.metrics.enforcements_active -= 1
                    else:
                        # De-escalated
                        self.metrics.de_escalations += 1
                
                # Notify callbacks
                for callback in self._healing_callbacks:
                    try:
                        callback(record)
                    except Exception as e:
                        logger.error(f"Healing callback error: {e}")
    
    # -------------------------------------------------------------------------
    # Action Management
    # -------------------------------------------------------------------------
    
    def _register_action(self, action: EnforcementAction) -> None:
        """Register an active action."""
        with self._lock:
            self.active_actions[action.action_id] = action
            self.entity_actions[action.entity_id].append(action.action_id)
    
    def _unregister_action(self, action: EnforcementAction) -> None:
        """Unregister an action."""
        with self._lock:
            if action.action_id in self.active_actions:
                del self.active_actions[action.action_id]
            
            if action.entity_id in self.entity_actions:
                self.entity_actions[action.entity_id] = [
                    aid for aid in self.entity_actions[action.entity_id]
                    if aid != action.action_id
                ]
    
    def _get_active_action(self, entity_id: str) -> Optional[EnforcementAction]:
        """Get active action for an entity."""
        with self._lock:
            action_ids = self.entity_actions.get(entity_id, [])
            for action_id in action_ids:
                action = self.active_actions.get(action_id)
                if action and action.state not in [
                    EnforcementState.RESOLVED, EnforcementState.FAILED
                ]:
                    return action
        return None
    
    # -------------------------------------------------------------------------
    # Manual Controls
    # -------------------------------------------------------------------------
    
    async def force_heal(
        self,
        entity_id: str,
        reason: str = "Manual intervention"
    ) -> Optional[HealingRecord]:
        """Force healing for an entity."""
        action = self._get_active_action(entity_id)
        
        if not action:
            return None
        
        record = HealingRecord(
            action_id=action.action_id,
            entity_id=entity_id,
            strategy_used=HealingStrategy.IMMEDIATE_RELEASE,
            previous_tier=action.tier,
            new_tier=None,
            resolution_reason=f"Manual: {reason}",
            rollback_performed=True,
        )
        
        try:
            success = await self.executor.rollback(action)
            record.success = success
            
            if success:
                action.state = EnforcementState.RESOLVED
                self._unregister_action(action)
                self.metrics.enforcements_active -= 1
                self.metrics.healings_performed += 1
                self.metrics.healings_successful += 1
                
                logger.info(f"Force healed entity {entity_id}: {reason}")
        except Exception as e:
            record.success = False
            record.error_message = str(e)
        
        return record
    
    async def force_enforce(
        self,
        entity_id: str,
        tier: EnforcementTier,
        reason: str,
        duration: Optional[timedelta] = None
    ) -> EnforcementAction:
        """Force enforcement for an entity."""
        action = EnforcementAction(
            entity_id=entity_id,
            tier=tier,
            trigger_signals=[],
            trigger_score=1.0,
            trigger_reason=f"Manual: {reason}",
            expires_at=datetime.now() + (
                duration or self.config.tier_durations.get(tier, timedelta(hours=1))
            ),
            healing_strategy=HealingStrategy.MANUAL_ONLY,
            resolution_criteria=ThreatResolutionCriteria.EXTERNAL_SIGNAL,
        )
        
        success = await self.executor.execute(action, tier)
        
        if success:
            self._register_action(action)
            self.metrics.enforcements_triggered += 1
            self.metrics.enforcements_active += 1
            
            logger.info(
                f"Force enforced {tier.name} on entity {entity_id}: {reason}"
            )
        
        return action
    
    def mark_false_positive(self, action_id: str) -> bool:
        """Mark an enforcement as a false positive."""
        with self._lock:
            if action_id in self.active_actions:
                self.metrics.false_positives += 1
                return True
        return False
    
    # -------------------------------------------------------------------------
    # Callbacks
    # -------------------------------------------------------------------------
    
    def on_signal(self, callback: Callable[[MLSignal], None]) -> None:
        """Register callback for signal events."""
        self._signal_callbacks.append(callback)
    
    def on_enforcement(self, callback: Callable[[EnforcementAction], None]) -> None:
        """Register callback for enforcement events."""
        self._enforcement_callbacks.append(callback)
    
    def on_healing(self, callback: Callable[[HealingRecord], None]) -> None:
        """Register callback for healing events."""
        self._healing_callbacks.append(callback)
    
    # -------------------------------------------------------------------------
    # Status and Metrics
    # -------------------------------------------------------------------------
    
    def get_status(self) -> Dict[str, Any]:
        """Get current loop status."""
        with self._lock:
            active_by_tier = defaultdict(int)
            for action in self.active_actions.values():
                active_by_tier[action.tier.name] += 1
        
        return {
            "running": self._running,
            "metrics": self.metrics.to_dict(),
            "active_enforcements": len(self.active_actions),
            "active_by_tier": dict(active_by_tier),
            "entities_enforced": len(self.entity_actions),
            "config": {
                "auto_escalation": self.config.enable_auto_escalation,
                "auto_de_escalation": self.config.enable_auto_de_escalation,
                "auto_healing": self.config.enable_auto_healing,
                "default_healing_strategy": self.config.default_healing_strategy.name,
            },
        }
    
    def get_entity_status(self, entity_id: str) -> Dict[str, Any]:
        """Get enforcement status for an entity."""
        action = self._get_active_action(entity_id)
        
        score, confidence, signal_count = \
            self.signal_aggregator.get_aggregated_score(entity_id)
        
        return {
            "entity_id": entity_id,
            "has_active_enforcement": action is not None,
            "current_action": action.to_dict() if action else None,
            "current_threat_score": score,
            "current_confidence": confidence,
            "recent_signal_count": signal_count,
            "healing_history": [
                r.to_dict() for r in 
                self.healing_engine.get_healing_history(entity_id)[-5:]
            ],
        }
    
    def get_active_actions(self) -> List[EnforcementAction]:
        """Get all active enforcement actions."""
        with self._lock:
            return list(self.active_actions.values())


# =============================================================================
# Factory Functions
# =============================================================================

def create_enforcement_loop(
    enable_auto_escalation: bool = True,
    enable_auto_healing: bool = True,
    default_healing_strategy: HealingStrategy = HealingStrategy.GRADUAL_RELEASE
) -> MLEnforcementLoop:
    """Create a configured ML enforcement loop."""
    config = EnforcementLoopConfig(
        enable_auto_escalation=enable_auto_escalation,
        enable_auto_de_escalation=enable_auto_healing,
        enable_auto_healing=enable_auto_healing,
        default_healing_strategy=default_healing_strategy,
    )
    return MLEnforcementLoop(config)


def create_ml_signal(
    entity_id: str,
    anomaly_score: float,
    risk_score: float,
    confidence: float,
    source_model: str = "unknown",
    signal_type: str = "anomaly",
    evidence: Optional[Dict[str, Any]] = None
) -> MLSignal:
    """Factory for creating ML signals."""
    return MLSignal(
        entity_id=entity_id,
        source_model=source_model,
        signal_type=signal_type,
        anomaly_score=max(0.0, min(1.0, anomaly_score)),
        risk_score=max(0.0, min(1.0, risk_score)),
        confidence=max(0.0, min(1.0, confidence)),
        evidence=evidence or {},
    )


# =============================================================================
# Integration with Defense Coordinator
# =============================================================================

class DefenseCoordinatorAdapter:
    """
    Adapter to integrate MLEnforcementLoop with DefenseCoordinator.
    
    Bridges the ML enforcement loop with the existing defense infrastructure.
    """
    
    def __init__(
        self,
        enforcement_loop: MLEnforcementLoop,
        coordinator: Optional[Any] = None  # DefenseCoordinator
    ):
        self.loop = enforcement_loop
        self.coordinator = coordinator
        
        # Register callbacks
        self.loop.on_enforcement(self._on_enforcement)
        self.loop.on_healing(self._on_healing)
    
    def _on_enforcement(self, action: EnforcementAction) -> None:
        """Handle enforcement event."""
        if self.coordinator:
            # Map to coordinator's response system
            logger.info(
                f"DefenseCoordinator notified of enforcement: {action.action_id}"
            )
    
    def _on_healing(self, record: HealingRecord) -> None:
        """Handle healing event."""
        if self.coordinator:
            # Notify coordinator of healing
            logger.info(
                f"DefenseCoordinator notified of healing: {record.record_id}"
            )
    
    async def process_threat_event(
        self,
        event: Dict[str, Any]
    ) -> Optional[EnforcementAction]:
        """
        Process a threat event from DefenseCoordinator.
        
        Converts coordinator events to ML signals.
        """
        signal = MLSignal(
            entity_id=event.get("entity_id", ""),
            source_model=event.get("source_system", "threat_response"),
            signal_type="threat",
            anomaly_score=event.get("severity", 0.5),
            risk_score=event.get("severity", 0.5),
            confidence=0.8,  # Default confidence from coordinator
            evidence=event.get("evidence", {}),
        )
        
        return await self.loop.process_signal(signal)
