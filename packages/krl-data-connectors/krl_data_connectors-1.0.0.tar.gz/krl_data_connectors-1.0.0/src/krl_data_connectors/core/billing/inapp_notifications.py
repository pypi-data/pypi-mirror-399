# =============================================================================
# IN-APP NOTIFICATION TEMPLATES (StoryBrand Compressed)
# =============================================================================
# Shorter-format notifications for banners, modals, and alerts
# Triggered by billing events and usage patterns
#
# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.inapp_notifications
# This stub remains for backward compatibility but will be removed in v2.0.
# =============================================================================
import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.inapp_notifications is deprecated. "
    "Import from 'app.services.billing.inapp_notifications' instead.",
    DeprecationWarning,
    stacklevel=2
)

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta, UTC


class NotificationFormat(Enum):
    """Display format for in-app notifications."""
    BANNER = "banner"           # Top-of-page persistent banner
    MODAL = "modal"             # Centered overlay modal
    ALERT = "alert"             # Urgent notification (non-dismissible)
    TOAST = "toast"             # Bottom-corner transient notification
    CELEBRATION = "celebration" # Success milestone with animation


class NotificationTone(Enum):
    """Tone/urgency level for notification messaging."""
    HELPFUL_WARNING = "helpful_warning"
    OPPORTUNITY_REVEAL = "opportunity_reveal"
    URGENT_PROTECTIVE = "urgent_protective"
    ACHIEVEMENT_UNLOCK = "achievement_unlock"
    INFORMATIONAL = "informational"


@dataclass
class InAppNotification:
    """Structured in-app notification configuration."""
    notification_id: str
    trigger: str
    format: NotificationFormat
    tone: NotificationTone
    notification_text: str
    cta_primary: str
    cta_url: str
    cta_secondary: Optional[str] = None
    cta_secondary_url: Optional[str] = None
    dismissible: bool = True
    reshow_after_dismiss: Optional[str] = None  # "24_hours", "7_days", "never"
    show_animation: bool = False
    icon: Optional[str] = None
    priority: int = 5  # 1-10, higher = more urgent


# =============================================================================
# IN-APP NOTIFICATION LIBRARY
# =============================================================================

