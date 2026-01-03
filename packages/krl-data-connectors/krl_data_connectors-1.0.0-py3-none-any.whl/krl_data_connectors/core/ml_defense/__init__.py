"""
ML Defense Package for KRL Data Connectors.

Week 15: Machine learning enhanced behavioral analysis and anomaly detection.
Week 20: Federated Model Manager + ML Governance.

Provides ML models for threat detection, pattern learning, risk scoring,
predictive modeling, and tiered ML governance.
"""

# Anomaly Detection
from .anomaly_detection import (
    AnomalyType,
    DetectionMethod,
    Severity,
    FeatureVector,
    Anomaly,
    DetectionResult,
    AnomalyDetector,
    ZScoreDetector,
    IQRDetector,
    MADDetector,
    IsolationForestDetector,
    LocalOutlierFactorDetector,
    EnsembleDetector,
    AnomalyConfig,
    AnomalyDetectionEngine,
)

# Pattern Learning
from .pattern_learning import (
    PatternType,
    PatternConfidence,
    LearningMode,
    Event,
    Pattern,
    PatternMatch,
    SequenceRule,
    PatternLearner,
    TemporalPatternLearner,
    SequencePatternLearner,
    VolumetricPatternLearner,
    CompositePatternLearner,
    PatternLearningConfig,
    PatternLearningEngine,
)

# Risk Scoring
from .risk_scoring import (
    RiskCategory,
    RiskLevel,
    RiskTrend,
    RiskFactor,
    RiskProfile,
    RiskEvent,
    RiskScorer,
    LicenseRiskScorer,
    BehavioralRiskScorer,
    EnvironmentalRiskScorer,
    TemporalRiskScorer,
    VolumetricRiskScorer,
    IdentityRiskScorer,
    RiskScoringConfig,
    RiskScoringEngine,
)

# Predictive Modeling
from .predictive_modeling import (
    PredictionType,
    PredictionConfidence,
    ModelType,
    Observation,
    Prediction,
    PredictionFeedback,
    PredictiveModel,
    MarkovChainModel,
    TimeSeriesPredictor,
    SequencePredictor,
    BayesianPredictor,
    EnsemblePredictor,
    PredictiveConfig,
    PredictiveModelingEngine,
)

# Model Orchestration
from .model_orchestration import (
    DecisionType,
    DecisionPriority,
    ModelStatus,
    ModelInfo,
    Decision,
    ModelVote,
    DecisionStrategy,
    MajorityVoteStrategy,
    ConservativeStrategy,
    WeightedConsensusStrategy,
    ModelRegistry,
    DecisionCache,
    OrchestrationConfig,
    ModelOrchestrator,
    OrchestratorSnapshot,
    create_snapshot,
)

# Federated Model Manager (Week 20)
from .federated_model_manager import (
    # Enums
    ModelTier,
    ModelState,
    GovernanceMode,
    FederatedRole,
    UpdateStrategy,
    AggregationMethod,
    DriftSeverity,
    # Data Classes
    SemanticVersion,
    ModelMetrics,
    DriftMetrics,
    ModelVersion,
    FederatedUpdate,
    FederatedRound,
    TierGovernanceConfig,
    # Constants
    TIER_GOVERNANCE,
    # Protocols
    ModelProtocol,
    DriftDetectorProtocol,
    # Aggregators
    FederatedAggregator,
    FedAvgAggregator,
    WeightedAvgAggregator,
    AGGREGATORS,
    # Registry
    VersionedModelRegistry,
    # Manager
    FederatedModelManager,
    # Factories
    create_model_manager,
    create_community_manager,
    create_pro_manager,
    create_enterprise_manager,
    # Functions
    get_governance_config,
)

# ML Governance (Week 20)
from .ml_governance import (
    # Enums
    PolicyAction,
    PolicyDecision,
    ComplianceStandard,
    AuditEventType,
    DataClassification,
    # Data Classes
    AuditEvent,
    PolicyRule,
    PolicyEvaluationResult,
    DataGovernancePolicy,
    ModelGovernanceConfig,
    # Classes
    PolicyEngine,
    AuditLogger,
    GovernanceController,
    # Factories
    create_governance_controller,
    create_hipaa_compliant_model_config,
    create_gdpr_compliant_model_config,
)

# Observability Bridge (Week 20 Adjustment)
from .observability_bridge import (
    MLObservabilityEvent,
    ObservabilityBridgeConfig,
    ObservabilityBridge,
    create_observability_bridge,
    drift_severity_to_threat_stage,
    model_state_to_enforcement_action,
)

