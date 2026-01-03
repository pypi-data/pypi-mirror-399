"""
Server-Side Intelligence Module for KRL Data Connectors.

Implements centralized threat intelligence and decision-making
for coordinated protection across all connected clients.

Features:
- Fleet-wide threat correlation
- Centralized policy management
- Real-time threat distribution
- Coordinated response orchestration
"""

import asyncio
import hashlib
import hmac
import json
import logging
import secrets
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from uuid import uuid4

logger = logging.getLogger(__name__)


class ClientTrustLevel(Enum):
    """Trust levels for connected clients."""
    
    UNTRUSTED = "untrusted"
    BASIC = "basic"
    VERIFIED = "verified"
    TRUSTED = "trusted"
    PRIVILEGED = "privileged"


class ThreatSeverity(Enum):
    """Severity levels for threat intelligence."""
    
    INFO = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class IntelligenceType(Enum):
    """Types of intelligence data."""
    
    THREAT_INDICATOR = "threat_indicator"
    POLICY_UPDATE = "policy_update"
    CLIENT_REVOCATION = "client_revocation"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"
    FEATURE_FLAG = "feature_flag"
    RATE_LIMIT = "rate_limit"
    BEHAVIORAL_BASELINE = "behavioral_baseline"


@dataclass
class ConnectedClient:
    """Represents a connected client in the fleet."""
    
    client_id: str
    license_id: str
    instance_id: str
    trust_level: ClientTrustLevel
    connected_at: datetime
    last_heartbeat: datetime
    ip_address: str
    geo_location: Optional[Dict[str, Any]] = None
    client_version: str = ""
    environment: str = "production"
    capabilities: List[str] = field(default_factory=list)
    active_features: Set[str] = field(default_factory=set)
    threat_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_active(self) -> bool:
        """Check if client is actively connected."""
        timeout = timedelta(minutes=5)
        return datetime.now(UTC) - self.last_heartbeat < timeout
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "client_id": self.client_id,
            "license_id": self.license_id,
            "instance_id": self.instance_id,
            "trust_level": self.trust_level.value,
            "connected_at": self.connected_at.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "ip_address": self.ip_address,
            "geo_location": self.geo_location,
            "client_version": self.client_version,
            "environment": self.environment,
            "capabilities": self.capabilities,
            "active_features": list(self.active_features),
            "threat_score": self.threat_score,
            "is_active": self.is_active,
        }


