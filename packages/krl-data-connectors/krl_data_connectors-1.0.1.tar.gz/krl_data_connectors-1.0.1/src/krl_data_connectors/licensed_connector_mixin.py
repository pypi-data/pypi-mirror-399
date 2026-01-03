# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2025 KR-Labs Foundation. All rights reserved.
# Licensed under Apache License 2.0 (see LICENSE file for details)

"""
Licensed Connector Mixin

Provides automatic license validation for tiered connectors.
This mixin integrates with the license validation infrastructure
to enforce tier access control.
"""

import os
from functools import wraps
from typing import Any, Callable, Optional

from krl_core import get_logger

from .core import (
    ConnectorLicenseValidator,
    ConnectorRegistry,
    DataTier,
    LicenseError,
    RateLimitError,
)

logger = get_logger(__name__)


def requires_license(func: Callable) -> Callable:
    """
    Decorator to validate license before executing data fetch methods.

    This decorator should be applied to any method that fetches data from
    a tiered connector (Professional or Enterprise).

    Args:
        func: The method to wrap with license validation

    Returns:
        Wrapped method with license validation

    Raises:
        LicenseError: If user's tier is insufficient
        RateLimitError: If daily quota is exceeded

    Example:
        ```python
        class FREDFullConnector(LicensedConnectorMixin, BaseConnector):
            @requires_license
            def get_series(self, series_id: str):
                # This method will be protected by license validation
                return self._fetch_series(series_id)
        ```
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Check if license checking is disabled (developer mode)
        if getattr(self, "_skip_license_check", False):
            return func(self, *args, **kwargs)

        # Get connector name from class
        connector_name = getattr(self, "_connector_name", None)
        if not connector_name:
            # Derive from class name
            class_name = self.__class__.__name__
            # Remove 'Connector' suffix if present
            connector_name = class_name.replace("Connector", "")

        # Get API key
        api_key = getattr(self, "api_key", None) or os.environ.get("KRL_API_KEY")

        # Check for developer mode (skip remote validation)
        skip_validation = os.environ.get("KRL_SKIP_LICENSE_VALIDATION", "").lower() in (
            "true",
            "1",
            "yes",
        )

        # Validate license
        validator = ConnectorLicenseValidator()

        try:
            result = validator.validate_access(
                api_key=api_key,
                connector_name=connector_name,
                skip_remote_validation=skip_validation,
            )

            if not result["allowed"]:
                raise LicenseError(
                    f"Access denied to {connector_name}. "
                    f"Required tier: {result.get('required_tier')}. "
                    f"Your tier: {result.get('user_tier')}. "
                    f"Upgrade at: https://app.krlabs.dev/upgrade"
                )

            # Log usage
            logger.debug(
                f"License validated for {connector_name}",
                extra={
                    "connector": connector_name,
                    "user_tier": result.get("user_tier"),
                    "requests_remaining": result.get("requests_remaining"),
                },
            )

            # Execute the original method
            response = func(self, *args, **kwargs)

            # Increment usage counter after successful request
            try:
                validator.increment_usage(api_key=api_key)
            except Exception as e:
                logger.warning(f"Failed to increment usage counter: {e}")

            return response

        except LicenseError:
            # Re-raise license errors
            raise
        except RateLimitError as e:
            # Add helpful message to rate limit errors
            logger.error(
                f"Rate limit exceeded for {connector_name}",
                extra={
                    "connector": connector_name,
                    "daily_limit": e.daily_limit,
                    "requests_used": e.requests_used,
                    "reset_time": e.reset_time,
                },
            )
            raise
        except Exception as e:
            # Log unexpected errors but don't block (fail-open)
            logger.error(
                f"Unexpected error during license validation: {e}",
                extra={"connector": connector_name},
            )
            # Allow the request to proceed (fail-open behavior)
            return func(self, *args, **kwargs)

    return wrapper


class LicensedConnectorMixin:
    """
    Mixin class for connectors requiring license validation.

    This mixin provides automatic license validation for Professional
    and Enterprise tier connectors. It integrates with the license
    validation infrastructure to enforce tier access control and
    rate limiting.

    Usage:
        ```python
        from krl_data_connectors import BaseConnector, LicensedConnectorMixin

        class FREDFullConnector(LicensedConnectorMixin, BaseConnector):
            _connector_name = "FRED_Full"
            _required_tier = DataTier.PROFESSIONAL

            @requires_license
            def get_series(self, series_id: str):
                # Data fetching logic
                return self._fetch_series(series_id)
        ```

    Attributes:
        _connector_name: Name of connector (must match ConnectorRegistry)
        _required_tier: Minimum tier required (DataTier enum)
        _skip_license_check: Set to True to disable license checking (testing only)
    """

    _connector_name: Optional[str] = None
    _required_tier: Optional[DataTier] = None
    _skip_license_check: bool = False

    def __init__(self, *args, **kwargs):
        """Initialize mixin and validate configuration."""
        super().__init__(*args, **kwargs)

        # Validate that connector name is set
        if not self._connector_name and not self._skip_license_check:
            logger.warning(
                f"{self.__class__.__name__} missing _connector_name attribute. "
                "License validation may not work correctly."
            )

        # Log license configuration
        if not self._skip_license_check:
            logger.info(
                f"Licensed connector initialized: {self._connector_name}",
                extra={
                    "connector": self._connector_name,
                    "required_tier": self._required_tier.name if self._required_tier else "UNKNOWN",
                    "has_api_key": bool(
                        getattr(self, "api_key", None) or os.environ.get("KRL_API_KEY")
                    ),
                },
            )

    def check_license(self, api_key: Optional[str] = None) -> dict:
        """
        Manually check license status without making a data request.

        Useful for:
        - Pre-flight checks before expensive operations
        - UI/CLI status displays
        - Testing and debugging

        Args:
            api_key: API key to check (defaults to self.api_key or env var)

        Returns:
            Dictionary with validation result:
            {
                'allowed': bool,
                'user_tier': str,
                'required_tier': str,
                'requests_remaining': int,
                'daily_limit': int,
                'reset_at': str
            }

        Example:
            ```python
            connector = FREDFullConnector(api_key="krl_pro_abc123")
            status = connector.check_license()

            if status['allowed']:
                print(f"Access granted. {status['requests_remaining']} requests remaining.")
            else:
                print(f"Access denied. Please upgrade to {status['required_tier']}.")
            ```
        """
        if self._skip_license_check:
            return {
                "allowed": True,
                "user_tier": "TESTING",
                "required_tier": "TESTING",
                "requests_remaining": 999999,
                "daily_limit": 999999,
                "reset_at": "N/A",
            }

        api_key = api_key or getattr(self, "api_key", None) or os.environ.get("KRL_API_KEY")
        connector_name = self._connector_name or self.__class__.__name__.replace("Connector", "")

        # Check for developer mode
        skip_validation = os.environ.get("KRL_SKIP_LICENSE_VALIDATION", "").lower() in (
            "true",
            "1",
            "yes",
        )

        validator = ConnectorLicenseValidator()

        try:
            return validator.validate_access(
                api_key=api_key,
                connector_name=connector_name,
                skip_remote_validation=skip_validation,
            )
        except (LicenseError, RateLimitError) as e:
            # Return structured error info instead of raising
            return {"allowed": False, "error": str(e), "error_type": e.__class__.__name__}

    def get_required_tier(self) -> DataTier:
        """
        Get the minimum tier required for this connector.

        Returns:
            DataTier enum (COMMUNITY, PROFESSIONAL, or ENTERPRISE)

        Example:
            ```python
            connector = FREDFullConnector()
            tier = connector.get_required_tier()
            print(f"This connector requires: {tier.name}")
            # Output: "This connector requires: PROFESSIONAL"
            ```
        """
        if self._required_tier:
            return self._required_tier

        # Look up from registry
        connector_name = self._connector_name or self.__class__.__name__.replace("Connector", "")

        try:
            return ConnectorRegistry.get_required_tier(connector_name)
        except KeyError:
            logger.warning(
                f"Connector {connector_name} not found in registry. "
                "Defaulting to PROFESSIONAL tier."
            )
            return DataTier.PROFESSIONAL

    def get_usage_info(self, api_key: Optional[str] = None) -> dict:
        """
        Get current usage statistics for this API key.

        Args:
            api_key: API key to check (defaults to self.api_key or env var)

        Returns:
            Dictionary with usage information:
            {
                'requests_used': int,
                'requests_remaining': int,
                'daily_limit': int,
                'reset_at': str (ISO 8601 timestamp),
                'tier': str
            }

        Example:
            ```python
            connector = FREDFullConnector(api_key="krl_pro_abc123")
            usage = connector.get_usage_info()

            print(f"Used: {usage['requests_used']}/{usage['daily_limit']}")
            print(f"Resets at: {usage['reset_at']}")
            ```
        """
        if self._skip_license_check:
            return {
                "requests_used": 0,
                "requests_remaining": 999999,
                "daily_limit": 999999,
                "reset_at": "N/A",
                "tier": "TESTING",
            }

        api_key = api_key or getattr(self, "api_key", None) or os.environ.get("KRL_API_KEY")

        validator = ConnectorLicenseValidator()

        try:
            status = self.check_license(api_key=api_key)
            return {
                "requests_used": status.get("daily_limit", 0) - status.get("requests_remaining", 0),
                "requests_remaining": status.get("requests_remaining", 0),
                "daily_limit": status.get("daily_limit", 0),
                "reset_at": status.get("reset_at", "Unknown"),
                "tier": status.get("user_tier", "Unknown"),
            }
        except Exception as e:
            logger.error(f"Failed to get usage info: {e}")
            return {"error": str(e), "error_type": e.__class__.__name__}


# Convenience function for testing
def skip_license_check(connector_instance):
    """
    Disable license checking for a connector instance (testing only).

    **WARNING:** This should ONLY be used in testing environments.
    Never use this in production code.

    Args:
        connector_instance: Instance of a LicensedConnectorMixin subclass

    Example:
        ```python
        # In your test file
        connector = FREDFullConnector(api_key="test_key")
        skip_license_check(connector)

        # Now license validation is disabled
        data = connector.get_series("UNRATE")  # No license check
        ```
    """
    if not isinstance(connector_instance, LicensedConnectorMixin):
        raise TypeError(
            f"skip_license_check() requires a LicensedConnectorMixin instance, "
            f"got {type(connector_instance)}"
        )

    connector_instance._skip_license_check = True
    logger.warning(
        f"License checking DISABLED for {connector_instance.__class__.__name__}. "
        "This should ONLY be used in testing!"
    )


__all__ = [
    "LicensedConnectorMixin",
    "requires_license",
    "skip_license_check",
]
