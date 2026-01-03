# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
EPA Air Quality Connector - AirNow API Integration

This connector provides access to real-time and historical air quality data from the
EPA AirNow program, which aggregates data from over 2,500 monitoring stations across
the United States, Canada, and Mexico.

Data Source: https://docs.airnowapi.org/
API Type: REST API (requires free API key)
Coverage: 2,500+ monitoring stations, 500+ cities with forecasts
Update Frequency: Real-time (hourly updates)

Key Features:
- Current air quality observations (AQI and pollutant concentrations)
- Air quality forecasts (daily predictions)
- Historical observations (past AQI data)
- Monitoring site queries (geographic searches)
- Contour maps (spatial visualization via KML)

AQI Scale (Air Quality Index):
- 0-50: Good (Green)
- 51-100: Moderate (Yellow)
- 101-150: Unhealthy for Sensitive Groups (Orange)
- 151-200: Unhealthy (Red)
- 201-300: Very Unhealthy (Purple)
- 301-500: Hazardous (Maroon)

Parameters Supported:
- PM2.5 (Fine particulate matter)
- PM10 (Coarse particulate matter)
- Ozone (O3)
- Carbon Monoxide (CO)
- Nitrogen Dioxide (NO2)
- Sulfur Dioxide (SO2)

Note: AirNow data is preliminary and unverified. For regulatory decisions,
use EPA's Air Quality System (AQS) API instead.

