# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Adaptive Billing Intelligence - Phase 3 Week 21

Attaches the Monetization Loop to three synchronized loops:
1. Observability Loop → Usage-based billing signals
2. Adaptive Defense Loop → Risk-adjusted pricing
3. Model Governance Loop → ML feature tier gating

Key Features:
- Dynamic pricing tension from detected risk
- Tier violation pattern monetization
- Behavioral score-driven upsell triggers
- Usage metering with DLS integration
- Revenue protection from license anomalies
"""

from __future__ import annotations

import hashlib
import logging
import statistics
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from decimal import Decimal
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
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
# Enums - Imported from krl-types (Single Source of Truth)
# =============================================================================

# Import canonical enums from krl-types package
from krl_types.billing import (
    Tier,
    CustomerSegment,
    ContractType,
    ContractStatus,
    PaymentTerms,
    CreditType,
    UsageMetricType,
    HealthCategory,
    ChurnRisk,
    InterventionType,
    PricingStrategy,
    ExperimentStatus,
    ExperimentType,
    ValueDriver,
    AuditAction,
    ActorType,
    StripeSyncStatus,
    StripeEntityType,
    # Deprecated but still supported
    BillingTier,
    KRLTier,
    PricingTier,
)

# Import currency utilities from krl-types
from krl_types.billing import (
    Currency,
    Money,
    round_currency,
    to_cents,
    from_cents,
    usd,
    eur,
    gbp,
)


# Local enums that are specific to this module (not shared)
class UpsellTriggerType(Enum):
    """Types of upsell triggers."""
    USAGE_THRESHOLD = "usage_threshold"
    FEATURE_GATE = "feature_gate"
    TIER_VIOLATION = "tier_violation"
    RISK_INCREASE = "risk_increase"
    VALUE_REALIZATION = "value_realization"
    BEHAVIORAL_PATTERN = "behavioral_pattern"


class RevenueEventType(Enum):
    """Types of revenue events."""
    USAGE_RECORDED = "usage_recorded"
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    TIER_VIOLATION = "tier_violation"
    UPSELL_TRIGGERED = "upsell_triggered"
    INVOICE_GENERATED = "invoice_generated"
    PAYMENT_RECEIVED = "payment_received"
    CHURN_RISK = "churn_risk"
    EXPANSION_OPPORTUNITY = "expansion_opportunity"


class RiskPricingFactor(Enum):
    """Factors that affect risk-adjusted pricing."""
    DLS_SCORE = "dls_score"
    THREAT_FREQUENCY = "threat_frequency"
    ANOMALY_RATE = "anomaly_rate"
    ENFORCEMENT_RATE = "enforcement_rate"
    DRIFT_SEVERITY = "drift_severity"
    VIOLATION_HISTORY = "violation_history"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class UsageRecord:
    """A single usage record for billing."""
    record_id: str
    tenant_id: str
    metric_type: UsageMetricType
    quantity: Decimal
    timestamp: datetime
    
    # Billing context
    tier: Tier
    unit_price: Decimal = Decimal("0")
    total_price: Decimal = Decimal("0")
    
    # Source tracing
    source: str = ""
    correlation_id: Optional[str] = None
    
    # Risk adjustment
    risk_multiplier: Decimal = Decimal("1.0")
    risk_factors: Dict[str, float] = field(default_factory=dict)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "tenant_id": self.tenant_id,
            "metric_type": self.metric_type.value,
            "quantity": str(self.quantity),
            "timestamp": self.timestamp.isoformat(),
            "tier": self.tier.value,
            "unit_price": str(self.unit_price),
            "total_price": str(self.total_price),
            "risk_multiplier": str(self.risk_multiplier),
            "source": self.source,
        }


@dataclass
class TierPricing:
    """Pricing configuration for a tier."""
    tier: Tier
    base_price: Decimal
    included_units: Dict[UsageMetricType, int]
    overage_rates: Dict[UsageMetricType, Decimal]
    
    # Limits
    hard_limits: Dict[UsageMetricType, int] = field(default_factory=dict)
    soft_limits: Dict[UsageMetricType, int] = field(default_factory=dict)
    
    # Risk pricing
    risk_pricing_enabled: bool = False
    max_risk_multiplier: Decimal = Decimal("2.0")
    
    # Features
    features: Set[str] = field(default_factory=set)
    ml_models_allowed: Set[str] = field(default_factory=set)


@dataclass
class UpsellTrigger:
    """Configuration for an upsell trigger."""
    trigger_id: str
    trigger_type: UpsellTriggerType
    name: str
    description: str
    
    # Conditions
    source_tier: BillingTier
    target_tier: BillingTier
    condition: Dict[str, Any]
    
    # Timing
    cooldown_hours: int = 24
    max_triggers_per_month: int = 3
    
    # Messaging
    message_template: str = ""
    cta_url: str = ""
    
    enabled: bool = True


@dataclass
class UpsellEvent:
    """A triggered upsell event."""
    event_id: str
    trigger_id: str
    tenant_id: str
    timestamp: datetime
    
    trigger_type: UpsellTriggerType
    source_tier: BillingTier
    target_tier: BillingTier
    
    # Context
    trigger_context: Dict[str, Any]
    message: str
    cta_url: str
    
    # Tracking
    viewed: bool = False
    clicked: bool = False
    converted: bool = False


@dataclass
class RiskPricingProfile:
    """Risk-based pricing profile for a tenant."""
    tenant_id: str
    
    # Current risk scores (0-1)
    dls_score: float = 1.0  # Higher is better (less risk)
    threat_score: float = 0.0  # Higher is worse
    anomaly_score: float = 0.0
    violation_score: float = 0.0
    
    # Computed multiplier
    risk_multiplier: Decimal = Decimal("1.0")
    
    # History
    score_history: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def compute_multiplier(
        self,
        weights: Dict[RiskPricingFactor, float],
        max_multiplier: Decimal = Decimal("2.0"),
    ) -> Decimal:
        """Compute risk multiplier from scores."""
        # Base: start at 1.0
        multiplier = 1.0
        
        # DLS: higher is better, so inverse contribution
        if RiskPricingFactor.DLS_SCORE in weights:
            # DLS 1.0 = no increase, DLS 0.5 = increase
            dls_penalty = (1.0 - self.dls_score) * weights[RiskPricingFactor.DLS_SCORE]
            multiplier += dls_penalty
        
        # Threat score: higher is worse
        if RiskPricingFactor.THREAT_FREQUENCY in weights:
            multiplier += self.threat_score * weights[RiskPricingFactor.THREAT_FREQUENCY]
        
        # Anomaly score
        if RiskPricingFactor.ANOMALY_RATE in weights:
            multiplier += self.anomaly_score * weights[RiskPricingFactor.ANOMALY_RATE]
        
        # Violation score
        if RiskPricingFactor.VIOLATION_HISTORY in weights:
            multiplier += self.violation_score * weights[RiskPricingFactor.VIOLATION_HISTORY]
        
        # Cap at max
        self.risk_multiplier = min(Decimal(str(multiplier)), max_multiplier)
        self.last_updated = datetime.now()
        
        return self.risk_multiplier


@dataclass
class BillingPeriod:
    """A billing period with accumulated usage."""
    period_id: str
    tenant_id: str
    tier: BillingTier
    
    start_date: datetime
    end_date: datetime
    
    # Usage
    usage: Dict[UsageMetricType, Decimal] = field(default_factory=dict)
    usage_records: List[str] = field(default_factory=list)  # record IDs
    
    # Pricing
    base_charge: Decimal = Decimal("0")
    overage_charges: Dict[UsageMetricType, Decimal] = field(default_factory=dict)
    risk_adjustments: Decimal = Decimal("0")
    discounts: Decimal = Decimal("0")
    total_charge: Decimal = Decimal("0")
    
    # Status
    finalized: bool = False
    invoiced: bool = False
    
    def compute_total(self) -> Decimal:
        """Compute total charge for the period."""
        self.total_charge = (
            self.base_charge
            + sum(self.overage_charges.values(), Decimal("0"))
            + self.risk_adjustments
            - self.discounts
        )
        return self.total_charge


# =============================================================================
# Default Tier Configurations
# =============================================================================

DEFAULT_TIER_PRICING: Dict[BillingTier, TierPricing] = {
    BillingTier.COMMUNITY: TierPricing(
        tier=BillingTier.COMMUNITY,
        base_price=Decimal("0"),
        included_units={
            UsageMetricType.API_CALLS: 10_000,
            UsageMetricType.ML_INFERENCES: 1_000,
            UsageMetricType.THREAT_DETECTIONS: 100,
            UsageMetricType.TELEMETRY_STORAGE_GB: 1,
        },
        overage_rates={
            UsageMetricType.API_CALLS: Decimal("0.001"),  # $0.001 per call
            UsageMetricType.ML_INFERENCES: Decimal("0.01"),  # $0.01 per inference
        },
        hard_limits={
            UsageMetricType.API_CALLS: 50_000,
            UsageMetricType.ML_INFERENCES: 5_000,
            UsageMetricType.FEDERATED_ROUNDS: 0,  # Not allowed
            UsageMetricType.CUSTOM_MODEL_DEPLOYMENTS: 0,
        },
        features={"basic_defense", "static_models"},
        ml_models_allowed={"anomaly_detection", "risk_scoring"},
    ),
    BillingTier.PRO: TierPricing(
        tier=BillingTier.PRO,
        base_price=Decimal("99"),
        included_units={
            UsageMetricType.API_CALLS: 100_000,
            UsageMetricType.ML_INFERENCES: 10_000,
            UsageMetricType.THREAT_DETECTIONS: 1_000,
            UsageMetricType.ENFORCEMENT_ACTIONS: 500,
            UsageMetricType.TELEMETRY_STORAGE_GB: 10,
            UsageMetricType.FEDERATED_ROUNDS: 4,
        },
        overage_rates={
            UsageMetricType.API_CALLS: Decimal("0.0008"),
            UsageMetricType.ML_INFERENCES: Decimal("0.008"),
            UsageMetricType.THREAT_DETECTIONS: Decimal("0.05"),
            UsageMetricType.FEDERATED_ROUNDS: Decimal("25"),
        },
        soft_limits={
            UsageMetricType.API_CALLS: 500_000,
            UsageMetricType.ML_INFERENCES: 50_000,
        },
        risk_pricing_enabled=True,
        max_risk_multiplier=Decimal("1.5"),
        features={"basic_defense", "static_models", "hybrid_models", "federated_learning", "drift_detection"},
        ml_models_allowed={"anomaly_detection", "risk_scoring", "pattern_learning", "predictive"},
    ),
    BillingTier.ENTERPRISE: TierPricing(
        tier=BillingTier.ENTERPRISE,
        base_price=Decimal("499"),
        included_units={
            UsageMetricType.API_CALLS: 1_000_000,
            UsageMetricType.ML_INFERENCES: 100_000,
            UsageMetricType.THREAT_DETECTIONS: 10_000,
            UsageMetricType.ENFORCEMENT_ACTIONS: 5_000,
            UsageMetricType.ANOMALY_ANALYSES: 10_000,
            UsageMetricType.TELEMETRY_STORAGE_GB: 100,
            UsageMetricType.MODEL_STORAGE_GB: 10,
            UsageMetricType.FEDERATED_ROUNDS: 52,  # Weekly
            UsageMetricType.CUSTOM_MODEL_DEPLOYMENTS: 5,
            UsageMetricType.CROWN_JEWEL_ACCESSES: 1_000,
        },
        overage_rates={
            UsageMetricType.API_CALLS: Decimal("0.0005"),
            UsageMetricType.ML_INFERENCES: Decimal("0.005"),
            UsageMetricType.THREAT_DETECTIONS: Decimal("0.03"),
            UsageMetricType.CUSTOM_MODEL_DEPLOYMENTS: Decimal("99"),
        },
        risk_pricing_enabled=True,
        max_risk_multiplier=Decimal("2.0"),
        features={"*"},  # All features
        ml_models_allowed={"*"},  # All models
    ),
}


# =============================================================================
# Default Upsell Triggers
# =============================================================================

DEFAULT_UPSELL_TRIGGERS: List[UpsellTrigger] = [
    # Community → Pro triggers
    UpsellTrigger(
        trigger_id="community_api_threshold",
        trigger_type=UpsellTriggerType.USAGE_THRESHOLD,
        name="API Usage Threshold",
        description="Triggered when Community user exceeds 80% of API call limit",
        source_tier=BillingTier.COMMUNITY,
        target_tier=BillingTier.PRO,
        condition={"metric": "API_CALLS", "threshold_percent": 80},
        message_template="You've used {usage_percent}% of your API calls. Upgrade to Pro for 10x more calls.",
        cta_url="https://krlabs.dev/pricing?upgrade=pro",
    ),
    UpsellTrigger(
        trigger_id="community_feature_gate",
        trigger_type=UpsellTriggerType.FEATURE_GATE,
        name="Federated Learning Gate",
        description="Triggered when Community user attempts federated learning",
        source_tier=BillingTier.COMMUNITY,
        target_tier=BillingTier.PRO,
        condition={"feature": "federated_learning"},
        message_template="Federated learning is available on Pro tier. Upgrade to train models collaboratively.",
        cta_url="https://krlabs.dev/pricing?feature=federated",
    ),
    UpsellTrigger(
        trigger_id="community_tier_violation",
        trigger_type=UpsellTriggerType.TIER_VIOLATION,
        name="Repeated Tier Violations",
        description="Triggered after 3 tier violations in 24 hours",
        source_tier=BillingTier.COMMUNITY,
        target_tier=BillingTier.PRO,
        condition={"violations_count": 3, "window_hours": 24},
        message_template="You've hit Community tier limits {count} times. Pro tier removes these restrictions.",
        cta_url="https://krlabs.dev/pricing?upgrade=pro",
    ),
    
    # Pro → Enterprise triggers
    UpsellTrigger(
        trigger_id="pro_risk_increase",
        trigger_type=UpsellTriggerType.RISK_INCREASE,
        name="Elevated Risk Profile",
        description="Triggered when Pro user's risk multiplier exceeds 1.3",
        source_tier=BillingTier.PRO,
        target_tier=BillingTier.ENTERPRISE,
        condition={"risk_multiplier_threshold": 1.3},
        message_template="Your security profile suggests advanced threats. Enterprise provides auto-rollback and adaptive ML.",
        cta_url="https://krlabs.dev/pricing?upgrade=enterprise",
    ),
    UpsellTrigger(
        trigger_id="pro_value_realization",
        trigger_type=UpsellTriggerType.VALUE_REALIZATION,
        name="High Value Usage",
        description="Triggered when threat detections prevented exceed $10K estimated damage",
        source_tier=BillingTier.PRO,
        target_tier=BillingTier.ENTERPRISE,
        condition={"estimated_value_saved": 10000},
        message_template="Your defense system has prevented an estimated ${value_saved} in damages. Enterprise maximizes protection.",
        cta_url="https://krlabs.dev/pricing?value=enterprise",
    ),
    UpsellTrigger(
        trigger_id="pro_behavioral_pattern",
        trigger_type=UpsellTriggerType.BEHAVIORAL_PATTERN,
        name="Enterprise Usage Patterns",
        description="Triggered when Pro user exhibits enterprise-like usage patterns",
        source_tier=BillingTier.PRO,
        target_tier=BillingTier.ENTERPRISE,
        condition={"patterns": ["multi_tenant", "high_volume", "custom_models"]},
        message_template="Your usage patterns match our Enterprise customers. Let's discuss a custom plan.",
        cta_url="https://krlabs.dev/contact?type=enterprise",
    ),
]


# =============================================================================
# Usage Meter
# =============================================================================

class UsageMeter:
    """
    Meters usage and records billing events.
    
    Integrates with:
    - Observability Loop (telemetry events → usage records)
    - Defense Loop (enforcement actions → billable events)
    - Governance Loop (ML operations → feature metering)
    """
    
    def __init__(
        self,
        tier_pricing: Optional[Dict[BillingTier, TierPricing]] = None,
    ):
        self._tier_pricing = tier_pricing or DEFAULT_TIER_PRICING
        
        # Usage storage
        self._records: Dict[str, UsageRecord] = {}
        self._tenant_usage: Dict[str, Dict[UsageMetricType, Decimal]] = {}
        self._record_counter = 0
        
        # Aggregations
        self._hourly_usage: Dict[str, Dict[str, Decimal]] = {}  # tenant:hour → metric → count
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Callbacks
        self._on_record: List[Callable[[UsageRecord], None]] = []
        self._on_threshold: List[Callable[[str, UsageMetricType, float], None]] = []
    
    def record_usage(
        self,
        tenant_id: str,
        metric_type: UsageMetricType,
        quantity: Decimal,
        tier: BillingTier,
        source: str = "",
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> UsageRecord:
        """Record a usage event."""
        with self._lock:
            self._record_counter += 1
            record_id = f"usage-{self._record_counter:08d}"
            
            # Get pricing
            pricing = self._tier_pricing.get(tier)
            unit_price = Decimal("0")
            if pricing:
                included = pricing.included_units.get(metric_type, 0)
                current = self._tenant_usage.get(tenant_id, {}).get(metric_type, Decimal("0"))
                
                # Check if over included units
                if current >= included:
                    unit_price = pricing.overage_rates.get(metric_type, Decimal("0"))
            
            record = UsageRecord(
                record_id=record_id,
                tenant_id=tenant_id,
                metric_type=metric_type,
                quantity=quantity,
                timestamp=datetime.now(),
                tier=tier,
                unit_price=unit_price,
                total_price=unit_price * quantity,
                source=source,
                correlation_id=correlation_id,
                metadata=metadata or {},
            )
            
            # Store
            self._records[record_id] = record
            
            # Update aggregations
            if tenant_id not in self._tenant_usage:
                self._tenant_usage[tenant_id] = {}
            
            current = self._tenant_usage[tenant_id].get(metric_type, Decimal("0"))
            self._tenant_usage[tenant_id][metric_type] = current + quantity
            
            # Check thresholds
            self._check_thresholds(tenant_id, metric_type, tier)
            
            # Notify
            for cb in self._on_record:
                try:
                    cb(record)
                except Exception as e:
                    logger.warning(f"Usage record callback error: {e}")
            
            return record
    
    def _check_thresholds(
        self,
        tenant_id: str,
        metric_type: UsageMetricType,
        tier: BillingTier,
    ) -> None:
        """Check if usage thresholds are exceeded."""
        pricing = self._tier_pricing.get(tier)
        if not pricing:
            return
        
        included = pricing.included_units.get(metric_type, 0)
        if included == 0:
            return
        
        current = self._tenant_usage.get(tenant_id, {}).get(metric_type, Decimal("0"))
        usage_percent = float(current) / included * 100
        
        # Check threshold levels
        for threshold in [50, 75, 90, 100]:
            if usage_percent >= threshold:
                for cb in self._on_threshold:
                    try:
                        cb(tenant_id, metric_type, usage_percent)
                    except Exception as e:
                        logger.warning(f"Threshold callback error: {e}")
                break
    
    def get_tenant_usage(
        self,
        tenant_id: str,
        metric_type: Optional[UsageMetricType] = None,
    ) -> Dict[UsageMetricType, Decimal]:
        """Get usage for a tenant."""
        with self._lock:
            usage = self._tenant_usage.get(tenant_id, {})
            if metric_type:
                return {metric_type: usage.get(metric_type, Decimal("0"))}
            return usage.copy()
    
    def get_usage_percent(
        self,
        tenant_id: str,
        tier: BillingTier,
        metric_type: UsageMetricType,
    ) -> float:
        """Get usage as percentage of included units."""
        pricing = self._tier_pricing.get(tier)
        if not pricing:
            return 0.0
        
        included = pricing.included_units.get(metric_type, 0)
        if included == 0:
            return 0.0
        
        current = self._tenant_usage.get(tenant_id, {}).get(metric_type, Decimal("0"))
        return float(current) / included * 100
    
    def on_usage_record(self, callback: Callable[[UsageRecord], None]) -> None:
        """Register usage record callback."""
        self._on_record.append(callback)
    
    def on_threshold_exceeded(
        self,
        callback: Callable[[str, UsageMetricType, float], None],
    ) -> None:
        """Register threshold exceeded callback."""
        self._on_threshold.append(callback)
    
    def reset_tenant_usage(self, tenant_id: str) -> None:
        """Reset usage for a tenant (e.g., new billing period)."""
        with self._lock:
            self._tenant_usage[tenant_id] = {}


# =============================================================================
# Risk Pricing Engine
# =============================================================================

class RiskPricingEngine:
    """
    Computes risk-adjusted pricing based on defense signals.
    
    Integrates with:
    - DLS scores from Observability Loop
    - Threat detections from Defense Loop
    - Drift events from Governance Loop
    """
    
    def __init__(
        self,
        risk_weights: Optional[Dict[RiskPricingFactor, float]] = None,
    ):
        self._weights = risk_weights or {
            RiskPricingFactor.DLS_SCORE: 0.4,
            RiskPricingFactor.THREAT_FREQUENCY: 0.25,
            RiskPricingFactor.ANOMALY_RATE: 0.15,
            RiskPricingFactor.VIOLATION_HISTORY: 0.2,
        }
        
        self._profiles: Dict[str, RiskPricingProfile] = {}
        self._lock = threading.RLock()
        
        # History for trend analysis
        self._score_history: Dict[str, deque] = {}
        self._max_history = 100
    
    def update_dls_score(self, tenant_id: str, score: float) -> None:
        """Update DLS score for tenant."""
        with self._lock:
            profile = self._get_or_create_profile(tenant_id)
            profile.dls_score = max(0.0, min(1.0, score))
            self._record_history(tenant_id, "dls", score)
    
    def update_threat_score(self, tenant_id: str, score: float) -> None:
        """Update threat score for tenant."""
        with self._lock:
            profile = self._get_or_create_profile(tenant_id)
            profile.threat_score = max(0.0, min(1.0, score))
            self._record_history(tenant_id, "threat", score)
    
    def update_anomaly_score(self, tenant_id: str, score: float) -> None:
        """Update anomaly score for tenant."""
        with self._lock:
            profile = self._get_or_create_profile(tenant_id)
            profile.anomaly_score = max(0.0, min(1.0, score))
            self._record_history(tenant_id, "anomaly", score)
    
    def update_violation_score(self, tenant_id: str, score: float) -> None:
        """Update violation score for tenant."""
        with self._lock:
            profile = self._get_or_create_profile(tenant_id)
            profile.violation_score = max(0.0, min(1.0, score))
            self._record_history(tenant_id, "violation", score)
    
    def compute_multiplier(
        self,
        tenant_id: str,
        tier: BillingTier,
        tier_pricing: Optional[Dict[BillingTier, TierPricing]] = None,
    ) -> Decimal:
        """Compute risk multiplier for tenant."""
        pricing = (tier_pricing or DEFAULT_TIER_PRICING).get(tier)
        
        if not pricing or not pricing.risk_pricing_enabled:
            return Decimal("1.0")
        
        with self._lock:
            profile = self._get_or_create_profile(tenant_id)
            return profile.compute_multiplier(
                self._weights,
                pricing.max_risk_multiplier,
            )
    
    def get_profile(self, tenant_id: str) -> Optional[RiskPricingProfile]:
        """Get risk profile for tenant."""
        return self._profiles.get(tenant_id)
    
    def _get_or_create_profile(self, tenant_id: str) -> RiskPricingProfile:
        """Get or create risk profile."""
        if tenant_id not in self._profiles:
            self._profiles[tenant_id] = RiskPricingProfile(tenant_id=tenant_id)
        return self._profiles[tenant_id]
    
    def _record_history(self, tenant_id: str, score_type: str, value: float) -> None:
        """Record score in history."""
        key = f"{tenant_id}:{score_type}"
        if key not in self._score_history:
            self._score_history[key] = deque(maxlen=self._max_history)
        
        self._score_history[key].append({
            "timestamp": datetime.now().isoformat(),
            "value": value,
        })


# =============================================================================
# Upsell Engine
# =============================================================================

class UpsellEngine:
    """
    Triggers upsell opportunities based on usage and behavior.
    
    Integrates with:
    - Usage Meter (threshold triggers)
    - Governance Loop (feature gate triggers)
    - Risk Engine (risk increase triggers)
    """
    
    def __init__(
        self,
        triggers: Optional[List[UpsellTrigger]] = None,
    ):
        self._triggers = {t.trigger_id: t for t in (triggers or DEFAULT_UPSELL_TRIGGERS)}
        
        # Tracking
        self._events: Dict[str, UpsellEvent] = {}
        self._tenant_triggers: Dict[str, List[str]] = {}  # tenant → event IDs
        self._trigger_history: Dict[str, List[datetime]] = {}  # trigger:tenant → timestamps
        
        self._event_counter = 0
        self._lock = threading.RLock()
        
        # Callbacks
        self._on_upsell: List[Callable[[UpsellEvent], None]] = []
    
    def check_usage_threshold(
        self,
        tenant_id: str,
        current_tier: BillingTier,
        metric_type: UsageMetricType,
        usage_percent: float,
    ) -> Optional[UpsellEvent]:
        """Check for usage threshold upsell triggers."""
        for trigger in self._triggers.values():
            if not trigger.enabled:
                continue
            if trigger.trigger_type != UpsellTriggerType.USAGE_THRESHOLD:
                continue
            if trigger.source_tier != current_tier:
                continue
            
            condition = trigger.condition
            if condition.get("metric") != metric_type.name:
                continue
            
            threshold = condition.get("threshold_percent", 80)
            if usage_percent >= threshold:
                return self._create_upsell_event(
                    trigger,
                    tenant_id,
                    {"usage_percent": usage_percent, "metric": metric_type.value},
                )
        
        return None
    
    def check_feature_gate(
        self,
        tenant_id: str,
        current_tier: BillingTier,
        feature: str,
    ) -> Optional[UpsellEvent]:
        """Check for feature gate upsell triggers."""
        for trigger in self._triggers.values():
            if not trigger.enabled:
                continue
            if trigger.trigger_type != UpsellTriggerType.FEATURE_GATE:
                continue
            if trigger.source_tier != current_tier:
                continue
            
            condition = trigger.condition
            if condition.get("feature") != feature:
                continue
            
            return self._create_upsell_event(
                trigger,
                tenant_id,
                {"feature": feature},
            )
        
        return None
    
    def check_tier_violation(
        self,
        tenant_id: str,
        current_tier: BillingTier,
        violation_count: int,
        window_hours: int = 24,
    ) -> Optional[UpsellEvent]:
        """Check for tier violation upsell triggers."""
        for trigger in self._triggers.values():
            if not trigger.enabled:
                continue
            if trigger.trigger_type != UpsellTriggerType.TIER_VIOLATION:
                continue
            if trigger.source_tier != current_tier:
                continue
            
            condition = trigger.condition
            required_count = condition.get("violations_count", 3)
            required_window = condition.get("window_hours", 24)
            
            if violation_count >= required_count and window_hours <= required_window:
                return self._create_upsell_event(
                    trigger,
                    tenant_id,
                    {"count": violation_count, "window_hours": window_hours},
                )
        
        return None
    
    def check_risk_increase(
        self,
        tenant_id: str,
        current_tier: BillingTier,
        risk_multiplier: Decimal,
    ) -> Optional[UpsellEvent]:
        """Check for risk increase upsell triggers."""
        for trigger in self._triggers.values():
            if not trigger.enabled:
                continue
            if trigger.trigger_type != UpsellTriggerType.RISK_INCREASE:
                continue
            if trigger.source_tier != current_tier:
                continue
            
            condition = trigger.condition
            threshold = Decimal(str(condition.get("risk_multiplier_threshold", 1.3)))
            
            if risk_multiplier >= threshold:
                return self._create_upsell_event(
                    trigger,
                    tenant_id,
                    {"risk_multiplier": str(risk_multiplier)},
                )
        
        return None
    
    def _create_upsell_event(
        self,
        trigger: UpsellTrigger,
        tenant_id: str,
        context: Dict[str, Any],
    ) -> Optional[UpsellEvent]:
        """Create an upsell event if cooldown allows."""
        with self._lock:
            # Check cooldown
            history_key = f"{trigger.trigger_id}:{tenant_id}"
            history = self._trigger_history.get(history_key, [])
            
            now = datetime.now()
            cooldown = timedelta(hours=trigger.cooldown_hours)
            
            # Filter recent triggers
            recent = [t for t in history if now - t < cooldown]
            
            if len(recent) >= trigger.max_triggers_per_month:
                return None
            
            # Create event
            self._event_counter += 1
            event_id = f"upsell-{self._event_counter:06d}"
            
            # Format message
            message = trigger.message_template
            for key, value in context.items():
                message = message.replace(f"{{{key}}}", str(value))
            
            event = UpsellEvent(
                event_id=event_id,
                trigger_id=trigger.trigger_id,
                tenant_id=tenant_id,
                timestamp=now,
                trigger_type=trigger.trigger_type,
                source_tier=trigger.source_tier,
                target_tier=trigger.target_tier,
                trigger_context=context,
                message=message,
                cta_url=trigger.cta_url,
            )
            
            # Store
            self._events[event_id] = event
            
            if tenant_id not in self._tenant_triggers:
                self._tenant_triggers[tenant_id] = []
            self._tenant_triggers[tenant_id].append(event_id)
            
            # Update history
            if history_key not in self._trigger_history:
                self._trigger_history[history_key] = []
            self._trigger_history[history_key].append(now)
            
            # Notify
            for cb in self._on_upsell:
                try:
                    cb(event)
                except Exception as e:
                    logger.warning(f"Upsell callback error: {e}")
            
            logger.info(f"Upsell triggered: {trigger.name} for {tenant_id}")
            
            return event
    
    def on_upsell_triggered(self, callback: Callable[[UpsellEvent], None]) -> None:
        """Register upsell triggered callback."""
        self._on_upsell.append(callback)
    
    def mark_viewed(self, event_id: str) -> bool:
        """Mark upsell as viewed."""
        if event_id in self._events:
            self._events[event_id].viewed = True
            return True
        return False
    
    def mark_clicked(self, event_id: str) -> bool:
        """Mark upsell as clicked."""
        if event_id in self._events:
            self._events[event_id].clicked = True
            return True
        return False
    
    def mark_converted(self, event_id: str) -> bool:
        """Mark upsell as converted."""
        if event_id in self._events:
            self._events[event_id].converted = True
            return True
        return False
    
    def get_tenant_upsells(
        self,
        tenant_id: str,
        active_only: bool = True,
    ) -> List[UpsellEvent]:
        """Get upsell events for a tenant."""
        event_ids = self._tenant_triggers.get(tenant_id, [])
        events = [self._events[eid] for eid in event_ids if eid in self._events]
        
        if active_only:
            events = [e for e in events if not e.converted]
        
        return events


# =============================================================================
# Adaptive Billing Controller
# =============================================================================

class AdaptiveBillingController:
    """
    Central controller for adaptive billing intelligence.
    
    Orchestrates:
    - Usage metering
    - Risk-adjusted pricing
    - Upsell triggering
    - Revenue event emission
    
    Connects to all three loops via callbacks and integrations.
    """
    
    def __init__(
        self,
        tier_pricing: Optional[Dict[BillingTier, TierPricing]] = None,
        upsell_triggers: Optional[List[UpsellTrigger]] = None,
    ):
        self._tier_pricing = tier_pricing or DEFAULT_TIER_PRICING
        
        # Core components
        self._usage_meter = UsageMeter(self._tier_pricing)
        self._risk_engine = RiskPricingEngine()
        self._upsell_engine = UpsellEngine(upsell_triggers)
        
        # Billing periods
        self._periods: Dict[str, BillingPeriod] = {}  # tenant:period → BillingPeriod
        
        # Revenue events
        self._revenue_events: List[Dict[str, Any]] = []
        self._max_events = 10000
        
        # Tenant state
        self._tenant_tiers: Dict[str, BillingTier] = {}
        self._tenant_violations: Dict[str, List[datetime]] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Wire internal callbacks
        self._wire_callbacks()
        
        # External callbacks
        self._on_revenue_event: List[Callable[[Dict[str, Any]], None]] = []
        
        logger.info("AdaptiveBillingController initialized")
    
    def _wire_callbacks(self) -> None:
        """Wire internal component callbacks."""
        self._usage_meter.on_threshold_exceeded(self._on_usage_threshold)
        self._upsell_engine.on_upsell_triggered(self._on_upsell_event)
    
    # =========================================================================
    # Integration Points (Connect to Three Loops)
    # =========================================================================
    
    def ingest_telemetry_event(
        self,
        tenant_id: str,
        event_type: str,
        metadata: Dict[str, Any],
    ) -> Optional[UsageRecord]:
        """
        Ingest from Observability Loop.
        
        Maps telemetry events to billable usage.
        """
        tier = self._get_tenant_tier(tenant_id)
        
        # Map event types to usage metrics
        metric_mapping = {
            "ml.inference": UsageMetricType.ML_INFERENCES,
            "ml.drift": UsageMetricType.ANOMALY_ANALYSES,
            "threat.detected": UsageMetricType.THREAT_DETECTIONS,
            "enforcement.action": UsageMetricType.ENFORCEMENT_ACTIONS,
            "api.request": UsageMetricType.API_CALLS,
            "crownjewel.access": UsageMetricType.CROWN_JEWEL_ACCESSES,
        }
        
        metric_type = metric_mapping.get(event_type)
        if not metric_type:
            return None
        
        return self._usage_meter.record_usage(
            tenant_id=tenant_id,
            metric_type=metric_type,
            quantity=Decimal("1"),
            tier=tier,
            source="telemetry",
            metadata=metadata,
        )
    
    def ingest_defense_event(
        self,
        tenant_id: str,
        event_type: str,
        severity: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Ingest from Adaptive Defense Loop.
        
        Updates risk scores and triggers pricing adjustments.
        """
        # Map severity to risk contribution
        severity_scores = {
            "low": 0.1,
            "medium": 0.3,
            "high": 0.6,
            "critical": 0.9,
        }
        
        if event_type == "threat_detected":
            score = severity_scores.get(severity or "medium", 0.3)
            current = self._risk_engine.get_profile(tenant_id)
            if current:
                new_score = min(1.0, current.threat_score + score * 0.1)
                self._risk_engine.update_threat_score(tenant_id, new_score)
        
        elif event_type == "anomaly_detected":
            score = severity_scores.get(severity or "medium", 0.3)
            current = self._risk_engine.get_profile(tenant_id)
            if current:
                new_score = min(1.0, current.anomaly_score + score * 0.1)
                self._risk_engine.update_anomaly_score(tenant_id, new_score)
        
        elif event_type == "enforcement_action":
            # Record as usage
            self._usage_meter.record_usage(
                tenant_id=tenant_id,
                metric_type=UsageMetricType.ENFORCEMENT_ACTIONS,
                quantity=Decimal("1"),
                tier=self._get_tenant_tier(tenant_id),
                source="defense",
                metadata=metadata or {},
            )
    
    def ingest_governance_event(
        self,
        tenant_id: str,
        event_type: str,
        model_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Ingest from Model Governance Loop.
        
        Updates ML usage and drift-related pricing.
        """
        tier = self._get_tenant_tier(tenant_id)
        
        if event_type == "federated_round":
            self._usage_meter.record_usage(
                tenant_id=tenant_id,
                metric_type=UsageMetricType.FEDERATED_ROUNDS,
                quantity=Decimal("1"),
                tier=tier,
                source="governance",
                metadata={"model_id": model_id, **(metadata or {})},
            )
        
        elif event_type == "drift_detected":
            drift_severity = (metadata or {}).get("severity", "medium")
            severity_scores = {"low": 0.1, "medium": 0.3, "high": 0.6, "critical": 0.9}
            score = severity_scores.get(drift_severity, 0.3)
            
            # Drift affects anomaly score
            current = self._risk_engine.get_profile(tenant_id)
            if current:
                new_score = min(1.0, current.anomaly_score + score * 0.2)
                self._risk_engine.update_anomaly_score(tenant_id, new_score)
        
        elif event_type == "model_deployed":
            self._usage_meter.record_usage(
                tenant_id=tenant_id,
                metric_type=UsageMetricType.CUSTOM_MODEL_DEPLOYMENTS,
                quantity=Decimal("1"),
                tier=tier,
                source="governance",
                metadata={"model_id": model_id, **(metadata or {})},
            )
    
    def update_dls_score(self, tenant_id: str, dls_score: float) -> None:
        """
        Update DLS score from Observability Loop.
        
        DLS is inverted for risk: higher DLS = lower risk.
        """
        # DLS is 0-100, normalize to 0-1
        normalized = max(0.0, min(1.0, dls_score / 100.0))
        self._risk_engine.update_dls_score(tenant_id, normalized)
        
        # Check for risk-based upsell
        tier = self._get_tenant_tier(tenant_id)
        multiplier = self._risk_engine.compute_multiplier(tenant_id, tier, self._tier_pricing)
        self._upsell_engine.check_risk_increase(tenant_id, tier, multiplier)
    
    def record_tier_violation(self, tenant_id: str, violation_type: str) -> None:
        """Record a tier violation."""
        with self._lock:
            if tenant_id not in self._tenant_violations:
                self._tenant_violations[tenant_id] = []
            
            now = datetime.now()
            self._tenant_violations[tenant_id].append(now)
            
            # Clean old violations
            cutoff = now - timedelta(hours=24)
            self._tenant_violations[tenant_id] = [
                v for v in self._tenant_violations[tenant_id] if v > cutoff
            ]
            
            # Update violation score
            count = len(self._tenant_violations[tenant_id])
            violation_score = min(1.0, count / 10.0)  # 10 violations = 1.0
            self._risk_engine.update_violation_score(tenant_id, violation_score)
            
            # Check for upsell
            tier = self._get_tenant_tier(tenant_id)
            self._upsell_engine.check_tier_violation(tenant_id, tier, count)
            
            # Emit event
            self._emit_revenue_event(RevenueEventType.TIER_VIOLATION, {
                "tenant_id": tenant_id,
                "violation_type": violation_type,
                "violation_count_24h": count,
            })
    
    def check_feature_access(
        self,
        tenant_id: str,
        feature: str,
    ) -> Tuple[bool, Optional[UpsellEvent]]:
        """
        Check if tenant can access a feature.
        
        Returns (allowed, upsell_event_if_blocked).
        """
        tier = self._get_tenant_tier(tenant_id)
        pricing = self._tier_pricing.get(tier)
        
        if not pricing:
            return False, None
        
        # Check if feature is allowed
        if "*" in pricing.features or feature in pricing.features:
            return True, None
        
        # Feature not allowed, trigger upsell
        upsell = self._upsell_engine.check_feature_gate(tenant_id, tier, feature)
        return False, upsell
    
    # =========================================================================
    # Internal Callbacks
    # =========================================================================
    
    def _on_usage_threshold(
        self,
        tenant_id: str,
        metric_type: UsageMetricType,
        usage_percent: float,
    ) -> None:
        """Handle usage threshold exceeded."""
        tier = self._get_tenant_tier(tenant_id)
        
        # Emit event
        self._emit_revenue_event(RevenueEventType.THRESHOLD_EXCEEDED, {
            "tenant_id": tenant_id,
            "metric_type": metric_type.value,
            "usage_percent": usage_percent,
            "tier": tier.value,
        })
        
        # Check for upsell
        self._upsell_engine.check_usage_threshold(
            tenant_id, tier, metric_type, usage_percent
        )
    
    def _on_upsell_event(self, event: UpsellEvent) -> None:
        """Handle upsell triggered."""
        self._emit_revenue_event(RevenueEventType.UPSELL_TRIGGERED, {
            "event_id": event.event_id,
            "tenant_id": event.tenant_id,
            "trigger_type": event.trigger_type.value,
            "source_tier": event.source_tier.value,
            "target_tier": event.target_tier.value,
            "message": event.message,
        })
    
    # =========================================================================
    # Billing Operations
    # =========================================================================
    
    def get_current_period(self, tenant_id: str) -> BillingPeriod:
        """Get or create current billing period for tenant."""
        with self._lock:
            now = datetime.now()
            period_key = f"{tenant_id}:{now.strftime('%Y-%m')}"
            
            if period_key not in self._periods:
                tier = self._get_tenant_tier(tenant_id)
                pricing = self._tier_pricing.get(tier)
                
                # Start of month
                start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                # End of month
                if now.month == 12:
                    end = start.replace(year=now.year + 1, month=1)
                else:
                    end = start.replace(month=now.month + 1)
                
                self._periods[period_key] = BillingPeriod(
                    period_id=period_key,
                    tenant_id=tenant_id,
                    tier=tier,
                    start_date=start,
                    end_date=end,
                    base_charge=pricing.base_price if pricing else Decimal("0"),
                )
            
            return self._periods[period_key]
    
    def compute_period_charges(self, tenant_id: str) -> BillingPeriod:
        """Compute charges for current billing period."""
        with self._lock:
            period = self.get_current_period(tenant_id)
            tier = self._get_tenant_tier(tenant_id)
            pricing = self._tier_pricing.get(tier)
            
            if not pricing:
                return period
            
            # Get usage
            usage = self._usage_meter.get_tenant_usage(tenant_id)
            period.usage = usage
            
            # Compute overages
            period.overage_charges = {}
            for metric_type, quantity in usage.items():
                included = pricing.included_units.get(metric_type, 0)
                overage = max(Decimal("0"), quantity - included)
                
                if overage > 0:
                    rate = pricing.overage_rates.get(metric_type, Decimal("0"))
                    period.overage_charges[metric_type] = overage * rate
            
            # Risk adjustment
            if pricing.risk_pricing_enabled:
                multiplier = self._risk_engine.compute_multiplier(tenant_id, tier, self._tier_pricing)
                base_overage = sum(period.overage_charges.values(), Decimal("0"))
                period.risk_adjustments = base_overage * (multiplier - Decimal("1"))
            
            period.compute_total()
            
            return period
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def _get_tenant_tier(self, tenant_id: str) -> BillingTier:
        """Get tier for tenant."""
        return self._tenant_tiers.get(tenant_id, BillingTier.COMMUNITY)
    
    def set_tenant_tier(self, tenant_id: str, tier: BillingTier) -> None:
        """Set tier for tenant."""
        with self._lock:
            old_tier = self._tenant_tiers.get(tenant_id)
            self._tenant_tiers[tenant_id] = tier
            
            if old_tier and old_tier != tier:
                self._emit_revenue_event(RevenueEventType.EXPANSION_OPPORTUNITY, {
                    "tenant_id": tenant_id,
                    "old_tier": old_tier.value,
                    "new_tier": tier.value,
                })
    
    def _emit_revenue_event(
        self,
        event_type: RevenueEventType,
        data: Dict[str, Any],
    ) -> None:
        """Emit a revenue event."""
        event = {
            "event_type": event_type.value,
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }
        
        with self._lock:
            self._revenue_events.append(event)
            if len(self._revenue_events) > self._max_events:
                self._revenue_events = self._revenue_events[-self._max_events:]
        
        for cb in self._on_revenue_event:
            try:
                cb(event)
            except Exception as e:
                logger.warning(f"Revenue event callback error: {e}")
    
    def on_revenue_event(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register revenue event callback."""
        self._on_revenue_event.append(callback)
    
    def get_revenue_events(
        self,
        event_type: Optional[RevenueEventType] = None,
        tenant_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get revenue events."""
        with self._lock:
            events = self._revenue_events
            
            if event_type:
                events = [e for e in events if e["event_type"] == event_type.value]
            
            if tenant_id:
                events = [e for e in events if e.get("data", {}).get("tenant_id") == tenant_id]
            
            return events[-limit:]
    
    def get_billing_summary(self, tenant_id: str) -> Dict[str, Any]:
        """Get comprehensive billing summary for tenant."""
        tier = self._get_tenant_tier(tenant_id)
        usage = self._usage_meter.get_tenant_usage(tenant_id)
        period = self.compute_period_charges(tenant_id)
        risk_profile = self._risk_engine.get_profile(tenant_id)
        upsells = self._upsell_engine.get_tenant_upsells(tenant_id)
        
        return {
            "tenant_id": tenant_id,
            "tier": tier.value,
            "period": {
                "start": period.start_date.isoformat(),
                "end": period.end_date.isoformat(),
                "base_charge": str(period.base_charge),
                "overage_charges": {k.value: str(v) for k, v in period.overage_charges.items()},
                "risk_adjustments": str(period.risk_adjustments),
                "total_charge": str(period.total_charge),
            },
            "usage": {k.value: str(v) for k, v in usage.items()},
            "risk_profile": {
                "dls_score": risk_profile.dls_score if risk_profile else 1.0,
                "threat_score": risk_profile.threat_score if risk_profile else 0.0,
                "risk_multiplier": str(risk_profile.risk_multiplier) if risk_profile else "1.0",
            },
            "active_upsells": len(upsells),
            "upsell_messages": [u.message for u in upsells[:3]],
        }


# =============================================================================
# Factory Functions
# =============================================================================

def create_billing_controller(
    tier_pricing: Optional[Dict[BillingTier, TierPricing]] = None,
) -> AdaptiveBillingController:
    """Create an adaptive billing controller."""
    return AdaptiveBillingController(tier_pricing=tier_pricing)


def create_usage_meter(
    tier_pricing: Optional[Dict[BillingTier, TierPricing]] = None,
) -> UsageMeter:
    """Create a usage meter."""
    return UsageMeter(tier_pricing=tier_pricing)


def create_risk_engine() -> RiskPricingEngine:
    """Create a risk pricing engine."""
    return RiskPricingEngine()


def create_upsell_engine(
    triggers: Optional[List[UpsellTrigger]] = None,
) -> UpsellEngine:
    """Create an upsell engine."""
    return UpsellEngine(triggers=triggers)


# =============================================================================
# Bridge Imports
# =============================================================================

from .billing_bridge import (
    BillingBridgeConfig,
    BillingBridge,
    TELEMETRY_TO_USAGE_MAP,
    create_billing_bridge,
    create_full_billing_stack,
)

# =============================================================================
# StoryBrand Upsell Integration - Day 1-2 Marketing Infrastructure
# =============================================================================

from .upsell_integration import (
    # Config
    DeliveryChannel,
    EmailProvider,
    EmailConfig,
    IntegrationConfig,
    # Services
    EmailDeliveryService,
    EmailDeliveryResult,
    InAppDeliveryService,
    InAppNotificationPayload,
    # Main integration
    UpsellMessageIntegration,
    # Utilities
    get_template_key_for_event,
    TRIGGER_TO_TEMPLATE_MAP,
    # Factory
    create_upsell_integration,
    wire_integration_to_billing,
)

from .storybrand_upsell import (
    UPSELL_MESSAGES_STORYBRAND,
    AB_TEST_FRAMEWORK,
    personalize_upsell_message,
)

from .inapp_notifications import (
    IN_APP_NOTIFICATIONS,
    NotificationFormat,
    get_notification_for_event,
    evaluate_notification_triggers,
)

from .awareness_routing import (
    AwarenessStage,
    AwarenessSignal,
    AwarenessDetector,
    AwarenessRouter,
    AWARENESS_STAGE_ROUTING,
    detect_awareness_stage,
    route_by_awareness,
)

from .landing_page_content import (
    LANDING_PAGE_CONTENT,
    get_landing_page_for_stage,
)


# =============================================================================
# Week 21B: Economic Layer Imports
# =============================================================================

# Pricing Intents - Economic Brain
from .pricing_intents import (
    PricingIntent,
    IntentConfidence,
    IntentTrigger,
    IntentAction,
    IntentSignal,
    IntentResult,
    IntentPolicy,
    IntentSignalsCollector,
    IntentEvaluator,
    PricingIntentsEngine,
    create_intents_engine,
    create_intent_policy,
)

# Unit Normalization - Economic Backbone
from .unit_normalization import (
    UnitType,
    UnitCategory,
    ConversionStrategy,
    ConversionRule,
    NormalizedUnit,
    UnitPricing,
    NormalizationResult,
    DEFAULT_CONVERSION_RULES,
    DEFAULT_UNIT_PRICING,
    UnitNormalizer,
    UnitAggregator,
    create_unit_normalizer,
    create_unit_aggregator,
)

# Billing Policy Tree - Economic Governance
from .billing_policy_tree import (
    PolicyDecision,
    PolicyTrigger,
    PolicyEscalation,
    GracePeriodType,
    PolicyContext,
    PolicyResult,
    PolicyRule,
    TierPolicyConfig,
    DEFAULT_POLICY_RULES,
    DEFAULT_TIER_POLICIES,
    BillingPolicyTree,
    create_policy_tree,
    create_policy_context,
)

# =============================================================================
# Week 22: Revenue Optimization & Predictive Forecasting
# =============================================================================

# Revenue Forecaster
from .revenue_forecaster import (
    ForecastHorizon as ForecastModel,
    ForecastMethod as ForecastPeriod,
    ForecastConfig,
    ForecastResult,
    RevenueSignal as ChurnSignal,
    RevenueSignal as ExpansionSignal,
    TenantRevenueProfile as TenantForecast,
    ForecastResult as RevenueProjection,
    ForecastConfig as DEFAULT_FORECAST_CONFIG,
    TimeSeriesUtils as TimeSeriesBuffer,
    RevenueForecaster,
    create_revenue_forecaster,
)

# Cohort Analytics
from .cohort_analytics import (
    CohortType,
    RetentionMetric,
    ExpansionType,
    ContractionType,
    CustomerHealth,
    CohortMember,
    Cohort as CohortSnapshot,
    RetentionPoint as RetentionCurve,
    LTVPrediction as CohortMetrics,
    LTVPrediction as LTVEstimate,
    CohortAnalyticsConfig as CohortComparison,
    CohortAnalyticsConfig as DEFAULT_COHORT_CONFIG,
    Cohort,
    CohortManager as CohortAnalytics,
    create_cohort_manager as create_cohort_analytics,
)

# Pricing Optimizer
from .pricing_optimizer import (
    ExperimentType,
    ExperimentStatus,
    PriceMetric,
    ElasticityBand,
    VariantAllocation,
    PriceVariant,
    ExperimentConfig,
    ExperimentResult,
    ElasticityResult,
    PricePoint,
    SimulationResult,
    DEFAULT_OPTIMIZER_CONFIG,
    PricingExperiment,
    ElasticityAnalyzer,
    PricingSimulator,
    PricingOptimizer,
    create_pricing_optimizer,
)

# Revenue Alerts
from .revenue_alerts import (
    AlertSeverity,
    AlertCategory,
    AlertStatus,
    AlertChannel,
    AnomalyType,
    Alert,
    AlertRule,
    AlertSubscription,
    MetricSnapshot,
    RevenueHealthStatus,
    DEFAULT_ALERT_CONFIG,
    AnomalyDetector,
    AlertManager,
    RevenueAlertSystem,
    create_revenue_alert_system,
)

# =============================================================================
# Week 23: Payment Gateway Adapters
# =============================================================================

# Payments Adapter (Abstract Interface)
from .payments_adapter import (
    PaymentsAdapter,
    PaymentProvider as AdapterPaymentProvider,
    AccountType,
    SubscriptionStatus,
    PaymentStatus,
    InvoiceStatus,
    WebhookEventType,
    PriceType,
    BillingInterval,
    Address,
    CustomerData,
    PriceData,
    SubscriptionData,
    SubscriptionItemData,
    UsageRecordData,
    InvoiceData,
    InvoiceLineData,
    PaymentData,
    RefundData,
    WebhookEvent as AdapterWebhookEvent,
    ConnectAccount,
    AdapterResult,
    AdapterConfig,
    AdapterRegistry,
    IDMappingStore,
    InMemoryIDMappingStore,
    create_adapter_config,
    create_payments_adapter,
    create_id_mapping_store,
)

# Stripe Adapter
from .stripe_adapter import (
    StripeAdapter,
)

# Lago Adapter
from .lago_adapter import (
    LagoAdapter,
)

# Webhook Dispatcher
from .webhook_dispatcher import (
    WebhookStatus,
    WebhookRecord,
    DispatcherConfig,
    WebhookDispatcher,
    create_webhook_dispatcher,
)

# Billing Integration
from .billing_integration import (
    PaymentProvider,
    BillingEvent,
    UsageRecord,
    PriceUpdate,
    SubscriptionChange,
    BillingIntegrationManager,
    CustomerLifecycleManager,
    create_billing_integration,
)

# =============================================================================
# Week 24: Revenue Reporting & Analytics
# =============================================================================

# Revenue Reporting
from .revenue_reporting import (
    ReportPeriod,
    RevenueSegment,
    MetricType,
    ReportFormat,
    RevenueMetrics,
    SubscriptionMetrics,
    CustomerMetrics,
    TierBreakdown,
    RevenueReport,
    LTVReport,
    RevenueCalculator,
    RevenueReportingEngine,
    create_revenue_reporting_engine,
)

# Billing Dashboards
from .billing_dashboards import (
    WidgetType,
    WidgetSize,
    RefreshRate,
    TrendDirection,
    MetricValue,
    ChartDataPoint,
    ChartSeries,
    WidgetConfig,
    DashboardLayout,
    WidgetData,
    BillingWidgets,
    WidgetDataProvider,
    BillingDashboardManager,
    create_billing_dashboard_manager,
)

# Subscription Analytics
from .subscription_analytics import (
    ChurnRisk,
    HealthScore,
    SubscriptionState,
    MovementType,
    ChurnRiskScore,
    CustomerHealthScore,
    SubscriptionMovement,
    ExpansionOpportunity,
    RenewalForecast,
    ChurnPredictor,
    CustomerHealthScorer,
    SubscriptionAnalytics,
    create_subscription_analytics,
)

# Billing Exports
from .billing_exports import (
    ExportFormat,
    ExportScope,
    CompressionType,
    ScheduleFrequency,
    ExportStatus,
    ExportConfig,
    ExportJob,
    ScheduledReport,
    ExportResult,
    DataSerializer,
    BillingExportEngine,
    ReportScheduler,
    create_billing_export_engine,
    create_report_scheduler,
)

# =============================================================================
# Week 24b: Advanced Billing Infrastructure
# =============================================================================

# Fraud Detection
from .fraud_detection import (
    RiskLevel as FraudRiskLevel,
    FraudSignalType,
    AbuseType,
    EnforcementAction as FraudDecisionAction,
    FraudSignal,
    RiskAssessment,
    AbusePattern,
    VelocityRule,
    RiskConfig as FraudConfig,
    StripeRadarIntegration,
    VelocityTracker,
    AbusePatternDetector,
    RiskMesh as InternalRiskMesh,
    FraudDetectionEngine,
)

# Billing State Machine
from .billing_state_machine import (
    SubscriptionState,
    TransitionTrigger,
    TenantStatus,
    StateTransition,
    TransitionRule,
    SubscriptionContext,
    TenantContext,
    SubscriptionStateMachine,
    TenantIsolationManager,
    BillingStateManager,
    create_billing_state_manager,
)

# Contract Enforcement
from .contract_enforcement import (
    ContractType,
    CommitmentType,
    SLAMetric,
    SLATier,
    BreachSeverity,
    ContractStatus,
    SLADefinition,
    SLAMeasurement,
    SLABreach,
    UsageCommitment,
    ContractTerms,
    ContractHealth,
    SLATracker,
    CommitmentTracker,
    ContractEnforcementEngine,
    create_contract_enforcement_engine,
)

# Limits Gateway
from .limits_gateway import (
    LimitType,
    EnforcementMode,
    LimitAction,
    CircuitState,
    LimitDefinition,
    LimitCheck,
    UsageSnapshot,
    GatewayContext,
    GatewayResponse,
    TokenBucket,
    SlidingWindowCounter,
    CircuitBreaker,
    LimitsGateway,
    create_limits_gateway,
)

# Entitlement Engine
from .entitlement_engine import (
    EntitlementType,
    FeatureFlagState,
    TierLevel,
    FeatureFlag,
    EntitlementGrant,
    EntitlementCheckResult,
    ConnectAccountMapping,
    EntitlementCache,
    FeatureFlagManager,
    SaaSEntitlementEngine,
    create_entitlement_engine,
)

# Stripe FastAPI Integration
from .stripe_fastapi import (
    StripeConfig,
    ProcessedStripeEvent,
    IdempotencyStore,
    TenantProfile,
    TenantMapping,
    TenantResolver,
    StripeAdapterEnhanced,
    WebhookEventRouter,
    get_stripe_adapter,
    get_idempotency_store,
    get_tenant_resolver,
    configure_stripe_adapter,
    create_stripe_webhook_router,
    get_metadata_schema,
)

# Stripe Persistence Layer (SQLAlchemy + Redis)
from .stripe_persistence import (
    # SQLAlchemy models
    ProcessedStripeEventModel,
    TenantMappingModel,
    # Persistent stores
    PersistentIdempotencyStore,
    PersistentTenantResolver,
    RedisCache,
    ProcessedEvent,
    # Engine wiring
    EngineWiring,
    # Configuration
    StripeEnvironmentConfig,
    create_env_template,
    # Factory
    create_persistent_stripe_router,
    # Documentation
    WEBHOOK_REGISTRATION_GUIDE,
    print_webhook_registration_guide,
    # Availability flags
    SQLALCHEMY_AVAILABLE,
    REDIS_AVAILABLE,
)

# Value-Based Pricing Engine (Phase 1)
from .value_pricing import (
    # Enums
    CustomerSegment,
    PricingTier,
    ValueDriver,
    ContractType as ValueContractType,
    # Data classes
    CustomerProfile,
    ValueCalculation,
    PricingRecommendation,
    # Engines
    ROICalculator,
    ValueBasedPricingEngine,
    CustomerSegmentationEngine,
    # Integration functions
    generate_stripe_metadata,
    calculate_customer_price,
)

# Multi-Year Contract Management (Phase 1)
from .contracts import (
    # Enums (renamed to avoid conflicts)
    ContractType as ContractTypeEnum,
    ContractStatus as ContractStatusEnum,
    PaymentTerms,
    CreditType,
    # Data classes
    VolumeDiscount,
    PrepaidCredit,
    SLATerms,
    ContractTerms as ContractTermsModel,
    RenewalOffer,
    # Engines
    ContractPricingEngine,
    PrepaidCreditManager,
    ContractManager,
    # Integration functions
    calculate_enterprise_pricing,
    create_enterprise_contract,
    purchase_api_credits,
    get_stripe_contract_metadata,
    sync_contract_to_stripe,
)

# Customer Health Scoring (Phase 1)
from .health_scoring import (
    # Enums
    HealthCategory,
    ChurnRisk as ChurnRiskLevel,
    InterventionType,
    # Data classes
    UsageMetrics as UsageMetricsModel,
    HealthScore as HealthScoreModel,
    ChurnPrediction,
    ExpansionOpportunity as ExpansionOpportunityModel,
    # Engines
    HealthScoringEngine,
    ChurnPredictionModel,
    ExpansionDetector,
    # Integration functions
    calculate_customer_health,
    predict_customer_churn,
    find_expansion_opportunities,
    get_stripe_health_metadata,
)

# Currency Utilities (Phase 1)
from .currency import (
    # Classes
    Currency as CurrencyCode,
    Money,
    InvoiceLineItem,
    # Functions
    round_currency,
    to_cents,
    from_cents,
    safe_decimal,
    apply_percentage,
    apply_discount as apply_currency_discount,
    format_currency,
    # Convenience constructors
    usd,
    eur,
    gbp,
    # Constants
    TWO_PLACES,
    FOUR_PLACES,
    # Exceptions
    CurrencyError,
    InvalidAmountError,
    CurrencyMismatchError,
)

# Centralized Enums (Phase 1)
from .enums import (
    Tier as BillingTierEnum,
    # CustomerSegment already imported from value_pricing
    ContractType as ContractTypeBase,
    ContractStatus as ContractStatusBase,
    PaymentTerms as PaymentTermsBase,
    HealthCategory as HealthCategoryBase,
    ChurnRisk as ChurnRiskBase,
    InterventionType as InterventionTypeBase,
    ExperimentStatus,
    # Currency already imported
)

# Stripe Metadata Security (Phase 1)
from .stripe_metadata import (
    MetadataCategory,
    MetadataField,
    StripeMetadataWriter,
    create_safe_customer_metadata,
    create_safe_subscription_metadata,
    validate_existing_metadata,
)

# Phase 6: Temporary Model Rental System
from .rental_api import (
    RentalMechanismType,
    TimePassType,
    InferenceBundleType,
    SessionTokenType,
    RentalStatus,
    RentalTriggerType,
    RentalFunnelStage,
    RentalSession,
    RentalOffer,
    RentalCreditBalance,
    RentalTransaction,
    FraudCheckResult,
    ConversionEvent,
    RentalSessionManager,
    RentalOfferEngine,
    RentalFraudDetector,
    ConversionTracker,
    get_session_manager,
    get_offer_engine,
    get_fraud_detector,
    get_conversion_tracker,
    TIME_PASS_PRICING,
    INFERENCE_BUNDLE_PRICING,
    SESSION_TOKEN_PRICING,
    RENTAL_CAPS_BY_TIER,
)

from .rental_ab_testing import (
    RentalExperimentType,
    ExperimentStatus as RentalExperimentStatus,
    RentalExperiment,
    Variant,
    ExperimentEvent,
    ExperimentResult,
    RentalABTestEngine,
    get_ab_test_engine,
    PRICING_EXPERIMENT_TEMPLATES,
    MESSAGING_EXPERIMENT_TEMPLATES,
    TRIGGER_EXPERIMENT_TEMPLATES,
)

from .rental_stripe import (
    RentalPaymentStatus,
    RefundReason,
    RentalPaymentIntent,
    RentalRefund,
    RentalPriceConfig,
    RentalStripeAdapter,
    get_rental_stripe_adapter,
)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # =========================================================================
    # Week 21A: Technical Layer
    # =========================================================================
    # Enums
    "BillingTier",
    "UsageMetricType",
    "PricingStrategy",
    "UpsellTriggerType",
    "RevenueEventType",
    "RiskPricingFactor",
    # Data Classes
    "UsageRecord",
    "TierPricing",
    "UpsellTrigger",
    "UpsellEvent",
    "RiskPricingProfile",
    "BillingPeriod",
    # Constants
    "DEFAULT_TIER_PRICING",
    "DEFAULT_UPSELL_TRIGGERS",
    # Classes
    "UsageMeter",
    "RiskPricingEngine",
    "UpsellEngine",
    "AdaptiveBillingController",
    # Bridge
    "BillingBridgeConfig",
    "BillingBridge",
    "TELEMETRY_TO_USAGE_MAP",
    # Factories
    "create_billing_controller",
    "create_usage_meter",
    "create_risk_engine",
    "create_upsell_engine",
    "create_billing_bridge",
    "create_full_billing_stack",
    
    # =========================================================================
    # StoryBrand Upsell Integration - Marketing Infrastructure
    # =========================================================================
    # Config
    "DeliveryChannel",
    "EmailProvider",
    "EmailConfig",
    "IntegrationConfig",
    # Services
    "EmailDeliveryService",
    "EmailDeliveryResult",
    "InAppDeliveryService",
    "InAppNotificationPayload",
    # Main integration
    "UpsellMessageIntegration",
    # Utilities
    "get_template_key_for_event",
    "TRIGGER_TO_TEMPLATE_MAP",
    # Factory
    "create_upsell_integration",
    "wire_integration_to_billing",
    # StoryBrand Messages
    "UPSELL_MESSAGES_STORYBRAND",
    "AB_TEST_FRAMEWORK",
    "personalize_upsell_message",
    # In-App Notifications
    "IN_APP_NOTIFICATIONS",
    "NotificationFormat",
    "get_notification_for_event",
    "evaluate_notification_triggers",
    # Awareness Routing
    "AwarenessStage",
    "AwarenessSignal",
    "AwarenessDetector",
    "AwarenessRouter",
    "AWARENESS_STAGE_ROUTING",
    "detect_awareness_stage",
    "route_by_awareness",
    # Landing Page Content
    "LANDING_PAGE_CONTENT",
    "get_landing_page_for_stage",
    
    # =========================================================================
    # Week 21B: Economic Layer
    # =========================================================================
    # Pricing Intents - Economic Brain
    "PricingIntent",
    "IntentConfidence",
    "IntentTrigger",
    "IntentAction",
    "IntentSignal",
    "IntentResult",
    "IntentPolicy",
    "IntentSignalsCollector",
    "IntentEvaluator",
    "PricingIntentsEngine",
    "create_intents_engine",
    "create_intent_policy",
    # Unit Normalization - Economic Backbone
    "UnitType",
    "UnitCategory",
    "ConversionStrategy",
    "ConversionRule",
    "NormalizedUnit",
    "UnitPricing",
    "NormalizationResult",
    "DEFAULT_CONVERSION_RULES",
    "DEFAULT_UNIT_PRICING",
    "UnitNormalizer",
    "UnitAggregator",
    "create_unit_normalizer",
    "create_unit_aggregator",
    # Billing Policy Tree - Economic Governance
    "PolicyDecision",
    "PolicyTrigger",
    "PolicyEscalation",
    "GracePeriodType",
    "PolicyContext",
    "PolicyResult",
    "PolicyRule",
    "TierPolicyConfig",
    "DEFAULT_POLICY_RULES",
    "DEFAULT_TIER_POLICIES",
    "BillingPolicyTree",
    "create_policy_tree",
    "create_policy_context",
    
    # =========================================================================
    # Week 22: Revenue Optimization & Predictive Forecasting
    # =========================================================================
    # Revenue Forecaster
    "ForecastModel",
    "ForecastPeriod",
    "ForecastConfig",
    "ForecastResult",
    "ChurnSignal",
    "ExpansionSignal",
    "TenantForecast",
    "RevenueProjection",
    "DEFAULT_FORECAST_CONFIG",
    "TimeSeriesBuffer",
    "RevenueForecaster",
    "create_revenue_forecaster",
    # Cohort Analytics
    "CohortType",
    "RetentionMetric",
    "ExpansionType",
    "ContractionType",
    "CustomerHealth",
    "CohortMember",
    "CohortSnapshot",
    "RetentionCurve",
    "CohortMetrics",
    "LTVEstimate",
    "CohortComparison",
    "DEFAULT_COHORT_CONFIG",
    "Cohort",
    "CohortAnalytics",
    "create_cohort_analytics",
    # Pricing Optimizer
    "ExperimentType",
    "ExperimentStatus",
    "PriceMetric",
    "ElasticityBand",
    "VariantAllocation",
    "PriceVariant",
    "ExperimentConfig",
    "ExperimentResult",
    "ElasticityResult",
    "PricePoint",
    "SimulationResult",
    "DEFAULT_OPTIMIZER_CONFIG",
    "PricingExperiment",
    "ElasticityAnalyzer",
    "PricingSimulator",
    "PricingOptimizer",
    "create_pricing_optimizer",
    # Revenue Alerts
    "AlertSeverity",
    "AlertCategory",
    "AlertStatus",
    "AlertChannel",
    "AnomalyType",
    "Alert",
    "AlertRule",
    "AlertSubscription",
    "MetricSnapshot",
    "RevenueHealthStatus",
    "DEFAULT_ALERT_CONFIG",
    "AnomalyDetector",
    "AlertManager",
    "RevenueAlertSystem",
    "create_revenue_alert_system",
    
    # =========================================================================
    # Week 23: Payment Gateway Adapters
    # =========================================================================
    # Payments Adapter (Abstract Interface)
    "PaymentsAdapter",
    "AdapterPaymentProvider",
    "AccountType",
    "SubscriptionStatus",
    "PaymentStatus",
    "InvoiceStatus",
    "WebhookEventType",
    "PriceType",
    "BillingInterval",
    "Address",
    "CustomerData",
    "PriceData",
    "SubscriptionData",
    "SubscriptionItemData",
    "UsageRecordData",
    "InvoiceData",
    "InvoiceLineData",
    "PaymentData",
    "RefundData",
    "AdapterWebhookEvent",
    "ConnectAccount",
    "AdapterResult",
    "AdapterConfig",
    "AdapterRegistry",
    "IDMappingStore",
    "InMemoryIDMappingStore",
    "create_adapter_config",
    "create_payments_adapter",
    "create_id_mapping_store",
    # Stripe Adapter
    "StripeAdapter",
    # Lago Adapter
    "LagoAdapter",
    # Webhook Dispatcher
    "WebhookStatus",
    "WebhookRecord",
    "DispatcherConfig",
    "WebhookDispatcher",
    "create_webhook_dispatcher",
    # Billing Integration
    "PaymentProvider",
    "BillingEvent",
    "UsageRecord",
    "PriceUpdate",
    "SubscriptionChange",
    "BillingIntegrationManager",
    "CustomerLifecycleManager",
    "create_billing_integration",
    
    # =========================================================================
    # Week 24: Revenue Reporting & Analytics
    # =========================================================================
    # Revenue Reporting
    "ReportPeriod",
    "RevenueSegment",
    "MetricType",
    "ReportFormat",
    "RevenueMetrics",
    "SubscriptionMetrics",
    "CustomerMetrics",
    "TierBreakdown",
    "RevenueReport",
    "LTVReport",
    "RevenueCalculator",
    "RevenueReportingEngine",
    "create_revenue_reporting_engine",
    # Billing Dashboards
    "WidgetType",
    "WidgetSize",
    "RefreshRate",
    "TrendDirection",
    "MetricValue",
    "ChartDataPoint",
    "ChartSeries",
    "WidgetConfig",
    "DashboardLayout",
    "WidgetData",
    "BillingWidgets",
    "WidgetDataProvider",
    "BillingDashboardManager",
    "create_billing_dashboard_manager",
    # Subscription Analytics
    "ChurnRisk",
    "HealthScore",
    "SubscriptionState",
    "MovementType",
    "ChurnRiskScore",
    "CustomerHealthScore",
    "SubscriptionMovement",
    "ExpansionOpportunity",
    "RenewalForecast",
    "ChurnPredictor",
    "CustomerHealthScorer",
    "SubscriptionAnalytics",
    "create_subscription_analytics",
    # Billing Exports
    "ExportFormat",
    "ExportScope",
    "CompressionType",
    "ScheduleFrequency",
    "ExportStatus",
    "ExportConfig",
    "ExportJob",
    "ScheduledReport",
    "ExportResult",
    "DataSerializer",
    "BillingExportEngine",
    "ReportScheduler",
    "create_billing_export_engine",
    "create_report_scheduler",
    
    # =========================================================================
    # Week 24b: Advanced Billing Infrastructure
    # =========================================================================
    # Fraud Detection
    "FraudRiskLevel",
    "FraudSignalType",
    "FraudDecisionAction",
    "FraudSignal",
    "RadarReview",
    "RiskScore",
    "FraudDecision",
    "AbusePattern",
    "FraudConfig",
    "StripeRadarIntegration",
    "InternalRiskMesh",
    "FraudDetectionEngine",
    "create_fraud_detection_engine",
    # Billing State Machine
    "SubscriptionState",
    "TransitionTrigger",
    "StateTransitionResult",
    "StateTransition",
    "StateContext",
    "TenantBillingState",
    "TransitionGuard",
    "StateHook",
    "BillingStateMachine",
    "MultiTenantStateManager",
    "create_billing_state_machine",
    "create_state_manager",
    # Contract Enforcement
    "ContractType",
    "CommitmentType",
    "SLATier",
    "ViolationType",
    "ContractStatus",
    "ContractTerms",
    "UsageCommitment",
    "SLADefinition",
    "SLAViolation",
    "ContractViolation",
    "EnforcementAction",
    "ContractValidator",
    "SLATracker",
    "ContractEnforcementEngine",
    "create_contract_enforcement_engine",
    # Limits Gateway
    "LimitType",
    "GatewayEnforcementAction",
    "LimitScope",
    "QuotaLimit",
    "RateLimitConfig",
    "LimitCheckResult",
    "QuotaUsage",
    "ThrottleDecision",
    "LimitViolation",
    "QuotaEnforcer",
    "RateLimitEnforcer",
    "LimitsGateway",
    "BillingGatewaySync",
    "create_limits_gateway",
    "create_billing_gateway_sync",
    # Entitlement Engine
    "EntitlementType",
    "FeatureFlagState",
    "TierLevel",
    "FeatureFlag",
    "EntitlementGrant",
    "EntitlementCheckResult",
    "ConnectAccountMapping",
    "EntitlementCache",
    "FeatureFlagManager",
    "SaaSEntitlementEngine",
    "DEFAULT_FEATURE_FLAGS",
    "create_entitlement_engine",
    # Stripe FastAPI Integration
    "StripeConfig",
    "ProcessedStripeEvent",
    "IdempotencyStore",
    "TenantMapping",
    "TenantResolver",
    "StripeAdapterEnhanced",
    "WebhookEventRouter",
    "get_stripe_adapter",
    "get_idempotency_store",
    "get_tenant_resolver",
    "configure_stripe_adapter",
    "create_stripe_webhook_router",
    "get_metadata_schema",
    "METADATA_SCHEMA",
    # Stripe Persistence Layer
    "ProcessedStripeEventModel",
    "TenantMappingModel",
    "PersistentIdempotencyStore",
    "PersistentTenantResolver",
    "RedisCache",
    "ProcessedEvent",
    "EngineWiring",
    "StripeEnvironmentConfig",
    "create_env_template",
    "create_persistent_stripe_router",
    "WEBHOOK_REGISTRATION_GUIDE",
    "print_webhook_registration_guide",
    "SQLALCHEMY_AVAILABLE",
    "REDIS_AVAILABLE",
    
    # =========================================================================
    # Phase 1: Value-Based Pricing & Customer Intelligence
    # =========================================================================
    # Value-Based Pricing Engine
    "KRLTier",
    "CustomerSegment",
    "ROIMetrics",
    "ValuePricingResult",
    "CustomerValueProfile",
    "ABTestConfig",
    "ABTestResult",
    "ValueBasedPricingEngine",
    "CustomerSegmentationEngine",
    "PriceOptimizer",
    "calculate_value_based_price",
    "segment_customer",
    "get_recommended_tier",
    "get_stripe_value_metadata",
    # Multi-Year Contract Management
    "ContractTypeEnum",
    "ContractStatusEnum",
    "PaymentTerms",
    "CreditType",
    "VolumeDiscount",
    "PrepaidCredit",
    "SLATerms",
    "ContractTermsModel",
    "RenewalOffer",
    "ContractPricingEngine",
    "PrepaidCreditManager",
    "ContractManager",
    "calculate_enterprise_pricing",
    "create_enterprise_contract",
    "purchase_api_credits",
    "get_stripe_contract_metadata",
    "sync_contract_to_stripe",
    # Customer Health Scoring
    "HealthCategory",
    "ChurnRiskLevel",
    "InterventionType",
    "UsageMetricsModel",
    "HealthScoreModel",
    "ChurnPrediction",
    "ExpansionOpportunityModel",
    "HealthScoringEngine",
    "ChurnPredictionModel",
    "ExpansionDetector",
    "calculate_customer_health",
    "predict_customer_churn",
    "find_expansion_opportunities",
    "get_stripe_health_metadata",
    # Currency Utilities
    "CurrencyCode",
    "Money",
    "InvoiceLineItem",
    "round_currency",
    "to_cents",
    "from_cents",
    "safe_decimal",
    "apply_percentage",
    "apply_currency_discount",
    "format_currency",
    "usd",
    "eur",
    "gbp",
    "TWO_PLACES",
    "FOUR_PLACES",
    "CurrencyError",
    "InvalidAmountError",
    "CurrencyMismatchError",
    # Centralized Enums
    "BillingTierEnum",
    "ContractTypeBase",
    "ContractStatusBase",
    "PaymentTermsBase",
    "HealthCategoryBase",
    "ChurnRiskBase",
    "InterventionTypeBase",
    "ExperimentStatus",
    # Stripe Metadata Security
    "StripeMetadataWriter",
    "MetadataValidationError",
    "sanitize_metadata_value",
    "ALLOWED_METADATA_KEYS",
    # =========================================================================
    # Phase 6: Temporary Model Rental System
    # =========================================================================
    # Rental Core API
    "RentalMechanismType",
    "TimePassType",
    "InferenceBundleType",
    "SessionTokenType",
    "RentalStatus",
    "RentalTriggerType",
    "RentalFunnelStage",
    "RentalSession",
    "RentalOffer",
    "RentalCreditBalance",
    "RentalTransaction",
    "FraudCheckResult",
    "ConversionEvent",
    "RentalSessionManager",
    "RentalOfferEngine",
    "RentalFraudDetector",
    "ConversionTracker",
    "get_session_manager",
    "get_offer_engine",
    "get_fraud_detector",
    "get_conversion_tracker",
    "TIME_PASS_PRICING",
    "INFERENCE_BUNDLE_PRICING",
    "SESSION_TOKEN_PRICING",
    "RENTAL_CAPS_BY_TIER",
    # Rental A/B Testing
    "RentalExperimentType",
    "RentalExperiment",
    "Variant",
    "ExperimentEvent",
    "ExperimentResult",
    "RentalABTestEngine",
    "get_ab_test_engine",
    "PRICING_EXPERIMENT_TEMPLATES",
    "MESSAGING_EXPERIMENT_TEMPLATES",
    "TRIGGER_EXPERIMENT_TEMPLATES",
    # Rental Stripe Integration
    "RentalPaymentStatus",
    "RefundReason",
    "RentalPaymentIntent",
    "RentalRefund",
    "RentalPriceConfig",
    "RentalStripeAdapter",
    "get_rental_stripe_adapter",
]
