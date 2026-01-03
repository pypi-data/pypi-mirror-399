# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.contracts
# This stub remains for backward compatibility but will be removed in v2.0.
import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.contracts is deprecated. "
    "Import from 'app.services.billing.contracts' instead.",
    DeprecationWarning,
    stacklevel=2
)

"""
Multi-Year Contract Management System for KRL.

This module implements enterprise contract management including:
- Multi-year commitment structures with volume discounts
- Prepaid credit systems with flexible drawdown
- Enterprise terms and SLA management
- Contract lifecycle tracking
- Renewal automation and churn reduction

Part of Phase 1 pricing strategy implementation.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum, auto
from typing import Any, Optional
from uuid import uuid4
import json


class ContractType(Enum):
    """Contract commitment types with associated discounts."""
    MONTHLY = auto()      # Standard month-to-month
    ANNUAL = auto()       # 1-year commitment
    MULTI_YEAR_2 = auto() # 2-year commitment
    MULTI_YEAR_3 = auto() # 3-year commitment
    ENTERPRISE = auto()   # Custom enterprise terms


class ContractStatus(Enum):
    """Contract lifecycle states."""
    DRAFT = auto()        # Being negotiated
    PENDING = auto()      # Awaiting signature
    ACTIVE = auto()       # Currently in force
    EXPIRING = auto()     # Within 90 days of expiry
    EXPIRED = auto()      # Past end date
    RENEWED = auto()      # Renewed to new contract
    CANCELLED = auto()    # Terminated early
    SUSPENDED = auto()    # Temporarily suspended


class PaymentTerms(Enum):
    """Payment schedule options."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"
    PREPAID = "prepaid"


class CreditType(Enum):
    """Types of prepaid credits."""
    API_CALLS = "api_calls"
    ML_INFERENCE = "ml_inference"
    STORAGE_GB = "storage_gb"
    COMPUTE_HOURS = "compute_hours"
    SUPPORT_HOURS = "support_hours"
    GENERAL = "general_credits"


@dataclass
class VolumeDiscount:
    """Volume-based discount tier."""
    min_volume: int
    max_volume: Optional[int]
    discount_percent: Decimal
    description: str


@dataclass
class PrepaidCredit:
    """Prepaid credit balance for a customer."""
    credit_id: str
    credit_type: CreditType
    original_amount: Decimal
    remaining_amount: Decimal
    expires_at: datetime
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def is_expired(self) -> bool:
        """Check if credit has expired."""
        return datetime.now(UTC) > self.expires_at
    
    def use_credit(self, amount: Decimal) -> tuple[Decimal, Decimal]:
        """
        Use credit amount.
        
        Returns:
            Tuple of (amount_used, remaining_needed)
        """
        if self.is_expired():
            return Decimal("0"), amount
        
        available = self.remaining_amount
        if available >= amount:
            self.remaining_amount -= amount
            return amount, Decimal("0")
        else:
            self.remaining_amount = Decimal("0")
            return available, amount - available


@dataclass
class SLATerms:
    """Service Level Agreement terms."""
    uptime_guarantee: Decimal = Decimal("99.9")  # Percentage
    response_time_p50_ms: int = 200
    response_time_p99_ms: int = 1000
    support_response_hours: int = 24
    dedicated_support: bool = False
    custom_integrations: bool = False
    priority_queue: bool = False
    
    # Credits for SLA violations
    uptime_credit_per_percent: Decimal = Decimal("10")  # % of monthly fee
    max_monthly_credit: Decimal = Decimal("30")  # Cap on credits


@dataclass
class ContractTerms:
    """Complete contract terms and conditions."""
    contract_id: str
    customer_id: str
    contract_type: ContractType
    status: ContractStatus
    
    # Dates
    start_date: datetime
    end_date: datetime
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    signed_at: Optional[datetime] = None
    
    # Pricing
    base_price: Decimal = Decimal("0")
    discount_percent: Decimal = Decimal("0")
    effective_price: Decimal = Decimal("0")
    payment_terms: PaymentTerms = PaymentTerms.MONTHLY
    
    # Commitments
    minimum_commitment: Decimal = Decimal("0")
    volume_commitments: dict[str, int] = field(default_factory=dict)
    
    # SLA
    sla_terms: SLATerms = field(default_factory=SLATerms)
    
    # Metadata
    notes: str = ""
    custom_terms: dict[str, Any] = field(default_factory=dict)
    docusign_envelope_id: Optional[str] = None
    
    def days_until_expiry(self) -> int:
        """Calculate days until contract expires."""
        delta = self.end_date - datetime.now(UTC)
        return max(0, delta.days)
    
    def is_expiring_soon(self, threshold_days: int = 90) -> bool:
        """Check if contract is expiring within threshold."""
        return 0 < self.days_until_expiry() <= threshold_days


