# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
U.S. Census TIGER/Line Geographic Data Connector.

Provides access to TIGER/Line shapefiles for geographic analysis including:
- State, county, census tract boundaries
- ZIP Code Tabulation Areas (ZCTAs)
- Congressional districts, school districts
- Urban areas, places, landmarks
- Roads, rails, water features

Data Source: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html

The TIGER/Line files are public domain and do not require an API key.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import zipfile
from datetime import datetime, UTC
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import pandas as pd
import requests

try:
    from krl_core import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


# Census TIGER/Line base URLs
TIGER_FTP_BASE = "https://www2.census.gov/geo/tiger"


class TIGERLayer(str, Enum):
    """TIGER/Line geographic layer types."""
    
    STATE = "STATE"
    COUNTY = "COUNTY"
    TRACT = "TRACT"
    BLOCK_GROUP = "BG"
    BLOCK = "TABBLOCK20"
    ZCTA = "ZCTA520"
    PLACE = "PLACE"
    COUSUB = "COUSUB"  # County subdivisions
    CONGRESSIONAL = "CD"
    STATE_LEGISLATIVE_UPPER = "SLDU"
    STATE_LEGISLATIVE_LOWER = "SLDL"
    SCHOOL_DISTRICT_UNIFIED = "UNSD"
    SCHOOL_DISTRICT_ELEMENTARY = "ELSD"
    SCHOOL_DISTRICT_SECONDARY = "SCSD"
    URBAN_AREA = "UAC20"
    CBSA = "CBSA"  # Core Based Statistical Areas
    ROADS = "ROADS"
    RAILS = "RAILS"
    WATER = "AREAWATER"
    COASTLINE = "COASTLINE"


class TIGERYear(str, Enum):
    """Available TIGER/Line years."""
    
    TIGER2020 = "TIGER2020"
    TIGER2021 = "TIGER2021"
    TIGER2022 = "TIGER2022"
    TIGER2023 = "TIGER2023"
    TIGER2024 = "TIGER2024"
    TIGER2025 = "TIGER2025"


# All U.S. state FIPS codes including territories
STATE_FIPS = {
    "01": "Alabama", "02": "Alaska", "04": "Arizona", "05": "Arkansas",
    "06": "California", "08": "Colorado", "09": "Connecticut", "10": "Delaware",
    "11": "District of Columbia", "12": "Florida", "13": "Georgia", "15": "Hawaii",
    "16": "Idaho", "17": "Illinois", "18": "Indiana", "19": "Iowa",
    "20": "Kansas", "21": "Kentucky", "22": "Louisiana", "23": "Maine",
    "24": "Maryland", "25": "Massachusetts", "26": "Michigan", "27": "Minnesota",
    "28": "Mississippi", "29": "Missouri", "30": "Montana", "31": "Nebraska",
    "32": "Nevada", "33": "New Hampshire", "34": "New Jersey", "35": "New Mexico",
    "36": "New York", "37": "North Carolina", "38": "North Dakota", "39": "Ohio",
    "40": "Oklahoma", "41": "Oregon", "42": "Pennsylvania", "44": "Rhode Island",
    "45": "South Carolina", "46": "South Dakota", "47": "Tennessee", "48": "Texas",
    "49": "Utah", "50": "Vermont", "51": "Virginia", "53": "Washington",
    "54": "West Virginia", "55": "Wisconsin", "56": "Wyoming",
    # Territories
    "60": "American Samoa", "66": "Guam", "69": "Northern Mariana Islands",
    "72": "Puerto Rico", "78": "U.S. Virgin Islands",
}

# Layers that are organized by state (one file per state)
STATE_ORGANIZED_LAYERS = {
    TIGERLayer.TRACT, TIGERLayer.BLOCK_GROUP, TIGERLayer.BLOCK,
    TIGERLayer.PLACE, TIGERLayer.COUSUB, TIGERLayer.ROADS,
    TIGERLayer.WATER,
}

# Layers that have a single national file
NATIONAL_LAYERS = {
    TIGERLayer.STATE, TIGERLayer.COUNTY, TIGERLayer.ZCTA,
    TIGERLayer.CBSA, TIGERLayer.URBAN_AREA,
}


