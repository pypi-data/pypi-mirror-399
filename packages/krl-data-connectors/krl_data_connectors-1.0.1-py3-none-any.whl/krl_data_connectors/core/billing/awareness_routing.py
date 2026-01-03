# =============================================================================
# AWARENESS STAGE DETECTION & ROUTING ENGINE
# =============================================================================
# Based on Eugene Schwartz's 5 Awareness Stages (Breakthrough Advertising)
# Implements intelligent routing to stage-appropriate landing experiences
#
# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.awareness_routing
# This stub remains for backward compatibility but will be removed in v2.0.
# =============================================================================
import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.awareness_routing is deprecated. "
    "Import from 'app.services.billing.awareness_routing' instead.",
    DeprecationWarning,
    stacklevel=2
)

from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import re
import hashlib
from datetime import datetime, UTC


class AwarenessStage(Enum):
    """
    Schwartz's 5 awareness stages.
    
    UNAWARE: Doesn't know problem exists
    PROBLEM_AWARE: Knows problem, not solutions
    SOLUTION_AWARE: Knows solution category exists
    PRODUCT_AWARE: Evaluating specific products
    MOST_AWARE: Ready to buy, needs final nudge
    """
    UNAWARE = "unaware"
    PROBLEM_AWARE = "problem_aware"
    SOLUTION_AWARE = "solution_aware"
    PRODUCT_AWARE = "product_aware"
    MOST_AWARE = "most_aware"


@dataclass
class AwarenessSignal:
    """Signal indicating awareness stage."""
    stage: AwarenessStage
    confidence: float  # 0.0-1.0
    signal_type: str   # "utm_source", "search_query", "referrer", "behavior"
    signal_value: str
    detected_at: Optional[datetime] = None


@dataclass
class AwarenessRoute:
    """Configuration for awareness-stage-specific landing page."""
    stage: AwarenessStage
    url_path: str
    headline: str
    subheadline: str
    cta_primary: str
    cta_primary_url: str
    cta_secondary: Optional[str] = None
    cta_secondary_url: Optional[str] = None
    content_focus: str = ""
    social_proof_type: str = ""
    meta_title: str = ""
    meta_description: str = ""


# =============================================================================
# AWARENESS DETECTION ENGINE
# =============================================================================

