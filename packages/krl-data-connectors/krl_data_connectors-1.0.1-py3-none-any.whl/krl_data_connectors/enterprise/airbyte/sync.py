# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Sync Management for Airbyte Integration.

Provides high-level sync job management, status tracking, and scheduling
for Airbyte data pipelines.
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import time
import threading

from krl_core import get_logger


class SyncStatus(Enum):
    """Status of a sync job."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    INCOMPLETE = "incomplete"


@dataclass
class SyncJob:
    """
    Represents an Airbyte sync job.

    Tracks job execution, status, and results.
    """

    job_id: int
    connection_id: str
    status: SyncStatus
    job_type: str = "sync"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    bytes_synced: int = 0
    records_synced: int = 0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate job duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    @property
    def is_complete(self) -> bool:
        """Check if job has completed (success or failure)."""
        return self.status in [
            SyncStatus.SUCCEEDED,
            SyncStatus.FAILED,
            SyncStatus.CANCELLED,
        ]

    @property
    def is_running(self) -> bool:
        """Check if job is currently running."""
        return self.status == SyncStatus.RUNNING

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "job_id": self.job_id,
            "connection_id": self.connection_id,
            "status": self.status.value,
            "job_type": self.job_type,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "bytes_synced": self.bytes_synced,
            "records_synced": self.records_synced,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


class SyncManager:
    """
    High-level sync job management for Airbyte.

    Provides convenient methods for triggering, monitoring, and
    managing sync jobs across multiple connections.

    Features:
    - Job triggering and status tracking
    - Polling with callbacks
    - Batch job management
    - Schedule validation

    Example:
        >>> from krl_data_connectors.enterprise.airbyte import AirbyteClient, SyncManager
        >>> client = AirbyteClient(api_key="...")
        >>> manager = SyncManager(client)
        >>>
        >>> # Trigger and wait for sync
        >>> job = manager.sync_and_wait("connection-id", timeout=300)
        >>> print(f"Synced {job.records_synced} records")
        >>>
        >>> # Trigger with callback
        >>> manager.sync_with_callback(
        ...     "connection-id",
        ...     on_complete=lambda j: print(f"Done: {j.status}")
        ... )
    """

    def __init__(self, client: "AirbyteClient"):
        """
        Initialize sync manager.

        Args:
            client: Configured AirbyteClient instance
        """
        self.client = client
        self.logger = get_logger("SyncManager")
        self._active_jobs: Dict[int, SyncJob] = {}
        self._callbacks: Dict[int, List[Callable]] = {}

    def trigger_sync(self, connection_id: str) -> SyncJob:
        """
        Trigger a sync job for a connection.

        Args:
            connection_id: Airbyte connection ID

        Returns:
            SyncJob with initial status
        """
        try:
            result = self.client.trigger_sync(connection_id)

            job = SyncJob(
                job_id=result["job_id"],
                connection_id=connection_id,
                status=SyncStatus(result.get("status", "pending")),
                start_time=datetime.now(),
            )

            self._active_jobs[job.job_id] = job
            self.logger.info(
                f"Triggered sync job",
                extra={
                    "job_id": job.job_id,
                    "connection_id": connection_id,
                },
            )

            return job

        except Exception as e:
            self.logger.error(f"Failed to trigger sync: {e}")
            raise

    def get_job_status(self, job_id: int) -> SyncJob:
        """
        Get current status of a sync job.

        Args:
            job_id: Job ID to check

        Returns:
            Updated SyncJob
        """
        try:
            result = self.client.get_job_status(job_id)

            # Update cached job if exists
            if job_id in self._active_jobs:
                job = self._active_jobs[job_id]
            else:
                job = SyncJob(
                    job_id=job_id,
                    connection_id=result.get("connection_id", ""),
                    status=SyncStatus.PENDING,
                )
                self._active_jobs[job_id] = job

            # Update status
            status_str = result.get("status", "pending")
            try:
                job.status = SyncStatus(status_str)
            except ValueError:
                job.status = SyncStatus.PENDING

            # Update timestamps
            if result.get("start_time"):
                if isinstance(result["start_time"], str):
                    job.start_time = datetime.fromisoformat(
                        result["start_time"].replace("Z", "+00:00")
                    )
                else:
                    job.start_time = result["start_time"]

            return job

        except Exception as e:
            self.logger.error(f"Failed to get job status: {e}")
            raise

    def sync_and_wait(
        self,
        connection_id: str,
        timeout: int = 3600,
        poll_interval: int = 10,
    ) -> SyncJob:
        """
        Trigger sync and wait for completion.

        Args:
            connection_id: Connection to sync
            timeout: Maximum wait time in seconds
            poll_interval: Seconds between status checks

        Returns:
            Completed SyncJob

        Raises:
            TimeoutError: If job doesn't complete within timeout
            RuntimeError: If job fails
        """
        job = self.trigger_sync(connection_id)
        start_time = time.time()

        while not job.is_complete:
            if time.time() - start_time > timeout:
                self.logger.error(f"Sync job {job.job_id} timed out")
                raise TimeoutError(
                    f"Sync job {job.job_id} did not complete within {timeout} seconds"
                )

            time.sleep(poll_interval)
            job = self.get_job_status(job.job_id)

            self.logger.debug(
                f"Job {job.job_id} status: {job.status.value}",
                extra={
                    "elapsed": time.time() - start_time,
                },
            )

        job.end_time = datetime.now()

        if job.status == SyncStatus.FAILED:
            raise RuntimeError(
                f"Sync job {job.job_id} failed: {job.error_message or 'Unknown error'}"
            )

        self.logger.info(
            f"Sync job completed",
            extra={
                "job_id": job.job_id,
                "status": job.status.value,
                "duration_seconds": job.duration_seconds,
            },
        )

        return job

    def sync_with_callback(
        self,
        connection_id: str,
        on_complete: Optional[Callable[[SyncJob], None]] = None,
        on_error: Optional[Callable[[SyncJob, Exception], None]] = None,
        on_progress: Optional[Callable[[SyncJob], None]] = None,
        poll_interval: int = 10,
        timeout: int = 3600,
    ) -> SyncJob:
        """
        Trigger sync with callbacks (non-blocking).

        Args:
            connection_id: Connection to sync
            on_complete: Called when job completes successfully
            on_error: Called when job fails
            on_progress: Called on each status poll
            poll_interval: Seconds between status checks
            timeout: Maximum wait time

        Returns:
            Initial SyncJob (callbacks fire asynchronously)
        """
        job = self.trigger_sync(connection_id)

        def _poll_thread():
            try:
                start_time = time.time()

                while not job.is_complete:
                    if time.time() - start_time > timeout:
                        if on_error:
                            on_error(job, TimeoutError("Sync timed out"))
                        return

                    time.sleep(poll_interval)
                    updated_job = self.get_job_status(job.job_id)

                    # Update the original job object
                    job.status = updated_job.status
                    job.bytes_synced = updated_job.bytes_synced
                    job.records_synced = updated_job.records_synced

                    if on_progress:
                        on_progress(job)

                job.end_time = datetime.now()

                if job.status == SyncStatus.SUCCEEDED and on_complete:
                    on_complete(job)
                elif job.status == SyncStatus.FAILED and on_error:
                    on_error(job, RuntimeError(job.error_message or "Sync failed"))

            except Exception as e:
                if on_error:
                    on_error(job, e)

        # Start polling in background thread
        thread = threading.Thread(target=_poll_thread, daemon=True)
        thread.start()

        return job

    def cancel_job(self, job_id: int) -> bool:
        """
        Cancel a running sync job.

        Args:
            job_id: Job ID to cancel

        Returns:
            True if cancelled successfully
        """
        result = self.client.cancel_job(job_id)

        if result and job_id in self._active_jobs:
            self._active_jobs[job_id].status = SyncStatus.CANCELLED
            self._active_jobs[job_id].end_time = datetime.now()

        return result

    def list_active_jobs(self) -> List[SyncJob]:
        """
        List all active (non-completed) jobs.

        Returns:
            List of active SyncJobs
        """
        return [j for j in self._active_jobs.values() if not j.is_complete]

    def list_recent_jobs(
        self,
        connection_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[SyncJob]:
        """
        List recent sync jobs.

        Args:
            connection_id: Filter by connection
            limit: Maximum results

        Returns:
            List of recent SyncJobs
        """
        try:
            results = self.client.list_jobs(
                connection_id=connection_id,
                limit=limit,
            )

            jobs = []
            for r in results:
                try:
                    status = SyncStatus(r.get("status", "pending"))
                except ValueError:
                    status = SyncStatus.PENDING

                job = SyncJob(
                    job_id=r["job_id"],
                    connection_id=r.get("connection_id", ""),
                    status=status,
                    job_type=r.get("job_type", "sync"),
                )
                jobs.append(job)

            return jobs

        except Exception as e:
            self.logger.error(f"Failed to list jobs: {e}")
            return []

    def bulk_sync(
        self,
        connection_ids: List[str],
        parallel: bool = False,
        timeout_per_job: int = 3600,
    ) -> Dict[str, SyncJob]:
        """
        Sync multiple connections.

        Args:
            connection_ids: List of connection IDs to sync
            parallel: Run syncs in parallel (default: sequential)
            timeout_per_job: Timeout per job in seconds

        Returns:
            Dict mapping connection_id to SyncJob result
        """
        results: Dict[str, SyncJob] = {}

        if parallel:
            threads = []
            for conn_id in connection_ids:

                def _sync_connection(cid: str):
                    try:
                        results[cid] = self.sync_and_wait(
                            cid, timeout=timeout_per_job
                        )
                    except Exception as e:
                        self.logger.error(f"Sync failed for {cid}: {e}")
                        results[cid] = SyncJob(
                            job_id=-1,
                            connection_id=cid,
                            status=SyncStatus.FAILED,
                            error_message=str(e),
                        )

                thread = threading.Thread(
                    target=_sync_connection, args=(conn_id,)
                )
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

        else:
            for conn_id in connection_ids:
                try:
                    results[conn_id] = self.sync_and_wait(
                        conn_id, timeout=timeout_per_job
                    )
                except Exception as e:
                    self.logger.error(f"Sync failed for {conn_id}: {e}")
                    results[conn_id] = SyncJob(
                        job_id=-1,
                        connection_id=conn_id,
                        status=SyncStatus.FAILED,
                        error_message=str(e),
                    )

        return results

    def get_sync_stats(
        self, connection_id: str, days: int = 7
    ) -> Dict[str, Any]:
        """
        Get sync statistics for a connection.

        Args:
            connection_id: Connection to analyze
            days: Number of days to look back

        Returns:
            Statistics dict with success rate, avg duration, etc.
        """
        jobs = self.list_recent_jobs(connection_id=connection_id, limit=100)

        if not jobs:
            return {
                "total_jobs": 0,
                "success_rate": 0.0,
                "avg_duration_seconds": 0.0,
            }

        succeeded = sum(1 for j in jobs if j.status == SyncStatus.SUCCEEDED)
        failed = sum(1 for j in jobs if j.status == SyncStatus.FAILED)
        total = len(jobs)

        durations = [
            j.duration_seconds for j in jobs if j.duration_seconds is not None
        ]
        avg_duration = sum(durations) / len(durations) if durations else 0

        return {
            "total_jobs": total,
            "succeeded": succeeded,
            "failed": failed,
            "success_rate": succeeded / total if total > 0 else 0.0,
            "avg_duration_seconds": avg_duration,
            "total_records_synced": sum(j.records_synced for j in jobs),
            "total_bytes_synced": sum(j.bytes_synced for j in jobs),
        }
