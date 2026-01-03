# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2025 KR-Labs Foundation. All rights reserved.
# Licensed under Apache License 2.0 (see LICENSE file for details)

"""Abstract base class for data connectors."""

import hashlib
import ipaddress
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from urllib.parse import urlencode, urlparse

import requests
from krl_core import ConfigManager, FileCache, get_logger


# =============================================================================
# CONNECTOR QUALITY MIXIN
# =============================================================================

class ConnectorQualityMixin:
    """
    Mixin to add quality scoring capabilities to data connectors.

    Provides methods for connectors to expose their quality metrics
    and capabilities across different data domains.
    """

    def get_quality_scores(self, domain: str):
        """
        Get quality scores for this connector in a specific domain.

        This method uses the QualityScorer to compute 6-dimensional
        quality scores (temporal coverage, geographic granularity,
        update frequency, completeness, reliability, tier accessibility).

        Args:
            domain: Data domain (e.g., "labor", "health", "economic")

        Returns:
            QualityScore with 6-dimensional assessment

        Example:
            >>> connector = FREDConnector()
            >>> scores = connector.get_quality_scores("economic")
            >>> print(scores.temporal_coverage)
            0.95
        """
        from krl_data_connectors.matrix.quality_scorer import QualityScorer

        scorer = QualityScorer()
        connector_name = self.__class__.__name__.replace("Connector", "").lower()

        return scorer.score_connector(
            connector_name=connector_name,
            domain=domain
        )

    def get_domain_capabilities(self) -> dict[str, dict]:
        """
        Introspect this connector's capabilities across domains.

        Returns a dictionary mapping domain names to capability profiles,
        showing what this connector can provide for each domain.

        Returns:
            Dict mapping domain names to capability profiles

        Example:
            >>> connector = CensusConnector()
            >>> caps = connector.get_domain_capabilities()
            >>> print(caps["demographic"]["geographic_levels"])
            ["national", "state", "county", "tract"]
        """
        # Default implementation - connectors can override
        connector_name = self.__class__.__name__.replace("Connector", "").lower()

        # Get metadata from QualityScorer
        from krl_data_connectors.matrix.quality_scorer import QualityScorer

        scorer = QualityScorer()
        metadata = scorer.CONNECTOR_METADATA.get(connector_name, scorer.CONNECTOR_METADATA["default"])

        return {
            "all_domains": {
                "temporal_years": metadata.get("temporal_years", 10),
                "geographic_levels": metadata.get("geographic_levels", ["national"]),
                "update_cadence": metadata.get("update_cadence", "annual"),
                "official_source": metadata.get("official_source", False),
                "tier": metadata.get("tier", "community")
            }
        }


# =============================================================================
# BASE CONNECTOR
# =============================================================================

