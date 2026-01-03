# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
#
# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.billing_state_machine
# This stub remains for backward compatibility but will be removed in v2.0.
# ----------------------------------------------------------------------

from __future__ import annotations

import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.billing_state_machine is deprecated. "
    "Import from 'app.services.billing.billing_state_machine' instead.",
    DeprecationWarning,
    stacklevel=2
)


"""
KRL Multi-Tenant Billing State Machine - Week 24b Day 2
======================================================

Manages subscription lifecycle states with proper transition rules
and tenant isolation for multi-tenant SaaS billing.

Features:
- Subscription state machine
- Valid state transitions
- Tenant isolation
- State change hooks
- Audit logging
"""


import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, UTC
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from uuid import uuid4

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class SubscriptionState(str, Enum):
    """Subscription lifecycle states."""
    # Initial states
    PENDING = "pending"          # Created, awaiting payment method
    TRIALING = "trialing"        # In trial period
    
    # Active states
    ACTIVE = "active"            # Paid and active
    PAST_DUE = "past_due"        # Payment failed, grace period
    
    # Paused states
    PAUSED = "paused"            # Voluntarily paused
    SUSPENDED = "suspended"      # Suspended due to policy violation
    
    # Terminal states
    CANCELED = "canceled"        # Customer canceled
    EXPIRED = "expired"          # Trial expired without conversion
    TERMINATED = "terminated"    # Terminated by admin


class TransitionTrigger(str, Enum):
    """What triggers state transitions."""
    CUSTOMER_ACTION = "customer_action"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILURE = "payment_failure"
    TRIAL_END = "trial_end"
    GRACE_PERIOD_END = "grace_period_end"
    ADMIN_ACTION = "admin_action"
    POLICY_VIOLATION = "policy_violation"
    SCHEDULED = "scheduled"
    SYSTEM = "system"


