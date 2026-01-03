# -*- coding: utf-8 -*-
"""
Aggressive Text Cleaning Utilities
==================================

Multi-stage text cleaning to remove navigation/UI pollution from extracted articles.

Problem Solved:
    - Article extractors include navigation ("Skip to Content", "Share this Story")
    - Headers and menus pollute embeddings
    - Ad text and subscription prompts reduce semantic quality

Solution:
    - Pattern-based removal of common UI elements
    - Heuristic line filtering (remove short lines, ALL CAPS headers)
    - Extract only substantial paragraphs (>100 chars)

Copyright (c) 2025 Khipu Research Labs. All rights reserved.
Trade Secret: Proprietary text cleaning heuristics.
"""

from __future__ import annotations

import re
from typing import List, Optional

__all__ = ["aggressive_text_cleaning", "TextCleaningConfig"]


class TextCleaningConfig:
    """Configuration for text cleaning operations."""

    # Navigation/UI patterns to remove
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
        r"^\s*[A-Z]{2,}\s*(?=[A-Z]{2,})",
    ]

    # Minimum line length to keep
    MIN_LINE_LENGTH: int = 20

    # Maximum uppercase ratio for non-header lines
    MAX_UPPERCASE_RATIO: float = 0.5

    # Common words indicating content (not menu)
    COMMON_CONTENT_WORDS: List[str] = [
        "a", "an", "the", "is", "are", "to", "of",
        "in", "on", "at", "for", "with",
    ]

    # Minimum paragraph length to be substantial
    MIN_PARAGRAPH_LENGTH: int = 100

    # Minimum text length to process
    MIN_TEXT_LENGTH: int = 100


def aggressive_text_cleaning(
    text: str,
    config: Optional[TextCleaningConfig] = None,
) -> str:
    """
    Multi-stage text cleaning to remove navigation/UI pollution.

    Stages:
        1. Pattern-based removal of common UI elements
        2. Heuristic line filtering
        3. Extract only substantial paragraphs
        4. Whitespace normalization

    Args:
        text: Raw extracted text from article.
        config: Optional cleaning configuration.

    Returns:
        Cleaned text with only article content.

    Example:
        >>> raw = "Skip to Content\\n\\nActual article text here..."
        >>> clean = aggressive_text_cleaning(raw)
        >>> assert "Skip to Content" not in clean
    """
    if config is None:
        config = TextCleaningConfig()

    if not isinstance(text, str) or len(text) < config.MIN_TEXT_LENGTH:
        return text if isinstance(text, str) else ""

    # Stage 1: Remove navigation/UI patterns
    text = _remove_navigation_patterns(text, config.NAVIGATION_PATTERNS)

    # Stage 2: Heuristic line filtering
    text = _filter_lines(
        text,
        min_length=config.MIN_LINE_LENGTH,
        max_uppercase_ratio=config.MAX_UPPERCASE_RATIO,
        common_words=config.COMMON_CONTENT_WORDS,
    )

    # Stage 3: Extract substantial paragraphs
    text = _extract_substantial_paragraphs(text, config.MIN_PARAGRAPH_LENGTH)

    # Stage 4: Normalize whitespace
    text = _normalize_whitespace(text)

    return text.strip()


def _remove_navigation_patterns(text: str, patterns: List[str]) -> str:
    """Remove common navigation/UI patterns from text."""
    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.MULTILINE)
    return text


def _filter_lines(
    text: str,
    min_length: int,
    max_uppercase_ratio: float,
    common_words: List[str],
) -> str:
    """Filter lines using heuristics."""
    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        # Skip very short lines (likely navigation)
        if len(line) < min_length:
            continue

        # Skip lines that are mostly capitals (likely headers/menus)
        if len(line) > 0:
            uppercase_ratio = sum(c.isupper() for c in line) / len(line)
            if uppercase_ratio > max_uppercase_ratio:
                continue

        # Skip menu-like lines (multiple words, no common articles/prepositions)
        words = line.split()
        if len(words) > 3:
            has_common_word = any(w.lower() in common_words for w in words)
            if not has_common_word:
                continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def _extract_substantial_paragraphs(text: str, min_length: int) -> str:
    """Extract only substantial paragraphs from text."""
    paragraphs = text.split("\n\n")
    substantial = [p for p in paragraphs if len(p) > min_length]

    if substantial:
        # Find first and last substantial paragraph
        first_idx = paragraphs.index(substantial[0])
        last_idx = paragraphs.index(substantial[-1])
        # Keep only content between them
        return "\n\n".join(paragraphs[first_idx : last_idx + 1])

    return text


def _normalize_whitespace(text: str) -> str:
    """Collapse excessive whitespace."""
    # Max 2 consecutive newlines
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    # Collapse multiple spaces
    text = re.sub(r" +", " ", text)
    return text
