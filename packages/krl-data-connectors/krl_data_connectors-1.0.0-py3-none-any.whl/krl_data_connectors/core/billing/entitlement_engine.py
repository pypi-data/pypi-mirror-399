"""
SaaS Entitlement Engine - DEPRECATED

⚠️ DEPRECATION WARNING (Dec 2025):
This module has been moved to krl-premium-backend.
Import from: app.services.billing.entitlement_engine

This stub remains for backward compatibility but will be removed in v2.0.
"""

from __future__ import annotations

import warnings
warnings.warn(
    "krl_data_connectors.core.billing.entitlement_engine is deprecated. "
    "This module has moved to krl-premium-backend. "
    "Import from 'app.services.billing.entitlement_engine' instead.",
    DeprecationWarning,
    stacklevel=2
)

import hashlib
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set


class EntitlementType(Enum):
    """Types of entitlements."""
    
    FEATURE = "feature"  # Boolean feature access
    QUOTA = "quota"  # Numeric limit
    TIER = "tier"  # Subscription tier level
    ADDON = "addon"  # Purchased add-on
    TRIAL = "trial"  # Time-limited trial
    BETA = "beta"  # Beta feature access
    CUSTOM = "custom"  # Custom enterprise entitlement


class FeatureFlagState(Enum):
    """Feature flag states."""
    
    ENABLED = "enabled"
    DISABLED = "disabled"
    PERCENTAGE = "percentage"  # Gradual rollout
    SEGMENT = "segment"  # Specific segments only
    EXPERIMENT = "experiment"  # A/B test


class TierLevel(Enum):
    """Subscription tier levels."""
    
    FREE = 0
    STARTER = 1
    PROFESSIONAL = 2
    BUSINESS = 3
    ENTERPRISE = 4
    CUSTOM = 5


@dataclass
class FeatureFlag:
    """Feature flag definition."""
    
    flag_id: str
    name: str
    description: str
    state: FeatureFlagState
    minimum_tier: TierLevel
    enabled_for_tiers: Set[TierLevel] = field(default_factory=set)
    rollout_percentage: float = 100.0  # For gradual rollout
    enabled_segments: List[str] = field(default_factory=list)
    experiment_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class EntitlementGrant:
    """An entitlement granted to a tenant."""
    
    grant_id: str
    tenant_id: str
    entitlement_type: EntitlementType
    resource_id: str  # Feature flag ID, quota name, etc.
    value: Any  # True/False for features, number for quotas
    source: str  # subscription, addon, promotion, etc.
    expires_at: Optional[datetime] = None
    granted_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        """Check if grant has expired."""
        if self.expires_at is None:
            return False
        return datetime.now(UTC) > self.expires_at


@dataclass
class EntitlementCheckResult:
    """Result of an entitlement check."""
    
    entitled: bool
    reason: str
    grant: Optional[EntitlementGrant] = None
    fallback_used: bool = False
    cached: bool = False
    check_latency_ms: float = 0.0


@dataclass
class ConnectAccountMapping:
    """Maps Stripe Connect account to entitlements."""
    
    connect_account_id: str
    tenant_id: str
    account_type: str  # standard, express, custom
    tier: TierLevel
    active_subscription_id: Optional[str] = None
    addons: List[str] = field(default_factory=list)
    custom_entitlements: Dict[str, Any] = field(default_factory=dict)
    onboarding_complete: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class EntitlementCache:
    """
    High-performance entitlement cache with TTL.
    
    Reduces database/API calls for frequent entitlement checks.
    """

    def __init__(
        self,
        default_ttl_seconds: int = 60,
        max_entries: int = 10000,
    ):
        self.default_ttl = default_ttl_seconds
        self.max_entries = max_entries
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_order: List[str] = []

    def _make_key(self, tenant_id: str, resource_id: str) -> str:
        """Create cache key."""
        return f"{tenant_id}:{resource_id}"

    def get(
        self,
        tenant_id: str,
        resource_id: str,
    ) -> Optional[EntitlementCheckResult]:
        """Get cached entitlement check result."""
        key = self._make_key(tenant_id, resource_id)
        entry = self._cache.get(key)
        
        if entry is None:
            return None
        
        # Check expiration
        if time.time() > entry["expires_at"]:
            del self._cache[key]
            return None
        
        # Update access order for LRU
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
        
        result = entry["result"]
        result.cached = True
        return result

    def set(
        self,
        tenant_id: str,
        resource_id: str,
        result: EntitlementCheckResult,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """Cache entitlement check result."""
        key = self._make_key(tenant_id, resource_id)
        ttl = ttl_seconds or self.default_ttl
        
        # Evict if at capacity
        while len(self._cache) >= self.max_entries and self._access_order:
            oldest_key = self._access_order.pop(0)
            self._cache.pop(oldest_key, None)
        
        self._cache[key] = {
            "result": result,
            "expires_at": time.time() + ttl,
        }
        self._access_order.append(key)

    def invalidate(self, tenant_id: str, resource_id: Optional[str] = None) -> int:
        """Invalidate cache entries for a tenant."""
        invalidated = 0
        prefix = f"{tenant_id}:"
        
        keys_to_remove = []
        for key in self._cache:
            if resource_id:
                if key == self._make_key(tenant_id, resource_id):
                    keys_to_remove.append(key)
            elif key.startswith(prefix):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
            invalidated += 1
        
        return invalidated

    def clear(self) -> None:
        """Clear entire cache."""
        self._cache.clear()
        self._access_order.clear()

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "entries": len(self._cache),
            "max_entries": self.max_entries,
            "default_ttl": self.default_ttl,
        }


