# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2025 KR-Labs Foundation. All rights reserved.
# Licensed under Apache License 2.0 (see LICENSE file for details)

"""
GDELT (Global Database of Events, Language, and Tone) Connector - Enhanced.

⚠️ **CRITICAL: GDELT Doc API Returns Metadata Only**

GDELT Doc API provides **article discovery** (URLs, titles, timestamps, domains, countries)
but does NOT return full article text. For production media intelligence:

**Discovery Phase** (This Connector):
- Query GDELT Doc API → Get article URLs + metadata
- Max 250 articles per query, 15-minute update cycle
- Free tier, no authentication required

**Enrichment Phase** (Requires External Tool):
- Use Crawl4AI, Newspaper3k, or similar to scrape full content from URLs
- Crawl4AI recommended: 4x faster than alternatives, async scraping
- See: https://github.com/unclecode/crawl4ai for integration

Provides comprehensive access to:
- GDELT Doc API: Article URL discovery + metadata (FREE - Community Tier)
- GDELT Event Database: Structured event data with CAMEO coding (PROFESSIONAL/ENTERPRISE)
- Global Knowledge Graph (GKG): Entity, theme, emotion extraction (PROFESSIONAL/ENTERPRISE)
- GDELT BigQuery: Historical analysis 1979-present (ENTERPRISE TIER)

Documentation:
- Doc API: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
- Event Database: https://blog.gdeltproject.org/gdelt-2-0-our-global-world-in-realtime/
- GKG: https://blog.gdeltproject.org/announcing-the-global-knowledge-graph-gkg/
- BigQuery: https://blog.gdeltproject.org/gdelt-2-0-now-in-google-bigquery/
- Crawl4AI Integration: https://github.com/unclecode/crawl4ai

Tier Access:
- Community Tier: Doc API metadata only (URLs + titles, no full text)
- Professional Tier: Doc API + Event Database CSV exports
- Enterprise Tier: Full BigQuery access (Events + GKG + 45+ years history)

Production Workflow:
1. Query GDELT Doc API for article URLs (this connector)
2. Scrape full content with Crawl4AI (separate integration)
3. Perform NLP analysis on scraped content
4. Optionally: Query Event DB/GKG for structured event data
"""

import json
from datetime import datetime, timedelta, UTC
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote_plus

import pandas as pd

from krl_data_connectors.base_dispatcher_connector import BaseDispatcherConnector
from krl_data_connectors.core import DataTier
from krl_data_connectors.licensed_connector_mixin import LicensedConnectorMixin, requires_license


