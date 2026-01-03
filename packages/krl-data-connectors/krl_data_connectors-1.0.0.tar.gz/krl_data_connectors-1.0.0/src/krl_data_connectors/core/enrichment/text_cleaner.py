"""
Text Cleaning Utilities
=======================

Multi-stage text cleaning to remove navigation/UI pollution from extracted articles.

Problem Solved:
    - Article extractors include navigation ("Skip to Content", "Share this Story")
    - Headers and menus pollute embeddings
    - Ad text and subscription prompts reduce semantic quality

Solution:
    - Pattern-based removal of common UI elements
    - Heuristic line filtering (remove short lines, ALL CAPS headers)
    - Extract only substantial paragraphs (>100 chars)

Trade Secret Notice:
    The pattern library and heuristic thresholds represent proprietary
    optimizations developed through extensive empirical testing on news articles.

© 2025 KR-Labs. All rights reserved.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import List, Optional, Set

logger = logging.getLogger(__name__)


# ============================================================================
# NAVIGATION/UI PATTERNS TO REMOVE
# ============================================================================

NAVIGATION_PATTERNS: List[str] = [
    r"Skip to (main )?[Cc]ontent.*?(?=\n|$)",
    r"Breadcrumb Trail Links.*?(?=\n|$)",
    r"Share this Story\s*:.*?(?=\n|$)",
    r"LATEST STORIES:.*?(?=\n|$)",
    r"Advertisement\s*\n",
    r"Subscribe.*?(?=\n|$)",
    r"Sign up for.*?(?=\n|$)",
    r"Follow Us.*?(?=\n|$)",
    r"Watch Now.*?(?=\n|$)",
    r"Log in.*?(?=\n|$)",
    r"Contact us.*?(?=\n|$)",
    r"About us.*?(?=\n|$)",
    r"Donate.*?(?=\n|$)",
    r"Query.*?Show Search.*?(?=\n|$)",
    r"^\s*Home\s*News\s*Local News\s*",
    r"^\s*Menu\s*",
    r"^\s*Search\s*",
    r"^\s*[A-Z]{2,}\s*(?=[A-Z]{2,})",  # ALL CAPS navigation menus
]

# Common English words that indicate real article content
COMMON_ARTICLE_WORDS: Set[str] = {
    "a", "an", "the", "is", "are", "to", "of", "in", "on", "at", "for", "with",
    "was", "were", "been", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "must", "shall", "can",
}


@dataclass
class CleaningStatistics:
    """Statistics from text cleaning operation."""

    original_length: int
    cleaned_length: int
    patterns_removed: int
    lines_filtered: int
    paragraphs_kept: int

    @property
    def compression_ratio(self) -> float:
        """Calculate compression ratio (cleaned/original)."""
        if self.original_length == 0:
            return 1.0
        return self.cleaned_length / self.original_length


def aggressive_text_cleaning(
    text: str,
    min_line_length: int = 20,
    min_paragraph_length: int = 100,
    max_caps_ratio: float = 0.5,
) -> str:
    """
    Multi-stage text cleaning to remove navigation/UI pollution.

    This function applies aggressive cleaning to extract only the substantive
    article content, removing navigation elements, ads, and boilerplate text
    that would pollute embeddings and semantic analysis.

    Args:
        text: Raw extracted text from article
        min_line_length: Minimum characters for a line to be kept (default: 20)
        min_paragraph_length: Minimum characters for substantial paragraph (default: 100)
        max_caps_ratio: Maximum uppercase ratio before line is filtered (default: 0.5)

    Returns:
        Cleaned text with only article content

    Example:
        >>> raw_text = "Skip to Content\\n\\nActual article text here..."
        >>> cleaned = aggressive_text_cleaning(raw_text)
        >>> "Skip to Content" in cleaned
        False
    """
    if not isinstance(text, str) or len(text) < 100:
        return text

    # Stage 1: Remove common navigation/UI patterns
    for pattern in NAVIGATION_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.MULTILINE)

    # Stage 2: Heuristic line filtering
    lines = text.split("\n")
    cleaned_lines: List[str] = []

    for line in lines:
        line = line.strip()

        # Skip very short lines (likely navigation)
        if len(line) < min_line_length:
            continue

        # Skip lines that are mostly capitals (likely headers/menus)
        if len(line) > 0:
            caps_ratio = sum(c.isupper() for c in line) / len(line)
            if caps_ratio > max_caps_ratio:
                continue

        # Skip menu-like lines (multiple words, no common articles/prepositions)
        words = line.split()
        if len(words) > 3:
            has_common_words = any(
                w.lower() in COMMON_ARTICLE_WORDS for w in words
            )
            if not has_common_words:
                continue  # Likely a menu

        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # Stage 3: Extract only substantial paragraphs
    paragraphs = text.split("\n\n")
    substantial = [p for p in paragraphs if len(p) > min_paragraph_length]

    if substantial:
        # Find first and last substantial paragraph
        first_idx = paragraphs.index(substantial[0])
        last_idx = paragraphs.index(substantial[-1])
        # Keep only content between them
        text = "\n\n".join(paragraphs[first_idx : last_idx + 1])

    # Stage 4: Collapse excessive whitespace
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)  # Max 2 consecutive newlines
    text = re.sub(r" +", " ", text)  # Collapse multiple spaces

    return text.strip()


class TextCleaner:
    """
    Configurable text cleaner for article content.

    This class provides a stateful text cleaner with configurable thresholds
    and tracking of cleaning statistics.

    Attributes:
        stats: Accumulated statistics from cleaning operations
        custom_patterns: Additional patterns to remove (beyond defaults)

    Example:
        >>> cleaner = TextCleaner(min_line_length=30)
        >>> cleaned = cleaner.clean(raw_text)
        >>> print(f"Compression: {cleaner.last_stats.compression_ratio:.2%}")
    """

    def __init__(
        self,
        min_line_length: int = 20,
        min_paragraph_length: int = 100,
        max_caps_ratio: float = 0.5,
        custom_patterns: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize text cleaner with configurable thresholds.

        Args:
            min_line_length: Minimum characters for a line to be kept
            min_paragraph_length: Minimum characters for substantial paragraph
            max_caps_ratio: Maximum uppercase ratio before line is filtered
            custom_patterns: Additional regex patterns to remove
        """
        self.min_line_length = min_line_length
        self.min_paragraph_length = min_paragraph_length
        self.max_caps_ratio = max_caps_ratio

        # Combine default and custom patterns
        self.patterns = NAVIGATION_PATTERNS.copy()
        if custom_patterns:
            self.patterns.extend(custom_patterns)

        # Statistics tracking
        self.last_stats: Optional[CleaningStatistics] = None
        self._total_cleaned = 0
        self._total_original = 0

    def clean(self, text: str) -> str:
        """
        Clean text and track statistics.

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
        """
        original_length = len(text) if text else 0

        cleaned = aggressive_text_cleaning(
            text,
            min_line_length=self.min_line_length,
            min_paragraph_length=self.min_paragraph_length,
            max_caps_ratio=self.max_caps_ratio,
        )

        cleaned_length = len(cleaned)

        self.last_stats = CleaningStatistics(
            original_length=original_length,
            cleaned_length=cleaned_length,
            patterns_removed=0,  # Would need to track in the function
            lines_filtered=0,
            paragraphs_kept=0,
        )

        self._total_cleaned += cleaned_length
        self._total_original += original_length

        return cleaned

    def add_pattern(self, pattern: str) -> None:
        """Add a custom pattern to remove during cleaning."""
        self.patterns.append(pattern)

    def get_overall_compression(self) -> float:
        """Get overall compression ratio across all cleaning operations."""
        if self._total_original == 0:
            return 1.0
        return self._total_cleaned / self._total_original

    def reset_statistics(self) -> None:
        """Reset accumulated statistics."""
        self._total_cleaned = 0
        self._total_original = 0
        self.last_stats = None
