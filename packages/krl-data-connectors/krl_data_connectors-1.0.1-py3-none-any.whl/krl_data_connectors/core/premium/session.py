# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# KR-Labs is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Session Manager - Authentication Lifecycle Management

Implements session lifecycle with:
- Automatic token refresh
- Session persistence across restarts
- Multi-session coordination
- Graceful session recovery
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, UTC
from pathlib import Path
from typing import Any, Dict, Optional, Callable
import uuid

logger = logging.getLogger(__name__)


@dataclass
class SessionState:
    """Session state container."""
    session_id: str
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    token_hash: str  # Hash of current token (not the token itself)
    machine_id: str
    tier: str = "community"
    features_enabled: list = field(default_factory=list)
    is_valid: bool = True
    invalidation_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for persistence."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "token_hash": self.token_hash,
            "machine_id": self.machine_id,
            "tier": self.tier,
            "features_enabled": self.features_enabled,
            "is_valid": self.is_valid,
            "invalidation_reason": self.invalidation_reason,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionState":
        """Deserialize from persistence."""
        return cls(
            session_id=data["session_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            last_activity=datetime.fromisoformat(data["last_activity"]),
            token_hash=data["token_hash"],
            machine_id=data["machine_id"],
            tier=data.get("tier", "community"),
            features_enabled=data.get("features_enabled", []),
            is_valid=data.get("is_valid", True),
            invalidation_reason=data.get("invalidation_reason"),
        )
    
    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.now(timezone.utc) >= self.expires_at
    
    @property
    def time_until_expiry(self) -> timedelta:
        """Get time until session expires."""
        return self.expires_at - datetime.now(timezone.utc)
    
    @property
    def needs_refresh(self) -> bool:
        """Check if session needs token refresh."""
        # Refresh when 80% of lifetime has passed
        total_lifetime = (self.expires_at - self.created_at).total_seconds()
        elapsed = (datetime.now(timezone.utc) - self.created_at).total_seconds()
        return elapsed >= (total_lifetime * 0.8)


@dataclass
class SessionConfig:
    """Session manager configuration."""
    # Persistence
    persist_sessions: bool = True
    session_file_path: Optional[str] = None
    
    # Timeouts
    session_timeout_minutes: int = 60
    refresh_before_expiry_minutes: int = 5
    inactivity_timeout_minutes: int = 30
    
    # Retry
    max_refresh_attempts: int = 3
    refresh_retry_delay_seconds: float = 5.0
    
    # Security
    validate_machine_id: bool = True
    allow_multiple_sessions: bool = False


class SessionManager:
    """
    Manages authentication session lifecycle.
    
    Features:
    - Automatic token refresh before expiry
    - Session state persistence
    - Machine binding verification
    - Inactivity timeout handling
    """
    
    def __init__(
        self,
        machine_id: str,
        refresh_func: Callable[[], Optional[Dict[str, Any]]],
        config: Optional[SessionConfig] = None,
    ):
        """
        Initialize session manager.
        
        Args:
            machine_id: Current machine identifier
            refresh_func: Function to refresh tokens
            config: Manager configuration
        """
        self._machine_id = machine_id
        self._refresh_func = refresh_func
        self._config = config or SessionConfig()
        
        self._session: Optional[SessionState] = None
        self._lock = threading.RLock()
        self._refresh_thread: Optional[threading.Thread] = None
        self._running = False
        
        # Session file path
        if self._config.persist_sessions:
            self._session_file = Path(
                self._config.session_file_path or
                os.path.expanduser("~/.krl/session_state.json")
            )
            self._session_file.parent.mkdir(parents=True, exist_ok=True)
        else:
            self._session_file = None
        
        # Try to restore previous session
        if self._config.persist_sessions:
            self._restore_session()
        
        logger.debug("SessionManager initialized for machine %s", machine_id[:8])
    
    def create_session(
        self,
        session_id: str,
        access_token: str,
        expires_at: datetime,
        tier: str = "community",
        features: Optional[list] = None,
    ) -> SessionState:
        """
        Create a new session.
        
        Args:
            session_id: Session identifier from backend
            access_token: Current access token
            expires_at: Token expiration time
            tier: License tier
            features: Enabled features
            
        Returns:
            New session state
        """
        with self._lock:
            now = datetime.now(timezone.utc)
            
            self._session = SessionState(
                session_id=session_id,
                created_at=now,
                expires_at=expires_at,
                last_activity=now,
                token_hash=self._hash_token(access_token),
                machine_id=self._machine_id,
                tier=tier,
                features_enabled=features or [],
            )
            
            self._persist_session()
            self._start_refresh_thread()
            
            logger.info("Session created: %s (tier: %s)", session_id[:8], tier)
            return self._session
    
    def update_session(
        self,
        access_token: str,
        expires_at: datetime,
    ) -> None:
        """Update session with refreshed tokens."""
        with self._lock:
            if not self._session:
                raise SessionError("No active session")
            
            self._session.token_hash = self._hash_token(access_token)
            self._session.expires_at = expires_at
            self._session.last_activity = datetime.now(timezone.utc)
            
            self._persist_session()
            logger.debug("Session updated, expires at %s", expires_at)
    
    def record_activity(self) -> None:
        """Record session activity (for inactivity tracking)."""
        with self._lock:
            if self._session:
                self._session.last_activity = datetime.now(timezone.utc)
    
    def invalidate_session(self, reason: str = "manual") -> None:
        """Invalidate current session."""
        with self._lock:
            if self._session:
                self._session.is_valid = False
                self._session.invalidation_reason = reason
                self._persist_session()
                logger.info("Session invalidated: %s", reason)
            
            self._stop_refresh_thread()
            self._session = None
            
            # Remove persisted session
            if self._session_file and self._session_file.exists():
                self._session_file.unlink()
    
    def get_session(self) -> Optional[SessionState]:
        """Get current session state."""
        with self._lock:
            return self._session
    
    @property
    def is_valid(self) -> bool:
        """Check if session is valid."""
        with self._lock:
            if not self._session:
                return False
            
            if not self._session.is_valid:
                return False
            
            if self._session.is_expired:
                return False
            
            # Check inactivity
            if self._config.inactivity_timeout_minutes > 0:
                inactive_time = datetime.now(timezone.utc) - self._session.last_activity
                if inactive_time > timedelta(minutes=self._config.inactivity_timeout_minutes):
                    self.invalidate_session("inactivity_timeout")
                    return False
            
            # Validate machine binding
            if self._config.validate_machine_id:
                if self._session.machine_id != self._machine_id:
                    self.invalidate_session("machine_id_mismatch")
                    return False
            
            return True
    
    @property
    def session_id(self) -> Optional[str]:
        """Get current session ID."""
        return self._session.session_id if self._session else None
    
    @property
    def tier(self) -> str:
        """Get current tier."""
        return self._session.tier if self._session else "community"
    
    def has_feature(self, feature: str) -> bool:
        """Check if feature is enabled."""
        if not self._session:
            return False
        return feature in self._session.features_enabled
    
    def _hash_token(self, token: str) -> str:
        """Hash token for storage (not the actual token)."""
        return hashlib.sha256(token.encode()).hexdigest()[:32]
    
    def _persist_session(self) -> None:
        """Persist session state to file."""
        if not self._session_file or not self._session:
            return
        
        try:
            with open(self._session_file, "w") as f:
                json.dump(self._session.to_dict(), f)
        except Exception as e:
            logger.warning("Failed to persist session: %s", e)
    
    def _restore_session(self) -> None:
        """Restore session from file."""
        if not self._session_file or not self._session_file.exists():
            return
        
        try:
            with open(self._session_file, "r") as f:
                data = json.load(f)
            
            session = SessionState.from_dict(data)
            
            # Validate restored session
            if not session.is_valid or session.is_expired:
                logger.info("Restored session is invalid/expired, discarding")
                self._session_file.unlink()
                return
            
            # Check machine binding
            if self._config.validate_machine_id and session.machine_id != self._machine_id:
                logger.warning("Restored session machine ID mismatch, discarding")
                self._session_file.unlink()
                return
            
            self._session = session
            self._start_refresh_thread()
            logger.info("Session restored: %s", session.session_id[:8])
            
        except Exception as e:
            logger.warning("Failed to restore session: %s", e)
            if self._session_file.exists():
                self._session_file.unlink()
    
    def _start_refresh_thread(self) -> None:
        """Start background refresh thread."""
        if self._refresh_thread and self._refresh_thread.is_alive():
            return
        
        self._running = True
        self._refresh_thread = threading.Thread(
            target=self._refresh_loop,
            name="session-refresh",
            daemon=True,
        )
        self._refresh_thread.start()
    
    def _stop_refresh_thread(self) -> None:
        """Stop background refresh thread."""
        self._running = False
    
    def _refresh_loop(self) -> None:
        """Background loop to refresh tokens before expiry."""
        while self._running:
            time.sleep(30)  # Check every 30 seconds
            
            with self._lock:
                if not self._session or not self._running:
                    break
                
                if not self._session.needs_refresh:
                    continue
            
            # Attempt refresh
            for attempt in range(self._config.max_refresh_attempts):
                try:
                    result = self._refresh_func()
                    if result:
                        self.update_session(
                            access_token=result.get("access_token", ""),
                            expires_at=datetime.fromisoformat(
                                result["expires_at"].replace("Z", "+00:00")
                            ),
                        )
                        logger.info("Session tokens refreshed")
                        break
                except Exception as e:
                    logger.warning(
                        "Token refresh attempt %d failed: %s",
                        attempt + 1, e
                    )
                    if attempt < self._config.max_refresh_attempts - 1:
                        time.sleep(self._config.refresh_retry_delay_seconds)
            else:
                # All attempts failed
                logger.error("Token refresh failed after all attempts")
                self.invalidate_session("refresh_failed")
    
    def __enter__(self) -> "SessionManager":
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self._stop_refresh_thread()


class SessionError(Exception):
    """Session management error."""
    pass
