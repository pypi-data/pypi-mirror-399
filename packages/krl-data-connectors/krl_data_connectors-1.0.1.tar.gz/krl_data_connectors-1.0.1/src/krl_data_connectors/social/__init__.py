# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""Social services data connectors."""

from .acf_connector import ACFConnector
from .irs990_connector import IRS990Connector
from .ssa_connector import SSAConnector

__all__ = ["SSAConnector", "ACFConnector", "IRS990Connector"]
