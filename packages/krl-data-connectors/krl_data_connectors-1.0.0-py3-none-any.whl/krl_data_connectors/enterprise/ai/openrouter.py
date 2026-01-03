# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
OpenRouter Client - Unified LLM Access
======================================

Provides unified access to 200+ LLM models through OpenRouter's API,
including OpenAI, Anthropic, Google, Meta, Mistral, and more.

Features:
    - OpenAI-compatible API for easy migration
    - Automatic model fallback and routing
    - Streaming support for real-time responses
    - Cost tracking and usage analytics
    - Model-specific parameter handling

Enterprise Tier Feature ($299/mo).

Example:
    >>> from krl_data_connectors.enterprise.ai import OpenRouterClient
    >>>
    >>> client = OpenRouterClient()
    >>> 
    >>> # Simple chat completion
    >>> response = await client.chat(
    ...     messages=[{"role": "user", "content": "Analyze GDP trends"}],
    ...     model="anthropic/claude-3-sonnet"
    ... )
    >>> print(response.content)
    >>>
    >>> # Streaming response
    >>> async for chunk in client.chat_stream(
    ...     messages=[{"role": "user", "content": "Explain inflation"}],
    ...     model="openai/gpt-4o"
    ... ):
    ...     print(chunk.delta, end="")
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    AsyncIterator,
    Dict,
    List,
    Literal,
    Optional,
    Union,
)

import httpx

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class OpenRouterConfig:
    """Configuration for OpenRouter client."""
    
    api_key: Optional[str] = None
    base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "openai/gpt-4o-mini"
    timeout: float = 60.0
    max_retries: int = 3
    
    # App identification for OpenRouter rankings
    site_url: Optional[str] = "https://krlabs.dev"
    site_name: Optional[str] = "Khipu Intelligence"
    
    # Rate limiting
    requests_per_minute: int = 60
    
    def __post_init__(self):
        if self.api_key is None:
            self.api_key = os.environ.get("OPENROUTER_API_KEY")


# =============================================================================
# Data Types
# =============================================================================

class MessageRole(str, Enum):
    """Message roles for chat completions."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class ChatMessage:
    """A chat message."""
    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API-compatible dictionary."""
        d = {
            "role": self.role.value if isinstance(self.role, MessageRole) else self.role,
            "content": self.content,
        }
        if self.name:
            d["name"] = self.name
        if self.tool_call_id:
            d["tool_call_id"] = self.tool_call_id
        return d


@dataclass
class ToolCall:
    """A tool/function call from the model."""
    id: str
    type: str = "function"
    function_name: str = ""
    function_arguments: str = ""


@dataclass
class Choice:
    """A completion choice."""
    index: int
    message: Optional[ChatMessage] = None
    delta: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None
    native_finish_reason: Optional[str] = None
    tool_calls: List[ToolCall] = field(default_factory=list)


