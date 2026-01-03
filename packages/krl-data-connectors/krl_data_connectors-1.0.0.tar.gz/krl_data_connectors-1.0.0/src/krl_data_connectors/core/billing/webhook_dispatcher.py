# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Webhook Dispatcher - DEPRECATED

⚠️ DEPRECATION WARNING (Dec 2025):
This module has been moved to krl-premium-backend.
Import from: app.services.billing.webhook_dispatcher

This stub remains for backward compatibility but will be removed in v2.0.
"""

from __future__ import annotations

import warnings
warnings.warn(
    "krl_data_connectors.core.billing.webhook_dispatcher is deprecated. "
    "This module has moved to krl-premium-backend. "
    "Import from 'app.services.billing.webhook_dispatcher' instead.",
    DeprecationWarning,
    stacklevel=2
)

import hashlib
import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from typing import Any, Callable, Deque, Dict, List, Optional, Set

from .payments_adapter import (
    PaymentProvider,
    PaymentsAdapter,
    WebhookEvent,
    WebhookEventType,
    AdapterResult,
    AdapterRegistry,
    AdapterConfig,
)

logger = logging.getLogger(__name__)


class WebhookStatus(Enum):
    """Webhook processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    RETRY = "retry"
    DEAD_LETTER = "dead_letter"


@dataclass
class WebhookRecord:
    """Record of a webhook event."""
    event_id: str
    provider: PaymentProvider
    event_type: WebhookEventType
    status: WebhookStatus = WebhookStatus.PENDING
    
    # Processing
    attempts: int = 0
    max_attempts: int = 3
    last_error: Optional[str] = None
    
    # Telemetry
    received_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    processed_at: Optional[datetime] = None
    
    # Data
    raw_payload: Optional[bytes] = None
    parsed_event: Optional[WebhookEvent] = None
    result: Optional[Dict[str, Any]] = None


@dataclass 
class DispatcherConfig:
    """Configuration for webhook dispatcher."""
    max_attempts: int = 3
    retry_delay_seconds: int = 60
    dedup_window_size: int = 1000
    dead_letter_enabled: bool = True
    telemetry_enabled: bool = True


