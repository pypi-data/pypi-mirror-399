# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# KR-Labs is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Premium Backend Integration

Phase 2 Week 11: Client-side integration with KRL Premium Backend.

Components:
- PremiumClient: Secure communication with backend
- SessionManager: Lifecycle management with auto-refresh
- TelemetryCollector: Async event collection and batching
- FailSafeController: Graceful degradation on errors
- ChallengeHandler: Cryptographic challenge-response
- EnvironmentCollector: Environment fingerprinting
- HeartbeatManager: Session keep-alive
- IntegrityBridge: Runtime integrity integration
"""

from krl_data_connectors.core.premium.client import (
    PremiumClient,
    PremiumClientError,
    ClientState,
    AuthTokens,
    EnvironmentFingerprint,
    RequestConfig,
)
from krl_data_connectors.core.premium.session import (
    SessionManager,
    SessionState,
    SessionConfig,
    SessionError,
)
from krl_data_connectors.core.premium.telemetry import (
    TelemetryCollector,
    TelemetryConfig,
    TelemetryEvent,
    EventType,
)
from krl_data_connectors.core.premium.failsafe import (
    FailSafeController,
    FailSafeConfig,
    FailSafeMode,
    FailureType,
    FailureEvent,
)
from krl_data_connectors.core.premium.challenge import (
    ChallengeHandler,
    Challenge,
    ChallengeResponse,
    ChallengeStatus,
    ChallengeFailed,
)
from krl_data_connectors.core.premium.environment import (
    EnvironmentCollector,
    EnvironmentFingerprint as EnvFingerprint,
    HardwareInfo,
    OSInfo,
    NetworkInfo,
    RuntimeInfo,
)
from krl_data_connectors.core.premium.heartbeat import (
    HeartbeatManager,
    HeartbeatConfig,
    HeartbeatResult,
    HeartbeatStatus,
)
from krl_data_connectors.core.premium.integrity_bridge import (
    IntegrityBridge,
    IntegrityGuard,
    IntegrityViolationError,
)

__all__ = [
    # Client
    "PremiumClient",
    "PremiumClientError",
    "ClientState",
    "AuthTokens",
    "EnvironmentFingerprint",
    "RequestConfig",
    # Session
    "SessionManager",
    "SessionState",
    "SessionConfig",
    "SessionError",
    # Telemetry
    "TelemetryCollector",
    "TelemetryConfig",
    "TelemetryEvent",
    "EventType",
    # FailSafe
    "FailSafeController",
    "FailSafeConfig",
    "FailSafeMode",
    "FailureType",
    "FailureEvent",
    # Challenge
    "ChallengeHandler",
    "Challenge",
    "ChallengeResponse",
    "ChallengeStatus",
    "ChallengeFailed",
    # Environment
    "EnvironmentCollector",
    "EnvFingerprint",
    "HardwareInfo",
    "OSInfo",
    "NetworkInfo",
    "RuntimeInfo",
    # Heartbeat
    "HeartbeatManager",
    "HeartbeatConfig",
    "HeartbeatResult",
    "HeartbeatStatus",
    # Integrity
    "IntegrityBridge",
    "IntegrityGuard",
    "IntegrityViolationError",
]
