"""
KRL Text Enrichment Module
==========================

Production-grade text extraction and enrichment with multi-method fallback.

Components:
    - JinaClient: Jina Reader API for JS-rendered page extraction
    - RobustTextEnricher: Multi-method fallback chain (96%+ success rate)
    - TextCleaner: Aggressive text cleaning for embedding quality

Trade Secret Notice:
    The fallback chain ordering and parameter tuning represent proprietary
    optimizations developed through extensive empirical testing.

Usage:
    >>> from krl_data_connectors.core.enrichment import RobustTextEnricher
    >>> enricher = RobustTextEnricher()
    >>> result = enricher.enrich_article(url="https://example.com/article")

© 2025 KR-Labs. All rights reserved.
"""

from .jina_client import JinaClient
from .robust_enricher import RobustTextEnricher
from .text_cleaner import aggressive_text_cleaning, TextCleaner

__all__ = [
    "JinaClient",
    "RobustTextEnricher",
    "TextCleaner",
    "aggressive_text_cleaning",
]
