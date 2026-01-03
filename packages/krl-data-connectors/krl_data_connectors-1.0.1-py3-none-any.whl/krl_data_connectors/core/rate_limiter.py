# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Rate Limiting & Throttling Module for Federal Economic Data APIs.

Implements agency-specific rate limiting, token bucket algorithms, and
exponential backoff strategies compliant with published API regulations.

Supported Agencies:
    - FRED (Federal Reserve Bank of St. Louis): ~120 req/min
    - BLS (Bureau of Labor Statistics): 50 req/10s burst, 500/day (registered)
    - BEA (Bureau of Economic Analysis): 100 req/min, 100 MB/min
    - Census Bureau: 500/day per IP (keyless), monitored with key

Usage:
    from krl_data_connectors.core.rate_limiter import RateLimiter, AgencyConfig
    
    # Create limiter with FRED defaults
    limiter = RateLimiter(AgencyConfig.FRED)
    
    # Acquire permission before making request
    limiter.acquire()  # Blocks if rate limit would be exceeded
    
    # Or check without blocking
    if limiter.try_acquire():
        make_request()
    else:
        print("Rate limited, try later")

References:
    - FRED: https://fred.stlouisfed.org/docs/api/api_key.html
    - BLS: https://www.bls.gov/developers/api_signature_v2.htm
    - BEA: https://apps.bea.gov/API/signup/index.cfm
    - Census: https://www.census.gov/data/developers/guidance.html
