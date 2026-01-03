# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
OpenRouter Client

Provides LLM chat capabilities via OpenRouter's unified API.
Supports streaming responses and multiple model providers.
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any, AsyncIterator, Dict, List, Optional, Union

import httpx

from .models import (
    Message,
    MessageRole,
    ChatRequest,
    ChatResponse,
    StreamingChunk,
    TokenUsage,
)

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class OpenRouterConfig:
    """OpenRouter client configuration."""
    api_key: str = field(default_factory=lambda: os.getenv("OPENROUTER_API_KEY", ""))
    base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "anthropic/claude-3.5-sonnet"
    timeout: float = 60.0
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Rate limiting
    requests_per_minute: int = 60
    tokens_per_minute: int = 100000
    
    # Headers
    app_name: str = "Khipu Intelligence"
    app_url: str = "https://krlabs.dev"
    
    def __post_init__(self):
        if not self.api_key:
            logger.warning("OpenRouter API key not configured")


# =============================================================================
# AVAILABLE MODELS
# =============================================================================

AVAILABLE_MODELS = {
    # Anthropic
    "anthropic/claude-3.5-sonnet": {
        "name": "Claude 3.5 Sonnet",
        "provider": "Anthropic",
        "context_length": 200000,
        "cost_per_1k_input": 0.003,
        "cost_per_1k_output": 0.015,
        "recommended": True,
    },
    "anthropic/claude-3-opus": {
        "name": "Claude 3 Opus",
        "provider": "Anthropic",
        "context_length": 200000,
        "cost_per_1k_input": 0.015,
        "cost_per_1k_output": 0.075,
        "recommended": False,
    },
    "anthropic/claude-3-haiku": {
        "name": "Claude 3 Haiku",
        "provider": "Anthropic",
        "context_length": 200000,
        "cost_per_1k_input": 0.00025,
        "cost_per_1k_output": 0.00125,
        "recommended": False,
    },
    # OpenAI
    "openai/gpt-4o": {
        "name": "GPT-4o",
        "provider": "OpenAI",
        "context_length": 128000,
        "cost_per_1k_input": 0.005,
        "cost_per_1k_output": 0.015,
        "recommended": True,
    },
    "openai/gpt-4o-mini": {
        "name": "GPT-4o Mini",
        "provider": "OpenAI",
        "context_length": 128000,
        "cost_per_1k_input": 0.00015,
        "cost_per_1k_output": 0.0006,
        "recommended": False,
    },
    # Google
    "google/gemini-pro-1.5": {
        "name": "Gemini Pro 1.5",
        "provider": "Google",
        "context_length": 2000000,
        "cost_per_1k_input": 0.00125,
        "cost_per_1k_output": 0.005,
        "recommended": False,
    },
    # Meta
    "meta-llama/llama-3.1-70b-instruct": {
        "name": "Llama 3.1 70B",
        "provider": "Meta",
        "context_length": 131072,
        "cost_per_1k_input": 0.00035,
        "cost_per_1k_output": 0.0004,
        "recommended": False,
    },
}


# =============================================================================
# CLIENT
# =============================================================================

