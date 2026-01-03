# =============================================================================
# LANDING PAGE CONTENT MATRIX
# =============================================================================
# Complete content specifications for all 5 awareness stage landing pages
# Based on Schwartz's Breakthrough Advertising + Ogilvy proof elements
#
# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.landing_page_content
# This stub remains for backward compatibility but will be removed in v2.0.
# =============================================================================
import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.landing_page_content is deprecated. "
    "Import from 'app.services.billing.landing_page_content' instead.",
    DeprecationWarning,
    stacklevel=2
)

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from .awareness_routing import AwarenessStage


# =============================================================================
# CONTENT STRUCTURE TYPES
# =============================================================================

@dataclass
class HeroSection:
    """Landing page hero section content."""
    headline: str
    subheadline: str
    background_image: Optional[str] = None
    cta_primary: str = ""
    cta_primary_url: str = ""
    cta_primary_action: Optional[str] = None  # e.g., "scroll_to_section"
    cta_secondary: Optional[str] = None
    cta_secondary_url: Optional[str] = None


@dataclass
class StatCallout:
    """Statistical proof point."""
    stat: str
    context: str
    source: Optional[str] = None


@dataclass
class Testimonial:
    """Customer testimonial."""
    quote: str
    source: str
    title: Optional[str] = None
    organization: Optional[str] = None
    outcome: Optional[str] = None


@dataclass
class FeatureComparison:
    """Competitive feature comparison row."""
    capability: str
    krl: str
    competitor_1: str
    competitor_2: str
    competitor_3: Optional[str] = None


@dataclass
class CaseStudy:
    """Customer case study summary."""
    agency: str
    challenge: str
    traditional_approach: str
    krl_approach: str
    outcome: str
    quote: Optional[str] = None
    quote_attribution: Optional[str] = None


@dataclass
class FAQ:
    """Frequently asked question."""
    question: str
    answer: str


# =============================================================================
# LANDING PAGE CONTENT BY AWARENESS STAGE
# =============================================================================

