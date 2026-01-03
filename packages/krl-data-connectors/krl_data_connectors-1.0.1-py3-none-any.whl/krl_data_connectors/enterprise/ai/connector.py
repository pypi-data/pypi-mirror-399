# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
AI Connector - Unified LLM + Memory Interface
==============================================

Provides a unified interface combining OpenRouter (LLM) and
Supermemory (RAG/Memory) for intelligent data analysis workflows.

Features:
    - Automatic RAG (Retrieval-Augmented Generation)
    - Conversation memory management
    - Multi-model LLM access
    - Context-aware responses
    - Streaming support

Enterprise Tier Feature ($299/mo).

Example:
    >>> from krl_data_connectors.enterprise.ai import create_ai_connector
    >>>
    >>> ai = create_ai_connector()
    >>>
    >>> # Chat with automatic memory
    >>> response = await ai.chat(
    ...     "What were the GDP growth trends in 2024?",
    ...     use_memory=True
    ... )
    >>>
    >>> # Store knowledge for retrieval
    >>> await ai.store_knowledge(
    ...     "Federal Reserve Policy Report 2024...",
    ...     tags=["fed", "policy", "2024"]
    ... )
    >>>
    >>> # Query with RAG
    >>> response = await ai.chat_with_rag(
    ...     "Summarize the Fed's interest rate decisions",
    ...     memory_container="fed-documents"
    ... )
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import (
    Any,
    AsyncIterator,
    Dict,
    List,
    Optional,
    Union,
)

from krl_data_connectors.enterprise.ai.openrouter import (
    OpenRouterClient,
    OpenRouterConfig,
    ChatMessage,
    ChatCompletion,
    MessageRole,
    StreamChunk,
)

