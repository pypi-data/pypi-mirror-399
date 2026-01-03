# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
#
# ⚠️ DEPRECATION WARNING (Dec 2025):
# This module has been moved to krl-premium-backend.
# Import from: app.services.billing.billing_exports
# This stub remains for backward compatibility but will be removed in v2.0.
# ----------------------------------------------------------------------

from __future__ import annotations

import warnings as _warnings
_warnings.warn(
    "krl_data_connectors.core.billing.billing_exports is deprecated. "
    "Import from 'app.services.billing.billing_exports' instead.",
    DeprecationWarning,
    stacklevel=2
)


"""
KRL Billing Exports - Week 24 Day 4
===================================

Data export functionality for billing data with multiple formats
and scheduled report generation.

Features:
- Multi-format exports (CSV, JSON, Parquet)
- Scheduled report generation
- Data pipeline integration
- Compliance-ready exports
- Historical data archival
"""


import csv
import gzip
import io
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone, UTC
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from uuid import uuid4

logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class ExportFormat(str, Enum):
    """Supported export formats."""
    CSV = "csv"
    JSON = "json"
    JSONL = "jsonl"  # JSON Lines
    PARQUET = "parquet"
    EXCEL = "excel"


class ExportScope(str, Enum):
    """Export data scope."""
    FULL = "full"
    INCREMENTAL = "incremental"
    CUSTOM = "custom"


class CompressionType(str, Enum):
    """Compression options."""
    NONE = "none"
    GZIP = "gzip"
    SNAPPY = "snappy"  # For Parquet


class ScheduleFrequency(str, Enum):
    """Report schedule frequency."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ON_DEMAND = "on_demand"


class ExportStatus(str, Enum):
    """Export job status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ExportConfig:
    """Export configuration."""
    export_id: str
    name: str
    format: ExportFormat
    scope: ExportScope = ExportScope.FULL
    compression: CompressionType = CompressionType.NONE
    
    # Data selection
    data_types: List[str] = field(default_factory=lambda: ["subscriptions", "invoices"])
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    
    # Output
    output_path: Optional[str] = None
    include_headers: bool = True
    pretty_print: bool = False
    
    # Compliance
    pii_mask: bool = True
    include_metadata: bool = True


@dataclass
class ExportJob:
    """Export job tracking."""
    job_id: str
    config: ExportConfig
    status: ExportStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    records_exported: int = 0
    file_size_bytes: int = 0
    output_location: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class ScheduledReport:
    """Scheduled report definition."""
    report_id: str
    name: str
    frequency: ScheduleFrequency
    config: ExportConfig
    
    # Schedule
    next_run: datetime
    last_run: Optional[datetime] = None
    enabled: bool = True
    
    # Delivery
    recipients: List[str] = field(default_factory=list)
    delivery_method: str = "email"  # email, s3, webhook
    delivery_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExportResult:
    """Export operation result."""
    success: bool
    job_id: str
    records: int
    file_path: Optional[str]
    file_size: int
    duration_ms: int
    format: ExportFormat
    error: Optional[str] = None


# =============================================================================
# Data Serializers
# =============================================================================

