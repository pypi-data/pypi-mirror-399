# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Community Tier Health Connectors

This module provides free access to health and healthcare data sources:
- FDA Connector - FDA drug approval and safety data
- Data.gov Health - HHS, CDC, FDA datasets from Data.gov catalog

Usage:
    from krl_data_connectors.community.health import (
        FDAConnector,
        DataGovHealthConnector,
    )
"""

from krl_data_connectors.community.health.fda_drug_approvals import FDAConnector
from krl_data_connectors.community.health.datagov_health import DataGovHealthConnector

__all__ = [
    "FDAConnector",
    "DataGovHealthConnector",
]
