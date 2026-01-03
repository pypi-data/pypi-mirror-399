# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""Economic and development data connectors."""

__all__: list[str] = []

try:
    from .census_bds_connector import CensusBDSConnector
    __all__.append("CensusBDSConnector")
except ImportError:
    pass

try:
    from .oecd_connector import OECDConnector
    __all__.append("OECDConnector")
except ImportError:
    pass

try:
    from .world_bank_connector import WorldBankConnector, WorldBankIndicator
    __all__.extend(["WorldBankConnector", "WorldBankIndicator"])
except ImportError:
    pass

try:
    from .oecd_connector import OECDDataset
    __all__.append("OECDDataset")
except ImportError:
    pass

try:
    from .bea_connector import BEAConnector
    __all__.append("BEAConnector")
except ImportError:
    pass
