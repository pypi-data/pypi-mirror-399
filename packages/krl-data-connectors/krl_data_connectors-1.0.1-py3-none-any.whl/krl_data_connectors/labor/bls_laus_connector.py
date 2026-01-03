# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
BLS LAUS Connector - Professional Tier

Access to Bureau of Labor Statistics Local Area Unemployment Statistics (LAUS).
Provides sub-national unemployment data at state, county, and metropolitan levels.

REMSOM v2 Integration:
    This connector provides labor market data for the INCOME and LABOR_MARKET
    opportunity domains in the REMSOM observatory architecture.

API Documentation:
    https://www.bls.gov/lau/

Available Data:
- State-level unemployment rates and employment levels
- County-level unemployment rates (monthly)
- Metropolitan statistical area (MSA) unemployment
- Labor force participation rates

Usage:
    from krl_data_connectors.labor import BLSLAUSConnector
    
    laus = BLSLAUSConnector(api_key="your_bls_key")
    
    # Get state unemployment rates
    state_data = laus.get_state_unemployment(state_fips="06")
    
    # Get county-level data
    county_data = laus.get_county_unemployment(
        state_fips="06", 
        county_fips="037"  # Los Angeles
    )
    
    # Get MSA data
    msa_data = laus.get_msa_unemployment(msa_code="31080")  # LA-Long Beach
