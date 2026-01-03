# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Supermemory Client - Memory API for AI Applications
====================================================

Provides scalable memory storage and semantic search capabilities
for AI applications using Supermemory's API.

Features:
    - Document storage with automatic chunking and embedding
    - Semantic search across stored documents
    - Container-based organization for multi-tenant use
    - Metadata support for filtering and retrieval
    - Batch operations for bulk document management

Enterprise Tier Feature ($299/mo).

Example:
    >>> from krl_data_connectors.enterprise.ai import SupermemoryClient
    >>>
    >>> client = SupermemoryClient()
    >>>
    >>> # Add a document
    >>> doc = await client.add_document(
    ...     content="Economic analysis report for Q4 2024...",
    ...     container_tag="economic-reports",
    ...     metadata={"year": 2024, "quarter": "Q4"}
    ... )
    >>>
    >>> # Search for relevant content
    >>> results = await client.search(
    ...     query="What were the GDP growth trends?",
    ...     container_tag="economic-reports"
    ... )
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
)

import httpx

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class SupermemoryConfig:
    """Configuration for Supermemory client."""
    
    api_key: Optional[str] = None
    base_url: str = "https://api.supermemory.ai/v3"
    timeout: float = 60.0
    max_retries: int = 3
    
    # Default container for documents
    default_container: Optional[str] = "krl-default"
    
    def __post_init__(self):
        if self.api_key is None:
            self.api_key = os.environ.get("SUPERMEMORY_API_KEY")


# =============================================================================
# Data Types
# =============================================================================

