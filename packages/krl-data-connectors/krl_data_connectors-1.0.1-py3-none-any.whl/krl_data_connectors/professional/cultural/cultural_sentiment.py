# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ and KRL Data Connectors™ are trademarks of Deloatch, Williams, Faison, & Parker, LLLP.
# Deloatch, Williams, Faison, & Parker, LLLP
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
D39 Cultural Sentiment Connector - Yelp Integration
=================================================

Extracts cultural sentiment data from Yelp Fusion API.
Analyzes business reviews, cultural indicators, and sentiment patterns.
"""

import logging
import re
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.base_connector import BaseConnector
from krl_data_connectors.core import DataTier
from krl_data_connectors.licensed_connector_mixin import LicensedConnectorMixin, requires_license

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from textblob import TextBlob

    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False


logger = logging.getLogger(__name__)


class CulturalSentimentConnector(LicensedConnectorMixin, BaseConnector):
    """Connector for Yelp Fusion API to extract cultural sentiment data.

    This connector interfaces with the Yelp Fusion API v3 to gather business
    information, reviews, and cultural indicators for sentiment analysis.

    Features:
    - Business search with location and category filters
    - Business details extraction (ratings, reviews, photos)
    - Review fetching with sentiment analysis (TextBlob)
    - Cultural indicator extraction (diversity, authenticity, cuisine types)
    - Aggregated sentiment metrics by location

    API Documentation: https://www.yelp.com/developers/documentation/v3
    """

    # Registry name for license validation
    _connector_name = "Cultural_Sentiment"

    BASE_NAME = "CulturalSentiment"
    BASE_URL = "https://api.yelp.com/v3"

    ENDPOINTS = {
        "business_search": "/businesses/search",
        "business_details": "/businesses/{business_id}",
        "business_reviews": "/businesses/{business_id}/reviews",
    }

    # Cultural categories of interest
    CULTURAL_CATEGORIES = [
        "restaurants",
        "arts",
        "museums",
        "theaters",
        "galleries",
        "culturalcenter",
        "festivals",
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        enable_sentiment: bool = True,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 86400,  # 24 hours
        timeout: int = 30,
        max_retries: int = 3,
        **kwargs,
    ):
        """Initialize Cultural Sentiment Connector.

        Args:
            api_key: Yelp Fusion API key
            enable_sentiment: Enable TextBlob sentiment analysis
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

        self.enable_sentiment = enable_sentiment

        if self.enable_sentiment and not TEXTBLOB_AVAILABLE:
            logger.warning("TextBlob not available. Sentiment analysis disabled.")
            self.enable_sentiment = False

        # Cache for reviews to avoid re-fetching
        self._review_cache: Dict[str, List[Dict]] = {}

        logger.info(
            f"Cultural Sentiment connector initialized (sentiment: {self.enable_sentiment})"
        )

    def _get_api_key(self) -> Optional[str]:
        """Get API key from configuration.

        Returns:
            API key string or None
        """
        return self.api_key

    def connect(self) -> None:
        """Establish connection to Yelp API.

        Tests the connection by making a simple search request.

        Raises:
            ConnectionError: If connection fails
            ValueError: If API key is missing
        """
        if not self.api_key:
            raise ValueError("Yelp API key is required. Get one at https://www.yelp.com/developers")

        try:
            # Test connection with a simple search
            test_url = f"{self.BASE_URL}{self.ENDPOINTS['business_search']}"
            headers = {"Authorization": f"Bearer {self.api_key}"}

            response = requests.get(
                test_url,
                headers=headers,
                params={"location": "San Francisco", "limit": 1},
                timeout=self.timeout,
            )

            if response.status_code == 401:
                raise ValueError("Invalid Yelp API key")
            elif response.status_code != 200:
                raise ConnectionError(f"Yelp API connection failed: {response.status_code}")

            logger.info("Successfully connected to Yelp Fusion API")

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Yelp API: {e}")

    def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, method: str = "GET"
    ) -> Dict[str, Any]:
        """Make authenticated request to Yelp API.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            method: HTTP method (GET, POST, etc.)

        Returns:
            JSON response as dictionary

        Raises:
            requests.exceptions.RequestException: If request fails
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            else:
                response = requests.post(url, headers=headers, json=params, timeout=self.timeout)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Request to {endpoint} failed: {e}")
            raise

    def search_businesses(
        self,
        location: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        categories: Optional[List[str]] = None,
        radius: int = 10000,  # meters
        limit: int = 50,
        sort_by: str = "best_match",
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """Search for businesses on Yelp.

        Args:
            location: Location string (e.g., "San Francisco, CA")
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            categories: List of category aliases to filter by
            radius: Search radius in meters (max 40000)
            limit: Number of results to return (max 50 per request)
            sort_by: Sort criteria (best_match, rating, review_count, distance)
            **kwargs: Additional search parameters

        Returns:
            List of business dictionaries

        Raises:
            ValueError: If neither location nor coordinates provided
        """
        if not location and not (latitude and longitude):
            raise ValueError("Must provide either location or coordinates")

        params = {
            "limit": min(limit, 50),
            "sort_by": sort_by,
            "radius": min(radius, 40000),
        }

        if location:
            params["location"] = location
        else:
            params["latitude"] = latitude
            params["longitude"] = longitude

        if categories:
            params["categories"] = ",".join(categories)

        # Add any additional parameters
        params.update(kwargs)

        try:
            data = self._make_request(self.ENDPOINTS["business_search"], params)
            businesses = data.get("businesses", [])

            logger.info(
                f"Found {len(businesses)} businesses for location: {location or f'({latitude}, {longitude})'}"
            )
            return businesses

        except Exception as e:
            logger.error(f"Business search failed: {e}")
            return []

    @requires_license
    def get_business_details(self, business_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific business.

        Args:
            business_id: Yelp business ID

        Returns:
            Business details dictionary or None if not found
        """
        endpoint = self.ENDPOINTS["business_details"].format(business_id=business_id)

        try:
            data = self._make_request(endpoint)
            return data

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Business not found: {business_id}")
                return None
            raise

    @requires_license
    def get_business_reviews(
        self, business_id: str, locale: str = "en_US", use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """Get reviews for a specific business.

        Args:
            business_id: Yelp business ID
            locale: Locale for reviews
            use_cache: Whether to use cached reviews

        Returns:
            List of review dictionaries
        """
        # Check cache first
        if use_cache and business_id in self._review_cache:
            return self._review_cache[business_id]

        endpoint = self.ENDPOINTS["business_reviews"].format(business_id=business_id)
        params = {"locale": locale}

        try:
            data = self._make_request(endpoint, params)
            reviews = data.get("reviews", [])

            # Cache the reviews
            if use_cache:
                self._review_cache[business_id] = reviews

            logger.debug(f"Retrieved {len(reviews)} reviews for business: {business_id}")
            return reviews

        except Exception as e:
            logger.error(f"Failed to get reviews for {business_id}: {e}")
            return []

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text using TextBlob.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with polarity and subjectivity scores
            - polarity: -1 (negative) to 1 (positive)
            - subjectivity: 0 (objective) to 1 (subjective)
        """
        if not self.enable_sentiment or not text:
            return {"polarity": 0.0, "subjectivity": 0.0}

        try:
            blob = TextBlob(text)
            return {
                "polarity": blob.sentiment.polarity,
                "subjectivity": blob.sentiment.subjectivity,
            }
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"polarity": 0.0, "subjectivity": 0.0}

    def extract_cultural_indicators(self, business: Dict[str, Any]) -> Dict[str, Any]:
        """Extract cultural indicators from business data.

        Analyzes business information to identify cultural characteristics:
        - Diversity indicators (international cuisine, multicultural elements)
        - Authenticity markers (traditional, heritage, family-owned)
        - Cultural categories (arts, music, food traditions)
        - Atmosphere descriptors

        Args:
            business: Business data dictionary

        Returns:
            Dictionary of cultural indicators
        """
        indicators = {
            "has_diversity_keywords": False,
            "has_authenticity_keywords": False,
            "cuisine_types": [],
            "cultural_categories": [],
            "atmosphere_tags": [],
        }

        # Extract text fields for analysis
        name = business.get("name", "").lower()
        categories = business.get("categories", [])

        # Diversity keywords
        diversity_keywords = [
            "international",
            "ethnic",
            "multicultural",
            "fusion",
            "global",
            "world",
            "diverse",
            "immigrant",
        ]

        # Authenticity keywords
        authenticity_keywords = [
            "traditional",
            "authentic",
            "original",
            "heritage",
            "family-owned",
            "artisan",
            "homemade",
            "local",
        ]

        # Check name and categories for keywords
        full_text = name + " " + " ".join([c.get("title", "").lower() for c in categories])

        indicators["has_diversity_keywords"] = any(kw in full_text for kw in diversity_keywords)
        indicators["has_authenticity_keywords"] = any(
            kw in full_text for kw in authenticity_keywords
        )

        # Extract cuisine types from categories
        cuisine_patterns = [
            "chinese",
            "japanese",
            "korean",
            "thai",
            "vietnamese",
            "indian",
            "mexican",
            "italian",
            "french",
            "greek",
            "mediterranean",
            "middle eastern",
            "african",
            "caribbean",
            "latin american",
            "ethiopian",
            "persian",
            "moroccan",
        ]

        for category in categories:
            title_lower = category.get("title", "").lower()
            alias = category.get("alias", "").lower()

            # Check for cuisine types
            for cuisine in cuisine_patterns:
                if cuisine in title_lower or cuisine in alias:
                    indicators["cuisine_types"].append(cuisine.title())

            # Check for cultural categories
            for cultural_cat in self.CULTURAL_CATEGORIES:
                if cultural_cat in alias:
                    indicators["cultural_categories"].append(cultural_cat)

        # Remove duplicates
        indicators["cuisine_types"] = list(set(indicators["cuisine_types"]))
        indicators["cultural_categories"] = list(set(indicators["cultural_categories"]))

        return indicators

    def fetch(
        self,
        location: str,
        categories: Optional[List[str]] = None,
        radius: int = 10000,
        limit: int = 50,
        include_reviews: bool = True,
        **kwargs,
    ) -> pd.DataFrame:
        """Fetch cultural sentiment data for a location.

        Main entry point for gathering comprehensive cultural data.

        Args:
            location: Location string (e.g., "San Francisco, CA")
            categories: List of Yelp category aliases to filter
            radius: Search radius in meters
            limit: Maximum number of businesses to fetch
            include_reviews: Whether to fetch and analyze reviews
            **kwargs: Additional search parameters

        Returns:
            DataFrame with business data, sentiment scores, and cultural indicators
        """
        # Search for businesses
        businesses = self.search_businesses(
            location=location,
            categories=categories or self.CULTURAL_CATEGORIES,
            radius=radius,
            limit=limit,
            **kwargs,
        )

        if not businesses:
            logger.warning(f"No businesses found for location: {location}")
            return pd.DataFrame()

        # Process each business
        results = []

        for business in businesses:
            business_id = business.get("id")

            # Base business data
            row = {
                "business_id": business_id,
                "name": business.get("name"),
                "rating": business.get("rating"),
                "review_count": business.get("review_count"),
                "price": business.get("price"),
                "latitude": business.get("coordinates", {}).get("latitude"),
                "longitude": business.get("coordinates", {}).get("longitude"),
                "address": ", ".join(business.get("location", {}).get("display_address", [])),
                "phone": business.get("phone"),
                "url": business.get("url"),
                "is_closed": business.get("is_closed", False),
            }

            # Add categories
            categories_list = [c.get("title") for c in business.get("categories", [])]
            row["categories"] = ", ".join(categories_list)

            # Extract cultural indicators
            indicators = self.extract_cultural_indicators(business)
            row.update(
                {
                    "has_diversity": indicators["has_diversity_keywords"],
                    "has_authenticity": indicators["has_authenticity_keywords"],
                    "cuisine_types": ", ".join(indicators["cuisine_types"]),
                    "cultural_categories": ", ".join(indicators["cultural_categories"]),
                }
            )

            # Fetch and analyze reviews if requested
            if include_reviews and business_id:
                reviews = self.get_business_reviews(business_id)

                if reviews:
                    # Aggregate sentiment from reviews
                    sentiments = []
                    for review in reviews:
                        review_text = review.get("text", "")
                        if review_text:
                            sentiment = self.analyze_sentiment(review_text)
                            sentiments.append(sentiment)

                    if sentiments:
                        avg_polarity = sum(s["polarity"] for s in sentiments) / len(sentiments)
                        avg_subjectivity = sum(s["subjectivity"] for s in sentiments) / len(
                            sentiments
                        )

                        row["sentiment_polarity"] = round(avg_polarity, 3)
                        row["sentiment_subjectivity"] = round(avg_subjectivity, 3)
                        row["sentiment_sample_size"] = len(sentiments)
                    else:
                        row["sentiment_polarity"] = None
                        row["sentiment_subjectivity"] = None
                        row["sentiment_sample_size"] = 0
                else:
                    row["sentiment_polarity"] = None
                    row["sentiment_subjectivity"] = None
                    row["sentiment_sample_size"] = 0

            # Add timestamp
            row["fetched_at"] = datetime.now(UTC).isoformat()

            results.append(row)

        # Create DataFrame
        df = pd.DataFrame(results)

        logger.info(f"Fetched {len(df)} businesses with cultural sentiment data")

        return df
