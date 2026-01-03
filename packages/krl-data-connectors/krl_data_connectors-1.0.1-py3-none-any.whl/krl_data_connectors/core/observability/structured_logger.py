# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Structured Logger - Phase 3 Week 18

JSON-structured logging for defense observability with:
- Automatic timestamp signing (HMAC)
- Correlation ID tracking across requests
- Performance budget tracking in log context
- Defense channel routing
- Log aggregation hooks

Integrates with:
- Log Channels for defense-specific routing
- Metric Types for budget tracking
- Telemetry Ingestion for real-time analysis
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Generator, List, Optional, Union

from .log_channels import LogChannelType, DEFENSE_LOG_CHANNELS, get_channel_logger


# =============================================================================
# Configuration
# =============================================================================

# Environment-based signing key (should be set in production)
SIGNING_KEY = os.environ.get(
    "KRL_LOG_SIGNING_KEY",
    "dev-signing-key-change-in-production"
).encode()

# Log retention configuration
DEFAULT_RETENTION_DAYS = 90
AUDIT_RETENTION_DAYS = 365
BILLING_RETENTION_DAYS = 730


# =============================================================================
# Log Severity
# =============================================================================

class LogSeverity(Enum):
    """Log severity levels matching standard logging."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    
    @classmethod
    def from_string(cls, s: str) -> "LogSeverity":
        """Parse severity from string."""
        return cls[s.upper()]


# =============================================================================
# Correlation Context
# =============================================================================

# Thread-local storage for correlation context
_correlation_context = threading.local()


def get_correlation_id() -> Optional[str]:
    """Get current correlation ID from thread-local storage."""
    return getattr(_correlation_context, "correlation_id", None)


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID in thread-local storage."""
    _correlation_context.correlation_id = correlation_id


def generate_correlation_id() -> str:
    """Generate a new correlation ID."""
    return str(uuid.uuid4())


@contextmanager
def correlation_scope(
    correlation_id: Optional[str] = None,
) -> Generator[str, None, None]:
    """
    Context manager for correlation ID scope.
    
    Usage:
        with correlation_scope() as corr_id:
            # All logs within this scope share correlation_id
            logger.info("Operation started", correlation_id=corr_id)
    """
    old_id = get_correlation_id()
    new_id = correlation_id or generate_correlation_id()
    set_correlation_id(new_id)
    try:
        yield new_id
    finally:
        if old_id:
            set_correlation_id(old_id)
        else:
            _correlation_context.correlation_id = None


# =============================================================================
# Log Entry
# =============================================================================