class TenantStatus(str, Enum):
    """Tenant account status."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING_DELETION = "pending_deletion"
    DELETED = "deleted"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class StateTransition:
    """Record of state transition."""
    transition_id: str
    subscription_id: str
    tenant_id: str
    from_state: SubscriptionState
    to_state: SubscriptionState
    trigger: TransitionTrigger
    triggered_by: str  # user_id or "system"
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class TransitionRule:
    """Rule defining valid state transitions."""
    from_states: Set[SubscriptionState]
    to_state: SubscriptionState
    allowed_triggers: Set[TransitionTrigger]
    requires_approval: bool = False
    auto_transition_after: Optional[timedelta] = None


@dataclass
class SubscriptionContext:
    """Context for subscription state evaluation."""
    subscription_id: str
    tenant_id: str
    current_state: SubscriptionState
    created_at: datetime
    state_entered_at: datetime
    trial_end: Optional[datetime] = None
    payment_method_attached: bool = False
    last_payment_date: Optional[datetime] = None
    failed_payment_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TenantContext:
    """Tenant-level context."""
    tenant_id: str
    status: TenantStatus
    created_at: datetime
    subscription_count: int = 0
    active_subscription_count: int = 0
    total_mrr: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# State Machine Definition
# =============================================================================

# Valid state transitions
TRANSITION_RULES: Dict[Tuple[SubscriptionState, SubscriptionState], TransitionRule] = {
    # From PENDING
    (SubscriptionState.PENDING, SubscriptionState.TRIALING): TransitionRule(
        from_states={SubscriptionState.PENDING},
        to_state=SubscriptionState.TRIALING,
        allowed_triggers={TransitionTrigger.CUSTOMER_ACTION, TransitionTrigger.SYSTEM},
    ),
    (SubscriptionState.PENDING, SubscriptionState.ACTIVE): TransitionRule(
        from_states={SubscriptionState.PENDING},
        to_state=SubscriptionState.ACTIVE,
        allowed_triggers={TransitionTrigger.PAYMENT_SUCCESS},
    ),
    (SubscriptionState.PENDING, SubscriptionState.CANCELED): TransitionRule(
        from_states={SubscriptionState.PENDING},
        to_state=SubscriptionState.CANCELED,
        allowed_triggers={TransitionTrigger.CUSTOMER_ACTION, TransitionTrigger.ADMIN_ACTION},
    ),
    
    # From TRIALING
    (SubscriptionState.TRIALING, SubscriptionState.ACTIVE): TransitionRule(
        from_states={SubscriptionState.TRIALING},
        to_state=SubscriptionState.ACTIVE,
        allowed_triggers={TransitionTrigger.PAYMENT_SUCCESS, TransitionTrigger.TRIAL_END},
    ),
    (SubscriptionState.TRIALING, SubscriptionState.EXPIRED): TransitionRule(
        from_states={SubscriptionState.TRIALING},
        to_state=SubscriptionState.EXPIRED,
        allowed_triggers={TransitionTrigger.TRIAL_END, TransitionTrigger.SCHEDULED},
    ),
    (SubscriptionState.TRIALING, SubscriptionState.CANCELED): TransitionRule(
        from_states={SubscriptionState.TRIALING},
        to_state=SubscriptionState.CANCELED,
        allowed_triggers={TransitionTrigger.CUSTOMER_ACTION},
    ),
    
    # From ACTIVE
    (SubscriptionState.ACTIVE, SubscriptionState.PAST_DUE): TransitionRule(
        from_states={SubscriptionState.ACTIVE},
        to_state=SubscriptionState.PAST_DUE,
        allowed_triggers={TransitionTrigger.PAYMENT_FAILURE},
    ),
    (SubscriptionState.ACTIVE, SubscriptionState.PAUSED): TransitionRule(
        from_states={SubscriptionState.ACTIVE},
        to_state=SubscriptionState.PAUSED,
        allowed_triggers={TransitionTrigger.CUSTOMER_ACTION, TransitionTrigger.ADMIN_ACTION},
    ),
    (SubscriptionState.ACTIVE, SubscriptionState.SUSPENDED): TransitionRule(
        from_states={SubscriptionState.ACTIVE},
        to_state=SubscriptionState.SUSPENDED,
        allowed_triggers={TransitionTrigger.POLICY_VIOLATION, TransitionTrigger.ADMIN_ACTION},
    ),
    (SubscriptionState.ACTIVE, SubscriptionState.CANCELED): TransitionRule(
        from_states={SubscriptionState.ACTIVE},
        to_state=SubscriptionState.CANCELED,
        allowed_triggers={TransitionTrigger.CUSTOMER_ACTION, TransitionTrigger.ADMIN_ACTION},
    ),
    
    # From PAST_DUE
    (SubscriptionState.PAST_DUE, SubscriptionState.ACTIVE): TransitionRule(
        from_states={SubscriptionState.PAST_DUE},
        to_state=SubscriptionState.ACTIVE,
        allowed_triggers={TransitionTrigger.PAYMENT_SUCCESS},
    ),
    (SubscriptionState.PAST_DUE, SubscriptionState.CANCELED): TransitionRule(
        from_states={SubscriptionState.PAST_DUE},
        to_state=SubscriptionState.CANCELED,
        allowed_triggers={TransitionTrigger.GRACE_PERIOD_END, TransitionTrigger.CUSTOMER_ACTION},
    ),
    (SubscriptionState.PAST_DUE, SubscriptionState.SUSPENDED): TransitionRule(
        from_states={SubscriptionState.PAST_DUE},
        to_state=SubscriptionState.SUSPENDED,
        allowed_triggers={TransitionTrigger.GRACE_PERIOD_END},
    ),
    
    # From PAUSED
    (SubscriptionState.PAUSED, SubscriptionState.ACTIVE): TransitionRule(
        from_states={SubscriptionState.PAUSED},
        to_state=SubscriptionState.ACTIVE,
        allowed_triggers={TransitionTrigger.CUSTOMER_ACTION, TransitionTrigger.PAYMENT_SUCCESS},
    ),
    (SubscriptionState.PAUSED, SubscriptionState.CANCELED): TransitionRule(
        from_states={SubscriptionState.PAUSED},
        to_state=SubscriptionState.CANCELED,
        allowed_triggers={TransitionTrigger.CUSTOMER_ACTION, TransitionTrigger.SCHEDULED},
    ),
    
    # From SUSPENDED
    (SubscriptionState.SUSPENDED, SubscriptionState.ACTIVE): TransitionRule(
        from_states={SubscriptionState.SUSPENDED},
        to_state=SubscriptionState.ACTIVE,
        allowed_triggers={TransitionTrigger.ADMIN_ACTION},
        requires_approval=True,
    ),
    (SubscriptionState.SUSPENDED, SubscriptionState.TERMINATED): TransitionRule(
        from_states={SubscriptionState.SUSPENDED},
        to_state=SubscriptionState.TERMINATED,
        allowed_triggers={TransitionTrigger.ADMIN_ACTION},
        requires_approval=True,
    ),
    
    # Admin overrides (any state to terminated)
    (SubscriptionState.ACTIVE, SubscriptionState.TERMINATED): TransitionRule(
        from_states={SubscriptionState.ACTIVE},
        to_state=SubscriptionState.TERMINATED,
        allowed_triggers={TransitionTrigger.ADMIN_ACTION},
        requires_approval=True,
    ),
}


# =============================================================================
# State Machine
# =============================================================================

class SubscriptionStateMachine:
    """
    Manages subscription state transitions with validation.
    
    Features:
    - State transition validation
    - Transition hooks (before/after)
    - Audit logging
    - Rollback support
    """
    
    def __init__(self):
        self._rules = TRANSITION_RULES.copy()
        self._before_hooks: Dict[SubscriptionState, List[Callable]] = {}
        self._after_hooks: Dict[SubscriptionState, List[Callable]] = {}
        self._transitions: List[StateTransition] = []
    
    def can_transition(
        self,
        from_state: SubscriptionState,
        to_state: SubscriptionState,
        trigger: TransitionTrigger,
    ) -> Tuple[bool, str]:
        """Check if transition is valid."""
        rule_key = (from_state, to_state)
        
        if rule_key not in self._rules:
            return False, f"No rule for {from_state.value} -> {to_state.value}"
        
        rule = self._rules[rule_key]
        
        if trigger not in rule.allowed_triggers:
            return False, f"Trigger {trigger.value} not allowed for this transition"
        
        return True, "Transition allowed"
    
    def transition(
        self,
        context: SubscriptionContext,
        to_state: SubscriptionState,
        trigger: TransitionTrigger,
        triggered_by: str,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, StateTransition]:
        """Execute state transition."""
        from_state = context.current_state
        
        # Validate transition
        can_do, message = self.can_transition(from_state, to_state, trigger)
        if not can_do:
            logger.warning(f"Invalid transition: {message}")
            raise ValueError(message)
        
        # Check if approval required
        rule = self._rules[(from_state, to_state)]
        if rule.requires_approval and trigger != TransitionTrigger.ADMIN_ACTION:
            raise PermissionError("This transition requires admin approval")
        
        # Execute before hooks
        for hook in self._before_hooks.get(to_state, []):
            try:
                hook(context, from_state, to_state)
            except Exception as e:
                logger.error(f"Before hook failed: {e}")
                raise
        
        # Create transition record
        transition = StateTransition(
            transition_id=uuid4().hex,
            subscription_id=context.subscription_id,
            tenant_id=context.tenant_id,
            from_state=from_state,
            to_state=to_state,
            trigger=trigger,
            triggered_by=triggered_by,
            reason=reason,
            metadata=metadata or {},
        )
        
        self._transitions.append(transition)
        
        # Execute after hooks
        for hook in self._after_hooks.get(to_state, []):
            try:
                hook(context, transition)
            except Exception as e:
                logger.error(f"After hook failed: {e}")
        
        logger.info(
            f"Subscription {context.subscription_id}: "
            f"{from_state.value} -> {to_state.value} ({trigger.value})"
        )
        
        return True, transition
    
    def on_enter(self, state: SubscriptionState, hook: Callable) -> None:
        """Register hook for entering state."""
        if state not in self._after_hooks:
            self._after_hooks[state] = []
        self._after_hooks[state].append(hook)
    
    def on_exit(self, state: SubscriptionState, hook: Callable) -> None:
        """Register hook for exiting state."""
        if state not in self._before_hooks:
            self._before_hooks[state] = []
        self._before_hooks[state].append(hook)
    
    def get_valid_transitions(
        self,
        from_state: SubscriptionState,
    ) -> List[Tuple[SubscriptionState, Set[TransitionTrigger]]]:
        """Get valid transitions from current state."""
        valid = []
        for (f_state, t_state), rule in self._rules.items():
            if f_state == from_state:
                valid.append((t_state, rule.allowed_triggers))
        return valid
    
    def get_transition_history(
        self,
        subscription_id: str,
        limit: int = 100,
    ) -> List[StateTransition]:
        """Get transition history for subscription."""
        history = [
            t for t in self._transitions
            if t.subscription_id == subscription_id
        ]
        return sorted(history, key=lambda x: x.timestamp, reverse=True)[:limit]


# =============================================================================
# Tenant Isolation Manager
# =============================================================================

class TenantIsolationManager:
    """
    Ensures proper tenant isolation for billing operations.
    
    Features:
    - Tenant context validation
    - Cross-tenant access prevention
    - Tenant-scoped queries
    - Resource quotas per tenant
    """
    
    def __init__(self):
        self._tenants: Dict[str, TenantContext] = {}
        self._subscriptions: Dict[str, str] = {}  # subscription_id -> tenant_id
        self._resource_quotas: Dict[str, Dict[str, int]] = {}  # tenant_id -> {resource: quota}
    
    def register_tenant(self, context: TenantContext) -> None:
        """Register tenant."""
        self._tenants[context.tenant_id] = context
        logger.info(f"Registered tenant: {context.tenant_id}")
    
    def register_subscription(
        self,
        subscription_id: str,
        tenant_id: str,
    ) -> None:
        """Register subscription to tenant."""
        if tenant_id not in self._tenants:
            raise ValueError(f"Unknown tenant: {tenant_id}")
        
        self._subscriptions[subscription_id] = tenant_id
    
    def validate_access(
        self,
        requesting_tenant: str,
        subscription_id: str,
    ) -> bool:
        """Validate tenant can access subscription."""
        if subscription_id not in self._subscriptions:
            return False
        
        owning_tenant = self._subscriptions[subscription_id]
        return owning_tenant == requesting_tenant
    
    def get_tenant_subscriptions(
        self,
        tenant_id: str,
    ) -> List[str]:
        """Get all subscriptions for tenant."""
        return [
            sub_id for sub_id, t_id in self._subscriptions.items()
            if t_id == tenant_id
        ]
    
    def set_resource_quota(
        self,
        tenant_id: str,
        resource: str,
        quota: int,
    ) -> None:
        """Set resource quota for tenant."""
        if tenant_id not in self._resource_quotas:
            self._resource_quotas[tenant_id] = {}
        self._resource_quotas[tenant_id][resource] = quota
    
    def check_quota(
        self,
        tenant_id: str,
        resource: str,
        requested: int,
        current_usage: int,
    ) -> Tuple[bool, str]:
        """Check if tenant has quota available."""
        quotas = self._resource_quotas.get(tenant_id, {})
        quota = quotas.get(resource)
        
        if quota is None:
            return True, "No quota limit set"
        
        if current_usage + requested > quota:
            return False, f"Would exceed quota ({current_usage + requested} > {quota})"
        
        return True, f"Quota available ({current_usage + requested} / {quota})"
    
    def get_tenant(self, tenant_id: str) -> Optional[TenantContext]:
        """Get tenant context."""
        return self._tenants.get(tenant_id)
    
    def suspend_tenant(self, tenant_id: str, reason: str) -> bool:
        """Suspend tenant."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return False
        
        tenant.status = TenantStatus.SUSPENDED
        logger.warning(f"Tenant suspended: {tenant_id} - {reason}")
        return True


