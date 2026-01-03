# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
#
# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.billing_dashboards
# This stub remains for backward compatibility but will be removed in v2.0.
# ----------------------------------------------------------------------

from __future__ import annotations

import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.billing_dashboards is deprecated. "
    "Import from 'app.services.billing.billing_dashboards' instead.",
    DeprecationWarning,
    stacklevel=2
)


"""
KRL Billing Dashboards - Week 24 Day 2
======================================

Dashboard widgets and real-time metrics for billing visualization.
Integrates with krl-dashboard for unified UI experience.

Features:
- Real-time MRR/ARR widgets
- Revenue trend charts
- Subscription health indicators
- Alert status panels
- Executive summary cards
"""


import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, UTC
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class WidgetType(str, Enum):
    """Dashboard widget types."""
    METRIC_CARD = "metric_card"
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    GAUGE = "gauge"
    TABLE = "table"
    HEATMAP = "heatmap"
    ALERT_LIST = "alert_list"


class WidgetSize(str, Enum):
    """Widget size presets."""
    SMALL = "small"      # 1x1
    MEDIUM = "medium"    # 2x1
    LARGE = "large"      # 2x2
    WIDE = "wide"        # 4x1
    TALL = "tall"        # 1x2


class RefreshRate(str, Enum):
    """Widget refresh rates."""
    REAL_TIME = "real_time"  # WebSocket
    FAST = "fast"            # 10 seconds
    NORMAL = "normal"        # 60 seconds
    SLOW = "slow"            # 5 minutes
    MANUAL = "manual"


class TrendDirection(str, Enum):
    """Metric trend direction."""
    UP = "up"
    DOWN = "down"
    FLAT = "flat"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class MetricValue:
    """Single metric value with trend."""
    value: Any
    formatted: str
    trend_direction: TrendDirection
    trend_percentage: float
    trend_period: str = "vs last period"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ChartDataPoint:
    """Single data point for charts."""
    label: str
    value: float
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChartSeries:
    """Series of data points."""
    name: str
    data: List[ChartDataPoint]
    color: Optional[str] = None


@dataclass
class WidgetConfig:
    """Widget configuration."""
    widget_id: str
    widget_type: WidgetType
    title: str
    size: WidgetSize = WidgetSize.MEDIUM
    refresh_rate: RefreshRate = RefreshRate.NORMAL
    position: Dict[str, int] = field(default_factory=lambda: {"row": 0, "col": 0})
    
    # Type-specific config
    metric_key: Optional[str] = None
    chart_series: List[ChartSeries] = field(default_factory=list)
    table_columns: List[str] = field(default_factory=list)
    
    # Styling
    show_trend: bool = True
    show_sparkline: bool = False
    custom_colors: Dict[str, str] = field(default_factory=dict)


@dataclass
class DashboardLayout:
    """Dashboard layout configuration."""
    dashboard_id: str
    name: str
    widgets: List[WidgetConfig]
    columns: int = 4
    row_height: int = 150
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class WidgetData:
    """Widget render data."""
    widget_id: str
    widget_type: WidgetType
    title: str
    data: Any
    last_updated: datetime
    error: Optional[str] = None


# =============================================================================
# Widget Definitions
# =============================================================================