class GDELTConnectorEnhanced(LicensedConnectorMixin, BaseDispatcherConnector):
    """
    Enhanced connector for GDELT Event Database and Global Knowledge Graph.

    ⚠️ **IMPORTANT: Doc API Returns Metadata Only**

    The free GDELT Doc API returns article **URLs and metadata**, not full text.
    For production use, pair this connector with Crawl4AI for content scraping:

    **Phase 1: Discovery** (This Connector)
    ```python
    articles = connector.get_articles(query="labor strikes", max_records=250)
    # Returns: URLs, titles, domains, dates, countries (NO full text)
    ```
    """

    # Registry name for license validation
    _connector_name = "GDELT"

    """

    **Phase 2: Enrichment** (External Tool - Crawl4AI Recommended)
    ```python
    from crawl4ai import AsyncWebCrawler
    async with AsyncWebCrawler() as crawler:
        for article in articles:
            result = await crawler.arun(article['url'])
            article['full_text'] = result.markdown
    ```

    GDELT Data Tiers:

    1. **Doc API** (FREE - Community Tier)
       - Article URL discovery with metadata
       - 250 articles max per query
       - 15-minute update cycle
       - NO full article text

    2. **Event Database** (PROFESSIONAL/ENTERPRISE Tier)
       - Structured event data (who, what, when, where, why)
       - CAMEO event taxonomy (300+ event types)
       - Actor identification (countries, organizations, people)
       - Geographic coding (latitude/longitude)
       - Goldstein scale (conflict/cooperation scoring)
       - Requires: BigQuery or CSV export processing

    3. **Global Knowledge Graph** (PROFESSIONAL/ENTERPRISE Tier)
       - Named entity extraction
       - Theme/topic identification (3,000+ themes)
       - Emotion/tone analysis via GCAM
       - Location extraction
       - Network/relationship mapping
       - Requires: BigQuery or CSV export processing

    4. **BigQuery** (ENTERPRISE Tier)
       - Historical analysis (1979-present)
       - Custom SQL queries on full GDELT dataset
       - Requires: Google Cloud account + BigQuery setup

    Uses the dispatcher pattern to route requests based on 'data_type' parameter.

    Example Usage:
        >>> connector = GDELTConnectorEnhanced()
        >>>
        >>> # Doc API: Get article URLs + metadata (Community Tier)
        >>> articles = connector.get_articles(
        ...     query="climate policy",
        ...     max_records=250,
        ...     timespan="7d"
        ... )
        >>> # Returns: list of dicts with 'url', 'title', 'domain', 'seendate', etc.
        >>> # Does NOT return: full article text (use Crawl4AI for that)
        >>>
        >>> # Event Database: Get structured events (Professional/Enterprise)
        >>> events = connector.fetch(
        ...     data_type='events',
        ...     actor='USA',
        ...     event_code='14',  # Protest
        ...     date='20250101',
        ...     use_csv=True  # or use_bigquery=True
        ... )
        >>>
        >>> # Global Knowledge Graph: Extract themes/entities (Professional/Enterprise)
        >>> gkg = connector.fetch(
        ...     data_type='gkg',
        ...     theme='ECON_INFLATION',
        ...     date='20250101',
        ...     use_csv=True
        ... )
        >>>
        >>> # Actor Network Analysis: Interaction patterns (Enterprise)
        >>> network = connector.fetch(
        ...     data_type='event_network',
        ...     actor1='USA',
        ...     actor2='CHN',
        ...     start_date='20240101',
        ...     end_date='20241231'
        ... )

    Recommended Workflow:
        1. Use get_articles() to discover URLs
        2. Integrate Crawl4AI to scrape full content from URLs
        3. Perform NLP analysis on scraped content
        4. Optionally: Query Event DB/GKG for structured insights

    Crawl4AI Integration:
        See: https://github.com/unclecode/crawl4ai
        Benchmarks: 4x faster than Firecrawl, 30x faster than sync scraping
    """

    # Dispatcher configuration - Enhanced with new endpoints
    DISPATCH_PARAM = "data_type"
    DISPATCH_MAP = {
        # Original Doc API methods
        "articles": "get_articles",
        "sentiment": "get_sentiment",
        "themes": "get_themes",
        "timeline": "get_timeline",
        "geographic": "get_geographic_coverage",
        # Event Database methods
        "events": "get_events",
        "event_codes": "get_event_codes",
        "actor_events": "get_actor_events",
        "event_network": "get_event_network",
        "conflict_cooperation": "get_conflict_cooperation_score",
        # Global Knowledge Graph methods
        "gkg": "get_gkg",
        "gkg_themes": "get_gkg_themes",
        "gkg_entities": "get_gkg_entities",
        "gkg_emotions": "get_gkg_emotions",
        "gkg_locations": "get_gkg_locations",
        # Advanced analytics
        "event_timeline": "get_event_timeline",
        "actor_network": "get_actor_network",
        "theme_evolution": "get_theme_evolution",
    }

    BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
    BIGQUERY_PROJECT = "gdelt-bq"
    BIGQUERY_DATASET = "gdeltv2"

    # GDELT 2.0 CSV Export URLs
    EVENTS_CSV_BASE = "http://data.gdeltproject.org/gdeltv2/"
    GKG_CSV_BASE = "http://data.gdeltproject.org/gdeltv2/"

    # CAMEO Event Codes (subset - most common)
    CAMEO_EVENT_CODES = {
        # Verbal Cooperation
        "01": "Make public statement",
        "02": "Appeal",
        "03": "Express intent to cooperate",
        "04": "Consult",
        "05": "Engage in diplomatic cooperation",
        "06": "Engage in material cooperation",
        # Material Cooperation
        "07": "Provide aid",
        "08": "Yield",
        # Verbal Conflict
        "09": "Investigate",
        "10": "Demand",
        "11": "Disapprove",
        "12": "Reject",
        "13": "Threaten",
        "14": "Protest",
        "15": "Exhibit force posture",
        # Material Conflict
        "16": "Reduce relations",
        "17": "Coerce",
        "18": "Assault",
        "19": "Fight",
        "20": "Use unconventional mass violence",
    }

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
        Initialize enhanced GDELT connector.

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

        Tests connection with Doc API and verifies BigQuery access if enabled.
        """
        try:
            # Test Doc API connection
            test_params = {
                "query": "test",
                "mode": "ArtList",
                "maxrecords": "1",
                "format": "json",
            }

            response = self._gdelt_request(test_params)
            self.logger.info("Successfully connected to GDELT Doc API")

            # Test BigQuery connection if enabled
            if self.use_bigquery and self._bigquery_client:
                test_query = """
                    SELECT COUNT(*) as row_count
                    FROM `gdelt-bq.gdeltv2.events`
                    WHERE DATE(_PARTITIONTIME) >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
                    LIMIT 1
                """
                result = list(self._bigquery_client.query(test_query).result())
                self.logger.info(
                    f"BigQuery connection verified: {result[0]['row_count']} recent events"
                )

        except Exception as e:
            self.logger.error(f"Failed to connect to GDELT: {e}")
            raise

    def _validate_date(self, date_str: str) -> str:
        """
        Validate and adjust date to prevent timezone issues.

        Args:
            date_str: Date in YYYYMMDD format

        Returns:
            Validated date string

        Raises:
            ValueError: If date is invalid or too far in future
        """
        try:
            query_date = datetime.strptime(date_str, "%Y%m%d")
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}. Use YYYYMMDD format.")

        # Check if date is too far in future (account for UTC)
        today_utc = datetime.now(UTC)
        if query_date > today_utc + timedelta(days=1):
            raise ValueError(
                f"Date {date_str} is in the future. "
                f"Current UTC date: {today_utc.strftime('%Y%m%d')}"
            )

        # Warn if date is very recent (may not have data yet)
        if query_date > today_utc - timedelta(hours=6):
            self.logger.warning(
                f"Date {date_str} is very recent. "
                f"GDELT has 15min update cycle + processing lag. "
                f"Consider using yesterday's date: {(today_utc - timedelta(days=1)).strftime('%Y%m%d')}"
            )

        # Check GDELT 2.0 start date
        gdelt_2_start = datetime(2015, 2, 19)
        if query_date < gdelt_2_start:
            raise ValueError(
                f"Date {date_str} predates GDELT 2.0 (started Feb 19, 2015). "
                f"Use GDELT 1.0 for historical data or query dates after 20150219."
            )

        return date_str

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
            session = self._init_session()

            self.logger.info(
                "Making GDELT API request", extra={"url": self.BASE_URL, "params": params}
            )

            response = session.get(self.BASE_URL, params=params, timeout=self.timeout)
            response.raise_for_status()

            if not response.text or response.text.strip() == "":
                self.logger.error("Empty response from GDELT API")
                raise ValueError("GDELT API returned empty response")

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

    def _download_csv_data(self, url: str) -> pd.DataFrame:
        """
        Download and parse GDELT CSV data with improved error handling.

        Args:
            url: URL to GDELT CSV file (may be gzipped)

        Returns:
            DataFrame with parsed data (empty if download fails)
        """
        import gzip
        from io import BytesIO

        import requests

        try:
            session = self._init_session()

            self.logger.info(f"Downloading CSV from: {url}")
            response = session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Handle gzipped/zipped files
            if url.endswith(".gz") or url.endswith(".zip"):
                data = gzip.decompress(response.content)
                df = pd.read_csv(BytesIO(data), sep="\t", header=None, low_memory=False)
            else:
                df = pd.read_csv(BytesIO(response.content), sep="\t", header=None, low_memory=False)

            if len(df) == 0:
                self.logger.warning(f"CSV download returned 0 rows from {url}")
                self.logger.warning("This may indicate:")
                self.logger.warning("  - No data available for this date")
                self.logger.warning("  - Date outside GDELT 2.0 range (post Feb 2015)")
                self.logger.warning("  - Service temporarily unavailable")
            else:
                self.logger.info(f"Successfully downloaded {len(df)} rows from CSV")

            return df

        except Exception as e:
            self.logger.error(f"Failed to download CSV data from {url}: {e}")
            self.logger.error("Returning empty DataFrame for graceful degradation")
            # Return empty DataFrame instead of raising - allows graceful fallback
            return pd.DataFrame()

    # ============================================================================
    # ORIGINAL DOC API METHODS (from base connector)
    # ============================================================================

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
        Search for articles matching query (returns URLs + metadata, NOT full text).

        ⚠️ **CRITICAL LIMITATION**: GDELT Doc API returns article metadata only.

        **What This Method Returns:**
        - `url`: Article URL (you must scrape this separately)
        - `title`: Headline/title (5-15 words typically)
        - `seendate`: Timestamp when GDELT indexed the article
        - `domain`: Source domain (e.g., "nytimes.com")
        - `language`: ISO 639-1 language code
        - `sourcecountry`: ISO 3166-1 alpha-3 country code
        - `socialimage`: Social media preview image URL (if available)

        **What This Method Does NOT Return:**
        - Full article text/content
        - Article body paragraphs
        - Rich content for deep NLP

        **For Full-Text Analysis:**
        Integrate Crawl4AI to scrape content from returned URLs:
        ```python
        from crawl4ai import AsyncWebCrawler

        articles = connector.get_articles(query="labor strikes", max_records=250)

        async with AsyncWebCrawler() as crawler:
            for article in articles:
                result = await crawler.arun(article['url'])
                article['full_text'] = result.markdown  # Now you have content!
        ```

        See: https://github.com/unclecode/crawl4ai for integration guide

        Args:
            query: Search query (keywords, phrases, Boolean operators)
                   Supports: AND, OR, NOT, quotes, sourcelang:eng, etc.
                   Example: "climate change AND policy AND sourcelang:eng"
            mode: Output mode (default: ArtList for article list)
                  Other modes: TimelineVol, TimelineTone (for aggregated data)
            max_records: Maximum articles to return (1-250, API limit)
            timespan: Time range (e.g., "7d" for 7 days, "12h" for 12 hours)
                      Default: Recent articles if not specified
            start_date: Start date (YYYYMMDDHHMMSS format)
            end_date: End date (YYYYMMDDHHMMSS format)
            sort: Sort order (DateDesc=newest first, DateAsc=oldest first)

        Returns:
            List of article metadata dictionaries (NO full text - use Crawl4AI)

        Example:
            >>> # Get URLs for labor strikes articles
            >>> articles = connector.get_articles(
            ...     query="labor strike OR worker protest AND sourcelang:eng",
            ...     timespan="30d",
            ...     max_records=250
            ... )
            >>> print(f"Found {len(articles)} article URLs")
            >>> print(f"First article: {articles[0]['title']}")
            >>> print(f"URL to scrape: {articles[0]['url']}")
            >>>
            >>> # Next step: Scrape with Crawl4AI for full content
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
        articles = response.get("articles", [])

        # Sanitize article data
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
        """Get sentiment/tone analysis for query."""
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

        return self._gdelt_request(params)

    @requires_license
    def get_themes(
        self,
        query: str,
        timespan: str = "7d",
        mode: str = "TimelineVol",
        max_records: int = 250,
    ) -> Dict[str, Any]:
        """Extract themes and topics from articles."""
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

        return self._gdelt_request(params)

    @requires_license
    def get_timeline(
        self,
        query: str,
        timespan: str = "30d",
        mode: str = "TimelineVol",
    ) -> Dict[str, Any]:
        """Get timeline of article volume and sentiment."""
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

        return self._gdelt_request(params)

    @requires_license
    def get_geographic_coverage(
        self,
        query: str,
        timespan: str = "7d",
    ) -> Dict[str, Any]:
        """Analyze geographic coverage of query."""
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

        return self._gdelt_request(params)

    # ============================================================================
    # EVENT DATABASE METHODS
    # ============================================================================

    @requires_license
    def get_events(
        self,
        date: Optional[str] = None,
        actor: Optional[str] = None,
        event_code: Optional[str] = None,
        country_code: Optional[str] = None,
        max_results: int = 1000,
        use_csv: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Query GDELT Event Database for structured event data.

        The Event Database contains coded events with:
        - CAMEO event taxonomy (300+ event types)
        - Actor identification (Actor1, Actor2)
        - Geographic locations
        - Goldstein conflict/cooperation scores
        - Event attributes and metadata

        Args:
            date: Date in YYYYMMDD format (default: yesterday)
            actor: Country/organization code (e.g., 'USA', 'CHN', 'NATO')
            event_code: CAMEO event code (e.g., '14' for protest, '19' for fight)
            country_code: Country where event occurred
            max_results: Maximum events to return
            use_csv: Use CSV export instead of BigQuery (default: False)

        Returns:
            List of events with full GDELT coding

        Example:
            >>> # Get protests in USA
            >>> events = connector.get_events(
            ...     date='20250101',
            ...     actor='USA',
            ...     event_code='14'  # Protest
            ... )
            >>>
            >>> # Get all China-related events
            >>> events = connector.get_events(
            ...     date='20250101',
            ...     actor='CHN'
            ... )

        Event Record Fields:
            - GLOBALEVENTID: Unique event identifier
            - SQLDATE: Event date (YYYYMMDD)
            - Actor1Code: Primary actor country/org code
            - Actor2Code: Secondary actor code
            - EventCode: CAMEO event type code
            - GoldsteinScale: Conflict(-10) to cooperation(+10) score
            - NumMentions: Number of source articles
            - AvgTone: Average sentiment (-100 to +100)
            - Actor1Geo_Lat/Lon: Event location coordinates
            - SOURCEURL: Source article URL
        """
        if not date:
            # Default to yesterday UTC (safer than today to avoid timezone issues)
            yesterday = datetime.now(UTC) - timedelta(days=1)
            date = yesterday.strftime("%Y%m%d")
            self.logger.info(f"No date provided, using yesterday UTC: {date}")
        else:
            # Validate date format and constraints
            date = self._validate_date(date)

        if use_csv or not self.use_bigquery:
            return self._get_events_from_csv(date, actor, event_code, country_code, max_results)
        else:
            return self._get_events_from_bigquery(
                date, actor, event_code, country_code, max_results
            )

    def _get_events_from_csv(
        self,
        date: str,
        actor: Optional[str],
        event_code: Optional[str],
        country_code: Optional[str],
        max_results: int,
    ) -> List[Dict[str, Any]]:
        """
        Get events from GDELT CSV export files.

        CSV files are updated every 15 minutes with latest events.
        Tries multiple URL formats for robustness.
        """
        # GDELT 2.0 publishes events in 15-minute batches
        # Try multiple URL formats as GDELT structure varies
        year = date[:4]
        csv_urls = [
            f"{self.EVENTS_CSV_BASE}{date}.export.CSV.zip",
            f"http://data.gdeltproject.org/gdeltv2/{year}/{date}.export.CSV.zip",
            f"{self.EVENTS_CSV_BASE}{date}.export.csv.gz",
        ]

        df = None
        for csv_url in csv_urls:
            self.logger.info(f"Trying CSV URL: {csv_url}")
            try:
                df = self._download_csv_data(csv_url)
                if len(df) > 0:
                    self.logger.info(f"Successfully retrieved data from: {csv_url}")
                    break
            except Exception as e:
                self.logger.debug(f"Failed to download from {csv_url}: {e}")
                continue

        if df is None or len(df) == 0:
            self.logger.error(f"Failed to retrieve events for date {date} from any CSV URL")
            self.logger.error("Possible causes:")
            self.logger.error("  1. Date outside GDELT 2.0 range (post Feb 2015)")
            self.logger.error("  2. CSV files not yet available for this date")
            self.logger.error("  3. GDELT service issues")
            self.logger.error("  4. Network connectivity problems")
            return []

        try:

            # Apply column names (58 columns in GDELT 2.0)
            df.columns = self._get_event_column_names()

            # Filter by criteria
            if actor:
                df = df[
                    (df["Actor1Code"].str.contains(actor, na=False))
                    | (df["Actor2Code"].str.contains(actor, na=False))
                ]

            if event_code:
                # Match event code (can be root code like '14' matching '141', '142', etc.)
                df = df[df["EventCode"].str.startswith(event_code, na=False)]

            if country_code:
                df = df[
                    (df["Actor1CountryCode"] == country_code)
                    | (df["Actor2CountryCode"] == country_code)
                ]

            # Limit results
            df = df.head(max_results)

            self.logger.info(f"Retrieved {len(df)} events from CSV")

            return df.to_dict("records")

        except Exception as e:
            self.logger.error(f"Failed to fetch events from CSV: {e}")
            raise

    def _get_events_from_bigquery(
        self,
        date: str,
        actor: Optional[str],
        event_code: Optional[str],
        country_code: Optional[str],
        max_results: int,
    ) -> List[Dict[str, Any]]:
        """Get events from BigQuery with advanced filtering."""
        if not self._bigquery_client:
            raise RuntimeError(
                "BigQuery client not initialized. Use get_events(use_csv=True) instead."
            )

        # Build WHERE clause
        where_clauses = [f"SQLDATE = {date}"]

        if actor:
            where_clauses.append(f"(Actor1Code LIKE '{actor}%' OR Actor2Code LIKE '{actor}%')")

        if event_code:
            where_clauses.append(f"EventCode LIKE '{event_code}%'")

        if country_code:
            where_clauses.append(
                f"(Actor1CountryCode = '{country_code}' OR Actor2CountryCode = '{country_code}')"
            )

        where_clause = " AND ".join(where_clauses)

        query = f"""
            SELECT
                GLOBALEVENTID,
                SQLDATE,
                Actor1Code,
                Actor1Name,
                Actor1CountryCode,
                Actor2Code,
                Actor2Name,
                Actor2CountryCode,
                EventCode,
                EventBaseCode,
                EventRootCode,
                QuadClass,
                GoldsteinScale,
                NumMentions,
                NumSources,
                NumArticles,
                AvgTone,
                Actor1Geo_Lat,
                Actor1Geo_Long,
                ActionGeo_Lat,
                ActionGeo_Long,
                SOURCEURL
            FROM `gdelt-bq.gdeltv2.events`
            WHERE {where_clause}
            ORDER BY NumMentions DESC
            LIMIT {max_results}
        """

        self.logger.info(f"Executing BigQuery event query")

        try:
            query_job = self._bigquery_client.query(query)
            results = query_job.result()

            events = [dict(row) for row in results]

            self.logger.info(f"Retrieved {len(events)} events from BigQuery")

            return events

        except Exception as e:
            self.logger.error(f"BigQuery event query failed: {e}")
            raise

    def _get_event_column_names(self) -> List[str]:
        """
        Get GDELT 2.0 Event Database column names.

        Returns:
            List of 58 column names for GDELT 2.0 events
        """
        return [
            "GLOBALEVENTID",
            "SQLDATE",
            "MonthYear",
            "Year",
            "FractionDate",
            "Actor1Code",
            "Actor1Name",
            "Actor1CountryCode",
            "Actor1KnownGroupCode",
            "Actor1EthnicCode",
            "Actor1Religion1Code",
            "Actor1Religion2Code",
            "Actor1Type1Code",
            "Actor1Type2Code",
            "Actor1Type3Code",
            "Actor2Code",
            "Actor2Name",
            "Actor2CountryCode",
            "Actor2KnownGroupCode",
            "Actor2EthnicCode",
            "Actor2Religion1Code",
            "Actor2Religion2Code",
            "Actor2Type1Code",
            "Actor2Type2Code",
            "Actor2Type3Code",
            "IsRootEvent",
            "EventCode",
            "EventBaseCode",
            "EventRootCode",
            "QuadClass",
            "GoldsteinScale",
            "NumMentions",
            "NumSources",
            "NumArticles",
            "AvgTone",
            "Actor1Geo_Type",
            "Actor1Geo_FullName",
            "Actor1Geo_CountryCode",
            "Actor1Geo_ADM1Code",
            "Actor1Geo_Lat",
            "Actor1Geo_Long",
            "Actor1Geo_FeatureID",
            "Actor2Geo_Type",
            "Actor2Geo_FullName",
            "Actor2Geo_CountryCode",
            "Actor2Geo_ADM1Code",
            "Actor2Geo_Lat",
            "Actor2Geo_Long",
            "Actor2Geo_FeatureID",
            "ActionGeo_Type",
            "ActionGeo_FullName",
            "ActionGeo_CountryCode",
            "ActionGeo_ADM1Code",
            "ActionGeo_Lat",
            "ActionGeo_Long",
            "ActionGeo_FeatureID",
            "DATEADDED",
            "SOURCEURL",
        ]

    @requires_license
    def get_event_codes(self) -> Dict[str, str]:
        """
        Get CAMEO event code taxonomy.

        Returns:
            Dictionary mapping event codes to descriptions

        Example:
            >>> codes = connector.get_event_codes()
            >>> print(codes['14'])  # 'Protest'
            >>> print(codes['19'])  # 'Fight'
        """
        return self.CAMEO_EVENT_CODES.copy()

    @requires_license
    def get_actor_events(
        self,
        actor: str,
        start_date: str,
        end_date: str,
        event_type: Optional[str] = None,
        max_results: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        Get all events involving a specific actor over time period.

        Args:
            actor: Country/organization code (e.g., 'USA', 'CHN')
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            event_type: Optional event code filter
            max_results: Maximum results

        Returns:
            List of events involving the actor

        Example:
            >>> # Get all USA events in January 2025
            >>> events = connector.get_actor_events(
            ...     actor='USA',
            ...     start_date='20250101',
            ...     end_date='20250131'
            ... )
        """
        if not self._bigquery_client:
            raise RuntimeError("This method requires BigQuery. Initialize with use_bigquery=True")

        event_filter = f"AND EventCode LIKE '{event_type}%'" if event_type else ""

        query = f"""
            SELECT
                GLOBALEVENTID,
                SQLDATE,
                Actor1Code,
                Actor1Name,
                Actor2Code,
                Actor2Name,
                EventCode,
                GoldsteinScale,
                NumMentions,
                AvgTone,
                ActionGeo_Lat,
                ActionGeo_Long,
                SOURCEURL
            FROM `gdelt-bq.gdeltv2.events`
            WHERE (Actor1Code LIKE '{actor}%' OR Actor2Code LIKE '{actor}%')
              AND SQLDATE BETWEEN {start_date} AND {end_date}
              {event_filter}
            ORDER BY SQLDATE DESC, NumMentions DESC
            LIMIT {max_results}
        """

        self.logger.info(f"Fetching events for actor: {actor} ({start_date} to {end_date})")

        try:
            query_job = self._bigquery_client.query(query)
            results = query_job.result()

            events = [dict(row) for row in results]

            self.logger.info(f"Retrieved {len(events)} events for {actor}")

            return events

        except Exception as e:
            self.logger.error(f"Actor events query failed: {e}")
            raise

    @requires_license
    def get_event_network(
        self,
        actor1: str,
        actor2: str,
        start_date: str,
        end_date: str,
        min_mentions: int = 5,
    ) -> Dict[str, Any]:
        """
        Analyze interaction network between two actors.

        Identifies all events where actor1 and actor2 interact,
        including event types, frequencies, and sentiment.

        Args:
            actor1: First actor code
            actor2: Second actor code
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            min_mentions: Minimum mentions threshold

        Returns:
            Network analysis data with:
            - events: List of interaction events
            - summary: Aggregated statistics
            - cooperation_score: Overall cooperation level
            - conflict_score: Overall conflict level

        Example:
            >>> # Analyze USA-China interactions
            >>> network = connector.get_event_network(
            ...     actor1='USA',
            ...     actor2='CHN',
            ...     start_date='20240101',
            ...     end_date='20241231'
            ... )
        """
        if not self._bigquery_client:
            raise RuntimeError("This method requires BigQuery")

        query = f"""
            SELECT
                GLOBALEVENTID,
                SQLDATE,
                Actor1Code,
                Actor1Name,
                Actor2Code,
                Actor2Name,
                EventCode,
                GoldsteinScale,
                NumMentions,
                AvgTone,
                SOURCEURL
            FROM `gdelt-bq.gdeltv2.events`
            WHERE (
                (Actor1Code LIKE '{actor1}%' AND Actor2Code LIKE '{actor2}%')
                OR
                (Actor1Code LIKE '{actor2}%' AND Actor2Code LIKE '{actor1}%')
            )
            AND SQLDATE BETWEEN {start_date} AND {end_date}
            AND NumMentions >= {min_mentions}
            ORDER BY SQLDATE DESC
        """

        self.logger.info(f"Analyzing event network: {actor1} <-> {actor2}")

        try:
            query_job = self._bigquery_client.query(query)
            results = query_job.result()

            events = [dict(row) for row in results]

            # Calculate network statistics
            total_events = len(events)
            avg_goldstein = (
                sum(e["GoldsteinScale"] for e in events) / total_events if total_events > 0 else 0
            )
            avg_tone = sum(e["AvgTone"] for e in events) / total_events if total_events > 0 else 0

            cooperation_events = [e for e in events if e["GoldsteinScale"] > 0]
            conflict_events = [e for e in events if e["GoldsteinScale"] < 0]

            network_data = {
                "events": events,
                "summary": {
                    "total_events": total_events,
                    "cooperation_events": len(cooperation_events),
                    "conflict_events": len(conflict_events),
                    "avg_goldstein_score": round(avg_goldstein, 2),
                    "avg_tone": round(avg_tone, 2),
                },
                "cooperation_score": round(avg_goldstein, 2) if avg_goldstein > 0 else 0,
                "conflict_score": round(abs(avg_goldstein), 2) if avg_goldstein < 0 else 0,
            }

            self.logger.info(
                f"Network analysis complete: {total_events} events, "
                f"Goldstein={avg_goldstein:.2f}, Tone={avg_tone:.2f}"
            )

            return network_data

        except Exception as e:
            self.logger.error(f"Event network query failed: {e}")
            raise

    @requires_license
    def get_conflict_cooperation_score(
        self,
        actor: str,
        date: str,
    ) -> Dict[str, float]:
        """
        Calculate conflict/cooperation score for actor on specific date.

        Uses Goldstein scale:
        - Positive scores: Cooperation
        - Negative scores: Conflict
        - Range: -10 (extreme conflict) to +10 (extreme cooperation)

        Args:
            actor: Actor code
            date: Date (YYYYMMDD)

        Returns:
            Dictionary with cooperation/conflict scores

        Example:
            >>> scores = connector.get_conflict_cooperation_score(
            ...     actor='USA',
            ...     date='20250101'
            ... )
            >>> print(scores)
            >>> # {'cooperation': 3.5, 'conflict': -2.1, 'net': 1.4}
        """
        events = self.get_events(date=date, actor=actor, max_results=10000)

        if not events:
            return {"cooperation": 0.0, "conflict": 0.0, "net": 0.0}

        cooperation_scores = [e["GoldsteinScale"] for e in events if e["GoldsteinScale"] > 0]
        conflict_scores = [e["GoldsteinScale"] for e in events if e["GoldsteinScale"] < 0]

        avg_cooperation = (
            sum(cooperation_scores) / len(cooperation_scores) if cooperation_scores else 0.0
        )
        avg_conflict = sum(conflict_scores) / len(conflict_scores) if conflict_scores else 0.0
        net_score = avg_cooperation + avg_conflict

        return {
            "cooperation": round(avg_cooperation, 2),
            "conflict": round(avg_conflict, 2),
            "net": round(net_score, 2),
        }

    # ============================================================================
    # GLOBAL KNOWLEDGE GRAPH (GKG) METHODS
    # ============================================================================

    @requires_license
    def get_gkg(
        self,
        date: Optional[str] = None,
        theme: Optional[str] = None,
        location: Optional[str] = None,
        max_results: int = 1000,
        use_csv: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Query Global Knowledge Graph for entity and theme extraction.

        GKG extracts structured knowledge from articles including:
        - Themes/topics (GDELT taxonomy of 3,000+ themes)
        - Named entities (people, organizations, locations)
        - Emotions and sentiment
        - Geographic locations
        - Event counts and tone

        Args:
            date: Date in YYYYMMDD format (default: yesterday)
            theme: GDELT theme code (e.g., 'ECON_INFLATION', 'ENV_CLIMATECHANGE')
            location: Location name or code
            max_results: Maximum records to return
            use_csv: Use CSV export instead of BigQuery

        Returns:
            List of GKG records with extracted knowledge

        Example:
            >>> # Get climate change articles
            >>> gkg = connector.get_gkg(
            ...     date='20250101',
            ...     theme='ENV_CLIMATECHANGE'
            ... )
            >>>
            >>> # Get articles mentioning specific location
            >>> gkg = connector.get_gkg(
            ...     date='20250101',
            ...     location='Washington, D.C.'
            ... )

        GKG Record Fields:
            - GKGRECORDID: Unique record identifier
            - DATE: Publication date
            - Themes: Semicolon-separated theme list
            - Locations: Geographic mentions
            - Persons: People mentioned
            - Organizations: Organizations mentioned
            - Tone: Overall sentiment score
            - GCAM: Global Content Analysis Measures
            - DocumentIdentifier: Source URL
        """
        if not date:
            # Use yesterday UTC for consistency
            yesterday = datetime.now(UTC) - timedelta(days=1)
            date = yesterday.strftime("%Y%m%d")
            self.logger.info(f"No date provided, using yesterday UTC: {date}")
        else:
            # Validate date
            date = self._validate_date(date)

        if use_csv or not self.use_bigquery:
            return self._get_gkg_from_csv(date, theme, location, max_results)
        else:
            return self._get_gkg_from_bigquery(date, theme, location, max_results)

    def _get_gkg_from_csv(
        self,
        date: str,
        theme: Optional[str],
        location: Optional[str],
        max_results: int,
    ) -> List[Dict[str, Any]]:
        """Get GKG data from CSV export."""
        csv_url = f"{self.GKG_CSV_BASE}{date}.gkg.csv.zip"

        self.logger.info(f"Downloading GKG from CSV: {csv_url}")

        try:
            df = self._download_csv_data(csv_url)

            # Apply GKG column names
            df.columns = self._get_gkg_column_names()

            # Filter by theme
            if theme:
                df = df[df["Themes"].str.contains(theme, na=False, case=False)]

            # Filter by location
            if location:
                df = df[df["Locations"].str.contains(location, na=False, case=False)]

            # Limit results
            df = df.head(max_results)

            self.logger.info(f"Retrieved {len(df)} GKG records from CSV")

            return df.to_dict("records")

        except Exception as e:
            self.logger.error(f"Failed to fetch GKG from CSV: {e}")
            raise

    def _get_gkg_from_bigquery(
        self,
        date: str,
        theme: Optional[str],
        location: Optional[str],
        max_results: int,
    ) -> List[Dict[str, Any]]:
        """Get GKG data from BigQuery."""
        if not self._bigquery_client:
            raise RuntimeError("BigQuery client not initialized")

        where_clauses = [f"DATE = {date}"]

        if theme:
            where_clauses.append(f"Themes LIKE '%{theme}%'")

        if location:
            where_clauses.append(f"Locations LIKE '%{location}%'")

        where_clause = " AND ".join(where_clauses)

        query = f"""
            SELECT
                GKGRECORDID,
                DATE,
                Themes,
                Locations,
                Persons,
                Organizations,
                Tone,
                GCAM,
                DocumentIdentifier
            FROM `gdelt-bq.gdeltv2.gkg`
            WHERE {where_clause}
            LIMIT {max_results}
        """

        self.logger.info(f"Executing BigQuery GKG query")

        try:
            query_job = self._bigquery_client.query(query)
            results = query_job.result()

            gkg_records = [dict(row) for row in results]

            self.logger.info(f"Retrieved {len(gkg_records)} GKG records from BigQuery")

            return gkg_records

        except Exception as e:
            self.logger.error(f"BigQuery GKG query failed: {e}")
            raise

    def _get_gkg_column_names(self) -> List[str]:
        """Get GKG column names."""
        return [
            "GKGRECORDID",
            "DATE",
            "SourceCollectionIdentifier",
            "SourceCommonName",
            "DocumentIdentifier",
            "Counts",
            "V2Counts",
            "Themes",
            "V2Themes",
            "Locations",
            "V2Locations",
            "Persons",
            "V2Persons",
            "Organizations",
            "V2Organizations",
            "V2Tone",
            "Dates",
            "GCAM",
            "SharingImage",
            "RelatedImages",
            "SocialImageEmbeds",
            "SocialVideoEmbeds",
            "Quotations",
            "AllNames",
            "Amounts",
            "TranslationInfo",
            "Extras",
        ]

    @requires_license
    def get_gkg_themes(
        self,
        date: str,
        top_n: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Get most common themes from GKG for a specific date.

        Args:
            date: Date (YYYYMMDD)
            top_n: Number of top themes to return

        Returns:
            List of themes with counts

        Example:
            >>> themes = connector.get_gkg_themes(date='20250101', top_n=20)
        """
        if not self._bigquery_client:
            raise RuntimeError("This method requires BigQuery")

        query = f"""
            SELECT
                theme,
                COUNT(*) as count
            FROM `gdelt-bq.gdeltv2.gkg`,
            UNNEST(SPLIT(Themes, ';')) as theme
            WHERE DATE = {date}
              AND theme != ''
            GROUP BY theme
            ORDER BY count DESC
            LIMIT {top_n}
        """

        self.logger.info(f"Fetching top {top_n} themes for {date}")

        try:
            query_job = self._bigquery_client.query(query)
            results = query_job.result()

            themes = [dict(row) for row in results]

            self.logger.info(f"Retrieved {len(themes)} themes")

            return themes

        except Exception as e:
            self.logger.error(f"GKG themes query failed: {e}")
            raise

    @requires_license
    def get_gkg_entities(
        self,
        date: str,
        entity_type: str = "persons",
        top_n: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Get most mentioned entities from GKG.

        Args:
            date: Date (YYYYMMDD)
            entity_type: Type of entity ('persons', 'organizations', 'locations')
            top_n: Number of top entities to return

        Returns:
            List of entities with mention counts

        Example:
            >>> # Get most mentioned people
            >>> people = connector.get_gkg_entities(
            ...     date='20250101',
            ...     entity_type='persons'
            ... )
        """
        if not self._bigquery_client:
            raise RuntimeError("This method requires BigQuery")

        # Map entity type to GKG column
        entity_columns = {
            "persons": "Persons",
            "organizations": "Organizations",
            "locations": "Locations",
        }

        if entity_type not in entity_columns:
            raise ValueError(f"entity_type must be one of: {list(entity_columns.keys())}")

        column = entity_columns[entity_type]

        query = f"""
            SELECT
                entity,
                COUNT(*) as mentions
            FROM `gdelt-bq.gdeltv2.gkg`,
            UNNEST(SPLIT({column}, ';')) as entity
            WHERE DATE = {date}
              AND entity != ''
            GROUP BY entity
            ORDER BY mentions DESC
            LIMIT {top_n}
        """

        self.logger.info(f"Fetching top {top_n} {entity_type} for {date}")

        try:
            query_job = self._bigquery_client.query(query)
            results = query_job.result()

            entities = [dict(row) for row in results]

            self.logger.info(f"Retrieved {len(entities)} {entity_type}")

            return entities

        except Exception as e:
            self.logger.error(f"GKG entities query failed: {e}")
            raise

    @requires_license
    def get_gkg_emotions(
        self,
        theme: str,
        start_date: str,
        end_date: str,
    ) -> Dict[str, Any]:
        """
        Analyze emotional tone around a theme over time.

        Uses GCAM (Global Content Analysis Measures) to extract
        emotional content from articles.

        Args:
            theme: GDELT theme code
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)

        Returns:
            Emotion analysis data with tone trends

        Example:
            >>> emotions = connector.get_gkg_emotions(
            ...     theme='ECON_INFLATION',
            ...     start_date='20240101',
            ...     end_date='20241231'
            ... )
        """
        if not self._bigquery_client:
            raise RuntimeError("This method requires BigQuery")

        query = f"""
            SELECT
                DATE,
                AVG(CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(0)] AS FLOAT64)) as avg_tone,
                COUNT(*) as article_count
            FROM `gdelt-bq.gdeltv2.gkg`
            WHERE Themes LIKE '%{theme}%'
              AND DATE BETWEEN {start_date} AND {end_date}
            GROUP BY DATE
            ORDER BY DATE
        """

        self.logger.info(f"Analyzing emotions for theme: {theme}")

        try:
            query_job = self._bigquery_client.query(query)
            results = query_job.result()

            emotion_data = [dict(row) for row in results]

            self.logger.info(f"Retrieved emotion data for {len(emotion_data)} days")

            return {
                "theme": theme,
                "date_range": f"{start_date} to {end_date}",
                "emotion_timeline": emotion_data,
            }

        except Exception as e:
            self.logger.error(f"GKG emotions query failed: {e}")
            raise

    @requires_license
    def get_gkg_locations(
        self,
        theme: str,
        date: str,
        top_n: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Get geographic distribution of theme coverage.

        Args:
            theme: GDELT theme code
            date: Date (YYYYMMDD)
            top_n: Number of top locations

        Returns:
            List of locations with article counts

        Example:
            >>> locations = connector.get_gkg_locations(
            ...     theme='TERROR',
            ...     date='20250101'
            ... )
        """
        if not self._bigquery_client:
            raise RuntimeError("This method requires BigQuery")

        query = f"""
            SELECT
                location,
                COUNT(*) as mentions
            FROM `gdelt-bq.gdeltv2.gkg`,
            UNNEST(SPLIT(Locations, ';')) as location
            WHERE Themes LIKE '%{theme}%'
              AND DATE = {date}
              AND location != ''
            GROUP BY location
            ORDER BY mentions DESC
            LIMIT {top_n}
        """

        self.logger.info(f"Fetching locations for theme: {theme}")

        try:
            query_job = self._bigquery_client.query(query)
            results = query_job.result()

            locations = [dict(row) for row in results]

            self.logger.info(f"Retrieved {len(locations)} locations")

            return locations

        except Exception as e:
            self.logger.error(f"GKG locations query failed: {e}")
            raise

    # ============================================================================
    # ADVANCED ANALYTICS METHODS
    # ============================================================================

    @requires_license
    def get_event_timeline(
        self,
        actor: str,
        event_code: str,
        start_date: str,
        end_date: str,
    ) -> Dict[str, Any]:
        """
        Create timeline of specific event type for an actor.

        Tracks how frequently a specific event type occurs over time,
        useful for analyzing trends and patterns.

        Args:
            actor: Actor code
            event_code: CAMEO event code
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)

        Returns:
            Timeline data with daily event counts

        Example:
            >>> # Track USA protests over time
            >>> timeline = connector.get_event_timeline(
            ...     actor='USA',
            ...     event_code='14',  # Protest
            ...     start_date='20240101',
            ...     end_date='20241231'
            ... )
        """
        if not self._bigquery_client:
            raise RuntimeError("This method requires BigQuery")

        query = f"""
            SELECT
                SQLDATE as date,
                COUNT(*) as event_count,
                AVG(GoldsteinScale) as avg_goldstein,
                AVG(AvgTone) as avg_tone,
                SUM(NumMentions) as total_mentions
            FROM `gdelt-bq.gdeltv2.events`
            WHERE (Actor1Code LIKE '{actor}%' OR Actor2Code LIKE '{actor}%')
              AND EventCode LIKE '{event_code}%'
              AND SQLDATE BETWEEN {start_date} AND {end_date}
            GROUP BY SQLDATE
            ORDER BY SQLDATE
        """

        self.logger.info(f"Creating event timeline: {actor} - Event {event_code}")

        try:
            query_job = self._bigquery_client.query(query)
            results = query_job.result()

            timeline = [dict(row) for row in results]

            self.logger.info(f"Retrieved timeline with {len(timeline)} data points")

            return {
                "actor": actor,
                "event_code": event_code,
                "event_name": self.CAMEO_EVENT_CODES.get(event_code, "Unknown"),
                "date_range": f"{start_date} to {end_date}",
                "timeline": timeline,
            }

        except Exception as e:
            self.logger.error(f"Event timeline query failed: {e}")
            raise

    @requires_license
    def get_actor_network(
        self,
        actor: str,
        date: str,
        min_interactions: int = 5,
    ) -> Dict[str, Any]:
        """
        Build interaction network for an actor.

        Identifies all actors who interact with the specified actor
        on a given date, including interaction types and frequencies.

        Args:
            actor: Primary actor code
            date: Date (YYYYMMDD)
            min_interactions: Minimum interaction threshold

        Returns:
            Network data with:
            - nodes: List of interacting actors
            - edges: List of interactions with types and weights

        Example:
            >>> # Build USA's interaction network
            >>> network = connector.get_actor_network(
            ...     actor='USA',
            ...     date='20250101'
            ... )
        """
        if not self._bigquery_client:
            raise RuntimeError("This method requires BigQuery")

        query = f"""
            SELECT
                CASE
                    WHEN Actor1Code LIKE '{actor}%' THEN Actor2Code
                    ELSE Actor1Code
                END as partner_actor,
                EventCode,
                COUNT(*) as interaction_count,
                AVG(GoldsteinScale) as avg_goldstein,
                AVG(AvgTone) as avg_tone
            FROM `gdelt-bq.gdeltv2.events`
            WHERE (Actor1Code LIKE '{actor}%' OR Actor2Code LIKE '{actor}%')
              AND SQLDATE = {date}
            GROUP BY partner_actor, EventCode
            HAVING interaction_count >= {min_interactions}
            ORDER BY interaction_count DESC
        """

        self.logger.info(f"Building actor network for {actor} on {date}")

        try:
            query_job = self._bigquery_client.query(query)
            results = query_job.result()

            interactions = [dict(row) for row in results]

            # Build nodes (unique actors)
            actors = set()
            for interaction in interactions:
                actors.add(interaction["partner_actor"])

            network = {
                "primary_actor": actor,
                "date": date,
                "nodes": [{"id": a, "label": a} for a in actors],
                "edges": [
                    {
                        "source": actor,
                        "target": i["partner_actor"],
                        "event_code": i["EventCode"],
                        "weight": i["interaction_count"],
                        "goldstein": round(i["avg_goldstein"], 2),
                        "tone": round(i["avg_tone"], 2),
                    }
                    for i in interactions
                ],
                "summary": {
                    "total_partners": len(actors),
                    "total_interactions": sum(i["interaction_count"] for i in interactions),
                },
            }

            self.logger.info(
                f"Network built: {len(actors)} partners, " f"{len(interactions)} interaction types"
            )

            return network

        except Exception as e:
            self.logger.error(f"Actor network query failed: {e}")
            raise

    @requires_license
    def get_theme_evolution(
        self,
        theme: str,
        start_date: str,
        end_date: str,
        granularity: str = "daily",
    ) -> Dict[str, Any]:
        """
        Track how a theme evolves over time in global media.

        Args:
            theme: GDELT theme code
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            granularity: Time granularity ('daily', 'weekly', 'monthly')

        Returns:
            Theme evolution data with:
            - coverage: Article counts over time
            - sentiment: Tone trends
            - locations: Geographic distribution changes
            - entities: Associated entities over time

        Example:
            >>> # Track climate change coverage
            >>> evolution = connector.get_theme_evolution(
            ...     theme='ENV_CLIMATECHANGE',
            ...     start_date='20240101',
            ...     end_date='20241231',
            ...     granularity='monthly'
            ... )
        """
        if not self._bigquery_client:
            raise RuntimeError("This method requires BigQuery")

        # Determine date grouping based on granularity
        if granularity == "daily":
            date_format = "DATE"
        elif granularity == "weekly":
            date_format = "EXTRACT(WEEK FROM PARSE_DATE('%Y%m%d', CAST(DATE AS STRING)))"
        elif granularity == "monthly":
            date_format = "SUBSTR(CAST(DATE AS STRING), 1, 6)"
        else:
            raise ValueError("granularity must be 'daily', 'weekly', or 'monthly'")

        query = f"""
            SELECT
                {date_format} as time_period,
                COUNT(*) as article_count,
                AVG(CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(0)] AS FLOAT64)) as avg_tone
            FROM `gdelt-bq.gdeltv2.gkg`
            WHERE Themes LIKE '%{theme}%'
              AND DATE BETWEEN {start_date} AND {end_date}
            GROUP BY time_period
            ORDER BY time_period
        """

        self.logger.info(f"Tracking theme evolution: {theme} ({granularity})")

        try:
            query_job = self._bigquery_client.query(query)
            results = query_job.result()

            evolution = [dict(row) for row in results]

            self.logger.info(f"Retrieved evolution data: {len(evolution)} time periods")

            return {
                "theme": theme,
                "date_range": f"{start_date} to {end_date}",
                "granularity": granularity,
                "evolution": evolution,
            }

        except Exception as e:
            self.logger.error(f"Theme evolution query failed: {e}")
            raise

    def query_bigquery(
        self,
        query: str = None,
        sql_query: str = None,
        max_results: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        Execute custom BigQuery query on GDELT data.

        Args:
            query: SQL query for GDELT BigQuery tables (primary parameter)
            sql_query: Alternative parameter name for SQL query (deprecated)
            max_results: Maximum rows to return

        Returns:
            Query results as list of dictionaries

        Example:
            >>> # Custom query
            >>> results = connector.query_bigquery('''
            ...     SELECT Actor1Name, COUNT(*) as event_count
            ...     FROM `gdelt-bq.gdeltv2.events`
            ...     WHERE DATE(_PARTITIONTIME) = '2025-01-01'
            ...     GROUP BY Actor1Name
            ...     ORDER BY event_count DESC
            ...     LIMIT 10
            ... ''')

        Note:
            BigQuery queries may incur costs based on data scanned.
        """
        if not self.use_bigquery:
            raise ValueError("BigQuery not enabled. Initialize with use_bigquery=True")

        if not self._bigquery_client:
            raise RuntimeError("BigQuery client not initialized")

        final_query = query or sql_query
        if not final_query:
            raise ValueError("query parameter is required")

        # SQL Injection Prevention
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
                    f"Potentially dangerous SQL keyword detected: {keyword}. "
                    f"Use parameterized queries instead."
                )

        self.logger.info(f"Executing BigQuery query (max {max_results} results)")

        try:
            query_job = self._bigquery_client.query(final_query)
            results = query_job.result(max_results=max_results)

            data = [dict(row) for row in results]

            self.logger.info(f"BigQuery returned {len(data)} rows")

            return data

        except Exception as e:
            self.logger.error(f"BigQuery query failed: {e}")
            raise
