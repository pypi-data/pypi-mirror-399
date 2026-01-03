# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Dashboard Hooks - Phase 3 Week 18 Refinement

Lightweight hooks for Week 19's dashboard integration.
Standardized schemas for:
- DLS metrics
- Enforcement heatmap events
- Threat flow visualization
- Anomaly correlation

These hooks capture data in a format optimized for
real-time dashboard rendering.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import deque
import threading


# =============================================================================
# Dashboard Event Types
# =============================================================================

class DashboardEventType(Enum):
    """Types of dashboard-relevant events."""
    
    # DLS Events
    DLS_UPDATE = "dls.update"
    DLS_COMPONENT_CHANGE = "dls.component_change"
    DLS_THRESHOLD_BREACH = "dls.threshold_breach"
    
    # Enforcement Events
    ENFORCEMENT_HEATMAP = "enforcement.heatmap"
    ENFORCEMENT_DECISION = "enforcement.decision"
    ENFORCEMENT_SPIKE = "enforcement.spike"
    
    # Threat Events
    THREAT_DETECTED = "threat.detected"
    THREAT_FLOW = "threat.flow"
    THREAT_CORRELATION = "threat.correlation"
    
    # Anomaly Events
    ANOMALY_DETECTED = "anomaly.detected"
    ANOMALY_CORRELATION = "anomaly.correlation"
    ANOMALY_CLUSTER = "anomaly.cluster"
    
    # Revenue Events
    TIER_USAGE = "tier.usage"
    REVENUE_ALERT = "revenue.alert"
    
    # System Events
    BUDGET_VIOLATION = "budget.violation"
    SYSTEM_HEALTH = "system.health"


# Backwards-compatible alias
HookType = DashboardEventType


# =============================================================================
# Dashboard Event Schema
# =============================================================================

@dataclass
class DashboardEvent:
    """
    Standardized event for dashboard consumption.
    
    Attributes:
        event_type: Type of dashboard event
        timestamp: Unix timestamp
        source: Event source component
        data: Event-specific payload
        tier: Associated tier (if applicable)
        correlation_id: For linking related events
        priority: Display priority (1-10)
    """
    event_type: DashboardEventType
    timestamp: float
    source: str
    data: Dict[str, Any]
    tier: Optional[str] = None
    correlation_id: Optional[str] = None
    priority: int = 5
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "source": self.source,
            "data": self.data,
            "tier": self.tier,
            "correlation_id": self.correlation_id,
            "priority": self.priority,
        }


# =============================================================================
# DLS Dashboard Schema
# =============================================================================

@dataclass
class DLSSnapshot:
    """
    DLS snapshot for dashboard rendering.
    
    Optimized schema for real-time gauge displays.
    """
    timestamp: float
    dls_score: float
    components: Dict[str, float]
    status: str  # healthy, degraded, warning, critical
    tier: str
    trend: str  # improving, stable, degrading
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "dls_score": self.dls_score,
            "components": self.components,
            "status": self.status,
            "tier": self.tier,
            "trend": self.trend,
        }
    
    def to_dashboard_event(self) -> DashboardEvent:
        return DashboardEvent(
            event_type=DashboardEventType.DLS_UPDATE,
            timestamp=self.timestamp,
            source="dls_scorer",
            data=self.to_dict(),
            tier=self.tier,
            priority=8 if self.status in ("warning", "critical") else 5,
        )


# =============================================================================
# Enforcement Heatmap Schema
# =============================================================================

@dataclass
class EnforcementHeatmapCell:
    """
    Single cell in enforcement heatmap.
    
    Represents enforcement activity for a specific
    dimension combination (e.g., tier x action).
    """
    dimension_x: str  # e.g., tier
    dimension_y: str  # e.g., action type
    value_x: str  # e.g., "community"
    value_y: str  # e.g., "throttle"
    count: int
    intensity: float  # 0.0-1.0 for color intensity
    last_update: float


@dataclass
class EnforcementHeatmap:
    """
    Enforcement heatmap data for dashboard.
    
    2D grid showing enforcement patterns across
    configurable dimensions.
    """
    timestamp: float
    dimension_x: str
    dimension_y: str
    cells: List[EnforcementHeatmapCell]
    total_enforcements: int
    window_sec: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "dimension_x": self.dimension_x,
            "dimension_y": self.dimension_y,
            "cells": [
                {
                    "x": c.value_x,
                    "y": c.value_y,
                    "count": c.count,
                    "intensity": c.intensity,
                }
                for c in self.cells
            ],
            "total": self.total_enforcements,
            "window_sec": self.window_sec,
        }
    
    def to_dashboard_event(self) -> DashboardEvent:
        return DashboardEvent(
            event_type=DashboardEventType.ENFORCEMENT_HEATMAP,
            timestamp=self.timestamp,
            source="enforcement_tracker",
            data=self.to_dict(),
            priority=6,
        )