# Policy Enforcement Loop (Week 20 Adjustment)
from .policy_enforcement_loop import (
    # Enums
    EnforcementEvent,
    AdaptiveAction,
    # Protocols
    PolicyPushService,
    AdaptiveControlsService,
    TelemetryIntegrationService,
    # Data Classes
    EnforcementChange,
    ThresholdConfig,
    AdaptiveControlState,
    # Default Implementations
    DefaultPolicyPushService,
    DefaultAdaptiveControlsService,
    DefaultTelemetryIntegrationService,
    # Controller
    PolicyEnforcementLoop,
    # Factories
    create_enforcement_loop,
    create_full_enforcement_loop,
)

__all__ = [
    # Anomaly Detection
    "AnomalyType",
    "DetectionMethod",
    "Severity",
    "FeatureVector",
    "Anomaly",
    "DetectionResult",
    "AnomalyDetector",
    "ZScoreDetector",
    "IQRDetector",
    "MADDetector",
    "IsolationForestDetector",
    "LocalOutlierFactorDetector",
    "EnsembleDetector",
    "AnomalyConfig",
    "AnomalyDetectionEngine",
    # Pattern Learning
    "PatternType",
    "PatternConfidence",
    "LearningMode",
    "Event",
    "Pattern",
    "PatternMatch",
    "SequenceRule",
    "PatternLearner",
    "TemporalPatternLearner",
    "SequencePatternLearner",
    "VolumetricPatternLearner",
    "CompositePatternLearner",
    "PatternLearningConfig",
    "PatternLearningEngine",
    # Risk Scoring
    "RiskCategory",
    "RiskLevel",
    "RiskTrend",
    "RiskFactor",
    "RiskProfile",
    "RiskEvent",
    "RiskScorer",
    "LicenseRiskScorer",
    "BehavioralRiskScorer",
    "EnvironmentalRiskScorer",
    "TemporalRiskScorer",
    "VolumetricRiskScorer",
    "IdentityRiskScorer",
    "RiskScoringConfig",
    "RiskScoringEngine",
    # Predictive Modeling
    "PredictionType",
    "PredictionConfidence",
    "ModelType",
    "Observation",
    "Prediction",
    "PredictionFeedback",
    "PredictiveModel",
    "MarkovChainModel",
    "TimeSeriesPredictor",
    "SequencePredictor",
    "BayesianPredictor",
    "EnsemblePredictor",
    "PredictiveConfig",
    "PredictiveModelingEngine",
    # Model Orchestration
    "DecisionType",
    "DecisionPriority",
    "ModelStatus",
    "ModelInfo",
    "Decision",
    "ModelVote",
    "DecisionStrategy",
    "MajorityVoteStrategy",
    "ConservativeStrategy",
    "WeightedConsensusStrategy",
    "ModelRegistry",
    "DecisionCache",
    "OrchestrationConfig",
    "ModelOrchestrator",
    "OrchestratorSnapshot",
    "create_snapshot",
    # Federated Model Manager (Week 20)
    "ModelTier",
    "ModelState",
    "GovernanceMode",
    "FederatedRole",
    "UpdateStrategy",
    "AggregationMethod",
    "DriftSeverity",
    "SemanticVersion",
    "ModelMetrics",
    "DriftMetrics",
    "ModelVersion",
    "FederatedUpdate",
    "FederatedRound",
    "TierGovernanceConfig",
    "TIER_GOVERNANCE",
    "ModelProtocol",
    "DriftDetectorProtocol",
    "FederatedAggregator",
    "FedAvgAggregator",
    "WeightedAvgAggregator",
    "AGGREGATORS",
    "VersionedModelRegistry",
    "FederatedModelManager",
    "create_model_manager",
    "create_community_manager",
    "create_pro_manager",
    "create_enterprise_manager",
    "get_governance_config",
    # ML Governance (Week 20)
    "PolicyAction",
    "PolicyDecision",
    "ComplianceStandard",
    "AuditEventType",
    "DataClassification",
    "AuditEvent",
    "PolicyRule",
    "PolicyEvaluationResult",
    "DataGovernancePolicy",
    "ModelGovernanceConfig",
    "PolicyEngine",
    "AuditLogger",
    "GovernanceController",
    "create_governance_controller",
    "create_hipaa_compliant_model_config",
    "create_gdpr_compliant_model_config",
    # Observability Bridge (Week 20 Adjustment)
    "MLObservabilityEvent",
    "ObservabilityBridgeConfig",
    "ObservabilityBridge",
    "create_observability_bridge",
    "drift_severity_to_threat_stage",
    "model_state_to_enforcement_action",
    # Policy Enforcement Loop (Week 20 Adjustment)
    "EnforcementEvent",
    "AdaptiveAction",
    "PolicyPushService",
    "AdaptiveControlsService",
    "TelemetryIntegrationService",
    "EnforcementChange",
    "ThresholdConfig",
    "AdaptiveControlState",
    "DefaultPolicyPushService",
    "DefaultAdaptiveControlsService",
    "DefaultTelemetryIntegrationService",
    "PolicyEnforcementLoop",
    "create_enforcement_loop",
    "create_full_enforcement_loop",
]
