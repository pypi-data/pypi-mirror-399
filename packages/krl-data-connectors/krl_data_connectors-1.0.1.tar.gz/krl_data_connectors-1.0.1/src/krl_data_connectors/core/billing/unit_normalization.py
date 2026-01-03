from __future__ import annotations

# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
#
# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.unit_normalization
# This stub remains for backward compatibility but will be removed in v2.0.
# ----------------------------------------------------------------------
import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.unit_normalization is deprecated. "
    "Import from 'app.services.billing.unit_normalization' instead.",
    DeprecationWarning,
    stacklevel=2
)

"""
Unit Normalization Engine - Phase 3 Week 21B

The economic backbone that converts raw usage metrics into
normalized billable units. Ensures consistent billing across
tiers and prevents risk pricing from multiplying inconsistent values.

Unit Types:
- BILLABLE: Standard usage that generates revenue
- PENALTY: Usage that incurs additional charges (violations, abuse)
- PREMIUM: High-value actions that generate premium revenue
- CREDIT: Usage that earns credits or discounts
- EXEMPT: Usage that is not billed (included, promotional, etc.)

This layer sits between TelemetryIngestion and UsageMeter.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, UTC
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class UnitType(Enum):
    """Types of normalized units."""
    BILLABLE = "billable"    # Standard revenue-generating usage
    PENALTY = "penalty"      # Additional charges for violations
    PREMIUM = "premium"      # High-value actions
    CREDIT = "credit"        # Earns credits/discounts
    EXEMPT = "exempt"        # Not billed


class UnitCategory(Enum):
    """Categories of billable units."""
    # Compute
    COMPUTE_UNIT = "compute_unit"          # 1 CU = 1 vCPU-second
    GPU_UNIT = "gpu_unit"                  # 1 GU = 1 GPU-second
    
    # API
    API_UNIT = "api_unit"                  # 1 AU = 1 API call
    BANDWIDTH_UNIT = "bandwidth_unit"      # 1 BU = 1 MB transferred
    
    # ML
    INFERENCE_UNIT = "inference_unit"      # 1 IU = 1 ML inference
    TRAINING_UNIT = "training_unit"        # 1 TU = 1 training minute
    FEDERATION_UNIT = "federation_unit"    # 1 FU = 1 federation round
    
    # Security
    THREAT_UNIT = "threat_unit"            # 1 THU = 1 threat detection
    ENFORCEMENT_UNIT = "enforcement_unit"  # 1 EU = 1 enforcement action
    ANOMALY_UNIT = "anomaly_unit"          # 1 ANU = 1 anomaly analysis
    
    # Storage
    STORAGE_UNIT = "storage_unit"          # 1 SU = 1 GB-month
    
    # Premium
    CROWN_JEWEL_UNIT = "crown_jewel_unit"  # 1 CJU = 1 crown jewel access
    CUSTOM_MODEL_UNIT = "custom_model_unit"  # 1 CMU = 1 custom model op


class ConversionStrategy(Enum):
    """Strategies for unit conversion."""
    DIRECT = "direct"           # 1:1 mapping
    SCALED = "scaled"           # Linear scaling
    TIERED = "tiered"           # Different rates at different volumes
    TIME_BASED = "time_based"   # Based on duration
    RESOURCE_BASED = "resource_based"  # Based on resources consumed
    COMPLEXITY = "complexity"   # Based on operation complexity


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ConversionRule:
    """Rule for converting raw metric to normalized unit."""
    rule_id: str
    source_metric: str  # Raw metric name (e.g., "api.request")
    target_category: UnitCategory
    unit_type: UnitType
    
    # Conversion parameters
    strategy: ConversionStrategy = ConversionStrategy.DIRECT
    conversion_factor: Decimal = Decimal("1.0")
    
    # Tiered conversion (for TIERED strategy)
    tiers: List[Tuple[int, Decimal]] = field(default_factory=list)
    # Format: [(threshold, factor), ...] e.g., [(100, 1.0), (1000, 0.9), (10000, 0.8)]
    
    # Time-based (for TIME_BASED strategy)
    time_divisor_seconds: int = 60  # Divide duration by this
    
    # Resource-based (for RESOURCE_BASED strategy)
    resource_multipliers: Dict[str, Decimal] = field(default_factory=dict)
    # e.g., {"cpu_cores": 1.0, "memory_gb": 0.5}
    
    # Complexity (for COMPLEXITY strategy)
    complexity_weights: Dict[str, Decimal] = field(default_factory=dict)
    # e.g., {"simple": 1.0, "medium": 2.0, "complex": 5.0}
    
    # Tier-specific overrides
    tier_factors: Dict[str, Decimal] = field(default_factory=dict)
    # e.g., {"community": 1.0, "pro": 0.9, "enterprise": 0.8}
    
    # Conditions
    min_value: Decimal = Decimal("0")
    max_value: Optional[Decimal] = None
    
    # Metadata
    description: str = ""
    enabled: bool = True


@dataclass
class NormalizedUnit:
    """A normalized billable unit."""
    unit_id: str
    tenant_id: str
    category: UnitCategory
    unit_type: UnitType
    
    # Quantity
    quantity: Decimal
    raw_quantity: Decimal  # Original value before conversion
    
    # Pricing
    unit_price: Decimal = Decimal("0")
    total_value: Decimal = Decimal("0")
    
    # Conversion trace
    source_metric: str = ""
    rule_id: str = ""
    conversion_factor: Decimal = Decimal("1.0")
    tier_factor: Decimal = Decimal("1.0")
    
    # Context
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "tenant_id": self.tenant_id,
            "category": self.category.value,
            "unit_type": self.unit_type.value,
            "quantity": str(self.quantity),
            "raw_quantity": str(self.raw_quantity),
            "unit_price": str(self.unit_price),
            "total_value": str(self.total_value),
            "source_metric": self.source_metric,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class UnitPricing:
    """Pricing for a unit category."""
    category: UnitCategory
    base_price: Decimal  # Per unit
    
    # Volume discounts
    volume_tiers: List[Tuple[int, Decimal]] = field(default_factory=list)
    # Format: [(threshold, discount_multiplier), ...]
    
    # Tier-specific pricing
    tier_pricing: Dict[str, Decimal] = field(default_factory=dict)
    # e.g., {"community": 0.01, "pro": 0.008, "enterprise": 0.005}
    
    # Premium multiplier for premium unit type
    premium_multiplier: Decimal = Decimal("1.5")
    
    # Penalty multiplier for penalty unit type
    penalty_multiplier: Decimal = Decimal("2.0")
    
    # Credit rate for credit unit type
    credit_rate: Decimal = Decimal("0.1")  # 10% credit


@dataclass
class NormalizationResult:
    """Result of normalizing a batch of metrics."""
    success: bool
    units: List[NormalizedUnit] = field(default_factory=list)
    
    # Aggregates
    total_billable: Decimal = Decimal("0")
    total_penalty: Decimal = Decimal("0")
    total_premium: Decimal = Decimal("0")
    total_credit: Decimal = Decimal("0")
    total_exempt: int = 0
    
    # Errors
    errors: List[str] = field(default_factory=list)
    unmapped_metrics: List[str] = field(default_factory=list)
    
    # Timing
    processed_at: datetime = field(default_factory=datetime.now)
    processing_time_ms: float = 0


# =============================================================================
# Default Conversion Rules
# =============================================================================

DEFAULT_CONVERSION_RULES: List[ConversionRule] = [
    # API conversions
    ConversionRule(
        rule_id="api_request",
        source_metric="api.request",
        target_category=UnitCategory.API_UNIT,
        unit_type=UnitType.BILLABLE,
        strategy=ConversionStrategy.DIRECT,
        conversion_factor=Decimal("1.0"),
        tier_factors={"community": Decimal("1.0"), "pro": Decimal("1.0"), "enterprise": Decimal("1.0")},
        description="Standard API request",
    ),
    ConversionRule(
        rule_id="api_response",
        source_metric="api.response",
        target_category=UnitCategory.API_UNIT,
        unit_type=UnitType.BILLABLE,
        strategy=ConversionStrategy.DIRECT,
        conversion_factor=Decimal("1.0"),
        description="Standard API response",
    ),
    ConversionRule(
        rule_id="api_bandwidth",
        source_metric="api.bandwidth_bytes",
        target_category=UnitCategory.BANDWIDTH_UNIT,
        unit_type=UnitType.BILLABLE,
        strategy=ConversionStrategy.SCALED,
        conversion_factor=Decimal("0.000001"),  # Bytes to MB
        description="Bandwidth in MB",
    ),
    
    # ML conversions
    ConversionRule(
        rule_id="ml_inference",
        source_metric="ml.inference",
        target_category=UnitCategory.INFERENCE_UNIT,
        unit_type=UnitType.BILLABLE,
        strategy=ConversionStrategy.COMPLEXITY,
        complexity_weights={
            "simple": Decimal("1.0"),
            "standard": Decimal("2.0"),
            "complex": Decimal("5.0"),
            "ensemble": Decimal("10.0"),
        },
        description="ML inference by complexity",
    ),
    ConversionRule(
        rule_id="ml_prediction",
        source_metric="ml.prediction",
        target_category=UnitCategory.INFERENCE_UNIT,
        unit_type=UnitType.BILLABLE,
        strategy=ConversionStrategy.DIRECT,
        conversion_factor=Decimal("1.0"),
        description="ML prediction",
    ),
    ConversionRule(
        rule_id="ml_training",
        source_metric="ml.training_seconds",
        target_category=UnitCategory.TRAINING_UNIT,
        unit_type=UnitType.PREMIUM,
        strategy=ConversionStrategy.TIME_BASED,
        time_divisor_seconds=60,  # Convert to minutes
        description="ML training in minutes",
    ),
    ConversionRule(
        rule_id="ml_retrain",
        source_metric="ml.retrain",
        target_category=UnitCategory.TRAINING_UNIT,
        unit_type=UnitType.PREMIUM,
        strategy=ConversionStrategy.SCALED,
        conversion_factor=Decimal("10.0"),  # Retrain = 10 training units
        description="Model retrain operation",
    ),
    ConversionRule(
        rule_id="federated_round",
        source_metric="ml.federation_round",
        target_category=UnitCategory.FEDERATION_UNIT,
        unit_type=UnitType.PREMIUM,
        strategy=ConversionStrategy.RESOURCE_BASED,
        resource_multipliers={
            "participants": Decimal("1.0"),
            "data_size_gb": Decimal("0.5"),
        },
        description="Federated learning round",
    ),
    
    # Security conversions
    ConversionRule(
        rule_id="threat_detected",
        source_metric="threat.detected",
        target_category=UnitCategory.THREAT_UNIT,
        unit_type=UnitType.BILLABLE,
        strategy=ConversionStrategy.COMPLEXITY,
        complexity_weights={
            "low": Decimal("1.0"),
            "medium": Decimal("2.0"),
            "high": Decimal("5.0"),
            "critical": Decimal("10.0"),
        },
        description="Threat detection by severity",
    ),
    ConversionRule(
        rule_id="enforcement_action",
        source_metric="enforcement.action",
        target_category=UnitCategory.ENFORCEMENT_UNIT,
        unit_type=UnitType.BILLABLE,
        strategy=ConversionStrategy.COMPLEXITY,
        complexity_weights={
            "warn": Decimal("0.5"),
            "throttle": Decimal("1.0"),
            "block": Decimal("2.0"),
            "quarantine": Decimal("5.0"),
        },
        description="Enforcement action by severity",
    ),
    ConversionRule(
        rule_id="anomaly_analysis",
        source_metric="anomaly.analysis",
        target_category=UnitCategory.ANOMALY_UNIT,
        unit_type=UnitType.BILLABLE,
        strategy=ConversionStrategy.DIRECT,
        conversion_factor=Decimal("1.0"),
        description="Anomaly analysis",
    ),
    
    # Premium conversions
    ConversionRule(
        rule_id="crown_jewel_access",
        source_metric="crownjewel.access",
        target_category=UnitCategory.CROWN_JEWEL_UNIT,
        unit_type=UnitType.PREMIUM,
        strategy=ConversionStrategy.DIRECT,
        conversion_factor=Decimal("1.0"),
        tier_factors={
            "community": Decimal("0"),  # Not available
            "pro": Decimal("1.0"),
            "enterprise": Decimal("1.0"),
        },
        description="Crown jewel asset access",
    ),
    ConversionRule(
        rule_id="custom_model_deploy",
        source_metric="model.custom_deploy",
        target_category=UnitCategory.CUSTOM_MODEL_UNIT,
        unit_type=UnitType.PREMIUM,
        strategy=ConversionStrategy.DIRECT,
        conversion_factor=Decimal("1.0"),
        tier_factors={
            "community": Decimal("0"),  # Not available
            "pro": Decimal("0"),  # Not available
            "enterprise": Decimal("1.0"),
        },
        description="Custom model deployment",
    ),
    
    # Penalty conversions
    ConversionRule(
        rule_id="tier_violation",
        source_metric="violation.tier",
        target_category=UnitCategory.API_UNIT,
        unit_type=UnitType.PENALTY,
        strategy=ConversionStrategy.SCALED,
        conversion_factor=Decimal("10.0"),  # 10x penalty
        description="Tier violation penalty",
    ),
    ConversionRule(
        rule_id="rate_limit_violation",
        source_metric="violation.rate_limit",
        target_category=UnitCategory.API_UNIT,
        unit_type=UnitType.PENALTY,
        strategy=ConversionStrategy.SCALED,
        conversion_factor=Decimal("5.0"),  # 5x penalty
        description="Rate limit violation penalty",
    ),
    ConversionRule(
        rule_id="abuse_event",
        source_metric="abuse.detected",
        target_category=UnitCategory.ENFORCEMENT_UNIT,
        unit_type=UnitType.PENALTY,
        strategy=ConversionStrategy.SCALED,
        conversion_factor=Decimal("20.0"),  # 20x penalty
        description="Abuse detection penalty",
    ),
]


# =============================================================================
# Default Unit Pricing
# =============================================================================

DEFAULT_UNIT_PRICING: Dict[UnitCategory, UnitPricing] = {
    UnitCategory.API_UNIT: UnitPricing(
        category=UnitCategory.API_UNIT,
        base_price=Decimal("0.0001"),  # $0.0001 per API call
        volume_tiers=[
            (100000, Decimal("0.9")),    # 10% discount after 100K
            (1000000, Decimal("0.8")),   # 20% discount after 1M
            (10000000, Decimal("0.7")),  # 30% discount after 10M
        ],
        tier_pricing={
            "community": Decimal("0"),      # Free tier
            "pro": Decimal("0.0001"),
            "enterprise": Decimal("0.00008"),
        },
    ),
    UnitCategory.BANDWIDTH_UNIT: UnitPricing(
        category=UnitCategory.BANDWIDTH_UNIT,
        base_price=Decimal("0.01"),  # $0.01 per MB
        tier_pricing={
            "community": Decimal("0"),
            "pro": Decimal("0.01"),
            "enterprise": Decimal("0.008"),
        },
    ),
    UnitCategory.INFERENCE_UNIT: UnitPricing(
        category=UnitCategory.INFERENCE_UNIT,
        base_price=Decimal("0.001"),  # $0.001 per inference
        volume_tiers=[
            (10000, Decimal("0.9")),
            (100000, Decimal("0.8")),
        ],
        tier_pricing={
            "community": Decimal("0"),
            "pro": Decimal("0.001"),
            "enterprise": Decimal("0.0008"),
        },
    ),
    UnitCategory.TRAINING_UNIT: UnitPricing(
        category=UnitCategory.TRAINING_UNIT,
        base_price=Decimal("0.10"),  # $0.10 per training minute
        tier_pricing={
            "community": Decimal("0"),
            "pro": Decimal("0.10"),
            "enterprise": Decimal("0.08"),
        },
        premium_multiplier=Decimal("1.5"),
    ),
    UnitCategory.FEDERATION_UNIT: UnitPricing(
        category=UnitCategory.FEDERATION_UNIT,
        base_price=Decimal("1.00"),  # $1.00 per federation round
        tier_pricing={
            "community": Decimal("0"),
            "pro": Decimal("1.00"),
            "enterprise": Decimal("0.80"),
        },
        premium_multiplier=Decimal("2.0"),
    ),
    UnitCategory.THREAT_UNIT: UnitPricing(
        category=UnitCategory.THREAT_UNIT,
        base_price=Decimal("0.01"),  # $0.01 per threat detection
        tier_pricing={
            "community": Decimal("0"),
            "pro": Decimal("0.01"),
            "enterprise": Decimal("0.008"),
        },
    ),
    UnitCategory.ENFORCEMENT_UNIT: UnitPricing(
        category=UnitCategory.ENFORCEMENT_UNIT,
        base_price=Decimal("0.005"),  # $0.005 per enforcement
        tier_pricing={
            "community": Decimal("0"),
            "pro": Decimal("0.005"),
            "enterprise": Decimal("0.004"),
        },
        penalty_multiplier=Decimal("3.0"),  # 3x for penalty type
    ),
    UnitCategory.ANOMALY_UNIT: UnitPricing(
        category=UnitCategory.ANOMALY_UNIT,
        base_price=Decimal("0.02"),  # $0.02 per anomaly analysis
        tier_pricing={
            "community": Decimal("0"),
            "pro": Decimal("0.02"),
            "enterprise": Decimal("0.016"),
        },
    ),
    UnitCategory.CROWN_JEWEL_UNIT: UnitPricing(
        category=UnitCategory.CROWN_JEWEL_UNIT,
        base_price=Decimal("0.10"),  # $0.10 per crown jewel access
        tier_pricing={
            "community": Decimal("0"),
            "pro": Decimal("0.10"),
            "enterprise": Decimal("0.08"),
        },
        premium_multiplier=Decimal("2.0"),
    ),
    UnitCategory.CUSTOM_MODEL_UNIT: UnitPricing(
        category=UnitCategory.CUSTOM_MODEL_UNIT,
        base_price=Decimal("5.00"),  # $5.00 per custom model operation
        tier_pricing={
            "community": Decimal("0"),
            "pro": Decimal("0"),
            "enterprise": Decimal("5.00"),
        },
        premium_multiplier=Decimal("1.0"),
    ),
    UnitCategory.STORAGE_UNIT: UnitPricing(
        category=UnitCategory.STORAGE_UNIT,
        base_price=Decimal("0.10"),  # $0.10 per GB-month
        tier_pricing={
            "community": Decimal("0"),
            "pro": Decimal("0.10"),
            "enterprise": Decimal("0.08"),
        },
    ),
    UnitCategory.COMPUTE_UNIT: UnitPricing(
        category=UnitCategory.COMPUTE_UNIT,
        base_price=Decimal("0.00001"),  # $0.00001 per compute unit
        tier_pricing={
            "community": Decimal("0"),
            "pro": Decimal("0.00001"),
            "enterprise": Decimal("0.000008"),
        },
    ),
    UnitCategory.GPU_UNIT: UnitPricing(
        category=UnitCategory.GPU_UNIT,
        base_price=Decimal("0.001"),  # $0.001 per GPU unit
        tier_pricing={
            "community": Decimal("0"),
            "pro": Decimal("0.001"),
            "enterprise": Decimal("0.0008"),
        },
        premium_multiplier=Decimal("1.5"),
    ),
}


# =============================================================================
# Unit Normalizer
# =============================================================================

class UnitNormalizer:
    """
    Normalizes raw metrics to billable units.
    
    Applies conversion rules and pricing to transform
    telemetry into consistent economic values.
    """
    
    def __init__(
        self,
        rules: Optional[List[ConversionRule]] = None,
        pricing: Optional[Dict[UnitCategory, UnitPricing]] = None,
    ):
        self._rules: Dict[str, ConversionRule] = {}
        self._pricing = pricing or dict(DEFAULT_UNIT_PRICING)
        
        # Index rules by source metric
        for rule in (rules or DEFAULT_CONVERSION_RULES):
            self._rules[rule.source_metric] = rule
        
        # Counters
        self._unit_counter = 0
        
        logger.info(f"UnitNormalizer initialized with {len(self._rules)} rules")
    
    def normalize(
        self,
        tenant_id: str,
        metric: str,
        value: float,
        tier: str = "community",
        metadata: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> Optional[NormalizedUnit]:
        """
        Normalize a single metric to a billable unit.
        
        Returns None if no rule exists or metric is exempt.
        """
        rule = self._rules.get(metric)
        if not rule or not rule.enabled:
            return None
        
        # Check tier availability
        tier_factor = rule.tier_factors.get(tier, Decimal("1.0"))
        if tier_factor == Decimal("0"):
            # Feature not available for this tier
            return None
        
        # Convert quantity
        raw_quantity = Decimal(str(value))
        quantity = self._apply_conversion(rule, raw_quantity, metadata or {})
        
        # Apply tier factor
        quantity = quantity * tier_factor
        
        # Check bounds
        if quantity < rule.min_value:
            return None
        if rule.max_value and quantity > rule.max_value:
            quantity = rule.max_value
        
        # Calculate price
        unit_price, total_value = self._calculate_price(
            rule.target_category,
            rule.unit_type,
            quantity,
            tier,
        )
        
        # Create normalized unit
        self._unit_counter += 1
        unit_id = f"NU-{self._unit_counter:012d}"
        
        return NormalizedUnit(
            unit_id=unit_id,
            tenant_id=tenant_id,
            category=rule.target_category,
            unit_type=rule.unit_type,
            quantity=quantity.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
            raw_quantity=raw_quantity,
            unit_price=unit_price,
            total_value=total_value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
            source_metric=metric,
            rule_id=rule.rule_id,
            conversion_factor=rule.conversion_factor,
            tier_factor=tier_factor,
            correlation_id=correlation_id,
            metadata=metadata or {},
        )
    
    def normalize_batch(
        self,
        tenant_id: str,
        metrics: List[Tuple[str, float]],
        tier: str = "community",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> NormalizationResult:
        """
        Normalize a batch of metrics.
        
        Returns aggregated result with all units.
        """
        import time
        start = time.time()
        
        result = NormalizationResult(success=True)
        
        for metric, value in metrics:
            try:
                unit = self.normalize(tenant_id, metric, value, tier, metadata)
                
                if unit:
                    result.units.append(unit)
                    
                    # Aggregate by type
                    if unit.unit_type == UnitType.BILLABLE:
                        result.total_billable += unit.total_value
                    elif unit.unit_type == UnitType.PENALTY:
                        result.total_penalty += unit.total_value
                    elif unit.unit_type == UnitType.PREMIUM:
                        result.total_premium += unit.total_value
                    elif unit.unit_type == UnitType.CREDIT:
                        result.total_credit += unit.total_value
                    elif unit.unit_type == UnitType.EXEMPT:
                        result.total_exempt += 1
                else:
                    # Check if metric is unmapped
                    if metric not in self._rules:
                        result.unmapped_metrics.append(metric)
                        
            except Exception as e:
                result.errors.append(f"Error normalizing {metric}: {e}")
        
        result.processing_time_ms = (time.time() - start) * 1000
        result.success = len(result.errors) == 0
        
        return result
    
    def _apply_conversion(
        self,
        rule: ConversionRule,
        value: Decimal,
        metadata: Dict[str, Any],
    ) -> Decimal:
        """Apply conversion strategy to value."""
        if rule.strategy == ConversionStrategy.DIRECT:
            return value * rule.conversion_factor
        
        elif rule.strategy == ConversionStrategy.SCALED:
            return value * rule.conversion_factor
        
        elif rule.strategy == ConversionStrategy.TIERED:
            return self._apply_tiered_conversion(value, rule.tiers, rule.conversion_factor)
        
        elif rule.strategy == ConversionStrategy.TIME_BASED:
            # Assume value is in seconds
            return value / Decimal(str(rule.time_divisor_seconds))
        
        elif rule.strategy == ConversionStrategy.RESOURCE_BASED:
            return self._apply_resource_conversion(value, rule.resource_multipliers, metadata)
        
        elif rule.strategy == ConversionStrategy.COMPLEXITY:
            return self._apply_complexity_conversion(value, rule.complexity_weights, metadata)
        
        return value * rule.conversion_factor
    
    def _apply_tiered_conversion(
        self,
        value: Decimal,
        tiers: List[Tuple[int, Decimal]],
        base_factor: Decimal,
    ) -> Decimal:
        """Apply tiered conversion with volume discounts."""
        if not tiers:
            return value * base_factor
        
        # Sort tiers by threshold descending
        sorted_tiers = sorted(tiers, key=lambda x: x[0], reverse=True)
        
        for threshold, factor in sorted_tiers:
            if value >= threshold:
                return value * factor * base_factor
        
        return value * base_factor
    
    def _apply_resource_conversion(
        self,
        value: Decimal,
        multipliers: Dict[str, Decimal],
        metadata: Dict[str, Any],
    ) -> Decimal:
        """Apply resource-based conversion."""
        total = value
        
        for resource, multiplier in multipliers.items():
            resource_value = metadata.get(resource, 0)
            if resource_value:
                total += Decimal(str(resource_value)) * multiplier
        
        return total
    
    def _apply_complexity_conversion(
        self,
        value: Decimal,
        weights: Dict[str, Decimal],
        metadata: Dict[str, Any],
    ) -> Decimal:
        """Apply complexity-based conversion."""
        complexity = metadata.get("complexity", "standard")
        weight = weights.get(complexity, Decimal("1.0"))
        return value * weight
    
    def _calculate_price(
        self,
        category: UnitCategory,
        unit_type: UnitType,
        quantity: Decimal,
        tier: str,
    ) -> Tuple[Decimal, Decimal]:
        """Calculate price for normalized units."""
        pricing = self._pricing.get(category)
        if not pricing:
            return Decimal("0"), Decimal("0")
        
        # Get base price for tier
        base_price = pricing.tier_pricing.get(tier, pricing.base_price)
        
        # Apply type multiplier
        if unit_type == UnitType.PREMIUM:
            base_price = base_price * pricing.premium_multiplier
        elif unit_type == UnitType.PENALTY:
            base_price = base_price * pricing.penalty_multiplier
        elif unit_type == UnitType.CREDIT:
            base_price = base_price * pricing.credit_rate * Decimal("-1")  # Negative for credit
        elif unit_type == UnitType.EXEMPT:
            base_price = Decimal("0")
        
        # Apply volume discount
        if pricing.volume_tiers:
            for threshold, discount in sorted(pricing.volume_tiers, key=lambda x: x[0], reverse=True):
                if quantity >= threshold:
                    base_price = base_price * discount
                    break
        
        total = quantity * base_price
        
        return base_price, total
    
    # =========================================================================
    # Rule Management
    # =========================================================================
    
    def add_rule(self, rule: ConversionRule) -> None:
        """Add or update a conversion rule."""
        self._rules[rule.source_metric] = rule
    
    def remove_rule(self, source_metric: str) -> None:
        """Remove a conversion rule."""
        self._rules.pop(source_metric, None)
    
    def get_rule(self, source_metric: str) -> Optional[ConversionRule]:
        """Get a conversion rule."""
        return self._rules.get(source_metric)
    
    def list_rules(self) -> List[ConversionRule]:
        """List all conversion rules."""
        return list(self._rules.values())
    
    # =========================================================================
    # Pricing Management
    # =========================================================================
    
    def set_pricing(self, category: UnitCategory, pricing: UnitPricing) -> None:
        """Set pricing for a unit category."""
        self._pricing[category] = pricing
    
    def get_pricing(self, category: UnitCategory) -> Optional[UnitPricing]:
        """Get pricing for a unit category."""
        return self._pricing.get(category)
    
    # =========================================================================
    # Status
    # =========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get normalizer status."""
        return {
            "rules_count": len(self._rules),
            "pricing_categories": len(self._pricing),
            "units_generated": self._unit_counter,
            "rules_by_type": self._count_rules_by_type(),
        }
    
    def _count_rules_by_type(self) -> Dict[str, int]:
        """Count rules by unit type."""
        counts: Dict[str, int] = {}
        for rule in self._rules.values():
            unit_type = rule.unit_type.value
            counts[unit_type] = counts.get(unit_type, 0) + 1
        return counts


