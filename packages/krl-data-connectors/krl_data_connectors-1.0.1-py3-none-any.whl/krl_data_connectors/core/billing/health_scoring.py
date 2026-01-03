# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.health_scoring
# This stub remains for backward compatibility but will be removed in v2.0.
import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.health_scoring is deprecated. "
    "Import from 'app.services.billing.health_scoring' instead.",
    DeprecationWarning,
    stacklevel=2
)

"""
Customer Health Scoring ML Pipeline for KRL.

This module implements predictive analytics for customer success:
- Health score calculation (0-100)
- Churn prediction with XGBoost
- Expansion opportunity detection
- Proactive intervention triggers

Part of Phase 1 pricing strategy implementation.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from decimal import Decimal
from enum import Enum, auto
from typing import Any, Optional
import math


class HealthCategory(Enum):
    """Health score categories for dashboard display."""
    CRITICAL = auto()   # 0-25: Immediate intervention needed
    AT_RISK = auto()    # 26-50: Close monitoring required
    HEALTHY = auto()    # 51-75: Normal engagement
    CHAMPION = auto()   # 76-100: Expansion candidates


class ChurnRisk(Enum):
    """Churn risk levels."""
    LOW = "low"           # <10% probability
    MEDIUM = "medium"     # 10-30% probability
    HIGH = "high"         # 30-60% probability
    CRITICAL = "critical" # >60% probability


class InterventionType(Enum):
    """Types of proactive interventions."""
    CS_CALL = "customer_success_call"
    EXEC_OUTREACH = "executive_outreach"
    FEATURE_TRAINING = "feature_training"
    DISCOUNT_OFFER = "discount_offer"
    USAGE_REVIEW = "usage_review"
    INTEGRATION_HELP = "integration_help"
    UPGRADE_OFFER = "upgrade_offer"


@dataclass
class UsageMetrics:
    """Customer usage metrics for health scoring."""
    customer_id: str
    
    # API Usage
    api_calls_30d: int = 0
    api_calls_trend: float = 0.0  # % change vs prior 30d
    unique_endpoints_used: int = 0
    error_rate_percent: float = 0.0
    
    # Engagement
    active_users: int = 0
    active_users_trend: float = 0.0
    login_frequency_weekly: float = 0.0
    features_adopted: int = 0
    total_features_available: int = 10
    
    # Support
    support_tickets_30d: int = 0
    avg_ticket_resolution_hours: float = 0.0
    nps_score: Optional[int] = None
    csat_score: Optional[float] = None
    
    # Financial
    mrr: Decimal = Decimal("0")
    mrr_trend: float = 0.0
    payment_failures_90d: int = 0
    days_until_renewal: int = 365
    
    # Behavioral signals
    last_login_days_ago: int = 0
    dashboard_views_30d: int = 0
    documentation_views_30d: int = 0
    
    # Contract
    contract_months_remaining: int = 12
    is_annual_contract: bool = False
    
    measured_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class HealthScore:
    """Comprehensive health score result."""
    customer_id: str
    overall_score: float
    category: HealthCategory
    
    # Component scores (0-100)
    usage_score: float
    engagement_score: float
    support_score: float
    financial_score: float
    
    # Risk assessment
    churn_probability: float
    churn_risk: ChurnRisk
    
    # Opportunities
    expansion_probability: float
    upsell_candidates: list[str]
    
    # Recommended actions
    interventions: list[InterventionType]
    intervention_priority: int  # 1-5, 1 being highest
    
    # Trend
    score_trend: float  # Change from last calculation
    calculated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ChurnPrediction:
    """Detailed churn prediction result."""
    customer_id: str
    churn_probability: float
    risk_level: ChurnRisk
    
    # Contributing factors (importance 0-1)
    risk_factors: dict[str, float]
    
    # Recommendations
    mitigation_actions: list[str]
    estimated_save_probability: float
    
    # Time horizon (with default)
    prediction_horizon_days: int = 90
    
    predicted_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ExpansionOpportunity:
    """Expansion/upsell opportunity detection."""
    customer_id: str
    opportunity_type: str  # upgrade, add-on, seats
    
    # Scoring
    probability: float
    estimated_arr_increase: Decimal
    
    # Signals
    trigger_signals: list[str]
    
    # Timing
    optimal_outreach_window: str  # e.g., "next 2 weeks"
    
    # Recommendation
    recommended_offer: str
    talking_points: list[str]
    
    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class HealthScoringEngine:
    """
    Calculates customer health scores using weighted metrics.
    
    Health Score Components:
    - Usage Score (30%): API activity, feature adoption
    - Engagement Score (25%): User activity, login frequency
    - Support Score (20%): Ticket volume, satisfaction
    - Financial Score (25%): Payment health, renewal proximity
    """
    
    # Component weights
    WEIGHTS = {
        "usage": 0.30,
        "engagement": 0.25,
        "support": 0.20,
        "financial": 0.25,
    }
    
    # Thresholds for categorization
    CATEGORY_THRESHOLDS = {
        HealthCategory.CRITICAL: 25,
        HealthCategory.AT_RISK: 50,
        HealthCategory.HEALTHY: 75,
        HealthCategory.CHAMPION: 100,
    }
    
    def calculate_health_score(
        self, metrics: UsageMetrics, historical_score: Optional[float] = None
    ) -> HealthScore:
        """
        Calculate comprehensive health score.
        
        Args:
            metrics: Current usage metrics
            historical_score: Previous health score for trend
            
        Returns:
            Complete health score with recommendations
        """
        # Calculate component scores
        usage_score = self._calculate_usage_score(metrics)
        engagement_score = self._calculate_engagement_score(metrics)
        support_score = self._calculate_support_score(metrics)
        financial_score = self._calculate_financial_score(metrics)
        
        # Weighted overall score
        overall_score = (
            usage_score * self.WEIGHTS["usage"] +
            engagement_score * self.WEIGHTS["engagement"] +
            support_score * self.WEIGHTS["support"] +
            financial_score * self.WEIGHTS["financial"]
        )
        
        # Determine category
        category = self._get_category(overall_score)
        
        # Calculate churn probability
        churn_prob, churn_risk = self._estimate_churn_probability(
            overall_score, metrics
        )
        
        # Detect expansion opportunities
        expansion_prob, upsell_candidates = self._detect_expansion_opportunity(
            overall_score, metrics
        )
        
        # Determine interventions
        interventions, priority = self._recommend_interventions(
            category, churn_risk, metrics
        )
        
        # Calculate trend
        score_trend = 0.0
        if historical_score is not None:
            score_trend = overall_score - historical_score
        
        return HealthScore(
            customer_id=metrics.customer_id,
            overall_score=round(overall_score, 1),
            category=category,
            usage_score=round(usage_score, 1),
            engagement_score=round(engagement_score, 1),
            support_score=round(support_score, 1),
            financial_score=round(financial_score, 1),
            churn_probability=round(churn_prob, 3),
            churn_risk=churn_risk,
            expansion_probability=round(expansion_prob, 3),
            upsell_candidates=upsell_candidates,
            interventions=interventions,
            intervention_priority=priority,
            score_trend=round(score_trend, 1),
        )
    
    def _calculate_usage_score(self, metrics: UsageMetrics) -> float:
        """Calculate usage component score."""
        score = 50.0  # Base score
        
        # API activity (±20 points)
        if metrics.api_calls_30d > 10000:
            score += 20
        elif metrics.api_calls_30d > 1000:
            score += 10
        elif metrics.api_calls_30d < 100:
            score -= 20
        
        # Usage trend (±15 points)
        if metrics.api_calls_trend > 0.2:  # 20% growth
            score += 15
        elif metrics.api_calls_trend > 0:
            score += 5
        elif metrics.api_calls_trend < -0.3:  # 30% decline
            score -= 15
        
        # Feature adoption (±15 points)
        if metrics.total_features_available > 0:
            adoption_rate = metrics.features_adopted / metrics.total_features_available
            if adoption_rate > 0.7:
                score += 15
            elif adoption_rate > 0.4:
                score += 5
            elif adoption_rate < 0.2:
                score -= 15
        
        # Error rate penalty
        if metrics.error_rate_percent > 5:
            score -= 10
        elif metrics.error_rate_percent > 2:
            score -= 5
        
        return max(0, min(100, score))
    
    def _calculate_engagement_score(self, metrics: UsageMetrics) -> float:
        """Calculate engagement component score."""
        score = 50.0
        
        # Active users (±20 points)
        if metrics.active_users >= 10:
            score += 20
        elif metrics.active_users >= 3:
            score += 10
        elif metrics.active_users == 0:
            score -= 25
        
        # Login frequency (±15 points)
        if metrics.login_frequency_weekly >= 5:
            score += 15
        elif metrics.login_frequency_weekly >= 2:
            score += 5
        elif metrics.login_frequency_weekly < 0.5:
            score -= 15
        
        # Recency (±15 points)
        if metrics.last_login_days_ago <= 1:
            score += 15
        elif metrics.last_login_days_ago <= 7:
            score += 5
        elif metrics.last_login_days_ago > 30:
            score -= 20
        
        # Dashboard/docs engagement
        total_views = metrics.dashboard_views_30d + metrics.documentation_views_30d
        if total_views > 50:
            score += 10
        elif total_views < 5:
            score -= 10
        
        return max(0, min(100, score))
    
    def _calculate_support_score(self, metrics: UsageMetrics) -> float:
        """Calculate support component score."""
        score = 70.0  # Start higher - no tickets is good
        
        # Ticket volume penalty
        if metrics.support_tickets_30d > 10:
            score -= 30
        elif metrics.support_tickets_30d > 5:
            score -= 15
        elif metrics.support_tickets_30d > 2:
            score -= 5
        
        # Resolution time
        if metrics.avg_ticket_resolution_hours > 48:
            score -= 15
        elif metrics.avg_ticket_resolution_hours < 4:
            score += 10
        
        # Satisfaction scores
        if metrics.nps_score is not None:
            if metrics.nps_score >= 9:
                score += 20
            elif metrics.nps_score >= 7:
                score += 5
            elif metrics.nps_score <= 5:
                score -= 20
        
        if metrics.csat_score is not None:
            if metrics.csat_score >= 4.5:
                score += 10
            elif metrics.csat_score < 3:
                score -= 15
        
        return max(0, min(100, score))
    
    def _calculate_financial_score(self, metrics: UsageMetrics) -> float:
        """Calculate financial component score."""
        score = 50.0
        
        # MRR trend (±20 points)
        if metrics.mrr_trend > 0.1:  # 10% growth
            score += 20
        elif metrics.mrr_trend > 0:
            score += 5
        elif metrics.mrr_trend < -0.1:
            score -= 20
        
        # Payment health (±15 points)
        if metrics.payment_failures_90d == 0:
            score += 15
        elif metrics.payment_failures_90d > 2:
            score -= 20
        
        # Renewal proximity risk
        if metrics.days_until_renewal <= 30:
            score -= 10  # Flag for attention
        elif metrics.days_until_renewal <= 90:
            score -= 5
        
        # Contract stability bonus
        if metrics.is_annual_contract:
            score += 15
        
        if metrics.contract_months_remaining > 6:
            score += 10
        
        return max(0, min(100, score))
    
    def _get_category(self, score: float) -> HealthCategory:
        """Determine health category from score."""
        if score <= self.CATEGORY_THRESHOLDS[HealthCategory.CRITICAL]:
            return HealthCategory.CRITICAL
        elif score <= self.CATEGORY_THRESHOLDS[HealthCategory.AT_RISK]:
            return HealthCategory.AT_RISK
        elif score <= self.CATEGORY_THRESHOLDS[HealthCategory.HEALTHY]:
            return HealthCategory.HEALTHY
        else:
            return HealthCategory.CHAMPION
    
    def _estimate_churn_probability(
        self, health_score: float, metrics: UsageMetrics
    ) -> tuple[float, ChurnRisk]:
        """
        Estimate churn probability based on health score and signals.
        
        This is a simplified model - production would use XGBoost.
        """
        # Base probability inversely related to health
        base_prob = (100 - health_score) / 200  # 0-50% range from health
        
        # Risk factors
        risk_adjustments = 0.0
        
        # Declining usage is strong churn signal
        if metrics.api_calls_trend < -0.3:
            risk_adjustments += 0.15
        
        # No recent activity
        if metrics.last_login_days_ago > 14:
            risk_adjustments += 0.10
        
        # Multiple payment failures
        if metrics.payment_failures_90d >= 2:
            risk_adjustments += 0.15
        
        # Low NPS
        if metrics.nps_score is not None and metrics.nps_score <= 5:
            risk_adjustments += 0.10
        
        # Near renewal without commitment
        if metrics.days_until_renewal <= 30 and not metrics.is_annual_contract:
            risk_adjustments += 0.10
        
        # High support tickets
        if metrics.support_tickets_30d > 5:
            risk_adjustments += 0.05
        
        # Protective factors
        if metrics.is_annual_contract:
            risk_adjustments -= 0.10
        if metrics.active_users > 5:
            risk_adjustments -= 0.05
        if metrics.features_adopted > 5:
            risk_adjustments -= 0.05
        
        churn_prob = max(0, min(1, base_prob + risk_adjustments))
        
        # Determine risk level
        if churn_prob >= 0.6:
            risk = ChurnRisk.CRITICAL
        elif churn_prob >= 0.3:
            risk = ChurnRisk.HIGH
        elif churn_prob >= 0.1:
            risk = ChurnRisk.MEDIUM
        else:
            risk = ChurnRisk.LOW
        
        return churn_prob, risk
    
    def _detect_expansion_opportunity(
        self, health_score: float, metrics: UsageMetrics
    ) -> tuple[float, list[str]]:
        """Detect expansion and upsell opportunities."""
        opportunities: list[str] = []
        probability = 0.0
        
        # Only healthy customers are expansion candidates
        if health_score < 60:
            return 0.0, []
        
        # Usage growth suggests tier upgrade
        if metrics.api_calls_trend > 0.3:
            opportunities.append("tier_upgrade")
            probability += 0.3
        
        # Multiple active users suggests seat expansion
        if metrics.active_users > 5 and metrics.active_users_trend > 0.2:
            opportunities.append("seat_expansion")
            probability += 0.25
        
        # High feature adoption suggests premium features
        if metrics.total_features_available > 0:
            adoption = metrics.features_adopted / metrics.total_features_available
            if adoption > 0.7:
                opportunities.append("premium_features")
                probability += 0.2
        
        # Champions are always expansion candidates
        if health_score >= 80:
            probability += 0.15
            if "multi_year_contract" not in opportunities:
                opportunities.append("multi_year_contract")
        
        return min(1.0, probability), opportunities
    
    def _recommend_interventions(
        self,
        category: HealthCategory,
        churn_risk: ChurnRisk,
        metrics: UsageMetrics,
    ) -> tuple[list[InterventionType], int]:
        """Determine appropriate interventions."""
        interventions: list[InterventionType] = []
        priority = 5  # Lowest priority by default
        
        if category == HealthCategory.CRITICAL:
            priority = 1
            interventions.append(InterventionType.EXEC_OUTREACH)
            interventions.append(InterventionType.CS_CALL)
            
            if metrics.support_tickets_30d > 3:
                interventions.append(InterventionType.INTEGRATION_HELP)
            
            if churn_risk == ChurnRisk.CRITICAL:
                interventions.append(InterventionType.DISCOUNT_OFFER)
        
        elif category == HealthCategory.AT_RISK:
            priority = 2
            interventions.append(InterventionType.CS_CALL)
            
            if metrics.features_adopted < 3:
                interventions.append(InterventionType.FEATURE_TRAINING)
            
            if metrics.api_calls_trend < 0:
                interventions.append(InterventionType.USAGE_REVIEW)
        
        elif category == HealthCategory.HEALTHY:
            priority = 4
            
            if metrics.days_until_renewal <= 60:
                interventions.append(InterventionType.CS_CALL)
                priority = 3
        
        elif category == HealthCategory.CHAMPION:
            priority = 5
            interventions.append(InterventionType.UPGRADE_OFFER)
        
        return interventions, priority


class ChurnPredictionModel:
    """
    XGBoost-based churn prediction model.
    
    In production, this would use a trained XGBoost model.
    This implementation uses a rule-based approximation.
    """
    
    # Feature importance weights (would come from trained model)
    FEATURE_WEIGHTS = {
        "api_calls_trend": 0.18,
        "login_recency": 0.15,
        "active_users_trend": 0.12,
        "payment_failures": 0.11,
        "support_tickets": 0.10,
        "nps_score": 0.09,
        "feature_adoption": 0.08,
        "contract_type": 0.07,
        "renewal_proximity": 0.06,
        "mrr_trend": 0.04,
    }
    
    def predict_churn(
        self, metrics: UsageMetrics, horizon_days: int = 90
    ) -> ChurnPrediction:
        """
        Predict churn probability with contributing factors.
        
        Args:
            metrics: Customer usage metrics
            horizon_days: Prediction time horizon
            
        Returns:
            Detailed churn prediction
        """
        # Calculate risk factors
        risk_factors: dict[str, float] = {}
        
        # API usage trend
        if metrics.api_calls_trend < -0.3:
            risk_factors["declining_api_usage"] = 0.8
        elif metrics.api_calls_trend < 0:
            risk_factors["declining_api_usage"] = 0.4
        
        # Login recency
        if metrics.last_login_days_ago > 14:
            risk_factors["inactive_logins"] = min(
                1.0, metrics.last_login_days_ago / 30
            )
        
        # Active users
        if metrics.active_users_trend < -0.2:
            risk_factors["declining_users"] = abs(metrics.active_users_trend)
        
        # Payment issues
        if metrics.payment_failures_90d > 0:
            risk_factors["payment_issues"] = min(
                1.0, metrics.payment_failures_90d / 3
            )
        
        # Support burden
        if metrics.support_tickets_30d > 5:
            risk_factors["high_support_volume"] = min(
                1.0, metrics.support_tickets_30d / 10
            )
        
        # NPS detractor
        if metrics.nps_score is not None and metrics.nps_score <= 6:
            risk_factors["low_nps"] = (7 - metrics.nps_score) / 7
        
        # Feature adoption
        if metrics.total_features_available > 0:
            adoption = metrics.features_adopted / metrics.total_features_available
            if adoption < 0.3:
                risk_factors["low_feature_adoption"] = 1 - adoption
        
        # Contract type (monthly = higher risk)
        if not metrics.is_annual_contract:
            risk_factors["monthly_contract"] = 0.5
        
        # Renewal proximity
        if metrics.days_until_renewal <= 30:
            risk_factors["imminent_renewal"] = 0.6
        
        # Calculate weighted probability
        total_risk = sum(
            factor_value * self.FEATURE_WEIGHTS.get(factor_name.split("_")[0], 0.05)
            for factor_name, factor_value in risk_factors.items()
        )
        
        # Normalize to probability
        churn_probability = min(0.95, total_risk)
        
        # Determine risk level
        if churn_probability >= 0.6:
            risk_level = ChurnRisk.CRITICAL
        elif churn_probability >= 0.3:
            risk_level = ChurnRisk.HIGH
        elif churn_probability >= 0.1:
            risk_level = ChurnRisk.MEDIUM
        else:
            risk_level = ChurnRisk.LOW
        
        # Generate mitigation recommendations
        mitigation_actions = self._generate_mitigation_actions(risk_factors)
        
        # Estimate save probability based on risk level
        save_probability = {
            ChurnRisk.LOW: 0.95,
            ChurnRisk.MEDIUM: 0.70,
            ChurnRisk.HIGH: 0.45,
            ChurnRisk.CRITICAL: 0.20,
        }.get(risk_level, 0.50)
        
        return ChurnPrediction(
            customer_id=metrics.customer_id,
            churn_probability=round(churn_probability, 3),
            risk_level=risk_level,
            risk_factors=risk_factors,
            prediction_horizon_days=horizon_days,
            mitigation_actions=mitigation_actions,
            estimated_save_probability=save_probability,
        )
    
    def _generate_mitigation_actions(
        self, risk_factors: dict[str, float]
    ) -> list[str]:
        """Generate specific mitigation actions based on risk factors."""
        actions = []
        
        if "declining_api_usage" in risk_factors:
            actions.append("Schedule usage review to understand workflow changes")
            actions.append("Offer integration assistance for new use cases")
        
        if "inactive_logins" in risk_factors:
            actions.append("Send re-engagement campaign with feature highlights")
            actions.append("Offer 1:1 training session")
        
        if "declining_users" in risk_factors:
            actions.append("Investigate team changes or organizational shifts")
            actions.append("Provide team onboarding resources")
        
        if "payment_issues" in risk_factors:
            actions.append("Proactive finance outreach to resolve billing")
            actions.append("Offer payment plan options if needed")
        
        if "high_support_volume" in risk_factors:
            actions.append("Escalate to dedicated support specialist")
            actions.append("Conduct technical architecture review")
        
        if "low_nps" in risk_factors:
            actions.append("Executive outreach to address concerns")
            actions.append("Create action plan for reported issues")
        
        if "low_feature_adoption" in risk_factors:
            actions.append("Personalized feature enablement session")
            actions.append("Share customer success stories for unused features")
        
        if "monthly_contract" in risk_factors:
            actions.append("Offer annual contract with discount incentive")
            actions.append("Highlight multi-year contract benefits")
        
        if "imminent_renewal" in risk_factors:
            actions.append("Urgent renewal conversation required")
            actions.append("Prepare value demonstration and ROI review")
        
        return actions[:5]  # Top 5 most relevant


class ExpansionDetector:
    """Detects and scores expansion opportunities."""
    
    def detect_opportunities(
        self, metrics: UsageMetrics, current_tier: str, current_seats: int
    ) -> list[ExpansionOpportunity]:
        """
        Detect all expansion opportunities for a customer.
        
        Args:
            metrics: Usage metrics
            current_tier: Current subscription tier
            current_seats: Current number of seats
            
        Returns:
            List of expansion opportunities
        """
        opportunities = []
        
        # Check for tier upgrade opportunity
        tier_opp = self._check_tier_upgrade(metrics, current_tier)
        if tier_opp:
            opportunities.append(tier_opp)
        
        # Check for seat expansion
        seat_opp = self._check_seat_expansion(metrics, current_seats)
        if seat_opp:
            opportunities.append(seat_opp)
        
        # Check for add-on opportunities
        addon_opps = self._check_addon_opportunities(metrics)
        opportunities.extend(addon_opps)
        
        # Sort by probability
        opportunities.sort(key=lambda x: x.probability, reverse=True)
        
        return opportunities
    
    def _check_tier_upgrade(
        self, metrics: UsageMetrics, current_tier: str
    ) -> Optional[ExpansionOpportunity]:
        """Check if customer should upgrade tier."""
        if current_tier == "enterprise":
            return None  # Already at top
        
        signals = []
        probability = 0.0
        
        # Usage exceeding tier limits
        if metrics.api_calls_30d > 50000:  # Example Pro limit
            signals.append("API usage exceeding tier limits")
            probability += 0.4
        
        # High feature adoption
        if metrics.total_features_available > 0:
            adoption = metrics.features_adopted / metrics.total_features_available
            if adoption > 0.7:
                signals.append("High feature adoption rate")
                probability += 0.2
        
        # Growth trajectory
        if metrics.api_calls_trend > 0.3:
            signals.append("Strong usage growth trajectory")
            probability += 0.2
        
        # Team growth
        if metrics.active_users > 5 and metrics.active_users_trend > 0.2:
            signals.append("Growing user base")
            probability += 0.1
        
        if probability < 0.3:
            return None
        
        next_tier = "pro" if current_tier == "community" else "enterprise"
        arr_increase = Decimal("1000") if next_tier == "pro" else Decimal("5000")
        
        return ExpansionOpportunity(
            customer_id=metrics.customer_id,
            opportunity_type="tier_upgrade",
            probability=min(1.0, probability),
            estimated_arr_increase=arr_increase,
            trigger_signals=signals,
            optimal_outreach_window="next 2 weeks",
            recommended_offer=f"Upgrade to {next_tier.title()} tier",
            talking_points=[
                f"Current usage suggests {next_tier} would be better fit",
                "Unlock advanced features and higher limits",
                "Annual commitment available with discount",
            ],
        )
    
    def _check_seat_expansion(
        self, metrics: UsageMetrics, current_seats: int
    ) -> Optional[ExpansionOpportunity]:
        """Check if customer needs more seats."""
        if metrics.active_users <= current_seats * 0.7:
            return None  # Not using existing seats
        
        signals = []
        probability = 0.0
        
        # Users near seat limit
        utilization = metrics.active_users / current_seats if current_seats > 0 else 0
        if utilization > 0.9:
            signals.append("Seat utilization above 90%")
            probability += 0.5
        elif utilization > 0.8:
            signals.append("Seat utilization above 80%")
            probability += 0.3
        
        # Growing user count
        if metrics.active_users_trend > 0.2:
            signals.append("User count growing")
            probability += 0.2
        
        if probability < 0.3:
            return None
        
        recommended_seats = max(current_seats + 5, int(metrics.active_users * 1.2))
        additional_seats = recommended_seats - current_seats
        
        return ExpansionOpportunity(
            customer_id=metrics.customer_id,
            opportunity_type="seat_expansion",
            probability=min(1.0, probability),
            estimated_arr_increase=Decimal(str(additional_seats * 10 * 12)),
            trigger_signals=signals,
            optimal_outreach_window="this week",
            recommended_offer=f"Add {additional_seats} seats",
            talking_points=[
                f"Team has grown to {metrics.active_users} active users",
                "Ensure everyone has proper access",
                "Volume discount available for larger seat packages",
            ],
        )
    
    def _check_addon_opportunities(
        self, metrics: UsageMetrics
    ) -> list[ExpansionOpportunity]:
        """Check for add-on product opportunities."""
        opportunities = []
        
        # Check for ML inference add-on
        # (Would check actual feature usage in production)
        
        # Check for premium support
        if metrics.support_tickets_30d > 3:
            opportunities.append(
                ExpansionOpportunity(
                    customer_id=metrics.customer_id,
                    opportunity_type="premium_support",
                    probability=0.4,
                    estimated_arr_increase=Decimal("2400"),
                    trigger_signals=["High support ticket volume"],
                    optimal_outreach_window="next month",
                    recommended_offer="Premium Support Package",
                    talking_points=[
                        "Dedicated support engineer",
                        "4-hour response time SLA",
                        "Quarterly business reviews",
                    ],
                )
            )
        
        return opportunities


# === Integration Functions ===

def calculate_customer_health(
    customer_id: str,
    api_calls_30d: int,
    api_calls_trend: float,
    active_users: int,
    features_adopted: int,
    support_tickets_30d: int = 0,
    nps_score: Optional[int] = None,
    mrr: float = 0,
    days_until_renewal: int = 365,
    is_annual: bool = False,
    last_login_days: int = 0,
) -> dict[str, Any]:
    """
    Calculate health score for a customer.
    
    Returns:
        Health score result as dictionary
    """
    metrics = UsageMetrics(
        customer_id=customer_id,
        api_calls_30d=api_calls_30d,
        api_calls_trend=api_calls_trend,
        active_users=active_users,
        features_adopted=features_adopted,
        support_tickets_30d=support_tickets_30d,
        nps_score=nps_score,
        mrr=Decimal(str(mrr)),
        days_until_renewal=days_until_renewal,
        is_annual_contract=is_annual,
        last_login_days_ago=last_login_days,
    )
    
    engine = HealthScoringEngine()
    score = engine.calculate_health_score(metrics)
    
    return {
        "customer_id": score.customer_id,
        "overall_score": score.overall_score,
        "category": score.category.name,
        "component_scores": {
            "usage": score.usage_score,
            "engagement": score.engagement_score,
            "support": score.support_score,
            "financial": score.financial_score,
        },
        "churn_risk": {
            "probability": score.churn_probability,
            "level": score.churn_risk.value,
        },
        "expansion": {
            "probability": score.expansion_probability,
            "opportunities": score.upsell_candidates,
        },
        "recommended_actions": [i.value for i in score.interventions],
        "priority": score.intervention_priority,
        "score_trend": score.score_trend,
    }


def predict_customer_churn(
    customer_id: str,
    api_calls_30d: int,
    api_calls_trend: float,
    active_users: int,
    last_login_days: int,
    support_tickets: int = 0,
    payment_failures: int = 0,
    nps_score: Optional[int] = None,
    is_annual: bool = False,
    days_until_renewal: int = 365,
) -> dict[str, Any]:
    """
    Predict churn probability for a customer.
    
    Returns:
        Churn prediction with risk factors and mitigation
    """
    metrics = UsageMetrics(
        customer_id=customer_id,
        api_calls_30d=api_calls_30d,
        api_calls_trend=api_calls_trend,
        active_users=active_users,
        last_login_days_ago=last_login_days,
        support_tickets_30d=support_tickets,
        payment_failures_90d=payment_failures,
        nps_score=nps_score,
        is_annual_contract=is_annual,
        days_until_renewal=days_until_renewal,
    )
    
    model = ChurnPredictionModel()
    prediction = model.predict_churn(metrics)
    
    return {
        "customer_id": prediction.customer_id,
        "churn_probability": prediction.churn_probability,
        "risk_level": prediction.risk_level.value,
        "risk_factors": prediction.risk_factors,
        "prediction_horizon_days": prediction.prediction_horizon_days,
        "mitigation_actions": prediction.mitigation_actions,
        "estimated_save_probability": prediction.estimated_save_probability,
    }


def find_expansion_opportunities(
    customer_id: str,
    current_tier: str,
    current_seats: int,
    api_calls_30d: int,
    api_calls_trend: float,
    active_users: int,
    active_users_trend: float,
    features_adopted: int,
    support_tickets: int = 0,
) -> list[dict[str, Any]]:
    """
    Find all expansion opportunities for a customer.
    
    Returns:
        List of expansion opportunities
    """
    metrics = UsageMetrics(
        customer_id=customer_id,
        api_calls_30d=api_calls_30d,
        api_calls_trend=api_calls_trend,
        active_users=active_users,
        active_users_trend=active_users_trend,
        features_adopted=features_adopted,
        support_tickets_30d=support_tickets,
    )
    
    detector = ExpansionDetector()
    opportunities = detector.detect_opportunities(metrics, current_tier, current_seats)
    
    return [
        {
            "customer_id": opp.customer_id,
            "opportunity_type": opp.opportunity_type,
            "probability": opp.probability,
            "estimated_arr_increase": float(opp.estimated_arr_increase),
            "trigger_signals": opp.trigger_signals,
            "optimal_outreach_window": opp.optimal_outreach_window,
            "recommended_offer": opp.recommended_offer,
            "talking_points": opp.talking_points,
        }
        for opp in opportunities
    ]


# === Stripe Metadata Integration ===

def get_stripe_health_metadata(health_score: HealthScore) -> dict[str, str]:
    """
    Generate Stripe-compatible metadata for health scoring.
    
    Args:
        health_score: Calculated health score
        
    Returns:
        Metadata dict for Stripe customer/subscription
    """
    return {
        "krl_health_score": str(health_score.overall_score),
        "krl_health_category": health_score.category.name,
        "krl_churn_probability": str(health_score.churn_probability),
        "krl_churn_risk": health_score.churn_risk.value,
        "krl_expansion_probability": str(health_score.expansion_probability),
        "krl_intervention_priority": str(health_score.intervention_priority),
        "krl_health_updated": health_score.calculated_at.isoformat(),
    }