"""

import json
import logging
import os
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, UTC
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union

logger = logging.getLogger(__name__)


# =============================================================================
# API LIMITS SPECIFICATION (Machine-Readable)
# =============================================================================

API_LIMITS_SPEC: Dict[str, Any] = {
    "FRED": {
        "rate_limits": {
            "requests_per_minute": 120,
            "http_on_exceed": 429,
            "retry_strategy": {
                "type": "exponential_backoff",
                "base_delay_ms": 500,
                "max_delay_ms": 10000,
            },
        },
        "quotas": {"daily_limit": None},
        "request_caps": {
            "notes": "No formal cap; series-level restrictions exist but not quota-based."
        },
        "regulations": {
            "api_key_required": True,
            "attribution_required": True,
            "prohibited": [
                "replicating FRED or ALFRED services",
                "misleading use of FRED trademarks",
            ],
            "copyright_notes": "Some series governed by third-party rights.",
        },
    },
    "BLS": {
        "unregistered": {
            "rate_limits": {"burst_limit_requests": 50, "burst_window_seconds": 10},
            "quotas": {"daily_requests": 25},
            "request_caps": {"max_series": 25, "max_years_per_request": 10},
        },
        "registered": {
            "rate_limits": {"burst_limit_requests": 50, "burst_window_seconds": 10},
            "quotas": {"daily_requests": 500},
            "request_caps": {"max_series": 50, "max_years_per_request": 20},
        },
        "regulations": {
            "branding_restrictions": True,
            "analysis_disclaimer_required": True,
            "metadata_inconsistency_possible": True,
        },
    },
    "BEA": {
        "rate_limits": {
            "requests_per_minute": 100,
            "data_volume_mb_per_minute": 100,
            "error_threshold_per_minute": 30,
            "error_penalty": {
                "condition": ">30_errors_per_minute",
                "lockout_duration_minutes": 60,
            },
        },
        "quotas": {"daily_limit": None},
        "request_caps": {
            "notes": "No fixed request-size cap; volumes governed by MB/min rule."
        },
        "regulations": {
            "userid_required": True,
            "excess_polling_prohibited": True,
            "dynamic_throttle_possible": True,
        },
    },
    "Census": {
        "rate_limits": {
            "keyless_daily_requests_per_ip": 500,
            "with_key": {"monitored": True, "soft_limits": True},
        },
        "request_caps": {"max_variables_per_request": 50},
        "regulations": {
            "prohibited": [
                "attempted re-identification of individuals, households, or businesses"
            ],
            "mandatory_disclaimer": True,
            "breach_reporting_required": True,
            "proxy_ip_aggregation": True,
        },
    },
}


# =============================================================================
# EXCEPTIONS
# =============================================================================


class RateLimitExceeded(Exception):
    """
    Raised when rate limit is exceeded and blocking is disabled.
    
    Attributes:
        agency: The agency whose limit was exceeded
        retry_after: Suggested wait time in seconds
        limit_type: Type of limit exceeded ('requests_per_minute', 'daily', 'burst')
    """

    def __init__(
        self,
        message: str,
        agency: str = None,
        retry_after: float = None,
        limit_type: str = None,
    ):
        super().__init__(message)
        self.agency = agency
        self.retry_after = retry_after
        self.limit_type = limit_type


class DailyQuotaExhausted(Exception):
    """
    Raised when daily request quota is exhausted.
    
    Attributes:
        agency: The agency whose quota was exhausted
        requests_made: Number of requests made today
        daily_limit: The daily limit
        resets_at: When the quota resets (midnight UTC)
    """

    def __init__(
        self,
        message: str,
        agency: str = None,
        requests_made: int = None,
        daily_limit: int = None,
        resets_at: datetime = None,
    ):
        super().__init__(message)
        self.agency = agency
        self.requests_made = requests_made
        self.daily_limit = daily_limit
        self.resets_at = resets_at


class ErrorThresholdExceeded(Exception):
    """
    Raised when error threshold triggers lockout (BEA-specific).
    
    Attributes:
        lockout_until: When the lockout expires
        errors_in_window: Number of errors that triggered lockout
    """

    def __init__(
        self,
        message: str,
        lockout_until: datetime = None,
        errors_in_window: int = None,
    ):
        super().__init__(message)
        self.lockout_until = lockout_until
        self.errors_in_window = errors_in_window


# =============================================================================
# AGENCY CONFIGURATION
# =============================================================================


class Agency(str, Enum):
    """Supported federal data agencies."""

    FRED = "FRED"
    BLS = "BLS"
    BEA = "BEA"
    CENSUS = "Census"


@dataclass
class AgencyConfig:
    """
    Rate limiting configuration for a specific agency.
    
    Attributes:
        agency: Agency identifier
        requests_per_minute: Maximum requests per minute (None = unlimited)
        requests_per_second: Maximum requests per second (None = unlimited)
        burst_limit: Maximum burst requests
        burst_window_seconds: Window for burst limiting
        daily_limit: Maximum requests per day (None = unlimited)
        min_request_interval_ms: Minimum milliseconds between requests
        base_delay_ms: Base delay for exponential backoff
        max_delay_ms: Maximum delay for exponential backoff
        error_threshold_per_minute: Errors per minute before lockout (BEA)
        lockout_duration_minutes: Lockout duration after error threshold (BEA)
        data_volume_mb_per_minute: Data volume limit in MB/min (BEA)
    """

    agency: Agency
    requests_per_minute: Optional[int] = None
    requests_per_second: Optional[float] = None
    burst_limit: Optional[int] = None
    burst_window_seconds: Optional[int] = None
    daily_limit: Optional[int] = None
    min_request_interval_ms: int = 0
    base_delay_ms: int = 500
    max_delay_ms: int = 10000
    error_threshold_per_minute: Optional[int] = None
    lockout_duration_minutes: Optional[int] = None
    data_volume_mb_per_minute: Optional[int] = None

    # Pre-configured agency defaults
    @classmethod
    def FRED(cls) -> "AgencyConfig":
        """FRED API configuration: ~120 req/min."""
        return cls(
            agency=Agency.FRED,
            requests_per_minute=120,
            requests_per_second=2.0,  # Conservative: 2 req/sec = 120/min
            min_request_interval_ms=500,  # 500ms between requests
            base_delay_ms=500,
            max_delay_ms=10000,
        )

    @classmethod
    def BLS_REGISTERED(cls) -> "AgencyConfig":
        """BLS API (registered): 50 req/10s burst, 500/day."""
        return cls(
            agency=Agency.BLS,
            burst_limit=50,
            burst_window_seconds=10,
            daily_limit=500,
            requests_per_second=5.0,  # 50 per 10 seconds
            min_request_interval_ms=200,
            base_delay_ms=500,
            max_delay_ms=10000,
        )

    @classmethod
    def BLS_UNREGISTERED(cls) -> "AgencyConfig":
        """BLS API (unregistered): 50 req/10s burst, 25/day."""
        return cls(
            agency=Agency.BLS,
            burst_limit=50,
            burst_window_seconds=10,
            daily_limit=25,
            requests_per_second=5.0,
            min_request_interval_ms=200,
            base_delay_ms=500,
            max_delay_ms=10000,
        )

    @classmethod
    def BEA(cls) -> "AgencyConfig":
        """BEA API: 100 req/min, 100 MB/min, 30 errors/min triggers lockout."""
        return cls(
            agency=Agency.BEA,
            requests_per_minute=100,
            requests_per_second=1.67,  # ~100/min
            min_request_interval_ms=600,
            error_threshold_per_minute=30,
            lockout_duration_minutes=60,
            data_volume_mb_per_minute=100,
            base_delay_ms=500,
            max_delay_ms=30000,
        )

    @classmethod
    def CENSUS_KEYLESS(cls) -> "AgencyConfig":
        """Census API (no key): 500/day per IP."""
        return cls(
            agency=Agency.CENSUS,
            daily_limit=500,
            requests_per_second=10.0,  # No per-minute limit, but be conservative
            min_request_interval_ms=100,
            base_delay_ms=500,
            max_delay_ms=10000,
        )

    @classmethod
    def CENSUS_WITH_KEY(cls) -> "AgencyConfig":
        """Census API (with key): monitored but higher limits."""
        return cls(
            agency=Agency.CENSUS,
            daily_limit=None,  # Effectively unlimited with key
            requests_per_second=20.0,
            min_request_interval_ms=50,
            base_delay_ms=500,
            max_delay_ms=10000,
        )


# =============================================================================
# TOKEN BUCKET ALGORITHM
# =============================================================================


class TokenBucket:
    """
    Token bucket algorithm for rate limiting.
    
    Tokens are added at a fixed rate up to a maximum capacity.
    Each request consumes one token. If no tokens available,
    request must wait.
    
    Thread-safe implementation using locks.
    
    Attributes:
        capacity: Maximum tokens in bucket
        refill_rate: Tokens added per second
        tokens: Current token count
    """

    def __init__(self, capacity: float, refill_rate: float):
        """
        Initialize token bucket.
        
        Args:
            capacity: Maximum tokens (burst capacity)
            refill_rate: Tokens per second to add
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        """Add tokens based on time elapsed since last refill."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def acquire(self, tokens: float = 1.0, blocking: bool = True, timeout: float = None) -> bool:
        """
        Acquire tokens from the bucket.
        
        Args:
            tokens: Number of tokens to acquire
            blocking: If True, wait for tokens. If False, return immediately.
            timeout: Maximum time to wait (None = wait forever)
        
        Returns:
            True if tokens acquired, False if not available (non-blocking)
        
        Raises:
            RateLimitExceeded: If blocking=False and no tokens available
        """
        deadline = None if timeout is None else time.monotonic() + timeout

        while True:
            with self._lock:
                self._refill()

                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True

                if not blocking:
                    return False

                # Calculate wait time for tokens
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.refill_rate

            # Check timeout
            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                wait_time = min(wait_time, remaining)

            time.sleep(min(wait_time, 0.1))  # Sleep in small increments

    def try_acquire(self, tokens: float = 1.0) -> bool:
        """Try to acquire tokens without blocking."""
        return self.acquire(tokens, blocking=False)

    @property
    def available_tokens(self) -> float:
        """Get current available tokens."""
        with self._lock:
            self._refill()
            return self.tokens

    def time_until_available(self, tokens: float = 1.0) -> float:
        """
        Calculate time until specified tokens are available.
        
        Returns:
            Seconds until tokens available (0 if already available)
        """
        with self._lock:
            self._refill()
            if self.tokens >= tokens:
                return 0.0
            tokens_needed = tokens - self.tokens
            return tokens_needed / self.refill_rate


# =============================================================================
# SLIDING WINDOW COUNTER
# =============================================================================


class SlidingWindowCounter:
    """
    Sliding window counter for tracking requests over time.
    
    Used for daily quotas and per-minute tracking.
    Thread-safe implementation.
    """

    def __init__(self, window_seconds: int, max_requests: int):
        """
        Initialize sliding window.
        
        Args:
            window_seconds: Size of the window in seconds
            max_requests: Maximum requests allowed in window
        """
        self.window_seconds = window_seconds
        self.max_requests = max_requests
        self.requests: List[float] = []  # Timestamps
        self._lock = threading.Lock()

    def _cleanup(self) -> None:
        """Remove expired timestamps from window."""
        cutoff = time.monotonic() - self.window_seconds
        self.requests = [ts for ts in self.requests if ts > cutoff]

    def try_acquire(self) -> bool:
        """
        Try to record a request.
        
        Returns:
            True if request allowed, False if limit exceeded
        """
        with self._lock:
            self._cleanup()
            if len(self.requests) >= self.max_requests:
                return False
            self.requests.append(time.monotonic())
            return True

    def acquire(self, blocking: bool = True, timeout: float = None) -> bool:
        """
        Acquire permission for a request.
        
        Args:
            blocking: If True, wait for slot. If False, return immediately.
            timeout: Maximum wait time
        
        Returns:
            True if acquired, False if not
        """
        deadline = None if timeout is None else time.monotonic() + timeout

        while True:
            if self.try_acquire():
                return True

            if not blocking:
                return False

            # Calculate wait time until oldest request expires
            with self._lock:
                if self.requests:
                    oldest = self.requests[0]
                    wait_time = (oldest + self.window_seconds) - time.monotonic()
                    wait_time = max(0.01, wait_time)
                else:
                    wait_time = 0.1

            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                wait_time = min(wait_time, remaining)

            time.sleep(min(wait_time, 0.5))

    @property
    def requests_in_window(self) -> int:
        """Get current request count in window."""
        with self._lock:
            self._cleanup()
            return len(self.requests)

    @property
    def remaining_capacity(self) -> int:
        """Get remaining request capacity."""
        with self._lock:
            self._cleanup()
            return max(0, self.max_requests - len(self.requests))

    def time_until_slot_available(self) -> float:
        """
        Calculate time until a request slot becomes available.
        
        Returns:
            Seconds until slot available (0 if available now)
        """
        with self._lock:
            self._cleanup()
            if len(self.requests) < self.max_requests:
                return 0.0
            if not self.requests:
                return 0.0
            oldest = self.requests[0]
            return max(0.0, (oldest + self.window_seconds) - time.monotonic())


# =============================================================================
# DAILY QUOTA TRACKER
# =============================================================================


class DailyQuotaTracker:
    """
    Tracks daily API request quotas with persistence.
    
    Persists quota usage to disk to survive process restarts.
    Resets at midnight UTC.
    """

    def __init__(
        self,
        agency: str,
        daily_limit: int,
        persistence_dir: Optional[str] = None,
    ):
        """
        Initialize daily quota tracker.
        
        Args:
            agency: Agency identifier for persistence file
            daily_limit: Maximum requests per day
            persistence_dir: Directory for persistence file
        """
        self.agency = agency
        self.daily_limit = daily_limit
        self._lock = threading.Lock()

        # Persistence
        if persistence_dir:
            self.persistence_dir = Path(persistence_dir)
        else:
            self.persistence_dir = Path.home() / ".krl_cache" / "rate_limits"
        self.persistence_dir.mkdir(parents=True, exist_ok=True)
        self.persistence_file = self.persistence_dir / f"{agency.lower()}_daily_quota.json"

        # Load or initialize state
        self._load_state()

    def _get_today(self) -> str:
        """Get current date in UTC as string."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _load_state(self) -> None:
        """Load quota state from disk."""
        try:
            if self.persistence_file.exists():
                with open(self.persistence_file, "r") as f:
                    state = json.load(f)
                    if state.get("date") == self._get_today():
                        self.requests_today = state.get("requests", 0)
                    else:
                        # New day, reset counter
                        self.requests_today = 0
            else:
                self.requests_today = 0
        except Exception as e:
            logger.warning(f"Failed to load quota state: {e}")
            self.requests_today = 0

    def _save_state(self) -> None:
        """Save quota state to disk."""
        try:
            state = {
                "date": self._get_today(),
                "requests": self.requests_today,
                "agency": self.agency,
                "daily_limit": self.daily_limit,
            }
            with open(self.persistence_file, "w") as f:
                json.dump(state, f)
        except Exception as e:
            logger.warning(f"Failed to save quota state: {e}")

    def try_acquire(self) -> bool:
        """
        Try to use a request from daily quota.
        
        Returns:
            True if quota available, False if exhausted
        """
        with self._lock:
            # Check if day rolled over
            if not hasattr(self, "_last_check_date") or self._last_check_date != self._get_today():
                self._load_state()
                self._last_check_date = self._get_today()

            if self.requests_today >= self.daily_limit:
                return False

            self.requests_today += 1
            self._save_state()
            return True

    @property
    def remaining_quota(self) -> int:
        """Get remaining daily quota."""
        with self._lock:
            if not hasattr(self, "_last_check_date") or self._last_check_date != self._get_today():
                self._load_state()
                self._last_check_date = self._get_today()
            return max(0, self.daily_limit - self.requests_today)

    @property
    def quota_resets_at(self) -> datetime:
        """Get datetime when quota resets (midnight UTC)."""
        tomorrow = datetime.now(timezone.utc).date() + timedelta(days=1)
        return datetime.combine(tomorrow, datetime.min.time(), tzinfo=timezone.utc)

    def reset(self) -> None:
        """Manually reset the daily quota (for testing)."""
        with self._lock:
            self.requests_today = 0
            self._save_state()