@dataclass
class RenewalOffer:
    """Contract renewal offer."""
    offer_id: str
    contract_id: str
    customer_id: str
    
    # Offer details
    proposed_contract_type: ContractType
    proposed_price: Decimal
    proposed_discount: Decimal
    valid_until: datetime
    
    # Incentives
    early_renewal_bonus: Decimal = Decimal("0")
    loyalty_discount: Decimal = Decimal("0")
    volume_upgrade_offer: Optional[str] = None
    
    # Tracking
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    sent_at: Optional[datetime] = None
    viewed_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None


class ContractPricingEngine:
    """
    Calculates contract pricing with volume discounts and commitment terms.
    """
    
    # Base discount rates by contract type
    COMMITMENT_DISCOUNTS: dict[ContractType, Decimal] = {
        ContractType.MONTHLY: Decimal("0"),
        ContractType.ANNUAL: Decimal("10"),      # 10% for annual
        ContractType.MULTI_YEAR_2: Decimal("15"), # 15% for 2-year
        ContractType.MULTI_YEAR_3: Decimal("20"), # 20% for 3-year
        ContractType.ENTERPRISE: Decimal("25"),   # Up to 25% for enterprise
    }
    
    # Volume discount tiers (based on annual commitment)
    VOLUME_TIERS: list[VolumeDiscount] = [
        VolumeDiscount(0, 10000, Decimal("0"), "Base tier"),
        VolumeDiscount(10001, 50000, Decimal("5"), "Growth tier"),
        VolumeDiscount(50001, 100000, Decimal("10"), "Scale tier"),
        VolumeDiscount(100001, 500000, Decimal("15"), "Enterprise tier"),
        VolumeDiscount(500001, None, Decimal("20"), "Strategic tier"),
    ]
    
    # Payment term adjustments
    PAYMENT_TERM_ADJUSTMENTS: dict[PaymentTerms, Decimal] = {
        PaymentTerms.MONTHLY: Decimal("0"),
        PaymentTerms.QUARTERLY: Decimal("2"),   # 2% discount
        PaymentTerms.SEMI_ANNUAL: Decimal("3"), # 3% discount
        PaymentTerms.ANNUAL: Decimal("5"),      # 5% discount
        PaymentTerms.PREPAID: Decimal("8"),     # 8% discount for prepaid
    }
    
    def calculate_contract_price(
        self,
        base_monthly_price: Decimal,
        contract_type: ContractType,
        payment_terms: PaymentTerms,
        annual_volume: int,
        custom_discount: Decimal = Decimal("0"),
    ) -> dict[str, Any]:
        """
        Calculate final contract pricing with all discounts.
        
        Args:
            base_monthly_price: Standard monthly price
            contract_type: Commitment length
            payment_terms: Payment schedule
            annual_volume: Expected annual API call volume
            custom_discount: Additional negotiated discount
            
        Returns:
            Pricing breakdown with all discounts applied
        """
        # Calculate term-based discount
        commitment_discount = self.COMMITMENT_DISCOUNTS.get(
            contract_type, Decimal("0")
        )
        
        # Calculate volume discount
        volume_discount = self._get_volume_discount(annual_volume)
        
        # Calculate payment term discount
        payment_discount = self.PAYMENT_TERM_ADJUSTMENTS.get(
            payment_terms, Decimal("0")
        )
        
        # Total discount (capped at 40% maximum)
        total_discount = min(
            commitment_discount + volume_discount + payment_discount + custom_discount,
            Decimal("40")
        )
        
        # Calculate effective prices
        discount_multiplier = (Decimal("100") - total_discount) / Decimal("100")
        effective_monthly = (base_monthly_price * discount_multiplier).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        
        # Calculate contract total based on type
        months = self._get_contract_months(contract_type)
        total_contract_value = effective_monthly * months
        
        return {
            "base_monthly_price": float(base_monthly_price),
            "effective_monthly_price": float(effective_monthly),
            "total_contract_value": float(total_contract_value),
            "contract_months": months,
            "discounts": {
                "commitment_discount": float(commitment_discount),
                "volume_discount": float(volume_discount),
                "payment_discount": float(payment_discount),
                "custom_discount": float(custom_discount),
                "total_discount": float(total_discount),
            },
            "annual_savings": float(
                (base_monthly_price * 12) - (effective_monthly * 12)
            ),
            "contract_type": contract_type.name,
            "payment_terms": payment_terms.value,
        }
    
    def _get_volume_discount(self, annual_volume: int) -> Decimal:
        """Get volume discount tier for given volume."""
        for tier in self.VOLUME_TIERS:
            if tier.min_volume <= annual_volume:
                if tier.max_volume is None or annual_volume <= tier.max_volume:
                    return tier.discount_percent
        return Decimal("0")
    
    def _get_contract_months(self, contract_type: ContractType) -> int:
        """Get contract duration in months."""
        mapping = {
            ContractType.MONTHLY: 1,
            ContractType.ANNUAL: 12,
            ContractType.MULTI_YEAR_2: 24,
            ContractType.MULTI_YEAR_3: 36,
            ContractType.ENTERPRISE: 36,  # Default to 3 years for enterprise
        }
        return mapping.get(contract_type, 12)


