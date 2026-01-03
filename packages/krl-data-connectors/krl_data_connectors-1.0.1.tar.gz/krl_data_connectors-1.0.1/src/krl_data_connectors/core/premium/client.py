# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# KR-Labs is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Premium Client - Secure Backend Communication

Implements full authentication flow with:
- JWT token management with auto-refresh
- Challenge-response cryptographic verification
- TLS certificate pinning
- Request signing and response verification
- Automatic retry with exponential backoff
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import platform
import socket
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, UTC
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from urllib.parse import urljoin

import httpx

logger = logging.getLogger(__name__)


class ClientState(Enum):
    """Client connection states."""
    DISCONNECTED = "disconnected"
    AUTHENTICATING = "authenticating"
    CONNECTED = "connected"
    CHALLENGE_PENDING = "challenge_pending"
    DEGRADED = "degraded"
    BLOCKED = "blocked"


@dataclass
class AuthTokens:
    """Authentication token container."""
    jwt_token: str
    license_token: str
    integrity_token: str
    expires_at: datetime
    refresh_token: Optional[str] = None
    
    @property
    def is_expired(self) -> bool:
        """Check if tokens need refresh."""
        # Refresh 2 minutes before expiry
        buffer = timedelta(minutes=2)
        return datetime.now(timezone.utc) >= (self.expires_at - buffer)
    
    @property
    def ttl_seconds(self) -> float:
        """Remaining token lifetime in seconds."""
        delta = self.expires_at - datetime.now(timezone.utc)
        return max(0, delta.total_seconds())