@dataclass
class LogEntry:
    """
    A structured log entry.
    
    Attributes:
        timestamp: Unix timestamp (ms precision)
        channel: Log channel name
        severity: Log severity level
        message: Log message
        context: Structured context data
        correlation_id: Request correlation ID
        signature: HMAC signature (if signed)
    """
    timestamp: float
    channel: str
    severity: LogSeverity
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    signature: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "channel": self.channel,
            "severity": self.severity.name,
            "message": self.message,
            "context": self.context,
            "correlation_id": self.correlation_id,
            "signature": self.signature,
        }
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LogEntry":
        """Create from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            channel=data["channel"],
            severity=LogSeverity.from_string(data["severity"]),
            message=data["message"],
            context=data.get("context", {}),
            correlation_id=data.get("correlation_id"),
            signature=data.get("signature"),
        )


# =============================================================================
# Log Signing
# =============================================================================

def sign_log_entry(entry: LogEntry, key: bytes = SIGNING_KEY) -> str:
    """
    Generate HMAC signature for a log entry.
    
    The signature covers:
    - timestamp
    - channel
    - severity
    - message
    - sorted context keys and values
    """
    # Build canonical string for signing
    parts = [
        str(entry.timestamp),
        entry.channel,
        entry.severity.name,
        entry.message,
    ]
    
    # Add context in sorted order
    for k in sorted(entry.context.keys()):
        parts.append(f"{k}={entry.context[k]}")
    
    canonical = "|".join(parts)
    
    # Generate HMAC-SHA256
    signature = hmac.new(
        key,
        canonical.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    return signature


def verify_log_signature(entry: LogEntry, key: bytes = SIGNING_KEY) -> bool:
    """Verify a log entry signature."""
    if not entry.signature:
        return False
    
    expected = sign_log_entry(entry, key)
    return hmac.compare_digest(entry.signature, expected)


# =============================================================================
# Structured Logger
# =============================================================================

class StructuredLogger:
    """
    Production-grade structured logger for defense systems.
    
    Features:
    - JSON structured output
    - Automatic HMAC signing for audit channels
    - Correlation ID propagation
    - Performance budget context
    - Defense channel routing
    """
    
    def __init__(
        self,
        name: str,
        channel: Optional[LogChannelType] = None,
        auto_sign: bool = True,
        context: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name (usually module name)
            channel: Default log channel (optional)
            auto_sign: Auto-sign entries for audit channels
            context: Default context for all entries
        """
        self._name = name
        self._channel = channel
        self._auto_sign = auto_sign
        self._context = context or {}
        self._handlers: List[Callable[[LogEntry], None]] = []
        
        # Get underlying Python logger
        self._logger = logging.getLogger(f"krl.{name}")
    
    def add_handler(self, handler: Callable[[LogEntry], None]) -> None:
        """Add a custom log handler."""
        self._handlers.append(handler)
    
    def _should_sign(self, channel: LogChannelType) -> bool:
        """Check if entries for this channel should be signed."""
        if not self._auto_sign:
            return False
        
        channel_def = DEFENSE_LOG_CHANNELS.get(channel)
        return channel_def.requires_signing if channel_def else False
    
    def _create_entry(
        self,
        severity: LogSeverity,
        message: str,
        channel: Optional[LogChannelType] = None,
        **context: Any,
    ) -> LogEntry:
        """Create a log entry."""
        ch = channel or self._channel
        channel_name = ch.value if ch else self._name
        
        entry = LogEntry(
            timestamp=time.time(),
            channel=channel_name,
            severity=severity,
            message=message,
            context={**self._context, **context},
            correlation_id=get_correlation_id(),
        )
        
        # Sign if required
        if ch and self._should_sign(ch):
            entry.signature = sign_log_entry(entry)
        
        return entry
    
    def _emit(self, entry: LogEntry) -> None:
        """Emit log entry to all handlers."""
        # Emit to Python logger
        log_method = getattr(self._logger, entry.severity.name.lower())
        log_method(entry.to_json())
        
        # Emit to custom handlers
        for handler in self._handlers:
            try:
                handler(entry)
            except Exception:
                # Don't let handler errors break logging
                pass
    
    def debug(
        self,
        message: str,
        channel: Optional[LogChannelType] = None,
        **context: Any,
    ) -> None:
        """Log debug message."""
        entry = self._create_entry(
            LogSeverity.DEBUG, message, channel, **context
        )
        self._emit(entry)
    
    def info(
        self,
        message: str,
        channel: Optional[LogChannelType] = None,
        **context: Any,
    ) -> None:
        """Log info message."""
        entry = self._create_entry(
            LogSeverity.INFO, message, channel, **context
        )
        self._emit(entry)
    
    def warning(
        self,
        message: str,
        channel: Optional[LogChannelType] = None,
        **context: Any,
    ) -> None:
        """Log warning message."""
        entry = self._create_entry(
            LogSeverity.WARNING, message, channel, **context
        )
        self._emit(entry)
    
    def error(
        self,
        message: str,
        channel: Optional[LogChannelType] = None,
        **context: Any,
    ) -> None:
        """Log error message."""
        entry = self._create_entry(
            LogSeverity.ERROR, message, channel, **context
        )
        self._emit(entry)
    
    def critical(
        self,
        message: str,
        channel: Optional[LogChannelType] = None,
        **context: Any,
    ) -> None:
        """Log critical message."""
        entry = self._create_entry(
            LogSeverity.CRITICAL, message, channel, **context
        )
        self._emit(entry)
    
    # -------------------------------------------------------------------------
    # Defense-Specific Logging Methods
    # -------------------------------------------------------------------------
    
    def log_enforcement(
        self,
        action: str,
        target: str,
        result: str,
        **context: Any,
    ) -> None:
        """Log an enforcement event (auto-signed)."""
        self.info(
            f"Enforcement: {action} on {target} -> {result}",
            channel=LogChannelType.ML_ENFORCEMENT,
            action=action,
            target=target,
            result=result,
            **context,
        )
    
    def log_threat(
        self,
        threat_type: str,
        severity_score: float,
        source: str,
        **context: Any,
    ) -> None:
        """Log a threat detection event (auto-signed)."""
        self.warning(
            f"Threat detected: {threat_type} (score={severity_score})",
            channel=LogChannelType.THREAT_DETECTED,
            threat_type=threat_type,
            severity_score=severity_score,
            source=source,
            **context,
        )
    
    def log_integrity_violation(
        self,
        component: str,
        violation_type: str,
        **context: Any,
    ) -> None:
        """Log an integrity violation (auto-signed)."""
        self.error(
            f"Integrity violation in {component}: {violation_type}",
            channel=LogChannelType.INTEGRITY_VIOLATION,
            component=component,
            violation_type=violation_type,
            **context,
        )
    
    def log_license_anomaly(
        self,
        license_id: str,
        anomaly_type: str,
        **context: Any,
    ) -> None:
        """Log a license anomaly (auto-signed)."""
        self.warning(
            f"License anomaly for {license_id}: {anomaly_type}",
            channel=LogChannelType.LICENSE_ANOMALY,
            license_id=license_id,
            anomaly_type=anomaly_type,
            **context,
        )
    
    def log_policy_update(
        self,
        policy_id: str,
        version: str,
        **context: Any,
    ) -> None:
        """Log a policy update (auto-signed)."""
        self.info(
            f"Policy {policy_id} updated to version {version}",
            channel=LogChannelType.POLICY_UPDATE,
            policy_id=policy_id,
            version=version,
            **context,
        )
    
    def log_crown_jewel_access(
        self,
        resource: str,
        accessor: str,
        action: str,
        **context: Any,
    ) -> None:
        """Log crown jewel API access (auto-signed)."""
        self.info(
            f"Crown jewel access: {accessor} {action} {resource}",
            channel=LogChannelType.CROWNJEWEL_ACCESS,
            resource=resource,
            accessor=accessor,
            action=action,
            **context,
        )
    
    def log_revenue_event(
        self,
        event_type: str,
        tier: str,
        amount: Optional[float] = None,
        **context: Any,
    ) -> None:
        """Log a revenue protection event (auto-signed)."""
        self.info(
            f"Revenue event: {event_type} for tier {tier}",
            channel=LogChannelType.REVENUE_PROTECTION,
            event_type=event_type,
            tier=tier,
            amount=amount,
            **context,
        )
    
    def log_performance_budget(
        self,
        operation: str,
        budget_ms: float,
        actual_ms: float,
        **context: Any,
    ) -> None:
        """Log a performance budget check."""
        over_budget = actual_ms > budget_ms
        level = LogSeverity.WARNING if over_budget else LogSeverity.DEBUG
        
        entry = self._create_entry(
            level,
            f"Performance: {operation} took {actual_ms:.2f}ms (budget: {budget_ms}ms)",
            channel=LogChannelType.ML_BUDGET,
            operation=operation,
            budget_ms=budget_ms,
            actual_ms=actual_ms,
            over_budget=over_budget,
            **context,
        )
        self._emit(entry)
    
    # -------------------------------------------------------------------------
    # Context Management
    # -------------------------------------------------------------------------
    
    def with_context(self, **context: Any) -> "StructuredLogger":
        """Create a new logger with additional context."""
        new_context = {**self._context, **context}
        logger = StructuredLogger(
            self._name,
            self._channel,
            self._auto_sign,
            new_context,
        )
        logger._handlers = self._handlers.copy()
        return logger
    
    @contextmanager
    def operation_scope(
        self,
        operation: str,
        **context: Any,
    ) -> Generator["StructuredLogger", None, None]:
        """
        Context manager for operation logging.
        
        Automatically logs operation start/end with timing.
        
        Usage:
            with logger.operation_scope("process_request", user_id=123) as op_log:
                op_log.info("Processing step 1")
                # ...
        """
        start_time = time.time()
        op_logger = self.with_context(operation=operation, **context)
        
        op_logger.debug(f"Starting operation: {operation}")
        
        try:
            yield op_logger
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            op_logger.error(
                f"Operation failed: {operation}",
                duration_ms=duration_ms,
                error=str(e),
            )
            raise
        else:
            duration_ms = (time.time() - start_time) * 1000
            op_logger.debug(
                f"Completed operation: {operation}",
                duration_ms=duration_ms,
            )


# =============================================================================
# Logger Factory
# =============================================================================

_loggers: Dict[str, StructuredLogger] = {}


def get_logger(
    name: str,
    channel: Optional[LogChannelType] = None,
) -> StructuredLogger:
    """
    Get or create a structured logger.
    
    Args:
        name: Logger name (usually __name__)
        channel: Optional default channel
        
    Returns:
        StructuredLogger instance
    """
    key = f"{name}:{channel.value if channel else 'default'}"
    
    if key not in _loggers:
        _loggers[key] = StructuredLogger(name, channel)
    
    return _loggers[key]


# =============================================================================
# Convenience Functions
# =============================================================================

def log_defense_event(
    channel: LogChannelType,
    message: str,
    **context: Any,
) -> None:
    """
    Quick helper to log a defense event.
    
    Usage:
        log_defense_event(
            LogChannelType.ML_ENFORCEMENT,
            "Blocked suspicious request",
            user_id=123,
            action="block",
        )
    """
    logger = get_logger("defense", channel)
    logger.info(message, channel=channel, **context)
