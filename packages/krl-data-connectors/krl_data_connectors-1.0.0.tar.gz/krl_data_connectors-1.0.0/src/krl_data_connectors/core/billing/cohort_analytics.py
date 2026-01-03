# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
#
# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.cohort_analytics
# This stub remains for backward compatibility but will be removed in v2.0.
# ----------------------------------------------------------------------

from __future__ import annotations

import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.cohort_analytics is deprecated. "
    "Import from 'app.services.billing.cohort_analytics' instead.",
    DeprecationWarning,
    stacklevel=2
)

"""
Cohort Analytics - Phase 3 Week 22

Customer cohort analysis for revenue optimization:
- Cohort definition and segmentation
- Retention curve analysis
- LTV (Lifetime Value) prediction
- Expansion/contraction tracking
- Net revenue retention calculation

Cohort Types:
- Time-based: By signup month/quarter
- Tier-based: By subscription tier
- Behavior-based: By usage patterns
- Source-based: By acquisition channel

This layer provides strategic insights for monetization decisions.
"""

import logging
import math
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class CohortType(Enum):
    """Types of cohort segmentation."""
    MONTHLY = "monthly"           # By signup month
    QUARTERLY = "quarterly"       # By signup quarter
    TIER = "tier"                 # By subscription tier
    USAGE_PATTERN = "usage"       # By usage behavior
    SOURCE = "source"             # By acquisition channel
    CUSTOM = "custom"             # Custom segmentation


class RetentionMetric(Enum):
    """Retention metrics to track."""
    LOGO_RETENTION = "logo"       # Customer count retention
    REVENUE_RETENTION = "revenue"  # Revenue retention
    NET_RETENTION = "net"         # Net revenue retention (with expansion)
    USAGE_RETENTION = "usage"     # Usage retention


class ExpansionType(Enum):
    """Types of revenue expansion."""
    TIER_UPGRADE = "tier_upgrade"
    SEAT_EXPANSION = "seat_expansion"
    USAGE_OVERAGE = "usage_overage"
    ADDON_PURCHASE = "addon_purchase"
    PRICE_INCREASE = "price_increase"


class ContractionType(Enum):
    """Types of revenue contraction."""
    TIER_DOWNGRADE = "tier_downgrade"
    SEAT_REDUCTION = "seat_reduction"
    USAGE_DECLINE = "usage_decline"
    DISCOUNT_APPLIED = "discount_applied"
    CHURN = "churn"