class PrepaidCreditManager:
    """
    Manages prepaid credit purchases and consumption.
    
    Prepaid credits offer:
    - 8% discount vs pay-as-you-go
    - Budget predictability
    - Rollover flexibility (12-month expiry)
    """
    
    # Credit package options (credits -> price with ~8% discount built in)
    CREDIT_PACKAGES: dict[int, Decimal] = {
        1000: Decimal("920"),     # $0.92/credit vs $1.00
        5000: Decimal("4500"),    # $0.90/credit
        10000: Decimal("8800"),   # $0.88/credit
        50000: Decimal("42500"),  # $0.85/credit
        100000: Decimal("80000"), # $0.80/credit
    }
    
    # Default credit expiry (months)
    DEFAULT_EXPIRY_MONTHS = 12
    
    def __init__(self):
        self._credits: dict[str, list[PrepaidCredit]] = {}  # customer_id -> credits
    
    def purchase_credits(
        self,
        customer_id: str,
        credit_type: CreditType,
        amount: int,
        expiry_months: int = DEFAULT_EXPIRY_MONTHS,
    ) -> PrepaidCredit:
        """
        Purchase prepaid credits for a customer.
        
        Args:
            customer_id: Customer identifier
            credit_type: Type of credit
            amount: Number of credits
            expiry_months: Months until expiry
            
        Returns:
            Created PrepaidCredit object
        """
        credit = PrepaidCredit(
            credit_id=str(uuid4()),
            credit_type=credit_type,
            original_amount=Decimal(str(amount)),
            remaining_amount=Decimal(str(amount)),
            expires_at=datetime.now(UTC) + timedelta(days=expiry_months * 30),
        )
        
        if customer_id not in self._credits:
            self._credits[customer_id] = []
        self._credits[customer_id].append(credit)
        
        return credit
    
    def get_balance(
        self, customer_id: str, credit_type: Optional[CreditType] = None
    ) -> dict[str, Any]:
        """
        Get credit balance for a customer.
        
        Args:
            customer_id: Customer identifier
            credit_type: Optional filter by credit type
            
        Returns:
            Balance summary by credit type
        """
        credits = self._credits.get(customer_id, [])
        
        balances: dict[str, Decimal] = {}
        expiring_soon: dict[str, Decimal] = {}
        
        for credit in credits:
            if credit.is_expired():
                continue
            if credit_type and credit.credit_type != credit_type:
                continue
                
            type_key = credit.credit_type.value
            balances[type_key] = balances.get(type_key, Decimal("0")) + credit.remaining_amount
            
            # Check for credits expiring in 30 days
            if credit.expires_at <= datetime.now(UTC) + timedelta(days=30):
                expiring_soon[type_key] = (
                    expiring_soon.get(type_key, Decimal("0")) + credit.remaining_amount
                )
        
        return {
            "customer_id": customer_id,
            "balances": {k: float(v) for k, v in balances.items()},
            "expiring_in_30_days": {k: float(v) for k, v in expiring_soon.items()},
            "total_balance": float(sum(balances.values())),
        }
    
    def consume_credits(
        self,
        customer_id: str,
        credit_type: CreditType,
        amount: Decimal,
    ) -> dict[str, Any]:
        """
        Consume credits for usage (FIFO - oldest first).
        
        Args:
            customer_id: Customer identifier
            credit_type: Type of credit to consume
            amount: Amount to consume
            
        Returns:
            Consumption result with any overage
        """
        credits = self._credits.get(customer_id, [])
        
        # Filter to matching type and sort by expiry (oldest first)
        matching = [
            c for c in credits 
            if c.credit_type == credit_type and not c.is_expired()
        ]
        matching.sort(key=lambda c: c.expires_at)
        
        remaining = amount
        consumed_from: list[dict] = []
        
        for credit in matching:
            if remaining <= 0:
                break
            used, remaining = credit.use_credit(remaining)
            if used > 0:
                consumed_from.append({
                    "credit_id": credit.credit_id,
                    "amount_used": float(used),
                    "remaining_in_credit": float(credit.remaining_amount),
                })
        
        return {
            "requested_amount": float(amount),
            "credits_consumed": float(amount - remaining),
            "overage_amount": float(remaining),
            "has_overage": remaining > 0,
            "consumption_details": consumed_from,
        }


