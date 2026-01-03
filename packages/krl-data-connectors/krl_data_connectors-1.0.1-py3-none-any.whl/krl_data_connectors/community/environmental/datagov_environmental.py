# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Environmental Domain Connector - Community Tier

Pre-configured access to environmental datasets from Data.gov, filtered to
EPA, NOAA, and other environmental agencies. Provides 25,000+ datasets on
air quality, water resources, climate, superfund sites, and more.

Domain Organizations:
- EPA (epa-gov): Air quality, water quality, toxic releases, superfund
- NOAA (noaa-gov): Climate data, weather, ocean observations
- DOI (doi-gov): Land, water, wildlife resources
- USGS: Geological and hydrological data

Key Dataset Categories:
- Air Quality: AQS, AirNow, emissions inventories
- Water Quality: WQP, drinking water, watersheds
- Climate: Historical weather, climate normals, projections
- Land: Superfund sites, brownfields, land use
- Wildlife: Species data, habitat assessments

Usage:
    from krl_data_connectors.community.environmental import DataGovEnvironmentalConnector
    
    env = DataGovEnvironmentalConnector()
    
    # Search environmental datasets (auto-filtered to EPA/NOAA)
    results = env.search_datasets("air quality monitoring")
    
    # Use agency-specific convenience methods
    epa_data = env.search_epa_datasets("superfund sites")
    noaa_data = env.search_noaa_datasets("sea level rise")
    
    # Cross-domain search (bypass environmental filter)
    all_health_env = env.search_all_domains("environmental health")
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.community.civic.datagov_catalog import DataGovCatalogConnector


class DataGovEnvironmentalConnector(DataGovCatalogConnector):
    """
    Data.gov Environmental Domain Connector - Community Tier

    Pre-configured for EPA, NOAA, and environmental agency datasets.
    All searches are automatically filtered to environmental organizations
    unless overridden with a specific organization parameter.

    Inherits from DataGovCatalogConnector with:
    - DOMAIN_ORGANIZATIONS: ["epa-gov", "noaa-gov", "doi-gov"]
    - Domain-specific popular datasets
    - Convenience methods for EPA, NOAA, and climate data

    Limitations (Community Tier):
    - Maximum 50 results per search query
    - No bulk export functionality
    - Upgrade to DataGovEnvironmentalFullConnector for unlimited access
    """

    _connector_name = "DataGov_Environmental"

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

    # Override popular datasets with environmental focus
    POPULAR_DATASETS: Dict[str, List[str]] = {
        "air_quality": [
            "air-quality-annual-summary",
            "epa-air-quality-system-aqs",
            "airnow-air-quality-index",
            "national-emissions-inventory",
            "toxic-release-inventory",
        ],
        "water": [
            "water-quality-portal",
            "national-water-quality-assessment",
            "safe-drinking-water-information-system",
            "watershed-boundary-dataset",
            "national-hydrography-dataset",
        ],
        "climate": [
            "global-historical-climatology-network",
            "noaa-climate-normals",
            "climate-data-online",
            "sea-level-trends",
            "drought-monitor",
        ],
        "land_contamination": [
            "superfund-sites",
            "brownfields-and-land-revitalization",
            "toxic-release-inventory",
            "hazardous-waste-generators",
            "rcra-corrective-action",
        ],
        "weather": [
            "local-climatological-data",
            "storm-events-database",
            "global-surface-summary-of-day",
            "integrated-surface-database",
            "u-s-hourly-climate-normals",
        ],
    }

    # Environmental organizations with descriptions
    WHITELISTED_ORGANIZATIONS: Dict[str, str] = {
        "epa-gov": "Environmental Protection Agency",
        "noaa-gov": "National Oceanic and Atmospheric Administration",
        "doi-gov": "Department of the Interior",
        "usgs": "United States Geological Survey",
        "nasa-gov": "National Aeronautics and Space Administration",
        "energy-gov": "Department of Energy",
    }

    def search_epa_datasets(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search EPA datasets specifically.

        Convenience method that filters to EPA organization regardless
        of domain settings.

        Args:
            query: Search query string
            formats: Filter by resource format (e.g., ['CSV', 'JSON'])
            rows: Number of results (max 50 for Community tier)

        Returns:
            DataFrame with EPA dataset metadata

        Example:
            >>> env = DataGovEnvironmentalConnector()
            >>> superfund = env.search_epa_datasets("superfund contamination")
        """
        return self.search_datasets(
            query=query,
            organization="epa-gov",
            formats=formats,
            rows=rows,
        )

    def search_noaa_datasets(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search NOAA datasets specifically.

        Convenience method for climate, weather, and ocean data.

        Args:
            query: Search query string
            formats: Filter by resource format (e.g., ['CSV', 'JSON'])
            rows: Number of results (max 50 for Community tier)

        Returns:
            DataFrame with NOAA dataset metadata

        Example:
            >>> env = DataGovEnvironmentalConnector()
            >>> climate = env.search_noaa_datasets("historical temperature")
        """
        return self.search_datasets(
            query=query,
            organization="noaa-gov",
            formats=formats,
            rows=rows,
        )

    def search_air_quality_data(
        self,
        query: str = "*:*",
        state: Optional[str] = None,
        rows: int = 10,
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

    def search_water_quality_data(
        self,
        query: str = "*:*",
        rows: int = 10,
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

    def search_climate_data(
        self,
        query: str = "*:*",
        rows: int = 10,
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
            >>> env = DataGovEnvironmentalConnector()
            >>> temp_data = env.search_climate_data("temperature trends")
        """
        search_query = f"climate {query}" if query != "*:*" else "climate weather"
        
        return self.search_datasets(
            query=search_query,
            organization="noaa-gov",
            rows=rows,
        )

    def search_superfund_sites(
        self,
        query: str = "*:*",
        state: Optional[str] = None,
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for EPA Superfund site datasets.

        Args:
            query: Search query (default: all superfund data)
            state: Optional state filter
            rows: Number of results

        Returns:
            DataFrame with superfund dataset metadata
        """
        search_query = f"superfund {query}" if query != "*:*" else "superfund sites"
        if state:
            search_query = f"{search_query} {state}"
        
        return self.search_datasets(
            query=search_query,
            organization="epa-gov",
            rows=rows,
        )

    def get_environmental_categories(self) -> List[str]:
        """
        Get available environmental dataset categories.

        Returns:
            List of category names specific to environmental data
        """
        return list(self.POPULAR_DATASETS.keys())

    def __repr__(self) -> str:
        return (
            f"DataGovEnvironmentalConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS}, "
            f"max_results={self.MAX_RESULTS})"
        )
