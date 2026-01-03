# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
AI Service

Unified AI service combining OpenRouter LLM and Supermemory RAG capabilities.
Provides intelligent analysis assistance with context-aware responses.
"""

from __future__ import annotations

import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any, AsyncIterator, Dict, List, Optional, Union

from .openrouter_client import OpenRouterClient, OpenRouterConfig
from .supermemory_client import SupermemoryClient, SupermemoryConfig
from .models import (
    Message,
    MessageRole,
    ChatRequest,
    ChatResponse,
    StreamingChunk,
    TokenUsage,
    MemoryDocument,
    MemorySearchRequest,
    MemorySearchResponse,
    AddDocumentRequest,
    AddDocumentResponse,
    AISuggestion,
    AISuggestContext,
    AISuggestRequest,
    AISuggestResponse,
    SuggestionType,
    SuggestionAction,
    AIUsageStats,
    TierLimits,
)

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class AIServiceConfig:
    """AI service configuration."""
    openrouter_config: OpenRouterConfig = field(default_factory=OpenRouterConfig)
    supermemory_config: SupermemoryConfig = field(default_factory=SupermemoryConfig)
    
    # System prompts
    default_system_prompt: str = """You are an expert AI assistant for Khipu Intelligence, 
a platform for economic and policy research. You help users with:
- Data analysis and interpretation
- Statistical methodology guidance  
- Causal inference approaches
- Policy impact assessment
- Research design recommendations

Be precise, cite relevant methodologies, and provide actionable insights.
When relevant context from memory is provided, incorporate it naturally."""

    suggestion_system_prompt: str = """You are an AI assistant that provides 
