"""
KRL Contract Enforcement Layer - DEPRECATED

⚠️ DEPRECATION WARNING (Dec 2025):
This module has been moved to krl-premium-backend.
Import from: app.services.billing.contract_enforcement

This stub remains for backward compatibility but will be removed in v2.0.
"""

from __future__ import annotations

import warnings
warnings.warn(
    "krl_data_connectors.core.billing.contract_enforcement is deprecated. "
    "This module has moved to krl-premium-backend. "
    "Import from 'app.services.billing.contract_enforcement' instead.",
    DeprecationWarning,
    stacklevel=2
)

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, UTC
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class ContractType(str, Enum):
    """Types of contracts."""
    STANDARD = "standard"           # Standard terms
    ENTERPRISE = "enterprise"       # Custom enterprise terms
    NEGOTIATED = "negotiated"       # Specially negotiated
    RESELLER = "reseller"           # Reseller agreement
    GOVERNMENT = "government"       # Government contract


class CommitmentType(str, Enum):
    """Types of usage commitments."""
    MINIMUM_SPEND = "minimum_spend"
    MINIMUM_USAGE = "minimum_usage"
    PREPAID_CREDITS = "prepaid_credits"
    VOLUME_COMMITMENT = "volume_commitment"


class SLAMetric(str, Enum):
    """SLA metrics to track."""
    UPTIME = "uptime"
    RESPONSE_TIME = "response_time"
    SUPPORT_RESPONSE = "support_response"
    API_LATENCY = "api_latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"


class SLATier(str, Enum):
    """SLA tier levels."""
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    PLATINUM = "platinum"


class BreachSeverity(str, Enum):
    """SLA breach severity."""
    WARNING = "warning"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class ContractStatus(str, Enum):
    """Contract lifecycle status."""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    RENEWED = "renewed"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class SLADefinition:
    """SLA definition with targets."""
    metric: SLAMetric
    target_value: float
    measurement_unit: str
    measurement_period: str  # hourly, daily, monthly
    breach_threshold: float
    penalty_percentage: float = 0.0
    credit_eligible: bool = True


@dataclass
class SLAMeasurement:
    """Single SLA measurement."""
    measurement_id: str
    metric: SLAMetric
    measured_value: float
    target_value: float
    period_start: datetime
    period_end: datetime
    is_breach: bool
    breach_severity: Optional[BreachSeverity] = None


@dataclass
class SLABreach:
    """SLA breach record."""
    breach_id: str
    contract_id: str
    metric: SLAMetric
    severity: BreachSeverity
    target_value: float
    actual_value: float
    breach_start: datetime
    breach_end: Optional[datetime] = None
    credit_amount: Decimal = Decimal("0")
    acknowledged: bool = False
    resolution_notes: str = ""


@dataclass
class UsageCommitment:
    """Usage commitment terms."""
    commitment_id: str
    commitment_type: CommitmentType
    committed_value: Decimal
    period_start: datetime
    period_end: datetime
    current_usage: Decimal = Decimal("0")
    rollover_allowed: bool = False
    overage_rate: Optional[Decimal] = None


@dataclass
class ContractTerms:
    """Contract terms definition."""
    contract_id: str
    contract_type: ContractType
    customer_id: str
    tenant_id: str
    
    # Dates
    effective_date: datetime
    expiration_date: datetime
    renewal_date: Optional[datetime] = None
    auto_renew: bool = False
    
    # Pricing
    annual_value: Decimal = Decimal("0")
    payment_terms_days: int = 30
    discount_percentage: float = 0.0
    
    # SLAs
    sla_tier: SLATier = SLATier.STANDARD
    slas: List[SLADefinition] = field(default_factory=list)
    
    # Commitments
    commitments: List[UsageCommitment] = field(default_factory=list)
    
    # Status
    status: ContractStatus = ContractStatus.DRAFT
    
    # Custom terms
    custom_terms: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContractHealth:
    """Contract health assessment."""
    contract_id: str
    overall_health: str  # healthy, at_risk, breached
    sla_compliance_rate: float
    commitment_utilization: float
    days_until_expiration: int
    active_breaches: int
    total_credits_issued: Decimal
    renewal_risk: str  # low, medium, high


# =============================================================================
# SLA Definitions by Tier
# =============================================================================