@dataclass
class ThreatBulletin:
    """Threat intelligence bulletin for distribution."""
    
    bulletin_id: str
    severity: ThreatSeverity
    intelligence_type: IntelligenceType
    title: str
    description: str
    indicators: List[Dict[str, Any]]
    recommended_actions: List[str]
    affected_versions: List[str]
    created_at: datetime
    expires_at: Optional[datetime] = None
    source: str = "server"
    signature: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for transmission."""
        return {
            "bulletin_id": self.bulletin_id,
            "severity": self.severity.value,
            "intelligence_type": self.intelligence_type.value,
            "title": self.title,
            "description": self.description,
            "indicators": self.indicators,
            "recommended_actions": self.recommended_actions,
            "affected_versions": self.affected_versions,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "source": self.source,
            "signature": self.signature,
            "metadata": self.metadata,
        }


@dataclass
class FleetPolicy:
    """Policy configuration for fleet-wide enforcement."""
    
    policy_id: str
    name: str
    description: str
    version: int
    rules: List[Dict[str, Any]]
    target_clients: Optional[List[str]] = None  # None = all clients
    target_trust_levels: Optional[List[ClientTrustLevel]] = None
    target_environments: Optional[List[str]] = None
    effective_from: datetime = field(default_factory=lambda: datetime.now(UTC))
    effective_until: Optional[datetime] = None
    priority: int = 0
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def applies_to(self, client: ConnectedClient) -> bool:
        """Check if policy applies to a specific client."""
        if not self.enabled:
            return False
        
        now = datetime.now(UTC)
        if now < self.effective_from:
            return False
        if self.effective_until and now > self.effective_until:
            return False
        
        if self.target_clients and client.client_id not in self.target_clients:
            return False
        
        if self.target_trust_levels and client.trust_level not in self.target_trust_levels:
            return False
        
        if self.target_environments and client.environment not in self.target_environments:
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "rules": self.rules,
            "target_clients": self.target_clients,
            "target_trust_levels": [t.value for t in self.target_trust_levels] if self.target_trust_levels else None,
            "target_environments": self.target_environments,
            "effective_from": self.effective_from.isoformat(),
            "effective_until": self.effective_until.isoformat() if self.effective_until else None,
            "priority": self.priority,
            "enabled": self.enabled,
        }


@dataclass
class ThreatCorrelation:
    """Correlated threat across multiple clients."""
    
    correlation_id: str
    threat_type: str
    severity: ThreatSeverity
    affected_clients: Set[str]
    first_seen: datetime
    last_seen: datetime
    indicators: Dict[str, int]  # indicator -> occurrence count
    confidence: float
    status: str = "active"
    notes: List[str] = field(default_factory=list)
    
    def add_occurrence(self, client_id: str, indicator: str) -> None:
        """Add a new occurrence to the correlation."""
        self.affected_clients.add(client_id)
        self.indicators[indicator] = self.indicators.get(indicator, 0) + 1
        self.last_seen = datetime.now(UTC)
        
        # Update confidence based on spread
        client_count = len(self.affected_clients)
        indicator_count = len(self.indicators)
        self.confidence = min(0.95, 0.3 + (client_count * 0.1) + (indicator_count * 0.05))


class IntelligenceChannel(ABC):
    """Abstract base for intelligence distribution channels."""
    
    @abstractmethod
    async def distribute(
        self,
        bulletin: ThreatBulletin,
        clients: List[ConnectedClient]
    ) -> Dict[str, bool]:
        """Distribute intelligence to clients."""
        pass
    
    @abstractmethod
    async def push_policy(
        self,
        policy: FleetPolicy,
        clients: List[ConnectedClient]
    ) -> Dict[str, bool]:
        """Push policy update to clients."""
        pass


class WebSocketChannel(IntelligenceChannel):
    """WebSocket-based intelligence distribution."""
    
    def __init__(self, connections: Dict[str, Any]):
        """Initialize WebSocket channel.
        
        Args:
            connections: Dict mapping client_id to WebSocket connections
        """
        self.connections = connections
        self.signing_key = secrets.token_bytes(32)
    
    def _sign_message(self, message: Dict[str, Any]) -> str:
        """Sign a message for authenticity."""
        payload = json.dumps(message, sort_keys=True).encode()
        return hmac.new(self.signing_key, payload, hashlib.sha256).hexdigest()
    
    async def distribute(
        self,
        bulletin: ThreatBulletin,
        clients: List[ConnectedClient]
    ) -> Dict[str, bool]:
        """Distribute bulletin via WebSocket."""
        results = {}
        message = {
            "type": "threat_bulletin",
            "data": bulletin.to_dict(),
            "timestamp": datetime.now(UTC).isoformat(),
        }
        message["signature"] = self._sign_message(message)
        
        for client in clients:
            if client.client_id in self.connections:
                try:
                    ws = self.connections[client.client_id]
                    # Simulate sending - in production this would be actual WebSocket send
                    logger.info(f"Distributing bulletin {bulletin.bulletin_id} to {client.client_id}")
                    results[client.client_id] = True
                except Exception as e:
                    logger.error(f"Failed to distribute to {client.client_id}: {e}")
                    results[client.client_id] = False
            else:
                results[client.client_id] = False
        
        return results
    
    async def push_policy(
        self,
        policy: FleetPolicy,
        clients: List[ConnectedClient]
    ) -> Dict[str, bool]:
        """Push policy via WebSocket."""
        results = {}
        message = {
            "type": "policy_update",
            "data": policy.to_dict(),
            "timestamp": datetime.now(UTC).isoformat(),
        }
        message["signature"] = self._sign_message(message)
        
        for client in clients:
            if policy.applies_to(client) and client.client_id in self.connections:
                try:
                    logger.info(f"Pushing policy {policy.policy_id} to {client.client_id}")
                    results[client.client_id] = True
                except Exception as e:
                    logger.error(f"Failed to push policy to {client.client_id}: {e}")
                    results[client.client_id] = False
            else:
                results[client.client_id] = False
        
        return results


class ServerIntelligence:
    """
    Centralized server-side intelligence and decision-making.
    
    Coordinates threat response across all connected clients,
    manages fleet-wide policies, and distributes threat intelligence.
    """
    
    def __init__(
        self,
        signing_key: Optional[bytes] = None,
        correlation_window: timedelta = timedelta(hours=1),
        min_correlation_clients: int = 3,
    ):
        """Initialize server intelligence.
        
        Args:
            signing_key: Key for signing intelligence data
            correlation_window: Time window for threat correlation
            min_correlation_clients: Min clients for correlation confidence
        """
        self.signing_key = signing_key or secrets.token_bytes(32)
        self.correlation_window = correlation_window
        self.min_correlation_clients = min_correlation_clients
        
        # Client registry
        self._clients: Dict[str, ConnectedClient] = {}
        self._client_by_license: Dict[str, Set[str]] = defaultdict(set)
        
        # Intelligence distribution
        self._bulletins: Dict[str, ThreatBulletin] = {}
        self._bulletin_acks: Dict[str, Set[str]] = defaultdict(set)
        
        # Policy management
        self._policies: Dict[str, FleetPolicy] = {}
        self._policy_versions: Dict[str, int] = {}
        
        # Threat correlation
        self._correlations: Dict[str, ThreatCorrelation] = {}
        self._indicator_index: Dict[str, Set[str]] = defaultdict(set)
        
        # Distribution channels
        self._channels: List[IntelligenceChannel] = []
        
        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        # Statistics
        self._stats = {
            "clients_registered": 0,
            "clients_active": 0,
            "bulletins_distributed": 0,
            "policies_pushed": 0,
            "correlations_detected": 0,
            "threats_blocked": 0,
        }
        
        logger.info("ServerIntelligence initialized")
    
    # Client Management
    
    def register_client(
        self,
        license_id: str,
        instance_id: str,
        ip_address: str,
        client_version: str = "",
        environment: str = "production",
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ConnectedClient:
        """Register a new client connection.
        
        Args:
            license_id: License identifier
            instance_id: Unique instance identifier
            ip_address: Client IP address
            client_version: Client software version
            environment: Deployment environment
            capabilities: Client capabilities
            metadata: Additional metadata
            
        Returns:
            ConnectedClient instance
        """
        client_id = f"{license_id}:{instance_id}"
        now = datetime.now(UTC)
        
        # Determine initial trust level
        trust_level = self._assess_initial_trust(license_id, ip_address)
        
        client = ConnectedClient(
            client_id=client_id,
            license_id=license_id,
            instance_id=instance_id,
            trust_level=trust_level,
            connected_at=now,
            last_heartbeat=now,
            ip_address=ip_address,
            client_version=client_version,
            environment=environment,
            capabilities=capabilities or [],
            metadata=metadata or {},
        )
        
        self._clients[client_id] = client
        self._client_by_license[license_id].add(client_id)
        self._stats["clients_registered"] += 1
        
        logger.info(f"Client registered: {client_id} with trust level {trust_level.value}")
        self._trigger_event("client_registered", client)
        
        return client
    
    def _assess_initial_trust(self, license_id: str, ip_address: str) -> ClientTrustLevel:
        """Assess initial trust level for a new client."""
        # Check if license has existing trusted clients
        existing_clients = self._client_by_license.get(license_id, set())
        if existing_clients:
            # Check if any existing client has elevated trust
            for cid in existing_clients:
                if cid in self._clients:
                    if self._clients[cid].trust_level in [
                        ClientTrustLevel.TRUSTED,
                        ClientTrustLevel.PRIVILEGED
                    ]:
                        return ClientTrustLevel.VERIFIED
        
        return ClientTrustLevel.BASIC
    
    def update_client_heartbeat(self, client_id: str) -> bool:
        """Update client heartbeat timestamp.
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if client exists and was updated
        """
        if client_id in self._clients:
            self._clients[client_id].last_heartbeat = datetime.now(UTC)
            return True
        return False
    
    def update_client_trust(
        self,
        client_id: str,
        trust_level: ClientTrustLevel,
        reason: str = ""
    ) -> bool:
        """Update client trust level.
        
        Args:
            client_id: Client identifier
            trust_level: New trust level
            reason: Reason for change
            
        Returns:
            True if updated successfully
        """
        if client_id not in self._clients:
            return False
        
        client = self._clients[client_id]
        old_level = client.trust_level
        client.trust_level = trust_level
        
        logger.info(
            f"Client {client_id} trust changed: {old_level.value} -> {trust_level.value}"
            f" (reason: {reason})"
        )
        
        self._trigger_event("trust_changed", {
            "client": client,
            "old_level": old_level,
            "new_level": trust_level,
            "reason": reason,
        })
        
        return True
    
    def disconnect_client(self, client_id: str, reason: str = "") -> bool:
        """Disconnect and remove a client.
        
        Args:
            client_id: Client identifier
            reason: Disconnect reason
            
        Returns:
            True if client was disconnected
        """
        if client_id not in self._clients:
            return False
        
        client = self._clients.pop(client_id)
        self._client_by_license[client.license_id].discard(client_id)
        
        logger.info(f"Client disconnected: {client_id} (reason: {reason})")
        self._trigger_event("client_disconnected", {"client": client, "reason": reason})
        
        return True
    
    def get_active_clients(self) -> List[ConnectedClient]:
        """Get all active clients."""
        return [c for c in self._clients.values() if c.is_active]
    
    def get_clients_by_trust(self, min_trust: ClientTrustLevel) -> List[ConnectedClient]:
        """Get clients with minimum trust level."""
        trust_order = [
            ClientTrustLevel.UNTRUSTED,
            ClientTrustLevel.BASIC,
            ClientTrustLevel.VERIFIED,
            ClientTrustLevel.TRUSTED,
            ClientTrustLevel.PRIVILEGED,
        ]
        min_idx = trust_order.index(min_trust)
        
        return [
            c for c in self._clients.values()
            if trust_order.index(c.trust_level) >= min_idx
        ]
    
    # Intelligence Distribution
    
    def add_channel(self, channel: IntelligenceChannel) -> None:
        """Add a distribution channel."""
        self._channels.append(channel)
    
    def create_bulletin(
        self,
        severity: ThreatSeverity,
        intelligence_type: IntelligenceType,
        title: str,
        description: str,
        indicators: List[Dict[str, Any]],
        recommended_actions: Optional[List[str]] = None,
        affected_versions: Optional[List[str]] = None,
        ttl_hours: int = 24,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ThreatBulletin:
        """Create a new threat bulletin.
        
        Args:
            severity: Threat severity
            intelligence_type: Type of intelligence
            title: Bulletin title
            description: Detailed description
            indicators: Threat indicators
            recommended_actions: Recommended response actions
            affected_versions: Affected client versions
            ttl_hours: Time to live in hours
            metadata: Additional metadata
            
        Returns:
            Created ThreatBulletin
        """
        bulletin_id = f"TB-{datetime.now(UTC).strftime('%Y%m%d')}-{uuid4().hex[:8]}"
        now = datetime.now(UTC)
        
        bulletin = ThreatBulletin(
            bulletin_id=bulletin_id,
            severity=severity,
            intelligence_type=intelligence_type,
            title=title,
            description=description,
            indicators=indicators,
            recommended_actions=recommended_actions or [],
            affected_versions=affected_versions or ["*"],
            created_at=now,
            expires_at=now + timedelta(hours=ttl_hours),
            metadata=metadata or {},
        )
        
        # Sign bulletin
        bulletin_data = bulletin.to_dict()
        del bulletin_data["signature"]
        payload = json.dumps(bulletin_data, sort_keys=True).encode()
        bulletin.signature = hmac.new(
            self.signing_key, payload, hashlib.sha256
        ).hexdigest()
        
        self._bulletins[bulletin_id] = bulletin
        
        logger.info(f"Created bulletin: {bulletin_id} - {title}")
        return bulletin
    
    async def distribute_bulletin(
        self,
        bulletin: ThreatBulletin,
        target_clients: Optional[List[str]] = None,
        min_trust: ClientTrustLevel = ClientTrustLevel.BASIC,
    ) -> Dict[str, bool]:
        """Distribute bulletin to clients.
        
        Args:
            bulletin: Bulletin to distribute
            target_clients: Specific clients or None for all
            min_trust: Minimum trust level for distribution
            
        Returns:
            Dict mapping client_id to delivery success
        """
        # Get target clients
        if target_clients:
            clients = [
                self._clients[cid] for cid in target_clients
                if cid in self._clients
            ]
        else:
            clients = self.get_clients_by_trust(min_trust)
        
        # Filter by active status and version
        clients = [
            c for c in clients
            if c.is_active and self._version_matches(c.client_version, bulletin.affected_versions)
        ]
        
        # Distribute via all channels
        all_results: Dict[str, bool] = {}
        for channel in self._channels:
            try:
                results = await channel.distribute(bulletin, clients)
                for client_id, success in results.items():
                    if success:
                        all_results[client_id] = True
                        self._bulletin_acks[bulletin.bulletin_id].add(client_id)
            except Exception as e:
                logger.error(f"Channel distribution failed: {e}")
        
        self._stats["bulletins_distributed"] += 1
        self._trigger_event("bulletin_distributed", {
            "bulletin": bulletin,
            "results": all_results,
        })
        
        return all_results
    
    def _version_matches(self, client_version: str, patterns: List[str]) -> bool:
        """Check if client version matches any pattern."""
        if "*" in patterns:
            return True
        
        # Simple version matching - could be enhanced
        return client_version in patterns
    
    # Policy Management
    
    def create_policy(
        self,
        name: str,
        description: str,
        rules: List[Dict[str, Any]],
        target_clients: Optional[List[str]] = None,
        target_trust_levels: Optional[List[ClientTrustLevel]] = None,
        target_environments: Optional[List[str]] = None,
        priority: int = 0,
        effective_hours: Optional[int] = None,
    ) -> FleetPolicy:
        """Create a new fleet policy.
        
        Args:
            name: Policy name
            description: Policy description
            rules: Policy rules
            target_clients: Target client IDs (None = all)
            target_trust_levels: Target trust levels
            target_environments: Target environments
            priority: Policy priority
            effective_hours: Hours until expiry (None = permanent)
            
        Returns:
            Created FleetPolicy
        """
        policy_id = f"POL-{uuid4().hex[:12]}"
        version = self._policy_versions.get(name, 0) + 1
        now = datetime.now(UTC)
        
        policy = FleetPolicy(
            policy_id=policy_id,
            name=name,
            description=description,
            version=version,
            rules=rules,
            target_clients=target_clients,
            target_trust_levels=target_trust_levels,
            target_environments=target_environments,
            effective_from=now,
            effective_until=now + timedelta(hours=effective_hours) if effective_hours else None,
            priority=priority,
        )
        
        self._policies[policy_id] = policy
        self._policy_versions[name] = version
        
        logger.info(f"Created policy: {policy_id} - {name} v{version}")
        return policy
    
    async def push_policy_update(
        self,
        policy: FleetPolicy,
        force: bool = False,
    ) -> Dict[str, bool]:
        """Push policy update to applicable clients.
        
        Args:
            policy: Policy to push
            force: Force push even to inactive clients
            
        Returns:
            Dict mapping client_id to delivery success
        """
        clients = [
            c for c in self._clients.values()
            if policy.applies_to(c) and (force or c.is_active)
        ]
        
        all_results: Dict[str, bool] = {}
        for channel in self._channels:
            try:
                results = await channel.push_policy(policy, clients)
                all_results.update(results)
            except Exception as e:
                logger.error(f"Policy push failed: {e}")
        
        self._stats["policies_pushed"] += 1
        self._trigger_event("policy_pushed", {
            "policy": policy,
            "results": all_results,
        })
        
        return all_results
    
    def get_policies_for_client(self, client_id: str) -> List[FleetPolicy]:
        """Get all active policies for a client."""
        if client_id not in self._clients:
            return []
        
        client = self._clients[client_id]
        policies = [p for p in self._policies.values() if p.applies_to(client)]
        
        # Sort by priority (higher first)
        return sorted(policies, key=lambda p: p.priority, reverse=True)
    
    # Threat Correlation
    
    def report_threat(
        self,
        client_id: str,
        threat_type: str,
        severity: ThreatSeverity,
        indicators: Dict[str, Any],
    ) -> Optional[ThreatCorrelation]:
        """Report a threat observation from a client.
        
        Args:
            client_id: Reporting client
            threat_type: Type of threat
            severity: Threat severity
            indicators: Threat indicators
            
        Returns:
            ThreatCorrelation if correlation detected
        """
        if client_id not in self._clients:
            return None
        
        # Look for existing correlation
        correlation = self._find_correlation(threat_type, indicators)
        
        if correlation:
            # Add to existing correlation
            for indicator_key, indicator_value in indicators.items():
                indicator_str = f"{indicator_key}:{indicator_value}"
                correlation.add_occurrence(client_id, indicator_str)
            
            # Check if correlation threshold reached
            if (len(correlation.affected_clients) >= self.min_correlation_clients
                    and correlation.status == "active"):
                self._trigger_event("correlation_threshold", correlation)
        else:
            # Create new correlation
            correlation_id = f"COR-{uuid4().hex[:12]}"
            now = datetime.now(UTC)
            
            indicator_strs = {
                f"{k}:{v}": 1 for k, v in indicators.items()
            }
            
            correlation = ThreatCorrelation(
                correlation_id=correlation_id,
                threat_type=threat_type,
                severity=severity,
                affected_clients={client_id},
                first_seen=now,
                last_seen=now,
                indicators=indicator_strs,
                confidence=0.3,
            )
            
            self._correlations[correlation_id] = correlation
            
            # Index indicators
            for indicator_str in indicator_strs:
                self._indicator_index[indicator_str].add(correlation_id)
        
        self._stats["correlations_detected"] = len(self._correlations)
        return correlation
    
    def _find_correlation(
        self,
        threat_type: str,
        indicators: Dict[str, Any]
    ) -> Optional[ThreatCorrelation]:
        """Find existing correlation matching indicators."""
        cutoff = datetime.now(UTC) - self.correlation_window
        
        # Search by indicator index
        candidate_ids: Set[str] = set()
        for key, value in indicators.items():
            indicator_str = f"{key}:{value}"
            candidate_ids.update(self._indicator_index.get(indicator_str, set()))
        
        for correlation_id in candidate_ids:
            correlation = self._correlations.get(correlation_id)
            if (correlation
                    and correlation.threat_type == threat_type
                    and correlation.last_seen > cutoff
                    and correlation.status == "active"):
                return correlation
        
        return None
    
    def get_active_correlations(
        self,
        min_confidence: float = 0.5
    ) -> List[ThreatCorrelation]:
        """Get active correlations above confidence threshold."""
        return [
            c for c in self._correlations.values()
            if c.status == "active" and c.confidence >= min_confidence
        ]
    
    async def escalate_correlation(
        self,
        correlation_id: str,
        action: str = "distribute_bulletin",
    ) -> bool:
        """Escalate a correlated threat.
        
        Args:
            correlation_id: Correlation identifier
            action: Escalation action to take
            
        Returns:
            True if escalation successful
        """
        if correlation_id not in self._correlations:
            return False
        
        correlation = self._correlations[correlation_id]
        
        if action == "distribute_bulletin":
            # Create and distribute bulletin
            bulletin = self.create_bulletin(
                severity=correlation.severity,
                intelligence_type=IntelligenceType.THREAT_INDICATOR,
                title=f"Correlated Threat: {correlation.threat_type}",
                description=f"Threat detected across {len(correlation.affected_clients)} clients",
                indicators=[
                    {"type": "correlation", "indicator": k, "count": v}
                    for k, v in correlation.indicators.items()
                ],
                recommended_actions=["investigate", "block_indicators"],
                ttl_hours=4,
            )
            
            await self.distribute_bulletin(bulletin)
            correlation.notes.append(f"Bulletin distributed: {bulletin.bulletin_id}")
            
        elif action == "isolate_clients":
            # Create isolation policy
            policy = self.create_policy(
                name=f"isolation_{correlation_id}",
                description=f"Isolation policy for correlation {correlation_id}",
                rules=[{"action": "restrict_features", "scope": "sensitive"}],
                target_clients=list(correlation.affected_clients),
                priority=100,
                effective_hours=24,
            )
            
            await self.push_policy_update(policy)
            correlation.notes.append(f"Isolation policy applied: {policy.policy_id}")
        
        return True
    
    # Event System
    
    def on_event(self, event_type: str, handler: Callable) -> None:
        """Register event handler.
        
        Args:
            event_type: Event type to handle
            handler: Handler function
        """
        self._event_handlers[event_type].append(handler)
    
    def _trigger_event(self, event_type: str, data: Any) -> None:
        """Trigger an event."""
        for handler in self._event_handlers.get(event_type, []):
            try:
                handler(data)
            except Exception as e:
                logger.error(f"Event handler error ({event_type}): {e}")
    
    # Emergency Response
    
    async def emergency_shutdown(
        self,
        reason: str,
        target_licenses: Optional[List[str]] = None,
    ) -> Dict[str, bool]:
        """Send emergency shutdown command.
        
        Args:
            reason: Shutdown reason
            target_licenses: Specific licenses or None for all
            
        Returns:
            Delivery results
        """
        logger.critical(f"EMERGENCY SHUTDOWN initiated: {reason}")
        
        bulletin = self.create_bulletin(
            severity=ThreatSeverity.CRITICAL,
            intelligence_type=IntelligenceType.EMERGENCY_SHUTDOWN,
            title="Emergency Shutdown",
            description=reason,
            indicators=[],
            recommended_actions=["shutdown_immediately"],
            ttl_hours=1,
        )
        
        # Target clients
        target_clients = None
        if target_licenses:
            target_clients = []
            for license_id in target_licenses:
                target_clients.extend(self._client_by_license.get(license_id, []))
        
        results = await self.distribute_bulletin(
            bulletin,
            target_clients=target_clients,
            min_trust=ClientTrustLevel.UNTRUSTED,
        )
        
        self._trigger_event("emergency_shutdown", {
            "reason": reason,
            "bulletin": bulletin,
            "results": results,
        })
        
        return results
    
    async def revoke_license(
        self,
        license_id: str,
        reason: str,
    ) -> Dict[str, bool]:
        """Revoke a license and disconnect all clients.
        
        Args:
            license_id: License to revoke
            reason: Revocation reason
            
        Returns:
            Delivery results
        """
        logger.warning(f"License revocation: {license_id} - {reason}")
        
        client_ids = list(self._client_by_license.get(license_id, []))
        
        # Create revocation bulletin
        bulletin = self.create_bulletin(
            severity=ThreatSeverity.HIGH,
            intelligence_type=IntelligenceType.CLIENT_REVOCATION,
            title="License Revoked",
            description=reason,
            indicators=[{"license_id": license_id}],
            recommended_actions=["terminate_session"],
            ttl_hours=720,  # 30 days
        )
        
        results = await self.distribute_bulletin(
            bulletin,
            target_clients=client_ids,
            min_trust=ClientTrustLevel.UNTRUSTED,
        )
        
        # Disconnect clients
        for client_id in client_ids:
            self.disconnect_client(client_id, reason=f"License revoked: {reason}")
        
        return results
    
    # Statistics
    
    def get_stats(self) -> Dict[str, Any]:
        """Get server intelligence statistics."""
        now = datetime.now(UTC)
        
        # Count active clients
        active_count = len(self.get_active_clients())
        self._stats["clients_active"] = active_count
        
        # Trust level distribution
        trust_dist = defaultdict(int)
        for client in self._clients.values():
            trust_dist[client.trust_level.value] += 1
        
        # Active correlations
        active_correlations = [
            c for c in self._correlations.values()
            if c.status == "active"
        ]
        
        return {
            **self._stats,
            "timestamp": now.isoformat(),
            "total_clients": len(self._clients),
            "trust_distribution": dict(trust_dist),
            "active_bulletins": len([
                b for b in self._bulletins.values()
                if b.expires_at is None or b.expires_at > now
            ]),
            "active_policies": len([
                p for p in self._policies.values()
                if p.enabled and (p.effective_until is None or p.effective_until > now)
            ]),
            "active_correlations": len(active_correlations),
            "high_severity_correlations": len([
                c for c in active_correlations
                if c.severity in [ThreatSeverity.HIGH, ThreatSeverity.CRITICAL]
            ]),
        }
    
    def get_fleet_health(self) -> Dict[str, Any]:
        """Get overall fleet health assessment."""
        clients = list(self._clients.values())
        active_clients = [c for c in clients if c.is_active]
        
        if not clients:
            return {"status": "no_clients", "score": 0.0}
        
        # Calculate health score
        active_ratio = len(active_clients) / len(clients)
        
        avg_threat_score = (
            sum(c.threat_score for c in clients) / len(clients)
            if clients else 0.0
        )
        
        high_threat_clients = [c for c in clients if c.threat_score > 0.7]
        
        # Active critical correlations
        critical_correlations = [
            c for c in self._correlations.values()
            if c.status == "active" and c.severity == ThreatSeverity.CRITICAL
        ]
        
        health_score = max(0.0, min(1.0,
            active_ratio * 0.3 +
            (1 - avg_threat_score) * 0.3 +
            (1 - len(high_threat_clients) / max(1, len(clients))) * 0.2 +
            (1 - len(critical_correlations) / 10) * 0.2
        ))
        
        if health_score >= 0.8:
            status = "healthy"
        elif health_score >= 0.6:
            status = "degraded"
        elif health_score >= 0.4:
            status = "warning"
        else:
            status = "critical"
        
        return {
            "status": status,
            "score": round(health_score, 2),
            "total_clients": len(clients),
            "active_clients": len(active_clients),
            "high_threat_clients": len(high_threat_clients),
            "critical_correlations": len(critical_correlations),
            "avg_threat_score": round(avg_threat_score, 3),
        }
