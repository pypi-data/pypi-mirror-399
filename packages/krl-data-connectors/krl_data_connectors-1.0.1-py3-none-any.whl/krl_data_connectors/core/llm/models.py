# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
AI Models and Data Types

Pydantic models for AI service requests and responses.
"""

from __future__ import annotations

from datetime import datetime, UTC
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, field_validator


# =============================================================================
# ENUMS
# =============================================================================

class MessageRole(str, Enum):
    """Chat message roles."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class DocumentSource(str, Enum):
    """Memory document source types."""
    ANALYSIS_RESULT = "analysis_result"
    DATASET_SUMMARY = "dataset_summary"
    USER_NOTE = "user_note"
    REPORT_EXCERPT = "report_excerpt"
    EXTERNAL_IMPORT = "external_import"
    SYSTEM_GENERATED = "system_generated"


class DocumentType(str, Enum):
    """Memory document type classification."""
    INSIGHT = "insight"
    METHODOLOGY = "methodology"
    FINDING = "finding"
    RECOMMENDATION = "recommendation"
    DEFINITION = "definition"
    CONTEXT = "context"
    REFERENCE = "reference"


class SuggestionType(str, Enum):
    """AI suggestion types."""
    MODEL = "model"
    FEATURE = "feature"
    ANALYSIS = "analysis"
    INSIGHT = "insight"
    CAUSAL = "causal"
    METHODOLOGY = "methodology"


# =============================================================================
# CHAT MODELS
# =============================================================================

class Message(BaseModel):
    """Chat message."""
    id: Optional[str] = None
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    model_config = {"use_enum_values": True}


class AnalysisContext(BaseModel):
    """Context about current analysis for better AI responses."""
    dataset_id: Optional[str] = None
    project_id: Optional[str] = None
    variables: Optional[List[str]] = None
    method_type: Optional[str] = None
    current_step: Optional[str] = None


class ChatRequest(BaseModel):
    """Chat completion request."""
    messages: List[Message]
    model: Optional[str] = "anthropic/claude-3.5-sonnet"
    temperature: Optional[float] = Field(default=0.7, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=2048, ge=1, le=32000)
    use_memory: Optional[bool] = True
    memory_limit: Optional[int] = Field(default=5, ge=1, le=20)
    analysis_context: Optional[AnalysisContext] = None
    stream: Optional[bool] = False
    user_id: Optional[str] = None
    
    model_config = {"use_enum_values": True}


class TokenUsage(BaseModel):
    """Token usage tracking."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatResponse(BaseModel):
    """Chat completion response."""
    id: str
    message: Message
    model: str
    usage: TokenUsage
    memory_documents: Optional[List["MemoryDocument"]] = None
    finish_reason: Optional[str] = None
    
    model_config = {"use_enum_values": True}


class StreamingChunk(BaseModel):
    """Streaming chat chunk."""
    id: str
    delta: str
    finished: bool = False
    usage: Optional[TokenUsage] = None
    error: Optional[str] = None


# =============================================================================
# MEMORY/RAG MODELS
# =============================================================================

class DocumentMetadata(BaseModel):
    """Memory document metadata."""
    source: DocumentSource = DocumentSource.USER_NOTE
    type: DocumentType = DocumentType.CONTEXT
    project_id: Optional[str] = None
    analysis_id: Optional[str] = None
    dataset_id: Optional[str] = None
    tags: Optional[List[str]] = None
    user_id: Optional[str] = None
    
    model_config = {"use_enum_values": True, "extra": "allow"}


class MemoryDocument(BaseModel):
    """Memory document stored in Supermemory."""
    id: str
    content: str
    title: Optional[str] = None
    metadata: Optional[DocumentMetadata] = None
    score: Optional[float] = None
    relevance_score: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = {"use_enum_values": True}


class MemorySearchRequest(BaseModel):
    """Memory search request."""
    query: str
    limit: Optional[int] = Field(default=10, ge=1, le=50)
    filters: Optional[Dict[str, Any]] = None
    container_tag: Optional[str] = None
    user_id: Optional[str] = None
    min_relevance: Optional[float] = Field(default=0.5, ge=0, le=1)


class MemorySearchResponse(BaseModel):
    """Memory search response."""
    documents: List[MemoryDocument]
    total_found: int
    query_time_ms: float


class AddDocumentRequest(BaseModel):
    """Add document to memory request."""
    content: str
    title: Optional[str] = None
    metadata: Optional[DocumentMetadata] = None
    container_tag: Optional[str] = None
    user_id: Optional[str] = None


class AddDocumentResponse(BaseModel):
    """Add document response."""
    id: str
    success: bool
    message: Optional[str] = None


# =============================================================================
# SUGGESTION MODELS
# =============================================================================

class SuggestionAction(BaseModel):
    """Action that can be applied from a suggestion."""
    type: Literal["apply", "dismiss", "explore"]
    target: Optional[str] = None
    params: Optional[Dict[str, Any]] = None


class AISuggestion(BaseModel):
    """AI-generated suggestion."""
    id: str
    type: SuggestionType
    title: str
    description: str
    confidence: float = Field(ge=0, le=1)
    action: Optional[SuggestionAction] = None
    rationale: Optional[str] = None
    
    model_config = {"use_enum_values": True}


class AISuggestContext(BaseModel):
    """Context for generating suggestions."""
    location: Literal["model_builder", "data_explorer", "policy_impact", "report_builder"]
    current_data: Optional[Dict[str, Any]] = None
    variables: Optional[List[str]] = None
    methodology: Optional[str] = None
    dataset_id: Optional[str] = None
    project_id: Optional[str] = None
    user_id: Optional[str] = None


class AISuggestRequest(BaseModel):
    """Request for AI suggestions."""
    context: AISuggestContext
    max_suggestions: Optional[int] = Field(default=5, ge=1, le=10)


class AISuggestResponse(BaseModel):
    """AI suggestions response."""
    suggestions: List[AISuggestion]
    context_used: bool = False
    model_used: str = ""


# =============================================================================
# USAGE MODELS
# =============================================================================

class AIUsageStats(BaseModel):
    """AI usage statistics for a user."""
    user_id: str
    period: str  # YYYY-MM format
    queries_used: int = 0
    queries_limit: int = 0
    memory_docs_used: int = 0
    memory_docs_limit: int = 0
    tokens_used: int = 0
    last_query_at: Optional[datetime] = None
    
    @property
    def queries_remaining(self) -> int:
        if self.queries_limit < 0:  # Unlimited
            return -1
        return max(0, self.queries_limit - self.queries_used)
    
    @property
    def is_query_limit_reached(self) -> bool:
        if self.queries_limit < 0:  # Unlimited
            return False
        return self.queries_used >= self.queries_limit


class TierLimits(BaseModel):
    """AI limits per subscription tier."""
    tier: str
    ai_queries_per_month: int  # -1 for unlimited
    ai_memory_documents: int  # -1 for unlimited
    
    @classmethod
    def for_tier(cls, tier: str) -> "TierLimits":
        """Get limits for a specific tier."""
        limits = {
            "community": cls(tier="community", ai_queries_per_month=0, ai_memory_documents=0),
            "pro": cls(tier="pro", ai_queries_per_month=100, ai_memory_documents=0),
            "team": cls(tier="team", ai_queries_per_month=500, ai_memory_documents=1000),
            "enterprise": cls(tier="enterprise", ai_queries_per_month=-1, ai_memory_documents=-1),
        }
        return limits.get(tier, limits["community"])


# Update forward references
ChatResponse.model_rebuild()
