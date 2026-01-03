"""
Celery Worker Integration for KRL Billing - DEPRECATED

⚠️ DEPRECATION WARNING (Dec 2025):
This module has been moved to krl-premium-backend.
Import from: app.services.billing.celery_tasks

This stub remains for backward compatibility but will be removed in v2.0.
"""

import warnings
warnings.warn(
    "krl_data_connectors.core.billing.celery_tasks is deprecated. "
    "This module has moved to krl-premium-backend. "
    "Import from 'app.services.billing.celery_tasks' instead.",
    DeprecationWarning,
    stacklevel=2
)

from celery import Celery, Task
from celery.utils.log import get_task_logger
from datetime import datetime, timedelta, UTC
from decimal import Decimal
from functools import wraps
from typing import Any, Callable, Optional, TypeVar
import hashlib
import json
import os
import time

# Try to import Redis for caching
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None  # type: ignore

logger = get_task_logger(__name__)

# Type variable for generic task functions
T = TypeVar("T")


# =============================================================================
# Celery Configuration
# =============================================================================

def get_celery_app(
    broker_url: Optional[str] = None,
    backend_url: Optional[str] = None,
    app_name: str = "krl_billing",
) -> Celery:
    """
    Create configured Celery application.
    
    Args:
        broker_url: Message broker URL (default: env CELERY_BROKER_URL or redis://localhost:6379/0)
        backend_url: Result backend URL (default: env CELERY_RESULT_BACKEND or redis://localhost:6379/1)
        app_name: Application name
        
    Returns:
        Configured Celery app
    """
    broker = broker_url or os.environ.get(
        "CELERY_BROKER_URL", "redis://localhost:6379/0"
    )
    backend = backend_url or os.environ.get(
        "CELERY_RESULT_BACKEND", "redis://localhost:6379/1"
    )
    
    app = Celery(
        app_name,
        broker=broker,
        backend=backend,
    )
    
    # Configure Celery
    app.conf.update(
        # Task settings
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        
        # Task execution
        task_acks_late=True,  # Acknowledge after task completes
        task_reject_on_worker_lost=True,  # Retry if worker dies
        task_time_limit=300,  # 5 minute hard limit
        task_soft_time_limit=240,  # 4 minute soft limit (raises SoftTimeLimitExceeded)
        
        # Result backend
        result_expires=3600,  # Results expire after 1 hour
        result_backend_transport_options={
            "retry_policy": {
                "timeout": 5.0,
            }
        },
        
        # Retry settings
        task_default_retry_delay=60,  # 1 minute default retry delay
        task_max_retries=3,
        
        # Routing
        task_routes={
            "krl_billing.tasks.calculate_roi_async": {"queue": "roi"},
            "krl_billing.tasks.calculate_health_score_async": {"queue": "health"},
            "krl_billing.tasks.predict_churn_async": {"queue": "ml"},
            "krl_billing.tasks.aggregate_usage_async": {"queue": "usage"},
            "krl_billing.tasks.process_renewals_batch": {"queue": "renewals"},
        },
        
        # Worker settings
        worker_prefetch_multiplier=1,  # Fetch one task at a time for fairness
        worker_concurrency=4,  # Default 4 workers
    )
    
    return app


# Default app instance (can be overridden)
celery_app = get_celery_app()


# =============================================================================
# Redis Cache Integration
# =============================================================================

