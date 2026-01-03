"""
API Hardening - Security-hardened API layer for license protection.

Week 16: Defense Integration & System Hardening
Provides secure API endpoints with rate limiting, validation, and audit logging.
"""

from __future__ import annotations

import asyncio
import functools
import hashlib
import hmac
import json
import logging
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TypeVar, Union
from collections import defaultdict
import threading
import uuid

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """API security levels."""
    
    PUBLIC = 1       # Public endpoints
    BASIC = 2        # Basic authentication
    STANDARD = 3     # Standard security
    ELEVATED = 4     # Enhanced validation
    RESTRICTED = 5   # Maximum security


class ValidationResult(Enum):
    """Validation result types."""
    
    VALID = auto()
    INVALID_FORMAT = auto()
    INVALID_LENGTH = auto()
    INVALID_CHARACTERS = auto()
    INJECTION_DETECTED = auto()
    RATE_LIMITED = auto()
    BLOCKED = auto()


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10
    burst_window_seconds: int = 1
    penalty_multiplier: float = 2.0
    max_penalty_duration_minutes: int = 60


@dataclass
class RateLimitState:
    """State for rate limiting."""
    
    minute_count: int = 0
    minute_window_start: datetime = field(default_factory=datetime.now)
    hour_count: int = 0
    hour_window_start: datetime = field(default_factory=datetime.now)
    burst_timestamps: List[float] = field(default_factory=list)
    penalty_until: Optional[datetime] = None
    violation_count: int = 0


class RateLimiter:
    """Advanced rate limiter with burst detection and penalties."""
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self.states: Dict[str, RateLimitState] = defaultdict(RateLimitState)
        self._lock = threading.Lock()
    
    def check(self, identifier: str) -> Tuple[bool, str]:
        """Check if request is allowed."""
        with self._lock:
            state = self.states[identifier]
            now = datetime.now()
            
            # Check penalty
            if state.penalty_until and now < state.penalty_until:
                remaining = (state.penalty_until - now).total_seconds()
                return False, f"Rate limited: {remaining:.0f}s remaining"
            
            # Reset penalty if expired
            if state.penalty_until and now >= state.penalty_until:
                state.penalty_until = None
            
            # Check minute window
            if (now - state.minute_window_start).total_seconds() >= 60:
                state.minute_count = 0
                state.minute_window_start = now
            
            if state.minute_count >= self.config.requests_per_minute:
                self._apply_penalty(state)
                return False, "Rate limit exceeded (per minute)"
            
            # Check hour window
            if (now - state.hour_window_start).total_seconds() >= 3600:
                state.hour_count = 0
                state.hour_window_start = now
            
            if state.hour_count >= self.config.requests_per_hour:
                self._apply_penalty(state)
                return False, "Rate limit exceeded (per hour)"
            
            # Check burst
            current_time = time.time()
            state.burst_timestamps = [
                ts for ts in state.burst_timestamps
                if current_time - ts <= self.config.burst_window_seconds
            ]
            
            if len(state.burst_timestamps) >= self.config.burst_limit:
                self._apply_penalty(state)
                return False, "Burst limit exceeded"
            
            # Update counters
            state.minute_count += 1
            state.hour_count += 1
            state.burst_timestamps.append(current_time)
            
            return True, "OK"
    
    def _apply_penalty(self, state: RateLimitState) -> None:
        """Apply rate limit penalty."""
        state.violation_count += 1
        
        # Exponential backoff
        penalty_minutes = min(
            self.config.max_penalty_duration_minutes,
            1 * (self.config.penalty_multiplier ** state.violation_count)
        )
        
        state.penalty_until = datetime.now() + timedelta(minutes=penalty_minutes)
        
        logger.warning(
            f"Rate limit penalty applied: {penalty_minutes:.1f} minutes, "
            f"violations: {state.violation_count}"
        )
    
    def get_status(self, identifier: str) -> Dict[str, Any]:
        """Get rate limit status for identifier."""
        with self._lock:
            state = self.states.get(identifier, RateLimitState())
            now = datetime.now()
            
            return {
                "minute_remaining": max(
                    0,
                    self.config.requests_per_minute - state.minute_count
                ),
                "hour_remaining": max(
                    0,
                    self.config.requests_per_hour - state.hour_count
                ),
                "penalty_active": state.penalty_until is not None and now < state.penalty_until,
                "penalty_remaining_seconds": (
                    (state.penalty_until - now).total_seconds()
                    if state.penalty_until and now < state.penalty_until
                    else 0
                ),
                "violation_count": state.violation_count,
            }
    
    def reset(self, identifier: str) -> None:
        """Reset rate limit state for identifier."""
        with self._lock:
            if identifier in self.states:
                del self.states[identifier]


