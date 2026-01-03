# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Tier-Aware Observability - Phase 3 Week 18 Refinement

Tier-specific telemetry routing and DLS aggregation.
Keeps Community overhead low while protecting revenue data.

Tiers:
- Community: Essential metrics only (minimal overhead)
- Pro: Full telemetry with standard weights
- Enterprise: Full telemetry + custom weights + priority routing

DLS Weights by Tier:
- Enterprise: 70% enforcement, 20% telemetry, 10% anomaly
- Pro: 60% enforcement, 25% telemetry, 15% anomaly
- Community: 50% enforcement, 30% telemetry, 20% anomaly
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from .log_channels import LogChannelType
from .telemetry_ingestion import TelemetryEventType


# =============================================================================
# Tier Definitions
# =============================================================================

class Tier(Enum):
    """Product tier levels."""
    COMMUNITY = "community"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass(frozen=True)
class TierConfig:
    """
    Tier-specific observability configuration.
    
    Attributes:
        tier: The tier level
        enabled_channels: Log channels enabled for this tier
        enabled_events: Telemetry events enabled for this tier
        dls_weights: Custom DLS component weights
        sampling_rate: Event sampling rate (1.0 = 100%)
        retention_days: Log/event retention period
        priority: Processing priority (higher = faster)
    """
    tier: Tier
    enabled_channels: Set[LogChannelType]
    enabled_events: Set[TelemetryEventType]
    dls_weights: Dict[str, float]
    sampling_rate: float = 1.0
    retention_days: int = 90
    priority: int = 1


# =============================================================================
# Essential Channels (All Tiers)
# =============================================================================

ESSENTIAL_CHANNELS: Set[LogChannelType] = {
    LogChannelType.ML_ENFORCEMENT,
    LogChannelType.INTEGRITY_VIOLATION,
    LogChannelType.LICENSE_ANOMALY,
    LogChannelType.THREAT_DETECTED,
    LogChannelType.TIER_VIOLATION,
}

ESSENTIAL_EVENTS: Set[TelemetryEventType] = {
    TelemetryEventType.ENFORCEMENT_DECISION,
    TelemetryEventType.ENFORCEMENT_RESULT,
    TelemetryEventType.THREAT_DETECTED,
    TelemetryEventType.THREAT_MITIGATED,
    TelemetryEventType.LICENSE_ANOMALY,
    TelemetryEventType.TIER_VIOLATION,
    TelemetryEventType.SYSTEM_ERROR,
}


# =============================================================================
# Pro Channels (Pro + Enterprise)
# =============================================================================

PRO_CHANNELS: Set[LogChannelType] = ESSENTIAL_CHANNELS | {
    LogChannelType.ML_INFERENCE,
    LogChannelType.ML_DRIFT,
    LogChannelType.LICENSE_REFRESH,
    LogChannelType.LICENSE_VALIDATION,
    LogChannelType.POLICY_UPDATE,
    LogChannelType.POLICY_APPLY,
    LogChannelType.THREAT_RESPONSE,
    LogChannelType.REVENUE_PROTECTION,
    LogChannelType.BILLING_HOOK,
    LogChannelType.API_ACCESS,
}

PRO_EVENTS: Set[TelemetryEventType] = ESSENTIAL_EVENTS | {
    TelemetryEventType.ENFORCEMENT_ACTION,
    TelemetryEventType.ML_INFERENCE,
    TelemetryEventType.ML_PREDICTION,
    TelemetryEventType.ML_DRIFT,
    TelemetryEventType.LICENSE_VALIDATION,
    TelemetryEventType.LICENSE_REFRESH,
    TelemetryEventType.POLICY_PUSH,
    TelemetryEventType.POLICY_APPLY,
    TelemetryEventType.THREAT_RESPONSE,
    TelemetryEventType.API_REQUEST,
    TelemetryEventType.API_RESPONSE,
    TelemetryEventType.BILLING_EVENT,
    TelemetryEventType.TIER_CHECK,
}


# =============================================================================
# Enterprise Channels (All)
# =============================================================================

