# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Airbyte API Client for KRL Data Connectors.

Provides a high-level interface to Airbyte Cloud and self-hosted instances,
wrapping the airbyte-api Python SDK with KRL patterns for logging, caching,
and error handling.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

try:
    import airbyte_api
    from airbyte_api import models
    from airbyte_api.errors import SDKError

    AIRBYTE_AVAILABLE = True
except ImportError:
    AIRBYTE_AVAILABLE = False
    airbyte_api = None
    models = None
    SDKError = Exception

from krl_core import ConfigManager, get_logger


class AirbyteEnvironment(Enum):
    """Airbyte deployment environment."""

    CLOUD = "cloud"
    OSS = "oss"  # Open Source Self-hosted
    ENTERPRISE = "enterprise"


@dataclass
class AirbyteConfig:
    """Configuration for Airbyte client."""

    api_key: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    server_url: str = "https://api.airbyte.com/v1"
    environment: AirbyteEnvironment = AirbyteEnvironment.CLOUD
    workspace_id: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3


@dataclass
class SourceDefinition:
    """Airbyte source definition."""

    id: str
    name: str
    docker_repository: str
    docker_image_tag: str
    documentation_url: Optional[str] = None
    icon: Optional[str] = None
    source_type: Optional[str] = None
    release_stage: Optional[str] = None
    supported_destination_sync_modes: List[str] = field(default_factory=list)


@dataclass
class DestinationDefinition:
    """Airbyte destination definition."""

    id: str
    name: str
    docker_repository: str
    docker_image_tag: str
    documentation_url: Optional[str] = None
    icon: Optional[str] = None
    supported_destination_sync_modes: List[str] = field(default_factory=list)


