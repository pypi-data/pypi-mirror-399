# ════════════════════════════════════════════════════════════════════════════════
# KRL Data Connectors - World Bank API Connector
# ════════════════════════════════════════════════════════════════════════════════
# Copyright (c) 2025 Khipu Research Labs. All rights reserved.
# Licensed under Apache-2.0

"""
World Bank Data API Connector.

Provides access to World Bank Open Data through the World Bank API v2.
Supports fetching indicators, country data, and time series for:
- Human Development indicators (education, health, living standards)
- Economic indicators (GDP, GNI, income distribution)
- Social indicators (poverty, inequality)
- Environmental indicators (emissions, resources)

API Documentation: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392

Note: The World Bank API is free and does not require an API key.
Rate limiting: 50 requests per second (generous).

Tier: COMMUNITY (no authentication required)
"""

from __future__ import annotations

import logging
from datetime import datetime, UTC
from typing import Any, Dict, List, Literal, Optional, Union

import pandas as pd

from krl_data_connectors.base_connector import BaseConnector

__all__ = ["WorldBankConnector", "WorldBankIndicator"]

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════════
# Common Indicator Codes
# ════════════════════════════════════════════════════════════════════════════════

class WorldBankIndicator:
    """
    Common World Bank indicator codes.
    
    Reference: https://data.worldbank.org/indicator
    """
    
    # Human Development
    LIFE_EXPECTANCY = "SP.DYN.LE00.IN"              # Life expectancy at birth
    EXPECTED_YEARS_SCHOOLING = "SE.SCH.LIFE"        # Expected years of schooling
    MEAN_YEARS_SCHOOLING = "SE.ADT.LITR.ZS"         # Adult literacy proxy
    GNI_PER_CAPITA_PPP = "NY.GNP.PCAP.PP.CD"        # GNI per capita, PPP
    GNI_PER_CAPITA_ATLAS = "NY.GNP.PCAP.CD"         # GNI per capita, Atlas method
    
    # Population
    POPULATION_TOTAL = "SP.POP.TOTL"                # Total population
    POPULATION_GROWTH = "SP.POP.GROW"               # Population growth (annual %)
    URBAN_POPULATION = "SP.URB.TOTL.IN.ZS"          # Urban population (% of total)
    
    # Economic
    GDP_CURRENT_USD = "NY.GDP.MKTP.CD"              # GDP (current US$)
    GDP_PER_CAPITA = "NY.GDP.PCAP.CD"               # GDP per capita (current US$)
    GDP_GROWTH = "NY.GDP.MKTP.KD.ZG"                # GDP growth (annual %)
    INFLATION_CPI = "FP.CPI.TOTL.ZG"                # Inflation, consumer prices (annual %)
    UNEMPLOYMENT = "SL.UEM.TOTL.ZS"                 # Unemployment (% of labor force)
    
    # Poverty & Inequality
    POVERTY_HEADCOUNT_190 = "SI.POV.DDAY"           # Poverty headcount at $1.90/day
    POVERTY_HEADCOUNT_320 = "SI.POV.LMIC"           # Poverty headcount at $3.20/day
    POVERTY_HEADCOUNT_550 = "SI.POV.UMIC"           # Poverty headcount at $5.50/day
    GINI_INDEX = "SI.POV.GINI"                      # Gini index
    INCOME_SHARE_BOTTOM_20 = "SI.DST.FRST.20"       # Income share (lowest 20%)
    INCOME_SHARE_TOP_10 = "SI.DST.10TH.10"          # Income share (highest 10%)
    
    # Health
    MORTALITY_UNDER5 = "SH.DYN.MORT"                # Mortality rate, under-5
    MORTALITY_INFANT = "SP.DYN.IMRT.IN"             # Mortality rate, infant
    MATERNAL_MORTALITY = "SH.STA.MMRT"              # Maternal mortality ratio
    PHYSICIANS = "SH.MED.PHYS.ZS"                   # Physicians (per 1,000 people)
    HOSPITAL_BEDS = "SH.MED.BEDS.ZS"                # Hospital beds (per 1,000 people)
    HEALTH_EXPENDITURE = "SH.XPD.CHEX.GD.ZS"        # Health expenditure (% GDP)
    
    # Education
    SCHOOL_ENROLLMENT_PRIMARY = "SE.PRM.ENRR"       # School enrollment, primary (% gross)
    SCHOOL_ENROLLMENT_SECONDARY = "SE.SEC.ENRR"     # School enrollment, secondary (% gross)
    SCHOOL_ENROLLMENT_TERTIARY = "SE.TER.ENRR"      # School enrollment, tertiary (% gross)
    LITERACY_RATE_ADULT = "SE.ADT.LITR.ZS"          # Literacy rate, adult total
    EDUCATION_EXPENDITURE = "SE.XPD.TOTL.GD.ZS"     # Education expenditure (% GDP)
    
    # Infrastructure & Living Standards
    ACCESS_ELECTRICITY = "EG.ELC.ACCS.ZS"           # Access to electricity (% population)
    ACCESS_WATER = "SH.H2O.BASW.ZS"                 # Access to basic water (% population)
    ACCESS_SANITATION = "SH.STA.BASS.ZS"            # Access to basic sanitation (% population)
    INTERNET_USERS = "IT.NET.USER.ZS"               # Internet users (% population)
    MOBILE_SUBSCRIPTIONS = "IT.CEL.SETS.P2"         # Mobile cellular subscriptions (per 100)
    
    # Environment
    CO2_EMISSIONS = "EN.ATM.CO2E.PC"                # CO2 emissions (metric tons per capita)
    FOREST_AREA = "AG.LND.FRST.ZS"                  # Forest area (% of land area)
    RENEWABLE_ENERGY = "EG.FEC.RNEW.ZS"             # Renewable energy consumption (%)

    @classmethod
    def hdi_indicators(cls) -> List[str]:
        """Return indicators needed for HDI calculation."""
        return [
            cls.LIFE_EXPECTANCY,
            cls.EXPECTED_YEARS_SCHOOLING,
            cls.MEAN_YEARS_SCHOOLING,
            cls.GNI_PER_CAPITA_PPP,
        ]
    
    @classmethod
    def mpi_indicators(cls) -> List[str]:
        """Return indicators relevant for MPI calculation."""
        return [
            cls.MORTALITY_UNDER5,
            cls.MORTALITY_INFANT,
            cls.SCHOOL_ENROLLMENT_PRIMARY,
            cls.SCHOOL_ENROLLMENT_SECONDARY,
            cls.ACCESS_ELECTRICITY,
            cls.ACCESS_WATER,
            cls.ACCESS_SANITATION,
        ]


