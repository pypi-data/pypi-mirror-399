"""Facts resource for Trix SDK - Knowledge Graph Triples."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .base import BaseAsyncResource, BaseSyncResource, validate_bulk_array
from ..types import (
    Fact,
    FactCreate,
    FactUpdate,
    FactList,
    FactQueryResult,
    FactExtractionResult,
    FactVerificationResult,
    FactSource,
    FactNodeType,
)
from ..utils.security import validate_id


def _build_fact_params(
    subject: Optional[str] = None,
    predicate: Optional[str] = None,
    obj: Optional[str] = None,
    min_confidence: Optional[float] = None,
    space_id: Optional[str] = None,
    limit: Optional[int] = None,
    page: Optional[int] = None,
    offset: Optional[int] = None,
) -> Dict[str, Any]:
    """Build query parameters for fact listing."""
    params: Dict[str, Any] = {}
    if subject is not None:
        params["subject"] = subject
    if predicate is not None:
        params["predicate"] = predicate
    if obj is not None:
        params["object"] = obj
    if min_confidence is not None:
        params["minConfidence"] = min_confidence
    if space_id is not None:
        params["spaceId"] = space_id
    if limit is not None:
        params["limit"] = limit
    if page is not None:
        params["page"] = page
    if offset is not None:
        params["offset"] = offset
    return params


class FactsResource(BaseSyncResource):
    """Resource for managing knowledge graph facts.

    Facts represent structured knowledge in Subject-Predicate-Object format,
    enabling powerful reasoning and querying over your knowledge base.

    Example:
        >>> # Create a fact
        >>> fact = client.facts.create(
        ...     subject="Albert Einstein",
        ...     predicate="was_born_in",
        ...     object="Ulm, Germany",
        ...     confidence=0.95
        ... )
        >>>
        >>> # Query facts
        >>> results = client.facts.query("Where was Einstein born?")
    """

    def create(
        self,
        subject: str,
        predicate: str,
        obj: str,
        confidence: float = 1.0,
        subject_type: Optional[FactNodeType] = None,
        object_type: Optional[FactNodeType] = None,
        source: Optional[FactSource] = None,
        valid_from: Optional[Union[str, datetime]] = None,
        valid_to: Optional[Union[str, datetime]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        space_id: Optional[str] = None,
    ) -> Fact:
        """Create a new fact.

        Args:
            subject: Subject of the triple (who/what)
            predicate: Predicate/relationship (verb/relation)
            obj: Object of the triple (whom/what)
            confidence: Confidence score (0.0-1.0)
            subject_type: Type of subject (entity, text, memory)
            object_type: Type of object (entity, text, memory)
            source: Source attribution for the fact
            valid_from: Start of temporal validity (ISO datetime)
            valid_to: End of temporal validity (ISO datetime)
            metadata: Additional metadata
            space_id: Space to create fact in

        Returns:
            Created fact object

        Example:
            >>> fact = client.facts.create(
            ...     subject="Trix",
            ...     predicate="is_a",
            ...     obj="memory database",
            ...     confidence=1.0
            ... )
        """
        data = FactCreate(
            subject=subject,
            predicate=predicate,
            object=obj,
            confidence=confidence,
            subject_type=subject_type,
            object_type=object_type,
            source=source,
            valid_from=valid_from,  # type: ignore[arg-type]
            valid_to=valid_to,  # type: ignore[arg-type]
            metadata=metadata,
            space_id=space_id,
        )
        response = self._request("POST", "/facts", json=data.model_dump(exclude_none=True))
        return Fact.model_validate(response)

    def get(self, id: str) -> Fact:
        """Get a fact by ID.

        Args:
            id: Fact ID

        Returns:
            Fact object

        Raises:
            ValidationError: If ID format is invalid
            NotFoundError: If fact doesn't exist
        """
        validate_id(id, "fact")
        response = self._request("GET", f"/facts/{id}")
        return Fact.model_validate(response)

    def list(
        self,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        obj: Optional[str] = None,
        min_confidence: Optional[float] = None,
        space_id: Optional[str] = None,
        limit: Optional[int] = None,
        page: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> FactList:
        """List facts with optional filters.

        Args:
            subject: Filter by subject
            predicate: Filter by predicate
            obj: Filter by object
            min_confidence: Minimum confidence threshold
            space_id: Filter by space
            limit: Maximum results to return
            page: Page number
            offset: Result offset

        Returns:
            Paginated list of facts
        """
        params = _build_fact_params(
            subject=subject,
            predicate=predicate,
            obj=obj,
            min_confidence=min_confidence,
            space_id=space_id,
            limit=limit,
            page=page,
            offset=offset,
        )
        response = self._request("GET", "/facts", params=params if params else None)
        return FactList.model_validate(response)

    def update(
        self,
        id: str,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        obj: Optional[str] = None,
        confidence: Optional[float] = None,
        valid_from: Optional[Union[str, datetime]] = None,
        valid_to: Optional[Union[str, datetime]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Fact:
        """Update a fact.

        Args:
            id: Fact ID
            subject: New subject
            predicate: New predicate
            obj: New object
            confidence: New confidence score
            valid_from: New temporal validity start
            valid_to: New temporal validity end
            metadata: New metadata

        Returns:
            Updated fact object
        """
        validate_id(id, "fact")
        data = FactUpdate(
            subject=subject,
            predicate=predicate,
            object=obj,
            confidence=confidence,
            valid_from=valid_from,  # type: ignore[arg-type]
            valid_to=valid_to,  # type: ignore[arg-type]
            metadata=metadata,
        )
        response = self._request("PATCH", f"/facts/{id}", json=data.model_dump(exclude_none=True))
        return Fact.model_validate(response)

    def delete(self, id: str) -> None:
        """Delete a fact.

        Args:
            id: Fact ID
        """
        validate_id(id, "fact")
        self._request("DELETE", f"/facts/{id}")

    def query(
        self,
        query: str,
        limit: Optional[int] = None,
        min_confidence: Optional[float] = None,
        space_id: Optional[str] = None,
    ) -> FactQueryResult:
        """Query facts using natural language.

        Args:
            query: Natural language query
            limit: Maximum results
            min_confidence: Minimum confidence threshold
            space_id: Space to search in

        Returns:
            Query results with scored facts
        """
        body: Dict[str, Any] = {"query": query}
        if limit is not None:
            body["limit"] = limit
        if min_confidence is not None:
            body["minConfidence"] = min_confidence
        if space_id is not None:
            body["spaceId"] = space_id
        response = self._request("POST", "/facts/query", json=body)
        return FactQueryResult.model_validate(response)

    def find_by_subject(
        self,
        subject: str,
        limit: Optional[int] = None,
    ) -> FactList:
        """Find facts by subject."""
        return self.list(subject=subject, limit=limit)

    def find_by_predicate(
        self,
        predicate: str,
        limit: Optional[int] = None,
    ) -> FactList:
        """Find facts by predicate."""
        return self.list(predicate=predicate, limit=limit)

    def find_by_object(
        self,
        obj: str,
        limit: Optional[int] = None,
    ) -> FactList:
        """Find facts by object."""
        return self.list(obj=obj, limit=limit)

    def bulk_create(self, facts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create multiple facts in bulk.

        Args:
            facts: List of fact dictionaries

        Returns:
            Bulk operation result

        Raises:
            ValueError: If array is empty or exceeds limit
        """
        validate_bulk_array(facts, "bulk_create")
        response = self._request("POST", "/facts/bulk", json={"facts": facts})
        return dict(response)

    def bulk_delete(self, ids: List[str]) -> Dict[str, Any]:
        """Delete multiple facts in bulk.

        Args:
            ids: List of fact IDs to delete

        Returns:
            Bulk operation result
        """
        validate_bulk_array(ids, "bulk_delete")
        response = self._request("DELETE", "/facts/bulk", json={"ids": ids})
        return dict(response)

    def extract(
        self,
        memory_id: str,
        save: bool = False,
    ) -> FactExtractionResult:
        """Extract facts from a memory.

        Args:
            memory_id: Memory ID to extract from
            save: Whether to save extracted facts

        Returns:
            Extracted facts
        """
        validate_id(memory_id, "memory")
        body: Dict[str, Any] = {}
        if save:
            body["save"] = save
        response = self._request("POST", f"/memories/{memory_id}/extract-facts", json=body)
        return FactExtractionResult.model_validate(response)

    def verify(
        self,
        fact_id: str,
        space_id: Optional[str] = None,
    ) -> FactVerificationResult:
        """Verify a fact against the knowledge base.

        Args:
            fact_id: Fact ID to verify
            space_id: Space to search in

        Returns:
            Verification result
        """
        validate_id(fact_id, "fact")
        body: Dict[str, Any] = {}
        if space_id is not None:
            body["spaceId"] = space_id
        response = self._request("POST", f"/facts/{fact_id}/verify", json=body)
        return FactVerificationResult.model_validate(response)