from krl_data_connectors.enterprise.ai.supermemory import (
    SupermemoryClient,
    SupermemoryConfig,
    Document,
    SearchResult,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class AIConnectorConfig:
    """Configuration for AI Connector."""
    
    # OpenRouter settings
    openrouter_api_key: Optional[str] = None
    default_model: str = "anthropic/claude-3.5-sonnet"
    temperature: float = 0.7
    max_tokens: int = 4096
    
    # Supermemory settings
    supermemory_api_key: Optional[str] = None
    default_memory_container: str = "krl-knowledge"
    conversation_container: str = "krl-conversations"
    
    # RAG settings
    rag_context_limit: int = 5
    rag_min_score: float = 0.5
    include_sources: bool = True
    
    # Memory settings
    auto_save_conversations: bool = True
    session_id: Optional[str] = None
    
    # Prompt templates
    system_prompt: str = """You are an expert data analyst and economist working with Khipu Intelligence.
You have access to comprehensive economic data and can help analyze trends,
explain concepts, and provide insights based on available information.
Always cite sources when using retrieved context."""


# =============================================================================
# AI Connector
# =============================================================================

class AIConnector:
    """
    Unified AI interface combining LLM and Memory capabilities.
    
    Integrates OpenRouter for LLM access and Supermemory for RAG,
    providing an easy-to-use interface for AI-powered analysis.
    
    Features:
        - Chat with 200+ LLM models via OpenRouter
        - Automatic RAG with Supermemory retrieval
        - Conversation memory for multi-turn context
        - Knowledge storage and retrieval
        - Streaming responses
    
    Example:
        >>> ai = AIConnector()
        >>>
        >>> # Simple chat
        >>> response = await ai.chat("Explain inflation")
        >>> print(response)
        >>>
        >>> # Chat with RAG
        >>> response = await ai.chat_with_rag(
        ...     "What does the Fed report say about rates?",
        ...     memory_container="fed-reports"
        ... )
        >>>
        >>> # Store knowledge
        >>> await ai.store_knowledge("Report content...", tags=["fed"])
    """
    
    def __init__(
        self,
        config: Optional[AIConnectorConfig] = None,
        openrouter_api_key: Optional[str] = None,
        supermemory_api_key: Optional[str] = None,
    ):
        """
        Initialize AI Connector.
        
        Args:
            config: Configuration object
            openrouter_api_key: OpenRouter API key (overrides config)
            supermemory_api_key: Supermemory API key (overrides config)
        """
        self.config = config or AIConnectorConfig()
        
        if openrouter_api_key:
            self.config.openrouter_api_key = openrouter_api_key
        if supermemory_api_key:
            self.config.supermemory_api_key = supermemory_api_key
        
        # Initialize clients
        self._llm: Optional[OpenRouterClient] = None
        self._memory: Optional[SupermemoryClient] = None
        
        # Conversation history
        self._conversation_history: List[ChatMessage] = []
        self._sources: List[SearchResult] = []
        
        logger.info(
            "AIConnector initialized",
            extra={
                "model": self.config.default_model,
                "memory_container": self.config.default_memory_container,
            }
        )
    
    @property
    def llm(self) -> OpenRouterClient:
        """Get LLM client (lazy initialization)."""
        if self._llm is None:
            self._llm = OpenRouterClient(
                config=OpenRouterConfig(
                    api_key=self.config.openrouter_api_key,
                    default_model=self.config.default_model,
                )
            )
        return self._llm
    
    @property
    def memory(self) -> SupermemoryClient:
        """Get memory client (lazy initialization)."""
        if self._memory is None:
            self._memory = SupermemoryClient(
                config=SupermemoryConfig(
                    api_key=self.config.supermemory_api_key,
                    default_container=self.config.default_memory_container,
                )
            )
        return self._memory
    
    async def close(self):
        """Close all clients."""
        if self._llm:
            await self._llm.close()
            self._llm = None
        if self._memory:
            await self._memory.close()
            self._memory = None
    
    # =========================================================================
    # Basic Chat
    # =========================================================================
    
    async def chat(
        self,
        message: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        use_memory: bool = False,
        save_to_memory: bool = True,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Send a chat message and get a response.
        
        Args:
            message: User message
            model: Model to use (default from config)
            system: System prompt (default from config)
            use_memory: Whether to use conversation history
            save_to_memory: Whether to save exchange to memory
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        
        Returns:
            Model response as string
        
        Example:
            >>> response = await ai.chat("What is GDP?")
            >>> print(response)
        """
        messages = self._build_messages(
            message,
            system=system or self.config.system_prompt,
            include_history=use_memory,
        )
        
        response = await self.llm.chat(
            messages=messages,
            model=model or self.config.default_model,
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
        )
        
        content = response.content or ""
        
        # Save to conversation history
        if use_memory or save_to_memory:
            self._conversation_history.append(
                ChatMessage(role=MessageRole.USER, content=message)
            )
            self._conversation_history.append(
                ChatMessage(role=MessageRole.ASSISTANT, content=content)
            )
        
        # Optionally save to long-term memory
        if save_to_memory and self.config.auto_save_conversations:
            try:
                await self.memory.add_memory(
                    user_message=message,
                    assistant_response=content,
                    container_tag=self.config.conversation_container,
                    session_id=self.config.session_id,
                )
            except Exception as e:
                logger.warning(f"Failed to save conversation to memory: {e}")
        
        return content
    
    async def chat_stream(
        self,
        message: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        use_memory: bool = False,
    ) -> AsyncIterator[str]:
        """
        Stream a chat response.
        
        Args:
            message: User message
            model: Model to use
            system: System prompt
            use_memory: Whether to use conversation history
        
        Yields:
            Response chunks as strings
        
        Example:
            >>> async for chunk in ai.chat_stream("Tell me about inflation"):
            ...     print(chunk, end="", flush=True)
        """
        messages = self._build_messages(
            message,
            system=system or self.config.system_prompt,
            include_history=use_memory,
        )
        
        full_response = ""
        async for chunk in self.llm.chat_stream(
            messages=messages,
            model=model or self.config.default_model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        ):
            full_response += chunk.delta
            yield chunk.delta
        
        # Save to history
        self._conversation_history.append(
            ChatMessage(role=MessageRole.USER, content=message)
        )
        self._conversation_history.append(
            ChatMessage(role=MessageRole.ASSISTANT, content=full_response)
        )
    
    # =========================================================================
    # RAG (Retrieval-Augmented Generation)
    # =========================================================================
    
    async def chat_with_rag(
        self,
        message: str,
        memory_container: Optional[str] = None,
        model: Optional[str] = None,
        system: Optional[str] = None,
        context_limit: Optional[int] = None,
        min_score: Optional[float] = None,
    ) -> str:
        """
        Chat with retrieval-augmented generation.
        
        Searches memory for relevant context and includes it in the prompt.
        
        Args:
            message: User message
            memory_container: Container to search for context
            model: Model to use
            system: System prompt
            context_limit: Maximum context items to include
            min_score: Minimum relevance score for context
        
        Returns:
            Model response with RAG context
        
        Example:
            >>> # Store some documents first
            >>> await ai.store_knowledge("Fed Report: Rates increased...")
            >>>
            >>> # Query with RAG
            >>> response = await ai.chat_with_rag(
            ...     "What did the Fed decide about rates?",
            ...     memory_container="krl-knowledge"
            ... )
        """
        # Search for relevant context
        self._sources = await self.memory.search(
            query=message,
            container_tag=memory_container or self.config.default_memory_container,
            limit=context_limit or self.config.rag_context_limit,
            min_score=min_score or self.config.rag_min_score,
        )
        
        # Build context string
        context_parts = []
        for i, result in enumerate(self._sources, 1):
            context_parts.append(f"[Source {i}] {result.content}")
        
        context_str = "\n\n".join(context_parts) if context_parts else "No relevant context found."
        
        # Build RAG system prompt
        rag_system = (
            (system or self.config.system_prompt) + 
            f"\n\n## Retrieved Context\n\n{context_str}\n\n"
            "Use the above context to inform your response. "
            "Cite sources by number when referencing specific information."
        )
        
        # Generate response
        messages = self._build_messages(message, system=rag_system)
        
        response = await self.llm.chat(
            messages=messages,
            model=model or self.config.default_model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        
        content = response.content or ""
        
        # Optionally append sources
        if self.config.include_sources and self._sources:
            content += "\n\n---\n**Sources:**\n"
            for i, src in enumerate(self._sources, 1):
                preview = src.content[:100] + "..." if len(src.content) > 100 else src.content
                content += f"\n[{i}] Score: {src.score:.2f} - {preview}"
        
        return content
    
    def get_last_sources(self) -> List[SearchResult]:
        """Get sources from the last RAG query."""
        return self._sources
    
    # =========================================================================
    # Knowledge Management
    # =========================================================================
    
    async def store_knowledge(
        self,
        content: str,
        container_tag: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Document:
        """
        Store knowledge for later retrieval.
        
        Args:
            content: Content to store (text, URL, or file URL)
            container_tag: Container to store in
            tags: Tags for categorization
            metadata: Additional metadata
        
        Returns:
            Document object
        
        Example:
            >>> doc = await ai.store_knowledge(
            ...     "Economic growth in Q4 was 2.8%...",
            ...     tags=["gdp", "q4-2024"],
            ...     metadata={"source": "BEA"}
            ... )
        """
        full_metadata = metadata or {}
        if tags:
            full_metadata["tags"] = tags
        
        return await self.memory.add_document(
            content=content,
            container_tag=container_tag or self.config.default_memory_container,
            metadata=full_metadata,
        )
    
    async def store_url(
        self,
        url: str,
        container_tag: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Document:
        """
        Store content from a URL.
        
        Supermemory will fetch and process the URL content.
        
        Args:
            url: URL to fetch and store
            container_tag: Container to store in
            metadata: Additional metadata
        
        Returns:
            Document object
        """
        full_metadata = metadata or {}
        full_metadata["source_url"] = url
        
        return await self.memory.add_document(
            content=url,
            container_tag=container_tag or self.config.default_memory_container,
            metadata=full_metadata,
        )
    
    async def search_knowledge(
        self,
        query: str,
        container_tag: Optional[str] = None,
        limit: int = 10,
    ) -> List[SearchResult]:
        """
        Search stored knowledge.
        
        Args:
            query: Search query
            container_tag: Container to search
            limit: Maximum results
        
        Returns:
            List of SearchResult objects
        """
        return await self.memory.search(
            query=query,
            container_tag=container_tag or self.config.default_memory_container,
            limit=limit,
        )
    
    # =========================================================================
    # Analysis Helpers
    # =========================================================================
    
    async def analyze_data(
        self,
        data: Union[str, Dict, List],
        question: str,
        model: Optional[str] = None,
    ) -> str:
        """
        Analyze data with a specific question.
        
        Args:
            data: Data to analyze (JSON, dict, or string)
            question: Analysis question
            model: Model to use
        
        Returns:
            Analysis response
        
        Example:
            >>> data = {"gdp_growth": [2.1, 2.4, 2.8], "quarters": ["Q1", "Q2", "Q3"]}
            >>> analysis = await ai.analyze_data(
            ...     data,
            ...     "What is the trend in GDP growth?"
            ... )
        """
        import json
        
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, indent=2)
        else:
            data_str = str(data)
        
        prompt = f"""Analyze the following data and answer the question.

## Data
```
{data_str}
```

## Question
{question}

Provide a clear, data-driven analysis."""
        
        return await self.chat(prompt, model=model, use_memory=False)
    
    async def summarize(
        self,
        content: str,
        style: str = "concise",
        model: Optional[str] = None,
    ) -> str:
        """
        Summarize content.
        
        Args:
            content: Content to summarize
            style: Summary style ("concise", "detailed", "bullet_points")
            model: Model to use
        
        Returns:
            Summary string
        """
        style_instructions = {
            "concise": "Provide a brief 2-3 sentence summary.",
            "detailed": "Provide a comprehensive summary covering all key points.",
            "bullet_points": "Summarize as a bulleted list of key points.",
        }
        
        prompt = f"""Summarize the following content.

{style_instructions.get(style, style_instructions['concise'])}

## Content
{content}"""
        
        return await self.chat(prompt, model=model, use_memory=False)
    
    # =========================================================================
    # Conversation Management
    # =========================================================================
    
    def clear_history(self):
        """Clear conversation history."""
        self._conversation_history = []
        self._sources = []
    
    def get_history(self) -> List[ChatMessage]:
        """Get conversation history."""
        return self._conversation_history.copy()
    
    def set_session(self, session_id: str):
        """Set session ID for memory storage."""
        self.config.session_id = session_id
    
    # =========================================================================
    # Internal Methods
    # =========================================================================
    
    def _build_messages(
        self,
        user_message: str,
        system: Optional[str] = None,
        include_history: bool = False,
    ) -> List[Dict[str, str]]:
        """Build messages list for API call."""
        messages = []
        
        # System message
        if system:
            messages.append({"role": "system", "content": system})
        
        # Conversation history
        if include_history:
            for msg in self._conversation_history[-10:]:  # Last 10 exchanges
                messages.append(msg.to_dict())
        
        # Current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# =============================================================================
# Factory Functions
# =============================================================================

def create_ai_connector(
    openrouter_api_key: Optional[str] = None,
    supermemory_api_key: Optional[str] = None,
    model: str = "anthropic/claude-3.5-sonnet",
    memory_container: str = "krl-knowledge",
) -> AIConnector:
    """
    Create an AI Connector with common settings.
    
    Args:
        openrouter_api_key: OpenRouter API key
        supermemory_api_key: Supermemory API key
        model: Default LLM model
        memory_container: Default memory container
    
    Returns:
        Configured AIConnector instance
    
    Example:
        >>> ai = create_ai_connector(model="openai/gpt-4o")
        >>> response = await ai.chat("Hello!")
    """
    config = AIConnectorConfig(
        openrouter_api_key=openrouter_api_key,
        supermemory_api_key=supermemory_api_key,
        default_model=model,
        default_memory_container=memory_container,
    )
    return AIConnector(config=config)


def create_analyst_connector(
    openrouter_api_key: Optional[str] = None,
    supermemory_api_key: Optional[str] = None,
) -> AIConnector:
    """
    Create an AI Connector configured for economic analysis.
    
    Pre-configured with economics-focused system prompt and
    appropriate model settings.
    
    Returns:
        AIConnector configured for analysis tasks
    """
    config = AIConnectorConfig(
        openrouter_api_key=openrouter_api_key,
        supermemory_api_key=supermemory_api_key,
        default_model="anthropic/claude-3.5-sonnet",
        default_memory_container="krl-economic-data",
        temperature=0.3,  # Lower for more factual responses
        system_prompt="""You are an expert economist and policy analyst working with Khipu Intelligence.

Your expertise includes:
- Macroeconomic analysis and forecasting
- Monetary and fiscal policy evaluation
- Econometric methods and causal inference
- International trade and finance
- Labor economics and demographic trends

When analyzing data or answering questions:
1. Be precise and cite specific figures when available
2. Acknowledge uncertainty and data limitations
3. Provide context for economic indicators
4. Explain methodology when relevant
5. Consider multiple perspectives on policy questions

Always base your analysis on evidence and sound economic reasoning."""
    )
    return AIConnector(config=config)