class DocumentStatus(str, Enum):
    """Document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Document:
    """A stored document."""
    id: str
    status: DocumentStatus
    content: Optional[str] = None
    container_tag: Optional[str] = None
    custom_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        """Create from API response."""
        return cls(
            id=data.get("id", ""),
            status=DocumentStatus(data.get("status", "pending")),
            content=data.get("content"),
            container_tag=data.get("containerTag"),
            custom_id=data.get("customId"),
            metadata=data.get("metadata", {}),
            created_at=data.get("createdAt"),
            updated_at=data.get("updatedAt"),
        )


@dataclass
class SearchResult:
    """A search result."""
    document_id: str
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    chunk_index: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResult":
        """Create from API response."""
        return cls(
            document_id=data.get("documentId", data.get("id", "")),
            content=data.get("content", data.get("text", "")),
            score=data.get("score", data.get("similarity", 0.0)),
            metadata=data.get("metadata", {}),
            chunk_index=data.get("chunkIndex"),
        )


@dataclass
class MemoryContainer:
    """A memory container for organizing documents."""
    tag: str
    document_count: int = 0
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchAddResult:
    """Result of batch document addition."""
    successful: int
    failed: int
    documents: List[Document] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)


# =============================================================================
# Supermemory Client
# =============================================================================

class SupermemoryClient:
    """
    Supermemory API client for memory and RAG operations.
    
    Provides document storage, embedding, and semantic search
    for building AI applications with long-term memory.
    
    Features:
        - Document storage with automatic embedding
        - Semantic search with relevance scoring
        - Container-based organization
        - Metadata filtering
        - Batch operations
    
    Example:
        >>> client = SupermemoryClient()
        >>>
        >>> # Store a document
        >>> doc = await client.add_document(
        ...     content="Federal Reserve announces rate decision...",
        ...     container_tag="fed-news",
        ...     metadata={"source": "reuters", "date": "2024-12-01"}
        ... )
        >>>
        >>> # Search with natural language
        >>> results = await client.search(
        ...     query="What is the Fed's interest rate policy?",
        ...     container_tag="fed-news",
        ...     limit=5
        ... )
        >>> for result in results:
        ...     print(f"Score: {result.score:.2f} - {result.content[:100]}...")
    """
    
    def __init__(
        self,
        config: Optional[SupermemoryConfig] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize Supermemory client.
        
        Args:
            config: Configuration object
            api_key: API key (overrides config and env var)
        """
        self.config = config or SupermemoryConfig()
        if api_key:
            self.config.api_key = api_key
        
        if not self.config.api_key:
            raise ValueError(
                "Supermemory API key required. Set SUPERMEMORY_API_KEY environment "
                "variable or pass api_key parameter."
            )
        
        self._client: Optional[httpx.AsyncClient] = None
        
        logger.info(
            "SupermemoryClient initialized",
            extra={"default_container": self.config.default_container}
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
                },
            )
        return self._client
    
    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    # =========================================================================
    # Document Management
    # =========================================================================
    
    async def add_document(
        self,
        content: str,
        container_tag: Optional[str] = None,
        custom_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Document:
        """
        Add a document to memory.
        
        The content can be:
        - Plain text
        - A URL (will be fetched and processed)
        - A file URL (PDF, images supported)
        
        Args:
            content: Document content, URL, or file URL
            container_tag: Container to store document in
            custom_id: Custom identifier for the document
            metadata: Additional metadata
        
        Returns:
            Document object with ID and status
        
        Example:
            >>> doc = await client.add_document(
            ...     content="Analysis of economic trends in 2024...",
            ...     container_tag="economic-analysis",
            ...     metadata={"author": "analyst", "category": "macro"}
            ... )
            >>> print(f"Document ID: {doc.id}")
        """
        client = await self._get_client()
        
        body: Dict[str, Any] = {"content": content}
        
        if container_tag:
            body["containerTag"] = container_tag
        elif self.config.default_container:
            body["containerTag"] = self.config.default_container
        
        if custom_id:
            body["customId"] = custom_id
        
        if metadata:
            body["metadata"] = metadata
        
        logger.debug(f"Adding document: container={container_tag}, has_metadata={bool(metadata)}")
        
        response = await self._request_with_retry("POST", "/documents", json=body)
        
        return Document(
            id=response.get("id", ""),
            status=DocumentStatus(response.get("status", "pending")),
            container_tag=container_tag or self.config.default_container,
            custom_id=custom_id,
            metadata=metadata or {},
        )
    
    async def add_documents_batch(
        self,
        documents: List[Dict[str, Any]],
        container_tag: Optional[str] = None,
    ) -> BatchAddResult:
        """
        Add multiple documents in batch.
        
        Args:
            documents: List of document dicts with "content" and optional "metadata"
            container_tag: Container for all documents
        
        Returns:
            BatchAddResult with success/failure counts
        
        Example:
            >>> docs = [
            ...     {"content": "Report 1...", "metadata": {"quarter": "Q1"}},
            ...     {"content": "Report 2...", "metadata": {"quarter": "Q2"}},
            ... ]
            >>> result = await client.add_documents_batch(docs, "reports")
            >>> print(f"Added {result.successful}, failed {result.failed}")
        """
        client = await self._get_client()
        
        # Prepare batch request
        batch_docs = []
        for doc in documents:
            item: Dict[str, Any] = {"content": doc["content"]}
            if container_tag:
                item["containerTag"] = container_tag
            elif self.config.default_container:
                item["containerTag"] = self.config.default_container
            if "metadata" in doc:
                item["metadata"] = doc["metadata"]
            if "customId" in doc:
                item["customId"] = doc["customId"]
            batch_docs.append(item)
        
        response = await self._request_with_retry(
            "POST", 
            "/documents/batch",
            json={"documents": batch_docs}
        )
        
        result = BatchAddResult(
            successful=response.get("successful", 0),
            failed=response.get("failed", 0),
        )
        
        for doc_data in response.get("documents", []):
            result.documents.append(Document.from_dict(doc_data))
        
        result.errors = response.get("errors", [])
        
        return result
    
    async def get_document(self, document_id: str) -> Document:
        """
        Get a document by ID.
        
        Args:
            document_id: Document ID
        
        Returns:
            Document object
        """
        response = await self._request_with_retry("GET", f"/documents/{document_id}")
        return Document.from_dict(response)
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document.
        
        Args:
            document_id: Document ID
        
        Returns:
            True if deleted successfully
        """
        await self._request_with_retry("DELETE", f"/documents/{document_id}")
        return True
    
    async def list_documents(
        self,
        container_tag: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Document]:
        """
        List documents in a container.
        
        Args:
            container_tag: Filter by container
            limit: Maximum documents to return
            offset: Pagination offset
        
        Returns:
            List of Document objects
        """
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if container_tag:
            params["containerTag"] = container_tag
        
        response = await self._request_with_retry("GET", "/documents", params=params)
        
        documents = []
        for doc_data in response.get("documents", response.get("data", [])):
            documents.append(Document.from_dict(doc_data))
        
        return documents
    
    # =========================================================================
    # Search
    # =========================================================================
    
    async def search(
        self,
        query: str,
        container_tag: Optional[str] = None,
        limit: int = 10,
        min_score: float = 0.0,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Search documents with semantic similarity.
        
        Args:
            query: Natural language search query
            container_tag: Limit search to specific container
            limit: Maximum results to return
            min_score: Minimum similarity score (0-1)
            metadata_filter: Filter by metadata fields
        
        Returns:
            List of SearchResult objects sorted by relevance
        
        Example:
            >>> results = await client.search(
            ...     query="What are the effects of monetary policy?",
            ...     container_tag="fed-research",
            ...     limit=5
            ... )
            >>> for r in results:
            ...     print(f"{r.score:.2f}: {r.content[:100]}...")
        """
        body: Dict[str, Any] = {
            "query": query,
            "limit": limit,
        }
        
        if container_tag:
            body["containerTag"] = container_tag
        elif self.config.default_container:
            body["containerTag"] = self.config.default_container
        
        if min_score > 0:
            body["minScore"] = min_score
        
        if metadata_filter:
            body["metadataFilter"] = metadata_filter
        
        logger.debug(f"Search: query='{query[:50]}...', container={container_tag}")
        
        response = await self._request_with_retry("POST", "/search", json=body)
        
        results = []
        for result_data in response.get("results", response.get("data", [])):
            results.append(SearchResult.from_dict(result_data))
        
        return results
    
    async def search_hybrid(
        self,
        query: str,
        container_tag: Optional[str] = None,
        limit: int = 10,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ) -> List[SearchResult]:
        """
        Hybrid search combining semantic and keyword matching.
        
        Args:
            query: Search query
            container_tag: Container to search
            limit: Maximum results
            semantic_weight: Weight for semantic similarity (0-1)
            keyword_weight: Weight for keyword matching (0-1)
        
        Returns:
            List of SearchResult objects
        """
        body: Dict[str, Any] = {
            "query": query,
            "limit": limit,
            "searchType": "hybrid",
            "semanticWeight": semantic_weight,
            "keywordWeight": keyword_weight,
        }
        
        if container_tag:
            body["containerTag"] = container_tag
        
        response = await self._request_with_retry("POST", "/search", json=body)
        
        results = []
        for result_data in response.get("results", response.get("data", [])):
            results.append(SearchResult.from_dict(result_data))
        
        return results
    
    # =========================================================================
    # Containers
    # =========================================================================
    
    async def list_containers(self) -> List[MemoryContainer]:
        """
        List all containers.
        
        Returns:
            List of MemoryContainer objects
        """
        response = await self._request_with_retry("GET", "/containers")
        
        containers = []
        for container_data in response.get("containers", response.get("data", [])):
            containers.append(MemoryContainer(
                tag=container_data.get("tag", ""),
                document_count=container_data.get("documentCount", 0),
                created_at=container_data.get("createdAt"),
                metadata=container_data.get("metadata", {}),
            ))
        
        return containers
    
    async def delete_container(self, container_tag: str) -> bool:
        """
        Delete a container and all its documents.
        
        Args:
            container_tag: Container tag to delete
        
        Returns:
            True if deleted successfully
        """
        await self._request_with_retry("DELETE", f"/containers/{container_tag}")
        return True
    
    # =========================================================================
    # Memory Operations (for chat applications)
    # =========================================================================
    
    async def add_memory(
        self,
        user_message: str,
        assistant_response: str,
        container_tag: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Document:
        """
        Add a conversation memory (user-assistant exchange).
        
        Useful for storing chat history for RAG retrieval.
        
        Args:
            user_message: User's message
            assistant_response: Assistant's response
            container_tag: Container for memories
            session_id: Session identifier
            metadata: Additional metadata
        
        Returns:
            Document representing the memory
        """
        content = f"User: {user_message}\n\nAssistant: {assistant_response}"
        
        full_metadata = metadata or {}
        if session_id:
            full_metadata["session_id"] = session_id
        full_metadata["type"] = "conversation_memory"
        full_metadata["timestamp"] = datetime.now(UTC).isoformat()
        
        return await self.add_document(
            content=content,
            container_tag=container_tag or "memories",
            metadata=full_metadata,
        )
    
    async def get_relevant_memories(
        self,
        query: str,
        container_tag: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 5,
    ) -> List[SearchResult]:
        """
        Retrieve relevant memories for context.
        
        Args:
            query: Current query/context
            container_tag: Container to search
            session_id: Filter by session
            limit: Maximum memories to retrieve
        
        Returns:
            List of relevant memory SearchResults
        """
        metadata_filter = None
        if session_id:
            metadata_filter = {"session_id": session_id}
        
        return await self.search(
            query=query,
            container_tag=container_tag or "memories",
            limit=limit,
            metadata_filter=metadata_filter,
        )
    
    # =========================================================================
    # Internal Methods
    # =========================================================================
    
    async def _request_with_retry(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make request with retry logic."""
        client = await self._get_client()
        
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                response = await client.request(method, path, **kwargs)
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code == 429:
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limited, waiting {wait_time}s")
                    await asyncio.sleep(wait_time)
                elif e.response.status_code >= 500:
                    await asyncio.sleep(1)
                else:
                    raise
            except httpx.RequestError as e:
                last_error = e
                await asyncio.sleep(1)
        
        raise last_error or Exception("Max retries exceeded")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# =============================================================================
# Convenience Functions
# =============================================================================

async def quick_search(
    query: str,
    container_tag: Optional[str] = None,
    api_key: Optional[str] = None,
    limit: int = 5,
) -> List[SearchResult]:
    """
    Quick semantic search.
    
    Args:
        query: Search query
        container_tag: Container to search
        api_key: Optional API key
        limit: Maximum results
    
    Returns:
        List of SearchResults
    """
    async with SupermemoryClient(api_key=api_key) as client:
        return await client.search(
            query=query,
            container_tag=container_tag,
            limit=limit,
        )


async def quick_add(
    content: str,
    container_tag: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Document:
    """
    Quick document addition.
    
    Args:
        content: Document content
        container_tag: Container tag
        api_key: Optional API key
    
    Returns:
        Document object
    """
    async with SupermemoryClient(api_key=api_key) as client:
        return await client.add_document(
            content=content,
            container_tag=container_tag,
        )
