"""
Hardened Stripe Metadata Writer - DEPRECATED

⚠️ DEPRECATION WARNING (Dec 2025):
This module has been moved to krl-premium-backend.
Import from: app.services.billing.stripe_metadata

This stub remains for backward compatibility but will be removed in v2.0.
"""

import warnings
warnings.warn(
    "krl_data_connectors.core.billing.stripe_metadata is deprecated. "
    "This module has moved to krl-premium-backend. "
    "Import from 'app.services.billing.stripe_metadata' instead.",
    DeprecationWarning,
    stacklevel=2
)

from dataclasses import dataclass, field
from datetime import datetime, UTC
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Optional
import hashlib
import json
import logging
import re

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

# Stripe limits
MAX_METADATA_KEYS = 50
MAX_KEY_LENGTH = 40
MAX_VALUE_LENGTH = 500

# Current schema version for migrations
METADATA_SCHEMA_VERSION = "v2"


class MetadataCategory(Enum):
    """Categories of metadata for organization."""
    IDENTITY = "identity"       # Tenant/customer identifiers
    TIER = "tier"               # Subscription tier info
    CONTRACT = "contract"       # Contract details
    HEALTH = "health"           # Health scores
    USAGE = "usage"             # Usage metrics
    SEGMENT = "segment"         # Customer segmentation
    EXPERIMENT = "experiment"   # A/B test assignments
    AUDIT = "audit"             # Timestamps and versions


@dataclass
class MetadataField:
    """Definition of an allowed metadata field."""
    key: str
    category: MetadataCategory
    description: str
    required: bool = False
    obfuscate: bool = False  # Hash the value
    max_length: int = MAX_VALUE_LENGTH
    validator: Optional[Callable[[Any], bool]] = None
    transformer: Optional[Callable[[Any], str]] = None


# =============================================================================
# Allowed Metadata Fields (Whitelist)
# =============================================================================