# =============================================================================
# Threat Flow Schema
# =============================================================================

@dataclass
class ThreatFlowNode:
    """
    Node in threat flow visualization.
    
    Represents a stage in threat detection/response pipeline.
    """
    node_id: str
    node_type: str  # detection, analysis, response, resolution
    label: str
    count: int
    avg_latency_ms: float
    status: str  # active, idle, error


@dataclass
class ThreatFlowEdge:
    """
    Edge in threat flow visualization.
    
    Represents flow between pipeline stages.
    """
    source_id: str
    target_id: str
    count: int
    avg_latency_ms: float


@dataclass
class ThreatFlow:
    """
    Threat flow data for Sankey/flow diagram.
    
    Shows threat progression through detection,
    analysis, response, and resolution stages.
    """
    timestamp: float
    nodes: List[ThreatFlowNode]
    edges: List[ThreatFlowEdge]
    total_threats: int
    window_sec: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "nodes": [
                {
                    "id": n.node_id,
                    "type": n.node_type,
                    "label": n.label,
                    "count": n.count,
                    "latency_ms": n.avg_latency_ms,
                    "status": n.status,
                }
                for n in self.nodes
            ],
            "edges": [
                {
                    "source": e.source_id,
                    "target": e.target_id,
                    "count": e.count,
                    "latency_ms": e.avg_latency_ms,
                }
                for e in self.edges
            ],
            "total": self.total_threats,
            "window_sec": self.window_sec,
        }
    
    def to_dashboard_event(self) -> DashboardEvent:
        return DashboardEvent(
            event_type=DashboardEventType.THREAT_FLOW,
            timestamp=self.timestamp,
            source="threat_tracker",
            data=self.to_dict(),
            priority=7,
        )


# =============================================================================
# Anomaly Correlation Schema
# =============================================================================

@dataclass
class AnomalyCorrelation:
    """
    Correlated anomaly cluster for dashboard.
    
    Groups related anomalies by correlation ID or
    temporal/spatial proximity.
    """
    cluster_id: str
    timestamp: float
    anomalies: List[Dict[str, Any]]
    correlation_strength: float  # 0.0-1.0
    root_cause: Optional[str]
    affected_components: List[str]
    recommended_action: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cluster_id": self.cluster_id,
            "timestamp": self.timestamp,
            "anomalies": self.anomalies,
            "correlation_strength": self.correlation_strength,
            "root_cause": self.root_cause,
            "affected_components": self.affected_components,
            "recommended_action": self.recommended_action,
        }
    
    def to_dashboard_event(self) -> DashboardEvent:
        return DashboardEvent(
            event_type=DashboardEventType.ANOMALY_CORRELATION,
            timestamp=self.timestamp,
            source="anomaly_correlator",
            data=self.to_dict(),
            correlation_id=self.cluster_id,
            priority=9,  # High priority for correlated anomalies
        )


# =============================================================================
# Dashboard Hook Registry
# =============================================================================

DashboardHook = Callable[[DashboardEvent], None]


