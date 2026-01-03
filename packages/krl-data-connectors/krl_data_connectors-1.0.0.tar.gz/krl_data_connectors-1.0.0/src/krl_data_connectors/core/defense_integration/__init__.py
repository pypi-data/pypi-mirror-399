"""
Defense Integration Package

Week 16: Defense Integration & System Hardening
Week 17: ML-driven Enforcement & Self-Healing Loop

Unified defense coordination, API hardening, monitoring, system hardening,
and explicit ML→Enforcement→Self-Healing closed loop.
"""

from .defense_coordinator import (
    DefenseLevel,
    ThreatDomain,
    ResponseAction,
    ThreatEvent,
    DefenseResponse,
    DefenseSubsystem,
    ThreatCorrelationEngine,
    DefenseLevelManager,
    ResponseExecutor,
    CoordinatorConfig,
    DefenseCoordinator,
    create_coordinator,
    create_threat_event,
)

from .api_hardening import (
    SecurityLevel,
    ValidationResult,
    RateLimitConfig,
    RateLimiter,
    InputValidator,
    AuditEntry,
    AuditLogger,
    RequestSigner,
    EndpointConfig,
    APIHardener,
    harden_endpoint,
    create_hardener,
)

from .security_monitoring import (
    AlertSeverity,
    MetricType,
    Alert,
    Metric,
    AlertHandler,
    LogAlertHandler,
    WebhookAlertHandler,
    CallbackAlertHandler,
    AlertRule,
    SecurityMonitor,
    SecurityDashboard,
    create_monitor,
)

from .system_hardening import (
    HardeningLevel,
    ProtectionType,
    SecurityConfig,
    SecureKeyManager,
    SecureSession,
    IntegrityChecker,
    ProtectionCheck,
    RuntimeProtection,
    SystemHardener,
    secure_function,
    create_hardener as create_system_hardener,
    create_key_manager,
    create_session_manager,
)

from .integration_layer import (
    IntegrationStatus,
    ComponentInfo,
    MessageBus,
    IntegrationBridge,
    ThreatResponseBridge,
    MLDefenseBridge,
    LicenseProtectionBridge,
    IntegrationConfig,
    IntegrationLayer,
    UnifiedDefenseSystem,
    create_integration_layer,
    create_unified_defense,
)

from .ml_enforcement_loop import (
    # Enums
    EnforcementState,
    HealingStrategy,
    ThreatResolutionCriteria,
    EnforcementTier,
    TIER_ESCALATION,
    TIER_DEESCALATION,
    # Data classes
    MLSignal,
    EnforcementAction,
    HealingRecord,
    LoopMetrics,
    EnforcementLoopConfig,
    # Components
    SignalAggregator,
    TierResolver,
    EnforcementExecutor,
    DefaultEnforcementExecutor,
    ResolutionEvaluator,
    SelfHealingEngine,
    MLEnforcementLoop,
    DefenseCoordinatorAdapter,
    # Factory functions
    create_enforcement_loop,
    create_ml_signal,
)

__all__ = [
    # Defense Coordinator
    "DefenseLevel",
    "ThreatDomain",
    "ResponseAction",
    "ThreatEvent",
    "DefenseResponse",
    "DefenseSubsystem",
    "ThreatCorrelationEngine",
    "DefenseLevelManager",
    "ResponseExecutor",
    "CoordinatorConfig",
    "DefenseCoordinator",
    "create_coordinator",
    "create_threat_event",
    
    # API Hardening
    "SecurityLevel",
    "ValidationResult",
    "RateLimitConfig",
    "RateLimiter",
    "InputValidator",
    "AuditEntry",
    "AuditLogger",
    "RequestSigner",
    "EndpointConfig",
    "APIHardener",
    "harden_endpoint",
    "create_hardener",
    
    # Security Monitoring
    "AlertSeverity",
    "MetricType",
    "Alert",
    "Metric",
    "AlertHandler",
    "LogAlertHandler",
    "WebhookAlertHandler",
    "CallbackAlertHandler",
    "AlertRule",
    "SecurityMonitor",
    "SecurityDashboard",
    "create_monitor",
    
    # System Hardening
    "HardeningLevel",
    "ProtectionType",
    "SecurityConfig",
    "SecureKeyManager",
    "SecureSession",
    "IntegrityChecker",
    "ProtectionCheck",
    "RuntimeProtection",
    "SystemHardener",
    "secure_function",
    "create_system_hardener",
    "create_key_manager",
    "create_session_manager",
    
    # Integration Layer
    "IntegrationStatus",
    "ComponentInfo",
    "MessageBus",
    "IntegrationBridge",
    "ThreatResponseBridge",
    "MLDefenseBridge",
    "LicenseProtectionBridge",
    "IntegrationConfig",
    "IntegrationLayer",
    "UnifiedDefenseSystem",
    "create_integration_layer",
    "create_unified_defense",
    
    # ML Enforcement Loop (Week 17)
    "EnforcementState",
    "HealingStrategy",
    "ThreatResolutionCriteria",
    "EnforcementTier",
    "TIER_ESCALATION",
    "TIER_DEESCALATION",
    "MLSignal",
    "EnforcementAction",
    "HealingRecord",
    "LoopMetrics",
    "EnforcementLoopConfig",
    "SignalAggregator",
    "TierResolver",
    "EnforcementExecutor",
    "DefaultEnforcementExecutor",
    "ResolutionEvaluator",
    "SelfHealingEngine",
    "MLEnforcementLoop",
    "DefenseCoordinatorAdapter",
    "create_enforcement_loop",
    "create_ml_signal",
]