analysis suggestions for researchers. Based on the context provided, suggest 
relevant analytical approaches, models, or methodologies. Return suggestions 
in a structured format with clear rationale."""

    # Feature flags
    enable_memory: bool = True
    memory_context_limit: int = 5
    
    @classmethod
    def from_env(cls) -> "AIServiceConfig":
        """Create configuration from environment variables."""
        return cls(
            openrouter_config=OpenRouterConfig(
                api_key=os.getenv("OPENROUTER_API_KEY", ""),
            ),
            supermemory_config=SupermemoryConfig(
                api_key=os.getenv("SUPERMEMORY_API_KEY", ""),
            ),
        )


# =============================================================================
# USAGE TRACKER
# =============================================================================

class AIUsageTracker:
    """
    Tracks AI usage per user for tier enforcement.
    
    In production, this would be backed by a database.
    """
    
    def __init__(self):
        self._usage: Dict[str, AIUsageStats] = {}
    
    def get_usage(self, user_id: str) -> AIUsageStats:
        """Get usage stats for a user."""
        period = self._current_period()
        key = f"{user_id}:{period}"
        
        if key not in self._usage:
            self._usage[key] = AIUsageStats(
                user_id=user_id,
                period=period,
            )
        
        return self._usage[key]
    
    def record_query(self, user_id: str, tokens_used: int = 0) -> AIUsageStats:
        """Record an AI query."""
        usage = self.get_usage(user_id)
        usage.queries_used += 1
        usage.tokens_used += tokens_used
        usage.last_query_at = datetime.now(UTC)
        return usage
    
    def record_memory_doc(self, user_id: str, count: int = 1) -> AIUsageStats:
        """Record memory document creation."""
        usage = self.get_usage(user_id)
        usage.memory_docs_used += count
        return usage
    
    def set_limits(self, user_id: str, tier: str) -> AIUsageStats:
        """Set usage limits based on tier."""
        usage = self.get_usage(user_id)
        limits = TierLimits.for_tier(tier)
        usage.queries_limit = limits.ai_queries_per_month
        usage.memory_docs_limit = limits.ai_memory_documents
        return usage
    
    def check_can_query(self, user_id: str, tier: str) -> tuple[bool, str]:
        """Check if user can make an AI query."""
        limits = TierLimits.for_tier(tier)
        
        if limits.ai_queries_per_month == 0:
            return False, "AI features not available on your tier"
        
        usage = self.get_usage(user_id)
        usage.queries_limit = limits.ai_queries_per_month
        
        if usage.is_query_limit_reached:
            return False, "Monthly AI query limit reached"
        
        return True, ""
    
    def check_can_add_memory(self, user_id: str, tier: str) -> tuple[bool, str]:
        """Check if user can add memory documents."""
        limits = TierLimits.for_tier(tier)
        
        if limits.ai_memory_documents == 0:
            return False, "Memory features not available on your tier"
        
        usage = self.get_usage(user_id)
        usage.memory_docs_limit = limits.ai_memory_documents
        
        if limits.ai_memory_documents > 0 and usage.memory_docs_used >= limits.ai_memory_documents:
            return False, "Memory document limit reached"
        
        return True, ""
    
    def _current_period(self) -> str:
        """Get current billing period."""
        now = datetime.now(UTC)
        return f"{now.year}-{now.month:02d}"


# =============================================================================
# AI SERVICE
# =============================================================================

class AIService:
    """
    Unified AI service for Khipu Intelligence.
    
    Combines LLM chat capabilities with RAG-powered context retrieval
    to provide intelligent, context-aware analysis assistance.
    """
    
    def __init__(self, config: Optional[AIServiceConfig] = None):
        self.config = config or AIServiceConfig.from_env()
        self.llm = OpenRouterClient(self.config.openrouter_config)
        self.memory = SupermemoryClient(self.config.supermemory_config)
        self.usage_tracker = AIUsageTracker()
    
    async def close(self):
        """Close all clients."""
        await self.llm.close()
    
    @property
    def is_llm_available(self) -> bool:
        """Check if LLM is available."""
        return bool(self.config.openrouter_config.api_key)
    
    @property
    def is_memory_available(self) -> bool:
        """Check if memory is available."""
        return self.memory.is_available
    
    async def chat(
        self,
        request: ChatRequest,
        tier: str = "community",
    ) -> ChatResponse:
        """
        Send a chat completion request with optional RAG context.
        
        Args:
            request: Chat request with messages and configuration
            tier: User's subscription tier
            
        Returns:
            ChatResponse with the assistant's message
        """
        user_id = request.user_id or "anonymous"
        
        # Check tier permissions
        can_query, error_msg = self.usage_tracker.check_can_query(user_id, tier)
        if not can_query:
            return ChatResponse(
                id=str(uuid.uuid4()),
                message=Message(
                    id=str(uuid.uuid4()),
                    role=MessageRole.ASSISTANT,
                    content=f"I'm sorry, but {error_msg}. Please upgrade your plan to continue using AI features.",
                    timestamp=datetime.now(UTC),
                ),
                model="",
                usage=TokenUsage(),
                finish_reason="tier_limit",
            )
        
        # Get memory context if enabled
        memory_docs: List[MemoryDocument] = []
        system_prompt = self.config.default_system_prompt
        
        if request.use_memory and self.is_memory_available and self.config.enable_memory:
            # Search for relevant context
            last_user_message = next(
                (m for m in reversed(request.messages) if m.role == MessageRole.USER),
                None
            )
            
            if last_user_message:
                search_result = await self.memory.search(
                    MemorySearchRequest(
                        query=last_user_message.content,
                        limit=request.memory_limit or self.config.memory_context_limit,
                        user_id=user_id,
                    )
                )
                memory_docs = search_result.documents
                
                # Enhance system prompt with context
                if memory_docs:
                    context_text = self._format_memory_context(memory_docs)
                    system_prompt = f"{self.config.default_system_prompt}\n\n{context_text}"
        
        # Make LLM request
        response = await self.llm.chat(request, system_prompt)
        
        # Track usage
        self.usage_tracker.record_query(
            user_id,
            response.usage.total_tokens if response.usage else 0
        )
        
        # Add memory documents to response
        response.memory_documents = memory_docs
        
        return response
    
    async def chat_stream(
        self,
        request: ChatRequest,
        tier: str = "community",
    ) -> AsyncIterator[StreamingChunk]:
        """
        Send a streaming chat completion request.
        
        Args:
            request: Chat request with messages and configuration
            tier: User's subscription tier
            
        Yields:
            StreamingChunk objects with response deltas
        """
        user_id = request.user_id or "anonymous"
        
        # Check tier permissions
        can_query, error_msg = self.usage_tracker.check_can_query(user_id, tier)
        if not can_query:
            yield StreamingChunk(
                id=str(uuid.uuid4()),
                delta=f"I'm sorry, but {error_msg}. Please upgrade your plan to continue using AI features.",
                finished=True,
                error=error_msg,
            )
            return
        
        # Get memory context if enabled
        system_prompt = self.config.default_system_prompt
        
        if request.use_memory and self.is_memory_available and self.config.enable_memory:
            last_user_message = next(
                (m for m in reversed(request.messages) if m.role == MessageRole.USER),
                None
            )
            
            if last_user_message:
                search_result = await self.memory.search(
                    MemorySearchRequest(
                        query=last_user_message.content,
                        limit=request.memory_limit or self.config.memory_context_limit,
                        user_id=user_id,
                    )
                )
                
                if search_result.documents:
                    context_text = self._format_memory_context(search_result.documents)
                    system_prompt = f"{self.config.default_system_prompt}\n\n{context_text}"
        
        # Track usage (before streaming starts)
        self.usage_tracker.record_query(user_id, 0)
        
        # Stream response
        async for chunk in self.llm.chat_stream(request, system_prompt):
            # Update token count when finished
            if chunk.finished and chunk.usage:
                usage = self.usage_tracker.get_usage(user_id)
                usage.tokens_used += chunk.usage.total_tokens
            
            yield chunk
    
    async def search_memory(
        self,
        request: MemorySearchRequest,
        tier: str = "community",
    ) -> MemorySearchResponse:
        """
        Search memory for relevant documents.
        
        Args:
            request: Search request
            tier: User's subscription tier
            
        Returns:
            MemorySearchResponse with matching documents
        """
        # Memory search requires at least Team tier
        limits = TierLimits.for_tier(tier)
        if limits.ai_memory_documents == 0:
            return MemorySearchResponse(
                documents=[],
                total_found=0,
                query_time_ms=0,
            )
        
        return await self.memory.search(request)
    
    async def add_to_memory(
        self,
        request: AddDocumentRequest,
        tier: str = "community",
    ) -> AddDocumentResponse:
        """
        Add a document to memory.
        
        Args:
            request: Add document request
            tier: User's subscription tier
            
        Returns:
            AddDocumentResponse with result
        """
        user_id = request.user_id or "anonymous"
        
        # Check tier permissions
        can_add, error_msg = self.usage_tracker.check_can_add_memory(user_id, tier)
        if not can_add:
            return AddDocumentResponse(
                id="",
                success=False,
                message=error_msg,
            )
        
        # Add to memory
        response = await self.memory.add_document(request)
        
        # Track usage
        if response.success:
            self.usage_tracker.record_memory_doc(user_id)
        
        return response
    
    async def get_suggestions(
        self,
        request: AISuggestRequest,
        tier: str = "community",
    ) -> AISuggestResponse:
        """
        Get AI-powered analysis suggestions.
        
        Args:
            request: Suggestion request with context
            tier: User's subscription tier
            
        Returns:
            AISuggestResponse with suggestions
        """
        user_id = request.context.user_id or "anonymous"
        
        # Check tier permissions
        can_query, error_msg = self.usage_tracker.check_can_query(user_id, tier)
        if not can_query:
            return AISuggestResponse(
                suggestions=[],
                context_used=False,
                model_used="",
            )
        
        # Build context message
        context_message = self._build_suggestion_context(request.context)
        
        # Create chat request
        chat_request = ChatRequest(
            messages=[
                Message(
                    role=MessageRole.USER,
                    content=context_message,
                )
            ],
            model="anthropic/claude-3-haiku",  # Use faster model for suggestions
            temperature=0.7,
            max_tokens=1024,
            use_memory=True,
            user_id=user_id,
        )
        
        # Get response
        response = await self.llm.chat(chat_request, self.config.suggestion_system_prompt)
        
        # Track usage
        self.usage_tracker.record_query(
            user_id,
            response.usage.total_tokens if response.usage else 0
        )
        
        # Parse suggestions from response
        suggestions = self._parse_suggestions(
            response.message.content,
            request.max_suggestions or 5
        )
        
        return AISuggestResponse(
            suggestions=suggestions,
            context_used=True,
            model_used=response.model,
        )
    
    def get_usage(self, user_id: str, tier: str) -> AIUsageStats:
        """Get usage stats for a user."""
        usage = self.usage_tracker.get_usage(user_id)
        limits = TierLimits.for_tier(tier)
        usage.queries_limit = limits.ai_queries_per_month
        usage.memory_docs_limit = limits.ai_memory_documents
        return usage
    
    def _format_memory_context(self, documents: List[MemoryDocument]) -> str:
        """Format memory documents as context for the LLM."""
        if not documents:
            return ""
        
        lines = ["Relevant context from memory:"]
        for i, doc in enumerate(documents, 1):
            title = doc.title or f"Document {i}"
            relevance = f" (relevance: {doc.relevance_score:.0%})" if doc.relevance_score else ""
            lines.append(f"\n[{title}]{relevance}:")
            lines.append(doc.content)
        
        return "\n".join(lines)
    
    def _build_suggestion_context(self, context: AISuggestContext) -> str:
        """Build context message for suggestion generation."""
        parts = [f"Generate analysis suggestions for the {context.location} page."]
        
        if context.methodology:
            parts.append(f"Current methodology: {context.methodology}")
        
        if context.variables:
            parts.append(f"Variables being considered: {', '.join(context.variables)}")
        
        if context.current_data:
            parts.append(f"Current configuration: {context.current_data}")
        
        parts.append("\nProvide 3-5 specific, actionable suggestions with confidence scores.")
        
        return "\n".join(parts)
    
    def _parse_suggestions(
        self,
        content: str,
        max_suggestions: int,
    ) -> List[AISuggestion]:
        """Parse suggestions from LLM response."""
        suggestions = []
        
        # Simple parsing - in production, use structured output
        lines = content.strip().split("\n")
        current_suggestion = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for numbered suggestions
            if line[0].isdigit() and "." in line[:3]:
                if current_suggestion:
                    suggestions.append(current_suggestion)
                    if len(suggestions) >= max_suggestions:
                        break
                
                title = line.split(".", 1)[1].strip() if "." in line else line
                current_suggestion = AISuggestion(
                    id=str(uuid.uuid4()),
                    type=SuggestionType.ANALYSIS,
                    title=title[:100],
                    description="",
                    confidence=0.75,  # Default confidence
                )
            elif current_suggestion:
                # Add to description
                if current_suggestion.description:
                    current_suggestion.description += " " + line
                else:
                    current_suggestion.description = line
        
        # Add last suggestion
        if current_suggestion and len(suggestions) < max_suggestions:
            suggestions.append(current_suggestion)
        
        # If no structured suggestions found, create a generic one
        if not suggestions:
            suggestions.append(AISuggestion(
                id=str(uuid.uuid4()),
                type=SuggestionType.ANALYSIS,
                title="Analysis Recommendation",
                description=content[:500],
                confidence=0.7,
            ))
        
        return suggestions
