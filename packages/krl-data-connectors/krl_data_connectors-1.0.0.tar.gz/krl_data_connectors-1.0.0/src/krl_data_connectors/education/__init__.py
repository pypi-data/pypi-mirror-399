# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
KRL Data Connectors - Education Domain

Education-related data connectors.

REMSOM v2 Integration:
    NCESCCDConnector provides K-12 education data for the EDUCATION
    opportunity domain in the REMSOM observatory architecture.
"""

__all__: list[str] = []

# Local connectors
try:
    from krl_data_connectors.education.nces_ccd_connector import NCESCCDConnector
    __all__.append("NCESCCDConnector")
except ImportError:
    pass

# Re-export from professional tier
try:
    from krl_data_connectors.professional.education.nces_ccd import NCESConnector
    __all__.append("NCESConnector")
except ImportError:
    pass

try:
    from krl_data_connectors.professional.education.college_scorecard import CollegeScorecardConnector
    __all__.append("CollegeScorecardConnector")
except ImportError:
    pass

try:
    from krl_data_connectors.professional.education.ipeds import IPEDSConnector
    __all__.append("IPEDSConnector")
except ImportError:
    pass
