# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.upsell_integration
# This stub remains for backward compatibility but will be removed in v2.0.
import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.upsell_integration is deprecated. "
    "Import from 'app.services.billing.upsell_integration' instead.",
    DeprecationWarning,
    stacklevel=2
)

"""
KRL Upsell Message Integration
==============================

Wires StoryBrand upsell messages to existing billing triggers.

This module:
1. Intercepts UpsellEvents from the billing system
2. Enriches them with personalized StoryBrand narrative messages
3. Routes to email delivery (SendGrid/SMTP) and in-app notifications
4. Tracks A/B testing variants and conversion metrics

Day 1-2 Deployment Roadmap:
- [x] Wire upsell messages to existing triggers
- [ ] Deploy in-app notifications
- [ ] Build awareness-stage landing pages
- [ ] Wire awareness routing to paid campaigns

Expected Impact: 2-3x conversion lift over transactional messages within 14 days.

Architecture:
    BillingBridge → UpsellEngine → on_upsell_triggered callback
                                        ↓
                              UpsellMessageIntegration
                                        ↓
                    ┌───────────────────┴───────────────────┐
                    ↓                                       ↓
          StorybrandUpsell                         InAppNotifications
          (email delivery)                         (dashboard banners)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
import logging
import uuid
import json
import hashlib

# Import our StoryBrand modules
from .storybrand_upsell import (
    UPSELL_MESSAGES_STORYBRAND,
    AB_TEST_FRAMEWORK,
    personalize_upsell_message,
)
from .inapp_notifications import (
    IN_APP_NOTIFICATIONS,
    NotificationFormat,
    get_notification_for_event,
    evaluate_notification_triggers,
)

# Import billing types
from . import (
    UpsellEvent,
    UpsellTriggerType,
    BillingTier,
    RevenueEventType,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

class DeliveryChannel(Enum):
    """Channels for delivering upsell messages."""
    EMAIL = "email"
    IN_APP_BANNER = "in_app_banner"
    IN_APP_MODAL = "in_app_modal"
    IN_APP_TOAST = "in_app_toast"
    SLACK_WEBHOOK = "slack_webhook"
    SMS = "sms"


class EmailProvider(Enum):
    """Supported email providers."""
    SENDGRID = "sendgrid"
    MAILGUN = "mailgun"
    AWS_SES = "aws_ses"
    SMTP = "smtp"
    MOCK = "mock"  # For testing


@dataclass
class EmailConfig:
    """Email provider configuration."""
    provider: EmailProvider = EmailProvider.MOCK
    api_key: str = ""
    from_email: str = "upgrades@krlabs.dev"
    from_name: str = "Khipu Intelligence"
    reply_to: str = "support@krlabs.dev"
    
    # SendGrid specific
    sendgrid_template_id: Optional[str] = None
    
    # SMTP specific
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""


@dataclass
class IntegrationConfig:
    """Configuration for upsell message integration."""
    # Delivery channels
    enabled_channels: List[DeliveryChannel] = field(default_factory=lambda: [
        DeliveryChannel.EMAIL,
        DeliveryChannel.IN_APP_BANNER,
    ])
    
    # Email config
    email_config: EmailConfig = field(default_factory=EmailConfig)
    
    # Timing
    email_delay_seconds: int = 0  # Delay before sending (allows for batching)
    in_app_delay_seconds: int = 0  # Immediate
    
    # A/B Testing
    ab_testing_enabled: bool = True
    default_variant: str = "B"  # StoryBrand variant
    
    # Rate limits
    max_emails_per_day_per_tenant: int = 3
    max_in_app_per_session: int = 2
    
    # Tracking
    track_opens: bool = True
    track_clicks: bool = True
    conversion_window_days: int = 14
    
    # Dashboard webhook
    dashboard_webhook_url: Optional[str] = None


# =============================================================================
# Trigger Type to StoryBrand Template Mapping
# =============================================================================

# Map billing system trigger types to StoryBrand message templates
TRIGGER_TO_TEMPLATE_MAP: Dict[Tuple[UpsellTriggerType, BillingTier, BillingTier], str] = {
    # Community → Pro triggers
    (UpsellTriggerType.USAGE_THRESHOLD, BillingTier.COMMUNITY, BillingTier.PRO): "capacity_expansion",
    (UpsellTriggerType.FEATURE_GATE, BillingTier.COMMUNITY, BillingTier.PRO): "federated_learning",
    (UpsellTriggerType.TIER_VIOLATION, BillingTier.COMMUNITY, BillingTier.PRO): "tier_violation",
    
    # Pro → Enterprise triggers  
    (UpsellTriggerType.RISK_INCREASE, BillingTier.PRO, BillingTier.ENTERPRISE): "risk_audit",
    (UpsellTriggerType.VALUE_REALIZATION, BillingTier.PRO, BillingTier.ENTERPRISE): "value_realization",
    (UpsellTriggerType.BEHAVIORAL_PATTERN, BillingTier.PRO, BillingTier.ENTERPRISE): "behavioral_pattern",
}

# Fallback mapping when exact match not found
TIER_UPGRADE_FALLBACK: Dict[Tuple[BillingTier, BillingTier], str] = {
    (BillingTier.COMMUNITY, BillingTier.PRO): "capacity_expansion",
    (BillingTier.PRO, BillingTier.ENTERPRISE): "value_realization",
}


def get_template_key_for_event(event: UpsellEvent) -> str:
    """
    Determine which StoryBrand template to use for an upsell event.
    
    Returns the template key from UPSELL_MESSAGES_STORYBRAND.
    """
    # Try exact match first
    exact_key = (event.trigger_type, event.source_tier, event.target_tier)
    if exact_key in TRIGGER_TO_TEMPLATE_MAP:
        return TRIGGER_TO_TEMPLATE_MAP[exact_key]
    
    # Try tier upgrade fallback
    tier_key = (event.source_tier, event.target_tier)
    if tier_key in TIER_UPGRADE_FALLBACK:
        return TIER_UPGRADE_FALLBACK[tier_key]
    
    # Default based on target tier
    if event.target_tier == BillingTier.PRO:
        return "capacity_expansion"
    elif event.target_tier == BillingTier.ENTERPRISE:
        return "value_realization"
    
    return "capacity_expansion"  # Ultimate fallback


# =============================================================================
# Email Delivery
# =============================================================================

class EmailDeliveryResult:
    """Result of an email delivery attempt."""
    def __init__(
        self,
        success: bool,
        message_id: Optional[str] = None,
        error: Optional[str] = None,
        provider_response: Optional[Dict[str, Any]] = None,
    ):
        self.success = success
        self.message_id = message_id
        self.error = error
        self.provider_response = provider_response


class EmailDeliveryService:
    """
    Email delivery service supporting multiple providers.
    
    SendGrid integration example:
    ```python
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content
    
    sg = sendgrid.SendGridAPIClient(api_key=config.api_key)
    message = Mail(
        from_email=config.from_email,
        to_emails=recipient,
        subject=subject,
        html_content=body_html
    )
    response = sg.send(message)
    ```
    """
    
    def __init__(self, config: EmailConfig):
        self.config = config
        self._sent_count: Dict[str, int] = {}  # tenant_id -> daily count
        self._last_reset: datetime = datetime.now()
    
    async def send(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str,
        tenant_id: str,
        tracking_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EmailDeliveryResult:
        """Send an email through the configured provider."""
        
        # Reset daily counter if needed
        now = datetime.now()
        if (now - self._last_reset).days >= 1:
            self._sent_count = {}
            self._last_reset = now
        
        # Add tracking pixel and click tracking
        if metadata and metadata.get("track_opens"):
            body_html = self._add_tracking_pixel(body_html, tracking_id)
        
        if metadata and metadata.get("track_clicks"):
            body_html = self._add_click_tracking(body_html, tracking_id)
        
        # Route to provider
        if self.config.provider == EmailProvider.SENDGRID:
            return await self._send_sendgrid(
                to_email, subject, body_html, body_text, tracking_id, metadata
            )
        elif self.config.provider == EmailProvider.AWS_SES:
            return await self._send_ses(
                to_email, subject, body_html, body_text, tracking_id, metadata
            )
        elif self.config.provider == EmailProvider.SMTP:
            return await self._send_smtp(
                to_email, subject, body_html, body_text, tracking_id, metadata
            )
        elif self.config.provider == EmailProvider.MOCK:
            return self._send_mock(
                to_email, subject, body_html, body_text, tracking_id, metadata
            )
        else:
            return EmailDeliveryResult(
                success=False,
                error=f"Unknown provider: {self.config.provider}"
            )
    
    async def _send_sendgrid(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str,
        tracking_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EmailDeliveryResult:
        """Send via SendGrid API."""
        try:
            # Import sendgrid only when needed
            import sendgrid
            from sendgrid.helpers.mail import Mail, Email, To, Content
            
            sg = sendgrid.SendGridAPIClient(api_key=self.config.api_key)
            
            message = Mail(
                from_email=Email(self.config.from_email, self.config.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", body_html),
            )
            
            # Add plain text version
            message.add_content(Content("text/plain", body_text))
            
            # Add custom headers for tracking
            message.header = {"X-KRL-Tracking-Id": tracking_id}
            
            # Send
            response = sg.send(message)
            
            return EmailDeliveryResult(
                success=response.status_code in [200, 201, 202],
                message_id=response.headers.get("X-Message-Id"),
                provider_response={"status_code": response.status_code},
            )
            
        except ImportError:
            return EmailDeliveryResult(
                success=False,
                error="SendGrid library not installed. Run: pip install sendgrid"
            )
        except Exception as e:
            logger.error(f"SendGrid error: {e}")
            return EmailDeliveryResult(
                success=False,
                error=str(e)
            )
    
    async def _send_ses(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str,
        tracking_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EmailDeliveryResult:
        """Send via AWS SES."""
        try:
            import boto3
            
            ses = boto3.client('ses')
            
            response = ses.send_email(
                Source=f"{self.config.from_name} <{self.config.from_email}>",
                Destination={"ToAddresses": [to_email]},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {
                        "Html": {"Data": body_html},
                        "Text": {"Data": body_text},
                    }
                },
                Tags=[{"Name": "TrackingId", "Value": tracking_id}]
            )
            
            return EmailDeliveryResult(
                success=True,
                message_id=response.get("MessageId"),
                provider_response=response,
            )
            
        except ImportError:
            return EmailDeliveryResult(
                success=False,
                error="boto3 library not installed. Run: pip install boto3"
            )
        except Exception as e:
            logger.error(f"AWS SES error: {e}")
            return EmailDeliveryResult(
                success=False,
                error=str(e)
            )
    
    async def _send_smtp(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str,
        tracking_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EmailDeliveryResult:
        """Send via SMTP."""
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.config.from_name} <{self.config.from_email}>"
            msg['To'] = to_email
            msg['X-KRL-Tracking-Id'] = tracking_id
            
            part1 = MIMEText(body_text, 'plain')
            part2 = MIMEText(body_html, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.smtp_username, self.config.smtp_password)
                server.sendmail(
                    self.config.from_email,
                    to_email,
                    msg.as_string()
                )
            
            return EmailDeliveryResult(
                success=True,
                message_id=tracking_id,
            )
            
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return EmailDeliveryResult(
                success=False,
                error=str(e)
            )
    
    def _send_mock(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str,
        tracking_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EmailDeliveryResult:
        """Mock send for testing."""
        logger.info(f"[MOCK EMAIL] To: {to_email}, Subject: {subject}")
        logger.debug(f"[MOCK EMAIL] Body: {body_text[:200]}...")
        
        return EmailDeliveryResult(
            success=True,
            message_id=f"mock-{tracking_id}",
            provider_response={"mock": True},
        )
    
    def _add_tracking_pixel(self, html: str, tracking_id: str) -> str:
        """Add invisible tracking pixel to HTML."""
        pixel = f'<img src="https://track.krlabs.dev/open/{tracking_id}" width="1" height="1" style="display:none;" />'
        return html.replace("</body>", f"{pixel}</body>")
    
    def _add_click_tracking(self, html: str, tracking_id: str) -> str:
        """Wrap links with click tracking redirect."""
        import re
        
        def wrap_link(match):
            original_url = match.group(1)
            encoded = hashlib.md5(original_url.encode()).hexdigest()[:8]
            tracked = f"https://track.krlabs.dev/click/{tracking_id}/{encoded}?url={original_url}"
            return f'href="{tracked}"'
        
        return re.sub(r'href="([^"]+)"', wrap_link, html)


# =============================================================================
# In-App Notification Delivery
# =============================================================================

@dataclass
class InAppNotificationPayload:
    """Payload for in-app notification delivery."""
    notification_id: str
    tenant_id: str
    format: NotificationFormat
    
    title: str
    message: str
    cta_text: str
    cta_url: str
    
    priority: int
    dismissable: bool
    auto_dismiss_seconds: Optional[int]
    
    theme: str  # warning, success, info, upgrade
    icon: str
    
    # Tracking
    tracking_id: str
    ab_variant: str
    
    # Display rules
    show_after: datetime
    hide_after: Optional[datetime]
    max_impressions: int
    
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "notification_id": self.notification_id,
            "tenant_id": self.tenant_id,
            "format": self.format.value,
            "title": self.title,
            "message": self.message,
            "cta_text": self.cta_text,
            "cta_url": self.cta_url,
            "priority": self.priority,
            "dismissable": self.dismissable,
            "auto_dismiss_seconds": self.auto_dismiss_seconds,
            "theme": self.theme,
            "icon": self.icon,
            "tracking_id": self.tracking_id,
            "ab_variant": self.ab_variant,
            "show_after": self.show_after.isoformat(),
            "hide_after": self.hide_after.isoformat() if self.hide_after else None,
            "max_impressions": self.max_impressions,
            "created_at": self.created_at.isoformat(),
        }


class InAppDeliveryService:
    """
    Manages in-app notification queue for dashboard rendering.
    
    Notifications are stored and served via the dashboard hooks
    when the user is active in the application.
    """
    
    def __init__(self):
        # Pending notifications per tenant
        self._queue: Dict[str, List[InAppNotificationPayload]] = {}
        
        # Delivered notifications for deduplication
        self._delivered: Dict[str, datetime] = {}  # notification_id -> delivered_at
        
        # Impression counts
        self._impressions: Dict[str, int] = {}  # notification_id -> count
    
    def queue_notification(
        self,
        payload: InAppNotificationPayload,
    ) -> bool:
        """Add notification to the queue."""
        if payload.tenant_id not in self._queue:
            self._queue[payload.tenant_id] = []
        
        # Check for duplicates (same tracking_id)
        existing = [n for n in self._queue[payload.tenant_id] 
                    if n.tracking_id == payload.tracking_id]
        if existing:
            logger.debug(f"Duplicate notification skipped: {payload.tracking_id}")
            return False
        
        self._queue[payload.tenant_id].append(payload)
        logger.info(f"Queued in-app notification for {payload.tenant_id}: {payload.title}")
        
        return True
    
    def get_pending_notifications(
        self,
        tenant_id: str,
        session_limit: int = 2,
    ) -> List[InAppNotificationPayload]:
        """Get pending notifications for a tenant session."""
        if tenant_id not in self._queue:
            return []
        
        now = datetime.now()
        eligible = []
        
        for notification in self._queue[tenant_id]:
            # Check time window
            if notification.show_after > now:
                continue
            if notification.hide_after and notification.hide_after < now:
                continue
            
            # Check impression limit
            impressions = self._impressions.get(notification.notification_id, 0)
            if impressions >= notification.max_impressions:
                continue
            
            eligible.append(notification)
        
        # Sort by priority (higher first)
        eligible.sort(key=lambda x: x.priority, reverse=True)
        
        # Limit per session
        return eligible[:session_limit]
    
    def record_impression(self, notification_id: str) -> None:
        """Record that a notification was shown."""
        self._impressions[notification_id] = self._impressions.get(notification_id, 0) + 1
    
    def record_dismissal(self, notification_id: str, tenant_id: str) -> None:
        """Record that a notification was dismissed."""
        if tenant_id in self._queue:
            self._queue[tenant_id] = [
                n for n in self._queue[tenant_id]
                if n.notification_id != notification_id
            ]
    
    def clear_tenant_queue(self, tenant_id: str) -> None:
        """Clear all pending notifications for a tenant."""
        self._queue.pop(tenant_id, None)


# =============================================================================
# Main Integration Class
# =============================================================================

class UpsellMessageIntegration:
    """
    Main integration class that wires StoryBrand upsell messages
    to the existing billing trigger system.
    
    Usage:
    ```python
    # Create integration
    integration = UpsellMessageIntegration(config)
    
    # Connect to billing controller
    controller.upsell_engine.on_upsell_triggered(integration.handle_upsell_event)
    
    # Or use with BillingBridge
    bridge.on_upsell(integration.handle_upsell_event)
    ```
    """
    
    def __init__(
        self,
        config: Optional[IntegrationConfig] = None,
        customer_data_provider: Optional[Callable[[str], Dict[str, Any]]] = None,
        usage_data_provider: Optional[Callable[[str], Dict[str, Any]]] = None,
    ):
        self.config = config or IntegrationConfig()
        
        # Data providers (injected for customer/usage data lookup)
        self._customer_provider = customer_data_provider or self._default_customer_provider
        self._usage_provider = usage_data_provider or self._default_usage_provider
        
        # Delivery services
        self._email_service = EmailDeliveryService(self.config.email_config)
        self._inapp_service = InAppDeliveryService()
        
        # Tracking
        self._events_processed: int = 0
        self._emails_sent: int = 0
        self._inapp_queued: int = 0
        self._ab_variants: Dict[str, str] = {}  # tenant_id -> variant
        
        # Conversion tracking
        self._conversion_tracking: Dict[str, Dict[str, Any]] = {}  # tracking_id -> data
        
        # Callbacks
        self._on_email_sent: List[Callable[[str, str, Dict], None]] = []
        self._on_inapp_queued: List[Callable[[InAppNotificationPayload], None]] = []
        
        logger.info("UpsellMessageIntegration initialized")
    
    # =========================================================================
    # Main Entry Point
    # =========================================================================
    
    async def handle_upsell_event(self, event: UpsellEvent) -> Dict[str, Any]:
        """
        Main handler for upsell events from the billing system.
        
        This is the callback registered with:
        - UpsellEngine.on_upsell_triggered()
        - BillingBridge.on_upsell()
        """
        self._events_processed += 1
        
        tracking_id = f"krl-upsell-{event.event_id}-{uuid.uuid4().hex[:8]}"
        results: Dict[str, Any] = {
            "event_id": event.event_id,
            "tracking_id": tracking_id,
            "channels": {},
        }
        
        try:
            # 1. Fetch customer and usage data
            customer_data = self._customer_provider(event.tenant_id)
            usage_data = self._usage_provider(event.tenant_id)
            
            # Enrich with event context
            usage_data.update({
                "current_tier": event.source_tier.value,
                "target_tier": event.target_tier.value,
                "trigger_context": event.trigger_context,
            })
            
            # 2. Determine template and A/B variant
            template_key = get_template_key_for_event(event)
            ab_variant = self._get_ab_variant(event.tenant_id)
            
            # 3. Generate personalized StoryBrand message
            personalized = personalize_upsell_message(
                template_key=template_key,
                customer_data=customer_data,
                usage_data=usage_data,
                ab_variant=ab_variant,
            )
            
            if not personalized:
                logger.warning(f"No template found for key: {template_key}")
                return {"error": f"Template not found: {template_key}"}
            
            # 4. Store conversion tracking data
            self._conversion_tracking[tracking_id] = {
                "event_id": event.event_id,
                "tenant_id": event.tenant_id,
                "template_key": template_key,
                "ab_variant": ab_variant,
                "source_tier": event.source_tier.value,
                "target_tier": event.target_tier.value,
                "created_at": datetime.now().isoformat(),
                "email_opened": False,
                "email_clicked": False,
                "inapp_viewed": False,
                "inapp_clicked": False,
                "converted": False,
            }
            
            # 5. Deliver via enabled channels
            for channel in self.config.enabled_channels:
                if channel == DeliveryChannel.EMAIL:
                    email_result = await self._deliver_email(
                        event, personalized, customer_data, tracking_id, ab_variant
                    )
                    results["channels"]["email"] = email_result
                
                elif channel in [
                    DeliveryChannel.IN_APP_BANNER,
                    DeliveryChannel.IN_APP_MODAL,
                    DeliveryChannel.IN_APP_TOAST,
                ]:
                    inapp_result = self._deliver_inapp(
                        event, personalized, channel, tracking_id, ab_variant
                    )
                    results["channels"]["in_app"] = inapp_result
            
            results["success"] = True
            logger.info(f"Processed upsell event {event.event_id} via {len(results['channels'])} channels")
            
        except Exception as e:
            logger.error(f"Error processing upsell event: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results
    
    # =========================================================================
    # Email Delivery
    # =========================================================================
    
    async def _deliver_email(
        self,
        event: UpsellEvent,
        personalized: Dict[str, Any],
        customer_data: Dict[str, Any],
        tracking_id: str,
        ab_variant: str,
    ) -> Dict[str, Any]:
        """Deliver personalized upsell via email."""
        
        # Get recipient email
        to_email = customer_data.get("email")
        if not to_email:
            return {"success": False, "error": "No email address for tenant"}
        
        # Build email content
        subject = personalized.get("subject_line", "Unlock More with Khipu Intelligence")
        
        # HTML email body
        body_html = self._render_email_html(personalized, customer_data, tracking_id)
        
        # Plain text fallback
        body_text = self._render_email_text(personalized)
        
        # Send
        result = await self._email_service.send(
            to_email=to_email,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            tenant_id=event.tenant_id,
            tracking_id=tracking_id,
            metadata={
                "track_opens": self.config.track_opens,
                "track_clicks": self.config.track_clicks,
                "ab_variant": ab_variant,
            }
        )
        
        if result.success:
            self._emails_sent += 1
            for cb in self._on_email_sent:
                cb(event.tenant_id, tracking_id, personalized)
        
        return {
            "success": result.success,
            "message_id": result.message_id,
            "error": result.error,
        }
    
    def _render_email_html(
        self,
        personalized: Dict[str, Any],
        customer_data: Dict[str, Any],
        tracking_id: str,
    ) -> str:
        """Render HTML email template with StoryBrand content."""
        
        customer_name = customer_data.get("company_name", customer_data.get("name", "there"))
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{personalized.get('subject_line', 'Khipu Intelligence')}</title>
</head>
<body style="margin:0;padding:0;font-family:Arial,sans-serif;background-color:#f4f4f4;">
    <table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;margin:0 auto;background:#ffffff;">
        
        <!-- Header -->
        <tr>
            <td style="background:#1a365d;padding:20px;text-align:center;">
                <img src="https://krlabs.dev/logo-white.png" alt="Khipu Intelligence" width="150" style="max-width:150px;">
            </td>
        </tr>
        
        <!-- Hero / Opening -->
        <tr>
            <td style="padding:30px 40px 20px;">
                <p style="color:#4a5568;font-size:16px;line-height:1.6;margin:0;">
                    Hi {customer_name},
                </p>
                <h1 style="color:#1a365d;font-size:24px;margin:20px 0 10px;">
                    {personalized.get('opening', 'Your analytics are growing')}
                </h1>
            </td>
        </tr>
        
        <!-- Problem Statement (StoryBrand: External Problem → Internal Frustration) -->
        <tr>
            <td style="padding:0 40px 20px;">
                <p style="color:#4a5568;font-size:16px;line-height:1.6;">
                    {personalized.get('problem_hook', '')}
                </p>
                <p style="color:#718096;font-style:italic;font-size:14px;line-height:1.6;">
                    {personalized.get('internal_frustration', '')}
                </p>
            </td>
        </tr>
        
        <!-- Guide Introduction (StoryBrand: Brand as Guide) -->
        <tr>
            <td style="padding:0 40px 20px;">
                <p style="color:#4a5568;font-size:16px;line-height:1.6;">
                    {personalized.get('guide_intro', '')}
                </p>
            </td>
        </tr>
        
        <!-- The Plan (StoryBrand: Clear Plan) -->
        <tr>
            <td style="padding:0 40px 20px;background:#f7fafc;">
                <h2 style="color:#2d3748;font-size:18px;margin:20px 0 15px;">
                    Here's how to unlock more:
                </h2>
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="padding:10px 0;">
                            <span style="display:inline-block;width:24px;height:24px;background:#48bb78;color:#fff;border-radius:50%;text-align:center;line-height:24px;font-size:14px;margin-right:10px;">1</span>
                            <span style="color:#4a5568;">{personalized.get('plan_step_1', 'Click the upgrade button below')}</span>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:10px 0;">
                            <span style="display:inline-block;width:24px;height:24px;background:#48bb78;color:#fff;border-radius:50%;text-align:center;line-height:24px;font-size:14px;margin-right:10px;">2</span>
                            <span style="color:#4a5568;">{personalized.get('plan_step_2', 'Choose your new plan')}</span>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:10px 0;">
                            <span style="display:inline-block;width:24px;height:24px;background:#48bb78;color:#fff;border-radius:50%;text-align:center;line-height:24px;font-size:14px;margin-right:10px;">3</span>
                            <span style="color:#4a5568;">{personalized.get('plan_step_3', 'Start using premium features immediately')}</span>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        
        <!-- Success Vision (StoryBrand: Success Ending) -->
        <tr>
            <td style="padding:20px 40px;">
                <p style="color:#2d3748;font-size:16px;line-height:1.6;font-weight:600;">
                    🎯 {personalized.get('success_vision', '')}
                </p>
            </td>
        </tr>
        
        <!-- CTA Button -->
        <tr>
            <td style="padding:10px 40px 30px;text-align:center;">
                <a href="{personalized.get('cta_url', 'https://krlabs.dev/upgrade')}"
                   style="display:inline-block;background:#48bb78;color:#ffffff;padding:15px 40px;text-decoration:none;border-radius:6px;font-size:16px;font-weight:600;">
                    {personalized.get('cta_text', 'Upgrade Now')}
                </a>
            </td>
        </tr>
        
        <!-- Stakes / Urgency (StoryBrand: Failure Ending) -->
        <tr>
            <td style="padding:0 40px 20px;">
                <p style="color:#718096;font-size:14px;line-height:1.6;">
                    {personalized.get('stakes', '')}
                </p>
            </td>
        </tr>
        
        <!-- Signature -->
        <tr>
            <td style="padding:20px 40px 30px;border-top:1px solid #e2e8f0;">
                <p style="color:#4a5568;font-size:14px;line-height:1.6;margin:0;">
                    {personalized.get('closing', 'Best,')}
                </p>
                <p style="color:#2d3748;font-size:14px;font-weight:600;margin:5px 0 0;">
                    {personalized.get('signature', 'The Khipu Intelligence Team')}
                </p>
            </td>
        </tr>
        
        <!-- Footer -->
        <tr>
            <td style="background:#f7fafc;padding:20px 40px;text-align:center;">
                <p style="color:#a0aec0;font-size:12px;margin:0;">
                    Khipu Intelligence • Data-Driven Policy Intelligence<br>
                    <a href="https://krlabs.dev/unsubscribe?t={tracking_id}" style="color:#a0aec0;">Unsubscribe</a> |
                    <a href="https://krlabs.dev/preferences" style="color:#a0aec0;">Email Preferences</a>
                </p>
            </td>
        </tr>
        
    </table>
</body>
</html>
"""
    
    def _render_email_text(self, personalized: Dict[str, Any]) -> str:
        """Render plain text version of email."""
        return f"""
{personalized.get('opening', '')}

{personalized.get('problem_hook', '')}

{personalized.get('internal_frustration', '')}

{personalized.get('guide_intro', '')}

Here's how to unlock more:
1. {personalized.get('plan_step_1', 'Click the upgrade link below')}
2. {personalized.get('plan_step_2', 'Choose your new plan')}
3. {personalized.get('plan_step_3', 'Start using premium features')}

{personalized.get('success_vision', '')}

→ {personalized.get('cta_text', 'Upgrade Now')}: {personalized.get('cta_url', '')}

{personalized.get('stakes', '')}

{personalized.get('closing', 'Best,')}
{personalized.get('signature', 'The Khipu Intelligence Team')}

---
Khipu Intelligence • Data-Driven Policy Intelligence
"""
    
    # =========================================================================
    # In-App Notification Delivery
    # =========================================================================
    
    def _deliver_inapp(
        self,
        event: UpsellEvent,
        personalized: Dict[str, Any],
        channel: DeliveryChannel,
        tracking_id: str,
        ab_variant: str,
    ) -> Dict[str, Any]:
        """Create and queue in-app notification."""
        
        # Map channel to notification format
        format_map = {
            DeliveryChannel.IN_APP_BANNER: NotificationFormat.BANNER,
            DeliveryChannel.IN_APP_MODAL: NotificationFormat.MODAL,
            DeliveryChannel.IN_APP_TOAST: NotificationFormat.TOAST,
        }
        notification_format = format_map.get(channel, NotificationFormat.BANNER)
        
        # Create notification payload
        notification_id = f"notif-{event.event_id}-{uuid.uuid4().hex[:6]}"
        
        payload = InAppNotificationPayload(
            notification_id=notification_id,
            tenant_id=event.tenant_id,
            format=notification_format,
            title=personalized.get("subject_line", "Upgrade Available"),
            message=personalized.get("opening", ""),
            cta_text=personalized.get("cta_text", "Learn More"),
            cta_url=personalized.get("cta_url", "https://krlabs.dev/upgrade"),
            priority=self._calculate_priority(event),
            dismissable=True,
            auto_dismiss_seconds=None if notification_format == NotificationFormat.MODAL else 30,
            theme="upgrade",
            icon="⬆️",
            tracking_id=tracking_id,
            ab_variant=ab_variant,
            show_after=datetime.now(),
            hide_after=datetime.now() + timedelta(days=7),
            max_impressions=3,
        )
        
        # Queue it
        queued = self._inapp_service.queue_notification(payload)
        
        if queued:
            self._inapp_queued += 1
            for cb in self._on_inapp_queued:
                cb(payload)
        
        return {
            "success": queued,
            "notification_id": notification_id,
            "format": notification_format.value,
        }
    
    def _calculate_priority(self, event: UpsellEvent) -> int:
        """Calculate notification priority based on trigger type and tier."""
        base_priority = 50
        
        # Higher priority for critical triggers
        if event.trigger_type == UpsellTriggerType.TIER_VIOLATION:
            base_priority += 30
        elif event.trigger_type == UpsellTriggerType.RISK_INCREASE:
            base_priority += 25
        elif event.trigger_type == UpsellTriggerType.USAGE_THRESHOLD:
            base_priority += 20
        
        # Higher priority for enterprise upsells (higher value)
        if event.target_tier == BillingTier.ENTERPRISE:
            base_priority += 10
        
        return min(base_priority, 100)
    
    # =========================================================================
    # A/B Testing
    # =========================================================================
    
    def _get_ab_variant(self, tenant_id: str) -> str:
        """Get or assign A/B test variant for a tenant."""
        if not self.config.ab_testing_enabled:
            return self.config.default_variant
        
        if tenant_id not in self._ab_variants:
            # Deterministic assignment based on tenant_id hash
            hash_val = int(hashlib.md5(tenant_id.encode()).hexdigest(), 16)
            self._ab_variants[tenant_id] = "A" if hash_val % 2 == 0 else "B"
        
        return self._ab_variants[tenant_id]
    
    # =========================================================================
    # Conversion Tracking
    # =========================================================================
    
    def track_email_open(self, tracking_id: str) -> bool:
        """Track that an email was opened."""
        if tracking_id in self._conversion_tracking:
            self._conversion_tracking[tracking_id]["email_opened"] = True
            self._conversion_tracking[tracking_id]["email_opened_at"] = datetime.now().isoformat()
            return True
        return False
    
    def track_email_click(self, tracking_id: str) -> bool:
        """Track that an email link was clicked."""
        if tracking_id in self._conversion_tracking:
            self._conversion_tracking[tracking_id]["email_clicked"] = True
            self._conversion_tracking[tracking_id]["email_clicked_at"] = datetime.now().isoformat()
            return True
        return False
    
    def track_inapp_view(self, tracking_id: str) -> bool:
        """Track that an in-app notification was viewed."""
        if tracking_id in self._conversion_tracking:
            self._conversion_tracking[tracking_id]["inapp_viewed"] = True
            self._conversion_tracking[tracking_id]["inapp_viewed_at"] = datetime.now().isoformat()
            return True
        return False
    
    def track_inapp_click(self, tracking_id: str) -> bool:
        """Track that an in-app notification CTA was clicked."""
        if tracking_id in self._conversion_tracking:
            self._conversion_tracking[tracking_id]["inapp_clicked"] = True
            self._conversion_tracking[tracking_id]["inapp_clicked_at"] = datetime.now().isoformat()
            return True
        return False
    
    def track_conversion(self, tracking_id: str, conversion_data: Dict[str, Any]) -> bool:
        """Track that a tracked upsell converted to purchase."""
        if tracking_id in self._conversion_tracking:
            self._conversion_tracking[tracking_id]["converted"] = True
            self._conversion_tracking[tracking_id]["converted_at"] = datetime.now().isoformat()
            self._conversion_tracking[tracking_id]["conversion_data"] = conversion_data
            return True
        return False
    
    def get_conversion_metrics(self) -> Dict[str, Any]:
        """Get aggregate conversion metrics for A/B analysis."""
        metrics = {
            "total_events": self._events_processed,
            "total_emails": self._emails_sent,
            "total_inapp": self._inapp_queued,
            "variants": {
                "A": {"sent": 0, "opened": 0, "clicked": 0, "converted": 0},
                "B": {"sent": 0, "opened": 0, "clicked": 0, "converted": 0},
            }
        }
        
        for tracking_id, data in self._conversion_tracking.items():
            variant = data.get("ab_variant", "B")
            if variant in metrics["variants"]:
                metrics["variants"][variant]["sent"] += 1
                if data.get("email_opened"):
                    metrics["variants"][variant]["opened"] += 1
                if data.get("email_clicked") or data.get("inapp_clicked"):
                    metrics["variants"][variant]["clicked"] += 1
                if data.get("converted"):
                    metrics["variants"][variant]["converted"] += 1
        
        # Calculate rates
        for variant in ["A", "B"]:
            v = metrics["variants"][variant]
            if v["sent"] > 0:
                v["open_rate"] = v["opened"] / v["sent"]
                v["click_rate"] = v["clicked"] / v["sent"]
                v["conversion_rate"] = v["converted"] / v["sent"]
        
        return metrics
    
    # =========================================================================
    # Dashboard Integration
    # =========================================================================
    
    def get_pending_notifications(self, tenant_id: str) -> List[Dict[str, Any]]:
        """
        Get pending in-app notifications for a tenant.
        
        Called by the dashboard to render notifications.
        """
        notifications = self._inapp_service.get_pending_notifications(
            tenant_id,
            session_limit=self.config.max_in_app_per_session
        )
        return [n.to_dict() for n in notifications]
    
    def dismiss_notification(self, notification_id: str, tenant_id: str) -> bool:
        """Dismiss a notification."""
        self._inapp_service.record_dismissal(notification_id, tenant_id)
        return True
    
    # =========================================================================
    # Data Providers (Default Implementations)
    # =========================================================================
    
    def _default_customer_provider(self, tenant_id: str) -> Dict[str, Any]:
        """Default customer data provider (override for real implementation)."""
        return {
            "tenant_id": tenant_id,
            "name": "Valued Customer",
            "company_name": "Your Organization",
            "email": None,  # Must be provided by real implementation
            "role": "Data Analyst",
        }
    
    def _default_usage_provider(self, tenant_id: str) -> Dict[str, Any]:
        """Default usage data provider (override for real implementation)."""
        return {
            "tenant_id": tenant_id,
            "total_api_calls": 0,
            "total_inferences": 0,
            "model_count": 0,
            "data_sources": 0,
        }
    
    # =========================================================================
    # Callback Registration
    # =========================================================================
    
    def on_email_sent(self, callback: Callable[[str, str, Dict], None]) -> None:
        """Register callback for email sent events."""
        self._on_email_sent.append(callback)
    
    def on_inapp_queued(self, callback: Callable[[InAppNotificationPayload], None]) -> None:
        """Register callback for in-app notification queued events."""
        self._on_inapp_queued.append(callback)
    
    # =========================================================================
    # Status
    # =========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status."""
        return {
            "enabled_channels": [c.value for c in self.config.enabled_channels],
            "email_provider": self.config.email_config.provider.value,
            "ab_testing_enabled": self.config.ab_testing_enabled,
            "events_processed": self._events_processed,
            "emails_sent": self._emails_sent,
            "inapp_queued": self._inapp_queued,
            "conversion_tracking_count": len(self._conversion_tracking),
        }


