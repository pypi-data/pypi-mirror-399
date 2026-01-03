# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# KR-Labs is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Fail-Safe Controller - Graceful Degradation

Implements graceful degradation for:
- Integrity violations
- Network failures
- Authentication failures
- Backend unavailability
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, UTC
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class FailureType(Enum):
    """Types of failures that trigger fail-safe."""
    INTEGRITY_VIOLATION = "integrity_violation"
    NETWORK_FAILURE = "network_failure"
    AUTH_FAILURE = "auth_failure"
    BACKEND_UNAVAILABLE = "backend_unavailable"
    RATE_LIMITED = "rate_limited"
    LICENSE_EXPIRED = "license_expired"
    CHALLENGE_FAILED = "challenge_failed"
    ANOMALY_DETECTED = "anomaly_detected"


class FailSafeMode(Enum):
    """Fail-safe operational modes."""
    NORMAL = "normal"
    DEGRADED = "degraded"
    RESTRICTED = "restricted"
    BLOCKED = "blocked"
    OFFLINE = "offline"


@dataclass
class FailureEvent:
    """Record of a failure event."""
    failure_type: FailureType
    timestamp: datetime
    details: Dict[str, Any]
    severity: int  # 1-5, 5 being most severe
    recoverable: bool = True
    recovery_attempted: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "failure_type": self.failure_type.value,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "severity": self.severity,
            "recoverable": self.recoverable,
            "recovery_attempted": self.recovery_attempted,
        }


@dataclass
class FailSafeConfig:
    """Fail-safe controller configuration."""
    # Mode thresholds
    degraded_threshold: int = 3  # Failures before degraded
    restricted_threshold: int = 5  # Failures before restricted
    blocked_threshold: int = 10  # Failures before blocked
    
    # Recovery
    recovery_window_seconds: float = 300.0  # 5 minutes
    auto_recovery_enabled: bool = True
    recovery_check_interval_seconds: float = 60.0
    
    # Failure weights by type
    failure_weights: Dict[str, int] = field(default_factory=lambda: {
        FailureType.INTEGRITY_VIOLATION.value: 5,
        FailureType.NETWORK_FAILURE.value: 1,
        FailureType.AUTH_FAILURE.value: 3,
        FailureType.BACKEND_UNAVAILABLE.value: 2,
        FailureType.RATE_LIMITED.value: 1,
        FailureType.LICENSE_EXPIRED.value: 5,
        FailureType.CHALLENGE_FAILED.value: 4,
        FailureType.ANOMALY_DETECTED.value: 4,
    })
    
    # Feature restrictions per mode
    allowed_features: Dict[str, Set[str]] = field(default_factory=lambda: {
        FailSafeMode.NORMAL.value: {"*"},  # All features
        FailSafeMode.DEGRADED.value: {"compute", "analyze", "basic"},
        FailSafeMode.RESTRICTED.value: {"basic"},
        FailSafeMode.BLOCKED.value: set(),
        FailSafeMode.OFFLINE.value: {"offline_cache"},
    })


