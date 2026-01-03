"""Initial billing schema for Phase 1 pricing infrastructure.

Revision ID: 001_initial_billing
Revises: 
Create Date: 2025-12-02

Tables created:
- customer_segments: Customer segmentation data for value-based pricing
- contracts: Multi-year contract management
- contract_renewals: Renewal offers and tracking
- prepaid_credits: Credit balance management
- customer_health_scores: Health score history
- churn_predictions: Churn prediction audit trail
- expansion_opportunities: Detected expansion opportunities
- pricing_experiments: A/B test tracking
- pricing_audit_log: Audit trail for pricing changes
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, UTC


# revision identifiers, used by Alembic.
revision = '001_initial_billing'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # =========================================================================
    # Customer Segments Table
    # =========================================================================
    op.create_table(
        'customer_segments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('customer_id', sa.String(255), nullable=False, index=True),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False, index=True),
        
        # Segmentation
        sa.Column('primary_segment', sa.String(50), nullable=False),  # startup, smb, midmarket, enterprise, strategic
        sa.Column('secondary_segments', JSONB, server_default='[]'),
        sa.Column('industry', sa.String(100)),
        sa.Column('company_size_tier', sa.String(50)),  # small, medium, large, enterprise
        
        # Firmographics
        sa.Column('annual_revenue', sa.Numeric(16, 2)),
        sa.Column('employee_count', sa.Integer),
        sa.Column('funding_stage', sa.String(50)),  # seed, series_a, series_b, growth, public
        sa.Column('geo_region', sa.String(50)),
        
        # Usage profile
        sa.Column('monthly_api_calls', sa.BigInteger, server_default='0'),
        sa.Column('monthly_active_users', sa.Integer, server_default='0'),
        sa.Column('features_adopted', sa.Integer, server_default='0'),
        sa.Column('feature_adoption_rate', sa.Numeric(5, 4)),  # 0.0000 to 1.0000
        
        # Value metrics
        sa.Column('estimated_annual_value', sa.Numeric(14, 2)),  # Value delivered to customer
        sa.Column('value_capture_rate', sa.Numeric(5, 4)),  # % of value we capture
        sa.Column('expansion_potential', sa.Numeric(5, 4)),
        sa.Column('churn_risk_score', sa.Numeric(5, 4)),
        
        # Timestamps
        sa.Column('segmented_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        
        # Constraints
        sa.UniqueConstraint('customer_id', 'tenant_id', name='uq_customer_segments_customer_tenant'),
    )
    
    op.create_index('idx_customer_segments_primary', 'customer_segments', ['primary_segment'])
    op.create_index('idx_customer_segments_industry', 'customer_segments', ['industry'])
    op.create_index('idx_customer_segments_expansion', 'customer_segments', ['expansion_potential'])
    
    # =========================================================================
    # Contracts Table
    # =========================================================================
    op.create_table(
        'contracts',
        sa.Column('contract_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('customer_id', sa.String(255), nullable=False, index=True),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('stripe_subscription_id', sa.String(255), index=True),
        
        # Contract type and status
        sa.Column('contract_type', sa.String(50), nullable=False),  # monthly, annual, multi_year_2, multi_year_3, enterprise
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),  # draft, pending, active, expiring, expired, renewed, cancelled
        
        # Term dates
        sa.Column('start_date', sa.Date, nullable=False),
        sa.Column('end_date', sa.Date, nullable=False),
        sa.Column('signed_at', sa.DateTime),
        sa.Column('activated_at', sa.DateTime),
        
        # Pricing (all in cents to avoid floating point issues, with currency)
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('base_price_cents', sa.BigInteger, nullable=False),  # Base monthly price in cents
        sa.Column('effective_price_cents', sa.BigInteger, nullable=False),  # After discounts
        sa.Column('total_contract_value_cents', sa.BigInteger, nullable=False),
        
        # Discounts (stored as basis points: 1000 = 10.00%)
        sa.Column('commitment_discount_bps', sa.Integer, server_default='0'),
        sa.Column('volume_discount_bps', sa.Integer, server_default='0'),
        sa.Column('payment_term_discount_bps', sa.Integer, server_default='0'),
        sa.Column('custom_discount_bps', sa.Integer, server_default='0'),
        sa.Column('total_discount_bps', sa.Integer, server_default='0'),
        
        # Payment terms
        sa.Column('payment_terms', sa.String(50), nullable=False, server_default='monthly'),  # monthly, quarterly, annual, prepaid
        sa.Column('billing_cycle_day', sa.Integer, server_default='1'),
        
        # Commitments
        sa.Column('minimum_commitment_cents', sa.BigInteger, server_default='0'),
        sa.Column('annual_api_volume_commitment', sa.BigInteger, server_default='0'),
        
        # SLA
        sa.Column('sla_uptime_guarantee_bps', sa.Integer, server_default='9990'),  # 99.90% = 9990 bps
        sa.Column('sla_response_time_hours', sa.Integer, server_default='24'),
        sa.Column('dedicated_support', sa.Boolean, server_default='false'),
        sa.Column('custom_integrations', sa.Boolean, server_default='false'),
        sa.Column('priority_queue', sa.Boolean, server_default='false'),
        
        # External references
        sa.Column('docusign_envelope_id', sa.String(255)),
        sa.Column('salesforce_opportunity_id', sa.String(255)),
        
        # Metadata
        sa.Column('custom_terms', JSONB, server_default='{}'),
        sa.Column('notes', sa.Text),
        
        # Audit
        sa.Column('created_by', sa.String(255)),
        sa.Column('approved_by', sa.String(255)),
        sa.Column('approval_date', sa.DateTime),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
    )
    
    op.create_index('idx_contracts_status', 'contracts', ['status'])
    op.create_index('idx_contracts_end_date', 'contracts', ['end_date'])
    op.create_index('idx_contracts_type_status', 'contracts', ['contract_type', 'status'])
    
    # =========================================================================
    # Contract Renewals Table
    # =========================================================================
    op.create_table(
        'contract_renewals',
        sa.Column('renewal_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('contract_id', UUID(as_uuid=True), sa.ForeignKey('contracts.contract_id'), nullable=False),
        sa.Column('customer_id', sa.String(255), nullable=False, index=True),
        
        # Offer details
        sa.Column('proposed_contract_type', sa.String(50), nullable=False),
        sa.Column('proposed_price_cents', sa.BigInteger, nullable=False),
        sa.Column('proposed_discount_bps', sa.Integer, server_default='0'),
        sa.Column('early_renewal_bonus_bps', sa.Integer, server_default='0'),
        sa.Column('loyalty_discount_bps', sa.Integer, server_default='0'),
        
        # Status
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),  # pending, sent, viewed, accepted, rejected, expired
        sa.Column('valid_until', sa.DateTime, nullable=False),
        
        # Tracking
        sa.Column('sent_at', sa.DateTime),
        sa.Column('viewed_at', sa.DateTime),
        sa.Column('accepted_at', sa.DateTime),
        sa.Column('rejected_at', sa.DateTime),
        sa.Column('rejection_reason', sa.Text),
        
        # New contract if accepted
        sa.Column('new_contract_id', UUID(as_uuid=True), sa.ForeignKey('contracts.contract_id')),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
    )
    
    op.create_index('idx_contract_renewals_status', 'contract_renewals', ['status'])
    op.create_index('idx_contract_renewals_valid_until', 'contract_renewals', ['valid_until'])
    
    # =========================================================================
    # Prepaid Credits Table
    # =========================================================================
    op.create_table(
        'prepaid_credits',
        sa.Column('credit_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('customer_id', sa.String(255), nullable=False, index=True),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False, index=True),
        
        # Credit type and amounts
        sa.Column('credit_type', sa.String(50), nullable=False),  # api_calls, ml_inference, storage_gb, compute_hours, support_hours, general
        sa.Column('original_amount', sa.BigInteger, nullable=False),  # In smallest unit (e.g., API calls, bytes)
        sa.Column('remaining_amount', sa.BigInteger, nullable=False),
        sa.Column('unit', sa.String(50), nullable=False, server_default='credits'),
        
        # Purchase info
        sa.Column('purchase_price_cents', sa.BigInteger, nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('price_per_unit_cents', sa.Integer),  # Calculated for reference
        
        # Validity
        sa.Column('purchased_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('is_expired', sa.Boolean, server_default='false'),
        
        # Stripe references
        sa.Column('stripe_invoice_id', sa.String(255)),
        sa.Column('stripe_payment_intent_id', sa.String(255)),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
    )
    
    op.create_index('idx_prepaid_credits_type', 'prepaid_credits', ['credit_type'])
    op.create_index('idx_prepaid_credits_expires', 'prepaid_credits', ['expires_at'])
    op.create_index('idx_prepaid_credits_remaining', 'prepaid_credits', ['remaining_amount'])
    
    # =========================================================================
    # Credit Consumption Ledger (for audit trail)
    # =========================================================================
    op.create_table(
        'credit_consumption_ledger',
        sa.Column('ledger_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('credit_id', UUID(as_uuid=True), sa.ForeignKey('prepaid_credits.credit_id'), nullable=False),
        sa.Column('customer_id', sa.String(255), nullable=False, index=True),
        
        # Consumption details
        sa.Column('amount_consumed', sa.BigInteger, nullable=False),
        sa.Column('balance_before', sa.BigInteger, nullable=False),
        sa.Column('balance_after', sa.BigInteger, nullable=False),
        
        # Context
        sa.Column('consumption_type', sa.String(100)),  # api_usage, ml_inference, etc.
        sa.Column('reference_id', sa.String(255)),  # Invoice ID, usage record ID, etc.
        sa.Column('description', sa.Text),
        
        # Timestamp
        sa.Column('consumed_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
    )
    
    op.create_index('idx_credit_ledger_consumed_at', 'credit_consumption_ledger', ['consumed_at'])
    
    # =========================================================================
    # Customer Health Scores Table
    # =========================================================================
    op.create_table(
        'customer_health_scores',
        sa.Column('score_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('customer_id', sa.String(255), nullable=False, index=True),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False, index=True),
        
        # Overall score
        sa.Column('overall_score', sa.Numeric(5, 2), nullable=False),  # 0.00 to 100.00
        sa.Column('category', sa.String(50), nullable=False),  # critical, at_risk, healthy, champion
        
        # Component scores
        sa.Column('usage_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('engagement_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('support_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('financial_score', sa.Numeric(5, 2), nullable=False),
        
        # Churn risk
        sa.Column('churn_probability', sa.Numeric(5, 4), nullable=False),  # 0.0000 to 1.0000
        sa.Column('churn_risk_level', sa.String(50), nullable=False),  # low, medium, high, critical
        
        # Expansion
        sa.Column('expansion_probability', sa.Numeric(5, 4)),
        sa.Column('upsell_candidates', JSONB, server_default='[]'),
        
        # Recommendations
        sa.Column('interventions', JSONB, server_default='[]'),
        sa.Column('intervention_priority', sa.Integer),  # 1-5, 1 being highest
        
        # Trend
        sa.Column('score_trend', sa.Numeric(6, 2)),  # Change from last calculation
        sa.Column('previous_score_id', UUID(as_uuid=True)),
        
        # Model metadata (for reproducibility)
        sa.Column('model_version', sa.String(50)),
        sa.Column('feature_hash', sa.String(64)),  # SHA256 of input features
        
        # Timestamps
        sa.Column('calculated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('valid_until', sa.DateTime),  # When to recalculate
    )
    
    op.create_index('idx_health_scores_category', 'customer_health_scores', ['category'])
    op.create_index('idx_health_scores_churn_risk', 'customer_health_scores', ['churn_risk_level'])
    op.create_index('idx_health_scores_calculated', 'customer_health_scores', ['calculated_at'])
    
    # =========================================================================
    # Churn Predictions Table (detailed audit trail)
    # =========================================================================
    op.create_table(
        'churn_predictions',
        sa.Column('prediction_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('customer_id', sa.String(255), nullable=False, index=True),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False, index=True),
        
        # Prediction
        sa.Column('churn_probability', sa.Numeric(5, 4), nullable=False),
        sa.Column('risk_level', sa.String(50), nullable=False),
        sa.Column('prediction_horizon_days', sa.Integer, nullable=False, server_default='90'),
        
        # Risk factors (stored as JSONB for flexibility)
        sa.Column('risk_factors', JSONB, nullable=False),
        
        # Mitigation
        sa.Column('mitigation_actions', JSONB, server_default='[]'),
        sa.Column('estimated_save_probability', sa.Numeric(5, 4)),
        
        # Outcome tracking (filled in later)
        sa.Column('actual_churned', sa.Boolean),
        sa.Column('churned_at', sa.DateTime),
        sa.Column('intervention_taken', sa.Boolean, server_default='false'),
        sa.Column('intervention_details', JSONB),
        
        # Model metadata
        sa.Column('model_version', sa.String(50)),
        sa.Column('feature_vector_hash', sa.String(64)),
        
        # Timestamps
        sa.Column('predicted_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
    )
    
    op.create_index('idx_churn_predictions_risk', 'churn_predictions', ['risk_level'])
    op.create_index('idx_churn_predictions_predicted', 'churn_predictions', ['predicted_at'])
    
    # =========================================================================
    # Expansion Opportunities Table
    # =========================================================================
    op.create_table(
        'expansion_opportunities',
        sa.Column('opportunity_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('customer_id', sa.String(255), nullable=False, index=True),
        sa.Column('tenant_id', UUID(as_uuid=True), nullable=False, index=True),
        
        # Opportunity details
        sa.Column('opportunity_type', sa.String(50), nullable=False),  # tier_upgrade, seat_expansion, add_on, multi_year_contract
        sa.Column('probability', sa.Numeric(5, 4), nullable=False),
        sa.Column('estimated_arr_increase_cents', sa.BigInteger),
        
        # Signals
        sa.Column('trigger_signals', JSONB, nullable=False),
        
        # Timing
        sa.Column('optimal_outreach_window', sa.String(100)),
        sa.Column('expires_at', sa.DateTime),
        
        # Recommendation
        sa.Column('recommended_offer', sa.Text),
        sa.Column('talking_points', JSONB, server_default='[]'),
        
        # Status
        sa.Column('status', sa.String(50), server_default='open'),  # open, contacted, converted, declined, expired
        sa.Column('contacted_at', sa.DateTime),
        sa.Column('converted_at', sa.DateTime),
        sa.Column('conversion_value_cents', sa.BigInteger),
        
        # Timestamps
        sa.Column('detected_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
    )
    
    op.create_index('idx_expansion_opps_type', 'expansion_opportunities', ['opportunity_type'])
    op.create_index('idx_expansion_opps_status', 'expansion_opportunities', ['status'])
    op.create_index('idx_expansion_opps_probability', 'expansion_opportunities', ['probability'])
    
    # =========================================================================
    # Pricing Experiments Table
    # =========================================================================
    op.create_table(
        'pricing_experiments',
        sa.Column('experiment_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        
        # Experiment definition
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('experiment_type', sa.String(50), nullable=False),  # price_test, discount_test, tier_test
        
        # Variants
        sa.Column('control_variant', JSONB, nullable=False),  # {price: X, ...}
        sa.Column('test_variants', JSONB, nullable=False),  # [{price: Y, ...}, ...]
        
        # Targeting
        sa.Column('target_segments', JSONB, server_default='[]'),  # Which segments to include
        sa.Column('allocation_percent', sa.Numeric(5, 2), server_default='10.00'),  # % of traffic to experiment
        
        # Safety guards
        sa.Column('min_sample_size', sa.Integer, nullable=False, server_default='100'),
        sa.Column('max_duration_days', sa.Integer, nullable=False, server_default='30'),
        sa.Column('min_confidence_level', sa.Numeric(5, 4), server_default='0.9500'),  # 95%
        sa.Column('negative_lift_threshold', sa.Numeric(5, 4), server_default='-0.0500'),  # -5% triggers auto-stop
        sa.Column('positive_lift_threshold', sa.Numeric(5, 4), server_default='0.0500'),  # +5% triggers winner
        
        # Status
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),  # draft, running, paused, completed, rolled_back
        sa.Column('started_at', sa.DateTime),
        sa.Column('ended_at', sa.DateTime),
        sa.Column('rollback_reason', sa.Text),
        
        # Results
        sa.Column('winner_variant', sa.String(50)),
        sa.Column('observed_lift', sa.Numeric(7, 4)),
        sa.Column('confidence_level', sa.Numeric(5, 4)),
        sa.Column('sample_size_achieved', sa.Integer, server_default='0'),
        
        # Audit
        sa.Column('created_by', sa.String(255)),
        sa.Column('approved_by', sa.String(255)),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
    )
    
    op.create_index('idx_pricing_experiments_status', 'pricing_experiments', ['status'])
    op.create_index('idx_pricing_experiments_type', 'pricing_experiments', ['experiment_type'])
    
    # =========================================================================
    # Pricing Audit Log
    # =========================================================================
    op.create_table(
        'pricing_audit_log',
        sa.Column('audit_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        
        # What changed
        sa.Column('entity_type', sa.String(50), nullable=False),  # contract, price, discount, experiment
        sa.Column('entity_id', sa.String(255), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),  # create, update, delete, approve, reject
        
        # Change details
        sa.Column('old_values', JSONB),
        sa.Column('new_values', JSONB),
        sa.Column('change_reason', sa.Text),
        
        # Actor
        sa.Column('actor_id', sa.String(255), nullable=False),
        sa.Column('actor_type', sa.String(50), nullable=False),  # user, system, api
        sa.Column('actor_role', sa.String(50)),
        sa.Column('ip_address', sa.String(45)),
        
        # Context
        sa.Column('request_id', sa.String(255)),  # Correlation ID
        sa.Column('session_id', sa.String(255)),
        
        # Timestamp
        sa.Column('occurred_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
    )
    
    op.create_index('idx_audit_log_entity', 'pricing_audit_log', ['entity_type', 'entity_id'])
    op.create_index('idx_audit_log_actor', 'pricing_audit_log', ['actor_id'])
    op.create_index('idx_audit_log_occurred', 'pricing_audit_log', ['occurred_at'])
    
    # =========================================================================
    # Stripe Sync Status Table (for tracking sync state)
    # =========================================================================
    op.create_table(
        'stripe_sync_status',
        sa.Column('sync_id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('entity_type', sa.String(50), nullable=False),  # customer, subscription, contract
        sa.Column('entity_id', sa.String(255), nullable=False),
        sa.Column('stripe_id', sa.String(255)),
        
        # Sync state
        sa.Column('last_synced_at', sa.DateTime),
        sa.Column('sync_status', sa.String(50), server_default='pending'),  # pending, synced, failed
        sa.Column('last_error', sa.Text),
        sa.Column('retry_count', sa.Integer, server_default='0'),
        
        # Idempotency
        sa.Column('idempotency_key', sa.String(255)),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        
        sa.UniqueConstraint('entity_type', 'entity_id', name='uq_stripe_sync_entity'),
    )
    
    op.create_index('idx_stripe_sync_status', 'stripe_sync_status', ['sync_status'])


def downgrade() -> None:
    op.drop_table('stripe_sync_status')
    op.drop_table('pricing_audit_log')
    op.drop_table('pricing_experiments')
    op.drop_table('expansion_opportunities')
    op.drop_table('churn_predictions')
    op.drop_table('customer_health_scores')
    op.drop_table('credit_consumption_ledger')
    op.drop_table('prepaid_credits')
    op.drop_table('contract_renewals')
    op.drop_table('contracts')
    op.drop_table('customer_segments')
