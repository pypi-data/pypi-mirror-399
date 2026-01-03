"""
KRL Real-Time Limits Gateway - DEPRECATED

⚠️ DEPRECATION WARNING (Dec 2025):
This module has been moved to krl-premium-backend.
Import from: app.services.billing.limits_gateway

This stub remains for backward compatibility but will be removed in v2.0.
"""

from __future__ import annotations

import warnings
warnings.warn(
    "krl_data_connectors.core.billing.limits_gateway is deprecated. "
    "This module has moved to krl-premium-backend. "
    "Import from 'app.services.billing.limits_gateway' instead.",
    DeprecationWarning,
    stacklevel=2
)

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, UTC
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from uuid import uuid4

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class LimitType(str, Enum):
    """Types of limits."""
    RATE_LIMIT = "rate_limit"         # Requests per time window
    QUOTA_LIMIT = "quota_limit"       # Total usage per period
    CONCURRENT_LIMIT = "concurrent"    # Concurrent operations
    BANDWIDTH_LIMIT = "bandwidth"      # Data transfer
    COMPUTE_LIMIT = "compute"          # Compute resources


class EnforcementMode(str, Enum):
    """Enforcement modes."""
    ENFORCE = "enforce"         # Block when limit exceeded
    WARN = "warn"              # Allow but log warning
    MONITOR = "monitor"        # Only track, no enforcement
    DISABLED = "disabled"      # No checking


class LimitAction(str, Enum):
    """Actions on limit enforcement."""
    ALLOW = "allow"
    THROTTLE = "throttle"
    QUEUE = "queue"
    REJECT = "reject"
    DEGRADE = "degrade"


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Rejecting requests
    HALF_OPEN = "half_open"  # Testing recovery


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class LimitDefinition:
    """Limit definition."""
    limit_id: str
    name: str
    limit_type: LimitType
    value: int
    window_seconds: int
    burst_allowance: float = 1.0  # Multiplier for burst
    enforce_mode: EnforcementMode = EnforcementMode.ENFORCE
    overage_action: LimitAction = LimitAction.REJECT
    tier_overrides: Dict[str, int] = field(default_factory=dict)  # tier -> limit value


@dataclass
class LimitCheck:
    """Result of limit check."""
    allowed: bool
    limit_id: str
    limit_type: LimitType
    current_usage: int
    limit_value: int
    remaining: int
    reset_at: datetime
    action: LimitAction
    retry_after_seconds: Optional[int] = None
    message: str = ""


@dataclass
class UsageSnapshot:
    """Point-in-time usage snapshot."""
    customer_id: str
    tier: str
    snapshots: Dict[str, int]  # limit_id -> current_usage
    timestamp: datetime


@dataclass
class GatewayContext:
    """Request context for gateway."""
    request_id: str
    customer_id: str
    tenant_id: str
    tier: str
    endpoint: str
    method: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_size_bytes: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GatewayResponse:
    """Gateway enforcement response."""
    allowed: bool
    request_id: str
    checks: List[LimitCheck]
    primary_action: LimitAction
    headers: Dict[str, str] = field(default_factory=dict)
    retry_after: Optional[int] = None
    degraded_mode: bool = False


# =============================================================================
# Default Limit Definitions
# =============================================================================

