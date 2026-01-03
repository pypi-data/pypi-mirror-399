# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
#
# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.revenue_reporting
# This stub remains for backward compatibility but will be removed in v2.0.
# ----------------------------------------------------------------------

from __future__ import annotations

import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.revenue_reporting is deprecated. "
    "Import from 'app.services.billing.revenue_reporting' instead.",
    DeprecationWarning,
    stacklevel=2
)


"""
KRL Revenue Reporting Engine - Week 24 Day 1
============================================

Comprehensive revenue reporting with MRR/ARR/LTV calculations,
subscription metrics, and revenue breakdown by segment.

Reports:
- Executive Revenue Summary
- MRR/ARR Trends & Projections
- Customer LTV Analysis
- Revenue by Tier/Segment
- Subscription Health Metrics
"""


import logging
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

class ReportPeriod(str, Enum):
    """Report time periods."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class RevenueSegment(str, Enum):
    """Revenue segmentation types."""
    BY_TIER = "by_tier"
    BY_REGION = "by_region"
    BY_COHORT = "by_cohort"
    BY_ACQUISITION = "by_acquisition"
    BY_INDUSTRY = "by_industry"


class MetricType(str, Enum):
    """Revenue metric types."""
    MRR = "mrr"
    ARR = "arr"
    NET_REVENUE = "net_revenue"
    GROSS_REVENUE = "gross_revenue"
    EXPANSION_MRR = "expansion_mrr"
    CONTRACTION_MRR = "contraction_mrr"
    CHURN_MRR = "churn_mrr"
    NEW_MRR = "new_mrr"


class ReportFormat(str, Enum):
    """Report output formats."""
    JSON = "json"
    DATAFRAME = "dataframe"
    HTML = "html"
    PDF = "pdf"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class RevenueMetrics:
    """Core revenue metrics snapshot."""
    timestamp: datetime
    mrr: Decimal
    arr: Decimal
    gross_revenue: Decimal
    net_revenue: Decimal
    new_mrr: Decimal = Decimal("0")
    expansion_mrr: Decimal = Decimal("0")
    contraction_mrr: Decimal = Decimal("0")
    churn_mrr: Decimal = Decimal("0")
    reactivation_mrr: Decimal = Decimal("0")
    
    @property
    def net_mrr_change(self) -> Decimal:
        """Net MRR movement."""
        return self.new_mrr + self.expansion_mrr + self.reactivation_mrr - self.contraction_mrr - self.churn_mrr
    
    @property
    def growth_rate(self) -> float:
        """MRR growth rate."""
        if self.mrr == 0:
            return 0.0
        return float(self.net_mrr_change / self.mrr) * 100


@dataclass
class SubscriptionMetrics:
    """Subscription-level metrics."""
    timestamp: datetime
    total_subscriptions: int
    active_subscriptions: int
    trial_subscriptions: int
    cancelled_subscriptions: int
    past_due_subscriptions: int
    
    # Movement
    new_subscriptions: int = 0
    upgrades: int = 0
    downgrades: int = 0
    churned: int = 0
    reactivations: int = 0
    
    @property
    def churn_rate(self) -> float:
        """Subscription churn rate."""
        if self.active_subscriptions == 0:
            return 0.0
        return self.churned / self.active_subscriptions * 100
    
    @property
    def net_growth(self) -> int:
        """Net subscription growth."""
        return self.new_subscriptions + self.reactivations - self.churned


@dataclass
class CustomerMetrics:
    """Customer-level metrics."""
    timestamp: datetime
    total_customers: int
    paying_customers: int
    free_customers: int
    enterprise_customers: int
    
    # Averages
    arpu: Decimal = Decimal("0")  # Average Revenue Per User
    arppu: Decimal = Decimal("0")  # Average Revenue Per Paying User
    avg_ltv: Decimal = Decimal("0")
    avg_subscription_age_days: float = 0.0


@dataclass
class TierBreakdown:
    """Revenue breakdown by tier."""
    tier: str
    customer_count: int
    subscription_count: int
    mrr: Decimal
    arr: Decimal
    percentage_of_total: float
    avg_revenue_per_customer: Decimal


@dataclass
class RevenueReport:
    """Complete revenue report."""
    report_id: str
    generated_at: datetime
    period: ReportPeriod
    start_date: datetime
    end_date: datetime
    
    # Core metrics
    revenue_metrics: RevenueMetrics
    subscription_metrics: SubscriptionMetrics
    customer_metrics: CustomerMetrics
    
    # Breakdowns
    tier_breakdown: List[TierBreakdown] = field(default_factory=list)
    
    # Trends
    mrr_trend: List[Tuple[datetime, Decimal]] = field(default_factory=list)
    arr_trend: List[Tuple[datetime, Decimal]] = field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LTVReport:
    """Customer Lifetime Value report."""
    report_id: str
    generated_at: datetime
    
    # Aggregates
    avg_ltv: Decimal
    median_ltv: Decimal
    total_ltv: Decimal
    
    # By tier
    ltv_by_tier: Dict[str, Decimal] = field(default_factory=dict)
    
    # By cohort
    ltv_by_cohort: Dict[str, Decimal] = field(default_factory=dict)
    
    # Projections
    projected_ltv_12m: Decimal = Decimal("0")
    projected_ltv_24m: Decimal = Decimal("0")


# =============================================================================
# Revenue Calculator
# =============================================================================

class RevenueCalculator:
    """
    Calculates revenue metrics from subscription data.
    
    Handles:
    - MRR/ARR calculations with proration
    - Revenue movement tracking
    - LTV calculations
    """
    
    def __init__(self, currency: str = "USD"):
        self.currency = currency
        self._discount_rate = 0.10  # For LTV calculations
    
    def calculate_mrr(
        self,
        subscriptions: List[Dict[str, Any]],
        as_of: Optional[datetime] = None,
    ) -> Decimal:
        """Calculate Monthly Recurring Revenue."""
        as_of = as_of or datetime.now(timezone.utc)
        total_mrr = Decimal("0")
        
        for sub in subscriptions:
            if sub.get("status") not in ("active", "trialing"):
                continue
            
            # Normalize to monthly
            amount = Decimal(str(sub.get("amount", 0)))
            interval = sub.get("interval", "month")
            
            if interval == "year":
                amount = amount / 12
            elif interval == "week":
                amount = amount * Decimal("4.33")
            elif interval == "day":
                amount = amount * 30
            
            total_mrr += amount
        
        return total_mrr.quantize(Decimal("0.01"))
    
    def calculate_arr(self, mrr: Decimal) -> Decimal:
        """Calculate Annual Recurring Revenue from MRR."""
        return (mrr * 12).quantize(Decimal("0.01"))
    
    def calculate_mrr_movement(
        self,
        current_subscriptions: List[Dict[str, Any]],
        previous_subscriptions: List[Dict[str, Any]],
    ) -> Dict[str, Decimal]:
        """Calculate MRR movement components."""
        current_map = {s["id"]: s for s in current_subscriptions}
        previous_map = {s["id"]: s for s in previous_subscriptions}
        
        new_mrr = Decimal("0")
        expansion_mrr = Decimal("0")
        contraction_mrr = Decimal("0")
        churn_mrr = Decimal("0")
        reactivation_mrr = Decimal("0")
        
        # New and expansion
        for sub_id, sub in current_map.items():
            if sub.get("status") not in ("active", "trialing"):
                continue
            
            current_amount = Decimal(str(sub.get("amount", 0)))
            
            if sub_id not in previous_map:
                # Check if reactivation
                if sub.get("previous_status") == "canceled":
                    reactivation_mrr += current_amount
                else:
                    new_mrr += current_amount
            else:
                prev = previous_map[sub_id]
                prev_amount = Decimal(str(prev.get("amount", 0)))
                
                if current_amount > prev_amount:
                    expansion_mrr += current_amount - prev_amount
                elif current_amount < prev_amount:
                    contraction_mrr += prev_amount - current_amount
        
        # Churn
        for sub_id, sub in previous_map.items():
            if sub_id not in current_map or current_map[sub_id].get("status") == "canceled":
                if sub.get("status") in ("active", "trialing"):
                    churn_mrr += Decimal(str(sub.get("amount", 0)))
        
        return {
            "new_mrr": new_mrr.quantize(Decimal("0.01")),
            "expansion_mrr": expansion_mrr.quantize(Decimal("0.01")),
            "contraction_mrr": contraction_mrr.quantize(Decimal("0.01")),
            "churn_mrr": churn_mrr.quantize(Decimal("0.01")),
            "reactivation_mrr": reactivation_mrr.quantize(Decimal("0.01")),
        }
    
    def calculate_ltv(
        self,
        arpu: Decimal,
        churn_rate: float,
        gross_margin: float = 0.80,
    ) -> Decimal:
        """
        Calculate Customer Lifetime Value.
        
        LTV = (ARPU × Gross Margin) / Churn Rate
        """
        if churn_rate <= 0:
            churn_rate = 0.01  # Minimum 1% to avoid division by zero
        
        ltv = (arpu * Decimal(str(gross_margin))) / Decimal(str(churn_rate / 100))
        return ltv.quantize(Decimal("0.01"))
    
    def calculate_cohort_ltv(
        self,
        cohort_revenue: List[Decimal],
        cohort_size: int,
    ) -> Decimal:
        """Calculate actual LTV from cohort data."""
        if cohort_size == 0:
            return Decimal("0")
        
        total = sum(cohort_revenue)
        return (total / cohort_size).quantize(Decimal("0.01"))


# =============================================================================
# Revenue Reporting Engine
# =============================================================================

class RevenueReportingEngine:
    """
    Generates comprehensive revenue reports.
    
    Features:
    - Multi-period reporting
    - Segment breakdowns
    - Trend analysis
    - LTV calculations
    """
    
    def __init__(
        self,
        calculator: Optional[RevenueCalculator] = None,
        currency: str = "USD",
    ):
        self.calculator = calculator or RevenueCalculator(currency)
        self.currency = currency
        
        # Data stores (would be backed by database in production)
        self._subscriptions: List[Dict[str, Any]] = []
        self._customers: List[Dict[str, Any]] = []
        self._historical_metrics: List[RevenueMetrics] = []
    
    def load_data(
        self,
        subscriptions: List[Dict[str, Any]],
        customers: List[Dict[str, Any]],
    ) -> None:
        """Load subscription and customer data."""
        self._subscriptions = subscriptions
        self._customers = customers
    
    def generate_revenue_report(
        self,
        period: ReportPeriod = ReportPeriod.MONTHLY,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> RevenueReport:
        """Generate comprehensive revenue report."""
        end_date = end_date or datetime.now(timezone.utc)
        start_date = start_date or self._get_period_start(end_date, period)
        
        # Calculate metrics
        mrr = self.calculator.calculate_mrr(self._subscriptions, end_date)
        arr = self.calculator.calculate_arr(mrr)
        
        # Revenue metrics
        revenue_metrics = RevenueMetrics(
            timestamp=end_date,
            mrr=mrr,
            arr=arr,
            gross_revenue=self._calculate_gross_revenue(start_date, end_date),
            net_revenue=self._calculate_net_revenue(start_date, end_date),
        )
        
        # Subscription metrics
        subscription_metrics = self._calculate_subscription_metrics(end_date)
        
        # Customer metrics
        customer_metrics = self._calculate_customer_metrics(end_date, mrr)
        
        # Tier breakdown
        tier_breakdown = self._calculate_tier_breakdown(mrr)
        
        return RevenueReport(
            report_id=uuid4().hex,
            generated_at=datetime.now(timezone.utc),
            period=period,
            start_date=start_date,
            end_date=end_date,
            revenue_metrics=revenue_metrics,
            subscription_metrics=subscription_metrics,
            customer_metrics=customer_metrics,
            tier_breakdown=tier_breakdown,
        )
    
    def generate_ltv_report(self) -> LTVReport:
        """Generate LTV analysis report."""
        paying_customers = [c for c in self._customers if c.get("status") == "paying"]
        
        if not paying_customers:
            return LTVReport(
                report_id=uuid4().hex,
                generated_at=datetime.now(timezone.utc),
                avg_ltv=Decimal("0"),
                median_ltv=Decimal("0"),
                total_ltv=Decimal("0"),
            )
        
        # Calculate LTVs
        ltvs = []
        for customer in paying_customers:
            customer_ltv = Decimal(str(customer.get("lifetime_value", 0)))
            ltvs.append(customer_ltv)
        
        ltvs.sort()
        total_ltv = sum(ltvs)
        avg_ltv = total_ltv / len(ltvs) if ltvs else Decimal("0")
        median_ltv = ltvs[len(ltvs) // 2] if ltvs else Decimal("0")
        
        # By tier
        ltv_by_tier: Dict[str, Decimal] = {}
        for customer in paying_customers:
            tier = customer.get("tier", "unknown")
            ltv = Decimal(str(customer.get("lifetime_value", 0)))
            ltv_by_tier[tier] = ltv_by_tier.get(tier, Decimal("0")) + ltv
        
        return LTVReport(
            report_id=uuid4().hex,
            generated_at=datetime.now(timezone.utc),
            avg_ltv=avg_ltv.quantize(Decimal("0.01")),
            median_ltv=median_ltv.quantize(Decimal("0.01")),
            total_ltv=total_ltv.quantize(Decimal("0.01")),
            ltv_by_tier=ltv_by_tier,
        )
    
    def generate_executive_summary(self) -> Dict[str, Any]:
        """Generate executive-level summary."""
        report = self.generate_revenue_report(ReportPeriod.MONTHLY)
        ltv_report = self.generate_ltv_report()
        
        return {
            "period": "monthly",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "headline_metrics": {
                "mrr": str(report.revenue_metrics.mrr),
                "arr": str(report.revenue_metrics.arr),
                "mrr_growth_rate": f"{report.revenue_metrics.growth_rate:.1f}%",
                "active_customers": report.customer_metrics.paying_customers,
                "arpu": str(report.customer_metrics.arpu),
                "avg_ltv": str(ltv_report.avg_ltv),
            },
            "health_indicators": {
                "churn_rate": f"{report.subscription_metrics.churn_rate:.2f}%",
                "net_subscription_growth": report.subscription_metrics.net_growth,
                "expansion_rate": self._calculate_expansion_rate(report),
            },
            "tier_distribution": [
                {
                    "tier": tb.tier,
                    "customers": tb.customer_count,
                    "mrr": str(tb.mrr),
                    "percentage": f"{tb.percentage_of_total:.1f}%",
                }
                for tb in report.tier_breakdown
            ],
        }
    
    # -------------------------------------------------------------------------
    # Private Helpers
    # -------------------------------------------------------------------------
    
    def _get_period_start(self, end_date: datetime, period: ReportPeriod) -> datetime:
        """Calculate period start date."""
        if period == ReportPeriod.DAILY:
            return end_date - timedelta(days=1)
        elif period == ReportPeriod.WEEKLY:
            return end_date - timedelta(weeks=1)
        elif period == ReportPeriod.MONTHLY:
            return end_date - timedelta(days=30)
        elif period == ReportPeriod.QUARTERLY:
            return end_date - timedelta(days=90)
        elif period == ReportPeriod.YEARLY:
            return end_date - timedelta(days=365)
        return end_date - timedelta(days=30)
    
    def _calculate_gross_revenue(self, start: datetime, end: datetime) -> Decimal:
        """Calculate gross revenue for period."""
        # Would aggregate from invoices/payments
        return self.calculator.calculate_mrr(self._subscriptions)
    
    def _calculate_net_revenue(self, start: datetime, end: datetime) -> Decimal:
        """Calculate net revenue (gross - refunds - discounts)."""
        gross = self._calculate_gross_revenue(start, end)
        # Would subtract refunds and discounts
        return gross * Decimal("0.95")  # Simplified
    
    def _calculate_subscription_metrics(self, as_of: datetime) -> SubscriptionMetrics:
        """Calculate subscription metrics."""
        active = sum(1 for s in self._subscriptions if s.get("status") == "active")
        trialing = sum(1 for s in self._subscriptions if s.get("status") == "trialing")
        cancelled = sum(1 for s in self._subscriptions if s.get("status") == "canceled")
        past_due = sum(1 for s in self._subscriptions if s.get("status") == "past_due")
        
        return SubscriptionMetrics(
            timestamp=as_of,
            total_subscriptions=len(self._subscriptions),
            active_subscriptions=active,
            trial_subscriptions=trialing,
            cancelled_subscriptions=cancelled,
            past_due_subscriptions=past_due,
        )
    
    def _calculate_customer_metrics(self, as_of: datetime, mrr: Decimal) -> CustomerMetrics:
        """Calculate customer metrics."""
        total = len(self._customers)
        paying = sum(1 for c in self._customers if c.get("status") == "paying")
        free = sum(1 for c in self._customers if c.get("status") == "free")
        enterprise = sum(1 for c in self._customers if c.get("tier") == "enterprise")
        
        arpu = mrr / total if total > 0 else Decimal("0")
        arppu = mrr / paying if paying > 0 else Decimal("0")
        
        return CustomerMetrics(
            timestamp=as_of,
            total_customers=total,
            paying_customers=paying,
            free_customers=free,
            enterprise_customers=enterprise,
            arpu=arpu.quantize(Decimal("0.01")),
            arppu=arppu.quantize(Decimal("0.01")),
        )
    
    def _calculate_tier_breakdown(self, total_mrr: Decimal) -> List[TierBreakdown]:
        """Calculate revenue breakdown by tier."""
        tier_data: Dict[str, Dict[str, Any]] = {}
        
        for sub in self._subscriptions:
            if sub.get("status") not in ("active", "trialing"):
                continue
            
            tier = sub.get("tier", "community")
            if tier not in tier_data:
                tier_data[tier] = {
                    "customer_ids": set(),
                    "subscription_count": 0,
                    "mrr": Decimal("0"),
                }
            
            tier_data[tier]["customer_ids"].add(sub.get("customer_id"))
            tier_data[tier]["subscription_count"] += 1
            tier_data[tier]["mrr"] += Decimal(str(sub.get("amount", 0)))
        
        breakdowns = []
        for tier, data in tier_data.items():
            customer_count = len(data["customer_ids"])
            mrr = data["mrr"]
            percentage = float(mrr / total_mrr * 100) if total_mrr > 0 else 0.0
            avg_rev = mrr / customer_count if customer_count > 0 else Decimal("0")
            
            breakdowns.append(TierBreakdown(
                tier=tier,
                customer_count=customer_count,
                subscription_count=data["subscription_count"],
                mrr=mrr.quantize(Decimal("0.01")),
                arr=(mrr * 12).quantize(Decimal("0.01")),
                percentage_of_total=percentage,
                avg_revenue_per_customer=avg_rev.quantize(Decimal("0.01")),
            ))
        
        return sorted(breakdowns, key=lambda x: x.mrr, reverse=True)
    
    def _calculate_expansion_rate(self, report: RevenueReport) -> str:
        """Calculate revenue expansion rate."""
        if report.revenue_metrics.mrr == 0:
            return "0.0%"
        rate = float(report.revenue_metrics.expansion_mrr / report.revenue_metrics.mrr * 100)
        return f"{rate:.1f}%"


# =============================================================================
# Factory Function
# =============================================================================

def create_revenue_reporting_engine(
    currency: str = "USD",
) -> RevenueReportingEngine:
    """Create configured RevenueReportingEngine."""
    calculator = RevenueCalculator(currency)
    return RevenueReportingEngine(calculator=calculator, currency=currency)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "ReportPeriod",
    "RevenueSegment",
    "MetricType",
    "ReportFormat",
    # Data Classes
    "RevenueMetrics",
    "SubscriptionMetrics",
    "CustomerMetrics",
    "TierBreakdown",
    "RevenueReport",
    "LTVReport",
    # Classes
    "RevenueCalculator",
    "RevenueReportingEngine",
    # Factory
    "create_revenue_reporting_engine",
]
