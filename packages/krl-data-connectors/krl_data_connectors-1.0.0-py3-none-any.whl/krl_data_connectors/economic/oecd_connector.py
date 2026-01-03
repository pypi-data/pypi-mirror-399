# ════════════════════════════════════════════════════════════════════════════════
# KRL Data Connectors - OECD API Connector
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
OECD Data API Connector.

Provides access to OECD.Stat and OECD Data API for statistical data covering:
- Economic indicators (GDP, trade, productivity)
- Social indicators (education, health, well-being)
- Environmental indicators (emissions, resources)
- Governance indicators (institutions, regulations)

API Documentation: https://data.oecd.org/api/

The OECD API uses SDMX (Statistical Data and Metadata eXchange) format.
Rate limiting: Moderate (no official limits, but be respectful).

Tier: COMMUNITY (no authentication required for public data)
"""

from __future__ import annotations

import logging
from datetime import datetime, UTC
from typing import Any, Dict, List, Literal, Optional, Union

import pandas as pd

from krl_data_connectors.base_connector import BaseConnector

__all__ = ["OECDConnector", "OECDDataset"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Common OECD Dataset Codes
# ════════════════════════════════════════════════════════════════════════════════


class OECDDataset:
    """
    Common OECD dataset identifiers.
    
    Reference: https://stats.oecd.org/
    """
    
    # Economic Outlook
    EO = "EO"                           # Economic Outlook
    QNA = "QNA"                         # Quarterly National Accounts
    SNA_TABLE1 = "SNA_TABLE1"           # Annual National Accounts (GDP)
    KEI = "KEI"                         # Key Economic Indicators
    MEI = "MEI"                         # Main Economic Indicators
    
    # Labor & Employment
    LFS_SEXAGE_I_R = "LFS_SEXAGE_I_R"   # Labour Force Statistics
    ALFS_SUMTAB = "ALFS_SUMTAB"         # Annual Labour Force Statistics
    STLABOUR = "STLABOUR"               # Short-Term Labour Statistics
    PDYGTH = "PDYGTH"                   # Productivity Growth
    AV_AN_WAGE = "AV_AN_WAGE"           # Average Annual Wages
    
    # Prices & Purchasing Power
    PPP2022 = "PPP2022"                 # Purchasing Power Parities
    PRICES_CPI = "PRICES_CPI"           # Consumer Price Indices
    
    # Trade
    BTD = "BTD"                         # Bilateral Trade in Goods
    TIVA_2021_C1 = "TIVA_2021_C1"       # Trade in Value Added
    
    # Education
    EAG_NEAC = "EAG_NEAC"               # Education at a Glance - Enrollment
    EAG_PERS_SHARE_AGE = "EAG_PERS_SHARE_AGE"  # Tertiary attainment
    RGRADSTY = "RGRADSTY"               # Graduates by Field
    EDU_ENRL_AGE = "EDU_ENRL_AGE"       # Enrollment by Age
    
    # Health
    HEALTH_STAT = "HEALTH_STAT"         # Health Status
    HEALTH_REAC = "HEALTH_REAC"         # Health Resources
    HEALTH_PROC = "HEALTH_PROC"         # Health Procedures
    SHA = "SHA"                         # System of Health Accounts
    
    # Well-being
    BLI = "BLI"                         # Better Life Index
    HW_NHW = "HW_NHW"                   # Household Net Worth
    IDD = "IDD"                         # Income Distribution
    
    # Environment
    AIR_GHG = "AIR_GHG"                 # Greenhouse Gas Emissions
    GREEN_GROWTH = "GREEN_GROWTH"       # Green Growth Indicators
    MATERIAL_RESOURCES = "MATERIAL_RESOURCES"  # Material Resources
    
    # Innovation & Technology
    MSTI = "MSTI"                       # Main Science and Technology Indicators
    PATS_IPC = "PATS_IPC"               # Patents by Technology
    BERD_INDUSTRY = "BERD_INDUSTRY"     # Business R&D by Industry
    
    # Social Protection
    SOCX_AGG = "SOCX_AGG"               # Social Expenditure (Aggregate)
    SOCX_DET = "SOCX_DET"               # Social Expenditure (Detailed)

    @classmethod
    def well_being_indicators(cls) -> List[str]:
        """Return datasets for well-being analysis."""
        return [cls.BLI, cls.IDD, cls.HEALTH_STAT]
    
    @classmethod
    def economic_indicators(cls) -> List[str]:
        """Return datasets for economic analysis."""
        return [cls.QNA, cls.KEI, cls.AV_AN_WAGE, cls.STLABOUR]


# ════════════════════════════════════════════════════════════════════════════════
# OECD Connector
# ════════════════════════════════════════════════════════════════════════════════


class OECDConnector(BaseConnector):
    """
    Connector for OECD Data API.
    
    Provides access to OECD statistical databases covering:
    - Economic indicators for 38 OECD member countries
    - Social statistics (education, health, well-being)
    - Environmental indicators
    - Trade and globalization data
    
    The OECD API uses SDMX format and is free for public data.
    
    Example:
        >>> connector = OECDConnector()
        >>> connector.connect()
        >>> 
        >>> # Fetch GDP data
        >>> gdp = connector.fetch_dataset(
        ...     dataset="QNA",
        ...     countries=["USA", "DEU", "JPN"],
        ...     measures=["GDP"],
        ...     start_year=2015
        ... )
        >>> 
        >>> # Fetch Better Life Index
        >>> bli = connector.fetch_better_life_index(countries=["USA", "SWE", "KOR"])
        >>> 
        >>> connector.disconnect()
    """
    
    BASE_URL = "https://stats.oecd.org/SDMX-JSON/data"
    DATA_EXPLORER_URL = "https://sdmx.oecd.org/public/rest/data"
    
    # OECD uses ISO 3166-1 alpha-3 codes, but some datasets use alpha-2
    MEMBER_COUNTRIES = [
        "AUS", "AUT", "BEL", "CAN", "CHL", "COL", "CRI", "CZE",
        "DNK", "EST", "FIN", "FRA", "DEU", "GRC", "HUN", "ISL",
        "IRL", "ISR", "ITA", "JPN", "KOR", "LVA", "LTU", "LUX",
        "MEX", "NLD", "NZL", "NOR", "POL", "PRT", "SVK", "SVN",
        "ESP", "SWE", "CHE", "TUR", "GBR", "USA"
    ]
    
    def __init__(
        self,
        cache_ttl: int = 86400,  # 24 hours
        timeout: int = 60,  # OECD API can be slow
        max_retries: int = 3,
        use_data_explorer: bool = False,
    ):
        """
        Initialize OECD connector.
        
        Args:
            cache_ttl: Cache time-to-live in seconds.
            timeout: Request timeout in seconds.
            max_retries: Maximum retry attempts.
            use_data_explorer: Use newer Data Explorer API (default: legacy SDMX-JSON).
        """
        super().__init__(
            api_key=None,  # OECD API is free
            cache_ttl=cache_ttl,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.use_data_explorer = use_data_explorer
        self._connected = False
    
    def _get_api_key(self) -> Optional[str]:
        """OECD API does not require authentication."""
        return None
    
    def connect(self) -> None:
        """
        Establish connection to OECD API.
        
        Validates API availability by testing a simple query.
        """
        try:
            # Test API with Better Life Index metadata
            test_url = f"{self.BASE_URL}/BLI/all/all"
            self._validate_url(test_url, allow_http=False)
            
            params = {
                "startTime": "2020",
                "endTime": "2020",
                "dimensionAtObservation": "allDimensions",
            }
            
            response = self._make_request(test_url, params=params, use_cache=True)
            
            if response and "dataSets" in response:
                self._connected = True
                self.logger.info("Connected to OECD API")
            else:
                raise ConnectionError("Invalid response from OECD API")
                
        except Exception as e:
            self._connected = False
            self.logger.error("Failed to connect to OECD API", exc_info=True)
            raise ConnectionError(f"OECD API connection failed: {e}") from e
    
    def fetch(self, **kwargs: Any) -> Any:
        """
        Generic fetch method - routes to specific fetch methods.
        
        Args:
            **kwargs: Must include 'dataset' key.
            
        Returns:
            Fetched data.
        """
        if "dataset" in kwargs:
            return self.fetch_dataset(**kwargs)
        else:
            raise ValueError("Must specify 'dataset' parameter")
    
    def fetch_dataset(
        self,
        dataset: str,
        countries: Union[str, List[str]] = "all",
        measures: Optional[List[str]] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        frequency: str = "A",  # Annual
        as_dataframe: bool = True,
    ) -> Union[pd.DataFrame, Dict[str, Any]]:
        """
        Fetch data from an OECD dataset.
        
        Args:
            dataset: OECD dataset identifier (e.g., "QNA", "BLI").
            countries: Country code(s) or "all".
            measures: List of measure codes (dataset-specific).
            start_year: Start year for filter.
            end_year: End year for filter.
            frequency: Data frequency (A=annual, Q=quarterly, M=monthly).
            as_dataframe: Return as DataFrame.
            
        Returns:
            DataFrame or raw API response.
        """
        if not self._connected:
            self.connect()
        
        # Build country filter
        if isinstance(countries, list):
            country_filter = "+".join(countries)
        elif countries == "all":
            country_filter = ""
        else:
            country_filter = countries
        
        # Build URL path
        # Format: /{dataset}/{filter}
        filter_str = country_filter if country_filter else "all"
        if measures:
            filter_str = f"{filter_str}+{'+'.join(measures)}"
        
        url = f"{self.BASE_URL}/{dataset}/{filter_str}/all"
        self._validate_url(url, allow_http=False)
        
        # Build query parameters
        params = {
            "dimensionAtObservation": "allDimensions",
        }
        
        if start_year:
            params["startTime"] = str(start_year)
        if end_year:
            params["endTime"] = str(end_year)
        
        # Make request
        response = self._make_request(url, params=params, use_cache=True)
        
        if not response:
            return pd.DataFrame() if as_dataframe else {}
        
        if as_dataframe:
            return self._sdmx_to_dataframe(response)
        
        return response
    
    def fetch_better_life_index(
        self,
        countries: Union[str, List[str]] = "all",
        year: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Fetch OECD Better Life Index data.
        
        The Better Life Index covers 11 dimensions of well-being:
        - Housing, Income, Jobs, Community, Education, Environment,
        - Civic Engagement, Health, Life Satisfaction, Safety, Work-Life Balance
        
        Args:
            countries: Country code(s).
            year: Specific year (default: latest).
            
        Returns:
            DataFrame with BLI indicators.
        """
        start_year = year if year else 2020
        end_year = year if year else datetime.now().year
        
        return self.fetch_dataset(
            dataset="BLI",
            countries=countries,
            start_year=start_year,
            end_year=end_year,
            as_dataframe=True,
        )
    
    def fetch_gdp(
        self,
        countries: Union[str, List[str]] = "all",
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        measure: Literal["GDP", "GDPPC", "GDPGR"] = "GDP",
    ) -> pd.DataFrame:
        """
        Fetch GDP data from Quarterly National Accounts.
        
        Args:
            countries: Country code(s).
            start_year: Start year.
            end_year: End year.
            measure: GDP measure type.
            
        Returns:
            DataFrame with GDP data.
        """
        return self.fetch_dataset(
            dataset="QNA",
            countries=countries,
            measures=[measure],
            start_year=start_year,
            end_year=end_year,
            as_dataframe=True,
        )
    
    def fetch_labor_statistics(
        self,
        countries: Union[str, List[str]] = "all",
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Fetch labor market statistics.
        
        Includes unemployment rates, employment ratios, and labor force participation.
        
        Args:
            countries: Country code(s).
            start_year: Start year.
            end_year: End year.
            
        Returns:
            DataFrame with labor statistics.
        """
        return self.fetch_dataset(
            dataset="STLABOUR",
            countries=countries,
            start_year=start_year,
            end_year=end_year,
            as_dataframe=True,
        )
    
    def fetch_education_statistics(
        self,
        countries: Union[str, List[str]] = "all",
        year: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Fetch education statistics from Education at a Glance.
        
        Args:
            countries: Country code(s).
            year: Specific year.
            
        Returns:
            DataFrame with education indicators.
        """
        start_year = year if year else 2015
        end_year = year if year else datetime.now().year
        
        return self.fetch_dataset(
            dataset="EAG_NEAC",
            countries=countries,
            start_year=start_year,
            end_year=end_year,
            as_dataframe=True,
        )
    
    def fetch_income_distribution(
        self,
        countries: Union[str, List[str]] = "all",
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Fetch income distribution data.
        
        Includes Gini coefficient, income shares, poverty rates.
        
        Args:
            countries: Country code(s).
            start_year: Start year.
            end_year: End year.
            
        Returns:
            DataFrame with income distribution data.
        """
        return self.fetch_dataset(
            dataset="IDD",
            countries=countries,
            start_year=start_year,
            end_year=end_year,
            as_dataframe=True,
        )
    
    def fetch_health_statistics(
        self,
        countries: Union[str, List[str]] = "all",
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Fetch health statistics.
        
        Args:
            countries: Country code(s).
            start_year: Start year.
            end_year: End year.
            
        Returns:
            DataFrame with health indicators.
        """
        return self.fetch_dataset(
            dataset="HEALTH_STAT",
            countries=countries,
            start_year=start_year,
            end_year=end_year,
            as_dataframe=True,
        )
    
    def fetch_ghg_emissions(
        self,
        countries: Union[str, List[str]] = "all",
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Fetch greenhouse gas emissions data.
        
        Args:
            countries: Country code(s).
            start_year: Start year.
            end_year: End year.
            
        Returns:
            DataFrame with emissions data.
        """
        return self.fetch_dataset(
            dataset="AIR_GHG",
            countries=countries,
            start_year=start_year,
            end_year=end_year,
            as_dataframe=True,
        )
    
    def _sdmx_to_dataframe(self, response: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert SDMX-JSON response to pandas DataFrame.
        
        OECD API returns data in SDMX format which needs parsing.
        
        Args:
            response: Raw API response.
            
        Returns:
            Parsed DataFrame.
        """
        try:
            # Extract structure
            structure = response.get("structure", {})
            dimensions = structure.get("dimensions", {}).get("observation", [])
            attributes = structure.get("attributes", {}).get("observation", [])
            
            # Build dimension lookups
            dim_lookups = {}
            for dim in dimensions:
                dim_id = dim.get("id")
                values = dim.get("values", [])
                dim_lookups[dim_id] = {
                    i: v.get("name", v.get("id", str(i)))
                    for i, v in enumerate(values)
                }
            
            # Extract data
            datasets = response.get("dataSets", [])
            if not datasets:
                return pd.DataFrame()
            
            observations = datasets[0].get("observations", {})
            
            # Parse observations
            records = []
            for obs_key, obs_value in observations.items():
                # obs_key is like "0:0:0:0:0" - indices into dimensions
                indices = [int(i) for i in obs_key.split(":")]
                
                record = {}
                for i, idx in enumerate(indices):
                    if i < len(dimensions):
                        dim_id = dimensions[i].get("id", f"dim_{i}")
                        record[dim_id] = dim_lookups.get(dim_id, {}).get(idx, idx)
                
                # obs_value is [value, status_idx, ...]
                record["value"] = obs_value[0] if obs_value else None
                
                records.append(record)
            
            df = pd.DataFrame(records)
            
            # Convert value column
            if "value" in df.columns:
                df["value"] = pd.to_numeric(df["value"], errors="coerce")
            
            return df
            
        except Exception as e:
            self.logger.warning(f"Failed to parse SDMX response: {e}")
            return pd.DataFrame()
    
    def list_datasets(self) -> pd.DataFrame:
        """
        List available OECD datasets.
        
        Returns:
            DataFrame with dataset metadata.
        """
        # OECD doesn't have a simple dataset list endpoint,
        # so we return a curated list of commonly used datasets
        datasets = [
            {"id": "BLI", "name": "Better Life Index", "category": "Well-being"},
            {"id": "QNA", "name": "Quarterly National Accounts", "category": "Economy"},
            {"id": "KEI", "name": "Key Economic Indicators", "category": "Economy"},
            {"id": "STLABOUR", "name": "Short-Term Labour Statistics", "category": "Labor"},
            {"id": "IDD", "name": "Income Distribution Database", "category": "Income"},
            {"id": "HEALTH_STAT", "name": "Health Status", "category": "Health"},
            {"id": "EAG_NEAC", "name": "Education at a Glance - Enrollment", "category": "Education"},
            {"id": "AIR_GHG", "name": "Greenhouse Gas Emissions", "category": "Environment"},
            {"id": "PPP2022", "name": "Purchasing Power Parities", "category": "Prices"},
            {"id": "SOCX_AGG", "name": "Social Expenditure (Aggregate)", "category": "Social"},
        ]
        
        return pd.DataFrame(datasets)