class FeatureFlagManager:
    """
    Manages feature flags and their states.
    
    Supports gradual rollouts, A/B testing, and segment targeting.
    """

    def __init__(self):
        self._flags: Dict[str, FeatureFlag] = {}
        self._tier_defaults: Dict[TierLevel, Set[str]] = {
            tier: set() for tier in TierLevel
        }

    def register_flag(self, flag: FeatureFlag) -> None:
        """Register a feature flag."""
        self._flags[flag.flag_id] = flag
        
        # Update tier defaults
        if flag.enabled_for_tiers:
            for tier in flag.enabled_for_tiers:
                self._tier_defaults[tier].add(flag.flag_id)
        elif flag.minimum_tier:
            # Enable for all tiers at or above minimum
            for tier in TierLevel:
                if tier.value >= flag.minimum_tier.value:
                    self._tier_defaults[tier].add(flag.flag_id)

    def get_flag(self, flag_id: str) -> Optional[FeatureFlag]:
        """Get a feature flag by ID."""
        return self._flags.get(flag_id)

    def evaluate_flag(
        self,
        flag_id: str,
        tenant_id: str,
        tier: TierLevel,
        segment: Optional[str] = None,
    ) -> bool:
        """Evaluate if a flag is enabled for a tenant."""
        flag = self._flags.get(flag_id)
        if flag is None:
            return False
        
        # Check state
        if flag.state == FeatureFlagState.DISABLED:
            return False
        
        if flag.state == FeatureFlagState.ENABLED:
            # Check tier access
            if flag.enabled_for_tiers:
                return tier in flag.enabled_for_tiers
            return tier.value >= flag.minimum_tier.value
        
        if flag.state == FeatureFlagState.SEGMENT:
            # Check if tenant is in enabled segment
            return segment in flag.enabled_segments if segment else False
        
        if flag.state == FeatureFlagState.PERCENTAGE:
            # Deterministic rollout based on tenant_id hash
            return self._in_rollout_percentage(
                tenant_id, flag_id, flag.rollout_percentage
            )
        
        if flag.state == FeatureFlagState.EXPERIMENT:
            # A/B test - deterministic variant assignment
            return self._get_experiment_variant(
                tenant_id, flag.experiment_id or flag_id
            ) == "treatment"
        
        return False

    def _in_rollout_percentage(
        self,
        tenant_id: str,
        flag_id: str,
        percentage: float,
    ) -> bool:
        """Check if tenant falls within rollout percentage."""
        hash_input = f"{tenant_id}:{flag_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        bucket = hash_value % 100
        return bucket < percentage

    def _get_experiment_variant(
        self,
        tenant_id: str,
        experiment_id: str,
    ) -> str:
        """Get deterministic experiment variant for tenant."""
        hash_input = f"{tenant_id}:{experiment_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        return "treatment" if hash_value % 2 == 0 else "control"

    def get_flags_for_tier(self, tier: TierLevel) -> Set[str]:
        """Get all flags enabled for a tier."""
        return self._tier_defaults.get(tier, set()).copy()

    def update_flag_state(
        self,
        flag_id: str,
        state: FeatureFlagState,
        **kwargs: Any,
    ) -> bool:
        """Update a flag's state."""
        flag = self._flags.get(flag_id)
        if flag is None:
            return False
        
        flag.state = state
        flag.updated_at = datetime.now(UTC)
        
        if "rollout_percentage" in kwargs:
            flag.rollout_percentage = kwargs["rollout_percentage"]
        if "enabled_segments" in kwargs:
            flag.enabled_segments = kwargs["enabled_segments"]
        if "experiment_id" in kwargs:
            flag.experiment_id = kwargs["experiment_id"]
        
        return True


