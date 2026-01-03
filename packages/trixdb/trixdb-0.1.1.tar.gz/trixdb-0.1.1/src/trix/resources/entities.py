"""Entities resource for Trix SDK - Named Entity Management."""

from typing import Any, Dict, List, Optional

from .base import BaseAsyncResource, BaseSyncResource, validate_bulk_array
from ..types import (
    Entity,
    EntityCreate,
    EntityUpdate,
    EntityList,
    EntitySearchResult,
    EntityResolutionResult,
    EntityMergeResult,
    EntityMemoryLinkResult,
    EntityExtractionResult,
    EntityTypesResult,
    EntityFactsResult,
)
from ..utils.security import validate_id


def _build_entity_params(
    entity_type: Optional[str] = None,
    space_id: Optional[str] = None,
    limit: Optional[int] = None,
    page: Optional[int] = None,
    offset: Optional[int] = None,
) -> Dict[str, Any]:
    """Build query parameters for entity listing."""
    params: Dict[str, Any] = {}
    if entity_type is not None:
        params["type"] = entity_type
    if space_id is not None:
        params["spaceId"] = space_id
    if limit is not None:
        params["limit"] = limit
    if page is not None:
        params["page"] = page
    if offset is not None:
        params["offset"] = offset
    return params


class EntitiesResource(BaseSyncResource):
    """Resource for managing named entities.

    Entities represent people, places, organizations, concepts, and other
    named objects in your knowledge base.

    Example:
        >>> # Create an entity
        >>> entity = client.entities.create(
        ...     name="Albert Einstein",
        ...     entity_type="person",
        ...     aliases=["Einstein", "A. Einstein"]
        ... )
        >>>
        >>> # Search entities
        >>> results = client.entities.search("Einstein")
    """

    def create(
        self,
        name: str,
        entity_type: str,
        aliases: Optional[List[str]] = None,
        description: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        memory_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        space_id: Optional[str] = None,
    ) -> Entity:
        """Create a new entity.

        Args:
            name: Entity name
            entity_type: Entity type (person, location, organization, etc.)
            aliases: Alternative names for the entity
            description: Description of the entity
            properties: Custom properties (flexible schema)
            memory_ids: IDs of memories to link
            metadata: Additional metadata
            space_id: Space to create entity in

        Returns:
            Created entity object

        Example:
            >>> entity = client.entities.create(
            ...     name="Trix",
            ...     entity_type="product",
            ...     properties={"language": "TypeScript"}
            ... )
        """
        data = EntityCreate(
            name=name,
            type=entity_type,
            aliases=aliases,
            description=description,
            properties=properties,
            memory_ids=memory_ids,
            metadata=metadata,
            space_id=space_id,
        )
        response = self._request("POST", "/entities", json=data.model_dump(exclude_none=True))
        return Entity.model_validate(response)

    def get(self, id: str) -> Entity:
        """Get an entity by ID.

        Args:
            id: Entity ID

        Returns:
            Entity object

        Raises:
            ValidationError: If ID format is invalid
            NotFoundError: If entity doesn't exist
        """
        validate_id(id, "entity")
        response = self._request("GET", f"/entities/{id}")
        return Entity.model_validate(response)

    def list(
        self,
        entity_type: Optional[str] = None,
        space_id: Optional[str] = None,
        limit: Optional[int] = None,
        page: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> EntityList:
        """List entities with optional filters.

        Args:
            entity_type: Filter by entity type
            space_id: Filter by space
            limit: Maximum results to return
            page: Page number
            offset: Result offset

        Returns:
            Paginated list of entities
        """
        params = _build_entity_params(
            entity_type=entity_type,
            space_id=space_id,
            limit=limit,
            page=page,
            offset=offset,
        )
        response = self._request("GET", "/entities", params=params if params else None)
        return EntityList.model_validate(response)

    def update(
        self,
        id: str,
        name: Optional[str] = None,
        entity_type: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        description: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Entity:
        """Update an entity.

        Args:
            id: Entity ID
            name: New name
            entity_type: New type
            aliases: New aliases
            description: New description
            properties: New properties
            metadata: New metadata

        Returns:
            Updated entity object
        """
        validate_id(id, "entity")
        data = EntityUpdate(
            name=name,
            type=entity_type,
            aliases=aliases,
            description=description,
            properties=properties,
            metadata=metadata,
        )
        response = self._request(
            "PATCH", f"/entities/{id}", json=data.model_dump(exclude_none=True)
        )
        return Entity.model_validate(response)

    def delete(self, id: str) -> None:
        """Delete an entity.

        Args:
            id: Entity ID
        """
        validate_id(id, "entity")
        self._request("DELETE", f"/entities/{id}")

    def search(
        self,
        query: str,
        entity_type: Optional[str] = None,
        space_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> EntitySearchResult:
        """Search entities by name or alias.

        Args:
            query: Search query
            entity_type: Filter by type
            space_id: Filter by space
            limit: Maximum results

        Returns:
            Search results with scored entities
        """
        body: Dict[str, Any] = {"query": query}
        if entity_type is not None:
            body["type"] = entity_type
        if space_id is not None:
            body["spaceId"] = space_id
        if limit is not None:
            body["limit"] = limit
        response = self._request("POST", "/entities/search", json=body)
        return EntitySearchResult.model_validate(response)

    def find_by_type(
        self,
        entity_type: str,
        limit: Optional[int] = None,
    ) -> EntityList:
        """Find entities by type."""
        return self.list(entity_type=entity_type, limit=limit)

    def find_by_memory(self, memory_id: str) -> EntityList:
        """Find entities linked to a memory.

        Args:
            memory_id: Memory ID

        Returns:
            List of linked entities
        """
        validate_id(memory_id, "memory")
        response = self._request("GET", f"/memories/{memory_id}/entities")
        return EntityList.model_validate(response)

    def resolve(
        self,
        text: str,
        context: Optional[str] = None,
        space_id: Optional[str] = None,
    ) -> EntityResolutionResult:
        """Resolve text to an entity.

        Args:
            text: Text to resolve
            context: Context for disambiguation
            space_id: Space to search in

        Returns:
            Resolution result with matched entity
        """
        body: Dict[str, Any] = {"text": text}
        if context is not None:
            body["context"] = context
        if space_id is not None:
            body["spaceId"] = space_id
        response = self._request("POST", "/entities/resolve", json=body)
        return EntityResolutionResult.model_validate(response)

    def merge(self, target_id: str, source_id: str) -> EntityMergeResult:
        """Merge two entities.

        Args:
            target_id: ID of entity to merge into
            source_id: ID of entity to merge from (will be deleted)

        Returns:
            Merge result
        """
        validate_id(target_id, "entity")
        validate_id(source_id, "entity")
        response = self._request(
            "POST", f"/entities/{target_id}/merge", json={"sourceId": source_id}
        )
        return EntityMergeResult.model_validate(response)

    def link_to_memory(self, entity_id: str, memory_id: str) -> EntityMemoryLinkResult:
        """Link an entity to a memory.

        Args:
            entity_id: Entity ID
            memory_id: Memory ID

        Returns:
            Link result
        """
        validate_id(entity_id, "entity")
        validate_id(memory_id, "memory")
        response = self._request(
            "POST", f"/entities/{entity_id}/memories", json={"memoryId": memory_id}
        )
        return EntityMemoryLinkResult.model_validate(response)

    def unlink_from_memory(self, entity_id: str, memory_id: str) -> None:
        """Unlink an entity from a memory.

        Args:
            entity_id: Entity ID
            memory_id: Memory ID
        """
        validate_id(entity_id, "entity")
        validate_id(memory_id, "memory")
        self._request("DELETE", f"/entities/{entity_id}/memories/{memory_id}")

    def bulk_create(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create multiple entities in bulk.

        Args:
            entities: List of entity dictionaries

        Returns:
            Bulk operation result

        Raises:
            ValueError: If array is empty or exceeds limit
        """
        validate_bulk_array(entities, "bulk_create")
        response = self._request("POST", "/entities/bulk", json={"entities": entities})
        return dict(response)

    def bulk_delete(self, ids: List[str]) -> Dict[str, Any]:
        """Delete multiple entities in bulk.

        Args:
            ids: List of entity IDs to delete

        Returns:
            Bulk operation result
        """
        validate_bulk_array(ids, "bulk_delete")
        response = self._request("DELETE", "/entities/bulk", json={"ids": ids})
        return dict(response)

    def extract(
        self,
        memory_id: str,
        save: bool = False,
        link: bool = False,
    ) -> EntityExtractionResult:
        """Extract entities from a memory.

        Args:
            memory_id: Memory ID to extract from
            save: Whether to save extracted entities
            link: Whether to link entities to the memory

        Returns:
            Extracted entities
        """
        validate_id(memory_id, "memory")
        body: Dict[str, Any] = {}
        if save:
            body["save"] = save
        if link:
            body["link"] = link
        response = self._request("POST", f"/memories/{memory_id}/extract-entities", json=body)
        return EntityExtractionResult.model_validate(response)

    def get_types(self) -> EntityTypesResult:
        """Get all entity types in the system.

        Returns:
            List of entity types with counts
        """
        response = self._request("GET", "/entities/types")
        return EntityTypesResult.model_validate(response)

    def get_facts(self, entity_id: str) -> EntityFactsResult:
        """Get facts about an entity.

        Args:
            entity_id: Entity ID

        Returns:
            List of facts about the entity
        """
        validate_id(entity_id, "entity")
        response = self._request("GET", f"/entities/{entity_id}/facts")
        return EntityFactsResult.model_validate(response)


class AsyncEntitiesResource(BaseAsyncResource):
    """Async resource for managing named entities.

    Entities represent people, places, organizations, concepts, and other
    named objects in your knowledge base.
    """

    async def create(
        self,
        name: str,
        entity_type: str,
        aliases: Optional[List[str]] = None,
        description: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        memory_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        space_id: Optional[str] = None,
    ) -> Entity:
        """Create a new entity (async)."""
        data = EntityCreate(
            name=name,
            type=entity_type,
            aliases=aliases,
            description=description,
            properties=properties,
            memory_ids=memory_ids,
            metadata=metadata,
            space_id=space_id,
        )
        response = await self._request("POST", "/entities", json=data.model_dump(exclude_none=True))
        return Entity.model_validate(response)

    async def get(self, id: str) -> Entity:
        """Get an entity by ID (async)."""
        validate_id(id, "entity")
        response = await self._request("GET", f"/entities/{id}")
        return Entity.model_validate(response)

    async def list(
        self,
        entity_type: Optional[str] = None,
        space_id: Optional[str] = None,
        limit: Optional[int] = None,
        page: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> EntityList:
        """List entities with optional filters (async)."""
        params = _build_entity_params(
            entity_type=entity_type,
            space_id=space_id,
            limit=limit,
            page=page,
            offset=offset,
        )
        response = await self._request("GET", "/entities", params=params if params else None)
        return EntityList.model_validate(response)

    async def update(
        self,
        id: str,
        name: Optional[str] = None,
        entity_type: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        description: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Entity:
        """Update an entity (async)."""
        validate_id(id, "entity")
        data = EntityUpdate(
            name=name,
            type=entity_type,
            aliases=aliases,
            description=description,
            properties=properties,
            metadata=metadata,
        )
        response = await self._request(
            "PATCH", f"/entities/{id}", json=data.model_dump(exclude_none=True)
        )
        return Entity.model_validate(response)

    async def delete(self, id: str) -> None:
        """Delete an entity (async)."""
        validate_id(id, "entity")
        await self._request("DELETE", f"/entities/{id}")

    async def search(
        self,
        query: str,
        entity_type: Optional[str] = None,
        space_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> EntitySearchResult:
        """Search entities by name or alias (async)."""
        body: Dict[str, Any] = {"query": query}
        if entity_type is not None:
            body["type"] = entity_type
        if space_id is not None:
            body["spaceId"] = space_id
        if limit is not None:
            body["limit"] = limit
        response = await self._request("POST", "/entities/search", json=body)
        return EntitySearchResult.model_validate(response)

    async def find_by_type(
        self,
        entity_type: str,
        limit: Optional[int] = None,
    ) -> EntityList:
        """Find entities by type (async)."""
        return await self.list(entity_type=entity_type, limit=limit)

    async def find_by_memory(self, memory_id: str) -> EntityList:
        """Find entities linked to a memory (async)."""
        validate_id(memory_id, "memory")
        response = await self._request("GET", f"/memories/{memory_id}/entities")
        return EntityList.model_validate(response)

    async def resolve(
        self,
        text: str,
        context: Optional[str] = None,
        space_id: Optional[str] = None,
    ) -> EntityResolutionResult:
        """Resolve text to an entity (async)."""
        body: Dict[str, Any] = {"text": text}
        if context is not None:
            body["context"] = context
        if space_id is not None:
            body["spaceId"] = space_id
        response = await self._request("POST", "/entities/resolve", json=body)
        return EntityResolutionResult.model_validate(response)

    async def merge(self, target_id: str, source_id: str) -> EntityMergeResult:
        """Merge two entities (async)."""
        validate_id(target_id, "entity")
        validate_id(source_id, "entity")
        response = await self._request(
            "POST", f"/entities/{target_id}/merge", json={"sourceId": source_id}
        )
        return EntityMergeResult.model_validate(response)

    async def link_to_memory(self, entity_id: str, memory_id: str) -> EntityMemoryLinkResult:
        """Link an entity to a memory (async)."""
        validate_id(entity_id, "entity")
        validate_id(memory_id, "memory")
        response = await self._request(
            "POST", f"/entities/{entity_id}/memories", json={"memoryId": memory_id}
        )
        return EntityMemoryLinkResult.model_validate(response)

    async def unlink_from_memory(self, entity_id: str, memory_id: str) -> None:
        """Unlink an entity from a memory (async)."""
        validate_id(entity_id, "entity")
        validate_id(memory_id, "memory")
        await self._request("DELETE", f"/entities/{entity_id}/memories/{memory_id}")

    async def bulk_create(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create multiple entities in bulk (async)."""
        validate_bulk_array(entities, "bulk_create")
        response = await self._request("POST", "/entities/bulk", json={"entities": entities})
        return dict(response)

    async def bulk_delete(self, ids: List[str]) -> Dict[str, Any]:
        """Delete multiple entities in bulk (async)."""
        validate_bulk_array(ids, "bulk_delete")
        response = await self._request("DELETE", "/entities/bulk", json={"ids": ids})
        return dict(response)

    async def extract(
        self,
        memory_id: str,
        save: bool = False,
        link: bool = False,
    ) -> EntityExtractionResult:
        """Extract entities from a memory (async)."""
        validate_id(memory_id, "memory")
        body: Dict[str, Any] = {}
        if save:
            body["save"] = save
        if link:
            body["link"] = link
        response = await self._request("POST", f"/memories/{memory_id}/extract-entities", json=body)
        return EntityExtractionResult.model_validate(response)

    async def get_types(self) -> EntityTypesResult:
        """Get all entity types in the system (async)."""
        response = await self._request("GET", "/entities/types")
        return EntityTypesResult.model_validate(response)

    async def get_facts(self, entity_id: str) -> EntityFactsResult:
        """Get facts about an entity (async)."""
        validate_id(entity_id, "entity")
        response = await self._request("GET", f"/entities/{entity_id}/facts")
        return EntityFactsResult.model_validate(response)
