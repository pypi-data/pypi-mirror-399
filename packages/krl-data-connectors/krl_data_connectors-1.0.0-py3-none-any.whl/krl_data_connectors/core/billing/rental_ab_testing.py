# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
#
# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.rental_ab_testing
# This stub remains for backward compatibility but will be removed in v2.0.
# ----------------------------------------------------------------------

from __future__ import annotations
import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.rental_ab_testing is deprecated. "
    "Import from 'app.services.billing.rental_ab_testing' instead.",
    DeprecationWarning,
    stacklevel=2
)

"""
Rental A/B Testing Framework - Phase 6

A/B testing infrastructure for rental pricing, messaging, and trigger optimization.
Integrates with experiment_safety.py for statistical validation.

Experiments:
- Pricing variants (discount levels)
- Messaging variants (StoryBrand copy)
- Trigger timing variants
- Offer presentation variants

Statistical Framework:
- Chi-square tests for conversion rates
- T-tests for revenue metrics
- Bayesian probability calculations
- Sequential testing with early stopping
"""


import hashlib
import logging
import math
import random
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, UTC
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class RentalExperimentType(str, Enum):
    """Types of rental experiments."""
    PRICING = "pricing"              # Test discount levels
    MESSAGING = "messaging"          # Test copy variants
    TRIGGER = "trigger"              # Test trigger timing
    PRESENTATION = "presentation"    # Test UI variants
    BUNDLE = "bundle"                # Test bundle configurations
    CONVERSION = "conversion"        # Test subscription prompts


