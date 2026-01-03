# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Stripe Persistent Storage Layer - DEPRECATED

⚠️ DEPRECATION WARNING (Dec 2025):
This module has been moved to krl-premium-backend.
Import from: app.services.billing.stripe_persistence

This stub remains for backward compatibility but will be removed in v2.0.
"""

from __future__ import annotations

import warnings
warnings.warn(
    "krl_data_connectors.core.billing.stripe_persistence is deprecated. "
    "This module has moved to krl-premium-backend. "
    "Import from 'app.services.billing.stripe_persistence' instead.",
    DeprecationWarning,
    stacklevel=2
)

import hashlib
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, UTC
from typing import Any, Callable, Dict, List, Optional, Protocol

logger = logging.getLogger(__name__)


# =============================================================================
# SQLAlchemy Models (using SQLAlchemy 2.0 style)
# =============================================================================

# Try to import SQLAlchemy - graceful degradation if not available
try:
    from sqlalchemy import (
        Boolean,
        Column,
        DateTime,
        Index,
        Integer,
        String,
        Text,
        create_engine,
        func,
    )
    from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
    from sqlalchemy.pool import StaticPool
    
    SQLALCHEMY_AVAILABLE = True
    
    class Base(DeclarativeBase):
        """SQLAlchemy declarative base for billing models."""
        pass
    
    class ProcessedStripeEventModel(Base):
        """
        Persistent storage for processed Stripe webhook events.
        
        Ensures idempotency across restarts and multi-instance deployments.
        """
        __tablename__ = "processed_stripe_events"
        
        event_id = Column(String(255), primary_key=True, index=True)
        event_type = Column(String(100), nullable=False, index=True)
        tenant_id = Column(String(100), nullable=True, index=True)
        processed_at = Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            nullable=False,
            index=True,
        )
        payload_hash = Column(String(64), nullable=True)  # SHA256 of payload
        processing_time_ms = Column(Integer, nullable=True)
        routed_to = Column(Text, nullable=True)  # JSON array of engine names
        error_message = Column(Text, nullable=True)
        
        __table_args__ = (
            Index("ix_processed_events_tenant_type", "tenant_id", "event_type"),
            Index("ix_processed_events_cleanup", "processed_at"),
        )
        
        def __repr__(self) -> str:
            return f"<ProcessedStripeEvent {self.event_id} ({self.event_type})>"
    
    class TenantMappingModel(Base):
        """
        Maps Stripe identifiers to internal tenant IDs.
        
        Allows resolving tenant from webhook events containing
        customer_id, account_id, or subscription_id.
        """
        __tablename__ = "tenant_stripe_mappings"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        tenant_id = Column(String(100), nullable=False, index=True, unique=True)
        stripe_customer_id = Column(String(255), nullable=True, index=True)
        stripe_account_id = Column(String(255), nullable=True, index=True)
        stripe_subscription_id = Column(String(255), nullable=True, index=True)
        tier = Column(String(50), default="community")
        created_at = Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
        )
        updated_at = Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
        )
        
        __table_args__ = (
            Index("ix_tenant_mapping_customer", "stripe_customer_id"),
            Index("ix_tenant_mapping_account", "stripe_account_id"),
        )
        
        def __repr__(self) -> str:
            return f"<TenantMapping {self.tenant_id}>"

except ImportError:
    SQLALCHEMY_AVAILABLE = False
    Base = None
    ProcessedStripeEventModel = None
    TenantMappingModel = None
    logger.warning(
        "SQLAlchemy not installed. Persistent storage unavailable. "
        "Run: pip install sqlalchemy"
    )


# =============================================================================
# Redis Cache (Optional)
# =============================================================================

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None


class RedisCache:
    """
    Optional Redis cache for high-throughput idempotency checks.
    
    Falls back gracefully if Redis is unavailable.
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        prefix: str = "stripe:idem:",
        ttl_seconds: int = 86400,  # 24 hours
    ):
        self.prefix = prefix
        self.ttl_seconds = ttl_seconds
        self._client: Optional[Any] = None
        
        if REDIS_AVAILABLE and url:
            try:
                self._client = redis.from_url(url, decode_responses=True)
                self._client.ping()  # Test connection
                logger.info(f"Redis cache connected: {url[:30]}...")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Using DB-only mode.")
                self._client = None
    
    @property
    def is_available(self) -> bool:
        """Check if Redis is connected."""
        return self._client is not None
    
    def exists(self, event_id: str) -> Optional[bool]:
        """
        Check if event exists in cache.
        
        Returns:
            True: Event is cached (already processed)
            False: Event not in cache (may or may not be processed)
            None: Cache unavailable
        """
        if not self._client:
            return None
        
        try:
            return self._client.exists(f"{self.prefix}{event_id}") > 0
        except Exception as e:
            logger.warning(f"Redis exists check failed: {e}")
            return None
    
    def set(self, event_id: str, event_type: str) -> bool:
        """
        Mark event as processed in cache.
        
        Returns True if successful, False otherwise.
        """
        if not self._client:
            return False
        
        try:
            self._client.setex(
                f"{self.prefix}{event_id}",
                self.ttl_seconds,
                event_type,
            )
            return True
        except Exception as e:
            logger.warning(f"Redis set failed: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self._client:
            return {"available": False}
        
        try:
            info = self._client.info("memory")
            keys = self._client.dbsize()
            return {
                "available": True,
                "used_memory": info.get("used_memory_human", "unknown"),
                "total_keys": keys,
                "prefix": self.prefix,
            }
        except Exception:
            return {"available": False}


# =============================================================================
# Persistent Idempotency Store
# =============================================================================

@dataclass
class ProcessedEvent:
    """Record of a processed event."""
    event_id: str
    event_type: str
    tenant_id: Optional[str] = None
    processed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: Optional[int] = None
    routed_to: Optional[List[str]] = None
    error_message: Optional[str] = None


class PersistentIdempotencyStore:
    """
    Production idempotency store with SQLAlchemy + Redis.
    
    Architecture:
    1. Check Redis cache first (fast path)
    2. Fall back to database query (guaranteed consistency)
    3. Write to both on mark_processed
    
    Thread-safe and multi-instance safe.
    """
    
    def __init__(
        self,
        database_url: Optional[str] = None,
        redis_url: Optional[str] = None,
        ttl_hours: int = 168,  # 7 days retention
    ):
        self.ttl = timedelta(hours=ttl_hours)
        self._session_factory: Optional[Callable[[], Session]] = None
        self._redis = RedisCache(redis_url) if redis_url else RedisCache()
        
        # Initialize database if available
        if SQLALCHEMY_AVAILABLE:
            db_url = database_url or os.getenv(
                "STRIPE_DATABASE_URL",
                os.getenv("DATABASE_URL", "sqlite:///stripe_events.db"),
            )
            
            # Use StaticPool for SQLite (thread safety)
            connect_args = {}
            poolclass = None
            if db_url.startswith("sqlite"):
                connect_args = {"check_same_thread": False}
                poolclass = StaticPool
            
            try:
                engine = create_engine(
                    db_url,
                    connect_args=connect_args,
                    poolclass=poolclass,
                    echo=os.getenv("SQL_DEBUG", "").lower() == "true",
                )
                Base.metadata.create_all(engine)
                self._session_factory = sessionmaker(bind=engine)
                logger.info(f"Idempotency store initialized: {db_url[:50]}...")
            except Exception as e:
                logger.error(f"Database initialization failed: {e}")
                self._session_factory = None
        else:
            logger.warning("SQLAlchemy not available. Using in-memory fallback.")
            self._fallback: Dict[str, ProcessedEvent] = {}
    
    def exists(self, event_id: str) -> bool:
        """
        Check if event has been processed.
        
        Checks Redis first (fast), then database (authoritative).
        """
        # Fast path: Redis cache
        redis_result = self._redis.exists(event_id)
        if redis_result is True:
            return True
        
        # Database check
        if self._session_factory:
            with self._session_factory() as session:
                cutoff = datetime.now(timezone.utc) - self.ttl
                exists = (
                    session.query(ProcessedStripeEventModel)
                    .filter(
                        ProcessedStripeEventModel.event_id == event_id,
                        ProcessedStripeEventModel.processed_at >= cutoff,
                    )
                    .first()
                    is not None
                )
                
                # Warm cache if found
                if exists:
                    self._redis.set(event_id, "found")
                
                return exists
        
        # Fallback: in-memory
        if hasattr(self, "_fallback"):
            event = self._fallback.get(event_id)
            if event:
                if datetime.now(timezone.utc) - event.processed_at <= self.ttl:
                    return True
                del self._fallback[event_id]
        
        return False
    
    def mark_processed(
        self,
        event_id: str,
        event_type: str,
        tenant_id: Optional[str] = None,
        processing_time_ms: Optional[int] = None,
        routed_to: Optional[List[str]] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """
        Mark event as processed.
        
        Writes to database and Redis (if available).
        """
        now = datetime.now(timezone.utc)
        
        # Write to Redis first (fast confirmation)
        self._redis.set(event_id, event_type)
        
        # Write to database
        if self._session_factory:
            with self._session_factory() as session:
                record = ProcessedStripeEventModel(
                    event_id=event_id,
                    event_type=event_type,
                    tenant_id=tenant_id,
                    processed_at=now,
                    processing_time_ms=processing_time_ms,
                    routed_to=",".join(routed_to) if routed_to else None,
                    error_message=error_message,
                )
                session.merge(record)  # Use merge to handle duplicates
                session.commit()
        elif hasattr(self, "_fallback"):
            # In-memory fallback
            self._fallback[event_id] = ProcessedEvent(
                event_id=event_id,
                event_type=event_type,
                tenant_id=tenant_id,
                processed_at=now,
                processing_time_ms=processing_time_ms,
                routed_to=routed_to,
                error_message=error_message,
            )
    
    def cleanup_expired(self) -> int:
        """
        Remove events older than TTL.
        
        Should be run periodically (e.g., daily cron job).
        Returns count of removed records.
        """
        if not self._session_factory:
            if hasattr(self, "_fallback"):
                now = datetime.now(timezone.utc)
                expired = [
                    eid for eid, event in self._fallback.items()
                    if now - event.processed_at > self.ttl
                ]
                for eid in expired:
                    del self._fallback[eid]
                return len(expired)
            return 0
        
        with self._session_factory() as session:
            cutoff = datetime.now(timezone.utc) - self.ttl
            result = (
                session.query(ProcessedStripeEventModel)
                .filter(ProcessedStripeEventModel.processed_at < cutoff)
                .delete()
            )
            session.commit()
            logger.info(f"Cleaned up {result} expired events")
            return result
    
    def get_recent_events(
        self,
        tenant_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[ProcessedEvent]:
        """
        Get recent processed events for debugging/monitoring.
        """
        if not self._session_factory:
            return []
        
        with self._session_factory() as session:
            query = session.query(ProcessedStripeEventModel).order_by(
                ProcessedStripeEventModel.processed_at.desc()
            )
            
            if tenant_id:
                query = query.filter(ProcessedStripeEventModel.tenant_id == tenant_id)
            if event_type:
                query = query.filter(ProcessedStripeEventModel.event_type == event_type)
            
            records = query.limit(limit).all()
            
            return [
                ProcessedEvent(
                    event_id=r.event_id,
                    event_type=r.event_type,
                    tenant_id=r.tenant_id,
                    processed_at=r.processed_at,
                    processing_time_ms=r.processing_time_ms,
                    routed_to=r.routed_to.split(",") if r.routed_to else None,
                    error_message=r.error_message,
                )
                for r in records
            ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get store statistics."""
        stats = {
            "redis": self._redis.get_stats(),
            "database": {"available": self._session_factory is not None},
        }
        
        if self._session_factory:
            with self._session_factory() as session:
                total = session.query(ProcessedStripeEventModel).count()
                recent = (
                    session.query(ProcessedStripeEventModel)
                    .filter(
                        ProcessedStripeEventModel.processed_at
                        >= datetime.now(timezone.utc) - timedelta(hours=24)
                    )
                    .count()
                )
                stats["database"].update({
                    "total_events": total,
                    "events_24h": recent,
                })
        
        return stats


# =============================================================================
# Persistent Tenant Resolver
# =============================================================================

@dataclass
class TenantMapping:
    """Mapping between Stripe identifiers and internal tenant."""
    tenant_id: str
    stripe_customer_id: Optional[str] = None
    stripe_account_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    tier: str = "community"


class PersistentTenantResolver:
    """
    Database-backed tenant resolver.
    
    Resolves tenant from Stripe webhook event data using
    customer_id, account_id, or metadata lookups.
    """
    
    def __init__(
        self,
        database_url: Optional[str] = None,
        cache_ttl_seconds: int = 300,  # 5 minute cache
    ):
        self._session_factory: Optional[Callable[[], Session]] = None
        self._cache: Dict[str, TenantMapping] = {}
        self._cache_expiry: Dict[str, datetime] = {}
        self._cache_ttl = timedelta(seconds=cache_ttl_seconds)
        
        if SQLALCHEMY_AVAILABLE:
            db_url = database_url or os.getenv(
                "STRIPE_DATABASE_URL",
                os.getenv("DATABASE_URL", "sqlite:///stripe_events.db"),
            )
            
            connect_args = {}
            poolclass = None
            if db_url.startswith("sqlite"):
                connect_args = {"check_same_thread": False}
                poolclass = StaticPool
            
            try:
                engine = create_engine(
                    db_url,
                    connect_args=connect_args,
                    poolclass=poolclass,
                )
                Base.metadata.create_all(engine)
                self._session_factory = sessionmaker(bind=engine)
            except Exception as e:
                logger.error(f"TenantResolver database init failed: {e}")
    
    def _check_cache(self, key: str) -> Optional[TenantMapping]:
        """Check local cache with expiry."""
        if key not in self._cache:
            return None
        
        if datetime.now(timezone.utc) > self._cache_expiry.get(key, datetime.min):
            del self._cache[key]
            del self._cache_expiry[key]
            return None
        
        return self._cache[key]
    
    def _set_cache(self, key: str, mapping: TenantMapping) -> None:
        """Set local cache entry."""
        self._cache[key] = mapping
        self._cache_expiry[key] = datetime.now(timezone.utc) + self._cache_ttl
    
    def register(self, mapping: TenantMapping) -> None:
        """
        Register a tenant mapping.
        
        Creates or updates database record.
        """
        if not self._session_factory:
            # In-memory fallback
            self._set_cache(mapping.tenant_id, mapping)
            if mapping.stripe_customer_id:
                self._set_cache(f"cust:{mapping.stripe_customer_id}", mapping)
            if mapping.stripe_account_id:
                self._set_cache(f"acct:{mapping.stripe_account_id}", mapping)
            return
        
        with self._session_factory() as session:
            record = TenantMappingModel(
                tenant_id=mapping.tenant_id,
                stripe_customer_id=mapping.stripe_customer_id,
                stripe_account_id=mapping.stripe_account_id,
                stripe_subscription_id=mapping.stripe_subscription_id,
                tier=mapping.tier,
            )
            session.merge(record)
            session.commit()
        
        # Update cache
        self._set_cache(mapping.tenant_id, mapping)
        if mapping.stripe_customer_id:
            self._set_cache(f"cust:{mapping.stripe_customer_id}", mapping)
        if mapping.stripe_account_id:
            self._set_cache(f"acct:{mapping.stripe_account_id}", mapping)
    
    def resolve(self, event_data: Dict[str, Any]) -> Optional[TenantMapping]:
        """
        Resolve tenant from webhook event data.
        
        Tries in order:
        1. customer ID
        2. account ID
        3. metadata.tenant_id
        """
        # Try customer
        customer_id = event_data.get("customer")
        if customer_id:
            cached = self._check_cache(f"cust:{customer_id}")
            if cached:
                return cached
            
            mapping = self._resolve_by_customer(customer_id)
            if mapping:
                self._set_cache(f"cust:{customer_id}", mapping)
                return mapping
        
        # Try account
        account_id = event_data.get("account")
        if account_id:
            cached = self._check_cache(f"acct:{account_id}")
            if cached:
                return cached
            
            mapping = self._resolve_by_account(account_id)
            if mapping:
                self._set_cache(f"acct:{account_id}", mapping)
                return mapping
        
        # Try metadata
        metadata = event_data.get("metadata") or {}
        tenant_id = metadata.get("tenant_id")
        if tenant_id:
            cached = self._check_cache(tenant_id)
            if cached:
                return cached
            
            mapping = self._resolve_by_tenant(tenant_id)
            if mapping:
                self._set_cache(tenant_id, mapping)
                return mapping
        
        return None
    
    def _resolve_by_customer(self, customer_id: str) -> Optional[TenantMapping]:
        """Look up tenant by Stripe customer ID."""
        if not self._session_factory:
            return None
        
        with self._session_factory() as session:
            record = (
                session.query(TenantMappingModel)
                .filter(TenantMappingModel.stripe_customer_id == customer_id)
                .first()
            )
            
            if record:
                return TenantMapping(
                    tenant_id=record.tenant_id,
                    stripe_customer_id=record.stripe_customer_id,
                    stripe_account_id=record.stripe_account_id,
                    stripe_subscription_id=record.stripe_subscription_id,
                    tier=record.tier,
                )
        
        return None
    
    def _resolve_by_account(self, account_id: str) -> Optional[TenantMapping]:
        """Look up tenant by Stripe Connect account ID."""
        if not self._session_factory:
            return None
        
        with self._session_factory() as session:
            record = (
                session.query(TenantMappingModel)
                .filter(TenantMappingModel.stripe_account_id == account_id)
                .first()
            )
            
            if record:
                return TenantMapping(
                    tenant_id=record.tenant_id,
                    stripe_customer_id=record.stripe_customer_id,
                    stripe_account_id=record.stripe_account_id,
                    stripe_subscription_id=record.stripe_subscription_id,
                    tier=record.tier,
                )
        
        return None
    
    def _resolve_by_tenant(self, tenant_id: str) -> Optional[TenantMapping]:
        """Look up mapping by tenant ID."""
        if not self._session_factory:
            return None
        
        with self._session_factory() as session:
            record = (
                session.query(TenantMappingModel)
                .filter(TenantMappingModel.tenant_id == tenant_id)
                .first()
            )
            
            if record:
                return TenantMapping(
                    tenant_id=record.tenant_id,
                    stripe_customer_id=record.stripe_customer_id,
                    stripe_account_id=record.stripe_account_id,
                    stripe_subscription_id=record.stripe_subscription_id,
                    tier=record.tier,
                )
        
        return None
    
    def get_all_mappings(self) -> List[TenantMapping]:
        """Get all registered tenant mappings."""
        if not self._session_factory:
            return list(self._cache.values())
        
        with self._session_factory() as session:
            records = session.query(TenantMappingModel).all()
            return [
                TenantMapping(
                    tenant_id=r.tenant_id,
                    stripe_customer_id=r.stripe_customer_id,
                    stripe_account_id=r.stripe_account_id,
                    stripe_subscription_id=r.stripe_subscription_id,
                    tier=r.tier,
                )
                for r in records
            ]


# =============================================================================
# Engine Wiring
# =============================================================================

class EngineWiring:
    """
    Wires real billing engines to WebhookEventRouter.
    
    Provides adapter wrappers to match protocol interfaces
    expected by WebhookEventRouter.
    """
    
    def __init__(self):
        self._billing_state_machine = None
        self._entitlement_engine = None
        self._fraud_detection = None
        self._contract_enforcement = None
        self._limits_gateway = None
    
    def set_billing_state_machine(self, engine: Any) -> "EngineWiring":
        """Set BillingStateMachine instance."""
        self._billing_state_machine = engine
        return self
    
    def set_entitlement_engine(self, engine: Any) -> "EngineWiring":
        """Set EntitlementEngine instance."""
        self._entitlement_engine = engine
        return self
    
    def set_fraud_detection(self, engine: Any) -> "EngineWiring":
        """Set FraudDetectionEngine instance."""
        self._fraud_detection = engine
        return self
    
    def set_contract_enforcement(self, engine: Any) -> "EngineWiring":
        """Set ContractEnforcementEngine instance."""
        self._contract_enforcement = engine
        return self
    
    def set_limits_gateway(self, engine: Any) -> "EngineWiring":
        """Set LimitsGateway instance."""
        self._limits_gateway = engine
        return self
    
    def create_billing_state_machine_adapter(self) -> Optional[Any]:
        """
        Create adapter for BillingStateMachine.
        
        Wraps actual engine methods to match protocol.
        """
        if not self._billing_state_machine:
            return None
        
        engine = self._billing_state_machine
        
        class Adapter:
            def to_past_due(self, tenant_id: str, data: Dict[str, Any]) -> None:
                # Map to actual engine method
                if hasattr(engine, "transition_to_past_due"):
                    engine.transition_to_past_due(tenant_id, data)
                elif hasattr(engine, "handle_payment_failed"):
                    engine.handle_payment_failed(tenant_id, data)
                else:
                    logger.warning(
                        f"BillingStateMachine missing to_past_due handler for {tenant_id}"
                    )
            
            def to_active(self, tenant_id: str, data: Dict[str, Any]) -> None:
                if hasattr(engine, "transition_to_active"):
                    engine.transition_to_active(tenant_id, data)
                elif hasattr(engine, "handle_payment_success"):
                    engine.handle_payment_success(tenant_id, data)
                else:
                    logger.warning(
                        f"BillingStateMachine missing to_active handler for {tenant_id}"
                    )
            
            def to_canceled(self, tenant_id: str, data: Dict[str, Any]) -> None:
                if hasattr(engine, "transition_to_canceled"):
                    engine.transition_to_canceled(tenant_id, data)
                elif hasattr(engine, "handle_cancellation"):
                    engine.handle_cancellation(tenant_id, data)
                else:
                    logger.warning(
                        f"BillingStateMachine missing to_canceled handler for {tenant_id}"
                    )
        
        return Adapter()
    
    def create_entitlement_engine_adapter(self) -> Optional[Any]:
        """Create adapter for EntitlementEngine."""
        if not self._entitlement_engine:
            return None
        
        engine = self._entitlement_engine
        
        class Adapter:
            def refresh_from_metadata(
                self, tenant_id: str, metadata: Dict[str, Any]
            ) -> None:
                if hasattr(engine, "refresh_from_metadata"):
                    engine.refresh_from_metadata(tenant_id, metadata)
                elif hasattr(engine, "sync_entitlements"):
                    engine.sync_entitlements(tenant_id, metadata)
                else:
                    logger.warning(
                        f"EntitlementEngine missing refresh handler for {tenant_id}"
                    )
            
            def apply_entitlements(
                self, tenant_id: str, entitlements: List[Dict[str, Any]]
            ) -> None:
                if hasattr(engine, "apply_entitlements"):
                    engine.apply_entitlements(tenant_id, entitlements)
                elif hasattr(engine, "grant_entitlements"):
                    for ent in entitlements:
                        engine.grant_entitlements(
                            tenant_id,
                            ent.get("feature"),
                            ent.get("value"),
                        )
                else:
                    logger.warning(
                        f"EntitlementEngine missing apply handler for {tenant_id}"
                    )
        
        return Adapter()
    
    def create_fraud_detection_adapter(self) -> Optional[Any]:
        """Create adapter for FraudDetectionEngine."""
        if not self._fraud_detection:
            return None
        
        engine = self._fraud_detection
        
        class Adapter:
            def clear_risk(self, tenant_id: str, data: Dict[str, Any]) -> None:
                if hasattr(engine, "clear_risk"):
                    engine.clear_risk(tenant_id, data)
                elif hasattr(engine, "reset_risk_score"):
                    engine.reset_risk_score(tenant_id)
                else:
                    logger.warning(
                        f"FraudDetectionEngine missing clear_risk handler for {tenant_id}"
                    )
            
            def flag_suspicious(self, tenant_id: str, data: Dict[str, Any]) -> None:
                if hasattr(engine, "flag_suspicious"):
                    engine.flag_suspicious(tenant_id, data)
                elif hasattr(engine, "raise_alert"):
                    engine.raise_alert(tenant_id, data)
                else:
                    logger.warning(
                        f"FraudDetectionEngine missing flag handler for {tenant_id}"
                    )
        
        return Adapter()
    
    def create_contract_enforcement_adapter(self) -> Optional[Any]:
        """Create adapter for ContractEnforcementEngine."""
        if not self._contract_enforcement:
            return None
        
        engine = self._contract_enforcement
        
        class Adapter:
            def flag_payment_failure(
                self, tenant_id: str, data: Dict[str, Any]
            ) -> None:
                if hasattr(engine, "flag_payment_failure"):
                    engine.flag_payment_failure(tenant_id, data)
                elif hasattr(engine, "record_payment_failure"):
                    engine.record_payment_failure(tenant_id, data)
                else:
                    logger.warning(
                        f"ContractEnforcement missing payment failure handler for {tenant_id}"
                    )
            
            def record_payment(self, tenant_id: str, data: Dict[str, Any]) -> None:
                if hasattr(engine, "record_payment"):
                    engine.record_payment(tenant_id, data)
                elif hasattr(engine, "track_payment"):
                    engine.track_payment(tenant_id, data)
                else:
                    logger.warning(
                        f"ContractEnforcement missing payment handler for {tenant_id}"
                    )
            
            def record_credit(self, tenant_id: str, data: Dict[str, Any]) -> None:
                if hasattr(engine, "record_credit"):
                    engine.record_credit(tenant_id, data)
                elif hasattr(engine, "apply_credit"):
                    engine.apply_credit(tenant_id, data)
                else:
                    logger.warning(
                        f"ContractEnforcement missing credit handler for {tenant_id}"
                    )
        
        return Adapter()
    
    def create_limits_gateway_adapter(self) -> Optional[Any]:
        """Create adapter for LimitsGateway."""
        if not self._limits_gateway:
            return None
        
        engine = self._limits_gateway
        
        class Adapter:
            def sync_limits(
                self, tenant_id: str, limits: Dict[str, Any]
            ) -> None:
                if hasattr(engine, "sync_limits"):
                    engine.sync_limits(tenant_id, limits)
                elif hasattr(engine, "update_quotas"):
                    engine.update_quotas(tenant_id, limits)
                elif hasattr(engine, "set_limits"):
                    for limit_name, limit_value in limits.items():
                        engine.set_limits(tenant_id, limit_name, limit_value)
                else:
                    logger.warning(
                        f"LimitsGateway missing sync handler for {tenant_id}"
                    )
        
        return Adapter()
    
    def wire_to_router(self, router: Any) -> None:
        """
        Wire all engines to a WebhookEventRouter.
        
        Usage:
            from stripe_fastapi import WebhookEventRouter
            
            wiring = EngineWiring()
            wiring.set_billing_state_machine(my_state_machine)
            wiring.set_entitlement_engine(my_entitlement_engine)
            # ... etc
            
            router = WebhookEventRouter(adapter, store, resolver)
            wiring.wire_to_router(router)
        """
        bsm = self.create_billing_state_machine_adapter()
        if bsm:
            router.connect_billing_state_machine(bsm)
            logger.info("Wired BillingStateMachine to router")
        
        ee = self.create_entitlement_engine_adapter()
        if ee:
            router.connect_entitlement_engine(ee)
            logger.info("Wired EntitlementEngine to router")
        
        fd = self.create_fraud_detection_adapter()
        if fd:
            router.connect_fraud_detection(fd)
            logger.info("Wired FraudDetectionEngine to router")
        
        ce = self.create_contract_enforcement_adapter()
        if ce:
            router.connect_contract_enforcement(ce)
            logger.info("Wired ContractEnforcementEngine to router")
        
        lg = self.create_limits_gateway_adapter()
        if lg:
            router.connect_limits_gateway(lg)
            logger.info("Wired LimitsGateway to router")


# =============================================================================
# Environment Configuration
# =============================================================================

@dataclass
class StripeEnvironmentConfig:
    """
    Complete Stripe configuration from environment.
    
    Required:
    - STRIPE_SECRET_KEY: API key
    - STRIPE_WEBHOOK_SECRET: Webhook signing secret
    
    Optional:
    - DATABASE_URL: PostgreSQL/SQLite connection string
    - REDIS_URL: Redis connection string for caching
    - STRIPE_CONNECT_FEE_PERCENT: Platform fee
    - STRIPE_API_VERSION: Override API version
    """
    secret_key: str
    webhook_secret: str
    database_url: str
    redis_url: Optional[str] = None
    connect_fee_percent: float = 0.0
    api_version: Optional[str] = None
    test_mode: bool = True
    
    @classmethod
    def from_env(cls) -> "StripeEnvironmentConfig":
        """
        Load configuration from environment variables.
        
        Validates required variables and provides defaults.
        """
        secret_key = os.getenv("STRIPE_SECRET_KEY", "")
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        
        if not secret_key:
            logger.warning("STRIPE_SECRET_KEY not set")
        if not webhook_secret:
            logger.warning("STRIPE_WEBHOOK_SECRET not set")
        
        database_url = os.getenv(
            "STRIPE_DATABASE_URL",
            os.getenv("DATABASE_URL", "sqlite:///stripe_events.db"),
        )
        
        return cls(
            secret_key=secret_key,
            webhook_secret=webhook_secret,
            database_url=database_url,
            redis_url=os.getenv("REDIS_URL"),
            connect_fee_percent=float(os.getenv("STRIPE_CONNECT_FEE_PERCENT", "0")),
            api_version=os.getenv("STRIPE_API_VERSION"),
            test_mode=secret_key.startswith("sk_test_") if secret_key else True,
        )
    
    def validate(self) -> List[str]:
        """
        Validate configuration.
        
        Returns list of validation errors (empty if valid).
        """
        errors = []
        
        if not self.secret_key:
            errors.append("STRIPE_SECRET_KEY is required")
        elif not self.secret_key.startswith(("sk_test_", "sk_live_")):
            errors.append("STRIPE_SECRET_KEY must start with sk_test_ or sk_live_")
        
        if not self.webhook_secret:
            errors.append("STRIPE_WEBHOOK_SECRET is required")
        elif not self.webhook_secret.startswith("whsec_"):
            errors.append("STRIPE_WEBHOOK_SECRET must start with whsec_")
        
        return errors
    
    def to_dict(self, mask_secrets: bool = True) -> Dict[str, Any]:
        """Convert to dictionary, optionally masking secrets."""
        def mask(value: str, prefix_len: int = 8) -> str:
            if not value or not mask_secrets:
                return value
            return value[:prefix_len] + "..." + value[-4:]
        
        return {
            "secret_key": mask(self.secret_key),
            "webhook_secret": mask(self.webhook_secret),
            "database_url": self.database_url,
            "redis_url": self.redis_url,
            "connect_fee_percent": self.connect_fee_percent,
            "api_version": self.api_version,
            "test_mode": self.test_mode,
        }


def create_env_template() -> str:
    """
    Generate .env template file content.
    
    Returns string suitable for writing to .env.example file.
    """
    return """\
# =============================================================================
# KRL Stripe Integration Environment Variables
# =============================================================================
# Copy this file to .env and fill in your values
# NEVER commit .env to version control!

# -----------------------------------------------------------------------------
# Required: Stripe API Keys
# -----------------------------------------------------------------------------
# Get these from https://dashboard.stripe.com/apikeys
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_secret_here

# -----------------------------------------------------------------------------
# Optional: Database Configuration
# -----------------------------------------------------------------------------
# PostgreSQL (recommended for production):
# DATABASE_URL=postgresql://user:password@localhost:5432/krl_billing

# SQLite (default, good for development):
DATABASE_URL=sqlite:///stripe_events.db

# -----------------------------------------------------------------------------
# Optional: Redis Cache
# -----------------------------------------------------------------------------
# Enables high-throughput webhook processing
# REDIS_URL=redis://localhost:6379/0

# -----------------------------------------------------------------------------
# Optional: Stripe Connect Settings
# -----------------------------------------------------------------------------
# Platform fee percentage (0-100)
STRIPE_CONNECT_FEE_PERCENT=0

# API version override (leave blank for default)
# STRIPE_API_VERSION=2025-11-17

# -----------------------------------------------------------------------------
# Optional: Debug Settings
# -----------------------------------------------------------------------------
# Enable SQL query logging
# SQL_DEBUG=true

# Logging level
# LOG_LEVEL=INFO
"""


# =============================================================================
# FastAPI Integration Factory
# =============================================================================

def create_persistent_stripe_router(
    config: Optional[StripeEnvironmentConfig] = None,
    wiring: Optional[EngineWiring] = None,
):
    """
    Create FastAPI router with persistent storage.
    
    Usage:
        from fastapi import FastAPI
        from stripe_persistence import (
            create_persistent_stripe_router,
            StripeEnvironmentConfig,
            EngineWiring,
        )
        
        # Load config
        config = StripeEnvironmentConfig.from_env()
        
        # Wire engines
        wiring = EngineWiring()
        wiring.set_billing_state_machine(my_state_machine)
        wiring.set_entitlement_engine(my_entitlement_engine)
        
        # Create app
        app = FastAPI()
        
        # Add router with persistence
        router = create_persistent_stripe_router(config, wiring)
        if router:
            app.include_router(router)
    """
    try:
        from fastapi import APIRouter, Depends, Header, HTTPException, Request
    except ImportError:
        logger.error("FastAPI not installed")
        return None
    
    # Load config
    cfg = config or StripeEnvironmentConfig.from_env()
    errors = cfg.validate()
    if errors:
        for error in errors:
            logger.error(f"Config error: {error}")
        return None
    
    # Create persistent stores
    idempotency_store = PersistentIdempotencyStore(
        database_url=cfg.database_url,
        redis_url=cfg.redis_url,
    )
    
    tenant_resolver = PersistentTenantResolver(
        database_url=cfg.database_url,
    )
    
    # Import adapter
    try:
        from .stripe_fastapi import StripeAdapterEnhanced, StripeConfig, WebhookEventRouter
    except ImportError:
        from stripe_fastapi import StripeAdapterEnhanced, StripeConfig, WebhookEventRouter
    
    # Create adapter
    adapter = StripeAdapterEnhanced(
        StripeConfig(
            secret_key=cfg.secret_key,
            webhook_secret=cfg.webhook_secret,
            connect_fee_percent=cfg.connect_fee_percent,
            api_version=cfg.api_version,
            test_mode=cfg.test_mode,
        )
    )
    adapter.initialize()
    
    # Create router
    router = APIRouter(prefix="/stripe", tags=["stripe"])
    
    @router.post("/webhook", status_code=204)
    async def stripe_webhook(
        request: Request,
        stripe_signature: str = Header(alias="stripe-signature"),
    ):
        """
        Stripe webhook endpoint with persistent idempotency.
        """
        import time
        start_time = time.time()
        
        payload = await request.body()
        
        # Verify signature
        try:
            event_data = adapter.verify_webhook(payload, stripe_signature)
        except Exception as e:
            logger.warning(f"Webhook verification failed: {e}")
            raise HTTPException(status_code=422, detail="Invalid signature")
        
        event_id = event_data["event_id"]
        event_type = event_data["event_type"]
        data = event_data["data"]
        
        # Check idempotency
        if idempotency_store.exists(event_id):
            logger.debug(f"Duplicate webhook: {event_id}")
            return  # Already processed
        
        # Create event router
        event_router = WebhookEventRouter(
            adapter=adapter,
            idempotency_store=idempotency_store,
            tenant_resolver=tenant_resolver,
        )
        
        # Wire engines if provided
        if wiring:
            wiring.wire_to_router(event_router)
        
        # Route event
        result = event_router.route_event(event_id, event_type, data)
        
        # Record processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Mark as processed with metadata
        idempotency_store.mark_processed(
            event_id=event_id,
            event_type=event_type,
            tenant_id=result.get("tenant_id"),
            processing_time_ms=processing_time_ms,
            routed_to=result.get("routed_to"),
            error_message=result.get("error"),
        )
        
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return  # 204 No Content
    
    @router.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "stripe_configured": bool(cfg.secret_key),
            "webhook_configured": bool(cfg.webhook_secret),
            "test_mode": cfg.test_mode,
            "idempotency_store": idempotency_store.get_stats(),
        }
    
    @router.get("/events")
    async def list_events(
        tenant_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
    ):
        """List recently processed events."""
        events = idempotency_store.get_recent_events(
            tenant_id=tenant_id,
            event_type=event_type,
            limit=limit,
        )
        return {
            "events": [
                {
                    "event_id": e.event_id,
                    "event_type": e.event_type,
                    "tenant_id": e.tenant_id,
                    "processed_at": e.processed_at.isoformat(),
                    "processing_time_ms": e.processing_time_ms,
                    "routed_to": e.routed_to,
                }
                for e in events
            ],
            "count": len(events),
        }
    
    return router


# =============================================================================
# Webhook Registration Instructions
# =============================================================================

WEBHOOK_REGISTRATION_GUIDE = """
================================================================================
Stripe Webhook Registration Guide
================================================================================

Step 1: Access Stripe Dashboard
-------------------------------
1. Log in to https://dashboard.stripe.com
2. Navigate to Developers → Webhooks

Step 2: Add Endpoint
--------------------
1. Click "+ Add endpoint"
2. Enter your endpoint URL:
   - Production: https://yourdomain.com/stripe/webhook
   - Staging: https://staging.yourdomain.com/stripe/webhook

Step 3: Select Events
---------------------
Subscribe to these events for KRL billing integration:

Payment Events:
  ✓ invoice.paid
  ✓ invoice.payment_failed
  ✓ invoice.payment_succeeded
  ✓ charge.refunded
  ✓ payment_intent.succeeded
  ✓ payment_intent.payment_failed

Subscription Events:
  ✓ customer.subscription.created
  ✓ customer.subscription.updated
  ✓ customer.subscription.deleted
  ✓ customer.subscription.trial_will_end

Customer Events:
  ✓ customer.created
  ✓ customer.updated
  ✓ customer.deleted

Connect Events (if using Stripe Connect):
  ✓ account.updated
  ✓ account.application.deauthorized
  ✓ account.external_account.created
  ✓ account.external_account.deleted

Step 4: Get Webhook Secret
--------------------------
1. After creating the endpoint, click on it
2. Click "Reveal" under "Signing secret"
3. Copy the secret (starts with whsec_)
4. Add to your environment:
   
   export STRIPE_WEBHOOK_SECRET="whsec_your_secret_here"

Step 5: Verify Endpoint
-----------------------
1. Click "Send test webhook"
2. Select any event type
3. Verify your server returns 204 No Content

Step 6: Monitor
---------------
- View event logs in Stripe Dashboard → Webhooks → [your endpoint]
- Failed deliveries are retried for up to 3 days
- Set up alerts for repeated failures

================================================================================
Local Testing with Stripe CLI
================================================================================

# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:8000/stripe/webhook

# Copy the webhook secret (whsec_...) and set it
export STRIPE_WEBHOOK_SECRET="whsec_..."

# Trigger test events
stripe trigger invoice.paid
stripe trigger customer.subscription.created

================================================================================
"""


def print_webhook_registration_guide() -> None:
    """Print the webhook registration guide."""
    print(WEBHOOK_REGISTRATION_GUIDE)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # SQLAlchemy models
    "Base",
    "ProcessedStripeEventModel",
    "TenantMappingModel",
    # Stores
    "PersistentIdempotencyStore",
    "PersistentTenantResolver",
    "RedisCache",
    "ProcessedEvent",
    "TenantMapping",
    # Wiring
    "EngineWiring",
    # Configuration
    "StripeEnvironmentConfig",
    "create_env_template",
    # Factory
    "create_persistent_stripe_router",
    # Documentation
    "WEBHOOK_REGISTRATION_GUIDE",
    "print_webhook_registration_guide",
    # Flags
    "SQLALCHEMY_AVAILABLE",
    "REDIS_AVAILABLE",
]
