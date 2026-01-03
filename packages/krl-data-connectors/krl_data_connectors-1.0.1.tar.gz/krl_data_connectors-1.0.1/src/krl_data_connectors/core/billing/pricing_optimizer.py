# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
#
# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.pricing_optimizer
# This stub remains for backward compatibility but will be removed in v2.0.
# ----------------------------------------------------------------------

from __future__ import annotations

import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.pricing_optimizer is deprecated. "
    "Import from 'app.services.billing.pricing_optimizer' instead.",
    DeprecationWarning,
    stacklevel=2
)

"""
Pricing Optimizer - Phase 3 Week 22

A/B testing framework and elasticity modeling for pricing optimization:
- Experiment design and execution
- Price elasticity measurement
- Optimal price point discovery
- Revenue impact simulation
- Statistical significance testing

Integrates with:
- PricingIntentsEngine for strategic alignment
- CohortAnalytics for segmentation
- RevenueForecaster for projections
- BillingPolicyTree for governance

This module enables data-driven pricing decisions.
"""

import hashlib
import logging
import math
import random
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class ExperimentType(Enum):
    """Types of pricing experiments."""
    AB_TEST = "ab_test"                    # Simple A/B test
    MULTIVARIATE = "multivariate"          # Multiple variants
    HOLDOUT = "holdout"                    # Control holdout
    BANDIT = "bandit"                      # Multi-armed bandit
    SEQUENTIAL = "sequential"              # Sequential testing


