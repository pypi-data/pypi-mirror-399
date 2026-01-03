# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ and KRL Data Connectors™ are trademarks of Deloatch, Williams, Faison, & Parker, LLLP.
# Deloatch, Williams, Faison, & Parker, LLLP
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Parks and Recreation Data Connector.

Provides access to parks, trails, recreational facilities, and green spaces data.
Supports national parks (NPS), state/local parks, trails, playgrounds, sports facilities,
and community recreation programs.
"""

import logging
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import pandas as pd

try:
    import requests
except ImportError:
    requests = None

from krl_data_connectors.base_connector import BaseConnector

from ...core import DataTier
from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license

logger = logging.getLogger(__name__)


class ParksRecreationConnector(LicensedConnectorMixin, BaseConnector):
    """Connector for parks and recreation data APIs."""

    # Registry name for license validation
    _connector_name = "Parks_Recreation"

    BASE_NAME = "ParksRecreation"
    BASE_URL = "https://api.recreation.gov"  # Mock endpoint

    # Park types and classifications
    PARK_TYPES = [
        "national_park",
        "state_park",
        "city_park",
        "regional_park",
        "nature_preserve",
        "recreation_area",
        "wilderness_area",
        "historic_site",
        "monument",
        "forest",
    ]

    # Facility types
    FACILITY_TYPES = [
        "campground",
        "picnic_area",
        "trail_head",
        "visitor_center",
        "boat_launch",
        "playground",
        "sports_field",
        "swimming_pool",
        "tennis_court",
        "basketball_court",
        "dog_park",
        "skate_park",
        "community_center",
    ]

    # Amenity categories
    AMENITIES = [
        "restrooms",
        "parking",
        "water_fountain",
        "grills",
        "picnic_tables",
        "ada_accessible",
        "pet_friendly",
        "wifi",
        "electric_hookup",
        "shower",
        "dump_station",
    ]

    # API endpoints
    ENDPOINTS = {
        "parks": "/v1/parks",
        "facilities": "/v1/facilities",
        "trails": "/v1/trails",
        "activities": "/v1/activities",
        "permits": "/v1/permits",
        "reservations": "/v1/reservations",
        "programs": "/v1/programs",
    }

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize Parks & Recreation connector.

        Args:
            api_key: API key for recreation.gov or similar service
            **kwargs: Additional arguments passed to BaseConnector
        """
        if requests is None:
            raise ImportError(
                "requests library is required for ParksRecreationConnector. "
                "Install it with: pip install requests"
            )

        super().__init__(api_key=api_key, cache_ttl=7200, **kwargs)  # 2 hour cache
        logger.info(f"{self.BASE_NAME} connector initialized")

    def _get_api_key(self) -> str:
        """Get API key from initialization or config."""
        return self.api_key or ""

    def connect(self) -> bool:
        """Test connection to parks API."""
        try:
            response = self._make_request(self.ENDPOINTS["parks"], {"limit": 1})
            return response is not None
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Make HTTP request to parks API."""
        url = f"{self.BASE_URL}{endpoint}"
        headers = {}

        api_key = self._get_api_key()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            if params:
                url = f"{url}?{urlencode(params)}"

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None

    def search_parks(
        self,
        state: Optional[str] = None,
        park_type: Optional[str] = None,
        name: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius: Optional[int] = None,
        limit: int = 100,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Search for parks.

        Args:
            state: State code (e.g., "CA", "NY")
            park_type: Type of park (from PARK_TYPES)
            name: Park name keyword search
            lat: Latitude for proximity search
            lon: Longitude for proximity search
            radius: Search radius in miles (used with lat/lon)
            limit: Maximum number of results
            **kwargs: Additional query parameters

        Returns:
            List of park dictionaries
        """
        params = {"limit": limit, **kwargs}

        if state:
            params["state"] = state.upper()
        if park_type:
            params["type"] = park_type
        if name:
            params["q"] = name
        if lat is not None and lon is not None:
            params["lat"] = lat
            params["lon"] = lon
            if radius:
                params["radius"] = radius

        response = self._make_request(self.ENDPOINTS["parks"], params)
        if response and "data" in response:
            return response["data"]
        return []

    @requires_license
    def get_facilities(
        self,
        park_id: Optional[str] = None,
        facility_type: Optional[str] = None,
        state: Optional[str] = None,
        accessible: Optional[bool] = None,
        limit: int = 100,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Get recreational facilities.

        Args:
            park_id: Specific park identifier
            facility_type: Type of facility (from FACILITY_TYPES)
            state: State code
            accessible: Filter for ADA accessible facilities
            limit: Maximum number of results
            **kwargs: Additional query parameters

        Returns:
            List of facility dictionaries
        """
        params = {"limit": limit, **kwargs}

        if park_id:
            params["park_id"] = park_id
        if facility_type:
            params["type"] = facility_type
        if state:
            params["state"] = state.upper()
        if accessible is not None:
            params["accessible"] = str(accessible).lower()

        response = self._make_request(self.ENDPOINTS["facilities"], params)
        if response and "data" in response:
            return response["data"]
        return []

    @requires_license
    def get_trails(
        self,
        park_id: Optional[str] = None,
        difficulty: Optional[str] = None,
        length_min: Optional[float] = None,
        length_max: Optional[float] = None,
        activities: Optional[List[str]] = None,
        limit: int = 100,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Get trail information.

        Args:
            park_id: Specific park identifier
            difficulty: Trail difficulty (easy, moderate, difficult)
            length_min: Minimum trail length in miles
            length_max: Maximum trail length in miles
            activities: List of activities (hiking, biking, horseback)
            limit: Maximum number of results
            **kwargs: Additional query parameters

        Returns:
            List of trail dictionaries
        """
        params = {"limit": limit, **kwargs}

        if park_id:
            params["park_id"] = park_id
        if difficulty:
            params["difficulty"] = difficulty
        if length_min is not None:
            params["length_min"] = length_min
        if length_max is not None:
            params["length_max"] = length_max
        if activities:
            params["activities"] = ",".join(activities)

        response = self._make_request(self.ENDPOINTS["trails"], params)
        if response and "data" in response:
            return response["data"]
        return []

    @requires_license
    def get_programs(
        self,
        park_id: Optional[str] = None,
        program_type: Optional[str] = None,
        age_group: Optional[str] = None,
        free_only: Optional[bool] = None,
        limit: int = 100,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Get recreation programs and activities.

        Args:
            park_id: Specific park identifier
            program_type: Type of program (sports, arts, education, fitness)
            age_group: Target age group (youth, adult, senior, family)
            free_only: Filter for free programs only
            limit: Maximum number of results
            **kwargs: Additional query parameters

        Returns:
            List of program dictionaries
        """
        params = {"limit": limit, **kwargs}

        if park_id:
            params["park_id"] = park_id
        if program_type:
            params["type"] = program_type
        if age_group:
            params["age_group"] = age_group
        if free_only is not None:
            params["free"] = str(free_only).lower()

        response = self._make_request(self.ENDPOINTS["programs"], params)
        if response and "data" in response:
            return response["data"]
        return []

    def extract_park_info(self, park: Dict[str, Any]) -> Dict[str, Any]:
        """Extract standardized park information."""
        return {
            "park_id": park.get("id"),
            "name": park.get("name"),
            "park_type": park.get("type"),
            "state": park.get("state"),
            "city": park.get("city"),
            "latitude": park.get("lat"),
            "longitude": park.get("lon"),
            "acres": park.get("acres"),
            "description": park.get("description"),
            "amenities": park.get("amenities", []),
            "website": park.get("website"),
            "phone": park.get("phone"),
        }

    def extract_facility_info(self, facility: Dict[str, Any]) -> Dict[str, Any]:
        """Extract standardized facility information."""
        return {
            "facility_id": facility.get("id"),
            "name": facility.get("name"),
            "facility_type": facility.get("type"),
            "park_id": facility.get("park_id"),
            "latitude": facility.get("lat"),
            "longitude": facility.get("lon"),
            "accessible": facility.get("ada_accessible", False),
            "capacity": facility.get("capacity"),
            "reservable": facility.get("reservable", False),
            "fee": facility.get("fee"),
        }

    def extract_trail_info(self, trail: Dict[str, Any]) -> Dict[str, Any]:
        """Extract standardized trail information."""
        return {
            "trail_id": trail.get("id"),
            "name": trail.get("name"),
            "park_id": trail.get("park_id"),
            "length_miles": trail.get("length"),
            "difficulty": trail.get("difficulty"),
            "elevation_gain": trail.get("elevation_gain"),
            "trail_type": trail.get("type"),  # loop, out-and-back, point-to-point
            "surface": trail.get("surface"),  # paved, gravel, dirt
            "activities": trail.get("activities", []),
            "dog_friendly": trail.get("dogs_allowed", False),
        }

    def fetch(
        self,
        data_type: str = "parks",
        state: Optional[str] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Fetch parks and recreation data as DataFrame.

        Args:
            data_type: Type of data ('parks', 'facilities', 'trails', 'programs')
            state: State code filter
            **kwargs: Additional parameters for specific data type

        Returns:
            DataFrame with parks and recreation data
        """
        data = []

        if data_type == "parks":
            parks = self.search_parks(state=state, **kwargs)
            data = [self.extract_park_info(p) for p in parks]

        elif data_type == "facilities":
            facilities = self.get_facilities(state=state, **kwargs)
            data = [self.extract_facility_info(f) for f in facilities]

        elif data_type == "trails":
            trails = self.get_trails(**kwargs)
            data = [self.extract_trail_info(t) for t in trails]

        elif data_type == "programs":
            programs = self.get_programs(**kwargs)
            data = programs  # Use raw program data

        else:
            logger.warning(f"Unknown data type: {data_type}")
            return pd.DataFrame()

        if not data:
            logger.warning(f"No {data_type} data found")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df["fetched_at"] = datetime.now(UTC).isoformat()

        logger.info(f"Fetched {len(df)} {data_type} records")
        return df