class AsyncFactsResource(BaseAsyncResource):
    """Async resource for managing knowledge graph facts.

    Facts represent structured knowledge in Subject-Predicate-Object format.
    """

    async def create(
        self,
        subject: str,
        predicate: str,
        obj: str,
        confidence: float = 1.0,
        subject_type: Optional[FactNodeType] = None,
        object_type: Optional[FactNodeType] = None,
        source: Optional[FactSource] = None,
        valid_from: Optional[Union[str, datetime]] = None,
        valid_to: Optional[Union[str, datetime]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        space_id: Optional[str] = None,
    ) -> Fact:
        """Create a new fact (async)."""
        data = FactCreate(
            subject=subject,
            predicate=predicate,
            object=obj,
            confidence=confidence,
            subject_type=subject_type,
            object_type=object_type,
            source=source,
            valid_from=valid_from,  # type: ignore[arg-type]
            valid_to=valid_to,  # type: ignore[arg-type]
            metadata=metadata,
            space_id=space_id,
        )
        response = await self._request("POST", "/facts", json=data.model_dump(exclude_none=True))
        return Fact.model_validate(response)

    async def get(self, id: str) -> Fact:
        """Get a fact by ID (async)."""
        validate_id(id, "fact")
        response = await self._request("GET", f"/facts/{id}")
        return Fact.model_validate(response)

    async def list(
        self,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        obj: Optional[str] = None,
        min_confidence: Optional[float] = None,
        space_id: Optional[str] = None,
        limit: Optional[int] = None,
        page: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> FactList:
        """List facts with optional filters (async)."""
        params = _build_fact_params(
            subject=subject,
            predicate=predicate,
            obj=obj,
            min_confidence=min_confidence,
            space_id=space_id,
            limit=limit,
            page=page,
            offset=offset,
        )
        response = await self._request("GET", "/facts", params=params if params else None)
        return FactList.model_validate(response)

    async def update(
        self,
        id: str,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        obj: Optional[str] = None,
        confidence: Optional[float] = None,
        valid_from: Optional[Union[str, datetime]] = None,
        valid_to: Optional[Union[str, datetime]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Fact:
        """Update a fact (async)."""
        validate_id(id, "fact")
        data = FactUpdate(
            subject=subject,
            predicate=predicate,
            object=obj,
            confidence=confidence,
            valid_from=valid_from,  # type: ignore[arg-type]
            valid_to=valid_to,  # type: ignore[arg-type]
            metadata=metadata,
        )
        response = await self._request(
            "PATCH", f"/facts/{id}", json=data.model_dump(exclude_none=True)
        )
        return Fact.model_validate(response)

    async def delete(self, id: str) -> None:
        """Delete a fact (async)."""
        validate_id(id, "fact")
        await self._request("DELETE", f"/facts/{id}")

    async def query(
        self,
        query: str,
        limit: Optional[int] = None,
        min_confidence: Optional[float] = None,
        space_id: Optional[str] = None,
    ) -> FactQueryResult:
        """Query facts using natural language (async)."""
        body: Dict[str, Any] = {"query": query}
        if limit is not None:
            body["limit"] = limit
        if min_confidence is not None:
            body["minConfidence"] = min_confidence
        if space_id is not None:
            body["spaceId"] = space_id
        response = await self._request("POST", "/facts/query", json=body)
        return FactQueryResult.model_validate(response)

    async def find_by_subject(
        self,
        subject: str,
        limit: Optional[int] = None,
    ) -> FactList:
        """Find facts by subject (async)."""
        return await self.list(subject=subject, limit=limit)

    async def find_by_predicate(
        self,
        predicate: str,
        limit: Optional[int] = None,
    ) -> FactList:
        """Find facts by predicate (async)."""
        return await self.list(predicate=predicate, limit=limit)

    async def find_by_object(
        self,
        obj: str,
        limit: Optional[int] = None,
    ) -> FactList:
        """Find facts by object (async)."""
        return await self.list(obj=obj, limit=limit)

    async def bulk_create(self, facts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create multiple facts in bulk (async)."""
        validate_bulk_array(facts, "bulk_create")
        response = await self._request("POST", "/facts/bulk", json={"facts": facts})
        return dict(response)

    async def bulk_delete(self, ids: List[str]) -> Dict[str, Any]:
        """Delete multiple facts in bulk (async)."""
        validate_bulk_array(ids, "bulk_delete")
        response = await self._request("DELETE", "/facts/bulk", json={"ids": ids})
        return dict(response)

    async def extract(
        self,
        memory_id: str,
        save: bool = False,
    ) -> FactExtractionResult:
        """Extract facts from a memory (async)."""
        validate_id(memory_id, "memory")
        body: Dict[str, Any] = {}
        if save:
            body["save"] = save
        response = await self._request("POST", f"/memories/{memory_id}/extract-facts", json=body)
        return FactExtractionResult.model_validate(response)

    async def verify(
        self,
        fact_id: str,
        space_id: Optional[str] = None,
    ) -> FactVerificationResult:
        """Verify a fact against the knowledge base (async)."""
        validate_id(fact_id, "fact")
        body: Dict[str, Any] = {}
        if space_id is not None:
            body["spaceId"] = space_id
        response = await self._request("POST", f"/facts/{fact_id}/verify", json=body)
        return FactVerificationResult.model_validate(response)