class InputValidator:
    """Validates and sanitizes API inputs."""
    
    # Injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE)\b)",
        r"(--|\#|\/\*)",
        r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+)",
        r"(\'\s*(OR|AND)\s*\')",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
    ]
    
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e",
        r"%252e%252e",
    ]
    
    COMMAND_INJECTION_PATTERNS = [
        r"[;&|`$]",
        r"\$\(",
        r"\$\{",
    ]
    
    def __init__(self, max_length: int = 10000):
        self.max_length = max_length
        
        # Compile patterns
        self.sql_patterns = [re.compile(p, re.IGNORECASE) for p in self.SQL_INJECTION_PATTERNS]
        self.xss_patterns = [re.compile(p, re.IGNORECASE) for p in self.XSS_PATTERNS]
        self.path_patterns = [re.compile(p, re.IGNORECASE) for p in self.PATH_TRAVERSAL_PATTERNS]
        self.cmd_patterns = [re.compile(p) for p in self.COMMAND_INJECTION_PATTERNS]
    
    def validate(
        self,
        value: str,
        field_name: str = "input",
        allow_html: bool = False,
        custom_pattern: Optional[str] = None
    ) -> Tuple[ValidationResult, str]:
        """Validate an input string."""
        if not isinstance(value, str):
            return ValidationResult.INVALID_FORMAT, f"{field_name}: Expected string"
        
        # Length check
        if len(value) > self.max_length:
            return (
                ValidationResult.INVALID_LENGTH,
                f"{field_name}: Exceeds maximum length ({self.max_length})"
            )
        
        # SQL injection check
        for pattern in self.sql_patterns:
            if pattern.search(value):
                logger.warning(f"SQL injection attempt in {field_name}")
                return (
                    ValidationResult.INJECTION_DETECTED,
                    f"{field_name}: SQL injection pattern detected"
                )
        
        # XSS check (unless HTML allowed)
        if not allow_html:
            for pattern in self.xss_patterns:
                if pattern.search(value):
                    logger.warning(f"XSS attempt in {field_name}")
                    return (
                        ValidationResult.INJECTION_DETECTED,
                        f"{field_name}: XSS pattern detected"
                    )
        
        # Path traversal check
        for pattern in self.path_patterns:
            if pattern.search(value):
                logger.warning(f"Path traversal attempt in {field_name}")
                return (
                    ValidationResult.INJECTION_DETECTED,
                    f"{field_name}: Path traversal pattern detected"
                )
        
        # Command injection check
        for pattern in self.cmd_patterns:
            if pattern.search(value):
                logger.warning(f"Command injection attempt in {field_name}")
                return (
                    ValidationResult.INJECTION_DETECTED,
                    f"{field_name}: Command injection pattern detected"
                )
        
        # Custom pattern check
        if custom_pattern:
            if not re.match(custom_pattern, value):
                return (
                    ValidationResult.INVALID_FORMAT,
                    f"{field_name}: Does not match required pattern"
                )
        
        return ValidationResult.VALID, "OK"
    
    def validate_license_key(self, key: str) -> Tuple[ValidationResult, str]:
        """Validate license key format."""
        # License key pattern: XXXX-XXXX-XXXX-XXXX
        pattern = r"^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$"
        
        result, message = self.validate(key, "license_key")
        if result != ValidationResult.VALID:
            return result, message
        
        if not re.match(pattern, key):
            return ValidationResult.INVALID_FORMAT, "Invalid license key format"
        
        return ValidationResult.VALID, "OK"
    
    def validate_entity_id(self, entity_id: str) -> Tuple[ValidationResult, str]:
        """Validate entity ID format."""
        # Entity ID pattern: alphanumeric with underscores/hyphens
        pattern = r"^[a-zA-Z0-9_-]{1,128}$"
        
        result, message = self.validate(entity_id, "entity_id")
        if result != ValidationResult.VALID:
            return result, message
        
        if not re.match(pattern, entity_id):
            return (
                ValidationResult.INVALID_FORMAT,
                "Invalid entity ID format (alphanumeric, _, - allowed)"
            )
        
        return ValidationResult.VALID, "OK"
    
    def sanitize(self, value: str) -> str:
        """Sanitize input by removing dangerous characters."""
        # Remove null bytes
        sanitized = value.replace('\x00', '')
        
        # HTML escape
        sanitized = (
            sanitized
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#x27;')
        )
        
        return sanitized