IN_APP_NOTIFICATIONS_STORYBRAND: Dict[str, Dict[str, Any]] = {
    
    # =========================================================================
    # COMMUNITY TIER NOTIFICATIONS
    # =========================================================================
    
    "community_capacity_warning": {
        "trigger": "API calls > 80% of tier limit",
        "format": NotificationFormat.BANNER,
        "tone": NotificationTone.HELPFUL_WARNING,
        "priority": 7,
        
        "notification_text": """
⚠️ **You've used {usage_percent}% of your monthly API quota** ({api_calls_used:,} of {api_limit:,} calls).

At your current pace, you'll hit the limit in {days_remaining} days. When that happens, your analysis stops cold.

**847 analysts upgraded to Pro at this exact moment** — 100K calls monthly, no more capacity stress.
        """,
        
        "cta_primary": "Upgrade to Pro",
        "cta_url": "/upgrade?tier=pro&trigger=capacity_warning",
        "cta_secondary": "View Usage Details",
        "cta_secondary_url": "/dashboard/usage",
        
        "dismissible": True,
        "reshow_after_dismiss": "24_hours",
        "icon": "⚠️",
    },
    
    "community_capacity_critical": {
        "trigger": "API calls > 95% of tier limit",
        "format": NotificationFormat.ALERT,
        "tone": NotificationTone.URGENT_PROTECTIVE,
        "priority": 9,
        
        "notification_text": """
🚨 **Critical: {api_calls_remaining:,} API calls remaining this month.**

Your analysis will stop when you hit 0. Active projects will stall. Stakeholders will wait.

**Upgrade now to avoid interruption.** Pro starts at 100K calls — your next analysis runs immediately.
        """,
        
        "cta_primary": "Upgrade Now — Avoid Interruption",
        "cta_url": "/upgrade?tier=pro&trigger=capacity_critical",
        
        "dismissible": False,  # Critical alerts non-dismissible
        "icon": "🚨",
    },
    
    "community_feature_gate_federated": {
        "trigger": "Clicked blocked federated learning feature",
        "format": NotificationFormat.MODAL,
        "tone": NotificationTone.OPPORTUNITY_REVEAL,
        "priority": 6,
        
        "notification_text": """
🔒 **Federated Learning** is a Pro feature.

You're trying to break down data silos — train models across jurisdictions without centralizing data.

**Real example:** State housing authority analyzed eviction patterns across 40 counties without centralizing tenant records. 6 weeks instead of 18-month data-sharing negotiation.

**Pro includes 4 federated rounds monthly.** Unlock collaborative rigor today.
        """,
        
        "cta_primary": "Unlock Federated Learning",
        "cta_url": "/upgrade?tier=pro&trigger=federated_gate",
        "cta_secondary": "Learn How It Works",
        "cta_secondary_url": "/docs/federated-learning",
        
        "dismissible": True,
        "reshow_after_dismiss": "7_days",
        "icon": "🔒",
    },
    
    "community_feature_gate_generic": {
        "trigger": "Clicked any blocked Pro feature",
        "format": NotificationFormat.MODAL,
        "tone": NotificationTone.OPPORTUNITY_REVEAL,
        "priority": 5,
        
        "notification_text": """
🔒 **{feature_name}** is available on Pro tier.

This feature unlocks:
{feature_benefits}

**847 policy analysts upgraded to Pro.** 94% stay after 6 months.
        """,
        
        "cta_primary": "Upgrade to Pro",
        "cta_url": "/upgrade?tier=pro&trigger=feature_gate",
        "cta_secondary": "See All Pro Features",
        "cta_secondary_url": "/pricing#pro",
        
        "dismissible": True,
        "reshow_after_dismiss": "3_days",
        "icon": "🔒",
    },
    
    "community_tier_violation_first": {
        "trigger": "First tier violation in 24 hours",
        "format": NotificationFormat.TOAST,
        "tone": NotificationTone.INFORMATIONAL,
        "priority": 4,
        
        "notification_text": """
ℹ️ You hit a Community tier limit. This feature is restricted on your current plan.

Need more capacity? **Pro removes these restrictions.**
        """,
        
        "cta_primary": "See Pro Benefits",
        "cta_url": "/pricing#pro",
        
        "dismissible": True,
        "reshow_after_dismiss": "never",  # Don't repeat same-day
        "icon": "ℹ️",
    },
    
    "community_tier_violation_pattern": {
        "trigger": "3+ tier violations in 24 hours",
        "format": NotificationFormat.BANNER,
        "tone": NotificationTone.HELPFUL_WARNING,
        "priority": 8,
        
        "notification_text": """
⚡ **You've hit tier limits {violation_count} times today.**

You're clearly doing important work under deadline pressure. Community tier wasn't designed for this intensity.

**412 analysts were exactly where you are.** They upgraded to Pro. Limits lifted in <2 minutes.
        """,
        
        "cta_primary": "End the Limit Nightmare",
        "cta_url": "/upgrade?tier=pro&trigger=violations",
        "cta_secondary": "Not Now",
        "cta_secondary_url": None,  # Dismiss action
        
        "dismissible": True,
        "reshow_after_dismiss": "12_hours",
        "icon": "⚡",
    },
    
    # =========================================================================
    # PRO TIER NOTIFICATIONS
    # =========================================================================
    
    "pro_soft_limit_warning": {
        "trigger": "Approaching Pro soft limit (80%)",
        "format": NotificationFormat.BANNER,
        "tone": NotificationTone.INFORMATIONAL,
        "priority": 5,
        
        "notification_text": """
📊 **Usage Update:** You've used {usage_percent}% of your Pro tier included units.

You can continue beyond the limit with overage pricing (${overage_rate}/call), or consider Enterprise for unlimited capacity.
        """,
        
        "cta_primary": "View Usage Dashboard",
        "cta_url": "/dashboard/usage",
        "cta_secondary": "Explore Enterprise",
        "cta_secondary_url": "/pricing#enterprise",
        
        "dismissible": True,
        "reshow_after_dismiss": "7_days",
        "icon": "📊",
    },
    
    "pro_risk_alert": {
        "trigger": "Risk multiplier > 1.3x baseline",
        "format": NotificationFormat.ALERT,
        "tone": NotificationTone.URGENT_PROTECTIVE,
        "priority": 10,
        
        "notification_text": """
🚨 **Security Risk Detected: {risk_multiplier}x Baseline**

Your environment is {risk_percentage}% more vulnerable than optimal configuration.

Signals detected:
{risk_signals}

**Enterprise adaptive defense** stops threats automatically — auto-rollback in <4 minutes vs. 6-hour manual response.
        """,
        
        "cta_primary": "Activate Enterprise Security",
        "cta_url": "/upgrade?tier=enterprise&trigger=risk_alert",
        "cta_secondary": "View Security Dashboard",
        "cta_secondary_url": "/dashboard/security",
        
        "dismissible": False,  # Security alerts non-dismissible
        "icon": "🚨",
    },
    
    "pro_value_milestone": {
        "trigger": "Estimated value saved > $10,000",
        "format": NotificationFormat.CELEBRATION,
        "tone": NotificationTone.ACHIEVEMENT_UNLOCK,
        "priority": 6,
        
        "notification_text": """
🎯 **Value Milestone Reached: ${value_saved:,} Saved!**

Your team just hit a major ROI benchmark:
→ {hours_saved} analyst hours automated
→ ${consultant_savings:,} in consultant fees avoided
→ {errors_caught} publication errors prevented

**You're at ~40% capacity utilization.** There's ${value_remaining:,}+ more value available.

Enterprise removes the ceiling: Same team, 2.5-3x throughput.
        """,
        
        "cta_primary": "Scale Your ROI",
        "cta_url": "/upgrade?tier=enterprise&trigger=value_milestone",
        "cta_secondary": "View Value Dashboard",
        "cta_secondary_url": "/dashboard/value",
        
        "dismissible": True,
        "reshow_after_dismiss": "30_days",  # Major milestone, don't repeat often
        "show_animation": True,  # Confetti or celebration animation
        "icon": "🎯",
    },
    
    "pro_enterprise_behavior_detected": {
        "trigger": "Usage patterns match enterprise profile",
        "format": NotificationFormat.MODAL,
        "tone": NotificationTone.OPPORTUNITY_REVEAL,
        "priority": 6,
        
        "notification_text": """
📈 **You're using Pro like an Enterprise customer.**

We're seeing:
→ {project_count}+ distinct projects with separate data domains
→ {concurrent_users} concurrent users
→ Custom workflow patterns

**You've outgrown Pro.** Your team is fighting the tool instead of using it.

Enterprise removes coordination overhead: Unlimited seats, multi-tenant isolation, priority support.

**Migration takes 2-4 hours.** Zero downtime.
        """,
        
        "cta_primary": "Schedule Enterprise Consultation",
        "cta_url": "/contact?type=enterprise&trigger=behavioral",
        "cta_secondary": "See Enterprise Features",
        "cta_secondary_url": "/pricing#enterprise",
        
        "dismissible": True,
        "reshow_after_dismiss": "14_days",
        "icon": "📈",
    },
    
    # =========================================================================
    # ENTERPRISE TIER NOTIFICATIONS
    # =========================================================================
    
    "enterprise_contract_renewal_reminder": {
        "trigger": "90 days before contract renewal",
        "format": NotificationFormat.BANNER,
        "tone": NotificationTone.INFORMATIONAL,
        "priority": 5,
        
        "notification_text": """
📋 **Contract Renewal Reminder**

Your Enterprise agreement renews on {renewal_date}. 

**This year's value delivered:** ${annual_value:,}
**ROI multiple:** {roi_multiple}x

Lock in multi-year pricing for 17-30% savings, or schedule a review with your account manager.
        """,
        
        "cta_primary": "Schedule Renewal Review",
        "cta_url": "/contact?type=renewal",
        "cta_secondary": "View Multi-Year Options",
        "cta_secondary_url": "/pricing#multi-year",
        
        "dismissible": True,
        "reshow_after_dismiss": "7_days",
        "icon": "📋",
    },
    
    "enterprise_custom_model_ready": {
        "trigger": "Custom model deployment completed",
        "format": NotificationFormat.CELEBRATION,
        "tone": NotificationTone.ACHIEVEMENT_UNLOCK,
        "priority": 7,
        
        "notification_text": """
🚀 **Your Custom Model is Live!**

**{model_name}** is now deployed and ready for use.

This model was built specifically for {use_case}. It's trained on your data patterns and optimized for your analytical needs.

Expected impact: {expected_improvement}

**Start using it now** — your team has full access.
        """,
        
        "cta_primary": "Start Using {model_name}",
        "cta_url": "/models/{model_id}",
        "cta_secondary": "View Documentation",
        "cta_secondary_url": "/docs/models/{model_id}",
        
        "dismissible": True,
        "show_animation": True,
        "icon": "🚀",
    },
    
    # =========================================================================
    # UNIVERSAL NOTIFICATIONS
    # =========================================================================
    
    "new_feature_announcement": {
        "trigger": "Feature release affecting user's tier",
        "format": NotificationFormat.TOAST,
        "tone": NotificationTone.INFORMATIONAL,
        "priority": 3,
        
        "notification_text": """
✨ **New Feature:** {feature_name}

{feature_description}

Available now on your {current_tier} plan.
        """,
        
        "cta_primary": "Try It Now",
        "cta_url": "{feature_url}",
        "cta_secondary": "Learn More",
        "cta_secondary_url": "/changelog#{feature_id}",
        
        "dismissible": True,
        "reshow_after_dismiss": "never",
        "icon": "✨",
    },
    
    "maintenance_window": {
        "trigger": "Scheduled maintenance approaching",
        "format": NotificationFormat.BANNER,
        "tone": NotificationTone.INFORMATIONAL,
        "priority": 8,
        
        "notification_text": """
🔧 **Scheduled Maintenance:** {maintenance_date} at {maintenance_time}

Expected duration: {duration}. Your work will be saved automatically.

Plan heavy analysis workloads before or after this window.
        """,
        
        "cta_primary": "View Details",
        "cta_url": "/status",
        
        "dismissible": True,
        "reshow_after_dismiss": "6_hours",
        "icon": "🔧",
    },
    
    "security_best_practice": {
        "trigger": "Security improvement opportunity detected",
        "format": NotificationFormat.TOAST,
        "tone": NotificationTone.HELPFUL_WARNING,
        "priority": 4,
        
        "notification_text": """
🔐 **Security Tip:** {tip_title}

{tip_description}

Taking this action reduces your risk profile by {risk_reduction}%.
        """,
        
        "cta_primary": "Apply Now",
        "cta_url": "{action_url}",
        "cta_secondary": "Learn More",
        "cta_secondary_url": "/docs/security#{tip_id}",
        
        "dismissible": True,
        "reshow_after_dismiss": "7_days",
        "icon": "🔐",
    },
}