class ResultCache:
    """
    Redis-based cache for task results.
    
    Caches expensive computation results to avoid re-computation.
    """
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        default_ttl: int = 3600,  # 1 hour default
    ):
        """
        Initialize cache.
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default TTL in seconds
        """
        self._redis: Optional[redis.Redis] = None
        self._default_ttl = default_ttl
        
        if REDIS_AVAILABLE:
            url = redis_url or os.environ.get(
                "REDIS_CACHE_URL", "redis://localhost:6379/2"
            )
            try:
                self._redis = redis.from_url(url, decode_responses=True)
                # Test connection
                self._redis.ping()
            except Exception as e:
                logger.warning(f"Redis cache unavailable: {e}")
                self._redis = None
    
    @property
    def is_available(self) -> bool:
        """Check if cache is available."""
        return self._redis is not None
    
    def _make_key(self, prefix: str, *args: Any, **kwargs: Any) -> str:
        """Generate cache key from arguments."""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()[:16]
        return f"krl:billing:{prefix}:{key_hash}"
    
    def get(self, prefix: str, *args: Any, **kwargs: Any) -> Optional[dict]:
        """Get cached result."""
        if not self._redis:
            return None
        
        try:
            key = self._make_key(prefix, *args, **kwargs)
            data = self._redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        return None
    
    def set(
        self,
        prefix: str,
        result: dict,
        *args: Any,
        ttl: Optional[int] = None,
        **kwargs: Any,
    ) -> bool:
        """Set cached result."""
        if not self._redis:
            return False
        
        try:
            key = self._make_key(prefix, *args, **kwargs)
            self._redis.setex(
                key,
                ttl or self._default_ttl,
                json.dumps(result, default=str),
            )
            return True
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
        return False
    
    def invalidate(self, prefix: str, *args: Any, **kwargs: Any) -> bool:
        """Invalidate cached result."""
        if not self._redis:
            return False
        
        try:
            key = self._make_key(prefix, *args, **kwargs)
            self._redis.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache invalidate failed: {e}")
        return False
    
    def invalidate_prefix(self, prefix: str) -> int:
        """Invalidate all keys with prefix."""
        if not self._redis:
            return 0
        
        try:
            pattern = f"krl:billing:{prefix}:*"
            keys = self._redis.keys(pattern)
            if keys:
                return self._redis.delete(*keys)
        except Exception as e:
            logger.warning(f"Cache invalidate_prefix failed: {e}")
        return 0


# Global cache instance
_cache: Optional[ResultCache] = None


def get_cache() -> ResultCache:
    """Get or create global cache instance."""
    global _cache
    if _cache is None:
        _cache = ResultCache()
    return _cache


# =============================================================================
# Task Decorators
# =============================================================================

def cached_task(
    cache_prefix: str,
    ttl: int = 3600,
    skip_cache_on_error: bool = True,
):
    """
    Decorator to add caching to Celery tasks.
    
    Args:
        cache_prefix: Prefix for cache keys
        ttl: Cache TTL in seconds
        skip_cache_on_error: Skip caching if task fails
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            cache = get_cache()
            
            # Try cache first
            cached = cache.get(cache_prefix, *args, **kwargs)
            if cached is not None:
                logger.info(f"Cache hit for {cache_prefix}")
                return cached  # type: ignore
            
            # Execute task
            try:
                result = func(*args, **kwargs)
                
                # Cache result
                if isinstance(result, dict):
                    cache.set(cache_prefix, result, *args, ttl=ttl, **kwargs)
                
                return result
            except Exception as e:
                if not skip_cache_on_error:
                    raise
                logger.error(f"Task {cache_prefix} failed: {e}")
                raise
        
        return wrapper
    return decorator


class RetryableTask(Task):
    """
    Base task class with exponential backoff retry logic.
    """
    
    # Retry configuration
    autoretry_for = (Exception,)
    retry_backoff = True
    retry_backoff_max = 600  # Max 10 minutes between retries
    retry_jitter = True
    max_retries = 3
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Log task failures."""
        logger.error(
            f"Task {self.name}[{task_id}] failed after {self.request.retries} retries: {exc}"
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)
    
    def on_success(self, retval, task_id, args, kwargs):
        """Log task success."""
        logger.info(f"Task {self.name}[{task_id}] succeeded")
        super().on_success(retval, task_id, args, kwargs)


# =============================================================================
# Billing Tasks
# =============================================================================

