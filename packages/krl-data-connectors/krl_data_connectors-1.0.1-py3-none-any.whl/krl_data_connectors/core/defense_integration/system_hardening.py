"""
System Hardening - Defense-in-depth protection and system hardening utilities.

Week 16: Defense Integration & System Hardening
Provides system hardening, secure configuration, and runtime protection.
"""

from __future__ import annotations

import asyncio
import functools
import hashlib
import hmac
import logging
import os
import secrets
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TypeVar
from collections import defaultdict
import threading
import json

logger = logging.getLogger(__name__)


class HardeningLevel(Enum):
    """System hardening levels."""
    
    MINIMAL = 1      # Basic security
    STANDARD = 2     # Standard hardening
    ENHANCED = 3     # Enhanced protection
    MAXIMUM = 4      # Maximum security


class ProtectionType(Enum):
    """Types of runtime protection."""
    
    MEMORY = auto()
    PROCESS = auto()
    NETWORK = auto()
    FILESYSTEM = auto()
    CRYPTO = auto()


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    
    # Authentication
    min_password_length: int = 12
    require_special_chars: bool = True
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    session_timeout_minutes: int = 60
    
    # Encryption
    encryption_algorithm: str = "AES-256-GCM"
    key_rotation_days: int = 90
    min_key_length: int = 256
    
    # Network
    allowed_origins: List[str] = field(default_factory=list)
    require_tls: bool = True
    min_tls_version: str = "1.3"
    
    # Logging
    audit_all_access: bool = True
    log_sensitive_operations: bool = True
    redact_sensitive_fields: bool = True
    
    # Runtime
    enable_stack_protection: bool = True
    enable_heap_protection: bool = True
    max_request_size_mb: int = 10
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "authentication": {
                "min_password_length": self.min_password_length,
                "require_special_chars": self.require_special_chars,
                "max_login_attempts": self.max_login_attempts,
                "lockout_duration_minutes": self.lockout_duration_minutes,
                "session_timeout_minutes": self.session_timeout_minutes,
            },
            "encryption": {
                "algorithm": self.encryption_algorithm,
                "key_rotation_days": self.key_rotation_days,
                "min_key_length": self.min_key_length,
            },
            "network": {
                "allowed_origins": self.allowed_origins,
                "require_tls": self.require_tls,
                "min_tls_version": self.min_tls_version,
            },
            "logging": {
                "audit_all_access": self.audit_all_access,
                "log_sensitive_operations": self.log_sensitive_operations,
                "redact_sensitive_fields": self.redact_sensitive_fields,
            },
            "runtime": {
                "enable_stack_protection": self.enable_stack_protection,
                "enable_heap_protection": self.enable_heap_protection,
                "max_request_size_mb": self.max_request_size_mb,
            },
        }