class AwarenessDetector:
    """
    Detects visitor awareness stage from multiple signals.
    Routes to appropriate landing page experience.
    """
    
    # =========================================================================
    # DETECTION RULES: SEARCH QUERIES
    # =========================================================================
    
    SEARCH_QUERY_PATTERNS = {
        AwarenessStage.UNAWARE: [
            r"policy analysis best practices",
            r"government program evaluation",
            r"evidence[- ]?based polic(y|ies|ymaking)",
            r"how to measure policy impact",
            r"public sector analytics",
            r"data[- ]?driven (government|policy)",
            r"program evaluation methods",
        ],
        AwarenessStage.PROBLEM_AWARE: [
            r"policy analysis takes too long",
            r"slow evidence building",
            r"data fragmentation government",
            r"manual policy research problems",
            r"8[- ]?week analysis timeline",
            r"government data integration challenges",
            r"policy analysis bottleneck",
            r"evidence delay(s)?",
            r"analyst time wasted",
            r"data silo(s)? (government|public sector)",
        ],
        AwarenessStage.SOLUTION_AWARE: [
            r"automated policy analysis",
            r"policy analysis software",
            r"government analytics platform",
            r"evidence automation tools?",
            r"policy research automation",
            r"policy analysis tools?",
            r"automat(e|ed|ion) (evidence|policy|analysis)",
            r"federal data connectors?",
            r"causal inference software",
            r"equity analysis (tool|platform)",
        ],
        AwarenessStage.PRODUCT_AWARE: [
            r"krl vs\.? h2o",
            r"krl vs\.? datarobot",
            r"khipu research labs? review",
            r"best policy analysis platform",
            r"government analytics tools? comparison",
            r"h2o\.?ai vs\.? (krl|khipu)",
            r"datarobot vs\.? (krl|khipu)",
            r"alteryx vs\.? (krl|khipu)",
            r"policy analysis (comparison|alternatives)",
            r"which policy analytics",
        ],
        AwarenessStage.MOST_AWARE: [
            r"krl (pricing|price|cost)",
            r"khipu research labs? (enterprise|pricing|demo)",
            r"krl (demo|trial|free)",
            r"krl customer support",
            r"krl (sign[- ]?up|register)",
            r"krlabs\.dev",
            r"buy krl",
            r"krl subscription",
            r"khipu (pricing|cost|demo)",
        ],
    }
    
    # =========================================================================
    # DETECTION RULES: UTM CAMPAIGNS
    # =========================================================================
    
    UTM_CAMPAIGN_MAPPING = {
        # Campaign name patterns → awareness stage
        "brand_awareness": AwarenessStage.UNAWARE,
        "awareness": AwarenessStage.UNAWARE,
        "top_funnel": AwarenessStage.UNAWARE,
        "education": AwarenessStage.UNAWARE,
        
        "problem_education": AwarenessStage.PROBLEM_AWARE,
        "problem": AwarenessStage.PROBLEM_AWARE,
        "pain_point": AwarenessStage.PROBLEM_AWARE,
        "challenge": AwarenessStage.PROBLEM_AWARE,
        
        "solution_category": AwarenessStage.SOLUTION_AWARE,
        "solution": AwarenessStage.SOLUTION_AWARE,
        "mid_funnel": AwarenessStage.SOLUTION_AWARE,
        "consideration": AwarenessStage.SOLUTION_AWARE,
        
        "competitive": AwarenessStage.PRODUCT_AWARE,
        "comparison": AwarenessStage.PRODUCT_AWARE,
        "vs_": AwarenessStage.PRODUCT_AWARE,
        "alternative": AwarenessStage.PRODUCT_AWARE,
        
        "bottom_funnel": AwarenessStage.MOST_AWARE,
        "conversion": AwarenessStage.MOST_AWARE,
        "pricing": AwarenessStage.MOST_AWARE,
        "demo": AwarenessStage.MOST_AWARE,
        "trial": AwarenessStage.MOST_AWARE,
        "brand": AwarenessStage.MOST_AWARE,  # Brand searches = high intent
    }
    
    # =========================================================================
    # DETECTION RULES: REFERRER PATTERNS
    # =========================================================================
    
    REFERRER_PATTERNS = {
        AwarenessStage.UNAWARE: [
            r"linkedin\.com/feed",
            r"twitter\.com/home",
            r"x\.com/home",
            r"news\.ycombinator\.com",
            r"reddit\.com/(r/)?datascience",
            r"medium\.com",
            r"substack\.com",
        ],
        AwarenessStage.PROBLEM_AWARE: [
            r"govtech\.com",
            r"federaltimes\.com",
            r"govloop\.com",
            r"governing\.com",
            r"routefifty\.com",
            r"nextgov\.com",
            r"fcw\.com",
        ],
        AwarenessStage.SOLUTION_AWARE: [
            r"g2\.com/categories",
            r"g2crowd\.com",
            r"capterra\.com",
            r"softwareadvice\.com",
            r"gartner\.com",
            r"trustradius\.com",
            r"getapp\.com",
        ],
        AwarenessStage.PRODUCT_AWARE: [
            r"h2o\.ai",
            r"datarobot\.com",
            r"alteryx\.com",
            r"alternativeto\.net",
            r"versus\.com",
            r"stackshare\.io",
        ],
        AwarenessStage.MOST_AWARE: [
            r"krlabs\.dev",
            r"docs\.krlabs\.dev",
            r"khipu\.io",
            r"github\.com/kr-?labs",
            r"pypi\.org.*krl",
        ],
    }
    
    # =========================================================================
    # DETECTION RULES: BEHAVIORAL PATTERNS
    # =========================================================================
    
    BEHAVIORAL_SIGNALS = {
        # Page sequence patterns → (stage, confidence)
        "visited_blog_then_pricing": (AwarenessStage.SOLUTION_AWARE, 0.8),
        "visited_docs_then_pricing": (AwarenessStage.PRODUCT_AWARE, 0.85),
        "direct_to_pricing_page": (AwarenessStage.MOST_AWARE, 0.9),
        "visited_3plus_comparison_pages": (AwarenessStage.PRODUCT_AWARE, 0.85),
        "downloaded_whitepaper": (AwarenessStage.PROBLEM_AWARE, 0.75),
        "watched_demo_video": (AwarenessStage.SOLUTION_AWARE, 0.8),
        "visited_case_study": (AwarenessStage.SOLUTION_AWARE, 0.75),
        "clicked_pricing_from_homepage": (AwarenessStage.MOST_AWARE, 0.85),
        "clicked_demo_request": (AwarenessStage.PRODUCT_AWARE, 0.9),
        "visited_comparison_page": (AwarenessStage.PRODUCT_AWARE, 0.8),
        "multiple_sessions_same_week": (AwarenessStage.SOLUTION_AWARE, 0.7),
        "returning_visitor_direct": (AwarenessStage.MOST_AWARE, 0.75),
    }
    
    # =========================================================================
    # DETECTION METHODS
    # =========================================================================
    
    def detect_from_search_query(self, query: str) -> Optional[AwarenessSignal]:
        """Detect awareness stage from search query."""
        if not query:
            return None
        
        query_lower = query.lower().strip()
        
        for stage, patterns in self.SEARCH_QUERY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    # Higher confidence for more specific stages
                    if stage in [AwarenessStage.PRODUCT_AWARE, AwarenessStage.MOST_AWARE]:
                        confidence = 0.9
                    elif stage == AwarenessStage.SOLUTION_AWARE:
                        confidence = 0.8
                    else:
                        confidence = 0.75
                    
                    return AwarenessSignal(
                        stage=stage,
                        confidence=confidence,
                        signal_type="search_query",
                        signal_value=query,
                        detected_at=datetime.now(),
                    )
        
        return None
    
    def detect_from_utm_params(
        self,
        utm_campaign: Optional[str] = None,
        utm_source: Optional[str] = None,
        utm_content: Optional[str] = None,
    ) -> Optional[AwarenessSignal]:
        """Detect awareness stage from UTM parameters."""
        if not utm_campaign:
            return None
        
        campaign_lower = utm_campaign.lower()
        
        for campaign_key, stage in self.UTM_CAMPAIGN_MAPPING.items():
            if campaign_key in campaign_lower:
                return AwarenessSignal(
                    stage=stage,
                    confidence=0.95,  # High confidence - we control UTM tags
                    signal_type="utm_campaign",
                    signal_value=f"{utm_campaign}|{utm_source or ''}|{utm_content or ''}",
                    detected_at=datetime.now(),
                )
        
        return None
    
    def detect_from_referrer(self, referrer: str) -> Optional[AwarenessSignal]:
        """Detect awareness stage from referrer URL."""
        if not referrer:
            return None
        
        referrer_lower = referrer.lower()
        
        for stage, patterns in self.REFERRER_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, referrer_lower):
                    return AwarenessSignal(
                        stage=stage,
                        confidence=0.7,  # Medium confidence - inferential
                        signal_type="referrer",
                        signal_value=referrer,
                        detected_at=datetime.now(),
                    )
        
        return None
    
    def detect_from_behavior(
        self,
        session_pages: Optional[List[str]] = None,
        actions: Optional[List[str]] = None,
        session_count: int = 1,
        is_returning: bool = False,
    ) -> Optional[AwarenessSignal]:
        """Detect awareness stage from behavioral patterns."""
        if not session_pages and not actions:
            return None
        
        session_pages = session_pages or []
        actions = actions or []
        
        # Normalize page names
        pages_lower = [p.lower() for p in session_pages]
        actions_lower = [a.lower() for a in actions]
        
        # Check page sequence patterns
        has_blog = any('blog' in p for p in pages_lower)
        has_docs = any('doc' in p for p in pages_lower)
        has_pricing = any('pricing' in p or 'price' in p for p in pages_lower)
        has_comparison = any('compare' in p or 'vs' in p for p in pages_lower)
        has_case_study = any('case' in p or 'customer' in p for p in pages_lower)
        
        # Determine behavior pattern
        if len(session_pages) == 1 and has_pricing:
            stage, confidence = self.BEHAVIORAL_SIGNALS["direct_to_pricing_page"]
            return AwarenessSignal(
                stage=stage, confidence=confidence,
                signal_type="behavior", signal_value="direct_pricing",
                detected_at=datetime.now(),
            )
        
        if has_docs and has_pricing:
            stage, confidence = self.BEHAVIORAL_SIGNALS["visited_docs_then_pricing"]
            return AwarenessSignal(
                stage=stage, confidence=confidence,
                signal_type="behavior", signal_value="docs→pricing",
                detected_at=datetime.now(),
            )
        
        if has_blog and has_pricing:
            stage, confidence = self.BEHAVIORAL_SIGNALS["visited_blog_then_pricing"]
            return AwarenessSignal(
                stage=stage, confidence=confidence,
                signal_type="behavior", signal_value="blog→pricing",
                detected_at=datetime.now(),
            )
        
        if has_comparison or sum(1 for p in pages_lower if 'compare' in p or 'vs' in p) >= 3:
            stage, confidence = self.BEHAVIORAL_SIGNALS["visited_3plus_comparison_pages"]
            return AwarenessSignal(
                stage=stage, confidence=confidence,
                signal_type="behavior", signal_value="comparison_research",
                detected_at=datetime.now(),
            )
        
        # Check action patterns
        if 'whitepaper_download' in actions_lower or 'ebook_download' in actions_lower:
            stage, confidence = self.BEHAVIORAL_SIGNALS["downloaded_whitepaper"]
            return AwarenessSignal(
                stage=stage, confidence=confidence,
                signal_type="behavior", signal_value="whitepaper",
                detected_at=datetime.now(),
            )
        
        if 'demo_video_watch' in actions_lower or 'video_complete' in actions_lower:
            stage, confidence = self.BEHAVIORAL_SIGNALS["watched_demo_video"]
            return AwarenessSignal(
                stage=stage, confidence=confidence,
                signal_type="behavior", signal_value="demo_video",
                detected_at=datetime.now(),
            )
        
        if 'demo_request' in actions_lower:
            stage, confidence = self.BEHAVIORAL_SIGNALS["clicked_demo_request"]
            return AwarenessSignal(
                stage=stage, confidence=confidence,
                signal_type="behavior", signal_value="demo_request",
                detected_at=datetime.now(),
            )
        
        # Returning visitor signals
        if is_returning and len(session_pages) <= 2:
            stage, confidence = self.BEHAVIORAL_SIGNALS["returning_visitor_direct"]
            return AwarenessSignal(
                stage=stage, confidence=confidence,
                signal_type="behavior", signal_value="returning_direct",
                detected_at=datetime.now(),
            )
        
        return None
    
    # =========================================================================
    # COMBINED DETECTION
    # =========================================================================
    
    def detect_awareness_stage(
        self,
        search_query: Optional[str] = None,
        utm_campaign: Optional[str] = None,
        utm_source: Optional[str] = None,
        utm_content: Optional[str] = None,
        referrer: Optional[str] = None,
        session_pages: Optional[List[str]] = None,
        actions: Optional[List[str]] = None,
        session_count: int = 1,
        is_returning: bool = False,
    ) -> Tuple[AwarenessStage, float, List[AwarenessSignal]]:
        """
        Detect awareness stage from multiple signals.
        
        Returns: (stage, confidence, signals)
        """
        signals: List[AwarenessSignal] = []
        
        # Collect all available signals
        if search_query:
            signal = self.detect_from_search_query(search_query)
            if signal:
                signals.append(signal)
        
        if utm_campaign:
            signal = self.detect_from_utm_params(utm_campaign, utm_source, utm_content)
            if signal:
                signals.append(signal)
        
        if referrer:
            signal = self.detect_from_referrer(referrer)
            if signal:
                signals.append(signal)
        
        if session_pages or actions:
            signal = self.detect_from_behavior(
                session_pages, actions, session_count, is_returning
            )
            if signal:
                signals.append(signal)
        
        # No signals detected - default to PROBLEM_AWARE (safest middle ground)
        if not signals:
            return (AwarenessStage.PROBLEM_AWARE, 0.5, [])
        
        # Single signal - return it
        if len(signals) == 1:
            return (signals[0].stage, signals[0].confidence, signals)
        
        # Multiple signals - weighted combination
        # Priority: UTM > Behavior > Search > Referrer
        signal_weights = {
            "utm_campaign": 1.0,
            "behavior": 0.9,
            "search_query": 0.8,
            "referrer": 0.6,
        }
        
        # Calculate weighted scores per stage
        stage_scores: Dict[AwarenessStage, float] = {}
        
        for signal in signals:
            weight = signal_weights.get(signal.signal_type, 0.5)
            weighted_confidence = signal.confidence * weight
            
            if signal.stage not in stage_scores:
                stage_scores[signal.stage] = 0
            stage_scores[signal.stage] += weighted_confidence
        
        # Return highest-scoring stage
        best_stage = max(stage_scores.keys(), key=lambda s: stage_scores[s])
        best_confidence = min(stage_scores[best_stage], 1.0)  # Cap at 1.0
        
        return (best_stage, best_confidence, signals)


