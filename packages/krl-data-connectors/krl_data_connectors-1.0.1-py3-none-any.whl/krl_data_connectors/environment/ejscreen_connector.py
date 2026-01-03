# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
EPA EJSCREEN (Environmental Justice Screening) Data Connector.

This connector provides access to EPA's EJSCREEN environmental justice
mapping and screening tool data. EJSCREEN combines environmental and
demographic indicators at the Census block group level to help identify
communities with potential environmental justice concerns.

Key Features:
- Block group level environmental indicator data
- Demographic indicator data
- EJ index calculations
- Facility proximity metrics
- Geographic queries (point-in-polygon, buffer analysis)
- Historical EJSCREEN versions (2019-2024)

Data Categories:
- Environmental Indicators: PM2.5, Ozone, Diesel PM, Air Toxics, etc.
- Demographic Indicators: Minority %, Low Income %, Linguistic Isolation, etc.
- EJ Indexes: Combined environmental + demographic scores
- Supplemental Indexes: Flood risk, wildfire risk, lack of greenspace, etc.

API Endpoints:
- EJSCREEN Map Services (ArcGIS REST)
- EJSCREEN Data Download (CSV/Shapefile)
- EJSCREEN Web Services

Usage:
    >>> from krl_data_connectors.environment import EJScreenConnector
    >>>
    >>> # Initialize connector
    >>> ej = EJScreenConnector()
    >>>
    >>> # Get EJ data for a location
    >>> data = ej.get_ejscreen_data(lat=33.7490, lon=-84.3880)
    >>>
    >>> # Get data for a Census block group
    >>> data = ej.get_block_group_data(geoid="131210024001")
    >>>
    >>> # Get all block groups in a county
    >>> gdf = ej.get_county_data(state_fips="13", county_fips="121")
    >>>
    >>> # Buffer analysis around a facility
    >>> gdf = ej.get_buffer_data(lat=33.7490, lon=-84.3880, distance_miles=3)

References:
    - EJSCREEN: https://www.epa.gov/ejscreen
    - Technical Documentation: https://www.epa.gov/ejscreen/technical-documentation-ejscreen
    - Data Dictionary: https://www.epa.gov/ejscreen/ejscreen-map-descriptions
    - API Services: https://ejscreen.epa.gov/mapper/
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlencode

import geopandas as gpd
import numpy as np
import pandas as pd
import requests
from shapely.geometry import Point, Polygon, box, mapping
from shapely.ops import transform

try:
    from krl_data_connectors.base_connector import BaseConnector
    from krl_data_connectors.core.rate_limiter import (
        ExponentialBackoff,
        RateLimiter,
        SlidingWindowCounter,
        TokenBucket,
    )
except ImportError:
    BaseConnector = object
    RateLimiter = None

try:
    from krl_core import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS AND CONFIGURATION
# =============================================================================

# EJSCREEN API Base URLs
EJSCREEN_API_BASE = "https://ejscreen.epa.gov/mapper/ejscreenRESTbroker.aspx"
EJSCREEN_ARCGIS_BASE = "https://geodata.epa.gov/arcgis/rest/services/OEI/EJSCREEN_"
EJSCREEN_DOWNLOAD_BASE = "https://gaftp.epa.gov/EJSCREEN/"

# Current EJSCREEN version
EJSCREEN_VERSION = "2024"
AVAILABLE_VERSIONS = ["2019", "2020", "2021", "2022", "2023", "2024"]

# Rate limits for EPA services (conservative estimates)
EPA_RATE_LIMITS = {
    "requests_per_minute": 60,
    "requests_per_day": 10000,
    "max_concurrent": 5,
}


class EJIndicator(Enum):
    """Environmental and demographic indicators available in EJSCREEN."""
    
    # Environmental Indicators
    PM25 = "pm25"  # Particulate Matter 2.5
    OZONE = "ozone"  # Ozone concentration
    DIESEL_PM = "dpm"  # Diesel particulate matter
    AIR_TOXICS_CANCER = "cancer"  # Air toxics cancer risk
    AIR_TOXICS_RESPIRATORY = "resp"  # Air toxics respiratory hazard
    TRAFFIC_PROXIMITY = "traffic"  # Traffic proximity and volume
    LEAD_PAINT = "lead"  # Lead paint indicator
    SUPERFUND_PROXIMITY = "npl"  # Proximity to NPL sites
    RMP_PROXIMITY = "rmp"  # Proximity to RMP facilities
    TSDF_PROXIMITY = "tsdf"  # Proximity to hazardous waste sites
    WASTEWATER = "pwdis"  # Wastewater discharge indicator
    UNDERGROUND_TANKS = "ust"  # Underground storage tanks
    
    # Demographic Indicators
    MINORITY_PCT = "minorpct"  # Minority percentage
    LOW_INCOME_PCT = "lowincpct"  # Low income percentage
    LESS_HS_EDUCATION = "lesshs"  # Less than high school education
    LINGUISTIC_ISOLATION = "lingiso"  # Linguistic isolation
    UNDER5_PCT = "under5"  # Under 5 years old percentage
    OVER64_PCT = "over64"  # Over 64 years old percentage
    
    # Supplemental Indicators (2024+)
    LACK_GREEN_SPACE = "noglspc"  # Lack of green space
    LACK_TREE_COVER = "notrees"  # Lack of tree cover  
    IMPERVIOUS_SURFACE = "impsurf"  # Impervious surface percentage
    FLOOD_RISK = "flood"  # Flood risk
    WILDFIRE_RISK = "wildfire"  # Wildfire risk
    EXTREME_HEAT = "heat"  # Extreme heat index