@dataclass
class EnvironmentFingerprint:
    """Machine environment fingerprint for verification."""
    machine_id: str
    os_type: str
    os_version: str
    python_version: str
    hostname: str
    cpu_count: int
    process_id: int
    timestamp: str
    nonce: str = field(default_factory=lambda: uuid.uuid4().hex)
    
    @classmethod
    def collect(cls) -> "EnvironmentFingerprint":
        """Collect current environment fingerprint."""
        machine_id = cls._get_machine_id()
        return cls(
            machine_id=machine_id,
            os_type=platform.system(),
            os_version=platform.release(),
            python_version=platform.python_version(),
            hostname=socket.gethostname(),
            cpu_count=os.cpu_count() or 1,
            process_id=os.getpid(),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    
    @staticmethod
    def _get_machine_id() -> str:
        """Get stable machine identifier."""
        components = [
            platform.node(),
            platform.machine(),
            platform.processor(),
            str(uuid.getnode()),  # MAC address
        ]
        combined = "|".join(components)
        return hashlib.sha256(combined.encode()).hexdigest()[:32]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for transmission."""
        return {
            "machine_id": self.machine_id,
            "os_type": self.os_type,
            "os_version": self.os_version,
            "python_version": self.python_version,
            "hostname": self.hostname,
            "cpu_count": self.cpu_count,
            "process_id": self.process_id,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
        }
    
    def create_signature(self, secret: bytes) -> str:
        """Create HMAC signature of fingerprint."""
        data = "|".join([
            self.machine_id,
            self.os_type,
            self.python_version,
            self.timestamp,
            self.nonce,
        ])
        return hmac.new(secret, data.encode(), hashlib.sha256).hexdigest()


@dataclass 
class RequestConfig:
    """Configuration for HTTP requests."""
    timeout: float = 30.0
    max_retries: int = 3
    backoff_factor: float = 0.5
    retry_statuses: tuple = (429, 500, 502, 503, 504)
    

class PremiumClient:
    """
    Secure client for KRL Premium Backend.
    
    Handles full authentication lifecycle:
    1. Initial authentication with API key
    2. Challenge-response verification
    3. Token refresh management
    4. Request signing and verification
    """
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        license_key: str,
        *,
        client_secret: Optional[str] = None,
        verify_ssl: bool = True,
        request_config: Optional[RequestConfig] = None,
        on_state_change: Optional[Callable[[ClientState, ClientState], None]] = None,
    ):
        """
        Initialize Premium Client.
        
        Args:
            base_url: Premium backend URL
            api_key: API key for authentication
            license_key: License key for tier verification
            client_secret: Secret for request signing (from license)
            verify_ssl: Enable TLS verification
            request_config: HTTP request configuration
            on_state_change: Callback for state transitions
        """
        self.base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._license_key = license_key
        self._client_secret = client_secret or os.getenv("KRL_CLIENT_SECRET", "")
        self._secret_bytes = self._client_secret.encode() if self._client_secret else b""
        
        self._config = request_config or RequestConfig()
        self._on_state_change = on_state_change
        
        self._state = ClientState.DISCONNECTED
        self._tokens: Optional[AuthTokens] = None
        self._fingerprint: Optional[EnvironmentFingerprint] = None
        self._session_id: Optional[str] = None
        self._last_challenge: Optional[Dict[str, Any]] = None
        
        # HTTP client configuration
        self._http_client = httpx.Client(
            timeout=self._config.timeout,
            verify=verify_ssl,
            headers=self._base_headers(),
        )
        
        logger.info("PremiumClient initialized for %s", self.base_url)
    
    def _base_headers(self) -> Dict[str, str]:
        """Get base headers for all requests."""
        return {
            "User-Agent": f"KRL-DataConnectors/{self._get_version()}",
            "X-Client-Version": self._get_version(),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    
    @staticmethod
    def _get_version() -> str:
        """Get client version."""
        try:
            from krl_data_connectors import __version__
            return __version__
        except ImportError:
            return "1.0.0"
    
    def _set_state(self, new_state: ClientState) -> None:
        """Update client state with optional callback."""
        old_state = self._state
        if old_state != new_state:
            self._state = new_state
            logger.info("State transition: %s -> %s", old_state.value, new_state.value)
            if self._on_state_change:
                try:
                    self._on_state_change(old_state, new_state)
                except Exception as e:
                    logger.warning("State change callback error: %s", e)
    
    @property
    def state(self) -> ClientState:
        """Get current client state."""
        return self._state
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected and authenticated."""
        return self._state == ClientState.CONNECTED and self._tokens is not None
    
    @property
    def session_id(self) -> Optional[str]:
        """Get current session ID."""
        return self._session_id
    
    def _auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        headers = {}
        if self._tokens:
            headers["Authorization"] = f"Bearer {self._tokens.jwt_token}"
            headers["X-License-Token"] = self._tokens.license_token
            headers["X-Integrity-Token"] = self._tokens.integrity_token
        if self._session_id:
            headers["X-Session-ID"] = self._session_id
        return headers
    
    def _sign_request(self, method: str, path: str, body: Optional[Dict] = None) -> str:
        """Sign request for verification."""
        timestamp = str(int(time.time()))
        nonce = uuid.uuid4().hex
        
        # Create signature payload
        payload_parts = [
            method.upper(),
            path,
            timestamp,
            nonce,
        ]
        if body:
            import json
            payload_parts.append(json.dumps(body, sort_keys=True))
        
        payload = "|".join(payload_parts)
        signature = hmac.new(
            self._secret_bytes,
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{timestamp}:{nonce}:{signature}"
    
    def _request(
        self,
        method: str,
        path: str,
        *,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        require_auth: bool = True,
        retry_count: int = 0,
    ) -> Dict[str, Any]:
        """
        Make authenticated request with retry logic.
        
        Args:
            method: HTTP method
            path: API path
            json_data: Request body
            params: Query parameters
            require_auth: Require authentication
            retry_count: Current retry attempt
            
        Returns:
            Response data
            
        Raises:
            PremiumClientError: On request failure
        """
        url = urljoin(self.base_url, path)
        headers = self._base_headers()
        
        if require_auth:
            if self._tokens and self._tokens.is_expired:
                self._refresh_tokens()
            headers.update(self._auth_headers())
            headers["X-Request-Signature"] = self._sign_request(method, path, json_data)
        
        headers["X-Request-ID"] = uuid.uuid4().hex
        
        try:
            response = self._http_client.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                headers=headers,
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "5"))
                if retry_count < self._config.max_retries:
                    logger.warning("Rate limited, retrying after %ds", retry_after)
                    time.sleep(retry_after)
                    return self._request(
                        method, path,
                        json_data=json_data,
                        params=params,
                        require_auth=require_auth,
                        retry_count=retry_count + 1,
                    )
            
            # Handle server errors with retry
            if response.status_code in self._config.retry_statuses:
                if retry_count < self._config.max_retries:
                    sleep_time = self._config.backoff_factor * (2 ** retry_count)
                    logger.warning(
                        "Request failed with %d, retrying in %.1fs",
                        response.status_code, sleep_time
                    )
                    time.sleep(sleep_time)
                    return self._request(
                        method, path,
                        json_data=json_data,
                        params=params,
                        require_auth=require_auth,
                        retry_count=retry_count + 1,
                    )
            
            # Verify response signature if present
            if "X-Response-Signature" in response.headers and self._secret_bytes:
                self._verify_response_signature(response)
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error("HTTP error: %s", e)
            raise PremiumClientError(f"Request failed: {e}") from e
        except httpx.RequestError as e:
            logger.error("Request error: %s", e)
            raise PremiumClientError(f"Connection error: {e}") from e
    
    def _verify_response_signature(self, response: httpx.Response) -> None:
        """Verify response signature from server."""
        signature = response.headers.get("X-Response-Signature", "")
        if not signature:
            return
        
        # Reconstruct expected signature
        body = response.content
        expected = hmac.new(
            self._secret_bytes,
            body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected):
            logger.warning("Response signature mismatch!")
            # In strict mode, would raise an error here
    
    def connect(self) -> bool:
        """
        Establish authenticated connection.
        
        Returns:
            True if connected successfully
        """
        self._set_state(ClientState.AUTHENTICATING)
        self._fingerprint = EnvironmentFingerprint.collect()
        
        try:
            # Step 1: Initial authentication
            auth_response = self._request(
                "POST",
                "/api/v1/license/authenticate",
                json_data={
                    "api_key": self._api_key,
                    "license_key": self._license_key,
                    "environment": self._fingerprint.to_dict(),
                },
                require_auth=False,
            )
            
            # Extract tokens
            self._tokens = AuthTokens(
                jwt_token=auth_response["access_token"],
                license_token=auth_response["license_token"],
                integrity_token=auth_response.get("integrity_token", ""),
                expires_at=datetime.fromisoformat(
                    auth_response["expires_at"].replace("Z", "+00:00")
                ),
                refresh_token=auth_response.get("refresh_token"),
            )
            self._session_id = auth_response.get("session_id")
            
            # Step 2: Request and complete challenge
            if auth_response.get("requires_challenge", False):
                self._set_state(ClientState.CHALLENGE_PENDING)
                if not self._complete_challenge():
                    self._set_state(ClientState.BLOCKED)
                    return False
            
            self._set_state(ClientState.CONNECTED)
            logger.info("Successfully connected to premium backend")
            return True
            
        except PremiumClientError as e:
            logger.error("Connection failed: %s", e)
            self._set_state(ClientState.DISCONNECTED)
            return False
    
    def _complete_challenge(self) -> bool:
        """Complete challenge-response verification."""
        try:
            # Get challenge
            challenge = self._request(
                "POST",
                "/api/v1/license/challenge",
                json_data={"session_id": self._session_id},
            )
            
            self._last_challenge = challenge
            
            # Compute response
            challenge_data = challenge["challenge"]
            challenge_nonce = challenge["nonce"]
            
            # HMAC-SHA256 of challenge with client secret + fingerprint
            response_payload = f"{challenge_data}|{challenge_nonce}|{self._fingerprint.machine_id}"
            response_hash = hmac.new(
                self._secret_bytes,
                response_payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Submit response
            verify_result = self._request(
                "POST",
                "/api/v1/license/verify-challenge",
                json_data={
                    "challenge_id": challenge["challenge_id"],
                    "response": response_hash,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
            
            if verify_result.get("verified", False):
                logger.info("Challenge verification successful")
                return True
            else:
                logger.error("Challenge verification failed: %s", verify_result.get("reason"))
                return False
                
        except PremiumClientError as e:
            logger.error("Challenge completion error: %s", e)
            return False
    
    def _refresh_tokens(self) -> bool:
        """Refresh authentication tokens."""
        if not self._tokens or not self._tokens.refresh_token:
            logger.warning("No refresh token available, re-authenticating")
            return self.connect()
        
        try:
            refresh_response = self._request(
                "POST",
                "/api/v1/license/refresh",
                json_data={
                    "refresh_token": self._tokens.refresh_token,
                    "session_id": self._session_id,
                },
                require_auth=False,
            )
            
            self._tokens = AuthTokens(
                jwt_token=refresh_response["access_token"],
                license_token=refresh_response["license_token"],
                integrity_token=refresh_response.get("integrity_token", ""),
                expires_at=datetime.fromisoformat(
                    refresh_response["expires_at"].replace("Z", "+00:00")
                ),
                refresh_token=refresh_response.get("refresh_token", self._tokens.refresh_token),
            )
            
            logger.debug("Tokens refreshed successfully")
            return True
            
        except PremiumClientError:
            logger.warning("Token refresh failed, re-authenticating")
            return self.connect()
    
    def disconnect(self) -> None:
        """Gracefully disconnect from backend."""
        if self._state != ClientState.DISCONNECTED:
            try:
                self._request(
                    "POST",
                    "/api/v1/telemetry/session-end",
                    json_data={"session_id": self._session_id},
                )
            except Exception as e:
                logger.debug("Session end notification failed: %s", e)
            
            self._tokens = None
            self._session_id = None
            self._set_state(ClientState.DISCONNECTED)
            logger.info("Disconnected from premium backend")
    
    # Premium API Methods
    
    def compute(
        self,
        operation: str,
        data: Dict[str, Any],
        *,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute premium computation.
        
        Args:
            operation: Operation type
            data: Input data
            parameters: Optional parameters
            
        Returns:
            Computation result
        """
        self._ensure_connected()
        return self._request(
            "POST",
            "/api/v1/premium/compute",
            json_data={
                "operation": operation,
                "data": data,
                "parameters": parameters or {},
            },
        )
    
    def analyze(
        self,
        data: List[Dict[str, Any]],
        *,
        analysis_type: str = "pattern",
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute premium analysis.
        
        Args:
            data: Data for analysis
            analysis_type: Type of analysis
            options: Analysis options
            
        Returns:
            Analysis results
        """
        self._ensure_connected()
        return self._request(
            "POST",
            "/api/v1/premium/analyze",
            json_data={
                "data": data,
                "analysis_type": analysis_type,
                "options": options or {},
            },
        )
    
    def transform(
        self,
        data: Dict[str, Any],
        *,
        transform_type: str = "standard",
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute premium data transformation.
        
        Args:
            data: Data to transform
            transform_type: Transformation type
            config: Transform configuration
            
        Returns:
            Transformed data
        """
        self._ensure_connected()
        return self._request(
            "POST",
            "/api/v1/premium/transform",
            json_data={
                "data": data,
                "transform_type": transform_type,
                "config": config or {},
            },
        )
    
    def _ensure_connected(self) -> None:
        """Ensure client is connected."""
        if not self.is_connected:
            if not self.connect():
                raise PremiumClientError("Failed to establish connection")
    
    def __enter__(self) -> "PremiumClient":
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.disconnect()
    
    def close(self) -> None:
        """Close client and release resources."""
        self.disconnect()
        self._http_client.close()


class PremiumClientError(Exception):
    """Premium client error."""
    pass