class FailSafeController:
    """
    Controls graceful degradation behavior.
    
    Features:
    - Failure tracking and scoring
    - Mode transitions based on failure severity
    - Automatic recovery attempts
    - Feature restriction enforcement
    """
    
    def __init__(
        self,
        config: Optional[FailSafeConfig] = None,
        on_mode_change: Optional[Callable[[FailSafeMode, FailSafeMode], None]] = None,
    ):
        """
        Initialize fail-safe controller.
        
        Args:
            config: Controller configuration
            on_mode_change: Callback for mode transitions
        """
        self._config = config or FailSafeConfig()
        self._on_mode_change = on_mode_change
        
        self._mode = FailSafeMode.NORMAL
        self._failure_events: List[FailureEvent] = []
        self._lock = threading.Lock()
        
        # Recovery tracking
        self._recovery_thread: Optional[threading.Thread] = None
        self._running = False
        self._last_recovery_attempt: Optional[datetime] = None
        
        # Blocked features
        self._blocked_features: Set[str] = set()
        
        logger.debug("FailSafeController initialized")
    
    @property
    def mode(self) -> FailSafeMode:
        """Get current fail-safe mode."""
        return self._mode
    
    @property
    def is_normal(self) -> bool:
        """Check if operating normally."""
        return self._mode == FailSafeMode.NORMAL
    
    @property
    def is_blocked(self) -> bool:
        """Check if fully blocked."""
        return self._mode == FailSafeMode.BLOCKED
    
    @property
    def failure_score(self) -> int:
        """Calculate current failure score."""
        with self._lock:
            cutoff = datetime.now(timezone.utc) - timedelta(
                seconds=self._config.recovery_window_seconds
            )
            
            score = 0
            for event in self._failure_events:
                if event.timestamp > cutoff:
                    weight = self._config.failure_weights.get(
                        event.failure_type.value, 1
                    )
                    score += weight * event.severity
            
            return score
    
    def record_failure(
        self,
        failure_type: FailureType,
        details: Optional[Dict[str, Any]] = None,
        severity: int = 3,
        recoverable: bool = True,
    ) -> FailSafeMode:
        """
        Record a failure event.
        
        Args:
            failure_type: Type of failure
            details: Additional details
            severity: Severity (1-5)
            recoverable: Whether failure is recoverable
            
        Returns:
            Current fail-safe mode after update
        """
        event = FailureEvent(
            failure_type=failure_type,
            timestamp=datetime.now(timezone.utc),
            details=details or {},
            severity=min(5, max(1, severity)),
            recoverable=recoverable,
        )
        
        with self._lock:
            self._failure_events.append(event)
            
            # Trim old events
            self._cleanup_old_events()
            
            # Log the failure
            logger.warning(
                "Failure recorded: %s (severity=%d, recoverable=%s)",
                failure_type.value, severity, recoverable
            )
        
        # Recalculate mode
        new_mode = self._calculate_mode()
        self._transition_mode(new_mode)
        
        # Handle critical failures
        if failure_type in (
            FailureType.INTEGRITY_VIOLATION,
            FailureType.LICENSE_EXPIRED,
        ):
            self._handle_critical_failure(event)
        
        return self._mode
    
    def record_success(self) -> None:
        """Record a successful operation (for recovery scoring)."""
        # Successes help reduce failure score over time
        with self._lock:
            # Remove oldest non-critical failure if any
            for i, event in enumerate(self._failure_events):
                if event.recoverable and event.severity < 4:
                    del self._failure_events[i]
                    break
        
        # Check for mode improvement
        new_mode = self._calculate_mode()
        if new_mode.value < self._mode.value:
            self._transition_mode(new_mode)
    
    def _calculate_mode(self) -> FailSafeMode:
        """Calculate appropriate mode based on failure score."""
        score = self.failure_score
        
        if score >= self._config.blocked_threshold:
            return FailSafeMode.BLOCKED
        elif score >= self._config.restricted_threshold:
            return FailSafeMode.RESTRICTED
        elif score >= self._config.degraded_threshold:
            return FailSafeMode.DEGRADED
        else:
            return FailSafeMode.NORMAL
    
    def _transition_mode(self, new_mode: FailSafeMode) -> None:
        """Transition to new mode if different."""
        if new_mode == self._mode:
            return
        
        old_mode = self._mode
        self._mode = new_mode
        
        logger.info(
            "Fail-safe mode transition: %s -> %s",
            old_mode.value, new_mode.value
        )
        
        if self._on_mode_change:
            try:
                self._on_mode_change(old_mode, new_mode)
            except Exception as e:
                logger.warning("Mode change callback error: %s", e)
        
        # Start recovery if auto-recovery enabled
        if (
            self._config.auto_recovery_enabled
            and new_mode != FailSafeMode.NORMAL
            and new_mode != FailSafeMode.BLOCKED
        ):
            self._start_recovery()
    
    def _handle_critical_failure(self, event: FailureEvent) -> None:
        """Handle critical failure types."""
        if event.failure_type == FailureType.INTEGRITY_VIOLATION:
            # Immediate escalation for integrity violations
            logger.critical("Integrity violation detected - escalating to blocked mode")
            self._transition_mode(FailSafeMode.BLOCKED)
            self._blocked_features.add("*")
        
        elif event.failure_type == FailureType.LICENSE_EXPIRED:
            logger.warning("License expired - transitioning to restricted mode")
            self._transition_mode(FailSafeMode.RESTRICTED)
    
    def _cleanup_old_events(self) -> None:
        """Remove events outside recovery window."""
        cutoff = datetime.now(timezone.utc) - timedelta(
            seconds=self._config.recovery_window_seconds
        )
        self._failure_events = [
            e for e in self._failure_events
            if e.timestamp > cutoff or not e.recoverable
        ]
    
    def is_feature_allowed(self, feature: str) -> bool:
        """
        Check if feature is allowed in current mode.
        
        Args:
            feature: Feature name to check
            
        Returns:
            True if feature is allowed
        """
        if feature in self._blocked_features:
            return False
        
        allowed = self._config.allowed_features.get(
            self._mode.value, set()
        )
        
        if "*" in allowed:
            return True
        
        return feature in allowed
    
    def block_feature(self, feature: str, reason: str = "") -> None:
        """Explicitly block a feature."""
        self._blocked_features.add(feature)
        logger.warning("Feature blocked: %s (reason: %s)", feature, reason)
    
    def unblock_feature(self, feature: str) -> None:
        """Remove explicit feature block."""
        self._blocked_features.discard(feature)
        logger.info("Feature unblocked: %s", feature)
    
    def force_mode(self, mode: FailSafeMode, reason: str = "") -> None:
        """Force transition to specific mode."""
        logger.warning("Forced mode transition to %s: %s", mode.value, reason)
        self._transition_mode(mode)
    
    def reset(self) -> None:
        """Reset controller to normal state."""
        with self._lock:
            self._failure_events.clear()
            self._blocked_features.clear()
        
        self._stop_recovery()
        self._transition_mode(FailSafeMode.NORMAL)
        logger.info("Fail-safe controller reset to normal")
    
    def _start_recovery(self) -> None:
        """Start background recovery thread."""
        if self._recovery_thread and self._recovery_thread.is_alive():
            return
        
        self._running = True
        self._recovery_thread = threading.Thread(
            target=self._recovery_loop,
            name="failsafe-recovery",
            daemon=True,
        )
        self._recovery_thread.start()
    
    def _stop_recovery(self) -> None:
        """Stop recovery thread."""
        self._running = False
    
    def _recovery_loop(self) -> None:
        """Background loop for automatic recovery."""
        while self._running:
            time.sleep(self._config.recovery_check_interval_seconds)
            
            if not self._running or self._mode == FailSafeMode.NORMAL:
                break
            
            # Check if score has improved enough
            new_mode = self._calculate_mode()
            if new_mode.value < self._mode.value:
                self._transition_mode(new_mode)
                
                if new_mode == FailSafeMode.NORMAL:
                    logger.info("Automatic recovery complete")
                    break
    
    def get_status(self) -> Dict[str, Any]:
        """Get current fail-safe status."""
        with self._lock:
            recent_failures = [
                e.to_dict() for e in self._failure_events[-10:]
            ]
        
        return {
            "mode": self._mode.value,
            "failure_score": self.failure_score,
            "thresholds": {
                "degraded": self._config.degraded_threshold,
                "restricted": self._config.restricted_threshold,
                "blocked": self._config.blocked_threshold,
            },
            "blocked_features": list(self._blocked_features),
            "recent_failures": recent_failures,
            "auto_recovery": self._config.auto_recovery_enabled,
        }
    
    def __enter__(self) -> "FailSafeController":
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self._stop_recovery()