class BillingWidgets:
    """
    Pre-defined billing dashboard widgets.
    
    Provides standardized widgets for common billing metrics.
    """
    
    @staticmethod
    def mrr_card() -> WidgetConfig:
        """MRR metric card."""
        return WidgetConfig(
            widget_id="mrr_card",
            widget_type=WidgetType.METRIC_CARD,
            title="Monthly Recurring Revenue",
            size=WidgetSize.MEDIUM,
            refresh_rate=RefreshRate.NORMAL,
            metric_key="mrr",
            show_trend=True,
        )
    
    @staticmethod
    def arr_card() -> WidgetConfig:
        """ARR metric card."""
        return WidgetConfig(
            widget_id="arr_card",
            widget_type=WidgetType.METRIC_CARD,
            title="Annual Recurring Revenue",
            size=WidgetSize.MEDIUM,
            refresh_rate=RefreshRate.NORMAL,
            metric_key="arr",
            show_trend=True,
        )
    
    @staticmethod
    def active_customers_card() -> WidgetConfig:
        """Active customers metric card."""
        return WidgetConfig(
            widget_id="active_customers",
            widget_type=WidgetType.METRIC_CARD,
            title="Active Customers",
            size=WidgetSize.SMALL,
            refresh_rate=RefreshRate.NORMAL,
            metric_key="active_customers",
        )
    
    @staticmethod
    def churn_rate_gauge() -> WidgetConfig:
        """Churn rate gauge widget."""
        return WidgetConfig(
            widget_id="churn_gauge",
            widget_type=WidgetType.GAUGE,
            title="Churn Rate",
            size=WidgetSize.SMALL,
            metric_key="churn_rate",
            custom_colors={
                "low": "#10b981",    # Green < 3%
                "medium": "#f59e0b", # Yellow 3-5%
                "high": "#ef4444",   # Red > 5%
            },
        )
    
    @staticmethod
    def mrr_trend_chart() -> WidgetConfig:
        """MRR trend line chart."""
        return WidgetConfig(
            widget_id="mrr_trend",
            widget_type=WidgetType.LINE_CHART,
            title="MRR Trend (12 Months)",
            size=WidgetSize.LARGE,
            refresh_rate=RefreshRate.SLOW,
            metric_key="mrr_trend",
        )
    
    @staticmethod
    def tier_distribution_pie() -> WidgetConfig:
        """Revenue by tier pie chart."""
        return WidgetConfig(
            widget_id="tier_distribution",
            widget_type=WidgetType.PIE_CHART,
            title="Revenue by Tier",
            size=WidgetSize.MEDIUM,
            metric_key="tier_breakdown",
        )
    
    @staticmethod
    def recent_alerts_list() -> WidgetConfig:
        """Recent billing alerts."""
        return WidgetConfig(
            widget_id="recent_alerts",
            widget_type=WidgetType.ALERT_LIST,
            title="Recent Alerts",
            size=WidgetSize.TALL,
            refresh_rate=RefreshRate.FAST,
            metric_key="billing_alerts",
        )
    
    @staticmethod
    def mrr_movement_bar() -> WidgetConfig:
        """MRR movement breakdown bar chart."""
        return WidgetConfig(
            widget_id="mrr_movement",
            widget_type=WidgetType.BAR_CHART,
            title="MRR Movement",
            size=WidgetSize.WIDE,
            metric_key="mrr_movement",
            custom_colors={
                "new": "#10b981",
                "expansion": "#3b82f6",
                "contraction": "#f59e0b",
                "churn": "#ef4444",
            },
        )
    
    @staticmethod
    def executive_layout() -> DashboardLayout:
        """Executive dashboard layout."""
        return DashboardLayout(
            dashboard_id="executive_billing",
            name="Executive Billing Dashboard",
            columns=4,
            widgets=[
                BillingWidgets.mrr_card(),
                BillingWidgets.arr_card(),
                BillingWidgets.active_customers_card(),
                BillingWidgets.churn_rate_gauge(),
                BillingWidgets.mrr_trend_chart(),
                BillingWidgets.tier_distribution_pie(),
                BillingWidgets.mrr_movement_bar(),
                BillingWidgets.recent_alerts_list(),
            ],
        )


# =============================================================================
# Widget Data Provider
# =============================================================================