DEFAULT_LIMITS: Dict[str, LimitDefinition] = {
    "api_rate_limit": LimitDefinition(
        limit_id="api_rate_limit",
        name="API Rate Limit",
        limit_type=LimitType.RATE_LIMIT,
        value=100,  # requests per minute
        window_seconds=60,
        burst_allowance=1.5,
        tier_overrides={
            "community": 60,
            "pro": 300,
            "enterprise": 1000,
        },
    ),
    "daily_quota": LimitDefinition(
        limit_id="daily_quota",
        name="Daily API Quota",
        limit_type=LimitType.QUOTA_LIMIT,
        value=10000,
        window_seconds=86400,  # 24 hours
        tier_overrides={
            "community": 1000,
            "pro": 50000,
            "enterprise": 500000,
        },
    ),
    "concurrent_requests": LimitDefinition(
        limit_id="concurrent_requests",
        name="Concurrent Requests",
        limit_type=LimitType.CONCURRENT_LIMIT,
        value=10,
        window_seconds=0,  # No window for concurrent
        tier_overrides={
            "community": 5,
            "pro": 25,
            "enterprise": 100,
        },
    ),
    "bandwidth_limit": LimitDefinition(
        limit_id="bandwidth_limit",
        name="Bandwidth Limit",
        limit_type=LimitType.BANDWIDTH_LIMIT,
        value=100_000_000,  # 100MB per hour
        window_seconds=3600,
        tier_overrides={
            "community": 10_000_000,
            "pro": 500_000_000,
            "enterprise": 5_000_000_000,
        },
    ),
}


# =============================================================================
# Token Bucket Rate Limiter
# =============================================================================

class TokenBucket:
    """
    Token bucket rate limiter implementation.
    
    Allows burst traffic while maintaining average rate.
    """
    
    def __init__(
        self,
        rate: float,
        capacity: float,
    ):
        self.rate = rate  # tokens per second
        self.capacity = capacity
        self._tokens = capacity
        self._last_update = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: float = 1.0) -> bool:
        """Try to acquire tokens."""
        async with self._lock:
            now = time.monotonic()
            
            # Refill tokens
            elapsed = now - self._last_update
            self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
            self._last_update = now
            
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False
    
    @property
    def available(self) -> float:
        """Get available tokens."""
        now = time.monotonic()
        elapsed = now - self._last_update
        return min(self.capacity, self._tokens + elapsed * self.rate)


# =============================================================================
# Sliding Window Counter
# =============================================================================

class SlidingWindowCounter:
    """
    Sliding window counter for quota tracking.
    
    More accurate than fixed windows for rate limiting.
    """
    
    def __init__(self, window_seconds: int):
        self.window_seconds = window_seconds
        self._counts: Dict[str, List[Tuple[float, int]]] = {}  # key -> [(timestamp, count), ...]
    
    def increment(self, key: str, count: int = 1) -> int:
        """Increment counter and return total in window."""
        now = time.time()
        
        if key not in self._counts:
            self._counts[key] = []
        
        # Add new count
        self._counts[key].append((now, count))
        
        # Clean old entries
        cutoff = now - self.window_seconds
        self._counts[key] = [
            (ts, c) for ts, c in self._counts[key]
            if ts > cutoff
        ]
        
        return sum(c for _, c in self._counts[key])
    
    def get_count(self, key: str) -> int:
        """Get current count in window."""
        now = time.time()
        cutoff = now - self.window_seconds
        
        entries = self._counts.get(key, [])
        return sum(c for ts, c in entries if ts > cutoff)
    
    def get_reset_time(self, key: str) -> datetime:
        """Get when the window resets."""
        entries = self._counts.get(key, [])
        if not entries:
            return datetime.now(timezone.utc)
        
        oldest = min(ts for ts, _ in entries)
        reset_time = oldest + self.window_seconds
        return datetime.fromtimestamp(reset_time, tz=timezone.utc)


# =============================================================================
# Circuit Breaker
# =============================================================================

