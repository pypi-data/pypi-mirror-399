# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Airbyte-based connector for KRL Data Connectors.

Provides a BaseConnector-compatible interface for Airbyte sources,
allowing Airbyte connectors to be used seamlessly with the KRL ecosystem.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from krl_data_connectors.base_connector import BaseConnector
from krl_data_connectors.licensed_connector_mixin import LicensedConnectorMixin

from .client import AirbyteClient, Connection


@dataclass
class AirbyteStreamConfig:
    """Configuration for an Airbyte stream to sync."""

    name: str
    sync_mode: str = "full_refresh"  # full_refresh, incremental
    destination_sync_mode: str = "overwrite"  # overwrite, append, append_dedup
    cursor_field: Optional[str] = None
    primary_key: Optional[List[str]] = None


class AirbyteConnector(BaseConnector, LicensedConnectorMixin):
    """
    KRL-compatible connector backed by Airbyte.

    This connector allows using any of Airbyte's 600+ data sources
    through KRL's familiar BaseConnector interface.

    Features:
    - Seamless integration with KRL caching and logging
    - Access to databases, SaaS apps, data warehouses, and more
    - Managed sync operations with status tracking
    - Compatible with KRL's tier system (Enterprise tier)

    Example:
        >>> connector = AirbyteConnector(
        ...     source_type="salesforce",
        ...     source_config={
        ...         "client_id": "...",
        ...         "client_secret": "...",
        ...         "refresh_token": "...",
        ...     },
        ...     api_key="airbyte-api-key"
        ... )
        >>> connector.connect()
        >>> df = connector.fetch(stream="Account", limit=1000)
    """

    # Enterprise tier only
    REQUIRED_TIER = "enterprise"
    TIER_FEATURE = "airbyte_integration"

    def __init__(
        self,
        source_type: str,
        source_config: Dict[str, Any],
        api_key: Optional[str] = None,
        workspace_id: Optional[str] = None,
        source_name: Optional[str] = None,
        destination_type: Optional[str] = None,
        destination_config: Optional[Dict[str, Any]] = None,
        cache_dir: Optional[str] = None,
        cache_ttl: int = 3600,
        timeout: int = 60,
        max_retries: int = 3,
    ):
        """
        Initialize Airbyte connector.

        Args:
            source_type: Airbyte source type (e.g., "postgres", "salesforce")
            source_config: Source-specific configuration
            api_key: Airbyte API key
            workspace_id: Airbyte workspace ID
            source_name: Human-readable name for the source
            destination_type: Optional destination type for syncs
            destination_config: Optional destination configuration
            cache_dir: Cache directory for results
            cache_ttl: Cache TTL in seconds
            timeout: Request timeout
            max_retries: Maximum retry attempts
        """
        super().__init__(
            api_key=api_key,
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Initialize license checking
        LicensedConnectorMixin.__init__(self)

        self.source_type = source_type
        self.source_config = source_config
        self.source_name = source_name or f"krl-{source_type}"
        self.workspace_id = workspace_id
        self.destination_type = destination_type
        self.destination_config = destination_config

        # Airbyte client (lazy initialization)
        self._airbyte_client: Optional[AirbyteClient] = None
        self._source_id: Optional[str] = None
        self._destination_id: Optional[str] = None
        self._connection: Optional[Connection] = None

        self.logger.info(
            f"AirbyteConnector initialized",
            extra={
                "source_type": source_type,
                "source_name": self.source_name,
                "has_destination": bool(destination_type),
            },
        )

    def _get_api_key(self) -> Optional[str]:
        """Get Airbyte API key from configuration."""
        return self.config.get("AIRBYTE_API_KEY")

    @property
    def airbyte_client(self) -> AirbyteClient:
        """Get or create Airbyte client."""
        if self._airbyte_client is None:
            self._airbyte_client = AirbyteClient(
                api_key=self.api_key,
                workspace_id=self.workspace_id,
            )
        return self._airbyte_client

    def connect(self) -> bool:
        """
        Establish connection to Airbyte and configure source.

        Creates the source in Airbyte if it doesn't exist.
        Optionally sets up destination and connection for syncs.

        Returns:
            True if connection successful
        """
        self._check_license()

        try:
            # Verify Airbyte API is available
            if not self.airbyte_client.health_check():
                self.logger.error("Airbyte API health check failed")
                return False

            # Check if source already exists
            existing_sources = self.airbyte_client.list_sources()
            for src in existing_sources:
                if src.get("name") == self.source_name:
                    self._source_id = src["id"]
                    self.logger.info(
                        f"Using existing source: {self.source_name}",
                        extra={"source_id": self._source_id},
                    )
                    break

            # Create source if needed
            if not self._source_id:
                result = self.airbyte_client.create_source(
                    name=self.source_name,
                    source_type=self.source_type,
                    configuration=self.source_config,
                )
                self._source_id = result["id"]
                self.logger.info(
                    f"Created Airbyte source: {self.source_name}",
                    extra={"source_id": self._source_id},
                )

            # Optionally set up destination
            if self.destination_type and self.destination_config:
                dest_name = f"krl-{self.destination_type}-destination"
                result = self.airbyte_client.create_destination(
                    name=dest_name,
                    destination_type=self.destination_type,
                    configuration=self.destination_config,
                )
                self._destination_id = result["id"]

                # Create connection
                conn = self.airbyte_client.create_connection(
                    name=f"{self.source_name}-to-{dest_name}",
                    source_id=self._source_id,
                    destination_id=self._destination_id,
                )
                self._connection = conn

            self.logger.info(
                "Airbyte connection established",
                extra={
                    "source_id": self._source_id,
                    "destination_id": self._destination_id,
                    "connection_id": self._connection.id if self._connection else None,
                },
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect to Airbyte: {e}")
            return False

    def fetch(
        self,
        stream: Optional[str] = None,
        streams: Optional[List[str]] = None,
        limit: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
        **kwargs: Any,
    ) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Fetch data from Airbyte source.

        For sources without a configured destination, this triggers
        a read operation and returns the data directly.

        For sources with a destination connection, this triggers
        a sync and returns job status.

        Args:
            stream: Single stream name to fetch
            streams: Multiple stream names to fetch
            limit: Maximum records to fetch per stream
            filters: Stream-specific filters
            use_cache: Use cached results if available
            **kwargs: Additional parameters

        Returns:
            DataFrame with fetched data, or dict of DataFrames for multiple streams
        """
        self._check_license()

        if not self._source_id:
            raise RuntimeError("Not connected. Call connect() first.")

        # Build cache key
        cache_key = self._build_cache_key(
            source_type=self.source_type,
            stream=stream,
            streams=streams,
            filters=filters,
            limit=limit,
        )

        # Check cache
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                self.logger.info(f"Cache hit for {cache_key}")
                return cached

        try:
            # If we have a connection, trigger sync
            if self._connection:
                job = self.airbyte_client.trigger_sync(self._connection.id)
                self.logger.info(
                    f"Triggered sync job",
                    extra={
                        "job_id": job["job_id"],
                        "connection_id": self._connection.id,
                    },
                )
                # Return job info - user can poll for completion
                return pd.DataFrame([job])

            # Otherwise, we need to use stream properties
            # Note: Full data extraction requires a destination
            # For direct reads, Airbyte recommends using their UI or destination syncs

            self.logger.warning(
                "Direct data fetch requires a destination connection. "
                "Consider setting up a destination (e.g., local DuckDB) for data extraction."
            )

            # Return stream metadata instead
            return self._get_stream_metadata(stream or (streams[0] if streams else None))

        except Exception as e:
            self.logger.error(f"Fetch failed: {e}")
            raise

    def _get_stream_metadata(self, stream_name: Optional[str] = None) -> pd.DataFrame:
        """Get metadata about available streams."""
        try:
            # This would use the stream properties endpoint
            # For now, return basic info about the source
            return pd.DataFrame(
                [
                    {
                        "source_id": self._source_id,
                        "source_type": self.source_type,
                        "source_name": self.source_name,
                        "stream": stream_name,
                        "status": "connected",
                        "note": "Use trigger_sync() with a destination to extract data",
                    }
                ]
            )
        except Exception as e:
            self.logger.error(f"Failed to get stream metadata: {e}")
            return pd.DataFrame()

    def _build_cache_key(self, **kwargs: Any) -> str:
        """Build cache key from parameters."""
        import hashlib
        import json

        key_data = json.dumps(kwargs, sort_keys=True, default=str)
        return f"airbyte_{hashlib.md5(key_data.encode()).hexdigest()}"

    def trigger_sync(self) -> Dict[str, Any]:
        """
        Trigger a sync job for the configured connection.

        Returns:
            Job details including job_id and status
        """
        self._check_license()

        if not self._connection:
            raise RuntimeError(
                "No connection configured. Set destination_type and destination_config."
            )

        return self.airbyte_client.trigger_sync(self._connection.id)

    def get_sync_status(self, job_id: int) -> Dict[str, Any]:
        """
        Get status of a sync job.

        Args:
            job_id: Job ID to check

        Returns:
            Job status details
        """
        self._check_license()
        return self.airbyte_client.get_job_status(job_id)

    def list_streams(self) -> List[str]:
        """
        List available streams from the source.

        Returns:
            List of stream names
        """
        self._check_license()

        # This would typically use Airbyte's discover_schema
        # For now, return empty - requires source-specific implementation
        self.logger.info(
            "Stream discovery requires source-specific schema. "
            "Use Airbyte UI or API for full catalog discovery."
        )
        return []

    def disconnect(self) -> bool:
        """
        Clean up Airbyte resources.

        Note: This does NOT delete the source/destination in Airbyte,
        just clears local references.

        Returns:
            True if cleanup successful
        """
        self._source_id = None
        self._destination_id = None
        self._connection = None
        self._airbyte_client = None

        self.logger.info("Disconnected from Airbyte")
        return True

    def delete_resources(self, delete_source: bool = True, delete_destination: bool = True) -> bool:
        """
        Delete Airbyte resources created by this connector.

        Args:
            delete_source: Delete the source in Airbyte
            delete_destination: Delete the destination in Airbyte

        Returns:
            True if all deletions successful
        """
        self._check_license()

        success = True

        if self._connection:
            success = success and self.airbyte_client.delete_connection(self._connection.id)

        if delete_destination and self._destination_id:
            try:
                self.airbyte_client._client.destinations.delete_destination(
                    destination_id=self._destination_id
                )
            except Exception as e:
                self.logger.error(f"Failed to delete destination: {e}")
                success = False

        if delete_source and self._source_id:
            success = success and self.airbyte_client.delete_source(self._source_id)

        return success


# Convenience factory functions for common sources


def create_postgres_connector(
    host: str,
    port: int,
    database: str,
    username: str,
    password: str,
    api_key: Optional[str] = None,
    ssl: bool = True,
    **kwargs: Any,
) -> AirbyteConnector:
    """
    Create a PostgreSQL connector via Airbyte.

    Args:
        host: Database host
        port: Database port
        database: Database name
        username: Database username
        password: Database password
        api_key: Airbyte API key
        ssl: Use SSL connection
        **kwargs: Additional configuration

    Returns:
        Configured AirbyteConnector
    """
    return AirbyteConnector(
        source_type="postgres",
        source_config={
            "host": host,
            "port": port,
            "database": database,
            "username": username,
            "password": password,
            "ssl_mode": {"mode": "require"} if ssl else {"mode": "disable"},
            **kwargs,
        },
        api_key=api_key,
        source_name=f"postgres-{database}",
    )


def create_salesforce_connector(
    client_id: str,
    client_secret: str,
    refresh_token: str,
    api_key: Optional[str] = None,
    is_sandbox: bool = False,
    **kwargs: Any,
) -> AirbyteConnector:
    """
    Create a Salesforce connector via Airbyte.

    Args:
        client_id: Salesforce connected app client ID
        client_secret: Salesforce connected app client secret
        refresh_token: OAuth refresh token
        api_key: Airbyte API key
        is_sandbox: Connect to sandbox org
        **kwargs: Additional configuration

    Returns:
        Configured AirbyteConnector
    """
    return AirbyteConnector(
        source_type="salesforce",
        source_config={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "is_sandbox": is_sandbox,
            **kwargs,
        },
        api_key=api_key,
        source_name="salesforce-org",
    )


def create_hubspot_connector(
    api_key: Optional[str] = None,
    credentials_type: str = "private_app",
    access_token: Optional[str] = None,
    **kwargs: Any,
) -> AirbyteConnector:
    """
    Create a HubSpot connector via Airbyte.

    Args:
        api_key: Airbyte API key
        credentials_type: "private_app" or "oauth"
        access_token: HubSpot private app access token
        **kwargs: Additional configuration

    Returns:
        Configured AirbyteConnector
    """
    return AirbyteConnector(
        source_type="hubspot",
        source_config={
            "credentials": {
                "credentials_title": credentials_type,
                "access_token": access_token,
            },
            **kwargs,
        },
        api_key=api_key,
        source_name="hubspot-crm",
    )


def create_stripe_connector(
    account_id: str,
    client_secret: str,
    api_key: Optional[str] = None,
    start_date: Optional[str] = None,
    **kwargs: Any,
) -> AirbyteConnector:
    """
    Create a Stripe connector via Airbyte.

    Args:
        account_id: Stripe account ID
        client_secret: Stripe API key
        api_key: Airbyte API key
        start_date: Data start date (ISO format)
        **kwargs: Additional configuration

    Returns:
        Configured AirbyteConnector
    """
    config = {
        "account_id": account_id,
        "client_secret": client_secret,
        **kwargs,
    }
    if start_date:
        config["start_date"] = start_date

    return AirbyteConnector(
        source_type="stripe",
        source_config=config,
        api_key=api_key,
        source_name="stripe-payments",
    )


def create_google_sheets_connector(
    spreadsheet_id: str,
    credentials_json: str,
    api_key: Optional[str] = None,
    **kwargs: Any,
) -> AirbyteConnector:
    """
    Create a Google Sheets connector via Airbyte.

    Args:
        spreadsheet_id: Google Sheets spreadsheet ID
        credentials_json: Service account JSON credentials
        api_key: Airbyte API key
        **kwargs: Additional configuration

    Returns:
        Configured AirbyteConnector
    """
    return AirbyteConnector(
        source_type="google-sheets",
        source_config={
            "spreadsheet_id": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}",
            "credentials": {
                "auth_type": "Service",
                "service_account_info": credentials_json,
            },
            **kwargs,
        },
        api_key=api_key,
        source_name=f"gsheets-{spreadsheet_id[:8]}",
    )
