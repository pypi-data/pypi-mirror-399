# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
Observability Package - Phase 3 Weeks 18-19

Comprehensive observability infrastructure for the defense system:
- Defense metrics collection with performance budgets
- Structured JSON logging with defense channels
- Telemetry ingestion and correlation
- Real-time DLS (Defense Liveness Score) calculation
- Runtime budget enforcement with alerts
- Tier-aware routing and weighted DLS
- Dashboard integration hooks
- Threat flow visualization (Week 19)
- Enforcement heatmap tracking (Week 19)
- Anomaly correlation engine (Week 19)

This package provides the "eyes" of the defense system - you can't
optimize what you can't see.

Components:
    Week 18 (Core):
        metric_types.py - Counter, Gauge, Histogram, Summary
        metrics_collector.py - DefenseMetrics with 20+ pre-defined metrics
        log_channels.py - Defense-specific logging channels
        structured_logger.py - JSON structured logging with HMAC signing
        telemetry_ingestion.py - Real-time event ingestion and DLS scoring
    
    Week 18 (Refinements):
        budget_enforcement.py - Runtime budget checks with alerts
        tier_aware.py - Tier-specific routing and DLS weights
        dashboard_hooks.py - Dashboard integration schemas
    
    Week 19 (Dashboard & Correlation):
        threat_flow.py - Threat pipeline visualization
        enforcement_heatmap.py - 2D enforcement activity heatmap
        correlation_engine.py - Anomaly correlation and root cause analysis
