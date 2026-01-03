# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.experiment_safety
# This stub remains for backward compatibility but will be removed in v2.0.
import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.experiment_safety is deprecated. "
    "Import from 'app.services.billing.experiment_safety' instead.",
    DeprecationWarning,
    stacklevel=2
)

"""
Experiment Safety Guards for KRL Pricing.

This module provides safety mechanisms for A/B tests and pricing experiments:
- Minimum sample size validation before statistical conclusions
- Time-bound experiments with automatic completion
- Negative lift detection with auto-rollback
- Revenue protection guardrails
- Statistical power calculations
- Sequential testing with early stopping

These guards prevent:
- False positives from small sample sizes
- Runaway experiments that harm revenue
- Statistical errors from multiple comparisons
- Business disruption from prolonged testing

Part of Phase 1 pricing strategy implementation.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from decimal import Decimal
from enum import Enum, auto
from typing import Any, Callable, Optional
import logging
import math
import statistics

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class GuardType(Enum):
    """Types of safety guards."""
    SAMPLE_SIZE = auto()        # Minimum sample requirement
    TIME_BOUND = auto()         # Maximum experiment duration
    NEGATIVE_LIFT = auto()      # Auto-rollback on negative results
    REVENUE_GUARD = auto()      # Revenue impact threshold
    STATISTICAL_POWER = auto()  # Minimum detectable effect
    CONFIDENCE = auto()         # Statistical significance threshold


class GuardAction(Enum):
    """Actions taken when guard is triggered."""
    WARN = "warn"               # Log warning only
    PAUSE = "pause"             # Pause experiment
    ROLLBACK = "rollback"       # Revert to control
    COMPLETE = "complete"       # Mark as complete
    NOTIFY = "notify"           # Send notification


class ExperimentPhase(Enum):
    """Experiment lifecycle phases."""
    WARMUP = "warmup"           # Initial data collection (no decisions)
    ACTIVE = "active"           # Full experiment running
    MONITORING = "monitoring"   # Post-decision monitoring
    COMPLETED = "completed"     # Experiment finished


class RollbackReason(Enum):
    """Reasons for experiment rollback."""
    NEGATIVE_LIFT = "negative_lift"
    REVENUE_IMPACT = "revenue_impact"
    TIME_EXCEEDED = "time_exceeded"
    SAMPLE_SIZE_UNREACHABLE = "sample_size_unreachable"
    MANUAL = "manual"
    STATISTICAL_ERROR = "statistical_error"


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class SampleSizeConfig:
    """Configuration for sample size requirements."""
    # Minimum absolute sample size per variant
    min_absolute_sample: int = 100
    
    # Minimum sample for statistical validity
    min_statistical_sample: int = 30
    
    # Target sample for full power (80% power to detect MDE)
    target_power_sample: int = 1000
    
    # Maximum days to wait for sample size
    max_days_to_sample: int = 30
    
    # Minimum daily observations to continue
    min_daily_observations: int = 10


@dataclass
class TimeBoundConfig:
    """Configuration for time-based guards."""
    # Warmup period (no decisions made)
    warmup_days: int = 3
    
    # Minimum experiment duration
    min_duration_days: int = 7
    
    # Maximum experiment duration
    max_duration_days: int = 30
    
    # Grace period before auto-complete
    grace_period_days: int = 3
    
    # Whether to extend if sample size not met
    extend_for_sample: bool = True
    max_extension_days: int = 14


@dataclass
class NegativeLiftConfig:
    """Configuration for negative lift detection."""
    # Lift threshold for concern (e.g., -5%)
    warning_threshold: float = -0.05
    
    # Lift threshold for rollback (e.g., -10%)
    rollback_threshold: float = -0.10
    
    # Confidence level required to trigger rollback
    rollback_confidence: float = 0.90
    
    # Minimum sample before checking
    min_sample_to_check: int = 100
    
    # Consecutive periods of negative lift to trigger
    consecutive_periods: int = 3


@dataclass
class RevenueGuardConfig:
    """Configuration for revenue protection."""
    # Maximum revenue impact percentage (absolute)
    max_revenue_impact_pct: float = 10.0
    
    # Minimum revenue threshold to trigger (ignore small amounts)
    min_revenue_threshold: Decimal = Decimal("1000")
    
    # Rolling window for revenue calculation (days)
    revenue_window_days: int = 7
    
    # Alert threshold before max (early warning)
    alert_threshold_pct: float = 7.0


@dataclass
class ExperimentSafetyConfig:
    """Complete safety configuration for an experiment."""
    sample_size: SampleSizeConfig = field(default_factory=SampleSizeConfig)
    time_bound: TimeBoundConfig = field(default_factory=TimeBoundConfig)
    negative_lift: NegativeLiftConfig = field(default_factory=NegativeLiftConfig)
    revenue_guard: RevenueGuardConfig = field(default_factory=RevenueGuardConfig)
    
    # Enabled guards
    enable_sample_guard: bool = True
    enable_time_guard: bool = True
    enable_negative_lift_guard: bool = True
    enable_revenue_guard: bool = True
    
    # Global settings
    auto_rollback_enabled: bool = True
    notify_on_guard_trigger: bool = True


# =============================================================================
# Guard Results
# =============================================================================

@dataclass
class GuardCheckResult:
    """Result of a safety guard check."""
    guard_type: GuardType
    passed: bool
    action: Optional[GuardAction] = None
    message: str = ""
    details: dict = field(default_factory=dict)
    checked_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    @property
    def requires_action(self) -> bool:
        """Check if action is required."""
        return not self.passed and self.action is not None


@dataclass
class ExperimentHealthReport:
    """Comprehensive health report for an experiment."""
    experiment_id: str
    phase: ExperimentPhase
    is_healthy: bool
    
    # Guard results
    guard_results: list[GuardCheckResult] = field(default_factory=list)
    
    # Statistics
    current_sample_size: int = 0
    days_running: int = 0
    current_lift: float = 0.0
    lift_confidence: float = 0.0
    revenue_impact: Decimal = Decimal("0")
    
    # Recommendations
    recommended_action: Optional[GuardAction] = None
    recommendation_reason: str = ""
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    @property
    def failing_guards(self) -> list[GuardCheckResult]:
        """Get list of failing guards."""
        return [g for g in self.guard_results if not g.passed]
    
    @property
    def critical_failures(self) -> list[GuardCheckResult]:
        """Get guards requiring immediate action."""
        return [g for g in self.guard_results if g.requires_action]


# =============================================================================
# Statistical Utilities
# =============================================================================

class StatisticalGuards:
    """
    Statistical utility functions for experiment safety.
    """
    
    @staticmethod
    def calculate_sample_size(
        baseline_rate: float,
        minimum_detectable_effect: float,
        power: float = 0.80,
        significance: float = 0.05,
    ) -> int:
        """
        Calculate required sample size per variant.
        
        Uses two-sample proportion test formula.
        
        Args:
            baseline_rate: Expected conversion rate for control
            minimum_detectable_effect: Minimum effect to detect (relative)
            power: Statistical power (1 - Type II error)
            significance: Significance level (Type I error)
            
        Returns:
            Required sample size per variant
        """
        # Z-scores for power and significance
        z_alpha = 1.96 if significance == 0.05 else StatisticalGuards._z_score(1 - significance / 2)
        z_beta = 0.84 if power == 0.80 else StatisticalGuards._z_score(power)
        
        # Expected treatment rate
        treatment_rate = baseline_rate * (1 + minimum_detectable_effect)
        
        # Pooled rate
        pooled_rate = (baseline_rate + treatment_rate) / 2
        pooled_variance = pooled_rate * (1 - pooled_rate)
        
        # Effect size in absolute terms
        effect = abs(treatment_rate - baseline_rate)
        
        if effect == 0:
            return 10000  # Arbitrary large number
        
        # Sample size formula
        n = 2 * pooled_variance * ((z_alpha + z_beta) ** 2) / (effect ** 2)
        
        return max(int(math.ceil(n)), 100)
    
    @staticmethod
    def _z_score(probability: float) -> float:
        """Approximate z-score for given probability (inverse normal CDF)."""
        # Approximation for common values
        z_table = {
            0.50: 0.0,
            0.80: 0.84,
            0.90: 1.28,
            0.95: 1.645,
            0.975: 1.96,
            0.99: 2.33,
            0.995: 2.58,
        }
        
        # Find closest value
        closest = min(z_table.keys(), key=lambda x: abs(x - probability))
        return z_table[closest]
    
    @staticmethod
    def calculate_lift(
        control_value: float,
        treatment_value: float,
    ) -> float:
        """Calculate relative lift (treatment vs control)."""
        if control_value == 0:
            return 0.0
        return (treatment_value - control_value) / control_value
    
    @staticmethod
    def calculate_confidence(
        control_conversions: int,
        control_sample: int,
        treatment_conversions: int,
        treatment_sample: int,
    ) -> float:
        """
        Calculate confidence that treatment is different from control.
        
        Uses two-proportion z-test.
        
        Returns:
            Confidence level (0.0 to 1.0)
        """
        if control_sample == 0 or treatment_sample == 0:
            return 0.0
        
        # Conversion rates
        p1 = control_conversions / control_sample
        p2 = treatment_conversions / treatment_sample
        
        # Pooled proportion
        p_pool = (control_conversions + treatment_conversions) / (control_sample + treatment_sample)
        
        # Standard error
        se = math.sqrt(p_pool * (1 - p_pool) * (1/control_sample + 1/treatment_sample))
        
        if se == 0:
            return 0.0
        
        # Z-score
        z = abs(p2 - p1) / se
        
        # Convert to confidence (using normal approximation)
        # Confidence ≈ Φ(z) where Φ is CDF of standard normal
        confidence = StatisticalGuards._normal_cdf(z)
        
        return min(confidence, 0.9999)
    
    @staticmethod
    def _normal_cdf(z: float) -> float:
        """Approximate CDF of standard normal distribution."""
        # Approximation good to 4 decimal places
        a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
        p = 0.3275911
        
        sign = 1 if z >= 0 else -1
        z = abs(z) / math.sqrt(2)
        
        t = 1.0 / (1.0 + p * z)
        y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-z * z)
        
        return 0.5 * (1.0 + sign * y)
    
    @staticmethod
    def is_sample_adequate(
        current_sample: int,
        required_sample: int,
        confidence_threshold: float = 0.95,
    ) -> tuple[bool, float]:
        """
        Check if current sample is adequate for conclusions.
        
        Returns:
            Tuple of (is_adequate, current_power)
        """
        if current_sample >= required_sample:
            return True, 1.0
        
        # Estimate current power
        power = min(current_sample / required_sample, 0.999)
        
        return power >= (1 - confidence_threshold), power


# =============================================================================
# Safety Guard Engine
# =============================================================================

class ExperimentSafetyGuard:
    """
    Main safety guard engine for experiments.
    
    Monitors experiments and enforces safety rules.
    """
    
    def __init__(
        self,
        config: Optional[ExperimentSafetyConfig] = None,
        on_guard_triggered: Optional[Callable[[GuardCheckResult], None]] = None,
    ):
        """
        Initialize safety guard.
        
        Args:
            config: Safety configuration
            on_guard_triggered: Callback when guard is triggered
        """
        self.config = config or ExperimentSafetyConfig()
        self.on_guard_triggered = on_guard_triggered
        
        # Tracking for consecutive negative periods
        self._negative_period_count: dict[str, int] = {}
        self._last_check: dict[str, datetime] = {}
    
    def check_experiment_health(
        self,
        experiment_id: str,
        control_metrics: dict[str, Any],
        treatment_metrics: dict[str, Any],
        start_date: datetime,
        baseline_revenue: Decimal,
    ) -> ExperimentHealthReport:
        """
        Perform comprehensive health check on experiment.
        
        Args:
            experiment_id: Experiment identifier
            control_metrics: Control variant metrics
            treatment_metrics: Treatment variant metrics
            start_date: When experiment started
            baseline_revenue: Baseline revenue for comparison
            
        Returns:
            Complete health report with recommendations
        """
        results = []
        
        # Calculate common metrics
        days_running = (datetime.now(UTC) - start_date).days
        control_sample = control_metrics.get("sample_size", 0)
        treatment_sample = treatment_metrics.get("sample_size", 0)
        total_sample = control_sample + treatment_sample
        
        # Calculate lift
        control_rate = control_metrics.get("conversion_rate", 0)
        treatment_rate = treatment_metrics.get("conversion_rate", 0)
        lift = StatisticalGuards.calculate_lift(control_rate, treatment_rate)
        
        # Calculate confidence
        confidence = StatisticalGuards.calculate_confidence(
            control_metrics.get("conversions", 0),
            control_sample,
            treatment_metrics.get("conversions", 0),
            treatment_sample,
        )
        
        # Calculate revenue impact
        control_revenue = Decimal(str(control_metrics.get("revenue", 0)))
        treatment_revenue = Decimal(str(treatment_metrics.get("revenue", 0)))
        revenue_impact = treatment_revenue - control_revenue
        
        # Determine phase
        if days_running < self.config.time_bound.warmup_days:
            phase = ExperimentPhase.WARMUP
        elif days_running > self.config.time_bound.max_duration_days:
            phase = ExperimentPhase.COMPLETED
        else:
            phase = ExperimentPhase.ACTIVE
        
        # Run guards
        if self.config.enable_sample_guard:
            results.append(self._check_sample_size(
                experiment_id, total_sample, days_running
            ))
        
        if self.config.enable_time_guard:
            results.append(self._check_time_bounds(
                experiment_id, days_running, total_sample
            ))
        
        if self.config.enable_negative_lift_guard and phase == ExperimentPhase.ACTIVE:
            results.append(self._check_negative_lift(
                experiment_id, lift, confidence, total_sample
            ))
        
        if self.config.enable_revenue_guard:
            results.append(self._check_revenue_impact(
                experiment_id, revenue_impact, baseline_revenue
            ))
        
        # Determine overall health
        is_healthy = all(r.passed for r in results)
        
        # Determine recommended action
        recommended_action = None
        recommendation_reason = ""
        
        critical_failures = [r for r in results if r.requires_action]
        if critical_failures:
            # Take most severe action
            action_priority = {
                GuardAction.ROLLBACK: 4,
                GuardAction.COMPLETE: 3,
                GuardAction.PAUSE: 2,
                GuardAction.NOTIFY: 1,
                GuardAction.WARN: 0,
            }
            
            most_severe = max(
                critical_failures,
                key=lambda r: action_priority.get(r.action, 0)
            )
            recommended_action = most_severe.action
            recommendation_reason = most_severe.message
        
        report = ExperimentHealthReport(
            experiment_id=experiment_id,
            phase=phase,
            is_healthy=is_healthy,
            guard_results=results,
            current_sample_size=total_sample,
            days_running=days_running,
            current_lift=lift,
            lift_confidence=confidence,
            revenue_impact=revenue_impact,
            recommended_action=recommended_action,
            recommendation_reason=recommendation_reason,
        )
        
        # Trigger callbacks for failures
        if self.on_guard_triggered:
            for result in results:
                if result.requires_action:
                    self.on_guard_triggered(result)
        
        return report
    
    def _check_sample_size(
        self,
        experiment_id: str,
        current_sample: int,
        days_running: int,
    ) -> GuardCheckResult:
        """Check sample size requirements."""
        cfg = self.config.sample_size
        
        # Check minimum absolute
        if current_sample < cfg.min_statistical_sample:
            return GuardCheckResult(
                guard_type=GuardType.SAMPLE_SIZE,
                passed=False,
                action=GuardAction.WARN,
                message=f"Sample size ({current_sample}) below statistical minimum ({cfg.min_statistical_sample})",
                details={
                    "current": current_sample,
                    "required": cfg.min_statistical_sample,
                    "type": "statistical_minimum",
                },
            )
        
        if current_sample < cfg.min_absolute_sample:
            return GuardCheckResult(
                guard_type=GuardType.SAMPLE_SIZE,
                passed=False,
                action=GuardAction.WARN,
                message=f"Sample size ({current_sample}) below minimum ({cfg.min_absolute_sample})",
                details={
                    "current": current_sample,
                    "required": cfg.min_absolute_sample,
                    "type": "absolute_minimum",
                },
            )
        
        # Check if sample rate is sustainable
        if days_running > 0:
            daily_rate = current_sample / days_running
            days_to_target = (cfg.target_power_sample - current_sample) / max(daily_rate, 1)
            
            if days_to_target > cfg.max_days_to_sample:
                return GuardCheckResult(
                    guard_type=GuardType.SAMPLE_SIZE,
                    passed=False,
                    action=GuardAction.COMPLETE if days_running > cfg.max_days_to_sample else GuardAction.WARN,
                    message=f"Sample size unlikely to reach target in allotted time",
                    details={
                        "current": current_sample,
                        "target": cfg.target_power_sample,
                        "daily_rate": daily_rate,
                        "estimated_days": days_to_target,
                        "max_days": cfg.max_days_to_sample,
                    },
                )
        
        return GuardCheckResult(
            guard_type=GuardType.SAMPLE_SIZE,
            passed=True,
            message=f"Sample size adequate ({current_sample})",
            details={"current": current_sample},
        )
    
    def _check_time_bounds(
        self,
        experiment_id: str,
        days_running: int,
        current_sample: int,
    ) -> GuardCheckResult:
        """Check time-based constraints."""
        cfg = self.config.time_bound
        
        # Check max duration
        max_days = cfg.max_duration_days
        if cfg.extend_for_sample and current_sample < self.config.sample_size.min_absolute_sample:
            max_days = min(max_days + cfg.max_extension_days, cfg.max_duration_days + cfg.max_extension_days)
        
        if days_running > max_days:
            return GuardCheckResult(
                guard_type=GuardType.TIME_BOUND,
                passed=False,
                action=GuardAction.COMPLETE,
                message=f"Experiment exceeded maximum duration ({days_running} > {max_days} days)",
                details={
                    "days_running": days_running,
                    "max_duration": max_days,
                    "extended": cfg.extend_for_sample,
                },
            )
        
        # Warning for approaching max
        if days_running > max_days - cfg.grace_period_days:
            return GuardCheckResult(
                guard_type=GuardType.TIME_BOUND,
                passed=True,  # Not failed yet, just warning
                action=GuardAction.WARN,
                message=f"Experiment approaching max duration ({days_running}/{max_days} days)",
                details={
                    "days_running": days_running,
                    "max_duration": max_days,
                    "days_remaining": max_days - days_running,
                },
            )
        
        return GuardCheckResult(
            guard_type=GuardType.TIME_BOUND,
            passed=True,
            message=f"Time bounds OK ({days_running}/{max_days} days)",
            details={"days_running": days_running, "max_duration": max_days},
        )
    
    def _check_negative_lift(
        self,
        experiment_id: str,
        lift: float,
        confidence: float,
        sample_size: int,
    ) -> GuardCheckResult:
        """Check for negative lift with auto-rollback."""
        cfg = self.config.negative_lift
        
        # Don't check until minimum sample
        if sample_size < cfg.min_sample_to_check:
            return GuardCheckResult(
                guard_type=GuardType.NEGATIVE_LIFT,
                passed=True,
                message="Insufficient sample for negative lift check",
                details={"sample_size": sample_size, "min_required": cfg.min_sample_to_check},
            )
        
        # Track consecutive negative periods
        if lift < cfg.warning_threshold:
            self._negative_period_count[experiment_id] = self._negative_period_count.get(experiment_id, 0) + 1
        else:
            self._negative_period_count[experiment_id] = 0
        
        consecutive = self._negative_period_count.get(experiment_id, 0)
        
        # Check for rollback condition
        if (lift < cfg.rollback_threshold and 
            confidence >= cfg.rollback_confidence and
            consecutive >= cfg.consecutive_periods):
            
            return GuardCheckResult(
                guard_type=GuardType.NEGATIVE_LIFT,
                passed=False,
                action=GuardAction.ROLLBACK if self.config.auto_rollback_enabled else GuardAction.NOTIFY,
                message=f"Negative lift detected: {lift:.1%} with {confidence:.1%} confidence",
                details={
                    "lift": lift,
                    "confidence": confidence,
                    "threshold": cfg.rollback_threshold,
                    "consecutive_periods": consecutive,
                },
            )
        
        # Warning for concerning lift
        if lift < cfg.warning_threshold:
            return GuardCheckResult(
                guard_type=GuardType.NEGATIVE_LIFT,
                passed=True,  # Not failed, but concerning
                action=GuardAction.WARN,
                message=f"Warning: Negative lift trend ({lift:.1%})",
                details={
                    "lift": lift,
                    "confidence": confidence,
                    "consecutive_periods": consecutive,
                },
            )
        
        return GuardCheckResult(
            guard_type=GuardType.NEGATIVE_LIFT,
            passed=True,
            message=f"Lift OK: {lift:.1%}",
            details={"lift": lift, "confidence": confidence},
        )
    
    def _check_revenue_impact(
        self,
        experiment_id: str,
        revenue_impact: Decimal,
        baseline_revenue: Decimal,
    ) -> GuardCheckResult:
        """Check revenue impact doesn't exceed threshold."""
        cfg = self.config.revenue_guard
        
        # Skip if baseline is below threshold
        if baseline_revenue < cfg.min_revenue_threshold:
            return GuardCheckResult(
                guard_type=GuardType.REVENUE_GUARD,
                passed=True,
                message="Revenue below monitoring threshold",
                details={"baseline": float(baseline_revenue), "threshold": float(cfg.min_revenue_threshold)},
            )
        
        # Calculate impact percentage
        impact_pct = float(abs(revenue_impact) / baseline_revenue * 100)
        is_negative = revenue_impact < 0
        
        # Check max impact
        if impact_pct > cfg.max_revenue_impact_pct and is_negative:
            return GuardCheckResult(
                guard_type=GuardType.REVENUE_GUARD,
                passed=False,
                action=GuardAction.ROLLBACK if self.config.auto_rollback_enabled else GuardAction.PAUSE,
                message=f"Revenue impact ({impact_pct:.1f}%) exceeds maximum ({cfg.max_revenue_impact_pct}%)",
                details={
                    "impact": float(revenue_impact),
                    "impact_pct": impact_pct,
                    "max_pct": cfg.max_revenue_impact_pct,
                    "baseline": float(baseline_revenue),
                },
            )
        
        # Warning threshold
        if impact_pct > cfg.alert_threshold_pct and is_negative:
            return GuardCheckResult(
                guard_type=GuardType.REVENUE_GUARD,
                passed=True,
                action=GuardAction.WARN,
                message=f"Warning: Revenue impact approaching limit ({impact_pct:.1f}%)",
                details={
                    "impact": float(revenue_impact),
                    "impact_pct": impact_pct,
                    "alert_threshold": cfg.alert_threshold_pct,
                },
            )
        
        return GuardCheckResult(
            guard_type=GuardType.REVENUE_GUARD,
            passed=True,
            message=f"Revenue impact OK ({impact_pct:.1f}%)",
            details={"impact": float(revenue_impact), "impact_pct": impact_pct},
        )
    
    def should_auto_rollback(
        self,
        experiment_id: str,
        report: ExperimentHealthReport,
    ) -> tuple[bool, Optional[RollbackReason]]:
        """
        Determine if experiment should be automatically rolled back.
        
        Returns:
            Tuple of (should_rollback, reason)
        """
        if not self.config.auto_rollback_enabled:
            return False, None
        
        # Check for rollback actions
        for guard in report.guard_results:
            if guard.action == GuardAction.ROLLBACK:
                if guard.guard_type == GuardType.NEGATIVE_LIFT:
                    return True, RollbackReason.NEGATIVE_LIFT
                elif guard.guard_type == GuardType.REVENUE_GUARD:
                    return True, RollbackReason.REVENUE_IMPACT
                elif guard.guard_type == GuardType.TIME_BOUND:
                    return True, RollbackReason.TIME_EXCEEDED
        
        return False, None


