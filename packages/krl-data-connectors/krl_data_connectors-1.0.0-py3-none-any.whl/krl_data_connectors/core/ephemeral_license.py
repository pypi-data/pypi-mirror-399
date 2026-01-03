# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Ephemeral License System - Phase 2 Defense Layer

Per-customer ephemeral license generation and validation system.
Each license is:
- Time-limited (configurable expiration)
- Customer-bound (unique customer ID embedded)
- Build-specific (tied to specific build hash)
- Revocable (server-side revocation list)

SECURITY PRINCIPLES:
    1. Licenses expire - no perpetual access from leaked licenses
    2. Customer-bound - leaked license traces back to source
    3. Build-specific - license only works with matching build
    4. Revocable - compromised licenses can be invalidated instantly

Usage:
    from krl_data_connectors.core.ephemeral_license import (
        EphemeralLicense,
        LicenseGenerator,
        LicenseValidator
    )
    
    # Generate a license (CI/build time)
    generator = LicenseGenerator(signing_key="...")
    license = generator.generate(
        customer_id="customer_123",
        tier="professional",
        expires_in_days=30
    )
    
    # Validate a license (runtime)
    validator = LicenseValidator()
    result = validator.validate(license)
    if result.valid:
        print(f"License valid for {result.tier} tier")
"""

import base64
import hashlib
import hmac
import json
import logging
import os
import secrets
import struct
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, UTC
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

# Configure module logger
logger = logging.getLogger(__name__)


class LicenseTier(Enum):
    """License tier levels."""
    COMMUNITY = "community"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    
    @classmethod
    def from_string(cls, value: str) -> "LicenseTier":
        """Convert string to LicenseTier."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.COMMUNITY
    
    def __ge__(self, other: "LicenseTier") -> bool:
        """Check if this tier is >= another tier."""
        order = [self.COMMUNITY, self.PROFESSIONAL, self.ENTERPRISE]
        return order.index(self) >= order.index(other)
    
    def __gt__(self, other: "LicenseTier") -> bool:
        """Check if this tier is > another tier."""
        order = [self.COMMUNITY, self.PROFESSIONAL, self.ENTERPRISE]
        return order.index(self) > order.index(other)


class LicenseError(Exception):
    """Base exception for license errors."""
    pass


class LicenseExpiredError(LicenseError):
    """Raised when a license has expired."""
    pass


class LicenseRevokedError(LicenseError):
    """Raised when a license has been revoked."""
    pass


class LicenseInvalidError(LicenseError):
    """Raised when a license signature is invalid."""
    pass


class LicenseBuildMismatchError(LicenseError):
    """Raised when license build hash doesn't match current build."""
    pass