class CustomerHealth(Enum):
    """Customer health classifications."""
    THRIVING = "thriving"      # Growing, engaged, expanding
    HEALTHY = "healthy"        # Stable, engaged
    AT_RISK = "at_risk"        # Declining engagement
    CRITICAL = "critical"      # Churn imminent
    CHURNED = "churned"        # No longer active


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class CohortMember:
    """A member of a cohort."""
    tenant_id: str
    cohort_id: str
    joined_at: datetime
    tier: str
    
    # Current state
    is_active: bool = True
    health: CustomerHealth = CustomerHealth.HEALTHY
    
    # Revenue
    initial_mrr: Decimal = Decimal("0")
    current_mrr: Decimal = Decimal("0")
    lifetime_revenue: Decimal = Decimal("0")
    
    # Expansion/contraction
    total_expansion: Decimal = Decimal("0")
    total_contraction: Decimal = Decimal("0")
    
    # Engagement
    usage_score: float = 1.0
    engagement_score: float = 1.0
    
    # Metadata
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def net_mrr_change(self) -> Decimal:
        return self.current_mrr - self.initial_mrr
    
    @property
    def months_active(self) -> int:
        return max(1, (datetime.now() - self.joined_at).days // 30)


@dataclass
class Cohort:
    """A customer cohort."""
    cohort_id: str
    cohort_type: CohortType
    name: str
    
    # Time bounds
    start_date: datetime
    end_date: Optional[datetime] = None
    
    # Members
    members: List[CohortMember] = field(default_factory=list)
    
    # Metrics (cached)
    _metrics_cache: Dict[str, Any] = field(default_factory=dict)
    _cache_time: Optional[datetime] = None
    
    @property
    def size(self) -> int:
        return len(self.members)
    
    @property
    def active_count(self) -> int:
        return len([m for m in self.members if m.is_active])
    
    @property
    def churned_count(self) -> int:
        return len([m for m in self.members if not m.is_active])


@dataclass
class RetentionPoint:
    """A point on a retention curve."""
    period: int  # Months since cohort start
    
    # Retention rates
    logo_retention: float = 1.0      # Customer count retention
    revenue_retention: float = 1.0   # Revenue retention
    net_retention: float = 1.0       # Net revenue retention
    
    # Counts
    active_count: int = 0
    churned_count: int = 0
    
    # Revenue
    starting_mrr: Decimal = Decimal("0")
    current_mrr: Decimal = Decimal("0")
    expansion_mrr: Decimal = Decimal("0")
    contraction_mrr: Decimal = Decimal("0")


@dataclass
class LTVPrediction:
    """Lifetime value prediction for a cohort or customer."""
    target_id: str  # Cohort ID or tenant ID
    target_type: str  # "cohort" or "tenant"
    
    # Predictions
    predicted_ltv: Decimal = Decimal("0")
    predicted_lifetime_months: int = 24
    
    # Components
    monthly_value: Decimal = Decimal("0")
    expected_expansion: Decimal = Decimal("0")
    churn_discount: Decimal = Decimal("0")
    
    # Confidence
    confidence_score: float = 0.5
    
    # Comparisons
    cohort_average_ltv: Optional[Decimal] = None
    tier_average_ltv: Optional[Decimal] = None
    
    # Calculation time
    calculated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_id": self.target_id,
            "target_type": self.target_type,
            "predicted_ltv": str(self.predicted_ltv),
            "predicted_lifetime_months": self.predicted_lifetime_months,
            "monthly_value": str(self.monthly_value),
            "confidence_score": self.confidence_score,
        }


@dataclass
class CohortAnalyticsConfig:
    """Configuration for cohort analytics."""
    # Retention calculation
    retention_periods: int = 24  # Months to track
    
    # LTV calculation
    default_lifetime_months: int = 24
    discount_rate: float = 0.10  # Annual discount rate for NPV
    
    # Health scoring
    usage_weight: float = 0.4
    engagement_weight: float = 0.3
    expansion_weight: float = 0.2
    payment_weight: float = 0.1
    
    # Thresholds
    thriving_threshold: float = 0.8
    healthy_threshold: float = 0.6
    at_risk_threshold: float = 0.4
    critical_threshold: float = 0.2
    
    # Cache
    cache_duration_minutes: int = 60


# =============================================================================
# Retention Calculator
# =============================================================================