# =============================================================================
# AWARENESS ROUTING CONFIGURATION
# =============================================================================

AWARENESS_ROUTES: Dict[AwarenessStage, AwarenessRoute] = {
    
    AwarenessStage.UNAWARE: AwarenessRoute(
        stage=AwarenessStage.UNAWARE,
        url_path="/discover/evidence-crisis",
        headline="Federal Agencies Waste 8 Weeks on Every Policy Analysis",
        subheadline="While leadership demands evidence-based decisions in days. The gap is crushing program credibility.",
        cta_primary="See the Hidden Costs",
        cta_primary_url="/discover/evidence-crisis#cost-calculator",
        cta_secondary="Why This Matters Now",
        cta_secondary_url="/discover/evidence-crisis#urgency",
        content_focus="problem_creation",
        social_proof_type="authority_stats",
        meta_title="The Hidden Crisis in Government Evidence-Building | KRL",
        meta_description="Federal agencies waste 8 weeks per policy analysis while leadership demands evidence in days. Discover the systemic problem crushing program credibility.",
    ),
    
    AwarenessStage.PROBLEM_AWARE: AwarenessRoute(
        stage=AwarenessStage.PROBLEM_AWARE,
        url_path="/solutions/automated-evidence",
        headline="Turn 8-Week Analyses Into 8-Minute Workflows",
        subheadline="Automated evidence infrastructure for policy teams who can't afford to wait.",
        cta_primary="See How It Works",
        cta_primary_url="/solutions/automated-evidence#demo",
        cta_secondary="Read Agency Case Study",
        cta_secondary_url="/case-studies/hud",
        content_focus="solution_category_education",
        social_proof_type="outcome_proof",
        meta_title="Automated Evidence Infrastructure for Government | KRL Platform",
        meta_description="Turn 8-week policy analyses into 8-minute workflows. Automated data integration, equity-aware models, and audit-ready documentation.",
    ),
    
    AwarenessStage.SOLUTION_AWARE: AwarenessRoute(
        stage=AwarenessStage.SOLUTION_AWARE,
        url_path="/platform/why-krl",
        headline="Policy Analysis Automation Built for Rigor, Not Just Speed",
        subheadline="79 data connectors, 40 proprietary equity-aware models, SOC 2 certified. Open-source alternatives can't match this.",
        cta_primary="Compare Approaches",
        cta_primary_url="/compare",
        cta_secondary="See Platform Demo",
        cta_secondary_url="/demo",
        content_focus="differentiation",
        social_proof_type="competitive_proof",
        meta_title="Why KRL: Policy Analysis Built for Rigor, Not Just Speed | Khipu Research Labs",
        meta_description="79 data connectors, 40 proprietary equity-aware models, SOC 2 certified. Compare KRL to open-source alternatives and general-purpose ML platforms.",
    ),
    
    AwarenessStage.PRODUCT_AWARE: AwarenessRoute(
        stage=AwarenessStage.PRODUCT_AWARE,
        url_path="/compare",
        headline="KRL vs. H2O.ai vs. DataRobot: The Honest Comparison",
        subheadline="When policy analysis accuracy matters more than general-purpose ML flexibility.",
        cta_primary="See Feature Comparison",
        cta_primary_url="/compare#features",
        cta_secondary="Schedule Technical Review",
        cta_secondary_url="/contact?type=technical-review",
        content_focus="competitive_battlecard",
        social_proof_type="switching_proof",
        meta_title="KRL vs H2O.ai vs DataRobot: Honest Comparison | Khipu Research Labs",
        meta_description="Feature-by-feature comparison: KRL vs general-purpose ML platforms. When policy analysis accuracy matters more than flexibility.",
    ),
    
    AwarenessStage.MOST_AWARE: AwarenessRoute(
        stage=AwarenessStage.MOST_AWARE,
        url_path="/pricing",
        headline="Evidence Infrastructure Starting at $25K Annually",
        subheadline="Enterprise pricing based on value delivered, not seat count. See ROI calculator below.",
        cta_primary="Calculate Your ROI",
        cta_primary_url="/pricing#roi-calculator",
        cta_secondary="Start Free Trial",
        cta_secondary_url="/trial",
        content_focus="pricing_roi_removal",
        social_proof_type="customer_logos",
        meta_title="KRL Platform Pricing: Evidence Infrastructure from $25K Annually",
        meta_description="Value-based pricing for government, academic, nonprofit, and consulting customers. Calculate your ROI in 3 minutes.",
    ),
}

