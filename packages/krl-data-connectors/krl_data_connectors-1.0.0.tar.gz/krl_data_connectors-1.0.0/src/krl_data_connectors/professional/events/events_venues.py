# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ and KRL Data Connectors™ are trademarks of Deloatch, Williams, Faison, & Parker, LLLP.
# Deloatch, Williams, Faison, & Parker, LLLP
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
D40 Events & Venues Connector - Ticketmaster Integration
========================================================

Extracts events, venues, and attractions data from Ticketmaster Discovery API.
Provides comprehensive event information including schedules, pricing, and venue details.
"""

import logging
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.base_connector import BaseConnector

from ...core import DataTier
from ...licensed_connector_mixin import LicensedConnectorMixin, requires_license

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


logger = logging.getLogger(__name__)


class EventsVenuesConnector(LicensedConnectorMixin, BaseConnector):
    """Connector for Ticketmaster Discovery API to extract events and venues data.

    This connector interfaces with the Ticketmaster Discovery API v2 to gather
    event information, venue details, attractions, and classifications.

    Features:
    - Event search with location, date, and category filters
    - Venue information extraction (capacity, location, amenities)
    - Attraction details (artists, teams, performers)
    - Event classifications (genres, segments, categories)
    - Price range information
    - Sales status and availability tracking

    API Documentation: https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/
    """

    # Registry name for license validation
    _connector_name = "Events_Venues"

    BASE_NAME = "EventsVenues"
    BASE_URL = "https://app.ticketmaster.com/discovery/v2"

    ENDPOINTS = {
        "events_search": "/events.json",
        "event_details": "/events/{event_id}.json",
        "venues_search": "/venues.json",
        "venue_details": "/venues/{venue_id}.json",
        "attractions_search": "/attractions.json",
        "attraction_details": "/attractions/{attraction_id}.json",
        "classifications": "/classifications.json",
    }

    # Event segments (high-level categories)
    EVENT_SEGMENTS = [
        "Music",
        "Sports",
        "Arts & Theatre",
        "Film",
        "Miscellaneous",
    ]

    # Music genres
    MUSIC_GENRES = [
        "Rock",
        "Pop",
        "Country",
        "Hip-Hop/Rap",
        "R&B",
        "Dance/Electronic",
        "Jazz",
        "Classical",
        "Alternative",
        "Metal",
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        country_code: str = "US",
        locale: str = "en-us",
        cache_dir: Optional[str] = None,
        cache_ttl: int = 3600,  # 1 hour (events change frequently)
        timeout: int = 30,
        max_retries: int = 3,
        **kwargs,
    ):
        """Initialize Events & Venues Connector.

        Args:
            api_key: Ticketmaster API key (required)
            country_code: Default country code for searches (ISO 3166-1 alpha-2)
            locale: Default locale for content
            cache_dir: Directory for caching responses
            cache_ttl: Cache time-to-live in seconds
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            **kwargs: Additional arguments passed to BaseConnector
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required. Install with: pip install requests")

        super().__init__(
            api_key=api_key,
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
            timeout=timeout,
            max_retries=max_retries,
            **kwargs,
        )

        self.country_code = country_code
        self.locale = locale

        logger.info(
            f"Events & Venues connector initialized (country: {country_code}, locale: {locale})"
        )

    def _get_api_key(self) -> Optional[str]:
        """Get API key from configuration.

        Returns:
            API key string or None
        """
        return self.api_key

    def connect(self) -> None:
        """Establish connection to Ticketmaster API.

        Tests the connection by making a simple events search.

        Raises:
            ConnectionError: If connection fails
            ValueError: If API key is missing
        """
        if not self.api_key:
            raise ValueError(
                "Ticketmaster API key is required. "
                "Get one at https://developer.ticketmaster.com/products-and-docs/apis/getting-started/"
            )

        try:
            # Test connection with a simple search
            test_url = f"{self.BASE_URL}{self.ENDPOINTS['events_search']}"

            response = requests.get(
                test_url,
                params={"apikey": self.api_key, "countryCode": self.country_code, "size": 1},
                timeout=self.timeout,
            )

            if response.status_code == 401:
                raise ValueError("Invalid Ticketmaster API key")
            elif response.status_code != 200:
                raise ConnectionError(f"Ticketmaster API connection failed: {response.status_code}")

            logger.info("Successfully connected to Ticketmaster Discovery API")

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Ticketmaster API: {e}")

    def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Ticketmaster API.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response as dictionary

        Raises:
            requests.exceptions.RequestException: If request fails
        """
        url = f"{self.BASE_URL}{endpoint}"

        # Ensure API key is included
        if params is None:
            params = {}
        params["apikey"] = self.api_key

        try:
            response = requests.get(url, params=params, timeout=self.timeout)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Request to {endpoint} failed: {e}")
            raise

    def search_events(
        self,
        keyword: Optional[str] = None,
        city: Optional[str] = None,
        state_code: Optional[str] = None,
        country_code: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        segment: Optional[str] = None,
        genre: Optional[str] = None,
        size: int = 20,
        page: int = 0,
        sort: str = "date,asc",
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """Search for events on Ticketmaster.

        Args:
            keyword: Search keyword (artist, venue, event name)
            city: City name
            state_code: State code (e.g., "CA", "NY")
            country_code: Country code (ISO 3166-1 alpha-2)
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius: Search radius in miles (requires lat/lng)
            start_date: Start date (ISO 8601 format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)
            end_date: End date (ISO 8601 format)
            segment: Event segment (Music, Sports, etc.)
            genre: Event genre
            size: Number of results per page (max 200)
            page: Page number
            sort: Sort order (date,asc | date,desc | name,asc | name,desc)
            **kwargs: Additional search parameters

        Returns:
            List of event dictionaries
        """
        params = {
            "countryCode": country_code or self.country_code,
            "locale": self.locale,
            "size": min(size, 200),
            "page": page,
            "sort": sort,
        }

        # Add optional search parameters
        if keyword:
            params["keyword"] = keyword
        if city:
            params["city"] = city
        if state_code:
            params["stateCode"] = state_code
        if latitude and longitude:
            params["latlong"] = f"{latitude},{longitude}"
            if radius:
                params["radius"] = radius
                params["unit"] = "miles"
        if start_date:
            params["startDateTime"] = start_date
        if end_date:
            params["endDateTime"] = end_date
        if segment:
            params["segmentName"] = segment
        if genre:
            params["genreName"] = genre

        # Add any additional parameters
        params.update(kwargs)

        try:
            data = self._make_request(self.ENDPOINTS["events_search"], params)

            # Extract events from embedded response
            events = data.get("_embedded", {}).get("events", [])

            logger.info(
                f"Found {len(events)} events " f"(page {page}, keyword: {keyword}, city: {city})"
            )
            return events

        except Exception as e:
            logger.error(f"Event search failed: {e}")
            return []

    @requires_license
    def get_event_details(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific event.

        Args:
            event_id: Ticketmaster event ID

        Returns:
            Event details dictionary or None if not found
        """
        endpoint = self.ENDPOINTS["event_details"].format(event_id=event_id)

        try:
            data = self._make_request(endpoint, {"locale": self.locale})
            return data

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Event not found: {event_id}")
                return None
            raise

    def search_venues(
        self,
        keyword: Optional[str] = None,
        city: Optional[str] = None,
        state_code: Optional[str] = None,
        country_code: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius: Optional[int] = None,
        size: int = 20,
        page: int = 0,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """Search for venues on Ticketmaster.

        Args:
            keyword: Search keyword (venue name)
            city: City name
            state_code: State code
            country_code: Country code
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius: Search radius in miles
            size: Number of results per page (max 200)
            page: Page number
            **kwargs: Additional search parameters

        Returns:
            List of venue dictionaries
        """
        params = {
            "countryCode": country_code or self.country_code,
            "locale": self.locale,
            "size": min(size, 200),
            "page": page,
        }

        if keyword:
            params["keyword"] = keyword
        if city:
            params["city"] = city
        if state_code:
            params["stateCode"] = state_code
        if latitude and longitude:
            params["latlong"] = f"{latitude},{longitude}"
            if radius:
                params["radius"] = radius
                params["unit"] = "miles"

        params.update(kwargs)

        try:
            data = self._make_request(self.ENDPOINTS["venues_search"], params)
            venues = data.get("_embedded", {}).get("venues", [])

            logger.info(f"Found {len(venues)} venues (keyword: {keyword}, city: {city})")
            return venues

        except Exception as e:
            logger.error(f"Venue search failed: {e}")
            return []

    @requires_license
    def get_venue_details(self, venue_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific venue.

        Args:
            venue_id: Ticketmaster venue ID

        Returns:
            Venue details dictionary or None if not found
        """
        endpoint = self.ENDPOINTS["venue_details"].format(venue_id=venue_id)

        try:
            data = self._make_request(endpoint, {"locale": self.locale})
            return data

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Venue not found: {venue_id}")
                return None
            raise

    def extract_event_info(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured information from event data.

        Args:
            event: Raw event data from API

        Returns:
            Dictionary with extracted event information
        """
        info = {
            "event_id": event.get("id"),
            "name": event.get("name"),
            "url": event.get("url"),
            "locale": event.get("locale"),
        }

        # Dates
        dates = event.get("dates", {})
        start = dates.get("start", {})
        info["start_date"] = start.get("localDate")
        info["start_time"] = start.get("localTime")
        info["timezone"] = dates.get("timezone")
        info["status"] = dates.get("status", {}).get("code")

        # Sales information
        sales = event.get("sales", {})
        public_sales = sales.get("public", {})
        info["sale_start"] = public_sales.get("startDateTime")
        info["sale_end"] = public_sales.get("endDateTime")

        # Price ranges
        price_ranges = event.get("priceRanges", [])
        if price_ranges:
            pr = price_ranges[0]
            info["price_min"] = pr.get("min")
            info["price_max"] = pr.get("max")
            info["currency"] = pr.get("currency")
        else:
            info["price_min"] = None
            info["price_max"] = None
            info["currency"] = None

        # Classifications
        classifications = event.get("classifications", [])
        if classifications:
            c = classifications[0]
            info["segment"] = c.get("segment", {}).get("name")
            info["genre"] = c.get("genre", {}).get("name")
            info["subgenre"] = c.get("subGenre", {}).get("name")
            info["type"] = c.get("type", {}).get("name")
            info["subtype"] = c.get("subType", {}).get("name")
        else:
            info["segment"] = None
            info["genre"] = None
            info["subgenre"] = None
            info["type"] = None
            info["subtype"] = None

        # Venue information
        embedded = event.get("_embedded", {})
        venues = embedded.get("venues", [])
        if venues:
            venue = venues[0]
            info["venue_id"] = venue.get("id")
            info["venue_name"] = venue.get("name")
            info["venue_city"] = venue.get("city", {}).get("name")
            info["venue_state"] = venue.get("state", {}).get("stateCode")
            info["venue_country"] = venue.get("country", {}).get("countryCode")

            location = venue.get("location", {})
            info["venue_latitude"] = location.get("latitude")
            info["venue_longitude"] = location.get("longitude")
        else:
            info["venue_id"] = None
            info["venue_name"] = None
            info["venue_city"] = None
            info["venue_state"] = None
            info["venue_country"] = None
            info["venue_latitude"] = None
            info["venue_longitude"] = None

        # Attractions (artists, teams, etc.)
        attractions = embedded.get("attractions", [])
        if attractions:
            attraction_names = [a.get("name") for a in attractions if a.get("name")]
            info["attractions"] = ", ".join(attraction_names)
            info["attraction_count"] = len(attractions)
        else:
            info["attractions"] = None
            info["attraction_count"] = 0

        return info

    def fetch(
        self,
        keyword: Optional[str] = None,
        city: Optional[str] = None,
        state_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        segment: Optional[str] = None,
        max_results: int = 100,
        **kwargs,
    ) -> pd.DataFrame:
        """Fetch events data for analysis.

        Main entry point for gathering comprehensive events data.

        Args:
            keyword: Search keyword
            city: City name
            state_code: State code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            segment: Event segment filter
            max_results: Maximum number of results to fetch
            **kwargs: Additional search parameters

        Returns:
            DataFrame with event data
        """
        all_events = []
        page = 0
        page_size = min(200, max_results)

        while len(all_events) < max_results:
            # Search for events
            events = self.search_events(
                keyword=keyword,
                city=city,
                state_code=state_code,
                start_date=start_date,
                end_date=end_date,
                segment=segment,
                size=page_size,
                page=page,
                **kwargs,
            )

            if not events:
                break

            # Extract information from each event
            for event in events:
                if len(all_events) >= max_results:
                    break

                event_info = self.extract_event_info(event)
                event_info["fetched_at"] = datetime.now(UTC).isoformat()
                all_events.append(event_info)

            # Check if there are more pages
            if len(events) < page_size:
                break

            page += 1

        # Create DataFrame
        df = pd.DataFrame(all_events)

        logger.info(
            f"Fetched {len(df)} events " f"(keyword: {keyword}, city: {city}, segment: {segment})"
        )

        return df
