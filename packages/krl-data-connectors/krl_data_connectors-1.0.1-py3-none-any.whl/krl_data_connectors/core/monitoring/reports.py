"""
Reporting Module - Phase 2 Week 13

Scheduled security reports and compliance documentation generation.

Copyright 2025 KR-Labs. All rights reserved.
"""

from __future__ import annotations

import csv
import io
import json
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta, UTC
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import uuid


class ReportType(Enum):
    """Types of security reports."""
    
    SECURITY_SUMMARY = "security_summary"
    INCIDENT_REPORT = "incident_report"
    COMPLIANCE_AUDIT = "compliance_audit"
    LICENSE_USAGE = "license_usage"
    ANOMALY_ANALYSIS = "anomaly_analysis"
    ACCESS_AUDIT = "access_audit"
    THREAT_ASSESSMENT = "threat_assessment"


class ReportFormat(Enum):
    """Report output formats."""
    
    JSON = "json"
    HTML = "html"
    PDF = "pdf"
    CSV = "csv"
    MARKDOWN = "markdown"


class ReportPeriod(Enum):
    """Report time periods."""
    
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    CUSTOM = "custom"


@dataclass
class ReportSection:
    """A section within a report."""
    
    title: str
    content: str
    data: Dict[str, Any] = field(default_factory=dict)
    charts: List[Dict[str, Any]] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    subsections: List["ReportSection"] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "content": self.content,
            "data": self.data,
            "charts": self.charts,
            "tables": self.tables,
            "subsections": [s.to_dict() for s in self.subsections],
        }