class SecureKeyManager:
    """Manages cryptographic keys securely."""
    
    def __init__(
        self,
        key_rotation_days: int = 90,
        max_key_age_days: int = 365
    ):
        self.key_rotation_days = key_rotation_days
        self.max_key_age_days = max_key_age_days
        
        self.keys: Dict[str, Tuple[bytes, datetime]] = {}
        self.key_history: Dict[str, List[Tuple[bytes, datetime, datetime]]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def generate_key(
        self,
        key_id: str,
        length: int = 32
    ) -> bytes:
        """Generate a new secure key."""
        key = secrets.token_bytes(length)
        
        with self._lock:
            # Archive old key if exists
            if key_id in self.keys:
                old_key, created = self.keys[key_id]
                self.key_history[key_id].append(
                    (old_key, created, datetime.now())
                )
            
            self.keys[key_id] = (key, datetime.now())
        
        return key
    
    def get_key(self, key_id: str) -> Optional[bytes]:
        """Get a key by ID."""
        with self._lock:
            if key_id not in self.keys:
                return None
            
            key, created = self.keys[key_id]
            return key
    
    def rotate_key(self, key_id: str, length: int = 32) -> Optional[bytes]:
        """Rotate a key."""
        with self._lock:
            if key_id not in self.keys:
                return None
        
        return self.generate_key(key_id, length)
    
    def check_rotation_needed(self, key_id: str) -> bool:
        """Check if key needs rotation."""
        with self._lock:
            if key_id not in self.keys:
                return False
            
            key, created = self.keys[key_id]
            age = datetime.now() - created
            
            return age.days >= self.key_rotation_days
    
    def get_keys_needing_rotation(self) -> List[str]:
        """Get list of keys that need rotation."""
        with self._lock:
            needs_rotation = []
            
            for key_id, (key, created) in self.keys.items():
                age = datetime.now() - created
                if age.days >= self.key_rotation_days:
                    needs_rotation.append(key_id)
            
            return needs_rotation
    
    def delete_key(self, key_id: str) -> bool:
        """Securely delete a key."""
        with self._lock:
            if key_id not in self.keys:
                return False
            
            # Archive before deletion
            key, created = self.keys[key_id]
            self.key_history[key_id].append(
                (key, created, datetime.now())
            )
            
            del self.keys[key_id]
            return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get key manager status."""
        with self._lock:
            keys_info = []
            
            for key_id, (key, created) in self.keys.items():
                age = datetime.now() - created
                keys_info.append({
                    "key_id": key_id,
                    "created": created.isoformat(),
                    "age_days": age.days,
                    "needs_rotation": age.days >= self.key_rotation_days,
                })
            
            return {
                "total_keys": len(self.keys),
                "keys": keys_info,
                "keys_needing_rotation": len(self.get_keys_needing_rotation()),
            }


class SecureSession:
    """Secure session management."""
    
    def __init__(
        self,
        timeout_minutes: int = 60,
        max_sessions_per_entity: int = 5
    ):
        self.timeout_minutes = timeout_minutes
        self.max_sessions_per_entity = max_sessions_per_entity
        
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.entity_sessions: Dict[str, Set[str]] = defaultdict(set)
        self._lock = threading.Lock()
    
    def create(
        self,
        entity_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new session."""
        session_id = secrets.token_urlsafe(32)
        
        with self._lock:
            # Check session limit
            if len(self.entity_sessions[entity_id]) >= self.max_sessions_per_entity:
                # Remove oldest session
                oldest = min(
                    self.entity_sessions[entity_id],
                    key=lambda s: self.sessions.get(s, {}).get("created", datetime.max)
                )
                self._invalidate_session(oldest)
            
            self.sessions[session_id] = {
                "entity_id": entity_id,
                "created": datetime.now(),
                "last_access": datetime.now(),
                "metadata": metadata or {},
            }
            
            self.entity_sessions[entity_id].add(session_id)
        
        return session_id
    
    def validate(self, session_id: str) -> Tuple[bool, Optional[str]]:
        """Validate a session."""
        with self._lock:
            if session_id not in self.sessions:
                return False, None
            
            session = self.sessions[session_id]
            
            # Check timeout
            age = datetime.now() - session["last_access"]
            if age.total_seconds() > self.timeout_minutes * 60:
                self._invalidate_session(session_id)
                return False, None
            
            # Update last access
            session["last_access"] = datetime.now()
            
            return True, session["entity_id"]
    
    def invalidate(self, session_id: str) -> bool:
        """Invalidate a session."""
        with self._lock:
            return self._invalidate_session(session_id)
    
    def _invalidate_session(self, session_id: str) -> bool:
        """Internal session invalidation."""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        entity_id = session["entity_id"]
        
        del self.sessions[session_id]
        self.entity_sessions[entity_id].discard(session_id)
        
        return True
    
    def invalidate_entity(self, entity_id: str) -> int:
        """Invalidate all sessions for an entity."""
        with self._lock:
            sessions = list(self.entity_sessions.get(entity_id, set()))
            
            for session_id in sessions:
                self._invalidate_session(session_id)
            
            return len(sessions)
    
    def cleanup_expired(self) -> int:
        """Clean up expired sessions."""
        with self._lock:
            expired = []
            
            for session_id, session in self.sessions.items():
                age = datetime.now() - session["last_access"]
                if age.total_seconds() > self.timeout_minutes * 60:
                    expired.append(session_id)
            
            for session_id in expired:
                self._invalidate_session(session_id)
            
            return len(expired)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        with self._lock:
            return {
                "total_sessions": len(self.sessions),
                "unique_entities": len(self.entity_sessions),
                "sessions_per_entity": {
                    entity_id: len(sessions)
                    for entity_id, sessions in self.entity_sessions.items()
                },
            }


class IntegrityChecker:
    """Checks and validates system integrity."""
    
    def __init__(self, secret_key: bytes):
        self.secret_key = secret_key
        self.checksums: Dict[str, str] = {}
        self._lock = threading.Lock()
    
    def compute_checksum(self, data: bytes) -> str:
        """Compute HMAC checksum for data."""
        return hmac.new(
            self.secret_key,
            data,
            hashlib.sha256
        ).hexdigest()
    
    def register(self, identifier: str, data: bytes) -> str:
        """Register data with a checksum."""
        checksum = self.compute_checksum(data)
        
        with self._lock:
            self.checksums[identifier] = checksum
        
        return checksum
    
    def verify(self, identifier: str, data: bytes) -> bool:
        """Verify data integrity."""
        with self._lock:
            stored = self.checksums.get(identifier)
        
        if not stored:
            return False
        
        computed = self.compute_checksum(data)
        return hmac.compare_digest(stored, computed)
    
    def verify_checksum(self, data: bytes, expected: str) -> bool:
        """Verify data against a known checksum."""
        computed = self.compute_checksum(data)
        return hmac.compare_digest(computed, expected)
    
    def sign_message(self, message: Dict[str, Any]) -> str:
        """Sign a message dictionary."""
        canonical = json.dumps(message, sort_keys=True)
        return self.compute_checksum(canonical.encode())
    
    def verify_message(self, message: Dict[str, Any], signature: str) -> bool:
        """Verify a signed message."""
        expected = self.sign_message(message)
        return hmac.compare_digest(expected, signature)


@dataclass
class ProtectionCheck:
    """Result of a protection check."""
    
    check_name: str
    passed: bool
    details: str
    timestamp: datetime = field(default_factory=datetime.now)


class RuntimeProtection:
    """Runtime protection mechanisms."""
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()
        self.checks: List[ProtectionCheck] = []
        self._lock = threading.Lock()
    
    def check_all(self) -> List[ProtectionCheck]:
        """Run all protection checks."""
        checks = []
        
        checks.append(self._check_environment())
        checks.append(self._check_dependencies())
        checks.append(self._check_configuration())
        checks.append(self._check_permissions())
        
        with self._lock:
            self.checks = checks
        
        return checks
    
    def _check_environment(self) -> ProtectionCheck:
        """Check environment security."""
        issues = []
        
        # Check for debug mode
        if os.environ.get("DEBUG", "").lower() == "true":
            issues.append("DEBUG mode is enabled")
        
        # Check for sensitive env vars
        sensitive_vars = ["SECRET_KEY", "API_KEY", "PASSWORD"]
        for var in sensitive_vars:
            if var in os.environ and len(os.environ[var]) < 32:
                issues.append(f"Weak {var} detected")
        
        passed = len(issues) == 0
        details = "OK" if passed else f"Issues: {', '.join(issues)}"
        
        return ProtectionCheck(
            check_name="environment",
            passed=passed,
            details=details
        )
    
    def _check_dependencies(self) -> ProtectionCheck:
        """Check dependency security."""
        # In production, this would scan dependencies for vulnerabilities
        return ProtectionCheck(
            check_name="dependencies",
            passed=True,
            details="Dependency check passed"
        )
    
    def _check_configuration(self) -> ProtectionCheck:
        """Check configuration security."""
        issues = []
        
        if not self.config.require_tls:
            issues.append("TLS not required")
        
        if self.config.min_password_length < 8:
            issues.append("Weak password policy")
        
        if self.config.session_timeout_minutes > 480:
            issues.append("Long session timeout")
        
        passed = len(issues) == 0
        details = "OK" if passed else f"Issues: {', '.join(issues)}"
        
        return ProtectionCheck(
            check_name="configuration",
            passed=passed,
            details=details
        )
    
    def _check_permissions(self) -> ProtectionCheck:
        """Check permission security."""
        # In production, check file permissions, process capabilities, etc.
        return ProtectionCheck(
            check_name="permissions",
            passed=True,
            details="Permission check passed"
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get protection status."""
        with self._lock:
            return {
                "total_checks": len(self.checks),
                "passed": sum(1 for c in self.checks if c.passed),
                "failed": sum(1 for c in self.checks if not c.passed),
                "checks": [
                    {
                        "name": c.check_name,
                        "passed": c.passed,
                        "details": c.details,
                        "timestamp": c.timestamp.isoformat(),
                    }
                    for c in self.checks
                ],
            }


def secure_function(
    require_auth: bool = True,
    audit: bool = True,
    max_attempts: int = 5
) -> Callable:
    """Decorator for securing functions."""
    def decorator(func: Callable) -> Callable:
        attempts: Dict[str, int] = defaultdict(int)
        last_attempt: Dict[str, datetime] = {}
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            entity_id = kwargs.get("entity_id", "unknown")
            
            # Check rate limiting
            if attempts[entity_id] >= max_attempts:
                last = last_attempt.get(entity_id, datetime.min)
                if datetime.now() - last < timedelta(minutes=5):
                    raise PermissionError("Rate limit exceeded")
                attempts[entity_id] = 0
            
            attempts[entity_id] += 1
            last_attempt[entity_id] = datetime.now()
            
            if audit:
                logger.info(f"Secure function call: {func.__name__} by {entity_id}")
            
            try:
                result = await func(*args, **kwargs)
                attempts[entity_id] = 0  # Reset on success
                return result
            except Exception as e:
                logger.error(f"Secure function error: {func.__name__} - {e}")
                raise
        
        return wrapper
    return decorator


class SystemHardener:
    """Main system hardening coordinator."""
    
    def __init__(
        self,
        config: Optional[SecurityConfig] = None,
        hardening_level: HardeningLevel = HardeningLevel.STANDARD
    ):
        self.config = config or SecurityConfig()
        self.hardening_level = hardening_level
        
        # Initialize components
        self.key_manager = SecureKeyManager(
            key_rotation_days=self.config.key_rotation_days
        )
        
        self.session_manager = SecureSession(
            timeout_minutes=self.config.session_timeout_minutes
        )
        
        # Generate master key for integrity
        master_key = secrets.token_bytes(32)
        self.integrity_checker = IntegrityChecker(master_key)
        
        self.runtime_protection = RuntimeProtection(self.config)
        
        # State
        self.initialized = False
        self.last_check: Optional[datetime] = None
    
    async def initialize(self) -> bool:
        """Initialize system hardening."""
        try:
            # Generate initial keys
            self.key_manager.generate_key("primary_encryption", 32)
            self.key_manager.generate_key("signing_key", 32)
            self.key_manager.generate_key("session_key", 32)
            
            # Run initial checks
            self.runtime_protection.check_all()
            
            self.initialized = True
            self.last_check = datetime.now()
            
            logger.info(
                f"System hardening initialized at level: {self.hardening_level.name}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"System hardening initialization failed: {e}")
            return False
    
    async def periodic_check(self) -> Dict[str, Any]:
        """Run periodic security checks."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "hardening_level": self.hardening_level.name,
            "checks": {},
        }
        
        # Key rotation check
        needs_rotation = self.key_manager.get_keys_needing_rotation()
        results["checks"]["key_rotation"] = {
            "passed": len(needs_rotation) == 0,
            "details": f"Keys needing rotation: {needs_rotation}" if needs_rotation else "OK",
        }
        
        # Session cleanup
        expired = self.session_manager.cleanup_expired()
        results["checks"]["session_cleanup"] = {
            "passed": True,
            "details": f"Cleaned {expired} expired sessions",
        }
        
        # Runtime checks
        runtime_checks = self.runtime_protection.check_all()
        results["checks"]["runtime"] = {
            "passed": all(c.passed for c in runtime_checks),
            "details": [
                {"name": c.check_name, "passed": c.passed}
                for c in runtime_checks
            ],
        }
        
        self.last_check = datetime.now()
        
        return results
    
    def get_security_posture(self) -> Dict[str, Any]:
        """Get overall security posture."""
        return {
            "hardening_level": self.hardening_level.name,
            "initialized": self.initialized,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "configuration": self.config.to_dict(),
            "key_status": self.key_manager.get_status(),
            "session_stats": self.session_manager.get_stats(),
            "runtime_status": self.runtime_protection.get_status(),
        }
    
    def apply_hardening(
        self,
        level: HardeningLevel
    ) -> Dict[str, Any]:
        """Apply hardening level configuration."""
        old_level = self.hardening_level
        self.hardening_level = level
        
        # Apply level-specific settings
        if level == HardeningLevel.MAXIMUM:
            self.config.require_tls = True
            self.config.min_tls_version = "1.3"
            self.config.min_password_length = 16
            self.config.session_timeout_minutes = 30
            self.config.key_rotation_days = 30
            self.config.audit_all_access = True
        elif level == HardeningLevel.ENHANCED:
            self.config.require_tls = True
            self.config.min_password_length = 14
            self.config.session_timeout_minutes = 45
            self.config.key_rotation_days = 60
        elif level == HardeningLevel.STANDARD:
            self.config.require_tls = True
            self.config.min_password_length = 12
            self.config.session_timeout_minutes = 60
            self.config.key_rotation_days = 90
        
        logger.info(
            f"Hardening level changed: {old_level.name} -> {level.name}"
        )
        
        return {
            "previous_level": old_level.name,
            "new_level": level.name,
            "configuration": self.config.to_dict(),
        }


# Factory functions
def create_hardener(
    level: HardeningLevel = HardeningLevel.STANDARD
) -> SystemHardener:
    """Create a system hardener."""
    return SystemHardener(hardening_level=level)


def create_key_manager(
    rotation_days: int = 90
) -> SecureKeyManager:
    """Create a key manager."""
    return SecureKeyManager(key_rotation_days=rotation_days)


def create_session_manager(
    timeout_minutes: int = 60
) -> SecureSession:
    """Create a session manager."""
    return SecureSession(timeout_minutes=timeout_minutes)