# Alias for backward compatibility
AWARENESS_STAGE_ROUTING = AWARENESS_ROUTES


# =============================================================================
# MODULE-LEVEL HELPER FUNCTIONS
# =============================================================================

# Global router instance for convenience functions
_default_router: Optional['AwarenessRouter'] = None


def _get_default_router() -> 'AwarenessRouter':
    """Get or create the default router instance."""
    global _default_router
    if _default_router is None:
        _default_router = AwarenessRouter()
    return _default_router


def detect_awareness_stage(
    search_query: Optional[str] = None,
    utm_campaign: Optional[str] = None,
    utm_source: Optional[str] = None,
    utm_content: Optional[str] = None,
    referrer: Optional[str] = None,
    session_pages: Optional[List[str]] = None,
    actions: Optional[List[str]] = None,
    session_count: int = 1,
    is_returning: bool = False,
) -> Tuple[AwarenessStage, float, List[AwarenessSignal]]:
    """
    Detect visitor's awareness stage from signals.
    
    Convenience function that uses the default AwarenessDetector.
    
    Returns:
        Tuple of (stage, confidence, signals)
    """
    detector = AwarenessDetector()
    return detector.detect_awareness_stage(
        search_query=search_query,
        utm_campaign=utm_campaign,
        utm_source=utm_source,
        utm_content=utm_content,
        referrer=referrer,
        session_pages=session_pages,
        actions=actions,
        session_count=session_count,
        is_returning=is_returning,
    )


