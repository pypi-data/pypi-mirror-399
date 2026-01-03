# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
FRED Full Connector - Professional Tier

Complete access to Federal Reserve Economic Data (FRED) database.
Requires Professional API key.

Features:
- 800,000+ economic time series
- Historical data back to 1776
- Real-time updates
- Custom data transformations
- Release calendar
- Category browsing

Rate Limiting:
- FRED API: ~120 requests/minute (enforced via token bucket)
- Automatic exponential backoff on 429 responses
- Minimum 500ms between requests to avoid bursts

Pricing: Included with Professional tier ($199/month)

Usage:
    from krl_data_connectors.professional import FREDFullConnector
    
    fred = FREDFullConnector(api_key="krl_pro_abc123")
    
    # Access any FRED series
    data = fred.get_series("MORTGAGE15US")
    
    # Search for series
    results = fred.search_series("unemployment", limit=10)
    
    # Get release information
    releases = fred.get_releases()
    
    # Check rate limit status
    print(fred.rate_limit_status)
"""

from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors import BaseConnector, LicensedConnectorMixin, requires_license
from krl_data_connectors.core import DataTier
from krl_data_connectors.core.rate_limiter import (
    AgencyConfig,
    RateLimiter,
    RateLimiterRegistry,
    RateLimitExceeded,
)


class FREDFullConnector(LicensedConnectorMixin, BaseConnector):
    """
    FRED Full Connector - Professional Tier

    Complete access to 800,000+ FRED economic time series.
    Requires Professional or Enterprise API key.
    
    Rate Limiting:
        This connector enforces FRED's API rate limits (~120 requests/minute)
        using a token bucket algorithm with automatic throttling. If you're
        making many requests, the connector will automatically space them out.
        
        Check `rate_limit_status` property for current usage.
    """

    _connector_name = "FRED_Full"
    _required_tier = DataTier.PROFESSIONAL
    
    # Shared rate limiter across all instances
    _rate_limiter: Optional[RateLimiter] = None

    def __init__(
        self,
        api_key: str,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 3600,
        timeout: int = 30,
        max_retries: int = 3,
        enable_rate_limiting: bool = True,
    ):
        """
        Initialize FRED Full connector.

        Args:
            api_key: KRL Professional API key (required)
            cache_dir: Directory for caching responses
            cache_ttl: Cache time-to-live in seconds
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            enable_rate_limiting: Enable automatic rate limiting (default: True)

        Raises:
            ValueError: If api_key is not provided
        """
        if not api_key:
            raise ValueError(
                "Professional API key required for FRED Full access. "
                "Get your key at: https://krlabs.dev/pricing"
            )

        # Initialize BaseConnector
        BaseConnector.__init__(
            self,
            api_key=api_key,
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Initialize LicensedConnectorMixin
        LicensedConnectorMixin.__init__(self)

        self.base_url = "https://api.stlouisfed.org/fred"
        self.fred_api_key = None  # Will be retrieved from KRL license server
        self.enable_rate_limiting = enable_rate_limiting
        
        # Initialize rate limiter (singleton per agency)
        if enable_rate_limiting and FREDFullConnector._rate_limiter is None:
            registry = RateLimiterRegistry()
            FREDFullConnector._rate_limiter = registry.get_limiter(AgencyConfig.FRED())

        self.logger.info(
            "Initialized FRED Full connector (Professional tier)",
            extra={
                "connector": self._connector_name,
                "rate_limiting": enable_rate_limiting,
            },
        )

    @property
    def rate_limiter(self) -> Optional[RateLimiter]:
        """Get the rate limiter instance."""
        return FREDFullConnector._rate_limiter if self.enable_rate_limiting else None

    @property
    def rate_limit_status(self) -> Dict[str, Any]:
        """
        Get current rate limit status.
        
        Returns:
            Dictionary with current limits, usage, and availability
        """
        if self.rate_limiter:
            return self.rate_limiter.get_status()
        return {"rate_limiting": "disabled"}

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a rate-limited request to FRED API.
        
        Args:
            endpoint: API endpoint URL
            params: Request parameters
            
        Returns:
            JSON response data
            
        Raises:
            RateLimitExceeded: If rate limit exceeded and can't retry
        """
        # Acquire rate limit permission (blocks if necessary)
        if self.rate_limiter:
            self.rate_limiter.acquire()
        
        try:
            response = self.session.get(endpoint, params=params, timeout=self.timeout)
            
            # Handle rate limit response
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                if self.rate_limiter:
                    self.rate_limiter.record_rate_limit_response(
                        float(retry_after) if retry_after else None
                    )
                raise RateLimitExceeded(
                    f"FRED API rate limit exceeded. Retry after {retry_after}s.",
                    agency="FRED",
                    retry_after=float(retry_after) if retry_after else 60.0,
                )
            
            response.raise_for_status()
            
            # Record success
            if self.rate_limiter:
                self.rate_limiter.record_success()
            
            return response.json()
            
        except Exception as e:
            if self.rate_limiter and not isinstance(e, RateLimitExceeded):
                self.rate_limiter.record_error()
            raise

    def _get_api_key(self) -> str:
        """Get KRL API key for license validation."""
        return self.api_key

    def _get_fred_api_key(self) -> str:
        """
        Get FRED API key from license server.

        Returns:
            FRED API key for making requests
        """
        # In production, this would fetch from license server
        # For now, return a placeholder
        return self.fred_api_key or "fred_pro_key"

    def connect(self) -> bool:
        """
        Test connection to FRED API.

        Returns:
            True if connection successful
        """
        try:
            data = self._make_request(
                f"{self.base_url}/series",
                params={
                    "series_id": "GDP",
                    "api_key": self._get_fred_api_key(),
                    "file_type": "json",
                },
            )
            self.logger.info("Successfully connected to FRED API")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to FRED API: {str(e)}")
            return False

    @requires_license
    def get_series(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        units: str = "lin",
        frequency: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get any FRED economic data series.

        Args:
            series_id: FRED series ID (any of 800,000+ series)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            units: Data transformation (lin, chg, ch1, pch, pc1, pca, cch, cca, log)
            frequency: Data frequency (d, w, bw, m, q, sa, a)

        Returns:
            DataFrame with date index and value column
        """
        self.logger.info(
            f"Fetching FRED series: {series_id}",
            extra={
                "series_id": series_id,
                "start_date": start_date,
                "end_date": end_date,
                "units": units,
                "frequency": frequency,
            },
        )

        # Build request parameters
        params = {
            "series_id": series_id,
            "api_key": self._get_fred_api_key(),
            "file_type": "json",
            "units": units,
        }

        if start_date:
            params["observation_start"] = start_date
        if end_date:
            params["observation_end"] = end_date
        if frequency:
            params["frequency"] = frequency

        # Make rate-limited request
        data = self._make_request(f"{self.base_url}/series/observations", params)
        observations = data.get("observations", [])

        # Convert to DataFrame
        df = pd.DataFrame(observations)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
            df = df[["date", "value"]].set_index("date")

        self.logger.info(
            f"Retrieved {len(df)} observations for {series_id}",
            extra={"series_id": series_id, "rows": len(df)},
        )

        return df

    def search_series(
        self, search_text: str, limit: int = 100, order_by: str = "popularity"
    ) -> List[Dict[str, Any]]:
        """
        Search for series by keyword.

        Args:
            search_text: Search query
            limit: Maximum results to return
            order_by: Sort order (search_rank, series_id, title, units,
                     frequency, seasonal_adjustment, realtime_start,
                     realtime_end, last_updated, observation_start,
                     observation_end, popularity)

        Returns:
            List of series matching search criteria
        """
        self.logger.info(f"Searching FRED series: {search_text}")

        data = self._make_request(
            f"{self.base_url}/series/search",
            params={
                "search_text": search_text,
                "api_key": self._get_fred_api_key(),
                "file_type": "json",
                "limit": limit,
                "order_by": order_by,
            },
        )
        return data.get("seriess", [])

    @requires_license
    def get_releases(self) -> List[Dict[str, Any]]:
        """
        Get all FRED data releases.

        Returns:
            List of release information
        """
        data = self._make_request(
            f"{self.base_url}/releases",
            params={"api_key": self._get_fred_api_key(), "file_type": "json"},
        )
        return data.get("releases", [])

    @requires_license
    def get_release_series(self, release_id: int, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Get all series in a release.

        Args:
            release_id: FRED release ID
            limit: Maximum series to return

        Returns:
            List of series in the release
        """
        data = self._make_request(
            f"{self.base_url}/release/series",
            params={
                "release_id": release_id,
                "api_key": self._get_fred_api_key(),
                "file_type": "json",
                "limit": limit,
            },
        )
        return data.get("seriess", [])

    @requires_license
    def get_categories(self, category_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get FRED categories.

        Args:
            category_id: Parent category ID (None for root categories)

        Returns:
            List of categories
        """
        endpoint = f"{self.base_url}/category"
        if category_id:
            endpoint = f"{self.base_url}/category/children"

        params = {"api_key": self._get_fred_api_key(), "file_type": "json"}
        if category_id:
            params["category_id"] = category_id

        data = self._make_request(endpoint, params)
        return data.get("categories", [])

    def fetch(self, series_id: str, **kwargs) -> pd.DataFrame:
        """
        Generic fetch method (alias for get_series).

        Args:
            series_id: FRED series ID
            **kwargs: Additional arguments passed to get_series

        Returns:
            DataFrame with series data
        """
        return self.get_series(series_id, **kwargs)