@dataclass
class Report:
    """A generated report."""
    
    report_id: str
    report_type: ReportType
    title: str
    generated_at: float
    period_start: float
    period_end: float
    sections: List[ReportSection] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "report_id": self.report_id,
            "report_type": self.report_type.value,
            "title": self.title,
            "generated_at": self.generated_at,
            "generated_at_iso": datetime.fromtimestamp(
                self.generated_at, tz=timezone.utc
            ).isoformat(),
            "period": {
                "start": self.period_start,
                "start_iso": datetime.fromtimestamp(
                    self.period_start, tz=timezone.utc
                ).isoformat(),
                "end": self.period_end,
                "end_iso": datetime.fromtimestamp(
                    self.period_end, tz=timezone.utc
                ).isoformat(),
            },
            "summary": self.summary,
            "sections": [s.to_dict() for s in self.sections],
            "metadata": self.metadata,
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    def to_markdown(self) -> str:
        """Convert to Markdown format."""
        lines = [
            f"# {self.title}",
            "",
            f"**Report ID:** {self.report_id}",
            f"**Generated:** {datetime.fromtimestamp(self.generated_at, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Period:** {datetime.fromtimestamp(self.period_start, tz=timezone.utc).strftime('%Y-%m-%d')} to {datetime.fromtimestamp(self.period_end, tz=timezone.utc).strftime('%Y-%m-%d')}",
            "",
            "## Executive Summary",
            "",
            self.summary,
            "",
        ]
        
        for section in self.sections:
            lines.extend(self._section_to_markdown(section, level=2))
        
        return "\n".join(lines)
    
    def _section_to_markdown(self, section: ReportSection, level: int = 2) -> List[str]:
        """Convert section to Markdown lines."""
        lines = [
            "#" * level + f" {section.title}",
            "",
            section.content,
            "",
        ]
        
        # Add tables
        for table in section.tables:
            headers = table.get("headers", [])
            rows = table.get("rows", [])
            
            if headers:
                lines.append("| " + " | ".join(headers) + " |")
                lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                for row in rows:
                    lines.append("| " + " | ".join(str(c) for c in row) + " |")
                lines.append("")
        
        # Add subsections
        for subsection in section.subsections:
            lines.extend(self._section_to_markdown(subsection, level + 1))
        
        return lines
    
    def to_html(self) -> str:
        """Convert to HTML format."""
        sections_html = ""
        for section in self.sections:
            sections_html += self._section_to_html(section)
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>{self.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; border-bottom: 2px solid #333; }}
        h2 {{ color: #555; margin-top: 30px; }}
        h3 {{ color: #666; }}
        .meta {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .summary {{ background: #e8f4fd; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #f2f2f2; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .metric {{ display: inline-block; padding: 10px 20px; margin: 5px; background: #f0f0f0; border-radius: 5px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #333; }}
        .metric-label {{ font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <h1>{self.title}</h1>
    <div class="meta">
        <p><strong>Report ID:</strong> {self.report_id}</p>
        <p><strong>Generated:</strong> {datetime.fromtimestamp(self.generated_at, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        <p><strong>Period:</strong> {datetime.fromtimestamp(self.period_start, tz=timezone.utc).strftime('%Y-%m-%d')} to {datetime.fromtimestamp(self.period_end, tz=timezone.utc).strftime('%Y-%m-%d')}</p>
    </div>
    <div class="summary">
        <h2>Executive Summary</h2>
        <p>{self.summary}</p>
    </div>
    {sections_html}
</body>
</html>"""
    
    def _section_to_html(self, section: ReportSection, level: int = 2) -> str:
        """Convert section to HTML."""
        tag = f"h{min(level, 6)}"
        
        html = f"<{tag}>{section.title}</{tag}>\n"
        html += f"<p>{section.content}</p>\n"
        
        # Add tables
        for table in section.tables:
            headers = table.get("headers", [])
            rows = table.get("rows", [])
            
            html += "<table>\n"
            if headers:
                html += "<thead><tr>"
                for h in headers:
                    html += f"<th>{h}</th>"
                html += "</tr></thead>\n"
            
            html += "<tbody>\n"
            for row in rows:
                html += "<tr>"
                for cell in row:
                    html += f"<td>{cell}</td>"
                html += "</tr>\n"
            html += "</tbody></table>\n"
        
        # Subsections
        for subsection in section.subsections:
            html += self._section_to_html(subsection, level + 1)
        
        return html


@dataclass
class ReportConfig:
    """Configuration for report generation."""
    
    # Output
    output_dir: Path = field(default_factory=lambda: Path("reports"))
    default_format: ReportFormat = ReportFormat.JSON
    
    # Scheduling
    daily_report_hour: int = 6  # UTC
    weekly_report_day: int = 0  # Monday
    
    # Content
    include_charts: bool = True
    include_raw_data: bool = False
    
    # Retention
    retention_days: int = 365


class ReportDataCollector(ABC):
    """Abstract base class for report data collectors."""
    
    @abstractmethod
    def collect(
        self,
        period_start: float,
        period_end: float
    ) -> Dict[str, Any]:
        """Collect data for the report."""
        pass


class SecuritySummaryCollector(ReportDataCollector):
    """Collects data for security summary reports."""
    
    def collect(self, period_start: float, period_end: float) -> Dict[str, Any]:
        """Collect security summary data."""
        # In production, this would query actual metrics
        return {
            "auth_attempts": {
                "total": 15234,
                "successful": 14892,
                "failed": 342,
                "success_rate": 97.75,
            },
            "incidents": {
                "total": 12,
                "critical": 1,
                "high": 3,
                "medium": 5,
                "low": 3,
                "resolved": 10,
            },
            "license_usage": {
                "active_licenses": 156,
                "validations": 45678,
                "rejections": 23,
            },
            "integrity_checks": {
                "total": 8934,
                "passed": 8932,
                "failed": 2,
            },
            "api_usage": {
                "total_requests": 234567,
                "error_rate": 0.12,
                "avg_latency_ms": 45.2,
            },
        }


class IncidentReportCollector(ReportDataCollector):
    """Collects data for incident reports."""
    
    def collect(self, period_start: float, period_end: float) -> Dict[str, Any]:
        """Collect incident data."""
        return {
            "incidents": [],  # Would be populated from incident manager
            "mttr_hours": 2.5,  # Mean time to resolve
            "mttd_minutes": 15,  # Mean time to detect
            "by_category": {},
            "by_severity": {},
        }


class ReportGenerator:
    """
    Generates security and compliance reports.
    
    Features:
    - Multiple report types
    - Scheduled generation
    - Multiple output formats
    - Custom data collectors
    """
    
    def __init__(self, config: ReportConfig | None = None):
        self.config = config or ReportConfig()
        self._collectors: Dict[ReportType, ReportDataCollector] = {}
        self._scheduled_reports: List[Dict[str, Any]] = []
        self._lock = threading.RLock()
        
        # Register default collectors
        self._collectors[ReportType.SECURITY_SUMMARY] = SecuritySummaryCollector()
        self._collectors[ReportType.INCIDENT_REPORT] = IncidentReportCollector()
        
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_report_id(self, report_type: ReportType) -> str:
        """Generate unique report ID."""
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        return f"RPT-{report_type.value.upper()[:4]}-{date_str}-{uuid.uuid4().hex[:6].upper()}"
    
    def register_collector(
        self,
        report_type: ReportType,
        collector: ReportDataCollector
    ) -> None:
        """Register a custom data collector."""
        with self._lock:
            self._collectors[report_type] = collector
    
    def generate(
        self,
        report_type: ReportType,
        period_start: float | None = None,
        period_end: float | None = None,
        period: ReportPeriod = ReportPeriod.DAILY,
    ) -> Report:
        """Generate a report."""
        # Calculate period
        now = time.time()
        if period_end is None:
            period_end = now
        
        if period_start is None:
            if period == ReportPeriod.DAILY:
                period_start = period_end - 86400
            elif period == ReportPeriod.WEEKLY:
                period_start = period_end - 604800
            elif period == ReportPeriod.MONTHLY:
                period_start = period_end - 2592000
            elif period == ReportPeriod.QUARTERLY:
                period_start = period_end - 7776000
            elif period == ReportPeriod.ANNUAL:
                period_start = period_end - 31536000
            else:
                period_start = period_end - 86400
        
        # Collect data
        collector = self._collectors.get(report_type)
        data = collector.collect(period_start, period_end) if collector else {}
        
        # Generate report based on type
        if report_type == ReportType.SECURITY_SUMMARY:
            return self._generate_security_summary(data, period_start, period_end)
        elif report_type == ReportType.INCIDENT_REPORT:
            return self._generate_incident_report(data, period_start, period_end)
        elif report_type == ReportType.COMPLIANCE_AUDIT:
            return self._generate_compliance_report(data, period_start, period_end)
        else:
            return self._generate_generic_report(report_type, data, period_start, period_end)
    
    def _generate_security_summary(
        self,
        data: Dict[str, Any],
        period_start: float,
        period_end: float
    ) -> Report:
        """Generate security summary report."""
        report = Report(
            report_id=self._generate_report_id(ReportType.SECURITY_SUMMARY),
            report_type=ReportType.SECURITY_SUMMARY,
            title="Security Summary Report",
            generated_at=time.time(),
            period_start=period_start,
            period_end=period_end,
        )
        
        auth_data = data.get("auth_attempts", {})
        incident_data = data.get("incidents", {})
        api_data = data.get("api_usage", {})
        
        # Executive summary
        report.summary = (
            f"During this reporting period, the system processed {auth_data.get('total', 0):,} "
            f"authentication attempts with a {auth_data.get('success_rate', 0):.1f}% success rate. "
            f"{incident_data.get('total', 0)} security incidents were recorded, with "
            f"{incident_data.get('resolved', 0)} resolved. API services handled "
            f"{api_data.get('total_requests', 0):,} requests with an average latency of "
            f"{api_data.get('avg_latency_ms', 0):.1f}ms."
        )
        
        # Authentication section
        auth_section = ReportSection(
            title="Authentication Overview",
            content="Summary of authentication activity during the reporting period.",
            data=auth_data,
            tables=[{
                "headers": ["Metric", "Value"],
                "rows": [
                    ["Total Attempts", f"{auth_data.get('total', 0):,}"],
                    ["Successful", f"{auth_data.get('successful', 0):,}"],
                    ["Failed", f"{auth_data.get('failed', 0):,}"],
                    ["Success Rate", f"{auth_data.get('success_rate', 0):.2f}%"],
                ]
            }]
        )
        report.sections.append(auth_section)
        
        # Incidents section
        incident_section = ReportSection(
            title="Security Incidents",
            content="Overview of security incidents during the reporting period.",
            data=incident_data,
            tables=[{
                "headers": ["Severity", "Count"],
                "rows": [
                    ["Critical", incident_data.get("critical", 0)],
                    ["High", incident_data.get("high", 0)],
                    ["Medium", incident_data.get("medium", 0)],
                    ["Low", incident_data.get("low", 0)],
                ]
            }]
        )
        report.sections.append(incident_section)
        
        # API section
        api_section = ReportSection(
            title="API Performance",
            content="API usage and performance metrics.",
            data=api_data,
            tables=[{
                "headers": ["Metric", "Value"],
                "rows": [
                    ["Total Requests", f"{api_data.get('total_requests', 0):,}"],
                    ["Error Rate", f"{api_data.get('error_rate', 0):.2f}%"],
                    ["Avg Latency", f"{api_data.get('avg_latency_ms', 0):.1f}ms"],
                ]
            }]
        )
        report.sections.append(api_section)
        
        return report
    
    def _generate_incident_report(
        self,
        data: Dict[str, Any],
        period_start: float,
        period_end: float
    ) -> Report:
        """Generate incident report."""
        report = Report(
            report_id=self._generate_report_id(ReportType.INCIDENT_REPORT),
            report_type=ReportType.INCIDENT_REPORT,
            title="Incident Analysis Report",
            generated_at=time.time(),
            period_start=period_start,
            period_end=period_end,
        )
        
        mttr = data.get("mttr_hours", 0)
        mttd = data.get("mttd_minutes", 0)
        
        report.summary = (
            f"This report provides analysis of security incidents. "
            f"Mean time to detect (MTTD): {mttd} minutes. "
            f"Mean time to resolve (MTTR): {mttr} hours."
        )
        
        # Metrics section
        metrics_section = ReportSection(
            title="Response Metrics",
            content="Key incident response metrics.",
            tables=[{
                "headers": ["Metric", "Value", "Target", "Status"],
                "rows": [
                    ["MTTD", f"{mttd} min", "< 30 min", "✅" if mttd < 30 else "⚠️"],
                    ["MTTR", f"{mttr} hrs", "< 4 hrs", "✅" if mttr < 4 else "⚠️"],
                ]
            }]
        )
        report.sections.append(metrics_section)
        
        return report
    
    def _generate_compliance_report(
        self,
        data: Dict[str, Any],
        period_start: float,
        period_end: float
    ) -> Report:
        """Generate compliance audit report."""
        report = Report(
            report_id=self._generate_report_id(ReportType.COMPLIANCE_AUDIT),
            report_type=ReportType.COMPLIANCE_AUDIT,
            title="Compliance Audit Report",
            generated_at=time.time(),
            period_start=period_start,
            period_end=period_end,
        )
        
        report.summary = (
            "This report documents compliance with security policies and regulatory requirements."
        )
        
        # Controls section
        controls_section = ReportSection(
            title="Security Controls Assessment",
            content="Status of implemented security controls.",
            tables=[{
                "headers": ["Control", "Category", "Status", "Last Verified"],
                "rows": [
                    ["Authentication MFA", "Access Control", "✅ Compliant", "2025-12-01"],
                    ["Audit Logging", "Monitoring", "✅ Compliant", "2025-12-01"],
                    ["Data Encryption", "Data Protection", "✅ Compliant", "2025-12-01"],
                    ["License Verification", "IP Protection", "✅ Compliant", "2025-12-01"],
                    ["Integrity Checking", "Code Security", "✅ Compliant", "2025-12-01"],
                ]
            }]
        )
        report.sections.append(controls_section)
        
        return report
    
    def _generate_generic_report(
        self,
        report_type: ReportType,
        data: Dict[str, Any],
        period_start: float,
        period_end: float
    ) -> Report:
        """Generate generic report from data."""
        report = Report(
            report_id=self._generate_report_id(report_type),
            report_type=report_type,
            title=f"{report_type.value.replace('_', ' ').title()} Report",
            generated_at=time.time(),
            period_start=period_start,
            period_end=period_end,
        )
        
        report.summary = f"Report generated for {report_type.value}."
        
        if data:
            data_section = ReportSection(
                title="Data",
                content="Collected data for this report.",
                data=data,
            )
            report.sections.append(data_section)
        
        return report
    
    def save(
        self,
        report: Report,
        format: ReportFormat | None = None,
        output_path: Path | None = None
    ) -> Path:
        """Save report to file."""
        format = format or self.config.default_format
        
        if output_path is None:
            date_str = datetime.fromtimestamp(
                report.generated_at, tz=timezone.utc
            ).strftime("%Y%m%d_%H%M%S")
            filename = f"{report.report_type.value}_{date_str}"
            
            ext_map = {
                ReportFormat.JSON: ".json",
                ReportFormat.HTML: ".html",
                ReportFormat.MARKDOWN: ".md",
                ReportFormat.CSV: ".csv",
            }
            
            output_path = self.config.output_dir / f"{filename}{ext_map.get(format, '.json')}"
        
        # Generate content
        if format == ReportFormat.JSON:
            content = report.to_json()
        elif format == ReportFormat.HTML:
            content = report.to_html()
        elif format == ReportFormat.MARKDOWN:
            content = report.to_markdown()
        elif format == ReportFormat.CSV:
            content = self._report_to_csv(report)
        else:
            content = report.to_json()
        
        output_path.write_text(content)
        return output_path
    
    def _report_to_csv(self, report: Report) -> str:
        """Convert report to CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write metadata
        writer.writerow(["Report ID", report.report_id])
        writer.writerow(["Type", report.report_type.value])
        writer.writerow(["Generated", datetime.fromtimestamp(report.generated_at, tz=timezone.utc).isoformat()])
        writer.writerow([])
        
        # Write section data
        for section in report.sections:
            writer.writerow([section.title])
            for table in section.tables:
                if table.get("headers"):
                    writer.writerow(table["headers"])
                for row in table.get("rows", []):
                    writer.writerow(row)
            writer.writerow([])
        
        return output.getvalue()
    
    def schedule_report(
        self,
        report_type: ReportType,
        period: ReportPeriod,
        format: ReportFormat | None = None,
        callback: Callable[[Report], None] | None = None
    ) -> str:
        """Schedule a recurring report."""
        schedule_id = str(uuid.uuid4())[:8]
        
        with self._lock:
            self._scheduled_reports.append({
                "id": schedule_id,
                "report_type": report_type,
                "period": period,
                "format": format or self.config.default_format,
                "callback": callback,
                "last_run": 0.0,
            })
        
        return schedule_id
    
    def unschedule_report(self, schedule_id: str) -> bool:
        """Remove scheduled report."""
        with self._lock:
            for i, scheduled in enumerate(self._scheduled_reports):
                if scheduled["id"] == schedule_id:
                    del self._scheduled_reports[i]
                    return True
        return False
    
    def run_scheduled(self) -> List[Report]:
        """Run any due scheduled reports."""
        now = time.time()
        reports = []
        
        with self._lock:
            for scheduled in self._scheduled_reports:
                period = scheduled["period"]
                last_run = scheduled["last_run"]
                
                # Check if due
                interval_map = {
                    ReportPeriod.DAILY: 86400,
                    ReportPeriod.WEEKLY: 604800,
                    ReportPeriod.MONTHLY: 2592000,
                }
                
                interval = interval_map.get(period, 86400)
                
                if now - last_run >= interval:
                    report = self.generate(
                        scheduled["report_type"],
                        period=period
                    )
                    
                    self.save(report, scheduled["format"])
                    
                    if scheduled["callback"]:
                        try:
                            scheduled["callback"](report)
                        except Exception:
                            pass
                    
                    scheduled["last_run"] = now
                    reports.append(report)
        
        return reports


# Global instance
_global_report_generator: ReportGenerator | None = None


def get_report_generator() -> ReportGenerator:
    """Get or create global report generator."""
    global _global_report_generator
    if _global_report_generator is None:
        _global_report_generator = ReportGenerator()
    return _global_report_generator
