# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2025 KR-Labs Foundation. All rights reserved.
# Licensed under Apache License 2.0 (see LICENSE file for details)

"""U.S. Census Bureau connector implementation."""

from typing import Any, Dict, List, Optional

import pandas as pd

from ...base_dispatcher_connector import BaseDispatcherConnector
from ...core import DataTier
from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license


class CensusConnector(LicensedConnectorMixin, BaseDispatcherConnector):
    """
        Connector for U.S. Census Bureau Data API.

        Provides access to demographic, economic, and geographic data including:
        - American Community Survey (ACS)
        - Decennial Census
        - Economic indicators
        - Population estimates

        API Documentation: https://www.census.gov/data/developers/data-sets.html

        **Dispatcher Pattern:**
        Uses the dispatcher pattern to route requests based on the `query_type` parameter:
        - ``data`` - Get demographic/economic data from Census datasets (default)
        - ``variables`` - List available variables for a dataset

        Args:
            api_key: Census API key (or set CENSUS_API_KEY environment variable)
            base_url: Census API base URL (default: official API endpoint)
            cache_dir: Cache directory (default: ~/.krl_cache)
            cache_ttl: Cache TTL in seconds (default: 3600)

        Example:
            >>> from krl_data_connectors import CensusConnector
    from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license
    from ...core import DataTier
            >>> census = CensusConnector(api_key="your_key")
            >>>
            >>> # Get demographic data
            >>> pop = census.fetch(
            ...     query_type="data",
            ...     dataset="acs/acs5",
            ...     year=2022,
            ...     variables=["B01001_001E"],
            ...     geography="state:*"
            ... )
            >>>
            >>> # List available variables
            >>> vars = census.fetch(query_type="variables", dataset="acs/acs5", year=2022)
    """

    DISPATCH_PARAM = "query_type"
    DISPATCH_MAP = {
        "data": "get_data",
        "variables": "list_variables",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.census.gov/data",
        cache_dir: Optional[str] = None,
        cache_ttl: int = 3600,
        **kwargs: Any,
    ):
        self.base_url = base_url
        self._connector_name = "Census_ACS_Detailed"  # Used by @requires_license decorator
        super().__init__(api_key=api_key, cache_dir=cache_dir, cache_ttl=cache_ttl, **kwargs)

    def _get_api_key(self) -> Optional[str]:
        """Get Census API key from configuration."""
        return self.config.get("CENSUS_API_KEY")

    def connect(self) -> None:
        """
        Connect to Census API (verify API key).

        Makes a simple API call to verify the API key is valid.
        """
        try:
            # Make a simple request to verify API key
            url = f"{self.base_url}/2020/dec/pl"
            params = {"get": "NAME", "for": "state:*", "key": self.api_key}

            self._make_request(url, params, use_cache=False)

            self.logger.info("Successfully connected to Census API")

        except Exception as e:
            self.logger.error(f"Failed to connect to Census API: {e}", exc_info=True)
            raise

    @requires_license
    def get_data(
        self,
        dataset: str,
        year: int,
        variables: List[str],
        geography: str = "us:*",
        predicates: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        Get data from Census API.

        Args:
            dataset: Dataset path (e.g., "acs/acs5", "dec/pl", "pep/population")
            year: Data year
            variables: List of variable codes (e.g., ["B01001_001E"] for total population)
            geography: Geographic level specification
                Examples:
                - "us:*" - United States
                - "state:*" - All states
                - "state:06" - California (FIPS code 06)
                - "county:*" - All counties
                - "county:*&in=state:06" - All counties in California
            predicates: Additional query predicates (optional)

        Returns:
            DataFrame with requested data

        Example:
            >>> census = CensusConnector(api_key="your_key")
            >>> # Get total population by state
            >>> pop = census.get_data(
            ...     dataset="acs/acs5",
            ...     year=2022,
            ...     variables=["B01001_001E", "NAME"],
            ...     geography="state:*"
            ... )
        """
        url = f"{self.base_url}/{year}/{dataset}"

        # Build parameters
        params = {
            "get": ",".join(variables),
            "for": geography,
            "key": self.api_key,
        }

        if predicates:
            params.update(predicates)

        self.logger.info(
            "Fetching Census data",
            extra={
                "dataset": dataset,
                "year": year,
                "variables": len(variables),
                "geography": geography,
            },
        )

        response = self._make_request(url, params)

        # Census API returns data as nested lists
        if not response or len(response) < 2:
            self.logger.warning("No data found")
            return pd.DataFrame()

        # First row is headers, rest is data
        headers = response[0]
        data = response[1:]

        # Convert to DataFrame
        df = pd.DataFrame(data, columns=headers)

        # Convert numeric columns
        for col in df.columns:
            if col not in ["NAME", "state", "county", "tract", "block group"]:
                numeric_series = pd.to_numeric(df[col], errors="coerce")
                # Convert numpy types to Python types for compatibility
                if pd.api.types.is_integer_dtype(numeric_series):
                    python_ints = [int(x) if pd.notna(x) else None for x in numeric_series]
                    df[col] = pd.Series(python_ints, dtype=object, index=df.index)
                elif pd.api.types.is_float_dtype(numeric_series):
                    python_floats = [float(x) if pd.notna(x) else None for x in numeric_series]
                    df[col] = pd.Series(python_floats, dtype=object, index=df.index)

        self.logger.info(
            "Census data fetched", extra={"dataset": dataset, "year": year, "rows": len(df)}
        )

        return df

    def list_variables(self, dataset: str, year: int, **kwargs: Any) -> pd.DataFrame:
        """
        List available variables for a dataset.

        Args:
            dataset: Dataset path (e.g., "acs/acs5")
            year: Data year

        Returns:
            DataFrame with variable metadata (name, label, concept, group)

        Example:
            >>> census = CensusConnector(api_key="your_key")
            >>> variables = census.list_variables("acs/acs5", 2022)
            >>> print(variables[variables["label"].str.contains("population")])
        """
        url = f"{self.base_url}/{year}/{dataset}/variables.json"

        self.logger.info("Listing Census variables", extra={"dataset": dataset, "year": year})

        response = self._make_request(url, {}, use_cache=True)

        # Parse variables from response
        variables = response.get("variables", {})

        # Convert to DataFrame
        var_list = []
        for var_name, var_info in variables.items():
            var_list.append(
                {
                    "name": var_name,
                    "label": var_info.get("label", ""),
                    "concept": var_info.get("concept", ""),
                    "predicateType": var_info.get("predicateType", ""),
                    "group": var_info.get("group", ""),
                }
            )

        df = pd.DataFrame(var_list)

        self.logger.info(
            "Variables listed", extra={"dataset": dataset, "year": year, "count": len(df)}
        )

        return df