class CircuitBreaker:
    """
    Circuit breaker for graceful degradation.
    
    Prevents cascade failures by failing fast.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        half_open_requests: int = 3,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_requests = half_open_requests
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_successes = 0
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        if self._state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self._last_failure_time:
                elapsed = time.time() - self._last_failure_time
                if elapsed >= self.recovery_timeout:
                    self._state = CircuitState.HALF_OPEN
                    self._half_open_successes = 0
        return self._state
    
    def allow_request(self) -> bool:
        """Check if request should be allowed."""
        state = self.state
        if state == CircuitState.CLOSED:
            return True
        elif state == CircuitState.HALF_OPEN:
            return True  # Allow test requests
        return False
    
    def record_success(self) -> None:
        """Record successful request."""
        if self._state == CircuitState.HALF_OPEN:
            self._half_open_successes += 1
            if self._half_open_successes >= self.half_open_requests:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
    
    def record_failure(self) -> None:
        """Record failed request."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
    
    def reset(self) -> None:
        """Reset circuit breaker."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._half_open_successes = 0


# =============================================================================
# Limits Gateway
# =============================================================================

class LimitsGateway:
    """
    Real-time limits enforcement gateway.
    
    Coordinates:
    - Rate limiting
    - Quota tracking
    - Concurrent request limiting
    - Circuit breaker protection
    """
    
    def __init__(
        self,
        limits: Optional[Dict[str, LimitDefinition]] = None,
        enforcement_mode: EnforcementMode = EnforcementMode.ENFORCE,
    ):
        self._limits = limits or DEFAULT_LIMITS.copy()
        self.enforcement_mode = enforcement_mode
        
        # Counters per limit
        self._counters: Dict[str, SlidingWindowCounter] = {}
        self._token_buckets: Dict[str, TokenBucket] = {}
        self._concurrent: Dict[str, int] = {}  # customer_id -> current concurrent
        
        # Circuit breakers per customer
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Metrics
        self._metrics = {
            "total_checks": 0,
            "allowed": 0,
            "rejected": 0,
            "throttled": 0,
        }
        
        # Initialize counters
        for limit_id, limit_def in self._limits.items():
            if limit_def.limit_type == LimitType.RATE_LIMIT:
                pass  # Token buckets created per customer
            else:
                self._counters[limit_id] = SlidingWindowCounter(limit_def.window_seconds)
    
    async def check_limits(
        self,
        context: GatewayContext,
    ) -> GatewayResponse:
        """Check all limits for request."""
        self._metrics["total_checks"] += 1
        
        checks: List[LimitCheck] = []
        all_allowed = True
        primary_action = LimitAction.ALLOW
        retry_after = None
        degraded = False
        
        # Check circuit breaker first
        cb = self._get_circuit_breaker(context.customer_id)
        if not cb.allow_request():
            all_allowed = False
            primary_action = LimitAction.REJECT
            retry_after = cb.recovery_timeout
        
        # Check each limit
        for limit_id, limit_def in self._limits.items():
            if limit_def.enforce_mode == EnforcementMode.DISABLED:
                continue
            
            check = await self._check_single_limit(context, limit_def)
            checks.append(check)
            
            if not check.allowed:
                all_allowed = False
                if check.action == LimitAction.REJECT:
                    primary_action = LimitAction.REJECT
                elif check.action == LimitAction.THROTTLE and primary_action == LimitAction.ALLOW:
                    primary_action = LimitAction.THROTTLE
                elif check.action == LimitAction.DEGRADE:
                    degraded = True
                
                if check.retry_after_seconds:
                    if retry_after is None or check.retry_after_seconds < retry_after:
                        retry_after = check.retry_after_seconds
        
        # Build response headers
        headers = self._build_response_headers(checks)
        if retry_after:
            headers["Retry-After"] = str(retry_after)
        
        # Update metrics
        if all_allowed:
            self._metrics["allowed"] += 1
        elif primary_action == LimitAction.THROTTLE:
            self._metrics["throttled"] += 1
        else:
            self._metrics["rejected"] += 1
        
        return GatewayResponse(
            allowed=all_allowed or self.enforcement_mode != EnforcementMode.ENFORCE,
            request_id=context.request_id,
            checks=checks,
            primary_action=primary_action,
            headers=headers,
            retry_after=retry_after,
            degraded_mode=degraded,
        )
    
    async def _check_single_limit(
        self,
        context: GatewayContext,
        limit_def: LimitDefinition,
    ) -> LimitCheck:
        """Check single limit definition."""
        # Get tier-specific limit
        limit_value = limit_def.tier_overrides.get(context.tier, limit_def.value)
        limit_value_with_burst = int(limit_value * limit_def.burst_allowance)
        
        key = f"{context.customer_id}:{limit_def.limit_id}"
        
        if limit_def.limit_type == LimitType.RATE_LIMIT:
            return await self._check_rate_limit(
                key, context, limit_def, limit_value, limit_value_with_burst
            )
        elif limit_def.limit_type == LimitType.QUOTA_LIMIT:
            return self._check_quota_limit(
                key, context, limit_def, limit_value
            )
        elif limit_def.limit_type == LimitType.CONCURRENT_LIMIT:
            return self._check_concurrent_limit(
                context.customer_id, limit_def, limit_value
            )
        elif limit_def.limit_type == LimitType.BANDWIDTH_LIMIT:
            return self._check_bandwidth_limit(
                key, context, limit_def, limit_value
            )
        
        # Default allow
        return LimitCheck(
            allowed=True,
            limit_id=limit_def.limit_id,
            limit_type=limit_def.limit_type,
            current_usage=0,
            limit_value=limit_value,
            remaining=limit_value,
            reset_at=datetime.now(timezone.utc) + timedelta(seconds=limit_def.window_seconds),
            action=LimitAction.ALLOW,
        )
    
    async def _check_rate_limit(
        self,
        key: str,
        context: GatewayContext,
        limit_def: LimitDefinition,
        limit_value: int,
        burst_value: int,
    ) -> LimitCheck:
        """Check rate limit using token bucket."""
        # Get or create token bucket
        if key not in self._token_buckets:
            rate = limit_value / limit_def.window_seconds
            self._token_buckets[key] = TokenBucket(rate=rate, capacity=burst_value)
        
        bucket = self._token_buckets[key]
        allowed = await bucket.acquire()
        
        available = int(bucket.available)
        reset_seconds = int((burst_value - available) / bucket.rate) if bucket.rate > 0 else 60
        
        return LimitCheck(
            allowed=allowed,
            limit_id=limit_def.limit_id,
            limit_type=limit_def.limit_type,
            current_usage=burst_value - available,
            limit_value=burst_value,
            remaining=available,
            reset_at=datetime.now(timezone.utc) + timedelta(seconds=reset_seconds),
            action=LimitAction.ALLOW if allowed else limit_def.overage_action,
            retry_after_seconds=None if allowed else max(1, int(1 / bucket.rate)),
            message="" if allowed else "Rate limit exceeded",
        )
    
    def _check_quota_limit(
        self,
        key: str,
        context: GatewayContext,
        limit_def: LimitDefinition,
        limit_value: int,
    ) -> LimitCheck:
        """Check quota limit."""
        counter = self._counters.get(limit_def.limit_id)
        if not counter:
            counter = SlidingWindowCounter(limit_def.window_seconds)
            self._counters[limit_def.limit_id] = counter
        
        current = counter.get_count(key)
        allowed = current < limit_value
        
        if allowed:
            counter.increment(key)
            current += 1
        
        return LimitCheck(
            allowed=allowed,
            limit_id=limit_def.limit_id,
            limit_type=limit_def.limit_type,
            current_usage=current,
            limit_value=limit_value,
            remaining=max(0, limit_value - current),
            reset_at=counter.get_reset_time(key),
            action=LimitAction.ALLOW if allowed else limit_def.overage_action,
            message="" if allowed else "Quota exceeded",
        )
    
    def _check_concurrent_limit(
        self,
        customer_id: str,
        limit_def: LimitDefinition,
        limit_value: int,
    ) -> LimitCheck:
        """Check concurrent request limit."""
        current = self._concurrent.get(customer_id, 0)
        allowed = current < limit_value
        
        return LimitCheck(
            allowed=allowed,
            limit_id=limit_def.limit_id,
            limit_type=limit_def.limit_type,
            current_usage=current,
            limit_value=limit_value,
            remaining=max(0, limit_value - current),
            reset_at=datetime.now(timezone.utc),  # No window for concurrent
            action=LimitAction.ALLOW if allowed else LimitAction.QUEUE,
            message="" if allowed else "Too many concurrent requests",
        )
    
    def _check_bandwidth_limit(
        self,
        key: str,
        context: GatewayContext,
        limit_def: LimitDefinition,
        limit_value: int,
    ) -> LimitCheck:
        """Check bandwidth limit."""
        counter = self._counters.get(limit_def.limit_id)
        if not counter:
            counter = SlidingWindowCounter(limit_def.window_seconds)
            self._counters[limit_def.limit_id] = counter
        
        current = counter.get_count(key)
        allowed = current + context.request_size_bytes <= limit_value
        
        if allowed:
            counter.increment(key, context.request_size_bytes)
            current += context.request_size_bytes
        
        return LimitCheck(
            allowed=allowed,
            limit_id=limit_def.limit_id,
            limit_type=limit_def.limit_type,
            current_usage=current,
            limit_value=limit_value,
            remaining=max(0, limit_value - current),
            reset_at=counter.get_reset_time(key),
            action=LimitAction.ALLOW if allowed else limit_def.overage_action,
            message="" if allowed else "Bandwidth limit exceeded",
        )
    
    def _get_circuit_breaker(self, customer_id: str) -> CircuitBreaker:
        """Get or create circuit breaker for customer."""
        if customer_id not in self._circuit_breakers:
            self._circuit_breakers[customer_id] = CircuitBreaker()
        return self._circuit_breakers[customer_id]
    
    def _build_response_headers(self, checks: List[LimitCheck]) -> Dict[str, str]:
        """Build rate limit response headers."""
        headers = {}
        
        # Use the most restrictive rate limit for headers
        rate_limits = [c for c in checks if c.limit_type == LimitType.RATE_LIMIT]
        if rate_limits:
            most_restrictive = min(rate_limits, key=lambda x: x.remaining)
            headers["X-RateLimit-Limit"] = str(most_restrictive.limit_value)
            headers["X-RateLimit-Remaining"] = str(most_restrictive.remaining)
            headers["X-RateLimit-Reset"] = str(int(most_restrictive.reset_at.timestamp()))
        
        return headers
    
    def acquire_concurrent(self, customer_id: str) -> bool:
        """Acquire concurrent slot."""
        limit_def = self._limits.get("concurrent_requests")
        if not limit_def:
            return True
        
        current = self._concurrent.get(customer_id, 0)
        limit = limit_def.value
        
        if current < limit:
            self._concurrent[customer_id] = current + 1
            return True
        return False
    
    def release_concurrent(self, customer_id: str) -> None:
        """Release concurrent slot."""
        current = self._concurrent.get(customer_id, 0)
        if current > 0:
            self._concurrent[customer_id] = current - 1
    
    def get_usage_snapshot(self, customer_id: str, tier: str) -> UsageSnapshot:
        """Get usage snapshot for customer."""
        snapshots = {}
        
        for limit_id, counter in self._counters.items():
            key = f"{customer_id}:{limit_id}"
            snapshots[limit_id] = counter.get_count(key)
        
        return UsageSnapshot(
            customer_id=customer_id,
            tier=tier,
            snapshots=snapshots,
            timestamp=datetime.now(timezone.utc),
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get gateway metrics."""
        return {
            **self._metrics,
            "circuit_breakers": {
                cid: cb.state.value
                for cid, cb in self._circuit_breakers.items()
            },
        }


# =============================================================================
# Factory Function
# =============================================================================

def create_limits_gateway(
    limits: Optional[Dict[str, LimitDefinition]] = None,
    enforcement_mode: EnforcementMode = EnforcementMode.ENFORCE,
) -> LimitsGateway:
    """Create configured LimitsGateway."""
    return LimitsGateway(limits=limits, enforcement_mode=enforcement_mode)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "LimitType",
    "EnforcementMode",
    "LimitAction",
    "CircuitState",
    # Data Classes
    "LimitDefinition",
    "LimitCheck",
    "UsageSnapshot",
    "GatewayContext",
    "GatewayResponse",
    # Constants
    "DEFAULT_LIMITS",
    # Classes
    "TokenBucket",
    "SlidingWindowCounter",
    "CircuitBreaker",
    "LimitsGateway",
    # Factory
    "create_limits_gateway",
]