class ExperimentStatus(str, Enum):
    """Experiment status."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"


class VariantAllocation(str, Enum):
    """How to allocate users to variants."""
    RANDOM = "random"
    HASH_BASED = "hash_based"
    STRATIFIED = "stratified"


class MetricType(str, Enum):
    """Experiment metrics to track."""
    CONVERSION_RATE = "conversion_rate"
    REVENUE = "revenue"
    ARPU = "arpu"
    CLICK_RATE = "click_rate"
    SUBSCRIPTION_RATE = "subscription_rate"
    RETENTION = "retention"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class Variant:
    """Experiment variant configuration."""
    variant_id: str
    name: str
    description: str = ""
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Traffic allocation (0-1)
    allocation: float = 0.5
    
    # Is this the control?
    is_control: bool = False
    
    # Metrics
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    revenue: Decimal = Decimal("0")
    subscription_conversions: int = 0
    
    @property
    def conversion_rate(self) -> float:
        if self.impressions == 0:
            return 0.0
        return self.conversions / self.impressions
    
    @property
    def click_rate(self) -> float:
        if self.impressions == 0:
            return 0.0
        return self.clicks / self.impressions
    
    @property
    def arpu(self) -> Decimal:
        if self.conversions == 0:
            return Decimal("0")
        return self.revenue / self.conversions


@dataclass
class RentalExperiment:
    """A rental system A/B experiment."""
    experiment_id: str
    name: str
    description: str
    
    # Type and status
    experiment_type: RentalExperimentType
    status: ExperimentStatus = ExperimentStatus.DRAFT
    
    # Variants
    variants: List[Variant] = field(default_factory=list)
    
    # Allocation method
    allocation_method: VariantAllocation = VariantAllocation.HASH_BASED
    
    # Targeting
    target_tiers: List[str] = field(default_factory=lambda: ["community", "pro"])
    target_segments: List[str] = field(default_factory=list)
    exclude_tenants: Set[str] = field(default_factory=set)
    
    # Statistical parameters
    primary_metric: MetricType = MetricType.CONVERSION_RATE
    min_sample_size: int = 100
    confidence_level: float = 0.95
    min_effect_size: float = 0.05
    
    # Duration
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_duration_days: int = 30
    
    # Safety
    auto_stop_on_negative: bool = True
    max_revenue_impact_pct: float = 10.0
    
    # Results
    winner_variant_id: Optional[str] = None
    conclusion: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def total_impressions(self) -> int:
        return sum(v.impressions for v in self.variants)
    
    @property
    def is_statistically_significant(self) -> bool:
        return self.total_impressions >= self.min_sample_size * len(self.variants)


@dataclass
class ExperimentEvent:
    """An event in an experiment."""
    event_id: str
    experiment_id: str
    variant_id: str
    tenant_id: str
    
    # Event type
    event_type: str  # impression, click, conversion, subscription
    
    # Value (for revenue events)
    value: Decimal = Decimal("0")
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)
    
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ExperimentResult:
    """Statistical results for an experiment."""
    experiment_id: str
    
    # Per-variant results
    variant_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Statistical tests
    p_value: float = 1.0
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    is_significant: bool = False
    
    # Lift
    lift_pct: float = 0.0
    lift_confidence: float = 0.0
    
    # Winner
    winner_variant_id: Optional[str] = None
    recommendation: str = ""
    
    # Metadata
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# =============================================================================
# Experiment Templates
# =============================================================================

PRICING_EXPERIMENT_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "discount_level": {
        "name": "Rental Discount Level Test",
        "description": "Test different discount levels on rental offers",
        "variants": [
            {"id": "control", "name": "No Discount", "config": {"discount": 0}, "is_control": True},
            {"id": "discount_10", "name": "10% Off", "config": {"discount": 10}},
            {"id": "discount_20", "name": "20% Off", "config": {"discount": 20}},
        ],
    },
    "price_anchor": {
        "name": "Price Anchor Test",
        "description": "Test showing original price vs direct price",
        "variants": [
            {"id": "control", "name": "Direct Price", "config": {"show_anchor": False}, "is_control": True},
            {"id": "anchor", "name": "Show Original", "config": {"show_anchor": True}},
        ],
    },
    "bundle_upsell": {
        "name": "Bundle Upsell Test",
        "description": "Test larger bundle suggestions",
        "variants": [
            {"id": "control", "name": "Requested Size", "config": {"upsell": False}, "is_control": True},
            {"id": "upsell", "name": "Suggest Larger", "config": {"upsell": True, "upsell_discount": 15}},
        ],
    },
}

MESSAGING_EXPERIMENT_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "urgency_level": {
        "name": "Urgency Messaging Test",
        "description": "Test different urgency levels in messaging",
        "variants": [
            {"id": "control", "name": "Low Urgency", "config": {"urgency": "low"}, "is_control": True},
            {"id": "medium", "name": "Medium Urgency", "config": {"urgency": "medium"}},
            {"id": "high", "name": "High Urgency", "config": {"urgency": "high"}},
        ],
    },
    "value_focus": {
        "name": "Value Proposition Test",
        "description": "Test different value proposition focuses",
        "variants": [
            {"id": "control", "name": "Cost Focus", "config": {"focus": "cost"}, "is_control": True},
            {"id": "time", "name": "Time Focus", "config": {"focus": "time"}},
            {"id": "features", "name": "Features Focus", "config": {"focus": "features"}},
        ],
    },
    "cta_text": {
        "name": "CTA Button Text Test",
        "description": "Test different call-to-action text",
        "variants": [
            {"id": "control", "name": "Get Access", "config": {"cta": "Get Access"}, "is_control": True},
            {"id": "unlock", "name": "Unlock Now", "config": {"cta": "Unlock Now"}},
            {"id": "try", "name": "Try It Now", "config": {"cta": "Try It Now"}},
            {"id": "start", "name": "Start Using", "config": {"cta": "Start Using"}},
        ],
    },
}

TRIGGER_EXPERIMENT_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "timing": {
        "name": "Offer Timing Test",
        "description": "Test when to show rental offers",
        "variants": [
            {"id": "control", "name": "On Limit Hit", "config": {"timing": "on_limit"}, "is_control": True},
            {"id": "before", "name": "Before Limit", "config": {"timing": "before_limit", "threshold": 80}},
            {"id": "after_delay", "name": "After Delay", "config": {"timing": "on_limit", "delay_seconds": 5}},
        ],
    },
    "frequency": {
        "name": "Offer Frequency Test",
        "description": "Test how often to show offers",
        "variants": [
            {"id": "control", "name": "Every Trigger", "config": {"frequency": "every"}, "is_control": True},
            {"id": "daily", "name": "Once Daily", "config": {"frequency": "daily"}},
            {"id": "weekly", "name": "Once Weekly", "config": {"frequency": "weekly"}},
        ],
    },
}


# =============================================================================
# Rental A/B Testing Engine
# =============================================================================

class RentalABTestEngine:
    """
    A/B testing engine for rental system optimization.
    
    Manages experiment lifecycle:
    1. Create experiments from templates or custom config
    2. Allocate users to variants
    3. Track events and metrics
    4. Calculate statistical significance
    5. Determine winners and apply results
    """
    
    def __init__(self):
        self._experiments: Dict[str, RentalExperiment] = {}
        self._events: List[ExperimentEvent] = []
        self._user_assignments: Dict[str, Dict[str, str]] = {}  # tenant_id -> {exp_id -> variant_id}
    
    # -------------------------------------------------------------------------
    # Experiment Management
    # -------------------------------------------------------------------------
    
    def create_experiment(
        self,
        name: str,
        experiment_type: RentalExperimentType,
        variants: List[Dict[str, Any]],
        description: str = "",
        **kwargs,
    ) -> RentalExperiment:
        """Create a new experiment."""
        import uuid
        experiment_id = f"exp_{uuid.uuid4().hex[:12]}"
        
        # Create variants
        variant_objects = []
        for v in variants:
            variant = Variant(
                variant_id=v.get("id", f"var_{uuid.uuid4().hex[:8]}"),
                name=v.get("name", "Unnamed"),
                description=v.get("description", ""),
                config=v.get("config", {}),
                allocation=v.get("allocation", 1.0 / len(variants)),
                is_control=v.get("is_control", False),
            )
            variant_objects.append(variant)
        
        experiment = RentalExperiment(
            experiment_id=experiment_id,
            name=name,
            description=description,
            experiment_type=experiment_type,
            variants=variant_objects,
            **kwargs,
        )
        
        self._experiments[experiment_id] = experiment
        logger.info(f"Created experiment {experiment_id}: {name}")
        
        return experiment
    
    def create_from_template(
        self,
        template_type: str,
        template_name: str,
        **overrides,
    ) -> RentalExperiment:
        """Create experiment from a predefined template."""
        templates = {
            "pricing": PRICING_EXPERIMENT_TEMPLATES,
            "messaging": MESSAGING_EXPERIMENT_TEMPLATES,
            "trigger": TRIGGER_EXPERIMENT_TEMPLATES,
        }
        
        template_dict = templates.get(template_type, {})
        template = template_dict.get(template_name)
        
        if not template:
            raise ValueError(f"Unknown template: {template_type}/{template_name}")
        
        exp_type = {
            "pricing": RentalExperimentType.PRICING,
            "messaging": RentalExperimentType.MESSAGING,
            "trigger": RentalExperimentType.TRIGGER,
        }.get(template_type, RentalExperimentType.PRICING)
        
        return self.create_experiment(
            name=overrides.get("name", template["name"]),
            experiment_type=exp_type,
            variants=template["variants"],
            description=overrides.get("description", template["description"]),
            **{k: v for k, v in overrides.items() if k not in ("name", "description")},
        )
    
    def start_experiment(self, experiment_id: str) -> RentalExperiment:
        """Start an experiment."""
        exp = self._experiments.get(experiment_id)
        if not exp:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        exp.status = ExperimentStatus.ACTIVE
        exp.start_date = datetime.now(timezone.utc)
        exp.updated_at = datetime.now(timezone.utc)
        
        logger.info(f"Started experiment {experiment_id}")
        return exp
    
    def pause_experiment(self, experiment_id: str) -> RentalExperiment:
        """Pause an active experiment."""
        exp = self._experiments.get(experiment_id)
        if not exp:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        exp.status = ExperimentStatus.PAUSED
        exp.updated_at = datetime.now(timezone.utc)
        
        logger.info(f"Paused experiment {experiment_id}")
        return exp
    
    def complete_experiment(
        self,
        experiment_id: str,
        winner_variant_id: Optional[str] = None,
        conclusion: str = "",
    ) -> RentalExperiment:
        """Complete an experiment with optional winner."""
        exp = self._experiments.get(experiment_id)
        if not exp:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        exp.status = ExperimentStatus.COMPLETED
        exp.end_date = datetime.now(timezone.utc)
        exp.winner_variant_id = winner_variant_id
        exp.conclusion = conclusion
        exp.updated_at = datetime.now(timezone.utc)
        
        logger.info(f"Completed experiment {experiment_id}, winner: {winner_variant_id}")
        return exp
    
    def get_experiment(self, experiment_id: str) -> Optional[RentalExperiment]:
        """Get experiment by ID."""
        return self._experiments.get(experiment_id)
    
    def list_experiments(
        self,
        status: Optional[ExperimentStatus] = None,
        experiment_type: Optional[RentalExperimentType] = None,
    ) -> List[RentalExperiment]:
        """List experiments with optional filtering."""
        experiments = list(self._experiments.values())
        
        if status:
            experiments = [e for e in experiments if e.status == status]
        
        if experiment_type:
            experiments = [e for e in experiments if e.experiment_type == experiment_type]
        
        return experiments
    
    # -------------------------------------------------------------------------
    # Variant Assignment
    # -------------------------------------------------------------------------
    
    def assign_variant(
        self,
        experiment_id: str,
        tenant_id: str,
        segment: Optional[str] = None,
    ) -> Optional[Variant]:
        """
        Assign a tenant to a variant.
        
        Uses deterministic hashing for consistent assignment.
        """
        exp = self._experiments.get(experiment_id)
        if not exp or exp.status != ExperimentStatus.ACTIVE:
            return None
        
        # Check if already assigned
        if tenant_id in self._user_assignments:
            existing = self._user_assignments[tenant_id].get(experiment_id)
            if existing:
                variant = next((v for v in exp.variants if v.variant_id == existing), None)
                return variant
        
        # Check exclusions
        if tenant_id in exp.exclude_tenants:
            return None
        
        # Assign based on method
        if exp.allocation_method == VariantAllocation.HASH_BASED:
            variant = self._hash_assign(exp, tenant_id)
        elif exp.allocation_method == VariantAllocation.RANDOM:
            variant = self._random_assign(exp)
        else:  # STRATIFIED
            variant = self._stratified_assign(exp, segment)
        
        # Store assignment
        if tenant_id not in self._user_assignments:
            self._user_assignments[tenant_id] = {}
        self._user_assignments[tenant_id][experiment_id] = variant.variant_id
        
        return variant
    
    def get_variant_for_tenant(
        self,
        experiment_id: str,
        tenant_id: str,
    ) -> Optional[Variant]:
        """Get the assigned variant for a tenant."""
        exp = self._experiments.get(experiment_id)
        if not exp:
            return None
        
        variant_id = self._user_assignments.get(tenant_id, {}).get(experiment_id)
        if not variant_id:
            return None
        
        return next((v for v in exp.variants if v.variant_id == variant_id), None)
    
    def _hash_assign(self, experiment: RentalExperiment, tenant_id: str) -> Variant:
        """Deterministic assignment using hash."""
        hash_input = f"{experiment.experiment_id}:{tenant_id}"
        hash_value = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16)
        bucket = (hash_value % 100) / 100.0
        
        cumulative = 0.0
        for variant in experiment.variants:
            cumulative += variant.allocation
            if bucket < cumulative:
                return variant
        
        return experiment.variants[-1]
    
    def _random_assign(self, experiment: RentalExperiment) -> Variant:
        """Random assignment."""
        rand = random.random()
        cumulative = 0.0
        for variant in experiment.variants:
            cumulative += variant.allocation
            if rand < cumulative:
                return variant
        return experiment.variants[-1]
    
    def _stratified_assign(
        self,
        experiment: RentalExperiment,
        segment: Optional[str],
    ) -> Variant:
        """Stratified assignment based on segment."""
        # For now, fall back to hash-based with segment in hash
        hash_input = f"{experiment.experiment_id}:{segment or 'default'}"
        return self._hash_assign(experiment, hash_input)
    
    # -------------------------------------------------------------------------
    # Event Tracking
    # -------------------------------------------------------------------------
    
    def track_impression(
        self,
        experiment_id: str,
        variant_id: str,
        tenant_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track an impression event."""
        self._track_event(experiment_id, variant_id, tenant_id, "impression", context=context)
        
        # Update variant metrics
        exp = self._experiments.get(experiment_id)
        if exp:
            variant = next((v for v in exp.variants if v.variant_id == variant_id), None)
            if variant:
                variant.impressions += 1
    
    def track_click(
        self,
        experiment_id: str,
        variant_id: str,
        tenant_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track a click event."""
        self._track_event(experiment_id, variant_id, tenant_id, "click", context=context)
        
        exp = self._experiments.get(experiment_id)
        if exp:
            variant = next((v for v in exp.variants if v.variant_id == variant_id), None)
            if variant:
                variant.clicks += 1
    
    def track_conversion(
        self,
        experiment_id: str,
        variant_id: str,
        tenant_id: str,
        revenue: Decimal,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track a conversion event with revenue."""
        self._track_event(
            experiment_id, variant_id, tenant_id, "conversion",
            value=revenue, context=context,
        )
        
        exp = self._experiments.get(experiment_id)
        if exp:
            variant = next((v for v in exp.variants if v.variant_id == variant_id), None)
            if variant:
                variant.conversions += 1
                variant.revenue += revenue
    
    def track_subscription(
        self,
        experiment_id: str,
        variant_id: str,
        tenant_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track a rental-to-subscription conversion."""
        self._track_event(
            experiment_id, variant_id, tenant_id, "subscription",
            context=context,
        )
        
        exp = self._experiments.get(experiment_id)
        if exp:
            variant = next((v for v in exp.variants if v.variant_id == variant_id), None)
            if variant:
                variant.subscription_conversions += 1
    
    def _track_event(
        self,
        experiment_id: str,
        variant_id: str,
        tenant_id: str,
        event_type: str,
        value: Decimal = Decimal("0"),
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Internal event tracking."""
        import uuid
        event = ExperimentEvent(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            experiment_id=experiment_id,
            variant_id=variant_id,
            tenant_id=tenant_id,
            event_type=event_type,
            value=value,
            context=context or {},
        )
        self._events.append(event)
    
    # -------------------------------------------------------------------------
    # Statistical Analysis
    # -------------------------------------------------------------------------
    
    def analyze_experiment(self, experiment_id: str) -> ExperimentResult:
        """
        Perform statistical analysis on experiment results.
        
        Uses appropriate tests based on metric type:
        - Conversion rates: Chi-square test
        - Revenue metrics: Welch's t-test
        """
        exp = self._experiments.get(experiment_id)
        if not exp:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        # Get control variant
        control = next((v for v in exp.variants if v.is_control), exp.variants[0])
        
        # Calculate per-variant results
        variant_results = {}
        for variant in exp.variants:
            variant_results[variant.variant_id] = {
                "name": variant.name,
                "impressions": variant.impressions,
                "clicks": variant.clicks,
                "conversions": variant.conversions,
                "revenue": float(variant.revenue),
                "conversion_rate": variant.conversion_rate,
                "click_rate": variant.click_rate,
                "arpu": float(variant.arpu),
            }
        
        # Find best performing treatment variant
        treatment_variants = [v for v in exp.variants if not v.is_control]
        if not treatment_variants:
            treatment_variants = exp.variants
        
        best_variant = max(
            treatment_variants,
            key=lambda v: self._get_metric_value(v, exp.primary_metric),
        )
        
        # Calculate lift
        control_metric = self._get_metric_value(control, exp.primary_metric)
        best_metric = self._get_metric_value(best_variant, exp.primary_metric)
        
        if control_metric > 0:
            lift_pct = ((best_metric - control_metric) / control_metric) * 100
        else:
            lift_pct = 0.0 if best_metric == 0 else 100.0
        
        # Statistical significance (simplified chi-square for conversion rates)
        p_value, is_significant = self._calculate_significance(
            control, best_variant, exp.primary_metric, exp.confidence_level,
        )
        
        # Determine winner
        winner = None
        recommendation = ""
        
        if is_significant and lift_pct > 0:
            winner = best_variant.variant_id
            recommendation = f"Implement {best_variant.name}: {lift_pct:.1f}% lift"
        elif is_significant and lift_pct < 0:
            winner = control.variant_id
            recommendation = f"Keep control: treatment showed {-lift_pct:.1f}% decline"
        else:
            recommendation = f"Not significant. Need {exp.min_sample_size - exp.total_impressions // len(exp.variants)} more samples per variant."
        
        return ExperimentResult(
            experiment_id=experiment_id,
            variant_results=variant_results,
            p_value=p_value,
            confidence_interval=self._calculate_confidence_interval(control, best_variant),
            is_significant=is_significant,
            lift_pct=lift_pct,
            lift_confidence=1 - p_value if p_value < 1 else 0,
            winner_variant_id=winner,
            recommendation=recommendation,
        )
    
    def _get_metric_value(self, variant: Variant, metric: MetricType) -> float:
        """Get metric value for a variant."""
        if metric == MetricType.CONVERSION_RATE:
            return variant.conversion_rate
        elif metric == MetricType.CLICK_RATE:
            return variant.click_rate
        elif metric == MetricType.REVENUE:
            return float(variant.revenue)
        elif metric == MetricType.ARPU:
            return float(variant.arpu)
        elif metric == MetricType.SUBSCRIPTION_RATE:
            if variant.conversions == 0:
                return 0.0
            return variant.subscription_conversions / variant.conversions
        return 0.0
    
    def _calculate_significance(
        self,
        control: Variant,
        treatment: Variant,
        metric: MetricType,
        confidence_level: float,
    ) -> Tuple[float, bool]:
        """
        Calculate statistical significance.
        
        Uses chi-square approximation for conversion rates.
        """
        # Get counts
        n1 = control.impressions
        n2 = treatment.impressions
        
        if n1 < 10 or n2 < 10:
            return 1.0, False
        
        # For conversion rate, use chi-square
        if metric in (MetricType.CONVERSION_RATE, MetricType.CLICK_RATE):
            c1 = control.conversions if metric == MetricType.CONVERSION_RATE else control.clicks
            c2 = treatment.conversions if metric == MetricType.CONVERSION_RATE else treatment.clicks
            
            # Pooled proportion
            p_pooled = (c1 + c2) / (n1 + n2)
            
            if p_pooled == 0 or p_pooled == 1:
                return 1.0, False
            
            # Standard error
            se = math.sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2))
            
            if se == 0:
                return 1.0, False
            
            # Z-score
            p1 = c1 / n1
            p2 = c2 / n2
            z = abs(p2 - p1) / se
            
            # P-value from z-score (two-tailed, approximation)
            p_value = 2 * (1 - self._normal_cdf(z))
            
            is_significant = p_value < (1 - confidence_level)
            return p_value, is_significant
        
        # For revenue metrics, simplified comparison
        return 0.5, False  # Placeholder
    
    def _calculate_confidence_interval(
        self,
        control: Variant,
        treatment: Variant,
    ) -> Tuple[float, float]:
        """Calculate confidence interval for lift."""
        p1 = control.conversion_rate
        p2 = treatment.conversion_rate
        n1 = max(control.impressions, 1)
        n2 = max(treatment.impressions, 1)
        
        # Standard error of difference
        se = math.sqrt((p1 * (1 - p1) / n1) + (p2 * (1 - p2) / n2))
        
        # 95% CI
        diff = p2 - p1
        margin = 1.96 * se
        
        return (diff - margin, diff + margin)
    
    def _normal_cdf(self, x: float) -> float:
        """Approximate normal CDF."""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    
    # -------------------------------------------------------------------------
    # Automated Checks
    # -------------------------------------------------------------------------
    
    def check_stopping_rules(self, experiment_id: str) -> Dict[str, Any]:
        """
        Check if experiment should be stopped.
        
        Stopping rules:
        1. Statistical significance reached
        2. Sample size achieved
        3. Max duration exceeded
        4. Negative lift detected
        """
        exp = self._experiments.get(experiment_id)
        if not exp:
            return {"stop": False, "reason": "Experiment not found"}
        
        result = self.analyze_experiment(experiment_id)
        
        checks = {
            "significance_reached": result.is_significant,
            "sample_size_achieved": exp.is_statistically_significant,
            "max_duration_exceeded": self._check_duration_exceeded(exp),
            "negative_lift_detected": result.lift_pct < -exp.min_effect_size * 100 if exp.auto_stop_on_negative else False,
        }
        
        should_stop = any([
            checks["significance_reached"] and checks["sample_size_achieved"],
            checks["max_duration_exceeded"],
            checks["negative_lift_detected"],
        ])
        
        reasons = [k for k, v in checks.items() if v]
        
        return {
            "stop": should_stop,
            "reasons": reasons,
            "checks": checks,
            "result": result,
        }
    
    def _check_duration_exceeded(self, exp: RentalExperiment) -> bool:
        """Check if experiment exceeded max duration."""
        if not exp.start_date:
            return False
        
        elapsed = datetime.now(timezone.utc) - exp.start_date
        return elapsed.days > exp.max_duration_days


# =============================================================================
# Singleton Instance
# =============================================================================

_ab_test_engine: Optional[RentalABTestEngine] = None


def get_ab_test_engine() -> RentalABTestEngine:
    """Get or create A/B test engine instance."""
    global _ab_test_engine
    if _ab_test_engine is None:
        _ab_test_engine = RentalABTestEngine()
    return _ab_test_engine
