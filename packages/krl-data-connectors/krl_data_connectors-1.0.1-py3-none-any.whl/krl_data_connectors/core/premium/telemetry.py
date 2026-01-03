# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# KR-Labs is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Telemetry Collector - Client-Side Telemetry

Implements comprehensive telemetry with:
- Async event batching
- Heartbeat/keep-alive management
- Usage metrics collection
- Error reporting with context
- Privacy-aware data collection
"""

from __future__ import annotations

import atexit
import hashlib
import logging
import os
import queue
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, UTC
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from weakref import WeakSet

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Telemetry event types."""
    # Session events
    SESSION_START = "session.start"
    SESSION_END = "session.end"
    SESSION_HEARTBEAT = "session.heartbeat"
    
    # API events
    API_REQUEST = "api.request"
    API_RESPONSE = "api.response"
    API_ERROR = "api.error"
    
    # Feature events
    FEATURE_ACCESS = "feature.access"
    FEATURE_COMPUTE = "feature.compute"
    FEATURE_DENIED = "feature.denied"
    
    # Security events
    INTEGRITY_CHECK = "security.integrity_check"
    INTEGRITY_VIOLATION = "security.integrity_violation"
    CHALLENGE_REQUEST = "security.challenge_request"
    CHALLENGE_RESPONSE = "security.challenge_response"
    ANOMALY_DETECTED = "security.anomaly_detected"
    
    # Error events
    ERROR_CLIENT = "error.client"
    ERROR_SERVER = "error.server"
    ERROR_NETWORK = "error.network"
    ERROR_AUTH = "error.auth"
    
    # Usage events
    USAGE_QUOTA = "usage.quota"
    USAGE_LIMIT_WARN = "usage.limit_warn"
    USAGE_LIMIT_HIT = "usage.limit_hit"


@dataclass
class TelemetryEvent:
    """Single telemetry event."""
    event_type: EventType
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    session_id: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for transmission."""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "properties": self._sanitize_properties(self.properties),
            "context": self.context,
        }
    
    @staticmethod
    def _sanitize_properties(props: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from properties."""
        sensitive_keys = {"password", "secret", "token", "api_key", "key", "credential"}
        sanitized = {}
        for key, value in props.items():
            key_lower = key.lower()
            if any(s in key_lower for s in sensitive_keys):
                # Hash sensitive values
                sanitized[key] = hashlib.sha256(str(value).encode()).hexdigest()[:16]
            else:
                sanitized[key] = value
        return sanitized


@dataclass
class TelemetryConfig:
    """Telemetry collector configuration."""
    # Batching
    batch_size: int = 50
    flush_interval_seconds: float = 30.0
    max_queue_size: int = 1000
    
    # Heartbeat
    heartbeat_interval_seconds: float = 60.0
    heartbeat_enabled: bool = True
    
    # Retry
    max_retries: int = 3
    retry_delay_seconds: float = 5.0
    
    # Privacy
    collect_hostname: bool = False
    collect_ip: bool = False
    anonymize_user_data: bool = True
    
    # Endpoints
    telemetry_endpoint: str = "/api/v1/telemetry/events"
    heartbeat_endpoint: str = "/api/v1/telemetry/heartbeat"