DEFAULT_SLAS: Dict[SLATier, List[SLADefinition]] = {
    SLATier.STANDARD: [
        SLADefinition(
            metric=SLAMetric.UPTIME,
            target_value=99.0,
            measurement_unit="percent",
            measurement_period="monthly",
            breach_threshold=98.0,
            penalty_percentage=5.0,
        ),
        SLADefinition(
            metric=SLAMetric.SUPPORT_RESPONSE,
            target_value=24,
            measurement_unit="hours",
            measurement_period="per_ticket",
            breach_threshold=48,
            penalty_percentage=0.0,
        ),
    ],
    SLATier.ENTERPRISE: [
        SLADefinition(
            metric=SLAMetric.UPTIME,
            target_value=99.9,
            measurement_unit="percent",
            measurement_period="monthly",
            breach_threshold=99.5,
            penalty_percentage=10.0,
        ),
        SLADefinition(
            metric=SLAMetric.SUPPORT_RESPONSE,
            target_value=4,
            measurement_unit="hours",
            measurement_period="per_ticket",
            breach_threshold=8,
            penalty_percentage=5.0,
        ),
        SLADefinition(
            metric=SLAMetric.API_LATENCY,
            target_value=200,
            measurement_unit="milliseconds",
            measurement_period="daily",
            breach_threshold=500,
            penalty_percentage=5.0,
        ),
    ],
    SLATier.PLATINUM: [
        SLADefinition(
            metric=SLAMetric.UPTIME,
            target_value=99.99,
            measurement_unit="percent",
            measurement_period="monthly",
            breach_threshold=99.9,
            penalty_percentage=15.0,
        ),
        SLADefinition(
            metric=SLAMetric.SUPPORT_RESPONSE,
            target_value=1,
            measurement_unit="hours",
            measurement_period="per_ticket",
            breach_threshold=2,
            penalty_percentage=10.0,
        ),
        SLADefinition(
            metric=SLAMetric.API_LATENCY,
            target_value=100,
            measurement_unit="milliseconds",
            measurement_period="daily",
            breach_threshold=200,
            penalty_percentage=10.0,
        ),
    ],
}


# =============================================================================
# SLA Tracker
# =============================================================================

