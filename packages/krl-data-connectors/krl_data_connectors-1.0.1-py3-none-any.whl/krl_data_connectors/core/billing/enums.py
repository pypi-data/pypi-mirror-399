"""
Centralized Billing Enums - Re-exports from krl-types.

MIGRATION NOTE (Phase 1 Complete - Dec 2025):
All billing enums are now sourced from the krl-types package.
This module re-exports them for backward compatibility.

Usage:
    # Preferred (direct from krl-types):
    from krl_types.billing import Tier, CustomerSegment, ContractType
    
    # Legacy (still works, but deprecated):
    from krl_data_connectors.core.billing.enums import (
        Tier, CustomerSegment, ContractType, ...
    )
"""

# Re-export all enums from krl-types for backward compatibility
from krl_types.billing.enums import (
    # Core
    Tier,
    CustomerSegment,
    # Contracts
    ContractType,
    ContractStatus,
    PaymentTerms,
    # Credits & Usage
    CreditType,
    UsageMetricType,
    # Health & Risk
    HealthCategory,
    ChurnRisk,
    InterventionType,
    # Pricing & Experiments
    PricingStrategy,
    ExperimentStatus,
    ExperimentType,
    ValueDriver,
    # Audit
    AuditAction,
    ActorType,
    # Stripe
    StripeSyncStatus,
    StripeEntityType,
    # Deprecated aliases
    KRLTier,
    BillingTier,
    PricingTier,
)

import warnings

# Issue deprecation warning when this module is imported directly
warnings.warn(
    "Importing from krl_data_connectors.core.billing.enums is deprecated. "
    "Use 'from krl_types.billing import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)


# =============================================================================
# Exports (all re-exported from krl-types)
# =============================================================================

__all__ = [
    # Core
    "Tier",
    "CustomerSegment",
    # Contracts
    "ContractType",
    "ContractStatus",
    "PaymentTerms",
    # Credits & Usage
    "CreditType",
    "UsageMetricType",
    # Health & Risk
    "HealthCategory",
    "ChurnRisk",
    "InterventionType",
    # Pricing & Experiments
    "PricingStrategy",
    "ExperimentStatus",
    "ExperimentType",
    "ValueDriver",
    # Audit
    "AuditAction",
    "ActorType",
    # Stripe
    "StripeSyncStatus",
    "StripeEntityType",
    # Deprecated aliases
    "KRLTier",
    "BillingTier",
    "PricingTier",
]