"""

from datetime import datetime, UTC
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from krl_data_connectors import BaseConnector
from krl_data_connectors.core import DataTier


class BLSLAUSConnector(BaseConnector):
    """
    BLS LAUS Connector - Professional Tier
    
    Access to Local Area Unemployment Statistics for sub-national
    labor market analysis. Requires BLS API key for v2 API access.
    
    LAUS Program:
        The Local Area Unemployment Statistics program produces monthly
        and annual employment, unemployment, and labor force data for
        Census regions and divisions, States, counties, metropolitan
        areas, and many cities.
    
    Series ID Format:
        LAUS{area_code}{measure_code}
        
        Area codes:
        - ST{fips}00000000000: State (e.g., ST0600000000000 for CA)
        - CN{state_fips}{county_fips}00000000: County
        - MT{msa_code}00000000000: Metropolitan area
        
        Measure codes:
        - 03: Unemployment rate
        - 04: Unemployment level
        - 05: Employment level
        - 06: Labor force level
    """
    
    _connector_name = "BLS_LAUS"
    _required_tier = DataTier.PROFESSIONAL
    
    BASE_URL_V2 = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    
    # Measure codes
    MEASURES = {
        "unemployment_rate": "03",
        "unemployment_level": "04",
        "employment_level": "05",
        "labor_force": "06",
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 3600,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize BLS LAUS connector.
        
        Args:
            api_key: BLS API key (required for v2 API access)
            cache_dir: Directory for caching responses
            cache_ttl: Cache time-to-live in seconds
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        super().__init__(
            api_key=api_key,
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.base_url = self.BASE_URL_V2
        self.logger.info(
            "Initialized BLS LAUS connector (Professional tier)",
            extra={"has_api_key": bool(self.api_key)},
        )
    
    def _get_api_key(self) -> Optional[str]:
        """
        Get BLS API key from configuration.
        
        Returns:
            BLS API key or None
        """
        return self.config.get("BLS_API_KEY")
    
    def connect(self) -> bool:
        """
        Test connection to BLS LAUS API.
        
        Returns:
            True if connection successful
        """
        try:
            self._init_session()
            
            # Test with California state unemployment
            series_id = self._build_state_series_id("06", "unemployment_rate")
            year = datetime.now().year
            
            payload = {
                "seriesid": [series_id],
                "startyear": str(year - 1),
                "endyear": str(year),
                "registrationkey": self.api_key,
            }
            
            response = self.session.post(
                self.base_url, json=payload, timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("status") == "REQUEST_SUCCEEDED":
                self.logger.info("Successfully connected to BLS LAUS API")
                return True
            else:
                self.logger.warning(
                    f"BLS LAUS API returned status: {data.get('status')}"
                )
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to connect to BLS LAUS API: {str(e)}")
            return False
    
    def fetch(
        self,
        series_ids: List[str],
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Fetch LAUS data for specified series.
        
        Args:
            series_ids: List of BLS series IDs
            start_year: Start year for data
            end_year: End year for data
        
        Returns:
            DataFrame with LAUS data
        """
        end_year = end_year or datetime.now().year
        start_year = start_year or (end_year - 10)
        
        cache_key = f"laus_{'-'.join(series_ids)}_{start_year}_{end_year}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            self.logger.debug(f"Cache hit for {cache_key}")
            return pd.DataFrame(cached)
        
        self._init_session()
        
        # BLS API limits to 50 series per request
        all_data = []
        for i in range(0, len(series_ids), 50):
            batch = series_ids[i:i + 50]
            
            payload = {
                "seriesid": batch,
                "startyear": str(start_year),
                "endyear": str(end_year),
            }
            if self.api_key:
                payload["registrationkey"] = self.api_key
            
            response = self.session.post(
                self.base_url, json=payload, timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("status") != "REQUEST_SUCCEEDED":
                raise ValueError(f"BLS API error: {result.get('message', 'Unknown')}")
            
            for series in result.get("Results", {}).get("series", []):
                series_id = series["seriesID"]
                for obs in series.get("data", []):
                    all_data.append({
                        "series_id": series_id,
                        "year": int(obs["year"]),
                        "period": obs["period"],
                        "value": float(obs["value"]),
                        "footnotes": obs.get("footnotes", []),
                    })
        
        df = pd.DataFrame(all_data)
        self.cache.set(cache_key, df.to_dict("records"))
        return df
    
    def _build_state_series_id(
        self,
        state_fips: str,
        measure: str = "unemployment_rate",
    ) -> str:
        """Build LAUS series ID for a state."""
        measure_code = self.MEASURES.get(measure, "03")
        return f"LASST{state_fips.zfill(2)}0000000000{measure_code}"
    
    def _build_county_series_id(
        self,
        state_fips: str,
        county_fips: str,
        measure: str = "unemployment_rate",
    ) -> str:
        """Build LAUS series ID for a county."""
        measure_code = self.MEASURES.get(measure, "03")
        return f"LAUCN{state_fips.zfill(2)}{county_fips.zfill(3)}0000000{measure_code}"
    
    def _build_msa_series_id(
        self,
        msa_code: str,
        measure: str = "unemployment_rate",
    ) -> str:
        """Build LAUS series ID for a metropolitan statistical area."""
        measure_code = self.MEASURES.get(measure, "03")
        return f"LAUMT{msa_code.zfill(5)}00000000{measure_code}"
    
    def get_state_unemployment(
        self,
        state_fips: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        measures: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Get unemployment data for a state.
        
        Args:
            state_fips: 2-digit state FIPS code (e.g., "06" for California)
            start_year: Start year for data
            end_year: End year for data
            measures: List of measures to fetch (default: all)
        
        Returns:
            DataFrame with state unemployment data
        """
        measures = measures or list(self.MEASURES.keys())
        series_ids = [
            self._build_state_series_id(state_fips, m) for m in measures
        ]
        
        df = self.fetch(series_ids, start_year, end_year)
        
        # Add metadata
        df["state_fips"] = state_fips
        df["geography_level"] = "state"
        
        # Pivot measures into columns
        if not df.empty:
            df["measure"] = df["series_id"].apply(
                lambda x: next(
                    (k for k, v in self.MEASURES.items() if x.endswith(v)),
                    "unknown"
                )
            )
        
        return df
    
    def get_county_unemployment(
        self,
        state_fips: str,
        county_fips: Optional[str] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Get unemployment data for county/counties.
        
        Args:
            state_fips: 2-digit state FIPS code
            county_fips: 3-digit county FIPS code (if None, gets all counties)
            start_year: Start year
            end_year: End year
        
        Returns:
            DataFrame with county unemployment data
        """
        if county_fips:
            series_ids = [
                self._build_county_series_id(state_fips, county_fips, m)
                for m in self.MEASURES.keys()
            ]
        else:
            # Would need county FIPS list - simplified for single county
            raise ValueError(
                "Full state county fetch requires county FIPS list. "
                "Use get_all_counties_in_state() instead."
            )
        
        df = self.fetch(series_ids, start_year, end_year)
        df["state_fips"] = state_fips
        df["county_fips"] = county_fips
        df["geography_level"] = "county"
        
        return df
    
    def get_msa_unemployment(
        self,
        msa_code: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Get unemployment data for a Metropolitan Statistical Area.
        
        Args:
            msa_code: 5-digit MSA code
            start_year: Start year
            end_year: End year
        
        Returns:
            DataFrame with MSA unemployment data
        """
        series_ids = [
            self._build_msa_series_id(msa_code, m) for m in self.MEASURES.keys()
        ]
        
        df = self.fetch(series_ids, start_year, end_year)
        df["msa_code"] = msa_code
        df["geography_level"] = "msa"
        
        return df
    
    def get_all_states_unemployment(
        self,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Get unemployment rates for all 50 states + DC.
        
        Args:
            start_year: Start year
            end_year: End year
        
        Returns:
            DataFrame with all states' unemployment data
        """
        # State FIPS codes (50 states + DC)
        state_fips_list = [
            "01", "02", "04", "05", "06", "08", "09", "10", "11", "12",
            "13", "15", "16", "17", "18", "19", "20", "21", "22", "23",
            "24", "25", "26", "27", "28", "29", "30", "31", "32", "33",
            "34", "35", "36", "37", "38", "39", "40", "41", "42", "44",
            "45", "46", "47", "48", "49", "50", "51", "53", "54", "55", "56",
        ]
        
        series_ids = [
            self._build_state_series_id(fips, "unemployment_rate")
            for fips in state_fips_list
        ]
        
        df = self.fetch(series_ids, start_year, end_year)
        
        # Extract state FIPS from series ID
        df["state_fips"] = df["series_id"].str[5:7]
        df["geography_level"] = "state"
        df["measure"] = "unemployment_rate"
        
        return df
    
    def to_remsom_bundle_format(
        self,
        df: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Convert LAUS data to REMSOM DataBundle format.
        
        Args:
            df: DataFrame from LAUS fetch
        
        Returns:
            Dict ready for DataBundle.from_dict()
        """
        # Pivot to wide format by year/geography
        if "measure" not in df.columns:
            df["measure"] = "unemployment_rate"
        
        # Annual averages (filter to annual period M13 or calculate)
        annual = df[df["period"] == "M13"].copy() if "M13" in df["period"].values else (
            df.groupby(["state_fips", "year", "measure"])["value"]
            .mean()
            .reset_index()
        )
        
        return {
            "labor": {
                "data": annual,
                "metadata": {
                    "source": "BLS LAUS",
                    "connector": "BLSLAUSConnector",
                    "fetch_time": datetime.now().isoformat(),
                },
            },
        }