class TelemetryCollector:
    """
    Asynchronous telemetry collector.
    
    Features:
    - Background event batching
    - Automatic heartbeats
    - Graceful shutdown with flush
    - Memory-bounded queue
    """
    
    # Track all instances for cleanup
    _instances: WeakSet = WeakSet()
    
    def __init__(
        self,
        session_id: str,
        send_func: Callable[[str, Dict[str, Any]], Optional[Dict[str, Any]]],
        config: Optional[TelemetryConfig] = None,
    ):
        """
        Initialize telemetry collector.
        
        Args:
            session_id: Current session identifier
            send_func: Function to send data (endpoint, data) -> response
            config: Collector configuration
        """
        self._session_id = session_id
        self._send_func = send_func
        self._config = config or TelemetryConfig()
        
        # Event queue
        self._event_queue: queue.Queue[TelemetryEvent] = queue.Queue(
            maxsize=self._config.max_queue_size
        )
        
        # State
        self._running = False
        self._flush_thread: Optional[threading.Thread] = None
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # Metrics
        self._events_sent = 0
        self._events_dropped = 0
        self._last_flush_time: Optional[datetime] = None
        self._last_heartbeat_time: Optional[datetime] = None
        
        # Register for cleanup
        TelemetryCollector._instances.add(self)
        
        logger.debug("TelemetryCollector initialized for session %s", session_id)
    
    def start(self) -> None:
        """Start background collection threads."""
        with self._lock:
            if self._running:
                return
            
            self._running = True
            
            # Start flush thread
            self._flush_thread = threading.Thread(
                target=self._flush_loop,
                name="telemetry-flush",
                daemon=True,
            )
            self._flush_thread.start()
            
            # Start heartbeat thread
            if self._config.heartbeat_enabled:
                self._heartbeat_thread = threading.Thread(
                    target=self._heartbeat_loop,
                    name="telemetry-heartbeat",
                    daemon=True,
                )
                self._heartbeat_thread.start()
            
            logger.info("Telemetry collector started")
    
    def stop(self, flush: bool = True) -> None:
        """
        Stop telemetry collection.
        
        Args:
            flush: Flush remaining events before stopping
        """
        with self._lock:
            if not self._running:
                return
            
            self._running = False
        
        if flush:
            self._flush_events()
        
        logger.info("Telemetry collector stopped")
    
    def track(
        self,
        event_type: EventType,
        properties: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Track a telemetry event.
        
        Args:
            event_type: Type of event
            properties: Event properties
            context: Additional context
            
        Returns:
            True if event was queued
        """
        event = TelemetryEvent(
            event_type=event_type,
            session_id=self._session_id,
            properties=properties or {},
            context=context or {},
        )
        
        try:
            self._event_queue.put_nowait(event)
            return True
        except queue.Full:
            self._events_dropped += 1
            logger.warning("Event queue full, dropping event: %s", event_type.value)
            return False
    
    def track_api_request(
        self,
        endpoint: str,
        method: str,
        duration_ms: float,
        status_code: int,
        success: bool,
    ) -> None:
        """Track an API request."""
        self.track(
            EventType.API_REQUEST,
            properties={
                "endpoint": endpoint,
                "method": method,
                "duration_ms": duration_ms,
                "status_code": status_code,
                "success": success,
            },
        )
    
    def track_feature_access(
        self,
        feature_name: str,
        tier_required: str,
        tier_current: str,
        allowed: bool,
    ) -> None:
        """Track feature access attempt."""
        event_type = EventType.FEATURE_ACCESS if allowed else EventType.FEATURE_DENIED
        self.track(
            event_type,
            properties={
                "feature": feature_name,
                "tier_required": tier_required,
                "tier_current": tier_current,
                "allowed": allowed,
            },
        )
    
    def track_integrity_check(
        self,
        component: str,
        passed: bool,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track integrity check result."""
        event_type = EventType.INTEGRITY_CHECK if passed else EventType.INTEGRITY_VIOLATION
        self.track(
            event_type,
            properties={
                "component": component,
                "passed": passed,
                "details": details or {},
            },
        )
    
    def track_error(
        self,
        error_type: str,
        message: str,
        error_code: Optional[str] = None,
        stack_trace: Optional[str] = None,
    ) -> None:
        """Track an error event."""
        event_types = {
            "client": EventType.ERROR_CLIENT,
            "server": EventType.ERROR_SERVER,
            "network": EventType.ERROR_NETWORK,
            "auth": EventType.ERROR_AUTH,
        }
        event_type = event_types.get(error_type, EventType.ERROR_CLIENT)
        
        self.track(
            event_type,
            properties={
                "error_type": error_type,
                "message": message,
                "error_code": error_code,
                # Truncate stack trace for privacy
                "stack_trace": stack_trace[:500] if stack_trace else None,
            },
        )
    
    def track_usage(
        self,
        quota_used: int,
        quota_limit: int,
        resource_type: str = "api_calls",
    ) -> None:
        """Track usage quota."""
        percentage = (quota_used / quota_limit * 100) if quota_limit > 0 else 0
        
        if percentage >= 100:
            event_type = EventType.USAGE_LIMIT_HIT
        elif percentage >= 80:
            event_type = EventType.USAGE_LIMIT_WARN
        else:
            event_type = EventType.USAGE_QUOTA
        
        self.track(
            event_type,
            properties={
                "resource_type": resource_type,
                "quota_used": quota_used,
                "quota_limit": quota_limit,
                "percentage": round(percentage, 2),
            },
        )
    
    def _flush_loop(self) -> None:
        """Background loop to flush events."""
        while self._running:
            time.sleep(self._config.flush_interval_seconds)
            if self._running:
                self._flush_events()
    
    def _flush_events(self) -> None:
        """Flush queued events to backend."""
        events: List[Dict[str, Any]] = []
        
        while len(events) < self._config.batch_size:
            try:
                event = self._event_queue.get_nowait()
                events.append(event.to_dict())
            except queue.Empty:
                break
        
        if not events:
            return
        
        # Send batch
        for attempt in range(self._config.max_retries):
            try:
                self._send_func(
                    self._config.telemetry_endpoint,
                    {"events": events, "batch_id": f"{self._session_id}-{time.time()}"},
                )
                self._events_sent += len(events)
                self._last_flush_time = datetime.now(timezone.utc)
                logger.debug("Flushed %d telemetry events", len(events))
                return
            except Exception as e:
                logger.warning(
                    "Telemetry flush attempt %d failed: %s",
                    attempt + 1, e
                )
                if attempt < self._config.max_retries - 1:
                    time.sleep(self._config.retry_delay_seconds)
        
        # All retries failed
        self._events_dropped += len(events)
        logger.error("Failed to flush %d telemetry events after retries", len(events))
    
    def _heartbeat_loop(self) -> None:
        """Background loop to send heartbeats."""
        while self._running:
            time.sleep(self._config.heartbeat_interval_seconds)
            if self._running:
                self._send_heartbeat()
    
    def _send_heartbeat(self) -> None:
        """Send heartbeat to backend."""
        try:
            self._send_func(
                self._config.heartbeat_endpoint,
                {
                    "session_id": self._session_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "metrics": {
                        "events_queued": self._event_queue.qsize(),
                        "events_sent": self._events_sent,
                        "events_dropped": self._events_dropped,
                    },
                },
            )
            self._last_heartbeat_time = datetime.now(timezone.utc)
            
            # Also track as event
            self.track(
                EventType.SESSION_HEARTBEAT,
                properties={"success": True},
            )
        except Exception as e:
            logger.debug("Heartbeat failed: %s", e)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collector statistics."""
        return {
            "session_id": self._session_id,
            "running": self._running,
            "events_queued": self._event_queue.qsize(),
            "events_sent": self._events_sent,
            "events_dropped": self._events_dropped,
            "last_flush": self._last_flush_time.isoformat() if self._last_flush_time else None,
            "last_heartbeat": self._last_heartbeat_time.isoformat() if self._last_heartbeat_time else None,
        }
    
    def __enter__(self) -> "TelemetryCollector":
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop(flush=True)


@atexit.register
def _cleanup_collectors() -> None:
    """Cleanup all collectors on process exit."""
    for collector in list(TelemetryCollector._instances):
        try:
            collector.stop(flush=True)
        except Exception:
            pass
