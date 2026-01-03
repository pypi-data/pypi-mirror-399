# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Pricing Intents Layer - DEPRECATED

⚠️ DEPRECATION WARNING (Dec 2025):
This module has been moved to krl-premium-backend.
Import from: app.services.billing.pricing_intents

This stub remains for backward compatibility but will be removed in v2.0.
"""

from __future__ import annotations

import warnings
warnings.warn(
    "krl_data_connectors.core.billing.pricing_intents is deprecated. "
    "This module has moved to krl-premium-backend. "
    "Import from 'app.services.billing.pricing_intents' instead.",
    DeprecationWarning,
    stacklevel=2
)

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class PricingIntent(Enum):
    """Strategic pricing intents."""
    SUSTAIN = "sustain"      # Keep revenue steady
    EXPAND = "expand"        # Increase ARPA
    DEFEND = "defend"        # Reduce churn risk
    THROTTLE = "throttle"    # Discourage abuse
    NEUTRAL = "neutral"      # No change needed


class IntentConfidence(Enum):
    """Confidence level for intent determination."""
    HIGH = "high"        # >80% signal alignment
    MEDIUM = "medium"    # 50-80% signal alignment
    LOW = "low"          # <50% signal alignment
    UNCERTAIN = "uncertain"  # Conflicting signals


class IntentTrigger(Enum):
    """What triggered the intent determination."""
    # Expansion triggers
    USAGE_GROWTH = "usage_growth"
    FEATURE_DEMAND = "feature_demand"
    VALUE_REALIZATION = "value_realization"
    TIER_CEILING = "tier_ceiling"
    
    # Defense triggers
    USAGE_DECLINE = "usage_decline"
    ENGAGEMENT_DROP = "engagement_drop"
    PAYMENT_RISK = "payment_risk"
    COMPETITOR_SIGNAL = "competitor_signal"
    
    # Throttle triggers
    ABUSE_PATTERN = "abuse_pattern"
    EXCESSIVE_COST = "excessive_cost"
    POLICY_VIOLATION = "policy_violation"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    
    # Sustain triggers
    STABLE_USAGE = "stable_usage"
    HEALTHY_ENGAGEMENT = "healthy_engagement"
    ON_TIME_PAYMENTS = "on_time_payments"
    
    # Neutral triggers
    NEW_CUSTOMER = "new_customer"
    INSUFFICIENT_DATA = "insufficient_data"
    EVALUATION_PERIOD = "evaluation_period"


class IntentAction(Enum):
    """Recommended actions based on intent."""
    # Expand actions
    SUGGEST_UPGRADE = "suggest_upgrade"
    OFFER_ADDON = "offer_addon"
    INCREASE_LIMIT = "increase_limit"
    PREMIUM_OUTREACH = "premium_outreach"
    
    # Defend actions
    OFFER_DISCOUNT = "offer_discount"
    FREEZE_PRICING = "freeze_pricing"
    EXTEND_TRIAL = "extend_trial"
    SUCCESS_OUTREACH = "success_outreach"
    REDUCE_FRICTION = "reduce_friction"
    
    # Throttle actions
    APPLY_OVERAGE = "apply_overage"
    ENFORCE_LIMIT = "enforce_limit"
    RATE_LIMIT = "rate_limit"
    REQUIRE_UPGRADE = "require_upgrade"
    SUSPEND_FEATURE = "suspend_feature"
    
    # Sustain actions
    MAINTAIN_CURRENT = "maintain_current"
    SCHEDULE_REVIEW = "schedule_review"
    
    # Neutral actions
    OBSERVE = "observe"
    COLLECT_DATA = "collect_data"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class IntentSignal:
    """A signal contributing to intent determination."""
    signal_name: str
    signal_value: float  # Normalized 0-1
    weight: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def weighted_value(self) -> float:
        return self.signal_value * self.weight


@dataclass
class IntentResult:
    """Result of intent determination."""
    intent: PricingIntent
    confidence: IntentConfidence
    confidence_score: float  # 0-1
    
    # What drove this intent
    primary_trigger: IntentTrigger
    contributing_triggers: List[IntentTrigger] = field(default_factory=list)
    
    # Recommended actions
    recommended_actions: List[IntentAction] = field(default_factory=list)
    action_priority: int = 0  # Higher = more urgent
    
    # Context
    tenant_id: str = ""
    evaluated_at: datetime = field(default_factory=datetime.now)
    valid_until: Optional[datetime] = None
    
    # Signal breakdown
    signals_used: List[IntentSignal] = field(default_factory=list)
    
    # Economic impact estimate
    revenue_impact: Optional[Decimal] = None
    risk_delta: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent.value,
            "confidence": self.confidence.value,
            "confidence_score": self.confidence_score,
            "primary_trigger": self.primary_trigger.value,
            "contributing_triggers": [t.value for t in self.contributing_triggers],
            "recommended_actions": [a.value for a in self.recommended_actions],
            "action_priority": self.action_priority,
            "tenant_id": self.tenant_id,
            "evaluated_at": self.evaluated_at.isoformat(),
            "revenue_impact": str(self.revenue_impact) if self.revenue_impact else None,
            "risk_delta": self.risk_delta,
        }


@dataclass
class IntentPolicy:
    """Policy configuration for intent determination."""
    # Thresholds for expansion
    expansion_usage_growth_threshold: float = 0.15  # 15% MoM growth
    expansion_utilization_threshold: float = 0.75   # 75% of limits
    expansion_feature_gate_hits: int = 5            # Feature gate attempts
    
    # Thresholds for defense
    defense_usage_decline_threshold: float = -0.20  # 20% MoM decline
    defense_engagement_decay_days: int = 14         # Days of low engagement
    defense_payment_delay_days: int = 7             # Days payment overdue
    
    # Thresholds for throttle
    throttle_overage_threshold: float = 1.20        # 120% of limit
    throttle_violation_count: int = 3               # Violations to trigger
    throttle_cost_ratio_threshold: float = 2.0      # Cost > 2x revenue
    
    # Confidence thresholds
    high_confidence_threshold: float = 0.80
    medium_confidence_threshold: float = 0.50
    
    # Intent validity
    intent_validity_hours: int = 24
    
    # Action mapping
    intent_actions: Dict[PricingIntent, List[IntentAction]] = field(
        default_factory=lambda: {
            PricingIntent.EXPAND: [
                IntentAction.SUGGEST_UPGRADE,
                IntentAction.OFFER_ADDON,
                IntentAction.PREMIUM_OUTREACH,
            ],
            PricingIntent.DEFEND: [
                IntentAction.SUCCESS_OUTREACH,
                IntentAction.FREEZE_PRICING,
                IntentAction.OFFER_DISCOUNT,
            ],
            PricingIntent.THROTTLE: [
                IntentAction.APPLY_OVERAGE,
                IntentAction.ENFORCE_LIMIT,
                IntentAction.REQUIRE_UPGRADE,
            ],
            PricingIntent.SUSTAIN: [
                IntentAction.MAINTAIN_CURRENT,
                IntentAction.SCHEDULE_REVIEW,
            ],
            PricingIntent.NEUTRAL: [
                IntentAction.OBSERVE,
                IntentAction.COLLECT_DATA,
            ],
        }
    )


# =============================================================================
# Intent Signals Collector
# =============================================================================

class IntentSignalsCollector:
    """
    Collects and normalizes signals from various sources for intent determination.
    
    Transforms raw metrics into normalized signals (0-1 scale).
    """
    
    def __init__(self):
        self._signals: Dict[str, List[IntentSignal]] = {}  # tenant_id -> signals
        self._signal_weights: Dict[str, float] = {
            # Usage signals
            "usage_growth": 1.2,
            "utilization_rate": 1.0,
            "feature_gate_hits": 1.1,
            
            # Engagement signals
            "api_frequency": 0.8,
            "session_depth": 0.7,
            "feature_breadth": 0.9,
            
            # Risk signals
            "dls_score": 1.3,
            "threat_density": 1.2,
            "enforcement_rate": 1.1,
            "drift_severity": 1.0,
            
            # Financial signals
            "payment_timeliness": 1.4,
            "revenue_trend": 1.2,
            "cost_ratio": 1.1,
            
            # Behavioral signals
            "churn_indicators": 1.5,
            "expansion_indicators": 1.3,
            "abuse_indicators": 1.4,
        }
    
    def add_signal(
        self,
        tenant_id: str,
        signal_name: str,
        raw_value: float,
        source: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> IntentSignal:
        """Add a signal for a tenant."""
        # Normalize to 0-1
        normalized = self._normalize_signal(signal_name, raw_value)
        
        signal = IntentSignal(
            signal_name=signal_name,
            signal_value=normalized,
            weight=self._signal_weights.get(signal_name, 1.0),
            source=source,
            metadata=metadata or {},
        )
        
        if tenant_id not in self._signals:
            self._signals[tenant_id] = []
        
        self._signals[tenant_id].append(signal)
        return signal
    
    def get_signals(
        self,
        tenant_id: str,
        max_age_hours: int = 24,
    ) -> List[IntentSignal]:
        """Get recent signals for a tenant."""
        if tenant_id not in self._signals:
            return []
        
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        return [
            s for s in self._signals[tenant_id]
            if s.timestamp >= cutoff
        ]
    
    def clear_signals(self, tenant_id: str) -> None:
        """Clear signals for a tenant."""
        self._signals.pop(tenant_id, None)
    
    def _normalize_signal(self, signal_name: str, raw_value: float) -> float:
        """Normalize raw value to 0-1 scale."""
        # Different normalization strategies per signal type
        if signal_name in ("usage_growth", "revenue_trend"):
            # Growth can be negative, normalize -1 to +1 → 0 to 1
            return max(0, min(1, (raw_value + 1) / 2))
        
        elif signal_name in ("utilization_rate", "dls_score", "payment_timeliness"):
            # Already 0-1 scale
            return max(0, min(1, raw_value))
        
        elif signal_name == "feature_gate_hits":
            # Count-based, cap at 10
            return min(1, raw_value / 10)
        
        elif signal_name in ("threat_density", "enforcement_rate", "drift_severity"):
            # Risk metrics, inverse scale (higher = worse)
            return max(0, min(1, raw_value))
        
        elif signal_name == "cost_ratio":
            # Cost/revenue ratio, inverse normalize
            # 0.5 ratio = good, 2.0 ratio = bad
            return max(0, min(1, raw_value / 2.5))
        
        elif signal_name in ("churn_indicators", "abuse_indicators"):
            # Probability-based
            return max(0, min(1, raw_value))
        
        elif signal_name == "expansion_indicators":
            return max(0, min(1, raw_value))
        
        else:
            # Default normalization
            return max(0, min(1, raw_value))
    
    # =========================================================================
    # Convenience Methods for Common Signal Sources
    # =========================================================================
    
    def ingest_usage_metrics(
        self,
        tenant_id: str,
        current_usage: float,
        limit: float,
        previous_usage: float,
    ) -> None:
        """Ingest usage metrics and derive signals."""
        # Utilization rate
        if limit > 0:
            utilization = current_usage / limit
            self.add_signal(tenant_id, "utilization_rate", utilization, "usage_meter")
        
        # Growth rate
        if previous_usage > 0:
            growth = (current_usage - previous_usage) / previous_usage
            self.add_signal(tenant_id, "usage_growth", growth, "usage_meter")
    
    def ingest_risk_profile(
        self,
        tenant_id: str,
        dls_score: float,
        threat_frequency: float,
        enforcement_rate: float,
        drift_severity: float,
    ) -> None:
        """Ingest risk profile and derive signals."""
        self.add_signal(tenant_id, "dls_score", dls_score, "risk_engine")
        self.add_signal(tenant_id, "threat_density", threat_frequency, "risk_engine")
        self.add_signal(tenant_id, "enforcement_rate", enforcement_rate, "risk_engine")
        self.add_signal(tenant_id, "drift_severity", drift_severity, "risk_engine")
    
    def ingest_payment_status(
        self,
        tenant_id: str,
        days_since_payment: int,
        payment_terms_days: int,
    ) -> None:
        """Ingest payment status and derive signals."""
        # Timeliness: 1.0 = on time, 0.0 = very late
        if payment_terms_days > 0:
            timeliness = max(0, 1 - (days_since_payment / (payment_terms_days * 2)))
            self.add_signal(tenant_id, "payment_timeliness", timeliness, "billing")
    
    def ingest_feature_gates(
        self,
        tenant_id: str,
        gate_attempts: int,
        blocked_count: int,
    ) -> None:
        """Ingest feature gate attempts."""
        self.add_signal(tenant_id, "feature_gate_hits", blocked_count, "access_control")
        
        # Expansion indicator based on gate attempts
        if gate_attempts > 0:
            expansion_signal = min(1, blocked_count / gate_attempts)
            self.add_signal(tenant_id, "expansion_indicators", expansion_signal, "access_control")


# =============================================================================
# Intent Evaluator
# =============================================================================

class IntentEvaluator:
    """
    Evaluates signals to determine pricing intent.
    
    Uses weighted signal analysis to determine the most appropriate
    economic strategy for each tenant.
    """
    
    def __init__(self, policy: Optional[IntentPolicy] = None):
        self._policy = policy or IntentPolicy()
        self._intent_history: Dict[str, List[IntentResult]] = {}
    
    def evaluate(
        self,
        tenant_id: str,
        signals: List[IntentSignal],
    ) -> IntentResult:
        """
        Evaluate signals and determine pricing intent.
        
        Returns the most appropriate intent with confidence and actions.
        """
        if not signals:
            return self._create_neutral_result(
                tenant_id,
                IntentTrigger.INSUFFICIENT_DATA,
            )
        
        # Calculate intent scores
        scores = self._calculate_intent_scores(signals)
        
        # Determine winning intent
        intent, confidence_score = self._determine_intent(scores)
        
        # Determine confidence level
        confidence = self._score_to_confidence(confidence_score)
        
        # Identify triggers
        primary_trigger, contributing = self._identify_triggers(intent, signals)
        
        # Get recommended actions
        actions = self._get_actions(intent, confidence)
        
        # Calculate priority
        priority = self._calculate_priority(intent, confidence_score, signals)
        
        # Create result
        result = IntentResult(
            intent=intent,
            confidence=confidence,
            confidence_score=confidence_score,
            primary_trigger=primary_trigger,
            contributing_triggers=contributing,
            recommended_actions=actions,
            action_priority=priority,
            tenant_id=tenant_id,
            valid_until=datetime.now() + timedelta(hours=self._policy.intent_validity_hours),
            signals_used=signals,
        )
        
        # Store in history
        if tenant_id not in self._intent_history:
            self._intent_history[tenant_id] = []
        self._intent_history[tenant_id].append(result)
        
        # Trim history
        self._intent_history[tenant_id] = self._intent_history[tenant_id][-50:]
        
        return result
    
    def _calculate_intent_scores(
        self,
        signals: List[IntentSignal],
    ) -> Dict[PricingIntent, float]:
        """Calculate scores for each intent based on signals."""
        scores = {
            PricingIntent.EXPAND: 0.0,
            PricingIntent.DEFEND: 0.0,
            PricingIntent.THROTTLE: 0.0,
            PricingIntent.SUSTAIN: 0.0,
            PricingIntent.NEUTRAL: 0.0,
        }
        
        total_weight = 0.0
        
        for signal in signals:
            weight = signal.weighted_value
            total_weight += signal.weight
            
            # Map signals to intents
            if signal.signal_name == "usage_growth":
                if signal.signal_value > 0.6:  # Positive growth
                    scores[PricingIntent.EXPAND] += weight * 0.8
                elif signal.signal_value < 0.4:  # Negative growth
                    scores[PricingIntent.DEFEND] += weight * 0.8
                else:
                    scores[PricingIntent.SUSTAIN] += weight * 0.5
            
            elif signal.signal_name == "utilization_rate":
                if signal.signal_value > 0.9:  # Near limit
                    scores[PricingIntent.EXPAND] += weight * 0.7
                    scores[PricingIntent.THROTTLE] += weight * 0.3
                elif signal.signal_value > 0.75:
                    scores[PricingIntent.EXPAND] += weight * 0.6
                elif signal.signal_value < 0.3:
                    scores[PricingIntent.DEFEND] += weight * 0.4
                else:
                    scores[PricingIntent.SUSTAIN] += weight * 0.5
            
            elif signal.signal_name == "feature_gate_hits":
                if signal.signal_value > 0.5:
                    scores[PricingIntent.EXPAND] += weight * 0.9
            
            elif signal.signal_name == "dls_score":
                # Lower DLS = higher risk
                if signal.signal_value < 0.3:
                    scores[PricingIntent.THROTTLE] += weight * 0.6
                    scores[PricingIntent.DEFEND] += weight * 0.3
                elif signal.signal_value > 0.8:
                    scores[PricingIntent.SUSTAIN] += weight * 0.4
            
            elif signal.signal_name == "threat_density":
                if signal.signal_value > 0.7:
                    scores[PricingIntent.THROTTLE] += weight * 0.7
                elif signal.signal_value > 0.4:
                    scores[PricingIntent.SUSTAIN] += weight * 0.3
            
            elif signal.signal_name == "enforcement_rate":
                if signal.signal_value > 0.5:
                    scores[PricingIntent.THROTTLE] += weight * 0.6
            
            elif signal.signal_name == "payment_timeliness":
                if signal.signal_value < 0.5:
                    scores[PricingIntent.DEFEND] += weight * 0.8
                    scores[PricingIntent.THROTTLE] += weight * 0.2
                elif signal.signal_value > 0.9:
                    scores[PricingIntent.SUSTAIN] += weight * 0.4
            
            elif signal.signal_name == "churn_indicators":
                if signal.signal_value > 0.6:
                    scores[PricingIntent.DEFEND] += weight * 0.9
            
            elif signal.signal_name == "expansion_indicators":
                if signal.signal_value > 0.5:
                    scores[PricingIntent.EXPAND] += weight * 0.8
            
            elif signal.signal_name == "abuse_indicators":
                if signal.signal_value > 0.5:
                    scores[PricingIntent.THROTTLE] += weight * 0.9
            
            elif signal.signal_name == "cost_ratio":
                if signal.signal_value > 0.8:  # High cost ratio
                    scores[PricingIntent.THROTTLE] += weight * 0.6
        
        # Normalize scores
        if total_weight > 0:
            for intent in scores:
                scores[intent] /= total_weight
        
        # Add baseline for neutral/sustain
        scores[PricingIntent.NEUTRAL] += 0.1
        scores[PricingIntent.SUSTAIN] += 0.15
        
        return scores
    
    def _determine_intent(
        self,
        scores: Dict[PricingIntent, float],
    ) -> Tuple[PricingIntent, float]:
        """Determine winning intent and confidence."""
        # Sort by score
        sorted_intents = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        
        winner, winner_score = sorted_intents[0]
        runner_up_score = sorted_intents[1][1] if len(sorted_intents) > 1 else 0
        
        # Confidence based on margin
        margin = winner_score - runner_up_score
        confidence = min(1.0, winner_score + margin)
        
        return winner, confidence
    
    def _score_to_confidence(self, score: float) -> IntentConfidence:
        """Convert confidence score to level."""
        if score >= self._policy.high_confidence_threshold:
            return IntentConfidence.HIGH
        elif score >= self._policy.medium_confidence_threshold:
            return IntentConfidence.MEDIUM
        elif score > 0.2:
            return IntentConfidence.LOW
        else:
            return IntentConfidence.UNCERTAIN
    
    def _identify_triggers(
        self,
        intent: PricingIntent,
        signals: List[IntentSignal],
    ) -> Tuple[IntentTrigger, List[IntentTrigger]]:
        """Identify what triggered the intent."""
        triggers: List[Tuple[IntentTrigger, float]] = []
        
        for signal in signals:
            trigger = self._signal_to_trigger(signal, intent)
            if trigger:
                triggers.append((trigger, signal.weighted_value))
        
        if not triggers:
            return IntentTrigger.INSUFFICIENT_DATA, []
        
        # Sort by contribution
        triggers.sort(key=lambda x: x[1], reverse=True)
        
        primary = triggers[0][0]
        contributing = [t[0] for t in triggers[1:4]]  # Top 3 contributing
        
        return primary, contributing
    
    def _signal_to_trigger(
        self,
        signal: IntentSignal,
        intent: PricingIntent,
    ) -> Optional[IntentTrigger]:
        """Map signal to trigger for given intent."""
        mapping = {
            PricingIntent.EXPAND: {
                "usage_growth": IntentTrigger.USAGE_GROWTH,
                "utilization_rate": IntentTrigger.TIER_CEILING,
                "feature_gate_hits": IntentTrigger.FEATURE_DEMAND,
                "expansion_indicators": IntentTrigger.VALUE_REALIZATION,
            },
            PricingIntent.DEFEND: {
                "usage_growth": IntentTrigger.USAGE_DECLINE,
                "payment_timeliness": IntentTrigger.PAYMENT_RISK,
                "churn_indicators": IntentTrigger.ENGAGEMENT_DROP,
            },
            PricingIntent.THROTTLE: {
                "utilization_rate": IntentTrigger.RESOURCE_EXHAUSTION,
                "threat_density": IntentTrigger.ABUSE_PATTERN,
                "enforcement_rate": IntentTrigger.POLICY_VIOLATION,
                "abuse_indicators": IntentTrigger.ABUSE_PATTERN,
                "cost_ratio": IntentTrigger.EXCESSIVE_COST,
            },
            PricingIntent.SUSTAIN: {
                "usage_growth": IntentTrigger.STABLE_USAGE,
                "payment_timeliness": IntentTrigger.ON_TIME_PAYMENTS,
                "dls_score": IntentTrigger.HEALTHY_ENGAGEMENT,
            },
            PricingIntent.NEUTRAL: {
                "": IntentTrigger.INSUFFICIENT_DATA,
            },
        }
        
        intent_map = mapping.get(intent, {})
        return intent_map.get(signal.signal_name)
    
    def _get_actions(
        self,
        intent: PricingIntent,
        confidence: IntentConfidence,
    ) -> List[IntentAction]:
        """Get recommended actions for intent."""
        actions = list(self._policy.intent_actions.get(intent, []))
        
        # Filter by confidence
        if confidence in (IntentConfidence.LOW, IntentConfidence.UNCERTAIN):
            # Only suggest observation actions for low confidence
            actions = [a for a in actions if a in (
                IntentAction.OBSERVE,
                IntentAction.COLLECT_DATA,
                IntentAction.SCHEDULE_REVIEW,
            )]
            if not actions:
                actions = [IntentAction.OBSERVE]
        
        return actions
    
    def _calculate_priority(
        self,
        intent: PricingIntent,
        confidence: float,
        signals: List[IntentSignal],
    ) -> int:
        """Calculate action priority (0-100, higher = more urgent)."""
        base_priority = {
            PricingIntent.THROTTLE: 80,
            PricingIntent.DEFEND: 60,
            PricingIntent.EXPAND: 40,
            PricingIntent.SUSTAIN: 20,
            PricingIntent.NEUTRAL: 10,
        }
        
        priority = base_priority.get(intent, 10)
        
        # Adjust by confidence
        priority = int(priority * confidence)
        
        # Boost for critical signals
        for signal in signals:
            if signal.signal_name == "abuse_indicators" and signal.signal_value > 0.8:
                priority = min(100, priority + 20)
            elif signal.signal_name == "churn_indicators" and signal.signal_value > 0.7:
                priority = min(100, priority + 15)
        
        return priority
    
    def _create_neutral_result(
        self,
        tenant_id: str,
        trigger: IntentTrigger,
    ) -> IntentResult:
        """Create a neutral result."""
        return IntentResult(
            intent=PricingIntent.NEUTRAL,
            confidence=IntentConfidence.UNCERTAIN,
            confidence_score=0.1,
            primary_trigger=trigger,
            recommended_actions=[IntentAction.COLLECT_DATA],
            action_priority=5,
            tenant_id=tenant_id,
            valid_until=datetime.now() + timedelta(hours=self._policy.intent_validity_hours),
        )
    
    def get_history(
        self,
        tenant_id: str,
        limit: int = 10,
    ) -> List[IntentResult]:
        """Get intent history for a tenant."""
        history = self._intent_history.get(tenant_id, [])
        return history[-limit:]


# =============================================================================
# Pricing Intents Engine
# =============================================================================

class PricingIntentsEngine:
    """
    Main engine for pricing intents.
    
    Combines signal collection, evaluation, and action routing
    into a cohesive economic brain.
    """
    
    def __init__(self, policy: Optional[IntentPolicy] = None):
        self._policy = policy or IntentPolicy()
        self._collector = IntentSignalsCollector()
        self._evaluator = IntentEvaluator(self._policy)
        
        # Action callbacks
        self._action_handlers: Dict[IntentAction, List[Callable]] = {}
        
        # Cached intents
        self._current_intents: Dict[str, IntentResult] = {}
        
        logger.info("PricingIntentsEngine initialized")
    
    # =========================================================================
    # Signal Ingestion
    # =========================================================================
    
    def ingest_usage(
        self,
        tenant_id: str,
        current: float,
        limit: float,
        previous: float,
    ) -> None:
        """Ingest usage metrics."""
        self._collector.ingest_usage_metrics(tenant_id, current, limit, previous)
    
    def ingest_risk(
        self,
        tenant_id: str,
        dls_score: float = 1.0,
        threat_frequency: float = 0.0,
        enforcement_rate: float = 0.0,
        drift_severity: float = 0.0,
    ) -> None:
        """Ingest risk profile."""
        self._collector.ingest_risk_profile(
            tenant_id, dls_score, threat_frequency, enforcement_rate, drift_severity
        )
    
    def ingest_payment(
        self,
        tenant_id: str,
        days_since_payment: int,
        payment_terms_days: int = 30,
    ) -> None:
        """Ingest payment status."""
        self._collector.ingest_payment_status(tenant_id, days_since_payment, payment_terms_days)
    
    def ingest_feature_gates(
        self,
        tenant_id: str,
        attempts: int,
        blocked: int,
    ) -> None:
        """Ingest feature gate activity."""
        self._collector.ingest_feature_gates(tenant_id, attempts, blocked)
    
    def add_signal(
        self,
        tenant_id: str,
        signal_name: str,
        value: float,
        source: str = "",
    ) -> None:
        """Add a custom signal."""
        self._collector.add_signal(tenant_id, signal_name, value, source)
    
    # =========================================================================
    # Intent Evaluation
    # =========================================================================
    
    def evaluate_tenant(self, tenant_id: str) -> IntentResult:
        """Evaluate and return intent for a tenant."""
        signals = self._collector.get_signals(tenant_id)
        result = self._evaluator.evaluate(tenant_id, signals)
        
        # Cache result
        self._current_intents[tenant_id] = result
        
        # Fire action handlers
        self._dispatch_actions(result)
        
        return result
    
    def get_current_intent(self, tenant_id: str) -> Optional[IntentResult]:
        """Get cached current intent for tenant."""
        result = self._current_intents.get(tenant_id)
        
        # Check validity
        if result and result.valid_until:
            if datetime.now() > result.valid_until:
                return None
        
        return result
    
    def get_intent_or_evaluate(self, tenant_id: str) -> IntentResult:
        """Get current intent or evaluate if expired."""
        current = self.get_current_intent(tenant_id)
        if current:
            return current
        return self.evaluate_tenant(tenant_id)
    
    # =========================================================================
    # Action Routing
    # =========================================================================
    
    def on_action(
        self,
        action: IntentAction,
        handler: Callable[[IntentResult], None],
    ) -> None:
        """Register handler for an action."""
        if action not in self._action_handlers:
            self._action_handlers[action] = []
        self._action_handlers[action].append(handler)
    
    def _dispatch_actions(self, result: IntentResult) -> None:
        """Dispatch recommended actions to handlers."""
        for action in result.recommended_actions:
            handlers = self._action_handlers.get(action, [])
            for handler in handlers:
                try:
                    handler(result)
                except Exception as e:
                    logger.warning(f"Action handler error for {action}: {e}")
    
    # =========================================================================
    # Queries
    # =========================================================================
    
    def get_expand_candidates(
        self,
        min_confidence: float = 0.5,
    ) -> List[IntentResult]:
        """Get tenants with EXPAND intent."""
        return [
            r for r in self._current_intents.values()
            if r.intent == PricingIntent.EXPAND
            and r.confidence_score >= min_confidence
        ]
    
    def get_defend_candidates(
        self,
        min_confidence: float = 0.5,
    ) -> List[IntentResult]:
        """Get tenants with DEFEND intent."""
        return [
            r for r in self._current_intents.values()
            if r.intent == PricingIntent.DEFEND
            and r.confidence_score >= min_confidence
        ]
    
    def get_throttle_candidates(
        self,
        min_confidence: float = 0.5,
    ) -> List[IntentResult]:
        """Get tenants with THROTTLE intent."""
        return [
            r for r in self._current_intents.values()
            if r.intent == PricingIntent.THROTTLE
            and r.confidence_score >= min_confidence
        ]
    
    def get_high_priority_intents(
        self,
        min_priority: int = 50,
    ) -> List[IntentResult]:
        """Get high priority intents across all tenants."""
        return sorted(
            [r for r in self._current_intents.values() if r.action_priority >= min_priority],
            key=lambda x: x.action_priority,
            reverse=True,
        )
    
    # =========================================================================
    # Status
    # =========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get engine status."""
        intent_counts = {}
        for result in self._current_intents.values():
            intent = result.intent.value
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        return {
            "total_tenants": len(self._current_intents),
            "intent_distribution": intent_counts,
            "action_handlers": {
                a.value: len(h) for a, h in self._action_handlers.items()
            },
            "high_priority_count": len(self.get_high_priority_intents()),
        }
    
    def clear_tenant(self, tenant_id: str) -> None:
        """Clear all data for a tenant."""
        self._collector.clear_signals(tenant_id)
        self._current_intents.pop(tenant_id, None)


# =============================================================================
# Factory Functions
# =============================================================================

def create_intents_engine(
    policy: Optional[IntentPolicy] = None,
) -> PricingIntentsEngine:
    """Create a pricing intents engine."""
    return PricingIntentsEngine(policy)


def create_intent_policy(
    expansion_threshold: float = 0.15,
    defense_threshold: float = -0.20,
    throttle_overage: float = 1.20,
) -> IntentPolicy:
    """Create a custom intent policy."""
    return IntentPolicy(
        expansion_usage_growth_threshold=expansion_threshold,
        defense_usage_decline_threshold=defense_threshold,
        throttle_overage_threshold=throttle_overage,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "PricingIntent",
    "IntentConfidence",
    "IntentTrigger",
    "IntentAction",
    # Data Classes
    "IntentSignal",
    "IntentResult",
    "IntentPolicy",
    # Classes
    "IntentSignalsCollector",
    "IntentEvaluator",
    "PricingIntentsEngine",
    # Factories
    "create_intents_engine",
    "create_intent_policy",
]
