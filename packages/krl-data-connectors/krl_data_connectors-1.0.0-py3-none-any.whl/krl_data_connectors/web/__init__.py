# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""Web scraping and data extraction connectors."""

__all__: list[str] = []

# Re-export from professional tier
try:
    from krl_data_connectors.professional.web.web_scraper import WebScraperConnector
    __all__.append("WebScraperConnector")
except ImportError:
    pass
