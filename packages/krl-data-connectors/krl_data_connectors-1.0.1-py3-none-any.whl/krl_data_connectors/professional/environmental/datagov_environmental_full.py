# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Environmental Domain Connector - Professional Tier

Full access to environmental datasets from Data.gov with unlimited search,
bulk export, and resource streaming. Pre-configured for EPA, NOAA, DOI,
and other environmental agencies.

Professional tier includes:
- Unlimited search results (vs 50 for Community)
- Bulk export up to 10,000 datasets
- Resource file streaming with local caching
- Parallel downloads for efficiency
- Full API access with higher rate limits

Domain Organizations:
- EPA (epa-gov): Air quality, water quality, toxic releases, superfund
- NOAA (noaa-gov): Climate data, weather, ocean observations
- DOI (doi-gov): Land, water, wildlife resources
- USGS: Geological and hydrological data

Usage:
    from krl_data_connectors.professional.environmental import DataGovEnvironmentalFullConnector
    
    env = DataGovEnvironmentalFullConnector()
    
    # Search environmental datasets (unlimited results)
    results = env.search_datasets("air quality monitoring", rows=500)
    
    # Bulk export EPA water datasets
    water_data = env.bulk_export(query="water quality", organization="epa-gov", max_datasets=1000)
    
    # Download and cache resource files
    path = env.download_resource("dataset-id", "resource-id")
    
    # Load directly as DataFrame
    df = env.fetch_as_dataframe("water-quality-data")
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovEnvironmentalFullConnector(DataGovFullConnector):
    """
    Data.gov Environmental Domain Connector - Professional Tier

    Full access to EPA, NOAA, and environmental agency datasets with
    unlimited search, bulk export, and resource streaming.

    Inherits from DataGovFullConnector with:
    - DOMAIN_ORGANIZATIONS: ["epa-gov", "noaa-gov", "doi-gov"]
    - Domain-specific popular datasets
    - Convenience methods for EPA, NOAA, and climate data
    - All Professional tier features (bulk export, streaming, caching)
    """

    _connector_name = "DataGov_Environmental_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_environmental"

    # Domain configuration - auto-filter searches to these organizations
    DOMAIN_ORGANIZATIONS: List[str] = [
        "epa-gov",      # Environmental Protection Agency
        "noaa-gov",     # National Oceanic and Atmospheric Administration
        "doi-gov",      # Department of the Interior
    ]
    
    DOMAIN_TAGS: List[str] = [
        "environment",
        "climate",
        "air-quality",
        "water-quality",
        "weather",
        "pollution",
        "emissions",
    ]
    
    DOMAIN_NAME: str = "Environmental"

    @requires_license
    def search_epa_datasets(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 100,
    ) -> pd.DataFrame:
        """
        Search EPA datasets specifically.

        Convenience method that filters to EPA organization regardless
        of domain settings.

        Args:
            query: Search query string
            formats: Filter by resource format (e.g., ['CSV', 'JSON'])
            rows: Number of results (unlimited for Professional tier)

        Returns:
            DataFrame with EPA dataset metadata

        Example:
            >>> env = DataGovEnvironmentalFullConnector()
            >>> superfund = env.search_epa_datasets("superfund contamination", rows=200)
        """
        return self.search_datasets(
            query=query,
            organization="epa-gov",
            formats=formats,
            rows=rows,
        )

    @requires_license
    def search_noaa_datasets(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 100,
    ) -> pd.DataFrame:
        """
        Search NOAA datasets specifically.

        Convenience method for climate, weather, and ocean data.

        Args:
            query: Search query string
            formats: Filter by resource format (e.g., ['CSV', 'JSON'])
            rows: Number of results (unlimited for Professional tier)

        Returns:
            DataFrame with NOAA dataset metadata

        Example:
            >>> env = DataGovEnvironmentalFullConnector()
            >>> climate = env.search_noaa_datasets("historical temperature", rows=500)
        """
        return self.search_datasets(
            query=query,
            organization="noaa-gov",
            formats=formats,
            rows=rows,
        )

    @requires_license
    def search_air_quality_data(
        self,
        query: str = "*:*",
        state: Optional[str] = None,
        rows: int = 100,
    ) -> pd.DataFrame:
        """
        Search for air quality monitoring datasets.

        Args:
            query: Search query (default: all air quality datasets)
            state: Optional state filter (e.g., "California")
            rows: Number of results

        Returns:
            DataFrame with air quality dataset metadata
        """
        search_query = f"air quality {query}" if query != "*:*" else "air quality monitoring"
        if state:
            search_query = f"{search_query} {state}"
        
        return self.search_datasets(
            query=search_query,
            tags=["air-quality"],
            rows=rows,
        )

    @requires_license
    def search_water_quality_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """
        Search for water quality monitoring datasets.

        Args:
            query: Search query (default: all water quality datasets)
            rows: Number of results

        Returns:
            DataFrame with water quality dataset metadata
        """
        search_query = f"water quality {query}" if query != "*:*" else "water quality monitoring"
        
        return self.search_datasets(
            query=search_query,
            tags=["water-quality"],
            rows=rows,
        )

    @requires_license
    def search_climate_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """
        Search for climate and weather datasets.

        Searches across NOAA climate datasets including historical
        observations, climate normals, and projections.

        Args:
            query: Search query (default: all climate datasets)
            rows: Number of results

        Returns:
            DataFrame with climate dataset metadata

        Example:
            >>> env = DataGovEnvironmentalFullConnector()
            >>> temp_data = env.search_climate_data("temperature trends", rows=200)
        """
        search_query = f"climate {query}" if query != "*:*" else "climate weather"
        
        return self.search_datasets(
            query=search_query,
            organization="noaa-gov",
            rows=rows,
        )

    @requires_license
    def bulk_export_epa_data(
        self,
        query: str = "*:*",
        max_datasets: int = 1000,
    ) -> pd.DataFrame:
        """
        Bulk export EPA datasets.

        Args:
            query: Search query
            max_datasets: Maximum datasets to export (up to 10,000)

        Returns:
            DataFrame with all matching EPA datasets
        """
        return self.bulk_export(
            query=query,
            organization="epa-gov",
            max_datasets=min(max_datasets, self.MAX_BULK_EXPORT),
        )

    def __repr__(self) -> str:
        return (
            f"DataGovEnvironmentalFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS}, "
            f"download_dir='{self.download_dir}')"
        )