# =============================================================================
# Factory Functions
# =============================================================================

def create_upsell_integration(
    email_provider: EmailProvider = EmailProvider.MOCK,
    email_api_key: str = "",
    from_email: str = "upgrades@krlabs.dev",
    customer_data_provider: Optional[Callable[[str], Dict[str, Any]]] = None,
    usage_data_provider: Optional[Callable[[str], Dict[str, Any]]] = None,
) -> UpsellMessageIntegration:
    """
    Factory function to create a configured UpsellMessageIntegration.
    
    Example:
    ```python
    integration = create_upsell_integration(
        email_provider=EmailProvider.SENDGRID,
        email_api_key=os.environ["SENDGRID_API_KEY"],
        customer_data_provider=my_customer_lookup,
        usage_data_provider=my_usage_lookup,
    )
    
    # Wire to billing
    billing_bridge.on_upsell(integration.handle_upsell_event)
    ```
    """
    config = IntegrationConfig(
        email_config=EmailConfig(
            provider=email_provider,
            api_key=email_api_key,
            from_email=from_email,
        )
    )
    
    return UpsellMessageIntegration(
        config=config,
        customer_data_provider=customer_data_provider,
        usage_data_provider=usage_data_provider,
    )


def wire_integration_to_billing(
    integration: UpsellMessageIntegration,
    billing_bridge: Any,  # BillingBridge instance
) -> None:
    """
    Wire the upsell integration to the BillingBridge.
    
    This connects:
    - UpsellEngine triggers → StoryBrand message personalization → Email/In-App delivery
    """
    # Get the billing controller from the bridge
    controller = billing_bridge._billing
    
    # Register our handler with the upsell engine
    if hasattr(controller, 'upsell_engine'):
        controller.upsell_engine.on_upsell_triggered(
            lambda event: integration.handle_upsell_event(event)
        )
        logger.info("Wired UpsellMessageIntegration to UpsellEngine")
    
    # Also listen for revenue events to track conversions
    if hasattr(controller, 'on_revenue_event'):
        def track_revenue_conversion(event: Dict[str, Any]):
            if event.get("type") == "purchase" and "tracking_id" in event:
                integration.track_conversion(
                    event["tracking_id"],
                    {"amount": event.get("amount"), "tier": event.get("tier")}
                )
        
        controller.on_revenue_event(track_revenue_conversion)
        logger.info("Wired conversion tracking to revenue events")


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Config
    "DeliveryChannel",
    "EmailProvider",
    "EmailConfig",
    "IntegrationConfig",
    
    # Services
    "EmailDeliveryService",
    "EmailDeliveryResult",
    "InAppDeliveryService",
    "InAppNotificationPayload",
    
    # Main integration
    "UpsellMessageIntegration",
    
    # Utilities
    "get_template_key_for_event",
    "TRIGGER_TO_TEMPLATE_MAP",
    
    # Factory
    "create_upsell_integration",
    "wire_integration_to_billing",
]
