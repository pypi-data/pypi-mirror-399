"""Feedback resource for Trix SDK."""

from typing import Any, Dict, List, Optional

from .base import BaseAsyncResource, BaseSyncResource, validate_ids
from ..types import FeedbackResponse, FeedbackResult, FeedbackSubmit
from ..utils.security import validate_id


def _build_batch_data(
    useful_ids: Optional[List[str]],
    not_useful_ids: Optional[List[str]],
    source_memory_id: Optional[str],
) -> Dict[str, Any]:
    """Build batch feedback request data with validation.

    Args:
        useful_ids: List of useful memory IDs
        not_useful_ids: List of not useful memory IDs
        source_memory_id: Optional source memory

    Returns:
        Request data dict with validated IDs
    """
    validate_ids(useful_ids, "memory")
    validate_ids(not_useful_ids, "memory")
    if source_memory_id:
        validate_id(source_memory_id, "source memory")

    data: Dict[str, Any] = {}
    if useful_ids:
        data["useful_ids"] = useful_ids
    if not_useful_ids:
        data["not_useful_ids"] = not_useful_ids
    if source_memory_id:
        data["source_memory_id"] = source_memory_id
    return data


def _build_quick_data(
    memory_id: str, useful: bool, source_memory_id: Optional[str]
) -> Dict[str, Any]:
    """Build quick feedback request data with validation.

    Args:
        memory_id: Memory ID to provide feedback on
        useful: Whether the memory was useful
        source_memory_id: Optional source memory

    Returns:
        Request data dict with validated IDs
    """
    validate_id(memory_id, "memory")
    if source_memory_id:
        validate_id(source_memory_id, "source memory")

    data: Dict[str, Any] = {"memory_id": memory_id, "useful": useful}
    if source_memory_id:
        data["source_memory_id"] = source_memory_id
    return data


class FeedbackResource(BaseSyncResource):
    """Resource for submitting feedback to improve search results.

    Feedback helps the system learn which memories are relevant for specific
    queries, improving future search results.

    Example:
        >>> # Submit quick feedback
        >>> response = client.feedback.quick(
        ...     memory_id="mem_123",
        ...     useful=True
        ... )
        >>>
        >>> # Submit batch feedback
        >>> response = client.feedback.batch(
        ...     useful_ids=["mem_123", "mem_456"],
        ...     not_useful_ids=["mem_789"]
        ... )
    """

    def submit(
        self,
        query_context: str,
        results: List[FeedbackResult],
        boost_amount: Optional[float] = None,
        create_relationships: bool = True,
    ) -> FeedbackResponse:
        """Submit detailed feedback on search results.

        Args:
            query_context: Original search query or context
            results: List of results with scores
            boost_amount: Amount to boost relevant memories
            create_relationships: Whether to create relationships

        Returns:
            Feedback response

        Example:
            >>> response = client.feedback.submit(
            ...     query_context="machine learning",
            ...     results=[
            ...         FeedbackResult(memory_id="mem_123", score=0.9, rank=1),
            ...         FeedbackResult(memory_id="mem_456", score=0.8, rank=2),
            ...     ],
            ...     boost_amount=0.5
            ... )
        """
        data = FeedbackSubmit(
            query_context=query_context,
            results=results,
            boost_amount=boost_amount,
            create_relationships=create_relationships,
        )
        response = self._request(
            "POST", "/feedback/submit", json=data.model_dump(exclude_none=True)
        )
        return FeedbackResponse.model_validate(response)

    def quick(
        self, memory_id: str, useful: bool, source_memory_id: Optional[str] = None
    ) -> FeedbackResponse:
        """Submit quick feedback on a single memory.

        Args:
            memory_id: Memory ID to provide feedback on
            useful: Whether the memory was useful
            source_memory_id: Optional source memory that led to this

        Returns:
            Feedback response

        Example:
            >>> response = client.feedback.quick(
            ...     memory_id="mem_123",
            ...     useful=True,
            ...     source_memory_id="mem_456"
            ... )
        """
        data = _build_quick_data(memory_id, useful, source_memory_id)
        response = self._request("POST", "/feedback/quick", json=data)
        return FeedbackResponse.model_validate(response)

    def batch(
        self,
        useful_ids: Optional[List[str]] = None,
        not_useful_ids: Optional[List[str]] = None,
        source_memory_id: Optional[str] = None,
    ) -> FeedbackResponse:
        """Submit batch feedback on multiple memories.

        Args:
            useful_ids: List of useful memory IDs
            not_useful_ids: List of not useful memory IDs
            source_memory_id: Optional source memory

        Returns:
            Feedback response

        Example:
            >>> response = client.feedback.batch(
            ...     useful_ids=["mem_123", "mem_456"],
            ...     not_useful_ids=["mem_789"]
            ... )
        """
        data = _build_batch_data(useful_ids, not_useful_ids, source_memory_id)
        response = self._request("POST", "/feedback/batch", json=data)
        return FeedbackResponse.model_validate(response)


class AsyncFeedbackResource(BaseAsyncResource):
    """Async resource for submitting feedback to improve search results.

    Example:
        >>> response = await client.feedback.quick(
        ...     memory_id="mem_123",
        ...     useful=True
        ... )
    """

    async def submit(
        self,
        query_context: str,
        results: List[FeedbackResult],
        boost_amount: Optional[float] = None,
        create_relationships: bool = True,
    ) -> FeedbackResponse:
        """Submit detailed feedback on search results (async).

        Args:
            query_context: Original search query or context
            results: List of results with scores
            boost_amount: Amount to boost relevant memories
            create_relationships: Whether to create relationships

        Returns:
            Feedback response
        """
        data = FeedbackSubmit(
            query_context=query_context,
            results=results,
            boost_amount=boost_amount,
            create_relationships=create_relationships,
        )
        response = await self._request(
            "POST", "/feedback/submit", json=data.model_dump(exclude_none=True)
        )
        return FeedbackResponse.model_validate(response)

    async def quick(
        self, memory_id: str, useful: bool, source_memory_id: Optional[str] = None
    ) -> FeedbackResponse:
        """Submit quick feedback on a single memory (async).

        Args:
            memory_id: Memory ID to provide feedback on
            useful: Whether the memory was useful
            source_memory_id: Optional source memory

        Returns:
            Feedback response
        """
        data = _build_quick_data(memory_id, useful, source_memory_id)
        response = await self._request("POST", "/feedback/quick", json=data)
        return FeedbackResponse.model_validate(response)

    async def batch(
        self,
        useful_ids: Optional[List[str]] = None,
        not_useful_ids: Optional[List[str]] = None,
        source_memory_id: Optional[str] = None,
    ) -> FeedbackResponse:
        """Submit batch feedback on multiple memories (async).

        Args:
            useful_ids: List of useful memory IDs
            not_useful_ids: List of not useful memory IDs
            source_memory_id: Optional source memory

        Returns:
            Feedback response
        """
        data = _build_batch_data(useful_ids, not_useful_ids, source_memory_id)
        response = await self._request("POST", "/feedback/batch", json=data)
        return FeedbackResponse.model_validate(response)
