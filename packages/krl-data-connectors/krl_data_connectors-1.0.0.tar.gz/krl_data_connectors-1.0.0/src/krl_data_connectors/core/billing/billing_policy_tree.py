# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Billing Policy Tree - DEPRECATED

⚠️ DEPRECATION WARNING (Dec 2025):
This module has been moved to krl-premium-backend.
Import from: app.services.billing.billing_policy_tree

This stub remains for backward compatibility but will be removed in v2.0.
"""

from __future__ import annotations

import warnings
warnings.warn(
    "krl_data_connectors.core.billing.billing_policy_tree is deprecated. "
    "This module has moved to krl-premium-backend. "
    "Import from 'app.services.billing.billing_policy_tree' instead.",
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

class PolicyDecision(Enum):
    """Decisions the policy tree can make."""
    # Allow
    ALLOW = "allow"                      # No intervention
    ALLOW_WITH_WARNING = "allow_warning"  # Allow but notify
    ALLOW_WITH_OVERAGE = "allow_overage"  # Allow with overage charges
    
    # Throttle
    SOFT_THROTTLE = "soft_throttle"      # Reduce rate limits
    HARD_THROTTLE = "hard_throttle"      # Aggressive rate limiting
    
    # Block
    SOFT_BLOCK = "soft_block"            # Block non-essential features
    HARD_BLOCK = "hard_block"            # Block all usage
    
    # Upgrade
    SUGGEST_UPGRADE = "suggest_upgrade"  # Recommend tier upgrade
    REQUIRE_UPGRADE = "require_upgrade"  # Force tier upgrade
    AUTO_UPGRADE = "auto_upgrade"        # Automatic tier upgrade
    
    # Remediation
    GRACE_PERIOD = "grace_period"        # Grant temporary grace
    SAFETY_NET = "safety_net"            # Apply safety net policy
    MANUAL_REVIEW = "manual_review"      # Flag for human review


class PolicyTrigger(Enum):
    """What triggered the policy evaluation."""
    # Threshold triggers
    THRESHOLD_80 = "threshold_80"        # 80% of limit
    THRESHOLD_100 = "threshold_100"      # 100% of limit
    THRESHOLD_120 = "threshold_120"      # 120% of limit (overage)
    THRESHOLD_150 = "threshold_150"      # 150% of limit (severe)
    
    # Burst triggers
    BURST_DETECTED = "burst_detected"    # Anomalous usage spike
    VELOCITY_EXCEEDED = "velocity_exceeded"  # Usage growth too fast
    
    # Pattern triggers
    RECURRING_VIOLATION = "recurring_violation"  # Repeated violations
    ABUSE_PATTERN = "abuse_pattern"       # Suspicious patterns
    FRAUD_SIGNAL = "fraud_signal"         # Potential fraud
    
    # Temporal triggers
    END_OF_PERIOD = "end_of_period"       # Approaching billing cycle end
    MID_PERIOD_SPIKE = "mid_period_spike"  # Unusual mid-period activity
    
    # External triggers
    PAYMENT_FAILED = "payment_failed"     # Payment processing failed
    ACCOUNT_FLAG = "account_flag"         # Account flagged by support


class PolicyEscalation(Enum):
    """Escalation levels for policy decisions."""
    NONE = "none"            # No escalation
    LOW = "low"              # Automated handling
    MEDIUM = "medium"        # Notify account team
    HIGH = "high"            # Notify management
    CRITICAL = "critical"    # Immediate action required


class GracePeriodType(Enum):
    """Types of grace periods."""
    FIRST_OFFENSE = "first_offense"      # First-time violation
    GOOD_STANDING = "good_standing"      # Long-term customer benefit
    PROMOTIONAL = "promotional"          # Promotional grace
    EMERGENCY = "emergency"              # Emergency extension
    NONE = "none"                        # No grace period


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class PolicyContext:
    """Context for policy evaluation."""
    tenant_id: str
    tier: str
    
    # Current usage state
    current_usage: Decimal
    limit: Decimal
    utilization_rate: float  # 0-1
    
    # Historical context
    previous_period_usage: Optional[Decimal] = None
    average_usage: Optional[Decimal] = None
    violation_count: int = 0
    days_since_last_violation: Optional[int] = None
    
    # Account health
    account_age_days: int = 0
    payment_status: str = "current"  # current, overdue, suspended
    customer_health_score: float = 1.0  # 0-1
    
    # Burst detection
    burst_magnitude: float = 0.0  # How much above normal
    velocity_rate: float = 0.0   # Usage growth rate
    
    # External flags
    manual_override: bool = False
    support_flag: Optional[str] = None
    
    # Timing
    days_remaining_in_period: int = 30
    is_end_of_period: bool = False
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyResult:
    """Result of policy evaluation."""
    decision: PolicyDecision
    trigger: PolicyTrigger
    escalation: PolicyEscalation
    
    # Context
    tenant_id: str
    evaluated_at: datetime = field(default_factory=datetime.now)
    
    # Decision details
    reason: str = ""
    confidence: float = 1.0  # 0-1
    
    # Actions
    actions: List[str] = field(default_factory=list)
    notifications: List[str] = field(default_factory=list)
    
    # Grace period
    grace_period: Optional[GracePeriodType] = None
    grace_expiry: Optional[datetime] = None
    
    # Limits adjustment
    new_soft_limit: Optional[Decimal] = None
    new_hard_limit: Optional[Decimal] = None
    overage_rate: Optional[Decimal] = None
    
    # Billing impact
    penalty_amount: Decimal = Decimal("0")
    credit_amount: Decimal = Decimal("0")
    
    # Next evaluation
    re_evaluate_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision.value,
            "trigger": self.trigger.value,
            "escalation": self.escalation.value,
            "tenant_id": self.tenant_id,
            "evaluated_at": self.evaluated_at.isoformat(),
            "reason": self.reason,
            "confidence": self.confidence,
            "actions": self.actions,
            "grace_period": self.grace_period.value if self.grace_period else None,
            "penalty_amount": str(self.penalty_amount),
        }


@dataclass
class PolicyRule:
    """A rule in the policy tree."""
    rule_id: str
    name: str
    description: str
    
    # Trigger conditions
    trigger: PolicyTrigger
    min_utilization: float = 0.0
    max_utilization: float = 2.0
    
    # Tier applicability
    applicable_tiers: Set[str] = field(default_factory=lambda: {"community", "pro", "enterprise"})
    
    # Decision
    decision: PolicyDecision = PolicyDecision.ALLOW
    
    # Conditions
    require_violation_count: int = 0
    require_burst_magnitude: float = 0.0
    require_good_standing: bool = False
    
    # Grace period
    grace_period_type: GracePeriodType = GracePeriodType.NONE
    grace_period_hours: int = 0
    
    # Escalation
    escalation: PolicyEscalation = PolicyEscalation.NONE
    
    # Actions
    actions: List[str] = field(default_factory=list)
    notifications: List[str] = field(default_factory=list)
    
    # Limits
    apply_overage: bool = False
    overage_multiplier: Decimal = Decimal("1.5")
    adjust_soft_limit: Optional[float] = None  # Multiplier
    adjust_hard_limit: Optional[float] = None
    
    # Priority (higher = evaluated first)
    priority: int = 0
    
    # Enabled
    enabled: bool = True


@dataclass
class TierPolicyConfig:
    """Policy configuration for a specific tier."""
    tier: str
    
    # Thresholds
    soft_warning_threshold: float = 0.80
    hard_warning_threshold: float = 0.90
    overage_threshold: float = 1.00
    emergency_threshold: float = 1.20
    
    # Burst detection
    burst_detection_enabled: bool = True
    burst_threshold_multiplier: float = 3.0  # 3x normal
    velocity_threshold_per_hour: float = 0.10  # 10% per hour
    
    # Grace periods
    grace_period_enabled: bool = True
    first_offense_grace_hours: int = 24
    good_standing_grace_hours: int = 72
    max_grace_periods_per_year: int = 3
    
    # Overages
    overage_allowed: bool = True
    max_overage_percent: float = 0.50  # Max 50% over
    overage_rate_multiplier: Decimal = Decimal("1.5")
    
    # Safety nets
    safety_net_enabled: bool = True
    safety_net_cap_percent: float = 2.00  # Cap at 200%
    
    # Escalation
    auto_escalate_violations: int = 3  # After 3 violations


# =============================================================================
# Default Policy Rules
# =============================================================================

DEFAULT_POLICY_RULES: List[PolicyRule] = [
    # ==========================================================================
    # 80% Threshold Rules
    # ==========================================================================
    PolicyRule(
        rule_id="threshold_80_warning",
        name="80% Usage Warning",
        description="Soft warning at 80% of limit",
        trigger=PolicyTrigger.THRESHOLD_80,
        min_utilization=0.80,
        max_utilization=0.90,
        decision=PolicyDecision.ALLOW_WITH_WARNING,
        actions=["log_warning", "update_dashboard"],
        notifications=["email_usage_alert"],
        escalation=PolicyEscalation.NONE,
        priority=10,
    ),
    PolicyRule(
        rule_id="threshold_80_upgrade_hint",
        name="80% Upgrade Suggestion",
        description="Suggest upgrade at 80% for community tier",
        trigger=PolicyTrigger.THRESHOLD_80,
        min_utilization=0.80,
        max_utilization=0.90,
        applicable_tiers={"community"},
        decision=PolicyDecision.SUGGEST_UPGRADE,
        actions=["show_upgrade_prompt", "track_upsell"],
        notifications=["email_upgrade_suggestion"],
        escalation=PolicyEscalation.NONE,
        priority=15,
    ),
    
    # ==========================================================================
    # 100% Threshold Rules
    # ==========================================================================
    PolicyRule(
        rule_id="threshold_100_community_block",
        name="Community Tier Hard Limit",
        description="Block at 100% for community tier",
        trigger=PolicyTrigger.THRESHOLD_100,
        min_utilization=1.00,
        max_utilization=1.10,
        applicable_tiers={"community"},
        decision=PolicyDecision.REQUIRE_UPGRADE,
        actions=["block_new_requests", "show_upgrade_modal"],
        notifications=["email_limit_reached", "slack_alert"],
        escalation=PolicyEscalation.LOW,
        priority=50,
    ),
    PolicyRule(
        rule_id="threshold_100_pro_overage",
        name="Pro Tier Overage Start",
        description="Allow overage at 100% for pro tier",
        trigger=PolicyTrigger.THRESHOLD_100,
        min_utilization=1.00,
        max_utilization=1.20,
        applicable_tiers={"pro"},
        decision=PolicyDecision.ALLOW_WITH_OVERAGE,
        apply_overage=True,
        overage_multiplier=Decimal("1.5"),
        actions=["enable_overage_billing", "log_overage"],
        notifications=["email_overage_started"],
        escalation=PolicyEscalation.NONE,
        priority=50,
    ),
    PolicyRule(
        rule_id="threshold_100_enterprise_allow",
        name="Enterprise Tier Soft Overage",
        description="Soft overage at 100% for enterprise",
        trigger=PolicyTrigger.THRESHOLD_100,
        min_utilization=1.00,
        max_utilization=1.50,
        applicable_tiers={"enterprise"},
        decision=PolicyDecision.ALLOW_WITH_WARNING,
        apply_overage=True,
        overage_multiplier=Decimal("1.25"),  # Lower rate for enterprise
        actions=["log_overage", "update_account_team"],
        notifications=["email_account_team"],
        escalation=PolicyEscalation.NONE,
        priority=50,
    ),
    
    # ==========================================================================
    # 120% Threshold Rules (Emergency)
    # ==========================================================================
    PolicyRule(
        rule_id="threshold_120_pro_throttle",
        name="Pro Tier Emergency Throttle",
        description="Throttle at 120% for pro tier",
        trigger=PolicyTrigger.THRESHOLD_120,
        min_utilization=1.20,
        max_utilization=1.50,
        applicable_tiers={"pro"},
        decision=PolicyDecision.HARD_THROTTLE,
        apply_overage=True,
        overage_multiplier=Decimal("2.0"),
        actions=["throttle_requests", "log_emergency"],
        notifications=["email_emergency_throttle", "slack_urgent"],
        escalation=PolicyEscalation.MEDIUM,
        priority=80,
    ),
    PolicyRule(
        rule_id="threshold_120_enterprise_warn",
        name="Enterprise Tier High Overage",
        description="Warning at 120% for enterprise",
        trigger=PolicyTrigger.THRESHOLD_120,
        min_utilization=1.20,
        max_utilization=2.00,
        applicable_tiers={"enterprise"},
        decision=PolicyDecision.ALLOW_WITH_OVERAGE,
        apply_overage=True,
        overage_multiplier=Decimal("1.5"),
        actions=["log_high_overage", "schedule_review"],
        notifications=["email_account_manager", "slack_account_team"],
        escalation=PolicyEscalation.MEDIUM,
        priority=80,
    ),
    
    # ==========================================================================
    # 150% Threshold Rules (Critical)
    # ==========================================================================
    PolicyRule(
        rule_id="threshold_150_safety_net",
        name="Safety Net Activation",
        description="Apply safety net at 150%",
        trigger=PolicyTrigger.THRESHOLD_150,
        min_utilization=1.50,
        max_utilization=2.00,
        decision=PolicyDecision.SAFETY_NET,
        apply_overage=True,
        overage_multiplier=Decimal("2.5"),
        adjust_hard_limit=1.50,  # Cap at 150%
        actions=["activate_safety_net", "cap_usage"],
        notifications=["email_safety_net", "slack_urgent", "page_oncall"],
        escalation=PolicyEscalation.HIGH,
        priority=90,
    ),
    
    # ==========================================================================
    # Burst Detection Rules
    # ==========================================================================
    PolicyRule(
        rule_id="burst_community_block",
        name="Community Burst Block",
        description="Block bursts for community tier",
        trigger=PolicyTrigger.BURST_DETECTED,
        require_burst_magnitude=3.0,
        applicable_tiers={"community"},
        decision=PolicyDecision.HARD_BLOCK,
        actions=["block_burst", "flag_review"],
        notifications=["email_burst_blocked"],
        escalation=PolicyEscalation.LOW,
        priority=95,
    ),
    PolicyRule(
        rule_id="burst_pro_throttle",
        name="Pro Burst Throttle",
        description="Throttle bursts for pro tier",
        trigger=PolicyTrigger.BURST_DETECTED,
        require_burst_magnitude=3.0,
        applicable_tiers={"pro"},
        decision=PolicyDecision.SOFT_THROTTLE,
        actions=["throttle_burst", "log_burst"],
        notifications=["email_burst_detected"],
        escalation=PolicyEscalation.NONE,
        priority=95,
    ),
    PolicyRule(
        rule_id="burst_enterprise_allow",
        name="Enterprise Burst Allow",
        description="Allow bursts for enterprise with monitoring",
        trigger=PolicyTrigger.BURST_DETECTED,
        require_burst_magnitude=3.0,
        applicable_tiers={"enterprise"},
        decision=PolicyDecision.ALLOW_WITH_WARNING,
        actions=["monitor_burst", "log_burst"],
        notifications=["slack_account_team"],
        escalation=PolicyEscalation.NONE,
        priority=95,
    ),
    
    # ==========================================================================
    # Recurring Violation Rules
    # ==========================================================================
    PolicyRule(
        rule_id="recurring_violations_escalate",
        name="Recurring Violations Escalation",
        description="Escalate after 3+ violations",
        trigger=PolicyTrigger.RECURRING_VIOLATION,
        require_violation_count=3,
        decision=PolicyDecision.MANUAL_REVIEW,
        actions=["flag_for_review", "limit_features"],
        notifications=["email_account_review", "slack_management"],
        escalation=PolicyEscalation.HIGH,
        priority=85,
    ),
    PolicyRule(
        rule_id="recurring_violations_suspend",
        name="Recurring Violations Suspension",
        description="Suspend after 5+ violations",
        trigger=PolicyTrigger.RECURRING_VIOLATION,
        require_violation_count=5,
        decision=PolicyDecision.HARD_BLOCK,
        actions=["suspend_account", "require_review"],
        notifications=["email_suspension", "slack_legal"],
        escalation=PolicyEscalation.CRITICAL,
        priority=100,
    ),
    
    # ==========================================================================
    # Abuse Detection Rules
    # ==========================================================================
    PolicyRule(
        rule_id="abuse_pattern_block",
        name="Abuse Pattern Block",
        description="Block detected abuse patterns",
        trigger=PolicyTrigger.ABUSE_PATTERN,
        decision=PolicyDecision.HARD_BLOCK,
        actions=["block_abuse", "capture_evidence", "flag_legal"],
        notifications=["email_abuse_detected", "slack_security", "page_security"],
        escalation=PolicyEscalation.CRITICAL,
        priority=100,
    ),
    PolicyRule(
        rule_id="fraud_signal_review",
        name="Fraud Signal Review",
        description="Flag fraud signals for review",
        trigger=PolicyTrigger.FRAUD_SIGNAL,
        decision=PolicyDecision.MANUAL_REVIEW,
        actions=["flag_fraud", "capture_evidence", "limit_features"],
        notifications=["email_fraud_alert", "slack_finance"],
        escalation=PolicyEscalation.HIGH,
        priority=100,
    ),
    
    # ==========================================================================
    # Grace Period Rules
    # ==========================================================================
    PolicyRule(
        rule_id="first_offense_grace",
        name="First Offense Grace Period",
        description="Grant grace period for first-time violations",
        trigger=PolicyTrigger.THRESHOLD_100,
        require_violation_count=0,
        require_good_standing=True,
        decision=PolicyDecision.GRACE_PERIOD,
        grace_period_type=GracePeriodType.FIRST_OFFENSE,
        grace_period_hours=24,
        actions=["grant_grace", "log_grace"],
        notifications=["email_grace_granted"],
        escalation=PolicyEscalation.NONE,
        priority=60,
    ),
    PolicyRule(
        rule_id="good_standing_grace",
        name="Good Standing Grace Period",
        description="Extended grace for long-term customers",
        trigger=PolicyTrigger.THRESHOLD_100,
        require_good_standing=True,
        decision=PolicyDecision.GRACE_PERIOD,
        grace_period_type=GracePeriodType.GOOD_STANDING,
        grace_period_hours=72,
        actions=["grant_extended_grace", "log_grace"],
        notifications=["email_grace_granted"],
        escalation=PolicyEscalation.NONE,
        priority=55,
    ),
    
    # ==========================================================================
    # Payment-Related Rules
    # ==========================================================================
    PolicyRule(
        rule_id="payment_failed_throttle",
        name="Payment Failed Throttle",
        description="Throttle usage when payment fails",
        trigger=PolicyTrigger.PAYMENT_FAILED,
        decision=PolicyDecision.SOFT_THROTTLE,
        actions=["throttle_usage", "retry_payment"],
        notifications=["email_payment_failed", "sms_payment_alert"],
        escalation=PolicyEscalation.MEDIUM,
        priority=75,
    ),
    PolicyRule(
        rule_id="payment_failed_block",
        name="Payment Failed Block",
        description="Block usage after extended payment failure",
        trigger=PolicyTrigger.PAYMENT_FAILED,
        require_violation_count=3,  # 3 failed payment attempts
        decision=PolicyDecision.SOFT_BLOCK,
        actions=["block_premium_features", "require_payment"],
        notifications=["email_payment_required", "slack_finance"],
        escalation=PolicyEscalation.HIGH,
        priority=85,
    ),
]


# =============================================================================
# Default Tier Policies
# =============================================================================

DEFAULT_TIER_POLICIES: Dict[str, TierPolicyConfig] = {
    "community": TierPolicyConfig(
        tier="community",
        soft_warning_threshold=0.70,
        hard_warning_threshold=0.85,
        overage_threshold=1.00,
        emergency_threshold=1.00,  # No overage for community
        burst_detection_enabled=True,
        burst_threshold_multiplier=2.0,
        velocity_threshold_per_hour=0.05,
        grace_period_enabled=True,
        first_offense_grace_hours=12,
        good_standing_grace_hours=24,
        max_grace_periods_per_year=2,
        overage_allowed=False,
        safety_net_enabled=False,
        auto_escalate_violations=2,
    ),
    "pro": TierPolicyConfig(
        tier="pro",
        soft_warning_threshold=0.80,
        hard_warning_threshold=0.90,
        overage_threshold=1.00,
        emergency_threshold=1.30,
        burst_detection_enabled=True,
        burst_threshold_multiplier=3.0,
        velocity_threshold_per_hour=0.10,
        grace_period_enabled=True,
        first_offense_grace_hours=24,
        good_standing_grace_hours=48,
        max_grace_periods_per_year=4,
        overage_allowed=True,
        max_overage_percent=0.30,
        overage_rate_multiplier=Decimal("1.5"),
        safety_net_enabled=True,
        safety_net_cap_percent=1.50,
        auto_escalate_violations=3,
    ),
    "enterprise": TierPolicyConfig(
        tier="enterprise",
        soft_warning_threshold=0.85,
        hard_warning_threshold=0.95,
        overage_threshold=1.00,
        emergency_threshold=1.50,
        burst_detection_enabled=True,
        burst_threshold_multiplier=5.0,
        velocity_threshold_per_hour=0.20,
        grace_period_enabled=True,
        first_offense_grace_hours=48,
        good_standing_grace_hours=72,
        max_grace_periods_per_year=6,
        overage_allowed=True,
        max_overage_percent=0.50,
        overage_rate_multiplier=Decimal("1.25"),
        safety_net_enabled=True,
        safety_net_cap_percent=2.00,
        auto_escalate_violations=5,
    ),
}


# =============================================================================
# Policy Tree Evaluator
# =============================================================================

class BillingPolicyTree:
    """
    Evaluates billing policies based on context.
    
    Implements a decision tree that considers:
    - Usage thresholds
    - Account health
    - Historical patterns
    - Tier-specific rules
    """
    
    def __init__(
        self,
        rules: Optional[List[PolicyRule]] = None,
        tier_policies: Optional[Dict[str, TierPolicyConfig]] = None,
    ):
        self._rules = sorted(
            rules or DEFAULT_POLICY_RULES,
            key=lambda r: r.priority,
            reverse=True,
        )
        self._tier_policies = tier_policies or dict(DEFAULT_TIER_POLICIES)
        
        # History tracking
        self._decision_history: Dict[str, List[PolicyResult]] = {}
        self._grace_periods: Dict[str, List[datetime]] = {}  # tenant -> expiries
        
        # Callbacks
        self._action_handlers: Dict[str, List[Callable]] = {}
        
        logger.info(f"BillingPolicyTree initialized with {len(self._rules)} rules")
    
    def evaluate(self, context: PolicyContext) -> PolicyResult:
        """
        Evaluate policy for a given context.
        
        Returns the highest-priority matching rule's decision.
        """
        tier_policy = self._tier_policies.get(context.tier)
        if not tier_policy:
            tier_policy = DEFAULT_TIER_POLICIES.get("community")
        
        # Determine trigger
        trigger = self._determine_trigger(context, tier_policy)
        
        # Check for active grace period
        if self._has_active_grace(context.tenant_id):
            return self._create_grace_result(context, trigger)
        
        # Find matching rules
        matching_rules = self._find_matching_rules(context, trigger, tier_policy)
        
        if not matching_rules:
            return self._create_default_result(context, trigger)
        
        # Apply highest priority rule
        rule = matching_rules[0]
        result = self._apply_rule(context, rule, trigger, tier_policy)
        
        # Store in history
        self._store_result(result)
        
        # Dispatch actions
        self._dispatch_actions(result)
        
        return result
    
    def _determine_trigger(
        self,
        context: PolicyContext,
        tier_policy: TierPolicyConfig,
    ) -> PolicyTrigger:
        """Determine the primary trigger for policy evaluation."""
        # Check for external triggers first
        if context.payment_status == "failed":
            return PolicyTrigger.PAYMENT_FAILED
        if context.support_flag == "abuse":
            return PolicyTrigger.ABUSE_PATTERN
        if context.support_flag == "fraud":
            return PolicyTrigger.FRAUD_SIGNAL
        
        # Check for recurring violations
        if context.violation_count >= tier_policy.auto_escalate_violations:
            return PolicyTrigger.RECURRING_VIOLATION
        
        # Check for burst
        if (tier_policy.burst_detection_enabled and 
            context.burst_magnitude >= tier_policy.burst_threshold_multiplier):
            return PolicyTrigger.BURST_DETECTED
        
        # Check for velocity
        if (tier_policy.burst_detection_enabled and
            context.velocity_rate >= tier_policy.velocity_threshold_per_hour):
            return PolicyTrigger.VELOCITY_EXCEEDED
        
        # Check threshold triggers
        if context.utilization_rate >= 1.50:
            return PolicyTrigger.THRESHOLD_150
        elif context.utilization_rate >= 1.20:
            return PolicyTrigger.THRESHOLD_120
        elif context.utilization_rate >= 1.00:
            return PolicyTrigger.THRESHOLD_100
        elif context.utilization_rate >= 0.80:
            return PolicyTrigger.THRESHOLD_80
        
        # Temporal triggers
        if context.is_end_of_period:
            return PolicyTrigger.END_OF_PERIOD
        
        return PolicyTrigger.THRESHOLD_80  # Default
    
    def _find_matching_rules(
        self,
        context: PolicyContext,
        trigger: PolicyTrigger,
        tier_policy: TierPolicyConfig,
    ) -> List[PolicyRule]:
        """Find all matching rules for the context."""
        matching = []
        
        for rule in self._rules:
            if not rule.enabled:
                continue
            
            # Check tier applicability
            if context.tier not in rule.applicable_tiers:
                continue
            
            # Check trigger match
            if rule.trigger != trigger:
                continue
            
            # Check utilization range
            if not (rule.min_utilization <= context.utilization_rate <= rule.max_utilization):
                continue
            
            # Check violation count
            if rule.require_violation_count > context.violation_count:
                continue
            
            # Check burst magnitude
            if rule.require_burst_magnitude > 0:
                if context.burst_magnitude < rule.require_burst_magnitude:
                    continue
            
            # Check good standing
            if rule.require_good_standing:
                if context.customer_health_score < 0.7:
                    continue
            
            matching.append(rule)
        
        return matching
    
    def _apply_rule(
        self,
        context: PolicyContext,
        rule: PolicyRule,
        trigger: PolicyTrigger,
        tier_policy: TierPolicyConfig,
    ) -> PolicyResult:
        """Apply a matched rule to create a result."""
        result = PolicyResult(
            decision=rule.decision,
            trigger=trigger,
            escalation=rule.escalation,
            tenant_id=context.tenant_id,
            reason=rule.description,
            actions=list(rule.actions),
            notifications=list(rule.notifications),
        )
        
        # Handle grace period
        if rule.grace_period_type != GracePeriodType.NONE:
            result.grace_period = rule.grace_period_type
            result.grace_expiry = datetime.now() + timedelta(hours=rule.grace_period_hours)
            self._record_grace_period(context.tenant_id, result.grace_expiry)
        
        # Handle overage
        if rule.apply_overage:
            result.overage_rate = rule.overage_multiplier
            
            # Calculate penalty
            if context.utilization_rate > 1.0:
                overage_units = context.current_usage - context.limit
                result.penalty_amount = overage_units * rule.overage_multiplier
        
        # Handle limit adjustments
        if rule.adjust_soft_limit is not None:
            result.new_soft_limit = context.limit * Decimal(str(rule.adjust_soft_limit))
        if rule.adjust_hard_limit is not None:
            result.new_hard_limit = context.limit * Decimal(str(rule.adjust_hard_limit))
        
        # Set re-evaluation time
        if rule.decision in (PolicyDecision.GRACE_PERIOD, PolicyDecision.SOFT_THROTTLE):
            result.re_evaluate_at = datetime.now() + timedelta(hours=1)
        elif rule.decision in (PolicyDecision.MANUAL_REVIEW,):
            result.re_evaluate_at = datetime.now() + timedelta(hours=24)
        
        return result
    
    def _create_default_result(
        self,
        context: PolicyContext,
        trigger: PolicyTrigger,
    ) -> PolicyResult:
        """Create default result when no rules match."""
        return PolicyResult(
            decision=PolicyDecision.ALLOW,
            trigger=trigger,
            escalation=PolicyEscalation.NONE,
            tenant_id=context.tenant_id,
            reason="No policy violation detected",
        )
    
    def _create_grace_result(
        self,
        context: PolicyContext,
        trigger: PolicyTrigger,
    ) -> PolicyResult:
        """Create result for active grace period."""
        return PolicyResult(
            decision=PolicyDecision.ALLOW_WITH_WARNING,
            trigger=trigger,
            escalation=PolicyEscalation.NONE,
            tenant_id=context.tenant_id,
            reason="Grace period active",
            grace_period=GracePeriodType.GOOD_STANDING,  # Existing grace
            actions=["log_grace_usage"],
        )
    
    # =========================================================================
    # Grace Period Management
    # =========================================================================
    
    def _has_active_grace(self, tenant_id: str) -> bool:
        """Check if tenant has active grace period."""
        periods = self._grace_periods.get(tenant_id, [])
        now = datetime.now()
        
        # Clean expired and check for active
        active = [p for p in periods if p > now]
        self._grace_periods[tenant_id] = active
        
        return len(active) > 0
    
    def _record_grace_period(self, tenant_id: str, expiry: datetime) -> None:
        """Record a new grace period."""
        if tenant_id not in self._grace_periods:
            self._grace_periods[tenant_id] = []
        self._grace_periods[tenant_id].append(expiry)
    
    def get_grace_status(self, tenant_id: str) -> Optional[datetime]:
        """Get grace period expiry for tenant."""
        periods = self._grace_periods.get(tenant_id, [])
        now = datetime.now()
        active = [p for p in periods if p > now]
        
        if active:
            return max(active)
        return None
    
    # =========================================================================
    # History & Actions
    # =========================================================================
    
    def _store_result(self, result: PolicyResult) -> None:
        """Store result in history."""
        tenant_id = result.tenant_id
        if tenant_id not in self._decision_history:
            self._decision_history[tenant_id] = []
        
        self._decision_history[tenant_id].append(result)
        
        # Trim history
        self._decision_history[tenant_id] = self._decision_history[tenant_id][-100:]
    
    def get_history(
        self,
        tenant_id: str,
        limit: int = 10,
    ) -> List[PolicyResult]:
        """Get policy decision history for tenant."""
        history = self._decision_history.get(tenant_id, [])
        return history[-limit:]
    
    def on_action(
        self,
        action: str,
        handler: Callable[[PolicyResult], None],
    ) -> None:
        """Register handler for a policy action."""
        if action not in self._action_handlers:
            self._action_handlers[action] = []
        self._action_handlers[action].append(handler)
    
    def _dispatch_actions(self, result: PolicyResult) -> None:
        """Dispatch result actions to handlers."""
        for action in result.actions:
            handlers = self._action_handlers.get(action, [])
            for handler in handlers:
                try:
                    handler(result)
                except Exception as e:
                    logger.warning(f"Action handler error for {action}: {e}")
    
    # =========================================================================
    # Rule Management
    # =========================================================================
    
    def add_rule(self, rule: PolicyRule) -> None:
        """Add a policy rule."""
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority, reverse=True)
    
    def remove_rule(self, rule_id: str) -> None:
        """Remove a policy rule."""
        self._rules = [r for r in self._rules if r.rule_id != rule_id]
    
    def get_rule(self, rule_id: str) -> Optional[PolicyRule]:
        """Get a rule by ID."""
        for rule in self._rules:
            if rule.rule_id == rule_id:
                return rule
        return None
    
    def enable_rule(self, rule_id: str) -> None:
        """Enable a rule."""
        rule = self.get_rule(rule_id)
        if rule:
            rule.enabled = True
    
    def disable_rule(self, rule_id: str) -> None:
        """Disable a rule."""
        rule = self.get_rule(rule_id)
        if rule:
            rule.enabled = False
    
    # =========================================================================
    # Status
    # =========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get policy tree status."""
        return {
            "rules_count": len(self._rules),
            "enabled_rules": len([r for r in self._rules if r.enabled]),
            "tier_policies": list(self._tier_policies.keys()),
            "tenants_with_history": len(self._decision_history),
            "active_grace_periods": sum(
                1 for periods in self._grace_periods.values()
                if any(p > datetime.now() for p in periods)
            ),
            "action_handlers": {k: len(v) for k, v in self._action_handlers.items()},
        }