class ContractManager:
    """
    Manages contract lifecycle from creation through renewal.
    """
    
    def __init__(self):
        self._contracts: dict[str, ContractTerms] = {}
        self._offers: dict[str, RenewalOffer] = {}
        self.pricing_engine = ContractPricingEngine()
        self.credit_manager = PrepaidCreditManager()
    
    def create_contract(
        self,
        customer_id: str,
        contract_type: ContractType,
        base_price: Decimal,
        payment_terms: PaymentTerms = PaymentTerms.MONTHLY,
        annual_volume: int = 0,
        custom_discount: Decimal = Decimal("0"),
        sla_terms: Optional[SLATerms] = None,
        custom_terms: Optional[dict[str, Any]] = None,
    ) -> ContractTerms:
        """
        Create a new contract.
        
        Args:
            customer_id: Customer identifier
            contract_type: Type of commitment
            base_price: Base monthly price
            payment_terms: Payment schedule
            annual_volume: Expected annual volume
            custom_discount: Additional negotiated discount
            sla_terms: Custom SLA terms
            custom_terms: Additional custom terms
            
        Returns:
            Created contract
        """
        # Calculate pricing
        pricing = self.pricing_engine.calculate_contract_price(
            base_price, contract_type, payment_terms, annual_volume, custom_discount
        )
        
        # Determine contract dates
        start_date = datetime.now(UTC)
        months = pricing["contract_months"]
        end_date = start_date + timedelta(days=months * 30)
        
        contract = ContractTerms(
            contract_id=str(uuid4()),
            customer_id=customer_id,
            contract_type=contract_type,
            status=ContractStatus.DRAFT,
            start_date=start_date,
            end_date=end_date,
            base_price=base_price,
            discount_percent=Decimal(str(pricing["discounts"]["total_discount"])),
            effective_price=Decimal(str(pricing["effective_monthly_price"])),
            payment_terms=payment_terms,
            minimum_commitment=Decimal(str(pricing["total_contract_value"])),
            volume_commitments={"annual_api_calls": annual_volume},
            sla_terms=sla_terms or SLATerms(),
            custom_terms=custom_terms or {},
        )
        
        self._contracts[contract.contract_id] = contract
        return contract
    
    def activate_contract(
        self, contract_id: str, signed_at: Optional[datetime] = None
    ) -> ContractTerms:
        """Mark contract as active (typically after signature)."""
        contract = self._contracts.get(contract_id)
        if not contract:
            raise ValueError(f"Contract {contract_id} not found")
        
        contract.status = ContractStatus.ACTIVE
        contract.signed_at = signed_at or datetime.now(UTC)
        return contract
    
    def get_expiring_contracts(
        self, threshold_days: int = 90
    ) -> list[ContractTerms]:
        """Get all contracts expiring within threshold."""
        return [
            c for c in self._contracts.values()
            if c.status == ContractStatus.ACTIVE and c.is_expiring_soon(threshold_days)
        ]
    
    def create_renewal_offer(
        self,
        contract_id: str,
        proposed_contract_type: Optional[ContractType] = None,
        early_renewal_bonus: Decimal = Decimal("5"),
        loyalty_discount: Decimal = Decimal("3"),
    ) -> RenewalOffer:
        """
        Create a renewal offer for an expiring contract.
        
        Args:
            contract_id: Contract to renew
            proposed_contract_type: Suggested contract type (defaults to same)
            early_renewal_bonus: Extra discount for early renewal
            loyalty_discount: Discount for tenure
            
        Returns:
            Renewal offer
        """
        contract = self._contracts.get(contract_id)
        if not contract:
            raise ValueError(f"Contract {contract_id} not found")
        
        proposed_type = proposed_contract_type or contract.contract_type
        
        # Calculate renewal pricing with loyalty benefits
        base_discount = self.pricing_engine.COMMITMENT_DISCOUNTS.get(
            proposed_type, Decimal("0")
        )
        total_discount = base_discount + early_renewal_bonus + loyalty_discount
        
        proposed_price = contract.base_price * (
            (Decimal("100") - total_discount) / Decimal("100")
        )
        
        offer = RenewalOffer(
            offer_id=str(uuid4()),
            contract_id=contract_id,
            customer_id=contract.customer_id,
            proposed_contract_type=proposed_type,
            proposed_price=proposed_price.quantize(Decimal("0.01")),
            proposed_discount=total_discount,
            valid_until=datetime.now(UTC) + timedelta(days=30),
            early_renewal_bonus=early_renewal_bonus,
            loyalty_discount=loyalty_discount,
        )
        
        self._offers[offer.offer_id] = offer
        return offer
    
    def accept_renewal(self, offer_id: str) -> ContractTerms:
        """
        Accept a renewal offer and create new contract.
        
        Args:
            offer_id: Renewal offer to accept
            
        Returns:
            New contract terms
        """
        offer = self._offers.get(offer_id)
        if not offer:
            raise ValueError(f"Offer {offer_id} not found")
        
        old_contract = self._contracts.get(offer.contract_id)
        if not old_contract:
            raise ValueError(f"Original contract not found")
        
        # Mark offer as accepted
        offer.accepted_at = datetime.now(UTC)
        
        # Mark old contract as renewed
        old_contract.status = ContractStatus.RENEWED
        
        # Create new contract
        new_contract = self.create_contract(
            customer_id=offer.customer_id,
            contract_type=offer.proposed_contract_type,
            base_price=old_contract.base_price,
            payment_terms=old_contract.payment_terms,
            annual_volume=old_contract.volume_commitments.get("annual_api_calls", 0),
            custom_discount=offer.early_renewal_bonus + offer.loyalty_discount,
            sla_terms=old_contract.sla_terms,
        )
        
        # Auto-activate with continuous dates
        new_contract.start_date = old_contract.end_date
        months = self.pricing_engine._get_contract_months(new_contract.contract_type)
        new_contract.end_date = new_contract.start_date + timedelta(days=months * 30)
        new_contract.status = ContractStatus.ACTIVE
        
        return new_contract
    
    def get_contract_summary(self, contract_id: str) -> dict[str, Any]:
        """Get comprehensive contract summary."""
        contract = self._contracts.get(contract_id)
        if not contract:
            raise ValueError(f"Contract {contract_id} not found")
        
        return {
            "contract_id": contract.contract_id,
            "customer_id": contract.customer_id,
            "status": contract.status.name,
            "type": contract.contract_type.name,
            "pricing": {
                "base_price": float(contract.base_price),
                "discount_percent": float(contract.discount_percent),
                "effective_price": float(contract.effective_price),
                "minimum_commitment": float(contract.minimum_commitment),
            },
            "dates": {
                "start_date": contract.start_date.isoformat(),
                "end_date": contract.end_date.isoformat(),
                "days_until_expiry": contract.days_until_expiry(),
                "is_expiring_soon": contract.is_expiring_soon(),
            },
            "sla": {
                "uptime_guarantee": float(contract.sla_terms.uptime_guarantee),
                "support_response_hours": contract.sla_terms.support_response_hours,
                "dedicated_support": contract.sla_terms.dedicated_support,
            },
            "payment_terms": contract.payment_terms.value,
        }