# =============================================================================
# Billing State Manager
# =============================================================================

class BillingStateManager:
    """
    High-level manager for subscription states across tenants.
    
    Coordinates:
    - State machine
    - Tenant isolation
    - Scheduled transitions
    - Grace period management
    """
    
    def __init__(self):
        self.state_machine = SubscriptionStateMachine()
        self.tenant_manager = TenantIsolationManager()
        
        # Subscription contexts
        self._subscriptions: Dict[str, SubscriptionContext] = {}
        
        # Grace period settings
        self._grace_periods = {
            SubscriptionState.PAST_DUE: timedelta(days=7),
            SubscriptionState.PAUSED: timedelta(days=90),
        }
        
        # Setup default hooks
        self._setup_hooks()
    
    def _setup_hooks(self) -> None:
        """Setup default state transition hooks."""
        # On entering PAST_DUE, schedule grace period end
        def on_past_due(context: SubscriptionContext, transition: StateTransition):
            grace_end = datetime.now(timezone.utc) + self._grace_periods[SubscriptionState.PAST_DUE]
            logger.info(f"Grace period for {context.subscription_id} ends at {grace_end}")
        
        self.state_machine.on_enter(SubscriptionState.PAST_DUE, on_past_due)
    
    def create_subscription(
        self,
        subscription_id: str,
        tenant_id: str,
        initial_state: SubscriptionState = SubscriptionState.PENDING,
        trial_days: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SubscriptionContext:
        """Create new subscription."""
        now = datetime.now(timezone.utc)
        
        trial_end = None
        if trial_days > 0:
            trial_end = now + timedelta(days=trial_days)
            initial_state = SubscriptionState.TRIALING
        
        context = SubscriptionContext(
            subscription_id=subscription_id,
            tenant_id=tenant_id,
            current_state=initial_state,
            created_at=now,
            state_entered_at=now,
            trial_end=trial_end,
            metadata=metadata or {},
        )
        
        self._subscriptions[subscription_id] = context
        self.tenant_manager.register_subscription(subscription_id, tenant_id)
        
        logger.info(f"Created subscription {subscription_id} for tenant {tenant_id}")
        return context
    
    def get_subscription(self, subscription_id: str) -> Optional[SubscriptionContext]:
        """Get subscription context."""
        return self._subscriptions.get(subscription_id)
    
    def transition_subscription(
        self,
        subscription_id: str,
        to_state: SubscriptionState,
        trigger: TransitionTrigger,
        triggered_by: str,
        reason: str,
        requesting_tenant: Optional[str] = None,
    ) -> StateTransition:
        """Transition subscription state with tenant validation."""
        context = self._subscriptions.get(subscription_id)
        if not context:
            raise ValueError(f"Unknown subscription: {subscription_id}")
        
        # Validate tenant access if specified
        if requesting_tenant:
            if not self.tenant_manager.validate_access(requesting_tenant, subscription_id):
                raise PermissionError("Tenant cannot access this subscription")
        
        # Execute transition
        success, transition = self.state_machine.transition(
            context=context,
            to_state=to_state,
            trigger=trigger,
            triggered_by=triggered_by,
            reason=reason,
        )
        
        # Update context
        context.current_state = to_state
        context.state_entered_at = transition.timestamp
        
        return transition
    
    def process_payment_success(
        self,
        subscription_id: str,
        triggered_by: str = "system",
    ) -> Optional[StateTransition]:
        """Process successful payment."""
        context = self._subscriptions.get(subscription_id)
        if not context:
            return None
        
        # Determine target state
        if context.current_state in (SubscriptionState.PENDING, SubscriptionState.TRIALING):
            to_state = SubscriptionState.ACTIVE
        elif context.current_state == SubscriptionState.PAST_DUE:
            to_state = SubscriptionState.ACTIVE
        elif context.current_state == SubscriptionState.PAUSED:
            to_state = SubscriptionState.ACTIVE
        else:
            return None  # No transition needed
        
        context.last_payment_date = datetime.now(timezone.utc)
        context.failed_payment_count = 0
        
        return self.transition_subscription(
            subscription_id=subscription_id,
            to_state=to_state,
            trigger=TransitionTrigger.PAYMENT_SUCCESS,
            triggered_by=triggered_by,
            reason="Payment successful",
        )
    
    def process_payment_failure(
        self,
        subscription_id: str,
        triggered_by: str = "system",
    ) -> Optional[StateTransition]:
        """Process failed payment."""
        context = self._subscriptions.get(subscription_id)
        if not context:
            return None
        
        context.failed_payment_count += 1
        
        if context.current_state == SubscriptionState.ACTIVE:
            return self.transition_subscription(
                subscription_id=subscription_id,
                to_state=SubscriptionState.PAST_DUE,
                trigger=TransitionTrigger.PAYMENT_FAILURE,
                triggered_by=triggered_by,
                reason=f"Payment failed ({context.failed_payment_count} attempts)",
            )
        
        return None
    
    def check_grace_periods(self) -> List[StateTransition]:
        """Check and process expired grace periods."""
        transitions = []
        now = datetime.now(timezone.utc)
        
        for sub_id, context in self._subscriptions.items():
            if context.current_state not in self._grace_periods:
                continue
            
            grace_period = self._grace_periods[context.current_state]
            grace_end = context.state_entered_at + grace_period
            
            if now >= grace_end:
                try:
                    transition = self.transition_subscription(
                        subscription_id=sub_id,
                        to_state=SubscriptionState.CANCELED,
                        trigger=TransitionTrigger.GRACE_PERIOD_END,
                        triggered_by="system",
                        reason=f"Grace period expired after {grace_period.days} days",
                    )
                    transitions.append(transition)
                except Exception as e:
                    logger.error(f"Grace period transition failed: {e}")
        
        return transitions
    
    def get_tenant_summary(self, tenant_id: str) -> Dict[str, Any]:
        """Get billing summary for tenant."""
        subscriptions = self.tenant_manager.get_tenant_subscriptions(tenant_id)
        
        state_counts: Dict[str, int] = {}
        for sub_id in subscriptions:
            context = self._subscriptions.get(sub_id)
            if context:
                state = context.current_state.value
                state_counts[state] = state_counts.get(state, 0) + 1
        
        return {
            "tenant_id": tenant_id,
            "total_subscriptions": len(subscriptions),
            "state_breakdown": state_counts,
            "subscription_ids": subscriptions,
        }


# =============================================================================
# Factory Function
# =============================================================================

def create_billing_state_manager() -> BillingStateManager:
    """Create configured BillingStateManager."""
    return BillingStateManager()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "SubscriptionState",
    "TransitionTrigger",
    "TenantStatus",
    # Data Classes
    "StateTransition",
    "TransitionRule",
    "SubscriptionContext",
    "TenantContext",
    # Constants
    "TRANSITION_RULES",
    # Classes
    "SubscriptionStateMachine",
    "TenantIsolationManager",
    "BillingStateManager",
    # Factory
    "create_billing_state_manager",
]
