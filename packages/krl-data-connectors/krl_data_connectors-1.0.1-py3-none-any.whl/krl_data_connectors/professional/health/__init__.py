# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Professional Health Data Connectors

This module provides full access to health and healthcare data sources:
- BRFSS - Behavioral Risk Factor Surveillance System
- County Health Rankings - county-level health metrics
- HRSA - Health Resources and Services Administration
- NIH Reporter - NIH research grants and projects
- PLACES - CDC chronic disease prevalence
- Data.gov Health - HHS, CDC, FDA datasets (unlimited search, bulk export)
"""

from .brfss import BRFSSConnector
from .county_health_rankings import CountyHealthRankingsConnector
from .hrsa import HRSAConnector
from .nih_reporter import NIHConnector
from .places import PLACESConnector
from .datagov_health_full import DataGovHealthFullConnector

__all__ = [
    "CountyHealthRankingsConnector",
    "BRFSSConnector",
    "HRSAConnector",
    "NIHConnector",
    "PLACESConnector",
    "DataGovHealthFullConnector",
]
