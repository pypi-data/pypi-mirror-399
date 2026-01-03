"""Relationships resource for Trix SDK."""

from typing import Any, Dict, List, Optional

from ..protocols import AsyncClientProtocol, SyncClientProtocol
from ..types import (
    RelatedMemoriesResult,
    ReinforceGroupResult,
    Relationship,
    RelationshipCreate,
    RelationshipList,
    RelationshipType,
    RelationshipTypeInfo,
    RelationshipUpdate,
)
from ..utils.security import validate_id


class RelationshipsResource:
    """Resource for managing relationships between memories."""

    def __init__(self, client: SyncClientProtocol) -> None:
        """Initialize relationships resource with client."""
        self._client = client

    def create(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType,
        description: Optional[str] = None,
        weight: float = 1.0,
        bidirectional: bool = False,
    ) -> Relationship:
        """
        Create a relationship between two memories.

        Args:
            source_id: Source memory ID
            target_id: Target memory ID
            relationship_type: Type of relationship
            description: Optional description
            weight: Relationship weight (default 1.0)
            bidirectional: Whether relationship is bidirectional

        Returns:
            Created relationship object

        Example:
            >>> rel = client.relationships.create(
            ...     source_id="mem_123",
            ...     target_id="mem_456",
            ...     relationship_type=RelationshipType.RELATED_TO
            ... )
        """
        validate_id(source_id, "source memory")
        validate_id(target_id, "target memory")
        data = RelationshipCreate(
            relationship_type=relationship_type,
            description=description,
            weight=weight,
            bidirectional=bidirectional,
        )
        response = self._client._request(
            "POST",
            f"/relationships/{source_id}/create/{target_id}",
            json=data.model_dump(exclude_none=True),
        )
        return Relationship.model_validate(response)

    def get_incoming(self, memory_id: str) -> RelationshipList:
        """
        Get all incoming relationships for a memory.

        Args:
            memory_id: Memory ID

        Returns:
            List of incoming relationships

        Example:
            >>> incoming = client.relationships.get_incoming("mem_123")
        """
        validate_id(memory_id, "memory")
        response = self._client._request("GET", f"/relationships/{memory_id}/incoming")
        return RelationshipList.model_validate(response)

    def get_outgoing(self, memory_id: str) -> RelationshipList:
        """
        Get all outgoing relationships for a memory.

        Args:
            memory_id: Memory ID

        Returns:
            List of outgoing relationships

        Example:
            >>> outgoing = client.relationships.get_outgoing("mem_123")
        """
        validate_id(memory_id, "memory")
        response = self._client._request("GET", f"/relationships/{memory_id}/outgoing")
        return RelationshipList.model_validate(response)

    def update(
        self,
        relationship_id: str,
        weight: Optional[float] = None,
        description: Optional[str] = None,
    ) -> Relationship:
        """
        Update a relationship.

        Args:
            relationship_id: Relationship ID
            weight: New weight value
            description: New description

        Returns:
            Updated relationship object

        Example:
            >>> rel = client.relationships.update(
            ...     "rel_123",
            ...     weight=2.0,
            ...     description="Stronger connection"
            ... )
        """
        validate_id(relationship_id, "relationship")
        data = RelationshipUpdate(weight=weight, description=description)
        response = self._client._request(
            "PATCH", f"/relationships/{relationship_id}", json=data.model_dump(exclude_none=True)
        )
        return Relationship.model_validate(response)

    def delete(self, relationship_id: str) -> None:
        """
        Delete a relationship.

        Args:
            relationship_id: Relationship ID

        Example:
            >>> client.relationships.delete("rel_123")
        """
        validate_id(relationship_id, "relationship")
        self._client._request("DELETE", f"/relationships/{relationship_id}")

    def reinforce(
        self,
        relationship_id: str,
        boost: Optional[float] = None,
        context: Optional[str] = None,
    ) -> Relationship:
        """
        Reinforce a relationship to strengthen its connection.

        Args:
            relationship_id: Relationship ID
            boost: Amount to boost weight (optional)
            context: Context for reinforcement (optional)

        Returns:
            Updated relationship object

        Example:
            >>> rel = client.relationships.reinforce("rel_123", boost=0.5)
        """
        validate_id(relationship_id, "relationship")
        params = {}
        if boost is not None:
            params["boost"] = str(boost)
        if context:
            params["context"] = context

        response = self._client._request(
            "POST", f"/relationships/{relationship_id}/reinforce", params=params
        )
        return Relationship.model_validate(response)

    def weaken(
        self,
        relationship_id: str,
        amount: Optional[float] = None,
    ) -> Relationship:
        """
        Weaken a relationship to decrease its strength.

        Args:
            relationship_id: Relationship ID
            amount: Amount to decrease weight (optional)

        Returns:
            Updated relationship object

        Example:
            >>> rel = client.relationships.weaken("rel_123", amount=0.2)
        """
        validate_id(relationship_id, "relationship")
        data: Dict[str, Any] = {}
        if amount is not None:
            data["amount"] = amount

        response = self._client._request(
            "POST", f"/relationships/{relationship_id}/weaken", json=data if data else None
        )
        return Relationship.model_validate(response)

    def get_types(self) -> List[RelationshipTypeInfo]:
        """
        Get available relationship types.

        Returns:
            List of relationship type information

        Example:
            >>> types = client.relationships.get_types()
            >>> for t in types:
            ...     print(f"{t.name}: {t.description}")
        """
        response = self._client._request("GET", "/relationships/types")
        return [RelationshipTypeInfo.model_validate(t) for t in response.get("types", [])]

    def get_related(self, memory_id: str) -> RelatedMemoriesResult:
        """
        Get related memories for a memory.

        Args:
            memory_id: Memory ID

        Returns:
            Related memories with relationship info

        Example:
            >>> related = client.relationships.get_related("mem_123")
            >>> for mem in related.memories:
            ...     print(f"{mem.id}: {mem.relationship_type}")
        """
        validate_id(memory_id, "memory")
        response = self._client._request("GET", f"/relationships/{memory_id}/related")
        return RelatedMemoriesResult.model_validate(response)

    def reinforce_group(
        self,
        relationship_ids: List[str],
        amount: Optional[float] = None,
    ) -> ReinforceGroupResult:
        """
        Reinforce a group of relationships at once.

        Args:
            relationship_ids: List of relationship IDs
            amount: Amount to boost each relationship (optional)

        Returns:
            Reinforce group result

        Example:
            >>> result = client.relationships.reinforce_group(
            ...     ["rel_123", "rel_456"],
            ...     amount=0.1
            ... )
        """
        data: Dict[str, Any] = {"relationship_ids": relationship_ids}
        if amount is not None:
            data["amount"] = amount

        response = self._client._request("POST", "/relationships/reinforce-group", json=data)
        return ReinforceGroupResult.model_validate(response)


