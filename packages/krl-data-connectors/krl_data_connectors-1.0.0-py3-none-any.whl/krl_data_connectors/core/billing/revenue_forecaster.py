from __future__ import annotations

# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
#
# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.revenue_forecaster
# This stub remains for backward compatibility but will be removed in v2.0.
# ----------------------------------------------------------------------
import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.revenue_forecaster is deprecated. "
    "Import from 'app.services.billing.revenue_forecaster' instead.",
    DeprecationWarning,
    stacklevel=2
)

"""
Revenue Forecasting Engine - Phase 3 Week 22

Predictive models for MRR/ARR forecasting based on:
- Historical usage patterns
- Churn signals from defense and behavioral data
- Expansion indicators from upsell engine
- Contraction signals from engagement decay

Forecasting Methods:
- Time series decomposition (trend, seasonality, noise)
- Cohort-based projection
- Usage-velocity forecasting
- Risk-adjusted revenue projection

This layer sits above the billing stack and feeds dashboard/alerts.
"""

import logging
import math
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class ForecastHorizon(Enum):
    """Forecast time horizons."""
    WEEK = "week"          # 7 days
    MONTH = "month"        # 30 days
    QUARTER = "quarter"    # 90 days
    YEAR = "year"          # 365 days


class ForecastMethod(Enum):
    """Forecasting methods."""
    SIMPLE_AVERAGE = "simple_average"
    WEIGHTED_AVERAGE = "weighted_average"
    LINEAR_TREND = "linear_trend"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    COHORT_BASED = "cohort_based"
    USAGE_VELOCITY = "usage_velocity"
    ENSEMBLE = "ensemble"


class RevenueStream(Enum):
    """Revenue stream types."""
    SUBSCRIPTION = "subscription"      # Recurring subscription fees
    USAGE_BASED = "usage_based"        # Pay-as-you-go usage
    OVERAGE = "overage"                # Over-limit charges
    PREMIUM_FEATURES = "premium"       # Premium feature add-ons
    PENALTY = "penalty"                # Violation penalties
    TOTAL = "total"                    # All streams combined


class ForecastConfidence(Enum):
    """Confidence levels for forecasts."""
    HIGH = "high"          # >80% confidence
    MEDIUM = "medium"      # 50-80% confidence
    LOW = "low"            # <50% confidence
    UNCERTAIN = "uncertain"  # Insufficient data


class RevenueSignal(Enum):
    """Signals affecting revenue forecasts."""
    # Positive signals
    USAGE_GROWTH = "usage_growth"
    ENGAGEMENT_INCREASE = "engagement_increase"
    FEATURE_ADOPTION = "feature_adoption"
    UPSELL_ACCEPTED = "upsell_accepted"
    PAYMENT_ON_TIME = "payment_on_time"
    
    # Negative signals
    USAGE_DECLINE = "usage_decline"
    ENGAGEMENT_DECAY = "engagement_decay"
    CHURN_INDICATOR = "churn_indicator"
    PAYMENT_DELAYED = "payment_delayed"
    DOWNGRADE_REQUEST = "downgrade_request"
    
    # Neutral signals
    STABLE_USAGE = "stable_usage"
    SEASONAL_PATTERN = "seasonal_pattern"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class RevenueDataPoint:
    """A single revenue data point for forecasting."""
    timestamp: datetime
    amount: Decimal
    stream: RevenueStream
    tenant_id: str
    tier: str
    
    # Context
    usage_level: float = 0.0  # 0-1 utilization
    risk_multiplier: float = 1.0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ForecastResult:
    """Result of a revenue forecast."""
    forecast_id: str
    created_at: datetime
    
    # Target
    horizon: ForecastHorizon
    stream: RevenueStream
    tenant_id: Optional[str] = None  # None = aggregate
    
    # Prediction
    predicted_amount: Decimal = Decimal("0")
    lower_bound: Decimal = Decimal("0")  # 95% CI lower
    upper_bound: Decimal = Decimal("0")  # 95% CI upper
    
    # Method
    method: ForecastMethod = ForecastMethod.ENSEMBLE
    confidence: ForecastConfidence = ForecastConfidence.MEDIUM
    confidence_score: float = 0.5
    
    # Components
    base_revenue: Decimal = Decimal("0")     # Current run-rate
    growth_component: Decimal = Decimal("0")  # Expected growth
    churn_component: Decimal = Decimal("0")   # Expected churn loss
    expansion_component: Decimal = Decimal("0")  # Expected expansion
    
    # Signals
    contributing_signals: List[RevenueSignal] = field(default_factory=list)
    
    # Accuracy (for backtesting)
    actual_amount: Optional[Decimal] = None
    error_percent: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "forecast_id": self.forecast_id,
            "created_at": self.created_at.isoformat(),
            "horizon": self.horizon.value,
            "stream": self.stream.value,
            "tenant_id": self.tenant_id,
            "predicted_amount": str(self.predicted_amount),
            "lower_bound": str(self.lower_bound),
            "upper_bound": str(self.upper_bound),
            "method": self.method.value,
            "confidence": self.confidence.value,
            "confidence_score": self.confidence_score,
            "base_revenue": str(self.base_revenue),
            "growth_component": str(self.growth_component),
            "churn_component": str(self.churn_component),
            "expansion_component": str(self.expansion_component),
        }


