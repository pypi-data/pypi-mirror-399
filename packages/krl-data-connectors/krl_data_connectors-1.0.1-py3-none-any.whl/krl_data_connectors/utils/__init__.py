# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""Utility functions for krl-data-connectors."""

from .config import find_config_file
from .formats import (
    detect_format,
    get_supported_formats,
    load_resource_to_dataframe,
)

__all__ = [
    "find_config_file",
    "detect_format",
    "get_supported_formats",
    "load_resource_to_dataframe",
]