class WidgetDataProvider:
    """
    Provides data for dashboard widgets.
    
    Integrates with RevenueReportingEngine and other billing components.
    """
    
    def __init__(self):
        self._data_sources: Dict[str, Callable] = {}
        self._cache: Dict[str, WidgetData] = {}
        self._cache_ttl: Dict[str, datetime] = {}
    
    def register_data_source(self, metric_key: str, provider: Callable) -> None:
        """Register data source for metric."""
        self._data_sources[metric_key] = provider
        logger.debug(f"Registered data source: {metric_key}")
    
    def get_widget_data(self, widget: WidgetConfig) -> WidgetData:
        """Get data for widget."""
        if not widget.metric_key:
            return self._empty_widget_data(widget)
        
        # Check cache
        cache_key = f"{widget.widget_id}:{widget.metric_key}"
        if self._is_cache_valid(cache_key, widget.refresh_rate):
            return self._cache[cache_key]
        
        # Fetch fresh data
        try:
            if widget.metric_key in self._data_sources:
                raw_data = self._data_sources[widget.metric_key]()
                data = self._transform_data(widget, raw_data)
            else:
                data = self._get_mock_data(widget)
            
            widget_data = WidgetData(
                widget_id=widget.widget_id,
                widget_type=widget.widget_type,
                title=widget.title,
                data=data,
                last_updated=datetime.now(timezone.utc),
            )
            
            # Update cache
            self._cache[cache_key] = widget_data
            self._cache_ttl[cache_key] = datetime.now(timezone.utc)
            
            return widget_data
            
        except Exception as e:
            logger.error(f"Error fetching widget data: {e}")
            return WidgetData(
                widget_id=widget.widget_id,
                widget_type=widget.widget_type,
                title=widget.title,
                data=None,
                last_updated=datetime.now(timezone.utc),
                error=str(e),
            )
    
    def _is_cache_valid(self, cache_key: str, refresh_rate: RefreshRate) -> bool:
        """Check if cached data is still valid."""
        if cache_key not in self._cache_ttl:
            return False
        
        ttl_seconds = {
            RefreshRate.REAL_TIME: 1,
            RefreshRate.FAST: 10,
            RefreshRate.NORMAL: 60,
            RefreshRate.SLOW: 300,
            RefreshRate.MANUAL: 3600,
        }
        
        age = (datetime.now(timezone.utc) - self._cache_ttl[cache_key]).total_seconds()
        return age < ttl_seconds.get(refresh_rate, 60)
    
    def _transform_data(self, widget: WidgetConfig, raw_data: Any) -> Any:
        """Transform raw data for widget type."""
        if widget.widget_type == WidgetType.METRIC_CARD:
            return self._transform_metric_card(raw_data)
        elif widget.widget_type == WidgetType.LINE_CHART:
            return self._transform_line_chart(raw_data)
        elif widget.widget_type == WidgetType.PIE_CHART:
            return self._transform_pie_chart(raw_data)
        elif widget.widget_type == WidgetType.BAR_CHART:
            return self._transform_bar_chart(raw_data)
        return raw_data
    
    def _transform_metric_card(self, raw_data: Any) -> MetricValue:
        """Transform data for metric card."""
        if isinstance(raw_data, dict):
            return MetricValue(
                value=raw_data.get("value", 0),
                formatted=raw_data.get("formatted", str(raw_data.get("value", 0))),
                trend_direction=TrendDirection(raw_data.get("trend", "flat")),
                trend_percentage=raw_data.get("trend_pct", 0.0),
            )
        return MetricValue(
            value=raw_data,
            formatted=str(raw_data),
            trend_direction=TrendDirection.FLAT,
            trend_percentage=0.0,
        )
    
    def _transform_line_chart(self, raw_data: Any) -> List[ChartSeries]:
        """Transform data for line chart."""
        if isinstance(raw_data, list):
            return [ChartSeries(
                name="primary",
                data=[ChartDataPoint(label=str(i), value=v) for i, v in enumerate(raw_data)],
            )]
        return []
    
    def _transform_pie_chart(self, raw_data: Any) -> List[ChartDataPoint]:
        """Transform data for pie chart."""
        if isinstance(raw_data, dict):
            return [ChartDataPoint(label=k, value=v) for k, v in raw_data.items()]
        return []
    
    def _transform_bar_chart(self, raw_data: Any) -> List[ChartDataPoint]:
        """Transform data for bar chart."""
        if isinstance(raw_data, dict):
            return [ChartDataPoint(label=k, value=v) for k, v in raw_data.items()]
        return []
    
    def _empty_widget_data(self, widget: WidgetConfig) -> WidgetData:
        """Return empty widget data."""
        return WidgetData(
            widget_id=widget.widget_id,
            widget_type=widget.widget_type,
            title=widget.title,
            data=None,
            last_updated=datetime.now(timezone.utc),
        )
    
    def _get_mock_data(self, widget: WidgetConfig) -> Any:
        """Get mock data for development."""
        mock_data = {
            "mrr": {"value": 125000, "formatted": "$125,000", "trend": "up", "trend_pct": 5.2},
            "arr": {"value": 1500000, "formatted": "$1.5M", "trend": "up", "trend_pct": 5.2},
            "active_customers": {"value": 450, "formatted": "450", "trend": "up", "trend_pct": 3.1},
            "churn_rate": {"value": 2.1, "formatted": "2.1%", "trend": "down", "trend_pct": -0.3},
            "mrr_trend": [100000, 105000, 108000, 112000, 118000, 125000],
            "tier_breakdown": {"Enterprise": 65000, "Pro": 45000, "Community": 15000},
            "mrr_movement": {"new": 8000, "expansion": 5000, "contraction": -2000, "churn": -3000},
        }
        return mock_data.get(widget.metric_key, None)


