# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# KR-Labs is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Integrity Bridge - Premium Subsystem Integration

Connects the premium client subsystem with the existing runtime
integrity verification system. Provides coordinated protection with:
- Bidirectional integrity reporting
- Unified failure handling
- Server-side violation notification
- Synchronized fail-safe mode transitions
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime, timezone, UTC
from typing import Any, Callable, Dict, List, Optional

from krl_data_connectors.core.premium.failsafe import (
    FailSafeController,
    FailSafeMode,
    FailureType,
)
from krl_data_connectors.core.premium.telemetry import (
    TelemetryCollector,
    EventType,
)

logger = logging.getLogger(__name__)


class IntegrityBridge:
    """
    Bridges premium client with runtime integrity verification.
    
    Responsibilities:
    - Monitor integrity verification results
    - Report violations to premium backend
    - Coordinate fail-safe mode transitions
    - Provide unified integrity status
    """
    
    def __init__(
        self,
        failsafe: FailSafeController,
        telemetry: Optional[TelemetryCollector] = None,
        on_violation: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ):
        """
        Initialize integrity bridge.
        
        Args:
            failsafe: Fail-safe controller instance
            telemetry: Telemetry collector for reporting
            on_violation: Callback for integrity violations
        """
        self._failsafe = failsafe
        self._telemetry = telemetry
        self._on_violation = on_violation
        
        self._lock = threading.Lock()
        self._violation_history: List[Dict[str, Any]] = []
        self._verifier_attached = False
        
        logger.debug("IntegrityBridge initialized")
    
    def attach_verifier(self, verifier: Any) -> bool:
        """
        Attach to existing IntegrityVerifier.
        
        Args:
            verifier: IntegrityVerifier instance from runtime_integrity.py
            
        Returns:
            True if attachment successful
        """
        try:
            # Hook into verifier's violation reporting
            if hasattr(verifier, '_violations'):
                self._monitor_verifier(verifier)
                self._verifier_attached = True
                logger.info("IntegrityBridge attached to verifier")
                return True
            else:
                logger.warning("Verifier does not support violation monitoring")
                return False
        except Exception as e:
            logger.error("Failed to attach to verifier: %s", e)
            return False
    
    def _monitor_verifier(self, verifier: Any) -> None:
        """Set up monitoring of verifier violations."""
        # Store original method if present
        original_report = getattr(verifier, '_report_violation', None)
        
        def wrapped_report(module_name: str, expected: str, actual: str) -> None:
            """Wrapped violation reporter that also notifies premium subsystem."""
            # Call original
            if original_report:
                original_report(module_name, expected, actual)
            
            # Notify premium subsystem
            self.report_violation(
                component=module_name,
                violation_type="hash_mismatch",
                details={
                    "expected_hash": expected[:16] + "..." if expected else None,
                    "actual_hash": actual[:16] + "..." if actual else None,
                    "source": "runtime_integrity",
                },
            )
        
        # Patch verifier
        verifier._report_violation = wrapped_report
    
    def report_violation(
        self,
        component: str,
        violation_type: str,
        details: Optional[Dict[str, Any]] = None,
        severity: int = 5,
    ) -> None:
        """
        Report an integrity violation.
        
        Args:
            component: Affected component/module
            violation_type: Type of violation
            details: Additional details
            severity: Severity (1-5)
        """
        violation = {
            "component": component,
            "violation_type": violation_type,
            "details": details or {},
            "severity": severity,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        with self._lock:
            self._violation_history.append(violation)
            # Keep last 100 violations
            if len(self._violation_history) > 100:
                self._violation_history.pop(0)
        
        logger.warning(
            "Integrity violation: %s (%s) severity=%d",
            component, violation_type, severity
        )
        
        # Record in fail-safe
        self._failsafe.record_failure(
            FailureType.INTEGRITY_VIOLATION,
            details=violation,
            severity=severity,
            recoverable=False,  # Integrity violations are not recoverable
        )
        
        # Track in telemetry
        if self._telemetry:
            self._telemetry.track_integrity_check(
                component=component,
                passed=False,
                details=violation,
            )
        
        # Call custom handler
        if self._on_violation:
            try:
                self._on_violation(component, violation)
            except Exception as e:
                logger.warning("Violation callback error: %s", e)
    
    def report_success(self, component: str) -> None:
        """
        Report successful integrity check.
        
        Args:
            component: Verified component/module
        """
        # Track in telemetry
        if self._telemetry:
            self._telemetry.track_integrity_check(
                component=component,
                passed=True,
            )
        
        # Record success in fail-safe (helps recovery scoring)
        self._failsafe.record_success()
    
    def verify_and_report(
        self,
        verifier: Any,
        module_name: str,
        expected_hash: Optional[str] = None,
    ) -> bool:
        """
        Verify module and report result through bridge.
        
        Args:
            verifier: IntegrityVerifier instance
            module_name: Module to verify
            expected_hash: Expected hash (optional)
            
        Returns:
            True if verification passed
        """
        try:
            result = verifier.verify_module(module_name, expected_hash)
            
            if result:
                self.report_success(module_name)
            else:
                # Violation already reported through hook if attached
                if not self._verifier_attached:
                    self.report_violation(
                        component=module_name,
                        violation_type="verification_failed",
                        severity=5,
                    )
            
            return result
            
        except Exception as e:
            logger.error("Verification error for %s: %s", module_name, e)
            self.report_violation(
                component=module_name,
                violation_type="verification_exception",
                details={"error": str(e)},
                severity=4,
            )
            return False
    
    def get_integrity_status(self) -> Dict[str, Any]:
        """Get current integrity status."""
        with self._lock:
            recent_violations = self._violation_history[-10:]
        
        return {
            "failsafe_mode": self._failsafe.mode.value,
            "is_blocked": self._failsafe.is_blocked,
            "verifier_attached": self._verifier_attached,
            "total_violations": len(self._violation_history),
            "recent_violations": recent_violations,
            "failure_score": self._failsafe.failure_score,
        }
    
    def is_operation_allowed(self, operation: str) -> bool:
        """
        Check if operation is allowed given integrity status.
        
        Args:
            operation: Operation/feature name
            
        Returns:
            True if operation is allowed
        """
        # Check fail-safe mode
        if not self._failsafe.is_feature_allowed(operation):
            logger.warning("Operation blocked by fail-safe: %s", operation)
            return False
        
        # Additional checks could be added here
        return True
    
    def clear_violations(self) -> None:
        """Clear violation history (for testing/recovery)."""
        with self._lock:
            self._violation_history.clear()


class IntegrityGuard:
    """
    Decorator/context manager for integrity-protected operations.
    
    Wraps premium operations with integrity checks:
    - Pre-operation verification
    - Post-operation validation
    - Automatic violation handling
    """
    
    def __init__(
        self,
        bridge: IntegrityBridge,
        verifier: Any,
        modules_to_verify: Optional[List[str]] = None,
    ):
        """
        Initialize integrity guard.
        
        Args:
            bridge: IntegrityBridge instance
            verifier: IntegrityVerifier instance
            modules_to_verify: Modules to verify before operation
        """
        self._bridge = bridge
        self._verifier = verifier
        self._modules = modules_to_verify or []
    
    def __enter__(self) -> "IntegrityGuard":
        """Context manager entry - verify before operation."""
        self._verify_all()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - optionally re-verify."""
        # Could add post-operation verification here
        pass
    
    def _verify_all(self) -> None:
        """Verify all configured modules."""
        for module in self._modules:
            if not self._bridge.verify_and_report(self._verifier, module):
                raise IntegrityViolationError(
                    f"Integrity check failed for {module}"
                )
    
    def guard(self, func: Callable) -> Callable:
        """Decorator to guard a function with integrity checks."""
        def wrapper(*args, **kwargs):
            self._verify_all()
            return func(*args, **kwargs)
        return wrapper


class IntegrityViolationError(Exception):
    """Raised when an integrity check fails in a guarded context."""
    pass
