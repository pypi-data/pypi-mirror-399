# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Threat Flow Visualization - Phase 3 Week 19

Real-time threat flow tracking for Sankey/flow diagram visualization.
Tracks threats through detection → analysis → response → resolution stages.

Features:
- Stage-based flow tracking (5 stages)
- Latency measurement between stages
- Automatic node/edge aggregation
- Time-windowed snapshots
- Integration with dashboard hooks
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import uuid

from .dashboard_hooks import (
    ThreatFlow,
    ThreatFlowNode,
    ThreatFlowEdge,
    DashboardEvent,
    DashboardEventType,
    get_dashboard_registry,
)
from .telemetry_ingestion import TelemetryEvent, TelemetryEventType


# =============================================================================
# Threat Flow Stages
# =============================================================================

class ThreatStage(Enum):
    """Stages in the threat detection/response pipeline."""
    
    INGESTION = "ingestion"       # Raw event received
    DETECTION = "detection"       # Threat detected by ML/rules
    ANALYSIS = "analysis"         # Threat analyzed for severity
    RESPONSE = "response"         # Response action initiated
    RESOLUTION = "resolution"     # Threat mitigated/resolved
    ESCAPED = "escaped"           # Threat escaped detection


# Stage display labels
STAGE_LABELS = {
    ThreatStage.INGESTION: "Event Ingestion",
    ThreatStage.DETECTION: "Threat Detection",
    ThreatStage.ANALYSIS: "Threat Analysis",
    ThreatStage.RESPONSE: "Response Action",
    ThreatStage.RESOLUTION: "Resolution",
    ThreatStage.ESCAPED: "Escaped",
}

# Valid stage transitions
VALID_TRANSITIONS: Dict[ThreatStage, Set[ThreatStage]] = {
    ThreatStage.INGESTION: {ThreatStage.DETECTION, ThreatStage.ESCAPED},
    ThreatStage.DETECTION: {ThreatStage.ANALYSIS, ThreatStage.ESCAPED},
    ThreatStage.ANALYSIS: {ThreatStage.RESPONSE, ThreatStage.ESCAPED},
    ThreatStage.RESPONSE: {ThreatStage.RESOLUTION, ThreatStage.ESCAPED},
    ThreatStage.RESOLUTION: set(),
    ThreatStage.ESCAPED: set(),
}


# =============================================================================
# Threat Record
# =============================================================================