class OpenRouterClient:
    """
    OpenRouter API client for LLM chat completions.
    
    Provides both synchronous and streaming chat capabilities
    with automatic retries and error handling.
    """
    
    def __init__(self, config: Optional[OpenRouterConfig] = None):
        self.config = config or OpenRouterConfig()
        self._client: Optional[httpx.AsyncClient] = None
        self._last_request_time: float = 0
        self._request_count: int = 0
        
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=self.config.timeout,
                headers=self._build_headers(),
            )
        return self._client
    
    def _build_headers(self) -> Dict[str, str]:
        """Build request headers."""
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.config.app_url,
            "X-Title": self.config.app_name,
        }
    
    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    async def chat(
        self,
        request: ChatRequest,
        system_prompt: Optional[str] = None,
    ) -> ChatResponse:
        """
        Send a chat completion request.
        
        Args:
            request: Chat request with messages and configuration
            system_prompt: Optional system prompt to prepend
            
        Returns:
            ChatResponse with the assistant's message
        """
        client = await self._get_client()
        
        # Build messages
        messages = self._build_messages(request.messages, system_prompt)
        
        # Build request payload
        payload = {
            "model": request.model or self.config.default_model,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": False,
        }
        
        # Make request with retries
        response = await self._make_request(client, payload)
        
        # Parse response
        return self._parse_response(response)
    
    async def chat_stream(
        self,
        request: ChatRequest,
        system_prompt: Optional[str] = None,
    ) -> AsyncIterator[StreamingChunk]:
        """
        Send a streaming chat completion request.
        
        Args:
            request: Chat request with messages and configuration
            system_prompt: Optional system prompt to prepend
            
        Yields:
            StreamingChunk objects with response deltas
        """
        client = await self._get_client()
        
        # Build messages
        messages = self._build_messages(request.messages, system_prompt)
        
        # Build request payload
        payload = {
            "model": request.model or self.config.default_model,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": True,
        }
        
        response_id = str(uuid.uuid4())
        total_content = ""
        
        try:
            async with client.stream(
                "POST",
                "/chat/completions",
                json=payload,
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    
                    data = line[6:]  # Remove "data: " prefix
                    
                    if data == "[DONE]":
                        yield StreamingChunk(
                            id=response_id,
                            delta="",
                            finished=True,
                        )
                        break
                    
                    try:
                        chunk_data = json.loads(data)
                        delta = chunk_data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        
                        if content:
                            total_content += content
                            yield StreamingChunk(
                                id=response_id,
                                delta=content,
                                finished=False,
                            )
                        
                        # Check for finish
                        finish_reason = chunk_data.get("choices", [{}])[0].get("finish_reason")
                        if finish_reason:
                            usage = chunk_data.get("usage", {})
                            yield StreamingChunk(
                                id=response_id,
                                delta="",
                                finished=True,
                                usage=TokenUsage(
                                    prompt_tokens=usage.get("prompt_tokens", 0),
                                    completion_tokens=usage.get("completion_tokens", 0),
                                    total_tokens=usage.get("total_tokens", 0),
                                ) if usage else None,
                            )
                            break
                            
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse streaming chunk: {data}")
                        continue
                        
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter streaming error: {e}")
            yield StreamingChunk(
                id=response_id,
                delta="",
                finished=True,
                error=str(e),
            )
        except Exception as e:
            logger.error(f"Unexpected streaming error: {e}")
            yield StreamingChunk(
                id=response_id,
                delta="",
                finished=True,
                error=str(e),
            )
    
    def _build_messages(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """Build message list for API request."""
        result = []
        
        # Add system prompt if provided
        if system_prompt:
            result.append({
                "role": "system",
                "content": system_prompt,
            })
        
        # Add conversation messages
        for msg in messages:
            result.append({
                "role": msg.role if isinstance(msg.role, str) else msg.role.value,
                "content": msg.content,
            })
        
        return result
    
    async def _make_request(
        self,
        client: httpx.AsyncClient,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Make API request with retries."""
        last_error: Optional[Exception] = None
        
        for attempt in range(self.config.max_retries):
            try:
                response = await client.post(
                    "/chat/completions",
                    json=payload,
                )
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code == 429:  # Rate limited
                    retry_after = float(e.response.headers.get("Retry-After", self.config.retry_delay * (attempt + 1)))
                    logger.warning(f"Rate limited, retrying after {retry_after}s")
                    await self._async_sleep(retry_after)
                elif e.response.status_code >= 500:  # Server error
                    logger.warning(f"Server error {e.response.status_code}, retrying...")
                    await self._async_sleep(self.config.retry_delay * (attempt + 1))
                else:
                    raise
                    
            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(f"Request timeout, retrying...")
                await self._async_sleep(self.config.retry_delay * (attempt + 1))
                
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error: {e}")
                raise
        
        raise last_error or Exception("Max retries exceeded")
    
    def _parse_response(self, response: Dict[str, Any]) -> ChatResponse:
        """Parse API response into ChatResponse."""
        choice = response.get("choices", [{}])[0]
        message_data = choice.get("message", {})
        usage_data = response.get("usage", {})
        
        return ChatResponse(
            id=response.get("id", str(uuid.uuid4())),
            message=Message(
                id=str(uuid.uuid4()),
                role=MessageRole(message_data.get("role", "assistant")),
                content=message_data.get("content", ""),
                timestamp=datetime.now(UTC),
            ),
            model=response.get("model", ""),
            usage=TokenUsage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
            ),
            finish_reason=choice.get("finish_reason"),
        )
    
    @staticmethod
    async def _async_sleep(seconds: float):
        """Async sleep for retry delays."""
        import asyncio
        await asyncio.sleep(seconds)
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model."""
        return AVAILABLE_MODELS.get(model_id)
    
    def list_models(self) -> Dict[str, Dict[str, Any]]:
        """List all available models."""
        return AVAILABLE_MODELS.copy()
