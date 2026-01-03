# ════════════════════════════════════════════════════════════════════════════════
# KRL Data Connectors - UN Data API Connector
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
UN Data API Connector.

Provides access to United Nations statistical databases including:
- UN Statistics Division (UNSD) data
- UN Development Programme (UNDP) Human Development data
- UN Population Division (World Population Prospects)
- UN COMTRADE (International Trade Statistics)
- ILO (International Labour Organization) statistics
- FAO (Food and Agriculture Organization) data

Primary APIs:
- UN Data API: https://data.un.org/
- UNDP HDR API: https://hdr.undp.org/data-center/api
- UN Population API: https://population.un.org/dataportalapi/

Tier: COMMUNITY (no authentication required for most endpoints)
"""

from __future__ import annotations

import logging
from datetime import datetime, UTC
from typing import Any, Dict, List, Literal, Optional, Union

import pandas as pd

from krl_data_connectors.base_connector import BaseConnector

__all__ = ["UNDataConnector", "UNIndicator", "HDRIndicator"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# UN Indicator Codes
# ════════════════════════════════════════════════════════════════════════════════


class UNIndicator:
    """
    Common UN Statistics Division indicator codes.
    
    Reference: https://data.un.org/
    """
    
    # Population
    POPULATION_TOTAL = "SP_POP_TOTL"
    POPULATION_GROWTH = "SP_POP_GROW"
    POPULATION_DENSITY = "EN_POP_DNST"
    LIFE_EXPECTANCY = "SP_DYN_LE00_IN"
    FERTILITY_RATE = "SP_DYN_TFRT_IN"
    
    # Economic
    GDP_CURRENT = "NY_GDP_MKTP_CD"
    GDP_PER_CAPITA = "NY_GDP_PCAP_CD"
    GNI_PER_CAPITA = "NY_GNP_PCAP_CD"
    
    # Environment
    CO2_EMISSIONS = "EN_ATM_CO2E_PC"
    FOREST_AREA = "AG_LND_FRST_ZS"
    
    # SDG Indicators
    SDG_1_1_1 = "SI_POV_DAY1"  # Poverty $1.90/day
    SDG_1_2_1 = "SI_POV_NAHC"  # National poverty line
    SDG_2_1_1 = "SN_ITK_DEFC"  # Undernourishment
    SDG_3_1_1 = "SH_STA_MMR"   # Maternal mortality
    SDG_3_2_1 = "SH_DYN_MORT"  # Under-5 mortality
    SDG_4_1_1 = "SE_TOT_PRFL"  # Reading proficiency
    SDG_5_5_1 = "SG_GEN_PARL"  # Women in parliament


class HDRIndicator:
    """
    UNDP Human Development Report indicator codes.
    
    Reference: https://hdr.undp.org/data-center/documentation-and-downloads
    """
    
    # Human Development Index
    HDI = "hdi"                             # Human Development Index
    HDI_RANK = "hdi_rank"                   # HDI Rank
    
    # HDI Components
    LIFE_EXPECTANCY = "le"                  # Life expectancy at birth
    EXPECTED_YEARS_SCHOOLING = "eys"        # Expected years of schooling
    MEAN_YEARS_SCHOOLING = "mys"            # Mean years of schooling
    GNI_PER_CAPITA = "gnipc"                # GNI per capita (PPP $)
    
    # Inequality-adjusted HDI
    IHDI = "ihdi"                           # Inequality-adjusted HDI
    IHDI_LIFE = "ineq_le"                   # Inequality in life expectancy
    IHDI_EDUCATION = "ineq_edu"             # Inequality in education
    IHDI_INCOME = "ineq_inc"                # Inequality in income
    
    # Gender Development Index
    GDI = "gdi"                             # Gender Development Index
    GDI_GROUP = "gdi_group"                 # GDI Group (1-5)
    HDI_FEMALE = "hdi_f"                    # Female HDI
    HDI_MALE = "hdi_m"                      # Male HDI
    
    # Gender Inequality Index
    GII = "gii"                             # Gender Inequality Index
    GII_RANK = "gii_rank"                   # GII Rank
    MATERNAL_MORTALITY = "mmr"              # Maternal mortality ratio
    ADOLESCENT_BIRTH_RATE = "abr"           # Adolescent birth rate
    PARLIAMENT_SHARE_FEMALE = "pr_f"        # Share of seats in parliament (female)
    LABOR_FORCE_FEMALE = "lfpr_f"           # Labour force participation (female)
    LABOR_FORCE_MALE = "lfpr_m"             # Labour force participation (male)
    
    # Multidimensional Poverty Index
    MPI = "mpi"                             # Multidimensional Poverty Index
    MPI_HEADCOUNT = "mpi_h"                 # MPI Headcount
    MPI_INTENSITY = "mpi_a"                 # MPI Intensity
    
    # Other indices
    PLANETARY_PRESSURES_ADJ_HDI = "phdi"    # Planetary pressures-adjusted HDI
    
    @classmethod
    def hdi_components(cls) -> List[str]:
        """Return HDI component indicators."""
        return [
            cls.HDI,
            cls.LIFE_EXPECTANCY,
            cls.EXPECTED_YEARS_SCHOOLING,
            cls.MEAN_YEARS_SCHOOLING,
            cls.GNI_PER_CAPITA,
        ]
    
    @classmethod
    def inequality_indicators(cls) -> List[str]:
        """Return inequality-related indicators."""
        return [cls.IHDI, cls.GII, cls.MPI]


# ════════════════════════════════════════════════════════════════════════════════
# UN Data Connector
# ════════════════════════════════════════════════════════════════════════════════


class UNDataConnector(BaseConnector):
    """
    Connector for UN statistical data APIs.
    
    Provides unified access to multiple UN data sources:
    - UNDP Human Development Report (HDR) API
    - UN Statistics Division (UNSD)
    - UN Population Division
    
    This connector prioritizes the HDR API for human development data
    as it provides the most reliable HDI calculations.
    
    Example:
        >>> connector = UNDataConnector()
        >>> connector.connect()
        >>> 
        >>> # Fetch HDI data
        >>> hdi = connector.fetch_hdi(countries=["USA", "NOR", "CHE"], year=2022)
        >>> 
        >>> # Fetch Gender Inequality Index
        >>> gii = connector.fetch_gii(countries=["all"])
        >>> 
        >>> # Fetch MPI data
        >>> mpi = connector.fetch_mpi()
        >>> 
        >>> connector.disconnect()
    """
    
    # UNDP Human Development Report API
    HDR_API_BASE = "https://hdr.undp.org/data-center/api"
    
    # UN Data API (UNSD)
    UNSD_API_BASE = "https://data.un.org/ws/rest/data"
    
    # UN Population API
    POPULATION_API_BASE = "https://population.un.org/dataportalapi/api/v1"
    
    def __init__(
        self,
        cache_ttl: int = 86400 * 7,  # 7 days (HDI updates annually)
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize UN Data connector.
        
        Args:
            cache_ttl: Cache TTL in seconds (default: 7 days).
            timeout: Request timeout in seconds.
            max_retries: Maximum retry attempts.
        """
        super().__init__(
            api_key=None,  # UN APIs are free
            cache_ttl=cache_ttl,
            timeout=timeout,
            max_retries=max_retries,
        )
        self._connected = False
        self._hdr_available = False
        self._unsd_available = False
    
    def _get_api_key(self) -> Optional[str]:
        """UN APIs do not require authentication."""
        return None
    
    def connect(self) -> None:
        """
        Establish connection to UN APIs.
        
        Tests both HDR and UNSD APIs for availability.
        """
        errors = []
        
        # Test HDR API
        try:
            test_url = f"{self.HDR_API_BASE}/indicator-data?indicator=hdi&country=USA&page=1&page_size=1"
            self._validate_url(test_url, allow_http=False)
            response = self._make_request(test_url, use_cache=True)
            
            if response:
                self._hdr_available = True
                self.logger.info("HDR API is available")
        except Exception as e:
            errors.append(f"HDR API: {e}")
            self.logger.warning(f"HDR API not available: {e}")
        
        # We consider connected if at least HDR API works
        if self._hdr_available:
            self._connected = True
            self.logger.info("Connected to UN Data APIs")
        else:
            raise ConnectionError(f"UN Data API connection failed: {'; '.join(errors)}")
    
    def fetch(self, **kwargs: Any) -> Any:
        """
        Generic fetch method - routes to specific methods.
        
        Args:
            **kwargs: Must include 'indicator' or 'method'.
            
        Returns:
            Fetched data.
        """
        if "method" in kwargs:
            method = kwargs.pop("method")
            if method == "hdi":
                return self.fetch_hdi(**kwargs)
            elif method == "gii":
                return self.fetch_gii(**kwargs)
            elif method == "mpi":
                return self.fetch_mpi(**kwargs)
            elif method == "countries":
                return self.fetch_countries(**kwargs)
            else:
                raise ValueError(f"Unknown method: {method}")
        elif "indicator" in kwargs:
            return self.fetch_indicator(**kwargs)
        else:
            raise ValueError("Must specify 'method' or 'indicator' parameter")
    
    def fetch_indicator(
        self,
        indicator: str,
        countries: Union[str, List[str]] = "all",
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        as_dataframe: bool = True,
    ) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Fetch a specific indicator from HDR API.
        
        Args:
            indicator: HDR indicator code (e.g., "hdi", "gii").
            countries: ISO 3166-1 alpha-3 codes or "all".
            start_year: Start year filter.
            end_year: End year filter.
            as_dataframe: Return as DataFrame.
            
        Returns:
            Indicator data.
        """
        if not self._connected:
            self.connect()
        
        if not self._hdr_available:
            raise ConnectionError("HDR API is not available")
        
        # Build country filter
        if isinstance(countries, list):
            country_param = ",".join(countries)
        elif countries == "all":
            country_param = None
        else:
            country_param = countries
        
        # Build URL
        url = f"{self.HDR_API_BASE}/indicator-data"
        self._validate_url(url, allow_http=False)
        
        params = {
            "indicator": indicator,
            "page_size": 500,
        }
        
        if country_param:
            params["country"] = country_param
        if start_year:
            params["year"] = f"{start_year}:{end_year or datetime.now().year}"
        
        # Fetch all pages
        all_data = []
        page = 1
        
        while True:
            params["page"] = page
            response = self._make_request(url, params=params, use_cache=True)
            
            if not response:
                break
            
            data = response.get("data", [])
            if not data:
                break
            
            all_data.extend(data)
            
            # Check pagination
            pagination = response.get("pagination", {})
            total_pages = pagination.get("total_pages", 1)
            
            if page >= total_pages:
                break
            
            page += 1
        
        if as_dataframe:
            return self._to_dataframe(all_data)
        
        return all_data
    
    def fetch_hdi(
        self,
        countries: Union[str, List[str]] = "all",
        year: Optional[int] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        include_components: bool = True,
    ) -> pd.DataFrame:
        """
        Fetch Human Development Index data.
        
        The HDI is a composite index measuring:
        1. Long and healthy life (life expectancy)
        2. Knowledge (expected + mean years of schooling)
        3. Standard of living (GNI per capita)
        
        Args:
            countries: Country code(s) or "all".
            year: Specific year (alternative to range).
            start_year: Start year of range.
            end_year: End year of range.
            include_components: Include HDI component indicators.
            
        Returns:
            DataFrame with HDI data.
        """
        if year:
            start_year = year
            end_year = year
        
        if include_components:
            indicators = HDRIndicator.hdi_components()
        else:
            indicators = [HDRIndicator.HDI]
        
        dfs = []
        for indicator in indicators:
            try:
                df = self.fetch_indicator(
                    indicator=indicator,
                    countries=countries,
                    start_year=start_year,
                    end_year=end_year,
                    as_dataframe=True,
                )
                if not df.empty:
                    dfs.append(df)
            except Exception as e:
                self.logger.warning(f"Failed to fetch {indicator}: {e}")
        
        if not dfs:
            return pd.DataFrame()
        
        # Combine all indicators
        result = dfs[0]
        for df in dfs[1:]:
            # Pivot and merge
            result = result.merge(
                df,
                on=["country_code", "country_name", "year"],
                how="outer",
                suffixes=("", "_dup")
            )
        
        # Drop duplicate columns
        result = result.loc[:, ~result.columns.str.endswith("_dup")]
        
        return result.sort_values(["year", "country_code"])
    
    def fetch_ihdi(
        self,
        countries: Union[str, List[str]] = "all",
        year: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Fetch Inequality-adjusted Human Development Index.
        
        The IHDI adjusts HDI for inequality in each dimension.
        
        Args:
            countries: Country code(s).
            year: Specific year.
            
        Returns:
            DataFrame with IHDI data.
        """
        indicators = [
            HDRIndicator.IHDI,
            HDRIndicator.IHDI_LIFE,
            HDRIndicator.IHDI_EDUCATION,
            HDRIndicator.IHDI_INCOME,
        ]
        
        dfs = []
        for indicator in indicators:
            df = self.fetch_indicator(
                indicator=indicator,
                countries=countries,
                start_year=year,
                end_year=year,
                as_dataframe=True,
            )
            if not df.empty:
                dfs.append(df)
        
        if not dfs:
            return pd.DataFrame()
        
        return pd.concat(dfs, ignore_index=True)
    
    def fetch_gii(
        self,
        countries: Union[str, List[str]] = "all",
        year: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Fetch Gender Inequality Index data.
        
        The GII reflects gender-based disadvantage in:
        - Reproductive health
        - Empowerment
        - Labor market
        
        Args:
            countries: Country code(s).
            year: Specific year.
            
        Returns:
            DataFrame with GII data.
        """
        return self.fetch_indicator(
            indicator=HDRIndicator.GII,
            countries=countries,
            start_year=year,
            end_year=year,
            as_dataframe=True,
        )
    
    def fetch_gdi(
        self,
        countries: Union[str, List[str]] = "all",
        year: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Fetch Gender Development Index data.
        
        The GDI measures gender gaps in human development.
        
        Args:
            countries: Country code(s).
            year: Specific year.
            
        Returns:
            DataFrame with GDI data.
        """
        indicators = [
            HDRIndicator.GDI,
            HDRIndicator.HDI_FEMALE,
            HDRIndicator.HDI_MALE,
        ]
        
        dfs = []
        for indicator in indicators:
            df = self.fetch_indicator(
                indicator=indicator,
                countries=countries,
                start_year=year,
                end_year=year,
            )
            if not df.empty:
                dfs.append(df)
        
        if not dfs:
            return pd.DataFrame()
        
        return pd.concat(dfs, ignore_index=True)
    
    def fetch_mpi(
        self,
        countries: Union[str, List[str]] = "all",
        year: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Fetch Multidimensional Poverty Index data.
        
        The global MPI examines overlapping deprivations in:
        - Health
        - Education
        - Standard of living
        
        Args:
            countries: Country code(s).
            year: Specific year.
            
        Returns:
            DataFrame with MPI data.
        """
        indicators = [
            HDRIndicator.MPI,
            HDRIndicator.MPI_HEADCOUNT,
            HDRIndicator.MPI_INTENSITY,
        ]
        
        dfs = []
        for indicator in indicators:
            df = self.fetch_indicator(
                indicator=indicator,
                countries=countries,
                start_year=year,
                end_year=year,
            )
            if not df.empty:
                dfs.append(df)
        
        if not dfs:
            return pd.DataFrame()
        
        return pd.concat(dfs, ignore_index=True)
    
    def fetch_phdi(
        self,
        countries: Union[str, List[str]] = "all",
        year: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Fetch Planetary Pressures-adjusted HDI.
        
        The PHDI adjusts HDI for planetary pressures (CO2 emissions, material footprint).
        
        Args:
            countries: Country code(s).
            year: Specific year.
            
        Returns:
            DataFrame with PHDI data.
        """
        return self.fetch_indicator(
            indicator=HDRIndicator.PLANETARY_PRESSURES_ADJ_HDI,
            countries=countries,
            start_year=year,
            end_year=year,
        )
    
    def fetch_countries(self, as_dataframe: bool = True) -> Union[pd.DataFrame, List[Dict]]:
        """
        Fetch list of countries with HDR data.
        
        Returns:
            Country metadata.
        """
        if not self._connected:
            self.connect()
        
        url = f"{self.HDR_API_BASE}/countries"
        self._validate_url(url, allow_http=False)
        
        response = self._make_request(url, use_cache=True)
        
        if not response:
            return pd.DataFrame() if as_dataframe else []
        
        data = response.get("data", [])
        
        if as_dataframe:
            return pd.DataFrame(data)
        
        return data
    
    def fetch_indicators_metadata(self) -> pd.DataFrame:
        """
        Fetch metadata about available HDR indicators.
        
        Returns:
            DataFrame with indicator definitions.
        """
        if not self._connected:
            self.connect()
        
        url = f"{self.HDR_API_BASE}/indicators"
        self._validate_url(url, allow_http=False)
        
        response = self._make_request(url, use_cache=True)
        
        if not response:
            return pd.DataFrame()
        
        return pd.DataFrame(response.get("data", []))
    
    def _to_dataframe(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert API response to DataFrame.
        
        Args:
            data: Raw API response data.
            
        Returns:
            Cleaned DataFrame.
        """
        if not data:
            return pd.DataFrame()
        
        records = []
        for record in data:
            records.append({
                "country_code": record.get("country_code") or record.get("iso3"),
                "country_name": record.get("country_name") or record.get("country"),
                "year": record.get("year"),
                "indicator_code": record.get("indicator_code") or record.get("indicator"),
                "indicator_name": record.get("indicator_name"),
                "value": record.get("value"),
            })
        
        df = pd.DataFrame(records)
        
        # Convert value to numeric
        if "value" in df.columns:
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
        
        # Convert year to int
        if "year" in df.columns:
            df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
        
        return df.sort_values(["country_code", "year"])
    
    def get_hdi_tier(self, hdi_value: float) -> str:
        """
        Classify HDI value into development tier.
        
        UNDP Classification:
        - Very High: 0.800 and above
        - High: 0.700–0.799
        - Medium: 0.550–0.699
        - Low: Below 0.550
        
        Args:
            hdi_value: HDI value (0-1).
            
        Returns:
            Development tier classification.
        """
        if hdi_value >= 0.800:
            return "Very High"
        elif hdi_value >= 0.700:
            return "High"
        elif hdi_value >= 0.550:
            return "Medium"
        else:
            return "Low"