class EJIndex(Enum):
    """Environmental Justice index types."""
    
    # Standard EJ Indexes (Environmental + Demographic)
    EJ_PM25 = "ej_pm25"
    EJ_OZONE = "ej_ozone"
    EJ_DIESEL = "ej_dpm"
    EJ_AIR_TOXICS_CANCER = "ej_cancer"
    EJ_AIR_TOXICS_RESP = "ej_resp"
    EJ_TRAFFIC = "ej_traffic"
    EJ_LEAD_PAINT = "ej_lead"
    EJ_SUPERFUND = "ej_npl"
    EJ_RMP = "ej_rmp"
    EJ_TSDF = "ej_tsdf"
    EJ_WASTEWATER = "ej_pwdis"
    EJ_UST = "ej_ust"
    
    # Supplemental EJ Indexes
    EJ_GREEN_SPACE = "ej_noglspc"
    EJ_FLOOD = "ej_flood"
    EJ_WILDFIRE = "ej_wildfire"
    EJ_HEAT = "ej_heat"


@dataclass
class EJScreenData:
    """Container for EJSCREEN data at a location or block group."""
    
    # Geographic identifiers
    geoid: str  # Census block group GEOID
    state_fips: str
    county_fips: str
    tract_fips: str
    blockgroup: str
    
    # Location
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Environmental indicators (values)
    pm25: Optional[float] = None
    ozone: Optional[float] = None
    diesel_pm: Optional[float] = None
    air_toxics_cancer: Optional[float] = None
    air_toxics_respiratory: Optional[float] = None
    traffic_proximity: Optional[float] = None
    lead_paint: Optional[float] = None
    superfund_proximity: Optional[float] = None
    rmp_proximity: Optional[float] = None
    tsdf_proximity: Optional[float] = None
    wastewater: Optional[float] = None
    underground_tanks: Optional[float] = None
    
    # Environmental indicators (percentiles)
    pm25_pctile: Optional[float] = None
    ozone_pctile: Optional[float] = None
    diesel_pm_pctile: Optional[float] = None
    air_toxics_cancer_pctile: Optional[float] = None
    air_toxics_respiratory_pctile: Optional[float] = None
    traffic_proximity_pctile: Optional[float] = None
    lead_paint_pctile: Optional[float] = None
    superfund_proximity_pctile: Optional[float] = None
    rmp_proximity_pctile: Optional[float] = None
    tsdf_proximity_pctile: Optional[float] = None
    wastewater_pctile: Optional[float] = None
    underground_tanks_pctile: Optional[float] = None
    
    # Demographic indicators
    total_population: Optional[int] = None
    minority_pct: Optional[float] = None
    low_income_pct: Optional[float] = None
    less_hs_education: Optional[float] = None
    linguistic_isolation: Optional[float] = None
    under5_pct: Optional[float] = None
    over64_pct: Optional[float] = None
    
    # EJ Indexes (combined scores)
    ej_indexes: Dict[str, float] = field(default_factory=dict)
    
    # Supplemental indicators
    supplemental: Dict[str, float] = field(default_factory=dict)
    
    # Metadata
    ejscreen_version: str = EJSCREEN_VERSION
    data_year: Optional[int] = None
    retrieved_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "geoid": self.geoid,
            "state_fips": self.state_fips,
            "county_fips": self.county_fips,
            "tract_fips": self.tract_fips,
            "blockgroup": self.blockgroup,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "pm25": self.pm25,
            "ozone": self.ozone,
            "diesel_pm": self.diesel_pm,
            "air_toxics_cancer": self.air_toxics_cancer,
            "air_toxics_respiratory": self.air_toxics_respiratory,
            "traffic_proximity": self.traffic_proximity,
            "lead_paint": self.lead_paint,
            "superfund_proximity": self.superfund_proximity,
            "rmp_proximity": self.rmp_proximity,
            "tsdf_proximity": self.tsdf_proximity,
            "wastewater": self.wastewater,
            "underground_tanks": self.underground_tanks,
            "pm25_pctile": self.pm25_pctile,
            "ozone_pctile": self.ozone_pctile,
            "diesel_pm_pctile": self.diesel_pm_pctile,
            "total_population": self.total_population,
            "minority_pct": self.minority_pct,
            "low_income_pct": self.low_income_pct,
            "less_hs_education": self.less_hs_education,
            "linguistic_isolation": self.linguistic_isolation,
            "under5_pct": self.under5_pct,
            "over64_pct": self.over64_pct,
            "ej_indexes": self.ej_indexes,
            "supplemental": self.supplemental,
            "ejscreen_version": self.ejscreen_version,
            "data_year": self.data_year,
            "retrieved_at": self.retrieved_at.isoformat() if self.retrieved_at else None,
        }