def route_by_awareness(
    search_query: Optional[str] = None,
    utm_campaign: Optional[str] = None,
    utm_source: Optional[str] = None,
    utm_content: Optional[str] = None,
    referrer: Optional[str] = None,
    session_pages: Optional[List[str]] = None,
    actions: Optional[List[str]] = None,
    session_count: int = 1,
    is_returning: bool = False,
) -> Tuple[AwarenessRoute, float, List[AwarenessSignal]]:
    """
    Route visitor to appropriate landing page based on awareness stage.
    
    Convenience function that uses the default AwarenessRouter.
    
    Returns:
        Tuple of (route, confidence, signals)
    """
    router = _get_default_router()
    return router.route_visitor(
        search_query=search_query,
        utm_campaign=utm_campaign,
        utm_source=utm_source,
        utm_content=utm_content,
        referrer=referrer,
        session_pages=session_pages,
        actions=actions,
        session_count=session_count,
        is_returning=is_returning,
    )


# =============================================================================
# AWARENESS ROUTER
# =============================================================================

class AwarenessRouter:
    """
    Routes visitors to awareness-stage-appropriate landing pages.
    """
    
    def __init__(self):
        self.detector = AwarenessDetector()
        self.routes = AWARENESS_ROUTES
    
    def route_visitor(
        self,
        search_query: Optional[str] = None,
        utm_campaign: Optional[str] = None,
        utm_source: Optional[str] = None,
        utm_content: Optional[str] = None,
        referrer: Optional[str] = None,
        session_pages: Optional[List[str]] = None,
        actions: Optional[List[str]] = None,
        session_count: int = 1,
        is_returning: bool = False,
    ) -> Tuple[AwarenessRoute, float, List[AwarenessSignal]]:
        """
        Detect awareness stage and return appropriate route.
        
        Returns: (route, confidence, signals)
        """
        stage, confidence, signals = self.detector.detect_awareness_stage(
            search_query=search_query,
            utm_campaign=utm_campaign,
            utm_source=utm_source,
            utm_content=utm_content,
            referrer=referrer,
            session_pages=session_pages,
            actions=actions,
            session_count=session_count,
            is_returning=is_returning,
        )
        
        route = self.routes[stage]
        return (route, confidence, signals)
    
    def get_route_for_stage(self, stage: AwarenessStage) -> AwarenessRoute:
        """Get route configuration for specific stage."""
        return self.routes[stage]
    
    def should_redirect(
        self,
        current_path: str,
        detected_stage: AwarenessStage,
        confidence_threshold: float = 0.7,
        detected_confidence: float = 0.5,
    ) -> bool:
        """
        Determine if visitor should be redirected to stage-appropriate page.
        
        Args:
            current_path: Current URL path
            detected_stage: Detected awareness stage
            confidence_threshold: Minimum confidence to trigger redirect
            detected_confidence: Confidence of stage detection
        
        Returns:
            True if redirect recommended
        """
        if detected_confidence < confidence_threshold:
            return False
        
        target_route = self.routes[detected_stage]
        
        # Don't redirect if already on target page
        if current_path.startswith(target_route.url_path):
            return False
        
        # Don't redirect from pricing to earlier stages (user is progressing)
        if '/pricing' in current_path and detected_stage != AwarenessStage.MOST_AWARE:
            return False
        
        # Don't redirect from deep content pages
        if any(x in current_path for x in ['/docs/', '/api/', '/dashboard/', '/settings/']):
            return False
        
        return True