@dataclass
class Usage:
    """Token usage information."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class ChatCompletion:
    """A chat completion response."""
    id: str
    model: str
    choices: List[Choice]
    created: int
    object: str = "chat.completion"
    usage: Optional[Usage] = None
    
    @property
    def content(self) -> Optional[str]:
        """Get the content of the first choice."""
        if self.choices and self.choices[0].message:
            return self.choices[0].message.content
        return None
    
    @property
    def finish_reason(self) -> Optional[str]:
        """Get the finish reason of the first choice."""
        if self.choices:
            return self.choices[0].finish_reason
        return None


@dataclass
class StreamChunk:
    """A streaming response chunk."""
    id: str
    model: str
    delta: str
    finish_reason: Optional[str] = None
    role: Optional[str] = None


@dataclass
class ModelInfo:
    """Information about an available model."""
    id: str
    name: str
    description: Optional[str] = None
    context_length: int = 0
    pricing: Optional[Dict[str, float]] = None
    top_provider: Optional[str] = None


# =============================================================================
# OpenRouter Client
# =============================================================================

class OpenRouterClient:
    """
    OpenRouter API client for unified LLM access.
    
    Provides access to 200+ LLM models through a single, unified API.
    Supports the OpenAI-compatible interface for easy migration.
    
    Features:
        - Multi-model support (OpenAI, Anthropic, Google, etc.)
        - Automatic fallback routing
        - Streaming responses
        - Tool/function calling
        - Cost tracking
    
    Example:
        >>> client = OpenRouterClient()
        >>> 
        >>> # Basic completion
        >>> response = await client.chat(
        ...     messages=[{"role": "user", "content": "Hello!"}]
        ... )
        >>> print(response.content)
        >>>
        >>> # With specific model
        >>> response = await client.chat(
        ...     messages=[{"role": "user", "content": "Analyze this data"}],
        ...     model="anthropic/claude-3-opus"
        ... )
    """
    
    # Popular models for quick reference
    MODELS = {
        # OpenAI
        "gpt-4o": "openai/gpt-4o",
        "gpt-4o-mini": "openai/gpt-4o-mini",
        "gpt-4-turbo": "openai/gpt-4-turbo",
        "gpt-3.5-turbo": "openai/gpt-3.5-turbo",
        # Anthropic
        "claude-3-opus": "anthropic/claude-3-opus",
        "claude-3-sonnet": "anthropic/claude-3-sonnet",
        "claude-3-haiku": "anthropic/claude-3-haiku",
        "claude-3.5-sonnet": "anthropic/claude-3.5-sonnet",
        # Google
        "gemini-pro": "google/gemini-pro",
        "gemini-1.5-pro": "google/gemini-1.5-pro",
        "gemini-1.5-flash": "google/gemini-1.5-flash",
        # Meta
        "llama-3.1-70b": "meta-llama/llama-3.1-70b-instruct",
        "llama-3.1-8b": "meta-llama/llama-3.1-8b-instruct",
        # Mistral
        "mistral-large": "mistralai/mistral-large",
        "mistral-medium": "mistralai/mistral-medium",
        "mixtral-8x7b": "mistralai/mixtral-8x7b-instruct",
        # DeepSeek
        "deepseek-chat": "deepseek/deepseek-chat",
        "deepseek-coder": "deepseek/deepseek-coder",
    }
    
    def __init__(
        self,
        config: Optional[OpenRouterConfig] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize OpenRouter client.
        
        Args:
            config: Configuration object
            api_key: API key (overrides config and env var)
        """
        self.config = config or OpenRouterConfig()
        if api_key:
            self.config.api_key = api_key
        
        if not self.config.api_key:
            raise ValueError(
                "OpenRouter API key required. Set OPENROUTER_API_KEY environment "
                "variable or pass api_key parameter."
            )
        
        self._client: Optional[httpx.AsyncClient] = None
        self._request_count = 0
        
        logger.info(
            "OpenRouterClient initialized",
            extra={
                "default_model": self.config.default_model,
                "site_name": self.config.site_name,
            }
        )
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=self.config.timeout,
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": self.config.site_url or "",
                    "X-Title": self.config.site_name or "",
                },
            )
        return self._client
    
    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    def _resolve_model(self, model: Optional[str]) -> str:
        """Resolve model shorthand to full model ID."""
        if model is None:
            return self.config.default_model
        return self.MODELS.get(model, model)
    
    async def chat(
        self,
        messages: List[Union[Dict[str, Any], ChatMessage]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        response_format: Optional[Dict[str, str]] = None,
        user: Optional[str] = None,
        **kwargs,
    ) -> ChatCompletion:
        """
        Create a chat completion.
        
        Args:
            messages: List of chat messages
            model: Model to use (default from config)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            stop: Stop sequences
            tools: Available tools for function calling
            tool_choice: Tool selection strategy
            response_format: Response format (e.g., {"type": "json_object"})
            user: End-user identifier for abuse detection
            **kwargs: Additional model-specific parameters
        
        Returns:
            ChatCompletion response
        
        Example:
            >>> response = await client.chat(
            ...     messages=[
            ...         {"role": "system", "content": "You are an economist."},
            ...         {"role": "user", "content": "Explain GDP"}
            ...     ],
            ...     model="claude-3-sonnet",
            ...     temperature=0.5
            ... )
        """
        client = await self._get_client()
        
        # Convert messages to dicts
        msg_dicts = []
        for msg in messages:
            if isinstance(msg, ChatMessage):
                msg_dicts.append(msg.to_dict())
            else:
                msg_dicts.append(msg)
        
        # Build request body
        body: Dict[str, Any] = {
            "model": self._resolve_model(model),
            "messages": msg_dicts,
            "temperature": temperature,
            "stream": False,
        }
        
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
        if top_p is not None:
            body["top_p"] = top_p
        if stop is not None:
            body["stop"] = stop
        if tools is not None:
            body["tools"] = tools
        if tool_choice is not None:
            body["tool_choice"] = tool_choice
        if response_format is not None:
            body["response_format"] = response_format
        if user is not None:
            body["user"] = user
        
        # Add extra kwargs
        body.update(kwargs)
        
        logger.debug(f"Chat request: model={body['model']}, messages={len(msg_dicts)}")
        
        # Make request with retry
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                response = await client.post("/chat/completions", json=body)
                response.raise_for_status()
                data = response.json()
                
                self._request_count += 1
                return self._parse_completion(data)
                
            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code == 429:
                    # Rate limited - wait and retry
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limited, waiting {wait_time}s")
                    await asyncio.sleep(wait_time)
                elif e.response.status_code >= 500:
                    # Server error - retry
                    await asyncio.sleep(1)
                else:
                    raise
            except httpx.RequestError as e:
                last_error = e
                await asyncio.sleep(1)
        
        raise last_error or Exception("Max retries exceeded")
    
    async def chat_stream(
        self,
        messages: List[Union[Dict[str, Any], ChatMessage]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        """
        Create a streaming chat completion.
        
        Yields chunks of the response as they're generated.
        
        Args:
            messages: List of chat messages
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional parameters
        
        Yields:
            StreamChunk objects with delta content
        
        Example:
            >>> async for chunk in client.chat_stream(
            ...     messages=[{"role": "user", "content": "Write a story"}]
            ... ):
            ...     print(chunk.delta, end="", flush=True)
        """
        client = await self._get_client()
        
        # Convert messages
        msg_dicts = []
        for msg in messages:
            if isinstance(msg, ChatMessage):
                msg_dicts.append(msg.to_dict())
            else:
                msg_dicts.append(msg)
        
        body: Dict[str, Any] = {
            "model": self._resolve_model(model),
            "messages": msg_dicts,
            "temperature": temperature,
            "stream": True,
        }
        
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
        body.update(kwargs)
        
        async with client.stream("POST", "/chat/completions", json=body) as response:
            response.raise_for_status()
            
            async for line in response.aiter_lines():
                if not line or line.startswith(":"):
                    continue
                
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    
                    try:
                        data = json.loads(data_str)
                        chunk = self._parse_stream_chunk(data)
                        if chunk:
                            yield chunk
                    except json.JSONDecodeError:
                        continue
        
        self._request_count += 1
    
    async def list_models(self) -> List[ModelInfo]:
        """
        List available models.
        
        Returns:
            List of ModelInfo objects
        """
        client = await self._get_client()
        response = await client.get("/models")
        response.raise_for_status()
        data = response.json()
        
        models = []
        for item in data.get("data", []):
            models.append(ModelInfo(
                id=item.get("id", ""),
                name=item.get("name", item.get("id", "")),
                description=item.get("description"),
                context_length=item.get("context_length", 0),
                pricing=item.get("pricing"),
                top_provider=item.get("top_provider", {}).get("name"),
            ))
        
        return models
    
    async def get_generation(self, generation_id: str) -> Dict[str, Any]:
        """
        Get details about a specific generation.
        
        Args:
            generation_id: The generation ID from a completion response
        
        Returns:
            Generation details including cost and native token counts
        """
        client = await self._get_client()
        response = await client.get(f"/generation?id={generation_id}")
        response.raise_for_status()
        return response.json()
    
    def _parse_completion(self, data: Dict[str, Any]) -> ChatCompletion:
        """Parse API response into ChatCompletion."""
        choices = []
        for choice_data in data.get("choices", []):
            message_data = choice_data.get("message", {})
            message = ChatMessage(
                role=MessageRole(message_data.get("role", "assistant")),
                content=message_data.get("content", ""),
            )
            
            tool_calls = []
            for tc in message_data.get("tool_calls", []):
                tool_calls.append(ToolCall(
                    id=tc.get("id", ""),
                    type=tc.get("type", "function"),
                    function_name=tc.get("function", {}).get("name", ""),
                    function_arguments=tc.get("function", {}).get("arguments", ""),
                ))
            
            choices.append(Choice(
                index=choice_data.get("index", 0),
                message=message,
                finish_reason=choice_data.get("finish_reason"),
                native_finish_reason=choice_data.get("native_finish_reason"),
                tool_calls=tool_calls,
            ))
        
        usage_data = data.get("usage")
        usage = None
        if usage_data:
            usage = Usage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
            )
        
        return ChatCompletion(
            id=data.get("id", ""),
            model=data.get("model", ""),
            choices=choices,
            created=data.get("created", 0),
            object=data.get("object", "chat.completion"),
            usage=usage,
        )
    
    def _parse_stream_chunk(self, data: Dict[str, Any]) -> Optional[StreamChunk]:
        """Parse streaming chunk."""
        choices = data.get("choices", [])
        if not choices:
            return None
        
        delta = choices[0].get("delta", {})
        content = delta.get("content", "")
        
        if not content and not delta.get("role"):
            return None
        
        return StreamChunk(
            id=data.get("id", ""),
            model=data.get("model", ""),
            delta=content,
            finish_reason=choices[0].get("finish_reason"),
            role=delta.get("role"),
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# =============================================================================
# Convenience Functions
# =============================================================================

async def quick_chat(
    prompt: str,
    model: str = "openai/gpt-4o-mini",
    system: Optional[str] = None,
    api_key: Optional[str] = None,
) -> str:
    """
    Quick single-turn chat completion.
    
    Args:
        prompt: User prompt
        model: Model to use
        system: Optional system message
        api_key: Optional API key
    
    Returns:
        Model response content
    
    Example:
        >>> response = await quick_chat("What is GDP?")
    """
    async with OpenRouterClient(api_key=api_key) as client:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = await client.chat(messages=messages, model=model)
        return response.content or ""