# Alias for backward compatibility
IN_APP_NOTIFICATIONS = IN_APP_NOTIFICATIONS_STORYBRAND


# =============================================================================
# NOTIFICATION PERSONALIZATION
# =============================================================================

def personalize_notification(
    notification_key: str,
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Personalize notification template with context data.
    
    Args:
        notification_key: Key from IN_APP_NOTIFICATIONS_STORYBRAND
        context: Dictionary of values to substitute into template
    
    Returns:
        Personalized notification configuration
    """
    if notification_key not in IN_APP_NOTIFICATIONS_STORYBRAND:
        raise ValueError(f"Unknown notification key: {notification_key}")
    
    template = IN_APP_NOTIFICATIONS_STORYBRAND[notification_key].copy()
    
    # Personalize text fields
    notification_text = template['notification_text']
    cta_primary = template['cta_primary']
    cta_url = template['cta_url']
    cta_secondary = template.get('cta_secondary', '')
    cta_secondary_url = template.get('cta_secondary_url', '')
    
    for key, value in context.items():
        placeholder = '{' + key + '}'
        placeholder_formatted = '{' + key + ':,}'
        
        str_value = str(value)
        formatted_value = f"{value:,}" if isinstance(value, (int, float)) else str_value
        
        notification_text = notification_text.replace(placeholder, str_value)
        notification_text = notification_text.replace(placeholder_formatted, formatted_value)
        
        cta_primary = cta_primary.replace(placeholder, str_value)
        cta_url = cta_url.replace(placeholder, str_value)
        
        if cta_secondary:
            cta_secondary = cta_secondary.replace(placeholder, str_value)
        if cta_secondary_url:
            cta_secondary_url = cta_secondary_url.replace(placeholder, str_value)
    
    return {
        'notification_key': notification_key,
        'notification_text': notification_text.strip(),
        'cta_primary': cta_primary,
        'cta_url': cta_url,
        'cta_secondary': cta_secondary or None,
        'cta_secondary_url': cta_secondary_url or None,
        'format': template['format'].value,
        'tone': template['tone'].value,
        'priority': template['priority'],
        'dismissible': template['dismissible'],
        'reshow_after_dismiss': template.get('reshow_after_dismiss'),
        'show_animation': template.get('show_animation', False),
        'icon': template.get('icon'),
    }


def get_notification_for_event(
    event_type: str,
    context: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Get appropriate notification for a given event type.
    
    Args:
        event_type: Type of event that occurred (e.g., 'capacity_warning', 'tier_violation')
        context: Context data for personalization
    
    Returns:
        Personalized notification dict or None if no matching notification
    """
    # Map event types to notification keys
    event_to_notification = {
        'capacity_warning': 'community_capacity_warning',
        'capacity_critical': 'community_capacity_critical',
        'tier_violation_first': 'community_tier_violation_first',
        'tier_violation_pattern': 'community_tier_violation_pattern',
        'federated_feature_gate': 'community_federated_feature_gate',
        'risk_increase': 'pro_risk_alert',
        'value_milestone': 'pro_value_milestone',
        'soft_limit_warning': 'pro_soft_limit_warning',
        'enterprise_behavior': 'pro_enterprise_behavior_detected',
        'contract_renewal': 'enterprise_contract_renewal_reminder',
    }
    
    notification_key = event_to_notification.get(event_type)
    if not notification_key:
        return None
    
    if notification_key not in IN_APP_NOTIFICATIONS_STORYBRAND:
        return None
    
    return personalize_notification(notification_key, context)


# =============================================================================
# NOTIFICATION DELIVERY ENGINE
# =============================================================================

@dataclass
class NotificationDismissal:
    """Record of user dismissing a notification."""
    notification_key: str
    customer_id: str
    dismissed_at: datetime
    reshow_at: Optional[datetime]


class NotificationDeliveryEngine:
    """
    Manages notification delivery, dismissal tracking, and rate limiting.
    """
    
    def __init__(self):
        self.dismissals: Dict[str, NotificationDismissal] = {}
        self.delivery_log: List[Dict[str, Any]] = []
    
    def should_show_notification(
        self,
        notification_key: str,
        customer_id: str,
    ) -> bool:
        """Check if notification should be shown to customer."""
        dismissal_key = f"{customer_id}:{notification_key}"
        
        if dismissal_key not in self.dismissals:
            return True
        
        dismissal = self.dismissals[dismissal_key]
        
        # If reshow_at is set and we're past that time, show again
        if dismissal.reshow_at and datetime.now() >= dismissal.reshow_at:
            return True
        
        return False
    
    def record_dismissal(
        self,
        notification_key: str,
        customer_id: str,
    ) -> None:
        """Record that customer dismissed a notification."""
        template = IN_APP_NOTIFICATIONS_STORYBRAND.get(notification_key, {})
        reshow_after = template.get('reshow_after_dismiss')
        
        reshow_at = None
        if reshow_after and reshow_after != 'never':
            if reshow_after == '6_hours':
                reshow_at = datetime.now() + timedelta(hours=6)
            elif reshow_after == '12_hours':
                reshow_at = datetime.now() + timedelta(hours=12)
            elif reshow_after == '24_hours':
                reshow_at = datetime.now() + timedelta(days=1)
            elif reshow_after == '3_days':
                reshow_at = datetime.now() + timedelta(days=3)
            elif reshow_after == '7_days':
                reshow_at = datetime.now() + timedelta(days=7)
            elif reshow_after == '14_days':
                reshow_at = datetime.now() + timedelta(days=14)
            elif reshow_after == '30_days':
                reshow_at = datetime.now() + timedelta(days=30)
        
        dismissal_key = f"{customer_id}:{notification_key}"
        self.dismissals[dismissal_key] = NotificationDismissal(
            notification_key=notification_key,
            customer_id=customer_id,
            dismissed_at=datetime.now(),
            reshow_at=reshow_at,
        )
    
    def get_active_notifications(
        self,
        customer_id: str,
        triggered_notifications: List[str],
        max_notifications: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Get prioritized list of notifications to show customer.
        
        Args:
            customer_id: Customer identifier
            triggered_notifications: List of notification keys that have been triggered
            max_notifications: Maximum number to return (prevent notification fatigue)
        
        Returns:
            Sorted list of notification configs, highest priority first
        """
        active = []
        
        for key in triggered_notifications:
            if self.should_show_notification(key, customer_id):
                template = IN_APP_NOTIFICATIONS_STORYBRAND.get(key)
                if template:
                    active.append({
                        'key': key,
                        'priority': template['priority'],
                        'format': template['format'].value,
                    })
        
        # Sort by priority (higher = more urgent)
        active.sort(key=lambda x: x['priority'], reverse=True)
        
        # Return top N
        return active[:max_notifications]
    
    def record_delivery(
        self,
        notification_key: str,
        customer_id: str,
        context: Dict[str, Any],
    ) -> None:
        """Record notification delivery for analytics."""
        self.delivery_log.append({
            'notification_key': notification_key,
            'customer_id': customer_id,
            'delivered_at': datetime.now().isoformat(),
            'context': context,
        })


# =============================================================================
# TRIGGER EVALUATION
# =============================================================================

def evaluate_notification_triggers(
    customer_data: Dict[str, Any],
    usage_data: Dict[str, Any],
    security_data: Dict[str, Any],
) -> List[str]:
    """
    Evaluate all notification triggers against current customer state.
    
    Returns list of triggered notification keys.
    """
    triggered = []
    
    current_tier = customer_data.get('current_tier', 'community')
    
    # Community tier triggers
    if current_tier == 'community':
        api_calls_used = usage_data.get('api_calls_used', 0)
        api_limit = usage_data.get('api_limit', 10000)
        usage_percent = (api_calls_used / api_limit) * 100 if api_limit > 0 else 0
        
        if usage_percent >= 95:
            triggered.append('community_capacity_critical')
        elif usage_percent >= 80:
            triggered.append('community_capacity_warning')
        
        violations_24h = usage_data.get('tier_violations_24h', 0)
        if violations_24h >= 3:
            triggered.append('community_tier_violation_pattern')
        elif violations_24h == 1:
            triggered.append('community_tier_violation_first')
    
    # Pro tier triggers
    if current_tier == 'pro':
        api_calls_used = usage_data.get('api_calls_used', 0)
        api_limit = usage_data.get('api_limit', 100000)
        usage_percent = (api_calls_used / api_limit) * 100 if api_limit > 0 else 0
        
        if usage_percent >= 80:
            triggered.append('pro_soft_limit_warning')
        
        risk_multiplier = security_data.get('risk_multiplier', 1.0)
        if risk_multiplier > 1.3:
            triggered.append('pro_risk_alert')
        
        value_saved = usage_data.get('value_saved', 0)
        if value_saved >= 10000:
            triggered.append('pro_value_milestone')
        
        project_count = usage_data.get('project_count', 0)
        concurrent_users = usage_data.get('concurrent_users', 0)
        if project_count >= 4 and concurrent_users >= 6:
            triggered.append('pro_enterprise_behavior_detected')
    
    # Enterprise tier triggers
    if current_tier == 'enterprise':
        days_to_renewal = customer_data.get('days_to_renewal', 999)
        if days_to_renewal <= 90:
            triggered.append('enterprise_contract_renewal_reminder')
    
    return triggered
