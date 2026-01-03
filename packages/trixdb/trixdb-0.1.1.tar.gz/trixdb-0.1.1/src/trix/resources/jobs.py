"""Jobs resource for Trix SDK."""

from typing import Any, Dict, List, Optional

from .base import BaseAsyncResource, BaseSyncResource
from ..types import Job, JobList, JobStats, JobStatus
from ..utils.security import validate_id


def _build_list_params(
    queue: Optional[str], status: Optional[JobStatus], limit: int
) -> Dict[str, Any]:
    """Build list params dict."""
    params: Dict[str, Any] = {"limit": limit}
    if queue:
        params["queue"] = queue
    if status:
        params["status"] = status.value
    return params


def _build_clean_params(grace: int, status: Optional[JobStatus]) -> Dict[str, Any]:
    """Build clean params dict."""
    params: Dict[str, Any] = {"grace": grace}
    if status:
        params["status"] = status.value
    return params


def _validate_queue_and_job(queue: str, job_id: str) -> None:
    """Validate queue and job ID."""
    validate_id(queue, "queue")
    validate_id(job_id, "job")


class JobsResource(BaseSyncResource):
    """Resource for managing background jobs.

    Jobs represent asynchronous operations like transcription, embedding
    generation, and other batch processing tasks.

    Example:
        >>> # Get job statistics
        >>> stats = client.jobs.get_stats()
        >>> for queue_stats in stats:
        ...     print(f"{queue_stats.queue}: {queue_stats.waiting} waiting")
        >>>
        >>> # List failed jobs
        >>> jobs = client.jobs.list(status=JobStatus.FAILED)
    """

    def get_stats(self) -> List[JobStats]:
        """Get statistics for all job queues.

        Returns:
            List of job statistics by queue

        Example:
            >>> stats = client.jobs.get_stats()
            >>> for queue_stats in stats:
            ...     print(f"{queue_stats.queue}: {queue_stats.waiting} waiting")
        """
        response = self._request("GET", "/jobs/stats")
        return [JobStats.model_validate(s) for s in response.get("queues", [])]

    def get(self, queue: str, id: str) -> Job:
        """Get a specific job.

        Args:
            queue: Queue name
            id: Job ID

        Returns:
            Job object

        Example:
            >>> job = client.jobs.get("transcription", "job_123")
        """
        _validate_queue_and_job(queue, id)
        response = self._request("GET", f"/jobs/{queue}/{id}")
        return Job.model_validate(response)

    def list(
        self,
        queue: Optional[str] = None,
        status: Optional[JobStatus] = None,
        limit: int = 100,
    ) -> JobList:
        """List jobs with optional filtering.

        Args:
            queue: Filter by queue name
            status: Filter by job status
            limit: Maximum number of jobs

        Returns:
            List of jobs

        Example:
            >>> jobs = client.jobs.list(
            ...     queue="embedding",
            ...     status=JobStatus.FAILED
            ... )
        """
        params = _build_list_params(queue, status, limit)
        response = self._request("GET", "/jobs", params=params)
        return JobList.model_validate(response)

    def retry(self, queue: str, id: str) -> Job:
        """Retry a failed job.

        Args:
            queue: Queue name
            id: Job ID

        Returns:
            Updated job object

        Example:
            >>> job = client.jobs.retry("transcription", "job_123")
        """
        _validate_queue_and_job(queue, id)
        response = self._request("POST", f"/jobs/{queue}/{id}/retry")
        return Job.model_validate(response)

    def remove(self, queue: str, id: str) -> None:
        """Remove a job from the queue.

        Args:
            queue: Queue name
            id: Job ID

        Example:
            >>> client.jobs.remove("embedding", "job_123")
        """
        _validate_queue_and_job(queue, id)
        self._request("DELETE", f"/jobs/{queue}/{id}")

    def clean(
        self,
        queue: str,
        grace: int = 3600,
        status: Optional[JobStatus] = None,
    ) -> Dict[str, Any]:
        """Clean old jobs from a queue.

        Args:
            queue: Queue name
            grace: Grace period in seconds (jobs older than this are removed)
            status: Optional status filter

        Returns:
            Cleanup result with count of removed jobs

        Example:
            >>> result = client.jobs.clean(
            ...     queue="embedding",
            ...     grace=7200,
            ...     status=JobStatus.COMPLETED
            ... )
        """
        validate_id(queue, "queue")
        params = _build_clean_params(grace, status)
        response = self._request("POST", f"/jobs/{queue}/clean", params=params)
        return dict(response)


class AsyncJobsResource(BaseAsyncResource):
    """Async resource for managing background jobs.

    Example:
        >>> stats = await client.jobs.get_stats()
        >>> jobs = await client.jobs.list(status=JobStatus.FAILED)
    """

    async def get_stats(self) -> List[JobStats]:
        """Get statistics for all job queues (async).

        Returns:
            List of job statistics by queue
        """
        response = await self._request("GET", "/jobs/stats")
        return [JobStats.model_validate(s) for s in response.get("queues", [])]

    async def get(self, queue: str, id: str) -> Job:
        """Get a specific job (async).

        Args:
            queue: Queue name
            id: Job ID

        Returns:
            Job object
        """
        _validate_queue_and_job(queue, id)
        response = await self._request("GET", f"/jobs/{queue}/{id}")
        return Job.model_validate(response)

    async def list(
        self,
        queue: Optional[str] = None,
        status: Optional[JobStatus] = None,
        limit: int = 100,
    ) -> JobList:
        """List jobs with optional filtering (async).

        Args:
            queue: Filter by queue name
            status: Filter by job status
            limit: Maximum number of jobs

        Returns:
            List of jobs
        """
        params = _build_list_params(queue, status, limit)
        response = await self._request("GET", "/jobs", params=params)
        return JobList.model_validate(response)

    async def retry(self, queue: str, id: str) -> Job:
        """Retry a failed job (async).

        Args:
            queue: Queue name
            id: Job ID

        Returns:
            Updated job object
        """
        _validate_queue_and_job(queue, id)
        response = await self._request("POST", f"/jobs/{queue}/{id}/retry")
        return Job.model_validate(response)

    async def remove(self, queue: str, id: str) -> None:
        """Remove a job from the queue (async).

        Args:
            queue: Queue name
            id: Job ID
        """
        _validate_queue_and_job(queue, id)
        await self._request("DELETE", f"/jobs/{queue}/{id}")

    async def clean(
        self,
        queue: str,
        grace: int = 3600,
        status: Optional[JobStatus] = None,
    ) -> Dict[str, Any]:
        """Clean old jobs from a queue (async).

        Args:
            queue: Queue name
            grace: Grace period in seconds
            status: Optional status filter

        Returns:
            Cleanup result with count of removed jobs
        """
        validate_id(queue, "queue")
        params = _build_clean_params(grace, status)
        response = await self._request("POST", f"/jobs/{queue}/clean", params=params)
        return dict(response)