# =============================================================================
# Factory Functions
# =============================================================================

def create_policy_tree(
    rules: Optional[List[PolicyRule]] = None,
    tier_policies: Optional[Dict[str, TierPolicyConfig]] = None,
) -> BillingPolicyTree:
    """Create a billing policy tree."""
    return BillingPolicyTree(rules, tier_policies)


def create_policy_context(
    tenant_id: str,
    tier: str,
    current_usage: float,
    limit: float,
    **kwargs,
) -> PolicyContext:
    """Create a policy context for evaluation."""
    utilization = current_usage / limit if limit > 0 else 0
    
    return PolicyContext(
        tenant_id=tenant_id,
        tier=tier,
        current_usage=Decimal(str(current_usage)),
        limit=Decimal(str(limit)),
        utilization_rate=utilization,
        **kwargs,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "PolicyDecision",
    "PolicyTrigger",
    "PolicyEscalation",
    "GracePeriodType",
    # Data Classes
    "PolicyContext",
    "PolicyResult",
    "PolicyRule",
    "TierPolicyConfig",
    # Constants
    "DEFAULT_POLICY_RULES",
    "DEFAULT_TIER_POLICIES",
    # Classes
    "BillingPolicyTree",
    # Factories
    "create_policy_tree",
    "create_policy_context",
]
