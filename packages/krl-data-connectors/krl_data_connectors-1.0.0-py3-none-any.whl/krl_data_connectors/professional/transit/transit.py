# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ and KRL Data Connectors™ are trademarks of Deloatch, Williams, Faison, & Parker, LLLP.
# Deloatch, Williams, Faison, & Parker, LLLP
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Transit Data Connector

Provides access to public transportation data including:
- GTFS (General Transit Feed Specification) static schedules
- Real-time vehicle locations and arrivals
- Route information and schedules
- Stop locations and accessibility
- Service alerts and disruptions
"""

import logging
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import pandas as pd

try:
    import requests
except ImportError:
    requests = None

from krl_data_connectors.base_connector import BaseConnector

from ...core import DataTier
from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license


class TransitConnector(LicensedConnectorMixin, BaseConnector):
    """
    Connector for public transit data (GTFS, real-time feeds).

    Provides unified access to:
    - Transit agency routes and schedules
    - Real-time vehicle locations
    - Stop information and predictions
    - Service alerts
    - Accessibility information
    """

    # Registry name for license validation
    _connector_name = "Transit"

    BASE_NAME = "Transit"
    BASE_URL = "https://api.transitdata.gov"  # Mock endpoint

    # Common transit agencies (extensible)
    AGENCIES = {
        "bart": {"name": "BART (Bay Area)", "region": "SF Bay Area", "state": "CA"},
        "mta": {"name": "MTA (New York)", "region": "New York City", "state": "NY"},
        "cta": {"name": "CTA (Chicago)", "region": "Chicago", "state": "IL"},
        "wmata": {"name": "WMATA (DC Metro)", "region": "Washington DC", "state": "DC"},
        "mbta": {"name": "MBTA (Boston)", "region": "Boston", "state": "MA"},
        "metro": {"name": "LA Metro", "region": "Los Angeles", "state": "CA"},
        "septa": {"name": "SEPTA (Philadelphia)", "region": "Philadelphia", "state": "PA"},
        "trimet": {"name": "TriMet (Portland)", "region": "Portland", "state": "OR"},
    }

    TRANSIT_MODES = [
        "bus",
        "subway",
        "rail",
        "light_rail",
        "ferry",
        "cable_car",
        "tram",
    ]

    ENDPOINTS = {
        "agencies": "/v1/agencies",
        "routes": "/v1/routes",
        "stops": "/v1/stops",
        "vehicles": "/v1/vehicles",
        "arrivals": "/v1/arrivals",
        "alerts": "/v1/alerts",
        "schedules": "/v1/schedules",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 3600,  # 1 hour cache for transit data
        timeout: int = 30,
        max_retries: int = 3,
        **kwargs,
    ):
        """
        Initialize Transit connector.

        Args:
            api_key: Optional API key for transit data services
            cache_dir: Directory for caching responses
            cache_ttl: Cache time-to-live in seconds (default: 1 hour)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            **kwargs: Additional arguments passed to BaseConnector
        """
        super().__init__(
            api_key=api_key,
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
            timeout=timeout,
            max_retries=max_retries,
            **kwargs,
        )

        if requests is None:
            raise ImportError("requests library is required. Install with: pip install requests")

    def _get_api_key(self) -> Optional[str]:
        """Get API key from initialization or environment."""
        return self.api_key

    def connect(self) -> None:
        """Test connection to transit API."""
        try:
            response = self._make_request("agencies", {"limit": 1})
            self.logger.info(f"Successfully connected to {self.BASE_NAME} API")
        except Exception as e:
            self.logger.error(f"Failed to connect to {self.BASE_NAME} API: {e}")
            raise

    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to transit API.

        Args:
            endpoint: API endpoint name
            params: Query parameters

        Returns:
            Response data as dictionary
        """
        if requests is None:
            raise ImportError("requests library required")

        url = urljoin(self.BASE_URL, self.ENDPOINTS[endpoint])
        headers = {}

        api_key = self._get_api_key()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        self.logger.debug(f"Making request to {url} with params: {params}")

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()

        return response.json()

    def search_agencies(
        self,
        state: Optional[str] = None,
        region: Optional[str] = None,
        agency_id: Optional[str] = None,
        limit: int = 100,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Search transit agencies.

        Args:
            state: State code filter (e.g., 'CA', 'NY')
            region: Region/city name filter
            agency_id: Specific agency ID
            limit: Maximum number of results
            **kwargs: Additional filter parameters

        Returns:
            List of transit agency information
        """
        params = {"limit": min(limit, 500)}

        if state:
            params["state"] = state.upper()
        if region:
            params["region"] = region
        if agency_id:
            params["agency_id"] = agency_id

        params.update(kwargs)

        try:
            response = self._make_request("agencies", params)
            agencies = response.get("agencies", [])

            self.logger.info(f"Found {len(agencies)} transit agencies")
            return agencies

        except Exception as e:
            self.logger.error(f"Error searching transit agencies: {e}")
            return []

    @requires_license
    def get_routes(
        self, agency_id: str, mode: Optional[str] = None, route_id: Optional[str] = None, **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Get transit routes for an agency.

        Args:
            agency_id: Transit agency ID
            mode: Transit mode filter (bus, subway, rail, etc.)
            route_id: Specific route ID
            **kwargs: Additional filter parameters

        Returns:
            List of transit routes
        """
        params = {"agency_id": agency_id}

        if mode and mode in self.TRANSIT_MODES:
            params["mode"] = mode
        if route_id:
            params["route_id"] = route_id

        params.update(kwargs)

        try:
            response = self._make_request("routes", params)
            routes = response.get("routes", [])

            self.logger.info(f"Found {len(routes)} routes for agency {agency_id}")
            return routes

        except Exception as e:
            self.logger.error(f"Error getting routes: {e}")
            return []

    @requires_license
    def get_stops(
        self,
        agency_id: str,
        route_id: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius: float = 1.0,  # miles
        accessible: Optional[bool] = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Get transit stops.

        Args:
            agency_id: Transit agency ID
            route_id: Optional route ID filter
            latitude: Latitude for proximity search
            longitude: Longitude for proximity search
            radius: Search radius in miles
            accessible: Filter for wheelchair accessible stops
            **kwargs: Additional filter parameters

        Returns:
            List of transit stops
        """
        params = {"agency_id": agency_id}

        if route_id:
            params["route_id"] = route_id
        if latitude is not None and longitude is not None:
            params["lat"] = latitude
            params["lon"] = longitude
            params["radius"] = radius
        if accessible is not None:
            params["accessible"] = str(accessible).lower()

        params.update(kwargs)

        try:
            response = self._make_request("stops", params)
            stops = response.get("stops", [])

            self.logger.info(f"Found {len(stops)} transit stops")
            return stops

        except Exception as e:
            self.logger.error(f"Error getting stops: {e}")
            return []

    @requires_license
    def get_real_time_arrivals(
        self,
        stop_id: str,
        agency_id: str,
        route_id: Optional[str] = None,
        limit: int = 10,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Get real-time arrival predictions for a stop.

        Args:
            stop_id: Transit stop ID
            agency_id: Transit agency ID
            route_id: Optional route filter
            limit: Maximum number of predictions
            **kwargs: Additional parameters

        Returns:
            List of arrival predictions
        """
        params = {"stop_id": stop_id, "agency_id": agency_id, "limit": min(limit, 50)}

        if route_id:
            params["route_id"] = route_id

        params.update(kwargs)

        try:
            response = self._make_request("arrivals", params)
            arrivals = response.get("arrivals", [])

            self.logger.info(f"Retrieved {len(arrivals)} arrival predictions for stop {stop_id}")
            return arrivals

        except Exception as e:
            self.logger.error(f"Error getting arrivals: {e}")
            return []

    @requires_license
    def get_vehicle_locations(
        self, agency_id: str, route_id: Optional[str] = None, **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Get real-time vehicle locations.

        Args:
            agency_id: Transit agency ID
            route_id: Optional route filter
            **kwargs: Additional parameters

        Returns:
            List of vehicle locations
        """
        params = {"agency_id": agency_id}

        if route_id:
            params["route_id"] = route_id

        params.update(kwargs)

        try:
            response = self._make_request("vehicles", params)
            vehicles = response.get("vehicles", [])

            self.logger.info(f"Retrieved locations for {len(vehicles)} vehicles")
            return vehicles

        except Exception as e:
            self.logger.error(f"Error getting vehicle locations: {e}")
            return []

    @requires_license
    def get_service_alerts(
        self,
        agency_id: str,
        route_id: Optional[str] = None,
        stop_id: Optional[str] = None,
        active_only: bool = True,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Get service alerts and disruptions.

        Args:
            agency_id: Transit agency ID
            route_id: Optional route filter
            stop_id: Optional stop filter
            active_only: Only return active alerts
            **kwargs: Additional parameters

        Returns:
            List of service alerts
        """
        params = {"agency_id": agency_id}

        if route_id:
            params["route_id"] = route_id
        if stop_id:
            params["stop_id"] = stop_id
        if active_only:
            params["status"] = "active"

        params.update(kwargs)

        try:
            response = self._make_request("alerts", params)
            alerts = response.get("alerts", [])

            self.logger.info(f"Retrieved {len(alerts)} service alerts")
            return alerts

        except Exception as e:
            self.logger.error(f"Error getting service alerts: {e}")
            return []

    def extract_route_info(self, route: Dict[str, Any]) -> Dict[str, Any]:
        """Extract standardized route information."""
        return {
            "route_id": route.get("route_id"),
            "route_name": route.get("route_short_name") or route.get("route_long_name"),
            "route_long_name": route.get("route_long_name"),
            "agency_id": route.get("agency_id"),
            "agency_name": route.get("agency_name"),
            "mode": route.get("route_type"),
            "color": route.get("route_color"),
            "text_color": route.get("route_text_color"),
            "description": route.get("route_desc"),
            "url": route.get("route_url"),
        }

    def extract_stop_info(self, stop: Dict[str, Any]) -> Dict[str, Any]:
        """Extract standardized stop information."""
        return {
            "stop_id": stop.get("stop_id"),
            "stop_name": stop.get("stop_name"),
            "stop_code": stop.get("stop_code"),
            "latitude": stop.get("stop_lat"),
            "longitude": stop.get("stop_lon"),
            "location_type": stop.get("location_type"),
            "parent_station": stop.get("parent_station"),
            "wheelchair_accessible": stop.get("wheelchair_boarding") == 1,
            "zone_id": stop.get("zone_id"),
            "url": stop.get("stop_url"),
            "timezone": stop.get("stop_timezone"),
        }

    def fetch(self, agency_id: str, data_type: str = "routes", **kwargs) -> pd.DataFrame:
        """
        Fetch transit data and return as DataFrame.

        Args:
            agency_id: Transit agency ID
            data_type: Type of data to fetch ('routes', 'stops', 'vehicles', 'alerts')
            **kwargs: Additional parameters for specific data type

        Returns:
            DataFrame with transit data
        """
        data = []

        if data_type == "routes":
            routes = self.get_routes(agency_id, **kwargs)
            data = [self.extract_route_info(r) for r in routes]

        elif data_type == "stops":
            stops = self.get_stops(agency_id, **kwargs)
            data = [self.extract_stop_info(s) for s in stops]

        elif data_type == "vehicles":
            vehicles = self.get_vehicle_locations(agency_id, **kwargs)
            data = vehicles

        elif data_type == "alerts":
            alerts = self.get_service_alerts(agency_id, **kwargs)
            data = alerts

        else:
            self.logger.error(f"Unknown data_type: {data_type}")
            return pd.DataFrame()

        df = pd.DataFrame(data)

        if not df.empty:
            df["fetched_at"] = datetime.now(UTC).isoformat()
            df["agency_id"] = agency_id

        self.logger.info(f"Compiled {len(df)} {data_type} records into DataFrame")
        return df
