# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# KR-Labs is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Heartbeat Manager - Session Keep-Alive

Implements heartbeat/keep-alive mechanism for:
- Session maintenance
- Connection health monitoring
- Backend availability detection
- Graceful reconnection
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone, UTC
from enum import Enum
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class HeartbeatStatus(Enum):
    """Heartbeat status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DISCONNECTED = "disconnected"


@dataclass
class HeartbeatResult:
    """Result of a heartbeat attempt."""
    success: bool
    timestamp: datetime
    latency_ms: float
    server_time: Optional[datetime] = None
    session_valid: bool = True
    quota_remaining: Optional[int] = None
    message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "timestamp": self.timestamp.isoformat(),
            "latency_ms": self.latency_ms,
            "server_time": self.server_time.isoformat() if self.server_time else None,
            "session_valid": self.session_valid,
            "quota_remaining": self.quota_remaining,
            "message": self.message,
        }


@dataclass
class HeartbeatConfig:
    """Heartbeat manager configuration."""
    # Timing
    interval_seconds: float = 30.0
    timeout_seconds: float = 10.0
    
    # Health thresholds
    healthy_latency_ms: float = 500.0
    degraded_latency_ms: float = 2000.0
    
    # Failure handling
    max_consecutive_failures: int = 3
    reconnect_delay_seconds: float = 5.0
    max_reconnect_attempts: int = 5
    
    # Adaptive interval
    adaptive_interval: bool = True
    min_interval_seconds: float = 10.0
    max_interval_seconds: float = 120.0


class HeartbeatManager:
    """
    Manages session heartbeats and health monitoring.
    
    Features:
    - Background heartbeat thread
    - Latency tracking
    - Adaptive interval adjustment
    - Automatic reconnection
    """
    
    def __init__(
        self,
        session_id: str,
        heartbeat_func: Callable[[], Optional[Dict[str, Any]]],
        reconnect_func: Optional[Callable[[], bool]] = None,
        config: Optional[HeartbeatConfig] = None,
        on_status_change: Optional[Callable[[HeartbeatStatus, HeartbeatStatus], None]] = None,
    ):
        """
        Initialize heartbeat manager.
        
        Args:
            session_id: Current session ID
            heartbeat_func: Function to send heartbeat
            reconnect_func: Function to reconnect on failure
            config: Manager configuration
            on_status_change: Callback for status changes
        """
        self._session_id = session_id
        self._heartbeat_func = heartbeat_func
        self._reconnect_func = reconnect_func
        self._config = config or HeartbeatConfig()
        self._on_status_change = on_status_change
        
        # State
        self._status = HeartbeatStatus.DISCONNECTED
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # Metrics
        self._consecutive_failures = 0
        self._total_heartbeats = 0
        self._successful_heartbeats = 0
        self._latency_history: list[float] = []
        self._last_heartbeat: Optional[HeartbeatResult] = None
        self._current_interval = self._config.interval_seconds
        
        logger.debug("HeartbeatManager initialized for session %s", session_id[:8])
    
    @property
    def status(self) -> HeartbeatStatus:
        """Get current status."""
        return self._status
    
    @property
    def is_healthy(self) -> bool:
        """Check if connection is healthy."""
        return self._status == HeartbeatStatus.HEALTHY
    
    @property
    def average_latency_ms(self) -> float:
        """Get average latency in milliseconds."""
        if not self._latency_history:
            return 0.0
        return sum(self._latency_history) / len(self._latency_history)
    
    @property
    def success_rate(self) -> float:
        """Get heartbeat success rate."""
        if self._total_heartbeats == 0:
            return 1.0
        return self._successful_heartbeats / self._total_heartbeats
    
    def start(self) -> None:
        """Start heartbeat thread."""
        with self._lock:
            if self._running:
                return
            
            self._running = True
            self._status = HeartbeatStatus.HEALTHY
            
            self._thread = threading.Thread(
                target=self._heartbeat_loop,
                name="heartbeat-manager",
                daemon=True,
            )
            self._thread.start()
            
            logger.info("Heartbeat manager started")
    
    def stop(self) -> None:
        """Stop heartbeat thread."""
        with self._lock:
            if not self._running:
                return
            
            self._running = False
        
        self._set_status(HeartbeatStatus.DISCONNECTED)
        logger.info("Heartbeat manager stopped")
    
    def _set_status(self, new_status: HeartbeatStatus) -> None:
        """Update status with callback."""
        old_status = self._status
        if old_status != new_status:
            self._status = new_status
            logger.info("Heartbeat status: %s -> %s", old_status.value, new_status.value)
            
            if self._on_status_change:
                try:
                    self._on_status_change(old_status, new_status)
                except Exception as e:
                    logger.warning("Status change callback error: %s", e)
    
    def _heartbeat_loop(self) -> None:
        """Background heartbeat loop."""
        while self._running:
            # Send heartbeat
            result = self._send_heartbeat()
            
            # Process result
            self._process_result(result)
            
            # Wait for next interval
            time.sleep(self._current_interval)
    
    def _send_heartbeat(self) -> HeartbeatResult:
        """Send single heartbeat."""
        start_time = time.time()
        self._total_heartbeats += 1
        
        try:
            response = self._heartbeat_func()
            latency_ms = (time.time() - start_time) * 1000
            
            if response:
                self._successful_heartbeats += 1
                self._consecutive_failures = 0
                
                return HeartbeatResult(
                    success=True,
                    timestamp=datetime.now(timezone.utc),
                    latency_ms=latency_ms,
                    server_time=datetime.fromisoformat(
                        response.get("server_time", datetime.now(timezone.utc).isoformat()).replace("Z", "+00:00")
                    ) if response.get("server_time") else None,
                    session_valid=response.get("session_valid", True),
                    quota_remaining=response.get("quota_remaining"),
                    message=response.get("message"),
                )
            else:
                self._consecutive_failures += 1
                return HeartbeatResult(
                    success=False,
                    timestamp=datetime.now(timezone.utc),
                    latency_ms=latency_ms,
                    message="Empty response",
                )
                
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self._consecutive_failures += 1
            
            logger.debug("Heartbeat failed: %s", e)
            
            return HeartbeatResult(
                success=False,
                timestamp=datetime.now(timezone.utc),
                latency_ms=latency_ms,
                message=str(e),
            )
    
    def _process_result(self, result: HeartbeatResult) -> None:
        """Process heartbeat result."""
        self._last_heartbeat = result
        
        if result.success:
            # Update latency history
            self._latency_history.append(result.latency_ms)
            if len(self._latency_history) > 100:
                self._latency_history.pop(0)
            
            # Determine status based on latency
            if result.latency_ms <= self._config.healthy_latency_ms:
                self._set_status(HeartbeatStatus.HEALTHY)
            elif result.latency_ms <= self._config.degraded_latency_ms:
                self._set_status(HeartbeatStatus.DEGRADED)
            else:
                self._set_status(HeartbeatStatus.UNHEALTHY)
            
            # Check session validity
            if not result.session_valid:
                logger.warning("Session invalidated by server")
                self._attempt_reconnect()
            
            # Adjust interval if adaptive
            if self._config.adaptive_interval:
                self._adjust_interval(result)
        else:
            # Handle failure
            if self._consecutive_failures >= self._config.max_consecutive_failures:
                self._set_status(HeartbeatStatus.DISCONNECTED)
                self._attempt_reconnect()
            else:
                self._set_status(HeartbeatStatus.UNHEALTHY)
    
    def _adjust_interval(self, result: HeartbeatResult) -> None:
        """Adjust heartbeat interval based on conditions."""
        if not self._config.adaptive_interval:
            return
        
        # Increase interval if healthy and stable
        if result.latency_ms < self._config.healthy_latency_ms:
            self._current_interval = min(
                self._current_interval * 1.1,
                self._config.max_interval_seconds
            )
        # Decrease interval if degraded
        elif result.latency_ms > self._config.degraded_latency_ms:
            self._current_interval = max(
                self._current_interval * 0.8,
                self._config.min_interval_seconds
            )
    
    def _attempt_reconnect(self) -> None:
        """Attempt to reconnect."""
        if not self._reconnect_func:
            logger.warning("No reconnect function provided")
            return
        
        for attempt in range(self._config.max_reconnect_attempts):
            logger.info("Reconnect attempt %d/%d", 
                       attempt + 1, self._config.max_reconnect_attempts)
            
            try:
                if self._reconnect_func():
                    logger.info("Reconnection successful")
                    self._consecutive_failures = 0
                    self._set_status(HeartbeatStatus.HEALTHY)
                    return
            except Exception as e:
                logger.warning("Reconnect attempt failed: %s", e)
            
            if attempt < self._config.max_reconnect_attempts - 1:
                time.sleep(self._config.reconnect_delay_seconds)
        
        logger.error("All reconnect attempts failed")
        self._set_status(HeartbeatStatus.DISCONNECTED)
    
    def force_heartbeat(self) -> HeartbeatResult:
        """Force immediate heartbeat."""
        result = self._send_heartbeat()
        self._process_result(result)
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get heartbeat statistics."""
        return {
            "status": self._status.value,
            "running": self._running,
            "total_heartbeats": self._total_heartbeats,
            "successful_heartbeats": self._successful_heartbeats,
            "success_rate": round(self.success_rate, 3),
            "consecutive_failures": self._consecutive_failures,
            "average_latency_ms": round(self.average_latency_ms, 2),
            "current_interval_seconds": round(self._current_interval, 1),
            "last_heartbeat": self._last_heartbeat.to_dict() if self._last_heartbeat else None,
        }
    
    def __enter__(self) -> "HeartbeatManager":
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop()