class SLATracker:
    """
    Tracks SLA compliance and detects breaches.
    
    Features:
    - Real-time metric tracking
    - Breach detection
    - Credit calculation
    - Historical analysis
    """
    
    def __init__(self):
        self._measurements: Dict[str, List[SLAMeasurement]] = {}  # contract_id -> measurements
        self._breaches: Dict[str, List[SLABreach]] = {}  # contract_id -> breaches
        self._active_breaches: Dict[str, Dict[SLAMetric, SLABreach]] = {}  # contract -> metric -> breach
    
    def record_measurement(
        self,
        contract_id: str,
        contract: ContractTerms,
        metric: SLAMetric,
        value: float,
        period_start: datetime,
        period_end: datetime,
    ) -> SLAMeasurement:
        """Record SLA measurement and check for breach."""
        # Find matching SLA definition
        sla_def = next(
            (s for s in contract.slas if s.metric == metric),
            None
        )
        
        if not sla_def:
            raise ValueError(f"No SLA definition for metric {metric.value}")
        
        # Check for breach
        is_breach = False
        breach_severity = None
        
        if metric in (SLAMetric.UPTIME,):
            # Higher is better
            is_breach = value < sla_def.breach_threshold
        else:
            # Lower is better (response time, latency, etc.)
            is_breach = value > sla_def.breach_threshold
        
        if is_breach:
            breach_severity = self._calculate_severity(sla_def, value)
        
        measurement = SLAMeasurement(
            measurement_id=uuid4().hex,
            metric=metric,
            measured_value=value,
            target_value=sla_def.target_value,
            period_start=period_start,
            period_end=period_end,
            is_breach=is_breach,
            breach_severity=breach_severity,
        )
        
        # Store measurement
        if contract_id not in self._measurements:
            self._measurements[contract_id] = []
        self._measurements[contract_id].append(measurement)
        
        # Handle breach
        if is_breach:
            self._handle_breach(contract_id, contract, sla_def, measurement)
        
        return measurement
    
    def _calculate_severity(self, sla_def: SLADefinition, value: float) -> BreachSeverity:
        """Calculate breach severity based on deviation."""
        target = sla_def.target_value
        threshold = sla_def.breach_threshold
        
        # Calculate deviation percentage
        if sla_def.metric in (SLAMetric.UPTIME,):
            deviation = (threshold - value) / threshold * 100
        else:
            deviation = (value - threshold) / threshold * 100
        
        if deviation > 50:
            return BreachSeverity.CRITICAL
        elif deviation > 20:
            return BreachSeverity.MAJOR
        elif deviation > 10:
            return BreachSeverity.MINOR
        return BreachSeverity.WARNING
    
    def _handle_breach(
        self,
        contract_id: str,
        contract: ContractTerms,
        sla_def: SLADefinition,
        measurement: SLAMeasurement,
    ) -> None:
        """Handle SLA breach."""
        if contract_id not in self._active_breaches:
            self._active_breaches[contract_id] = {}
        
        # Check if breach is ongoing
        if sla_def.metric in self._active_breaches[contract_id]:
            # Update existing breach
            breach = self._active_breaches[contract_id][sla_def.metric]
            if measurement.breach_severity and breach.severity:
                # Escalate if worse
                severities = list(BreachSeverity)
                if severities.index(measurement.breach_severity) > severities.index(breach.severity):
                    breach.severity = measurement.breach_severity
        else:
            # Create new breach
            credit = self._calculate_credit(contract, sla_def)
            
            breach = SLABreach(
                breach_id=uuid4().hex,
                contract_id=contract_id,
                metric=sla_def.metric,
                severity=measurement.breach_severity or BreachSeverity.WARNING,
                target_value=sla_def.target_value,
                actual_value=measurement.measured_value,
                breach_start=measurement.period_start,
                credit_amount=credit,
            )
            
            self._active_breaches[contract_id][sla_def.metric] = breach
            
            if contract_id not in self._breaches:
                self._breaches[contract_id] = []
            self._breaches[contract_id].append(breach)
            
            logger.warning(
                f"SLA breach detected: {contract_id} - {sla_def.metric.value} "
                f"({measurement.measured_value} vs target {sla_def.target_value})"
            )
    
    def _calculate_credit(
        self,
        contract: ContractTerms,
        sla_def: SLADefinition,
    ) -> Decimal:
        """Calculate credit for SLA breach."""
        if not sla_def.credit_eligible:
            return Decimal("0")
        
        monthly_value = contract.annual_value / 12
        credit = monthly_value * Decimal(str(sla_def.penalty_percentage / 100))
        return credit.quantize(Decimal("0.01"))
    
    def resolve_breach(
        self,
        contract_id: str,
        metric: SLAMetric,
        resolution_notes: str,
    ) -> Optional[SLABreach]:
        """Resolve an active breach."""
        if contract_id not in self._active_breaches:
            return None
        
        if metric not in self._active_breaches[contract_id]:
            return None
        
        breach = self._active_breaches[contract_id][metric]
        breach.breach_end = datetime.now(timezone.utc)
        breach.acknowledged = True
        breach.resolution_notes = resolution_notes
        
        del self._active_breaches[contract_id][metric]
        return breach
    
    def get_compliance_rate(
        self,
        contract_id: str,
        metric: Optional[SLAMetric] = None,
    ) -> float:
        """Calculate SLA compliance rate."""
        measurements = self._measurements.get(contract_id, [])
        
        if metric:
            measurements = [m for m in measurements if m.metric == metric]
        
        if not measurements:
            return 100.0
        
        compliant = sum(1 for m in measurements if not m.is_breach)
        return (compliant / len(measurements)) * 100
    
    def get_active_breaches(self, contract_id: str) -> List[SLABreach]:
        """Get active breaches for contract."""
        return list(self._active_breaches.get(contract_id, {}).values())


# =============================================================================
# Commitment Tracker
# =============================================================================

