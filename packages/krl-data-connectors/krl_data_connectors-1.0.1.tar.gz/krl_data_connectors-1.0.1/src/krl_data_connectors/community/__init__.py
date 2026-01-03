# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Deloatch, Williams, Faison, & Parker, LLLP.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
KRL Data Connectors - Community Tier

Free tier with 15 essential data connectors across multiple domains.
Open source, no license required.

Available Connectors:
- Economic: FRED_Basic, BLS_Basic, BEA_National, OECD_Indicators
- Demographic: Census_ACS_Public, Census_CBP_Summary, SSA_Actuarial
- Health: FDA_Drug_Approvals
- Environmental: NOAA_Climate_Current
- Geographic: USGS_Earthquakes
- Financial: Treasury_Public_Debt
- Education: NCES_School_Directory

Usage:
    from krl_data_connectors.community import FREDBasicConnector
    
    fred = FREDBasicConnector()
    data = fred.fetch(query_type="series", series_id="UNRATE")
"""

from .bls_basic import BLSBasicConnector
from .census_acs_public import CensusACSPublicConnector

# Civic domain
from .civic.datagov_catalog import DataGovCatalogConnector

# Demographic domain
from .demographic.census_cbp_summary import CountyBusinessPatternsConnector
from .demographic.ssa_actuarial import SSAConnector
from .demographic.datagov_demographic import DataGovDemographicConnector

# Economic domain
from .economic.bea_national import BEAConnector
from .economic.oecd_indicators import OECDConnector
from .economic.datagov_economic import DataGovEconomicConnector

# Education domain
from .education.nces_school_directory import NCESConnector
from .education.datagov_education import DataGovEducationConnector

# Environmental domain
from .environmental.noaa_climate_current import NOAAClimateConnector

# Financial domain
from .financial.treasury_public_debt import TreasuryConnector
from .financial.datagov_financial import DataGovFinancialConnector

# Root-level connectors
from .fred_basic import FREDBasicConnector

# Geographic domain
from .geographic.usgs_earthquakes import USGSConnector
from .geographic.datagov_geographic import DataGovGeographicConnector

# Health domain
from .health.fda_drug_approvals import FDAConnector

__all__ = [
    # Root-level
    "FREDBasicConnector",
    "BLSBasicConnector",
    "CensusACSPublicConnector",
    # Civic
    "DataGovCatalogConnector",
    # Economic
    "BEAConnector",
    "OECDConnector",
    "DataGovEconomicConnector",
    # Demographic
    "CountyBusinessPatternsConnector",
    "SSAConnector",
    "DataGovDemographicConnector",
    # Health
    "FDAConnector",
    # Environmental
    "NOAAClimateConnector",
    # Geographic
    "USGSConnector",
    "DataGovGeographicConnector",
    # Financial
    "TreasuryConnector",
    "DataGovFinancialConnector",
    # Education
    "NCESConnector",
    "DataGovEducationConnector",
]