class ExperimentStatus(Enum):
    """Status of a pricing experiment."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PriceMetric(Enum):
    """Metrics to optimize for."""
    REVENUE = "revenue"
    CONVERSION = "conversion"
    RETENTION = "retention"
    LTV = "ltv"
    ARPU = "arpu"
    MARGIN = "margin"


class ElasticityBand(Enum):
    """Price elasticity classifications."""
    HIGHLY_ELASTIC = "highly_elastic"      # |e| > 2.0
    ELASTIC = "elastic"                     # 1.0 < |e| <= 2.0
    UNIT_ELASTIC = "unit_elastic"          # |e| ≈ 1.0
    INELASTIC = "inelastic"                # 0.5 < |e| < 1.0
    HIGHLY_INELASTIC = "highly_inelastic"  # |e| <= 0.5


class VariantAllocation(Enum):
    """How to allocate traffic to variants."""
    RANDOM = "random"
    HASH_BASED = "hash_based"
    STRATIFIED = "stratified"
    SEQUENTIAL = "sequential"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class PriceVariant:
    """A pricing variant in an experiment."""
    variant_id: str
    name: str
    
    # Pricing details
    base_price: Decimal
    unit_price: Optional[Decimal] = None
    discount_pct: Decimal = Decimal("0")
    
    # Traffic allocation
    allocation_weight: float = 0.5
    
    # Results
    impressions: int = 0
    conversions: int = 0
    revenue: Decimal = Decimal("0")
    churns: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def conversion_rate(self) -> float:
        """Calculate conversion rate."""
        if self.impressions == 0:
            return 0.0
        return self.conversions / self.impressions

    @property
    def arpu(self) -> Decimal:
        """Average revenue per user."""
        if self.conversions == 0:
            return Decimal("0")
        return self.revenue / self.conversions

    @property
    def effective_price(self) -> Decimal:
        """Price after discount."""
        return self.base_price * (1 - self.discount_pct / 100)


@dataclass
class ExperimentConfig:
    """Configuration for a pricing experiment."""
    experiment_id: str
    name: str
    description: str
    
    # Experiment parameters
    experiment_type: ExperimentType = ExperimentType.AB_TEST
    target_metric: PriceMetric = PriceMetric.REVENUE
    allocation_method: VariantAllocation = VariantAllocation.HASH_BASED
    
    # Targeting
    target_tiers: List[str] = field(default_factory=lambda: ["pro"])
    target_cohorts: List[str] = field(default_factory=list)
    exclude_tenants: Set[str] = field(default_factory=set)
    
    # Statistical parameters
    min_sample_size: int = 100
    confidence_level: float = 0.95
    min_effect_size: float = 0.05
    
    # Duration
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_duration_days: int = 30
    
    # Safety
    max_revenue_impact_pct: float = 10.0
    auto_stop_on_negative: bool = True
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ExperimentResult:
    """Results of a pricing experiment."""
    experiment_id: str
    variant_id: str
    
    # Sample sizes
    sample_size: int
    control_size: int
    
    # Metric results
    metric_value: float
    control_value: float
    lift: float
    lift_pct: float
    
    # Statistical significance
    p_value: float
    confidence_interval: Tuple[float, float]
    is_significant: bool
    
    # Revenue impact
    revenue_impact: Decimal
    projected_annual_impact: Decimal
    
    # Recommendation
    recommendation: str
    confidence: float
    
    # Timestamps
    calculated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ElasticityResult:
    """Price elasticity analysis result."""
    product_id: str
    tier: str
    
    # Elasticity
    elasticity: float
    band: ElasticityBand
    
    # Optimal price
    optimal_price: Decimal
    current_price: Decimal
    price_change_pct: float
    
    # Revenue projection
    current_revenue: Decimal
    projected_revenue: Decimal
    revenue_change_pct: float
    
    # Confidence
    r_squared: float
    sample_size: int
    confidence: float
    
    # Timestamps
    calculated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class PricePoint:
    """A price point observation."""
    price: Decimal
    quantity_sold: int
    revenue: Decimal
    time_period: str
    tier: str
    tenant_count: int = 0


@dataclass
class SimulationResult:
    """Result of a pricing simulation."""
    scenario_name: str
    
    # Price changes
    current_price: Decimal
    new_price: Decimal
    change_pct: float
    
    # Volume impact
    current_volume: int
    projected_volume: int
    volume_change_pct: float
    
    # Revenue impact
    current_revenue: Decimal
    projected_revenue: Decimal
    revenue_change_pct: float
    
    # Risk assessment
    churn_risk: float
    competitor_risk: float
    overall_risk: float
    
    # Confidence
    confidence_level: float
    simulation_runs: int


# =============================================================================
# Pricing Experiment
# =============================================================================

class PricingExperiment:
    """
    Manages a single pricing experiment.
    
    Handles:
    - Variant assignment
    - Result tracking
    - Statistical analysis
    - Experiment lifecycle
    """

    def __init__(self, config: ExperimentConfig, variants: List[PriceVariant]):
        self.config = config
        self.variants = {v.variant_id: v for v in variants}
        self.status = ExperimentStatus.DRAFT
        self.control_variant_id: Optional[str] = None
        
        # Assignment tracking
        self._assignments: Dict[str, str] = {}  # tenant_id -> variant_id
        
        # Set control variant (first by default)
        if variants:
            self.control_variant_id = variants[0].variant_id

    def start(self) -> None:
        """Start the experiment."""
        if self.status != ExperimentStatus.DRAFT:
            logger.warning(f"Experiment {self.config.experiment_id} not in draft status")
            return
        
        self.status = ExperimentStatus.ACTIVE
        if self.config.start_date is None:
            self.config.start_date = datetime.now(UTC)
        
        logger.info(f"Started experiment {self.config.experiment_id}")

    def pause(self) -> None:
        """Pause the experiment."""
        if self.status != ExperimentStatus.ACTIVE:
            return
        self.status = ExperimentStatus.PAUSED
        logger.info(f"Paused experiment {self.config.experiment_id}")

    def resume(self) -> None:
        """Resume a paused experiment."""
        if self.status != ExperimentStatus.PAUSED:
            return
        self.status = ExperimentStatus.ACTIVE
        logger.info(f"Resumed experiment {self.config.experiment_id}")

    def complete(self) -> None:
        """Complete the experiment."""
        if self.status not in (ExperimentStatus.ACTIVE, ExperimentStatus.PAUSED):
            return
        self.status = ExperimentStatus.COMPLETED
        if self.config.end_date is None:
            self.config.end_date = datetime.now(UTC)
        logger.info(f"Completed experiment {self.config.experiment_id}")

    def cancel(self) -> None:
        """Cancel the experiment."""
        self.status = ExperimentStatus.CANCELLED
        logger.info(f"Cancelled experiment {self.config.experiment_id}")

    def assign_variant(self, tenant_id: str, tier: str) -> Optional[PriceVariant]:
        """
        Assign a tenant to an experiment variant.
        
        Uses consistent hashing for deterministic assignment.
        """
        if self.status != ExperimentStatus.ACTIVE:
            return None
        
        # Check eligibility
        if tier not in self.config.target_tiers:
            return None
        if tenant_id in self.config.exclude_tenants:
            return None
        
        # Return existing assignment
        if tenant_id in self._assignments:
            return self.variants.get(self._assignments[tenant_id])
        
        # Determine assignment based on allocation method
        variant_id = self._allocate_variant(tenant_id)
        
        if variant_id:
            self._assignments[tenant_id] = variant_id
            variant = self.variants[variant_id]
            variant.impressions += 1
            return variant
        
        return None

    def _allocate_variant(self, tenant_id: str) -> Optional[str]:
        """Allocate tenant to variant based on method."""
        if self.config.allocation_method == VariantAllocation.HASH_BASED:
            return self._hash_allocate(tenant_id)
        elif self.config.allocation_method == VariantAllocation.RANDOM:
            return self._random_allocate()
        elif self.config.allocation_method == VariantAllocation.STRATIFIED:
            return self._stratified_allocate(tenant_id)
        else:
            return self._random_allocate()

    def _hash_allocate(self, tenant_id: str) -> str:
        """Deterministic hash-based allocation."""
        hash_input = f"{self.config.experiment_id}:{tenant_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        bucket = (hash_value % 1000) / 1000.0
        
        cumulative = 0.0
        for variant_id, variant in self.variants.items():
            cumulative += variant.allocation_weight
            if bucket < cumulative:
                return variant_id
        
        return list(self.variants.keys())[-1]

    def _random_allocate(self) -> str:
        """Random allocation based on weights."""
        weights = [v.allocation_weight for v in self.variants.values()]
        variant_ids = list(self.variants.keys())
        return random.choices(variant_ids, weights=weights)[0]

    def _stratified_allocate(self, tenant_id: str) -> str:
        """Stratified allocation for balanced groups."""
        # Simple round-robin for stratified
        variant_ids = list(self.variants.keys())
        assignment_count = len(self._assignments)
        return variant_ids[assignment_count % len(variant_ids)]

    def record_conversion(self, tenant_id: str, revenue: Decimal) -> None:
        """Record a conversion event."""
        if tenant_id not in self._assignments:
            return
        
        variant_id = self._assignments[tenant_id]
        variant = self.variants[variant_id]
        variant.conversions += 1
        variant.revenue += revenue

    def record_churn(self, tenant_id: str) -> None:
        """Record a churn event."""
        if tenant_id not in self._assignments:
            return
        
        variant_id = self._assignments[tenant_id]
        self.variants[variant_id].churns += 1

    def get_results(self) -> List[ExperimentResult]:
        """Calculate experiment results for all variants."""
        if not self.control_variant_id:
            return []
        
        control = self.variants[self.control_variant_id]
        results = []
        
        for variant_id, variant in self.variants.items():
            if variant_id == self.control_variant_id:
                continue
            
            result = self._calculate_variant_result(variant, control)
            if result:
                results.append(result)
        
        return results

    def _calculate_variant_result(
        self, 
        variant: PriceVariant, 
        control: PriceVariant
    ) -> Optional[ExperimentResult]:
        """Calculate result for a single variant vs control."""
        if variant.impressions < self.config.min_sample_size:
            return None
        if control.impressions < self.config.min_sample_size:
            return None
        
        # Get metric values based on target
        if self.config.target_metric == PriceMetric.CONVERSION:
            metric_value = variant.conversion_rate
            control_value = control.conversion_rate
        elif self.config.target_metric == PriceMetric.REVENUE:
            metric_value = float(variant.revenue)
            control_value = float(control.revenue)
        elif self.config.target_metric == PriceMetric.ARPU:
            metric_value = float(variant.arpu)
            control_value = float(control.arpu)
        else:
            metric_value = variant.conversion_rate
            control_value = control.conversion_rate
        
        # Calculate lift
        if control_value == 0:
            lift = metric_value
            lift_pct = 100.0 if metric_value > 0 else 0.0
        else:
            lift = metric_value - control_value
            lift_pct = (lift / control_value) * 100
        
        # Statistical significance (simplified z-test for proportions)
        p_value, confidence_interval = self._calculate_significance(
            variant, control
        )
        is_significant = p_value < (1 - self.config.confidence_level)
        
        # Revenue impact
        revenue_impact = variant.revenue - control.revenue
        # Annualize based on experiment duration
        days_running = (datetime.now(UTC) - (self.config.start_date or datetime.now(UTC))).days or 1
        projected_annual = (revenue_impact / days_running) * 365
        
        # Recommendation
        if not is_significant:
            recommendation = "Insufficient data for conclusion"
            confidence = 0.5
        elif lift > 0:
            recommendation = f"Adopt variant {variant.name}"
            confidence = 1 - p_value
        else:
            recommendation = f"Keep control, variant {variant.name} underperforms"
            confidence = 1 - p_value
        
        return ExperimentResult(
            experiment_id=self.config.experiment_id,
            variant_id=variant.variant_id,
            sample_size=variant.impressions,
            control_size=control.impressions,
            metric_value=metric_value,
            control_value=control_value,
            lift=lift,
            lift_pct=lift_pct,
            p_value=p_value,
            confidence_interval=confidence_interval,
            is_significant=is_significant,
            revenue_impact=revenue_impact,
            projected_annual_impact=projected_annual,
            recommendation=recommendation,
            confidence=confidence,
        )

    def _calculate_significance(
        self, 
        variant: PriceVariant, 
        control: PriceVariant
    ) -> Tuple[float, Tuple[float, float]]:
        """
        Calculate statistical significance using z-test.
        
        Returns (p_value, confidence_interval).
        """
        n1 = variant.impressions
        n2 = control.impressions
        p1 = variant.conversion_rate
        p2 = control.conversion_rate
        
        if n1 == 0 or n2 == 0:
            return 1.0, (0.0, 0.0)
        
        # Pooled proportion
        p_pool = (variant.conversions + control.conversions) / (n1 + n2)
        
        if p_pool == 0 or p_pool == 1:
            return 1.0, (p1 - 0.1, p1 + 0.1)
        
        # Standard error
        se = math.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))
        
        if se == 0:
            return 1.0, (p1 - 0.1, p1 + 0.1)
        
        # Z-score
        z = (p1 - p2) / se
        
        # P-value (two-tailed)
        p_value = 2 * (1 - self._norm_cdf(abs(z)))
        
        # Confidence interval for difference
        z_alpha = 1.96  # 95% confidence
        margin = z_alpha * se
        ci = (p1 - p2 - margin, p1 - p2 + margin)
        
        return p_value, ci

    @staticmethod
    def _norm_cdf(x: float) -> float:
        """Approximate normal CDF."""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def should_stop_early(self) -> Tuple[bool, str]:
        """Check if experiment should stop early."""
        # Check duration
        if self.config.start_date:
            days_running = (datetime.now(UTC) - self.config.start_date).days
            if days_running >= self.config.max_duration_days:
                return True, "Max duration reached"
        
        # Check for significant negative impact
        if self.config.auto_stop_on_negative:
            results = self.get_results()
            for result in results:
                if result.is_significant and result.lift_pct < -self.config.max_revenue_impact_pct:
                    return True, f"Significant negative impact detected: {result.lift_pct:.1f}%"
        
        return False, ""


# =============================================================================
# Elasticity Analyzer
# =============================================================================

class ElasticityAnalyzer:
    """
    Analyzes price elasticity of demand.
    
    Uses historical price points to calculate elasticity
    and determine optimal pricing.
    """

    def __init__(self):
        self._price_history: Dict[str, List[PricePoint]] = {}

    def add_price_point(self, product_id: str, point: PricePoint) -> None:
        """Add a price observation."""
        if product_id not in self._price_history:
            self._price_history[product_id] = []
        self._price_history[product_id].append(point)

    def add_price_points(self, product_id: str, points: List[PricePoint]) -> None:
        """Add multiple price observations."""
        for point in points:
            self.add_price_point(product_id, point)

    def calculate_elasticity(
        self, 
        product_id: str,
        tier: Optional[str] = None
    ) -> Optional[ElasticityResult]:
        """
        Calculate price elasticity for a product.
        
        Elasticity = (% change in quantity) / (% change in price)
        
        e < 1: Inelastic (price increase → revenue increase)
        e > 1: Elastic (price increase → revenue decrease)
        e = 1: Unit elastic (revenue unchanged)
        """
        if product_id not in self._price_history:
            return None
        
        points = self._price_history[product_id]
        
        # Filter by tier if specified
        if tier:
            points = [p for p in points if p.tier == tier]
        
        if len(points) < 3:
            logger.warning(f"Insufficient data for elasticity calculation: {len(points)} points")
            return None
        
        # Calculate elasticity using log-log regression
        elasticity, r_squared = self._calculate_log_elasticity(points)
        
        # Classify elasticity
        band = self._classify_elasticity(elasticity)
        
        # Find optimal price
        current_price = points[-1].price
        optimal_price = self._find_optimal_price(points, elasticity)
        
        # Calculate revenue projections
        current_revenue = sum(p.revenue for p in points[-3:]) / 3  # Average of last 3
        projected_revenue = self._project_revenue(
            current_price, optimal_price, current_revenue, elasticity
        )
        
        price_change = float((optimal_price - current_price) / current_price * 100)
        revenue_change = float((projected_revenue - current_revenue) / current_revenue * 100)
        
        return ElasticityResult(
            product_id=product_id,
            tier=tier or "all",
            elasticity=elasticity,
            band=band,
            optimal_price=optimal_price,
            current_price=current_price,
            price_change_pct=price_change,
            current_revenue=current_revenue,
            projected_revenue=projected_revenue,
            revenue_change_pct=revenue_change,
            r_squared=r_squared,
            sample_size=len(points),
            confidence=min(r_squared, 0.95),
        )

    def _calculate_log_elasticity(
        self, 
        points: List[PricePoint]
    ) -> Tuple[float, float]:
        """
        Calculate elasticity using log-log regression.
        
        ln(Q) = a + e * ln(P) + error
        
        Returns (elasticity, r_squared).
        """
        if len(points) < 2:
            return -1.0, 0.0
        
        # Prepare data
        log_prices = []
        log_quantities = []
        
        for p in points:
            if p.price > 0 and p.quantity_sold > 0:
                log_prices.append(math.log(float(p.price)))
                log_quantities.append(math.log(float(p.quantity_sold)))
        
        if len(log_prices) < 2:
            return -1.0, 0.0
        
        # Simple linear regression
        n = len(log_prices)
        sum_x = sum(log_prices)
        sum_y = sum(log_quantities)
        sum_xy = sum(x * y for x, y in zip(log_prices, log_quantities))
        sum_x2 = sum(x * x for x in log_prices)
        
        denominator = n * sum_x2 - sum_x ** 2
        if denominator == 0:
            return -1.0, 0.0
        
        # Slope (elasticity)
        elasticity = (n * sum_xy - sum_x * sum_y) / denominator
        
        # R-squared
        mean_y = sum_y / n
        ss_tot = sum((y - mean_y) ** 2 for y in log_quantities)
        
        # Calculate predicted values
        intercept = (sum_y - elasticity * sum_x) / n
        predicted = [intercept + elasticity * x for x in log_prices]
        ss_res = sum((y - p) ** 2 for y, p in zip(log_quantities, predicted))
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        r_squared = max(0, min(1, r_squared))  # Clamp to [0, 1]
        
        return elasticity, r_squared

    def _classify_elasticity(self, elasticity: float) -> ElasticityBand:
        """Classify elasticity into bands."""
        abs_e = abs(elasticity)
        
        if abs_e > 2.0:
            return ElasticityBand.HIGHLY_ELASTIC
        elif abs_e > 1.0:
            return ElasticityBand.ELASTIC
        elif abs_e > 0.9:
            return ElasticityBand.UNIT_ELASTIC
        elif abs_e > 0.5:
            return ElasticityBand.INELASTIC
        else:
            return ElasticityBand.HIGHLY_INELASTIC

    def _find_optimal_price(
        self, 
        points: List[PricePoint], 
        elasticity: float
    ) -> Decimal:
        """
        Find optimal price to maximize revenue.
        
        For constant elasticity: optimal when MR = MC
        Simplified: P* = MC / (1 + 1/e)
        
        Assumes marginal cost is ~20% of current price.
        """
        current_price = points[-1].price
        
        # Assume marginal cost is 20% of price
        marginal_cost = current_price * Decimal("0.2")
        
        if elasticity >= -1:
            # Inelastic: can raise price
            # But cap at 2x current
            return min(current_price * Decimal("2.0"), current_price * Decimal("1.1"))
        else:
            # Elastic: use markup formula
            markup = Decimal(str(1 / (1 + 1/elasticity)))
            optimal = marginal_cost / markup if markup > 0 else current_price
            
            # Sanity bounds: 50% to 200% of current
            min_price = current_price * Decimal("0.5")
            max_price = current_price * Decimal("2.0")
            
            return max(min_price, min(max_price, optimal))

    def _project_revenue(
        self, 
        current_price: Decimal,
        new_price: Decimal,
        current_revenue: Decimal,
        elasticity: float
    ) -> Decimal:
        """Project revenue at new price point."""
        if current_price == 0:
            return current_revenue
        
        price_change_pct = float((new_price - current_price) / current_price)
        quantity_change_pct = elasticity * price_change_pct
        
        # New revenue = new_price * new_quantity
        # = current_price * (1 + price_change) * current_quantity * (1 + quantity_change)
        # Approximation: current_revenue * (1 + price_change) * (1 + quantity_change)
        
        new_revenue = current_revenue * Decimal(str(
            (1 + price_change_pct) * (1 + quantity_change_pct)
        ))
        
        return max(Decimal("0"), new_revenue)


# =============================================================================
# Pricing Simulator
# =============================================================================

class PricingSimulator:
    """
    Simulates pricing changes and their impact.
    
    Provides "what-if" analysis for pricing decisions.
    """

    def __init__(self, elasticity_analyzer: Optional[ElasticityAnalyzer] = None):
        self.elasticity = elasticity_analyzer or ElasticityAnalyzer()
        self._competitor_prices: Dict[str, Decimal] = {}
        self._churn_sensitivity: float = 0.5  # How sensitive customers are to price increases

    def set_competitor_price(self, product_id: str, price: Decimal) -> None:
        """Set competitor price for comparison."""
        self._competitor_prices[product_id] = price

    def set_churn_sensitivity(self, sensitivity: float) -> None:
        """Set customer churn sensitivity (0-1)."""
        self._churn_sensitivity = max(0, min(1, sensitivity))

    def simulate_price_change(
        self,
        product_id: str,
        current_price: Decimal,
        new_price: Decimal,
        current_volume: int,
        current_revenue: Decimal,
        tier: str = "pro",
        runs: int = 1000
    ) -> SimulationResult:
        """
        Simulate the impact of a price change.
        
        Uses Monte Carlo simulation with elasticity estimates.
        """
        change_pct = float((new_price - current_price) / current_price * 100)
        
        # Get elasticity estimate
        elasticity_result = self.elasticity.calculate_elasticity(product_id, tier)
        base_elasticity = elasticity_result.elasticity if elasticity_result else -1.0
        
        # Monte Carlo simulation
        volume_results = []
        revenue_results = []
        
        for _ in range(runs):
            # Add noise to elasticity
            noise = random.gauss(0, 0.2)
            e = base_elasticity * (1 + noise)
            
            # Calculate volume change
            volume_change_pct = e * (change_pct / 100)
            new_volume = int(current_volume * (1 + volume_change_pct))
            new_volume = max(0, new_volume)
            
            # Calculate revenue
            revenue = new_price * new_volume
            
            volume_results.append(new_volume)
            revenue_results.append(float(revenue))
        
        # Average results
        projected_volume = int(statistics.mean(volume_results))
        projected_revenue = Decimal(str(statistics.mean(revenue_results)))
        
        volume_change = (projected_volume - current_volume) / current_volume * 100 if current_volume > 0 else 0
        revenue_change = float((projected_revenue - current_revenue) / current_revenue * 100) if current_revenue > 0 else 0
        
        # Risk assessment
        churn_risk = self._calculate_churn_risk(change_pct)
        competitor_risk = self._calculate_competitor_risk(product_id, new_price)
        overall_risk = (churn_risk + competitor_risk) / 2
        
        # Confidence based on simulation variance
        revenue_std = statistics.stdev(revenue_results) if len(revenue_results) > 1 else 0
        confidence = 1 - min(revenue_std / max(float(current_revenue), 1), 0.5)
        
        return SimulationResult(
            scenario_name=f"{product_id} price change",
            current_price=current_price,
            new_price=new_price,
            change_pct=change_pct,
            current_volume=current_volume,
            projected_volume=projected_volume,
            volume_change_pct=volume_change,
            current_revenue=current_revenue,
            projected_revenue=projected_revenue,
            revenue_change_pct=revenue_change,
            churn_risk=churn_risk,
            competitor_risk=competitor_risk,
            overall_risk=overall_risk,
            confidence_level=confidence,
            simulation_runs=runs,
        )

    def _calculate_churn_risk(self, price_change_pct: float) -> float:
        """Calculate churn risk based on price change."""
        if price_change_pct <= 0:
            return 0.0  # Price decrease, no churn risk
        
        # Risk increases with price increase
        # Base: 10% increase → 5% churn risk at mid sensitivity
        base_risk = (price_change_pct / 100) * 0.5
        risk = base_risk * self._churn_sensitivity
        
        return min(1.0, risk)

    def _calculate_competitor_risk(
        self, 
        product_id: str, 
        new_price: Decimal
    ) -> float:
        """Calculate competitive risk based on pricing."""
        if product_id not in self._competitor_prices:
            return 0.3  # Unknown competitor, moderate risk
        
        competitor_price = self._competitor_prices[product_id]
        
        if competitor_price == 0:
            return 0.3
        
        price_ratio = float(new_price / competitor_price)
        
        if price_ratio <= 0.8:
            return 0.1  # Well below competitor
        elif price_ratio <= 1.0:
            return 0.2  # At or below competitor
        elif price_ratio <= 1.2:
            return 0.4  # Slightly above
        elif price_ratio <= 1.5:
            return 0.6  # Noticeably above
        else:
            return 0.8  # Significantly above

    def run_scenarios(
        self,
        product_id: str,
        current_price: Decimal,
        current_volume: int,
        current_revenue: Decimal,
        scenarios: List[float],  # List of price change percentages
        tier: str = "pro"
    ) -> List[SimulationResult]:
        """Run multiple pricing scenarios."""
        results = []
        
        for change_pct in scenarios:
            new_price = current_price * Decimal(str(1 + change_pct / 100))
            result = self.simulate_price_change(
                product_id=product_id,
                current_price=current_price,
                new_price=new_price,
                current_volume=current_volume,
                current_revenue=current_revenue,
                tier=tier,
            )
            result.scenario_name = f"{change_pct:+.0f}% price change"
            results.append(result)
        
        return results


# =============================================================================
# Pricing Optimizer (Main Orchestrator)
# =============================================================================

class PricingOptimizer:
    """
    Main orchestrator for pricing optimization.
    
    Integrates experiments, elasticity analysis, and simulation
    to provide data-driven pricing recommendations.
    """

    def __init__(self):
        self.experiments: Dict[str, PricingExperiment] = {}
        self.elasticity_analyzer = ElasticityAnalyzer()
        self.simulator = PricingSimulator(self.elasticity_analyzer)
        
        # Integration hooks
        self._pricing_intents_hook: Optional[Callable[[], Any]] = None
        self._cohort_hook: Optional[Callable[[str], Any]] = None
        self._forecaster_hook: Optional[Callable[[], Any]] = None

    # -------------------------------------------------------------------------
    # Integration Hooks
    # -------------------------------------------------------------------------

    def connect_pricing_intents(self, hook: Callable[[], Any]) -> None:
        """Connect to PricingIntentsEngine for strategic alignment."""
        self._pricing_intents_hook = hook
        logger.info("Connected to PricingIntentsEngine")

    def connect_cohort_analytics(self, hook: Callable[[str], Any]) -> None:
        """Connect to CohortAnalytics for segmentation."""
        self._cohort_hook = hook
        logger.info("Connected to CohortAnalytics")

    def connect_forecaster(self, hook: Callable[[], Any]) -> None:
        """Connect to RevenueForecaster for projections."""
        self._forecaster_hook = hook
        logger.info("Connected to RevenueForecaster")

    # -------------------------------------------------------------------------
    # Experiment Management
    # -------------------------------------------------------------------------

    def create_experiment(
        self,
        name: str,
        description: str,
        control_price: Decimal,
        test_prices: List[Decimal],
        target_tiers: List[str] = None,
        **config_kwargs
    ) -> PricingExperiment:
        """Create a new pricing experiment."""
        experiment_id = f"exp_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{name[:10]}"
        
        config = ExperimentConfig(
            experiment_id=experiment_id,
            name=name,
            description=description,
            target_tiers=target_tiers or ["pro"],
            **config_kwargs
        )
        
        # Create variants
        variants = [
            PriceVariant(
                variant_id="control",
                name="Control",
                base_price=control_price,
                allocation_weight=0.5,
            )
        ]
        
        weight_per_test = 0.5 / len(test_prices) if test_prices else 0.5
        for i, price in enumerate(test_prices):
            variants.append(PriceVariant(
                variant_id=f"test_{i+1}",
                name=f"Test {i+1} (${price})",
                base_price=price,
                allocation_weight=weight_per_test,
            ))
        
        experiment = PricingExperiment(config, variants)
        self.experiments[experiment_id] = experiment
        
        logger.info(f"Created experiment {experiment_id} with {len(variants)} variants")
        return experiment

    def get_experiment(self, experiment_id: str) -> Optional[PricingExperiment]:
        """Get experiment by ID."""
        return self.experiments.get(experiment_id)

    def list_experiments(
        self, 
        status: Optional[ExperimentStatus] = None
    ) -> List[PricingExperiment]:
        """List experiments, optionally filtered by status."""
        experiments = list(self.experiments.values())
        
        if status:
            experiments = [e for e in experiments if e.status == status]
        
        return experiments

    # -------------------------------------------------------------------------
    # Price Assignment
    # -------------------------------------------------------------------------

    def get_price_for_tenant(
        self, 
        tenant_id: str, 
        tier: str, 
        product_id: str,
        base_price: Decimal
    ) -> Tuple[Decimal, Optional[str]]:
        """
        Get the price for a tenant, considering active experiments.
        
        Returns (price, experiment_id or None).
        """
        # Check active experiments
        for exp_id, experiment in self.experiments.items():
            if experiment.status != ExperimentStatus.ACTIVE:
                continue
            
            variant = experiment.assign_variant(tenant_id, tier)
            if variant:
                return variant.effective_price, exp_id
        
        return base_price, None

    # -------------------------------------------------------------------------
    # Recommendations
    # -------------------------------------------------------------------------

    def get_pricing_recommendation(
        self,
        product_id: str,
        tier: str,
        current_price: Decimal,
        current_volume: int,
        current_revenue: Decimal
    ) -> Dict[str, Any]:
        """
        Get comprehensive pricing recommendation.
        
        Combines elasticity analysis, simulation, and strategic alignment.
        """
        recommendation = {
            "product_id": product_id,
            "tier": tier,
            "current_price": float(current_price),
            "current_revenue": float(current_revenue),
            "analysis_timestamp": datetime.now(UTC).isoformat(),
            "elasticity": None,
            "simulations": [],
            "strategic_alignment": None,
            "recommended_action": "maintain",
            "recommended_price": float(current_price),
            "confidence": 0.5,
        }
        
        # Elasticity analysis
        elasticity = self.elasticity_analyzer.calculate_elasticity(product_id, tier)
        if elasticity:
            recommendation["elasticity"] = {
                "value": elasticity.elasticity,
                "band": elasticity.band.value,
                "optimal_price": float(elasticity.optimal_price),
                "r_squared": elasticity.r_squared,
            }
        
        # Simulation scenarios
        scenarios = [-20, -10, 0, 10, 20, 30]
        sim_results = self.simulator.run_scenarios(
            product_id=product_id,
            current_price=current_price,
            current_volume=current_volume,
            current_revenue=current_revenue,
            scenarios=scenarios,
            tier=tier,
        )
        
        recommendation["simulations"] = [
            {
                "scenario": r.scenario_name,
                "new_price": float(r.new_price),
                "projected_revenue": float(r.projected_revenue),
                "revenue_change_pct": r.revenue_change_pct,
                "churn_risk": r.churn_risk,
                "overall_risk": r.overall_risk,
            }
            for r in sim_results
        ]
        
        # Strategic alignment (if connected)
        if self._pricing_intents_hook:
            try:
                intent = self._pricing_intents_hook()
                if intent:
                    recommendation["strategic_alignment"] = {
                        "intent": str(intent),
                    }
            except Exception as e:
                logger.warning(f"Failed to get pricing intent: {e}")
        
        # Determine recommendation
        best_scenario = self._select_best_scenario(sim_results, elasticity)
        if best_scenario:
            if best_scenario.change_pct > 5:
                recommendation["recommended_action"] = "increase"
            elif best_scenario.change_pct < -5:
                recommendation["recommended_action"] = "decrease"
            else:
                recommendation["recommended_action"] = "maintain"
            
            recommendation["recommended_price"] = float(best_scenario.new_price)
            recommendation["confidence"] = best_scenario.confidence_level
        
        return recommendation

    def _select_best_scenario(
        self,
        simulations: List[SimulationResult],
        elasticity: Optional[ElasticityResult]
    ) -> Optional[SimulationResult]:
        """Select the best pricing scenario."""
        if not simulations:
            return None
        
        # Score each scenario
        scored = []
        for sim in simulations:
            # Revenue improvement score
            revenue_score = sim.revenue_change_pct / 100
            
            # Risk penalty
            risk_penalty = sim.overall_risk * 0.5
            
            # Confidence boost
            confidence_bonus = sim.confidence_level * 0.2
            
            # Total score
            score = revenue_score - risk_penalty + confidence_bonus
            scored.append((score, sim))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        
        return scored[0][1] if scored else None

    # -------------------------------------------------------------------------
    # Bulk Analysis
    # -------------------------------------------------------------------------

    def analyze_tier_pricing(
        self,
        tier: str,
        products: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze pricing for an entire tier.
        
        products: List of dicts with product_id, price, volume, revenue
        """
        analysis = {
            "tier": tier,
            "timestamp": datetime.now(UTC).isoformat(),
            "products": [],
            "summary": {
                "total_revenue": Decimal("0"),
                "optimization_potential": Decimal("0"),
                "avg_elasticity": 0.0,
                "recommendations_count": {"increase": 0, "decrease": 0, "maintain": 0},
            },
        }
        
        elasticities = []
        
        for product in products:
            rec = self.get_pricing_recommendation(
                product_id=product["product_id"],
                tier=tier,
                current_price=Decimal(str(product["price"])),
                current_volume=product["volume"],
                current_revenue=Decimal(str(product["revenue"])),
            )
            analysis["products"].append(rec)
            
            # Update summary
            analysis["summary"]["total_revenue"] += Decimal(str(product["revenue"]))
            
            if rec["elasticity"]:
                elasticities.append(rec["elasticity"]["value"])
            
            action = rec["recommended_action"]
            analysis["summary"]["recommendations_count"][action] = \
                analysis["summary"]["recommendations_count"].get(action, 0) + 1
            
            # Calculate optimization potential
            if rec["simulations"]:
                best_sim = max(rec["simulations"], key=lambda x: x["projected_revenue"])
                potential = best_sim["projected_revenue"] - float(product["revenue"])
                if potential > 0:
                    analysis["summary"]["optimization_potential"] += Decimal(str(potential))
        
        if elasticities:
            analysis["summary"]["avg_elasticity"] = statistics.mean(elasticities)
        
        return analysis