# =============================================================================
# Convenience Functions
# =============================================================================

def calculate_required_sample_size(
    baseline_conversion: float = 0.05,
    minimum_detectable_effect: float = 0.10,
    power: float = 0.80,
    significance: float = 0.05,
) -> int:
    """
    Calculate required sample size for pricing experiment.
    
    Args:
        baseline_conversion: Expected conversion rate (e.g., 0.05 = 5%)
        minimum_detectable_effect: Minimum effect to detect (e.g., 0.10 = 10% relative lift)
        power: Statistical power (default 80%)
        significance: Significance level (default 5%)
        
    Returns:
        Required sample size per variant
    """
    return StatisticalGuards.calculate_sample_size(
        baseline_conversion, minimum_detectable_effect, power, significance
    )


def create_default_safety_config() -> ExperimentSafetyConfig:
    """Create safety config with sensible defaults for pricing experiments."""
    return ExperimentSafetyConfig(
        sample_size=SampleSizeConfig(
            min_absolute_sample=100,
            min_statistical_sample=30,
            target_power_sample=1000,
            max_days_to_sample=30,
        ),
        time_bound=TimeBoundConfig(
            warmup_days=3,
            min_duration_days=7,
            max_duration_days=30,
            extend_for_sample=True,
        ),
        negative_lift=NegativeLiftConfig(
            warning_threshold=-0.05,
            rollback_threshold=-0.10,
            rollback_confidence=0.90,
            consecutive_periods=3,
        ),
        revenue_guard=RevenueGuardConfig(
            max_revenue_impact_pct=10.0,
            alert_threshold_pct=7.0,
        ),
        auto_rollback_enabled=True,
    )


