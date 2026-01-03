# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Geographic Domain Connector - Community Tier

Pre-configured access to geographic datasets from Data.gov, filtered to
USGS, DOI, Census, and NOAA agencies. Provides datasets on geology,
boundaries, topography, land use, and natural resources.

Domain Organizations:
- USGS (usgs-gov): Geological surveys, earthquakes, water resources
- DOI (doi-gov): Land, natural resources, public lands
- Census (census-gov): Geographic boundaries, TIGER files
- NOAA (noaa-gov): Coastal, ocean geography

Key Dataset Categories:
- Geology: Surveys, mineral resources, geologic maps
- Boundaries: Political, administrative boundaries
- Topography: Elevation, terrain, landforms
- Land Use: Land cover, development patterns
- Natural Resources: Water, minerals, energy

Usage:
    from krl_data_connectors.community.geographic import DataGovGeographicConnector
    
    geo = DataGovGeographicConnector()
    
    # Search geographic datasets (auto-filtered to USGS/DOI)
    results = geo.search_datasets("topographic maps")
    
    # Use convenience methods
    usgs = geo.search_usgs_data("earthquake hazards")
    boundaries = geo.search_boundaries_data("county lines")
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.community.civic.datagov_catalog import DataGovCatalogConnector


class DataGovGeographicConnector(DataGovCatalogConnector):
    """
    Data.gov Geographic Domain Connector - Community Tier

    Pre-configured for USGS, DOI, Census, and geographic agency datasets.
    All searches are automatically filtered to geographic organizations
    unless overridden with a specific organization parameter.

    Limitations (Community Tier):
    - Maximum 50 results per search query
    - No bulk export functionality
    - Upgrade to DataGovGeographicFullConnector for unlimited access
    """

    _connector_name = "DataGov_Geographic"

    # Domain configuration - auto-filter searches to these organizations
    DOMAIN_ORGANIZATIONS: List[str] = [
        "usgs-gov",     # United States Geological Survey
        "doi-gov",      # Department of the Interior
        "census-gov",   # Census Bureau (geographic boundaries)
        "noaa-gov",     # NOAA (coastal/ocean geography)
    ]
    
    DOMAIN_TAGS: List[str] = [
        "geography",
        "maps",
        "boundaries",
        "geology",
        "topography",
        "gis",
        "land-use",
    ]
    
    DOMAIN_NAME: str = "Geographic"

    # Override popular datasets with geographic focus
    POPULAR_DATASETS: Dict[str, List[str]] = {
        "geology": [
            "usgs-geologic-maps",
            "mineral-resources",
            "earthquake-catalog",
            "volcano-monitoring",
            "landslide-inventory",
        ],
        "boundaries": [
            "tiger-line-shapefiles",
            "county-boundaries",
            "state-boundaries",
            "congressional-districts",
            "zip-code-tabulation-areas",
        ],
        "topography": [
            "national-elevation-dataset",
            "3dep-elevation",
            "digital-elevation-models",
            "terrain-analysis",
            "contour-maps",
        ],
        "land_use": [
            "national-land-cover-database",
            "land-use-land-cover",
            "protected-areas",
            "gap-analysis-program",
            "urban-areas",
        ],
        "hydrology": [
            "national-hydrography-dataset",
            "watershed-boundaries",
            "streamflow-data",
            "groundwater-levels",
            "water-use-data",
        ],
    }

    # Geographic organizations with descriptions
    WHITELISTED_ORGANIZATIONS: Dict[str, str] = {
        "usgs-gov": "United States Geological Survey",
        "doi-gov": "Department of the Interior",
        "census-gov": "U.S. Census Bureau",
        "noaa-gov": "National Oceanic and Atmospheric Administration",
        "blm-gov": "Bureau of Land Management",
        "nps-gov": "National Park Service",
    }

    def search_usgs_data(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search USGS datasets specifically.

        Args:
            query: Search query string
            formats: Filter by resource format
            rows: Number of results (max 50 for Community tier)

        Returns:
            DataFrame with USGS dataset metadata
        """
        return self.search_datasets(
            query=query,
            organization="usgs-gov",
            formats=formats,
            rows=rows,
        )

    def search_boundaries_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for geographic boundary datasets.

        Args:
            query: Search query (default: all boundary datasets)
            rows: Number of results

        Returns:
            DataFrame with boundary dataset metadata
        """
        search_query = f"boundaries {query}" if query != "*:*" else "boundaries TIGER shapefile"
        
        return self.search_datasets(
            query=search_query,
            organization="census-gov",
            rows=rows,
        )

    def search_earthquake_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for earthquake and seismic datasets.

        Args:
            query: Search query (default: all earthquake datasets)
            rows: Number of results

        Returns:
            DataFrame with earthquake dataset metadata
        """
        search_query = f"earthquake {query}" if query != "*:*" else "earthquake seismic hazards"
        
        return self.search_datasets(
            query=search_query,
            organization="usgs-gov",
            rows=rows,
        )

    def search_elevation_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for elevation and topography datasets.

        Args:
            query: Search query (default: all elevation datasets)
            rows: Number of results

        Returns:
            DataFrame with elevation dataset metadata
        """
        search_query = f"elevation {query}" if query != "*:*" else "elevation DEM topography"
        
        return self.search_datasets(
            query=search_query,
            rows=rows,
        )

    def search_land_cover_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for land use and land cover datasets.

        Args:
            query: Search query (default: all land cover datasets)
            rows: Number of results

        Returns:
            DataFrame with land cover dataset metadata
        """
        search_query = f"land cover {query}" if query != "*:*" else "land cover land use NLCD"
        
        return self.search_datasets(
            query=search_query,
            rows=rows,
        )

    def search_hydrology_data(
        self,
        query: str = "*:*",
        rows: int = 10,
    ) -> pd.DataFrame:
        """
        Search for water and hydrology datasets.

        Args:
            query: Search query (default: all hydrology datasets)
            rows: Number of results

        Returns:
            DataFrame with hydrology dataset metadata
        """
        search_query = f"hydrology water {query}" if query != "*:*" else "hydrology streamflow watershed"
        
        return self.search_datasets(
            query=search_query,
            organization="usgs-gov",
            rows=rows,
        )

    def get_geographic_categories(self) -> List[str]:
        """Get available geographic dataset categories."""
        return list(self.POPULAR_DATASETS.keys())

    def __repr__(self) -> str:
        return (
            f"DataGovGeographicConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS}, "
            f"max_results={self.MAX_RESULTS})"
        )