# =============================================================================
# ANALYTICS & TRACKING
# =============================================================================

@dataclass
class AwarenessDetectionEvent:
    """Analytics event for awareness detection."""
    visitor_id: str
    session_id: str
    detected_stage: AwarenessStage
    confidence: float
    signals: List[AwarenessSignal]
    routed_to: str
    was_redirected: bool
    timestamp: datetime


class AwarenessAnalytics:
    """
    Track awareness detection and routing for optimization.
    """
    
    def __init__(self):
        self.events: List[AwarenessDetectionEvent] = []
    
    def record_detection(
        self,
        visitor_id: str,
        session_id: str,
        stage: AwarenessStage,
        confidence: float,
        signals: List[AwarenessSignal],
        routed_to: str,
        was_redirected: bool,
    ) -> None:
        """Record awareness detection event."""
        event = AwarenessDetectionEvent(
            visitor_id=visitor_id,
            session_id=session_id,
            detected_stage=stage,
            confidence=confidence,
            signals=signals,
            routed_to=routed_to,
            was_redirected=was_redirected,
            timestamp=datetime.now(),
        )
        self.events.append(event)
    
    def get_stage_distribution(self) -> Dict[AwarenessStage, int]:
        """Get distribution of detected stages."""
        distribution = {stage: 0 for stage in AwarenessStage}
        for event in self.events:
            distribution[event.detected_stage] += 1
        return distribution
    
    def get_signal_effectiveness(self) -> Dict[str, Dict[str, Any]]:
        """Analyze which signals are most effective at detecting stages."""
        signal_stats: Dict[str, Dict[str, Any]] = {}
        
        for event in self.events:
            for signal in event.signals:
                if signal.signal_type not in signal_stats:
                    signal_stats[signal.signal_type] = {
                        'count': 0,
                        'avg_confidence': 0,
                        'stages_detected': {},
                    }
                
                stats = signal_stats[signal.signal_type]
                stats['count'] += 1
                stats['avg_confidence'] = (
                    (stats['avg_confidence'] * (stats['count'] - 1) + signal.confidence)
                    / stats['count']
                )
                
                stage_name = signal.stage.value
                if stage_name not in stats['stages_detected']:
                    stats['stages_detected'][stage_name] = 0
                stats['stages_detected'][stage_name] += 1
        
        return signal_stats
    
    def get_redirect_rate(self) -> float:
        """Get percentage of visitors who were redirected."""
        if not self.events:
            return 0.0
        redirected = sum(1 for e in self.events if e.was_redirected)
        return redirected / len(self.events)


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