@dataclass
class Connection:
    """Airbyte connection (source -> destination sync)."""

    id: str
    name: str
    source_id: str
    destination_id: str
    status: str
    schedule: Optional[Dict[str, Any]] = None
    sync_catalog: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AirbyteClient:
    """
    High-level client for Airbyte API.

    Provides access to Airbyte's 600+ data connectors for enterprise data
    integration. Supports Airbyte Cloud, OSS, and Enterprise deployments.

    Features:
    - Source and destination management
    - Connection creation and configuration
    - Sync job triggering and monitoring
    - OAuth credential handling
    - Workspace management

    Example:
        >>> client = AirbyteClient(api_key="your-api-key")
        >>> sources = client.list_source_definitions()
        >>> for source in sources[:5]:
        ...     print(f"{source.name}: {source.docker_repository}")
        Postgres: airbyte/source-postgres
        MySQL: airbyte/source-mysql
        ...
    """

    # Popular source categories for quick access
    DATABASE_SOURCES = [
        "postgres",
        "mysql",
        "mssql",
        "oracle",
        "mongodb",
        "dynamodb",
        "cockroachdb",
        "clickhouse",
        "mariadb",
        "db2",
    ]

    WAREHOUSE_SOURCES = [
        "snowflake",
        "bigquery",
        "redshift",
        "databricks",
        "s3",
        "gcs",
        "azure-blob",
    ]

    SAAS_SOURCES = [
        "salesforce",
        "hubspot",
        "stripe",
        "zendesk",
        "jira",
        "github",
        "gitlab",
        "slack",
        "notion",
        "airtable",
        "google-sheets",
        "google-analytics",
        "facebook-marketing",
        "linkedin-ads",
        "google-ads",
        "shopify",
        "quickbooks",
        "netsuite",
        "workday",
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        server_url: Optional[str] = None,
        workspace_id: Optional[str] = None,
        config: Optional[AirbyteConfig] = None,
    ):
        """
        Initialize Airbyte client.

        Args:
            api_key: Airbyte API key (for bearer auth)
            username: Username for basic auth
            password: Password for basic auth
            server_url: Airbyte API server URL
            workspace_id: Default workspace ID
            config: Full configuration object (overrides other params)
        """
        self.logger = get_logger("AirbyteClient")
        self._config_manager = ConfigManager()

        if not AIRBYTE_AVAILABLE:
            self.logger.error(
                "airbyte-api package not installed. "
                "Install with: pip install airbyte-api"
            )
            raise ImportError(
                "airbyte-api package is required for Airbyte integration. "
                "Install with: pip install airbyte-api"
            )

        # Build configuration
        if config:
            self._config = config
        else:
            self._config = AirbyteConfig(
                api_key=api_key or self._config_manager.get("AIRBYTE_API_KEY"),
                username=username or self._config_manager.get("AIRBYTE_USERNAME"),
                password=password or self._config_manager.get("AIRBYTE_PASSWORD"),
                server_url=server_url
                or self._config_manager.get(
                    "AIRBYTE_SERVER_URL", default="https://api.airbyte.com/v1"
                ),
                workspace_id=workspace_id
                or self._config_manager.get("AIRBYTE_WORKSPACE_ID"),
            )

        # Initialize SDK client
        self._client = self._create_client()
        self.workspace_id = self._config.workspace_id

        self.logger.info(
            "Airbyte client initialized",
            extra={
                "server_url": self._config.server_url,
                "workspace_id": self.workspace_id,
                "auth_type": "bearer" if self._config.api_key else "basic",
            },
        )

    def _create_client(self) -> "airbyte_api.AirbyteAPI":
        """Create the underlying Airbyte SDK client."""
        security = None

        if self._config.api_key:
            security = models.Security(
                bearer_auth=self._config.api_key,
            )
        elif self._config.username and self._config.password:
            security = models.Security(
                basic_auth=models.SchemeBasicAuth(
                    username=self._config.username,
                    password=self._config.password,
                ),
            )

        return airbyte_api.AirbyteAPI(
            server_url=self._config.server_url,
            security=security,
        )

    # -------------------------------------------------------------------------
    # Health & Status
    # -------------------------------------------------------------------------

    def health_check(self) -> bool:
        """
        Check Airbyte API health.

        Returns:
            True if API is healthy, False otherwise
        """
        try:
            res = self._client.health.get_health_check()
            return res.status_code == 200
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    # -------------------------------------------------------------------------
    # Source Definitions
    # -------------------------------------------------------------------------

    def list_source_definitions(
        self, limit: int = 100, offset: int = 0
    ) -> List[SourceDefinition]:
        """
        List available source definitions.

        These are the connector types available (Postgres, Salesforce, etc.),
        not specific configured sources.

        Args:
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of available source definitions
        """
        try:
            res = self._client.source_definitions.list_source_definitions()

            if res.source_definitions_response is None:
                return []

            definitions = []
            for sd in res.source_definitions_response.data or []:
                definitions.append(
                    SourceDefinition(
                        id=sd.source_definition_id,
                        name=sd.name,
                        docker_repository=sd.docker_repository or "",
                        docker_image_tag=sd.docker_image_tag or "",
                        documentation_url=sd.documentation_url,
                        icon=sd.icon,
                        source_type=sd.source_type,
                        release_stage=sd.release_stage,
                    )
                )

            self.logger.info(
                f"Retrieved {len(definitions)} source definitions",
                extra={"count": len(definitions)},
            )
            return definitions

        except SDKError as e:
            self.logger.error(f"Failed to list source definitions: {e}")
            raise

    def get_source_definition(self, source_definition_id: str) -> Optional[SourceDefinition]:
        """
        Get details for a specific source definition.

        Args:
            source_definition_id: The source definition ID

        Returns:
            Source definition details or None if not found
        """
        try:
            res = self._client.source_definitions.get_source_definition(
                source_definition_id=source_definition_id
            )

            if res.source_definition_response is None:
                return None

            sd = res.source_definition_response
            return SourceDefinition(
                id=sd.source_definition_id,
                name=sd.name,
                docker_repository=sd.docker_repository or "",
                docker_image_tag=sd.docker_image_tag or "",
                documentation_url=sd.documentation_url,
                icon=sd.icon,
                source_type=sd.source_type,
                release_stage=sd.release_stage,
            )

        except SDKError as e:
            self.logger.error(f"Failed to get source definition: {e}")
            return None

    def search_source_definitions(self, query: str) -> List[SourceDefinition]:
        """
        Search source definitions by name.

        Args:
            query: Search string (case-insensitive)

        Returns:
            Matching source definitions
        """
        all_definitions = self.list_source_definitions(limit=500)
        query_lower = query.lower()

        return [
            d
            for d in all_definitions
            if query_lower in d.name.lower()
            or query_lower in (d.docker_repository or "").lower()
        ]

    # -------------------------------------------------------------------------
    # Sources (Configured Instances)
    # -------------------------------------------------------------------------

    def list_sources(
        self,
        workspace_id: Optional[str] = None,
        include_deleted: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        List configured sources in a workspace.

        Args:
            workspace_id: Workspace ID (uses default if not specified)
            include_deleted: Include deleted sources

        Returns:
            List of configured sources
        """
        ws_id = workspace_id or self.workspace_id

        try:
            res = self._client.sources.list_sources(
                workspace_ids=[ws_id] if ws_id else None,
                include_deleted=include_deleted,
            )

            if res.sources_response is None:
                return []

            return [
                {
                    "id": s.source_id,
                    "name": s.name,
                    "source_type": s.source_type,
                    "workspace_id": s.workspace_id,
                    "configuration": s.configuration,
                }
                for s in res.sources_response.data or []
            ]

        except SDKError as e:
            self.logger.error(f"Failed to list sources: {e}")
            raise

    def create_source(
        self,
        name: str,
        source_type: str,
        configuration: Dict[str, Any],
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new source.

        Args:
            name: Human-readable name for the source
            source_type: Source type (e.g., "postgres", "salesforce")
            configuration: Source-specific configuration
            workspace_id: Target workspace ID

        Returns:
            Created source details

        Example:
            >>> source = client.create_source(
            ...     name="Production Postgres",
            ...     source_type="postgres",
            ...     configuration={
            ...         "host": "db.example.com",
            ...         "port": 5432,
            ...         "database": "production",
            ...         "username": "readonly",
            ...         "password": "***",
            ...     }
            ... )
        """
        ws_id = workspace_id or self.workspace_id
        if not ws_id:
            raise ValueError("workspace_id is required")

        try:
            # Build the source create request dynamically based on source_type
            request = models.SourceCreateRequest(
                name=name,
                workspace_id=ws_id,
                configuration=configuration,
            )

            res = self._client.sources.create_source(request=request)

            if res.source_response is None:
                raise RuntimeError("Source creation returned no response")

            self.logger.info(
                f"Created source: {name}",
                extra={
                    "source_id": res.source_response.source_id,
                    "source_type": source_type,
                },
            )

            return {
                "id": res.source_response.source_id,
                "name": res.source_response.name,
                "source_type": res.source_response.source_type,
                "workspace_id": res.source_response.workspace_id,
            }

        except SDKError as e:
            self.logger.error(f"Failed to create source: {e}")
            raise

    def delete_source(self, source_id: str) -> bool:
        """
        Delete a source.

        Args:
            source_id: Source ID to delete

        Returns:
            True if deleted successfully
        """
        try:
            self._client.sources.delete_source(source_id=source_id)
            self.logger.info(f"Deleted source: {source_id}")
            return True
        except SDKError as e:
            self.logger.error(f"Failed to delete source: {e}")
            return False

    # -------------------------------------------------------------------------
    # Destinations
    # -------------------------------------------------------------------------

    def list_destination_definitions(
        self, limit: int = 100
    ) -> List[DestinationDefinition]:
        """
        List available destination definitions.

        Returns:
            List of available destination types
        """
        try:
            res = self._client.destination_definitions.list_destination_definitions()

            if res.destination_definitions_response is None:
                return []

            definitions = []
            for dd in res.destination_definitions_response.data or []:
                definitions.append(
                    DestinationDefinition(
                        id=dd.destination_definition_id,
                        name=dd.name,
                        docker_repository=dd.docker_repository or "",
                        docker_image_tag=dd.docker_image_tag or "",
                        documentation_url=dd.documentation_url,
                        icon=dd.icon,
                    )
                )

            return definitions

        except SDKError as e:
            self.logger.error(f"Failed to list destination definitions: {e}")
            raise

    def list_destinations(
        self, workspace_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List configured destinations in a workspace.

        Args:
            workspace_id: Workspace ID (uses default if not specified)

        Returns:
            List of configured destinations
        """
        ws_id = workspace_id or self.workspace_id

        try:
            res = self._client.destinations.list_destinations(
                workspace_ids=[ws_id] if ws_id else None,
            )

            if res.destinations_response is None:
                return []

            return [
                {
                    "id": d.destination_id,
                    "name": d.name,
                    "destination_type": d.destination_type,
                    "workspace_id": d.workspace_id,
                }
                for d in res.destinations_response.data or []
            ]

        except SDKError as e:
            self.logger.error(f"Failed to list destinations: {e}")
            raise

    def create_destination(
        self,
        name: str,
        destination_type: str,
        configuration: Dict[str, Any],
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new destination.

        Args:
            name: Human-readable name
            destination_type: Destination type (e.g., "bigquery", "snowflake")
            configuration: Destination-specific configuration
            workspace_id: Target workspace ID

        Returns:
            Created destination details
        """
        ws_id = workspace_id or self.workspace_id
        if not ws_id:
            raise ValueError("workspace_id is required")

        try:
            request = models.DestinationCreateRequest(
                name=name,
                workspace_id=ws_id,
                configuration=configuration,
            )

            res = self._client.destinations.create_destination(request=request)

            if res.destination_response is None:
                raise RuntimeError("Destination creation returned no response")

            self.logger.info(
                f"Created destination: {name}",
                extra={
                    "destination_id": res.destination_response.destination_id,
                    "destination_type": destination_type,
                },
            )

            return {
                "id": res.destination_response.destination_id,
                "name": res.destination_response.name,
                "destination_type": res.destination_response.destination_type,
                "workspace_id": res.destination_response.workspace_id,
            }

        except SDKError as e:
            self.logger.error(f"Failed to create destination: {e}")
            raise

    # -------------------------------------------------------------------------
    # Connections
    # -------------------------------------------------------------------------

    def list_connections(
        self, workspace_id: Optional[str] = None
    ) -> List[Connection]:
        """
        List connections in a workspace.

        Args:
            workspace_id: Workspace ID (uses default if not specified)

        Returns:
            List of connections
        """
        ws_id = workspace_id or self.workspace_id

        try:
            res = self._client.connections.list_connections(
                workspace_ids=[ws_id] if ws_id else None,
            )

            if res.connections_response is None:
                return []

            connections = []
            for c in res.connections_response.data or []:
                connections.append(
                    Connection(
                        id=c.connection_id,
                        name=c.name or "",
                        source_id=c.source_id,
                        destination_id=c.destination_id,
                        status=c.status or "unknown",
                        schedule=c.schedule.__dict__ if c.schedule else None,
                    )
                )

            return connections

        except SDKError as e:
            self.logger.error(f"Failed to list connections: {e}")
            raise

    def create_connection(
        self,
        name: str,
        source_id: str,
        destination_id: str,
        schedule: Optional[Dict[str, Any]] = None,
        namespace_definition: str = "destination",
        namespace_format: Optional[str] = None,
        prefix: Optional[str] = None,
    ) -> Connection:
        """
        Create a connection between a source and destination.

        Args:
            name: Connection name
            source_id: Source ID
            destination_id: Destination ID
            schedule: Sync schedule configuration
            namespace_definition: How to handle namespaces
            namespace_format: Custom namespace format
            prefix: Table prefix in destination

        Returns:
            Created connection
        """
        try:
            request = models.ConnectionCreateRequest(
                name=name,
                source_id=source_id,
                destination_id=destination_id,
            )

            res = self._client.connections.create_connection(request=request)

            if res.connection_response is None:
                raise RuntimeError("Connection creation returned no response")

            conn = res.connection_response
            self.logger.info(
                f"Created connection: {name}",
                extra={
                    "connection_id": conn.connection_id,
                    "source_id": source_id,
                    "destination_id": destination_id,
                },
            )

            return Connection(
                id=conn.connection_id,
                name=conn.name or "",
                source_id=conn.source_id,
                destination_id=conn.destination_id,
                status=conn.status or "created",
            )

        except SDKError as e:
            self.logger.error(f"Failed to create connection: {e}")
            raise

    def get_connection(self, connection_id: str) -> Optional[Connection]:
        """
        Get connection details.

        Args:
            connection_id: Connection ID

        Returns:
            Connection details or None if not found
        """
        try:
            res = self._client.connections.get_connection(connection_id=connection_id)

            if res.connection_response is None:
                return None

            conn = res.connection_response
            return Connection(
                id=conn.connection_id,
                name=conn.name or "",
                source_id=conn.source_id,
                destination_id=conn.destination_id,
                status=conn.status or "unknown",
            )

        except SDKError as e:
            self.logger.error(f"Failed to get connection: {e}")
            return None

    def delete_connection(self, connection_id: str) -> bool:
        """
        Delete a connection.

        Args:
            connection_id: Connection ID

        Returns:
            True if deleted successfully
        """
        try:
            self._client.connections.delete_connection(connection_id=connection_id)
            self.logger.info(f"Deleted connection: {connection_id}")
            return True
        except SDKError as e:
            self.logger.error(f"Failed to delete connection: {e}")
            return False

    # -------------------------------------------------------------------------
    # Jobs (Sync Operations)
    # -------------------------------------------------------------------------

    def trigger_sync(self, connection_id: str) -> Dict[str, Any]:
        """
        Trigger a sync job for a connection.

        Args:
            connection_id: Connection ID to sync

        Returns:
            Job details including job_id and status
        """
        try:
            request = models.JobCreateRequest(
                connection_id=connection_id,
                job_type=models.JobTypeEnum.SYNC,
            )

            res = self._client.jobs.create_job(request=request)

            if res.job_response is None:
                raise RuntimeError("Job creation returned no response")

            self.logger.info(
                f"Triggered sync job",
                extra={
                    "job_id": res.job_response.job_id,
                    "connection_id": connection_id,
                },
            )

            return {
                "job_id": res.job_response.job_id,
                "connection_id": connection_id,
                "status": res.job_response.status,
                "job_type": res.job_response.job_type,
            }

        except SDKError as e:
            self.logger.error(f"Failed to trigger sync: {e}")
            raise

    def get_job_status(self, job_id: int) -> Dict[str, Any]:
        """
        Get job status and details.

        Args:
            job_id: Job ID

        Returns:
            Job status and details
        """
        try:
            res = self._client.jobs.get_job(job_id=job_id)

            if res.job_response is None:
                return {"status": "unknown"}

            return {
                "job_id": res.job_response.job_id,
                "status": res.job_response.status,
                "job_type": res.job_response.job_type,
                "start_time": res.job_response.start_time,
                "connection_id": res.job_response.connection_id,
            }

        except SDKError as e:
            self.logger.error(f"Failed to get job status: {e}")
            raise

    def cancel_job(self, job_id: int) -> bool:
        """
        Cancel a running job.

        Args:
            job_id: Job ID to cancel

        Returns:
            True if cancelled successfully
        """
        try:
            self._client.jobs.cancel_job(job_id=job_id)
            self.logger.info(f"Cancelled job: {job_id}")
            return True
        except SDKError as e:
            self.logger.error(f"Failed to cancel job: {e}")
            return False

    def list_jobs(
        self,
        connection_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        List sync jobs.

        Args:
            connection_id: Filter by connection
            status: Filter by status
            limit: Maximum results

        Returns:
            List of jobs
        """
        try:
            res = self._client.jobs.list_jobs(
                connection_id=connection_id,
                status=status,
                limit=limit,
            )

            if res.jobs_response is None:
                return []

            return [
                {
                    "job_id": j.job_id,
                    "connection_id": j.connection_id,
                    "status": j.status,
                    "job_type": j.job_type,
                    "start_time": j.start_time,
                }
                for j in res.jobs_response.data or []
            ]

        except SDKError as e:
            self.logger.error(f"Failed to list jobs: {e}")
            raise

    # -------------------------------------------------------------------------
    # Workspaces
    # -------------------------------------------------------------------------

    def list_workspaces(self) -> List[Dict[str, Any]]:
        """
        List available workspaces.

        Returns:
            List of workspaces
        """
        try:
            res = self._client.workspaces.list_workspaces()

            if res.workspaces_response is None:
                return []

            return [
                {
                    "id": w.workspace_id,
                    "name": w.name,
                    "data_residency": getattr(w, "data_residency", None),
                }
                for w in res.workspaces_response.data or []
            ]

        except SDKError as e:
            self.logger.error(f"Failed to list workspaces: {e}")
            raise

    def create_workspace(self, name: str) -> Dict[str, Any]:
        """
        Create a new workspace.

        Args:
            name: Workspace name

        Returns:
            Created workspace details
        """
        try:
            request = models.WorkspaceCreateRequest(name=name)
            res = self._client.workspaces.create_workspace(request=request)

            if res.workspace_response is None:
                raise RuntimeError("Workspace creation returned no response")

            self.logger.info(
                f"Created workspace: {name}",
                extra={"workspace_id": res.workspace_response.workspace_id},
            )

            return {
                "id": res.workspace_response.workspace_id,
                "name": res.workspace_response.name,
            }

        except SDKError as e:
            self.logger.error(f"Failed to create workspace: {e}")
            raise

    # -------------------------------------------------------------------------
    # Convenience Methods
    # -------------------------------------------------------------------------

    def get_popular_sources(
        self, category: str = "all"
    ) -> List[SourceDefinition]:
        """
        Get popular source definitions by category.

        Args:
            category: One of "database", "warehouse", "saas", or "all"

        Returns:
            List of popular sources in the category
        """
        categories = {
            "database": self.DATABASE_SOURCES,
            "warehouse": self.WAREHOUSE_SOURCES,
            "saas": self.SAAS_SOURCES,
        }

        if category == "all":
            search_terms = (
                self.DATABASE_SOURCES + self.WAREHOUSE_SOURCES + self.SAAS_SOURCES
            )
        else:
            search_terms = categories.get(category, [])

        all_definitions = self.list_source_definitions(limit=500)

        results = []
        for defn in all_definitions:
            name_lower = defn.name.lower()
            for term in search_terms:
                if term in name_lower or term in (defn.docker_repository or "").lower():
                    results.append(defn)
                    break

        return results

    def quick_connect_database(
        self,
        name: str,
        database_type: str,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
        workspace_id: Optional[str] = None,
        ssl: bool = True,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Quick setup for database source.

        Args:
            name: Source name
            database_type: postgres, mysql, mssql, etc.
            host: Database host
            port: Database port
            database: Database name
            username: Database username
            password: Database password
            workspace_id: Target workspace
            ssl: Use SSL connection
            **kwargs: Additional configuration

        Returns:
            Created source details
        """
        config = {
            "host": host,
            "port": port,
            "database": database,
            "username": username,
            "password": password,
            "ssl": ssl,
            **kwargs,
        }

        return self.create_source(
            name=name,
            source_type=database_type,
            configuration=config,
            workspace_id=workspace_id,
        )

    def quick_connect_warehouse(
        self,
        name: str,
        warehouse_type: str,
        credentials: Dict[str, Any],
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Quick setup for data warehouse destination.

        Args:
            name: Destination name
            warehouse_type: snowflake, bigquery, redshift, etc.
            credentials: Warehouse credentials
            workspace_id: Target workspace

        Returns:
            Created destination details
        """
        return self.create_destination(
            name=name,
            destination_type=warehouse_type,
            configuration=credentials,
            workspace_id=workspace_id,
        )