"""

# Metric types with performance budget support
from .metric_types import (
    Counter,
    Gauge,
    Histogram,
    Summary,
    MetricValue,
    LabelSet,
)

# Defense metrics collector
from .metrics_collector import (
    DefenseMetrics,
    MetricBuffer,
    SamplingStrategy,
)

# Structured logging
from .structured_logger import (
    StructuredLogger,
    LogEntry,
    LogSeverity,
    get_logger,
    log_defense_event,
    correlation_scope,
    get_correlation_id,
    set_correlation_id,
    sign_log_entry,
    verify_log_signature,
)

# Log channels
from .log_channels import (
    LogChannel,
    LogChannelType,
    ChannelLogger,
    DEFENSE_LOG_CHANNELS,
    get_channel_logger,
    get_audit_channels,
    get_sensitive_channels,
    get_channels_by_prefix,
)

# Telemetry ingestion
from .telemetry_ingestion import (
    TelemetryEvent,
    TelemetryEventType,
    TelemetryIngestion,
    TelemetrySink,
    MemorySink,
    FileSink,
    CallbackSink,
    EventCorrelator,
    DLSScorer,
    get_global_ingestion,
    emit_event,
)

# Budget enforcement (Week 18 Refinement)
from .budget_enforcement import (
    # Budget definitions
    PerformanceBudget,
    BudgetSeverity,
    BudgetViolation,
    PERFORMANCE_BUDGETS,
    BUDGET_ML_INFERENCE_MS,
    BUDGET_ENFORCEMENT_LOOP_MS,
    BUDGET_TELEMETRY_BATCH_MS,
    BUDGET_CROWN_JEWEL_MS,
    # Budget tracking
    BudgetTracker,
    get_global_tracker,
    register_violation_handler,
    # Decorators and context managers
    track_budget,
    BudgetScope,
    AsyncBudgetScope,
    # Async correlation
    AsyncCorrelationScope,
    correlation_id_var,
    tenant_id_var,
    tier_var,
    get_async_correlation_id,
    set_async_correlation_id,
    get_async_tenant_id,
    set_async_tenant_id,
    get_async_tier,
    set_async_tier,
)

# Tier-aware observability (Week 18 Refinement)
from .tier_aware import (
    Tier,
    TierConfig,
    TIER_CONFIGS,
    get_tier_config,
    get_tier_from_string,
    # Tier-specific channel/event sets
    ESSENTIAL_CHANNELS,
    ESSENTIAL_EVENTS,
    PRO_CHANNELS,
    PRO_EVENTS,
    ENTERPRISE_CHANNELS,
    ENTERPRISE_EVENTS,
    # Tiered DLS
    TieredDLSScorer,
    COMMUNITY_DLS_WEIGHTS,
    PRO_DLS_WEIGHTS,
    ENTERPRISE_DLS_WEIGHTS,
    # Tier routing
    TierAwareRouter,
    get_global_router,
    set_default_tier,
)

# Dashboard hooks (Week 18 Refinement)
from .dashboard_hooks import (
    DashboardEventType,
    DashboardEvent,
    DLSSnapshot,
    EnforcementHeatmap,
    EnforcementHeatmapCell,
    ThreatFlow,
    ThreatFlowNode,
    ThreatFlowEdge,
    AnomalyCorrelation,
    DashboardHookRegistry,
    get_dashboard_registry,
    # Convenience emitters
    emit_dls_update,
    emit_enforcement_event,
    emit_threat_detected,
    emit_budget_violation,
    emit_system_health,
)

# Threat flow visualization (Week 19)
from .threat_flow import (
    ThreatStage,
    ThreatRecord,
    ThreatFlowTracker,
    get_threat_flow_tracker,
    track_threat,
    transition_threat,
    detect_threat,
    analyze_threat,
    respond_to_threat,
    resolve_threat,
    threat_escaped,
)

# Enforcement heatmap (Week 19)
from .enforcement_heatmap import (
    EnforcementAction,
    HeatmapCellData,
    EnforcementHeatmapTracker,
    TierActionHeatmap,
    TenantActionHeatmap,
    SourceTargetHeatmap,
    get_enforcement_heatmap,
    record_enforcement,
    emit_heatmap_snapshot,
)

# Correlation engine (Week 19)
from .correlation_engine import (
    CorrelationType,
    CorrelationRule,
    CorrelationCluster,
    CorrelationEngine,
    BUILT_IN_RULES,
    get_correlation_engine,
    correlate_event,
    get_active_correlations,
    analyze_tenant_correlations,
)


__all__ = [
    # Metric types
    "Counter",
    "Gauge",
    "Histogram",
    "Summary",
    "MetricValue",
    "LabelSet",
    # Metrics collector
    "DefenseMetrics",
    "MetricBuffer",
    "SamplingStrategy",
    # Structured logging
    "StructuredLogger",
    "LogEntry",
    "LogSeverity",
    "get_logger",
    "log_defense_event",
    "correlation_scope",
    "get_correlation_id",
    "set_correlation_id",
    "sign_log_entry",
    "verify_log_signature",
    # Log channels
    "LogChannel",
    "LogChannelType",
    "ChannelLogger",
    "DEFENSE_LOG_CHANNELS",
    "get_channel_logger",
    "get_audit_channels",
    "get_sensitive_channels",
    "get_channels_by_prefix",
    # Telemetry ingestion
    "TelemetryEvent",
    "TelemetryEventType",
    "TelemetryIngestion",
    "TelemetrySink",
    "MemorySink",
    "FileSink",
    "CallbackSink",
    "EventCorrelator",
    "DLSScorer",
    "get_global_ingestion",
    "emit_event",
    # Budget enforcement
    "PerformanceBudget",
    "BudgetSeverity",
    "BudgetViolation",
    "PERFORMANCE_BUDGETS",
    "BUDGET_ML_INFERENCE_MS",
    "BUDGET_ENFORCEMENT_LOOP_MS",
    "BUDGET_TELEMETRY_BATCH_MS",
    "BUDGET_CROWN_JEWEL_MS",
    "BudgetTracker",
    "get_global_tracker",
    "register_violation_handler",
    "track_budget",
    "BudgetScope",
    "AsyncBudgetScope",
    # Async correlation
    "AsyncCorrelationScope",
    "correlation_id_var",
    "tenant_id_var",
    "tier_var",
    "get_async_correlation_id",
    "set_async_correlation_id",
    "get_async_tenant_id",
    "set_async_tenant_id",
    "get_async_tier",
    "set_async_tier",
    # Tier-aware
    "Tier",
    "TierConfig",
    "TIER_CONFIGS",
    "get_tier_config",
    "get_tier_from_string",
    "ESSENTIAL_CHANNELS",
    "ESSENTIAL_EVENTS",
    "PRO_CHANNELS",
    "PRO_EVENTS",
    "ENTERPRISE_CHANNELS",
    "ENTERPRISE_EVENTS",
    "TieredDLSScorer",
    "COMMUNITY_DLS_WEIGHTS",
    "PRO_DLS_WEIGHTS",
    "ENTERPRISE_DLS_WEIGHTS",
    "TierAwareRouter",
    "get_global_router",
    "set_default_tier",
    # Dashboard hooks
    "DashboardEventType",
    "DashboardEvent",
    "DLSSnapshot",
    "EnforcementHeatmap",
    "EnforcementHeatmapCell",
    "ThreatFlow",
    "ThreatFlowNode",
    "ThreatFlowEdge",
    "AnomalyCorrelation",
    "DashboardHookRegistry",
    "get_dashboard_registry",
    "emit_dls_update",
    "emit_enforcement_event",
    "emit_threat_detected",
    "emit_budget_violation",
    "emit_system_health",
    # Threat flow (Week 19)
    "ThreatStage",
    "ThreatRecord",
    "ThreatFlowTracker",
    "get_threat_flow_tracker",
    "track_threat",
    "transition_threat",
    "detect_threat",
    "analyze_threat",
    "respond_to_threat",
    "resolve_threat",
    "threat_escaped",
    # Enforcement heatmap (Week 19)
    "EnforcementAction",
    "HeatmapCellData",
    "EnforcementHeatmapTracker",
    "TierActionHeatmap",
    "TenantActionHeatmap",
    "SourceTargetHeatmap",
    "get_enforcement_heatmap",
    "record_enforcement",
    "emit_heatmap_snapshot",
    # Correlation engine (Week 19)
    "CorrelationType",
    "CorrelationRule",
    "CorrelationCluster",
    "CorrelationEngine",
    "BUILT_IN_RULES",
    "get_correlation_engine",
    "correlate_event",
    "get_active_correlations",
    "analyze_tenant_correlations",
]
