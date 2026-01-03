# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
KRL AI Services Integration Module
==================================

Enterprise-tier AI services integration providing:
- OpenRouter: Unified access to 200+ LLM models via single API
- Supermemory: Scalable memory/RAG API for AI applications

This module enables KRL applications to leverage state-of-the-art
AI capabilities for data analysis, natural language processing,
and intelligent data extraction.

Components:
    - OpenRouterClient: Multi-model LLM access with automatic routing
    - SupermemoryClient: Memory storage and semantic search
    - AIConnector: Unified interface combining LLM + Memory

Example:
    >>> from krl_data_connectors.enterprise.ai import (
    ...     OpenRouterClient,
    ...     SupermemoryClient,
    ...     AIConnector,
    ... )
    >>>
    >>> # Use OpenRouter for LLM completions
    >>> llm = OpenRouterClient()
    >>> response = await llm.chat("Analyze this economic data...")
    >>>
    >>> # Use Supermemory for RAG
    >>> memory = SupermemoryClient()
    >>> await memory.add_document("Economic report 2024...")
    >>> context = await memory.search("GDP growth trends")
"""

from krl_data_connectors.enterprise.ai.openrouter import (
    OpenRouterClient,
    OpenRouterConfig,
    ChatMessage,
    ChatCompletion,
    ModelInfo,
)

from krl_data_connectors.enterprise.ai.supermemory import (
    SupermemoryClient,
    SupermemoryConfig,
    Document,
    SearchResult,
    MemoryContainer,
)

from krl_data_connectors.enterprise.ai.connector import (
    AIConnector,
    AIConnectorConfig,
    create_ai_connector,
)

__all__ = [
    # OpenRouter
    "OpenRouterClient",
    "OpenRouterConfig",
    "ChatMessage",
    "ChatCompletion",
    "ModelInfo",
    # Supermemory
    "SupermemoryClient",
    "SupermemoryConfig",
    "Document",
    "SearchResult",
    "MemoryContainer",
    # AI Connector
    "AIConnector",
    "AIConnectorConfig",
    "create_ai_connector",
]