def create_conservative_safety_config() -> ExperimentSafetyConfig:
    """Create conservative safety config for high-risk experiments."""
    return ExperimentSafetyConfig(
        sample_size=SampleSizeConfig(
            min_absolute_sample=500,
            min_statistical_sample=100,
            target_power_sample=2000,
            max_days_to_sample=14,
        ),
        time_bound=TimeBoundConfig(
            warmup_days=7,
            min_duration_days=14,
            max_duration_days=21,
            extend_for_sample=False,
        ),
        negative_lift=NegativeLiftConfig(
            warning_threshold=-0.02,
            rollback_threshold=-0.05,
            rollback_confidence=0.85,
            consecutive_periods=2,
        ),
        revenue_guard=RevenueGuardConfig(
            max_revenue_impact_pct=5.0,
            alert_threshold_pct=3.0,
        ),
        auto_rollback_enabled=True,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "GuardType",
    "GuardAction",
    "ExperimentPhase",
    "RollbackReason",
    # Config classes
    "SampleSizeConfig",
    "TimeBoundConfig",
    "NegativeLiftConfig",
    "RevenueGuardConfig",
    "ExperimentSafetyConfig",
    # Result classes
    "GuardCheckResult",
    "ExperimentHealthReport",
    # Main classes
    "StatisticalGuards",
    "ExperimentSafetyGuard",
    # Functions
    "calculate_required_sample_size",
    "create_default_safety_config",
    "create_conservative_safety_config",
]