# =============================================================================
# Unit Aggregator
# =============================================================================

class UnitAggregator:
    """
    Aggregates normalized units for billing periods.
    
    Provides rollups by category, type, and time period.
    """
    
    def __init__(self):
        self._units: Dict[str, List[NormalizedUnit]] = {}  # tenant_id -> units
    
    def add_unit(self, unit: NormalizedUnit) -> None:
        """Add a unit to the aggregator."""
        if unit.tenant_id not in self._units:
            self._units[unit.tenant_id] = []
        self._units[unit.tenant_id].append(unit)
    
    def add_units(self, units: List[NormalizedUnit]) -> None:
        """Add multiple units."""
        for unit in units:
            self.add_unit(unit)
    
    def get_tenant_total(self, tenant_id: str) -> Decimal:
        """Get total billable value for a tenant."""
        units = self._units.get(tenant_id, [])
        return sum((u.total_value for u in units), Decimal("0"))
    
    def get_tenant_breakdown(
        self,
        tenant_id: str,
    ) -> Dict[str, Dict[str, Decimal]]:
        """Get breakdown by category and type for a tenant."""
        units = self._units.get(tenant_id, [])
        
        breakdown: Dict[str, Dict[str, Decimal]] = {}
        
        for unit in units:
            category = unit.category.value
            unit_type = unit.unit_type.value
            
            if category not in breakdown:
                breakdown[category] = {}
            
            if unit_type not in breakdown[category]:
                breakdown[category][unit_type] = Decimal("0")
            
            breakdown[category][unit_type] += unit.total_value
        
        return breakdown
    
    def get_type_totals(self, tenant_id: str) -> Dict[str, Decimal]:
        """Get totals by unit type for a tenant."""
        units = self._units.get(tenant_id, [])
        
        totals: Dict[str, Decimal] = {
            "billable": Decimal("0"),
            "penalty": Decimal("0"),
            "premium": Decimal("0"),
            "credit": Decimal("0"),
            "exempt": Decimal("0"),
        }
        
        for unit in units:
            totals[unit.unit_type.value] += unit.total_value
        
        return totals
    
    def clear_tenant(self, tenant_id: str) -> None:
        """Clear units for a tenant."""
        self._units.pop(tenant_id, None)
    
    def clear_all(self) -> None:
        """Clear all units."""
        self._units.clear()


# =============================================================================
# Factory Functions
# =============================================================================

def create_unit_normalizer(
    rules: Optional[List[ConversionRule]] = None,
    pricing: Optional[Dict[UnitCategory, UnitPricing]] = None,
) -> UnitNormalizer:
    """Create a unit normalizer."""
    return UnitNormalizer(rules, pricing)


def create_unit_aggregator() -> UnitAggregator:
    """Create a unit aggregator."""
    return UnitAggregator()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "UnitType",
    "UnitCategory",
    "ConversionStrategy",
    # Data Classes
    "ConversionRule",
    "NormalizedUnit",
    "UnitPricing",
    "NormalizationResult",
    # Constants
    "DEFAULT_CONVERSION_RULES",
    "DEFAULT_UNIT_PRICING",
    # Classes
    "UnitNormalizer",
    "UnitAggregator",
    # Factories
    "create_unit_normalizer",
    "create_unit_aggregator",
]