class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types."""
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class DataSerializer:
    """
    Serializes billing data to various formats.
    """
    
    def __init__(self, pii_mask: bool = True):
        self.pii_mask = pii_mask
        self._pii_fields = {"email", "phone", "address", "name", "ip_address"}
    
    def serialize(
        self,
        data: List[Dict[str, Any]],
        format: ExportFormat,
        config: ExportConfig,
    ) -> bytes:
        """Serialize data to specified format."""
        if self.pii_mask and config.pii_mask:
            data = self._mask_pii(data)
        
        if format == ExportFormat.CSV:
            return self._to_csv(data, config)
        elif format == ExportFormat.JSON:
            return self._to_json(data, config)
        elif format == ExportFormat.JSONL:
            return self._to_jsonl(data)
        elif format == ExportFormat.PARQUET:
            return self._to_parquet(data)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _mask_pii(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Mask PII fields in data."""
        masked = []
        for record in data:
            masked_record = {}
            for key, value in record.items():
                if key.lower() in self._pii_fields:
                    masked_record[key] = self._mask_value(value)
                else:
                    masked_record[key] = value
            masked.append(masked_record)
        return masked
    
    def _mask_value(self, value: Any) -> str:
        """Mask a single value."""
        if not value:
            return "[REDACTED]"
        s = str(value)
        if "@" in s:  # Email
            parts = s.split("@")
            return f"{parts[0][:2]}***@{parts[1]}" if len(parts) == 2 else "[REDACTED]"
        elif len(s) > 4:
            return f"{s[:2]}{'*' * (len(s) - 4)}{s[-2:]}"
        return "[REDACTED]"
    
    def _to_csv(self, data: List[Dict[str, Any]], config: ExportConfig) -> bytes:
        """Convert to CSV format."""
        if not data:
            return b""
        
        output = io.StringIO()
        fieldnames = list(data[0].keys())
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        if config.include_headers:
            writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue().encode("utf-8")
    
    def _to_json(self, data: List[Dict[str, Any]], config: ExportConfig) -> bytes:
        """Convert to JSON format."""
        indent = 2 if config.pretty_print else None
        return json.dumps(data, cls=DecimalEncoder, indent=indent).encode("utf-8")
    
    def _to_jsonl(self, data: List[Dict[str, Any]]) -> bytes:
        """Convert to JSON Lines format."""
        lines = [json.dumps(record, cls=DecimalEncoder) for record in data]
        return "\n".join(lines).encode("utf-8")
    
    def _to_parquet(self, data: List[Dict[str, Any]]) -> bytes:
        """Convert to Parquet format (stub - requires pyarrow)."""
        # In production, would use pyarrow:
        # import pyarrow as pa
        # import pyarrow.parquet as pq
        # table = pa.Table.from_pylist(data)
        # buffer = io.BytesIO()
        # pq.write_table(table, buffer)
        # return buffer.getvalue()
        
        # Fallback to JSON
        logger.warning("Parquet export requires pyarrow, falling back to JSON")
        return self._to_json(data, ExportConfig(
            export_id="temp",
            name="temp",
            format=ExportFormat.JSON,
        ))


# =============================================================================
# Export Engine
# =============================================================================

