"""
Audit Logging Module - Phase 2 Week 13

Comprehensive audit trail for security events, access patterns,
and compliance tracking.

Copyright 2025 KR-Labs. All rights reserved.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta, UTC
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TextIO
import uuid


class AuditCategory(Enum):
    """Categories of audit events."""
    
    # Authentication & Authorization
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    SESSION = "session"
    
    # Data Access
    DATA_READ = "data_read"
    DATA_WRITE = "data_write"
    DATA_DELETE = "data_delete"
    DATA_EXPORT = "data_export"
    
    # Security Events
    SECURITY_ALERT = "security_alert"
    INTEGRITY_CHECK = "integrity_check"
    LICENSE_EVENT = "license_event"
    
    # System Events
    CONFIGURATION = "configuration"
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    
    # Administrative
    USER_MANAGEMENT = "user_management"
    PERMISSION_CHANGE = "permission_change"
    AUDIT_ACCESS = "audit_access"


class AuditSeverity(Enum):
    """Severity levels for audit events."""
    
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """An audit log event."""
    
    event_id: str
    timestamp: float
    category: AuditCategory
    severity: AuditSeverity
    action: str
    actor_id: str
    actor_type: str  # user, system, service
    resource_type: str
    resource_id: str
    outcome: str  # success, failure, denied
    description: str
    ip_address: str = ""
    user_agent: str = ""
    session_id: str = ""
    request_id: str = ""
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    previous_state: Dict[str, Any] = field(default_factory=dict)
    new_state: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "timestamp_iso": datetime.fromtimestamp(
                self.timestamp, tz=timezone.utc
            ).isoformat(),
            "category": self.category.value,
            "severity": self.severity.value,
            "action": self.action,
            "actor": {
                "id": self.actor_id,
                "type": self.actor_type,
            },
            "resource": {
                "type": self.resource_type,
                "id": self.resource_id,
            },
            "outcome": self.outcome,
            "description": self.description,
            "context": {
                "ip_address": self.ip_address,
                "user_agent": self.user_agent,
                "session_id": self.session_id,
                "request_id": self.request_id,
            },
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
            "state_change": {
                "previous": self.previous_state,
                "new": self.new_state,
            } if self.previous_state or self.new_state else None,
        }
    
    def to_json(self, indent: int | None = None) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    def compute_hash(self) -> str:
        """Compute SHA-256 hash of the event for integrity verification."""
        data = json.dumps(self.to_dict(), sort_keys=True, default=str)
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class AuditConfig:
    """Configuration for audit logging."""
    
    # Output settings
    log_dir: Path = field(default_factory=lambda: Path("audit_logs"))
    log_prefix: str = "audit"
    rotate_size_mb: int = 100
    rotate_count: int = 30
    compress_rotated: bool = True
    
    # Filtering
    min_severity: AuditSeverity = AuditSeverity.INFO
    enabled_categories: List[AuditCategory] | None = None  # None = all
    
    # Buffer settings
    buffer_size: int = 1000
    flush_interval_seconds: float = 10.0
    
    # Integrity
    include_hash: bool = True
    chain_events: bool = True  # Include previous event hash
    
    # Retention
    retention_days: int = 90
    
    # Real-time
    enable_streaming: bool = True


class AuditBuffer:
    """Thread-safe buffer for audit events."""
    
    def __init__(self, max_size: int = 1000):
        self._buffer: deque[AuditEvent] = deque(maxlen=max_size)
        self._lock = threading.Lock()
    
    def add(self, event: AuditEvent) -> None:
        """Add event to buffer."""
        with self._lock:
            self._buffer.append(event)
    
    def flush(self) -> List[AuditEvent]:
        """Flush and return all buffered events."""
        with self._lock:
            events = list(self._buffer)
            self._buffer.clear()
            return events
    
    def __len__(self) -> int:
        with self._lock:
            return len(self._buffer)


class AuditFileWriter:
    """Handles writing audit logs to files with rotation."""
    
    def __init__(self, config: AuditConfig):
        self.config = config
        self._current_file: TextIO | None = None
        self._current_path: Path | None = None
        self._current_size: int = 0
        self._lock = threading.Lock()
        
        # Ensure log directory exists
        self.config.log_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_log_path(self) -> Path:
        """Get path for current log file."""
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self.config.log_dir / f"{self.config.log_prefix}_{date_str}.jsonl"
    
    def _should_rotate(self) -> bool:
        """Check if log rotation is needed."""
        if self._current_path is None:
            return True
        
        # Rotate on date change
        expected_path = self._get_log_path()
        if expected_path != self._current_path:
            return True
        
        # Rotate on size
        max_bytes = self.config.rotate_size_mb * 1024 * 1024
        if self._current_size >= max_bytes:
            return True
        
        return False
    
    def _rotate(self) -> None:
        """Rotate log files."""
        if self._current_file:
            self._current_file.close()
            self._current_file = None
            
            # Compress if configured
            if self.config.compress_rotated and self._current_path:
                self._compress_file(self._current_path)
        
        self._current_path = self._get_log_path()
        self._current_file = open(self._current_path, "a", encoding="utf-8")
        self._current_size = self._current_path.stat().st_size if self._current_path.exists() else 0
    
    def _compress_file(self, path: Path) -> None:
        """Compress a log file."""
        compressed_path = path.with_suffix(".jsonl.gz")
        
        try:
            with open(path, "rb") as f_in:
                with gzip.open(compressed_path, "wb") as f_out:
                    f_out.writelines(f_in)
            
            # Remove original after successful compression
            path.unlink()
        except Exception:
            pass  # Keep original if compression fails
    
    def write(self, events: List[AuditEvent]) -> int:
        """Write events to log file."""
        if not events:
            return 0
        
        with self._lock:
            if self._should_rotate():
                self._rotate()
            
            written = 0
            for event in events:
                line = event.to_json() + "\n"
                if self._current_file:
                    self._current_file.write(line)
                    self._current_size += len(line.encode())
                    written += 1
            
            if self._current_file:
                self._current_file.flush()
            
            return written
    
    def close(self) -> None:
        """Close the current file."""
        with self._lock:
            if self._current_file:
                self._current_file.close()
                self._current_file = None


class AuditLogger:
    """
    Comprehensive audit logging system.
    
    Features:
    - Structured audit events
    - File-based persistence with rotation
    - Event chaining for integrity
    - Real-time streaming
    - Buffered writes for performance
    """
    
    def __init__(self, config: AuditConfig | None = None):
        self.config = config or AuditConfig()
        self._buffer = AuditBuffer(self.config.buffer_size)
        self._writer = AuditFileWriter(self.config)
        self._subscribers: List[Callable[[AuditEvent], None]] = []
        self._lock = threading.RLock()
        
        # Event chaining
        self._last_event_hash: str = ""
        
        # Background flusher
        self._running = False
        self._flush_thread: threading.Thread | None = None
        
        # Statistics
        self._stats = {
            "total_events": 0,
            "events_by_category": {},
            "events_by_severity": {},
        }
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        return str(uuid.uuid4())
    
    def _should_log(self, category: AuditCategory, severity: AuditSeverity) -> bool:
        """Check if event should be logged based on config."""
        # Check severity
        severity_order = list(AuditSeverity)
        if severity_order.index(severity) < severity_order.index(self.config.min_severity):
            return False
        
        # Check category
        if self.config.enabled_categories:
            if category not in self.config.enabled_categories:
                return False
        
        return True
    
    def log(
        self,
        category: AuditCategory,
        action: str,
        actor_id: str,
        resource_type: str,
        resource_id: str,
        outcome: str = "success",
        severity: AuditSeverity = AuditSeverity.INFO,
        actor_type: str = "user",
        description: str = "",
        ip_address: str = "",
        user_agent: str = "",
        session_id: str = "",
        request_id: str = "",
        duration_ms: float = 0.0,
        metadata: Dict[str, Any] | None = None,
        previous_state: Dict[str, Any] | None = None,
        new_state: Dict[str, Any] | None = None,
    ) -> AuditEvent | None:
        """Log an audit event."""
        if not self._should_log(category, severity):
            return None
        
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=time.time(),
            category=category,
            severity=severity,
            action=action,
            actor_id=actor_id,
            actor_type=actor_type,
            resource_type=resource_type,
            resource_id=resource_id,
            outcome=outcome,
            description=description or f"{action} on {resource_type}/{resource_id}",
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            request_id=request_id,
            duration_ms=duration_ms,
            metadata=metadata or {},
            previous_state=previous_state or {},
            new_state=new_state or {},
        )
        
        # Add chain hash
        if self.config.chain_events:
            event.metadata["previous_hash"] = self._last_event_hash
        
        # Compute hash
        if self.config.include_hash:
            event.metadata["hash"] = event.compute_hash()
            self._last_event_hash = event.metadata["hash"]
        
        # Add to buffer
        self._buffer.add(event)
        
        # Update stats
        self._update_stats(event)
        
        # Stream to subscribers
        if self.config.enable_streaming:
            self._notify_subscribers(event)
        
        return event
    
    def _update_stats(self, event: AuditEvent) -> None:
        """Update internal statistics."""
        with self._lock:
            self._stats["total_events"] += 1
            
            cat_key = event.category.value
            self._stats["events_by_category"][cat_key] = (
                self._stats["events_by_category"].get(cat_key, 0) + 1
            )
            
            sev_key = event.severity.value
            self._stats["events_by_severity"][sev_key] = (
                self._stats["events_by_severity"].get(sev_key, 0) + 1
            )
    
    def _notify_subscribers(self, event: AuditEvent) -> None:
        """Notify all subscribers of new event."""
        for callback in self._subscribers:
            try:
                callback(event)
            except Exception:
                pass
    
    def subscribe(self, callback: Callable[[AuditEvent], None]) -> None:
        """Subscribe to audit events."""
        with self._lock:
            self._subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable[[AuditEvent], None]) -> None:
        """Unsubscribe from audit events."""
        with self._lock:
            if callback in self._subscribers:
                self._subscribers.remove(callback)
    
    def flush(self) -> int:
        """Flush buffered events to storage."""
        events = self._buffer.flush()
        return self._writer.write(events)
    
    def start(self) -> None:
        """Start background flush thread."""
        if self._running:
            return
        
        self._running = True
        self._flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self._flush_thread.start()
    
    def stop(self) -> None:
        """Stop background flush thread."""
        self._running = False
        if self._flush_thread:
            self._flush_thread.join(timeout=5.0)
            self._flush_thread = None
        
        # Final flush
        self.flush()
        self._writer.close()
    
    def _flush_loop(self) -> None:
        """Background loop for periodic flushing."""
        while self._running:
            try:
                if len(self._buffer) > 0:
                    self.flush()
            except Exception:
                pass
            
            time.sleep(self.config.flush_interval_seconds)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get audit statistics."""
        with self._lock:
            return {
                **self._stats,
                "buffer_size": len(self._buffer),
            }
    
    # Convenience methods for common audit events
    
    def log_authentication(
        self,
        actor_id: str,
        outcome: str,
        ip_address: str = "",
        method: str = "password",
        **kwargs
    ) -> AuditEvent | None:
        """Log authentication event."""
        return self.log(
            category=AuditCategory.AUTHENTICATION,
            action=f"auth_{method}",
            actor_id=actor_id,
            resource_type="auth",
            resource_id="system",
            outcome=outcome,
            severity=AuditSeverity.INFO if outcome == "success" else AuditSeverity.WARNING,
            ip_address=ip_address,
            **kwargs
        )
    
    def log_authorization(
        self,
        actor_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        outcome: str,
        **kwargs
    ) -> AuditEvent | None:
        """Log authorization event."""
        return self.log(
            category=AuditCategory.AUTHORIZATION,
            action=f"authz_{action}",
            actor_id=actor_id,
            resource_type=resource_type,
            resource_id=resource_id,
            outcome=outcome,
            severity=AuditSeverity.INFO if outcome == "success" else AuditSeverity.WARNING,
            **kwargs
        )
    
    def log_data_access(
        self,
        actor_id: str,
        resource_type: str,
        resource_id: str,
        access_type: str,  # read, write, delete
        **kwargs
    ) -> AuditEvent | None:
        """Log data access event."""
        category_map = {
            "read": AuditCategory.DATA_READ,
            "write": AuditCategory.DATA_WRITE,
            "delete": AuditCategory.DATA_DELETE,
            "export": AuditCategory.DATA_EXPORT,
        }
        
        return self.log(
            category=category_map.get(access_type, AuditCategory.DATA_READ),
            action=f"data_{access_type}",
            actor_id=actor_id,
            resource_type=resource_type,
            resource_id=resource_id,
            **kwargs
        )
    
    def log_security_alert(
        self,
        actor_id: str,
        alert_type: str,
        description: str,
        severity: AuditSeverity = AuditSeverity.WARNING,
        **kwargs
    ) -> AuditEvent | None:
        """Log security alert."""
        return self.log(
            category=AuditCategory.SECURITY_ALERT,
            action=f"alert_{alert_type}",
            actor_id=actor_id,
            resource_type="security",
            resource_id=alert_type,
            outcome="detected",
            severity=severity,
            description=description,
            **kwargs
        )
    
    def log_configuration_change(
        self,
        actor_id: str,
        config_key: str,
        previous_value: Any,
        new_value: Any,
        **kwargs
    ) -> AuditEvent | None:
        """Log configuration change."""
        return self.log(
            category=AuditCategory.CONFIGURATION,
            action="config_update",
            actor_id=actor_id,
            resource_type="config",
            resource_id=config_key,
            previous_state={"value": previous_value},
            new_state={"value": new_value},
            severity=AuditSeverity.INFO,
            **kwargs
        )
    
    def __enter__(self) -> "AuditLogger":
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop()


# Convenience function for global audit logger
_global_audit_logger: AuditLogger | None = None


def get_audit_logger() -> AuditLogger:
    """Get or create the global audit logger."""
    global _global_audit_logger
    if _global_audit_logger is None:
        _global_audit_logger = AuditLogger()
        _global_audit_logger.start()
    return _global_audit_logger


def audit_event(
    category: AuditCategory,
    action: str,
    actor_id: str,
    resource_type: str,
    resource_id: str,
    **kwargs
) -> AuditEvent | None:
    """Log an audit event using the global logger."""
    return get_audit_logger().log(
        category=category,
        action=action,
        actor_id=actor_id,
        resource_type=resource_type,
        resource_id=resource_id,
        **kwargs
    )