# =============================================================================
# Dashboard Manager
# =============================================================================

class BillingDashboardManager:
    """
    Manages billing dashboards and widget lifecycle.
    
    Features:
    - Dashboard CRUD operations
    - Widget data aggregation
    - Real-time updates
    - Layout persistence
    """
    
    def __init__(self, data_provider: Optional[WidgetDataProvider] = None):
        self.data_provider = data_provider or WidgetDataProvider()
        self._dashboards: Dict[str, DashboardLayout] = {}
        self._active_subscriptions: Dict[str, List[str]] = {}  # dashboard_id -> [client_ids]
    
    def create_dashboard(
        self,
        name: str,
        widgets: Optional[List[WidgetConfig]] = None,
    ) -> DashboardLayout:
        """Create new dashboard."""
        dashboard = DashboardLayout(
            dashboard_id=uuid4().hex,
            name=name,
            widgets=widgets or [],
        )
        self._dashboards[dashboard.dashboard_id] = dashboard
        logger.info(f"Created dashboard: {name}")
        return dashboard
    
    def get_dashboard(self, dashboard_id: str) -> Optional[DashboardLayout]:
        """Get dashboard by ID."""
        return self._dashboards.get(dashboard_id)
    
    def add_widget(self, dashboard_id: str, widget: WidgetConfig) -> bool:
        """Add widget to dashboard."""
        dashboard = self._dashboards.get(dashboard_id)
        if not dashboard:
            return False
        
        dashboard.widgets.append(widget)
        dashboard.updated_at = datetime.now(timezone.utc)
        return True
    
    def remove_widget(self, dashboard_id: str, widget_id: str) -> bool:
        """Remove widget from dashboard."""
        dashboard = self._dashboards.get(dashboard_id)
        if not dashboard:
            return False
        
        dashboard.widgets = [w for w in dashboard.widgets if w.widget_id != widget_id]
        dashboard.updated_at = datetime.now(timezone.utc)
        return True
    
    def get_dashboard_data(self, dashboard_id: str) -> Dict[str, WidgetData]:
        """Get all widget data for dashboard."""
        dashboard = self._dashboards.get(dashboard_id)
        if not dashboard:
            return {}
        
        return {
            widget.widget_id: self.data_provider.get_widget_data(widget)
            for widget in dashboard.widgets
        }
    
    def get_executive_dashboard(self) -> DashboardLayout:
        """Get or create executive dashboard."""
        exec_id = "executive_billing"
        if exec_id not in self._dashboards:
            layout = BillingWidgets.executive_layout()
            self._dashboards[exec_id] = layout
        return self._dashboards[exec_id]
    
    def export_layout(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """Export dashboard layout as JSON."""
        dashboard = self._dashboards.get(dashboard_id)
        if not dashboard:
            return None
        
        return {
            "dashboard_id": dashboard.dashboard_id,
            "name": dashboard.name,
            "columns": dashboard.columns,
            "row_height": dashboard.row_height,
            "widgets": [
                {
                    "widget_id": w.widget_id,
                    "widget_type": w.widget_type.value,
                    "title": w.title,
                    "size": w.size.value,
                    "position": w.position,
                    "metric_key": w.metric_key,
                }
                for w in dashboard.widgets
            ],
        }


# =============================================================================
# Factory Function
# =============================================================================

def create_billing_dashboard_manager() -> BillingDashboardManager:
    """Create configured BillingDashboardManager."""
    provider = WidgetDataProvider()
    return BillingDashboardManager(data_provider=provider)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "WidgetType",
    "WidgetSize",
    "RefreshRate",
    "TrendDirection",
    # Data Classes
    "MetricValue",
    "ChartDataPoint",
    "ChartSeries",
    "WidgetConfig",
    "DashboardLayout",
    "WidgetData",
    # Classes
    "BillingWidgets",
    "WidgetDataProvider",
    "BillingDashboardManager",
    # Factory
    "create_billing_dashboard_manager",
]