Author: KR-Labs Development Team
License: MIT
"""

import logging
import os
import re
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests

from ...base_dispatcher_connector import BaseDispatcherConnector
from ...core import DataTier
from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license

logger = logging.getLogger(__name__)


class SecurityValidationError(Exception):
    """Exception raised for obvious security violations (malicious input)."""

    pass


class EPAAirQualityConnector(LicensedConnectorMixin, BaseDispatcherConnector):
    """
    Connector for EPA AirNow Air Quality API.

    Provides access to real-time and historical air quality data including:
    - Current AQI observations
    - Air quality forecasts
    - Historical AQI data
    - Monitoring site information
    - Spatial contour maps

    **Dispatcher Pattern:**
    Uses the dispatcher pattern to route requests based on the `query_type` parameter:
    - ``current_zip`` - Get current air quality by ZIP code
    - ``current_latlon`` - Get current air quality by coordinates
    - ``forecast_zip`` - Get air quality forecast by ZIP code
    - ``forecast_latlon`` - Get air quality forecast by coordinates
    - ``historical_zip`` - Get historical air quality by ZIP code
    - ``historical_latlon`` - Get historical air quality by coordinates

    Attributes:
        base_url (str): Base URL for AirNow API
        api_key (str): API key for authentication

    Example:
        >>> connector = EPAAirQualityConnector(api_key="your_api_key")
        >>> # Get current AQI by ZIP
        >>> current = connector.fetch(query_type="current_zip", zip_code="94102")
        >>> # Get forecast by coordinates
        >>> forecast = connector.fetch(query_type="forecast_latlon", latitude=37.7749, longitude=-122.4194)
    """

    # Registry name for license validation
    _connector_name = "EPA_Air_Quality_Full"

    DISPATCH_PARAM = "query_type"
    DISPATCH_MAP = {
        "current_zip": "get_current_by_zip",
        "current_latlon": "get_current_by_latlon",
        "forecast_zip": "get_forecast_by_zip",
        "forecast_latlon": "get_forecast_by_latlon",
        "historical_zip": "get_historical_by_zip",
        "historical_latlon": "get_historical_by_latlon",
    }

    # API Configuration
    BASE_URL = "https://www.airnowapi.org/aq"

    # AQI Categories
    AQI_CATEGORIES = {
        "Good": (0, 50),
        "Moderate": (51, 100),
        "Unhealthy for Sensitive Groups": (101, 150),
        "Unhealthy": (151, 200),
        "Very Unhealthy": (201, 300),
        "Hazardous": (301, 500),
    }

    # Parameter codes
    PARAMETERS = {
        "PM25": "PM2.5",
        "PM10": "PM10",
        "OZONE": "OZONE",
        "O3": "OZONE",
        "CO": "CO",
        "NO2": "NO2",
        "SO2": "SO2",
    }

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize EPA Air Quality connector.

        Args:
            api_key: AirNow API key. If not provided, will look for AIRNOW_API_KEY
                    environment variable.
            **kwargs: Additional arguments passed to BaseConnector

        Raises:
            ValueError: If no API key provided or found in environment
        """
        super().__init__(**kwargs)

        self.api_key = api_key or os.getenv("AIRNOW_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Provide via api_key parameter or "
                "set AIRNOW_API_KEY environment variable. "
                "Register for free at https://docs.airnowapi.org/login"
            )

        self.base_url = self.BASE_URL
        self._session = None

        logger.info("EPA Air Quality connector initialized")

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from instance variable or ConfigManager.

        Checks in order:
        1. Instance variable (passed during __init__)
        2. ConfigManager (checks ~/.krl/apikeys and environment)
        3. None

        Returns:
            API key if available, None otherwise
        """
        # Check if set during initialization
        if hasattr(self, "_epa_api_key") and self._epa_api_key:
            return self._epa_api_key

        # Fall back to ConfigManager (environment + ~/.krl/apikeys)
        return self.config.get("EPA_API_KEY")

    def connect(self) -> None:
        """
        Establish connection and verify API key.

        Tests the API key by making a simple request.

        Raises:
            ConnectionError: If API key is invalid or service unavailable
        """
        try:
            # Test API key with a simple request (current AQI for a valid ZIP)
            test_url = f"{self.base_url}/observation/zipCode/current/"
            params = {
                "format": "application/json",
                "zipCode": "20001",  # Washington DC
                "distance": "25",
                "API_KEY": self.api_key,
            }

            response = requests.get(test_url, params=params, timeout=10)

            if response.status_code == 403:
                raise ConnectionError(
                    "Invalid API key. Register at https://docs.airnowapi.org/login"
                )
            elif response.status_code != 200:
                raise ConnectionError(f"API connection failed: {response.status_code}")

            # Create session for subsequent requests
            self._session = requests.Session()
            self._session.headers.update({"User-Agent": "KR-Labs-Data-Connectors/1.0"})

            logger.info("Successfully connected to AirNow API")

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to AirNow API: {str(e)}")

    def disconnect(self) -> None:
        """Close the API session."""
        if self._session:
            self._session.close()
            self._session = None
        logger.info("Disconnected from AirNow API")

    def _validate_zip_code(self, zip_code: str) -> str:
        """
        Validate and sanitize ZIP code input.

        Args:
            zip_code: ZIP code to validate

        Returns:
            Sanitized ZIP code

        Raises:
            ValueError: If ZIP code format is invalid but reasonable
            SecurityValidationError: If ZIP code is obviously malicious
            TypeError: If ZIP code contains null bytes or wrong type
        """
        if not isinstance(zip_code, str):
            raise TypeError("ZIP code must be a string")

        # Check for null bytes (security)
        if "\x00" in zip_code:
            raise TypeError("ZIP code cannot contain null bytes")

        # Check for obviously malicious inputs (security)
        # Extreme length suggests attack (DoS, injection)
        if len(zip_code) > 20:
            raise SecurityValidationError("ZIP code is suspiciously long")

        # Check for non-digit characters first
        if not zip_code.isdigit():
            # If it contains special characters and is long, it's likely malicious
            if len(zip_code) > 10:
                raise SecurityValidationError(
                    "ZIP code contains invalid characters and is too long"
                )
            else:
                raise ValueError("ZIP code must contain only digits")

        # Must be exactly 5 digits (normal validation)
        if len(zip_code) != 5:
            raise ValueError("ZIP code must be 5 digits")

        return zip_code

    def _validate_coordinates(self, latitude: float, longitude: float) -> tuple[float, float]:
        """
        Validate latitude and longitude.

        Args:
            latitude: Latitude to validate
            longitude: Longitude to validate

        Returns:
            Tuple of (latitude, longitude)

        Raises:
            TypeError: If coordinates are not numeric
            ValueError: If coordinates are out of range
        """
        # Type validation
        try:
            lat = float(latitude)
            lon = float(longitude)
        except (TypeError, ValueError) as e:
            raise TypeError(f"Coordinates must be numeric: {e}")

        # Range validation
        if not -90 <= lat <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        if not -180 <= lon <= 180:
            raise ValueError("Longitude must be between -180 and 180")

        return lat, lon

    def _validate_date(self, date: Union[str, datetime, None]) -> Optional[str]:
        """
        Validate and sanitize date input.

        Args:
            date: Date to validate

        Returns:
            Sanitized date string or None

        Raises:
            ValueError: If date format is invalid
            TypeError: If date is neither string nor datetime
        """
        if date is None:
            return None

        if isinstance(date, datetime):
            return date.strftime("%Y-%m-%d")

        if not isinstance(date, str):
            raise TypeError("Date must be a string or datetime object")

        # Check for null bytes
        if "\x00" in date:
            raise TypeError("Date cannot contain null bytes")

        # Validate date format using regex
        # Accept YYYY-MM-DD or YYYY-MM-DDTHH formats
        date_pattern = r"^\d{4}-\d{2}-\d{2}(T\d{2})?$"
        if not re.match(date_pattern, date):
            raise ValueError("Date must be in YYYY-MM-DD or YYYY-MM-DDTHH format")

        # Try to parse the date to ensure it's valid
        try:
            if "T" in date:
                datetime.strptime(date.split("T")[0], "%Y-%m-%d")
            else:
                datetime.strptime(date, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid date: {e}")

        return date

    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Union[List[Dict], Dict]:
        """
        Make API request with error handling.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response as dict or list

        Raises:
            requests.exceptions.RequestException: For API errors
        """
        # Add API key and format to params
        params["API_KEY"] = self.api_key
        params["format"] = "application/json"

        url = f"{self.base_url}/{endpoint}"

        session = self._session or requests
        response = session.get(url, params=params, timeout=30)

        if response.status_code == 403:
            raise requests.exceptions.HTTPError("Invalid API key")
        elif response.status_code == 404:
            logger.warning(f"No data found for request: {endpoint}")
            return []

        response.raise_for_status()

        return response.json()

    @requires_license
    def get_current_by_zip(self, zip_code: str, distance: int = 25, **kwargs: Any) -> pd.DataFrame:
        """
        Get current air quality observations by ZIP code.

        Args:
            zip_code: 5-digit US ZIP code
            distance: Search radius in miles (default: 25)

        Returns:
            DataFrame with columns:
                - DateObserved: Observation date
                - HourObserved: Observation hour
                - LocalTimeZone: Time zone
                - ReportingArea: Geographic area name
                - StateCode: State abbreviation
                - Latitude: Monitoring site latitude
                - Longitude: Monitoring site longitude
                - ParameterName: Pollutant (PM2.5, Ozone, etc.)
                - AQI: Air Quality Index value
                - Category.Number: AQI category number (1-6)
                - Category.Name: AQI category name

        Example:
            >>> connector = EPAAirQualityConnector(api_key="key")
            >>> current = connector.get_current_by_zip("94102")
            >>> print(current[['ReportingArea', 'ParameterName', 'AQI', 'Category.Name']])
        """
        # Validate and sanitize ZIP code
        # Catch security violations and type errors, let ValueError propagate
        try:
            zip_code = self._validate_zip_code(zip_code)
        except (SecurityValidationError, TypeError) as e:
            # Security issues - return empty DataFrame
            logger.warning(f"Security issue with ZIP code '{zip_code}': {e}")
            return pd.DataFrame()
        # ValueError (invalid but reasonable format) will propagate to caller

        params = {"zipCode": zip_code, "distance": str(distance)}

        data = self._make_request("observation/zipCode/current/", params)

        if not data:
            logger.warning(f"No current observations found for ZIP {zip_code}")
            return pd.DataFrame()

        return pd.DataFrame(data)

    @requires_license
    def get_current_by_latlon(
        self, latitude: float, longitude: float, distance: int = 25, **kwargs: Any
    ) -> pd.DataFrame:
        """
        Get current air quality observations by latitude/longitude.

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            distance: Search radius in miles (default: 25)

        Returns:
            DataFrame with current AQI observations (same format as get_current_by_zip)

        Example:
            >>> connector = EPAAirQualityConnector(api_key="key")
            >>> current = connector.get_current_by_latlon(37.7749, -122.4194)
        """
        # Validate coordinates - catches TypeError for non-numeric, lets ValueError propagate
        try:
            latitude, longitude = self._validate_coordinates(latitude, longitude)
        except TypeError as e:
            # Type errors (e.g., string instead of number) - return empty DataFrame
            logger.warning(f"Invalid coordinate types ({latitude}, {longitude}): {e}")
            return pd.DataFrame()
        # ValueError (out of range) will propagate to caller

        params = {"latitude": str(latitude), "longitude": str(longitude), "distance": str(distance)}

        data = self._make_request("observation/latLong/current/", params)

        if not data:
            logger.warning(f"No current observations found for {latitude}, {longitude}")
            return pd.DataFrame()

        return pd.DataFrame(data)

    @requires_license
    def get_forecast_by_zip(
        self, zip_code: str, date: Optional[str] = None, distance: int = 25, **kwargs: Any
    ) -> pd.DataFrame:
        """Get air quality forecast by ZIP code.

        Args:
            zip_code: 5-digit US ZIP code
            date: Forecast date (YYYY-MM-DD format, optional)
            distance: Search radius in miles (default 25)

        Returns:
            DataFrame with forecast air quality data
        """
        try:
            zip_code = self._validate_zip_code(zip_code)
        except (SecurityValidationError, TypeError) as e:
            # Security issues - return empty DataFrame
            logger.warning(f"Security issue with ZIP code '{zip_code}': {e}")
            return pd.DataFrame()
        # ValueError (invalid format/length) will propagate to caller

        # Date validation - let exceptions propagate
        date = self._validate_date(date)

        endpoint = f"{self.base_url}/forecast/zipCode/"
        params = {"zipCode": zip_code, "distance": distance, "format": "application/json"}
        if date:
            params["date"] = date
        data = self._make_request(endpoint, params)
        return pd.DataFrame(data) if data else pd.DataFrame()

    @requires_license
    def get_forecast_by_latlon(
        self,
        latitude: float,
        longitude: float,
        date: Optional[Union[str, datetime]] = None,
        distance: int = 25,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        Get air quality forecast by latitude/longitude.

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            date: Forecast date (YYYY-MM-DD). If None, returns today's forecast.
            distance: Search radius in miles (default: 25)

        Returns:
            DataFrame with forecast data (same format as get_forecast_by_zip)

        Example:
            >>> connector = EPAAirQualityConnector(api_key="key")
            >>> forecast = connector.get_forecast_by_latlon(37.7749, -122.4194)
        """
        # Validate coordinates - catch TypeError, let ValueError propagate
        try:
            latitude, longitude = self._validate_coordinates(latitude, longitude)
        except TypeError as e:
            logger.warning(f"Invalid coordinate types ({latitude}, {longitude}): {e}")
            return pd.DataFrame()
        # ValueError (out of range) will propagate to caller

        # Validate date
        try:
            date_str = self._validate_date(date)
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid date ({date}): {e}")
            return pd.DataFrame()

        params = {"latitude": str(latitude), "longitude": str(longitude), "distance": str(distance)}

        if date_str:
            params["date"] = date_str

        data = self._make_request("forecast/latLong/", params)

        if not data:
            logger.warning(f"No forecast found for {latitude}, {longitude}")
            return pd.DataFrame()

        return pd.DataFrame(data)

    @requires_license
    def get_historical_by_zip(
        self,
        zip_code: str,
        start_date: Union[str, datetime],
        end_date: Optional[Union[str, datetime]] = None,
        distance: int = 25,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        Get historical air quality observations by ZIP code.

        Args:
            zip_code: 5-digit US ZIP code
            start_date: Start date (YYYY-MM-DD or YYYY-MM-DDTHH format)
            end_date: End date (YYYY-MM-DD or YYYY-MM-DDTHH). If None, uses start_date.
            distance: Search radius in miles (default: 25)

        Returns:
            DataFrame with historical observations

        Note:
            Historical data typically available for past 1-2 years.

        Example:
            >>> connector = EPAAirQualityConnector(api_key="key")
            >>> historical = connector.get_historical_by_zip(
            ...     "94102",
            ...     start_date="2025-10-01",
            ...     end_date="2025-10-15"
            ... )
        """
        if not zip_code or len(zip_code) != 5:
            raise ValueError("ZIP code must be 5 digits")

        if isinstance(start_date, datetime):
            start_str = start_date.strftime("%Y-%m-%dT00")
        else:
            start_str = start_date

        if end_date:
            if isinstance(end_date, datetime):
                end_str = end_date.strftime("%Y-%m-%dT23")
            else:
                end_str = end_date
        else:
            end_str = start_str

        params = {"zipCode": zip_code, "date": start_str, "distance": str(distance)}

        # For date ranges, make multiple requests
        data = self._make_request("observation/zipCode/historical/", params)

        if not data:
            logger.warning(f"No historical data found for ZIP {zip_code}")
            return pd.DataFrame()

        return pd.DataFrame(data)

    @requires_license
    def get_historical_by_latlon(
        self,
        latitude: float,
        longitude: float,
        start_date: Union[str, datetime],
        end_date: Optional[Union[str, datetime]] = None,
        distance: int = 25,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        Get historical air quality observations by latitude/longitude.

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            start_date: Start date (YYYY-MM-DD or YYYY-MM-DDTHH format)
            end_date: End date (YYYY-MM-DD or YYYY-MM-DDTHH). If None, uses start_date.
            distance: Search radius in miles (default: 25)

        Returns:
            DataFrame with historical observations

        Example:
            >>> connector = EPAAirQualityConnector(api_key="key")
            >>> historical = connector.get_historical_by_latlon(
            ...     37.7749, -122.4194,
            ...     start_date="2025-10-01"
            ... )
        """
        if not -90 <= latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        if not -180 <= longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180")

        if isinstance(start_date, datetime):
            start_str = start_date.strftime("%Y-%m-%dT00")
        else:
            start_str = start_date

        params = {
            "latitude": str(latitude),
            "longitude": str(longitude),
            "date": start_str,
            "distance": str(distance),
        }

        data = self._make_request("observation/latLong/historical/", params)

        if not data:
            logger.warning(f"No historical data found for {latitude}, {longitude}")
            return pd.DataFrame()

        return pd.DataFrame(data)

    @requires_license
    def get_aqi_category(self, aqi_value: int) -> str:
        """
        Get AQI category name from AQI value.

        Args:
            aqi_value: Air Quality Index value (0-500)

        Returns:
            Category name (e.g., 'Good', 'Moderate', 'Unhealthy')

        Example:
            >>> connector = EPAAirQualityConnector(api_key="key")
            >>> category = connector.get_aqi_category(75)
            >>> print(category)  # 'Moderate'
        """
        for category, (min_val, max_val) in self.AQI_CATEGORIES.items():
            if min_val <= aqi_value <= max_val:
                return category
        return "Unknown"

    def filter_by_parameter(self, data: pd.DataFrame, parameter: str) -> pd.DataFrame:
        """
        Filter observations by pollutant parameter.

        Args:
            data: DataFrame with air quality data
            parameter: Parameter name (PM2.5, PM10, OZONE, CO, NO2, SO2)

        Returns:
            Filtered DataFrame

        Example:
            >>> connector = EPAAirQualityConnector(api_key="key")
            >>> current = connector.get_current_by_zip("94102")
            >>> pm25_only = connector.filter_by_parameter(current, "PM2.5")
        """
        if data.empty:
            return data

        # Normalize parameter name
        parameter_upper = parameter.upper()
        if parameter_upper in self.PARAMETERS:
            parameter_normalized = self.PARAMETERS[parameter_upper]
        else:
            parameter_normalized = parameter

        if "ParameterName" not in data.columns:
            raise ValueError("Data does not contain 'ParameterName' column")

        return data[data["ParameterName"].str.upper() == parameter_normalized.upper()].copy()

    def filter_by_aqi_threshold(
        self, data: pd.DataFrame, threshold: int, above: bool = True
    ) -> pd.DataFrame:
        """
        Filter observations by AQI threshold.

        Args:
            data: DataFrame with air quality data
            threshold: AQI threshold value
            above: If True, return AQI >= threshold. If False, return AQI < threshold.

        Returns:
            Filtered DataFrame

        Example:
            >>> connector = EPAAirQualityConnector(api_key="key")
            >>> current = connector.get_current_by_zip("94102")
            >>> unhealthy = connector.filter_by_aqi_threshold(current, 101)
        """
        if data.empty:
            return data

        if "AQI" not in data.columns:
            raise ValueError("Data does not contain 'AQI' column")

        if above:
            return data[data["AQI"] >= threshold].copy()
        else:
            return data[data["AQI"] < threshold].copy()

    def summarize_by_parameter(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Summarize air quality statistics by parameter.

        Args:
            data: DataFrame with air quality observations

        Returns:
            DataFrame with statistics for each parameter:
                - ParameterName: Pollutant name
                - Count: Number of observations
                - Mean_AQI: Average AQI
                - Max_AQI: Maximum AQI
                - Min_AQI: Minimum AQI

        Example:
            >>> connector = EPAAirQualityConnector(api_key="key")
            >>> current = connector.get_current_by_zip("94102")
            >>> summary = connector.summarize_by_parameter(current)
        """
        if data.empty:
            return pd.DataFrame()

        if "ParameterName" not in data.columns or "AQI" not in data.columns:
            raise ValueError("Data must contain 'ParameterName' and 'AQI' columns")

        return (
            data.groupby("ParameterName")["AQI"]
            .agg(Count="count", Mean_AQI="mean", Max_AQI="max", Min_AQI="min")
            .reset_index()
        )

    # Aliases for backward compatibility with tests
    @requires_license
    def get_current_observations_by_zip(self, zip_code: str, distance: int = 25) -> pd.DataFrame:
        """Alias for get_current_by_zip for backward compatibility."""
        return self.get_current_by_zip(zip_code, distance)

    @requires_license
    def get_current_observations_by_latlon(
        self, latitude: float, longitude: float, distance: int = 25
    ) -> pd.DataFrame:
        """Alias for get_current_by_latlon for backward compatibility."""
        return self.get_current_by_latlon(latitude, longitude, distance)
