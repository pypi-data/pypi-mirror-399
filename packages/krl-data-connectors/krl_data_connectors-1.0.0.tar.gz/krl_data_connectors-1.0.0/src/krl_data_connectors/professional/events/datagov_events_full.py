# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Events Domain Connector - Professional Tier

Full access to events and disaster datasets with unlimited search.
Pre-configured for FEMA, NWS, USGS.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovEventsFullConnector(DataGovFullConnector):
    """
    Data.gov Events Domain Connector - Professional Tier
    """

    _connector_name = "DataGov_Events_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_events"

    DOMAIN_ORGANIZATIONS: List[str] = [
        "fema-gov",         # Federal Emergency Management Agency
        "nws-gov",          # National Weather Service
        "usgs-gov",         # US Geological Survey
    ]
    
    DOMAIN_TAGS: List[str] = [
        "events",
        "disasters",
        "emergencies",
        "incidents",
        "weather",
    ]
    
    DOMAIN_NAME: str = "Events"

    POPULAR_DATASETS: Dict[str, List[str]] = {
        "disasters": [
            "fema-disaster-declarations",
            "presidential-declarations",
            "disaster-assistance",
        ],
        "weather_events": [
            "storm-events",
            "severe-weather",
            "tornado-data",
            "hurricane-data",
        ],
        "emergencies": [
            "emergency-response",
            "public-assistance",
            "individual-assistance",
        ],
        "seismic": [
            "earthquake-catalog",
            "seismic-events",
            "volcano-events",
        ],
    }

    @requires_license
    def search_fema_datasets(
        self,
        query: str,
        formats: Optional[List[str]] = None,
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search FEMA datasets specifically."""
        return self.search_datasets(
            query=query,
            organization="fema-gov",
            formats=formats,
            rows=rows,
        )

    @requires_license
    def search_disaster_events(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for disaster event datasets."""
        search_query = f"disaster {query}" if query != "*:*" else "disaster declaration FEMA"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_weather_events(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for weather event datasets."""
        search_query = f"storm weather {query}" if query != "*:*" else "storm events severe weather"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_emergency_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for emergency response datasets."""
        search_query = f"emergency {query}" if query != "*:*" else "emergency response assistance"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_seismic_events(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for earthquake/seismic datasets."""
        search_query = f"earthquake {query}" if query != "*:*" else "earthquake seismic events"
        return self.search_datasets(query=search_query, organization="usgs-gov", rows=rows)

    def __repr__(self) -> str:
        return (
            f"DataGovEventsFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS})"
        )