ALLOWED_METADATA_FIELDS: dict[str, MetadataField] = {
    # Identity (no PII - use IDs only)
    "krl_tenant_id": MetadataField(
        key="krl_tenant_id",
        category=MetadataCategory.IDENTITY,
        description="Internal tenant UUID",
        required=True,
        max_length=40,
    ),
    "krl_schema_version": MetadataField(
        key="krl_schema_version",
        category=MetadataCategory.AUDIT,
        description="Metadata schema version for migrations",
        required=True,
    ),
    
    # Tier & Pricing
    "krl_tier": MetadataField(
        key="krl_tier",
        category=MetadataCategory.TIER,
        description="Current subscription tier",
        required=True,
        validator=lambda v: v in {"community", "professional", "team", "enterprise", "custom"},
    ),
    "krl_tier_effective_date": MetadataField(
        key="krl_tier_effective_date",
        category=MetadataCategory.TIER,
        description="When tier became effective (ISO date)",
    ),
    "krl_price_id": MetadataField(
        key="krl_price_id",
        category=MetadataCategory.TIER,
        description="Stripe price ID for current tier",
    ),
    
    # Contract
    "krl_contract_id": MetadataField(
        key="krl_contract_id",
        category=MetadataCategory.CONTRACT,
        description="Internal contract UUID",
    ),
    "krl_contract_type": MetadataField(
        key="krl_contract_type",
        category=MetadataCategory.CONTRACT,
        description="Contract commitment type",
        validator=lambda v: v in {"monthly", "annual", "multi_year_2", "multi_year_3", "enterprise"},
    ),
    "krl_contract_status": MetadataField(
        key="krl_contract_status",
        category=MetadataCategory.CONTRACT,
        description="Contract lifecycle status",
    ),
    "krl_contract_end_date": MetadataField(
        key="krl_contract_end_date",
        category=MetadataCategory.CONTRACT,
        description="Contract end date (ISO date)",
    ),
    "krl_discount_bps": MetadataField(
        key="krl_discount_bps",
        category=MetadataCategory.CONTRACT,
        description="Total discount in basis points",
        transformer=lambda v: str(int(v)),
    ),
    "krl_sla_tier": MetadataField(
        key="krl_sla_tier",
        category=MetadataCategory.CONTRACT,
        description="SLA tier level",
    ),
    
    # Customer Segment
    "krl_segment": MetadataField(
        key="krl_segment",
        category=MetadataCategory.SEGMENT,
        description="Primary customer segment",
    ),
    "krl_industry": MetadataField(
        key="krl_industry",
        category=MetadataCategory.SEGMENT,
        description="Industry vertical",
    ),
    "krl_size_tier": MetadataField(
        key="krl_size_tier",
        category=MetadataCategory.SEGMENT,
        description="Company size tier",
    ),
    "krl_expansion_score": MetadataField(
        key="krl_expansion_score",
        category=MetadataCategory.SEGMENT,
        description="Expansion potential (0-100)",
        transformer=lambda v: str(int(min(100, max(0, float(v))))),
    ),
    
    # Health Scores
    "krl_health_score": MetadataField(
        key="krl_health_score",
        category=MetadataCategory.HEALTH,
        description="Overall health score (0-100)",
        transformer=lambda v: str(int(min(100, max(0, float(v))))),
    ),
    "krl_health_category": MetadataField(
        key="krl_health_category",
        category=MetadataCategory.HEALTH,
        description="Health category",
        validator=lambda v: v in {"critical", "at_risk", "healthy", "champion"},
    ),
    "krl_churn_risk": MetadataField(
        key="krl_churn_risk",
        category=MetadataCategory.HEALTH,
        description="Churn risk level",
        validator=lambda v: v in {"low", "medium", "high", "critical"},
    ),
    "krl_churn_prob_pct": MetadataField(
        key="krl_churn_prob_pct",
        category=MetadataCategory.HEALTH,
        description="Churn probability percentage (0-100)",
        transformer=lambda v: str(int(min(100, max(0, float(v) * 100)))),
    ),
    "krl_health_updated": MetadataField(
        key="krl_health_updated",
        category=MetadataCategory.HEALTH,
        description="Last health score update (ISO date)",
    ),
    
    # Usage Metrics (aggregated, not raw)
    "krl_usage_tier": MetadataField(
        key="krl_usage_tier",
        category=MetadataCategory.USAGE,
        description="Usage tier (low, medium, high, very_high)",
    ),
    "krl_api_calls_bucket": MetadataField(
        key="krl_api_calls_bucket",
        category=MetadataCategory.USAGE,
        description="API usage bucket (1k, 10k, 100k, 1m)",
    ),
    "krl_active_users_bucket": MetadataField(
        key="krl_active_users_bucket",
        category=MetadataCategory.USAGE,
        description="Active users bucket (1-5, 6-20, 21-100, 100+)",
    ),
    "krl_feature_adoption_pct": MetadataField(
        key="krl_feature_adoption_pct",
        category=MetadataCategory.USAGE,
        description="Feature adoption percentage",
        transformer=lambda v: str(int(min(100, max(0, float(v))))),
    ),
    
    # Experiment Assignments
    "krl_experiment_id": MetadataField(
        key="krl_experiment_id",
        category=MetadataCategory.EXPERIMENT,
        description="Current experiment ID (if enrolled)",
    ),
    "krl_experiment_variant": MetadataField(
        key="krl_experiment_variant",
        category=MetadataCategory.EXPERIMENT,
        description="Experiment variant assignment",
    ),
    
    # Audit Timestamps
    "krl_created_at": MetadataField(
        key="krl_created_at",
        category=MetadataCategory.AUDIT,
        description="Record creation timestamp",
    ),
    "krl_updated_at": MetadataField(
        key="krl_updated_at",
        category=MetadataCategory.AUDIT,
        description="Last update timestamp",
    ),
}


# =============================================================================
# PII Detection Patterns
# =============================================================================

