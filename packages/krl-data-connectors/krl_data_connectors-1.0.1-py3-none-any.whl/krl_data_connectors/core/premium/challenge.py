# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# KR-Labs is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Challenge-Response Handler - Cryptographic Verification

Implements client-side challenge-response protocol:
- Challenge reception and parsing
- Cryptographic response computation
- Timing-safe verification
- Replay attack prevention
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, UTC
from enum import Enum
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class ChallengeStatus(Enum):
    """Challenge processing status."""
    PENDING = "pending"
    COMPUTING = "computing"
    SUBMITTED = "submitted"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"
    INVALID = "invalid"


@dataclass
class Challenge:
    """Challenge data container."""
    challenge_id: str
    challenge_data: str
    nonce: str
    issued_at: datetime
    expires_at: datetime
    algorithm: str = "HMAC-SHA256"
    additional_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """Check if challenge has expired."""
        return datetime.now(timezone.utc) >= self.expires_at
    
    @property
    def time_remaining(self) -> timedelta:
        """Get time remaining to respond."""
        return self.expires_at - datetime.now(timezone.utc)
    
    @classmethod
    def from_response(cls, data: Dict[str, Any]) -> "Challenge":
        """Create from server response."""
        return cls(
            challenge_id=data["challenge_id"],
            challenge_data=data["challenge"],
            nonce=data["nonce"],
            issued_at=datetime.fromisoformat(
                data.get("issued_at", datetime.now(timezone.utc).isoformat()).replace("Z", "+00:00")
            ),
            expires_at=datetime.fromisoformat(
                data["expires_at"].replace("Z", "+00:00")
            ),
            algorithm=data.get("algorithm", "HMAC-SHA256"),
            additional_data=data.get("additional_data", {}),
        )