ENTERPRISE_CHANNELS: Set[LogChannelType] = set(LogChannelType)

ENTERPRISE_EVENTS: Set[TelemetryEventType] = set(TelemetryEventType)


# =============================================================================
# DLS Weights by Tier
# =============================================================================

COMMUNITY_DLS_WEIGHTS: Dict[str, float] = {
    "detection_accuracy": 0.20,
    "enforcement_latency": 0.15,
    "telemetry_coverage": 0.15,
    "policy_delivery": 0.15,
    "false_positive_rate": 0.15,
    "drift_rate": 0.10,
    "chaos_survival": 0.10,
}

PRO_DLS_WEIGHTS: Dict[str, float] = {
    "detection_accuracy": 0.20,
    "enforcement_latency": 0.20,  # Increased for Pro
    "telemetry_coverage": 0.15,
    "policy_delivery": 0.15,
    "false_positive_rate": 0.12,
    "drift_rate": 0.08,
    "chaos_survival": 0.10,
}

ENTERPRISE_DLS_WEIGHTS: Dict[str, float] = {
    "detection_accuracy": 0.15,
    "enforcement_latency": 0.25,  # Highest for Enterprise
    "telemetry_coverage": 0.15,
    "policy_delivery": 0.15,
    "false_positive_rate": 0.10,
    "drift_rate": 0.10,
    "chaos_survival": 0.10,
}


# =============================================================================
# Tier Configurations
# =============================================================================

TIER_CONFIGS: Dict[Tier, TierConfig] = {
    Tier.COMMUNITY: TierConfig(
        tier=Tier.COMMUNITY,
        enabled_channels=ESSENTIAL_CHANNELS,
        enabled_events=ESSENTIAL_EVENTS,
        dls_weights=COMMUNITY_DLS_WEIGHTS,
        sampling_rate=0.1,  # 10% sampling for community
        retention_days=30,
        priority=1,
    ),
    Tier.PRO: TierConfig(
        tier=Tier.PRO,
        enabled_channels=PRO_CHANNELS,
        enabled_events=PRO_EVENTS,
        dls_weights=PRO_DLS_WEIGHTS,
        sampling_rate=0.5,  # 50% sampling for pro
        retention_days=90,
        priority=5,
    ),
    Tier.ENTERPRISE: TierConfig(
        tier=Tier.ENTERPRISE,
        enabled_channels=ENTERPRISE_CHANNELS,
        enabled_events=ENTERPRISE_EVENTS,
        dls_weights=ENTERPRISE_DLS_WEIGHTS,
        sampling_rate=1.0,  # Full telemetry for enterprise
        retention_days=365,
        priority=10,
    ),
}


def get_tier_config(tier: Tier) -> TierConfig:
    """Get configuration for a tier."""
    return TIER_CONFIGS[tier]


def get_tier_from_string(tier_str: str) -> Tier:
    """Parse tier from string."""
    return Tier(tier_str.lower())


# =============================================================================
# Tier-Aware DLS Scorer
# =============================================================================