LANDING_PAGE_CONTENT: Dict[AwarenessStage, Dict[str, Any]] = {
    
    # =========================================================================
    # STAGE 1: UNAWARE — Problem Creation
    # =========================================================================
    AwarenessStage.UNAWARE: {
        "url": "/discover/evidence-crisis",
        "stage_objective": "Create problem urgency — make visitor realize they have a problem they didn't know about",
        
        "meta": {
            "title": "The Hidden Crisis in Government Evidence-Building | KRL",
            "description": "Federal agencies waste 8 weeks per policy analysis while leadership demands evidence in days. Discover the systemic problem crushing program credibility.",
            "og_image": "/images/og/evidence-crisis.png",
        },
        
        "hero": HeroSection(
            headline="Federal Agencies Waste 8 Weeks on Every Policy Analysis",
            subheadline="While leadership demands evidence-based decisions in days. The gap is crushing program credibility.",
            background_image="analyst_drowning_in_spreadsheets.jpg",
            cta_primary="See the Hidden Costs →",
            cta_primary_action="scroll_to_cost_calculator",
            cta_secondary="Why This Matters Now",
            cta_secondary_url="#urgency",
        ),
        
        "problem_section": {
            "section_id": "evidence-crisis",
            "section_title": "The Evidence-Building Crisis Nobody Talks About",
            "content": """
Congress passed the Foundations for Evidence-Based Policymaking Act in 2018. Seven years later, most agencies still operate the same way:

→ **8-12 week analysis timelines** (by the time evidence arrives, policy window closed)
→ **Fragmented data across 6-12 systems** (analysts spend 60% of time on integration, not analysis)
→ **Manual quality checks catching errors post-publication** (credibility hits that stick)
→ **Equity assessments done as afterthoughts** (because rigorous methods take too long)

**The result:** Policy decisions made on hunches, not evidence. Programs scaled without proof of impact. Budgets justified with outdated data.

Leadership asks: "What does the evidence show?"
Analysts answer: "We'll have that in 6-8 weeks."
Leadership decides anyway.

**The evidence arrives too late to matter.**
            """,
            
            "stat_callouts": [
                StatCallout(stat="73%", context="of federal agencies cite analysis delays as #1 barrier to evidence-based decisions", source="GAO Report 2024"),
                StatCallout(stat="8 weeks", context="average time from data request to usable analysis", source="OMB Evidence Survey"),
                StatCallout(stat="60%", context="of analyst time spent on data integration, not analysis", source="Federal Analytics Workforce Study"),
            ],
        },
        
        "cost_calculator_section": {
            "section_id": "cost-calculator",
            "section_title": "What This Crisis Costs Your Agency",
            
            "calculator_inputs": [
                {"id": "analyst_count", "label": "Number of policy analysts on staff", "type": "number", "default": 10},
                {"id": "hourly_rate", "label": "Average loaded cost per analyst hour ($)", "type": "number", "default": 55},
                {"id": "analyses_per_quarter", "label": "Number of analyses per quarter", "type": "number", "default": 8},
            ],
            
            "calculator_formula": """
                integration_hours = analyst_count * 15 * analyses_per_quarter  # 15 hrs/analysis on integration
                integration_cost = integration_hours * hourly_rate
                delay_cost = analyses_per_quarter * 5000  # Opportunity cost per delayed analysis
                error_cost = analyses_per_quarter * 0.15 * 8000  # 15% error rate, $8K per error
                equity_cost = analyses_per_quarter * 2000  # Compliance risk
                total = integration_cost + delay_cost + error_cost + equity_cost
            """,
            
            "calculator_output_template": """
**Your agency is losing ${total:,} annually to analysis inefficiency.**

Breakdown:
→ ${integration_cost:,}: Analyst time on manual data integration
→ ${delay_cost:,}: Opportunity cost of slow evidence delivery
→ ${error_cost:,}: Rework from data quality issues
→ ${equity_cost:,}: Compliance risk from inadequate equity assessments

**This isn't a technology problem. It's a systems problem.** Agencies cobble together tools never designed to work together, then wonder why evidence-building takes months.
            """,
            
            "cta": "Discover the Solution Category →",
            "cta_url": "/solutions/automated-evidence",
        },
        
        "urgency_section": {
            "section_id": "urgency",
            "section_title": "Why This Matters Now",
            "content": """
**Foundations Act compliance deadlines approaching.** OMB guidance requires agencies to demonstrate "evaluation capacity" and "data maturity." Slow, manual processes won't pass scrutiny.

**Budget justification standards rising.** Congress increasingly demands evidence of program impact. "We think it works" doesn't clear appropriations committees anymore.

**Equity mandates intensifying.** Executive orders require equity assessments on major policy decisions. Manual methods can't keep pace with regulatory timelines.

**The window is closing.** Agencies that build evidence infrastructure now will lead. Those that don't will justify why they're still using 2015 methods in 2026.
            """,
        },
        
        "next_step_section": {
            "headline": "There's a Better Way to Build Evidence",
            "subheadline": "Agencies are collapsing 8-week timelines into 8 minutes through automated evidence infrastructure.",
            "cta_primary": "See How It Works →",
            "cta_url": "/solutions/automated-evidence",
        },
        
        "footer_social_proof": {
            "type": "authority_stats",
            "items": [
                "SOC 2 Type II Certified",
                "Trusted by Federal Agencies",
                "Built for Foundations Act Compliance",
            ],
        },
    },
    
    # =========================================================================
    # STAGE 2: PROBLEM-AWARE — Solution Category Education
    # =========================================================================
    AwarenessStage.PROBLEM_AWARE: {
        "url": "/solutions/automated-evidence",
        "stage_objective": "Educate on solution category — show that automated evidence infrastructure exists and works",
        
        "meta": {
            "title": "Automated Evidence Infrastructure for Government | KRL Platform",
            "description": "Turn 8-week policy analyses into 8-minute workflows. Automated data integration, equity-aware models, and audit-ready documentation.",
            "og_image": "/images/og/automated-evidence.png",
        },
        
        "hero": HeroSection(
            headline="Turn 8-Week Analyses Into 8-Minute Workflows",
            subheadline="Automated evidence infrastructure for policy teams who can't afford to wait.",
            background_image="analyst_confident_dashboard.jpg",
            cta_primary="See Platform Demo →",
            cta_primary_url="/demo",
            cta_secondary="Read Agency Case Study",
            cta_secondary_url="/case-studies/hud",
        ),
        
        "solution_overview": {
            "section_id": "how-it-works",
            "section_title": "How Automated Evidence Infrastructure Works",
            
            "traditional_approach": {
                "title": "The Traditional Approach (8+ Weeks)",
                "steps": [
                    "Week 1-2: Request data from 6 different systems, wait for access",
                    "Week 3-4: Manually clean, standardize, merge datasets (Excel hell)",
                    "Week 5-6: Run analyses, discover data quality issues, restart",
                    "Week 7-8: Generate reports, manually check for equity implications",
                    "Week 9+: Leadership reviews, asks follow-up questions, timeline extends",
                ],
            },
            
            "automated_approach": {
                "title": "The Automated Approach (8 Minutes)",
                "steps": [
                    "Minute 1: State your policy question in plain language",
                    "Minute 2-4: System automatically pulls from 79 integrated data sources",
                    "Minute 5-6: AI applies appropriate causal inference + equity methods",
                    "Minute 7-8: Audit-ready report generated with documentation",
                ],
            },
            
            "key_insight": "What changed: Infrastructure designed from the ground up for policy analysis rigor, not generic data science workflows.",
        },
        
        "four_pillars_section": {
            "section_id": "pillars",
            "section_title": "The Four Pillars of Automated Evidence",
            
            "pillars": [
                {
                    "title": "Unified Data Integration",
                    "description": "79 pre-built connectors to federal data sources (Census, BLS, HUD, CMS, IRS, etc.). Authentication handled. Updates automated. You query, system retrieves.",
                    "stat": "Eliminates 2-3 weeks of manual data gathering",
                    "icon": "database",
                },
                {
                    "title": "Methodological Automation",
                    "description": "40 proprietary statistical models (causal inference, spatial analysis, equity assessment) applied automatically based on your question. No PhD required.",
                    "stat": "Eliminates 1-2 weeks of model selection + validation",
                    "icon": "chart",
                },
                {
                    "title": "Equity-Aware Analysis",
                    "description": "Every analysis automatically includes disparate impact assessment, disaggregated results by protected classes, and compliance documentation.",
                    "stat": "Eliminates 1-2 weeks of post-hoc equity checks",
                    "icon": "balance",
                },
                {
                    "title": "Audit-Ready Documentation",
                    "description": "Every step logged. Every assumption documented. Every result reproducible. IG reviews pass on first submission.",
                    "stat": "Eliminates 60-120 hours of audit preparation",
                    "icon": "clipboard",
                },
            ],
        },
        
        "case_study_section": {
            "section_id": "case-study",
            "case_study": CaseStudy(
                agency="U.S. Department of Housing and Urban Development",
                challenge="Evaluate rental assistance program impact across 300+ jurisdictions under 4-week congressional deadline.",
                traditional_approach="Would require 12-16 weeks: data requests to 300 PHAs, manual integration, separate analyses per jurisdiction, equity assessment as final step.",
                krl_approach="3.5 weeks: Automated data pull from HUD systems + Census, unified causal analysis, disaggregated equity results, audit-ready documentation.",
                outcome="Delivered evidence to congressional committee with 4 days to spare. Analysis survived IG review without revisions.",
                quote="We went from 'we think this works' to 'here's the evidence' in less time than it used to take to gather the data.",
                quote_attribution="Deputy Assistant Secretary, HUD Office of Policy Development & Research",
            ),
            "cta": "Read Full Case Study →",
            "cta_url": "/case-studies/hud",
        },
        
        "next_step_section": {
            "headline": "See It In Action",
            "subheadline": "15-minute platform demo showing real federal data analyzed in real-time.",
            "cta_primary": "Schedule Demo →",
            "cta_url": "/demo",
            "cta_secondary": "Compare to Other Approaches →",
            "cta_secondary_url": "/platform/why-krl",
        },
        
        "footer_social_proof": {
            "type": "outcome_proof",
            "items": [
                "HUD cut analysis time 94%",
                "12 state agencies deployed in 2025",
                "Trusted for Foundations Act compliance",
            ],
        },
    },
    
    # =========================================================================
    # STAGE 3: SOLUTION-AWARE — Differentiation & Proof
    # =========================================================================
    AwarenessStage.SOLUTION_AWARE: {
        "url": "/platform/why-krl",
        "stage_objective": "Differentiate KRL from alternatives — show why purpose-built beats generic",
        
        "meta": {
            "title": "Why KRL: Policy Analysis Built for Rigor, Not Just Speed | Khipu Research Labs",
            "description": "79 data connectors, 40 proprietary equity-aware models, SOC 2 certified. Compare KRL to open-source alternatives and general-purpose ML platforms.",
            "og_image": "/images/og/why-krl.png",
        },
        
        "hero": HeroSection(
            headline="Policy Analysis Automation Built for Rigor, Not Just Speed",
            subheadline="79 data connectors, 40 proprietary equity-aware models, SOC 2 certified. Open-source alternatives can't match this.",
            cta_primary="See What Makes KRL Different →",
            cta_primary_url="#differentiation",
            cta_secondary="Talk to Our Methods Team",
            cta_secondary_url="/contact?type=methods",
        ),
        
        "market_landscape_section": {
            "section_id": "differentiation",
            "section_title": "Why KRL Exists: The Gap in the Market",
            
            "options": [
                {
                    "name": "Open-Source Tools (Python, R, Jupyter)",
                    "pros": ["Free", "Flexible"],
                    "cons": ["Requires PhD-level expertise", "No built-in equity methods", "Every analysis is a custom build", "No audit trail by default"],
                },
                {
                    "name": "General-Purpose ML Platforms (H2O.ai, DataRobot, Alteryx)",
                    "pros": ["User-friendly interfaces", "Automated ML"],
                    "cons": ["Built for business analytics, not policy rigor", "No causal inference methods", "No equity-aware models", "Compliance features bolted on as afterthought"],
                },
                {
                    "name": "Consulting Firms (Big 4, Boutique Policy Shops)",
                    "pros": ["High-touch expertise", "Custom methods"],
                    "cons": ["$150K-500K per project", "12-16 week timelines", "Methods aren't reusable", "Creates vendor dependence"],
                },
                {
                    "name": "KRL: Purpose-Built for Policy Analysis",
                    "pros": ["Ease of use (no coding required)", "Methodological rigor (causal inference, spatial, equity built-in)", "Speed (8 minutes vs. 8 weeks)", "Cost (subscription, not per-project consulting)", "Audit-ready (compliance by design)"],
                    "cons": [],
                },
            ],
        },
        
        "capability_comparison_section": {
            "section_id": "capabilities",
            "section_title": "Capability-by-Capability Breakdown",
            
            "table_headers": ["Capability", "Open Source", "H2O.ai/DataRobot", "Consulting Firm", "KRL"],
            
            "rows": [
                FeatureComparison("Federal Data Integration", "Manual (2-3 weeks)", "Some connectors", "Custom per project", "79 pre-built connectors"),
                FeatureComparison("Causal Inference Methods", "Build from scratch", "Not available", "Expert-dependent", "Automated (RDD, DID, IV, PSM)"),
                FeatureComparison("Equity-Aware Models", "Build from scratch", "Not available", "Custom development", "40 proprietary models"),
                FeatureComparison("Audit Documentation", "Manual creation", "Basic logging", "Included in deliverable", "Auto-generated, IG-ready"),
                FeatureComparison("Time to First Insight", "2-4 weeks", "1-2 weeks", "8-12 weeks", "8 minutes"),
                FeatureComparison("Annual Cost", "$0 (plus $120K analyst time)", "$50K-150K", "$150K-500K per project", "$25K-200K (all projects)"),
            ],
        },
        
        "proprietary_advantage_section": {
            "section_id": "proprietary",
            "section_title": "The KRL Advantage: Proprietary Policy Methods",
            
            "advantages": [
                {
                    "title": "Equity-Aware Statistical Models",
                    "description": "40 proprietary models that automatically detect and measure disparate impact across protected classes. No competitor offers this — it's our core IP.",
                    "example": "Housing subsidy analysis automatically checks for discrimination patterns across race, income, family structure, disability status. Flags potential violations before program launch.",
                },
                {
                    "title": "Geospatial Policy Analysis",
                    "description": "Spatial spillover detection, geographic targeting optimization, place-based impact estimation. Built for jurisdictional analysis.",
                    "example": "Minimum wage increase in City A — what's the impact on employment in adjacent City B? Spatial methods capture cross-border effects traditional models miss.",
                },
                {
                    "title": "Automated Causal Inference",
                    "description": "System selects appropriate quasi-experimental method (RDD, DID, IV, PSM, Synthetic Control) based on your data structure. Eliminates 'correlation is not causation' problem.",
                    "example": "Did the affordable housing program cause rent decreases, or did it launch in areas where rents were already falling? Causal methods separate program effect from background trends.",
                },
            ],
        },
        
        "proof_section": {
            "section_id": "proof",
            "section_title": "Evidence That KRL Works",
            
            "metrics": [
                StatCallout(stat="94%", context="Average reduction in analysis time (8 weeks → 4 days)", source="Measured across 47 federal/state projects in 2024-2025"),
                StatCallout(stat="100%", context="IG audit pass rate (first submission, no revisions)", source="12 agencies, 28 audits conducted"),
                StatCallout(stat="$4.2M", context="Average annual value delivered to Enterprise customers", source="Time savings + error prevention + compliance value"),
            ],
        },
        
        "next_step_section": {
            "headline": "Ready to Compare Directly?",
            "subheadline": "See KRL analyze real federal data side-by-side with open-source tools and general ML platforms.",
            "cta_primary": "Schedule Technical Comparison Demo →",
            "cta_url": "/demo?type=comparison",
            "cta_secondary": "Read Customer Switching Stories →",
            "cta_secondary_url": "/case-studies/switching",
        },
        
        "footer_social_proof": {
            "type": "competitive_proof",
            "items": [
                "Why agencies choose KRL over H2O.ai",
                "What former Big 4 clients say",
                "Open-source refugees: 'We tried building ourselves. Never again.'",
            ],
        },
    },
    
    # =========================================================================
    # STAGE 4: PRODUCT-AWARE — Competitive Battlecard
    # =========================================================================
    AwarenessStage.PRODUCT_AWARE: {
        "url": "/compare",
        "stage_objective": "Win competitive evaluation — provide ammunition to choose KRL over alternatives",
        
        "meta": {
            "title": "KRL vs H2O.ai vs DataRobot: Honest Comparison | Khipu Research Labs",
            "description": "Feature-by-feature comparison: KRL vs general-purpose ML platforms. When policy analysis accuracy matters more than flexibility.",
            "og_image": "/images/og/compare.png",
        },
        
        "hero": HeroSection(
            headline="KRL vs. H2O.ai vs. DataRobot: The Honest Comparison",
            subheadline="When policy analysis accuracy matters more than general-purpose ML flexibility.",
            cta_primary="See Feature Comparison →",
            cta_primary_url="#features",
            cta_secondary="Talk to Someone Who Switched",
            cta_secondary_url="/contact?type=reference",
        ),
        
        "when_to_choose_section": {
            "section_id": "when-to-choose",
            "section_title": "When to Choose Each Platform",
            
            "options": [
                {
                    "platform": "H2O.ai",
                    "headline": "Choose H2O.ai if...",
                    "scenarios": [
                        "You're building predictive models for business operations (fraud detection, churn prediction)",
                        "You have a strong data science team comfortable coding in Python/R",
                        "Policy rigor is secondary to speed and flexibility",
                        "You don't need built-in equity or causal methods",
                    ],
                },
                {
                    "platform": "DataRobot",
                    "headline": "Choose DataRobot if...",
                    "scenarios": [
                        "You need general-purpose AutoML across diverse use cases",
                        "Your primary users are business analysts, not policy specialists",
                        "Compliance is nice-to-have, not mission-critical",
                        "You're okay with 'good enough' methods vs. policy-grade rigor",
                    ],
                },
                {
                    "platform": "KRL",
                    "headline": "Choose KRL if...",
                    "scenarios": [
                        "You're a government agency, nonprofit, or consulting firm doing policy analysis",
                        "Equity assessments are mandatory, not optional",
                        "Audit readiness is non-negotiable (IG reviews, congressional testimony)",
                        "You need causal inference, not just prediction",
                        "Your reputation depends on getting analysis right, not just fast",
                    ],
                    "highlighted": True,
                },
            ],
        },
        
        "switching_stories_section": {
            "section_id": "switching",
            "section_title": "Why Customers Switch to KRL",
            
            "stories": [
                Testimonial(
                    quote="H2O was great for predicting unemployment claims. But when we needed to evaluate a job training program's causal impact, we had to build everything custom. With KRL, it's built-in.",
                    source="State Labor Department",
                    title="Data Analytics Director",
                    outcome="Switched after 18 months on H2O.ai",
                ),
                Testimonial(
                    quote="DataRobot's AutoML is impressive. But it kept recommending methods that wouldn't pass our methods review board. KRL knows policy analysis standards.",
                    source="Federal Health Agency",
                    title="Chief Evaluation Officer",
                    outcome="Switched after 8 months on DataRobot",
                ),
                Testimonial(
                    quote="We were maintaining 15,000 lines of custom Python for data integration alone. KRL's connectors eliminated 90% of our codebase. We can focus on client questions, not infrastructure.",
                    source="Policy Consulting Firm",
                    title="Managing Director",
                    outcome="Switched after 3 years building/maintaining internal tools",
                ),
            ],
        },
        
        "objection_handling_section": {
            "section_id": "objections",
            "section_title": "Common Objections, Honest Answers",
            
            "objections": [
                FAQ(
                    question="H2O.ai is cheaper. Why pay more for KRL?",
                    answer="H2O.ai is cheaper upfront ($50-150/mo vs. our $99-499/mo). But factor in analyst time: If KRL saves your team 10 hours/month on data integration and methods implementation, that's $400-800/mo in labor cost savings. You're paying less total cost of ownership with KRL.",
                ),
                FAQ(
                    question="Can't we just build this ourselves with open-source tools?",
                    answer="Yes. Budget 18-24 months and $500K-1M in engineering costs (2 FTEs × 2 years at loaded cost). Then ongoing maintenance. Three agencies tried this path — all eventually switched to KRL because maintenance burden exceeded expectations. Building is the easy part. Maintaining across evolving data sources, methods standards, and compliance requirements is where internal tools die.",
                ),
                FAQ(
                    question="What if KRL doesn't have the specific method we need?",
                    answer="Enterprise tier includes custom model development. Our methods team (PhD economists + statisticians) will build the specific approach you need. Typical development: 4-8 weeks. This is still faster and cheaper than maintaining it yourself long-term.",
                ),
            ],
        },
        
        "next_step_section": {
            "headline": "See KRL in Your Environment",
            "subheadline": "Bring your actual data, your actual policy question. We'll run it live alongside H2O.ai or DataRobot if you want direct comparison.",
            "cta_primary": "Schedule Technical Review →",
            "cta_url": "/contact?type=technical-review",
            "cta_secondary": "Download Comparison Guide (PDF)",
            "cta_secondary_url": "/resources/comparison-guide.pdf",
        },
        
        "footer_social_proof": {
            "type": "switching_proof",
            "items": [
                "12 DataRobot customers switched to KRL in 2024-2025",
                "Why policy teams outgrow general ML platforms",
                "ROI comparison: H2O vs KRL (real customer data)",
            ],
        },
    },
    
    # =========================================================================
    # STAGE 5: MOST-AWARE — Pricing & Friction Removal
    # =========================================================================
    AwarenessStage.MOST_AWARE: {
        "url": "/pricing",
        "stage_objective": "Remove friction — get ready-to-buy visitors to convert with minimal obstacles",
        
        "meta": {
            "title": "KRL Platform Pricing: Evidence Infrastructure from $25K Annually",
            "description": "Value-based pricing for government, academic, nonprofit, and consulting customers. Calculate your ROI in 3 minutes.",
            "og_image": "/images/og/pricing.png",
        },
        
        "hero": HeroSection(
            headline="Evidence Infrastructure Starting at $25K Annually",
            subheadline="Enterprise pricing based on value delivered, not seat count. ROI calculator below.",
            cta_primary="Calculate Your ROI →",
            cta_primary_url="#roi-calculator",
            cta_secondary="Start Free Trial",
            cta_secondary_url="/trial",
        ),
        
        "pricing_tiers_section": {
            "section_id": "tiers",
            "section_title": "Choose Your Plan",
            
            "tiers": [
                {
                    "name": "Community",
                    "price": "$0",
                    "price_period": "forever",
                    "description": "For individual analysts exploring evidence-based policy analysis.",
                    "included": [
                        "10K API calls/month",
                        "1K ML inferences/month",
                        "100 threat detections/month",
                        "1GB storage",
                        "Basic anomaly detection",
                        "Community support",
                    ],
                    "limitations": [
                        "No federated learning",
                        "No custom models",
                        "50K API call hard cap",
                    ],
                    "cta": "Get Started Free",
                    "cta_url": "/signup?tier=community",
                    "highlighted": False,
                },
                {
                    "name": "Professional",
                    "price": "$99",
                    "price_period": "/month",
                    "description": "For policy teams running production analyses.",
                    "included": [
                        "100K API calls/month",
                        "10K ML inferences/month",
                        "1K threat detections/month",
                        "10GB storage",
                        "4 federated learning rounds/month",
                        "Advanced models + threat detection",
                        "Email support (24hr response)",
                    ],
                    "limitations": [],
                    "cta": "Start Pro Trial",
                    "cta_url": "/trial?tier=pro",
                    "highlighted": True,
                    "badge": "Most Popular",
                },
                {
                    "name": "Enterprise",
                    "price": "Custom",
                    "price_period": "starting $25K/year",
                    "description": "For agencies requiring unlimited capacity and custom solutions.",
                    "included": [
                        "Unlimited API calls",
                        "Unlimited ML inferences",
                        "Unlimited threat detections",
                        "100GB+ storage",
                        "Unlimited federated learning",
                        "Custom model development",
                        "Multi-tenant architecture",
                        "Priority support (5min response SLA)",
                        "Dedicated account manager",
                        "SOC 2 + FedRAMP documentation",
                    ],
                    "limitations": [],
                    "cta": "Contact Sales",
                    "cta_url": "/contact?type=enterprise",
                    "highlighted": False,
                },
            ],
            
            "note": "All tiers include audit-ready documentation, SOC 2 compliance, and equity-aware analysis.",
        },
        
        "roi_calculator_section": {
            "section_id": "roi-calculator",
            "section_title": "What's KRL Worth to Your Organization?",
            
            "calculator_inputs": [
                {"id": "analyses_per_year", "label": "Number of policy analyses per year", "type": "number", "default": 24},
                {"id": "hourly_rate", "label": "Average analyst loaded cost per hour ($)", "type": "number", "default": 55},
                {"id": "current_hours_per_analysis", "label": "Current time per analysis (hours)", "type": "number", "default": 160},
                {"id": "analyst_count", "label": "Number of analysts on team", "type": "number", "default": 5},
            ],
            
            "calculator_formula": """
                # Time savings
                krl_hours_per_analysis = 8  # Average with KRL
                hours_saved = (current_hours_per_analysis - krl_hours_per_analysis) * analyses_per_year
                time_savings_value = hours_saved * hourly_rate
                
                # Consultant avoidance
                consultant_avoidance = analyses_per_year * 0.2 * 15000  # 20% outsourced, $15K avg
                
                # Error prevention
                error_prevention = analyses_per_year * 0.1 * 8000  # 10% error rate, $8K per error
                
                # Compliance value
                compliance_value = 100 * hourly_rate  # 100 audit prep hours saved
                
                # Equity risk mitigation
                equity_value = analyses_per_year * 0.05 * 50000  # 5% equity issue risk, $50K cost
                
                total_annual_value = time_savings_value + consultant_avoidance + error_prevention + compliance_value + equity_value
                
                # Assume Enterprise tier for most organizations
                krl_annual_cost = 50000  # Mid-range Enterprise
                net_value = total_annual_value - krl_annual_cost
                roi_multiple = total_annual_value / krl_annual_cost
            """,
            
            "calculator_output_template": """
**Annual Value Delivered: ${total_annual_value:,}**

**Cost Savings:**
→ ${time_savings_value:,}: Analyst time freed up ({hours_saved:,} hours @ ${hourly_rate})
→ ${consultant_avoidance:,}: Consulting fees avoided
→ ${error_prevention:,}: Data quality issues caught pre-publication

**Risk Mitigation:**
→ ${compliance_value:,}: Audit preparation time eliminated
→ ${equity_value:,}: Disparate impact violations prevented

**KRL Annual Cost: ${krl_annual_cost:,}**
**Net Value: ${net_value:,}**
**ROI: {roi_multiple:.1f}x**

---

**What this means:**
For every dollar you spend on KRL, you get ${roi_multiple:.1f} dollars back in time savings, risk mitigation, and improved decision quality.
            """,
            
            "cta": "Get Custom Pricing Quote →",
            "cta_url": "/contact?type=pricing",
        },
        
        "faq_section": {
            "section_id": "faq",
            "section_title": "Pricing Questions, Straight Answers",
            
            "faqs": [
                FAQ(
                    question="Why is Enterprise tier priced per organization, not per seat?",
                    answer="Because value scales with analyses run, not users logged in. A 3-person team running 50 analyses annually creates more value than a 20-person team running 10 analyses. We price on value delivered, not arbitrary user counts.",
                ),
                FAQ(
                    question="Can I pay monthly instead of annually?",
                    answer="Pro tier: yes, monthly at $99-499/mo. Enterprise tier: annual contracts only (but 17-30% discount for multi-year prepay). Why? Enterprise onboarding costs us 60-80 hours. We need commitment to justify that investment.",
                ),
                FAQ(
                    question="What if we're a nonprofit or academic institution?",
                    answer="Academic: $25K-40K annually (vs. $100K+ for federal agencies). Nonprofits: Case-by-case, typically 30-50% discount. We want evidence-driven policy everywhere, not just agencies with big budgets.",
                ),
                FAQ(
                    question="Do you offer free trials?",
                    answer="Community tier: free forever. Pro/Enterprise: 30-day trial with full feature access. No credit card required. If you don't see 3x+ ROI in 30 days, we're not the right fit.",
                ),
            ],
        },
        
        "customer_logos_section": {
            "section_id": "customers",
            "section_title": "Trusted By",
            
            "logos": [
                "U.S. Department of Housing and Urban Development",
                "12 State Agencies",
                "40+ Municipal Governments",
                "15 Academic Research Institutions",
                "8 Policy Consulting Firms",
            ],
            
            "certifications": [
                {"name": "SOC 2 Type II Certified", "icon": "shield-check"},
                {"name": "FedRAMP In Process", "icon": "government"},
                {"name": "HIPAA Compliant", "icon": "health"},
            ],
        },
        
        "next_step_section": {
            "headline": "Ready to Start?",
            "subheadline": "Free 30-day trial. Full platform access. No credit card required.",
            "cta_primary": "Start Free Trial →",
            "cta_url": "/trial",
            "cta_secondary": "Schedule Demo First →",
            "cta_secondary_url": "/demo",
        },
        
        "footer_social_proof": {
            "type": "customer_logos",
            "items": [
                "Trusted by federal agencies",
                "SOC 2 certified",
                "94% customer retention rate",
            ],
        },
    },
}


# =============================================================================
# CONTENT RETRIEVAL FUNCTIONS
# =============================================================================

def get_landing_page_content(stage: AwarenessStage) -> Dict[str, Any]:
    """Get complete landing page content for awareness stage."""
    return LANDING_PAGE_CONTENT.get(stage, LANDING_PAGE_CONTENT[AwarenessStage.PROBLEM_AWARE])


# Alias for backward compatibility
def get_landing_page_for_stage(stage: AwarenessStage) -> Dict[str, Any]:
    """Get complete landing page content for awareness stage. Alias for get_landing_page_content."""
    return get_landing_page_content(stage)


def get_hero_content(stage: AwarenessStage) -> HeroSection:
    """Get hero section content for awareness stage."""
    content = get_landing_page_content(stage)
    return content.get('hero')


def get_meta_content(stage: AwarenessStage) -> Dict[str, str]:
    """Get meta tags content for awareness stage."""
    content = get_landing_page_content(stage)
    return content.get('meta', {})


def get_section_content(stage: AwarenessStage, section_id: str) -> Optional[Dict[str, Any]]:
    """Get specific section content from landing page."""
    content = get_landing_page_content(stage)
    
    for key, value in content.items():
        if isinstance(value, dict) and value.get('section_id') == section_id:
            return value
    
    return None


def get_all_testimonials() -> List[Testimonial]:
    """Get all testimonials from all landing pages."""
    testimonials = []
    
    for stage, content in LANDING_PAGE_CONTENT.items():
        if 'switching_stories_section' in content:
            stories = content['switching_stories_section'].get('stories', [])
            testimonials.extend(stories)
        if 'case_study_section' in content:
            cs = content['case_study_section'].get('case_study')
            if cs and cs.quote:
                testimonials.append(Testimonial(
                    quote=cs.quote,
                    source=cs.agency,
                    title=cs.quote_attribution,
                ))
    
    return testimonials


def get_all_stat_callouts() -> List[StatCallout]:
    """Get all statistical proof points from all landing pages."""
    stats = []
    
    for stage, content in LANDING_PAGE_CONTENT.items():
        for key, value in content.items():
            if isinstance(value, dict):
                if 'stat_callouts' in value:
                    stats.extend(value['stat_callouts'])
                if 'metrics' in value:
                    stats.extend(value['metrics'])
    
    return stats