@celery_app.task(
    bind=True,
    base=RetryableTask,
    name="krl_billing.tasks.calculate_roi_async",
)
@cached_task("roi", ttl=1800)  # Cache for 30 minutes
def calculate_roi_async(
    self,
    customer_id: str,
    segment: str,
    usage_data: dict,
    pricing_config: Optional[dict] = None,
) -> dict:
    """
    Calculate customer ROI asynchronously.
    
    Args:
        customer_id: Customer identifier
        segment: Customer segment
        usage_data: Usage metrics for ROI calculation
        pricing_config: Optional pricing configuration overrides
        
    Returns:
        ROI calculation results
    """
    from .value_pricing import ValueBasedPricingEngine, CustomerSegment
    
    start_time = time.time()
    logger.info(f"Starting ROI calculation for customer {customer_id}")
    
    try:
        # Initialize engine with config
        engine = ValueBasedPricingEngine()
        if pricing_config:
            # Apply custom config if provided
            pass  # Engine configuration would go here
        
        # Parse segment
        try:
            customer_segment = CustomerSegment[segment.upper()]
        except KeyError:
            customer_segment = CustomerSegment.SMB
        
        # Calculate ROI
        roi_result = engine.calculate_roi(
            customer_id=customer_id,
            segment=customer_segment,
            usage_metrics=usage_data,
        )
        
        duration = time.time() - start_time
        logger.info(f"ROI calculation for {customer_id} completed in {duration:.2f}s")
        
        return {
            "customer_id": customer_id,
            "segment": segment,
            "roi_metrics": roi_result,
            "calculated_at": datetime.now(UTC).isoformat(),
            "duration_seconds": duration,
        }
    
    except Exception as e:
        logger.error(f"ROI calculation failed for {customer_id}: {e}")
        raise


@celery_app.task(
    bind=True,
    base=RetryableTask,
    name="krl_billing.tasks.calculate_health_score_async",
)
@cached_task("health", ttl=900)  # Cache for 15 minutes
def calculate_health_score_async(
    self,
    customer_id: str,
    usage_metrics: dict,
    engagement_metrics: dict,
    support_metrics: dict,
    financial_metrics: dict,
) -> dict:
    """
    Calculate customer health score asynchronously.
    
    Args:
        customer_id: Customer identifier
        usage_metrics: Usage data
        engagement_metrics: Engagement data
        support_metrics: Support ticket data
        financial_metrics: Payment and billing data
        
    Returns:
        Health score and component breakdown
    """
    from .health_scoring import HealthScoringEngine, UsageMetrics
    
    start_time = time.time()
    logger.info(f"Starting health score calculation for customer {customer_id}")
    
    try:
        engine = HealthScoringEngine()
        
        # Build usage metrics object
        metrics = UsageMetrics(
            api_calls_daily_avg=usage_metrics.get("api_calls_daily_avg", 0),
            api_calls_trend=usage_metrics.get("api_calls_trend", 0),
            feature_adoption_rate=usage_metrics.get("feature_adoption_rate", 0),
            unique_features_used=usage_metrics.get("unique_features_used", 0),
            dau_mau_ratio=engagement_metrics.get("dau_mau_ratio", 0),
            sessions_per_week=engagement_metrics.get("sessions_per_week", 0),
            avg_session_duration_min=engagement_metrics.get("avg_session_duration", 0),
            days_since_last_login=engagement_metrics.get("days_since_last_login", 30),
            nps_score=engagement_metrics.get("nps_score"),
            support_tickets_last_30d=support_metrics.get("tickets_last_30d", 0),
            critical_tickets_open=support_metrics.get("critical_open", 0),
            avg_resolution_time_hours=support_metrics.get("avg_resolution_hours", 24),
            payment_on_time_rate=financial_metrics.get("payment_on_time_rate", 1.0),
            invoices_overdue=financial_metrics.get("invoices_overdue", 0),
            contract_utilization=financial_metrics.get("contract_utilization", 0),
        )
        
        # Calculate health score
        health_score = engine.calculate_health_score(customer_id, metrics)
        
        duration = time.time() - start_time
        logger.info(f"Health score for {customer_id}: {health_score.overall_score:.1f} (took {duration:.2f}s)")
        
        return {
            "customer_id": customer_id,
            "overall_score": float(health_score.overall_score),
            "health_category": health_score.category.name,
            "component_scores": {
                "usage": float(health_score.usage_score),
                "engagement": float(health_score.engagement_score),
                "support": float(health_score.support_score),
                "financial": float(health_score.financial_score),
            },
            "risk_factors": health_score.risk_factors,
            "recommendations": health_score.recommendations,
            "calculated_at": datetime.now(UTC).isoformat(),
            "duration_seconds": duration,
        }
    
    except Exception as e:
        logger.error(f"Health score calculation failed for {customer_id}: {e}")
        raise