# === Integration Functions ===

def calculate_enterprise_pricing(
    base_monthly: float,
    contract_years: int,
    annual_api_volume: int,
    prepay_annual: bool = False,
) -> dict[str, Any]:
    """
    Calculate enterprise contract pricing.
    
    Args:
        base_monthly: Base monthly price
        contract_years: Contract length (1, 2, or 3 years)
        annual_api_volume: Expected annual API calls
        prepay_annual: Whether customer will prepay annually
        
    Returns:
        Complete pricing breakdown
    """
    engine = ContractPricingEngine()
    
    contract_type = {
        1: ContractType.ANNUAL,
        2: ContractType.MULTI_YEAR_2,
        3: ContractType.MULTI_YEAR_3,
    }.get(contract_years, ContractType.ANNUAL)
    
    payment_terms = PaymentTerms.ANNUAL if prepay_annual else PaymentTerms.MONTHLY
    
    return engine.calculate_contract_price(
        base_monthly_price=Decimal(str(base_monthly)),
        contract_type=contract_type,
        payment_terms=payment_terms,
        annual_volume=annual_api_volume,
    )


def create_enterprise_contract(
    customer_id: str,
    base_monthly: float,
    contract_years: int = 1,
    annual_api_volume: int = 0,
    dedicated_support: bool = False,
    custom_sla: bool = False,
) -> dict[str, Any]:
    """
    Create an enterprise contract with full terms.
    
    Args:
        customer_id: Customer identifier
        base_monthly: Base monthly price
        contract_years: Contract length
        annual_api_volume: Expected volume
        dedicated_support: Include dedicated support
        custom_sla: Use enhanced SLA terms
        
    Returns:
        Contract summary
    """
    manager = ContractManager()
    
    contract_type = {
        1: ContractType.ANNUAL,
        2: ContractType.MULTI_YEAR_2,
        3: ContractType.MULTI_YEAR_3,
    }.get(contract_years, ContractType.ANNUAL)
    
    # Build SLA terms
    sla = SLATerms(
        uptime_guarantee=Decimal("99.99") if custom_sla else Decimal("99.9"),
        support_response_hours=4 if dedicated_support else 24,
        dedicated_support=dedicated_support,
        custom_integrations=dedicated_support,
        priority_queue=custom_sla,
    )
    
    contract = manager.create_contract(
        customer_id=customer_id,
        contract_type=contract_type,
        base_price=Decimal(str(base_monthly)),
        payment_terms=PaymentTerms.ANNUAL,
        annual_volume=annual_api_volume,
        sla_terms=sla,
    )
    
    return manager.get_contract_summary(contract.contract_id)