class RetentionCalculator:
    """Calculates retention curves for cohorts."""
    
    def __init__(self, config: Optional[CohortAnalyticsConfig] = None):
        self._config = config or CohortAnalyticsConfig()
    
    def calculate_retention_curve(
        self,
        cohort: Cohort,
        metric: RetentionMetric = RetentionMetric.NET_RETENTION,
        periods: Optional[int] = None,
    ) -> List[RetentionPoint]:
        """
        Calculate retention curve for a cohort.
        
        Returns list of retention points from period 0 to n.
        """
        periods = periods or self._config.retention_periods
        
        if not cohort.members:
            return []
        
        # Period 0 = cohort start
        initial_count = len(cohort.members)
        initial_mrr = sum(m.initial_mrr for m in cohort.members)
        
        curve = []
        
        for period in range(periods + 1):
            point = self._calculate_period(
                cohort, period, initial_count, initial_mrr
            )
            curve.append(point)
        
        return curve
    
    def _calculate_period(
        self,
        cohort: Cohort,
        period: int,
        initial_count: int,
        initial_mrr: Decimal,
    ) -> RetentionPoint:
        """Calculate retention for a specific period."""
        # Get cutoff date
        cutoff = cohort.start_date + timedelta(days=period * 30)
        
        # Count active at this point
        # (In production, would use historical data)
        active = [m for m in cohort.members if m.is_active or m.months_active > period]
        active_count = len(active)
        
        # Calculate revenue metrics
        current_mrr = sum(m.current_mrr for m in active)
        expansion = sum(m.total_expansion for m in active)
        contraction = sum(m.total_contraction for m in active)
        
        # Calculate retention rates
        logo_retention = active_count / initial_count if initial_count > 0 else 0
        revenue_retention = float(current_mrr / initial_mrr) if initial_mrr > 0 else 0
        
        # Net retention includes expansion
        if initial_mrr > 0:
            net_retention = float((current_mrr + expansion - contraction) / initial_mrr)
        else:
            net_retention = 0
        
        return RetentionPoint(
            period=period,
            logo_retention=logo_retention,
            revenue_retention=revenue_retention,
            net_retention=net_retention,
            active_count=active_count,
            churned_count=initial_count - active_count,
            starting_mrr=initial_mrr,
            current_mrr=current_mrr,
            expansion_mrr=expansion,
            contraction_mrr=contraction,
        )
    
    def calculate_average_retention(
        self,
        cohorts: List[Cohort],
        period: int,
        metric: RetentionMetric = RetentionMetric.NET_RETENTION,
    ) -> float:
        """Calculate average retention across cohorts at a specific period."""
        values = []
        
        for cohort in cohorts:
            curve = self.calculate_retention_curve(cohort, metric, period)
            if len(curve) > period:
                if metric == RetentionMetric.LOGO_RETENTION:
                    values.append(curve[period].logo_retention)
                elif metric == RetentionMetric.REVENUE_RETENTION:
                    values.append(curve[period].revenue_retention)
                else:
                    values.append(curve[period].net_retention)
        
        return statistics.mean(values) if values else 0.0
    
    def project_retention(
        self,
        curve: List[RetentionPoint],
        periods_ahead: int,
    ) -> List[RetentionPoint]:
        """Project retention curve forward using decay model."""
        if len(curve) < 3:
            return curve
        
        # Fit exponential decay
        recent_rates = [p.net_retention for p in curve[-6:]]
        decay_rate = self._estimate_decay_rate(recent_rates)
        
        last_point = curve[-1]
        projected = list(curve)
        
        for i in range(1, periods_ahead + 1):
            period = last_point.period + i
            
            # Apply decay
            projected_retention = last_point.net_retention * math.exp(-decay_rate * i)
            
            projected.append(RetentionPoint(
                period=period,
                net_retention=max(0, projected_retention),
                logo_retention=max(0, projected_retention * 0.9),  # Approximation
                revenue_retention=max(0, projected_retention * 0.95),
            ))
        
        return projected
    
    def _estimate_decay_rate(self, rates: List[float]) -> float:
        """Estimate decay rate from retention rates."""
        if len(rates) < 2:
            return 0.05  # Default 5% monthly decay
        
        # Simple linear regression on log of rates
        log_rates = [math.log(max(0.01, r)) for r in rates]
        
        n = len(log_rates)
        x_mean = (n - 1) / 2
        y_mean = sum(log_rates) / n
        
        numerator = sum((i - x_mean) * (lr - y_mean) for i, lr in enumerate(log_rates))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.05
        
        return -numerator / denominator


# =============================================================================
# LTV Calculator
# =============================================================================

