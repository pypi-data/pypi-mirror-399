# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
License Validator - Validates connector access based on user subscription tier.

This module integrates with the KR-Labs license server (same infrastructure as
Model Zoo) to enforce tier-based access control for data connectors.
"""

import hashlib
import os
from typing import Dict, Optional

import requests

from .connector_registry import ConnectorRegistry, DataTier


class LicenseError(Exception):
    """
    Raised when connector access is denied due to tier restrictions.

    This exception is raised when a user attempts to access a connector
    that requires a higher subscription tier than they currently have.

    Example:
        >>> from krl_data_connectors import FRED_Full
        >>> fred = FRED_Full(api_key="community_key")
        Traceback (most recent call last):
        ...
        LicenseError: FRED_Full requires Professional tier or higher.
        Your current tier: Community. Upgrade at https://krlabs.dev/pricing
    """

    pass


class RateLimitError(Exception):
    """
    Raised when daily request limit is exceeded.

    This exception is raised when a user has exhausted their daily API
    request quota for their subscription tier.

    Example:
        >>> fred.get_series("UNRATE")
        Traceback (most recent call last):
        ...
        RateLimitError: Daily request limit exceeded (100/100).
        Resets at 2026-03-02 00:00:00 UTC. Upgrade to Professional for 1,000/day.
    """

    pass


class ConnectorLicenseValidator:
    """
    Validates connector access based on user subscription tier.

    Integrates with the KR-Labs license server (same infrastructure as Model Zoo)
    to enforce tier-based access control. Validates both tier access and usage limits.

    Attributes:
        license_server_url: URL of the KR-Labs license validation server
        timeout: Request timeout in seconds (default: 5)

    Example:
        >>> validator = ConnectorLicenseValidator()
        >>> result = validator.validate_access(
        ...     api_key="krl_abc123...",
        ...     connector_name="FRED_Full"
        ... )
        >>> print(result['allowed'])
        True
        >>> print(result['tier'])
        'professional'
    """

    def __init__(self, license_server_url: str = None, timeout: int = 5):
        """
        Initialize the license validator.

        Args:
            license_server_url: URL of license server (defaults to production)
            timeout: Request timeout in seconds
        """
        self.license_server_url = license_server_url or os.getenv(
            "KRL_LICENSE_SERVER_URL", "https://api.krlabs.dev"
        )
        self.timeout = timeout

    def validate_access(
        self, api_key: Optional[str], connector_name: str, skip_remote_validation: bool = False
    ) -> Dict[str, any]:
        """
        Validate user access to a specific connector.

        This is the main entry point for license validation. It performs:
        1. Tier requirement lookup (from local registry)
        2. User tier validation (from license server)
        3. Tier hierarchy check (can user access this connector?)
        4. Usage limit check (have they exceeded daily quota?)

        Args:
            api_key: User's KRL API key (None for Community tier)
            connector_name: Name of connector to validate
            skip_remote_validation: Skip license server call (for testing/offline)

        Returns:
            Dictionary with validation results:
            {
                'allowed': bool,
                'user_tier': str,
                'required_tier': str,
                'reason': str,
                'requests_remaining': int,
                'daily_limit': int,
                'upgrade_url': str
            }

        Raises:
            LicenseError: If access is denied
            RateLimitError: If daily limit exceeded

        Example:
            >>> validator = ConnectorLicenseValidator()
            >>> result = validator.validate_access(
            ...     api_key="krl_abc123",
            ...     connector_name="FRED_Full"
            ... )
            >>> if result['allowed']:
            ...     print(f"Access granted! {result['requests_remaining']} requests remaining")
        """
        # Check for global license validation bypass (testing mode)
        if os.environ.get("KRL_SKIP_LICENSE_VALIDATION", "").lower() == "true":
            return {
                "allowed": True,
                "user_tier": "ENTERPRISE",
                "required_tier": str(connector_name),
                "reason": "License validation bypassed (KRL_SKIP_LICENSE_VALIDATION=true)",
                "requests_remaining": 999999,
                "daily_limit": 999999,
                "upgrade_url": None,
            }

        # Step 1: Get required tier for this connector
        try:
            required_tier = ConnectorRegistry.get_required_tier(connector_name)
        except KeyError as e:
            raise LicenseError(f"Unknown connector: {connector_name}") from e

        # Step 2: Determine user tier
        if api_key is None or api_key == "":
            # No API key = Community tier
            user_tier = DataTier.COMMUNITY
            skip_remote_validation = True
        elif skip_remote_validation:
            # For testing/offline mode, assume tier from API key prefix
            user_tier = self._infer_tier_from_key(api_key)
        else:
            # Production: validate with license server
            user_tier = self._get_user_tier(api_key)

        # Step 3: Check tier hierarchy
        tier_access_granted = self._check_tier_access(user_tier, required_tier)

        # Step 4: Check usage limits (if allowed)
        usage_info = {}
        if tier_access_granted and not skip_remote_validation:
            usage_info = self._check_usage_limits(api_key or "", user_tier)
        else:
            # Default limits for Community tier (no remote check)
            usage_info = {
                "requests_remaining": 100 if user_tier == DataTier.COMMUNITY else 1000,
                "daily_limit": 100 if user_tier == DataTier.COMMUNITY else 1000,
                "requests_used": 0,
            }

        # Build response
        result = {
            "allowed": tier_access_granted,
            "user_tier": user_tier.value,
            "required_tier": required_tier.value,
            "connector_name": connector_name,
            "requests_remaining": usage_info.get("requests_remaining", 0),
            "daily_limit": usage_info.get("daily_limit", 0),
            "requests_used": usage_info.get("requests_used", 0),
            "upgrade_url": "https://krlabs.dev/pricing",
        }

        if not tier_access_granted:
            result["reason"] = (
                f"{connector_name} requires {required_tier.value.title()} tier or higher. "
                f"Your current tier: {user_tier.value.title()}. "
                f"Upgrade at {result['upgrade_url']}"
            )
            raise LicenseError(result["reason"])

        # Check if rate limit exceeded
        if usage_info.get("requests_remaining", 1) <= 0:
            result["reason"] = (
                f"Daily request limit exceeded ({usage_info['requests_used']}/{usage_info['daily_limit']}). "
                f"Resets at midnight UTC. "
                f"Upgrade to Professional for 1,000-100,000 requests/day."
            )
            raise RateLimitError(result["reason"])

        result["reason"] = "Access granted"
        return result

    def _get_user_tier(self, api_key: str) -> DataTier:
        """
        Query license server for user's subscription tier.

        Args:
            api_key: User's KRL API key

        Returns:
            DataTier enum value

        Raises:
            LicenseError: If API key is invalid or server unreachable
        """
        try:
            response = requests.post(
                f"{self.license_server_url}/v1/validate",
                json={"api_key": api_key, "resource_type": "data_connector"},
                timeout=self.timeout,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 401:
                raise LicenseError("Invalid API key. Get your key at https://krlabs.dev/account")

            if response.status_code != 200:
                # Fail open for server errors (don't block legitimate users)
                import warnings

                warnings.warn(
                    f"License server error ({response.status_code}). "
                    "Temporarily allowing access.",
                    UserWarning,
                )
                return DataTier.PROFESSIONAL

            data = response.json()
            tier_str = data.get("tier", "community")
            return DataTier(tier_str)

        except requests.exceptions.RequestException as e:
            # Network error - fail open (don't block legitimate users)
            import warnings

            warnings.warn(
                f"Could not reach license server: {e}. Temporarily allowing access.", UserWarning
            )
            return DataTier.PROFESSIONAL

    def _check_tier_access(self, user_tier: DataTier, required_tier: DataTier) -> bool:
        """
        Check if user tier grants access to required tier.

        Tier hierarchy: Community < Professional < Enterprise

        Args:
            user_tier: User's current subscription tier
            required_tier: Minimum tier required for connector

        Returns:
            True if user has sufficient tier, False otherwise
        """
        tier_hierarchy = {
            DataTier.COMMUNITY: 1,
            DataTier.PROFESSIONAL: 2,
            DataTier.ENTERPRISE: 3,
        }
        return tier_hierarchy[user_tier] >= tier_hierarchy[required_tier]

    def _check_usage_limits(self, api_key: str, tier: DataTier) -> Dict[str, int]:
        """
        Check usage limits from rate limiter (Redis-backed).

        Args:
            api_key: User's KRL API key
            tier: User's subscription tier

        Returns:
            Dictionary with usage information:
            {
                'requests_used': int,
                'requests_remaining': int,
                'daily_limit': int,
                'reset_at': str (ISO timestamp)
            }
        """
        try:
            response = requests.get(
                f"{self.license_server_url}/v1/usage",
                params={"api_key": api_key},
                timeout=self.timeout,
            )

            if response.status_code == 200:
                return response.json()
            else:
                # Fail open - return generous limits
                return {
                    "requests_used": 0,
                    "requests_remaining": 10000,
                    "daily_limit": 10000,
                }

        except requests.exceptions.RequestException:
            # Network error - fail open
            return {
                "requests_used": 0,
                "requests_remaining": 10000,
                "daily_limit": 10000,
            }

    def _infer_tier_from_key(self, api_key: str) -> DataTier:
        """
        Infer tier from API key prefix (for testing/offline mode).

        API key format: krl_{tier}_{random_hash}
        Example: krl_pro_abc123... = Professional tier

        Args:
            api_key: User's KRL API key

        Returns:
            DataTier enum value (defaults to COMMUNITY if can't infer)
        """
        if not api_key or not api_key.startswith("krl_"):
            return DataTier.COMMUNITY

        parts = api_key.split("_")
        if len(parts) < 2:
            return DataTier.COMMUNITY

        tier_prefix = parts[1].lower()
        tier_map = {
            "community": DataTier.COMMUNITY,
            "comm": DataTier.COMMUNITY,
            "free": DataTier.COMMUNITY,
            "professional": DataTier.PROFESSIONAL,
            "pro": DataTier.PROFESSIONAL,
            "team": DataTier.PROFESSIONAL,
            "enterprise": DataTier.ENTERPRISE,
            "ent": DataTier.ENTERPRISE,
            "custom": DataTier.ENTERPRISE,
        }

        return tier_map.get(tier_prefix, DataTier.COMMUNITY)

    def increment_usage(self, api_key: str) -> None:
        """
        Increment usage counter for this API key (called after successful request).

        Args:
            api_key: User's KRL API key
        """
        if not api_key or api_key == "":
            return  # Community tier, no tracking

        try:
            requests.post(
                f"{self.license_server_url}/v1/usage/increment",
                json={"api_key": api_key},
                timeout=self.timeout,
            )
        except requests.exceptions.RequestException:
            # Don't fail the request if usage tracking fails
            pass


# Singleton instance for reuse across connectors
_validator_instance: Optional[ConnectorLicenseValidator] = None


def get_validator() -> ConnectorLicenseValidator:
    """
    Get the singleton license validator instance.

    Returns:
        ConnectorLicenseValidator instance

    Example:
        >>> validator = get_validator()
        >>> validator.validate_access(api_key="krl_...", connector_name="FRED_Full")
    """
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = ConnectorLicenseValidator()
    return _validator_instance