@dataclass
class AuditEntry:
    """Audit log entry."""
    
    entry_id: str
    timestamp: datetime
    action: str
    entity_id: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_data: Dict[str, Any]
    response_status: int
    security_level: SecurityLevel
    validation_results: List[str]
    duration_ms: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action,
            "entity_id": self.entity_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "request_data": self.request_data,
            "response_status": self.response_status,
            "security_level": self.security_level.name,
            "validation_results": self.validation_results,
            "duration_ms": self.duration_ms,
        }


class AuditLogger:
    """Security-focused audit logger."""
    
    def __init__(self, max_entries: int = 100000):
        self.max_entries = max_entries
        self.entries: List[AuditEntry] = []
        self.suspicious_entries: List[AuditEntry] = []
        self._lock = threading.Lock()
    
    def log(
        self,
        action: str,
        entity_id: str,
        request_data: Dict[str, Any],
        response_status: int,
        security_level: SecurityLevel,
        validation_results: List[str],
        duration_ms: float,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditEntry:
        """Log an API action."""
        entry = AuditEntry(
            entry_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            action=action,
            entity_id=entity_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_data=self._sanitize_request_data(request_data),
            response_status=response_status,
            security_level=security_level,
            validation_results=validation_results,
            duration_ms=duration_ms
        )
        
        with self._lock:
            self.entries.append(entry)
            
            # Trim if needed
            if len(self.entries) > self.max_entries:
                self.entries = self.entries[-self.max_entries:]
            
            # Track suspicious activity
            if response_status >= 400 or any(
                "INJECTION" in r for r in validation_results
            ):
                self.suspicious_entries.append(entry)
        
        return entry
    
    def _sanitize_request_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize request data for logging (redact sensitive fields)."""
        sensitive_fields = {
            "password", "secret", "token", "key", "credential",
            "api_key", "apikey", "auth", "authorization"
        }
        
        sanitized = {}
        for key, value in data.items():
            if any(s in key.lower() for s in sensitive_fields):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_request_data(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    def get_entries(
        self,
        entity_id: Optional[str] = None,
        action: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditEntry]:
        """Get audit entries with filters."""
        with self._lock:
            filtered = self.entries
            
            if entity_id:
                filtered = [e for e in filtered if e.entity_id == entity_id]
            
            if action:
                filtered = [e for e in filtered if e.action == action]
            
            if since:
                filtered = [e for e in filtered if e.timestamp >= since]
            
            return filtered[-limit:]
    
    def get_suspicious_activity(
        self,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditEntry]:
        """Get suspicious activity entries."""
        with self._lock:
            filtered = self.suspicious_entries
            
            if since:
                filtered = [e for e in filtered if e.timestamp >= since]
            
            return filtered[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get audit statistics."""
        with self._lock:
            if not self.entries:
                return {"total_entries": 0}
            
            now = datetime.now()
            last_hour = [
                e for e in self.entries
                if e.timestamp > now - timedelta(hours=1)
            ]
            
            return {
                "total_entries": len(self.entries),
                "suspicious_entries": len(self.suspicious_entries),
                "entries_last_hour": len(last_hour),
                "unique_entities": len(set(e.entity_id for e in self.entries)),
                "actions": dict(
                    (action, len([e for e in self.entries if e.action == action]))
                    for action in set(e.action for e in self.entries)
                ),
                "status_codes": dict(
                    (code, len([e for e in self.entries if e.response_status == code]))
                    for code in set(e.response_status for e in self.entries)
                ),
            }


class RequestSigner:
    """Signs and verifies API requests."""
    
    def __init__(self, secret_key: str, algorithm: str = "sha256"):
        self.secret_key = secret_key.encode()
        self.algorithm = algorithm
    
    def sign(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        timestamp: Optional[int] = None
    ) -> str:
        """Sign a request."""
        timestamp = timestamp or int(time.time())
        
        # Create canonical string
        canonical = f"{method.upper()}\n{path}\n{timestamp}"
        
        if body:
            body_hash = hashlib.sha256(
                json.dumps(body, sort_keys=True).encode()
            ).hexdigest()
            canonical += f"\n{body_hash}"
        
        # Generate signature
        signature = hmac.new(
            self.secret_key,
            canonical.encode(),
            self.algorithm
        ).hexdigest()
        
        return f"{timestamp}:{signature}"
    
    def verify(
        self,
        signature: str,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        max_age_seconds: int = 300
    ) -> Tuple[bool, str]:
        """Verify a request signature."""
        try:
            parts = signature.split(":")
            if len(parts) != 2:
                return False, "Invalid signature format"
            
            timestamp_str, sig = parts
            timestamp = int(timestamp_str)
            
            # Check timestamp freshness
            now = int(time.time())
            if abs(now - timestamp) > max_age_seconds:
                return False, "Signature expired"
            
            # Regenerate signature
            expected = self.sign(method, path, body, timestamp)
            expected_sig = expected.split(":")[1]
            
            if hmac.compare_digest(sig, expected_sig):
                return True, "OK"
            
            return False, "Invalid signature"
            
        except Exception as e:
            return False, f"Verification error: {str(e)}"


@dataclass
class EndpointConfig:
    """Configuration for an API endpoint."""
    
    path: str
    methods: List[str]
    security_level: SecurityLevel
    rate_limit_config: Optional[RateLimitConfig] = None
    requires_signature: bool = False
    allowed_fields: Optional[Set[str]] = None
    required_fields: Optional[Set[str]] = None


class APIHardener:
    """Hardens API endpoints with security controls."""
    
    def __init__(
        self,
        default_rate_limit: Optional[RateLimitConfig] = None,
        signing_key: Optional[str] = None
    ):
        self.default_rate_limit = default_rate_limit or RateLimitConfig()
        self.rate_limiter = RateLimiter(self.default_rate_limit)
        self.validator = InputValidator()
        self.audit_logger = AuditLogger()
        self.signer = RequestSigner(signing_key) if signing_key else None
        
        self.endpoints: Dict[str, EndpointConfig] = {}
        self.blocked_entities: Set[str] = set()
        
        self._lock = threading.Lock()
    
    def register_endpoint(self, config: EndpointConfig) -> None:
        """Register an endpoint with security configuration."""
        self.endpoints[config.path] = config
        
        # Set up custom rate limit if specified
        if config.rate_limit_config:
            self.rate_limiter = RateLimiter(config.rate_limit_config)
    
    def block_entity(self, entity_id: str, reason: str = "") -> None:
        """Block an entity from API access."""
        with self._lock:
            self.blocked_entities.add(entity_id)
            logger.warning(f"Entity blocked: {entity_id}. Reason: {reason}")
    
    def unblock_entity(self, entity_id: str) -> None:
        """Unblock an entity."""
        with self._lock:
            self.blocked_entities.discard(entity_id)
            logger.info(f"Entity unblocked: {entity_id}")
    
    async def validate_request(
        self,
        method: str,
        path: str,
        entity_id: str,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        ip_address: Optional[str] = None
    ) -> Tuple[bool, str, List[str]]:
        """Validate an API request."""
        validation_results = []
        start_time = time.time()
        
        # Check if blocked
        if entity_id in self.blocked_entities:
            return False, "Entity is blocked", ["BLOCKED"]
        
        # Get endpoint config
        endpoint_config = self.endpoints.get(path)
        security_level = (
            endpoint_config.security_level
            if endpoint_config
            else SecurityLevel.STANDARD
        )
        
        # Rate limiting
        allowed, rate_msg = self.rate_limiter.check(entity_id)
        if not allowed:
            validation_results.append(f"RATE_LIMITED: {rate_msg}")
            return False, rate_msg, validation_results
        
        # Signature verification (if required)
        if endpoint_config and endpoint_config.requires_signature:
            if not self.signer:
                validation_results.append("SIGNATURE_REQUIRED_NO_KEY")
                return False, "Signature verification not configured", validation_results
            
            signature = (headers or {}).get("X-Signature", "")
            valid, sig_msg = self.signer.verify(signature, method, path, body)
            
            if not valid:
                validation_results.append(f"SIGNATURE_INVALID: {sig_msg}")
                return False, sig_msg, validation_results
        
        # Body validation
        if body and security_level.value >= SecurityLevel.STANDARD.value:
            # Check required fields
            if endpoint_config and endpoint_config.required_fields:
                missing = endpoint_config.required_fields - set(body.keys())
                if missing:
                    validation_results.append(f"MISSING_FIELDS: {missing}")
                    return False, f"Missing required fields: {missing}", validation_results
            
            # Check allowed fields
            if endpoint_config and endpoint_config.allowed_fields:
                extra = set(body.keys()) - endpoint_config.allowed_fields
                if extra:
                    validation_results.append(f"EXTRA_FIELDS: {extra}")
                    # Remove extra fields instead of failing
                    for field in extra:
                        del body[field]
            
            # Validate each field
            for field, value in body.items():
                if isinstance(value, str):
                    result, msg = self.validator.validate(value, field)
                    if result != ValidationResult.VALID:
                        validation_results.append(f"{result.name}: {field}")
                        if result == ValidationResult.INJECTION_DETECTED:
                            return False, msg, validation_results
        
        # Entity ID validation
        result, msg = self.validator.validate_entity_id(entity_id)
        if result != ValidationResult.VALID:
            validation_results.append(f"INVALID_ENTITY_ID: {msg}")
            return False, msg, validation_results
        
        return True, "OK", validation_results
    
    def create_hardened_handler(
        self,
        handler: Callable,
        endpoint_config: EndpointConfig
    ) -> Callable:
        """Wrap a handler with security controls."""
        @functools.wraps(handler)
        async def hardened_handler(
            request_data: Dict[str, Any],
            entity_id: str,
            **kwargs
        ):
            start_time = time.time()
            
            # Extract request details
            method = request_data.get("method", "POST")
            headers = request_data.get("headers", {})
            body = request_data.get("body")
            ip_address = request_data.get("ip_address")
            
            # Validate
            valid, message, validation_results = await self.validate_request(
                method=method,
                path=endpoint_config.path,
                entity_id=entity_id,
                body=body,
                headers=headers,
                ip_address=ip_address
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            if not valid:
                # Log failed request
                self.audit_logger.log(
                    action=endpoint_config.path,
                    entity_id=entity_id,
                    request_data=request_data,
                    response_status=403,
                    security_level=endpoint_config.security_level,
                    validation_results=validation_results,
                    duration_ms=duration_ms,
                    ip_address=ip_address,
                    user_agent=headers.get("User-Agent")
                )
                
                return {
                    "success": False,
                    "error": message,
                    "status": 403
                }
            
            # Execute handler
            try:
                result = await handler(request_data, entity_id, **kwargs)
                status = result.get("status", 200)
            except Exception as e:
                logger.error(f"Handler error: {e}")
                status = 500
                result = {"success": False, "error": "Internal error", "status": 500}
            
            # Log successful request
            duration_ms = (time.time() - start_time) * 1000
            self.audit_logger.log(
                action=endpoint_config.path,
                entity_id=entity_id,
                request_data=request_data,
                response_status=status,
                security_level=endpoint_config.security_level,
                validation_results=validation_results,
                duration_ms=duration_ms,
                ip_address=ip_address,
                user_agent=headers.get("User-Agent")
            )
            
            return result
        
        return hardened_handler
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get security statistics."""
        return {
            "audit_stats": self.audit_logger.get_statistics(),
            "blocked_entities": len(self.blocked_entities),
            "registered_endpoints": len(self.endpoints),
            "security_levels": dict(
                (path, config.security_level.name)
                for path, config in self.endpoints.items()
            ),
        }


# Integration helpers
def harden_endpoint(
    hardener: APIHardener,
    path: str,
    methods: List[str],
    security_level: SecurityLevel = SecurityLevel.STANDARD,
    requires_signature: bool = False,
    allowed_fields: Optional[Set[str]] = None,
    required_fields: Optional[Set[str]] = None
) -> Callable:
    """Decorator to harden an endpoint."""
    config = EndpointConfig(
        path=path,
        methods=methods,
        security_level=security_level,
        requires_signature=requires_signature,
        allowed_fields=allowed_fields,
        required_fields=required_fields
    )
    hardener.register_endpoint(config)
    
    def decorator(handler: Callable) -> Callable:
        return hardener.create_hardened_handler(handler, config)
    
    return decorator


def create_hardener(
    signing_key: Optional[str] = None,
    requests_per_minute: int = 60
) -> APIHardener:
    """Factory for creating API hardener."""
    rate_config = RateLimitConfig(requests_per_minute=requests_per_minute)
    return APIHardener(
        default_rate_limit=rate_config,
        signing_key=signing_key
    )