# =============================================================================
# ERROR TRACKER (BEA-specific)
# =============================================================================


class ErrorTracker:
    """
    Tracks API errors within a time window for lockout enforcement.
    
    Specifically for BEA's 30 errors/minute triggering 1-hour lockout.
    """

    def __init__(
        self,
        error_threshold: int,
        window_seconds: int,
        lockout_duration_seconds: int,
    ):
        """
        Initialize error tracker.
        
        Args:
            error_threshold: Errors allowed before lockout
            window_seconds: Window for counting errors
            lockout_duration_seconds: Lockout duration after threshold
        """
        self.error_threshold = error_threshold
        self.window_seconds = window_seconds
        self.lockout_duration_seconds = lockout_duration_seconds
        self.errors: List[float] = []
        self.lockout_until: Optional[float] = None
        self._lock = threading.Lock()

    def _cleanup(self) -> None:
        """Remove expired error timestamps."""
        cutoff = time.monotonic() - self.window_seconds
        self.errors = [ts for ts in self.errors if ts > cutoff]

    def record_error(self) -> None:
        """
        Record an API error.
        
        May trigger lockout if threshold exceeded.
        """
        with self._lock:
            self._cleanup()
            self.errors.append(time.monotonic())

            if len(self.errors) >= self.error_threshold:
                self.lockout_until = time.monotonic() + self.lockout_duration_seconds
                logger.warning(
                    f"Error threshold exceeded ({len(self.errors)}/{self.error_threshold}). "
                    f"Lockout until {datetime.now() + timedelta(seconds=self.lockout_duration_seconds)}"
                )

    def is_locked_out(self) -> bool:
        """Check if currently in lockout period."""
        with self._lock:
            if self.lockout_until is None:
                return False
            if time.monotonic() >= self.lockout_until:
                self.lockout_until = None
                self.errors.clear()
                return False
            return True

    @property
    def lockout_remaining_seconds(self) -> float:
        """Get remaining lockout time in seconds."""
        with self._lock:
            if self.lockout_until is None:
                return 0.0
            return max(0.0, self.lockout_until - time.monotonic())

    @property
    def errors_in_window(self) -> int:
        """Get current error count in window."""
        with self._lock:
            self._cleanup()
            return len(self.errors)


# =============================================================================
# EXPONENTIAL BACKOFF
# =============================================================================


class ExponentialBackoff:
    """
    Exponential backoff strategy for retry logic.
    
    Implements exponential delay with jitter to avoid thundering herd.
    """

    def __init__(
        self,
        base_delay_ms: int = 500,
        max_delay_ms: int = 10000,
        multiplier: float = 2.0,
        jitter: float = 0.1,
    ):
        """
        Initialize backoff strategy.
        
        Args:
            base_delay_ms: Initial delay in milliseconds
            max_delay_ms: Maximum delay in milliseconds
            multiplier: Delay multiplier per retry
            jitter: Random jitter factor (0-1)
        """
        self.base_delay_ms = base_delay_ms
        self.max_delay_ms = max_delay_ms
        self.multiplier = multiplier
        self.jitter = jitter
        self.attempt = 0
        self._lock = threading.Lock()

    def get_delay(self) -> float:
        """
        Get delay for current attempt in seconds.
        
        Returns:
            Delay in seconds
        """
        import random

        with self._lock:
            delay_ms = self.base_delay_ms * (self.multiplier ** self.attempt)
            delay_ms = min(delay_ms, self.max_delay_ms)

            # Add jitter
            jitter_range = delay_ms * self.jitter
            delay_ms += random.uniform(-jitter_range, jitter_range)

            self.attempt += 1
            return delay_ms / 1000.0

    def reset(self) -> None:
        """Reset attempt counter after successful request."""
        with self._lock:
            self.attempt = 0

    def wait(self) -> None:
        """Sleep for the current backoff delay."""
        delay = self.get_delay()
        logger.debug(f"Backoff sleeping for {delay:.2f}s (attempt {self.attempt})")
        time.sleep(delay)


