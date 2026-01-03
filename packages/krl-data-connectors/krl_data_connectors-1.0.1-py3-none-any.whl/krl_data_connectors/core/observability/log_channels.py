# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Log Channels - Phase 3 Week 18

Defense-specific logging channels for structured observability.
Each channel corresponds to a specific defense subsystem and
provides consistent logging context for:
- ML enforcement decisions
- Integrity violations
- License anomalies
- Policy updates
- Revenue protection events

Channels support:
- Structured JSON output
- Log level filtering
- Context propagation
- Correlation ID tracking
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import json


# =============================================================================
# Log Channel Definitions
# =============================================================================

class LogChannelType(Enum):
    """Types of defense log channels."""
    
    # ML & Enforcement
    ML_ENFORCEMENT = "ml.enforcement"
    ML_INFERENCE = "ml.inference"
    ML_BUDGET = "ml.budget"
    ML_DRIFT = "ml.drift"
    
    # Integrity
    INTEGRITY_VIOLATION = "integrity.violation"
    INTEGRITY_CHECK = "integrity.check"
    
    # License
    LICENSE_ANOMALY = "license.anomaly"
    LICENSE_REFRESH = "license.refresh"
    LICENSE_VALIDATION = "license.validation"
    
    # Policy
    POLICY_UPDATE = "policy.update"
    POLICY_APPLY = "policy.apply"
    POLICY_ROLLOUT = "policy.rollout"
    
    # Access
    CROWNJEWEL_ACCESS = "crownjewel.access"
    API_ACCESS = "api.access"
    
    # Threats
    THREAT_DETECTED = "threat.detected"
    THREAT_RESPONSE = "threat.response"
    THREAT_ESCALATION = "threat.escalation"
    
    # Revenue
    REVENUE_PROTECTION = "revenue.protection"
    BILLING_HOOK = "billing.hook"
    TIER_VIOLATION = "tier.violation"
    
    # Telemetry
    TELEMETRY_INGESTION = "telemetry.ingestion"
    TELEMETRY_CORRELATION = "telemetry.correlation"


@dataclass
class LogChannel:
    """
    A defense logging channel with metadata.
    
    Attributes:
        channel_type: The channel type enum
        description: Human-readable description
        default_level: Default logging level
        requires_signing: Whether logs require HMAC signing
        sensitive: Whether channel may contain sensitive data
        retention_days: Log retention period
    """
    channel_type: LogChannelType
    description: str
    default_level: int = logging.INFO
    requires_signing: bool = False
    sensitive: bool = False
    retention_days: int = 90
    
    @property
    def name(self) -> str:
        """Get channel name string."""
        return self.channel_type.value
    
    def get_logger(self) -> logging.Logger:
        """Get a logger for this channel."""
        return logging.getLogger(f"krl.{self.name}")


# =============================================================================
# Channel Registry
# =============================================================================

DEFENSE_LOG_CHANNELS: Dict[LogChannelType, LogChannel] = {
    # ML & Enforcement Channels
    LogChannelType.ML_ENFORCEMENT: LogChannel(
        channel_type=LogChannelType.ML_ENFORCEMENT,
        description="ML enforcement decisions and actions",
        default_level=logging.INFO,
        requires_signing=True,
        retention_days=365,  # Keep for audit
    ),
    LogChannelType.ML_INFERENCE: LogChannel(
        channel_type=LogChannelType.ML_INFERENCE,
        description="Model inference events and timings",
        default_level=logging.DEBUG,
    ),
    LogChannelType.ML_BUDGET: LogChannel(
        channel_type=LogChannelType.ML_BUDGET,
        description="Performance budget tracking for ML",
        default_level=logging.WARNING,
    ),
    LogChannelType.ML_DRIFT: LogChannel(
        channel_type=LogChannelType.ML_DRIFT,
        description="Model drift detection events",
        default_level=logging.WARNING,
    ),
    
    # Integrity Channels
    LogChannelType.INTEGRITY_VIOLATION: LogChannel(
        channel_type=LogChannelType.INTEGRITY_VIOLATION,
        description="Integrity check failures",
        default_level=logging.ERROR,
        requires_signing=True,
        retention_days=365,
    ),
    LogChannelType.INTEGRITY_CHECK: LogChannel(
        channel_type=LogChannelType.INTEGRITY_CHECK,
        description="Successful integrity checks",
        default_level=logging.DEBUG,
    ),
    
    # License Channels
    LogChannelType.LICENSE_ANOMALY: LogChannel(
        channel_type=LogChannelType.LICENSE_ANOMALY,
        description="License anomalies detected",
        default_level=logging.WARNING,
        requires_signing=True,
        retention_days=365,
    ),
    LogChannelType.LICENSE_REFRESH: LogChannel(
        channel_type=LogChannelType.LICENSE_REFRESH,
        description="Token refresh events",
        default_level=logging.INFO,
    ),
    LogChannelType.LICENSE_VALIDATION: LogChannel(
        channel_type=LogChannelType.LICENSE_VALIDATION,
        description="License validation events",
        default_level=logging.DEBUG,
    ),
    
    # Policy Channels
    LogChannelType.POLICY_UPDATE: LogChannel(
        channel_type=LogChannelType.POLICY_UPDATE,
        description="Policy updates received",
        default_level=logging.INFO,
        requires_signing=True,
    ),
    LogChannelType.POLICY_APPLY: LogChannel(
        channel_type=LogChannelType.POLICY_APPLY,
        description="Policy application events",
        default_level=logging.INFO,
    ),
    LogChannelType.POLICY_ROLLOUT: LogChannel(
        channel_type=LogChannelType.POLICY_ROLLOUT,
        description="Policy rollout progress",
        default_level=logging.INFO,
    ),
    
    # Access Channels
    LogChannelType.CROWNJEWEL_ACCESS: LogChannel(
        channel_type=LogChannelType.CROWNJEWEL_ACCESS,
        description="Crown jewel API access events",
        default_level=logging.INFO,
        requires_signing=True,
        sensitive=True,
        retention_days=365,
    ),
    LogChannelType.API_ACCESS: LogChannel(
        channel_type=LogChannelType.API_ACCESS,
        description="General API access events",
        default_level=logging.DEBUG,
    ),
    
    # Threat Channels
    LogChannelType.THREAT_DETECTED: LogChannel(
        channel_type=LogChannelType.THREAT_DETECTED,
        description="Threat detection events",
        default_level=logging.WARNING,
        requires_signing=True,
        retention_days=365,
    ),
    LogChannelType.THREAT_RESPONSE: LogChannel(
        channel_type=LogChannelType.THREAT_RESPONSE,
        description="Threat response actions taken",
        default_level=logging.INFO,
        requires_signing=True,
        retention_days=365,
    ),
    LogChannelType.THREAT_ESCALATION: LogChannel(
        channel_type=LogChannelType.THREAT_ESCALATION,
        description="Threat escalation events",
        default_level=logging.WARNING,
        requires_signing=True,
    ),
    
    # Revenue Channels
    LogChannelType.REVENUE_PROTECTION: LogChannel(
        channel_type=LogChannelType.REVENUE_PROTECTION,
        description="Revenue protection events",
        default_level=logging.INFO,
        requires_signing=True,
        retention_days=730,  # 2 years for billing
    ),
    LogChannelType.BILLING_HOOK: LogChannel(
        channel_type=LogChannelType.BILLING_HOOK,
        description="Billing integration events",
        default_level=logging.INFO,
        retention_days=730,
    ),
    LogChannelType.TIER_VIOLATION: LogChannel(
        channel_type=LogChannelType.TIER_VIOLATION,
        description="Tier limit violations",
        default_level=logging.WARNING,
        requires_signing=True,
    ),
    
    # Telemetry Channels
    LogChannelType.TELEMETRY_INGESTION: LogChannel(
        channel_type=LogChannelType.TELEMETRY_INGESTION,
        description="Telemetry event ingestion",
        default_level=logging.DEBUG,
    ),
    LogChannelType.TELEMETRY_CORRELATION: LogChannel(
        channel_type=LogChannelType.TELEMETRY_CORRELATION,
        description="Telemetry correlation events",
        default_level=logging.DEBUG,
    ),
}