class AsyncRelationshipsResource:
    """Async resource for managing relationships between memories."""

    def __init__(self, client: AsyncClientProtocol) -> None:
        """Initialize async relationships resource with client."""
        self._client = client

    async def create(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType,
        description: Optional[str] = None,
        weight: float = 1.0,
        bidirectional: bool = False,
    ) -> Relationship:
        """Create a relationship between two memories (async)."""
        validate_id(source_id, "source memory")
        validate_id(target_id, "target memory")
        data = RelationshipCreate(
            relationship_type=relationship_type,
            description=description,
            weight=weight,
            bidirectional=bidirectional,
        )
        response = await self._client._request(
            "POST",
            f"/relationships/{source_id}/create/{target_id}",
            json=data.model_dump(exclude_none=True),
        )
        return Relationship.model_validate(response)

    async def get_incoming(self, memory_id: str) -> RelationshipList:
        """Get all incoming relationships for a memory (async)."""
        validate_id(memory_id, "memory")
        response = await self._client._request("GET", f"/relationships/{memory_id}/incoming")
        return RelationshipList.model_validate(response)

    async def get_outgoing(self, memory_id: str) -> RelationshipList:
        """Get all outgoing relationships for a memory (async)."""
        validate_id(memory_id, "memory")
        response = await self._client._request("GET", f"/relationships/{memory_id}/outgoing")
        return RelationshipList.model_validate(response)

    async def update(
        self,
        relationship_id: str,
        weight: Optional[float] = None,
        description: Optional[str] = None,
    ) -> Relationship:
        """Update a relationship (async)."""
        validate_id(relationship_id, "relationship")
        data = RelationshipUpdate(weight=weight, description=description)
        response = await self._client._request(
            "PATCH", f"/relationships/{relationship_id}", json=data.model_dump(exclude_none=True)
        )
        return Relationship.model_validate(response)

    async def delete(self, relationship_id: str) -> None:
        """Delete a relationship (async)."""
        validate_id(relationship_id, "relationship")
        await self._client._request("DELETE", f"/relationships/{relationship_id}")

    async def reinforce(
        self,
        relationship_id: str,
        boost: Optional[float] = None,
        context: Optional[str] = None,
    ) -> Relationship:
        """Reinforce a relationship to strengthen its connection (async)."""
        validate_id(relationship_id, "relationship")
        params = {}
        if boost is not None:
            params["boost"] = str(boost)
        if context:
            params["context"] = context

        response = await self._client._request(
            "POST", f"/relationships/{relationship_id}/reinforce", params=params
        )
        return Relationship.model_validate(response)

    async def weaken(
        self,
        relationship_id: str,
        amount: Optional[float] = None,
    ) -> Relationship:
        """Weaken a relationship to decrease its strength (async)."""
        validate_id(relationship_id, "relationship")
        data: Dict[str, Any] = {}
        if amount is not None:
            data["amount"] = amount

        response = await self._client._request(
            "POST", f"/relationships/{relationship_id}/weaken", json=data if data else None
        )
        return Relationship.model_validate(response)

    async def get_types(self) -> List[RelationshipTypeInfo]:
        """Get available relationship types (async)."""
        response = await self._client._request("GET", "/relationships/types")
        return [RelationshipTypeInfo.model_validate(t) for t in response.get("types", [])]

    async def get_related(self, memory_id: str) -> RelatedMemoriesResult:
        """Get related memories for a memory (async)."""
        validate_id(memory_id, "memory")
        response = await self._client._request("GET", f"/relationships/{memory_id}/related")
        return RelatedMemoriesResult.model_validate(response)

    async def reinforce_group(
        self,
        relationship_ids: List[str],
        amount: Optional[float] = None,
    ) -> ReinforceGroupResult:
        """Reinforce a group of relationships at once (async)."""
        data: Dict[str, Any] = {"relationship_ids": relationship_ids}
        if amount is not None:
            data["amount"] = amount

        response = await self._client._request("POST", "/relationships/reinforce-group", json=data)
        return ReinforceGroupResult.model_validate(response)