# =============================================================================
# MAIN RATE LIMITER CLASS
# =============================================================================


class RateLimiter:
    """
    Comprehensive rate limiter for federal data APIs.
    
    Combines token bucket, sliding window, daily quota, and error tracking
    to enforce all agency-specific rate limits.
    
    Thread-safe and suitable for multi-threaded applications.
    
    Example:
        >>> limiter = RateLimiter(AgencyConfig.FRED())
        >>> 
        >>> # Before each API request:
        >>> limiter.acquire()  # Blocks until request allowed
        >>> response = make_api_request()
        >>> 
        >>> # After request:
        >>> if response.status_code == 429:
        ...     limiter.record_rate_limit_response()
        >>> elif response.status_code >= 400:
        ...     limiter.record_error()
        >>> else:
        ...     limiter.record_success()
    """

    def __init__(
        self,
        config: AgencyConfig,
        persistence_dir: Optional[str] = None,
    ):
        """
        Initialize rate limiter with agency configuration.
        
        Args:
            config: Agency-specific rate limit configuration
            persistence_dir: Directory for quota persistence
        """
        self.config = config
        self.agency = config.agency.value

        # Token bucket for per-second rate limiting
        if config.requests_per_second:
            self.token_bucket = TokenBucket(
                capacity=config.requests_per_second * 2,  # Allow small bursts
                refill_rate=config.requests_per_second,
            )
        else:
            self.token_bucket = None

        # Sliding window for per-minute limits
        if config.requests_per_minute:
            self.minute_window = SlidingWindowCounter(
                window_seconds=60,
                max_requests=config.requests_per_minute,
            )
        else:
            self.minute_window = None

        # Sliding window for burst limits
        if config.burst_limit and config.burst_window_seconds:
            self.burst_window = SlidingWindowCounter(
                window_seconds=config.burst_window_seconds,
                max_requests=config.burst_limit,
            )
        else:
            self.burst_window = None

        # Daily quota tracker
        if config.daily_limit:
            self.daily_quota = DailyQuotaTracker(
                agency=self.agency,
                daily_limit=config.daily_limit,
                persistence_dir=persistence_dir,
            )
        else:
            self.daily_quota = None

        # Error tracker (BEA-specific)
        if config.error_threshold_per_minute and config.lockout_duration_minutes:
            self.error_tracker = ErrorTracker(
                error_threshold=config.error_threshold_per_minute,
                window_seconds=60,
                lockout_duration_seconds=config.lockout_duration_minutes * 60,
            )
        else:
            self.error_tracker = None

        # Exponential backoff for retries
        self.backoff = ExponentialBackoff(
            base_delay_ms=config.base_delay_ms,
            max_delay_ms=config.max_delay_ms,
        )

        # Minimum interval enforcement
        self.min_interval_seconds = config.min_request_interval_ms / 1000.0
        self.last_request_time = 0.0
        self._lock = threading.Lock()

        logger.info(
            f"Initialized {self.agency} rate limiter: "
            f"rpm={config.requests_per_minute}, "
            f"rps={config.requests_per_second}, "
            f"daily={config.daily_limit}"
        )

    def _enforce_min_interval(self) -> None:
        """Enforce minimum interval between requests."""
        if self.min_interval_seconds <= 0:
            return

        with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_request_time
            if elapsed < self.min_interval_seconds:
                sleep_time = self.min_interval_seconds - elapsed
                time.sleep(sleep_time)
            self.last_request_time = time.monotonic()

    def acquire(self, blocking: bool = True, timeout: float = None) -> bool:
        """
        Acquire permission to make an API request.
        
        Checks all applicable rate limits (token bucket, sliding windows,
        daily quota, error lockout) and blocks until request is allowed.
        
        Args:
            blocking: If True, wait for permission. If False, return immediately.
            timeout: Maximum wait time in seconds
        
        Returns:
            True if permission granted, False if denied (non-blocking mode)
        
        Raises:
            DailyQuotaExhausted: If daily quota exhausted (always raised)
            ErrorThresholdExceeded: If in error lockout (always raised)
            RateLimitExceeded: If blocking=False and limit exceeded
        """
        # Check error lockout first (BEA-specific)
        if self.error_tracker and self.error_tracker.is_locked_out():
            lockout_remaining = self.error_tracker.lockout_remaining_seconds
            raise ErrorThresholdExceeded(
                f"{self.agency} API locked out due to excessive errors. "
                f"Retry in {lockout_remaining:.0f}s.",
                lockout_until=datetime.now() + timedelta(seconds=lockout_remaining),
                errors_in_window=self.error_tracker.errors_in_window,
            )

        # Check daily quota
        if self.daily_quota:
            if self.daily_quota.remaining_quota <= 0:
                raise DailyQuotaExhausted(
                    f"{self.agency} daily quota exhausted "
                    f"({self.daily_quota.daily_limit}/{self.daily_quota.daily_limit}). "
                    f"Resets at {self.daily_quota.quota_resets_at}.",
                    agency=self.agency,
                    requests_made=self.daily_quota.requests_today,
                    daily_limit=self.daily_quota.daily_limit,
                    resets_at=self.daily_quota.quota_resets_at,
                )
            # Reserve the daily quota slot
            if not self.daily_quota.try_acquire():
                raise DailyQuotaExhausted(
                    f"{self.agency} daily quota exhausted.",
                    agency=self.agency,
                )

        # Check burst window
        if self.burst_window:
            if not self.burst_window.acquire(blocking=blocking, timeout=timeout):
                if not blocking:
                    raise RateLimitExceeded(
                        f"{self.agency} burst limit exceeded.",
                        agency=self.agency,
                        retry_after=self.burst_window.time_until_slot_available(),
                        limit_type="burst",
                    )
                return False

        # Check per-minute window
        if self.minute_window:
            if not self.minute_window.acquire(blocking=blocking, timeout=timeout):
                if not blocking:
                    raise RateLimitExceeded(
                        f"{self.agency} per-minute limit exceeded.",
                        agency=self.agency,
                        retry_after=self.minute_window.time_until_slot_available(),
                        limit_type="requests_per_minute",
                    )
                return False

        # Check token bucket
        if self.token_bucket:
            if not self.token_bucket.acquire(blocking=blocking, timeout=timeout):
                if not blocking:
                    raise RateLimitExceeded(
                        f"{self.agency} rate limit exceeded.",
                        agency=self.agency,
                        retry_after=self.token_bucket.time_until_available(),
                        limit_type="tokens",
                    )
                return False

        # Enforce minimum interval
        self._enforce_min_interval()

        # Reset backoff on successful acquire
        self.backoff.reset()

        return True

    def try_acquire(self) -> bool:
        """Try to acquire without blocking."""
        try:
            return self.acquire(blocking=False)
        except (DailyQuotaExhausted, ErrorThresholdExceeded, RateLimitExceeded):
            return False

    def record_success(self) -> None:
        """Record a successful API response."""
        self.backoff.reset()

    def record_error(self) -> None:
        """Record an API error (non-rate-limit)."""
        if self.error_tracker:
            self.error_tracker.record_error()

    def record_rate_limit_response(self, retry_after: float = None) -> None:
        """
        Record a 429 rate limit response.
        
        Args:
            retry_after: Retry-After header value in seconds
        """
        if retry_after:
            logger.warning(f"{self.agency} rate limited. Retry-After: {retry_after}s")
            time.sleep(retry_after)
        else:
            self.backoff.wait()

    def get_status(self) -> Dict[str, Any]:
        """
        Get current rate limiter status.
        
        Returns:
            Dictionary with current limits, usage, and availability
        """
        status = {
            "agency": self.agency,
            "limits": {
                "requests_per_minute": self.config.requests_per_minute,
                "requests_per_second": self.config.requests_per_second,
                "daily_limit": self.config.daily_limit,
                "burst_limit": self.config.burst_limit,
            },
            "current_usage": {},
            "availability": {},
        }

        if self.token_bucket:
            status["current_usage"]["tokens_available"] = self.token_bucket.available_tokens
            status["availability"]["time_until_token"] = self.token_bucket.time_until_available()

        if self.minute_window:
            status["current_usage"]["requests_this_minute"] = self.minute_window.requests_in_window
            status["current_usage"]["minute_capacity_remaining"] = self.minute_window.remaining_capacity
            status["availability"]["time_until_minute_slot"] = self.minute_window.time_until_slot_available()

        if self.burst_window:
            status["current_usage"]["requests_in_burst_window"] = self.burst_window.requests_in_window
            status["current_usage"]["burst_capacity_remaining"] = self.burst_window.remaining_capacity

        if self.daily_quota:
            status["current_usage"]["requests_today"] = self.daily_quota.requests_today
            status["current_usage"]["daily_quota_remaining"] = self.daily_quota.remaining_quota
            status["availability"]["quota_resets_at"] = self.daily_quota.quota_resets_at.isoformat()

        if self.error_tracker:
            status["current_usage"]["errors_this_minute"] = self.error_tracker.errors_in_window
            status["availability"]["is_locked_out"] = self.error_tracker.is_locked_out()
            if self.error_tracker.is_locked_out():
                status["availability"]["lockout_remaining_seconds"] = self.error_tracker.lockout_remaining_seconds

        return status


# =============================================================================
# CONVENIENCE DECORATORS
# =============================================================================

T = TypeVar("T")


def rate_limited(limiter: RateLimiter):
    """
    Decorator to apply rate limiting to a function.
    
    Example:
        >>> limiter = RateLimiter(AgencyConfig.FRED())
        >>> 
        >>> @rate_limited(limiter)
        ... def fetch_fred_series(series_id: str):
        ...     return requests.get(f"https://api.stlouisfed.org/fred/series?series_id={series_id}")
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            limiter.acquire()
            try:
                result = func(*args, **kwargs)
                limiter.record_success()
                return result
            except Exception as e:
                # Check if it's a rate limit response
                if hasattr(e, "response") and hasattr(e.response, "status_code"):
                    if e.response.status_code == 429:
                        retry_after = e.response.headers.get("Retry-After")
                        if retry_after:
                            limiter.record_rate_limit_response(float(retry_after))
                        else:
                            limiter.record_rate_limit_response()
                    else:
                        limiter.record_error()
                raise

        return wrapper

    return decorator


# =============================================================================
# RATE LIMITER REGISTRY
# =============================================================================


class RateLimiterRegistry:
    """
    Global registry for rate limiters to ensure singleton per agency.
    
    Ensures consistent rate limiting across all connector instances.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._limiters: Dict[str, RateLimiter] = {}
                    cls._instance._registry_lock = threading.Lock()
        return cls._instance

    def get_limiter(
        self,
        config: AgencyConfig,
        persistence_dir: Optional[str] = None,
    ) -> RateLimiter:
        """
        Get or create a rate limiter for an agency.
        
        Args:
            config: Agency configuration
            persistence_dir: Directory for quota persistence
        
        Returns:
            Rate limiter instance (singleton per agency)
        """
        key = config.agency.value
        with self._registry_lock:
            if key not in self._limiters:
                self._limiters[key] = RateLimiter(config, persistence_dir)
            return self._limiters[key]

    def get_status_all(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all registered rate limiters."""
        with self._registry_lock:
            return {key: limiter.get_status() for key, limiter in self._limiters.items()}


# Convenience function
def get_rate_limiter(agency: str, registered: bool = True) -> RateLimiter:
    """
    Get a rate limiter for a specific agency.
    
    Args:
        agency: Agency name ('FRED', 'BLS', 'BEA', 'Census')
        registered: For BLS/Census, whether using registered API key
    
    Returns:
        Configured rate limiter
    """
    registry = RateLimiterRegistry()

    agency_upper = agency.upper()
    if agency_upper == "FRED":
        config = AgencyConfig.FRED()
    elif agency_upper == "BLS":
        config = AgencyConfig.BLS_REGISTERED() if registered else AgencyConfig.BLS_UNREGISTERED()
    elif agency_upper == "BEA":
        config = AgencyConfig.BEA()
    elif agency_upper in ("CENSUS", "CENSUS_BUREAU"):
        config = AgencyConfig.CENSUS_WITH_KEY() if registered else AgencyConfig.CENSUS_KEYLESS()
    else:
        raise ValueError(f"Unknown agency: {agency}")

    return registry.get_limiter(config)


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    # Exceptions
    "RateLimitExceeded",
    "DailyQuotaExhausted",
    "ErrorThresholdExceeded",
    # Configuration
    "Agency",
    "AgencyConfig",
    "API_LIMITS_SPEC",
    # Core algorithms
    "TokenBucket",
    "SlidingWindowCounter",
    "DailyQuotaTracker",
    "ErrorTracker",
    "ExponentialBackoff",
    # Main class
    "RateLimiter",
    # Utilities
    "rate_limited",
    "RateLimiterRegistry",
    "get_rate_limiter",
]