# =============================================================================
# Channel Logger Factory
# =============================================================================

def get_channel_logger(
    channel: LogChannelType,
    context: Optional[Dict[str, Any]] = None,
) -> "ChannelLogger":
    """
    Get a logger for a specific defense channel.
    
    Args:
        channel: The log channel type
        context: Optional context to include in all log entries
        
    Returns:
        ChannelLogger instance for the channel
    """
    channel_def = DEFENSE_LOG_CHANNELS.get(channel)
    if not channel_def:
        raise ValueError(f"Unknown channel: {channel}")
    
    return ChannelLogger(channel_def, context)


class ChannelLogger:
    """
    A logger bound to a specific defense channel.
    
    Provides structured logging with automatic context
    enrichment and channel-specific formatting.
    """
    
    def __init__(
        self,
        channel: LogChannel,
        context: Optional[Dict[str, Any]] = None,
    ):
        self._channel = channel
        self._context = context or {}
        self._logger = channel.get_logger()
    
    def _format_message(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Format log message as structured data."""
        import time
        
        data = {
            "channel": self._channel.name,
            "message": message,
            "timestamp": time.time(),
            **self._context,
        }
        
        if extra:
            data.update(extra)
        
        return data
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        data = self._format_message(message, kwargs)
        self._logger.debug(json.dumps(data))
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        data = self._format_message(message, kwargs)
        self._logger.info(json.dumps(data))
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        data = self._format_message(message, kwargs)
        self._logger.warning(json.dumps(data))
    
    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        data = self._format_message(message, kwargs)
        self._logger.error(json.dumps(data))
    
    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message."""
        data = self._format_message(message, kwargs)
        self._logger.critical(json.dumps(data))
    
    def with_context(self, **context: Any) -> "ChannelLogger":
        """Create a new logger with additional context."""
        new_context = {**self._context, **context}
        return ChannelLogger(self._channel, new_context)
    
    @property
    def requires_signing(self) -> bool:
        """Check if this channel requires signed logs."""
        return self._channel.requires_signing
    
    @property
    def channel_name(self) -> str:
        """Get the channel name."""
        return self._channel.name


# =============================================================================
# Channel Utilities
# =============================================================================

def get_audit_channels() -> List[LogChannel]:
    """Get all channels that require audit-grade logging."""
    return [
        channel for channel in DEFENSE_LOG_CHANNELS.values()
        if channel.requires_signing
    ]


def get_sensitive_channels() -> List[LogChannel]:
    """Get all channels that may contain sensitive data."""
    return [
        channel for channel in DEFENSE_LOG_CHANNELS.values()
        if channel.sensitive
    ]


def get_channels_by_prefix(prefix: str) -> List[LogChannel]:
    """Get all channels with a given prefix (e.g., 'ml', 'license')."""
    return [
        channel for channel in DEFENSE_LOG_CHANNELS.values()
        if channel.name.startswith(prefix)
    ]