@dataclass
class EphemeralLicense:
    """
    An ephemeral, customer-bound license.
    
    Attributes:
        license_id: Unique license identifier (UUID-like)
        customer_id: Customer identifier (for traceability)
        tier: License tier (community, professional, enterprise)
        issued_at: When the license was issued (Unix timestamp)
        expires_at: When the license expires (Unix timestamp)
        build_hash: SHA256 hash of the build this license is for
        features: Set of enabled feature flags
        metadata: Additional license metadata
        signature: HMAC signature for validation
    """
    license_id: str
    customer_id: str
    tier: LicenseTier
    issued_at: int
    expires_at: int
    build_hash: str
    features: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    signature: str = ""
    
    def is_expired(self, current_time: Optional[int] = None) -> bool:
        """Check if the license has expired."""
        now = current_time or int(time.time())
        return now >= self.expires_at
    
    def time_remaining(self) -> timedelta:
        """Get remaining time until expiration."""
        remaining = self.expires_at - int(time.time())
        return timedelta(seconds=max(0, remaining))
    
    def has_feature(self, feature: str) -> bool:
        """Check if a feature is enabled."""
        return feature in self.features
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert license to dictionary (for serialization)."""
        return {
            "license_id": self.license_id,
            "customer_id": self.customer_id,
            "tier": self.tier.value,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "build_hash": self.build_hash,
            "features": list(self.features),
            "metadata": self.metadata,
            "signature": self.signature
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EphemeralLicense":
        """Create license from dictionary."""
        return cls(
            license_id=data["license_id"],
            customer_id=data["customer_id"],
            tier=LicenseTier.from_string(data["tier"]),
            issued_at=data["issued_at"],
            expires_at=data["expires_at"],
            build_hash=data["build_hash"],
            features=set(data.get("features", [])),
            metadata=data.get("metadata", {}),
            signature=data.get("signature", "")
        )
    
    def encode(self) -> str:
        """
        Encode license to a compact string format.
        
        Format: base64(json(license_data))
        """
        data = self.to_dict()
        json_bytes = json.dumps(data, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(json_bytes).decode("ascii")
    
    @classmethod
    def decode(cls, encoded: str) -> "EphemeralLicense":
        """Decode license from compact string format."""
        try:
            json_bytes = base64.urlsafe_b64decode(encoded.encode("ascii"))
            data = json.loads(json_bytes.decode("utf-8"))
            return cls.from_dict(data)
        except Exception as e:
            raise LicenseInvalidError(f"Failed to decode license: {e}")


@dataclass
class ValidationResult:
    """Result of license validation."""
    valid: bool
    license: Optional[EphemeralLicense] = None
    tier: LicenseTier = LicenseTier.COMMUNITY
    error: Optional[str] = None
    error_code: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "valid": self.valid,
            "tier": self.tier.value,
            "error": self.error,
            "error_code": self.error_code,
            "license_id": self.license.license_id if self.license else None,
            "customer_id": self.license.customer_id if self.license else None,
            "expires_at": self.license.expires_at if self.license else None
        }


class LicenseGenerator:
    """
    Generates ephemeral, per-customer licenses.
    
    Used at build/CI time to create licenses for specific customers.
    The signing key should be kept secret and only accessible in CI.
    
    Security:
        - Uses HMAC-SHA256 for signature
        - Signing key should be stored in CI secrets
        - Each license is unique and traceable
    
    Example:
        generator = LicenseGenerator(signing_key=os.environ["LICENSE_SIGNING_KEY"])
        license = generator.generate(
            customer_id="acme_corp",
            tier="enterprise",
            expires_in_days=30,
            features={"advanced_ml", "batch_processing"}
        )
        encoded = license.encode()  # Store this in the build
    """
    
    # Default license durations by tier
    DEFAULT_DURATIONS = {
        LicenseTier.COMMUNITY: 365,    # 1 year
        LicenseTier.PROFESSIONAL: 30,  # 30 days
        LicenseTier.ENTERPRISE: 90     # 90 days (renewable)
    }
    
    def __init__(
        self,
        signing_key: Optional[str] = None,
        default_build_hash: Optional[str] = None
    ):
        """
        Initialize the license generator.
        
        Args:
            signing_key: Secret key for signing licenses (from env if None)
            default_build_hash: Default build hash to embed in licenses
        """
        self.signing_key = signing_key or os.getenv("KRL_LICENSE_SIGNING_KEY", "")
        if not self.signing_key:
            logger.warning("No signing key provided - using insecure default")
            self.signing_key = "INSECURE_DEFAULT_KEY_DO_NOT_USE_IN_PRODUCTION"
        
        self.default_build_hash = default_build_hash or os.getenv("KRL_BUILD_HASH", "")
    
    def _generate_license_id(self) -> str:
        """Generate a unique license ID."""
        # Format: KRL-{timestamp_hex}-{random_hex}
        timestamp_hex = format(int(time.time()), 'x')
        random_hex = secrets.token_hex(8)
        return f"KRL-{timestamp_hex}-{random_hex}"
    
    def _compute_signature(self, license: EphemeralLicense) -> str:
        """Compute HMAC-SHA256 signature for a license."""
        # Create canonical representation (excluding signature field)
        canonical = json.dumps({
            "license_id": license.license_id,
            "customer_id": license.customer_id,
            "tier": license.tier.value,
            "issued_at": license.issued_at,
            "expires_at": license.expires_at,
            "build_hash": license.build_hash,
            "features": sorted(license.features)
        }, separators=(",", ":"), sort_keys=True)
        
        # Compute HMAC
        signature = hmac.new(
            self.signing_key.encode("utf-8"),
            canonical.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def generate(
        self,
        customer_id: str,
        tier: str = "community",
        expires_in_days: Optional[int] = None,
        build_hash: Optional[str] = None,
        features: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EphemeralLicense:
        """
        Generate an ephemeral license for a customer.
        
        Args:
            customer_id: Unique customer identifier
            tier: License tier (community, professional, enterprise)
            expires_in_days: Days until expiration (default by tier)
            build_hash: Build hash to bind to (default from env)
            features: Set of enabled features
            metadata: Additional metadata to embed
            
        Returns:
            Signed EphemeralLicense instance
        """
        license_tier = LicenseTier.from_string(tier)
        
        # Determine expiration
        if expires_in_days is None:
            expires_in_days = self.DEFAULT_DURATIONS.get(license_tier, 30)
        
        now = int(time.time())
        expires_at = now + (expires_in_days * 24 * 60 * 60)
        
        # Create license
        license = EphemeralLicense(
            license_id=self._generate_license_id(),
            customer_id=customer_id,
            tier=license_tier,
            issued_at=now,
            expires_at=expires_at,
            build_hash=build_hash or self.default_build_hash,
            features=features or set(),
            metadata=metadata or {}
        )
        
        # Sign the license
        license.signature = self._compute_signature(license)
        
        logger.info(
            f"Generated license {license.license_id} for customer {customer_id} "
            f"(tier: {tier}, expires: {datetime.fromtimestamp(expires_at, timezone.utc).isoformat()})"
        )
        
        return license


class LicenseValidator:
    """
    Validates ephemeral licenses at runtime.
    
    Performs multiple validation checks:
    1. Signature verification (HMAC-SHA256)
    2. Expiration check
    3. Build hash match (optional)
    4. Revocation check (server-side)
    
    Example:
        validator = LicenseValidator()
        result = validator.validate(license)
        if result.valid:
            if result.tier >= LicenseTier.PROFESSIONAL:
                # Enable pro features
                pass
    """
    
    def __init__(
        self,
        signing_key: Optional[str] = None,
        current_build_hash: Optional[str] = None,
        license_server_url: Optional[str] = None,
        check_revocation: bool = True,
        enforce_build_hash: bool = False
    ):
        """
        Initialize the license validator.
        
        Args:
            signing_key: Secret key for signature verification
            current_build_hash: Current build's hash for matching
            license_server_url: URL for revocation checks
            check_revocation: Whether to check revocation list
            enforce_build_hash: Whether to require build hash match
        """
        self.signing_key = signing_key or os.getenv("KRL_LICENSE_SIGNING_KEY", "")
        if not self.signing_key:
            logger.warning("No signing key provided - using insecure default")
            self.signing_key = "INSECURE_DEFAULT_KEY_DO_NOT_USE_IN_PRODUCTION"
        
        self.current_build_hash = current_build_hash or os.getenv("KRL_BUILD_HASH", "")
        self.license_server_url = license_server_url or os.getenv(
            "KRL_LICENSE_SERVER_URL", "https://api.krlabs.dev"
        )
        self.check_revocation = check_revocation
        self.enforce_build_hash = enforce_build_hash
        
        # Local cache of revoked licenses
        self._revocation_cache: Set[str] = set()
        self._revocation_cache_time: int = 0
        self._revocation_cache_ttl: int = 300  # 5 minutes
    
    def _verify_signature(self, license: EphemeralLicense) -> bool:
        """Verify the license signature."""
        canonical = json.dumps({
            "license_id": license.license_id,
            "customer_id": license.customer_id,
            "tier": license.tier.value,
            "issued_at": license.issued_at,
            "expires_at": license.expires_at,
            "build_hash": license.build_hash,
            "features": sorted(license.features)
        }, separators=(",", ":"), sort_keys=True)
        
        expected_signature = hmac.new(
            self.signing_key.encode("utf-8"),
            canonical.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(license.signature, expected_signature)
    
    def _check_revocation(self, license_id: str) -> bool:
        """
        Check if a license has been revoked.
        
        Returns True if revoked, False if valid.
        """
        # Check cache first
        now = int(time.time())
        if now - self._revocation_cache_time < self._revocation_cache_ttl:
            return license_id in self._revocation_cache
        
        # Refresh cache from server
        try:
            import requests
            
            response = requests.get(
                f"{self.license_server_url}/v1/licenses/revoked",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self._revocation_cache = set(data.get("revoked_licenses", []))
                self._revocation_cache_time = now
                return license_id in self._revocation_cache
            
        except Exception as e:
            logger.debug(f"Failed to check revocation list: {e}")
        
        # On failure, assume not revoked (fail open for availability)
        return False
    
    def validate(
        self,
        license: EphemeralLicense,
        current_time: Optional[int] = None
    ) -> ValidationResult:
        """
        Validate an ephemeral license.
        
        Args:
            license: The license to validate
            current_time: Current Unix timestamp (for testing)
            
        Returns:
            ValidationResult with validation status and details
        """
        now = current_time or int(time.time())
        
        # 1. Verify signature
        if not self._verify_signature(license):
            logger.warning(f"Invalid signature for license {license.license_id}")
            return ValidationResult(
                valid=False,
                license=license,
                error="Invalid license signature",
                error_code="INVALID_SIGNATURE"
            )
        
        # 2. Check expiration
        if license.is_expired(now):
            logger.info(f"License {license.license_id} has expired")
            return ValidationResult(
                valid=False,
                license=license,
                error="License has expired",
                error_code="EXPIRED"
            )
        
        # 3. Check build hash (if enforced)
        if self.enforce_build_hash and self.current_build_hash:
            if license.build_hash != self.current_build_hash:
                logger.warning(
                    f"Build hash mismatch for license {license.license_id}: "
                    f"expected {self.current_build_hash[:16]}..., "
                    f"got {license.build_hash[:16]}..."
                )
                return ValidationResult(
                    valid=False,
                    license=license,
                    error="License not valid for this build",
                    error_code="BUILD_MISMATCH"
                )
        
        # 4. Check revocation
        if self.check_revocation and self._check_revocation(license.license_id):
            logger.warning(f"License {license.license_id} has been revoked")
            return ValidationResult(
                valid=False,
                license=license,
                error="License has been revoked",
                error_code="REVOKED"
            )
        
        # Valid!
        logger.debug(
            f"License {license.license_id} validated successfully "
            f"(tier: {license.tier.value}, customer: {license.customer_id})"
        )
        
        return ValidationResult(
            valid=True,
            license=license,
            tier=license.tier
        )
    
    def validate_encoded(self, encoded_license: str) -> ValidationResult:
        """Validate an encoded license string."""
        try:
            license = EphemeralLicense.decode(encoded_license)
            return self.validate(license)
        except LicenseInvalidError as e:
            return ValidationResult(
                valid=False,
                error=str(e),
                error_code="DECODE_ERROR"
            )


# =============================================================================
# LICENSE MANAGER - High-level interface for runtime use
# =============================================================================

class LicenseManager:
    """
    High-level license management for runtime use.
    
    Provides a simple interface for applications to:
    - Load licenses from environment or file
    - Validate on startup
    - Check feature access
    - Handle license errors gracefully
    
    Example:
        manager = LicenseManager()
        manager.load_from_environment()
        
        if manager.has_feature("advanced_ml"):
            # Enable advanced ML features
            pass
        
        if manager.tier >= LicenseTier.PROFESSIONAL:
            # Enable pro features
            pass
    """
    
    def __init__(self, validator: Optional[LicenseValidator] = None):
        """Initialize the license manager."""
        self.validator = validator or LicenseValidator()
        self.current_license: Optional[EphemeralLicense] = None
        self.validation_result: Optional[ValidationResult] = None
    
    @property
    def tier(self) -> LicenseTier:
        """Get the current license tier."""
        if self.validation_result and self.validation_result.valid:
            return self.validation_result.tier
        return LicenseTier.COMMUNITY
    
    @property
    def is_valid(self) -> bool:
        """Check if current license is valid."""
        return self.validation_result is not None and self.validation_result.valid
    
    def load_from_environment(self) -> bool:
        """
        Load and validate license from environment variable.
        
        Looks for KRL_LICENSE environment variable.
        
        Returns:
            True if license loaded and validated successfully
        """
        encoded_license = os.getenv("KRL_LICENSE", "")
        if not encoded_license:
            logger.debug("No license found in environment")
            return False
        
        return self.load_from_string(encoded_license)
    
    def load_from_file(self, path: str) -> bool:
        """
        Load and validate license from file.
        
        Args:
            path: Path to license file
            
        Returns:
            True if license loaded and validated successfully
        """
        try:
            with open(path, "r") as f:
                encoded_license = f.read().strip()
            return self.load_from_string(encoded_license)
        except Exception as e:
            logger.warning(f"Failed to load license from {path}: {e}")
            return False
    
    def load_from_string(self, encoded_license: str) -> bool:
        """
        Load and validate license from encoded string.
        
        Args:
            encoded_license: Base64-encoded license string
            
        Returns:
            True if license loaded and validated successfully
        """
        try:
            self.current_license = EphemeralLicense.decode(encoded_license)
            self.validation_result = self.validator.validate(self.current_license)
            
            if self.validation_result.valid:
                logger.info(
                    f"License loaded: {self.current_license.license_id} "
                    f"(tier: {self.tier.value}, customer: {self.current_license.customer_id})"
                )
            else:
                logger.warning(
                    f"License validation failed: {self.validation_result.error}"
                )
            
            return self.validation_result.valid
            
        except Exception as e:
            logger.warning(f"Failed to load license: {e}")
            self.current_license = None
            self.validation_result = None
            return False
    
    def has_feature(self, feature: str) -> bool:
        """Check if a feature is enabled by the current license."""
        if self.current_license and self.is_valid:
            return self.current_license.has_feature(feature)
        return False
    
    def get_customer_id(self) -> Optional[str]:
        """Get the customer ID from the current license."""
        if self.current_license and self.is_valid:
            return self.current_license.customer_id
        return None
    
    def time_remaining(self) -> Optional[timedelta]:
        """Get time remaining until license expiration."""
        if self.current_license and self.is_valid:
            return self.current_license.time_remaining()
        return None


# =============================================================================
# MODULE-LEVEL SINGLETON
# =============================================================================

# Global license manager instance
_license_manager: Optional[LicenseManager] = None


def get_license_manager() -> LicenseManager:
    """Get or create the global license manager."""
    global _license_manager
    if _license_manager is None:
        _license_manager = LicenseManager()
        _license_manager.load_from_environment()
    return _license_manager


def get_current_tier() -> LicenseTier:
    """Get the current license tier."""
    return get_license_manager().tier


def has_feature(feature: str) -> bool:
    """Check if a feature is enabled."""
    return get_license_manager().has_feature(feature)


def require_tier(minimum_tier: LicenseTier):
    """
    Decorator to require a minimum license tier.
    
    Example:
        @require_tier(LicenseTier.PROFESSIONAL)
        def advanced_function():
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            current = get_current_tier()
            if not current >= minimum_tier:
                raise LicenseError(
                    f"{func.__name__} requires {minimum_tier.value} tier or higher. "
                    f"Current tier: {current.value}"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator
