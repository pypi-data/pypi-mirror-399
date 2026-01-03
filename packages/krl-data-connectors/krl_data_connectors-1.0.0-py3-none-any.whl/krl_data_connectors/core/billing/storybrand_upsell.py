# =============================================================================
# STORYBRAND UPSELL MESSAGE TEMPLATES
# =============================================================================
# Based on Donald Miller's Building a StoryBrand framework
# Integrated with Cialdini's persuasion principles and Schwartz's awareness stages
#
# Customer = Hero facing external villain
# KRL = Guide offering clear plan leading to success or avoiding failure
#
# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.storybrand_upsell
# This stub remains for backward compatibility but will be removed in v2.0.
# =============================================================================
import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.storybrand_upsell is deprecated. "
    "Import from 'app.services.billing.storybrand_upsell' instead.",
    DeprecationWarning,
    stacklevel=2
)

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import re


class UpsellTrigger(Enum):
    """Behavioral triggers that initiate upsell messaging."""
    COMMUNITY_USAGE_THRESHOLD = "community_usage_threshold"
    COMMUNITY_FEATURE_GATE_FEDERATED = "community_feature_gate_federated"
    COMMUNITY_TIER_VIOLATION_PATTERN = "community_tier_violation_pattern"
    PRO_RISK_INCREASE = "pro_risk_increase"
    PRO_VALUE_REALIZATION = "pro_value_realization"
    PRO_BEHAVIORAL_ENTERPRISE_PATTERN = "pro_behavioral_enterprise_pattern"


@dataclass
class StoryBrandMessage:
    """Structured StoryBrand message with all narrative components."""
    trigger_condition: str
    hero: str
    villain: str
    guide_positioning: str
    subject_line: str
    message_body: str
    cta_primary: str
    cta_url: str
    cta_secondary: Optional[str] = None
    success_vision: Optional[str] = None
    failure_stakes: Optional[str] = None
    social_proof: Optional[str] = None
    authority_signal: Optional[str] = None
    objection_handlers: Optional[Dict[str, str]] = None


# =============================================================================
# COMMUNITY → PRO UPSELL MESSAGES
# =============================================================================

UPSELL_MESSAGES_STORYBRAND: Dict[str, Dict[str, Any]] = {
    
    # =========================================================================
    # COMMUNITY → PRO UPGRADES
    # =========================================================================
    
    "community_usage_threshold": {
        "trigger_condition": "API calls > 8000 (80% of 10K limit)",
        "hero": "Policy analyst managing multiple concurrent projects",
        "villain": "Artificial capacity limits disrupting critical work",
        "guide_positioning": "KRL Pro",
        
        "subject_line": "Your analysis just hit a wall. Here's the fix.",
        
        "message_body": """
You're in the middle of building evidence for {current_project_name}. Your team depends on you to deliver insights that shape million-dollar decisions.

But you just burned through 8,000 of your 10,000 monthly API calls. In 3-5 days, your analysis stops cold. Reports stall. Stakeholders wait. Deadlines slip.

Here's what happens next without Pro:

→ You ration remaining capacity across projects (spreading thin never works)
→ You manually export/import data to work around limits (hello, 2am spreadsheet hell)  
→ You explain to leadership why "the tool stopped working" (credibility hit)

**847 policy analysts faced this exact moment.** They upgraded to Pro.

Here's what changed:

✓ 100,000 API calls monthly (10x capacity — one less thing to manage)
✓ Federated learning unlocked (train models across your agency's data without centralizing)
✓ Advanced threat detection (catch data quality issues before they become report errors)

**The choice:**
Keep fighting artificial limits, or get back to the work that matters.

→ Upgrade to Pro now — your next 100K calls start immediately.

P.S. Pro customers report saving 12-18 hours monthly previously spent "managing capacity." That's half a work week back for actual analysis.
        """,
        
        "cta_primary": "Upgrade to Pro — Remove Limits",
        "cta_url": "https://krlabs.dev/upgrade?tier=pro&trigger=capacity",
        "cta_secondary": "See what Pro unlocks",
        
        "success_vision": "Uninterrupted analysis. Projects delivered on time. Leadership trusts your infrastructure.",
        "failure_stakes": "Stalled reports. Missed deadlines. Manual workarounds eating your weekends.",
        
        "objection_handlers": {
            "too_expensive": "Pro costs $99/mo. Your time is worth $40-80/hr. If Pro saves you 3 hours monthly, it pays for itself. Most users save 12+.",
            "not_sure_ill_use_it": "You've already used 80% of Community tier in {days_in_period} days. At your current pace, you'll hit Pro limits in 8-10 months. Growth is good — Pro grows with you.",
            "can_i_try_it": "Start Pro today. If you use <20K calls in month 1, we'll refund the difference. Zero risk."
        },
        
        "social_proof": "847 policy analysts upgraded at this exact moment. 94% stay on Pro after 6 months.",
        "authority_signal": "Used by HUD, 12 state agencies, 40+ municipal governments.",
    },
    
    "community_feature_gate_federated": {
        "trigger_condition": "Attempted federated learning (blocked feature)",
        "hero": "Data scientist building multi-jurisdictional models",
        "villain": "Data silos preventing collaborative analysis",
        "guide_positioning": "KRL Pro unlocks federated learning",
        
        "subject_line": "You just tried to break down data silos. Let's finish that.",
        
        "message_body": """
You clicked "Train Federated Model." That's not a casual click.

You're trying to build insights across datasets you don't control — state agencies that won't share raw data, partner organizations with compliance restrictions, jurisdictions with different privacy rules.

**This is the hard problem.** Centralized analysis won't work. Manual coordination takes months. Traditional tools force you to choose: rigor or collaboration. Never both.

Here's what you're up against without federated learning:

→ You build separate models per jurisdiction (inconsistent methods, impossible comparisons)
→ You negotiate data-sharing agreements (6-12 month legal review cycles)
→ You compromise on sample size (analysis on 10% of available data because you can't access the rest)

**KRL Pro solves this differently.**

Federated learning lets you train models collaboratively without moving data:

✓ Each jurisdiction keeps data on their infrastructure (compliance maintained)
✓ Models learn from combined patterns (full statistical power)
✓ You get unified insights in days, not months (legal delays eliminated)

**Real example:** State housing authority used Pro to analyze eviction patterns across 40 counties without centralizing tenant records. 6-week project instead of 18-month data-sharing negotiation.

**The decision:**
Keep building isolated models on partial data, or unlock collaborative rigor today.

→ Upgrade to Pro — Federated learning activates immediately.

P.S. Pro includes 4 federated rounds monthly. Most multi-jurisdictional projects use 2-3. You'll have capacity to spare.
        """,
        
        "cta_primary": "Unlock Federated Learning — Upgrade to Pro",
        "cta_url": "https://krlabs.dev/upgrade?tier=pro&trigger=federated",
        
        "success_vision": "Multi-jurisdictional insights without data-sharing delays. Compliance maintained. Statistical power maximized.",
        "failure_stakes": "Fragmented analysis. Months lost to legal negotiations. Models trained on 10% of available data.",
        
        "social_proof": "284 Pro users run federated models monthly. Average time savings: 4.7 months per project.",
    },
    
    "community_tier_violation_pattern": {
        "trigger_condition": "3 tier violations in 24 hours",
        "hero": "Analyst under deadline crushing pressure",
        "villain": "Artificial constraints during critical reporting window",
        "guide_positioning": "KRL Pro as the pressure relief valve",
        
        "subject_line": "You've hit the wall 3 times today. This is the solution.",
        
        "message_body": """
You've hit your Community tier limits 3 times in the last 24 hours.

That's not random. You're either:
→ Facing an urgent deadline (board meeting, legislative session, grant application)
→ Onboarding new team members (suddenly 4 people using your account)
→ Expanding scope mid-project (client asked for "just one more analysis")

**Here's what happens in the next 48 hours if you don't upgrade:**

Hour 6: You hit limit #4. Start rationing API calls across team members.
Hour 12: Junior analyst's work blocked. They ping you. You manually prioritize.
Hour 18: You're copying data to spreadsheets to work around limits (accuracy risk).
Hour 24: Your manager asks "why is this taking so long?" You blame "the tool."
Hour 36: You're working at 11pm because daytime capacity went to firefighting.

**412 analysts were exactly where you are right now.** They upgraded to Pro. Here's what changed:

✓ Limits disappear (100K calls = ~60 days of buffer at your current burn rate)
✓ Team friction disappears (everyone works without rationing)
✓ Weekend work disappears (infrastructure stops being the bottleneck)

**The math:**
Community: 10K calls, you're burning ~{burn_rate}/day = stress in 2.5 days
Pro: 100K calls, same burn rate = stress-free for 25 days

→ Upgrade to Pro now — limits lift in <2 minutes.

P.S. Pro customers who upgraded during crunch periods report 73% less "tool-related stress." One analyst: "I stopped checking my usage dashboard 40 times a day."
        """,
        
        "cta_primary": "End the Limit Nightmare — Upgrade to Pro",
        "cta_url": "https://krlabs.dev/upgrade?tier=pro&trigger=violations",
        
        "success_vision": "Team operates smoothly. Deadlines met without heroics. You sleep normal hours.",
        "failure_stakes": "Nightly firefighting. Rationing work across team. Manager questions your tool choice.",
    },
    
    # =========================================================================
    # PRO → ENTERPRISE UPGRADES
    # =========================================================================
    
    "pro_risk_increase": {
        "trigger_condition": "Risk multiplier > 1.3x",
        "hero": "Infrastructure lead responsible for platform security",
        "villain": "Emerging threats exposing agency to data breaches",
        "guide_positioning": "KRL Enterprise as security partner",
        
        "subject_line": "Your security risk just spiked. We detected it. Here's why.",
        
        "message_body": """
Our defense systems flagged your account 47 minutes ago: **risk multiplier increased to {risk_multiplier}x baseline.**

Translation: Your KRL environment is now {risk_percentage}% more vulnerable than optimal configuration. This isn't theoretical — we're seeing signals consistent with:

→ Outdated authentication protocols (lateral movement risk)
→ Anomalous API access patterns (potential credential compromise)
→ Unpatched integration points (data exfiltration vulnerability)

**Why this matters:**
You're running policy analysis on sensitive data. Housing records. Employment data. Health outcomes. A breach doesn't just cost money — it costs careers, program credibility, and constituent trust.

**What happens if you stay on Pro with elevated risk:**

Week 1: Vulnerability persists. We monitor, but can't auto-remediate (Pro tier restriction).
Week 4: Attack surface expands as you integrate more data sources.
Week 8: Incident occurs. You're in incident response mode (legal, PR, technical cleanup).
Week 12: You're testifying about "what controls were in place." Pro's manual response looks negligent in hindsight.

**73 Pro customers faced elevated risk profiles.** Those who upgraded to Enterprise avoided incidents. Those who didn't... didn't.

**Enterprise changes the equation:**

✓ **Adaptive defense:** Auto-rollback on anomalous activity (threats stopped before damage)
✓ **Priority threat response:** Security team monitoring (not just automated alerts)
✓ **Audit-ready compliance:** SOC 2 documentation + incident reports (board/counsel requirement)
✓ **Zero-trust architecture:** Every request authenticated, every action logged

**Real incident (anonymized):**
Pro customer: Risk spike detected → manual intervention required → 6-hour response → minor data exposure → 40 hours cleanup
Enterprise customer (same threat profile): Risk spike detected → auto-rollback in 4 minutes → zero exposure → 20-minute post-incident review

**The stakes:**
Continue manually managing security, or let Enterprise defend your infrastructure 24/7.

→ Upgrade to Enterprise — Adaptive defense activates within 2 hours.

P.S. If you're preparing for audits (IG review, legislative oversight, compliance check), Enterprise's documentation has saved customers 60-120 hours of "proving what controls existed."
        """,
        
        "cta_primary": "Activate Enterprise Security — Upgrade Now",
        "cta_url": "https://krlabs.dev/upgrade?tier=enterprise&trigger=risk",
        
        "success_vision": "Threats stopped automatically. Audits pass cleanly. Leadership trusts your security posture.",
        "failure_stakes": "Manual firefighting during incidents. Audit failures. Constituent data at risk.",
        
        "authority_signal": "SOC 2 Type II certified. Trusted by federal agencies managing HIPAA, FedRAMP, and state privacy law compliance.",
        "social_proof": "Enterprise customers experience 94% fewer security incidents than Pro users with comparable risk profiles.",
    },
    
    "pro_value_realization": {
        "trigger_condition": "Estimated value saved > $10,000",
        "hero": "Program director maximizing ROI on analytics investment",
        "villain": "Leaving money on the table by not scaling proven value",
        "guide_positioning": "KRL Enterprise as force multiplier",
        
        "subject_line": "Your platform just saved you ${value_saved:,}. Time to scale that.",
        
        "message_body": """
Our value tracking system just calculated what KRL Pro delivered to your team in the last 90 days:

**${value_saved:,} in prevented costs.**

Here's the breakdown:
→ ${time_savings:,}: Analyst time saved ({hours_saved} hours automated @ ${hourly_rate}/hr loaded cost)
→ ${consultant_savings:,}: Avoided consultant fees (data integration work you didn't outsource)
→ ${error_savings:,}: Error prevention ({errors_caught} data quality issues caught pre-publication)

**You're getting {roi_multiple}x ROI on your Pro subscription.** That's exceptional.

**But here's the problem:** You're capacity-constrained.

Pro tier is delivering massive value on ~40% utilization. Your team is:
→ Manually prioritizing which analyses to run (because you're managing capacity)
→ Queuing projects instead of running them parallel (because you're rationing compute)
→ Saying "we can't do that" to stakeholders (because you're hitting soft limits)

**Your current state:** ${value_saved:,} value captured. ~${value_left_on_table:,}+ value left on table because infrastructure constrains you.

**What Enterprise unlocks:**

✓ **Unlimited capacity:** No more prioritization overhead (run everything, let impact sort itself)
✓ **Custom models:** Proprietary equity/causal methods (5-10x better fit for your specific programs)
✓ **Multi-tenant architecture:** Separate environments per department (scale across agency without chaos)
✓ **White-glove support:** Direct line to our methods team (not just bug fixes — optimize your analytical approach)

**Expected outcome:** Same team, 2.5-3x analysis throughput. Value captured scales proportionally: ${value_saved:,} → ${projected_value:,} quarterly.

**Real example (state education agency):**
Pro tier: $11K quarterly value, team of 6, running 18 analyses/quarter
Enterprise upgrade: $38K quarterly value, same team, running 52 analyses/quarter
ROI improvement: 3.45x (value scaling faster than team growth)

**The decision:**
Stay at 40% capacity utilization, or remove the ceiling.

→ Upgrade to Enterprise — Value scaling starts immediately.

P.S. Enterprise pricing is outcome-based. We'll build custom ROI dashboard showing value delivered weekly. If you're not seeing 2x+ impact in 90 days, we adjust pricing. You win either way.
        """,
        
        "cta_primary": "Scale Your ROI — Upgrade to Enterprise",
        "cta_url": "https://krlabs.dev/upgrade?tier=enterprise&trigger=value",
        
        "success_vision": "Infrastructure invisible. Team running at full capacity. Value delivered compounds quarterly.",
        "failure_stakes": "Value left on table. Team frustrated by constraints. Stakeholders hear 'no' too often.",
        
        "social_proof": "Enterprise customers report 2.1-3.8x value scaling post-upgrade. Median time to positive ROI: 47 days.",
    },
    
    "pro_behavioral_enterprise_pattern": {
        "trigger_condition": "Usage patterns match enterprise profile",
        "hero": "Operations lead managing growing analytics practice",
        "villain": "Tool friction slowing institutional momentum",
        "guide_positioning": "KRL Enterprise as the natural next step",
        
        "subject_line": "You're using Pro like an enterprise. Let's make it official.",
        
        "message_body": """
Our usage analytics flagged your account for an unusual reason: **You're behaving like our Enterprise customers, but you're still on Pro tier.**

Specifically, we're seeing:
→ Multi-tenant patterns ({project_count}+ distinct projects with separate data domains)
→ High-volume collaborative work ({concurrent_users} concurrent users)
→ Custom workflow requirements (integrations we typically see at Enterprise scale)

**Translation:** You've outgrown Pro. Your team is fighting the tool instead of using it.

**What this looks like day-to-day:**

Morning standup: "Who's running the housing analysis? Okay, Sarah holds off on education work until that's done." (Manual coordination tax)

Mid-afternoon: Junior analyst pings you: "I need access to the transportation data connector, but it's locked behind someone else's project." (Permission friction)

End of week: You're manually merging results from {project_count} separate Pro workspaces because you can't run integrated analysis. (Architecture debt)

**14 organizations were exactly here.** They upgraded to Enterprise not because Pro stopped working — but because they needed infrastructure that scales with ambition, not against it.

**What changes:**

✓ **Unlimited seats:** Entire team operates simultaneously (coordination tax disappears)
✓ **Multi-tenant isolation:** Each program/department gets clean workspace (no cross-contamination)
✓ **Custom model deployment:** Build once, deploy everywhere (stop rebuilding wheels)
✓ **Priority support:** Direct Slack channel with our team (5-minute response SLA, not 24-hour tickets)

**The pattern we see:**
Year 1: Pro works great (1-2 analysts, focused use case)
Year 2: Team grows, Pro feels cramped (workarounds emerge)
Year 3: Either upgrade to Enterprise, or team fragments across multiple Pro accounts (coordination nightmare)

You're at the Year 2 → Year 3 inflection point.

**The choice:**
Fight tool friction while your team scales, or get infrastructure that scales with you.

→ Let's talk Enterprise — 15-minute consultation, no pressure.

P.S. Enterprise migrations take 2-4 hours. We handle it. Your team experiences zero downtime. You flip the switch Friday afternoon, by Monday morning everyone's working in the new environment.
        """,
        
        "cta_primary": "Schedule Enterprise Consultation",
        "cta_url": "https://krlabs.dev/contact?type=enterprise&trigger=behavioral",
        "cta_secondary": "See Enterprise pricing",
        
        "success_vision": "Team operates independently. Infrastructure invisible. Growth doesn't create friction.",
        "failure_stakes": "Endless coordination meetings. Permission bottlenecks. Team morale erodes as tool fights them.",
        
        "social_proof": "Organizations that upgraded at your usage profile report 67% reduction in 'tool friction' complaints from staff.",
    },
}


# =============================================================================
# MESSAGE PERSONALIZATION ENGINE
# =============================================================================

def calculate_days_until_limit(usage_data: Dict[str, Any]) -> int:
    """Calculate days until user hits tier limit at current burn rate."""
    api_calls_used = usage_data.get('api_calls_used', 0)
    days_in_period = usage_data.get('days_in_period', 1)
    tier_limit = usage_data.get('tier_limit', 10000)
    
    if days_in_period == 0:
        return 0
    
    daily_burn_rate = api_calls_used / days_in_period
    remaining_calls = tier_limit - api_calls_used
    
    if daily_burn_rate == 0:
        return 999  # Effectively unlimited
    
    return int(remaining_calls / daily_burn_rate)


def calculate_value_saved(usage_data: Dict[str, Any]) -> float:
    """Calculate estimated value saved based on usage patterns."""
    # Time savings
    hours_automated = usage_data.get('hours_automated', 0)
    hourly_rate = usage_data.get('hourly_rate', 55)
    time_savings = hours_automated * hourly_rate
    
    # Error prevention
    errors_caught = usage_data.get('errors_caught', 0)
    error_cost = 500  # Average cost per data quality error
    error_savings = errors_caught * error_cost
    
    # Consultant avoidance
    consultant_savings = usage_data.get('consultant_savings', 0)
    
    return time_savings + error_savings + consultant_savings


def personalize_upsell_message(
    template_key: str,
    customer_data: Dict[str, Any],
    usage_data: Dict[str, Any],
) -> Dict[str, str]:
    """
    Inject customer-specific data into StoryBrand templates.
    
    Args:
        template_key: Key from UPSELL_MESSAGES_STORYBRAND
        customer_data: {customer_id, name, organization, segment, current_tier}
        usage_data: {api_calls_used, days_in_period, project_names, team_size, 
                    hours_automated, errors_caught, hourly_rate}
    
    Returns:
        Personalized message dict with filled template variables
    """
    if template_key not in UPSELL_MESSAGES_STORYBRAND:
        raise ValueError(f"Unknown template key: {template_key}")
    
    template = UPSELL_MESSAGES_STORYBRAND[template_key]
    
    # Calculate personalization metrics
    days_to_limit = calculate_days_until_limit(usage_data)
    value_saved = calculate_value_saved(usage_data)
    
    days_in_period = usage_data.get('days_in_period', 1)
    api_calls_used = usage_data.get('api_calls_used', 0)
    burn_rate = api_calls_used / days_in_period if days_in_period > 0 else 0
    
    # Build personalization context
    context = {
        'current_project_name': usage_data.get('project_names', ['your current project'])[0],
        'days_in_period': str(usage_data.get('days_in_period', 'recent')),
        'customer_name': customer_data.get('name', 'there'),
        'organization': customer_data.get('organization', 'your organization'),
        'value_saved': f"${value_saved:,.0f}",
        'team_size': str(usage_data.get('team_size', 'your team')),
        'burn_rate': f"{burn_rate:.0f}",
        'days_to_limit': str(days_to_limit),
        'hours_saved': str(usage_data.get('hours_automated', 0)),
        'hourly_rate': str(usage_data.get('hourly_rate', 55)),
        'errors_caught': str(usage_data.get('errors_caught', 0)),
        'time_savings': f"${usage_data.get('hours_automated', 0) * usage_data.get('hourly_rate', 55):,.0f}",
        'consultant_savings': f"${usage_data.get('consultant_savings', 0):,.0f}",
        'error_savings': f"${usage_data.get('errors_caught', 0) * 500:,.0f}",
        'roi_multiple': f"{(value_saved / 99) if value_saved > 0 else 0:.1f}",
        'value_left_on_table': f"${value_saved * 1.5:,.0f}",
        'projected_value': f"${value_saved * 2.5:,.0f}",
        'risk_multiplier': str(usage_data.get('risk_multiplier', 1.0)),
        'risk_percentage': str(int((usage_data.get('risk_multiplier', 1.0) - 1) * 100)),
        'project_count': str(usage_data.get('project_count', 4)),
        'concurrent_users': str(usage_data.get('concurrent_users', 6)),
    }
    
    # Replace variables in message body
    personalized_message = template['message_body']
    for var, value in context.items():
        personalized_message = personalized_message.replace('{' + var + '}', value)
        personalized_message = personalized_message.replace('{' + var + ':,}', value)
    
    # Personalize subject line
    personalized_subject = template['subject_line']
    for var, value in context.items():
        personalized_subject = personalized_subject.replace('{' + var + '}', value)
        personalized_subject = personalized_subject.replace('{' + var + ':,}', value)
    
    return {
        'template_key': template_key,
        'subject_line': personalized_subject,
        'message_body': personalized_message.strip(),
        'cta_primary': template['cta_primary'],
        'cta_url': template['cta_url'],
        'cta_secondary': template.get('cta_secondary'),
        'success_vision': template.get('success_vision'),
        'failure_stakes': template.get('failure_stakes'),
        'social_proof': template.get('social_proof'),
        'authority_signal': template.get('authority_signal'),
        'objection_handlers': template.get('objection_handlers'),
        'hero': template['hero'],
        'villain': template['villain'],
    }


def get_upsell_message_for_trigger(
    trigger: UpsellTrigger,
    customer_data: Dict[str, Any],
    usage_data: Dict[str, Any],
) -> Dict[str, str]:
    """
    Get personalized upsell message for a specific behavioral trigger.
    
    Args:
        trigger: UpsellTrigger enum value
        customer_data: Customer profile data
        usage_data: Usage metrics data
    
    Returns:
        Personalized message dict ready for delivery
    """
    return personalize_upsell_message(trigger.value, customer_data, usage_data)


# =============================================================================
# A/B TESTING SUPPORT
# =============================================================================

@dataclass
class MessageVariant:
    """A/B test variant for upsell messaging."""
    variant_id: str
    template_key: str
    modifications: Dict[str, str]  # Field -> modified value


MESSAGE_AB_TESTS = {
    "villain_specificity_test": {
        "test_name": "Villain Specificity (Week 1-2)",
        "description": "Generic villain vs. specific villain",
        "template_key": "community_usage_threshold",
        "variants": {
            "A": {"subject_line": "Your analysis capacity is running low"},
            "B": {"subject_line": "Your analysis just hit a wall. Here's the fix."},
        },
        "success_metric": "click_through_rate",
        "expected_lift": "25-40%",
        "sample_size": 500,
    },
    "success_vision_test": {
        "test_name": "Success Vision Detail (Week 3-4)",
        "description": "Abstract success vs. concrete success",
        "template_key": "community_tier_violation_pattern",
        "variants": {
            "A": {"success_vision": "Better analysis workflow"},
            "B": {"success_vision": "Hit deadlines without weekend work"},
        },
        "success_metric": "conversion_rate",
        "expected_lift": "15-30%",
        "sample_size": 500,
    },
    "social_proof_placement_test": {
        "test_name": "Social Proof Placement (Week 5-6)",
        "description": "Social proof in body vs. subject line",
        "template_key": "pro_value_realization",
        "variants": {
            "A": {"subject_line": "Your platform delivered exceptional ROI. Time to scale."},
            "B": {"subject_line": "Join 847 analysts who scaled from here"},
        },
        "success_metric": "open_rate",
        "expected_lift": "10-20%",
        "sample_size": 500,
    },
}

# Alias for backward compatibility with imports expecting AB_TEST_FRAMEWORK
AB_TEST_FRAMEWORK = MESSAGE_AB_TESTS


def get_ab_test_variant(
    test_name: str,
    customer_id: str,
) -> str:
    """
    Deterministically assign customer to A/B test variant.
    
    Uses customer_id hash for consistent assignment.
    """
    import hashlib
    
    hash_input = f"{test_name}:{customer_id}".encode()
    hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)
    
    return "A" if hash_value % 2 == 0 else "B"


def get_personalized_message_with_ab_test(
    template_key: str,
    customer_data: Dict[str, Any],
    usage_data: Dict[str, Any],
    active_tests: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Get personalized message with A/B test modifications applied.
    
    Args:
        template_key: Base template key
        customer_data: Customer profile (must include customer_id)
        usage_data: Usage metrics
        active_tests: List of active A/B test names to apply
    
    Returns:
        Personalized message with test variant metadata
    """
    message = personalize_upsell_message(template_key, customer_data, usage_data)
    
    applied_tests = []
    
    if active_tests:
        for test_name in active_tests:
            if test_name in MESSAGE_AB_TESTS:
                test = MESSAGE_AB_TESTS[test_name]
                if test['template_key'] == template_key:
                    variant = get_ab_test_variant(test_name, customer_data['customer_id'])
                    modifications = test['variants'].get(variant, {})
                    
                    for field, value in modifications.items():
                        if field in message:
                            message[field] = value
                    
                    applied_tests.append({
                        'test_name': test_name,
                        'variant': variant,
                    })
    
    message['ab_tests_applied'] = applied_tests
    return message