@dataclass
class TenantRevenueProfile:
    """Revenue profile for a tenant."""
    tenant_id: str
    tier: str
    
    # Current state
    mrr: Decimal = Decimal("0")  # Monthly recurring revenue
    arr: Decimal = Decimal("0")  # Annual recurring revenue
    
    # Historical
    revenue_history: List[RevenueDataPoint] = field(default_factory=list)
    
    # Metrics
    average_monthly_usage: float = 0.0
    usage_trend: float = 0.0  # Positive = growing
    engagement_score: float = 1.0
    
    # Risk
    churn_probability: float = 0.0
    expansion_probability: float = 0.0
    contraction_probability: float = 0.0
    
    # LTV
    estimated_ltv: Decimal = Decimal("0")
    months_active: int = 0
    
    # Last update
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ForecastConfig:
    """Configuration for forecasting."""
    # Method weights (for ensemble)
    method_weights: Dict[ForecastMethod, float] = field(default_factory=lambda: {
        ForecastMethod.LINEAR_TREND: 0.3,
        ForecastMethod.EXPONENTIAL_SMOOTHING: 0.3,
        ForecastMethod.COHORT_BASED: 0.2,
        ForecastMethod.USAGE_VELOCITY: 0.2,
    })
    
    # Smoothing parameters
    alpha: float = 0.3  # Exponential smoothing
    beta: float = 0.1   # Trend smoothing
    
    # Confidence intervals
    confidence_level: float = 0.95
    
    # Churn/expansion defaults
    default_churn_rate: float = 0.05      # 5% monthly
    default_expansion_rate: float = 0.03   # 3% monthly
    
    # Minimum data requirements
    min_data_points: int = 3
    min_months_for_trend: int = 2
    
    # Seasonality
    detect_seasonality: bool = True
    seasonality_period: int = 12  # Monthly


# =============================================================================
# Time Series Utilities
# =============================================================================

