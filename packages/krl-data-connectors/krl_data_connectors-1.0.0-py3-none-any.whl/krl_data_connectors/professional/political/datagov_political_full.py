# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Data.gov Political Domain Connector - Professional Tier

Full access to political and election datasets.
Pre-configured for FEC, EAC, GPO.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.professional.civic.datagov_full import DataGovFullConnector
from krl_data_connectors.licensed_connector_mixin import requires_license


class DataGovPoliticalFullConnector(DataGovFullConnector):
    """
    Data.gov Political Domain Connector - Professional Tier
    """

    _connector_name = "DataGov_Political_Full"
    DEFAULT_DOWNLOAD_DIR = "~/.krl/data/datagov_political"

    DOMAIN_ORGANIZATIONS: List[str] = [
        "fec-gov",          # Federal Election Commission
        "eac-gov",          # Election Assistance Commission
        "gpo-gov",          # Government Publishing Office
    ]
    
    DOMAIN_TAGS: List[str] = [
        "elections",
        "voting",
        "campaigns",
        "legislation",
        "politics",
    ]
    
    DOMAIN_NAME: str = "Political"

    POPULAR_DATASETS: Dict[str, List[str]] = {
        "elections": [
            "election-results",
            "voter-turnout",
            "ballot-data",
        ],
        "campaign_finance": [
            "campaign-contributions",
            "candidate-spending",
            "pac-data",
        ],
        "legislation": [
            "congressional-records",
            "bill-data",
            "voting-records",
        ],
    }

    @requires_license
    def search_fec_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for FEC campaign finance datasets."""
        search_query = f"campaign finance {query}" if query != "*:*" else "campaign contributions FEC"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_election_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for election datasets."""
        search_query = f"election {query}" if query != "*:*" else "election results voting"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_legislation_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for legislation datasets."""
        search_query = f"legislation {query}" if query != "*:*" else "legislation congressional bills"
        return self.search_datasets(query=search_query, rows=rows)

    @requires_license
    def search_voter_data(
        self,
        query: str = "*:*",
        rows: int = 100,
    ) -> pd.DataFrame:
        """Search for voter datasets."""
        search_query = f"voter {query}" if query != "*:*" else "voter registration turnout"
        return self.search_datasets(query=search_query, rows=rows)

    def __repr__(self) -> str:
        return (
            f"DataGovPoliticalFullConnector("
            f"domain='{self.DOMAIN_NAME}', "
            f"organizations={self.DOMAIN_ORGANIZATIONS})"
        )