class SaaSEntitlementEngine:
    """
    Main entitlement engine connecting Stripe Connect to feature flags.
    
    Provides real-time entitlement checks with caching, handles
    subscription changes, and manages custom enterprise entitlements.
    """

    def __init__(
        self,
        cache_ttl_seconds: int = 60,
        cache_max_entries: int = 10000,
    ):
        self.cache = EntitlementCache(
            default_ttl_seconds=cache_ttl_seconds,
            max_entries=cache_max_entries,
        )
        self.flag_manager = FeatureFlagManager()
        self._account_mappings: Dict[str, ConnectAccountMapping] = {}
        self._tenant_grants: Dict[str, List[EntitlementGrant]] = {}
        self._hooks: Dict[str, List[Callable]] = {
            "entitlement_granted": [],
            "entitlement_revoked": [],
            "check_performed": [],
        }

    def register_hook(
        self,
        event: str,
        callback: Callable,
    ) -> None:
        """Register a hook for entitlement events."""
        if event in self._hooks:
            self._hooks[event].append(callback)

    def _emit_event(self, event: str, **kwargs: Any) -> None:
        """Emit an event to registered hooks."""
        for callback in self._hooks.get(event, []):
            try:
                callback(**kwargs)
            except Exception:
                pass  # Don't let hook errors affect engine

    def register_connect_account(
        self,
        connect_account_id: str,
        tenant_id: str,
        account_type: str,
        tier: TierLevel,
        subscription_id: Optional[str] = None,
        addons: Optional[List[str]] = None,
    ) -> ConnectAccountMapping:
        """Register a Stripe Connect account mapping."""
        mapping = ConnectAccountMapping(
            connect_account_id=connect_account_id,
            tenant_id=tenant_id,
            account_type=account_type,
            tier=tier,
            active_subscription_id=subscription_id,
            addons=addons or [],
        )
        self._account_mappings[connect_account_id] = mapping
        
        # Grant tier-based entitlements
        self._apply_tier_entitlements(tenant_id, tier)
        
        return mapping

    def _apply_tier_entitlements(
        self,
        tenant_id: str,
        tier: TierLevel,
    ) -> None:
        """Apply all entitlements for a subscription tier."""
        # Get all flags for this tier
        tier_flags = self.flag_manager.get_flags_for_tier(tier)
        
        for flag_id in tier_flags:
            grant = EntitlementGrant(
                grant_id=f"{tenant_id}:{flag_id}:tier",
                tenant_id=tenant_id,
                entitlement_type=EntitlementType.FEATURE,
                resource_id=flag_id,
                value=True,
                source=f"subscription_tier:{tier.name}",
            )
            self._add_grant(grant)

    def _add_grant(self, grant: EntitlementGrant) -> None:
        """Add an entitlement grant."""
        if grant.tenant_id not in self._tenant_grants:
            self._tenant_grants[grant.tenant_id] = []
        
        # Remove existing grant for same resource
        self._tenant_grants[grant.tenant_id] = [
            g for g in self._tenant_grants[grant.tenant_id]
            if g.resource_id != grant.resource_id
        ]
        
        self._tenant_grants[grant.tenant_id].append(grant)
        
        # Invalidate cache
        self.cache.invalidate(grant.tenant_id, grant.resource_id)
        
        self._emit_event(
            "entitlement_granted",
            tenant_id=grant.tenant_id,
            grant=grant,
        )

    def grant_entitlement(
        self,
        tenant_id: str,
        entitlement_type: EntitlementType,
        resource_id: str,
        value: Any,
        source: str,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EntitlementGrant:
        """Grant an entitlement to a tenant."""
        grant = EntitlementGrant(
            grant_id=f"{tenant_id}:{resource_id}:{int(time.time())}",
            tenant_id=tenant_id,
            entitlement_type=entitlement_type,
            resource_id=resource_id,
            value=value,
            source=source,
            expires_at=expires_at,
            metadata=metadata or {},
        )
        self._add_grant(grant)
        return grant

    def revoke_entitlement(
        self,
        tenant_id: str,
        resource_id: str,
    ) -> bool:
        """Revoke an entitlement from a tenant."""
        if tenant_id not in self._tenant_grants:
            return False
        
        original_count = len(self._tenant_grants[tenant_id])
        self._tenant_grants[tenant_id] = [
            g for g in self._tenant_grants[tenant_id]
            if g.resource_id != resource_id
        ]
        
        revoked = len(self._tenant_grants[tenant_id]) < original_count
        
        if revoked:
            self.cache.invalidate(tenant_id, resource_id)
            self._emit_event(
                "entitlement_revoked",
                tenant_id=tenant_id,
                resource_id=resource_id,
            )
        
        return revoked

    def check_entitlement(
        self,
        tenant_id: str,
        resource_id: str,
        use_cache: bool = True,
    ) -> EntitlementCheckResult:
        """Check if a tenant has an entitlement."""
        start_time = time.time()
        
        # Check cache first
        if use_cache:
            cached = self.cache.get(tenant_id, resource_id)
            if cached is not None:
                return cached
        
        # Check explicit grants
        grants = self._tenant_grants.get(tenant_id, [])
        for grant in grants:
            if grant.resource_id == resource_id:
                if grant.is_expired:
                    continue
                
                result = EntitlementCheckResult(
                    entitled=bool(grant.value),
                    reason=f"Granted via {grant.source}",
                    grant=grant,
                    check_latency_ms=(time.time() - start_time) * 1000,
                )
                
                if use_cache:
                    self.cache.set(tenant_id, resource_id, result)
                
                self._emit_event(
                    "check_performed",
                    tenant_id=tenant_id,
                    resource_id=resource_id,
                    result=result,
                )
                
                return result
        
        # Check via feature flags (tier-based)
        account = self._get_account_by_tenant(tenant_id)
        if account:
            entitled = self.flag_manager.evaluate_flag(
                resource_id,
                tenant_id,
                account.tier,
            )
            
            result = EntitlementCheckResult(
                entitled=entitled,
                reason=f"Tier-based: {account.tier.name}" if entitled else "Not included in tier",
                fallback_used=True,
                check_latency_ms=(time.time() - start_time) * 1000,
            )
            
            if use_cache:
                self.cache.set(tenant_id, resource_id, result)
            
            self._emit_event(
                "check_performed",
                tenant_id=tenant_id,
                resource_id=resource_id,
                result=result,
            )
            
            return result
        
        # No entitlement found
        result = EntitlementCheckResult(
            entitled=False,
            reason="No entitlement found",
            check_latency_ms=(time.time() - start_time) * 1000,
        )
        
        if use_cache:
            # Cache negative results with shorter TTL
            self.cache.set(tenant_id, resource_id, result, ttl_seconds=30)
        
        return result

    def _get_account_by_tenant(
        self,
        tenant_id: str,
    ) -> Optional[ConnectAccountMapping]:
        """Get Connect account mapping by tenant ID."""
        for mapping in self._account_mappings.values():
            if mapping.tenant_id == tenant_id:
                return mapping
        return None

    def get_tenant_entitlements(
        self,
        tenant_id: str,
    ) -> Dict[str, Any]:
        """Get all entitlements for a tenant."""
        grants = self._tenant_grants.get(tenant_id, [])
        account = self._get_account_by_tenant(tenant_id)
        
        result: Dict[str, Any] = {
            "tenant_id": tenant_id,
            "tier": account.tier.name if account else None,
            "explicit_grants": [],
            "tier_features": [],
            "total_entitlements": 0,
        }
        
        # Explicit grants
        for grant in grants:
            if not grant.is_expired:
                result["explicit_grants"].append({
                    "resource_id": grant.resource_id,
                    "type": grant.entitlement_type.value,
                    "value": grant.value,
                    "source": grant.source,
                    "expires_at": grant.expires_at.isoformat() if grant.expires_at else None,
                })
        
        # Tier-based features
        if account:
            tier_flags = self.flag_manager.get_flags_for_tier(account.tier)
            result["tier_features"] = list(tier_flags)
        
        result["total_entitlements"] = (
            len(result["explicit_grants"]) + len(result["tier_features"])
        )
        
        return result

    def handle_subscription_change(
        self,
        tenant_id: str,
        old_tier: TierLevel,
        new_tier: TierLevel,
    ) -> Dict[str, Any]:
        """Handle subscription tier change."""
        # Get feature differences
        old_features = self.flag_manager.get_flags_for_tier(old_tier)
        new_features = self.flag_manager.get_flags_for_tier(new_tier)
        
        added = new_features - old_features
        removed = old_features - new_features
        
        # Update account mapping
        account = self._get_account_by_tenant(tenant_id)
        if account:
            account.tier = new_tier
        
        # Revoke removed entitlements
        for feature_id in removed:
            self.revoke_entitlement(tenant_id, feature_id)
        
        # Grant new entitlements
        for feature_id in added:
            self.grant_entitlement(
                tenant_id=tenant_id,
                entitlement_type=EntitlementType.FEATURE,
                resource_id=feature_id,
                value=True,
                source=f"subscription_upgrade:{new_tier.name}",
            )
        
        # Invalidate all cached entitlements for tenant
        self.cache.invalidate(tenant_id)
        
        return {
            "tenant_id": tenant_id,
            "old_tier": old_tier.name,
            "new_tier": new_tier.name,
            "features_added": list(added),
            "features_removed": list(removed),
        }

    def grant_trial(
        self,
        tenant_id: str,
        feature_id: str,
        duration_days: int = 14,
    ) -> EntitlementGrant:
        """Grant a time-limited trial for a feature."""
        expires_at = datetime.now(UTC) + timedelta(days=duration_days)
        
        return self.grant_entitlement(
            tenant_id=tenant_id,
            entitlement_type=EntitlementType.TRIAL,
            resource_id=feature_id,
            value=True,
            source="trial",
            expires_at=expires_at,
            metadata={"duration_days": duration_days},
        )

    def grant_beta_access(
        self,
        tenant_id: str,
        feature_id: str,
    ) -> EntitlementGrant:
        """Grant beta access to a feature."""
        return self.grant_entitlement(
            tenant_id=tenant_id,
            entitlement_type=EntitlementType.BETA,
            resource_id=feature_id,
            value=True,
            source="beta_program",
        )

    def stats(self) -> Dict[str, Any]:
        """Get engine statistics."""
        total_grants = sum(
            len(grants) for grants in self._tenant_grants.values()
        )
        
        return {
            "accounts_registered": len(self._account_mappings),
            "tenants_with_grants": len(self._tenant_grants),
            "total_grants": total_grants,
            "flags_registered": len(self.flag_manager._flags),
            "cache": self.cache.stats(),
        }


# Default feature flag definitions
DEFAULT_FEATURE_FLAGS = [
    FeatureFlag(
        flag_id="api_access",
        name="API Access",
        description="Access to REST and GraphQL APIs",
        state=FeatureFlagState.ENABLED,
        minimum_tier=TierLevel.FREE,
    ),
    FeatureFlag(
        flag_id="advanced_analytics",
        name="Advanced Analytics",
        description="Access to advanced analytics dashboards",
        state=FeatureFlagState.ENABLED,
        minimum_tier=TierLevel.PROFESSIONAL,
    ),
    FeatureFlag(
        flag_id="custom_integrations",
        name="Custom Integrations",
        description="Build custom integrations with webhooks",
        state=FeatureFlagState.ENABLED,
        minimum_tier=TierLevel.BUSINESS,
    ),
    FeatureFlag(
        flag_id="sso_saml",
        name="SSO/SAML",
        description="Single sign-on with SAML",
        state=FeatureFlagState.ENABLED,
        minimum_tier=TierLevel.ENTERPRISE,
    ),
    FeatureFlag(
        flag_id="dedicated_support",
        name="Dedicated Support",
        description="Dedicated support channel",
        state=FeatureFlagState.ENABLED,
        minimum_tier=TierLevel.ENTERPRISE,
    ),
    FeatureFlag(
        flag_id="audit_logs",
        name="Audit Logs",
        description="Detailed audit logging",
        state=FeatureFlagState.ENABLED,
        minimum_tier=TierLevel.BUSINESS,
    ),
    FeatureFlag(
        flag_id="data_export",
        name="Data Export",
        description="Export data in multiple formats",
        state=FeatureFlagState.ENABLED,
        minimum_tier=TierLevel.STARTER,
    ),
    FeatureFlag(
        flag_id="team_collaboration",
        name="Team Collaboration",
        description="Team workspace features",
        state=FeatureFlagState.ENABLED,
        minimum_tier=TierLevel.PROFESSIONAL,
    ),
]


def create_entitlement_engine(
    cache_ttl_seconds: int = 60,
    cache_max_entries: int = 10000,
    register_default_flags: bool = True,
) -> SaaSEntitlementEngine:
    """
    Create and configure a SaaS entitlement engine.
    
    Args:
        cache_ttl_seconds: TTL for cached entitlement checks
        cache_max_entries: Maximum cache entries
        register_default_flags: Whether to register default feature flags
    
    Returns:
        Configured SaaSEntitlementEngine
    """
    engine = SaaSEntitlementEngine(
        cache_ttl_seconds=cache_ttl_seconds,
        cache_max_entries=cache_max_entries,
    )
    
    if register_default_flags:
        for flag in DEFAULT_FEATURE_FLAGS:
            engine.flag_manager.register_flag(flag)
    
    return engine