class CommitmentTracker:
    """
    Tracks usage against commitments.
    
    Features:
    - Usage tracking vs commitment
    - Overage calculation
    - Rollover handling
    - Commitment renewal
    """
    
    def __init__(self):
        self._usage: Dict[str, Dict[str, Decimal]] = {}  # commitment_id -> {metric: usage}
    
    def record_usage(
        self,
        commitment: UsageCommitment,
        usage_amount: Decimal,
        metric: str = "default",
    ) -> Dict[str, Any]:
        """Record usage against commitment."""
        if commitment.commitment_id not in self._usage:
            self._usage[commitment.commitment_id] = {}
        
        current = self._usage[commitment.commitment_id].get(metric, Decimal("0"))
        new_usage = current + usage_amount
        self._usage[commitment.commitment_id][metric] = new_usage
        
        commitment.current_usage = new_usage
        
        # Calculate utilization
        utilization = float(new_usage / commitment.committed_value * 100) if commitment.committed_value > 0 else 0
        
        # Calculate overage
        overage = max(Decimal("0"), new_usage - commitment.committed_value)
        overage_cost = Decimal("0")
        if overage > 0 and commitment.overage_rate:
            overage_cost = overage * commitment.overage_rate
        
        return {
            "commitment_id": commitment.commitment_id,
            "current_usage": str(new_usage),
            "committed_value": str(commitment.committed_value),
            "utilization_percent": utilization,
            "overage": str(overage),
            "overage_cost": str(overage_cost),
        }
    
    def get_utilization(self, commitment: UsageCommitment) -> float:
        """Get commitment utilization percentage."""
        if commitment.committed_value == 0:
            return 0.0
        return float(commitment.current_usage / commitment.committed_value * 100)
    
    def check_commitment_status(
        self,
        commitment: UsageCommitment,
    ) -> Dict[str, Any]:
        """Check commitment status."""
        now = datetime.now(timezone.utc)
        days_remaining = (commitment.period_end - now).days
        utilization = self.get_utilization(commitment)
        
        # Expected utilization based on time elapsed
        total_days = (commitment.period_end - commitment.period_start).days
        elapsed_days = (now - commitment.period_start).days
        expected_utilization = (elapsed_days / total_days * 100) if total_days > 0 else 0
        
        # Status assessment
        if utilization < expected_utilization * 0.5:
            status = "underutilized"
        elif utilization > 100:
            status = "exceeded"
        elif utilization > expected_utilization * 1.2:
            status = "trending_over"
        else:
            status = "on_track"
        
        return {
            "commitment_id": commitment.commitment_id,
            "status": status,
            "current_utilization": utilization,
            "expected_utilization": expected_utilization,
            "days_remaining": days_remaining,
            "committed_value": str(commitment.committed_value),
            "current_usage": str(commitment.current_usage),
        }


# =============================================================================
# Contract Enforcement Engine
# =============================================================================