class BaseConnector(ABC, ConnectorQualityMixin):
    """
    Abstract base class for data connectors.

    Provides common functionality for all data connectors including:
    - Structured logging
    - Configuration management
    - Intelligent caching
    - HTTP session management
    - Error handling and retries
    - Rate limiting

    Subclasses must implement:
    - _get_api_key(): Return API key from config
    - connect(): Establish connection to data source
    - fetch(): Fetch data from source

    Args:
        api_key: API key for the data source (optional if in config)
        cache_dir: Directory for cache files (default: from config or ~/.krl_cache)
        cache_ttl: Cache time-to-live in seconds (default: 3600)
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum number of retry attempts (default: 3)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 3600,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        # Initialize logger
        self.logger = get_logger(self.__class__.__name__)

        # Initialize configuration manager
        self.config = ConfigManager()

        # Initialize cache
        cache_dir = cache_dir or self.config.get("CACHE_DIR", default="~/.krl_cache")
        self.cache = FileCache(
            cache_dir=cache_dir,
            default_ttl=cache_ttl,
            namespace=self.__class__.__name__.lower(),
        )

        # Get API key
        self.api_key = api_key or self._get_api_key()
        if not self.api_key:
            self.logger.warning("No API key provided", extra={"connector": self.__class__.__name__})

        # HTTP session settings
        self.timeout = timeout
        self.max_retries = max_retries
        self.session: Optional[requests.Session] = None

        self.logger.info(
            "Connector initialized",
            extra={
                "connector": self.__class__.__name__,
                "cache_dir": str(self.cache.cache_dir),
                "cache_ttl": cache_ttl,
                "has_api_key": bool(self.api_key),
            },
        )

    @property
    def cache_dir(self) -> str:
        """
        Get the cache directory path.

        Returns:
            Cache directory path as string
        """
        return str(self.cache.cache_dir)

    @cache_dir.setter
    def cache_dir(self, value: str):
        """
        Set the cache directory with path traversal prevention.

        Args:
            value: New cache directory path

        Raises:
            ValueError: If path contains directory traversal attempts
        """
        import os
        from pathlib import Path

        # Reject obvious path traversal attempts
        if (
            ".." in value
            or value.startswith("/etc/")
            or value.startswith("/sys/")
            or value.startswith("/proc/")
        ):
            raise ValueError(f"Invalid cache directory path: {value}")

        # Normalize and validate path
        try:
            normalized = os.path.normpath(value)
            # Ensure normalized path doesn't escape to system directories
            if (
                normalized.startswith("/etc/")
                or normalized.startswith("/sys/")
                or normalized.startswith("/proc/")
            ):
                raise ValueError(f"Cannot set cache directory to system path: {normalized}")
        except Exception as e:
            raise ValueError(f"Invalid cache directory path: {value}") from e

        # Update cache directory
        self.cache.cache_dir = Path(value)

    @abstractmethod
    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from configuration.

        Should be implemented by subclasses to retrieve the appropriate
        API key from environment variables or config files.

        Returns:
            API key or None if not found
        """

    def _init_session(self) -> requests.Session:
        """
        Initialize HTTP session with retry logic.

        Returns:
            Configured requests.Session object
        """
        if self.session is None:
            self.session = requests.Session()

            # Configure retries
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry

            retry_strategy = Retry(
                total=self.max_retries,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"],
            )

            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)

            self.logger.debug("HTTP session initialized")

        return self.session

    def _mask_sensitive_params(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Mask sensitive parameters for logging.

        Args:
            params: Request parameters

        Returns:
            Parameters with sensitive values masked
        """
        if not params:
            return {}

        # Keys that should be masked
        sensitive_keys = {
            "api_key",
            "apikey",
            "key",
            "token",
            "access_token",
            "password",
            "secret",
            "auth",
            "authorization",
            "credentials",
        }

        masked = {}
        for key, value in params.items():
            key_lower = key.lower()
            if key_lower in sensitive_keys or any(
                sensitive in key_lower for sensitive in sensitive_keys
            ):
                masked[key] = "***MASKED***"
            else:
                masked[key] = value

        return masked

    def _validate_url(self, url: str, allow_http: bool = False) -> None:
        """
        Validate URL for security issues.

        Prevents SSRF attacks by blocking:
        - Internal/private IP addresses
        - Cloud metadata endpoints
        - Dangerous protocols (file://, ftp://, etc.)
        - Localhost references

        Args:
            url: URL to validate
            allow_http: Whether to allow HTTP (default: False, HTTPS only)

        Raises:
            ValueError: If URL is invalid or potentially dangerous
        """
        try:
            parsed = urlparse(url)

            # Check protocol
            if parsed.scheme not in ["http", "https"]:
                raise ValueError(f"Unsupported protocol: {parsed.scheme}")

            if not allow_http and parsed.scheme == "http":
                raise ValueError("HTTP not allowed, use HTTPS")

            # Check for localhost
            hostname = parsed.hostname
            if not hostname:
                raise ValueError("Invalid URL: no hostname")

            hostname_lower = hostname.lower()

            # Block localhost references (not binding - false positive for B104)
            if hostname_lower in ["localhost", "127.0.0.1", "0.0.0.0", "::1"]:  # nosec B104
                raise ValueError(f"Localhost access not allowed: {hostname}")

            # Block cloud metadata endpoints
            metadata_hosts = [
                "169.254.169.254",  # AWS, Azure, GCP
                "metadata.google.internal",  # GCP
                "metadata",
            ]
            if hostname_lower in metadata_hosts:
                raise ValueError(f"Cloud metadata access not allowed: {hostname}")

            # Try to parse as IP address
            is_ip_address = False
            try:
                ip = ipaddress.ip_address(hostname)
                is_ip_address = True

                # Block private IP ranges
                if ip.is_private or ip.is_loopback or ip.is_link_local:
                    raise ValueError(f"Private IP address not allowed: {hostname}")

            except ValueError as e:
                # Check if this is our security error or a parsing error
                if is_ip_address or "not allowed" in str(e):
                    # This is a security violation, re-raise it
                    raise
                # Not an IP address, check for internal hostnames
                if "internal" in hostname_lower or "local" in hostname_lower:
                    raise ValueError(f"Internal hostname not allowed: {hostname}")

        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Invalid URL: {e}")

    def _validate_string_length(
        self, value: str, field_name: str, max_length: int = 1000, min_length: int = 0
    ) -> None:
        """
        Validate string length.

        Args:
            value: String value to validate
            field_name: Name of field (for error messages)
            max_length: Maximum allowed length (default: 1000)
            min_length: Minimum required length (default: 0)

        Raises:
            ValueError: If string length is invalid
        """
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")

        value_len = len(value)

        if value_len < min_length:
            raise ValueError(f"{field_name} must be at least {min_length} characters")

        if value_len > max_length:
            raise ValueError(f"{field_name} must not exceed {max_length} characters")

    def _make_cache_key(self, url: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a cache key from URL and parameters.

        Args:
            url: Request URL
            params: Request parameters

        Returns:
            Cache key (SHA256 hash of URL + params)
        """
        # Create a deterministic string representation
        param_str = urlencode(sorted((params or {}).items()))
        cache_str = f"{url}?{param_str}"

        # Hash to create shorter key
        return hashlib.sha256(cache_str.encode()).hexdigest()

    def _make_request(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Make HTTP request with caching and error handling.

        Args:
            url: Request URL
            params: Query parameters
            use_cache: Whether to use cache (default: True)

        Returns:
            Response data as dictionary

        Raises:
            requests.RequestException: If request fails after retries
        """
        # Check cache first
        if use_cache:
            cache_key = self._make_cache_key(url, params)
            cached_response = self.cache.get(cache_key)

            if cached_response is not None:
                self.logger.info("Cache hit", extra={"url": url, "cache_key": cache_key[:16]})
                return cached_response

        # Make request
        session = self._init_session()

        # Mask sensitive parameters for logging
        masked_params = self._mask_sensitive_params(params)
        self.logger.info("Making API request", extra={"url": url, "params": masked_params})

        try:
            response = session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            # Cache successful response
            if use_cache:
                cache_key = self._make_cache_key(url, params)
                self.cache.set(cache_key, data)

                self.logger.debug("Response cached", extra={"cache_key": cache_key[:16]})

            return data

        except requests.exceptions.HTTPError as e:
            extra_info = {"url": url}
            if e.response is not None:
                extra_info["status_code"] = e.response.status_code
            self.logger.error("HTTP error", extra=extra_info, exc_info=True)
            raise

        except requests.exceptions.Timeout:
            self.logger.error(
                "Request timeout", extra={"url": url, "timeout": self.timeout}, exc_info=True
            )
            raise

        except requests.exceptions.RequestException as e:
            self.logger.error("Request failed", extra={"url": url, "error": str(e)}, exc_info=True)
            raise

    @abstractmethod
    def connect(self) -> None:
        """
        Establish connection to the data source.

        Should be implemented by subclasses to perform any necessary
        connection setup or authentication.
        """

    @abstractmethod
    def fetch(self, **kwargs: Any) -> Any:
        """
        Fetch data from the source.

        Should be implemented by subclasses to retrieve data.

        Args:
            **kwargs: Connector-specific parameters

        Returns:
            Fetched data (format depends on connector)
        """

    def disconnect(self) -> None:
        """
        Close connection and cleanup resources.

        Closes HTTP session and cleans up any resources.
        Can be overridden by subclasses for additional cleanup.
        """
        if self.session:
            self.session.close()
            self.session = None
            self.logger.debug("HTTP session closed")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics (hits, misses, size, etc.)
        """
        return self.cache.get_stats()

    def clear_cache(self) -> None:
        """Clear all cached responses for this connector."""
        self.cache.clear()
        self.logger.info("Cache cleared")

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
        return False

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"{self.__class__.__name__}("
            f"has_api_key={bool(self.api_key)}, "
            f"cache_dir='{self.cache.cache_dir}'"
            ")"
        )
