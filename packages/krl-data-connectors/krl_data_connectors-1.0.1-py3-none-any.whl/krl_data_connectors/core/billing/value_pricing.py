"""
KRL Value-Based Pricing Engine - DEPRECATED

⚠️ DEPRECATION WARNING (Dec 2025):
This module has been moved to krl-premium-backend.
Import from: app.services.billing.value_pricing

This stub remains for backward compatibility but will be removed in v2.0.
"""

from __future__ import annotations

import warnings
warnings.warn(
    "krl_data_connectors.core.billing.value_pricing is deprecated. "
    "This module has moved to krl-premium-backend. "
    "Import from 'app.services.billing.value_pricing' instead.",
    DeprecationWarning,
    stacklevel=2
)

import logging
import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, UTC
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Callable
from functools import lru_cache

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS & CONSTANTS
# =============================================================================

class CustomerSegment(Enum):
    """
    Customer segments based on firmographics, usage, and value profile.
    Each segment has different willingness-to-pay and pricing strategy.
    """
    # By company size
    STARTUP = "startup"              # <50 employees, Series A/B
    SMB = "smb"                       # 50-500 employees
    MIDMARKET = "midmarket"           # 500-5000 employees
    ENTERPRISE = "enterprise"         # 5000+ employees
    
    # By industry vertical
    GOVERNMENT = "government"         # Federal/state agencies, NGOs
    ACADEMIC = "academic"             # Universities, research institutions
    HEALTHCARE = "healthcare"         # Hospitals, pharma, biotech
    FINANCE = "finance"               # Banks, hedge funds, insurance
    CONSULTING = "consulting"         # Big 4, strategy firms
    
    # By usage pattern
    DEVELOPER = "developer"           # API-heavy, experimentation
    ANALYST = "analyst"               # Dashboard-heavy, reporting
    DATA_SCIENTIST = "data_scientist" # Model training, ML pipelines
    EXECUTIVE = "executive"           # High-level insights, minimal usage


class PricingTier(Enum):
    """
    KRL subscription tiers with associated base prices.
    See: Model_Monetization_Strategy.md Section 2.2
    """
    COMMUNITY = "community"           # Free, 20 models, 10K API calls
    PROFESSIONAL = "professional"     # $29-99/mo, 50 models, 100K API calls
    TEAM = "team"                     # $199-299/mo, 5 seats, collaboration
    ENTERPRISE = "enterprise"         # $999-5000/mo, unlimited, custom


class ValueDriver(Enum):
    """
    Key value drivers that translate platform features into customer outcomes.
    Used to calculate ROI and justify value-based pricing.
    """
    TIME_SAVED = "time_saved"                     # Analyst hours saved per month
    COST_REDUCTION = "cost_reduction"             # Infrastructure/tool cost savings
    REVENUE_IMPACT = "revenue_impact"             # Revenue enabled by insights
    RISK_MITIGATION = "risk_mitigation"           # Compliance/audit cost avoidance
    DECISION_QUALITY = "decision_quality"         # Better decisions from data
    SPEED_TO_INSIGHT = "speed_to_insight"         # Faster time-to-value
    DATA_ACCESS = "data_access"                   # Unique data not available elsewhere
    MODEL_ACCURACY = "model_accuracy"             # Improved prediction quality


class ContractType(Enum):
    """Contract structures that reduce churn and increase LTV."""
    MONTHLY = "monthly"               # Month-to-month, highest churn
    ANNUAL = "annual"                 # 12-month commitment, 15-20% discount
    MULTI_YEAR = "multi_year"         # 2-3 year, 25-35% discount
    ENTERPRISE = "enterprise"         # Custom terms, SLA, dedicated support
    PREPAID_CREDITS = "prepaid_credits"  # Upfront payment, credits expire


# Pricing configuration constants
VALUE_CAPTURE_MIN = Decimal("0.02")   # 2% minimum value capture
VALUE_CAPTURE_MAX = Decimal("0.10")   # 10% maximum value capture
VALUE_CAPTURE_DEFAULT = Decimal("0.05")  # 5% default

# Segment-specific value capture rates
SEGMENT_VALUE_CAPTURE: Dict[CustomerSegment, Decimal] = {
    CustomerSegment.STARTUP: Decimal("0.03"),       # Startups: 3% (price sensitive)
    CustomerSegment.SMB: Decimal("0.05"),           # SMB: 5% (balanced)
    CustomerSegment.MIDMARKET: Decimal("0.07"),     # Midmarket: 7% (less price sensitive)
    CustomerSegment.ENTERPRISE: Decimal("0.10"),    # Enterprise: 10% (value focused)
    CustomerSegment.GOVERNMENT: Decimal("0.04"),    # Government: 4% (budget constrained)
    CustomerSegment.ACADEMIC: Decimal("0.02"),      # Academic: 2% (educational discount)
    CustomerSegment.HEALTHCARE: Decimal("0.08"),    # Healthcare: 8% (compliance value)
    CustomerSegment.FINANCE: Decimal("0.10"),       # Finance: 10% (high value)
    CustomerSegment.CONSULTING: Decimal("0.06"),    # Consulting: 6% (project-based)
    CustomerSegment.DEVELOPER: Decimal("0.03"),     # Developer: 3% (individual)
    CustomerSegment.ANALYST: Decimal("0.05"),       # Analyst: 5% (team use)
    CustomerSegment.DATA_SCIENTIST: Decimal("0.06"),  # DS: 6% (power users)
    CustomerSegment.EXECUTIVE: Decimal("0.08"),     # Executive: 8% (strategic value)
}

# Annual discount by contract type
CONTRACT_DISCOUNTS: Dict[ContractType, Decimal] = {
    ContractType.MONTHLY: Decimal("0.00"),
    ContractType.ANNUAL: Decimal("0.17"),           # 17% discount (2 months free)
    ContractType.MULTI_YEAR: Decimal("0.30"),       # 30% discount
    ContractType.ENTERPRISE: Decimal("0.25"),       # 25% + custom terms
    ContractType.PREPAID_CREDITS: Decimal("0.20"),  # 20% discount
}


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class CustomerProfile:
    """
    Complete customer profile for pricing calculation.
    Combines firmographics, usage patterns, and value indicators.
    """
    # Identity
    customer_id: str
    company_name: str
    email: str
    
    # Firmographics
    employee_count: int
    annual_revenue: Optional[Decimal] = None  # In USD
    industry: Optional[str] = None
    country: str = "US"
    
    # Segments (can be multiple)
    segments: List[CustomerSegment] = field(default_factory=list)
    primary_segment: Optional[CustomerSegment] = None
    
    # Current state
    current_tier: PricingTier = PricingTier.COMMUNITY
    current_mrr: Decimal = Decimal("0")
    contract_type: ContractType = ContractType.MONTHLY
    contract_start: Optional[datetime] = None
    contract_end: Optional[datetime] = None
    
    # Usage patterns (last 30 days)
    api_calls: int = 0
    models_used: int = 0
    connectors_used: int = 0
    active_users: int = 1
    compute_hours: Decimal = Decimal("0")
    data_gb_processed: Decimal = Decimal("0")
    
    # Value indicators
    analyst_hours_saved: Decimal = Decimal("0")  # Estimated monthly
    decisions_influenced: int = 0
    reports_generated: int = 0
    
    # Health scores (0-100)
    engagement_score: int = 50
    expansion_potential: int = 50
    churn_risk: int = 50
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Auto-assign primary segment if not set."""
        if not self.primary_segment and self.segments:
            self.primary_segment = self.segments[0]
        elif not self.primary_segment:
            self.primary_segment = self._infer_segment()
    
    def _infer_segment(self) -> CustomerSegment:
        """Infer primary segment from firmographics."""
        if self.employee_count < 50:
            return CustomerSegment.STARTUP
        elif self.employee_count < 500:
            return CustomerSegment.SMB
        elif self.employee_count < 5000:
            return CustomerSegment.MIDMARKET
        else:
            return CustomerSegment.ENTERPRISE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert enums to strings
        data['segments'] = [s.value for s in self.segments]
        data['primary_segment'] = self.primary_segment.value if self.primary_segment else None
        data['current_tier'] = self.current_tier.value
        data['contract_type'] = self.contract_type.value
        # Convert decimals to strings
        for key in ['annual_revenue', 'current_mrr', 'compute_hours', 
                    'data_gb_processed', 'analyst_hours_saved']:
            if data[key] is not None:
                data[key] = str(data[key])
        # Convert datetimes
        for key in ['contract_start', 'contract_end', 'created_at', 'updated_at']:
            if data[key] is not None:
                data[key] = data[key].isoformat()
        return data


@dataclass
class ValueCalculation:
    """
    Detailed value calculation showing how customer value was computed.
    Used for sales enablement and pricing justification.
    """
    customer_id: str
    calculation_date: datetime
    
    # Input metrics
    inputs: Dict[str, Any] = field(default_factory=dict)
    
    # Value by driver
    value_by_driver: Dict[ValueDriver, Decimal] = field(default_factory=dict)
    
    # Totals
    total_monthly_value: Decimal = Decimal("0")
    total_annual_value: Decimal = Decimal("0")
    
    # Pricing outputs
    value_capture_rate: Decimal = VALUE_CAPTURE_DEFAULT
    recommended_monthly_price: Decimal = Decimal("0")
    recommended_annual_price: Decimal = Decimal("0")
    
    # Confidence
    confidence_score: Decimal = Decimal("0.5")  # 0-1
    confidence_factors: List[str] = field(default_factory=list)
    
    # Narrative
    value_story: str = ""
    key_benefits: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON/API response."""
        return {
            'customer_id': self.customer_id,
            'calculation_date': self.calculation_date.isoformat(),
            'inputs': self.inputs,
            'value_by_driver': {k.value: str(v) for k, v in self.value_by_driver.items()},
            'total_monthly_value': str(self.total_monthly_value),
            'total_annual_value': str(self.total_annual_value),
            'value_capture_rate': str(self.value_capture_rate),
            'recommended_monthly_price': str(self.recommended_monthly_price),
            'recommended_annual_price': str(self.recommended_annual_price),
            'confidence_score': str(self.confidence_score),
            'confidence_factors': self.confidence_factors,
            'value_story': self.value_story,
            'key_benefits': self.key_benefits,
        }


@dataclass
class PricingRecommendation:
    """
    Complete pricing recommendation for a customer.
    Includes tier, price, contract terms, and sales narrative.
    """
    customer_id: str
    generated_at: datetime
    
    # Recommended pricing
    recommended_tier: PricingTier
    recommended_contract: ContractType
    monthly_price: Decimal
    annual_price: Decimal
    
    # Price breakdown
    base_price: Decimal
    value_premium: Decimal
    segment_adjustment: Decimal
    contract_discount: Decimal
    
    # Comparison
    current_tier: Optional[PricingTier] = None
    current_price: Decimal = Decimal("0")
    price_increase: Decimal = Decimal("0")
    price_increase_pct: Decimal = Decimal("0")
    
    # Justification
    value_calculation: Optional[ValueCalculation] = None
    pricing_story: str = ""
    objection_handlers: Dict[str, str] = field(default_factory=dict)
    
    # Alternatives
    alternative_tiers: List[Dict[str, Any]] = field(default_factory=list)
    
    # Risk assessment
    acceptance_probability: Decimal = Decimal("0.5")
    churn_risk_if_applied: Decimal = Decimal("0.1")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'customer_id': self.customer_id,
            'generated_at': self.generated_at.isoformat(),
            'recommended_tier': self.recommended_tier.value,
            'recommended_contract': self.recommended_contract.value,
            'monthly_price': str(self.monthly_price),
            'annual_price': str(self.annual_price),
            'base_price': str(self.base_price),
            'value_premium': str(self.value_premium),
            'segment_adjustment': str(self.segment_adjustment),
            'contract_discount': str(self.contract_discount),
            'current_tier': self.current_tier.value if self.current_tier else None,
            'current_price': str(self.current_price),
            'price_increase': str(self.price_increase),
            'price_increase_pct': str(self.price_increase_pct),
            'value_calculation': self.value_calculation.to_dict() if self.value_calculation else None,
            'pricing_story': self.pricing_story,
            'objection_handlers': self.objection_handlers,
            'alternative_tiers': self.alternative_tiers,
            'acceptance_probability': str(self.acceptance_probability),
            'churn_risk_if_applied': str(self.churn_risk_if_applied),
        }


# =============================================================================
# ROI CALCULATOR
# =============================================================================

