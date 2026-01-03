# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Enforcement Heatmap - Phase 3 Week 19

Real-time enforcement activity visualization as a 2D heatmap.
Tracks enforcement patterns across configurable dimensions.

Default Dimensions:
- X-axis: Tier (community, pro, enterprise)
- Y-axis: Action (allow, warn, throttle, block, quarantine)

Features:
- Time-windowed aggregation
- Intensity normalization
- Spike detection
- Multi-tenant support
- Dashboard integration
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from .dashboard_hooks import (
    EnforcementHeatmap,
    EnforcementHeatmapCell,
    DashboardEvent,
    DashboardEventType,
    get_dashboard_registry,
)
from .tier_aware import Tier


# =============================================================================
# Enforcement Actions
# =============================================================================

class EnforcementAction(Enum):
    """Types of enforcement actions."""
    
    ALLOW = "allow"
    WARN = "warn"
    THROTTLE = "throttle"
    BLOCK = "block"
    QUARANTINE = "quarantine"
    DEGRADE = "degrade"
    ESCALATE = "escalate"


# Action severity for intensity calculation
ACTION_SEVERITY: Dict[EnforcementAction, float] = {
    EnforcementAction.ALLOW: 0.0,
    EnforcementAction.WARN: 0.2,
    EnforcementAction.THROTTLE: 0.4,
    EnforcementAction.DEGRADE: 0.5,
    EnforcementAction.BLOCK: 0.7,
    EnforcementAction.QUARANTINE: 0.9,
    EnforcementAction.ESCALATE: 1.0,
}


# =============================================================================
# Heatmap Cell Data
# =============================================================================

@dataclass
class HeatmapCellData:
    """
    Internal tracking data for a heatmap cell.
    
    Tracks counts and timestamps for windowed aggregation.
    """
    dimension_x: str
    dimension_y: str
    value_x: str
    value_y: str
    
    # Event timestamps for windowing
    events: List[float] = field(default_factory=list)
    
    # Severity-weighted score
    severity_sum: float = 0.0
    
    def add_event(self, timestamp: float, severity: float = 0.5) -> None:
        """Add an event to this cell."""
        self.events.append(timestamp)
        self.severity_sum += severity
    
    def get_windowed_count(self, window_sec: float) -> int:
        """Get count of events within the time window."""
        cutoff = time.time() - window_sec
        return sum(1 for ts in self.events if ts >= cutoff)
    
    def prune_old(self, window_sec: float) -> None:
        """Remove events older than the window."""
        cutoff = time.time() - window_sec
        old_count = len(self.events)
        self.events = [ts for ts in self.events if ts >= cutoff]
        
        # Proportionally reduce severity sum
        if old_count > 0:
            ratio = len(self.events) / old_count
            self.severity_sum *= ratio
    
    def get_intensity(self, max_count: int, window_sec: float) -> float:
        """Calculate intensity (0.0-1.0) based on count and severity."""
        count = self.get_windowed_count(window_sec)
        if count == 0 or max_count == 0:
            return 0.0
        
        # Combine count ratio with average severity
        count_intensity = min(1.0, count / max_count)
        avg_severity = self.severity_sum / len(self.events) if self.events else 0.5
        
        # Weighted combination
        return 0.6 * count_intensity + 0.4 * avg_severity


# =============================================================================
# Enforcement Heatmap Tracker
# =============================================================================

