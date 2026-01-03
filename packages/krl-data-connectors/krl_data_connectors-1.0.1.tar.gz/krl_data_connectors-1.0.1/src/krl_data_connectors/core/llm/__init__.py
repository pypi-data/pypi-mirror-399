# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
LLM & AI Integration Module

Provides AI-powered capabilities for KRL Data Connectors:
- OpenRouter integration for LLM chat
- Supermemory integration for RAG/memory
- Streaming response handling
- Usage tracking and tier enforcement
"""

from .openrouter_client import OpenRouterClient, OpenRouterConfig
from .supermemory_client import SupermemoryClient, SupermemoryConfig
from .ai_service import AIService, AIServiceConfig
from .api_router import router as ai_router, ai_router_startup, ai_router_shutdown
from .models import (
    Message,
    MessageRole,
    ChatRequest,
    ChatResponse,
    StreamingChunk,
    TokenUsage,
    MemoryDocument,
    DocumentMetadata,
    DocumentSource,
    DocumentType,
    MemorySearchRequest,
    MemorySearchResponse,
    AddDocumentRequest,
    AddDocumentResponse,
    AISuggestion,
    AISuggestContext,
    AISuggestRequest,
    AISuggestResponse,
    SuggestionType,
    AIUsageStats,
    TierLimits,
)

__all__ = [
    # Clients
    "OpenRouterClient",
    "OpenRouterConfig",
    "SupermemoryClient",
    "SupermemoryConfig",
    # Service
    "AIService",
    "AIServiceConfig",
    # Router
    "ai_router",
    "ai_router_startup",
    "ai_router_shutdown",
    # Models
    "Message",
    "MessageRole",
    "ChatRequest",
    "ChatResponse",
    "StreamingChunk",
    "TokenUsage",
    "MemoryDocument",
    "DocumentMetadata",
    "DocumentSource",
    "DocumentType",
    "MemorySearchRequest",
    "MemorySearchResponse",
    "AddDocumentRequest",
    "AddDocumentResponse",
    "AISuggestion",
    "AISuggestContext",
    "AISuggestRequest",
    "AISuggestResponse",
    "SuggestionType",
    "AIUsageStats",
    "TierLimits",
]