class ROICalculator:
    """
    Calculates customer ROI and value delivered by KRL platform.
    
    This is the foundation of value-based pricing - we must quantify
    the value we deliver before we can price appropriately.
    
    Value Drivers:
    1. Time Saved: Analyst hours saved through automation
    2. Cost Reduction: Tool consolidation, infrastructure savings
    3. Revenue Impact: Better decisions → more revenue
    4. Risk Mitigation: Compliance, audit, equity assessments
    5. Speed to Insight: Faster time-to-value
    6. Data Access: Unique data not available elsewhere
    7. Model Accuracy: Improved prediction quality
    """
    
    # Average hourly rates by role (USD)
    HOURLY_RATES = {
        "analyst": Decimal("75"),
        "senior_analyst": Decimal("100"),
        "data_scientist": Decimal("125"),
        "senior_data_scientist": Decimal("150"),
        "manager": Decimal("175"),
        "director": Decimal("225"),
        "vp": Decimal("300"),
        "executive": Decimal("400"),
    }
    
    # Time savings multipliers by feature
    TIME_SAVINGS_MULTIPLIERS = {
        "data_connectors": Decimal("0.40"),     # 40% of data wrangling time
        "pre_trained_models": Decimal("0.30"),  # 30% of model development
        "dashboards": Decimal("0.25"),          # 25% of reporting time
        "causal_inference": Decimal("0.50"),    # 50% of analysis time
        "network_analysis": Decimal("0.35"),    # 35% of graph work
    }
    
    # Tool cost replacements (monthly)
    TOOL_REPLACEMENTS = {
        "data_prep_tools": Decimal("500"),      # Trifacta, Alteryx alternatives
        "bi_dashboards": Decimal("300"),        # Tableau, Looker savings
        "ml_platforms": Decimal("1000"),        # DataRobot, H2O alternatives
        "data_subscriptions": Decimal("2000"),  # Various data feeds
    }
    
    def __init__(self):
        """Initialize ROI calculator."""
        self.logger = logging.getLogger(f"{__name__}.ROICalculator")
    
    def calculate_value(
        self,
        profile: CustomerProfile,
        usage_context: Optional[Dict[str, Any]] = None
    ) -> ValueCalculation:
        """
        Calculate total value delivered to customer.
        
        Args:
            profile: Customer profile with firmographics and usage
            usage_context: Additional context about how they use the platform
        
        Returns:
            ValueCalculation with detailed breakdown
        """
        calc = ValueCalculation(
            customer_id=profile.customer_id,
            calculation_date=datetime.now(UTC),
            inputs={
                'employee_count': profile.employee_count,
                'active_users': profile.active_users,
                'api_calls': profile.api_calls,
                'models_used': profile.models_used,
                'connectors_used': profile.connectors_used,
            }
        )
        
        # Calculate each value driver
        calc.value_by_driver[ValueDriver.TIME_SAVED] = self._calculate_time_saved(
            profile, usage_context
        )
        calc.value_by_driver[ValueDriver.COST_REDUCTION] = self._calculate_cost_reduction(
            profile, usage_context
        )
        calc.value_by_driver[ValueDriver.REVENUE_IMPACT] = self._calculate_revenue_impact(
            profile, usage_context
        )
        calc.value_by_driver[ValueDriver.RISK_MITIGATION] = self._calculate_risk_mitigation(
            profile, usage_context
        )
        calc.value_by_driver[ValueDriver.SPEED_TO_INSIGHT] = self._calculate_speed_value(
            profile, usage_context
        )
        calc.value_by_driver[ValueDriver.DATA_ACCESS] = self._calculate_data_access_value(
            profile, usage_context
        )
        
        # Sum total monthly value
        calc.total_monthly_value = sum(calc.value_by_driver.values())
        calc.total_annual_value = calc.total_monthly_value * 12
        
        # Determine value capture rate based on segment
        calc.value_capture_rate = SEGMENT_VALUE_CAPTURE.get(
            profile.primary_segment, VALUE_CAPTURE_DEFAULT
        )
        
        # Calculate recommended prices
        calc.recommended_monthly_price = (
            calc.total_monthly_value * calc.value_capture_rate
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        calc.recommended_annual_price = (
            calc.recommended_monthly_price * 12 * (1 - CONTRACT_DISCOUNTS[ContractType.ANNUAL])
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        # Calculate confidence
        calc.confidence_score, calc.confidence_factors = self._calculate_confidence(
            profile, calc
        )
        
        # Generate value story
        calc.value_story = self._generate_value_story(profile, calc)
        calc.key_benefits = self._generate_key_benefits(profile, calc)
        
        self.logger.info(
            f"Calculated value for {profile.customer_id}: "
            f"${calc.total_monthly_value}/mo, "
            f"recommended price: ${calc.recommended_monthly_price}/mo"
        )
        
        return calc
    
    def _calculate_time_saved(
        self,
        profile: CustomerProfile,
        context: Optional[Dict[str, Any]]
    ) -> Decimal:
        """
        Calculate monthly value of time saved.
        
        Formula: hours_saved * hourly_rate * users
        """
        # Base hours saved per user per month
        base_hours_saved = Decimal("0")
        
        # Data connectors: save 20 hours/month per analyst on data wrangling
        if profile.connectors_used > 0:
            connector_hours = Decimal("20") * self.TIME_SAVINGS_MULTIPLIERS["data_connectors"]
            base_hours_saved += connector_hours
        
        # Pre-trained models: save 40 hours/month on model development
        if profile.models_used > 0:
            model_hours = Decimal("40") * self.TIME_SAVINGS_MULTIPLIERS["pre_trained_models"]
            base_hours_saved += model_hours
        
        # Dashboards: save 10 hours/month on reporting
        if profile.reports_generated > 0:
            dashboard_hours = Decimal("10") * self.TIME_SAVINGS_MULTIPLIERS["dashboards"]
            base_hours_saved += dashboard_hours
        
        # Scale by number of active users
        total_hours_saved = base_hours_saved * profile.active_users
        
        # Determine appropriate hourly rate based on company size
        if profile.employee_count > 5000:
            hourly_rate = self.HOURLY_RATES["senior_data_scientist"]
        elif profile.employee_count > 500:
            hourly_rate = self.HOURLY_RATES["data_scientist"]
        else:
            hourly_rate = self.HOURLY_RATES["analyst"]
        
        return total_hours_saved * hourly_rate
    
    def _calculate_cost_reduction(
        self,
        profile: CustomerProfile,
        context: Optional[Dict[str, Any]]
    ) -> Decimal:
        """
        Calculate monthly value of tool/infrastructure cost reduction.
        """
        cost_savings = Decimal("0")
        
        # Data connector tools replaced
        if profile.connectors_used >= 5:
            cost_savings += self.TOOL_REPLACEMENTS["data_prep_tools"]
            cost_savings += self.TOOL_REPLACEMENTS["data_subscriptions"] * Decimal("0.5")
        
        # BI tools partially replaced
        if profile.reports_generated > 10:
            cost_savings += self.TOOL_REPLACEMENTS["bi_dashboards"] * Decimal("0.3")
        
        # ML platform replacement
        if profile.models_used >= 10:
            cost_savings += self.TOOL_REPLACEMENTS["ml_platforms"] * Decimal("0.4")
        
        return cost_savings
    
    def _calculate_revenue_impact(
        self,
        profile: CustomerProfile,
        context: Optional[Dict[str, Any]]
    ) -> Decimal:
        """
        Estimate revenue impact from better insights.
        
        Conservative estimate: 0.01-0.1% of revenue influenced by better decisions.
        """
        if profile.annual_revenue is None:
            return Decimal("0")
        
        # Base impact rate depends on how much they use the platform
        if profile.api_calls > 50000 and profile.models_used > 20:
            impact_rate = Decimal("0.001")  # 0.1% of revenue
        elif profile.api_calls > 10000 and profile.models_used > 5:
            impact_rate = Decimal("0.0005")  # 0.05% of revenue
        else:
            impact_rate = Decimal("0.0001")  # 0.01% of revenue
        
        annual_impact = profile.annual_revenue * impact_rate
        monthly_impact = annual_impact / 12
        
        return monthly_impact.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    def _calculate_risk_mitigation(
        self,
        profile: CustomerProfile,
        context: Optional[Dict[str, Any]]
    ) -> Decimal:
        """
        Calculate value of risk mitigation (compliance, equity assessments).
        
        Especially valuable for government, healthcare, finance segments.
        """
        risk_value = Decimal("0")
        
        # High-compliance industries get more value from equity-aware models
        high_compliance_segments = {
            CustomerSegment.GOVERNMENT,
            CustomerSegment.HEALTHCARE,
            CustomerSegment.FINANCE,
        }
        
        if profile.primary_segment in high_compliance_segments:
            # Value of avoiding compliance issues: $5K-50K/month equivalent
            base_risk_value = Decimal("5000")
            
            # Scale by company size
            if profile.employee_count > 5000:
                base_risk_value *= 10
            elif profile.employee_count > 500:
                base_risk_value *= 3
            
            # Discount by probability of issue (assume 10% monthly)
            risk_value = base_risk_value * Decimal("0.10")
        
        return risk_value
    
    def _calculate_speed_value(
        self,
        profile: CustomerProfile,
        context: Optional[Dict[str, Any]]
    ) -> Decimal:
        """
        Calculate value of faster time-to-insight.
        
        Faster insights = faster decisions = competitive advantage.
        """
        # Value is higher for fast-moving industries
        fast_industries = {"technology", "finance", "consulting"}
        
        if profile.industry and profile.industry.lower() in fast_industries:
            # Getting insights 2x faster is worth ~$2K/month for SMB
            speed_value = Decimal("2000")
            
            # Scale by company size
            if profile.employee_count > 5000:
                speed_value *= 5
            elif profile.employee_count > 500:
                speed_value *= 2
            
            return speed_value
        
        return Decimal("0")
    
    def _calculate_data_access_value(
        self,
        profile: CustomerProfile,
        context: Optional[Dict[str, Any]]
    ) -> Decimal:
        """
        Calculate value of access to unique data sources.
        
        Our 95+ connectors to socioeconomic data are unique in the market.
        """
        if profile.connectors_used == 0:
            return Decimal("0")
        
        # Each unique data source has value
        # Premium sources: ACLED, proprietary economic indicators
        # Standard sources: Census, WorldBank
        
        # Base value per connector per month
        base_value_per_connector = Decimal("100")
        
        # Premium connectors are worth more
        premium_connector_count = min(profile.connectors_used, 10)  # Cap at 10
        standard_connector_count = max(0, profile.connectors_used - 10)
        
        premium_value = premium_connector_count * base_value_per_connector * 3
        standard_value = standard_connector_count * base_value_per_connector
        
        return premium_value + standard_value
    
    def _calculate_confidence(
        self,
        profile: CustomerProfile,
        calc: ValueCalculation
    ) -> Tuple[Decimal, List[str]]:
        """
        Calculate confidence score in value calculation.
        
        Higher confidence when we have more data about the customer.
        """
        factors = []
        score = Decimal("0.5")  # Base confidence
        
        # Firmographic completeness
        if profile.annual_revenue is not None:
            score += Decimal("0.1")
            factors.append("Known revenue")
        else:
            factors.append("Revenue unknown (estimate used)")
        
        if profile.industry:
            score += Decimal("0.05")
            factors.append(f"Industry: {profile.industry}")
        
        # Usage data completeness
        if profile.api_calls > 0:
            score += Decimal("0.1")
            factors.append(f"{profile.api_calls:,} API calls observed")
        
        if profile.active_users > 1:
            score += Decimal("0.1")
            factors.append(f"{profile.active_users} active users")
        
        # Historical relationship
        if profile.current_tier != PricingTier.COMMUNITY:
            score += Decimal("0.1")
            factors.append("Existing paying customer")
        
        # Engagement score
        if profile.engagement_score > 70:
            score += Decimal("0.05")
            factors.append("High engagement")
        
        return min(score, Decimal("1.0")), factors
    
    def _generate_value_story(
        self,
        profile: CustomerProfile,
        calc: ValueCalculation
    ) -> str:
        """
        Generate a narrative explaining the value delivered.
        
        This is for sales enablement - helping reps tell the pricing story.
        """
        company = profile.company_name
        monthly_value = calc.total_monthly_value
        price = calc.recommended_monthly_price
        
        # Find top value driver
        top_driver = max(calc.value_by_driver.items(), key=lambda x: x[1])
        driver_name = top_driver[0].value.replace("_", " ").title()
        driver_value = top_driver[1]
        
        story = f"""
**Value Story for {company}**

{company} currently derives approximately **${monthly_value:,.0f}/month** in value from KRL, 
primarily through **{driver_name}** (${driver_value:,.0f}/month).

At the recommended price of **${price:,.0f}/month**, {company} achieves a 
**{int(monthly_value / price) if price > 0 else 0}x return** on their investment.

Key value drivers:
"""
        for driver, value in sorted(calc.value_by_driver.items(), key=lambda x: -x[1]):
            if value > 0:
                story += f"- {driver.value.replace('_', ' ').title()}: ${value:,.0f}/month\n"
        
        return story.strip()
    
    def _generate_key_benefits(
        self,
        profile: CustomerProfile,
        calc: ValueCalculation
    ) -> List[str]:
        """Generate list of key benefits for this customer."""
        benefits = []
        
        for driver, value in calc.value_by_driver.items():
            if value > 0:
                if driver == ValueDriver.TIME_SAVED:
                    hours = value / self.HOURLY_RATES["analyst"]
                    benefits.append(f"Save {hours:.0f}+ analyst hours per month")
                elif driver == ValueDriver.COST_REDUCTION:
                    benefits.append(f"Reduce tool costs by ${value:,.0f}/month")
                elif driver == ValueDriver.RISK_MITIGATION:
                    benefits.append("Ensure equity compliance in all analyses")
                elif driver == ValueDriver.DATA_ACCESS:
                    benefits.append(f"Access {profile.connectors_used}+ unique data sources")
        
        return benefits[:5]  # Top 5 benefits


# =============================================================================
# VALUE-BASED PRICING ENGINE
# =============================================================================

class ValueBasedPricingEngine:
    """
    Generates pricing recommendations based on customer value.
    
    Philosophy: Price is a story. We price based on the value we deliver,
    not our costs or competitor prices.
    
    Process:
    1. Calculate value delivered (ROI Calculator)
    2. Apply segment-specific value capture rate (2-10%)
    3. Adjust for contract type and term
    4. Generate pricing story and objection handlers
    """
    
    # Base prices by tier (monthly)
    BASE_PRICES: Dict[PricingTier, Decimal] = {
        PricingTier.COMMUNITY: Decimal("0"),
        PricingTier.PROFESSIONAL: Decimal("29"),
        PricingTier.TEAM: Decimal("199"),
        PricingTier.ENTERPRISE: Decimal("999"),
    }
    
    # Price caps by tier (monthly)
    PRICE_CAPS: Dict[PricingTier, Decimal] = {
        PricingTier.COMMUNITY: Decimal("0"),
        PricingTier.PROFESSIONAL: Decimal("99"),
        PricingTier.TEAM: Decimal("499"),
        PricingTier.ENTERPRISE: Decimal("5000"),
    }
    
    def __init__(self, roi_calculator: Optional[ROICalculator] = None):
        """Initialize pricing engine."""
        self.roi_calculator = roi_calculator or ROICalculator()
        self.logger = logging.getLogger(f"{__name__}.ValueBasedPricingEngine")
    
    def generate_recommendation(
        self,
        profile: CustomerProfile,
        usage_context: Optional[Dict[str, Any]] = None
    ) -> PricingRecommendation:
        """
        Generate complete pricing recommendation for customer.
        
        Args:
            profile: Customer profile
            usage_context: Additional usage context
        
        Returns:
            PricingRecommendation with tier, price, and justification
        """
        # Step 1: Calculate value
        value_calc = self.roi_calculator.calculate_value(profile, usage_context)
        
        # Step 2: Determine appropriate tier
        recommended_tier = self._determine_tier(profile, value_calc)
        
        # Step 3: Calculate value-based price
        base_price = self.BASE_PRICES[recommended_tier]
        value_premium = self._calculate_value_premium(profile, value_calc, recommended_tier)
        segment_adjustment = self._calculate_segment_adjustment(profile, base_price)
        
        # Calculate monthly price (base + premium + segment adjustment)
        monthly_price = base_price + value_premium + segment_adjustment
        
        # Apply tier caps
        monthly_price = min(monthly_price, self.PRICE_CAPS[recommended_tier])
        monthly_price = max(monthly_price, base_price)  # Never below base
        
        # Step 4: Determine contract type and discount
        recommended_contract = self._determine_contract(profile, value_calc)
        contract_discount = CONTRACT_DISCOUNTS[recommended_contract]
        
        # Calculate annual price with discount
        annual_price = monthly_price * 12 * (1 - contract_discount)
        
        # Step 5: Build recommendation
        rec = PricingRecommendation(
            customer_id=profile.customer_id,
            generated_at=datetime.now(UTC),
            recommended_tier=recommended_tier,
            recommended_contract=recommended_contract,
            monthly_price=monthly_price.quantize(Decimal("0.01")),
            annual_price=annual_price.quantize(Decimal("0.01")),
            base_price=base_price,
            value_premium=value_premium.quantize(Decimal("0.01")),
            segment_adjustment=segment_adjustment.quantize(Decimal("0.01")),
            contract_discount=contract_discount,
            current_tier=profile.current_tier,
            current_price=profile.current_mrr,
            value_calculation=value_calc,
        )
        
        # Calculate price change
        if profile.current_mrr > 0:
            rec.price_increase = rec.monthly_price - profile.current_mrr
            rec.price_increase_pct = (
                rec.price_increase / profile.current_mrr * 100
            ).quantize(Decimal("0.1"))
        
        # Generate narrative
        rec.pricing_story = self._generate_pricing_story(profile, rec)
        rec.objection_handlers = self._generate_objection_handlers(profile, rec)
        rec.alternative_tiers = self._generate_alternatives(profile, rec)
        
        # Risk assessment
        rec.acceptance_probability = self._estimate_acceptance(profile, rec)
        rec.churn_risk_if_applied = self._estimate_churn_risk(profile, rec)
        
        self.logger.info(
            f"Generated recommendation for {profile.customer_id}: "
            f"{recommended_tier.value} at ${monthly_price}/mo"
        )
        
        return rec
    
    def _determine_tier(
        self,
        profile: CustomerProfile,
        value_calc: ValueCalculation
    ) -> PricingTier:
        """Determine appropriate pricing tier based on usage and value."""
        # High-value customers → Enterprise
        if value_calc.total_monthly_value > Decimal("10000"):
            return PricingTier.ENTERPRISE
        
        # Team usage → Team tier
        if profile.active_users > 3:
            return PricingTier.TEAM
        
        # Significant usage → Professional
        if (profile.api_calls > 5000 or 
            profile.models_used > 5 or 
            value_calc.total_monthly_value > Decimal("1000")):
            return PricingTier.PROFESSIONAL
        
        # Default to community
        return PricingTier.COMMUNITY
    
    def _calculate_value_premium(
        self,
        profile: CustomerProfile,
        value_calc: ValueCalculation,
        tier: PricingTier
    ) -> Decimal:
        """
        Calculate premium above base price based on value delivered.
        
        Premium = (Total Value × Capture Rate) - Base Price
        """
        if tier == PricingTier.COMMUNITY:
            return Decimal("0")
        
        value_based_price = (
            value_calc.total_monthly_value * value_calc.value_capture_rate
        )
        
        base = self.BASE_PRICES[tier]
        premium = max(Decimal("0"), value_based_price - base)
        
        return premium
    
    def _calculate_segment_adjustment(
        self,
        profile: CustomerProfile,
        base_price: Decimal
    ) -> Decimal:
        """
        Adjust price based on customer segment.
        
        - Academic/Nonprofit: -30%
        - Government: -20%
        - Enterprise: +20%
        - Finance: +30%
        """
        adjustments = {
            CustomerSegment.ACADEMIC: Decimal("-0.30"),
            CustomerSegment.GOVERNMENT: Decimal("-0.20"),
            CustomerSegment.STARTUP: Decimal("-0.10"),
            CustomerSegment.ENTERPRISE: Decimal("0.20"),
            CustomerSegment.FINANCE: Decimal("0.30"),
            CustomerSegment.HEALTHCARE: Decimal("0.20"),
        }
        
        adjustment_rate = adjustments.get(profile.primary_segment, Decimal("0"))
        return base_price * adjustment_rate
    
    def _determine_contract(
        self,
        profile: CustomerProfile,
        value_calc: ValueCalculation
    ) -> ContractType:
        """Recommend contract type based on customer profile."""
        # Enterprise customers → multi-year or enterprise contracts
        if profile.primary_segment == CustomerSegment.ENTERPRISE:
            return ContractType.ENTERPRISE
        
        # High-value with low churn risk → annual
        if (value_calc.total_annual_value > Decimal("50000") and 
            profile.churn_risk < 30):
            return ContractType.ANNUAL
        
        # Government often prefers annual (budget cycles)
        if profile.primary_segment == CustomerSegment.GOVERNMENT:
            return ContractType.ANNUAL
        
        # Default to monthly for flexibility
        return ContractType.MONTHLY
    
    def _generate_pricing_story(
        self,
        profile: CustomerProfile,
        rec: PricingRecommendation
    ) -> str:
        """Generate sales narrative for the pricing."""
        if rec.value_calculation is None:
            return "Standard pricing based on tier features."
        
        vc = rec.value_calculation
        roi = (vc.total_monthly_value / rec.monthly_price
               if rec.monthly_price > 0 else Decimal("0"))
        
        story = f"""
## Pricing Rationale for {profile.company_name}

### Value Delivered
{profile.company_name} currently realizes **${vc.total_monthly_value:,.0f}/month** in value 
from KRL through:
{chr(10).join(f'- {b}' for b in vc.key_benefits)}

### Investment
At **${rec.monthly_price:,.0f}/month** ({rec.recommended_tier.value.title()} tier), 
{profile.company_name} achieves a **{roi:.0f}x ROI**.

### Why This Price?
- Base {rec.recommended_tier.value.title()} tier: ${rec.base_price}/month
- Value-based premium: ${rec.value_premium}/month
- Segment adjustment: ${rec.segment_adjustment}/month

### Contract Recommendation
We recommend a **{rec.recommended_contract.value.replace('_', ' ').title()}** contract 
with a **{int(rec.contract_discount * 100)}% discount** for commitment.
"""
        return story.strip()
    
    def _generate_objection_handlers(
        self,
        profile: CustomerProfile,
        rec: PricingRecommendation
    ) -> Dict[str, str]:
        """Generate responses to common pricing objections."""
        handlers = {}
        
        # Price increase objection
        if rec.price_increase_pct > 0:
            handlers["price_increase"] = f"""
Your current plan at ${rec.current_price}/mo doesn't fully capture the value you're 
receiving. Based on {rec.value_calculation.total_monthly_value if rec.value_calculation else 'N/A'}/mo 
in analyst time saved and cost reduction, this {rec.price_increase_pct}% adjustment 
still delivers {int(rec.value_calculation.total_monthly_value / rec.monthly_price) if rec.value_calculation and rec.monthly_price > 0 else 'significant'}x ROI.
"""
        
        # Competitor comparison
        handlers["competitor_pricing"] = """
Unlike general-purpose ML platforms, KRL is purpose-built for equity-aware policy 
analysis with 95+ socioeconomic data connectors. The alternative isn't cheaper software—
it's building this capability internally, which typically costs 3-5x more.
"""
        
        # Budget constraint
        handlers["budget_constraint"] = f"""
We offer flexible options:
- Annual commitment: {int(CONTRACT_DISCOUNTS[ContractType.ANNUAL] * 100)}% discount
- Multi-year: {int(CONTRACT_DISCOUNTS[ContractType.MULTI_YEAR] * 100)}% discount
- Academic/nonprofit: Additional 30% discount
- Start with a lower tier and upgrade as value becomes clear
"""
        
        # Not ready to commit
        handlers["not_ready"] = """
Start with our Community tier (free) to validate the value. Once you've seen the 
time savings and insight quality, upgrading is seamless. Most teams upgrade within 
60 days of active use.
"""
        
        return handlers
    
    def _generate_alternatives(
        self,
        profile: CustomerProfile,
        rec: PricingRecommendation
    ) -> List[Dict[str, Any]]:
        """Generate alternative tier options."""
        alternatives = []
        
        for tier in PricingTier:
            if tier == rec.recommended_tier:
                continue
            
            base = self.BASE_PRICES[tier]
            if tier == PricingTier.COMMUNITY:
                alternatives.append({
                    'tier': tier.value,
                    'price': '0',
                    'note': 'Free tier with limited features - good for evaluation',
                })
            elif tier == PricingTier.PROFESSIONAL:
                alternatives.append({
                    'tier': tier.value,
                    'price': str(base),
                    'note': 'Individual use - 100K API calls, 50 models',
                })
            elif tier == PricingTier.TEAM:
                alternatives.append({
                    'tier': tier.value,
                    'price': str(base),
                    'note': 'Up to 5 seats, collaboration features',
                })
            elif tier == PricingTier.ENTERPRISE:
                alternatives.append({
                    'tier': tier.value,
                    'price': f'{base}+',
                    'note': 'Unlimited usage, SSO, dedicated support, SLA',
                })
        
        return alternatives
    
    def _estimate_acceptance(
        self,
        profile: CustomerProfile,
        rec: PricingRecommendation
    ) -> Decimal:
        """Estimate probability customer accepts the price."""
        base_probability = Decimal("0.50")
        
        # Higher engagement → higher acceptance
        if profile.engagement_score > 70:
            base_probability += Decimal("0.15")
        elif profile.engagement_score > 50:
            base_probability += Decimal("0.05")
        
        # Existing customer more likely to accept upgrade
        if profile.current_tier != PricingTier.COMMUNITY:
            base_probability += Decimal("0.10")
        
        # Large price increase → lower acceptance
        if rec.price_increase_pct > 50:
            base_probability -= Decimal("0.20")
        elif rec.price_increase_pct > 25:
            base_probability -= Decimal("0.10")
        
        # High-value customers more likely to see ROI
        if (rec.value_calculation and 
            rec.value_calculation.total_monthly_value > Decimal("5000")):
            base_probability += Decimal("0.10")
        
        return min(max(base_probability, Decimal("0.10")), Decimal("0.95"))
    
    def _estimate_churn_risk(
        self,
        profile: CustomerProfile,
        rec: PricingRecommendation
    ) -> Decimal:
        """Estimate churn risk if price is applied."""
        base_risk = Decimal(str(profile.churn_risk / 100))
        
        # Price increase adds churn risk
        if rec.price_increase_pct > 50:
            base_risk += Decimal("0.15")
        elif rec.price_increase_pct > 25:
            base_risk += Decimal("0.08")
        
        # Multi-year contract reduces churn
        if rec.recommended_contract in [ContractType.ANNUAL, ContractType.MULTI_YEAR]:
            base_risk -= Decimal("0.10")
        
        return min(max(base_risk, Decimal("0.01")), Decimal("0.50"))


# =============================================================================
# CUSTOMER SEGMENTATION ENGINE
# =============================================================================

class CustomerSegmentationEngine:
    """
    Segments customers for targeted pricing and marketing.
    
    Uses K-means clustering on:
    - Firmographics (size, revenue, industry)
    - Usage patterns (API calls, features used)
    - Value indicators (engagement, expansion potential)
    - Behavioral signals (time-to-value, feature adoption)
    """
    
    def __init__(self):
        """Initialize segmentation engine."""
        self.logger = logging.getLogger(f"{__name__}.CustomerSegmentationEngine")
    
    def segment_customer(self, profile: CustomerProfile) -> List[CustomerSegment]:
        """
        Assign segments to a customer based on their profile.
        
        Returns list of applicable segments (primary first).
        """
        segments = []
        
        # Size-based segment (always assigned)
        size_segment = self._segment_by_size(profile)
        segments.append(size_segment)
        
        # Industry segment (if identifiable)
        if profile.industry:
            industry_segment = self._segment_by_industry(profile.industry)
            if industry_segment:
                segments.append(industry_segment)
        
        # Usage-based segment
        usage_segment = self._segment_by_usage(profile)
        if usage_segment and usage_segment not in segments:
            segments.append(usage_segment)
        
        return segments
    
    def _segment_by_size(self, profile: CustomerProfile) -> CustomerSegment:
        """Segment by company size."""
        if profile.employee_count < 50:
            return CustomerSegment.STARTUP
        elif profile.employee_count < 500:
            return CustomerSegment.SMB
        elif profile.employee_count < 5000:
            return CustomerSegment.MIDMARKET
        else:
            return CustomerSegment.ENTERPRISE
    
    def _segment_by_industry(self, industry: str) -> Optional[CustomerSegment]:
        """Segment by industry vertical."""
        industry_lower = industry.lower()
        
        industry_map = {
            'government': CustomerSegment.GOVERNMENT,
            'federal': CustomerSegment.GOVERNMENT,
            'state': CustomerSegment.GOVERNMENT,
            'public sector': CustomerSegment.GOVERNMENT,
            'ngo': CustomerSegment.GOVERNMENT,
            'nonprofit': CustomerSegment.GOVERNMENT,
            
            'university': CustomerSegment.ACADEMIC,
            'academic': CustomerSegment.ACADEMIC,
            'research': CustomerSegment.ACADEMIC,
            'education': CustomerSegment.ACADEMIC,
            
            'healthcare': CustomerSegment.HEALTHCARE,
            'health': CustomerSegment.HEALTHCARE,
            'pharma': CustomerSegment.HEALTHCARE,
            'biotech': CustomerSegment.HEALTHCARE,
            'hospital': CustomerSegment.HEALTHCARE,
            
            'finance': CustomerSegment.FINANCE,
            'banking': CustomerSegment.FINANCE,
            'insurance': CustomerSegment.FINANCE,
            'investment': CustomerSegment.FINANCE,
            'fintech': CustomerSegment.FINANCE,
            
            'consulting': CustomerSegment.CONSULTING,
            'advisory': CustomerSegment.CONSULTING,
            'professional services': CustomerSegment.CONSULTING,
        }
        
        for keyword, segment in industry_map.items():
            if keyword in industry_lower:
                return segment
        
        return None
    
    def _segment_by_usage(self, profile: CustomerProfile) -> Optional[CustomerSegment]:
        """Segment by usage pattern."""
        # Heavy API usage → Developer
        if profile.api_calls > 50000:
            return CustomerSegment.DEVELOPER
        
        # Dashboard/report heavy → Analyst
        if profile.reports_generated > 20:
            return CustomerSegment.ANALYST
        
        # Model training heavy → Data Scientist
        if profile.models_used > 15:
            return CustomerSegment.DATA_SCIENTIST
        
        return None
    
    def calculate_expansion_potential(self, profile: CustomerProfile) -> int:
        """
        Calculate expansion potential score (0-100).
        
        Identifies customers likely to upgrade or expand usage.
        """
        score = 50  # Base score
        
        # Growing usage → high expansion potential
        # (Would need historical data for real calculation)
        if profile.api_calls > 50000:
            score += 15
        if profile.active_users > 3:
            score += 15
        if profile.models_used > 10:
            score += 10
        
        # Engagement indicates willingness to invest more
        if profile.engagement_score > 70:
            score += 10
        
        # Current tier has room to grow
        if profile.current_tier == PricingTier.COMMUNITY:
            score += 10
        elif profile.current_tier == PricingTier.PROFESSIONAL:
            score += 5
        
        return min(max(score, 0), 100)
    
    def identify_expansion_triggers(
        self, 
        profile: CustomerProfile
    ) -> List[Dict[str, str]]:
        """
        Identify signals that customer is ready to expand.
        
        Returns list of triggers with recommended actions.
        """
        triggers = []
        
        # Usage approaching limits
        tier_limits = {
            PricingTier.COMMUNITY: 10000,
            PricingTier.PROFESSIONAL: 100000,
            PricingTier.TEAM: 500000,
        }
        limit = tier_limits.get(profile.current_tier, 1000000)
        usage_pct = profile.api_calls / limit * 100
        
        if usage_pct > 80:
            triggers.append({
                'trigger': 'usage_limit_approaching',
                'signal': f'{usage_pct:.0f}% of API quota used',
                'action': 'Reach out about tier upgrade',
                'urgency': 'high' if usage_pct > 90 else 'medium',
            })
        
        # Adding team members
        if profile.active_users > 3 and profile.current_tier == PricingTier.PROFESSIONAL:
            triggers.append({
                'trigger': 'team_growth',
                'signal': f'{profile.active_users} active users on individual plan',
                'action': 'Propose Team tier',
                'urgency': 'medium',
            })
        
        # High engagement
        if profile.engagement_score > 80:
            triggers.append({
                'trigger': 'high_engagement',
                'signal': f'Engagement score: {profile.engagement_score}',
                'action': 'NPS survey, case study opportunity',
                'urgency': 'low',
            })
        
        # Premium feature exploration
        if profile.connectors_used > 10:
            triggers.append({
                'trigger': 'feature_exploration',
                'signal': f'{profile.connectors_used} connectors in use',
                'action': 'Demo advanced analytics features',
                'urgency': 'medium',
            })
        
        return triggers


# =============================================================================
# STRIPE METADATA INTEGRATION
# =============================================================================

def generate_stripe_metadata(
    profile: CustomerProfile,
    recommendation: PricingRecommendation
) -> Dict[str, str]:
    """
    Generate Stripe metadata from pricing recommendation.
    
    This metadata is attached to Stripe customers, subscriptions, and invoices
    for analytics, segmentation, and feature gating.
    
    Stripe limits:
    - 50 keys max
    - Key names up to 40 chars
    - Values up to 500 chars
    """
    metadata = {
        # Core identifiers
        'krl_tenant_id': profile.customer_id[:40],
        'krl_version': '2.0',
        
        # Segmentation
        'krl_segment_primary': profile.primary_segment.value if profile.primary_segment else 'unknown',
        'krl_segment_size': CustomerSegmentationEngine()._segment_by_size(profile).value,
        'krl_industry': (profile.industry or 'unknown')[:40],
        
        # Pricing
        'krl_tier': recommendation.recommended_tier.value,
        'krl_contract_type': recommendation.recommended_contract.value,
        'krl_price_monthly': str(recommendation.monthly_price),
        'krl_price_annual': str(recommendation.annual_price),
        
        # Value metrics
        'krl_value_monthly': str(recommendation.value_calculation.total_monthly_value if recommendation.value_calculation else '0'),
        'krl_value_capture_rate': str(recommendation.value_calculation.value_capture_rate if recommendation.value_calculation else '0.05'),
        
        # Health scores
        'krl_engagement_score': str(profile.engagement_score),
        'krl_expansion_potential': str(profile.expansion_potential),
        'krl_churn_risk': str(profile.churn_risk),
        
        # Usage context
        'krl_api_calls': str(profile.api_calls),
        'krl_active_users': str(profile.active_users),
        'krl_models_used': str(profile.models_used),
        'krl_connectors_used': str(profile.connectors_used),
        
        # Company info
        'krl_company': profile.company_name[:40],
        'krl_employee_count': str(profile.employee_count),
        
        # Timestamps
        'krl_last_priced': datetime.now(UTC).isoformat()[:19],
    }
    
    return metadata


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def calculate_customer_price(
    customer_id: str,
    company_name: str,
    email: str,
    employee_count: int,
    api_calls: int = 0,
    models_used: int = 0,
    connectors_used: int = 0,
    active_users: int = 1,
    industry: Optional[str] = None,
    annual_revenue: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Convenience function to calculate pricing for a customer.
    
    Returns dict with recommended tier, price, and value justification.
    """
    # Build profile
    profile = CustomerProfile(
        customer_id=customer_id,
        company_name=company_name,
        email=email,
        employee_count=employee_count,
        api_calls=api_calls,
        models_used=models_used,
        connectors_used=connectors_used,
        active_users=active_users,
        industry=industry,
        annual_revenue=Decimal(str(annual_revenue)) if annual_revenue else None,
    )
    
    # Segment
    segmentation = CustomerSegmentationEngine()
    profile.segments = segmentation.segment_customer(profile)
    profile.primary_segment = profile.segments[0] if profile.segments else None
    profile.expansion_potential = segmentation.calculate_expansion_potential(profile)
    
    # Price
    pricing = ValueBasedPricingEngine()
    recommendation = pricing.generate_recommendation(profile)
    
    # Generate Stripe metadata
    stripe_metadata = generate_stripe_metadata(profile, recommendation)
    
    return {
        'profile': profile.to_dict(),
        'recommendation': recommendation.to_dict(),
        'stripe_metadata': stripe_metadata,
    }


# Example usage
if __name__ == "__main__":
    # Example: Price a mid-market fintech company
    result = calculate_customer_price(
        customer_id="cust_example_123",
        company_name="Acme Financial Analytics",
        email="cfo@acmefinancial.com",
        employee_count=800,
        api_calls=45000,
        models_used=12,
        connectors_used=8,
        active_users=5,
        industry="Fintech",
        annual_revenue=50_000_000,
    )
    
    print(json.dumps(result, indent=2, default=str))