class LTVCalculator:
    """Calculates customer lifetime value."""
    
    def __init__(self, config: Optional[CohortAnalyticsConfig] = None):
        self._config = config or CohortAnalyticsConfig()
    
    def calculate_ltv(
        self,
        member: CohortMember,
        retention_curve: Optional[List[RetentionPoint]] = None,
    ) -> LTVPrediction:
        """
        Calculate LTV for a cohort member.
        
        Uses discounted cash flow with churn probability.
        """
        monthly_value = member.current_mrr
        
        # Estimate lifetime based on health
        lifetime = self._estimate_lifetime(member)
        
        # Calculate expected expansion
        expansion_rate = self._estimate_expansion_rate(member)
        
        # Calculate churn-adjusted NPV
        discount_rate = self._config.discount_rate / 12  # Monthly
        churn_rate = 1 - self._estimate_retention_rate(member)
        
        ltv = Decimal("0")
        
        for month in range(1, lifetime + 1):
            # Survival probability
            survival = (1 - churn_rate) ** month
            
            # Expected monthly value with expansion
            expected_value = monthly_value * Decimal(str(1 + expansion_rate * month))
            
            # Discount factor
            discount = Decimal(str(1 / ((1 + discount_rate) ** month)))
            
            ltv += expected_value * Decimal(str(survival)) * discount
        
        # Calculate components
        base_ltv = monthly_value * Decimal(str(lifetime))
        expansion_value = ltv - base_ltv
        churn_discount = base_ltv - ltv
        
        return LTVPrediction(
            target_id=member.tenant_id,
            target_type="tenant",
            predicted_ltv=ltv.quantize(Decimal("0.01")),
            predicted_lifetime_months=lifetime,
            monthly_value=monthly_value,
            expected_expansion=max(Decimal("0"), expansion_value),
            churn_discount=max(Decimal("0"), churn_discount),
            confidence_score=self._calculate_confidence(member),
        )
    
    def calculate_cohort_ltv(
        self,
        cohort: Cohort,
        retention_curve: Optional[List[RetentionPoint]] = None,
    ) -> LTVPrediction:
        """Calculate average LTV for a cohort."""
        if not cohort.members:
            return LTVPrediction(
                target_id=cohort.cohort_id,
                target_type="cohort",
            )
        
        # Calculate individual LTVs
        ltvs = [
            self.calculate_ltv(m, retention_curve)
            for m in cohort.members
        ]
        
        # Aggregate
        avg_ltv = sum(l.predicted_ltv for l in ltvs) / len(ltvs)
        avg_lifetime = sum(l.predicted_lifetime_months for l in ltvs) // len(ltvs)
        avg_monthly = sum(l.monthly_value for l in ltvs) / len(ltvs)
        avg_confidence = statistics.mean(l.confidence_score for l in ltvs)
        
        return LTVPrediction(
            target_id=cohort.cohort_id,
            target_type="cohort",
            predicted_ltv=avg_ltv.quantize(Decimal("0.01")),
            predicted_lifetime_months=avg_lifetime,
            monthly_value=avg_monthly,
            confidence_score=avg_confidence,
        )
    
    def _estimate_lifetime(self, member: CohortMember) -> int:
        """Estimate remaining customer lifetime in months."""
        base_lifetime = self._config.default_lifetime_months
        
        # Adjust based on health
        health_multipliers = {
            CustomerHealth.THRIVING: 1.5,
            CustomerHealth.HEALTHY: 1.0,
            CustomerHealth.AT_RISK: 0.6,
            CustomerHealth.CRITICAL: 0.2,
            CustomerHealth.CHURNED: 0.0,
        }
        
        multiplier = health_multipliers.get(member.health, 1.0)
        
        # Adjust based on tenure (longer tenure = longer expected lifetime)
        tenure_bonus = min(0.5, member.months_active / 24 * 0.5)
        
        return int(base_lifetime * multiplier * (1 + tenure_bonus))
    
    def _estimate_retention_rate(self, member: CohortMember) -> float:
        """Estimate monthly retention probability."""
        base_rate = 0.95  # 95% base retention
        
        # Health adjustment
        health_adjustments = {
            CustomerHealth.THRIVING: 0.02,
            CustomerHealth.HEALTHY: 0.0,
            CustomerHealth.AT_RISK: -0.05,
            CustomerHealth.CRITICAL: -0.15,
            CustomerHealth.CHURNED: -0.95,
        }
        
        adjustment = health_adjustments.get(member.health, 0.0)
        
        # Engagement adjustment
        engagement_adjustment = (member.engagement_score - 0.5) * 0.05
        
        return max(0.5, min(0.99, base_rate + adjustment + engagement_adjustment))
    
    def _estimate_expansion_rate(self, member: CohortMember) -> float:
        """Estimate monthly expansion rate."""
        base_rate = 0.02  # 2% base expansion
        
        # Adjust based on usage
        if member.usage_score > 0.8:
            base_rate *= 1.5  # High usage = more expansion
        elif member.usage_score < 0.3:
            base_rate *= 0.5  # Low usage = less expansion
        
        # Adjust based on tier headroom
        tier_headroom = {
            "community": 0.5,  # Most headroom
            "pro": 0.3,
            "enterprise": 0.1,  # Least headroom
        }
        
        headroom = tier_headroom.get(member.tier.lower(), 0.2)
        
        return base_rate * (1 + headroom)
    
    def _calculate_confidence(self, member: CohortMember) -> float:
        """Calculate confidence score for LTV prediction."""
        score = 0.5
        
        # Tenure bonus
        if member.months_active >= 12:
            score += 0.2
        elif member.months_active >= 6:
            score += 0.1
        
        # Engagement bonus
        if member.engagement_score > 0.7:
            score += 0.1
        
        # Usage data bonus
        if member.usage_score > 0:
            score += 0.1
        
        return min(1.0, score)