@dataclass
class ThreatRecord:
    """
    Record of a single threat flowing through the pipeline.
    
    Tracks stage transitions with timestamps for latency calculation.
    """
    threat_id: str
    correlation_id: Optional[str]
    threat_type: str
    severity: float
    source: str
    tenant_id: Optional[str]
    tier: Optional[str]
    
    # Stage tracking
    current_stage: ThreatStage = ThreatStage.INGESTION
    stage_timestamps: Dict[ThreatStage, float] = field(default_factory=dict)
    stage_metadata: Dict[ThreatStage, Dict[str, Any]] = field(default_factory=dict)
    
    # Outcome
    resolved: bool = False
    escaped: bool = False
    resolution_action: Optional[str] = None
    
    created_at: float = field(default_factory=time.time)
    
    def __post_init__(self):
        # Record initial stage timestamp
        if ThreatStage.INGESTION not in self.stage_timestamps:
            self.stage_timestamps[ThreatStage.INGESTION] = self.created_at
    
    def transition_to(
        self,
        stage: ThreatStage,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Transition threat to a new stage.
        
        Returns True if transition was valid.
        """
        if stage not in VALID_TRANSITIONS.get(self.current_stage, set()):
            return False
        
        now = time.time()
        self.current_stage = stage
        self.stage_timestamps[stage] = now
        
        if metadata:
            self.stage_metadata[stage] = metadata
        
        # Handle terminal states
        if stage == ThreatStage.RESOLUTION:
            self.resolved = True
        elif stage == ThreatStage.ESCAPED:
            self.escaped = True
        
        return True
    
    def get_stage_latency(
        self,
        from_stage: ThreatStage,
        to_stage: ThreatStage,
    ) -> Optional[float]:
        """Get latency in ms between two stages."""
        from_ts = self.stage_timestamps.get(from_stage)
        to_ts = self.stage_timestamps.get(to_stage)
        
        if from_ts is None or to_ts is None:
            return None
        
        return (to_ts - from_ts) * 1000  # Convert to ms
    
    def get_total_latency(self) -> Optional[float]:
        """Get total time from ingestion to resolution/escape."""
        start = self.stage_timestamps.get(ThreatStage.INGESTION)
        
        if self.resolved:
            end = self.stage_timestamps.get(ThreatStage.RESOLUTION)
        elif self.escaped:
            end = self.stage_timestamps.get(ThreatStage.ESCAPED)
        else:
            end = time.time()
        
        if start is None or end is None:
            return None
        
        return (end - start) * 1000
    
    def is_terminal(self) -> bool:
        """Check if threat reached a terminal state."""
        return self.resolved or self.escaped
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "threat_id": self.threat_id,
            "correlation_id": self.correlation_id,
            "threat_type": self.threat_type,
            "severity": self.severity,
            "source": self.source,
            "tenant_id": self.tenant_id,
            "tier": self.tier,
            "current_stage": self.current_stage.value,
            "stages_completed": [s.value for s in self.stage_timestamps.keys()],
            "total_latency_ms": self.get_total_latency(),
            "resolved": self.resolved,
            "escaped": self.escaped,
        }


# =============================================================================
# Threat Flow Tracker
# =============================================================================

class ThreatFlowTracker:
    """
    Tracks threats flowing through the detection/response pipeline.
    
    Aggregates data for Sankey/flow diagram visualization.
    """
    
    def __init__(
        self,
        window_sec: float = 300.0,
        max_active_threats: int = 10_000,
        emit_to_dashboard: bool = True,
    ):
        self._window_sec = window_sec
        self._max_active = max_active_threats
        self._emit_to_dashboard = emit_to_dashboard
        
        # Active threats by ID
        self._threats: Dict[str, ThreatRecord] = {}
        
        # Aggregated flow stats (reset on snapshot)
        self._node_counts: Dict[ThreatStage, int] = defaultdict(int)
        self._node_latencies: Dict[ThreatStage, List[float]] = defaultdict(list)
        self._edge_counts: Dict[Tuple[ThreatStage, ThreatStage], int] = defaultdict(int)
        self._edge_latencies: Dict[Tuple[ThreatStage, ThreatStage], List[float]] = defaultdict(list)
        
        self._lock = threading.Lock()
        self._last_snapshot = time.time()
    
    def create_threat(
        self,
        threat_type: str,
        severity: float,
        source: str,
        correlation_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        tier: Optional[str] = None,
        threat_id: Optional[str] = None,
    ) -> ThreatRecord:
        """
        Create and track a new threat.
        
        Returns the ThreatRecord for subsequent stage transitions.
        """
        threat_id = threat_id or str(uuid.uuid4())
        
        record = ThreatRecord(
            threat_id=threat_id,
            correlation_id=correlation_id,
            threat_type=threat_type,
            severity=severity,
            source=source,
            tenant_id=tenant_id,
            tier=tier,
        )
        
        with self._lock:
            self._threats[threat_id] = record
            self._node_counts[ThreatStage.INGESTION] += 1
            
            # Trim if too many active
            self._prune_old_threats()
        
        return record
    
    def transition_threat(
        self,
        threat_id: str,
        to_stage: ThreatStage,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Transition a threat to a new stage.
        
        Returns True if transition was successful.
        """
        with self._lock:
            record = self._threats.get(threat_id)
            if not record:
                return False
            
            from_stage = record.current_stage
            
            if not record.transition_to(to_stage, metadata):
                return False
            
            # Update aggregates
            self._node_counts[to_stage] += 1
            self._edge_counts[(from_stage, to_stage)] += 1
            
            # Record latency
            latency = record.get_stage_latency(from_stage, to_stage)
            if latency is not None:
                self._edge_latencies[(from_stage, to_stage)].append(latency)
                self._node_latencies[to_stage].append(latency)
            
            # Emit to dashboard
            if self._emit_to_dashboard:
                self._emit_transition_event(record, from_stage, to_stage, latency)
            
            return True
    
    def get_threat(self, threat_id: str) -> Optional[ThreatRecord]:
        """Get a threat record by ID."""
        with self._lock:
            return self._threats.get(threat_id)
    
    def generate_flow_snapshot(self) -> ThreatFlow:
        """
        Generate a ThreatFlow snapshot for dashboard.
        
        Aggregates node and edge data from the current window.
        """
        with self._lock:
            now = time.time()
            
            # Build nodes
            nodes = []
            for stage in ThreatStage:
                count = self._node_counts[stage]
                latencies = self._node_latencies[stage]
                
                avg_latency = (
                    sum(latencies) / len(latencies)
                    if latencies else 0.0
                )
                
                # Determine status based on active threats
                active_in_stage = sum(
                    1 for t in self._threats.values()
                    if t.current_stage == stage and not t.is_terminal()
                )
                
                status = (
                    "active" if active_in_stage > 0 else
                    "idle" if count > 0 else
                    "inactive"
                )
                
                nodes.append(ThreatFlowNode(
                    node_id=stage.value,
                    node_type=self._get_node_type(stage),
                    label=STAGE_LABELS[stage],
                    count=count,
                    avg_latency_ms=avg_latency,
                    status=status,
                ))
            
            # Build edges
            edges = []
            for (from_stage, to_stage), count in self._edge_counts.items():
                if count == 0:
                    continue
                
                latencies = self._edge_latencies[(from_stage, to_stage)]
                avg_latency = (
                    sum(latencies) / len(latencies)
                    if latencies else 0.0
                )
                
                edges.append(ThreatFlowEdge(
                    source_id=from_stage.value,
                    target_id=to_stage.value,
                    count=count,
                    avg_latency_ms=avg_latency,
                ))
            
            # Total threats
            total = self._node_counts[ThreatStage.INGESTION]
            
            flow = ThreatFlow(
                timestamp=now,
                nodes=nodes,
                edges=edges,
                total_threats=total,
                window_sec=self._window_sec,
            )
            
            self._last_snapshot = now
            
            return flow
    
    def emit_flow_snapshot(self) -> None:
        """Generate and emit flow snapshot to dashboard."""
        flow = self.generate_flow_snapshot()
        get_dashboard_registry().emit(flow.to_dashboard_event())
    
    def reset_aggregates(self) -> None:
        """Reset aggregated counts (typically after snapshot)."""
        with self._lock:
            self._node_counts.clear()
            self._node_latencies.clear()
            self._edge_counts.clear()
            self._edge_latencies.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tracker statistics."""
        with self._lock:
            active = sum(
                1 for t in self._threats.values()
                if not t.is_terminal()
            )
            resolved = sum(1 for t in self._threats.values() if t.resolved)
            escaped = sum(1 for t in self._threats.values() if t.escaped)
            
            return {
                "total_tracked": len(self._threats),
                "active": active,
                "resolved": resolved,
                "escaped": escaped,
                "resolution_rate": resolved / len(self._threats) if self._threats else 0,
                "escape_rate": escaped / len(self._threats) if self._threats else 0,
            }
    
    def _prune_old_threats(self) -> None:
        """Remove old terminal threats to limit memory."""
        if len(self._threats) <= self._max_active:
            return
        
        # Sort by creation time, remove oldest terminal
        terminal = [
            (t.created_at, tid)
            for tid, t in self._threats.items()
            if t.is_terminal()
        ]
        terminal.sort()
        
        # Remove oldest 10%
        to_remove = len(terminal) // 10 + 1
        for _, tid in terminal[:to_remove]:
            del self._threats[tid]
    
    def _get_node_type(self, stage: ThreatStage) -> str:
        """Map stage to node type for visualization."""
        mapping = {
            ThreatStage.INGESTION: "input",
            ThreatStage.DETECTION: "detection",
            ThreatStage.ANALYSIS: "analysis",
            ThreatStage.RESPONSE: "response",
            ThreatStage.RESOLUTION: "output",
            ThreatStage.ESCAPED: "error",
        }
        return mapping.get(stage, "unknown")
    
    def _emit_transition_event(
        self,
        record: ThreatRecord,
        from_stage: ThreatStage,
        to_stage: ThreatStage,
        latency_ms: Optional[float],
    ) -> None:
        """Emit stage transition event to dashboard."""
        event = DashboardEvent(
            event_type=DashboardEventType.THREAT_FLOW,
            timestamp=time.time(),
            source="threat_flow_tracker",
            data={
                "threat_id": record.threat_id,
                "threat_type": record.threat_type,
                "severity": record.severity,
                "from_stage": from_stage.value,
                "to_stage": to_stage.value,
                "latency_ms": latency_ms,
                "is_terminal": record.is_terminal(),
            },
            tier=record.tier,
            correlation_id=record.correlation_id,
            priority=8 if record.severity > 0.7 else 5,
        )
        get_dashboard_registry().emit(event)


# =============================================================================
# Global Tracker Instance
# =============================================================================

_global_tracker: Optional[ThreatFlowTracker] = None


def get_threat_flow_tracker() -> ThreatFlowTracker:
    """Get or create global threat flow tracker."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = ThreatFlowTracker()
    return _global_tracker


# =============================================================================
# Convenience Functions
# =============================================================================

def track_threat(
    threat_type: str,
    severity: float,
    source: str,
    **kwargs: Any,
) -> ThreatRecord:
    """Create and track a new threat."""
    return get_threat_flow_tracker().create_threat(
        threat_type=threat_type,
        severity=severity,
        source=source,
        **kwargs,
    )


def transition_threat(
    threat_id: str,
    to_stage: ThreatStage,
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """Transition a threat to a new stage."""
    return get_threat_flow_tracker().transition_threat(
        threat_id=threat_id,
        to_stage=to_stage,
        metadata=metadata,
    )


def detect_threat(threat_id: str, **metadata: Any) -> bool:
    """Mark threat as detected."""
    return transition_threat(threat_id, ThreatStage.DETECTION, metadata or None)


def analyze_threat(threat_id: str, **metadata: Any) -> bool:
    """Mark threat as analyzed."""
    return transition_threat(threat_id, ThreatStage.ANALYSIS, metadata or None)


def respond_to_threat(threat_id: str, **metadata: Any) -> bool:
    """Mark threat as responded to."""
    return transition_threat(threat_id, ThreatStage.RESPONSE, metadata or None)


def resolve_threat(threat_id: str, action: str = "mitigated", **metadata: Any) -> bool:
    """Mark threat as resolved."""
    meta = {"action": action, **(metadata or {})}
    return transition_threat(threat_id, ThreatStage.RESOLUTION, meta)


def threat_escaped(threat_id: str, reason: str = "unknown", **metadata: Any) -> bool:
    """Mark threat as escaped detection."""
    meta = {"reason": reason, **(metadata or {})}
    return transition_threat(threat_id, ThreatStage.ESCAPED, meta)


# Backwards-compatible aliases
ThreatFlowEvent = ThreatRecord