"""
# In your web application routing layer (FastAPI example):

from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse

app = FastAPI()
router = AwarenessRouter()
analytics = AwarenessAnalytics()

@app.middleware("http")
async def awareness_routing_middleware(request: Request, call_next):
    # Skip for API routes, static files, etc.
    if request.url.path.startswith(('/api/', '/static/', '/docs/', '/dashboard/')):
        return await call_next(request)
    
    # Extract signals from request
    route, confidence, signals = router.route_visitor(
        search_query=request.query_params.get('q'),
        utm_campaign=request.query_params.get('utm_campaign'),
        utm_source=request.query_params.get('utm_source'),
        utm_content=request.query_params.get('utm_content'),
        referrer=request.headers.get('referer'),
        session_pages=request.session.get('pages_visited', []),
        actions=request.session.get('actions', []),
        session_count=request.session.get('session_count', 1),
        is_returning=request.cookies.get('returning') == 'true',
    )
    
    # Check if redirect needed
    should_redirect = router.should_redirect(
        current_path=request.url.path,
        detected_stage=route.stage,
        confidence_threshold=0.7,
        detected_confidence=confidence,
    )
    
    # Record analytics
    analytics.record_detection(
        visitor_id=request.cookies.get('visitor_id', 'unknown'),
        session_id=request.session.get('session_id', 'unknown'),
        stage=route.stage,
        confidence=confidence,
        signals=signals,
        routed_to=route.url_path if should_redirect else request.url.path,
        was_redirected=should_redirect,
    )
    
    if should_redirect:
        # Preserve query params in redirect
        redirect_url = route.url_path
        if request.url.query:
            redirect_url += f"?{request.url.query}"
        return RedirectResponse(url=redirect_url, status_code=302)
    
    return await call_next(request)

@app.get("/")
async def homepage(request: Request):
    # If not redirected by middleware, render appropriate content
    route, confidence, signals = router.route_visitor(
        referrer=request.headers.get('referer'),
        # ... other signals
    )
    
    return templates.TemplateResponse(
        'landing_page.html',
        {
            'request': request,
            'headline': route.headline,
            'subheadline': route.subheadline,
            'cta_primary': route.cta_primary,
            'cta_primary_url': route.cta_primary_url,
            'cta_secondary': route.cta_secondary,
            'meta_title': route.meta_title,
            'meta_description': route.meta_description,
        }
    )
"""
