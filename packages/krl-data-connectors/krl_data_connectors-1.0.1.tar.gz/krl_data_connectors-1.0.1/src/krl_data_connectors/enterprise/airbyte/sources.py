# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Airbyte Source Catalog for KRL Data Connectors.

Provides organized access to Airbyte's 600+ connectors by category,
making it easy to discover and use relevant data sources.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from krl_core import get_logger


class SourceCategory(Enum):
    """Categories of Airbyte sources."""

    DATABASE = "database"
    WAREHOUSE = "warehouse"
    SAAS = "saas"
    MARKETING = "marketing"
    SALES = "sales"
    FINANCE = "finance"
    HR = "hr"
    ENGINEERING = "engineering"
    PRODUCT = "product"
    FILE = "file"
    API = "api"
    OTHER = "other"


@dataclass
class SourceInfo:
    """Information about an Airbyte source."""

    name: str
    source_type: str  # The Airbyte source type identifier
    category: SourceCategory
    description: str
    documentation_url: Optional[str] = None
    auth_type: str = "api_key"  # api_key, oauth, basic, none
    tier_required: str = "enterprise"  # community, pro, enterprise
    popular: bool = False
    config_template: Dict = field(default_factory=dict)


class AirbyteSourceCatalog:
    """
    Catalog of available Airbyte sources organized by category.

    Provides discovery and filtering of Airbyte's 600+ connectors
    with KRL-specific metadata like tier requirements and usage patterns.

    Example:
        >>> catalog = AirbyteSourceCatalog()
        >>> databases = catalog.get_by_category(SourceCategory.DATABASE)
        >>> popular = catalog.get_popular()
        >>> salesforce = catalog.get_source("salesforce")
    """

    def __init__(self):
        self.logger = get_logger("AirbyteSourceCatalog")
        self._sources: Dict[str, SourceInfo] = {}
        self._load_catalog()

    def _load_catalog(self) -> None:
        """Load the source catalog with KRL-curated sources."""

        # =====================================================================
        # DATABASE SOURCES
        # =====================================================================

        self._add_source(
            SourceInfo(
                name="PostgreSQL",
                source_type="postgres",
                category=SourceCategory.DATABASE,
                description="Production-grade relational database. Most popular open-source database.",
                documentation_url="https://docs.airbyte.com/integrations/sources/postgres",
                auth_type="basic",
                popular=True,
                config_template={
                    "host": "your-host.com",
                    "port": 5432,
                    "database": "your_database",
                    "username": "your_username",
                    "password": "your_password",
                    "ssl_mode": {"mode": "require"},
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="MySQL",
                source_type="mysql",
                category=SourceCategory.DATABASE,
                description="World's most popular open-source relational database.",
                documentation_url="https://docs.airbyte.com/integrations/sources/mysql",
                auth_type="basic",
                popular=True,
                config_template={
                    "host": "your-host.com",
                    "port": 3306,
                    "database": "your_database",
                    "username": "your_username",
                    "password": "your_password",
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="Microsoft SQL Server",
                source_type="mssql",
                category=SourceCategory.DATABASE,
                description="Microsoft's enterprise relational database.",
                documentation_url="https://docs.airbyte.com/integrations/sources/mssql",
                auth_type="basic",
                popular=True,
                config_template={
                    "host": "your-host.com",
                    "port": 1433,
                    "database": "your_database",
                    "username": "your_username",
                    "password": "your_password",
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="MongoDB",
                source_type="mongodb-v2",
                category=SourceCategory.DATABASE,
                description="Leading NoSQL document database.",
                documentation_url="https://docs.airbyte.com/integrations/sources/mongodb-v2",
                auth_type="basic",
                popular=True,
                config_template={
                    "connection_string": "mongodb+srv://...",
                    "database": "your_database",
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="Oracle",
                source_type="oracle",
                category=SourceCategory.DATABASE,
                description="Enterprise-grade Oracle database.",
                documentation_url="https://docs.airbyte.com/integrations/sources/oracle",
                auth_type="basic",
                config_template={
                    "host": "your-host.com",
                    "port": 1521,
                    "sid": "your_sid",
                    "username": "your_username",
                    "password": "your_password",
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="DuckDB",
                source_type="duckdb",
                category=SourceCategory.DATABASE,
                description="Embedded analytical database, great for local development.",
                documentation_url="https://docs.airbyte.com/integrations/sources/duckdb",
                auth_type="none",
                config_template={
                    "database": "/path/to/database.duckdb",
                },
            )
        )

        # =====================================================================
        # DATA WAREHOUSE SOURCES
        # =====================================================================

        self._add_source(
            SourceInfo(
                name="Snowflake",
                source_type="snowflake",
                category=SourceCategory.WAREHOUSE,
                description="Cloud data warehouse for analytics and data engineering.",
                documentation_url="https://docs.airbyte.com/integrations/sources/snowflake",
                auth_type="oauth",
                popular=True,
                config_template={
                    "host": "account.snowflakecomputing.com",
                    "role": "ACCOUNTADMIN",
                    "warehouse": "COMPUTE_WH",
                    "database": "your_database",
                    "schema": "PUBLIC",
                    "username": "your_username",
                    "password": "your_password",
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="BigQuery",
                source_type="bigquery",
                category=SourceCategory.WAREHOUSE,
                description="Google's serverless data warehouse.",
                documentation_url="https://docs.airbyte.com/integrations/sources/bigquery",
                auth_type="oauth",
                popular=True,
                config_template={
                    "project_id": "your-project-id",
                    "dataset_id": "your_dataset",
                    "credentials_json": "{ ... service account ... }",
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="Amazon Redshift",
                source_type="redshift",
                category=SourceCategory.WAREHOUSE,
                description="AWS cloud data warehouse.",
                documentation_url="https://docs.airbyte.com/integrations/sources/redshift",
                auth_type="basic",
                popular=True,
                config_template={
                    "host": "your-cluster.region.redshift.amazonaws.com",
                    "port": 5439,
                    "database": "your_database",
                    "username": "your_username",
                    "password": "your_password",
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="Databricks",
                source_type="databricks",
                category=SourceCategory.WAREHOUSE,
                description="Unified analytics platform with Delta Lake.",
                documentation_url="https://docs.airbyte.com/integrations/sources/databricks",
                auth_type="oauth",
                config_template={
                    "server_hostname": "your-workspace.cloud.databricks.com",
                    "http_path": "/sql/1.0/warehouses/...",
                    "access_token": "your_token",
                },
            )
        )

        # =====================================================================
        # SAAS / CRM SOURCES
        # =====================================================================

        self._add_source(
            SourceInfo(
                name="Salesforce",
                source_type="salesforce",
                category=SourceCategory.SALES,
                description="World's #1 CRM platform.",
                documentation_url="https://docs.airbyte.com/integrations/sources/salesforce",
                auth_type="oauth",
                popular=True,
                config_template={
                    "client_id": "your_client_id",
                    "client_secret": "your_client_secret",
                    "refresh_token": "your_refresh_token",
                    "is_sandbox": False,
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="HubSpot",
                source_type="hubspot",
                category=SourceCategory.MARKETING,
                description="Inbound marketing, sales, and CRM platform.",
                documentation_url="https://docs.airbyte.com/integrations/sources/hubspot",
                auth_type="oauth",
                popular=True,
                config_template={
                    "credentials": {
                        "credentials_title": "Private App",
                        "access_token": "your_access_token",
                    },
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="Stripe",
                source_type="stripe",
                category=SourceCategory.FINANCE,
                description="Online payment processing for internet businesses.",
                documentation_url="https://docs.airbyte.com/integrations/sources/stripe",
                auth_type="api_key",
                popular=True,
                config_template={
                    "account_id": "acct_...",
                    "client_secret": "sk_live_...",
                    "start_date": "2020-01-01T00:00:00Z",
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="Zendesk",
                source_type="zendesk-support",
                category=SourceCategory.SALES,
                description="Customer service and engagement platform.",
                documentation_url="https://docs.airbyte.com/integrations/sources/zendesk-support",
                auth_type="oauth",
                config_template={
                    "subdomain": "your-subdomain",
                    "credentials": {
                        "credentials": "api_token",
                        "email": "your@email.com",
                        "api_token": "your_token",
                    },
                },
            )
        )

        # =====================================================================
        # MARKETING ANALYTICS SOURCES
        # =====================================================================

        self._add_source(
            SourceInfo(
                name="Google Analytics 4",
                source_type="google-analytics-data-api",
                category=SourceCategory.MARKETING,
                description="Web analytics service from Google.",
                documentation_url="https://docs.airbyte.com/integrations/sources/google-analytics-data-api",
                auth_type="oauth",
                popular=True,
                config_template={
                    "property_id": "123456789",
                    "credentials": {
                        "auth_type": "Service",
                        "credentials_json": "{ ... }",
                    },
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="Google Ads",
                source_type="google-ads",
                category=SourceCategory.MARKETING,
                description="Google's advertising platform.",
                documentation_url="https://docs.airbyte.com/integrations/sources/google-ads",
                auth_type="oauth",
                popular=True,
                config_template={
                    "customer_id": "123-456-7890",
                    "credentials": {
                        "developer_token": "...",
                        "client_id": "...",
                        "client_secret": "...",
                        "refresh_token": "...",
                    },
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="Facebook Marketing",
                source_type="facebook-marketing",
                category=SourceCategory.MARKETING,
                description="Meta's advertising platform for Facebook and Instagram.",
                documentation_url="https://docs.airbyte.com/integrations/sources/facebook-marketing",
                auth_type="oauth",
                popular=True,
                config_template={
                    "account_id": "act_123456789",
                    "access_token": "your_access_token",
                    "start_date": "2020-01-01T00:00:00Z",
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="LinkedIn Ads",
                source_type="linkedin-ads",
                category=SourceCategory.MARKETING,
                description="LinkedIn's advertising platform.",
                documentation_url="https://docs.airbyte.com/integrations/sources/linkedin-ads",
                auth_type="oauth",
                config_template={
                    "credentials": {
                        "auth_method": "oAuth2.0",
                        "client_id": "...",
                        "client_secret": "...",
                        "refresh_token": "...",
                    },
                    "start_date": "2020-01-01",
                    "account_ids": [123456789],
                },
            )
        )

        # =====================================================================
        # PRODUCTIVITY / COLLABORATION SOURCES
        # =====================================================================

        self._add_source(
            SourceInfo(
                name="GitHub",
                source_type="github",
                category=SourceCategory.ENGINEERING,
                description="Code hosting and collaboration platform.",
                documentation_url="https://docs.airbyte.com/integrations/sources/github",
                auth_type="oauth",
                popular=True,
                config_template={
                    "credentials": {
                        "personal_access_token": "ghp_...",
                    },
                    "repositories": ["owner/repo"],
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="Jira",
                source_type="jira",
                category=SourceCategory.ENGINEERING,
                description="Project management and issue tracking.",
                documentation_url="https://docs.airbyte.com/integrations/sources/jira",
                auth_type="api_key",
                popular=True,
                config_template={
                    "api_token": "your_api_token",
                    "domain": "your-domain.atlassian.net",
                    "email": "your@email.com",
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="Slack",
                source_type="slack",
                category=SourceCategory.OTHER,
                description="Business communication platform.",
                documentation_url="https://docs.airbyte.com/integrations/sources/slack",
                auth_type="oauth",
                config_template={
                    "api_token": "xoxb-...",
                    "start_date": "2020-01-01T00:00:00Z",
                    "lookback_window": 7,
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="Notion",
                source_type="notion",
                category=SourceCategory.OTHER,
                description="All-in-one workspace for notes, docs, and collaboration.",
                documentation_url="https://docs.airbyte.com/integrations/sources/notion",
                auth_type="oauth",
                config_template={
                    "credentials": {
                        "auth_type": "token",
                        "token": "secret_...",
                    },
                    "start_date": "2020-01-01T00:00:00.000Z",
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="Airtable",
                source_type="airtable",
                category=SourceCategory.OTHER,
                description="Spreadsheet-database hybrid for organizing work.",
                documentation_url="https://docs.airbyte.com/integrations/sources/airtable",
                auth_type="api_key",
                popular=True,
                config_template={
                    "api_key": "pat...",
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="Google Sheets",
                source_type="google-sheets",
                category=SourceCategory.FILE,
                description="Cloud-based spreadsheet application.",
                documentation_url="https://docs.airbyte.com/integrations/sources/google-sheets",
                auth_type="oauth",
                popular=True,
                config_template={
                    "spreadsheet_id": "https://docs.google.com/spreadsheets/d/...",
                    "credentials": {
                        "auth_type": "Service",
                        "service_account_info": "{ ... }",
                    },
                },
            )
        )

        # =====================================================================
        # HR / FINANCE SOURCES
        # =====================================================================

        self._add_source(
            SourceInfo(
                name="Workday",
                source_type="workday",
                category=SourceCategory.HR,
                description="Enterprise HR and finance management.",
                documentation_url="https://docs.airbyte.com/integrations/sources/workday",
                auth_type="oauth",
                config_template={
                    "tenant_name": "your_tenant",
                    "api_version": "v1",
                    "credentials": {
                        "credentials_type": "OAuth",
                        "client_id": "...",
                        "client_secret": "...",
                        "refresh_token": "...",
                    },
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="QuickBooks",
                source_type="quickbooks",
                category=SourceCategory.FINANCE,
                description="Accounting software for small businesses.",
                documentation_url="https://docs.airbyte.com/integrations/sources/quickbooks",
                auth_type="oauth",
                config_template={
                    "credentials": {
                        "client_id": "...",
                        "client_secret": "...",
                        "refresh_token": "...",
                        "realm_id": "...",
                    },
                    "start_date": "2020-01-01",
                    "sandbox": False,
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="NetSuite",
                source_type="netsuite",
                category=SourceCategory.FINANCE,
                description="Enterprise resource planning (ERP) software.",
                documentation_url="https://docs.airbyte.com/integrations/sources/netsuite",
                auth_type="oauth",
                config_template={
                    "realm": "123456",
                    "consumer_key": "...",
                    "consumer_secret": "...",
                    "token_key": "...",
                    "token_secret": "...",
                },
            )
        )

        # =====================================================================
        # FILE / STORAGE SOURCES
        # =====================================================================

        self._add_source(
            SourceInfo(
                name="Amazon S3",
                source_type="s3",
                category=SourceCategory.FILE,
                description="AWS cloud object storage.",
                documentation_url="https://docs.airbyte.com/integrations/sources/s3",
                auth_type="api_key",
                popular=True,
                config_template={
                    "bucket": "your-bucket",
                    "aws_access_key_id": "...",
                    "aws_secret_access_key": "...",
                    "region_name": "us-east-1",
                    "path_prefix": "data/",
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="Google Cloud Storage",
                source_type="gcs",
                category=SourceCategory.FILE,
                description="Google Cloud object storage.",
                documentation_url="https://docs.airbyte.com/integrations/sources/gcs",
                auth_type="oauth",
                config_template={
                    "bucket": "your-bucket",
                    "service_account": "{ ... }",
                },
            )
        )

        self._add_source(
            SourceInfo(
                name="Azure Blob Storage",
                source_type="azure-blob-storage",
                category=SourceCategory.FILE,
                description="Microsoft Azure cloud object storage.",
                documentation_url="https://docs.airbyte.com/integrations/sources/azure-blob-storage",
                auth_type="api_key",
                config_template={
                    "azure_blob_storage_account_name": "your_account",
                    "azure_blob_storage_account_key": "...",
                    "azure_blob_storage_container_name": "your-container",
                },
            )
        )

        self.logger.info(
            f"Loaded {len(self._sources)} Airbyte sources into catalog"
        )

    def _add_source(self, source: SourceInfo) -> None:
        """Add a source to the catalog."""
        self._sources[source.source_type] = source

    def get_source(self, source_type: str) -> Optional[SourceInfo]:
        """
        Get information about a specific source.

        Args:
            source_type: Airbyte source type identifier

        Returns:
            Source information or None if not found
        """
        return self._sources.get(source_type)

    def get_by_category(self, category: SourceCategory) -> List[SourceInfo]:
        """
        Get all sources in a category.

        Args:
            category: Source category to filter by

        Returns:
            List of sources in the category
        """
        return [s for s in self._sources.values() if s.category == category]

    def get_popular(self) -> List[SourceInfo]:
        """
        Get popular/commonly used sources.

        Returns:
            List of popular sources
        """
        return [s for s in self._sources.values() if s.popular]

    def search(self, query: str) -> List[SourceInfo]:
        """
        Search sources by name or description.

        Args:
            query: Search string (case-insensitive)

        Returns:
            Matching sources
        """
        query_lower = query.lower()
        return [
            s
            for s in self._sources.values()
            if query_lower in s.name.lower() or query_lower in s.description.lower()
        ]

    def list_all(self) -> List[SourceInfo]:
        """
        List all sources in the catalog.

        Returns:
            All cataloged sources
        """
        return list(self._sources.values())

    def get_config_template(self, source_type: str) -> Dict:
        """
        Get configuration template for a source.

        Args:
            source_type: Airbyte source type identifier

        Returns:
            Configuration template dictionary
        """
        source = self.get_source(source_type)
        if source:
            return source.config_template.copy()
        return {}


# Convenience category accessors
class DatabaseSources:
    """Quick access to database sources."""

    POSTGRES = "postgres"
    MYSQL = "mysql"
    MSSQL = "mssql"
    MONGODB = "mongodb-v2"
    ORACLE = "oracle"
    DUCKDB = "duckdb"


class WarehouseSources:
    """Quick access to data warehouse sources."""

    SNOWFLAKE = "snowflake"
    BIGQUERY = "bigquery"
    REDSHIFT = "redshift"
    DATABRICKS = "databricks"


class SaaSSources:
    """Quick access to SaaS application sources."""

    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    STRIPE = "stripe"
    ZENDESK = "zendesk-support"
    GITHUB = "github"
    JIRA = "jira"
    SLACK = "slack"
    NOTION = "notion"
    AIRTABLE = "airtable"
    GOOGLE_SHEETS = "google-sheets"
    GOOGLE_ANALYTICS = "google-analytics-data-api"
    GOOGLE_ADS = "google-ads"
    FACEBOOK_MARKETING = "facebook-marketing"
    LINKEDIN_ADS = "linkedin-ads"
    QUICKBOOKS = "quickbooks"
    NETSUITE = "netsuite"
    WORKDAY = "workday"
