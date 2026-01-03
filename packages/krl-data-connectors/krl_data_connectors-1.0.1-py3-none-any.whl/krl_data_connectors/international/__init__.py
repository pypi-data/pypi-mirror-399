# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""International and multilateral organization data connectors."""

__all__: list[str] = []

try:
    from .un_data_connector import UNDataConnector, UNIndicator, HDRIndicator
    __all__.extend(["UNDataConnector", "UNIndicator", "HDRIndicator"])
except ImportError:
    pass