class ContractEnforcementEngine:
    """
    Main contract enforcement engine.
    
    Coordinates:
    - Contract management
    - SLA tracking
    - Commitment tracking
    - Renewal management
    """
    
    def __init__(self):
        self.sla_tracker = SLATracker()
        self.commitment_tracker = CommitmentTracker()
        
        self._contracts: Dict[str, ContractTerms] = {}
        self._renewal_handlers: List[Callable[[ContractTerms], None]] = []
    
    def create_contract(
        self,
        customer_id: str,
        tenant_id: str,
        contract_type: ContractType,
        sla_tier: SLATier,
        effective_date: datetime,
        duration_months: int = 12,
        annual_value: Decimal = Decimal("0"),
        commitments: Optional[List[UsageCommitment]] = None,
        custom_terms: Optional[Dict[str, Any]] = None,
    ) -> ContractTerms:
        """Create new contract."""
        contract_id = uuid4().hex
        expiration_date = effective_date + timedelta(days=duration_months * 30)
        
        # Get default SLAs for tier
        slas = DEFAULT_SLAS.get(sla_tier, DEFAULT_SLAS[SLATier.STANDARD]).copy()
        
        contract = ContractTerms(
            contract_id=contract_id,
            contract_type=contract_type,
            customer_id=customer_id,
            tenant_id=tenant_id,
            effective_date=effective_date,
            expiration_date=expiration_date,
            annual_value=annual_value,
            sla_tier=sla_tier,
            slas=slas,
            commitments=commitments or [],
            status=ContractStatus.DRAFT,
            custom_terms=custom_terms or {},
        )
        
        self._contracts[contract_id] = contract
        logger.info(f"Created contract {contract_id} for customer {customer_id}")
        return contract
    
    def activate_contract(self, contract_id: str) -> ContractTerms:
        """Activate a draft contract."""
        contract = self._contracts.get(contract_id)
        if not contract:
            raise ValueError(f"Unknown contract: {contract_id}")
        
        if contract.status != ContractStatus.DRAFT:
            raise ValueError(f"Contract is not in draft status: {contract.status}")
        
        contract.status = ContractStatus.ACTIVE
        logger.info(f"Activated contract {contract_id}")
        return contract
    
    def record_sla_metric(
        self,
        contract_id: str,
        metric: SLAMetric,
        value: float,
        period_start: datetime,
        period_end: datetime,
    ) -> SLAMeasurement:
        """Record SLA metric measurement."""
        contract = self._contracts.get(contract_id)
        if not contract:
            raise ValueError(f"Unknown contract: {contract_id}")
        
        return self.sla_tracker.record_measurement(
            contract_id=contract_id,
            contract=contract,
            metric=metric,
            value=value,
            period_start=period_start,
            period_end=period_end,
        )
    
    def record_usage(
        self,
        contract_id: str,
        commitment_id: str,
        usage_amount: Decimal,
    ) -> Dict[str, Any]:
        """Record usage against commitment."""
        contract = self._contracts.get(contract_id)
        if not contract:
            raise ValueError(f"Unknown contract: {contract_id}")
        
        commitment = next(
            (c for c in contract.commitments if c.commitment_id == commitment_id),
            None
        )
        
        if not commitment:
            raise ValueError(f"Unknown commitment: {commitment_id}")
        
        return self.commitment_tracker.record_usage(commitment, usage_amount)
    
    def get_contract_health(self, contract_id: str) -> ContractHealth:
        """Get contract health assessment."""
        contract = self._contracts.get(contract_id)
        if not contract:
            raise ValueError(f"Unknown contract: {contract_id}")
        
        now = datetime.now(timezone.utc)
        
        # SLA compliance
        sla_compliance = self.sla_tracker.get_compliance_rate(contract_id)
        
        # Active breaches
        active_breaches = self.sla_tracker.get_active_breaches(contract_id)
        
        # Total credits
        all_breaches = self.sla_tracker._breaches.get(contract_id, [])
        total_credits = sum(b.credit_amount for b in all_breaches)
        
        # Commitment utilization
        avg_utilization = 0.0
        if contract.commitments:
            utilizations = [
                self.commitment_tracker.get_utilization(c)
                for c in contract.commitments
            ]
            avg_utilization = sum(utilizations) / len(utilizations)
        
        # Days until expiration
        days_until_exp = (contract.expiration_date - now).days
        
        # Overall health
        if len(active_breaches) > 0 or sla_compliance < 95:
            overall_health = "breached"
        elif sla_compliance < 99 or avg_utilization < 50:
            overall_health = "at_risk"
        else:
            overall_health = "healthy"
        
        # Renewal risk
        if overall_health == "breached" or days_until_exp < 30:
            renewal_risk = "high"
        elif overall_health == "at_risk" or days_until_exp < 90:
            renewal_risk = "medium"
        else:
            renewal_risk = "low"
        
        return ContractHealth(
            contract_id=contract_id,
            overall_health=overall_health,
            sla_compliance_rate=sla_compliance,
            commitment_utilization=avg_utilization,
            days_until_expiration=days_until_exp,
            active_breaches=len(active_breaches),
            total_credits_issued=total_credits,
            renewal_risk=renewal_risk,
        )
    
    def check_renewals(self, days_ahead: int = 90) -> List[ContractTerms]:
        """Get contracts due for renewal."""
        now = datetime.now(timezone.utc)
        cutoff = now + timedelta(days=days_ahead)
        
        due_for_renewal = [
            c for c in self._contracts.values()
            if c.status == ContractStatus.ACTIVE
            and c.expiration_date <= cutoff
        ]
        
        return sorted(due_for_renewal, key=lambda x: x.expiration_date)
    
    def on_renewal_due(self, handler: Callable[[ContractTerms], None]) -> None:
        """Register renewal due handler."""
        self._renewal_handlers.append(handler)
    
    def get_contract(self, contract_id: str) -> Optional[ContractTerms]:
        """Get contract by ID."""
        return self._contracts.get(contract_id)


# =============================================================================
# Factory Function
# =============================================================================

def create_contract_enforcement_engine() -> ContractEnforcementEngine:
    """Create configured ContractEnforcementEngine."""
    return ContractEnforcementEngine()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "ContractType",
    "CommitmentType",
    "SLAMetric",
    "SLATier",
    "BreachSeverity",
    "ContractStatus",
    # Data Classes
    "SLADefinition",
    "SLAMeasurement",
    "SLABreach",
    "UsageCommitment",
    "ContractTerms",
    "ContractHealth",
    # Constants
    "DEFAULT_SLAS",
    # Classes
    "SLATracker",
    "CommitmentTracker",
    "ContractEnforcementEngine",
    # Factory
    "create_contract_enforcement_engine",
]