# =============================================================================
# Default Configuration
# =============================================================================

DEFAULT_OPTIMIZER_CONFIG = {
    "experiment_defaults": {
        "min_sample_size": 100,
        "confidence_level": 0.95,
        "max_duration_days": 30,
        "auto_stop_on_negative": True,
    },
    "elasticity_defaults": {
        "min_data_points": 5,
        "lookback_months": 6,
    },
    "simulation_defaults": {
        "runs": 1000,
        "churn_sensitivity": 0.5,
    },
    "tier_specific": {
        "community": {
            "experiment_allowed": False,
            "price_change_cap_pct": 0,
        },
        "pro": {
            "experiment_allowed": True,
            "price_change_cap_pct": 20,
        },
        "enterprise": {
            "experiment_allowed": True,
            "price_change_cap_pct": 30,
        },
    },
}


# =============================================================================
# Factory Function
# =============================================================================

def create_pricing_optimizer(
    config: Optional[Dict[str, Any]] = None
) -> PricingOptimizer:
    """
    Factory function to create a configured PricingOptimizer.
    
    Args:
        config: Optional configuration overrides
        
    Returns:
        Configured PricingOptimizer instance
    """
    optimizer = PricingOptimizer()
    
    # Apply configuration
    effective_config = {**DEFAULT_OPTIMIZER_CONFIG, **(config or {})}
    
    # Set simulator defaults
    sim_config = effective_config.get("simulation_defaults", {})
    optimizer.simulator.set_churn_sensitivity(
        sim_config.get("churn_sensitivity", 0.5)
    )
    
    logger.info("Created PricingOptimizer with configuration")
    return optimizer
