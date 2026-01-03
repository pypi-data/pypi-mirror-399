# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
CDC WONDER API Connector for mortality, natality, and population data.

CDC WONDER (Wide-ranging Online Data for Epidemiologic Research) provides access to:
- Mortality data (Underlying Cause of Death, Multiple Cause of Death)
- Natality data (Birth statistics)
- Population estimates
- Cancer statistics
- Vaccine adverse events

⚠️ **CRITICAL LIMITATION**: CDC WONDER does NOT provide a functional programmatic API.
   - The API endpoint (https://wonder.cdc.gov/controller/datarequest/) returns HTTP 500 errors
   - API documentation pages return 404 errors
   - CDC redirects API requests to web form interface
   - This connector demonstrates the INTENDED interface design for when/if API becomes available
   - For actual data access, use CDC WONDER web interface: https://wonder.cdc.gov/

**Status**: BETA - Implementation complete but CDC API is non-functional
**Recommendation**: Use CDC WONDER web interface for reliable data access

Copyright (c) 2024-2025 KR-Labs Foundation
Licensed under the Apache License, Version 2.0
"""

import logging
import xml.etree.ElementTree as ET  # For building XML

try:
    from defusedxml import (
        ElementTree as DefusedET,  # Secure XML parsing (prevents XXE/XML bomb attacks)
    )
except ImportError:
    DefusedET = ET  # Fall back to regular ET if defusedxml not available
    import warnings
    warnings.warn("defusedxml not available - using xml.etree (vulnerable to XXE attacks)")
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

from ...base_dispatcher_connector import BaseDispatcherConnector
from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license

logger = logging.getLogger(__name__)


class CDCWonderConnector(LicensedConnectorMixin, BaseDispatcherConnector):
    """
    Connector for CDC WONDER API.

    ⚠️ **CRITICAL**: CDC WONDER does NOT have a functional programmatic API.
    This connector implements the intended interface but will fail with HTTP 500 errors
    because CDC's servers do not support automated API access.

    **Current Status**: BETA - Implementation complete, but CDC API is non-functional
    **Recommendation**: Use CDC WONDER web interface (https://wonder.cdc.gov/) for actual data access

    CDC WONDER provides access to public health data including mortality,
    natality, cancer, and population statistics. No API key required (when/if API works).

    **Data Domains:**
    - D04: Health (primary)
    - D25: Food & Nutrition (related)
    - D28: Mental Health (related)

    **Key Features (when API works):**
    - No authentication required
    - XML-based API requests
    - Supports mortality, natality, population data
    - County, state, and national geographic levels

    **Dispatcher Pattern:**
    Uses the dispatcher pattern to route requests based on the `dataset` parameter:
    - ``mortality`` - Get mortality/cause of death data (default)
    - ``natality`` - Get birth/natality statistics
    - ``population`` - Get population estimates

    Example:
        >>> from krl_data_connectors.health import CDCWonderConnector
from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license
from ...core import DataTier
        >>> cdc = CDCWonderConnector()
        >>> # Using dispatcher pattern
        >>> mortality = cdc.fetch(dataset='mortality', years=[2020], states=['CA'])
        >>> births = cdc.fetch(dataset='natality', years=[2021], states=['NY'])
        >>> population = cdc.fetch(dataset='population', years=[2020])
        >>> 
        >>> # Direct method calls also work
        >>> mortality = cdc.get_mortality_data(years=[2020], states=['CA'])
    """

    # Registry name for license validation
    _connector_name = "CDC_Full_API"

    DISPATCH_PARAM = "dataset"
    DISPATCH_MAP = {
        "mortality": "get_mortality_data",
        "natality": "get_natality_data",
        "population": "get_population_estimates",
    }

    BASE_URL = "https://wonder.cdc.gov/controller/datarequest"

    # Database codes for different datasets
    DATABASES = {
        "mortality_underlying": "D76",  # Underlying Cause of Death, 1999-2020
        "mortality_multiple": "D77",  # Multiple Cause of Death, 1999-2020
        "natality": "D149",  # Natality, 2016-2022
        "population": "D157",  # Bridged-Race Population Estimates
    }

    def __init__(self, cache_dir: Optional[str] = None, cache_ttl: int = 86400):
        """
        Initialize CDC WONDER connector.

        Args:
            cache_dir: Directory for caching responses (default: ~/.krl/cache)
            cache_ttl: Cache time-to-live in seconds (default: 24 hours)
        """
        super().__init__(api_key=None, cache_dir=cache_dir, cache_ttl=cache_ttl)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "KRL-Data-Connectors/1.0",
            }
        )

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from configuration.
        CDC WONDER doesn't require an API key, so this returns None.

        Returns:
            None (no API key needed)
        """
        return None

    def connect(self) -> None:
        """
        Test connection to CDC WONDER API.

        Validates that the API is accessible by making a simple test request.

        Raises:
            Exception: If connection fails
        """
        try:
            # Make a simple request to verify API is accessible
            df = self.get_population_estimates(years=[2020], states=["06"])
            if df.empty:
                raise Exception("Test request returned no data")
            self.logger.info("Successfully connected to CDC WONDER API")
        except Exception as e:
            self.logger.error(f"Failed to connect to CDC WONDER API: {e}", exc_info=True)
            raise

    def _make_cdc_request(
        self, database: str, parameters: Dict[str, Any], stage: str = "request"
    ) -> str:
        """
        Make a request to CDC WONDER API.

        Args:
            database: Database code (e.g., 'D76' for mortality)
            parameters: Query parameters as dictionary
            stage: Request stage ('request' or 'export')

        Returns:
            XML response as string
        """
        # Build XML request
        xml_request = self._build_xml_request(database, parameters)

        # Prepare form data
        data = {"request_xml": xml_request, "accept_datause_restrictions": "true", "stage": stage}

        cache_key = f"cdc_{database}_{hash(frozenset(parameters.items()))}"

        def fetch_data():
            logger.info(f"Fetching data from CDC WONDER database {database}")
            response = self.session.post(f"{self.BASE_URL}/{database}", data=data, timeout=30)
            response.raise_for_status()
            return response.text

        # Use cache if available
        cached_response = self.cache.get(cache_key)
        if cached_response is not None:
            return cached_response

        # Make request and cache
        result = fetch_data()
        self.cache.set(cache_key, result)
        return result

    def _build_xml_request(self, database: str, parameters: Dict[str, Any]) -> str:
        """
        Build XML request for CDC WONDER API.

        Args:
            database: Database code
            parameters: Query parameters

        Returns:
            XML string
        """
        root = ET.Element("request-parameters")

        # Add database version
        ET.SubElement(root, "dataset").text = database

        # Add parameters
        for key, value in parameters.items():
            if isinstance(value, list):
                for item in value:
                    param = ET.SubElement(root, "parameter")
                    ET.SubElement(param, "name").text = key
                    ET.SubElement(param, "value").text = str(item)
            else:
                param = ET.SubElement(root, "parameter")
                ET.SubElement(param, "name").text = key
                ET.SubElement(param, "value").text = str(value)

        return ET.tostring(root, encoding="unicode")

    def _parse_response(self, xml_response: str) -> pd.DataFrame:
        """
        Parse XML response into DataFrame.

        Args:
            xml_response: XML response string

        Returns:
            Pandas DataFrame with parsed data
        """
        root = DefusedET.fromstring(xml_response)  # Use defusedxml for secure parsing

        # Check for errors
        error = root.find(".//error")
        if error is not None:
            error_msg = error.text or "Unknown error"
            raise ValueError(f"CDC WONDER API error: {error_msg}")

        # Extract data rows
        rows = []
        for data_table in root.findall(".//data-table/r"):
            row = {}
            for cell in data_table.findall("c"):
                label = cell.get("l", "")
                value = cell.get("v", cell.text or "")
                if label:
                    row[label] = value
            if row:
                rows.append(row)

        if not rows:
            logger.warning("No data returned from CDC WONDER API")
            return pd.DataFrame()

        df = pd.DataFrame(rows)

        # Convert numeric columns
        numeric_cols = ["Deaths", "Population", "Crude Rate", "Age Adjusted Rate", "Births"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    @requires_license
    def get_mortality_data(
        self,
        years: Optional[List[int]] = None,
        geo_level: str = "state",
        states: Optional[List[str]] = None,
        counties: Optional[List[str]] = None,
        cause_of_death: Optional[List[str]] = None,
        age_groups: Optional[List[str]] = None,
        database: str = "mortality_underlying",
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        Get mortality data from CDC WONDER.

        Args:
            years: List of years (e.g., [2019, 2020, 2021])
            geo_level: Geographic level ('national', 'state', 'county')
            states: List of state FIPS codes (e.g., ['06', '36'])
            counties: List of county FIPS codes (5-digit)
            cause_of_death: List of ICD-10 codes or cause categories
            age_groups: List of age groups (e.g., ['1-4 years', '5-14 years'])
            database: Database type ('mortality_underlying' or 'mortality_multiple')

        Returns:
            DataFrame with mortality statistics

        Example:
            >>> cdc = CDCWonderConnector()
            >>> df = cdc.get_mortality_data(
            ...     years=[2020, 2021],
            ...     geo_level='state',
            ...     states=['06', '36']
            ... )
        """
        # Validate years parameter
        if years is not None:
            validated_years = []
            for year in years:
                try:
                    validated_years.append(int(year))
                except (TypeError, ValueError, AttributeError):
                    raise TypeError("All years must be numeric")
            years = validated_years

        # Validate geo_level parameter
        valid_geo_levels = ["national", "state", "county"]
        if geo_level not in valid_geo_levels:
            raise ValueError(f"geo_level must be one of {valid_geo_levels}, got '{geo_level}'")

        if years is None:
            years = [2020]

        parameters = {
            "B_1": "D76.V2",  # Year parameter
            "B_2": "D76.V9",  # State parameter
        }

        # Add year values
        for year in years:
            parameters["F_D76.V2"] = year

        # Add geographic parameters
        if geo_level == "state" and states:
            for state in states:
                parameters["F_D76.V9"] = state
        elif geo_level == "county" and counties:
            for county in counties:
                parameters["F_D76.V27"] = county

        # Add cause of death if specified
        if cause_of_death:
            for cause in cause_of_death:
                parameters["F_D76.V4"] = cause

        # Add age groups if specified
        if age_groups:
            for age in age_groups:
                parameters["F_D76.V5"] = age

        # Group by settings
        parameters["O_V2_fmode"] = "freg"  # Show zero values
        parameters["O_show_totals"] = "true"
        parameters["O_precision"] = "1"

        db_code = self.DATABASES.get(database, self.DATABASES["mortality_underlying"])
        xml_response = self._make_cdc_request(db_code, parameters)

        df = self._parse_response(xml_response)

        if not df.empty:
            df["data_source"] = "CDC WONDER"
            df["database"] = database
            df["retrieved_at"] = datetime.now().isoformat()

        return df

    @requires_license
    def get_natality_data(
        self,
        years: Optional[List[int]] = None,
        geo_level: str = "state",
        states: Optional[List[str]] = None,
        counties: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        Get birth statistics from CDC WONDER.

        Args:
            years: List of years (e.g., [2020, 2021])
            geo_level: Geographic level ('national', 'state', 'county')
            states: List of state FIPS codes
            counties: List of county FIPS codes

        Returns:
            DataFrame with natality statistics

        Example:
            >>> cdc = CDCWonderConnector()
            >>> df = cdc.get_natality_data(
            ...     years=[2020, 2021],
            ...     geo_level='state'
            ... )
        """
        if years is None:
            years = [2020]

        parameters = {
            "B_1": "D149.V2",  # Year parameter
            "B_2": "D149.V9",  # State parameter
        }

        # Add year values
        for year in years:
            parameters["F_D149.V2"] = year

        # Add geographic parameters
        if geo_level == "state" and states:
            for state in states:
                parameters["F_D149.V9"] = state
        elif geo_level == "county" and counties:
            for county in counties:
                parameters["F_D149.V27"] = county

        parameters["O_show_totals"] = "true"

        db_code = self.DATABASES["natality"]
        xml_response = self._make_cdc_request(db_code, parameters)

        df = self._parse_response(xml_response)

        if not df.empty:
            df["data_source"] = "CDC WONDER"
            df["database"] = "natality"
            df["retrieved_at"] = datetime.now().isoformat()

        return df

    @requires_license
    def get_population_estimates(
        self,
        years: Optional[List[int]] = None,
        geo_level: str = "state",
        states: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        Get population estimates from CDC WONDER.

        Args:
            years: List of years
            geo_level: Geographic level ('national', 'state', 'county')
            states: List of state FIPS codes

        Returns:
            DataFrame with population estimates

        Example:
            >>> cdc = CDCWonderConnector()
            >>> df = cdc.get_population_estimates(
            ...     years=[2020, 2021],
            ...     states=['06', '36']
            ... )
        """
        if years is None:
            years = [2020]

        parameters = {
            "B_1": "D157.V2",  # Year parameter
            "B_2": "D157.V9",  # State parameter
        }

        for year in years:
            parameters["F_D157.V2"] = year

        if states:
            for state in states:
                parameters["F_D157.V9"] = state

        parameters["O_show_totals"] = "true"

        db_code = self.DATABASES["population"]
        xml_response = self._make_cdc_request(db_code, parameters)

        df = self._parse_response(xml_response)

        if not df.empty:
            df["data_source"] = "CDC WONDER"
            df["database"] = "population"
            df["retrieved_at"] = datetime.now().isoformat()

        return df

    def validate_connection(self) -> bool:
        """
        Validate connection to CDC WONDER API.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try to fetch a small dataset
            df = self.get_population_estimates(years=[2020], states=["06"])
            return not df.empty
        except Exception as e:
            logger.error(f"CDC WONDER connection validation failed: {str(e)}")
            return False

    @requires_license
    def get_available_databases(self) -> Dict[str, str]:
        """
        Get list of available databases.

        Returns:
            Dictionary mapping database names to codes
        """
        return self.DATABASES.copy()
