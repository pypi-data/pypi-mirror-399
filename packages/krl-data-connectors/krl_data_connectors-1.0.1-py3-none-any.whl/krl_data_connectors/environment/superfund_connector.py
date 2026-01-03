# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
EPA Superfund Sites (NPL) Data Connector.

Provides access to:
- National Priorities List (NPL) sites
- Superfund site contamination data
- Remediation status information
- Hazardous waste site proximity

API Reference: https://www.epa.gov/enviro/sems-search
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests

try:
    from krl_core import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


# EPA Envirofacts API
ENVIROFACTS_BASE = "https://data.epa.gov/efservice"


class EPASuperfundConnector:
    """
    Connector for EPA Superfund/NPL site data.
    
    Access National Priorities List sites, contamination data,
    and remediation information.
    
    Example:
        >>> sf = EPASuperfundConnector()
        >>> sites = sf.get_npl_sites(state="GA")
        >>> site_info = sf.get_site_details(site_id="GAD003348929")
    """
    
    def __init__(
        self,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 86400,
    ):
        """
        Initialize Superfund connector.
        
        Args:
            cache_dir: Directory for cached data
            cache_ttl: Cache time-to-live in seconds
        """
        self.cache_ttl = cache_ttl
        self.cache_dir = Path(cache_dir or Path.home() / ".krl_cache" / "superfund")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for test compatibility
        self.cache: Dict[str, Any] = {}
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "KRL-DataConnectors/1.0",
            "Accept": "application/json",
        })
    
    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """Make request to EPA Envirofacts API."""
        # Build URL with filters
        url = f"{ENVIROFACTS_BASE}/{endpoint}"
        if params:
            for key, value in params.items():
                url += f"/{key}/{value}"
        url += "/json"
        
        response = self.session.get(url, timeout=60)
        response.raise_for_status()
        
        return response.json()
    
    def get_npl_sites(
        self,
        state: Optional[str] = None,
        city: Optional[str] = None,
        status: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get National Priorities List (NPL) Superfund sites.
        
        Args:
            state: 2-letter state code
            city: City name
            status: NPL status (Final, Proposed, Deleted)
        
        Returns:
            DataFrame with NPL site information
        """
        params = {}
        if state:
            params["state_code"] = state
        if city:
            params["city_name"] = city.upper()
        if status:
            params["npl_status"] = status
        
        data = self._make_request("SEMS_ACTIVE_SITES", params)
        return pd.DataFrame(data)
    
    def get_site_details(
        self,
        site_id: str,
    ) -> pd.DataFrame:
        """
        Get details for a specific Superfund site.
        
        Args:
            site_id: EPA Site ID
        
        Returns:
            DataFrame with site details
        """
        data = self._make_request("SEMS_ACTIVE_SITES", {"site_epa_id": site_id})
        return pd.DataFrame(data)
    
    def get_contaminants(
        self,
        state: Optional[str] = None,
        contaminant: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Get contamination data for Superfund sites.
        
        Args:
            state: 2-letter state code
            contaminant: Contaminant name
        
        Returns:
            DataFrame with contaminant information
        """
        params = {}
        if state:
            params["state_code"] = state
        if contaminant:
            params["contaminant_name"] = contaminant.upper()
        
        try:
            data = self._make_request("SEMS_CONTAMINANTS", params)
            return pd.DataFrame(data)
        except Exception as e:
            logger.warning(f"Error fetching contaminants: {e}")
            return pd.DataFrame()
    
    def search_by_location(
        self,
        lat: float,
        lon: float,
        radius_miles: float = 5.0,
    ) -> pd.DataFrame:
        """
        Search for Superfund sites near a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius_miles: Search radius in miles
        
        Returns:
            DataFrame with nearby sites
        """
        # Get all sites and filter by distance
        # Note: A more efficient implementation would use a spatial query
        import math
        
        all_sites = self.get_npl_sites()
        
        if all_sites.empty:
            return all_sites
        
        def haversine_distance(lat1, lon1, lat2, lon2):
            """Calculate distance between two points in miles."""
            R = 3959  # Earth radius in miles
            
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            
            return R * c
        
        # Filter by distance
        if "latitude" in all_sites.columns and "longitude" in all_sites.columns:
            all_sites["distance_miles"] = all_sites.apply(
                lambda row: haversine_distance(
                    lat, lon,
                    float(row.get("latitude", 0) or 0),
                    float(row.get("longitude", 0) or 0)
                ),
                axis=1
            )
            return all_sites[all_sites["distance_miles"] <= radius_miles].copy()
        
        return all_sites
    
    def __repr__(self) -> str:
        return "EPASuperfundConnector()"


# Backwards compatible alias
SuperfundConnector = EPASuperfundConnector