def purchase_api_credits(
    customer_id: str,
    credit_amount: int,
    expiry_months: int = 12,
) -> dict[str, Any]:
    """
    Purchase prepaid API credits.
    
    Args:
        customer_id: Customer identifier
        credit_amount: Number of credits to purchase
        expiry_months: Months until expiry
        
    Returns:
        Credit purchase confirmation
    """
    manager = PrepaidCreditManager()
    
    # Find best package
    package_price = None
    for pkg_amount, price in sorted(manager.CREDIT_PACKAGES.items()):
        if pkg_amount >= credit_amount:
            package_price = price
            break
    
    if package_price is None:
        # Custom pricing for very large amounts
        package_price = Decimal(str(credit_amount)) * Decimal("0.80")
    
    credit = manager.purchase_credits(
        customer_id=customer_id,
        credit_type=CreditType.API_CALLS,
        amount=credit_amount,
        expiry_months=expiry_months,
    )
    
    return {
        "credit_id": credit.credit_id,
        "customer_id": customer_id,
        "credits_purchased": credit_amount,
        "price_paid": float(package_price),
        "price_per_credit": float(package_price / credit_amount),
        "expires_at": credit.expires_at.isoformat(),
        "balance": manager.get_balance(customer_id),
    }


# === Stripe Integration Helpers ===

def get_stripe_contract_metadata(contract: ContractTerms) -> dict[str, str]:
    """
    Generate Stripe-compatible metadata for a contract.
    
    Args:
        contract: Contract terms
        
    Returns:
        Metadata dict for Stripe subscription
    """
    return {
        "krl_contract_id": contract.contract_id,
        "krl_contract_type": contract.contract_type.name,
        "krl_contract_status": contract.status.name,
        "krl_discount_percent": str(contract.discount_percent),
        "krl_effective_price": str(contract.effective_price),
        "krl_start_date": contract.start_date.isoformat(),
        "krl_end_date": contract.end_date.isoformat(),
        "krl_payment_terms": contract.payment_terms.value,
        "krl_sla_uptime": str(contract.sla_terms.uptime_guarantee),
        "krl_dedicated_support": str(contract.sla_terms.dedicated_support).lower(),
    }


def sync_contract_to_stripe(
    contract: ContractTerms,
    stripe_subscription_id: str,
) -> dict[str, Any]:
    """
    Prepare contract data for Stripe subscription update.
    
    Args:
        contract: Contract terms
        stripe_subscription_id: Stripe subscription ID
        
    Returns:
        Stripe update payload
    """
    metadata = get_stripe_contract_metadata(contract)
    
    return {
        "subscription_id": stripe_subscription_id,
        "metadata": metadata,
        "billing_cycle_anchor": "now" if contract.payment_terms == PaymentTerms.PREPAID else None,
        "proration_behavior": "create_prorations",
    }