class DashboardHookRegistry:
    """
    Registry for dashboard event hooks.
    
    Allows dashboard components to subscribe to
    specific event types for real-time updates.
    """
    
    def __init__(self, buffer_size: int = 1000):
        self._hooks: Dict[DashboardEventType, List[DashboardHook]] = {}
        self._global_hooks: List[DashboardHook] = []
        self._buffer: deque[DashboardEvent] = deque(maxlen=buffer_size)
        self._lock = threading.Lock()
    
    def register(
        self,
        event_type: Optional[DashboardEventType],
        hook: DashboardHook,
    ) -> None:
        """
        Register a dashboard hook.
        
        Args:
            event_type: Event type to hook, or None for all events
            hook: Callback function
        """
        with self._lock:
            if event_type is None:
                self._global_hooks.append(hook)
            else:
                if event_type not in self._hooks:
                    self._hooks[event_type] = []
                self._hooks[event_type].append(hook)
    
    def unregister(
        self,
        event_type: Optional[DashboardEventType],
        hook: DashboardHook,
    ) -> None:
        """Unregister a dashboard hook."""
        with self._lock:
            if event_type is None:
                if hook in self._global_hooks:
                    self._global_hooks.remove(hook)
            else:
                if event_type in self._hooks and hook in self._hooks[event_type]:
                    self._hooks[event_type].remove(hook)
    
    def emit(self, event: DashboardEvent) -> None:
        """
        Emit event to registered hooks.
        
        Also buffers event for late subscribers.
        """
        with self._lock:
            self._buffer.append(event)
            
            # Call type-specific hooks
            hooks = self._hooks.get(event.event_type, [])
            for hook in hooks:
                try:
                    hook(event)
                except Exception:
                    pass  # Don't let hook errors break emission
            
            # Call global hooks
            for hook in self._global_hooks:
                try:
                    hook(event)
                except Exception:
                    pass
    
    def get_recent(
        self,
        event_type: Optional[DashboardEventType] = None,
        count: int = 100,
    ) -> List[DashboardEvent]:
        """Get recent buffered events."""
        with self._lock:
            events = list(self._buffer)
            
            if event_type:
                events = [e for e in events if e.event_type == event_type]
            
            return events[-count:]
    
    def clear_buffer(self) -> None:
        """Clear event buffer."""
        with self._lock:
            self._buffer.clear()


# =============================================================================
# Global Registry Instance
# =============================================================================

_global_registry: Optional[DashboardHookRegistry] = None


def get_dashboard_registry() -> DashboardHookRegistry:
    """Get or create global dashboard hook registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = DashboardHookRegistry()
    return _global_registry


# =============================================================================
# Convenience Emission Functions
# =============================================================================

def emit_dls_update(
    dls_score: float,
    components: Dict[str, float],
    tier: str,
    trend: str = "stable",
) -> None:
    """Emit DLS update to dashboard."""
    status = (
        "critical" if dls_score < 60 else
        "warning" if dls_score < 75 else
        "healthy" if dls_score >= 85 else
        "degraded"
    )
    
    snapshot = DLSSnapshot(
        timestamp=time.time(),
        dls_score=dls_score,
        components=components,
        status=status,
        tier=tier,
        trend=trend,
    )
    
    get_dashboard_registry().emit(snapshot.to_dashboard_event())


def emit_enforcement_event(
    tier: str,
    action: str,
    target: str,
    result: str,
    latency_ms: float,
) -> None:
    """Emit enforcement event to dashboard."""
    event = DashboardEvent(
        event_type=DashboardEventType.ENFORCEMENT_DECISION,
        timestamp=time.time(),
        source="enforcement_engine",
        data={
            "tier": tier,
            "action": action,
            "target": target,
            "result": result,
            "latency_ms": latency_ms,
        },
        tier=tier,
        priority=6,
    )
    
    get_dashboard_registry().emit(event)


def emit_threat_detected(
    threat_type: str,
    severity: float,
    source: str,
    details: Dict[str, Any],
    correlation_id: Optional[str] = None,
) -> None:
    """Emit threat detection to dashboard."""
    event = DashboardEvent(
        event_type=DashboardEventType.THREAT_DETECTED,
        timestamp=time.time(),
        source=source,
        data={
            "threat_type": threat_type,
            "severity": severity,
            **details,
        },
        correlation_id=correlation_id,
        priority=9 if severity > 0.7 else 7,
    )
    
    get_dashboard_registry().emit(event)


def emit_budget_violation(
    budget_name: str,
    duration_ms: float,
    threshold_ms: float,
    severity: str,
) -> None:
    """Emit budget violation to dashboard."""
    event = DashboardEvent(
        event_type=DashboardEventType.BUDGET_VIOLATION,
        timestamp=time.time(),
        source="budget_enforcer",
        data={
            "budget": budget_name,
            "duration_ms": duration_ms,
            "threshold_ms": threshold_ms,
            "severity": severity,
            "exceeded_by_ms": duration_ms - threshold_ms,
        },
        priority=8 if severity == "critical" else 6,
    )
    
    get_dashboard_registry().emit(event)


def emit_system_health(
    component: str,
    status: str,
    metrics: Dict[str, float],
) -> None:
    """Emit system health status to dashboard."""
    event = DashboardEvent(
        event_type=DashboardEventType.SYSTEM_HEALTH,
        timestamp=time.time(),
        source=component,
        data={
            "status": status,
            "metrics": metrics,
        },
        priority=4,
    )
    
    get_dashboard_registry().emit(event)
