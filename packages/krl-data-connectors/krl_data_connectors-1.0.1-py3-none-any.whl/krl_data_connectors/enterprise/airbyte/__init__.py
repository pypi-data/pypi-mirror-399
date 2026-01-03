# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Airbyte Integration Module for KRL Data Connectors.

This module provides enterprise-grade integration with Airbyte's 600+ data connectors,
enabling seamless access to databases, data warehouses, SaaS applications, and more.

Key Features:
- Unified interface compatible with KRL's BaseConnector architecture
- Access to 600+ Airbyte connectors (databases, APIs, SaaS tools)
- Managed sync/ETL capabilities
- OAuth credential management
- Connection health monitoring
- Job scheduling and status tracking

Enterprise Tier Only:
This module requires an Airbyte Cloud API key or self-hosted Airbyte instance.
Available in KRL Enterprise tier.

Example Usage:
    >>> from krl_data_connectors.enterprise.airbyte import AirbyteClient
    >>> client = AirbyteClient(api_key="your-airbyte-api-key")
    >>> sources = client.list_available_sources()
    >>> connection = client.create_connection(
    ...     source_type="postgres",
    ...     source_config={"host": "...", "database": "..."},
    ...     destination_type="bigquery",
    ...     destination_config={...}
    ... )
"""

from .client import AirbyteClient
from .connector import AirbyteConnector
from .sources import (
    AirbyteSourceCatalog,
    DatabaseSources,
    SaaSSources,
    WarehouseSources,
)
from .sync import SyncManager, SyncJob, SyncStatus

__all__ = [
    # Core client
    "AirbyteClient",
    "AirbyteConnector",
    # Source catalogs
    "AirbyteSourceCatalog",
    "DatabaseSources",
    "SaaSSources",
    "WarehouseSources",
    # Sync management
    "SyncManager",
    "SyncJob",
    "SyncStatus",
]
