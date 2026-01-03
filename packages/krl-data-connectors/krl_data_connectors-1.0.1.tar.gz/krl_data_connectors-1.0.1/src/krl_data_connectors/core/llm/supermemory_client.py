# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Supermemory Client

Provides RAG (Retrieval Augmented Generation) capabilities via Supermemory.
Enables storing, searching, and retrieving contextual memories.
"""

from __future__ import annotations

import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Try to import supermemory SDK
try:
    from supermemory import Supermemory
    HAS_SUPERMEMORY = True
except ImportError:
    HAS_SUPERMEMORY = False
    logger.warning("Supermemory SDK not installed. Install with: pip install supermemory")

from .models import (
    MemoryDocument,
    DocumentMetadata,
    DocumentSource,
    DocumentType,
    MemorySearchRequest,
    MemorySearchResponse,
    AddDocumentRequest,
    AddDocumentResponse,
)


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class SupermemoryConfig:
    """Supermemory client configuration."""
    api_key: str = field(default_factory=lambda: os.getenv("SUPERMEMORY_API_KEY", ""))
    default_container: str = "krl_analytics"
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Search defaults
    default_limit: int = 10
    min_relevance_threshold: float = 0.5
    
    def __post_init__(self):
        if not self.api_key:
            logger.warning("Supermemory API key not configured")


# =============================================================================
# CLIENT
# =============================================================================

class SupermemoryClient:
    """
    Supermemory client for RAG/memory operations.
    
    Provides document storage, semantic search, and retrieval
    for enhancing AI responses with relevant context.
    """
    
    def __init__(self, config: Optional[SupermemoryConfig] = None):
        self.config = config or SupermemoryConfig()
        self._client: Optional[Any] = None
        self._initialized = False
        
    def _get_client(self) -> Any:
        """Get or create the Supermemory client."""
        if not HAS_SUPERMEMORY:
            raise RuntimeError(
                "Supermemory SDK not installed. Install with: pip install supermemory"
            )
        
        if self._client is None:
            if not self.config.api_key:
                raise ValueError("Supermemory API key not configured")
            
            self._client = Supermemory(api_key=self.config.api_key)
            self._initialized = True
        
        return self._client
    
    @property
    def is_available(self) -> bool:
        """Check if Supermemory is available and configured."""
        return HAS_SUPERMEMORY and bool(self.config.api_key)
    
    async def add_document(
        self,
        request: AddDocumentRequest,
    ) -> AddDocumentResponse:
        """
        Add a document to memory.
        
        Args:
            request: Add document request with content and metadata
            
        Returns:
            AddDocumentResponse with the document ID
        """
        if not self.is_available:
            return AddDocumentResponse(
                id="",
                success=False,
                message="Supermemory not available",
            )
        
        try:
            client = self._get_client()
            
            # Build container tag
            container_tag = request.container_tag or self._build_container_tag(
                request.user_id,
                request.metadata,
            )
            
            # Build metadata
            metadata = self._build_metadata(request.metadata, request.user_id)
            if request.title:
                metadata["title"] = request.title
            
            # Add to Supermemory
            response = client.memories.add(
                content=request.content,
                container_tag=container_tag,
                metadata=metadata,
            )
            
            # Extract ID from response
            doc_id = str(getattr(response, "id", None) or uuid.uuid4())
            
            logger.info(f"Added document to Supermemory: {doc_id}")
            
            return AddDocumentResponse(
                id=doc_id,
                success=True,
                message="Document added successfully",
            )
            
        except Exception as e:
            logger.error(f"Failed to add document to Supermemory: {e}")
            return AddDocumentResponse(
                id="",
                success=False,
                message=str(e),
            )
    
    async def search(
        self,
        request: MemorySearchRequest,
    ) -> MemorySearchResponse:
        """
        Search for relevant documents.
        
        Args:
            request: Search request with query and filters
            
        Returns:
            MemorySearchResponse with matching documents
        """
        if not self.is_available:
            return MemorySearchResponse(
                documents=[],
                total_found=0,
                query_time_ms=0,
            )
        
        start_time = time.time()
        
        try:
            client = self._get_client()
            
            # Execute search
            response = client.search.execute(
                q=request.query,
            )
            
            # Parse results
            documents = []
            results = getattr(response, "results", []) or []
            
            for result in results:
                # Extract relevance score
                score = getattr(result, "score", None) or getattr(result, "relevance", 0.5)
                
                # Skip low relevance results
                if score < request.min_relevance:
                    continue
                
                # Parse metadata
                raw_metadata = getattr(result, "metadata", {}) or {}
                metadata = self._parse_metadata(raw_metadata)
                
                # Apply filters if provided
                if request.filters and not self._matches_filters(metadata, request.filters):
                    continue
                
                # Build document
                doc = MemoryDocument(
                    id=str(getattr(result, "id", uuid.uuid4())),
                    content=getattr(result, "content", "") or getattr(result, "text", ""),
                    title=raw_metadata.get("title"),
                    metadata=metadata,
                    score=score,
                    relevance_score=score,
                    created_at=self._parse_datetime(raw_metadata.get("created_at")),
                    updated_at=self._parse_datetime(raw_metadata.get("updated_at")),
                )
                documents.append(doc)
                
                # Limit results
                if len(documents) >= request.limit:
                    break
            
            query_time_ms = (time.time() - start_time) * 1000
            
            logger.info(f"Supermemory search found {len(documents)} documents in {query_time_ms:.2f}ms")
            
            return MemorySearchResponse(
                documents=documents,
                total_found=len(documents),
                query_time_ms=query_time_ms,
            )
            
        except Exception as e:
            logger.error(f"Supermemory search failed: {e}")
            return MemorySearchResponse(
                documents=[],
                total_found=0,
                query_time_ms=(time.time() - start_time) * 1000,
            )
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from memory.
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            True if deletion was successful
        """
        if not self.is_available:
            return False
        
        try:
            client = self._get_client()
            # Note: Supermemory SDK may have different method for deletion
            # This is a placeholder - check actual SDK documentation
            if hasattr(client, "memories") and hasattr(client.memories, "delete"):
                client.memories.delete(id=document_id)
                logger.info(f"Deleted document from Supermemory: {document_id}")
                return True
            else:
                logger.warning("Supermemory delete not available in SDK")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete document from Supermemory: {e}")
            return False
    
    def _build_container_tag(
        self,
        user_id: Optional[str],
        metadata: Optional[DocumentMetadata],
    ) -> str:
        """Build container tag for organization."""
        parts = [self.config.default_container]
        
        if user_id:
            parts.append(f"user_{user_id[:8]}")
        
        if metadata:
            if metadata.project_id:
                parts.append(f"project_{metadata.project_id[:8]}")
            if metadata.source:
                source = metadata.source if isinstance(metadata.source, str) else metadata.source.value
                parts.append(source)
        
        return "_".join(parts)
    
    def _build_metadata(
        self,
        metadata: Optional[DocumentMetadata],
        user_id: Optional[str],
    ) -> Dict[str, Any]:
        """Build metadata dict for storage."""
        result: Dict[str, Any] = {
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
        }
        
        if user_id:
            result["user_id"] = user_id
        
        if metadata:
            if metadata.source:
                result["source"] = metadata.source if isinstance(metadata.source, str) else metadata.source.value
            if metadata.type:
                result["type"] = metadata.type if isinstance(metadata.type, str) else metadata.type.value
            if metadata.project_id:
                result["project_id"] = metadata.project_id
            if metadata.analysis_id:
                result["analysis_id"] = metadata.analysis_id
            if metadata.dataset_id:
                result["dataset_id"] = metadata.dataset_id
            if metadata.tags:
                result["tags"] = metadata.tags
        
        return result
    
    def _parse_metadata(self, raw_metadata: Dict[str, Any]) -> DocumentMetadata:
        """Parse raw metadata into DocumentMetadata."""
        source = raw_metadata.get("source", "user_note")
        doc_type = raw_metadata.get("type", "context")
        
        # Convert string to enum if needed
        try:
            source_enum = DocumentSource(source) if isinstance(source, str) else source
        except ValueError:
            source_enum = DocumentSource.USER_NOTE
        
        try:
            type_enum = DocumentType(doc_type) if isinstance(doc_type, str) else doc_type
        except ValueError:
            type_enum = DocumentType.CONTEXT
        
        return DocumentMetadata(
            source=source_enum,
            type=type_enum,
            project_id=raw_metadata.get("project_id"),
            analysis_id=raw_metadata.get("analysis_id"),
            dataset_id=raw_metadata.get("dataset_id"),
            tags=raw_metadata.get("tags"),
            user_id=raw_metadata.get("user_id"),
        )
    
    def _matches_filters(
        self,
        metadata: DocumentMetadata,
        filters: Dict[str, Any],
    ) -> bool:
        """Check if metadata matches filters."""
        for key, value in filters.items():
            if hasattr(metadata, key):
                attr_value = getattr(metadata, key)
                if attr_value != value:
                    return False
        return True
    
    def _parse_datetime(self, value: Optional[str]) -> Optional[datetime]:
        """Parse datetime string."""
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None
