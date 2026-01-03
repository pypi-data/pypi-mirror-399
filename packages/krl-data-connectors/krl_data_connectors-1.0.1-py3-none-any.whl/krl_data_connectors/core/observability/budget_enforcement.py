# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Budget Enforcement - Phase 3 Week 18 Refinement

Runtime performance budget enforcement with alerts.
Ensures Defense Liveness Score (DLS) remains reliable under load.

Features:
- Decorator-based budget tracking (@track_budget)
- Automatic alerting on budget violations
- Warning/Critical threshold escalation
- Async support via contextvars
- Budget violation metrics collection

Performance Budgets:
- ML Inference: 5ms (warning), 10ms (critical)
- Enforcement Loop: 50ms (warning), 100ms (critical)
- Telemetry Batch: 10ms (warning), 20ms (critical)
- Crown Jewel: 100ms (warning), 200ms (critical)
"""

from __future__ import annotations

import asyncio
import functools
import time
import threading
from contextvars import ContextVar
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    TypeVar,
    Union,
    Awaitable,
)

# =============================================================================
# Performance Budget Definitions
# =============================================================================

# Budget constants (milliseconds)
BUDGET_ML_INFERENCE_MS = 5.0
BUDGET_ENFORCEMENT_LOOP_MS = 50.0
BUDGET_TELEMETRY_BATCH_MS = 10.0
BUDGET_CROWN_JEWEL_MS = 100.0
BUDGET_TOKEN_VALIDATION_MS = 20.0
BUDGET_POLICY_DELIVERY_MS = 30.0


class BudgetSeverity(Enum):
    """Severity levels for budget violations."""
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class PerformanceBudget:
    """
    A performance budget with warning and critical thresholds.
    
    Attributes:
        name: Budget identifier
        warning_ms: Warning threshold in milliseconds
        critical_ms: Critical threshold in milliseconds  
        description: Human-readable description
        dls_component: Associated DLS component
    """
    name: str
    warning_ms: float
    critical_ms: float
    description: str = ""
    dls_component: Optional[str] = None
    
    def check(self, duration_ms: float) -> BudgetSeverity:
        """Check duration against thresholds."""
        if duration_ms >= self.critical_ms:
            return BudgetSeverity.CRITICAL
        elif duration_ms >= self.warning_ms:
            return BudgetSeverity.WARNING
        return BudgetSeverity.OK
    
    def is_exceeded(self, duration_ms: float) -> bool:
        """Check if budget is exceeded (warning or critical)."""
        return duration_ms >= self.warning_ms


# Pre-defined performance budgets
PERFORMANCE_BUDGETS: Dict[str, PerformanceBudget] = {
    "ml_inference": PerformanceBudget(
        name="ml_inference",
        warning_ms=5.0,
        critical_ms=10.0,
        description="ML model inference latency",
        dls_component="enforcement_latency",
    ),
    "enforcement_loop": PerformanceBudget(
        name="enforcement_loop",
        warning_ms=50.0,
        critical_ms=100.0,
        description="Full enforcement decision loop",
        dls_component="enforcement_latency",
    ),
    "telemetry_batch": PerformanceBudget(
        name="telemetry_batch",
        warning_ms=10.0,
        critical_ms=20.0,
        description="Telemetry batch flush",
        dls_component="telemetry_coverage",
    ),
    "crown_jewel": PerformanceBudget(
        name="crown_jewel",
        warning_ms=100.0,
        critical_ms=200.0,
        description="Crown jewel API protection",
        dls_component="detection_accuracy",
    ),
    "token_validation": PerformanceBudget(
        name="token_validation",
        warning_ms=20.0,
        critical_ms=40.0,
        description="Token validation and refresh",
        dls_component="policy_delivery",
    ),
    "policy_delivery": PerformanceBudget(
        name="policy_delivery",
        warning_ms=30.0,
        critical_ms=60.0,
        description="Policy push and application",
        dls_component="policy_delivery",
    ),
}


# =============================================================================
# Budget Violation Tracking
# =============================================================================

@dataclass
class BudgetViolation:
    """
    Record of a budget violation event.
    
    Attributes:
        budget_name: Name of the violated budget
        duration_ms: Actual duration in milliseconds
        threshold_ms: Threshold that was exceeded
        severity: Violation severity
        timestamp: When violation occurred
        context: Additional context (operation, labels, etc.)
    """
    budget_name: str
    duration_ms: float
    threshold_ms: float
    severity: BudgetSeverity
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "budget_name": self.budget_name,
            "duration_ms": self.duration_ms,
            "threshold_ms": self.threshold_ms,
            "severity": self.severity.value,
            "timestamp": self.timestamp,
            "context": self.context,
        }


# Violation callback type
ViolationCallback = Callable[[BudgetViolation], None]

# Global violation handlers
_violation_handlers: List[ViolationCallback] = []


def register_violation_handler(handler: ViolationCallback) -> None:
    """Register a handler for budget violations."""
    _violation_handlers.append(handler)


def unregister_violation_handler(handler: ViolationCallback) -> None:
    """Unregister a violation handler."""
    if handler in _violation_handlers:
        _violation_handlers.remove(handler)


def _emit_violation(violation: BudgetViolation) -> None:
    """Emit violation to all registered handlers."""
    for handler in _violation_handlers:
        try:
            handler(violation)
        except Exception:
            pass  # Don't let handler errors break enforcement


# =============================================================================
# Budget Tracker
# =============================================================================

class BudgetTracker:
    """
    Tracks budget violations and generates reports.
    
    Thread-safe collection of violation metrics for
    analysis and alerting.
    """
    
    def __init__(self, max_violations: int = 10_000):
        self._violations: List[BudgetViolation] = []
        self._max_violations = max_violations
        self._lock = threading.Lock()
        
        # Summary statistics
        self._stats: Dict[str, Dict[str, Any]] = {}
    
    def record_violation(self, violation: BudgetViolation) -> None:
        """Record a budget violation."""
        with self._lock:
            self._violations.append(violation)
            
            # Update stats
            name = violation.budget_name
            if name not in self._stats:
                self._stats[name] = {
                    "total_violations": 0,
                    "warning_count": 0,
                    "critical_count": 0,
                    "max_duration_ms": 0.0,
                    "total_duration_ms": 0.0,
                }
            
            stats = self._stats[name]
            stats["total_violations"] += 1
            stats["total_duration_ms"] += violation.duration_ms
            stats["max_duration_ms"] = max(
                stats["max_duration_ms"],
                violation.duration_ms
            )
            
            if violation.severity == BudgetSeverity.WARNING:
                stats["warning_count"] += 1
            elif violation.severity == BudgetSeverity.CRITICAL:
                stats["critical_count"] += 1
            
            # Trim old violations
            if len(self._violations) > self._max_violations:
                self._violations = self._violations[-self._max_violations:]
    
    def get_violations(
        self,
        budget_name: Optional[str] = None,
        severity: Optional[BudgetSeverity] = None,
        since: Optional[float] = None,
    ) -> List[BudgetViolation]:
        """Query violations with optional filters."""
        with self._lock:
            results = self._violations
            
            if budget_name:
                results = [v for v in results if v.budget_name == budget_name]
            if severity:
                results = [v for v in results if v.severity == severity]
            if since:
                results = [v for v in results if v.timestamp >= since]
            
            return results.copy()
    
    def get_stats(self, budget_name: Optional[str] = None) -> Dict[str, Any]:
        """Get violation statistics."""
        with self._lock:
            if budget_name:
                return self._stats.get(budget_name, {}).copy()
            return {k: v.copy() for k, v in self._stats.items()}
    
    def generate_report(self, window_sec: float = 300.0) -> Dict[str, Any]:
        """
        Generate a budget health report.
        
        Args:
            window_sec: Time window for recent violations
            
        Returns:
            Report with summary and recommendations
        """
        cutoff = time.time() - window_sec
        recent = self.get_violations(since=cutoff)
        
        report = {
            "window_sec": window_sec,
            "total_violations": len(recent),
            "by_severity": {
                "warning": len([v for v in recent if v.severity == BudgetSeverity.WARNING]),
                "critical": len([v for v in recent if v.severity == BudgetSeverity.CRITICAL]),
            },
            "by_budget": {},
            "recommendations": [],
        }
        
        # Group by budget
        for v in recent:
            if v.budget_name not in report["by_budget"]:
                report["by_budget"][v.budget_name] = {
                    "count": 0,
                    "max_ms": 0,
                    "avg_ms": 0,
                    "durations": [],
                }
            
            budget_report = report["by_budget"][v.budget_name]
            budget_report["count"] += 1
            budget_report["durations"].append(v.duration_ms)
            budget_report["max_ms"] = max(budget_report["max_ms"], v.duration_ms)
        
        # Calculate averages and generate recommendations
        for name, data in report["by_budget"].items():
            if data["durations"]:
                data["avg_ms"] = sum(data["durations"]) / len(data["durations"])
            del data["durations"]  # Don't include raw data
            
            # Generate recommendations
            budget = PERFORMANCE_BUDGETS.get(name)
            if budget and data["count"] > 5:
                if data["avg_ms"] > budget.critical_ms:
                    report["recommendations"].append(
                        f"CRITICAL: {name} consistently exceeds critical threshold. "
                        f"Avg: {data['avg_ms']:.1f}ms vs budget: {budget.critical_ms}ms"
                    )
                elif data["avg_ms"] > budget.warning_ms:
                    report["recommendations"].append(
                        f"WARNING: {name} often exceeds warning threshold. "
                        f"Avg: {data['avg_ms']:.1f}ms vs budget: {budget.warning_ms}ms"
                    )
        
        return report
    
    def clear(self) -> None:
        """Clear all violations and stats."""
        with self._lock:
            self._violations.clear()
            self._stats.clear()


# Global tracker instance
_global_tracker = BudgetTracker()


def get_global_tracker() -> BudgetTracker:
    """Get the global budget tracker."""
    return _global_tracker


# =============================================================================
# Budget Enforcement Decorator
# =============================================================================

F = TypeVar("F", bound=Callable[..., Any])


def track_budget(
    budget: Union[str, PerformanceBudget],
    emit_on_warning: bool = True,
    emit_on_critical: bool = True,
    include_context: bool = True,
) -> Callable[[F], F]:
    """
    Decorator to track performance budget for a function.
    
    Supports both sync and async functions.
    
    Args:
        budget: Budget name or PerformanceBudget instance
        emit_on_warning: Emit violation event on warning
        emit_on_critical: Emit violation event on critical
        include_context: Include function args in context
        
    Example:
        @track_budget("ml_inference")
        def predict(model, features):
            return model.predict(features)
            
        @track_budget("enforcement_loop", emit_on_warning=False)
        async def enforce(request):
            ...
    """
    # Resolve budget
    if isinstance(budget, str):
        budget_obj = PERFORMANCE_BUDGETS.get(budget)
        if not budget_obj:
            raise ValueError(f"Unknown budget: {budget}")
    else:
        budget_obj = budget
    
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                duration_ms = (time.perf_counter() - start) * 1000
                _check_and_record(
                    budget_obj, duration_ms, func.__name__,
                    args if include_context else None,
                    kwargs if include_context else None,
                    emit_on_warning, emit_on_critical,
                )
        
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                return await func(*args, **kwargs)
            finally:
                duration_ms = (time.perf_counter() - start) * 1000
                _check_and_record(
                    budget_obj, duration_ms, func.__name__,
                    args if include_context else None,
                    kwargs if include_context else None,
                    emit_on_warning, emit_on_critical,
                )
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore
    
    return decorator


def _check_and_record(
    budget: PerformanceBudget,
    duration_ms: float,
    func_name: str,
    args: Optional[tuple],
    kwargs: Optional[dict],
    emit_on_warning: bool,
    emit_on_critical: bool,
) -> None:
    """Check budget and record violation if needed."""
    severity = budget.check(duration_ms)
    
    if severity == BudgetSeverity.OK:
        return
    
    # Determine threshold
    threshold_ms = (
        budget.critical_ms if severity == BudgetSeverity.CRITICAL
        else budget.warning_ms
    )
    
    # Build context
    context: Dict[str, Any] = {"function": func_name}
    if args:
        # Only include serializable args
        context["args_count"] = len(args)
    if kwargs:
        context["kwargs_keys"] = list(kwargs.keys())
    
    violation = BudgetViolation(
        budget_name=budget.name,
        duration_ms=duration_ms,
        threshold_ms=threshold_ms,
        severity=severity,
        context=context,
    )
    
    # Record to tracker
    _global_tracker.record_violation(violation)
    
    # Emit to handlers
    should_emit = (
        (severity == BudgetSeverity.WARNING and emit_on_warning) or
        (severity == BudgetSeverity.CRITICAL and emit_on_critical)
    )
    
    if should_emit:
        _emit_violation(violation)


# =============================================================================
# Context Manager for Budget Tracking
# =============================================================================

class BudgetScope:
    """
    Context manager for budget tracking.
    
    Example:
        with BudgetScope("ml_inference") as scope:
            result = model.predict(features)
        print(f"Took {scope.duration_ms:.2f}ms")
    """
    
    def __init__(
        self,
        budget: Union[str, PerformanceBudget],
        operation: str = "",
        emit_violations: bool = True,
    ):
        if isinstance(budget, str):
            budget_obj = PERFORMANCE_BUDGETS.get(budget)
            if not budget_obj:
                raise ValueError(f"Unknown budget: {budget}")
            self._budget = budget_obj
        else:
            self._budget = budget
        
        self._operation = operation
        self._emit_violations = emit_violations
        self._start: float = 0
        self.duration_ms: float = 0
        self.severity: BudgetSeverity = BudgetSeverity.OK
    
    def __enter__(self) -> "BudgetScope":
        self._start = time.perf_counter()
        return self
    
    def __exit__(self, *args: Any) -> None:
        self.duration_ms = (time.perf_counter() - self._start) * 1000
        self.severity = self._budget.check(self.duration_ms)
        
        if self.severity != BudgetSeverity.OK:
            violation = BudgetViolation(
                budget_name=self._budget.name,
                duration_ms=self.duration_ms,
                threshold_ms=(
                    self._budget.critical_ms
                    if self.severity == BudgetSeverity.CRITICAL
                    else self._budget.warning_ms
                ),
                severity=self.severity,
                context={"operation": self._operation} if self._operation else {},
            )
            
            _global_tracker.record_violation(violation)
            
            if self._emit_violations:
                _emit_violation(violation)
    
    @property
    def exceeded(self) -> bool:
        """Check if budget was exceeded."""
        return self.severity != BudgetSeverity.OK


class AsyncBudgetScope:
    """
    Async context manager for budget tracking.
    
    Example:
        async with AsyncBudgetScope("enforcement_loop") as scope:
            await enforce_policy(request)
    """
    
    def __init__(
        self,
        budget: Union[str, PerformanceBudget],
        operation: str = "",
        emit_violations: bool = True,
    ):
        self._sync_scope = BudgetScope(budget, operation, emit_violations)
    
    async def __aenter__(self) -> "AsyncBudgetScope":
        self._sync_scope.__enter__()
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        self._sync_scope.__exit__(*args)
    
    @property
    def duration_ms(self) -> float:
        return self._sync_scope.duration_ms
    
    @property
    def severity(self) -> BudgetSeverity:
        return self._sync_scope.severity
    
    @property
    def exceeded(self) -> bool:
        return self._sync_scope.exceeded


# =============================================================================
# Async Correlation Context (contextvars)
# =============================================================================

# Context variables for async correlation
correlation_id_var: ContextVar[Optional[str]] = ContextVar(
    "correlation_id", default=None
)
tenant_id_var: ContextVar[Optional[str]] = ContextVar(
    "tenant_id", default=None
)
tier_var: ContextVar[Optional[str]] = ContextVar(
    "tier", default=None
)


def get_async_correlation_id() -> Optional[str]:
    """Get correlation ID from async context."""
    return correlation_id_var.get()


def set_async_correlation_id(correlation_id: str) -> None:
    """Set correlation ID in async context."""
    correlation_id_var.set(correlation_id)


def get_async_tenant_id() -> Optional[str]:
    """Get tenant ID from async context."""
    return tenant_id_var.get()


def set_async_tenant_id(tenant_id: str) -> None:
    """Set tenant ID in async context."""
    tenant_id_var.set(tenant_id)


def get_async_tier() -> Optional[str]:
    """Get tier from async context."""
    return tier_var.get()


def set_async_tier(tier: str) -> None:
    """Set tier in async context."""
    tier_var.set(tier)


class AsyncCorrelationScope:
    """
    Async context manager for correlation scope.
    
    Propagates correlation context across async tasks.
    
    Example:
        async with AsyncCorrelationScope(
            correlation_id="req-123",
            tenant_id="tenant-456",
            tier="pro"
        ):
            await process_request()
            await emit_telemetry()  # Will inherit context
    """
    
    def __init__(
        self,
        correlation_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        tier: Optional[str] = None,
    ):
        self._correlation_id = correlation_id or str(__import__("uuid").uuid4())
        self._tenant_id = tenant_id
        self._tier = tier
        
        self._old_correlation: Optional[str] = None
        self._old_tenant: Optional[str] = None
        self._old_tier: Optional[str] = None
    
    async def __aenter__(self) -> "AsyncCorrelationScope":
        self._old_correlation = correlation_id_var.get()
        self._old_tenant = tenant_id_var.get()
        self._old_tier = tier_var.get()
        
        correlation_id_var.set(self._correlation_id)
        if self._tenant_id:
            tenant_id_var.set(self._tenant_id)
        if self._tier:
            tier_var.set(self._tier)
        
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        correlation_id_var.set(self._old_correlation)
        tenant_id_var.set(self._old_tenant)
        tier_var.set(self._old_tier)
    
    @property
    def correlation_id(self) -> str:
        return self._correlation_id