@dataclass
class ChallengeResponse:
    """Challenge response data."""
    challenge_id: str
    response_hash: str
    response_nonce: str
    computed_at: datetime
    machine_id: str
    proof: str  # Additional proof of work
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for submission."""
        return {
            "challenge_id": self.challenge_id,
            "response": self.response_hash,
            "response_nonce": self.response_nonce,
            "timestamp": self.computed_at.isoformat(),
            "machine_id": self.machine_id,
            "proof": self.proof,
        }


class ChallengeHandler:
    """
    Handles cryptographic challenge-response verification.
    
    Security features:
    - Time-bounded challenge validity
    - Unique response nonces
    - Machine-bound responses
    - Timing attack resistance
    """
    
    def __init__(
        self,
        client_secret: bytes,
        machine_id: str,
        *,
        max_response_time_seconds: float = 30.0,
        min_response_time_seconds: float = 0.1,
    ):
        """
        Initialize challenge handler.
        
        Args:
            client_secret: Secret for HMAC computation
            machine_id: Machine identifier for binding
            max_response_time_seconds: Maximum time to respond
            min_response_time_seconds: Minimum time (prevents timing attacks)
        """
        self._secret = client_secret
        self._machine_id = machine_id
        self._max_response_time = max_response_time_seconds
        self._min_response_time = min_response_time_seconds
        
        # Track processed challenges (replay prevention)
        self._processed_challenges: Dict[str, datetime] = {}
        self._last_cleanup = datetime.now(timezone.utc)
        
        # Current challenge
        self._current_challenge: Optional[Challenge] = None
        self._status = ChallengeStatus.PENDING
        
        logger.debug("ChallengeHandler initialized")
    
    @property
    def status(self) -> ChallengeStatus:
        """Get current challenge status."""
        return self._status
    
    @property
    def has_pending_challenge(self) -> bool:
        """Check if there's a pending challenge."""
        return (
            self._current_challenge is not None
            and not self._current_challenge.is_expired
            and self._status == ChallengeStatus.PENDING
        )
    
    def receive_challenge(self, challenge_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Receive and validate a challenge.
        
        Args:
            challenge_data: Challenge data from server
            
        Returns:
            Tuple of (success, message)
        """
        try:
            challenge = Challenge.from_response(challenge_data)
            
            # Check for replay
            if challenge.challenge_id in self._processed_challenges:
                logger.warning("Replay attack detected: challenge already processed")
                self._status = ChallengeStatus.INVALID
                return False, "Challenge already processed (replay detected)"
            
            # Check expiry
            if challenge.is_expired:
                logger.warning("Received expired challenge")
                self._status = ChallengeStatus.EXPIRED
                return False, "Challenge has expired"
            
            # Validate algorithm
            if challenge.algorithm not in ("HMAC-SHA256", "HMAC-SHA384", "HMAC-SHA512"):
                logger.warning("Unsupported algorithm: %s", challenge.algorithm)
                self._status = ChallengeStatus.INVALID
                return False, f"Unsupported algorithm: {challenge.algorithm}"
            
            self._current_challenge = challenge
            self._status = ChallengeStatus.PENDING
            logger.info("Challenge received: %s", challenge.challenge_id[:8])
            
            return True, "Challenge received successfully"
            
        except KeyError as e:
            logger.error("Invalid challenge format: missing %s", e)
            self._status = ChallengeStatus.INVALID
            return False, f"Invalid challenge format: missing {e}"
        except Exception as e:
            logger.error("Challenge reception error: %s", e)
            self._status = ChallengeStatus.INVALID
            return False, str(e)
    
    def compute_response(self) -> Optional[ChallengeResponse]:
        """
        Compute response to current challenge.
        
        Returns:
            Challenge response or None if computation fails
        """
        if not self._current_challenge:
            logger.error("No challenge to respond to")
            return None
        
        if self._current_challenge.is_expired:
            self._status = ChallengeStatus.EXPIRED
            logger.error("Challenge expired before response")
            return None
        
        self._status = ChallengeStatus.COMPUTING
        start_time = time.time()
        
        try:
            challenge = self._current_challenge
            
            # Generate response nonce
            response_nonce = secrets.token_hex(16)
            
            # Build response payload
            payload = self._build_response_payload(
                challenge.challenge_data,
                challenge.nonce,
                response_nonce,
            )
            
            # Compute HMAC based on algorithm
            response_hash = self._compute_hmac(payload, challenge.algorithm)
            
            # Compute proof of work (additional binding)
            proof = self._compute_proof(challenge.challenge_id, response_hash)
            
            # Ensure minimum response time (timing attack resistance)
            elapsed = time.time() - start_time
            if elapsed < self._min_response_time:
                time.sleep(self._min_response_time - elapsed)
            
            response = ChallengeResponse(
                challenge_id=challenge.challenge_id,
                response_hash=response_hash,
                response_nonce=response_nonce,
                computed_at=datetime.now(timezone.utc),
                machine_id=self._machine_id,
                proof=proof,
            )
            
            self._status = ChallengeStatus.SUBMITTED
            logger.debug("Response computed for challenge %s", challenge.challenge_id[:8])
            
            return response
            
        except Exception as e:
            logger.error("Response computation failed: %s", e)
            self._status = ChallengeStatus.FAILED
            return None
    
    def _build_response_payload(
        self,
        challenge_data: str,
        server_nonce: str,
        response_nonce: str,
    ) -> bytes:
        """Build payload for HMAC computation."""
        components = [
            challenge_data,
            server_nonce,
            response_nonce,
            self._machine_id,
            str(int(time.time())),  # Timestamp binding
        ]
        return "|".join(components).encode("utf-8")
    
    def _compute_hmac(self, payload: bytes, algorithm: str) -> str:
        """Compute HMAC with specified algorithm."""
        hash_funcs = {
            "HMAC-SHA256": hashlib.sha256,
            "HMAC-SHA384": hashlib.sha384,
            "HMAC-SHA512": hashlib.sha512,
        }
        hash_func = hash_funcs.get(algorithm, hashlib.sha256)
        return hmac.new(self._secret, payload, hash_func).hexdigest()
    
    def _compute_proof(self, challenge_id: str, response_hash: str) -> str:
        """Compute additional proof binding response to environment."""
        proof_data = f"{challenge_id}|{response_hash}|{self._machine_id}"
        return hashlib.sha256(
            (proof_data + self._machine_id).encode()
        ).hexdigest()[:32]
    
    def mark_verified(self, verified: bool, reason: Optional[str] = None) -> None:
        """Mark challenge as verified or failed."""
        if verified:
            self._status = ChallengeStatus.VERIFIED
            if self._current_challenge:
                # Record as processed (replay prevention)
                self._processed_challenges[self._current_challenge.challenge_id] = \
                    datetime.now(timezone.utc)
            logger.info("Challenge verified successfully")
        else:
            self._status = ChallengeStatus.FAILED
            logger.warning("Challenge verification failed: %s", reason)
        
        self._current_challenge = None
        self._cleanup_processed()
    
    def _cleanup_processed(self) -> None:
        """Remove old processed challenges."""
        now = datetime.now(timezone.utc)
        if (now - self._last_cleanup).total_seconds() < 300:  # Every 5 minutes
            return
        
        cutoff = now - timedelta(hours=1)
        self._processed_challenges = {
            cid: ts for cid, ts in self._processed_challenges.items()
            if ts > cutoff
        }
        self._last_cleanup = now
    
    def reset(self) -> None:
        """Reset handler state."""
        self._current_challenge = None
        self._status = ChallengeStatus.PENDING


class ChallengeFailed(Exception):
    """Challenge verification failed."""
    pass
