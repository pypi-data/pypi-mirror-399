# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2025 KR-Labs Foundation. All rights reserved.
# Licensed under Apache License 2.0 (see LICENSE file for details)

"""Civic engagement and voting access data connectors."""

__all__: list[str] = []

# Re-export from professional tier
try:
    from krl_data_connectors.professional.civic.google_civic_info import GoogleCivicInfoConnector
    __all__.append("GoogleCivicInfoConnector")
except ImportError:
    pass

# Local connectors
try:
    from .census_tiger_connector import CensusTIGERConnector, TIGERLayer, TIGERYear
    __all__.extend(["CensusTIGERConnector", "TIGERLayer", "TIGERYear"])
except ImportError:
    pass
