# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
KRL Data Connectors - Community Civic Domain

Free tier civic data connectors for government open data.
"""

from .datagov_catalog import DataGovCatalogConnector

__all__ = [
    "DataGovCatalogConnector",
]