# =============================================================================
# Cohort Manager
# =============================================================================

class CohortManager:
    """
    Manages cohorts and provides analytics.
    
    Handles cohort creation, membership, and metric calculation.
    """
    
    def __init__(self, config: Optional[CohortAnalyticsConfig] = None):
        self._config = config or CohortAnalyticsConfig()
        self._retention_calc = RetentionCalculator(self._config)
        self._ltv_calc = LTVCalculator(self._config)
        
        # Cohorts
        self._cohorts: Dict[str, Cohort] = {}
        
        # Member index
        self._member_index: Dict[str, Set[str]] = {}  # tenant_id -> cohort_ids
        
        # Counters
        self._cohort_counter = 0
        
        logger.info("CohortManager initialized")
    
    # =========================================================================
    # Cohort Management
    # =========================================================================
    
    def create_cohort(
        self,
        cohort_type: CohortType,
        name: str,
        start_date: datetime,
        end_date: Optional[datetime] = None,
    ) -> Cohort:
        """Create a new cohort."""
        self._cohort_counter += 1
        cohort_id = f"COH-{self._cohort_counter:06d}"
        
        cohort = Cohort(
            cohort_id=cohort_id,
            cohort_type=cohort_type,
            name=name,
            start_date=start_date,
            end_date=end_date,
        )
        
        self._cohorts[cohort_id] = cohort
        return cohort
    
    def create_monthly_cohorts(
        self,
        start_month: datetime,
        end_month: datetime,
    ) -> List[Cohort]:
        """Create monthly cohorts for a date range."""
        cohorts = []
        current = start_month.replace(day=1)
        
        while current <= end_month:
            # End of month
            if current.month == 12:
                next_month = current.replace(year=current.year + 1, month=1)
            else:
                next_month = current.replace(month=current.month + 1)
            
            end = next_month - timedelta(days=1)
            
            name = current.strftime("%Y-%m")
            cohort = self.create_cohort(
                CohortType.MONTHLY,
                f"Monthly {name}",
                current,
                end,
            )
            cohorts.append(cohort)
            
            current = next_month
        
        return cohorts
    
    def add_member(
        self,
        cohort_id: str,
        tenant_id: str,
        tier: str,
        joined_at: Optional[datetime] = None,
        initial_mrr: Decimal = Decimal("0"),
        source: str = "",
    ) -> Optional[CohortMember]:
        """Add a member to a cohort."""
        cohort = self._cohorts.get(cohort_id)
        if not cohort:
            return None
        
        member = CohortMember(
            tenant_id=tenant_id,
            cohort_id=cohort_id,
            joined_at=joined_at or datetime.now(),
            tier=tier,
            initial_mrr=initial_mrr,
            current_mrr=initial_mrr,
            source=source,
        )
        
        cohort.members.append(member)
        
        # Update index
        if tenant_id not in self._member_index:
            self._member_index[tenant_id] = set()
        self._member_index[tenant_id].add(cohort_id)
        
        return member
    
    def update_member(
        self,
        tenant_id: str,
        cohort_id: str,
        **updates,
    ) -> Optional[CohortMember]:
        """Update a cohort member."""
        cohort = self._cohorts.get(cohort_id)
        if not cohort:
            return None
        
        for member in cohort.members:
            if member.tenant_id == tenant_id:
                for key, value in updates.items():
                    if hasattr(member, key):
                        setattr(member, key, value)
                return member
        
        return None
    
    def get_member_cohorts(self, tenant_id: str) -> List[Cohort]:
        """Get all cohorts a tenant belongs to."""
        cohort_ids = self._member_index.get(tenant_id, set())
        return [self._cohorts[cid] for cid in cohort_ids if cid in self._cohorts]
    
    # =========================================================================
    # Expansion/Contraction Tracking
    # =========================================================================
    
    def record_expansion(
        self,
        tenant_id: str,
        amount: Decimal,
        expansion_type: ExpansionType,
        new_mrr: Optional[Decimal] = None,
    ) -> None:
        """Record revenue expansion for a customer."""
        cohort_ids = self._member_index.get(tenant_id, set())
        
        for cohort_id in cohort_ids:
            cohort = self._cohorts.get(cohort_id)
            if not cohort:
                continue
            
            for member in cohort.members:
                if member.tenant_id == tenant_id:
                    member.total_expansion += amount
                    if new_mrr is not None:
                        member.current_mrr = new_mrr
                    
                    # Update health
                    self._update_member_health(member)
    
    def record_contraction(
        self,
        tenant_id: str,
        amount: Decimal,
        contraction_type: ContractionType,
        new_mrr: Optional[Decimal] = None,
    ) -> None:
        """Record revenue contraction for a customer."""
        cohort_ids = self._member_index.get(tenant_id, set())
        
        for cohort_id in cohort_ids:
            cohort = self._cohorts.get(cohort_id)
            if not cohort:
                continue
            
            for member in cohort.members:
                if member.tenant_id == tenant_id:
                    member.total_contraction += amount
                    if new_mrr is not None:
                        member.current_mrr = new_mrr
                    
                    # Mark as churned if applicable
                    if contraction_type == ContractionType.CHURN:
                        member.is_active = False
                        member.health = CustomerHealth.CHURNED
                    else:
                        self._update_member_health(member)
    
    def _update_member_health(self, member: CohortMember) -> None:
        """Update member health classification."""
        # Calculate health score
        score = (
            member.usage_score * self._config.usage_weight +
            member.engagement_score * self._config.engagement_weight
        )
        
        # Expansion bonus
        if member.total_expansion > 0:
            score += 0.1
        
        # Contraction penalty
        if member.total_contraction > member.initial_mrr * Decimal("0.1"):
            score -= 0.2
        
        # Classify
        if score >= self._config.thriving_threshold:
            member.health = CustomerHealth.THRIVING
        elif score >= self._config.healthy_threshold:
            member.health = CustomerHealth.HEALTHY
        elif score >= self._config.at_risk_threshold:
            member.health = CustomerHealth.AT_RISK
        elif score >= self._config.critical_threshold:
            member.health = CustomerHealth.CRITICAL
        else:
            member.health = CustomerHealth.CRITICAL
    
    # =========================================================================
    # Analytics
    # =========================================================================
    
    def get_retention_curve(
        self,
        cohort_id: str,
        metric: RetentionMetric = RetentionMetric.NET_RETENTION,
    ) -> List[RetentionPoint]:
        """Get retention curve for a cohort."""
        cohort = self._cohorts.get(cohort_id)
        if not cohort:
            return []
        
        return self._retention_calc.calculate_retention_curve(cohort, metric)
    
    def get_ltv(self, tenant_id: str) -> Optional[LTVPrediction]:
        """Get LTV prediction for a tenant."""
        cohorts = self.get_member_cohorts(tenant_id)
        if not cohorts:
            return None
        
        # Find member in first cohort
        for member in cohorts[0].members:
            if member.tenant_id == tenant_id:
                return self._ltv_calc.calculate_ltv(member)
        
        return None
    
    def get_cohort_metrics(self, cohort_id: str) -> Dict[str, Any]:
        """Get comprehensive metrics for a cohort."""
        cohort = self._cohorts.get(cohort_id)
        if not cohort:
            return {}
        
        members = cohort.members
        if not members:
            return {"cohort_id": cohort_id, "size": 0}
        
        active = [m for m in members if m.is_active]
        
        # Calculate metrics
        total_mrr = sum(m.current_mrr for m in active)
        initial_mrr = sum(m.initial_mrr for m in members)
        total_expansion = sum(m.total_expansion for m in members)
        total_contraction = sum(m.total_contraction for m in members)
        
        # Health distribution
        health_dist = {}
        for health in CustomerHealth:
            count = len([m for m in members if m.health == health])
            health_dist[health.value] = count
        
        # LTV
        cohort_ltv = self._ltv_calc.calculate_cohort_ltv(cohort)
        
        return {
            "cohort_id": cohort_id,
            "name": cohort.name,
            "type": cohort.cohort_type.value,
            "size": len(members),
            "active_count": len(active),
            "churned_count": len(members) - len(active),
            "logo_retention": len(active) / len(members) if members else 0,
            "initial_mrr": str(initial_mrr),
            "current_mrr": str(total_mrr),
            "net_mrr_change": str(total_mrr - initial_mrr),
            "total_expansion": str(total_expansion),
            "total_contraction": str(total_contraction),
            "net_retention": float(total_mrr / initial_mrr) if initial_mrr > 0 else 0,
            "health_distribution": health_dist,
            "average_ltv": str(cohort_ltv.predicted_ltv),
        }
    
    def get_nrr(
        self,
        cohort_id: Optional[str] = None,
        period_months: int = 12,
    ) -> float:
        """
        Calculate Net Revenue Retention (NRR).
        
        NRR = (Starting MRR + Expansion - Contraction - Churn) / Starting MRR
        """
        if cohort_id:
            cohorts = [self._cohorts.get(cohort_id)]
        else:
            cohorts = list(self._cohorts.values())
        
        starting_mrr = Decimal("0")
        current_mrr = Decimal("0")
        
        for cohort in cohorts:
            if not cohort:
                continue
            
            for member in cohort.members:
                starting_mrr += member.initial_mrr
                if member.is_active:
                    current_mrr += member.current_mrr
        
        if starting_mrr == 0:
            return 1.0
        
        return float(current_mrr / starting_mrr)
    
    def get_health_summary(self) -> Dict[str, int]:
        """Get health summary across all customers."""
        summary = {h.value: 0 for h in CustomerHealth}
        
        seen_tenants = set()
        
        for cohort in self._cohorts.values():
            for member in cohort.members:
                if member.tenant_id not in seen_tenants:
                    seen_tenants.add(member.tenant_id)
                    summary[member.health.value] += 1
        
        return summary
    
    # =========================================================================
    # Status
    # =========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get manager status."""
        total_members = sum(len(c.members) for c in self._cohorts.values())
        
        return {
            "cohort_count": len(self._cohorts),
            "total_members": total_members,
            "unique_tenants": len(self._member_index),
            "cohort_types": list(set(c.cohort_type.value for c in self._cohorts.values())),
        }
    
    def get_cohort(self, cohort_id: str) -> Optional[Cohort]:
        """Get a cohort by ID."""
        return self._cohorts.get(cohort_id)
    
    def list_cohorts(self, cohort_type: Optional[CohortType] = None) -> List[Cohort]:
        """List cohorts, optionally filtered by type."""
        cohorts = list(self._cohorts.values())
        
        if cohort_type:
            cohorts = [c for c in cohorts if c.cohort_type == cohort_type]
        
        return sorted(cohorts, key=lambda c: c.start_date)


# =============================================================================
# Factory Functions
# =============================================================================

def create_cohort_manager(
    config: Optional[CohortAnalyticsConfig] = None,
) -> CohortManager:
    """Create a cohort manager."""
    return CohortManager(config)


def create_cohort_config(
    retention_periods: int = 24,
    default_lifetime_months: int = 24,
    discount_rate: float = 0.10,
) -> CohortAnalyticsConfig:
    """Create cohort analytics configuration."""
    return CohortAnalyticsConfig(
        retention_periods=retention_periods,
        default_lifetime_months=default_lifetime_months,
        discount_rate=discount_rate,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "CohortType",
    "RetentionMetric",
    "ExpansionType",
    "ContractionType",
    "CustomerHealth",
    # Data Classes
    "CohortMember",
    "Cohort",
    "RetentionPoint",
    "LTVPrediction",
    "CohortAnalyticsConfig",
    # Classes
    "RetentionCalculator",
    "LTVCalculator",
    "CohortManager",
    # Factories
    "create_cohort_manager",
    "create_cohort_config",
]