class EnforcementHeatmapTracker:
    """
    Tracks enforcement activity for heatmap visualization.
    
    Aggregates enforcement events across two configurable dimensions.
    """
    
    def __init__(
        self,
        dimension_x: str = "tier",
        dimension_y: str = "action",
        window_sec: float = 300.0,
        spike_threshold: float = 2.0,
        emit_to_dashboard: bool = True,
    ):
        """
        Initialize heatmap tracker.
        
        Args:
            dimension_x: X-axis dimension name
            dimension_y: Y-axis dimension name
            window_sec: Time window for aggregation
            spike_threshold: Multiplier for spike detection (vs baseline)
            emit_to_dashboard: Auto-emit to dashboard hooks
        """
        self._dimension_x = dimension_x
        self._dimension_y = dimension_y
        self._window_sec = window_sec
        self._spike_threshold = spike_threshold
        self._emit_to_dashboard = emit_to_dashboard
        
        # Cell data: (value_x, value_y) -> HeatmapCellData
        self._cells: Dict[Tuple[str, str], HeatmapCellData] = {}
        
        # Track baseline for spike detection
        self._baseline_counts: Dict[Tuple[str, str], float] = defaultdict(float)
        self._baseline_window_count = 0
        
        # Lock for thread safety
        self._lock = threading.Lock()
        
        # Statistics
        self._total_events = 0
        self._last_prune = time.time()
    
    def record_enforcement(
        self,
        value_x: str,
        value_y: str,
        severity: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record an enforcement event.
        
        Args:
            value_x: X-dimension value (e.g., "community")
            value_y: Y-dimension value (e.g., "throttle")
            severity: Event severity 0.0-1.0
            metadata: Additional event metadata
        """
        now = time.time()
        key = (value_x, value_y)
        
        with self._lock:
            # Get or create cell
            if key not in self._cells:
                self._cells[key] = HeatmapCellData(
                    dimension_x=self._dimension_x,
                    dimension_y=self._dimension_y,
                    value_x=value_x,
                    value_y=value_y,
                )
            
            cell = self._cells[key]
            cell.add_event(now, severity)
            self._total_events += 1
            
            # Check for spike
            if self._emit_to_dashboard:
                self._check_and_emit_spike(cell, metadata)
            
            # Periodic pruning
            if now - self._last_prune > self._window_sec / 10:
                self._prune_all()
                self._last_prune = now
    
    def record_tier_action(
        self,
        tier: Tier,
        action: EnforcementAction,
        target: Optional[str] = None,
        **metadata: Any,
    ) -> None:
        """
        Convenience method for tier x action heatmap.
        
        Args:
            tier: The tier (community/pro/enterprise)
            action: The enforcement action
            target: Optional target identifier
            **metadata: Additional metadata
        """
        severity = ACTION_SEVERITY.get(action, 0.5)
        
        self.record_enforcement(
            value_x=tier.value,
            value_y=action.value,
            severity=severity,
            metadata={"target": target, **metadata} if target else metadata or None,
        )
    
    def generate_heatmap(self) -> EnforcementHeatmap:
        """
        Generate EnforcementHeatmap snapshot for dashboard.
        """
        with self._lock:
            now = time.time()
            
            # Find max count for intensity normalization
            max_count = max(
                (cell.get_windowed_count(self._window_sec) for cell in self._cells.values()),
                default=1
            )
            
            # Build cells
            cells = []
            total = 0
            
            for (value_x, value_y), cell_data in self._cells.items():
                count = cell_data.get_windowed_count(self._window_sec)
                if count == 0:
                    continue
                
                total += count
                intensity = cell_data.get_intensity(max_count, self._window_sec)
                
                cells.append(EnforcementHeatmapCell(
                    dimension_x=self._dimension_x,
                    dimension_y=self._dimension_y,
                    value_x=value_x,
                    value_y=value_y,
                    count=count,
                    intensity=intensity,
                    last_update=now,
                ))
            
            return EnforcementHeatmap(
                timestamp=now,
                dimension_x=self._dimension_x,
                dimension_y=self._dimension_y,
                cells=cells,
                total_enforcements=total,
                window_sec=self._window_sec,
            )
    
    def emit_heatmap(self) -> None:
        """Generate and emit heatmap to dashboard."""
        heatmap = self.generate_heatmap()
        get_dashboard_registry().emit(heatmap.to_dashboard_event())
    
    def get_cell_count(self, value_x: str, value_y: str) -> int:
        """Get current count for a specific cell."""
        with self._lock:
            cell = self._cells.get((value_x, value_y))
            if cell:
                return cell.get_windowed_count(self._window_sec)
            return 0
    
    def get_row_totals(self) -> Dict[str, int]:
        """Get total counts per X-dimension value."""
        with self._lock:
            totals: Dict[str, int] = defaultdict(int)
            for (value_x, _), cell in self._cells.items():
                totals[value_x] += cell.get_windowed_count(self._window_sec)
            return dict(totals)
    
    def get_column_totals(self) -> Dict[str, int]:
        """Get total counts per Y-dimension value."""
        with self._lock:
            totals: Dict[str, int] = defaultdict(int)
            for (_, value_y), cell in self._cells.items():
                totals[value_y] += cell.get_windowed_count(self._window_sec)
            return dict(totals)
    
    def get_hotspots(self, top_n: int = 5) -> List[Tuple[str, str, int]]:
        """Get top N cells by count."""
        with self._lock:
            cell_counts = [
                (value_x, value_y, cell.get_windowed_count(self._window_sec))
                for (value_x, value_y), cell in self._cells.items()
            ]
            cell_counts.sort(key=lambda x: x[2], reverse=True)
            return cell_counts[:top_n]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tracker statistics."""
        with self._lock:
            return {
                "dimension_x": self._dimension_x,
                "dimension_y": self._dimension_y,
                "window_sec": self._window_sec,
                "total_events": self._total_events,
                "active_cells": len(self._cells),
                "row_totals": self.get_row_totals(),
                "column_totals": self.get_column_totals(),
                "hotspots": self.get_hotspots(3),
            }
    
    def update_baseline(self) -> None:
        """
        Update baseline counts for spike detection.
        
        Should be called periodically (e.g., hourly).
        """
        with self._lock:
            for key, cell in self._cells.items():
                current = cell.get_windowed_count(self._window_sec)
                # Exponential moving average
                alpha = 0.3
                self._baseline_counts[key] = (
                    alpha * current +
                    (1 - alpha) * self._baseline_counts[key]
                )
            self._baseline_window_count += 1
    
    def _check_and_emit_spike(
        self,
        cell: HeatmapCellData,
        metadata: Optional[Dict[str, Any]],
    ) -> None:
        """Check for spike and emit event if detected."""
        key = (cell.value_x, cell.value_y)
        current = cell.get_windowed_count(self._window_sec)
        baseline = self._baseline_counts.get(key, 10)  # Default baseline
        
        # Need some baseline data before detecting spikes
        if self._baseline_window_count < 3:
            return
        
        if current > baseline * self._spike_threshold:
            event = DashboardEvent(
                event_type=DashboardEventType.ENFORCEMENT_SPIKE,
                timestamp=time.time(),
                source="enforcement_heatmap",
                data={
                    self._dimension_x: cell.value_x,
                    self._dimension_y: cell.value_y,
                    "current_count": current,
                    "baseline_count": baseline,
                    "spike_ratio": current / baseline if baseline > 0 else float("inf"),
                    "metadata": metadata,
                },
                priority=8,
            )
            get_dashboard_registry().emit(event)
    
    def _prune_all(self) -> None:
        """Prune old events from all cells."""
        for cell in self._cells.values():
            cell.prune_old(self._window_sec)


# =============================================================================
# Specialized Heatmap Trackers
# =============================================================================

class TierActionHeatmap(EnforcementHeatmapTracker):
    """
    Pre-configured heatmap for Tier × Action analysis.
    
    Standard dimensions for monetization-focused enforcement tracking.
    """
    
    def __init__(self, **kwargs: Any):
        super().__init__(
            dimension_x="tier",
            dimension_y="action",
            **kwargs,
        )
    
    def record(
        self,
        tier: Tier,
        action: EnforcementAction,
        **metadata: Any,
    ) -> None:
        """Record a tier/action enforcement event."""
        self.record_tier_action(tier, action, **metadata)


class TenantActionHeatmap(EnforcementHeatmapTracker):
    """
    Pre-configured heatmap for Tenant × Action analysis.
    
    Useful for identifying problematic tenants.
    """
    
    def __init__(self, **kwargs: Any):
        super().__init__(
            dimension_x="tenant",
            dimension_y="action",
            **kwargs,
        )
    
    def record(
        self,
        tenant_id: str,
        action: EnforcementAction,
        **metadata: Any,
    ) -> None:
        """Record a tenant/action enforcement event."""
        severity = ACTION_SEVERITY.get(action, 0.5)
        self.record_enforcement(
            value_x=tenant_id,
            value_y=action.value,
            severity=severity,
            metadata=metadata or None,
        )


class SourceTargetHeatmap(EnforcementHeatmapTracker):
    """
    Pre-configured heatmap for Source × Target analysis.
    
    Useful for identifying attack patterns.
    """
    
    def __init__(self, **kwargs: Any):
        super().__init__(
            dimension_x="source",
            dimension_y="target",
            **kwargs,
        )
    
    def record(
        self,
        source: str,
        target: str,
        severity: float = 0.5,
        **metadata: Any,
    ) -> None:
        """Record a source/target event."""
        self.record_enforcement(
            value_x=source,
            value_y=target,
            severity=severity,
            metadata=metadata or None,
        )


# =============================================================================
# Global Tracker Instance
# =============================================================================

_global_tracker: Optional[TierActionHeatmap] = None


def get_enforcement_heatmap() -> TierActionHeatmap:
    """Get or create global tier×action enforcement heatmap."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = TierActionHeatmap()
    return _global_tracker


# =============================================================================
# Convenience Functions
# =============================================================================

def record_enforcement(
    tier: Tier,
    action: EnforcementAction,
    target: Optional[str] = None,
    **metadata: Any,
) -> None:
    """Record an enforcement event to global heatmap."""
    get_enforcement_heatmap().record_tier_action(tier, action, target, **metadata)


def emit_heatmap_snapshot() -> None:
    """Emit current heatmap to dashboard."""
    get_enforcement_heatmap().emit_heatmap()
