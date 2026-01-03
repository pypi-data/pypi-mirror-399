"""Enrichments resource for Trix SDK."""

from typing import Any, Dict, List, Optional

from ..protocols import AsyncClientProtocol, SyncClientProtocol
from ..types import (
    Enrichment,
    EnrichmentResult,
    EnrichmentStatus,
)
from ..utils.security import validate_id


class EnrichmentsResource:
    """Resource for managing memory enrichments.

    Enrichments are automatic processing operations that add value to memories,
    such as entity extraction, summarization, sentiment analysis, etc.
    """

    def __init__(self, client: SyncClientProtocol) -> None:
        """Initialize enrichments resource with client."""
        self._client = client

    def list(
        self,
        memory_id: str,
        status: Optional[EnrichmentStatus] = None,
    ) -> List[Enrichment]:
        """
        List all enrichments for a memory.

        Args:
            memory_id: Memory ID
            status: Optional filter by status

        Returns:
            List of enrichments

        Example:
            >>> enrichments = client.enrichments.list("mem_123")
            >>> for e in enrichments:
            ...     print(f"{e.type}: {e.status}")
        """
        validate_id(memory_id, "memory")
        params: Dict[str, Any] = {}
        if status:
            params["status"] = status.value

        response = self._client._request("GET", f"/memories/{memory_id}/enrichments", params=params)
        return [Enrichment.model_validate(e) for e in response.get("data", [])]

    def get(self, memory_id: str, enrichment_type: str) -> Enrichment:
        """
        Get a specific enrichment by type.

        Args:
            memory_id: Memory ID
            enrichment_type: Enrichment type (e.g., 'entities', 'summary')

        Returns:
            Enrichment object

        Example:
            >>> entities = client.enrichments.get("mem_123", "entities")
            >>> print(entities.data)
        """
        validate_id(memory_id, "memory")
        if not enrichment_type or not isinstance(enrichment_type, str):
            raise ValueError("Enrichment type is required")

        response = self._client._request(
            "GET", f"/memories/{memory_id}/enrichments/{enrichment_type}"
        )
        return Enrichment.model_validate(response)

    def trigger(
        self,
        memory_id: str,
        types: Optional[List[str]] = None,
        priority: Optional[str] = None,
        force: bool = False,
    ) -> EnrichmentResult:
        """
        Trigger enrichment processing for a memory.

        Args:
            memory_id: Memory ID
            types: Optional list of enrichment types to trigger
            priority: Priority level ('low', 'normal', 'high')
            force: Force re-processing even if already completed

        Returns:
            Enrichment result with job info

        Example:
            >>> result = client.enrichments.trigger(
            ...     "mem_123",
            ...     types=["entities", "summary"],
            ...     priority="high"
            ... )
        """
        validate_id(memory_id, "memory")
        data: Dict[str, Any] = {}
        if types:
            data["types"] = types
        if priority:
            data["priority"] = priority
        if force:
            data["force"] = force

        response = self._client._request("POST", f"/memories/{memory_id}/enrichments", json=data)
        return EnrichmentResult.model_validate(response)

    def retry(
        self,
        memory_id: str,
        types: Optional[List[str]] = None,
    ) -> EnrichmentResult:
        """
        Retry failed enrichments for a memory.

        Args:
            memory_id: Memory ID
            types: Optional specific types to retry

        Returns:
            Enrichment result with job info

        Example:
            >>> result = client.enrichments.retry("mem_123")
        """
        validate_id(memory_id, "memory")
        data: Dict[str, Any] = {}
        if types:
            data["types"] = types

        response = self._client._request(
            "POST", f"/memories/{memory_id}/enrichments/retry", json=data
        )
        return EnrichmentResult.model_validate(response)

    def trigger_full(
        self,
        memory_id: str,
        priority: Optional[str] = None,
    ) -> EnrichmentResult:
        """
        Trigger full enrichment pipeline for a memory.

        This runs all enrichment types, regardless of previous status.
        Useful for reprocessing after content updates.

        Args:
            memory_id: Memory ID
            priority: Priority level ('low', 'normal', 'high')

        Returns:
            Enrichment result with job info

        Example:
            >>> result = client.enrichments.trigger_full("mem_123", priority="high")
        """
        validate_id(memory_id, "memory")
        data: Dict[str, Any] = {}
        if priority:
            data["priority"] = priority

        response = self._client._request(
            "POST", f"/memories/{memory_id}/enrichments/full", json=data
        )
        return EnrichmentResult.model_validate(response)


class AsyncEnrichmentsResource:
    """Async resource for managing memory enrichments."""

    def __init__(self, client: AsyncClientProtocol) -> None:
        """Initialize async enrichments resource with client."""
        self._client = client

    async def list(
        self,
        memory_id: str,
        status: Optional[EnrichmentStatus] = None,
    ) -> List[Enrichment]:
        """List all enrichments for a memory (async)."""
        validate_id(memory_id, "memory")
        params: Dict[str, Any] = {}
        if status:
            params["status"] = status.value

        response = await self._client._request(
            "GET", f"/memories/{memory_id}/enrichments", params=params
        )
        return [Enrichment.model_validate(e) for e in response.get("data", [])]

    async def get(self, memory_id: str, enrichment_type: str) -> Enrichment:
        """Get a specific enrichment by type (async)."""
        validate_id(memory_id, "memory")
        if not enrichment_type or not isinstance(enrichment_type, str):
            raise ValueError("Enrichment type is required")

        response = await self._client._request(
            "GET", f"/memories/{memory_id}/enrichments/{enrichment_type}"
        )
        return Enrichment.model_validate(response)

    async def trigger(
        self,
        memory_id: str,
        types: Optional[List[str]] = None,
        priority: Optional[str] = None,
        force: bool = False,
    ) -> EnrichmentResult:
        """Trigger enrichment processing for a memory (async)."""
        validate_id(memory_id, "memory")
        data: Dict[str, Any] = {}
        if types:
            data["types"] = types
        if priority:
            data["priority"] = priority
        if force:
            data["force"] = force

        response = await self._client._request(
            "POST", f"/memories/{memory_id}/enrichments", json=data
        )
        return EnrichmentResult.model_validate(response)

    async def retry(
        self,
        memory_id: str,
        types: Optional[List[str]] = None,
    ) -> EnrichmentResult:
        """Retry failed enrichments for a memory (async)."""
        validate_id(memory_id, "memory")
        data: Dict[str, Any] = {}
        if types:
            data["types"] = types

        response = await self._client._request(
            "POST", f"/memories/{memory_id}/enrichments/retry", json=data
        )
        return EnrichmentResult.model_validate(response)

    async def trigger_full(
        self,
        memory_id: str,
        priority: Optional[str] = None,
    ) -> EnrichmentResult:
        """Trigger full enrichment pipeline for a memory (async)."""
        validate_id(memory_id, "memory")
        data: Dict[str, Any] = {}
        if priority:
            data["priority"] = priority

        response = await self._client._request(
            "POST", f"/memories/{memory_id}/enrichments/full", json=data
        )
        return EnrichmentResult.model_validate(response)