class TimeSeriesUtils:
    """Utilities for time series analysis."""
    
    @staticmethod
    def calculate_trend(values: List[float]) -> Tuple[float, float]:
        """
        Calculate linear trend (slope and intercept).
        
        Returns (slope, intercept).
        """
        n = len(values)
        if n < 2:
            return 0.0, values[0] if values else 0.0
        
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        
        numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0, y_mean
        
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        return slope, intercept
    
    @staticmethod
    def exponential_smoothing(
        values: List[float],
        alpha: float = 0.3,
    ) -> List[float]:
        """Apply simple exponential smoothing."""
        if not values:
            return []
        
        smoothed = [values[0]]
        for v in values[1:]:
            smoothed.append(alpha * v + (1 - alpha) * smoothed[-1])
        
        return smoothed
    
    @staticmethod
    def holt_linear(
        values: List[float],
        alpha: float = 0.3,
        beta: float = 0.1,
        periods: int = 1,
    ) -> float:
        """
        Holt's linear trend method.
        
        Returns forecast for n periods ahead.
        """
        if len(values) < 2:
            return values[-1] if values else 0.0
        
        # Initialize
        level = values[0]
        trend = values[1] - values[0]
        
        # Update
        for v in values[1:]:
            new_level = alpha * v + (1 - alpha) * (level + trend)
            new_trend = beta * (new_level - level) + (1 - beta) * trend
            level = new_level
            trend = new_trend
        
        return level + periods * trend
    
    @staticmethod
    def moving_average(values: List[float], window: int = 3) -> List[float]:
        """Calculate moving average."""
        if len(values) < window:
            return values
        
        result = []
        for i in range(len(values) - window + 1):
            avg = sum(values[i:i + window]) / window
            result.append(avg)
        
        return result
    
    @staticmethod
    def detect_seasonality(
        values: List[float],
        period: int = 12,
    ) -> List[float]:
        """
        Detect seasonal factors.
        
        Returns list of seasonal indices.
        """
        if len(values) < period * 2:
            return [1.0] * period
        
        # Calculate overall average
        avg = sum(values) / len(values)
        if avg == 0:
            return [1.0] * period
        
        # Calculate seasonal indices
        seasonal = []
        for i in range(period):
            period_values = [values[j] for j in range(i, len(values), period)]
            period_avg = sum(period_values) / len(period_values)
            seasonal.append(period_avg / avg)
        
        return seasonal
    
    @staticmethod
    def calculate_volatility(values: List[float]) -> float:
        """Calculate coefficient of variation (volatility)."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        if mean == 0:
            return 0.0
        
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std_dev = math.sqrt(variance)
        
        return std_dev / mean


# =============================================================================
# Revenue Forecaster
# =============================================================================

class RevenueForecaster:
    """
    Forecasts revenue using multiple methods.
    
    Combines time series analysis with business signals
    to produce accurate revenue predictions.
    """
    
    def __init__(self, config: Optional[ForecastConfig] = None):
        self._config = config or ForecastConfig()
        self._ts_utils = TimeSeriesUtils()
        
        # Tenant profiles
        self._profiles: Dict[str, TenantRevenueProfile] = {}
        
        # Historical data
        self._revenue_history: List[RevenueDataPoint] = []
        
        # Forecast history (for backtesting)
        self._forecast_history: List[ForecastResult] = []
        
        # Counters
        self._forecast_counter = 0
        
        logger.info("RevenueForecaster initialized")
    
    # =========================================================================
    # Data Ingestion
    # =========================================================================
    
    def record_revenue(
        self,
        tenant_id: str,
        amount: Decimal,
        stream: RevenueStream,
        tier: str,
        timestamp: Optional[datetime] = None,
        usage_level: float = 0.0,
        risk_multiplier: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a revenue data point."""
        point = RevenueDataPoint(
            timestamp=timestamp or datetime.now(),
            amount=amount,
            stream=stream,
            tenant_id=tenant_id,
            tier=tier,
            usage_level=usage_level,
            risk_multiplier=risk_multiplier,
            metadata=metadata or {},
        )
        
        self._revenue_history.append(point)
        
        # Update tenant profile
        self._update_profile(point)
    
    def _update_profile(self, point: RevenueDataPoint) -> None:
        """Update tenant revenue profile."""
        tenant_id = point.tenant_id
        
        if tenant_id not in self._profiles:
            self._profiles[tenant_id] = TenantRevenueProfile(
                tenant_id=tenant_id,
                tier=point.tier,
            )
        
        profile = self._profiles[tenant_id]
        profile.revenue_history.append(point)
        profile.tier = point.tier
        profile.updated_at = datetime.now()
        
        # Recalculate metrics
        self._recalculate_profile_metrics(profile)
    
    def _recalculate_profile_metrics(self, profile: TenantRevenueProfile) -> None:
        """Recalculate profile metrics from history."""
        history = profile.revenue_history
        if not history:
            return
        
        # Calculate MRR (last 30 days)
        now = datetime.now()
        month_ago = now - timedelta(days=30)
        recent = [p for p in history if p.timestamp >= month_ago]
        
        if recent:
            profile.mrr = sum(p.amount for p in recent)
            profile.arr = profile.mrr * Decimal("12")
        
        # Calculate usage trend
        if len(history) >= 2:
            usage_values = [p.usage_level for p in history[-12:]]
            slope, _ = self._ts_utils.calculate_trend(usage_values)
            profile.usage_trend = slope
        
        # Calculate average usage
        profile.average_monthly_usage = statistics.mean(
            p.usage_level for p in history[-12:]
        ) if history else 0.0
        
        # Calculate months active
        if history:
            first = min(p.timestamp for p in history)
            profile.months_active = max(1, (now - first).days // 30)
    
    def update_churn_probability(
        self,
        tenant_id: str,
        probability: float,
    ) -> None:
        """Update churn probability from external signal."""
        if tenant_id in self._profiles:
            self._profiles[tenant_id].churn_probability = max(0, min(1, probability))
    
    def update_expansion_probability(
        self,
        tenant_id: str,
        probability: float,
    ) -> None:
        """Update expansion probability from external signal."""
        if tenant_id in self._profiles:
            self._profiles[tenant_id].expansion_probability = max(0, min(1, probability))
    
    def update_engagement_score(
        self,
        tenant_id: str,
        score: float,
    ) -> None:
        """Update engagement score from external signal."""
        if tenant_id in self._profiles:
            self._profiles[tenant_id].engagement_score = max(0, min(1, score))
    
    # =========================================================================
    # Forecasting Methods
    # =========================================================================
    
    def forecast(
        self,
        horizon: ForecastHorizon,
        stream: RevenueStream = RevenueStream.TOTAL,
        tenant_id: Optional[str] = None,
        method: ForecastMethod = ForecastMethod.ENSEMBLE,
    ) -> ForecastResult:
        """
        Generate a revenue forecast.
        
        Args:
            horizon: Forecast horizon
            stream: Revenue stream to forecast
            tenant_id: Specific tenant (None = aggregate)
            method: Forecasting method
        
        Returns:
            ForecastResult with prediction and confidence
        """
        # Get historical data
        history = self._get_history_for_forecast(stream, tenant_id)
        
        # Check minimum data
        if len(history) < self._config.min_data_points:
            return self._create_insufficient_data_result(
                horizon, stream, tenant_id
            )
        
        # Convert to values
        values = [float(p.amount) for p in history]
        
        # Get periods for horizon
        periods = self._horizon_to_periods(horizon)
        
        # Forecast based on method
        if method == ForecastMethod.ENSEMBLE:
            prediction = self._ensemble_forecast(values, periods, tenant_id)
        elif method == ForecastMethod.LINEAR_TREND:
            prediction = self._linear_trend_forecast(values, periods)
        elif method == ForecastMethod.EXPONENTIAL_SMOOTHING:
            prediction = self._exponential_forecast(values, periods)
        elif method == ForecastMethod.COHORT_BASED:
            prediction = self._cohort_forecast(values, periods, tenant_id)
        elif method == ForecastMethod.USAGE_VELOCITY:
            prediction = self._usage_velocity_forecast(values, periods, tenant_id)
        else:
            prediction = self._simple_average_forecast(values, periods)
        
        # Calculate confidence interval
        volatility = self._ts_utils.calculate_volatility(values)
        confidence_width = prediction * volatility * 1.96  # 95% CI
        
        lower_bound = max(0, prediction - confidence_width)
        upper_bound = prediction + confidence_width
        
        # Calculate components
        base, growth, churn, expansion = self._calculate_components(
            values, prediction, tenant_id
        )
        
        # Determine confidence
        confidence, conf_score = self._calculate_confidence(
            values, volatility, tenant_id
        )
        
        # Identify signals
        signals = self._identify_contributing_signals(tenant_id)
        
        # Create result
        self._forecast_counter += 1
        result = ForecastResult(
            forecast_id=f"FC-{self._forecast_counter:08d}",
            created_at=datetime.now(),
            horizon=horizon,
            stream=stream,
            tenant_id=tenant_id,
            predicted_amount=Decimal(str(round(prediction, 2))),
            lower_bound=Decimal(str(round(lower_bound, 2))),
            upper_bound=Decimal(str(round(upper_bound, 2))),
            method=method,
            confidence=confidence,
            confidence_score=conf_score,
            base_revenue=Decimal(str(round(base, 2))),
            growth_component=Decimal(str(round(growth, 2))),
            churn_component=Decimal(str(round(churn, 2))),
            expansion_component=Decimal(str(round(expansion, 2))),
            contributing_signals=signals,
        )
        
        # Store for backtesting
        self._forecast_history.append(result)
        
        return result
    
    def _ensemble_forecast(
        self,
        values: List[float],
        periods: int,
        tenant_id: Optional[str],
    ) -> float:
        """Ensemble forecast combining multiple methods."""
        forecasts: Dict[ForecastMethod, float] = {}
        
        # Linear trend
        forecasts[ForecastMethod.LINEAR_TREND] = self._linear_trend_forecast(
            values, periods
        )
        
        # Exponential smoothing
        forecasts[ForecastMethod.EXPONENTIAL_SMOOTHING] = self._exponential_forecast(
            values, periods
        )
        
        # Cohort-based
        forecasts[ForecastMethod.COHORT_BASED] = self._cohort_forecast(
            values, periods, tenant_id
        )
        
        # Usage velocity
        forecasts[ForecastMethod.USAGE_VELOCITY] = self._usage_velocity_forecast(
            values, periods, tenant_id
        )
        
        # Weighted average
        total_weight = 0.0
        weighted_sum = 0.0
        
        for method, forecast in forecasts.items():
            weight = self._config.method_weights.get(method, 0.25)
            weighted_sum += forecast * weight
            total_weight += weight
        
        if total_weight == 0:
            return values[-1] if values else 0.0
        
        return weighted_sum / total_weight
    
    def _linear_trend_forecast(
        self,
        values: List[float],
        periods: int,
    ) -> float:
        """Forecast using linear trend extrapolation."""
        slope, intercept = self._ts_utils.calculate_trend(values)
        n = len(values)
        return intercept + slope * (n - 1 + periods)
    
    def _exponential_forecast(
        self,
        values: List[float],
        periods: int,
    ) -> float:
        """Forecast using Holt's exponential smoothing."""
        return self._ts_utils.holt_linear(
            values,
            alpha=self._config.alpha,
            beta=self._config.beta,
            periods=periods,
        )
    
    def _cohort_forecast(
        self,
        values: List[float],
        periods: int,
        tenant_id: Optional[str],
    ) -> float:
        """Forecast based on cohort behavior."""
        if not values:
            return 0.0
        
        # Get base from recent values
        base = statistics.mean(values[-3:]) if len(values) >= 3 else values[-1]
        
        # Apply cohort adjustments
        if tenant_id and tenant_id in self._profiles:
            profile = self._profiles[tenant_id]
            
            # Churn adjustment
            monthly_churn = profile.churn_probability
            churn_factor = (1 - monthly_churn) ** (periods / 30)
            
            # Expansion adjustment
            monthly_expansion = profile.expansion_probability
            expansion_factor = 1 + (monthly_expansion * periods / 30)
            
            return base * churn_factor * expansion_factor
        
        # Default cohort behavior
        default_churn = self._config.default_churn_rate
        default_expansion = self._config.default_expansion_rate
        
        churn_factor = (1 - default_churn) ** (periods / 30)
        expansion_factor = 1 + (default_expansion * periods / 30)
        
        return base * churn_factor * expansion_factor
    
    def _usage_velocity_forecast(
        self,
        values: List[float],
        periods: int,
        tenant_id: Optional[str],
    ) -> float:
        """Forecast based on usage velocity."""
        if not values:
            return 0.0
        
        # Get usage trend
        usage_trend = 0.0
        if tenant_id and tenant_id in self._profiles:
            usage_trend = self._profiles[tenant_id].usage_trend
        
        # Calculate revenue velocity
        if len(values) >= 2:
            revenue_velocity = (values[-1] - values[0]) / len(values)
        else:
            revenue_velocity = 0
        
        # Combine with usage trend
        adjusted_velocity = revenue_velocity * (1 + usage_trend)
        
        return values[-1] + adjusted_velocity * periods
    
    def _simple_average_forecast(
        self,
        values: List[float],
        periods: int,
    ) -> float:
        """Simple average forecast."""
        if not values:
            return 0.0
        return statistics.mean(values)
    
    def _calculate_components(
        self,
        values: List[float],
        prediction: float,
        tenant_id: Optional[str],
    ) -> Tuple[float, float, float, float]:
        """Calculate forecast components."""
        if not values:
            return 0.0, 0.0, 0.0, 0.0
        
        # Base = recent average
        base = statistics.mean(values[-3:]) if len(values) >= 3 else values[-1]
        
        # Get profile if available
        churn_rate = self._config.default_churn_rate
        expansion_rate = self._config.default_expansion_rate
        
        if tenant_id and tenant_id in self._profiles:
            profile = self._profiles[tenant_id]
            churn_rate = profile.churn_probability
            expansion_rate = profile.expansion_probability
        
        # Calculate components
        churn = base * churn_rate
        expansion = base * expansion_rate
        growth = prediction - base + churn - expansion
        
        return base, growth, churn, expansion
    
    def _calculate_confidence(
        self,
        values: List[float],
        volatility: float,
        tenant_id: Optional[str],
    ) -> Tuple[ForecastConfidence, float]:
        """Calculate confidence level and score."""
        score = 0.5  # Base score
        
        # Data quantity bonus
        if len(values) >= 12:
            score += 0.2
        elif len(values) >= 6:
            score += 0.1
        
        # Volatility penalty
        if volatility < 0.1:
            score += 0.15
        elif volatility < 0.2:
            score += 0.05
        elif volatility > 0.5:
            score -= 0.2
        
        # Profile bonus
        if tenant_id and tenant_id in self._profiles:
            profile = self._profiles[tenant_id]
            if profile.months_active >= 6:
                score += 0.1
            if profile.engagement_score > 0.7:
                score += 0.05
        
        score = max(0, min(1, score))
        
        # Map to confidence level
        if score >= 0.8:
            confidence = ForecastConfidence.HIGH
        elif score >= 0.5:
            confidence = ForecastConfidence.MEDIUM
        elif score > 0.2:
            confidence = ForecastConfidence.LOW
        else:
            confidence = ForecastConfidence.UNCERTAIN
        
        return confidence, score
    
    def _identify_contributing_signals(
        self,
        tenant_id: Optional[str],
    ) -> List[RevenueSignal]:
        """Identify signals contributing to forecast."""
        signals = []
        
        if not tenant_id or tenant_id not in self._profiles:
            return [RevenueSignal.STABLE_USAGE]
        
        profile = self._profiles[tenant_id]
        
        # Usage trend signals
        if profile.usage_trend > 0.05:
            signals.append(RevenueSignal.USAGE_GROWTH)
        elif profile.usage_trend < -0.05:
            signals.append(RevenueSignal.USAGE_DECLINE)
        else:
            signals.append(RevenueSignal.STABLE_USAGE)
        
        # Engagement signals
        if profile.engagement_score > 0.8:
            signals.append(RevenueSignal.ENGAGEMENT_INCREASE)
        elif profile.engagement_score < 0.4:
            signals.append(RevenueSignal.ENGAGEMENT_DECAY)
        
        # Churn signals
        if profile.churn_probability > 0.3:
            signals.append(RevenueSignal.CHURN_INDICATOR)
        
        # Expansion signals
        if profile.expansion_probability > 0.3:
            signals.append(RevenueSignal.FEATURE_ADOPTION)
        
        return signals if signals else [RevenueSignal.STABLE_USAGE]
    
    # =========================================================================
    # Helper Methods
    # =========================================================================
    
    def _get_history_for_forecast(
        self,
        stream: RevenueStream,
        tenant_id: Optional[str],
    ) -> List[RevenueDataPoint]:
        """Get relevant history for forecasting."""
        history = self._revenue_history
        
        # Filter by tenant
        if tenant_id:
            history = [p for p in history if p.tenant_id == tenant_id]
        
        # Filter by stream
        if stream != RevenueStream.TOTAL:
            history = [p for p in history if p.stream == stream]
        
        # Sort by timestamp
        history.sort(key=lambda p: p.timestamp)
        
        return history
    
    def _horizon_to_periods(self, horizon: ForecastHorizon) -> int:
        """Convert horizon to number of periods (days)."""
        return {
            ForecastHorizon.WEEK: 7,
            ForecastHorizon.MONTH: 30,
            ForecastHorizon.QUARTER: 90,
            ForecastHorizon.YEAR: 365,
        }.get(horizon, 30)
    
    def _create_insufficient_data_result(
        self,
        horizon: ForecastHorizon,
        stream: RevenueStream,
        tenant_id: Optional[str],
    ) -> ForecastResult:
        """Create result for insufficient data."""
        self._forecast_counter += 1
        return ForecastResult(
            forecast_id=f"FC-{self._forecast_counter:08d}",
            created_at=datetime.now(),
            horizon=horizon,
            stream=stream,
            tenant_id=tenant_id,
            confidence=ForecastConfidence.UNCERTAIN,
            confidence_score=0.0,
            contributing_signals=[],
        )
    
    # =========================================================================
    # Aggregate Forecasts
    # =========================================================================
    
    def forecast_mrr(
        self,
        horizon: ForecastHorizon = ForecastHorizon.MONTH,
    ) -> ForecastResult:
        """Forecast total MRR."""
        return self.forecast(horizon, RevenueStream.TOTAL)
    
    def forecast_arr(self) -> Decimal:
        """Forecast ARR based on current MRR forecast."""
        mrr_forecast = self.forecast_mrr()
        return mrr_forecast.predicted_amount * Decimal("12")
    
    def forecast_by_tier(
        self,
        horizon: ForecastHorizon = ForecastHorizon.MONTH,
    ) -> Dict[str, ForecastResult]:
        """Forecast revenue by tier."""
        tier_forecasts = {}
        
        # Group profiles by tier
        tiers = set(p.tier for p in self._profiles.values())
        
        for tier in tiers:
            # Get tenants in tier
            tier_tenants = [
                tid for tid, p in self._profiles.items()
                if p.tier == tier
            ]
            
            # Aggregate forecast
            tier_history = [
                p for p in self._revenue_history
                if p.tenant_id in tier_tenants
            ]
            
            if tier_history:
                values = [float(p.amount) for p in tier_history]
                periods = self._horizon_to_periods(horizon)
                prediction = self._ensemble_forecast(values, periods, None)
                
                self._forecast_counter += 1
                tier_forecasts[tier] = ForecastResult(
                    forecast_id=f"FC-{self._forecast_counter:08d}",
                    created_at=datetime.now(),
                    horizon=horizon,
                    stream=RevenueStream.TOTAL,
                    predicted_amount=Decimal(str(round(prediction, 2))),
                )
        
        return tier_forecasts
    
    # =========================================================================
    # Backtesting
    # =========================================================================
    
    def backtest(
        self,
        actual_amount: Decimal,
        forecast_id: str,
    ) -> Optional[float]:
        """
        Backtest a forecast with actual results.
        
        Returns error percentage.
        """
        for forecast in self._forecast_history:
            if forecast.forecast_id == forecast_id:
                forecast.actual_amount = actual_amount
                
                if forecast.predicted_amount != 0:
                    error = float(
                        (actual_amount - forecast.predicted_amount) / forecast.predicted_amount
                    )
                    forecast.error_percent = error * 100
                    return forecast.error_percent
                
                return None
        
        return None
    
    def get_forecast_accuracy(self) -> Dict[str, float]:
        """Get forecast accuracy metrics."""
        backtested = [
            f for f in self._forecast_history
            if f.error_percent is not None
        ]
        
        if not backtested:
            return {}
        
        errors = [abs(f.error_percent) for f in backtested]
        
        return {
            "mean_absolute_error": statistics.mean(errors),
            "median_error": statistics.median(errors),
            "max_error": max(errors),
            "within_10_percent": len([e for e in errors if e <= 10]) / len(errors),
            "within_20_percent": len([e for e in errors if e <= 20]) / len(errors),
            "forecast_count": len(backtested),
        }
    
    # =========================================================================
    # Status
    # =========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get forecaster status."""
        return {
            "tenant_profiles": len(self._profiles),
            "revenue_data_points": len(self._revenue_history),
            "forecasts_generated": self._forecast_counter,
            "backtested_forecasts": len([
                f for f in self._forecast_history if f.actual_amount is not None
            ]),
        }
    
    def get_profile(self, tenant_id: str) -> Optional[TenantRevenueProfile]:
        """Get tenant revenue profile."""
        return self._profiles.get(tenant_id)


# =============================================================================
# Factory Functions
# =============================================================================

def create_revenue_forecaster(
    config: Optional[ForecastConfig] = None,
) -> RevenueForecaster:
    """Create a revenue forecaster."""
    return RevenueForecaster(config)


def create_forecast_config(
    alpha: float = 0.3,
    beta: float = 0.1,
    default_churn_rate: float = 0.05,
    default_expansion_rate: float = 0.03,
) -> ForecastConfig:
    """Create a forecast configuration."""
    return ForecastConfig(
        alpha=alpha,
        beta=beta,
        default_churn_rate=default_churn_rate,
        default_expansion_rate=default_expansion_rate,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "ForecastHorizon",
    "ForecastMethod",
    "RevenueStream",
    "ForecastConfidence",
    "RevenueSignal",
    # Data Classes
    "RevenueDataPoint",
    "ForecastResult",
    "TenantRevenueProfile",
    "ForecastConfig",
    # Utilities
    "TimeSeriesUtils",
    # Classes
    "RevenueForecaster",
    # Factories
    "create_revenue_forecaster",
    "create_forecast_config",
]