class WebhookDispatcher:
    """
    Centralized webhook dispatcher for all payment providers.
    
    Provides:
    - Provider routing based on endpoint or signature
    - Deduplication via event ID tracking
    - Retry logic with exponential backoff
    - Dead-letter queue for failed events
    - Telemetry integration for closed-loop
    """

    def __init__(self, config: Optional[DispatcherConfig] = None):
        self.config = config or DispatcherConfig()
        
        # Adapter instances
        self._adapters: Dict[PaymentProvider, PaymentsAdapter] = {}
        
        # Event tracking
        self._processed_ids: Deque[str] = deque(maxlen=self.config.dedup_window_size)
        self._pending: Dict[str, WebhookRecord] = {}
        self._dead_letter: List[WebhookRecord] = []
        
        # Hooks
        self._telemetry_hook: Optional[Callable[[WebhookEvent], None]] = None
        self._dashboard_hook: Optional[Callable[[WebhookEvent], None]] = None
        self._billing_hook: Optional[Callable[[WebhookEvent], None]] = None
        
        # Event handlers by type
        self._handlers: Dict[WebhookEventType, List[Callable[[WebhookEvent], None]]] = {}

    # -------------------------------------------------------------------------
    # Adapter Management
    # -------------------------------------------------------------------------

    def register_adapter(self, provider: PaymentProvider, adapter: PaymentsAdapter) -> None:
        """Register an adapter for a provider."""
        self._adapters[provider] = adapter
        logger.info(f"Registered adapter for {provider.value}")

    def get_adapter(self, provider: PaymentProvider) -> Optional[PaymentsAdapter]:
        """Get adapter for a provider."""
        return self._adapters.get(provider)

    # -------------------------------------------------------------------------
    # Hook Registration
    # -------------------------------------------------------------------------

    def connect_telemetry(self, hook: Callable[[WebhookEvent], None]) -> None:
        """Connect to TelemetryIngestion for closed-loop."""
        self._telemetry_hook = hook
        logger.info("Connected telemetry hook")

    def connect_dashboard(self, hook: Callable[[WebhookEvent], None]) -> None:
        """Connect to dashboard for observability."""
        self._dashboard_hook = hook
        logger.info("Connected dashboard hook")

    def connect_billing(self, hook: Callable[[WebhookEvent], None]) -> None:
        """Connect to billing controller for revenue events."""
        self._billing_hook = hook
        logger.info("Connected billing hook")

    def register_handler(
        self, 
        event_type: WebhookEventType, 
        handler: Callable[[WebhookEvent], None]
    ) -> None:
        """Register a handler for specific event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    # -------------------------------------------------------------------------
    # Webhook Processing
    # -------------------------------------------------------------------------

    def dispatch(
        self,
        provider: PaymentProvider,
        payload: bytes,
        signature: str,
    ) -> AdapterResult[Dict[str, Any]]:
        """
        Dispatch a webhook to the appropriate adapter.
        
        Args:
            provider: Payment provider
            payload: Raw webhook payload
            signature: Webhook signature header
            
        Returns:
            Processing result
        """
        adapter = self._adapters.get(provider)
        if not adapter:
            return AdapterResult.fail("no_adapter", f"No adapter for {provider.value}")
        
        # Parse webhook
        parse_result = adapter.parse_webhook(payload, signature)
        if not parse_result.success:
            return AdapterResult.fail(parse_result.error_code, parse_result.error_message)
        
        event = parse_result.data
        
        # Deduplication
        if event.event_id in self._processed_ids:
            logger.debug(f"Duplicate webhook: {event.event_id}")
            return AdapterResult.ok({"status": "duplicate", "event_id": event.event_id})
        
        # Create record
        record = WebhookRecord(
            event_id=event.event_id,
            provider=provider,
            event_type=event.event_type,
            raw_payload=payload,
            parsed_event=event,
        )
        
        # Process
        return self._process_webhook(record, adapter)

    def _process_webhook(
        self, 
        record: WebhookRecord, 
        adapter: PaymentsAdapter
    ) -> AdapterResult[Dict[str, Any]]:
        """Process a webhook record."""
        record.status = WebhookStatus.PROCESSING
        record.attempts += 1
        
        try:
            # Call adapter handler
            result = adapter.handle_webhook(record.parsed_event)
            
            if result.success:
                record.status = WebhookStatus.SUCCEEDED
                record.processed_at = datetime.now(UTC)
                record.result = result.data
                
                # Mark as processed
                self._processed_ids.append(record.event_id)
                
                # Fire hooks
                self._fire_hooks(record.parsed_event)
                
                # Fire type-specific handlers
                self._fire_handlers(record.parsed_event)
                
                logger.info(f"Processed webhook {record.event_id}")
                return result
            else:
                record.last_error = result.error_message
                return self._handle_failure(record, result.error_message)
                
        except Exception as e:
            record.last_error = str(e)
            return self._handle_failure(record, str(e))

    def _handle_failure(self, record: WebhookRecord, error: str) -> AdapterResult[Dict[str, Any]]:
        """Handle webhook processing failure."""
        if record.attempts < record.max_attempts:
            record.status = WebhookStatus.RETRY
            self._pending[record.event_id] = record
            logger.warning(f"Webhook {record.event_id} failed, will retry: {error}")
            return AdapterResult.fail("retry_scheduled", error)
        else:
            record.status = WebhookStatus.DEAD_LETTER
            if self.config.dead_letter_enabled:
                self._dead_letter.append(record)
            logger.error(f"Webhook {record.event_id} sent to dead letter: {error}")
            return AdapterResult.fail("dead_letter", error)

    def _fire_hooks(self, event: WebhookEvent) -> None:
        """Fire integration hooks."""
        if self._telemetry_hook:
            try:
                self._telemetry_hook(event)
            except Exception as e:
                logger.error(f"Telemetry hook error: {e}")
        
        if self._dashboard_hook:
            try:
                self._dashboard_hook(event)
            except Exception as e:
                logger.error(f"Dashboard hook error: {e}")
        
        if self._billing_hook and self._is_billing_event(event):
            try:
                self._billing_hook(event)
            except Exception as e:
                logger.error(f"Billing hook error: {e}")

    def _fire_handlers(self, event: WebhookEvent) -> None:
        """Fire type-specific handlers."""
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Handler error for {event.event_type}: {e}")

    def _is_billing_event(self, event: WebhookEvent) -> bool:
        """Check if event is billing-related."""
        billing_types = {
            WebhookEventType.INVOICE_PAID,
            WebhookEventType.INVOICE_PAYMENT_FAILED,
            WebhookEventType.PAYMENT_SUCCEEDED,
            WebhookEventType.PAYMENT_FAILED,
            WebhookEventType.SUBSCRIPTION_CREATED,
            WebhookEventType.SUBSCRIPTION_CANCELED,
        }
        return event.event_type in billing_types

    # -------------------------------------------------------------------------
    # Retry Processing
    # -------------------------------------------------------------------------

    def process_retries(self) -> int:
        """Process pending retries. Returns count processed."""
        processed = 0
        to_remove = []
        
        for event_id, record in self._pending.items():
            if record.status != WebhookStatus.RETRY:
                continue
            
            adapter = self._adapters.get(record.provider)
            if not adapter:
                continue
            
            result = self._process_webhook(record, adapter)
            if result.success or record.status == WebhookStatus.DEAD_LETTER:
                to_remove.append(event_id)
            processed += 1
        
        for event_id in to_remove:
            del self._pending[event_id]
        
        return processed

    # -------------------------------------------------------------------------
    # Dead Letter Management
    # -------------------------------------------------------------------------

    def get_dead_letters(self) -> List[WebhookRecord]:
        """Get dead letter queue."""
        return self._dead_letter.copy()

    def replay_dead_letter(self, event_id: str) -> AdapterResult[Dict[str, Any]]:
        """Replay a dead letter event."""
        for i, record in enumerate(self._dead_letter):
            if record.event_id == event_id:
                record.attempts = 0
                record.max_attempts = 1
                adapter = self._adapters.get(record.provider)
                if adapter:
                    result = self._process_webhook(record, adapter)
                    if result.success:
                        self._dead_letter.pop(i)
                    return result
                return AdapterResult.fail("no_adapter", "Adapter not found")
        
        return AdapterResult.fail("not_found", "Event not in dead letter queue")

    def clear_dead_letters(self) -> int:
        """Clear dead letter queue. Returns count cleared."""
        count = len(self._dead_letter)
        self._dead_letter.clear()
        return count

    # -------------------------------------------------------------------------
    # Stats
    # -------------------------------------------------------------------------

    def get_stats(self) -> Dict[str, Any]:
        """Get dispatcher statistics."""
        return {
            "adapters_registered": len(self._adapters),
            "providers": [p.value for p in self._adapters.keys()],
            "processed_count": len(self._processed_ids),
            "pending_retries": len(self._pending),
            "dead_letters": len(self._dead_letter),
            "hooks": {
                "telemetry": self._telemetry_hook is not None,
                "dashboard": self._dashboard_hook is not None,
                "billing": self._billing_hook is not None,
            },
            "handlers_registered": sum(len(h) for h in self._handlers.values()),
        }


# =============================================================================
# Convenience Functions
# =============================================================================

def create_webhook_dispatcher(
    config: Optional[DispatcherConfig] = None,
    stripe_config: Optional[AdapterConfig] = None,
    lago_config: Optional[AdapterConfig] = None,
) -> WebhookDispatcher:
    """
    Factory to create configured WebhookDispatcher.
    
    Args:
        config: Dispatcher configuration
        stripe_config: Optional Stripe adapter config
        lago_config: Optional Lago adapter config
    """
    dispatcher = WebhookDispatcher(config)
    
    if stripe_config:
        adapter = AdapterRegistry.create_adapter(stripe_config)
        if adapter:
            adapter.initialize()
            dispatcher.register_adapter(stripe_config.provider, adapter)
    
    if lago_config:
        adapter = AdapterRegistry.create_adapter(lago_config)
        if adapter:
            adapter.initialize()
            dispatcher.register_adapter(PaymentProvider.LAGO, adapter)
    
    return dispatcher


DEFAULT_DISPATCHER_CONFIG = DispatcherConfig(
    max_attempts=3,
    retry_delay_seconds=60,
    dedup_window_size=1000,
    dead_letter_enabled=True,
    telemetry_enabled=True,
)