PII_PATTERNS = [
    (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', "email"),
    (r'\b(?:\d{3}[-.]?\d{3}[-.]?\d{4})\b', "phone"),
    (r'\b(?:sk_live_|sk_test_|pk_live_|pk_test_)[a-zA-Z0-9]+\b', "stripe_key"),
    (r'\b(?:api[_-]?key|secret|password|token)[_-]?\w*[:=]\s*\S+', "secret"),
    (r'\b\d{3}[-]?\d{2}[-]?\d{4}\b', "ssn"),
    (r'\b(?:\d{4}[-\s]?){4}\b', "credit_card"),
]


# =============================================================================
# Hardened Metadata Writer
# =============================================================================

class StripeMetadataWriter:
    """
    Hardened Stripe metadata writer with security and validation.
    
    Features:
    - Whitelist enforcement (only allowed keys)
    - PII detection and blocking
    - Value obfuscation for sensitive data
    - Size limit enforcement
    - Schema versioning
    - Audit logging
    """
    
    def __init__(
        self,
        strict_mode: bool = True,
        audit_logger: Optional[Callable[[dict], None]] = None,
    ):
        """
        Initialize the metadata writer.
        
        Args:
            strict_mode: If True, reject unknown keys. If False, skip them with warning.
            audit_logger: Optional callback to log metadata changes.
        """
        self.strict_mode = strict_mode
        self.audit_logger = audit_logger
        self._compiled_pii_patterns = [
            (re.compile(pattern, re.IGNORECASE), name)
            for pattern, name in PII_PATTERNS
        ]
    
    def write_metadata(
        self,
        data: dict[str, Any],
        entity_type: str = "subscription",
        entity_id: Optional[str] = None,
    ) -> dict[str, str]:
        """
        Validate and transform data into safe Stripe metadata.
        
        Args:
            data: Raw metadata dict (key -> value)
            entity_type: What Stripe entity this is for (customer, subscription, etc.)
            entity_id: ID of the entity being updated (for audit logging)
            
        Returns:
            Safe metadata dict ready for Stripe API
            
        Raises:
            ValueError: If strict mode and unknown key, or PII detected
        """
        result: dict[str, str] = {}
        errors: list[str] = []
        warnings: list[str] = []
        
        # Always add schema version
        result["krl_schema_version"] = METADATA_SCHEMA_VERSION
        
        for key, value in data.items():
            try:
                safe_key, safe_value = self._process_field(key, value)
                if safe_key and safe_value is not None:
                    result[safe_key] = safe_value
            except ValueError as e:
                if self.strict_mode:
                    errors.append(str(e))
                else:
                    warnings.append(str(e))
        
        # Validate total size
        if len(result) > MAX_METADATA_KEYS:
            raise ValueError(
                f"Metadata exceeds {MAX_METADATA_KEYS} key limit: {len(result)} keys"
            )
        
        # Check for required fields
        for key, field_def in ALLOWED_METADATA_FIELDS.items():
            if field_def.required and key not in result:
                errors.append(f"Required field missing: {key}")
        
        # Raise accumulated errors
        if errors:
            raise ValueError(f"Metadata validation failed: {'; '.join(errors)}")
        
        # Log warnings
        for warning in warnings:
            logger.warning(f"Metadata warning: {warning}")
        
        # Audit log
        if self.audit_logger:
            self.audit_logger({
                "action": "write_metadata",
                "entity_type": entity_type,
                "entity_id": entity_id,
                "keys_written": list(result.keys()),
                "timestamp": datetime.now(UTC).isoformat(),
            })
        
        return result
    
    def _process_field(
        self, key: str, value: Any
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Process a single metadata field.
        
        Returns:
            Tuple of (safe_key, safe_value) or (None, None) if should skip
        """
        # Check if key is allowed
        field_def = ALLOWED_METADATA_FIELDS.get(key)
        if field_def is None:
            raise ValueError(f"Unknown metadata key: {key}")
        
        # Handle None values
        if value is None:
            return None, None
        
        # Convert to string
        str_value = self._to_string(value)
        
        # Check for PII
        pii_type = self._detect_pii(str_value)
        if pii_type:
            raise ValueError(
                f"PII detected in field {key}: {pii_type}. "
                "Remove sensitive data or use ID references."
            )
        
        # Apply transformer if defined
        if field_def.transformer:
            try:
                str_value = field_def.transformer(value)
            except Exception as e:
                raise ValueError(f"Transform failed for {key}: {e}")
        
        # Validate
        if field_def.validator and not field_def.validator(str_value):
            raise ValueError(f"Validation failed for {key}: {str_value}")
        
        # Obfuscate if needed
        if field_def.obfuscate:
            str_value = self._hash_value(str_value)
        
        # Enforce length limits
        if len(str_value) > field_def.max_length:
            str_value = str_value[:field_def.max_length - 3] + "..."
        
        # Validate key length
        if len(key) > MAX_KEY_LENGTH:
            raise ValueError(f"Key too long: {key} ({len(key)} > {MAX_KEY_LENGTH})")
        
        return key, str_value
    
    def _to_string(self, value: Any) -> str:
        """Convert value to string representation."""
        if isinstance(value, str):
            return value
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (int, float, Decimal)):
            return str(value)
        elif isinstance(value, datetime):
            return value.isoformat()[:19]  # Truncate microseconds
        elif isinstance(value, Enum):
            return value.value
        elif isinstance(value, (list, dict)):
            # Compact JSON for complex types
            return json.dumps(value, separators=(',', ':'))[:MAX_VALUE_LENGTH]
        else:
            return str(value)[:MAX_VALUE_LENGTH]
    
    def _detect_pii(self, value: str) -> Optional[str]:
        """Check if value contains PII patterns."""
        for pattern, pii_type in self._compiled_pii_patterns:
            if pattern.search(value):
                return pii_type
        return None
    
    def _hash_value(self, value: str, prefix_length: int = 8) -> str:
        """
        Hash a value for obfuscation while keeping prefix for debugging.
        
        Returns: "{prefix}...{hash_suffix}"
        """
        hash_suffix = hashlib.sha256(value.encode()).hexdigest()[:8]
        if len(value) > prefix_length:
            return f"{value[:prefix_length]}...{hash_suffix}"
        return f"{value}_{hash_suffix}"


# =============================================================================
# Convenience Functions
# =============================================================================

def create_safe_customer_metadata(
    tenant_id: str,
    tier: str,
    segment: Optional[str] = None,
    contract_type: Optional[str] = None,
    health_score: Optional[float] = None,
    churn_risk: Optional[str] = None,
) -> dict[str, str]:
    """
    Create safe metadata for a Stripe customer.
    
    Args:
        tenant_id: Internal tenant UUID
        tier: Subscription tier
        segment: Customer segment
        contract_type: Contract type
        health_score: Health score (0-100)
        churn_risk: Churn risk level
        
    Returns:
        Validated metadata dict
    """
    writer = StripeMetadataWriter(strict_mode=False)
    
    data = {
        "krl_tenant_id": tenant_id,
        "krl_tier": tier,
        "krl_updated_at": datetime.now(UTC).isoformat()[:19],
    }
    
    if segment:
        data["krl_segment"] = segment
    if contract_type:
        data["krl_contract_type"] = contract_type
    if health_score is not None:
        data["krl_health_score"] = health_score
    if churn_risk:
        data["krl_churn_risk"] = churn_risk
    
    return writer.write_metadata(data, entity_type="customer")


def create_safe_subscription_metadata(
    tenant_id: str,
    tier: str,
    contract_id: Optional[str] = None,
    contract_end_date: Optional[str] = None,
    discount_bps: int = 0,
    experiment_id: Optional[str] = None,
    experiment_variant: Optional[str] = None,
) -> dict[str, str]:
    """
    Create safe metadata for a Stripe subscription.
    
    Args:
        tenant_id: Internal tenant UUID
        tier: Subscription tier
        contract_id: Contract UUID
        contract_end_date: Contract end date (ISO format)
        discount_bps: Total discount in basis points
        experiment_id: A/B test experiment ID
        experiment_variant: Experiment variant assignment
        
    Returns:
        Validated metadata dict
    """
    writer = StripeMetadataWriter(strict_mode=False)
    
    data = {
        "krl_tenant_id": tenant_id,
        "krl_tier": tier,
        "krl_updated_at": datetime.now(UTC).isoformat()[:19],
    }
    
    if contract_id:
        data["krl_contract_id"] = contract_id
    if contract_end_date:
        data["krl_contract_end_date"] = contract_end_date
    if discount_bps:
        data["krl_discount_bps"] = discount_bps
    if experiment_id:
        data["krl_experiment_id"] = experiment_id
        data["krl_experiment_variant"] = experiment_variant or "control"
    
    return writer.write_metadata(data, entity_type="subscription")


def validate_existing_metadata(metadata: dict[str, str]) -> tuple[bool, list[str]]:
    """
    Validate existing Stripe metadata for compliance.
    
    Args:
        metadata: Existing metadata from Stripe
        
    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []
    writer = StripeMetadataWriter(strict_mode=False)
    
    for key, value in metadata.items():
        # Check if key is in our schema
        if key.startswith("krl_") and key not in ALLOWED_METADATA_FIELDS:
            issues.append(f"Unknown KRL key: {key}")
        
        # Check for PII
        pii_type = writer._detect_pii(str(value))
        if pii_type:
            issues.append(f"PII ({pii_type}) found in {key}")
    
    # Check schema version
    if metadata.get("krl_schema_version") != METADATA_SCHEMA_VERSION:
        issues.append(
            f"Schema version mismatch: {metadata.get('krl_schema_version')} "
            f"vs {METADATA_SCHEMA_VERSION}"
        )
    
    return len(issues) == 0, issues


# =============================================================================
# Usage Bucketing Functions
# =============================================================================

def bucket_api_calls(calls: int) -> str:
    """Convert raw API call count to privacy-safe bucket."""
    if calls < 1000:
        return "1k"
    elif calls < 10000:
        return "10k"
    elif calls < 100000:
        return "100k"
    elif calls < 1000000:
        return "1m"
    else:
        return "1m+"


def bucket_active_users(users: int) -> str:
    """Convert raw user count to privacy-safe bucket."""
    if users <= 5:
        return "1-5"
    elif users <= 20:
        return "6-20"
    elif users <= 100:
        return "21-100"
    else:
        return "100+"


def bucket_revenue(revenue: float) -> str:
    """Convert revenue to privacy-safe bucket."""
    if revenue < 1000000:
        return "under_1m"
    elif revenue < 10000000:
        return "1m_10m"
    elif revenue < 100000000:
        return "10m_100m"
    else:
        return "100m_plus"


__all__ = [
    "StripeMetadataWriter",
    "MetadataField",
    "MetadataCategory",
    "ALLOWED_METADATA_FIELDS",
    "METADATA_SCHEMA_VERSION",
    "create_safe_customer_metadata",
    "create_safe_subscription_metadata",
    "validate_existing_metadata",
    "bucket_api_calls",
    "bucket_active_users",
    "bucket_revenue",
]