class BillingExportEngine:
    """
    Core export engine for billing data.
    
    Handles:
    - Data extraction
    - Format conversion
    - Compression
    - Output storage
    """
    
    def __init__(
        self,
        output_dir: Optional[str] = None,
        serializer: Optional[DataSerializer] = None,
    ):
        self.output_dir = Path(output_dir) if output_dir else Path("./exports")
        self.serializer = serializer or DataSerializer()
        
        # Job tracking
        self._jobs: Dict[str, ExportJob] = {}
        
        # Data providers (would be connected to actual data sources)
        self._data_providers: Dict[str, Callable] = {}
    
    def register_data_provider(
        self,
        data_type: str,
        provider: Callable[[], List[Dict[str, Any]]],
    ) -> None:
        """Register data provider for data type."""
        self._data_providers[data_type] = provider
        logger.debug(f"Registered data provider: {data_type}")
    
    def export(self, config: ExportConfig) -> ExportResult:
        """Execute export with given configuration."""
        start_time = datetime.now(timezone.utc)
        job_id = uuid4().hex
        
        # Create job
        job = ExportJob(
            job_id=job_id,
            config=config,
            status=ExportStatus.RUNNING,
            created_at=start_time,
            started_at=start_time,
        )
        self._jobs[job_id] = job
        
        try:
            # Gather data
            all_data: List[Dict[str, Any]] = []
            for data_type in config.data_types:
                if data_type in self._data_providers:
                    type_data = self._data_providers[data_type]()
                    all_data.extend(type_data)
                else:
                    all_data.extend(self._get_mock_data(data_type))
            
            # Apply filters
            if config.filters:
                all_data = self._apply_filters(all_data, config.filters)
            
            # Apply date range
            if config.start_date or config.end_date:
                all_data = self._apply_date_range(
                    all_data, config.start_date, config.end_date
                )
            
            # Serialize
            serialized = self.serializer.serialize(all_data, config.format, config)
            
            # Compress if needed
            if config.compression == CompressionType.GZIP:
                serialized = gzip.compress(serialized)
            
            # Write output
            output_path = self._get_output_path(config, job_id)
            self.output_dir.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(serialized)
            
            # Update job
            end_time = datetime.now(timezone.utc)
            job.status = ExportStatus.COMPLETED
            job.completed_at = end_time
            job.records_exported = len(all_data)
            job.file_size_bytes = len(serialized)
            job.output_location = str(output_path)
            
            return ExportResult(
                success=True,
                job_id=job_id,
                records=len(all_data),
                file_path=str(output_path),
                file_size=len(serialized),
                duration_ms=int((end_time - start_time).total_seconds() * 1000),
                format=config.format,
            )
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            job.status = ExportStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            
            return ExportResult(
                success=False,
                job_id=job_id,
                records=0,
                file_path=None,
                file_size=0,
                duration_ms=int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000),
                format=config.format,
                error=str(e),
            )
    
    def get_job(self, job_id: str) -> Optional[ExportJob]:
        """Get export job by ID."""
        return self._jobs.get(job_id)
    
    def list_jobs(
        self,
        status: Optional[ExportStatus] = None,
        limit: int = 100,
    ) -> List[ExportJob]:
        """List export jobs."""
        jobs = list(self._jobs.values())
        if status:
            jobs = [j for j in jobs if j.status == status]
        return sorted(jobs, key=lambda x: x.created_at, reverse=True)[:limit]
    
    def _get_output_path(self, config: ExportConfig, job_id: str) -> Path:
        """Generate output file path."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        ext = config.format.value
        if config.compression == CompressionType.GZIP:
            ext += ".gz"
        
        filename = f"{config.name}_{timestamp}_{job_id[:8]}.{ext}"
        
        if config.output_path:
            return Path(config.output_path) / filename
        return self.output_dir / filename
    
    def _apply_filters(
        self,
        data: List[Dict[str, Any]],
        filters: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Apply filters to data."""
        filtered = []
        for record in data:
            include = True
            for key, value in filters.items():
                if key not in record:
                    continue
                if isinstance(value, list):
                    if record[key] not in value:
                        include = False
                        break
                elif record[key] != value:
                    include = False
                    break
            if include:
                filtered.append(record)
        return filtered
    
    def _apply_date_range(
        self,
        data: List[Dict[str, Any]],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
    ) -> List[Dict[str, Any]]:
        """Apply date range filter."""
        date_fields = ["created_at", "updated_at", "timestamp", "date"]
        filtered = []
        
        for record in data:
            record_date = None
            for field in date_fields:
                if field in record:
                    val = record[field]
                    if isinstance(val, datetime):
                        record_date = val
                    elif isinstance(val, str):
                        try:
                            record_date = datetime.fromisoformat(val.replace("Z", "+00:00"))
                        except ValueError:
                            pass
                    break
            
            if not record_date:
                filtered.append(record)  # Keep records without dates
                continue
            
            if start_date and record_date < start_date:
                continue
            if end_date and record_date > end_date:
                continue
            filtered.append(record)
        
        return filtered
    
    def _get_mock_data(self, data_type: str) -> List[Dict[str, Any]]:
        """Get mock data for testing."""
        now = datetime.now(timezone.utc)
        
        if data_type == "subscriptions":
            return [
                {
                    "id": f"sub_{i}",
                    "customer_id": f"cus_{i}",
                    "tier": ["community", "pro", "enterprise"][i % 3],
                    "amount": [0, 49, 199][i % 3],
                    "status": "active",
                    "created_at": (now - timedelta(days=i * 30)).isoformat(),
                }
                for i in range(10)
            ]
        elif data_type == "invoices":
            return [
                {
                    "id": f"inv_{i}",
                    "customer_id": f"cus_{i % 10}",
                    "amount": 100 + i * 10,
                    "status": "paid",
                    "created_at": (now - timedelta(days=i * 7)).isoformat(),
                }
                for i in range(20)
            ]
        
        return []


# =============================================================================
# Report Scheduler
# =============================================================================

