# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
#
# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.subscription_analytics
# This stub remains for backward compatibility but will be removed in v2.0.
# ----------------------------------------------------------------------

from __future__ import annotations

import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.subscription_analytics is deprecated. "
    "Import from 'app.services.billing.subscription_analytics' instead.",
    DeprecationWarning,
    stacklevel=2
)


"""
KRL Subscription Analytics - Week 24 Day 3
==========================================

Deep subscription analytics for churn prediction, expansion tracking,
and customer health scoring.

Features:
- Churn risk prediction
- Expansion/contraction tracking
- Customer health scores
- Subscription lifecycle analysis
- Renewal forecasting
"""


import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, UTC
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class ChurnRisk(str, Enum):
    """Churn risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class HealthScore(str, Enum):
    """Customer health score levels."""
    EXCELLENT = "excellent"  # 80-100
    GOOD = "good"            # 60-79
    FAIR = "fair"            # 40-59
    POOR = "poor"            # 20-39
    CRITICAL = "critical"    # 0-19


class SubscriptionState(str, Enum):
    """Subscription lifecycle states."""
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    PAUSED = "paused"
    CANCELED = "canceled"
    EXPIRED = "expired"


class MovementType(str, Enum):
    """Subscription movement types."""
    NEW = "new"
    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"
    REACTIVATION = "reactivation"
    CHURN = "churn"
    EXPANSION = "expansion"
    CONTRACTION = "contraction"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ChurnRiskScore:
    """Churn risk assessment."""
    customer_id: str
    subscription_id: str
    risk_level: ChurnRisk
    risk_score: float  # 0-100
    risk_factors: List[str]
    predicted_churn_date: Optional[datetime] = None
    confidence: float = 0.0
    calculated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CustomerHealthScore:
    """Customer health assessment."""
    customer_id: str
    overall_score: float  # 0-100
    health_level: HealthScore
    
    # Component scores
    usage_score: float = 0.0
    engagement_score: float = 0.0
    payment_score: float = 0.0
    support_score: float = 0.0
    tenure_score: float = 0.0
    
    # Insights
    strengths: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    calculated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SubscriptionMovement:
    """Record of subscription movement."""
    movement_id: str
    subscription_id: str
    customer_id: str
    movement_type: MovementType
    from_tier: Optional[str]
    to_tier: Optional[str]
    mrr_change: Decimal
    occurred_at: datetime
    reason: Optional[str] = None


@dataclass
class ExpansionOpportunity:
    """Expansion opportunity for a customer."""
    customer_id: str
    subscription_id: str
    current_tier: str
    recommended_tier: str
    potential_mrr_increase: Decimal
    confidence: float
    triggers: List[str]
    best_approach: str


@dataclass
class RenewalForecast:
    """Renewal forecast for subscription."""
    subscription_id: str
    customer_id: str
    renewal_date: datetime
    renewal_probability: float
    expected_mrr: Decimal
    risk_level: ChurnRisk
    days_until_renewal: int


# =============================================================================
# Churn Predictor
# =============================================================================

class ChurnPredictor:
    """
    Predicts churn risk based on behavioral and transactional signals.
    
    Signals:
    - Usage decline patterns
    - Support ticket frequency
    - Payment failures
    - Engagement drop-off
    - Feature adoption rate
    """
    
    def __init__(self):
        # Risk weights (would be ML-trained in production)
        self._weights = {
            "usage_decline": 0.25,
            "payment_issues": 0.20,
            "support_tickets": 0.15,
            "engagement_drop": 0.20,
            "tenure_factor": 0.10,
            "nps_score": 0.10,
        }
    
    def predict_churn(
        self,
        customer_id: str,
        subscription_id: str,
        signals: Dict[str, Any],
    ) -> ChurnRiskScore:
        """Predict churn risk for subscription."""
        risk_factors = []
        weighted_score = 0.0
        
        # Usage decline
        usage_trend = signals.get("usage_trend", 0)
        if usage_trend < -0.3:
            risk_factors.append("Significant usage decline (>30%)")
            weighted_score += self._weights["usage_decline"] * 100
        elif usage_trend < -0.1:
            risk_factors.append("Moderate usage decline")
            weighted_score += self._weights["usage_decline"] * 50
        
        # Payment issues
        failed_payments = signals.get("failed_payments_30d", 0)
        if failed_payments >= 2:
            risk_factors.append(f"{failed_payments} failed payments in 30 days")
            weighted_score += self._weights["payment_issues"] * 100
        elif failed_payments >= 1:
            risk_factors.append("Payment failure detected")
            weighted_score += self._weights["payment_issues"] * 50
        
        # Support tickets
        tickets = signals.get("support_tickets_30d", 0)
        if tickets >= 5:
            risk_factors.append("High support ticket volume")
            weighted_score += self._weights["support_tickets"] * 80
        elif tickets >= 3:
            risk_factors.append("Elevated support tickets")
            weighted_score += self._weights["support_tickets"] * 40
        
        # Engagement
        last_login_days = signals.get("days_since_last_login", 0)
        if last_login_days > 30:
            risk_factors.append(f"No login in {last_login_days} days")
            weighted_score += self._weights["engagement_drop"] * 100
        elif last_login_days > 14:
            risk_factors.append("Decreased login frequency")
            weighted_score += self._weights["engagement_drop"] * 50
        
        # Tenure
        tenure_months = signals.get("tenure_months", 0)
        if tenure_months < 3:
            risk_factors.append("New customer (< 3 months)")
            weighted_score += self._weights["tenure_factor"] * 60
        elif tenure_months > 24:
            weighted_score -= self._weights["tenure_factor"] * 30  # Long tenure reduces risk
        
        # NPS score
        nps = signals.get("nps_score", 50)
        if nps < 20:
            risk_factors.append("Low NPS score (detractor)")
            weighted_score += self._weights["nps_score"] * 100
        elif nps < 40:
            risk_factors.append("Below average NPS")
            weighted_score += self._weights["nps_score"] * 50
        
        # Normalize score
        risk_score = max(0, min(100, weighted_score))
        
        # Determine risk level
        if risk_score >= 75:
            risk_level = ChurnRisk.CRITICAL
        elif risk_score >= 50:
            risk_level = ChurnRisk.HIGH
        elif risk_score >= 25:
            risk_level = ChurnRisk.MEDIUM
        else:
            risk_level = ChurnRisk.LOW
        
        # Predict churn date (simplified)
        predicted_date = None
        if risk_level in (ChurnRisk.CRITICAL, ChurnRisk.HIGH):
            days_to_churn = int(90 * (1 - risk_score / 100))
            predicted_date = datetime.now(timezone.utc) + timedelta(days=days_to_churn)
        
        return ChurnRiskScore(
            customer_id=customer_id,
            subscription_id=subscription_id,
            risk_level=risk_level,
            risk_score=risk_score,
            risk_factors=risk_factors if risk_factors else ["No significant risk factors"],
            predicted_churn_date=predicted_date,
            confidence=0.75 if len(signals) >= 5 else 0.5,
        )


# =============================================================================
# Health Scorer
# =============================================================================

class CustomerHealthScorer:
    """
    Calculates comprehensive customer health scores.
    
    Components:
    - Usage health: API calls, feature adoption
    - Engagement health: Logins, time in app
    - Payment health: On-time payments, payment method
    - Support health: Ticket volume, resolution satisfaction
    - Tenure health: Relationship length, upgrades
    """
    
    def __init__(self):
        self._component_weights = {
            "usage": 0.30,
            "engagement": 0.25,
            "payment": 0.20,
            "support": 0.15,
            "tenure": 0.10,
        }
    
    def calculate_health(
        self,
        customer_id: str,
        metrics: Dict[str, Any],
    ) -> CustomerHealthScore:
        """Calculate overall health score."""
        # Component scores
        usage_score = self._score_usage(metrics)
        engagement_score = self._score_engagement(metrics)
        payment_score = self._score_payment(metrics)
        support_score = self._score_support(metrics)
        tenure_score = self._score_tenure(metrics)
        
        # Weighted overall
        overall = (
            usage_score * self._component_weights["usage"]
            + engagement_score * self._component_weights["engagement"]
            + payment_score * self._component_weights["payment"]
            + support_score * self._component_weights["support"]
            + tenure_score * self._component_weights["tenure"]
        )
        
        # Determine health level
        if overall >= 80:
            health_level = HealthScore.EXCELLENT
        elif overall >= 60:
            health_level = HealthScore.GOOD
        elif overall >= 40:
            health_level = HealthScore.FAIR
        elif overall >= 20:
            health_level = HealthScore.POOR
        else:
            health_level = HealthScore.CRITICAL
        
        # Generate insights
        strengths, concerns, recommendations = self._generate_insights(
            usage_score, engagement_score, payment_score, support_score, tenure_score
        )
        
        return CustomerHealthScore(
            customer_id=customer_id,
            overall_score=round(overall, 1),
            health_level=health_level,
            usage_score=round(usage_score, 1),
            engagement_score=round(engagement_score, 1),
            payment_score=round(payment_score, 1),
            support_score=round(support_score, 1),
            tenure_score=round(tenure_score, 1),
            strengths=strengths,
            concerns=concerns,
            recommendations=recommendations,
        )
    
    def _score_usage(self, metrics: Dict[str, Any]) -> float:
        """Score usage health (0-100)."""
        usage_pct = metrics.get("usage_vs_plan_pct", 50)
        feature_adoption = metrics.get("feature_adoption_pct", 50)
        
        # Ideal usage is 60-80% of plan
        if 60 <= usage_pct <= 80:
            usage_component = 100
        elif usage_pct > 80:
            usage_component = max(60, 100 - (usage_pct - 80) * 2)
        else:
            usage_component = min(80, usage_pct * 1.5)
        
        return (usage_component * 0.6 + feature_adoption * 0.4)
    
    def _score_engagement(self, metrics: Dict[str, Any]) -> float:
        """Score engagement health (0-100)."""
        logins_30d = metrics.get("logins_30d", 0)
        active_users_pct = metrics.get("active_users_pct", 0)
        
        login_score = min(100, logins_30d * 5)  # 20 logins = 100
        return (login_score * 0.5 + active_users_pct * 0.5)
    
    def _score_payment(self, metrics: Dict[str, Any]) -> float:
        """Score payment health (0-100)."""
        failed_payments = metrics.get("failed_payments_12m", 0)
        on_time_pct = metrics.get("on_time_payment_pct", 100)
        
        failure_penalty = min(50, failed_payments * 15)
        return max(0, on_time_pct - failure_penalty)
    
    def _score_support(self, metrics: Dict[str, Any]) -> float:
        """Score support health (0-100)."""
        tickets_30d = metrics.get("support_tickets_30d", 0)
        csat_score = metrics.get("csat_score", 80)
        
        # High tickets can be good or bad depending on resolution
        if tickets_30d > 5:
            ticket_factor = max(0, 100 - (tickets_30d - 5) * 10)
        else:
            ticket_factor = 100
        
        return (ticket_factor * 0.4 + csat_score * 0.6)
    
    def _score_tenure(self, metrics: Dict[str, Any]) -> float:
        """Score tenure health (0-100)."""
        tenure_months = metrics.get("tenure_months", 0)
        upgrades = metrics.get("upgrade_count", 0)
        
        tenure_score = min(100, tenure_months * 4)  # 25 months = 100
        upgrade_bonus = min(20, upgrades * 10)
        
        return min(100, tenure_score + upgrade_bonus)
    
    def _generate_insights(
        self,
        usage: float,
        engagement: float,
        payment: float,
        support: float,
        tenure: float,
    ) -> Tuple[List[str], List[str], List[str]]:
        """Generate strengths, concerns, and recommendations."""
        strengths = []
        concerns = []
        recommendations = []
        
        scores = {
            "usage": usage,
            "engagement": engagement,
            "payment": payment,
            "support": support,
            "tenure": tenure,
        }
        
        for name, score in scores.items():
            if score >= 80:
                strengths.append(f"Strong {name} score ({score:.0f})")
            elif score < 40:
                concerns.append(f"Low {name} score ({score:.0f})")
                recommendations.append(f"Investigate {name} issues")
        
        if not strengths:
            strengths.append("No critical issues detected")
        if not concerns:
            concerns.append("All metrics within acceptable range")
        
        return strengths, concerns, recommendations


# =============================================================================
# Subscription Analytics
# =============================================================================

class SubscriptionAnalytics:
    """
    Comprehensive subscription analytics engine.
    
    Tracks:
    - Subscription movements
    - Expansion/contraction patterns
    - Renewal forecasting
    - Cohort behavior
    """
    
    def __init__(self):
        self.churn_predictor = ChurnPredictor()
        self.health_scorer = CustomerHealthScorer()
        
        # Data stores
        self._movements: List[SubscriptionMovement] = []
        self._subscriptions: Dict[str, Dict[str, Any]] = {}
        self._customers: Dict[str, Dict[str, Any]] = {}
    
    def load_data(
        self,
        subscriptions: List[Dict[str, Any]],
        customers: List[Dict[str, Any]],
    ) -> None:
        """Load subscription and customer data."""
        self._subscriptions = {s["id"]: s for s in subscriptions}
        self._customers = {c["id"]: c for c in customers}
    
    def analyze_churn_risk(
        self,
        subscription_id: str,
        signals: Optional[Dict[str, Any]] = None,
    ) -> Optional[ChurnRiskScore]:
        """Analyze churn risk for subscription."""
        sub = self._subscriptions.get(subscription_id)
        if not sub:
            return None
        
        signals = signals or self._gather_signals(subscription_id)
        return self.churn_predictor.predict_churn(
            customer_id=sub.get("customer_id", ""),
            subscription_id=subscription_id,
            signals=signals,
        )
    
    def calculate_customer_health(
        self,
        customer_id: str,
        metrics: Optional[Dict[str, Any]] = None,
    ) -> Optional[CustomerHealthScore]:
        """Calculate health score for customer."""
        customer = self._customers.get(customer_id)
        if not customer:
            return None
        
        metrics = metrics or self._gather_metrics(customer_id)
        return self.health_scorer.calculate_health(customer_id, metrics)
    
    def find_expansion_opportunities(
        self,
        min_confidence: float = 0.6,
    ) -> List[ExpansionOpportunity]:
        """Find expansion opportunities across all customers."""
        opportunities = []
        
        for customer_id, customer in self._customers.items():
            opp = self._evaluate_expansion(customer_id, customer)
            if opp and opp.confidence >= min_confidence:
                opportunities.append(opp)
        
        return sorted(opportunities, key=lambda x: x.confidence, reverse=True)
    
    def forecast_renewals(
        self,
        days_ahead: int = 90,
    ) -> List[RenewalForecast]:
        """Forecast upcoming renewals."""
        forecasts = []
        cutoff = datetime.now(timezone.utc) + timedelta(days=days_ahead)
        
        for sub_id, sub in self._subscriptions.items():
            renewal_date = sub.get("current_period_end")
            if not renewal_date or renewal_date > cutoff:
                continue
            
            # Get churn risk for renewal probability
            churn_risk = self.analyze_churn_risk(sub_id)
            risk_score = churn_risk.risk_score if churn_risk else 25
            
            forecasts.append(RenewalForecast(
                subscription_id=sub_id,
                customer_id=sub.get("customer_id", ""),
                renewal_date=renewal_date,
                renewal_probability=1 - (risk_score / 100),
                expected_mrr=Decimal(str(sub.get("amount", 0))),
                risk_level=churn_risk.risk_level if churn_risk else ChurnRisk.LOW,
                days_until_renewal=(renewal_date - datetime.now(timezone.utc)).days,
            ))
        
        return sorted(forecasts, key=lambda x: x.renewal_date)
    
    def record_movement(
        self,
        subscription_id: str,
        movement_type: MovementType,
        from_tier: Optional[str],
        to_tier: Optional[str],
        mrr_change: Decimal,
        reason: Optional[str] = None,
    ) -> SubscriptionMovement:
        """Record subscription movement."""
        sub = self._subscriptions.get(subscription_id, {})
        
        movement = SubscriptionMovement(
            movement_id=uuid4().hex,
            subscription_id=subscription_id,
            customer_id=sub.get("customer_id", ""),
            movement_type=movement_type,
            from_tier=from_tier,
            to_tier=to_tier,
            mrr_change=mrr_change,
            occurred_at=datetime.now(timezone.utc),
            reason=reason,
        )
        
        self._movements.append(movement)
        return movement
    
    def get_movement_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get summary of subscription movements."""
        end_date = end_date or datetime.now(timezone.utc)
        start_date = start_date or (end_date - timedelta(days=30))
        
        filtered = [
            m for m in self._movements
            if start_date <= m.occurred_at <= end_date
        ]
        
        summary = {
            MovementType.NEW.value: {"count": 0, "mrr": Decimal("0")},
            MovementType.UPGRADE.value: {"count": 0, "mrr": Decimal("0")},
            MovementType.DOWNGRADE.value: {"count": 0, "mrr": Decimal("0")},
            MovementType.CHURN.value: {"count": 0, "mrr": Decimal("0")},
            MovementType.REACTIVATION.value: {"count": 0, "mrr": Decimal("0")},
        }
        
        for m in filtered:
            key = m.movement_type.value
            if key in summary:
                summary[key]["count"] += 1
                summary[key]["mrr"] += m.mrr_change
        
        return summary
    
    # -------------------------------------------------------------------------
    # Private Helpers
    # -------------------------------------------------------------------------
    
    def _gather_signals(self, subscription_id: str) -> Dict[str, Any]:
        """Gather signals for churn prediction."""
        # Would aggregate from various sources
        return {
            "usage_trend": 0.0,
            "failed_payments_30d": 0,
            "support_tickets_30d": 0,
            "days_since_last_login": 3,
            "tenure_months": 12,
            "nps_score": 50,
        }
    
    def _gather_metrics(self, customer_id: str) -> Dict[str, Any]:
        """Gather metrics for health scoring."""
        return {
            "usage_vs_plan_pct": 65,
            "feature_adoption_pct": 70,
            "logins_30d": 15,
            "active_users_pct": 80,
            "failed_payments_12m": 0,
            "on_time_payment_pct": 100,
            "support_tickets_30d": 2,
            "csat_score": 85,
            "tenure_months": 18,
            "upgrade_count": 1,
        }
    
    def _evaluate_expansion(
        self,
        customer_id: str,
        customer: Dict[str, Any],
    ) -> Optional[ExpansionOpportunity]:
        """Evaluate expansion opportunity for customer."""
        current_tier = customer.get("tier", "community")
        usage_pct = customer.get("usage_vs_plan_pct", 0)
        
        # High usage = expansion candidate
        if usage_pct < 70:
            return None
        
        tier_upgrades = {
            "community": ("pro", Decimal("49")),
            "pro": ("enterprise", Decimal("199")),
        }
        
        if current_tier not in tier_upgrades:
            return None
        
        recommended_tier, mrr_increase = tier_upgrades[current_tier]
        
        triggers = []
        if usage_pct >= 90:
            triggers.append("Usage at 90%+ of plan limits")
        if usage_pct >= 80:
            triggers.append("Consistent high usage")
        
        confidence = min(0.95, usage_pct / 100)
        
        return ExpansionOpportunity(
            customer_id=customer_id,
            subscription_id=customer.get("subscription_id", ""),
            current_tier=current_tier,
            recommended_tier=recommended_tier,
            potential_mrr_increase=mrr_increase,
            confidence=confidence,
            triggers=triggers,
            best_approach="In-app upgrade prompt" if usage_pct >= 90 else "Email campaign",
        )


# =============================================================================
# Factory Function
# =============================================================================

def create_subscription_analytics() -> SubscriptionAnalytics:
    """Create configured SubscriptionAnalytics."""
    return SubscriptionAnalytics()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "ChurnRisk",
    "HealthScore",
    "SubscriptionState",
    "MovementType",
    # Data Classes
    "ChurnRiskScore",
    "CustomerHealthScore",
    "SubscriptionMovement",
    "ExpansionOpportunity",
    "RenewalForecast",
    # Classes
    "ChurnPredictor",
    "CustomerHealthScorer",
    "SubscriptionAnalytics",
    # Factory
    "create_subscription_analytics",
]
