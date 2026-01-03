# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2025 KR-Labs Foundation. All rights reserved.
# Licensed under Apache License 2.0 (see LICENSE file for details)

"""
GDELT (Global Database of Events, Language, and Tone) Connector.

Provides access to:
- GDELT Doc API: Article search and sentiment analysis (FREE - Community Tier)
- GDELT BigQuery: Historical event data analysis (ENTERPRISE TIER ONLY)
- Real-time global media monitoring (100+ languages)
- Tone and sentiment scoring
- Theme and entity extraction

Documentation: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
BigQuery: https://blog.gdeltproject.org/gdelt-2-0-now-in-google-bigquery/

Tier Access:
- Community Tier: Doc API (free, no setup required)
- Professional Tier: Doc API only
- Enterprise Tier: Doc API + BigQuery (historical data 1979-present)
"""

import json
from datetime import datetime, timedelta, UTC
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

from krl_data_connectors.base_dispatcher_connector import BaseDispatcherConnector
from krl_data_connectors.core import DataTier
from krl_data_connectors.licensed_connector_mixin import LicensedConnectorMixin, requires_license


class GDELTConnector(LicensedConnectorMixin, BaseDispatcherConnector):
    """
    Connector for GDELT (Global Database of Events, Language, and Tone).

    GDELT monitors global news media in 100+ languages and identifies events,
    sentiment, themes, and entities mentioned in articles worldwide.

    Key Features:
    - Real-time article search across global media
    - Sentiment/tone analysis (positive, negative, neutral)
    - Theme extraction (topics, entities, organizations)
    - Timeline analysis (trending topics over time)
    - Geographic coverage analysis
    - BigQuery integration for historical analysis

    Uses the dispatcher pattern to route requests based on the 'data_type' parameter.
    """

    # Registry name for license validation
    _connector_name = "GDELT"

    """
    API Endpoints:
    - Doc API v2.0: Article search and analysis (No API key required - free tier)
    - BigQuery: Historical event data (Requires Google Cloud credentials)

    Rate Limits:
    - Doc API: ~250 requests/15 minutes (free tier)
    - BigQuery: Based on Google Cloud quotas

    Example Usage:
        >>> connector = GDELTConnector()
        >>> # Using dispatcher pattern
        >>> articles = connector.fetch(
        ...     data_type='articles',
        ...     query="climate change",
        ...     max_records=10
        ... )
        >>> # Or call methods directly
        >>> articles = connector.get_articles(
        ...     query="climate change",
        ...     mode="ArtList",
        ...     max_records=10
        ... )
        >>> # Get sentiment analysis
        >>> sentiment = connector.get_sentiment(
        ...     query="renewable energy",
        ...     timespan="7d"
        ... )
        >>> # Extract themes
        >>> themes = connector.get_themes(
        ...     query="artificial intelligence",
        ...     mode="TimelineVol"
        ... )
    """

    # Dispatcher configuration
    DISPATCH_PARAM = "data_type"
    DISPATCH_MAP = {
        "articles": "get_articles",
        "sentiment": "get_sentiment",
        "themes": "get_themes",
        "timeline": "get_timeline",
        "geographic": "get_geographic_coverage",
    }

    BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
    BIGQUERY_PROJECT = "gdelt-bq"
    BIGQUERY_DATASET = "gdeltv2"

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 3600,
        timeout: int = 30,
        max_retries: int = 3,
        use_bigquery: bool = False,
    ):
        """
        Initialize GDELT connector.

        Args:
            api_key: Not required for Doc API (optional for BigQuery)
            cache_dir: Directory for cache files
            cache_ttl: Cache time-to-live in seconds (default: 1 hour)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            use_bigquery: Enable BigQuery integration (requires Google Cloud setup)
        """
        super().__init__(
            api_key=api_key,
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.use_bigquery = use_bigquery
        self._bigquery_client = None

        # Wrap query_bigquery to add validation
        if hasattr(self.__class__, "_original_query_bigquery"):
            # Already wrapped
            pass
        else:
            # Store original method
            self.__class__._original_query_bigquery = self.__class__.query_bigquery

            # Create wrapper with validation
            def validated_query_bigquery(self, query=None, sql_query=None, max_results=1000):
                """Wrapper that validates SQL before executing query."""
                # Use query parameter, fallback to sql_query for backward compatibility
                final_query = query or sql_query
                if not final_query:
                    raise ValueError("query parameter is required")

                # SQL Injection Prevention: Check for dangerous SQL keywords
                dangerous_keywords = [
                    "DROP TABLE",
                    "DELETE FROM",
                    "TRUNCATE",
                    "ALTER TABLE",
                    "CREATE TABLE",
                    "INSERT INTO",
                    "UPDATE ",
                ]
                query_upper = final_query.upper()

                for keyword in dangerous_keywords:
                    if keyword in query_upper:
                        raise ValueError(
                            f"Potentially dangerous SQL keyword detected: {keyword}. Use parameterized queries instead."
                        )

                # Call original method
                return self.__class__._original_query_bigquery(
                    self, query=query, sql_query=sql_query, max_results=max_results
                )

            # Replace method with validated version
            self.__class__.query_bigquery = validated_query_bigquery

        if use_bigquery:
            self._init_bigquery()

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from configuration.

        GDELT Doc API doesn't require an API key (free tier).
        BigQuery requires Google Cloud credentials.

        Returns:
            API key or None
        """
        return self.config.get("GDELT_API_KEY")

    def _init_bigquery(self):
        """Initialize Google BigQuery client for historical data access."""
        try:
            from google.cloud import bigquery

            self._bigquery_client = bigquery.Client()
            self.logger.info("BigQuery client initialized for GDELT historical data")
        except ImportError:
            self.logger.error(
                "google-cloud-bigquery not installed. "
                "Install with: pip install google-cloud-bigquery"
            )
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize BigQuery client: {e}")
            raise

    def connect(self) -> None:
        """
        Establish connection to GDELT.

        GDELT Doc API is always available (no authentication required).
        Tests connection with a simple query.
        """
        try:
            # Test connection with a simple query
            test_params = {
                "query": "test",
                "mode": "ArtList",
                "maxrecords": "1",
                "format": "json",
            }

            response = self._gdelt_request(test_params)
            self.logger.info("Successfully connected to GDELT Doc API")

        except Exception as e:
            self.logger.error(f"Failed to connect to GDELT: {e}")
            raise

    def _gdelt_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make request to GDELT Doc API with improved error handling.

        Args:
            params: Query parameters

        Returns:
            API response as dictionary
        """
        import requests

        try:
            # Make direct request to avoid parent's JSON parsing issues
            session = self._init_session()

            # Log the request
            self.logger.info(
                "Making GDELT API request", extra={"url": self.BASE_URL, "params": params}
            )

            # Make request
            response = session.get(self.BASE_URL, params=params, timeout=self.timeout)
            response.raise_for_status()

            # Check if response is empty
            if not response.text or response.text.strip() == "":
                self.logger.error("Empty response from GDELT API")
                raise ValueError("GDELT API returned empty response")

            # Parse JSON
            try:
                data = response.json()
            except requests.exceptions.JSONDecodeError as e:
                self.logger.error(
                    f"Failed to parse JSON response",
                    extra={"error": str(e), "response_text": response.text[:500]},
                )
                raise ValueError(
                    f"GDELT API returned invalid JSON: {e}. "
                    f"Response snippet: {response.text[:100]}"
                )

            return data

        except requests.exceptions.HTTPError as e:
            self.logger.error(
                "HTTP error from GDELT API",
                extra={"status_code": e.response.status_code if e.response else None},
            )
            raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise

    @requires_license
    def get_articles(
        self,
        query: str,
        mode: str = "ArtList",
        max_records: int = 250,
        timespan: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        sort: str = "DateDesc",
    ) -> List[Dict[str, Any]]:
        """
        Search for articles matching query.

        Args:
            query: Search query (keywords, phrases, Boolean operators)
            mode: Output mode (ArtList, TimelineVol, TimelineTone, etc.)
            max_records: Maximum articles to return (1-250)
            timespan: Time range (e.g., "7d" for 7 days, "12h" for 12 hours)
            start_date: Start date (YYYYMMDDHHMMSS format)
            end_date: End date (YYYYMMDDHHMMSS format)
            sort: Sort order (DateDesc, DateAsc, etc.)

        Returns:
            List of articles with metadata

        Example:
            >>> articles = connector.get_articles(
            ...     query="climate change renewable energy",
            ...     timespan="30d",
            ...     max_records=50
            ... )
        """
        params = {
            "query": query,
            "mode": mode,
            "maxrecords": str(max_records),
            "format": "json",
            "sort": sort,
        }

        if timespan:
            params["timespan"] = timespan
        if start_date:
            params["startdatetime"] = start_date
        if end_date:
            params["enddatetime"] = end_date

        self.logger.info(
            f"Fetching GDELT articles",
            extra={"query": query, "mode": mode, "max_records": max_records},
        )

        response = self._gdelt_request(params)

        # Extract articles from response
        articles = response.get("articles", [])

        # Sanitize article data to prevent XSS
        import html

        for article in articles:
            if "title" in article:
                article["title"] = html.escape(str(article["title"]))
            if "description" in article and article["description"]:
                article["description"] = html.escape(str(article["description"]))

        self.logger.info(f"Retrieved {len(articles)} articles from GDELT")

        return articles

    @requires_license
    def get_sentiment(
        self,
        query: str,
        timespan: str = "7d",
        mode: str = "TimelineTone",
    ) -> Dict[str, Any]:
        """
        Get sentiment/tone analysis for query.

        Analyzes the tone (positive, negative, neutral) of articles
        matching the query over time.

        Args:
            query: Search query
            timespan: Time range (e.g., "7d", "30d", "12h")
            mode: Analysis mode (TimelineTone recommended for sentiment)

        Returns:
            Sentiment analysis data with tone scores

        Example:
            >>> sentiment = connector.get_sentiment(
            ...     query="stock market",
            ...     timespan="14d"
            ... )
            >>> # Tone scores: -100 (very negative) to +100 (very positive)
        """
        params = {
            "query": query,
            "mode": mode,
            "timespan": timespan,
            "format": "json",
        }

        self.logger.info(
            f"Fetching sentiment analysis",
            extra={"query": query, "timespan": timespan},
        )

        response = self._gdelt_request(params)

        return response

    @requires_license
    def get_themes(
        self,
        query: str,
        timespan: str = "7d",
        mode: str = "TimelineVol",
        max_records: int = 250,
    ) -> Dict[str, Any]:
        """
        Extract themes and topics from articles.

        Identifies major themes, entities, and organizations mentioned
        in articles matching the query.

        Args:
            query: Search query
            timespan: Time range
            mode: Analysis mode (TimelineVol for volume, TimelineTone for sentiment)
            max_records: Maximum records to analyze

        Returns:
            Theme analysis data

        Example:
            >>> themes = connector.get_themes(
            ...     query="artificial intelligence healthcare",
            ...     timespan="30d"
            ... )
        """
        params = {
            "query": query,
            "mode": mode,
            "timespan": timespan,
            "maxrecords": str(max_records),
            "format": "json",
        }

        self.logger.info(
            f"Extracting themes",
            extra={"query": query, "timespan": timespan},
        )

        response = self._gdelt_request(params)

        return response

    @requires_license
    def get_timeline(
        self,
        query: str,
        timespan: str = "30d",
        mode: str = "TimelineVol",
    ) -> Dict[str, Any]:
        """
        Get timeline of article volume and sentiment.

        Tracks how media coverage of a topic changes over time,
        including volume and tone trends.

        Args:
            query: Search query
            timespan: Time range
            mode: Timeline mode (TimelineVol, TimelineTone, TimelineVolInfo)

        Returns:
            Timeline data with timestamps and metrics

        Example:
            >>> timeline = connector.get_timeline(
            ...     query="election 2024",
            ...     timespan="90d",
            ...     mode="TimelineTone"
            ... )
        """
        params = {
            "query": query,
            "mode": mode,
            "timespan": timespan,
            "format": "json",
        }

        self.logger.info(
            f"Fetching timeline",
            extra={"query": query, "timespan": timespan, "mode": mode},
        )

        response = self._gdelt_request(params)

        return response

    @requires_license
    def get_geographic_coverage(
        self,
        query: str,
        timespan: str = "7d",
    ) -> Dict[str, Any]:
        """
        Analyze geographic coverage of query.

        Shows which countries and regions are most prominently
        covered in articles matching the query.

        Args:
            query: Search query
            timespan: Time range

        Returns:
            Geographic coverage data

        Example:
            >>> coverage = connector.get_geographic_coverage(
            ...     query="climate summit",
            ...     timespan="14d"
            ... )
        """
        params = {
            "query": query,
            "mode": "ArtGeo",
            "timespan": timespan,
            "format": "json",
        }

        self.logger.info(
            f"Fetching geographic coverage",
            extra={"query": query, "timespan": timespan},
        )

        response = self._gdelt_request(params)

        return response

    def query_bigquery(
        self,
        query: str = None,  # Changed from sql_query to match test expectations
        sql_query: str = None,  # Keep backward compatibility
        max_results: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        Query GDELT historical data via BigQuery.

        Requires BigQuery to be enabled and Google Cloud credentials configured.

        Args:
            query: SQL query for GDELT BigQuery tables (primary parameter)
            sql_query: Alternative parameter name for SQL query (deprecated)
            max_results: Maximum rows to return

        Returns:
            Query results as list of dictionaries

        Example:
            >>> # Query requires BigQuery setup
            >>> connector = GDELTConnector(use_bigquery=True)
            >>> results = connector.query_bigquery('''
            ...     SELECT Actor1Name, COUNT(*) as event_count
            ...     FROM `gdelt-bq.gdeltv2.events`
            ...     WHERE DATE(_PARTITIONTIME) = '2025-01-01'
            ...     GROUP BY Actor1Name
            ...     ORDER BY event_count DESC
            ...     LIMIT 10
            ... ''')

        Note:
            BigQuery queries may incur Google Cloud costs based on data scanned.
            See: https://cloud.google.com/bigquery/pricing
        """
        if not self.use_bigquery:
            raise ValueError("BigQuery not enabled. Initialize with use_bigquery=True")

        if not self._bigquery_client:
            raise RuntimeError("BigQuery client not initialized")

        # Use query parameter, fallback to sql_query for backward compatibility
        final_query = query or sql_query
        if not final_query:
            raise ValueError("query parameter is required")

        # SQL Injection Prevention: Check for dangerous SQL keywords
        dangerous_keywords = [
            "DROP TABLE",
            "DELETE FROM",
            "TRUNCATE",
            "ALTER TABLE",
            "CREATE TABLE",
            "INSERT INTO",
            "UPDATE ",
        ]
        query_upper = final_query.upper()

        for keyword in dangerous_keywords:
            if keyword in query_upper:
                raise ValueError(
                    f"Potentially dangerous SQL keyword detected: {keyword}. Use parameterized queries instead."
                )

        self.logger.info(f"Executing BigQuery query (max {max_results} results)")

        try:
            query_job = self._bigquery_client.query(final_query)
            results = query_job.result(max_results=max_results)

            # Convert to list of dictionaries
            data = [dict(row) for row in results]

            self.logger.info(f"BigQuery returned {len(data)} rows")

            return data

        except Exception as e:
            self.logger.error(f"BigQuery query failed: {e}")
            raise

    # fetch() method inherited from BaseDispatcherConnector
