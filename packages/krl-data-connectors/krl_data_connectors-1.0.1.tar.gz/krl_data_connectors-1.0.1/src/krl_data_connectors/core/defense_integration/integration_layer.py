"""
Integration Layer - Connects all defense systems into unified protection.

Week 16: Defense Integration & System Hardening
Provides integration bridges between threat_response, ml_defense, and protection layers.
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from collections import defaultdict
import threading
import uuid

logger = logging.getLogger(__name__)


class IntegrationStatus(Enum):
    """Status of integration components."""
    
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    DEGRADED = auto()
    FAILED = auto()


@dataclass
class ComponentInfo:
    """Information about an integrated component."""
    
    component_id: str
    name: str
    component_type: str
    version: str
    status: IntegrationStatus
    last_heartbeat: Optional[datetime] = None
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "component_id": self.component_id,
            "name": self.name,
            "component_type": self.component_type,
            "version": self.version,
            "status": self.status.name,
            "last_heartbeat": (
                self.last_heartbeat.isoformat()
                if self.last_heartbeat else None
            ),
            "capabilities": self.capabilities,
            "metadata": self.metadata,
        }


class MessageBus:
    """Internal message bus for component communication."""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.message_history: List[Dict[str, Any]] = []
        self.max_history = 1000
        self._lock = threading.Lock()
    
    def subscribe(self, topic: str, handler: Callable) -> str:
        """Subscribe to a topic."""
        subscription_id = str(uuid.uuid4())
        
        with self._lock:
            self.subscribers[topic].append((subscription_id, handler))
        
        return subscription_id
    
    def unsubscribe(self, topic: str, subscription_id: str) -> bool:
        """Unsubscribe from a topic."""
        with self._lock:
            handlers = self.subscribers.get(topic, [])
            original_len = len(handlers)
            
            self.subscribers[topic] = [
                (sid, h) for sid, h in handlers
                if sid != subscription_id
            ]
            
            return len(self.subscribers[topic]) < original_len
    
    async def publish(
        self,
        topic: str,
        message: Dict[str, Any],
        source: str = "unknown"
    ) -> int:
        """Publish a message to a topic."""
        message_record = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "source": source,
            "message": message,
        }
        
        with self._lock:
            self.message_history.append(message_record)
            
            # Trim history
            if len(self.message_history) > self.max_history:
                self.message_history = self.message_history[-self.max_history:]
            
            handlers = list(self.subscribers.get(topic, []))
        
        delivered = 0
        for subscription_id, handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
                delivered += 1
            except Exception as e:
                logger.error(f"Message handler error on {topic}: {e}")
        
        return delivered
    
    def get_topics(self) -> List[str]:
        """Get all active topics."""
        with self._lock:
            return list(self.subscribers.keys())
    
    def get_subscriber_count(self, topic: str) -> int:
        """Get number of subscribers for a topic."""
        with self._lock:
            return len(self.subscribers.get(topic, []))


class IntegrationBridge(ABC):
    """Abstract base for integration bridges."""
    
    @property
    @abstractmethod
    def bridge_type(self) -> str:
        """Type of bridge."""
        pass
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect."""
        pass
    
    @abstractmethod
    async def translate(
        self,
        source_format: str,
        target_format: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Translate data between formats."""
        pass


class ThreatResponseBridge(IntegrationBridge):
    """Bridge for threat_response module integration."""
    
    def __init__(self):
        self.connected = False
        self.threat_handlers: Dict[str, Callable] = {}
    
    @property
    def bridge_type(self) -> str:
        return "threat_response"
    
    async def connect(self) -> bool:
        """Connect to threat response system."""
        self.connected = True
        logger.info("ThreatResponseBridge connected")
        return True
    
    async def disconnect(self) -> bool:
        """Disconnect from threat response system."""
        self.connected = False
        return True
    
    async def translate(
        self,
        source_format: str,
        target_format: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Translate between formats."""
        if source_format == "coordinator" and target_format == "threat_response":
            return {
                "threat_id": data.get("event_id"),
                "severity_level": self._map_severity(data.get("severity", 0.5)),
                "entity": data.get("entity_id"),
                "indicators": data.get("evidence", {}),
                "timestamp": data.get("timestamp"),
            }
        elif source_format == "threat_response" and target_format == "coordinator":
            return {
                "event_id": data.get("threat_id"),
                "severity": self._reverse_map_severity(data.get("severity_level", "medium")),
                "entity_id": data.get("entity"),
                "evidence": data.get("indicators", {}),
            }
        return data
    
    def _map_severity(self, severity: float) -> str:
        """Map numeric severity to level."""
        if severity >= 0.8:
            return "critical"
        elif severity >= 0.6:
            return "high"
        elif severity >= 0.4:
            return "medium"
        elif severity >= 0.2:
            return "low"
        return "info"
    
    def _reverse_map_severity(self, level: str) -> float:
        """Map level to numeric severity."""
        mapping = {
            "critical": 0.9,
            "high": 0.7,
            "medium": 0.5,
            "low": 0.3,
            "info": 0.1,
        }
        return mapping.get(level.lower(), 0.5)
    
    def register_threat_handler(
        self,
        threat_type: str,
        handler: Callable
    ) -> None:
        """Register a handler for a threat type."""
        self.threat_handlers[threat_type] = handler
    
    async def process_threat(
        self,
        threat_type: str,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Process a threat through the appropriate handler."""
        handler = self.threat_handlers.get(threat_type)
        if not handler:
            return None
        
        if asyncio.iscoroutinefunction(handler):
            return await handler(data)
        return handler(data)


class MLDefenseBridge(IntegrationBridge):
    """Bridge for ml_defense module integration."""
    
    def __init__(self):
        self.connected = False
        self.models: Dict[str, Any] = {}
    
    @property
    def bridge_type(self) -> str:
        return "ml_defense"
    
    async def connect(self) -> bool:
        """Connect to ML defense system."""
        self.connected = True
        logger.info("MLDefenseBridge connected")
        return True
    
    async def disconnect(self) -> bool:
        """Disconnect from ML defense system."""
        self.connected = False
        return True
    
    async def translate(
        self,
        source_format: str,
        target_format: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Translate between formats."""
        if source_format == "coordinator" and target_format == "ml_defense":
            return {
                "features": self._extract_features(data),
                "context": {
                    "entity_id": data.get("entity_id"),
                    "timestamp": data.get("timestamp"),
                },
            }
        elif source_format == "ml_defense" and target_format == "coordinator":
            return {
                "anomaly_score": data.get("score", 0.0),
                "prediction": data.get("prediction"),
                "confidence": data.get("confidence", 0.0),
                "model_id": data.get("model_id"),
            }
        return data
    
    def _extract_features(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Extract ML features from event data."""
        features = {}
        
        # Map common fields to features
        features["severity"] = data.get("severity", 0.0)
        
        evidence = data.get("evidence", {})
        features["evidence_count"] = float(len(evidence))
        
        # Add more feature extraction as needed
        return features
    
    async def get_prediction(
        self,
        features: Dict[str, float]
    ) -> Dict[str, Any]:
        """Get prediction from ML models."""
        # In production, this would call actual ML models
        return {
            "prediction": "normal",
            "confidence": 0.85,
            "model_id": "ensemble_v1",
        }


class LicenseProtectionBridge(IntegrationBridge):
    """Bridge for license protection integration."""
    
    def __init__(self):
        self.connected = False
        self.license_checks: Dict[str, datetime] = {}
    
    @property
    def bridge_type(self) -> str:
        return "license_protection"
    
    async def connect(self) -> bool:
        """Connect to license protection system."""
        self.connected = True
        logger.info("LicenseProtectionBridge connected")
        return True
    
    async def disconnect(self) -> bool:
        """Disconnect from license protection system."""
        self.connected = False
        return True
    
    async def translate(
        self,
        source_format: str,
        target_format: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Translate between formats."""
        if source_format == "coordinator" and target_format == "license":
            return {
                "license_id": data.get("entity_id"),
                "violation_type": self._map_to_violation(data.get("domain")),
                "details": data.get("evidence", {}),
            }
        return data
    
    def _map_to_violation(self, domain: str) -> str:
        """Map domain to violation type."""
        mapping = {
            "license": "license_violation",
            "behavioral": "usage_anomaly",
            "data_exfiltration": "data_theft",
            "network": "network_abuse",
        }
        return mapping.get(domain, "unknown")
    
    async def check_license(self, license_id: str) -> Dict[str, Any]:
        """Check license status."""
        self.license_checks[license_id] = datetime.now()
        
        return {
            "license_id": license_id,
            "status": "valid",
            "tier": "enterprise",
            "expires": (datetime.now() + timedelta(days=365)).isoformat(),
        }


@dataclass
class IntegrationConfig:
    """Configuration for integration layer."""
    
    enable_message_bus: bool = True
    heartbeat_interval_seconds: int = 30
    connection_timeout_seconds: int = 10
    max_retry_attempts: int = 3
    enable_auto_reconnect: bool = True


class IntegrationLayer:
    """Main integration layer coordinating all bridges."""
    
    def __init__(self, config: Optional[IntegrationConfig] = None):
        self.config = config or IntegrationConfig()
        
        # Components
        self.components: Dict[str, ComponentInfo] = {}
        self.bridges: Dict[str, IntegrationBridge] = {}
        
        # Message bus
        self.message_bus = MessageBus() if self.config.enable_message_bus else None
        
        # State
        self._running = False
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._lock = threading.Lock()
    
    def register_component(
        self,
        component_id: str,
        name: str,
        component_type: str,
        version: str = "1.0.0",
        capabilities: Optional[List[str]] = None
    ) -> ComponentInfo:
        """Register an integration component."""
        info = ComponentInfo(
            component_id=component_id,
            name=name,
            component_type=component_type,
            version=version,
            status=IntegrationStatus.DISCONNECTED,
            capabilities=capabilities or [],
        )
        
        with self._lock:
            self.components[component_id] = info
        
        logger.info(f"Registered component: {name} ({component_type})")
        return info
    
    def register_bridge(
        self,
        bridge_id: str,
        bridge: IntegrationBridge
    ) -> None:
        """Register an integration bridge."""
        with self._lock:
            self.bridges[bridge_id] = bridge
        
        logger.info(f"Registered bridge: {bridge_id} ({bridge.bridge_type})")
    
    async def connect_all(self) -> Dict[str, bool]:
        """Connect all bridges."""
        results = {}
        
        for bridge_id, bridge in self.bridges.items():
            try:
                success = await bridge.connect()
                results[bridge_id] = success
                
                # Update component status
                for comp_id, comp in self.components.items():
                    if comp.component_type == bridge.bridge_type:
                        comp.status = (
                            IntegrationStatus.CONNECTED
                            if success
                            else IntegrationStatus.FAILED
                        )
                        comp.last_heartbeat = datetime.now()
            except Exception as e:
                logger.error(f"Failed to connect bridge {bridge_id}: {e}")
                results[bridge_id] = False
        
        return results
    
    async def disconnect_all(self) -> Dict[str, bool]:
        """Disconnect all bridges."""
        results = {}
        
        for bridge_id, bridge in self.bridges.items():
            try:
                success = await bridge.disconnect()
                results[bridge_id] = success
            except Exception as e:
                logger.error(f"Failed to disconnect bridge {bridge_id}: {e}")
                results[bridge_id] = False
        
        return results
    
    async def route_message(
        self,
        source: str,
        target: str,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Route and translate a message between components."""
        # Find appropriate bridge
        target_bridge = None
        for bridge in self.bridges.values():
            if bridge.bridge_type == target:
                target_bridge = bridge
                break
        
        if not target_bridge:
            logger.warning(f"No bridge found for target: {target}")
            return None
        
        # Translate data
        translated = await target_bridge.translate(
            source_format=source,
            target_format=target,
            data=data
        )
        
        # Publish to message bus if enabled
        if self.message_bus:
            await self.message_bus.publish(
                topic=f"{source}_to_{target}",
                message=translated,
                source=source
            )
        
        return translated
    
    async def broadcast(
        self,
        message: Dict[str, Any],
        source: str
    ) -> Dict[str, int]:
        """Broadcast a message to all components."""
        results = {}
        
        if self.message_bus:
            for topic in self.message_bus.get_topics():
                delivered = await self.message_bus.publish(
                    topic=topic,
                    message=message,
                    source=source
                )
                results[topic] = delivered
        
        return results
    
    async def start_heartbeat(self) -> None:
        """Start heartbeat monitoring."""
        self._running = True
        
        async def heartbeat_loop():
            while self._running:
                for comp_id, comp in self.components.items():
                    if comp.status == IntegrationStatus.CONNECTED:
                        comp.last_heartbeat = datetime.now()
                
                await asyncio.sleep(self.config.heartbeat_interval_seconds)
        
        self._heartbeat_task = asyncio.create_task(heartbeat_loop())
    
    async def stop_heartbeat(self) -> None:
        """Stop heartbeat monitoring."""
        self._running = False
        
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration layer status."""
        return {
            "running": self._running,
            "components": {
                comp_id: comp.to_dict()
                for comp_id, comp in self.components.items()
            },
            "bridges": {
                bridge_id: {
                    "type": bridge.bridge_type,
                    "connected": getattr(bridge, "connected", False),
                }
                for bridge_id, bridge in self.bridges.items()
            },
            "message_bus": {
                "enabled": self.message_bus is not None,
                "topics": (
                    self.message_bus.get_topics()
                    if self.message_bus else []
                ),
            },
        }


class UnifiedDefenseSystem:
    """Unified defense system integrating all protection layers."""
    
    def __init__(self):
        self.integration = IntegrationLayer()
        
        # Create bridges
        self.threat_bridge = ThreatResponseBridge()
        self.ml_bridge = MLDefenseBridge()
        self.license_bridge = LicenseProtectionBridge()
        
        # Register bridges
        self.integration.register_bridge("threat", self.threat_bridge)
        self.integration.register_bridge("ml", self.ml_bridge)
        self.integration.register_bridge("license", self.license_bridge)
        
        # Register components
        self.integration.register_component(
            "threat_response",
            "Threat Response System",
            "threat_response",
            "1.0.0",
            ["detect", "respond", "remediate"]
        )
        
        self.integration.register_component(
            "ml_defense",
            "ML Defense System",
            "ml_defense",
            "1.0.0",
            ["anomaly_detection", "prediction", "pattern_learning"]
        )
        
        self.integration.register_component(
            "license_protection",
            "License Protection System",
            "license_protection",
            "1.0.0",
            ["validate", "enforce", "audit"]
        )
    
    async def initialize(self) -> bool:
        """Initialize the unified defense system."""
        try:
            # Connect all bridges
            results = await self.integration.connect_all()
            
            if not all(results.values()):
                logger.warning("Some bridges failed to connect")
            
            # Start heartbeat
            await self.integration.start_heartbeat()
            
            # Subscribe to events
            if self.integration.message_bus:
                self.integration.message_bus.subscribe(
                    "security_events",
                    self._handle_security_event
                )
            
            logger.info("Unified defense system initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize defense system: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the unified defense system."""
        await self.integration.stop_heartbeat()
        await self.integration.disconnect_all()
        logger.info("Unified defense system shut down")
    
    async def _handle_security_event(self, event: Dict[str, Any]) -> None:
        """Handle incoming security events."""
        logger.info(f"Security event received: {event.get('type', 'unknown')}")
    
    async def process_threat(
        self,
        threat_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a threat through all defense layers."""
        results = {
            "threat_data": threat_data,
            "layers": {},
        }
        
        # Threat response layer
        threat_formatted = await self.integration.route_message(
            source="coordinator",
            target="threat_response",
            data=threat_data
        )
        results["layers"]["threat_response"] = threat_formatted
        
        # ML defense layer
        ml_formatted = await self.integration.route_message(
            source="coordinator",
            target="ml_defense",
            data=threat_data
        )
        results["layers"]["ml_defense"] = ml_formatted
        
        # Get ML prediction
        if ml_formatted:
            prediction = await self.ml_bridge.get_prediction(
                ml_formatted.get("features", {})
            )
            results["layers"]["ml_prediction"] = prediction
        
        # License protection layer
        license_formatted = await self.integration.route_message(
            source="coordinator",
            target="license",
            data=threat_data
        )
        results["layers"]["license_protection"] = license_formatted
        
        return results
    
    def get_defense_status(self) -> Dict[str, Any]:
        """Get unified defense system status."""
        return {
            "system": "unified_defense",
            "version": "1.0.0",
            "integration": self.integration.get_status(),
        }


# Factory functions
def create_integration_layer(
    enable_message_bus: bool = True
) -> IntegrationLayer:
    """Create an integration layer."""
    config = IntegrationConfig(enable_message_bus=enable_message_bus)
    return IntegrationLayer(config)


def create_unified_defense() -> UnifiedDefenseSystem:
    """Create a unified defense system."""
    return UnifiedDefenseSystem()