@celery_app.task(
    bind=True,
    base=RetryableTask,
    name="krl_billing.tasks.predict_churn_async",
)
@cached_task("churn", ttl=3600)  # Cache for 1 hour
def predict_churn_async(
    self,
    customer_id: str,
    health_score: float,
    historical_data: dict,
) -> dict:
    """
    Predict customer churn probability asynchronously.
    
    Args:
        customer_id: Customer identifier
        health_score: Current health score
        historical_data: Historical customer data
        
    Returns:
        Churn prediction with risk factors
    """
    from .health_scoring import ChurnPredictionModel, ChurnRisk
    
    start_time = time.time()
    logger.info(f"Starting churn prediction for customer {customer_id}")
    
    try:
        model = ChurnPredictionModel()
        
        # Predict churn
        prediction = model.predict_churn(
            customer_id=customer_id,
            health_score=health_score,
            contract_months_remaining=historical_data.get("contract_months_remaining", 12),
            usage_trend=historical_data.get("usage_trend", 0),
            engagement_trend=historical_data.get("engagement_trend", 0),
            support_sentiment=historical_data.get("support_sentiment", 0.5),
            competitor_mentions=historical_data.get("competitor_mentions", 0),
        )
        
        duration = time.time() - start_time
        logger.info(
            f"Churn prediction for {customer_id}: {prediction.churn_probability:.1%} "
            f"({prediction.risk_level.name}) (took {duration:.2f}s)"
        )
        
        return {
            "customer_id": customer_id,
            "churn_probability": float(prediction.churn_probability),
            "risk_level": prediction.risk_level.name,
            "days_until_likely_churn": prediction.days_until_likely_churn,
            "risk_factors": prediction.risk_factors,
            "recommended_interventions": [
                {
                    "type": i.intervention_type.name,
                    "priority": i.priority,
                    "description": i.description,
                    "expected_impact": float(i.expected_impact),
                }
                for i in prediction.recommended_interventions
            ],
            "confidence": float(prediction.confidence),
            "predicted_at": datetime.now(UTC).isoformat(),
            "duration_seconds": duration,
        }
    
    except Exception as e:
        logger.error(f"Churn prediction failed for {customer_id}: {e}")
        raise


@celery_app.task(
    bind=True,
    base=RetryableTask,
    name="krl_billing.tasks.aggregate_usage_async",
)
def aggregate_usage_async(
    self,
    tenant_id: str,
    start_date: str,
    end_date: str,
    metric_types: list[str],
) -> dict:
    """
    Aggregate usage metrics for billing period.
    
    Args:
        tenant_id: Tenant identifier
        start_date: Period start (ISO format)
        end_date: Period end (ISO format)
        metric_types: List of metrics to aggregate
        
    Returns:
        Aggregated usage data
    """
    start_time = time.time()
    logger.info(f"Starting usage aggregation for tenant {tenant_id}")
    
    try:
        # This would typically query a time-series database
        # For now, return a placeholder structure
        
        aggregated = {
            "tenant_id": tenant_id,
            "period": {
                "start": start_date,
                "end": end_date,
            },
            "metrics": {},
            "aggregated_at": datetime.now(UTC).isoformat(),
        }
        
        for metric in metric_types:
            # Placeholder - real implementation would query actual data
            aggregated["metrics"][metric] = {
                "total": 0,
                "average": 0,
                "peak": 0,
                "p95": 0,
            }
        
        duration = time.time() - start_time
        logger.info(f"Usage aggregation for {tenant_id} completed in {duration:.2f}s")
        
        aggregated["duration_seconds"] = duration
        return aggregated
    
    except Exception as e:
        logger.error(f"Usage aggregation failed for {tenant_id}: {e}")
        raise


