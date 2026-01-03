# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
AI API Router

FastAPI router providing AI endpoints for:
- Streaming chat completions
- Memory search and storage
- Analysis suggestions
- Usage tracking

Integrates with OpenRouter and Supermemory backends.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .models import (
    ChatRequest,
    ChatResponse,
    MemorySearchRequest,
    MemorySearchResponse,
    AddDocumentRequest,
    AddDocumentResponse,
    AISuggestRequest,
    AISuggestResponse,
    AIUsageStats,
)
from .ai_service import AIService, AIServiceConfig

logger = logging.getLogger(__name__)


# =============================================================================
# ROUTER SETUP
# =============================================================================

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

# Global AI service instance (initialized on startup)
_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """Get the AI service instance."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService(AIServiceConfig.from_env())
    return _ai_service


async def get_user_tier(
    x_user_tier: Optional[str] = Header(None, alias="X-User-Tier"),
    authorization: Optional[str] = Header(None),
) -> str:
    """
    Extract user tier from request headers.
    
    In production, this would validate the JWT and lookup the user's tier.
    """
    if x_user_tier and x_user_tier in ("community", "pro", "team", "enterprise"):
        return x_user_tier
    return "community"


async def get_user_id(
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    authorization: Optional[str] = Header(None),
) -> str:
    """
    Extract user ID from request headers.
    
    In production, this would extract from JWT token.
    """
    return x_user_id or "anonymous"


# =============================================================================
# HEALTH CHECK
# =============================================================================

class AIHealthResponse(BaseModel):
    """AI service health status."""
    status: str
    llm_available: bool
    memory_available: bool
    version: str = "1.0.0"


@router.get("/health", response_model=AIHealthResponse)
async def ai_health_check(
    ai_service: AIService = Depends(get_ai_service),
) -> AIHealthResponse:
    """Check AI service health and availability."""
    return AIHealthResponse(
        status="healthy" if ai_service.is_llm_available else "degraded",
        llm_available=ai_service.is_llm_available,
        memory_available=ai_service.is_memory_available,
    )


# =============================================================================
# CHAT ENDPOINTS
# =============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest,
    ai_service: AIService = Depends(get_ai_service),
    tier: str = Depends(get_user_tier),
    user_id: str = Depends(get_user_id),
) -> ChatResponse:
    """
    Send a chat completion request.
    
    Supports RAG-enhanced responses when memory is enabled.
    """
    # Set user ID on request
    request.user_id = user_id
    
    try:
        response = await ai_service.chat(request, tier)
        return response
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    ai_service: AIService = Depends(get_ai_service),
    tier: str = Depends(get_user_tier),
    user_id: str = Depends(get_user_id),
) -> StreamingResponse:
    """
    Send a streaming chat completion request.
    
    Returns Server-Sent Events (SSE) with response chunks.
    """
    request.user_id = user_id
    request.stream = True
    
    async def generate_sse():
        try:
            async for chunk in ai_service.chat_stream(request, tier):
                data = json.dumps({
                    "id": chunk.id,
                    "delta": chunk.delta,
                    "finished": chunk.finished,
                    "usage": chunk.usage.model_dump() if chunk.usage else None,
                    "error": chunk.error,
                })
                yield f"data: {data}\n\n"
                
                if chunk.finished:
                    yield "data: [DONE]\n\n"
                    break
                    
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            error_data = json.dumps({
                "id": "",
                "delta": "",
                "finished": True,
                "error": str(e),
            })
            yield f"data: {error_data}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# =============================================================================
# MEMORY ENDPOINTS
# =============================================================================

@router.post("/memory/search", response_model=MemorySearchResponse)
async def search_memory(
    request: MemorySearchRequest,
    ai_service: AIService = Depends(get_ai_service),
    tier: str = Depends(get_user_tier),
    user_id: str = Depends(get_user_id),
) -> MemorySearchResponse:
    """
    Search memory for relevant documents.
    
    Requires Team tier or above.
    """
    request.user_id = user_id
    
    try:
        response = await ai_service.search_memory(request, tier)
        return response
    except Exception as e:
        logger.error(f"Memory search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memory/add", response_model=AddDocumentResponse)
async def add_to_memory(
    request: AddDocumentRequest,
    ai_service: AIService = Depends(get_ai_service),
    tier: str = Depends(get_user_tier),
    user_id: str = Depends(get_user_id),
) -> AddDocumentResponse:
    """
    Add a document to memory.
    
    Requires Team tier or above.
    """
    request.user_id = user_id
    
    try:
        response = await ai_service.add_to_memory(request, tier)
        return response
    except Exception as e:
        logger.error(f"Add to memory error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# SUGGESTION ENDPOINTS
# =============================================================================

@router.post("/suggest", response_model=AISuggestResponse)
async def get_suggestions(
    request: AISuggestRequest,
    ai_service: AIService = Depends(get_ai_service),
    tier: str = Depends(get_user_tier),
    user_id: str = Depends(get_user_id),
) -> AISuggestResponse:
    """
    Get AI-powered analysis suggestions.
    
    Provides context-aware recommendations based on current workflow.
    """
    request.context.user_id = user_id
    
    try:
        response = await ai_service.get_suggestions(request, tier)
        return response
    except Exception as e:
        logger.error(f"Suggestions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# USAGE ENDPOINTS
# =============================================================================

@router.get("/usage", response_model=AIUsageStats)
async def get_usage(
    ai_service: AIService = Depends(get_ai_service),
    tier: str = Depends(get_user_tier),
    user_id: str = Depends(get_user_id),
) -> AIUsageStats:
    """
    Get AI usage statistics for the current user.
    
    Returns query counts, limits, and remaining quota.
    """
    try:
        usage = ai_service.get_usage(user_id, tier)
        return usage
    except Exception as e:
        logger.error(f"Usage fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# MODELS ENDPOINT
# =============================================================================

class ModelInfo(BaseModel):
    """AI model information."""
    id: str
    name: str
    provider: str
    context_length: int
    recommended: bool


class ModelsResponse(BaseModel):
    """Available models response."""
    models: list[ModelInfo]


@router.get("/models", response_model=ModelsResponse)
async def list_models(
    ai_service: AIService = Depends(get_ai_service),
) -> ModelsResponse:
    """List available AI models."""
    models_dict = ai_service.llm.list_models()
    
    models = [
        ModelInfo(
            id=model_id,
            name=info["name"],
            provider=info["provider"],
            context_length=info["context_length"],
            recommended=info.get("recommended", False),
        )
        for model_id, info in models_dict.items()
    ]
    
    return ModelsResponse(models=models)


# =============================================================================
# LIFECYCLE
# =============================================================================

async def ai_router_startup():
    """Initialize AI service on startup."""
    global _ai_service
    logger.info("Initializing AI service...")
    _ai_service = AIService(AIServiceConfig.from_env())
    logger.info(f"AI service initialized - LLM: {_ai_service.is_llm_available}, Memory: {_ai_service.is_memory_available}")


async def ai_router_shutdown():
    """Cleanup AI service on shutdown."""
    global _ai_service
    if _ai_service:
        logger.info("Shutting down AI service...")
        await _ai_service.close()
        _ai_service = None