class TieredDLSScorer:
    """
    DLS scorer with tier-specific weights.
    
    Makes DLS actionable for automated escalation by
    applying different weights based on tier priorities.
    """
    
    def __init__(self, tier: Tier = Tier.PRO):
        self._tier = tier
        self._config = TIER_CONFIGS[tier]
        self._components: Dict[str, float] = {}
    
    @property
    def tier(self) -> Tier:
        return self._tier
    
    @property
    def weights(self) -> Dict[str, float]:
        return self._config.dls_weights.copy()
    
    def set_component(self, name: str, score: float) -> None:
        """Set a DLS component score (0-100)."""
        self._components[name] = max(0.0, min(100.0, score))
    
    def set_components(self, components: Dict[str, float]) -> None:
        """Set multiple DLS component scores."""
        for name, score in components.items():
            self.set_component(name, score)
    
    def compute_dls(self) -> float:
        """
        Compute DLS using tier-specific weights.
        
        Returns:
            DLS score 0-100
        """
        if not self._components:
            return 0.0
        
        weights = self._config.dls_weights
        total = 0.0
        total_weight = 0.0
        
        for name, weight in weights.items():
            if name in self._components:
                # Handle inverted metrics (lower is better)
                score = self._components[name]
                if name in ("false_positive_rate", "drift_rate"):
                    score = 100.0 - score
                
                total += weight * score
                total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        # Normalize if not all components present
        return total / total_weight * sum(weights.values())
    
    def get_status(self) -> Dict[str, Any]:
        """Get DLS status with tier context."""
        dls = self.compute_dls()
        
        return {
            "tier": self._tier.value,
            "dls": dls,
            "components": self._components.copy(),
            "weights": self._config.dls_weights.copy(),
            "thresholds": {
                "critical": 60.0,
                "warning": 75.0,
                "healthy": 85.0,
            },
            "status": (
                "critical" if dls < 60 else
                "warning" if dls < 75 else
                "healthy" if dls >= 85 else
                "degraded"
            ),
        }


# =============================================================================
# Tier-Aware Channel Router
# =============================================================================

class TierAwareRouter:
    """
    Routes telemetry and logs based on tier.
    
    Ensures:
    - Community: Essential metrics only
    - Pro: Full telemetry with standard routing
    - Enterprise: All channels with priority processing
    """
    
    def __init__(self, default_tier: Tier = Tier.COMMUNITY):
        self._default_tier = default_tier
    
    def should_log_channel(
        self,
        channel: LogChannelType,
        tier: Optional[Tier] = None,
    ) -> bool:
        """Check if channel should be logged for tier."""
        tier = tier or self._default_tier
        config = TIER_CONFIGS[tier]
        return channel in config.enabled_channels
    
    def should_emit_event(
        self,
        event_type: TelemetryEventType,
        tier: Optional[Tier] = None,
    ) -> bool:
        """Check if event should be emitted for tier."""
        tier = tier or self._default_tier
        config = TIER_CONFIGS[tier]
        return event_type in config.enabled_events
    
    def should_sample(
        self,
        tier: Optional[Tier] = None,
        force_sample: bool = False,
    ) -> bool:
        """
        Determine if event should be sampled.
        
        Args:
            tier: The tier to check
            force_sample: Force sampling (for critical events)
            
        Returns:
            True if event should be recorded
        """
        if force_sample:
            return True
        
        tier = tier or self._default_tier
        config = TIER_CONFIGS[tier]
        
        import random
        return random.random() < config.sampling_rate
    
    def get_retention_days(self, tier: Optional[Tier] = None) -> int:
        """Get retention period for tier."""
        tier = tier or self._default_tier
        return TIER_CONFIGS[tier].retention_days
    
    def get_priority(self, tier: Optional[Tier] = None) -> int:
        """Get processing priority for tier."""
        tier = tier or self._default_tier
        return TIER_CONFIGS[tier].priority
    
    def filter_channels(
        self,
        channels: List[LogChannelType],
        tier: Optional[Tier] = None,
    ) -> List[LogChannelType]:
        """Filter channels to those enabled for tier."""
        tier = tier or self._default_tier
        config = TIER_CONFIGS[tier]
        return [c for c in channels if c in config.enabled_channels]
    
    def filter_events(
        self,
        events: List[TelemetryEventType],
        tier: Optional[Tier] = None,
    ) -> List[TelemetryEventType]:
        """Filter events to those enabled for tier."""
        tier = tier or self._default_tier
        config = TIER_CONFIGS[tier]
        return [e for e in events if e in config.enabled_events]


# =============================================================================
# Global Router Instance
# =============================================================================

_global_router: Optional[TierAwareRouter] = None


def get_global_router() -> TierAwareRouter:
    """Get or create global tier-aware router."""
    global _global_router
    if _global_router is None:
        _global_router = TierAwareRouter()
    return _global_router


def set_default_tier(tier: Tier) -> None:
    """Set default tier for global router."""
    global _global_router
    _global_router = TierAwareRouter(default_tier=tier)