@celery_app.task(
    bind=True,
    base=RetryableTask,
    name="krl_billing.tasks.process_renewals_batch",
)
def process_renewals_batch(
    self,
    contract_ids: list[str],
    renewal_date: str,
) -> dict:
    """
    Process batch of contract renewals.
    
    Args:
        contract_ids: List of contract IDs to process
        renewal_date: Target renewal date
        
    Returns:
        Batch processing results
    """
    from .contracts import ContractManager
    
    start_time = time.time()
    logger.info(f"Starting renewal batch for {len(contract_ids)} contracts")
    
    results = {
        "processed": 0,
        "succeeded": 0,
        "failed": 0,
        "errors": [],
        "renewal_offers": [],
    }
    
    manager = ContractManager()
    
    for contract_id in contract_ids:
        results["processed"] += 1
        try:
            # Generate renewal offer
            offer = manager.generate_renewal_offer(
                contract_id=contract_id,
                target_date=datetime.fromisoformat(renewal_date),
            )
            results["succeeded"] += 1
            results["renewal_offers"].append({
                "contract_id": contract_id,
                "offer_id": offer.offer_id,
                "proposed_price": str(offer.proposed_price),
                "discount": str(offer.proposed_discount),
            })
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({
                "contract_id": contract_id,
                "error": str(e),
            })
            logger.warning(f"Renewal failed for {contract_id}: {e}")
    
    duration = time.time() - start_time
    logger.info(
        f"Renewal batch completed: {results['succeeded']}/{results['processed']} "
        f"succeeded in {duration:.2f}s"
    )
    
    results["duration_seconds"] = duration
    results["completed_at"] = datetime.now(UTC).isoformat()
    return results


# =============================================================================
# Batch Operations
# =============================================================================

@celery_app.task(name="krl_billing.tasks.daily_health_scores")
def daily_health_scores() -> dict:
    """
    Daily job to recalculate all customer health scores.
    
    Should be scheduled via Celery Beat.
    """
    from .health_scoring import HealthScoringEngine
    
    start_time = time.time()
    logger.info("Starting daily health score recalculation")
    
    # In production, this would iterate over all active customers
    # For now, return a summary structure
    
    return {
        "job": "daily_health_scores",
        "started_at": datetime.now(UTC).isoformat(),
        "customers_processed": 0,
        "average_score": 0,
        "risk_distribution": {
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0,
        },
        "duration_seconds": time.time() - start_time,
    }


@celery_app.task(name="krl_billing.tasks.weekly_churn_report")
def weekly_churn_report() -> dict:
    """
    Weekly churn risk report generation.
    
    Should be scheduled via Celery Beat.
    """
    start_time = time.time()
    logger.info("Starting weekly churn report generation")
    
    return {
        "job": "weekly_churn_report",
        "started_at": datetime.now(UTC).isoformat(),
        "high_risk_customers": [],
        "interventions_scheduled": 0,
        "duration_seconds": time.time() - start_time,
    }


# =============================================================================
# Task Orchestration
# =============================================================================

def calculate_customer_intelligence(customer_id: str, data: dict) -> str:
    """
    Orchestrate full customer intelligence calculation.
    
    Chains ROI → Health Score → Churn Prediction tasks.
    
    Args:
        customer_id: Customer identifier
        data: All required customer data
        
    Returns:
        Celery chain task ID
    """
    from celery import chain
    
    # Build task chain
    workflow = chain(
        calculate_roi_async.s(
            customer_id,
            data.get("segment", "SMB"),
            data.get("usage_data", {}),
        ),
        calculate_health_score_async.s(
            customer_id,
            data.get("usage_metrics", {}),
            data.get("engagement_metrics", {}),
            data.get("support_metrics", {}),
            data.get("financial_metrics", {}),
        ),
        predict_churn_async.s(
            customer_id,
            data.get("health_score", 50.0),
            data.get("historical_data", {}),
        ),
    )
    
    # Execute chain
    result = workflow.apply_async()
    return result.id


def invalidate_customer_cache(customer_id: str) -> None:
    """
    Invalidate all cached results for a customer.
    
    Call when customer data changes significantly.
    """
    cache = get_cache()
    cache.invalidate("roi", customer_id)
    cache.invalidate("health", customer_id)
    cache.invalidate("churn", customer_id)
    logger.info(f"Invalidated cache for customer {customer_id}")


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Celery app
    "celery_app",
    "get_celery_app",
    # Cache
    "ResultCache",
    "get_cache",
    # Task classes
    "RetryableTask",
    "cached_task",
    # Tasks
    "calculate_roi_async",
    "calculate_health_score_async",
    "predict_churn_async",
    "aggregate_usage_async",
    "process_renewals_batch",
    # Batch jobs
    "daily_health_scores",
    "weekly_churn_report",
    # Orchestration
    "calculate_customer_intelligence",
    "invalidate_customer_cache",
]