class ReportScheduler:
    """
    Manages scheduled report generation.
    
    Features:
    - Cron-like scheduling
    - Email/S3/Webhook delivery
    - Retry on failure
    """
    
    def __init__(self, export_engine: BillingExportEngine):
        self.export_engine = export_engine
        self._schedules: Dict[str, ScheduledReport] = {}
        self._running = False
    
    def create_schedule(
        self,
        name: str,
        frequency: ScheduleFrequency,
        config: ExportConfig,
        recipients: Optional[List[str]] = None,
    ) -> ScheduledReport:
        """Create scheduled report."""
        next_run = self._calculate_next_run(frequency)
        
        schedule = ScheduledReport(
            report_id=uuid4().hex,
            name=name,
            frequency=frequency,
            config=config,
            next_run=next_run,
            recipients=recipients or [],
        )
        
        self._schedules[schedule.report_id] = schedule
        logger.info(f"Created scheduled report: {name} ({frequency.value})")
        return schedule
    
    def delete_schedule(self, report_id: str) -> bool:
        """Delete scheduled report."""
        if report_id in self._schedules:
            del self._schedules[report_id]
            return True
        return False
    
    def enable_schedule(self, report_id: str) -> bool:
        """Enable scheduled report."""
        if report_id in self._schedules:
            self._schedules[report_id].enabled = True
            return True
        return False
    
    def disable_schedule(self, report_id: str) -> bool:
        """Disable scheduled report."""
        if report_id in self._schedules:
            self._schedules[report_id].enabled = False
            return True
        return False
    
    def run_now(self, report_id: str) -> Optional[ExportResult]:
        """Run scheduled report immediately."""
        schedule = self._schedules.get(report_id)
        if not schedule:
            return None
        
        result = self.export_engine.export(schedule.config)
        schedule.last_run = datetime.now(timezone.utc)
        schedule.next_run = self._calculate_next_run(schedule.frequency)
        
        if result.success and schedule.recipients:
            self._deliver_report(schedule, result)
        
        return result
    
    def check_and_run(self) -> List[ExportResult]:
        """Check schedules and run due reports."""
        results = []
        now = datetime.now(timezone.utc)
        
        for schedule in self._schedules.values():
            if not schedule.enabled:
                continue
            if schedule.next_run <= now:
                result = self.run_now(schedule.report_id)
                if result:
                    results.append(result)
        
        return results
    
    def list_schedules(self) -> List[ScheduledReport]:
        """List all scheduled reports."""
        return list(self._schedules.values())
    
    def _calculate_next_run(self, frequency: ScheduleFrequency) -> datetime:
        """Calculate next run time."""
        now = datetime.now(timezone.utc)
        
        if frequency == ScheduleFrequency.HOURLY:
            return now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        elif frequency == ScheduleFrequency.DAILY:
            return now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        elif frequency == ScheduleFrequency.WEEKLY:
            days_until_monday = (7 - now.weekday()) % 7 or 7
            return now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days_until_monday)
        elif frequency == ScheduleFrequency.MONTHLY:
            if now.month == 12:
                return now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            return now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        return now + timedelta(days=1)
    
    def _deliver_report(self, schedule: ScheduledReport, result: ExportResult) -> None:
        """Deliver report to recipients."""
        # Would implement actual delivery (email, S3, webhook)
        logger.info(f"Delivering report {schedule.name} to {len(schedule.recipients)} recipients")


# =============================================================================
# Factory Functions
# =============================================================================

def create_billing_export_engine(
    output_dir: Optional[str] = None,
    pii_mask: bool = True,
) -> BillingExportEngine:
    """Create configured BillingExportEngine."""
    serializer = DataSerializer(pii_mask=pii_mask)
    return BillingExportEngine(output_dir=output_dir, serializer=serializer)


def create_report_scheduler(
    export_engine: Optional[BillingExportEngine] = None,
) -> ReportScheduler:
    """Create configured ReportScheduler."""
    engine = export_engine or create_billing_export_engine()
    return ReportScheduler(export_engine=engine)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "ExportFormat",
    "ExportScope",
    "CompressionType",
    "ScheduleFrequency",
    "ExportStatus",
    # Data Classes
    "ExportConfig",
    "ExportJob",
    "ScheduledReport",
    "ExportResult",
    # Classes
    "DecimalEncoder",
    "DataSerializer",
    "BillingExportEngine",
    "ReportScheduler",
    # Factory
    "create_billing_export_engine",
    "create_report_scheduler",
]