class CensusTIGERConnector:
    """
    Connector for U.S. Census TIGER/Line geographic data.
    
    Downloads, caches, and provides access to Census TIGER/Line
    shapefiles for geographic boundary analysis.
    
    Example:
        >>> tiger = CensusTIGERConnector()
        >>> # Get all state boundaries
        >>> states = tiger.get_boundaries(TIGERLayer.STATE)
        >>> # Get tracts for California
        >>> ca_tracts = tiger.get_boundaries(
        ...     TIGERLayer.TRACT,
        ...     state_fips="06"
        ... )
        >>> # Get ZCTAs (ZIP Code Tabulation Areas)
        >>> zctas = tiger.get_boundaries(TIGERLayer.ZCTA)
    
    Attributes:
        STATE_FIPS: Dict mapping FIPS codes to state names
        NATIONAL_LAYERS: Set of layers with single national files
        STATE_ORGANIZED_LAYERS: Set of layers organized by state
    """
    
    STATE_FIPS = STATE_FIPS
    NATIONAL_LAYERS = NATIONAL_LAYERS
    STATE_ORGANIZED_LAYERS = STATE_ORGANIZED_LAYERS
    
    def __init__(
        self,
        cache_dir: Optional[str] = None,
        tiger_year: Union[str, TIGERYear] = TIGERYear.TIGER2025,
        auto_extract: bool = True,
    ):
        """
        Initialize Census TIGER connector.
        
        Args:
            cache_dir: Directory for downloaded/cached files
            tiger_year: TIGER/Line year version to use
            auto_extract: Automatically extract ZIP files after download
        """
        self.tiger_year = TIGERYear(tiger_year) if isinstance(tiger_year, str) else tiger_year
        self.auto_extract = auto_extract
        
        self.cache_dir = Path(cache_dir or Path.home() / ".krl_cache" / "tiger")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "KRL-DataConnectors/1.0 (Census TIGER downloader)",
        })
        
        # Import geopandas lazily for reading shapefiles
        self._gpd = None
        
        logger.info(
            f"Initialized TIGER connector for {self.tiger_year.value}, "
            f"cache: {self.cache_dir}"
        )
    
    @property
    def gpd(self):
        """Lazy import of geopandas."""
        if self._gpd is None:
            try:
                import geopandas
                self._gpd = geopandas
            except ImportError:
                raise ImportError(
                    "geopandas is required for reading TIGER shapefiles. "
                    "Install with: pip install geopandas"
                )
        return self._gpd
    
    def _get_tiger_url(self, layer: TIGERLayer, state_fips: Optional[str] = None) -> str:
        """
        Build URL for TIGER file download.
        
        Args:
            layer: Geographic layer type
            state_fips: State FIPS code for state-organized layers
            
        Returns:
            Full URL to the TIGER ZIP file
        """
        base = f"{TIGER_FTP_BASE}/{self.tiger_year.value}"
        
        if layer in NATIONAL_LAYERS:
            # National file - single file for whole US
            filename = f"tl_{self.tiger_year.value[-4:]}_{layer.value.lower()}.zip"
            return f"{base}/{layer.value}/{filename}"
        elif layer in STATE_ORGANIZED_LAYERS and state_fips:
            # State-specific file
            year_short = self.tiger_year.value[-4:]
            filename = f"tl_{year_short}_{state_fips}_{layer.value.lower()}.zip"
            return f"{base}/{layer.value}/{filename}"
        else:
            raise ValueError(
                f"Layer {layer.value} requires state_fips parameter for download"
            )
    
    def _get_cache_path(self, layer: TIGERLayer, state_fips: Optional[str] = None) -> Path:
        """Get local cache path for a TIGER file."""
        layer_dir = self.cache_dir / self.tiger_year.value / layer.value
        layer_dir.mkdir(parents=True, exist_ok=True)
        
        if state_fips:
            return layer_dir / f"{state_fips}_{layer.value.lower()}"
        else:
            return layer_dir / layer.value.lower()
    
    def download_layer(
        self,
        layer: TIGERLayer,
        state_fips: Optional[str] = None,
        force: bool = False,
    ) -> Path:
        """
        Download a TIGER/Line layer.
        
        Args:
            layer: Geographic layer type
            state_fips: State FIPS code for state-organized layers
            force: Force re-download even if cached
            
        Returns:
            Path to downloaded/extracted directory
            
        Raises:
            ValueError: If state_fips required but not provided
            requests.HTTPError: On download failure
        """
        cache_path = self._get_cache_path(layer, state_fips)
        
        # Check if already downloaded
        if not force and cache_path.exists():
            logger.debug(f"Using cached {layer.value} for {state_fips or 'national'}")
            return cache_path
        
        url = self._get_tiger_url(layer, state_fips)
        logger.info(f"Downloading {layer.value} from {url}")
        
        # Download to temporary file
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            response = self.session.get(url, stream=True, timeout=300)
            response.raise_for_status()
            
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                tmp.write(chunk)
            tmp_path = tmp.name
        
        # Extract if auto_extract enabled
        if self.auto_extract:
            try:
                with zipfile.ZipFile(tmp_path, 'r') as zf:
                    cache_path.mkdir(parents=True, exist_ok=True)
                    zf.extractall(cache_path)
                logger.info(f"Extracted to {cache_path}")
            finally:
                os.unlink(tmp_path)
        else:
            # Just move the ZIP file
            zip_path = cache_path.with_suffix(".zip")
            shutil.move(tmp_path, zip_path)
            cache_path = zip_path
        
        return cache_path
    
    def get_boundaries(
        self,
        layer: TIGERLayer,
        state_fips: Optional[str] = None,
        columns: Optional[List[str]] = None,
    ) -> "gpd.GeoDataFrame":
        """
        Get geographic boundaries as a GeoDataFrame.
        
        Args:
            layer: Geographic layer type (STATE, COUNTY, TRACT, etc.)
            state_fips: State FIPS code for state-organized layers
            columns: Specific columns to return (default: all)
            
        Returns:
            GeoDataFrame with geographic boundaries
            
        Example:
            >>> tiger = CensusTIGERConnector()
            >>> states = tiger.get_boundaries(TIGERLayer.STATE)
            >>> states[['STATEFP', 'NAME', 'geometry']].head()
        """
        cache_path = self.download_layer(layer, state_fips)
        
        # Find shapefile in extracted directory
        shp_files = list(cache_path.glob("*.shp"))
        if not shp_files:
            raise FileNotFoundError(f"No shapefile found in {cache_path}")
        
        gdf = self.gpd.read_file(shp_files[0])
        
        if columns:
            # Always include geometry
            cols = list(set(columns) | {"geometry"})
            cols = [c for c in cols if c in gdf.columns]
            gdf = gdf[cols]
        
        logger.info(f"Loaded {len(gdf)} features from {layer.value}")
        return gdf
    
    def get_state_boundaries(
        self,
        include_territories: bool = False,
    ) -> "gpd.GeoDataFrame":
        """
        Get U.S. state boundaries.
        
        Args:
            include_territories: Include U.S. territories (PR, VI, GU, etc.)
            
        Returns:
            GeoDataFrame with state boundaries
        """
        gdf = self.get_boundaries(TIGERLayer.STATE)
        
        if not include_territories:
            # Filter to 50 states + DC
            mainland_fips = [f for f in STATE_FIPS.keys() if int(f) <= 56]
            gdf = gdf[gdf["STATEFP"].isin(mainland_fips)]
        
        return gdf
    
    def get_county_boundaries(
        self,
        state_fips: Optional[str] = None,
    ) -> "gpd.GeoDataFrame":
        """
        Get U.S. county boundaries.
        
        Args:
            state_fips: Filter to specific state (optional)
            
        Returns:
            GeoDataFrame with county boundaries
        """
        gdf = self.get_boundaries(TIGERLayer.COUNTY)
        
        if state_fips:
            gdf = gdf[gdf["STATEFP"] == state_fips]
        
        return gdf
    
    def get_tract_boundaries(
        self,
        state_fips: str,
    ) -> "gpd.GeoDataFrame":
        """
        Get census tract boundaries for a state.
        
        Args:
            state_fips: 2-digit state FIPS code (required)
            
        Returns:
            GeoDataFrame with tract boundaries
        """
        return self.get_boundaries(TIGERLayer.TRACT, state_fips=state_fips)
    
    def get_zcta_boundaries(self) -> "gpd.GeoDataFrame":
        """
        Get ZIP Code Tabulation Area (ZCTA) boundaries.
        
        Returns:
            GeoDataFrame with ZCTA boundaries
        """
        return self.get_boundaries(TIGERLayer.ZCTA)
    
    def get_cbsa_boundaries(self) -> "gpd.GeoDataFrame":
        """
        Get Core Based Statistical Area (metro/micro) boundaries.
        
        Returns:
            GeoDataFrame with CBSA boundaries
        """
        return self.get_boundaries(TIGERLayer.CBSA)
    
    def get_layer_metadata(self, layer: TIGERLayer) -> Dict[str, Any]:
        """
        Get metadata about a TIGER layer.
        
        Args:
            layer: Geographic layer type
            
        Returns:
            Dict with layer metadata
        """
        # Layer-specific metadata
        metadata = {
            TIGERLayer.STATE: {
                "description": "U.S. State and Territory boundaries",
                "feature_count_approx": 56,
                "key_fields": ["STATEFP", "STUSPS", "NAME"],
                "is_national": True,
            },
            TIGERLayer.COUNTY: {
                "description": "County and equivalent boundaries",
                "feature_count_approx": 3200,
                "key_fields": ["STATEFP", "COUNTYFP", "GEOID", "NAME"],
                "is_national": True,
            },
            TIGERLayer.TRACT: {
                "description": "Census tract boundaries",
                "feature_count_approx": 85000,
                "key_fields": ["STATEFP", "COUNTYFP", "TRACTCE", "GEOID"],
                "is_national": False,
                "requires_state_fips": True,
            },
            TIGERLayer.ZCTA: {
                "description": "ZIP Code Tabulation Areas",
                "feature_count_approx": 33000,
                "key_fields": ["ZCTA5CE20", "GEOID20"],
                "is_national": True,
            },
            TIGERLayer.CBSA: {
                "description": "Core Based Statistical Areas (Metro/Micro)",
                "feature_count_approx": 400,
                "key_fields": ["CBSAFP", "NAME", "LSAD"],
                "is_national": True,
            },
        }
        
        return metadata.get(layer, {
            "description": f"{layer.value} boundaries",
            "is_national": layer in NATIONAL_LAYERS,
            "requires_state_fips": layer in STATE_ORGANIZED_LAYERS,
        })
    
    def list_available_layers(self) -> pd.DataFrame:
        """
        List all available TIGER/Line layers.
        
        Returns:
            DataFrame with layer information
        """
        records = []
        for layer in TIGERLayer:
            meta = self.get_layer_metadata(layer)
            records.append({
                "layer": layer.value,
                "description": meta.get("description", ""),
                "is_national": meta.get("is_national", False),
                "requires_state_fips": meta.get("requires_state_fips", False),
                "approx_features": meta.get("feature_count_approx"),
            })
        
        return pd.DataFrame(records)
    
    def list_cached_files(self) -> pd.DataFrame:
        """
        List all cached TIGER files.
        
        Returns:
            DataFrame with cached file information
        """
        records = []
        
        for year_dir in self.cache_dir.iterdir():
            if not year_dir.is_dir():
                continue
            
            for layer_dir in year_dir.iterdir():
                if not layer_dir.is_dir():
                    continue
                
                for item in layer_dir.iterdir():
                    size_mb = sum(
                        f.stat().st_size for f in item.rglob("*") if f.is_file()
                    ) / (1024 * 1024) if item.is_dir() else item.stat().st_size / (1024 * 1024)
                    
                    records.append({
                        "year": year_dir.name,
                        "layer": layer_dir.name,
                        "name": item.name,
                        "size_mb": round(size_mb, 2),
                        "path": str(item),
                    })
        
        return pd.DataFrame(records)
    
    def clear_cache(self, layer: Optional[TIGERLayer] = None) -> int:
        """
        Clear cached TIGER files.
        
        Args:
            layer: Specific layer to clear (None = all layers)
            
        Returns:
            Number of files/directories removed
        """
        count = 0
        
        if layer:
            layer_dir = self.cache_dir / self.tiger_year.value / layer.value
            if layer_dir.exists():
                shutil.rmtree(layer_dir)
                count = 1
        else:
            for item in self.cache_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                    count += 1
        
        logger.info(f"Cleared {count} cached items")
        return count
    
    def download_all_states(
        self,
        layer: TIGERLayer,
        state_fips_list: Optional[List[str]] = None,
    ) -> Dict[str, Path]:
        """
        Download layer for all states (parallel-ready).
        
        Args:
            layer: Geographic layer type (must be state-organized)
            state_fips_list: List of state FIPS codes (default: all states)
            
        Returns:
            Dict mapping state FIPS to downloaded paths
        """
        if layer not in STATE_ORGANIZED_LAYERS:
            raise ValueError(f"{layer.value} is not a state-organized layer")
        
        fips_list = state_fips_list or list(STATE_FIPS.keys())
        
        results = {}
        for fips in fips_list:
            try:
                path = self.download_layer(layer, state_fips=fips)
                results[fips] = path
            except Exception as e:
                logger.warning(f"Failed to download {layer.value} for {fips}: {e}")
                results[fips] = None
        
        return results
    
    def __repr__(self) -> str:
        return (
            f"CensusTIGERConnector("
            f"year={self.tiger_year.value}, "
            f"cache_dir='{self.cache_dir}')"
        )