# ════════════════════════════════════════════════════════════════════════════════
# World Bank Connector
# ════════════════════════════════════════════════════════════════════════════════


class WorldBankConnector(BaseConnector):
    """
    Connector for World Bank Open Data API.
    
    Provides access to 16,000+ development indicators covering:
    - Economic indicators (GDP, GNI, trade)
    - Social indicators (education, health, poverty)
    - Environmental indicators (emissions, resources)
    - Demographic indicators (population, labor)
    
    The World Bank API is free and does not require authentication.
    
    Example:
        >>> connector = WorldBankConnector()
        >>> connector.connect()
        >>> 
        >>> # Fetch single indicator for a country
        >>> data = connector.fetch_indicator(
        ...     indicator="SP.DYN.LE00.IN",  # Life expectancy
        ...     country="USA",
        ...     start_year=2000,
        ...     end_year=2023
        ... )
        >>> 
        >>> # Fetch multiple indicators for HDI calculation
        >>> hdi_data = connector.fetch_hdi_indicators(
        ...     countries=["USA", "CAN", "MEX"],
        ...     year=2022
        ... )
        >>> 
        >>> connector.disconnect()
    """
    
    BASE_URL = "https://api.worldbank.org/v2"
    
    def __init__(
        self,
        cache_ttl: int = 86400,  # 24 hours (World Bank data updates infrequently)
        timeout: int = 30,
        max_retries: int = 3,
        per_page: int = 500,
    ):
        """
        Initialize World Bank connector.
        
        Args:
            cache_ttl: Cache time-to-live in seconds (default: 24 hours).
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
            per_page: Number of records per page (max 500).
        """
        super().__init__(
            api_key=None,  # World Bank API is free, no key required
            cache_ttl=cache_ttl,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.per_page = min(per_page, 500)  # API max is 500
        self._connected = False
    
    def _get_api_key(self) -> Optional[str]:
        """World Bank API does not require authentication."""
        return None
    
    def connect(self) -> None:
        """
        Establish connection to World Bank API.
        
        Validates API availability by fetching basic metadata.
        """
        try:
            # Test API with a simple metadata request
            url = f"{self.BASE_URL}/sources?format=json"
            self._validate_url(url, allow_http=False)
            response = self._make_request(url, use_cache=True)
            
            if response:
                self._connected = True
                self.logger.info(
                    "Connected to World Bank API",
                    extra={"sources_available": len(response[1]) if len(response) > 1 else 0}
                )
            else:
                raise ConnectionError("Empty response from World Bank API")
                
        except Exception as e:
            self._connected = False
            self.logger.error("Failed to connect to World Bank API", exc_info=True)
            raise ConnectionError(f"World Bank API connection failed: {e}") from e
    
    def fetch(self, **kwargs: Any) -> Any:
        """
        Generic fetch method - routes to specific fetch methods.
        
        Args:
            **kwargs: Must include 'indicator' or 'method' key.
            
        Returns:
            Fetched data based on method.
        """
        if "indicator" in kwargs:
            return self.fetch_indicator(**kwargs)
        elif "method" in kwargs:
            method = kwargs.pop("method")
            if method == "countries":
                return self.fetch_countries(**kwargs)
            elif method == "indicators":
                return self.fetch_indicator_metadata(**kwargs)
            else:
                raise ValueError(f"Unknown method: {method}")
        else:
            raise ValueError("Must specify 'indicator' or 'method' parameter")
    
    def fetch_indicator(
        self,
        indicator: str,
        country: Union[str, List[str]] = "all",
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        mrv: Optional[int] = None,
        frequency: Literal["Y", "M", "Q"] = "Y",
        as_dataframe: bool = True,
    ) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Fetch indicator data for countries.
        
        Args:
            indicator: World Bank indicator code (e.g., "SP.DYN.LE00.IN").
            country: ISO 3166-1 alpha-3 code(s) or "all".
            start_year: Start year for time range filter.
            end_year: End year for time range filter.
            mrv: Most recent values (alternative to date range).
            frequency: Data frequency (Y=yearly, M=monthly, Q=quarterly).
            as_dataframe: Return pandas DataFrame (default True).
            
        Returns:
            DataFrame or list of records with indicator values.
            
        Raises:
            ValueError: If invalid parameters.
            ConnectionError: If API request fails.
        """
        if not self._connected:
            self.connect()
        
        # Validate indicator code
        self._validate_string_length(indicator, "indicator", max_length=100, min_length=1)
        
        # Build country string
        if isinstance(country, list):
            country_str = ";".join(country)
        else:
            country_str = country
        
        # Build date range
        date_param = ""
        if mrv:
            date_param = f"&mrv={mrv}"
        elif start_year and end_year:
            date_param = f"&date={start_year}:{end_year}"
        elif start_year:
            date_param = f"&date={start_year}:{datetime.now().year}"
        
        # Construct URL
        url = f"{self.BASE_URL}/country/{country_str}/indicator/{indicator}"
        self._validate_url(url, allow_http=False)
        
        params = {
            "format": "json",
            "per_page": self.per_page,
            "page": 1,
        }
        
        if date_param:
            # Parse date param into query params
            if "mrv=" in date_param:
                params["mrv"] = mrv
            elif "date=" in date_param:
                params["date"] = f"{start_year}:{end_year}" if end_year else f"{start_year}:{datetime.now().year}"
        
        # Fetch all pages
        all_data = []
        page = 1
        total_pages = 1
        
        while page <= total_pages:
            params["page"] = page
            response = self._make_request(url, params=params, use_cache=True)
            
            if not response or len(response) < 2:
                break
            
            metadata = response[0]
            data = response[1]
            
            if page == 1:
                total_pages = metadata.get("pages", 1)
                self.logger.debug(
                    "Fetching indicator",
                    extra={
                        "indicator": indicator,
                        "total_records": metadata.get("total", 0),
                        "pages": total_pages,
                    }
                )
            
            if data:
                all_data.extend(data)
            
            page += 1
        
        # Convert to DataFrame if requested
        if as_dataframe and all_data:
            df = self._to_dataframe(all_data)
            return df
        
        return all_data
    
    def fetch_multiple_indicators(
        self,
        indicators: List[str],
        country: Union[str, List[str]] = "all",
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        mrv: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Fetch multiple indicators and combine into a single DataFrame.
        
        Args:
            indicators: List of indicator codes.
            country: Country code(s).
            start_year: Start year.
            end_year: End year.
            mrv: Most recent values.
            
        Returns:
            DataFrame with columns for each indicator.
        """
        dfs = []
        
        for indicator in indicators:
            try:
                df = self.fetch_indicator(
                    indicator=indicator,
                    country=country,
                    start_year=start_year,
                    end_year=end_year,
                    mrv=mrv,
                    as_dataframe=True,
                )
                if isinstance(df, pd.DataFrame) and not df.empty:
                    # Rename value column to indicator name
                    df = df.rename(columns={"value": indicator})
                    dfs.append(df[["country_code", "country_name", "year", indicator]])
            except Exception as e:
                self.logger.warning(f"Failed to fetch indicator {indicator}: {e}")
                continue
        
        if not dfs:
            return pd.DataFrame()
        
        # Merge all DataFrames
        result = dfs[0]
        for df in dfs[1:]:
            result = result.merge(
                df,
                on=["country_code", "country_name", "year"],
                how="outer"
            )
        
        return result.sort_values(["country_code", "year"])
    
    def fetch_hdi_indicators(
        self,
        countries: Union[str, List[str]] = "all",
        year: Optional[int] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Fetch indicators needed for Human Development Index calculation.
        
        HDI Components:
        1. Life expectancy at birth
        2. Expected years of schooling
        3. Mean years of schooling (approximated by literacy rate)
        4. GNI per capita (PPP)
        
        Args:
            countries: Country code(s) or "all".
            year: Specific year (uses mrv=1 if not available).
            start_year: Start year for range.
            end_year: End year for range.
            
        Returns:
            DataFrame with HDI component indicators.
        """
        indicators = WorldBankIndicator.hdi_indicators()
        
        if year and not start_year:
            start_year = year
            end_year = year
        
        return self.fetch_multiple_indicators(
            indicators=indicators,
            country=countries,
            start_year=start_year,
            end_year=end_year,
            mrv=5 if not start_year else None,  # Get 5 most recent if no date range
        )
    
    def fetch_countries(
        self,
        region: Optional[str] = None,
        income_level: Optional[str] = None,
        as_dataframe: bool = True,
    ) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Fetch country metadata.
        
        Args:
            region: Filter by region code (e.g., "EAS", "LAC").
            income_level: Filter by income level (e.g., "HIC", "LIC").
            as_dataframe: Return as DataFrame.
            
        Returns:
            Country metadata.
        """
        if not self._connected:
            self.connect()
        
        url = f"{self.BASE_URL}/country"
        self._validate_url(url, allow_http=False)
        
        params = {
            "format": "json",
            "per_page": 300,  # There are ~217 countries
        }
        
        if region:
            params["region"] = region
        if income_level:
            params["incomeLevel"] = income_level
        
        response = self._make_request(url, params=params, use_cache=True)
        
        if not response or len(response) < 2:
            return pd.DataFrame() if as_dataframe else []
        
        data = response[1]
        
        if as_dataframe:
            records = []
            for c in data:
                records.append({
                    "country_code": c.get("id"),
                    "country_name": c.get("name"),
                    "region_code": c.get("region", {}).get("id"),
                    "region_name": c.get("region", {}).get("value"),
                    "income_level_code": c.get("incomeLevel", {}).get("id"),
                    "income_level_name": c.get("incomeLevel", {}).get("value"),
                    "capital_city": c.get("capitalCity"),
                    "longitude": c.get("longitude"),
                    "latitude": c.get("latitude"),
                })
            return pd.DataFrame(records)
        
        return data
    
    def fetch_indicator_metadata(
        self,
        indicator: Optional[str] = None,
        source: int = 2,  # 2 = World Development Indicators
    ) -> Dict[str, Any]:
        """
        Fetch metadata about an indicator.
        
        Args:
            indicator: Indicator code (if None, lists all indicators).
            source: Data source ID (default: 2 for WDI).
            
        Returns:
            Indicator metadata.
        """
        if not self._connected:
            self.connect()
        
        if indicator:
            url = f"{self.BASE_URL}/indicator/{indicator}"
        else:
            url = f"{self.BASE_URL}/source/{source}/indicator"
        
        self._validate_url(url, allow_http=False)
        
        params = {
            "format": "json",
            "per_page": 1000,
        }
        
        response = self._make_request(url, params=params, use_cache=True)
        
        if not response or len(response) < 2:
            return {}
        
        return response[1][0] if indicator else response[1]
    
    def _to_dataframe(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert API response to pandas DataFrame.
        
        Args:
            data: List of records from API.
            
        Returns:
            Cleaned DataFrame.
        """
        records = []
        
        for record in data:
            if record is None:
                continue
                
            country = record.get("country", {})
            indicator = record.get("indicator", {})
            
            records.append({
                "country_code": country.get("id"),
                "country_name": country.get("value"),
                "indicator_code": indicator.get("id"),
                "indicator_name": indicator.get("value"),
                "year": int(record.get("date")) if record.get("date") else None,
                "value": record.get("value"),
                "decimal": record.get("decimal"),
                "unit": record.get("unit"),
            })
        
        df = pd.DataFrame(records)
        
        # Convert value column to numeric
        if "value" in df.columns:
            df["value"] = pd.to_numeric(df["value"], errors="coerce")
        
        # Sort by country and year
        if "year" in df.columns and "country_code" in df.columns:
            df = df.sort_values(["country_code", "year"])
        
        return df
    
    def search_indicators(
        self,
        query: str,
        source: int = 2,
    ) -> pd.DataFrame:
        """
        Search for indicators by keyword.
        
        Args:
            query: Search query.
            source: Data source ID.
            
        Returns:
            DataFrame of matching indicators.
        """
        if not self._connected:
            self.connect()
        
        # Fetch all indicators and filter locally
        # (World Bank API doesn't have a search endpoint)
        all_indicators = self.fetch_indicator_metadata(source=source)
        
        if not all_indicators:
            return pd.DataFrame()
        
        # Filter by query
        query_lower = query.lower()
        matches = []
        
        for ind in all_indicators:
            name = ind.get("name", "").lower()
            source_note = ind.get("sourceNote", "").lower()
            
            if query_lower in name or query_lower in source_note:
                matches.append({
                    "indicator_code": ind.get("id"),
                    "name": ind.get("name"),
                    "source": ind.get("source", {}).get("value"),
                    "source_note": ind.get("sourceNote", "")[:200],  # Truncate
                })
        
        return pd.DataFrame(matches)