class EJScreenConnector:
    """
    Connector for EPA EJSCREEN environmental justice data.
    
    Provides access to environmental and demographic indicators at the
    Census block group level, along with EJ index calculations.
    
    Attributes:
        version: EJSCREEN data version (default: 2024)
        cache_dir: Directory for caching downloaded data
        rate_limiter: Rate limiter for API requests
    
    Example:
        >>> ej = EJScreenConnector()
        >>> 
        >>> # Get data for a specific location
        >>> data = ej.get_ejscreen_data(lat=33.7490, lon=-84.3880)
        >>> print(f"PM2.5 percentile: {data.pm25_pctile}")
        >>> 
        >>> # Get county-level GeoDataFrame
        >>> gdf = ej.get_county_data(state_fips="13", county_fips="121")
        >>> print(f"Block groups: {len(gdf)}")
    """
    
    def __init__(
        self,
        version: str = EJSCREEN_VERSION,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 86400,  # 24 hours
        timeout: int = 60,
        max_retries: int = 3,
    ):
        """
        Initialize EJSCREEN connector.
        
        Args:
            version: EJSCREEN data version (2019-2024)
            cache_dir: Directory for cached data
            cache_ttl: Cache time-to-live in seconds
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        if version not in AVAILABLE_VERSIONS:
            raise ValueError(f"Invalid version: {version}. Available: {AVAILABLE_VERSIONS}")
        
        self.version = version
        self.cache_ttl = cache_ttl
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Initialize cache directory
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / ".krl_cache" / "ejscreen"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize HTTP session
        self.session = self._init_session()
        
        # Initialize rate limiter
        self._rate_limiter = TokenBucket(
            capacity=EPA_RATE_LIMITS["requests_per_minute"],
            refill_rate=EPA_RATE_LIMITS["requests_per_minute"] / 60,
        ) if TokenBucket else None
        
        # Cache for downloaded data files
        self._data_cache: Dict[str, gpd.GeoDataFrame] = {}
        
        logger.info(f"EJScreenConnector initialized: version={version}")
    
    def _init_session(self) -> requests.Session:
        """Initialize HTTP session with retry logic."""
        session = requests.Session()
        
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set user agent
        session.headers.update({
            "User-Agent": "KRL-DataConnectors/1.0 (Environmental Research)",
        })
        
        return session
    
    def _rate_limit_wait(self) -> None:
        """Wait for rate limit if necessary."""
        if self._rate_limiter:
            self._rate_limiter.acquire()
    
    def _get_cache_key(self, *args) -> str:
        """Generate cache key from arguments."""
        key_str = "_".join(str(a) for a in args)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cached_data(self, cache_key: str) -> Optional[Any]:
        """Get data from cache if not expired."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if datetime.now() - mtime < timedelta(seconds=self.cache_ttl):
                with open(cache_file, "r") as f:
                    return json.load(f)
        return None
    
    def _save_to_cache(self, cache_key: str, data: Any) -> None:
        """Save data to cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        with open(cache_file, "w") as f:
            json.dump(data, f)
    
    # =========================================================================
    # POINT QUERY METHODS
    # =========================================================================
    
    def get_ejscreen_data(
        self,
        lat: float,
        lon: float,
        include_supplemental: bool = True,
    ) -> EJScreenData:
        """
        Get EJSCREEN data for a specific latitude/longitude point.
        
        Uses EPA's EJSCREEN REST broker to identify the Census block group
        containing the point and retrieve all environmental/demographic indicators.
        
        Args:
            lat: Latitude (decimal degrees)
            lon: Longitude (decimal degrees)
            include_supplemental: Include supplemental indicators (2024+)
        
        Returns:
            EJScreenData object with all indicators
        
        Raises:
            ValueError: If coordinates are invalid
            requests.RequestException: If API request fails
        
        Example:
            >>> data = ej.get_ejscreen_data(lat=33.7490, lon=-84.3880)
            >>> print(f"Block group: {data.geoid}")
            >>> print(f"PM2.5: {data.pm25} (percentile: {data.pm25_pctile})")
            >>> print(f"Minority %: {data.minority_pct}")
        """
        # Validate coordinates
        if not -90 <= lat <= 90:
            raise ValueError(f"Invalid latitude: {lat}")
        if not -180 <= lon <= 180:
            raise ValueError(f"Invalid longitude: {lon}")
        
        # Check cache
        cache_key = self._get_cache_key("point", lat, lon, self.version)
        cached = self._get_cached_data(cache_key)
        if cached:
            logger.debug(f"Cache hit for point ({lat}, {lon})")
            return self._parse_ejscreen_response(cached, lat, lon)
        
        # Rate limit
        self._rate_limit_wait()
        
        # Query EJSCREEN REST API
        params = {
            "latitude": lat,
            "longitude": lon,
            "namestr": "",
            "geometry": "",
            "distance": "0",
            "unit": "9035",
            "aession": "",
            "f": "json",
        }
        
        try:
            response = self.session.get(
                EJSCREEN_API_BASE,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            
            # Cache response
            self._save_to_cache(cache_key, data)
            
            return self._parse_ejscreen_response(data, lat, lon)
            
        except requests.RequestException as e:
            logger.error(f"EJSCREEN API request failed: {e}")
            raise
    
    def _parse_ejscreen_response(
        self,
        data: Dict[str, Any],
        lat: float,
        lon: float,
    ) -> EJScreenData:
        """Parse EJSCREEN API response into EJScreenData object."""
        # Extract raw data - handle different response formats
        if isinstance(data, dict):
            raw = data.get("RAW_DATA", data)
            if isinstance(raw, list) and len(raw) > 0:
                raw = raw[0]
        else:
            raw = {}
        
        # Parse geographic identifiers
        geoid = str(raw.get("ID", raw.get("GEOID", raw.get("blockgroup", ""))))
        if len(geoid) >= 12:
            state_fips = geoid[:2]
            county_fips = geoid[2:5]
            tract_fips = geoid[5:11]
            blockgroup = geoid[11:12] if len(geoid) > 11 else ""
        else:
            state_fips = raw.get("STATE_NAME", "")[:2] if raw.get("STATE_NAME") else ""
            county_fips = raw.get("CNTY_NAME", "")[:3] if raw.get("CNTY_NAME") else ""
            tract_fips = ""
            blockgroup = ""
        
        # Parse environmental indicators
        def safe_float(key: str, default: Optional[float] = None) -> Optional[float]:
            val = raw.get(key)
            if val is not None:
                try:
                    return float(val)
                except (ValueError, TypeError):
                    pass
            return default
        
        # Create EJScreenData object
        ejdata = EJScreenData(
            geoid=geoid,
            state_fips=state_fips,
            county_fips=county_fips,
            tract_fips=tract_fips,
            blockgroup=blockgroup,
            latitude=lat,
            longitude=lon,
            
            # Environmental indicators (values)
            pm25=safe_float("PM25"),
            ozone=safe_float("OZONE"),
            diesel_pm=safe_float("DSLPM"),
            air_toxics_cancer=safe_float("CANCER"),
            air_toxics_respiratory=safe_float("RESP"),
            traffic_proximity=safe_float("PTRAF"),
            lead_paint=safe_float("PNPL") or safe_float("PLEAD"),
            superfund_proximity=safe_float("PNPL"),
            rmp_proximity=safe_float("PRMP"),
            tsdf_proximity=safe_float("PTSDF"),
            wastewater=safe_float("PWDIS"),
            underground_tanks=safe_float("UST"),
            
            # Environmental indicators (percentiles)
            pm25_pctile=safe_float("P_PM25") or safe_float("P_PM25_PER"),
            ozone_pctile=safe_float("P_OZONE") or safe_float("P_OZONE_PER"),
            diesel_pm_pctile=safe_float("P_DSLPM") or safe_float("P_DIESEL_PER"),
            air_toxics_cancer_pctile=safe_float("P_CANCER") or safe_float("P_CANCER_PER"),
            air_toxics_respiratory_pctile=safe_float("P_RESP") or safe_float("P_RESP_PER"),
            traffic_proximity_pctile=safe_float("P_PTRAF") or safe_float("P_TRAFFIC_PER"),
            lead_paint_pctile=safe_float("P_PLEAD") or safe_float("P_LEAD_PER"),
            superfund_proximity_pctile=safe_float("P_PNPL") or safe_float("P_NPL_PER"),
            rmp_proximity_pctile=safe_float("P_PRMP") or safe_float("P_RMP_PER"),
            tsdf_proximity_pctile=safe_float("P_PTSDF") or safe_float("P_TSDF_PER"),
            wastewater_pctile=safe_float("P_PWDIS") or safe_float("P_WATER_PER"),
            underground_tanks_pctile=safe_float("P_UST"),
            
            # Demographic indicators
            total_population=int(safe_float("ACSTOTPOP", 0) or 0),
            minority_pct=safe_float("MINORPCT") or safe_float("PEOPCOLOR_PCT"),
            low_income_pct=safe_float("LOWINCPCT") or safe_float("LOWINCOME_PCT"),
            less_hs_education=safe_float("LESSHSPCT") or safe_float("LESSHS_PCT"),
            linguistic_isolation=safe_float("LINGISOPCT") or safe_float("LINGISO_PCT"),
            under5_pct=safe_float("UNDER5PCT") or safe_float("UNDER5_PCT"),
            over64_pct=safe_float("OVER64PCT") or safe_float("OVER64_PCT"),
            
            # Metadata
            ejscreen_version=self.version,
            data_year=int(self.version),
            retrieved_at=datetime.now(),
        )
        
        # Parse EJ indexes
        ej_prefixes = [
            ("D2_PM25", "ej_pm25"),
            ("D2_OZONE", "ej_ozone"),
            ("D2_DSLPM", "ej_diesel"),
            ("D2_CANCER", "ej_cancer"),
            ("D2_RESP", "ej_resp"),
            ("D2_PTRAF", "ej_traffic"),
            ("D2_PNPL", "ej_superfund"),
            ("D2_PRMP", "ej_rmp"),
            ("D2_PTSDF", "ej_tsdf"),
            ("D2_PWDIS", "ej_wastewater"),
        ]
        for api_key, index_name in ej_prefixes:
            val = safe_float(api_key)
            if val is not None:
                ejdata.ej_indexes[index_name] = val
        
        # Parse supplemental indicators (2024+)
        if self.version >= "2024":
            supplemental_keys = [
                ("NOGLSPC", "lack_green_space"),
                ("NOTREES", "lack_tree_cover"),
                ("IMPSURF", "impervious_surface"),
                ("FLOOD", "flood_risk"),
                ("WILDFIRE", "wildfire_risk"),
                ("HEAT", "extreme_heat"),
            ]
            for api_key, indicator_name in supplemental_keys:
                val = safe_float(api_key)
                if val is not None:
                    ejdata.supplemental[indicator_name] = val
        
        return ejdata
    
    # =========================================================================
    # BLOCK GROUP METHODS
    # =========================================================================
    
    def get_block_group_data(self, geoid: str) -> EJScreenData:
        """
        Get EJSCREEN data for a specific Census block group.
        
        Args:
            geoid: 12-digit Census block group GEOID (SSCCCTTTTTTB)
                   SS = State FIPS, CCC = County FIPS, TTTTTT = Tract, B = Block Group
        
        Returns:
            EJScreenData object with all indicators
        
        Example:
            >>> data = ej.get_block_group_data("131210024001")
            >>> print(f"PM2.5 percentile: {data.pm25_pctile}")
        """
        if len(geoid) != 12:
            raise ValueError(f"Invalid GEOID length: {len(geoid)}. Expected 12 characters.")
        
        # Parse GEOID components
        state_fips = geoid[:2]
        county_fips = geoid[2:5]
        tract_fips = geoid[5:11]
        blockgroup = geoid[11:12]
        
        # Check cache
        cache_key = self._get_cache_key("bg", geoid, self.version)
        cached = self._get_cached_data(cache_key)
        if cached:
            return self._parse_ejscreen_response(cached, None, None)
        
        # Try to get data from county-level file
        county_gdf = self.get_county_data(state_fips, county_fips)
        
        # Find block group in county data
        bg_data = county_gdf[county_gdf["ID"] == geoid]
        
        if len(bg_data) == 0:
            raise ValueError(f"Block group not found: {geoid}")
        
        # Convert row to EJScreenData
        row = bg_data.iloc[0].to_dict()
        self._save_to_cache(cache_key, row)
        
        return self._parse_ejscreen_response(row, None, None)
    
    # =========================================================================
    # GEOGRAPHIC AREA METHODS
    # =========================================================================
    
    def get_county_data(
        self,
        state_fips: str,
        county_fips: str,
    ) -> gpd.GeoDataFrame:
        """
        Get EJSCREEN data for all block groups in a county.
        
        Downloads state-level EJSCREEN data and filters to the specified county.
        Data is cached for subsequent queries.
        
        Args:
            state_fips: 2-digit state FIPS code
            county_fips: 3-digit county FIPS code
        
        Returns:
            GeoDataFrame with all block groups in the county
        
        Example:
            >>> gdf = ej.get_county_data(state_fips="13", county_fips="121")
            >>> print(f"Block groups: {len(gdf)}")
            >>> print(f"Mean PM2.5 percentile: {gdf['P_PM25'].mean():.1f}")
        """
        # Get state data (handles caching internally)
        state_gdf = self.get_state_data(state_fips)
        
        # Filter to county
        county_mask = state_gdf["ID"].str[2:5] == county_fips
        county_gdf = state_gdf[county_mask].copy()
        
        logger.info(f"Retrieved {len(county_gdf)} block groups for county {state_fips}{county_fips}")
        
        return county_gdf
    
    def get_state_data(self, state_fips: str) -> gpd.GeoDataFrame:
        """
        Get EJSCREEN data for all block groups in a state.
        
        Downloads and caches state-level EJSCREEN geodatabase files.
        
        Args:
            state_fips: 2-digit state FIPS code
        
        Returns:
            GeoDataFrame with all block groups in the state
        
        Example:
            >>> gdf = ej.get_state_data("13")  # Georgia
            >>> print(f"Block groups: {len(gdf)}")
        """
        cache_key = f"state_{state_fips}_{self.version}"
        
        # Check memory cache
        if cache_key in self._data_cache:
            return self._data_cache[cache_key]
        
        # Check file cache
        cache_file = self.cache_dir / f"{cache_key}.parquet"
        if cache_file.exists():
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if datetime.now() - mtime < timedelta(seconds=self.cache_ttl * 7):  # Week cache for files
                gdf = gpd.read_parquet(cache_file)
                self._data_cache[cache_key] = gdf
                logger.debug(f"Loaded state {state_fips} from cache")
                return gdf
        
        # Download state data
        logger.info(f"Downloading EJSCREEN data for state {state_fips}...")
        gdf = self._download_state_data(state_fips)
        
        # Cache to file
        gdf.to_parquet(cache_file)
        self._data_cache[cache_key] = gdf
        
        return gdf
    
    def _download_state_data(self, state_fips: str) -> gpd.GeoDataFrame:
        """Download state EJSCREEN data from EPA."""
        # Map state FIPS to state name for download URL
        state_names = self._get_state_names()
        state_name = state_names.get(state_fips)
        
        if not state_name:
            raise ValueError(f"Unknown state FIPS: {state_fips}")
        
        # Try multiple download URLs
        urls = [
            f"{EJSCREEN_DOWNLOAD_BASE}{self.version}/EJSCREEN_{self.version}_{state_name}.gdb.zip",
            f"{EJSCREEN_DOWNLOAD_BASE}{self.version}/EJSCREEN_{self.version}_StatePct_{state_name}.csv.zip",
            f"{EJSCREEN_DOWNLOAD_BASE}{self.version}/EJSCREEN_{self.version}_BG_{state_name}.csv.zip",
        ]
        
        for url in urls:
            try:
                self._rate_limit_wait()
                response = self.session.get(url, timeout=self.timeout * 2)
                
                if response.status_code == 200:
                    return self._extract_data_from_zip(response.content, state_fips)
                    
            except Exception as e:
                logger.warning(f"Failed to download from {url}: {e}")
                continue
        
        # Fallback: Use ArcGIS REST API
        return self._query_arcgis_state(state_fips)
    
    def _extract_data_from_zip(self, content: bytes, state_fips: str) -> gpd.GeoDataFrame:
        """Extract GeoDataFrame from downloaded zip file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "data.zip"
            
            with open(zip_path, "wb") as f:
                f.write(content)
            
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(tmpdir)
            
            # Look for geodatabase or CSV files
            for ext in [".gdb", ".csv", ".shp"]:
                files = list(Path(tmpdir).rglob(f"*{ext}"))
                if files:
                    if ext == ".gdb":
                        return gpd.read_file(files[0], driver="OpenFileGDB")
                    elif ext == ".shp":
                        return gpd.read_file(files[0])
                    else:
                        df = pd.read_csv(files[0])
                        # Create geometry from lat/lon if available
                        if "INTPTLAT" in df.columns and "INTPTLON" in df.columns:
                            geometry = [Point(lon, lat) for lat, lon in 
                                        zip(df["INTPTLAT"], df["INTPTLON"])]
                            return gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
                        return gpd.GeoDataFrame(df)
        
        raise ValueError("Could not extract data from zip file")
    
    def _query_arcgis_state(self, state_fips: str) -> gpd.GeoDataFrame:
        """Query EJSCREEN ArcGIS REST service for state data."""
        url = f"{EJSCREEN_ARCGIS_BASE}{self.version}/MapServer/0/query"
        
        all_features = []
        offset = 0
        batch_size = 1000
        
        while True:
            self._rate_limit_wait()
            
            params = {
                "where": f"ID LIKE '{state_fips}%'",
                "outFields": "*",
                "returnGeometry": "true",
                "f": "geojson",
                "resultOffset": offset,
                "resultRecordCount": batch_size,
            }
            
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                features = data.get("features", [])
                if not features:
                    break
                
                all_features.extend(features)
                offset += batch_size
                
                if len(features) < batch_size:
                    break
                    
            except Exception as e:
                logger.error(f"ArcGIS query failed: {e}")
                break
        
        if not all_features:
            raise ValueError(f"No data found for state {state_fips}")
        
        # Convert to GeoDataFrame
        geojson = {"type": "FeatureCollection", "features": all_features}
        gdf = gpd.GeoDataFrame.from_features(geojson, crs="EPSG:4326")
        
        logger.info(f"Retrieved {len(gdf)} block groups from ArcGIS for state {state_fips}")
        return gdf
    
    # =========================================================================
    # BUFFER / PROXIMITY METHODS
    # =========================================================================
    
    def get_buffer_data(
        self,
        lat: float,
        lon: float,
        distance_miles: float = 3.0,
        aggregate: bool = False,
    ) -> gpd.GeoDataFrame:
        """
        Get EJSCREEN data for block groups within a buffer distance.
        
        Useful for analyzing environmental justice impacts around a
        specific facility or point of interest.
        
        Args:
            lat: Latitude of center point
            lon: Longitude of center point
            distance_miles: Buffer radius in miles
            aggregate: If True, return population-weighted aggregates
        
        Returns:
            GeoDataFrame with block groups intersecting the buffer
        
        Example:
            >>> # Get block groups within 3 miles of a facility
            >>> gdf = ej.get_buffer_data(lat=33.7490, lon=-84.3880, distance_miles=3)
            >>> print(f"Affected block groups: {len(gdf)}")
            >>> print(f"Affected population: {gdf['ACSTOTPOP'].sum():,}")
        """
        # Create buffer geometry
        point = Point(lon, lat)
        
        # Convert miles to degrees (approximate)
        buffer_degrees = distance_miles / 69.0  # ~69 miles per degree at mid-latitudes
        buffer_geom = point.buffer(buffer_degrees)
        
        # Get bounding box
        minx, miny, maxx, maxy = buffer_geom.bounds
        
        # Query EJSCREEN via ArcGIS REST
        url = f"{EJSCREEN_ARCGIS_BASE}{self.version}/MapServer/0/query"
        
        self._rate_limit_wait()
        
        params = {
            "geometry": f"{minx},{miny},{maxx},{maxy}",
            "geometryType": "esriGeometryEnvelope",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "*",
            "returnGeometry": "true",
            "f": "geojson",
        }
        
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            features = data.get("features", [])
            if not features:
                return gpd.GeoDataFrame()
            
            geojson = {"type": "FeatureCollection", "features": features}
            gdf = gpd.GeoDataFrame.from_features(geojson, crs="EPSG:4326")
            
            # Filter to only features that intersect the buffer
            gdf = gdf[gdf.geometry.intersects(buffer_geom)]
            
            # Calculate distance to center point
            gdf["distance_miles"] = gdf.geometry.centroid.distance(point) * 69
            
            if aggregate:
                return self._aggregate_buffer_data(gdf)
            
            return gdf
            
        except Exception as e:
            logger.error(f"Buffer query failed: {e}")
            raise
    
    def _aggregate_buffer_data(self, gdf: gpd.GeoDataFrame) -> pd.Series:
        """Compute population-weighted aggregates for buffer area."""
        if "ACSTOTPOP" not in gdf.columns:
            raise ValueError("Population column not found")
        
        total_pop = gdf["ACSTOTPOP"].sum()
        if total_pop == 0:
            total_pop = 1  # Avoid division by zero
        
        # Population-weighted means for key indicators
        weighted_cols = [
            "PM25", "OZONE", "DSLPM", "CANCER", "RESP",
            "MINORPCT", "LOWINCPCT", "LESSHSPCT", "LINGISOPCT",
        ]
        
        result = {"total_population": total_pop, "n_block_groups": len(gdf)}
        
        for col in weighted_cols:
            if col in gdf.columns:
                weights = gdf["ACSTOTPOP"] / total_pop
                result[f"weighted_{col.lower()}"] = (gdf[col] * weights).sum()
        
        return pd.Series(result)
    
    # =========================================================================
    # FACILITY PROXIMITY METHODS
    # =========================================================================
    
    def get_ej_summary_for_facility(
        self,
        lat: float,
        lon: float,
        facility_name: str = "",
        buffer_distances: List[float] = [1, 3, 5],
    ) -> Dict[str, Any]:
        """
        Generate EJ summary report for a facility location.
        
        Provides statistics at multiple buffer distances, useful for
        environmental impact assessments and permit applications.
        
        Args:
            lat: Facility latitude
            lon: Facility longitude
            facility_name: Name of facility (for reporting)
            buffer_distances: List of buffer radii in miles
        
        Returns:
            Dictionary with summary statistics at each buffer distance
        
        Example:
            >>> summary = ej.get_ej_summary_for_facility(
            ...     lat=33.7490, lon=-84.3880,
            ...     facility_name="Example Plant",
            ...     buffer_distances=[1, 3, 5]
            ... )
            >>> print(f"3-mile population: {summary['3_mile']['total_population']:,}")
        """
        summary = {
            "facility_name": facility_name,
            "latitude": lat,
            "longitude": lon,
            "host_block_group": None,
            "buffer_analyses": {},
        }
        
        # Get host block group data
        try:
            host_data = self.get_ejscreen_data(lat, lon)
            summary["host_block_group"] = host_data.to_dict()
        except Exception as e:
            logger.warning(f"Could not get host block group data: {e}")
        
        # Analyze each buffer distance
        for distance in buffer_distances:
            try:
                gdf = self.get_buffer_data(lat, lon, distance_miles=distance)
                
                if len(gdf) == 0:
                    continue
                
                buffer_summary = {
                    "distance_miles": distance,
                    "n_block_groups": len(gdf),
                    "total_population": int(gdf["ACSTOTPOP"].sum()) if "ACSTOTPOP" in gdf.columns else None,
                }
                
                # Calculate percentile statistics
                pctile_cols = [col for col in gdf.columns if col.startswith("P_")]
                for col in pctile_cols[:10]:  # Top 10 percentile columns
                    if gdf[col].notna().any():
                        buffer_summary[f"mean_{col}"] = float(gdf[col].mean())
                        buffer_summary[f"max_{col}"] = float(gdf[col].max())
                
                summary["buffer_analyses"][f"{distance}_mile"] = buffer_summary
                
            except Exception as e:
                logger.warning(f"Buffer analysis failed for {distance} miles: {e}")
        
        return summary
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _get_state_names(self) -> Dict[str, str]:
        """Get mapping of state FIPS codes to state names."""
        return {
            "01": "Alabama", "02": "Alaska", "04": "Arizona", "05": "Arkansas",
            "06": "California", "08": "Colorado", "09": "Connecticut", "10": "Delaware",
            "11": "DistrictOfColumbia", "12": "Florida", "13": "Georgia", "15": "Hawaii",
            "16": "Idaho", "17": "Illinois", "18": "Indiana", "19": "Iowa",
            "20": "Kansas", "21": "Kentucky", "22": "Louisiana", "23": "Maine",
            "24": "Maryland", "25": "Massachusetts", "26": "Michigan", "27": "Minnesota",
            "28": "Mississippi", "29": "Missouri", "30": "Montana", "31": "Nebraska",
            "32": "Nevada", "33": "NewHampshire", "34": "NewJersey", "35": "NewMexico",
            "36": "NewYork", "37": "NorthCarolina", "38": "NorthDakota", "39": "Ohio",
            "40": "Oklahoma", "41": "Oregon", "42": "Pennsylvania", "44": "RhodeIsland",
            "45": "SouthCarolina", "46": "SouthDakota", "47": "Tennessee", "48": "Texas",
            "49": "Utah", "50": "Vermont", "51": "Virginia", "53": "Washington",
            "54": "WestVirginia", "55": "Wisconsin", "56": "Wyoming",
            "72": "PuertoRico", "78": "VirginIslands",
        }
    
    def list_indicators(self) -> Dict[str, List[str]]:
        """
        List all available EJSCREEN indicators.
        
        Returns:
            Dictionary with indicator categories and names
        """
        return {
            "environmental": [e.value for e in EJIndicator if not e.value.startswith("low")],
            "demographic": ["minority_pct", "low_income_pct", "less_hs_education", 
                          "linguistic_isolation", "under5_pct", "over64_pct"],
            "ej_indexes": [e.value for e in EJIndex],
            "supplemental": ["lack_green_space", "lack_tree_cover", "impervious_surface",
                           "flood_risk", "wildfire_risk", "extreme_heat"],
        }
    
    def get_indicator_description(self, indicator: str) -> str:
        """
        Get description for an EJSCREEN indicator.
        
        Args:
            indicator: Indicator name
        
        Returns:
            Human-readable description
        """
        descriptions = {
            "pm25": "Annual average PM2.5 concentration (μg/m³)",
            "ozone": "Summer seasonal average of daily maximum 8-hour ozone concentration (ppb)",
            "diesel_pm": "Diesel particulate matter from mobile sources (μg/m³)",
            "air_toxics_cancer": "Lifetime cancer risk from inhalation of air toxics",
            "air_toxics_respiratory": "Air toxics respiratory hazard index",
            "traffic_proximity": "Count of vehicles at major roads within 500 meters",
            "lead_paint": "Percentage of housing units built before 1960",
            "superfund_proximity": "Count of NPL sites within 5 km, distance-weighted",
            "rmp_proximity": "Count of RMP facilities within 5 km, distance-weighted",
            "tsdf_proximity": "Count of TSDFs within 5 km, distance-weighted",
            "wastewater": "RSEI modeled toxic concentrations from wastewater discharge",
            "underground_tanks": "Count of underground storage tanks within 500 meters",
            "minority_pct": "Percentage of population that is minority",
            "low_income_pct": "Percentage of population below poverty level × 2",
            "less_hs_education": "Percentage of population 25+ without high school diploma",
            "linguistic_isolation": "Percentage of limited English speaking households",
            "under5_pct": "Percentage of population under 5 years old",
            "over64_pct": "Percentage of population over 64 years old",
            "lack_green_space": "Percentage of land lacking green space",
            "flood_risk": "FEMA flood risk index",
            "wildfire_risk": "Wildfire hazard potential",
            "extreme_heat": "Extreme summer heat index",
        }
        return descriptions.get(indicator, "Description not available")
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        import shutil
        
        # Clear file cache
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Clear memory cache
        self._data_cache.clear()
        
        logger.info("EJSCREEN cache cleared")
    
    def __repr__(self) -> str:
        """String representation."""
        return f"EJScreenConnector(version={self.version}, cache_dir={self.cache_dir})"
