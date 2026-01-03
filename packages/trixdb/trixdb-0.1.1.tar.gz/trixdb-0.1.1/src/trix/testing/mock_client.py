"""
Mock Trix client for testing.

Provides fully-typed mock clients that can be used in unit tests
without making real API calls.

Example:
    >>> from trix.testing import MockTrix, create_mock_memory
    >>>
    >>> mock_client = MockTrix()
    >>>
    >>> # Configure mock responses
    >>> mock_client.memories.mock_create(create_mock_memory(content="Test"))
    >>>
    >>> # Use in tests
    >>> memory = mock_client.memories.create(content="Test")
    >>> assert memory.content == "Test"
    >>>
    >>> # Verify calls
    >>> assert len(mock_client.memories.create_calls) == 1
    >>> assert mock_client.memories.create_calls[0]["content"] == "Test"
"""

from __future__ import annotations

import random
import string
from dataclasses import dataclass, field
from datetime import datetime
from typing import (
    Any,
    Callable,
    Generic,
    Optional,
    TypeVar,
    Union,
)

from ..types import (
    BulkResult,
    Cluster,
    Entity,
    Fact,
    Memory,
    MemoryType,
    PaginatedResponse,
    Pagination,
    Relationship,
    RelationshipType,
)


# ============================================================================
# Helper Functions
# ============================================================================


def random_id() -> str:
    """Generate a random ID string."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=8))


# ============================================================================
# Mock Data Factories
# ============================================================================


def create_mock_memory(
    id: Optional[str] = None,
    space_id: Optional[str] = None,
    content: str = "Mock memory content",
    type: MemoryType = MemoryType.TEXT,
    tags: Optional[list[str]] = None,
    metadata: Optional[dict[str, Any]] = None,
    **kwargs: Any,
) -> Memory:
    """Create a mock Memory object."""
    now = datetime.utcnow()
    return Memory(
        id=id or f"mem_{random_id()}",
        space_id=space_id,
        content=content,
        type=type,
        tags=tags or [],
        metadata=metadata or {},
        created_at=now,
        updated_at=now,
        **kwargs,
    )


def create_mock_cluster(
    id: Optional[str] = None,
    name: str = "Mock Cluster",
    description: str = "A mock cluster for testing",
    color: Optional[str] = None,
    memory_count: int = 0,
    metadata: Optional[dict[str, Any]] = None,
    **kwargs: Any,
) -> Cluster:
    """Create a mock Cluster object."""
    now = datetime.utcnow()
    return Cluster(
        id=id or f"clus_{random_id()}",
        name=name,
        description=description,
        color=color,
        memory_count=memory_count,
        metadata=metadata or {},
        created_at=now,
        updated_at=now,
        **kwargs,
    )


def create_mock_relationship(
    id: Optional[str] = None,
    source_id: Optional[str] = None,
    target_id: Optional[str] = None,
    relationship_type: RelationshipType = RelationshipType.RELATED_TO,
    description: Optional[str] = None,
    weight: float = 1.0,
    bidirectional: bool = False,
    **kwargs: Any,
) -> Relationship:
    """Create a mock Relationship object."""
    now = datetime.utcnow()
    return Relationship(
        id=id or f"rel_{random_id()}",
        source_id=source_id or f"mem_{random_id()}",
        target_id=target_id or f"mem_{random_id()}",
        relationship_type=relationship_type,
        description=description,
        weight=weight,
        bidirectional=bidirectional,
        created_at=now,
        updated_at=now,
        **kwargs,
    )


def create_mock_entity(
    id: Optional[str] = None,
    name: str = "Mock Entity",
    type: str = "person",
    aliases: Optional[list[str]] = None,
    description: Optional[str] = None,
    properties: Optional[dict[str, Any]] = None,
    memory_ids: Optional[list[str]] = None,
    metadata: Optional[dict[str, Any]] = None,
    space_id: Optional[str] = None,
    **kwargs: Any,
) -> Entity:
    """Create a mock Entity object."""
    now = datetime.utcnow()
    return Entity(
        id=id or f"ent_{random_id()}",
        name=name,
        type=type,
        aliases=aliases or [],
        description=description,
        properties=properties or {},
        memory_ids=memory_ids or [],
        metadata=metadata or {},
        space_id=space_id,
        created_at=now,
        updated_at=now,
        **kwargs,
    )


def create_mock_fact(
    id: Optional[str] = None,
    subject: str = "Subject",
    predicate: str = "is",
    object: str = "Object",
    confidence: float = 1.0,
    metadata: Optional[dict[str, Any]] = None,
    space_id: Optional[str] = None,
    **kwargs: Any,
) -> Fact:
    """Create a mock Fact object."""
    now = datetime.utcnow()
    return Fact(
        id=id or f"fact_{random_id()}",
        subject=subject,
        predicate=predicate,
        object=object,
        confidence=confidence,
        metadata=metadata or {},
        space_id=space_id,
        created_at=now,
        updated_at=now,
        **kwargs,
    )


T = TypeVar("T")


def create_mock_paginated_response(
    data: list[T],
    total: Optional[int] = None,
    page: int = 1,
    limit: int = 100,
    has_more: bool = False,
) -> PaginatedResponse[T]:
    """Create a mock paginated response."""
    return PaginatedResponse(
        data=data,
        pagination=Pagination(
            total=total if total is not None else len(data),
            page=page,
            limit=limit,
            has_more=has_more,
        ),
    )


def create_mock_bulk_result(
    success: int = 1,
    failed: int = 0,
    errors: Optional[list[dict[str, Any]]] = None,
) -> BulkResult:
    """Create a mock bulk result."""
    return BulkResult(
        success=success,
        failed=failed,
        errors=errors or [],
    )


# ============================================================================
# Mock Response Types
# ============================================================================

TItem = TypeVar("TItem")
MockResponse = Union[TItem, Exception, Callable[[], TItem]]


# ============================================================================
# Mock Resource Classes (Sync)
# ============================================================================


@dataclass
class MockResource(Generic[TItem]):
    """Base mock resource with call tracking."""

    _create_response: Optional[MockResponse[TItem]] = None
    _list_response: Optional[MockResponse[PaginatedResponse[TItem]]] = None
    _get_response: Optional[MockResponse[TItem]] = None
    _update_response: Optional[MockResponse[TItem]] = None
    _delete_response: Optional[MockResponse[None]] = None

    create_calls: list[dict[str, Any]] = field(default_factory=list)
    list_calls: list[dict[str, Any]] = field(default_factory=list)
    get_calls: list[str] = field(default_factory=list)
    update_calls: list[dict[str, Any]] = field(default_factory=list)
    delete_calls: list[str] = field(default_factory=list)

    def mock_create(self, response: MockResponse[TItem]) -> None:
        """Set mock response for create calls."""
        self._create_response = response

    def mock_list(self, response: MockResponse[PaginatedResponse[TItem]]) -> None:
        """Set mock response for list calls."""
        self._list_response = response

    def mock_get(self, response: MockResponse[TItem]) -> None:
        """Set mock response for get calls."""
        self._get_response = response

    def mock_update(self, response: MockResponse[TItem]) -> None:
        """Set mock response for update calls."""
        self._update_response = response

    def mock_delete(self, response: MockResponse[None]) -> None:
        """Set mock response for delete calls."""
        self._delete_response = response

    def _resolve_response(self, response: Optional[MockResponse[T]]) -> T:
        """Resolve a mock response value."""
        if response is None:
            raise ValueError("No mock response configured")
        if isinstance(response, Exception):
            raise response
        if callable(response):
            return response()
        return response

    def create(self, **kwargs: Any) -> TItem:
        """Mock create method."""
        self.create_calls.append(kwargs)
        return self._resolve_response(self._create_response)

    def list(self, **kwargs: Any) -> PaginatedResponse[TItem]:
        """Mock list method."""
        self.list_calls.append(kwargs)
        return self._resolve_response(self._list_response)

    def get(self, id: str) -> TItem:
        """Mock get method."""
        self.get_calls.append(id)
        return self._resolve_response(self._get_response)

    def update(self, id: str, **kwargs: Any) -> TItem:
        """Mock update method."""
        self.update_calls.append({"id": id, **kwargs})
        return self._resolve_response(self._update_response)

    def delete(self, id: str) -> None:
        """Mock delete method."""
        self.delete_calls.append(id)
        self._resolve_response(self._delete_response)  # type: ignore[arg-type]

    def reset(self) -> None:
        """Reset all mock responses and call history."""
        self._create_response = None
        self._list_response = None
        self._get_response = None
        self._update_response = None
        self._delete_response = None
        self.create_calls.clear()
        self.list_calls.clear()
        self.get_calls.clear()
        self.update_calls.clear()
        self.delete_calls.clear()


@dataclass
class MockMemoriesResource(MockResource[Memory]):
    """Mock Memories resource with additional methods."""

    _bulk_create_response: Optional[MockResponse[BulkResult]] = None
    bulk_create_calls: list[list[dict[str, Any]]] = field(default_factory=list)

    def mock_bulk_create(self, response: MockResponse[BulkResult]) -> None:
        """Set mock response for bulk_create calls."""
        self._bulk_create_response = response

    def bulk_create(self, memories: list[dict[str, Any]]) -> BulkResult:
        """Mock bulk_create method."""
        self.bulk_create_calls.append(memories)
        if self._bulk_create_response is None:
            return create_mock_bulk_result(success=len(memories))
        return self._resolve_response(self._bulk_create_response)


@dataclass
class MockClustersResource(MockResource[Cluster]):
    """Mock Clusters resource."""

    pass


@dataclass
class MockEntitiesResource(MockResource[Entity]):
    """Mock Entities resource with search."""

    _search_response: Optional[MockResponse[PaginatedResponse[Entity]]] = None
    search_calls: list[dict[str, Any]] = field(default_factory=list)

    def mock_search(self, response: MockResponse[PaginatedResponse[Entity]]) -> None:
        """Set mock response for search calls."""
        self._search_response = response

    def search(self, query: str, **kwargs: Any) -> PaginatedResponse[Entity]:
        """Mock search method."""
        self.search_calls.append({"query": query, **kwargs})
        if self._search_response is None:
            return create_mock_paginated_response([])
        return self._resolve_response(self._search_response)


@dataclass
class MockFactsResource(MockResource[Fact]):
    """Mock Facts resource."""

    pass


# ============================================================================
# Mock Resource Classes (Async)
# ============================================================================


@dataclass
class MockAsyncResource(Generic[TItem]):
    """Base async mock resource with call tracking."""

    _create_response: Optional[MockResponse[TItem]] = None
    _list_response: Optional[MockResponse[PaginatedResponse[TItem]]] = None
    _get_response: Optional[MockResponse[TItem]] = None
    _update_response: Optional[MockResponse[TItem]] = None
    _delete_response: Optional[MockResponse[None]] = None

    create_calls: list[dict[str, Any]] = field(default_factory=list)
    list_calls: list[dict[str, Any]] = field(default_factory=list)
    get_calls: list[str] = field(default_factory=list)
    update_calls: list[dict[str, Any]] = field(default_factory=list)
    delete_calls: list[str] = field(default_factory=list)

    def mock_create(self, response: MockResponse[TItem]) -> None:
        """Set mock response for create calls."""
        self._create_response = response

    def mock_list(self, response: MockResponse[PaginatedResponse[TItem]]) -> None:
        """Set mock response for list calls."""
        self._list_response = response

    def mock_get(self, response: MockResponse[TItem]) -> None:
        """Set mock response for get calls."""
        self._get_response = response

    def mock_update(self, response: MockResponse[TItem]) -> None:
        """Set mock response for update calls."""
        self._update_response = response

    def mock_delete(self, response: MockResponse[None]) -> None:
        """Set mock response for delete calls."""
        self._delete_response = response

    def _resolve_response(self, response: Optional[MockResponse[T]]) -> T:
        """Resolve a mock response value."""
        if response is None:
            raise ValueError("No mock response configured")
        if isinstance(response, Exception):
            raise response
        if callable(response):
            return response()
        return response

    async def create(self, **kwargs: Any) -> TItem:
        """Mock async create method."""
        self.create_calls.append(kwargs)
        return self._resolve_response(self._create_response)

    async def list(self, **kwargs: Any) -> PaginatedResponse[TItem]:
        """Mock async list method."""
        self.list_calls.append(kwargs)
        return self._resolve_response(self._list_response)

    async def get(self, id: str) -> TItem:
        """Mock async get method."""
        self.get_calls.append(id)
        return self._resolve_response(self._get_response)

    async def update(self, id: str, **kwargs: Any) -> TItem:
        """Mock async update method."""
        self.update_calls.append({"id": id, **kwargs})
        return self._resolve_response(self._update_response)

    async def delete(self, id: str) -> None:
        """Mock async delete method."""
        self.delete_calls.append(id)
        self._resolve_response(self._delete_response)  # type: ignore[arg-type]

    def reset(self) -> None:
        """Reset all mock responses and call history."""
        self._create_response = None
        self._list_response = None
        self._get_response = None
        self._update_response = None
        self._delete_response = None
        self.create_calls.clear()
        self.list_calls.clear()
        self.get_calls.clear()
        self.update_calls.clear()
        self.delete_calls.clear()


@dataclass
class MockAsyncMemoriesResource(MockAsyncResource[Memory]):
    """Mock async Memories resource."""

    _bulk_create_response: Optional[MockResponse[BulkResult]] = None
    bulk_create_calls: list[list[dict[str, Any]]] = field(default_factory=list)

    def mock_bulk_create(self, response: MockResponse[BulkResult]) -> None:
        """Set mock response for bulk_create calls."""
        self._bulk_create_response = response

    async def bulk_create(self, memories: list[dict[str, Any]]) -> BulkResult:
        """Mock async bulk_create method."""
        self.bulk_create_calls.append(memories)
        if self._bulk_create_response is None:
            return create_mock_bulk_result(success=len(memories))
        return self._resolve_response(self._bulk_create_response)


@dataclass
class MockAsyncClustersResource(MockAsyncResource[Cluster]):
    """Mock async Clusters resource."""

    pass


@dataclass
class MockAsyncEntitiesResource(MockAsyncResource[Entity]):
    """Mock async Entities resource with search."""

    _search_response: Optional[MockResponse[PaginatedResponse[Entity]]] = None
    search_calls: list[dict[str, Any]] = field(default_factory=list)

    def mock_search(self, response: MockResponse[PaginatedResponse[Entity]]) -> None:
        """Set mock response for search calls."""
        self._search_response = response

    async def search(self, query: str, **kwargs: Any) -> PaginatedResponse[Entity]:
        """Mock async search method."""
        self.search_calls.append({"query": query, **kwargs})
        if self._search_response is None:
            return create_mock_paginated_response([])
        return self._resolve_response(self._search_response)


@dataclass
class MockAsyncFactsResource(MockAsyncResource[Fact]):
    """Mock async Facts resource."""

    pass


# ============================================================================
# Main Mock Clients
# ============================================================================


@dataclass
class MockTrix:
    """Mock Trix client for synchronous testing.

    Example:
        >>> from trix.testing import MockTrix, create_mock_memory
        >>>
        >>> def test_my_service():
        ...     mock_client = MockTrix()
        ...
        ...     # Configure mock responses
        ...     mock_mem = create_mock_memory(content="Test")
        ...     mock_client.memories.mock_create(mock_mem)
        ...
        ...     # Use in tests
        ...     result = my_service.create_memory(mock_client, "Test")
        ...
        ...     assert result.id == mock_mem.id
        ...     assert len(mock_client.memories.create_calls) == 1
        ...     assert mock_client.memories.create_calls[0]["content"] == "Test"
    """

    memories: MockMemoriesResource = field(default_factory=MockMemoriesResource)
    clusters: MockClustersResource = field(default_factory=MockClustersResource)
    entities: MockEntitiesResource = field(default_factory=MockEntitiesResource)
    facts: MockFactsResource = field(default_factory=MockFactsResource)

    def reset(self) -> None:
        """Reset all mock resources and call history."""
        self.memories.reset()
        self.clusters.reset()
        self.entities.reset()
        self.facts.reset()


@dataclass
class MockAsyncTrix:
    """Mock Trix client for asynchronous testing.

    Example:
        >>> from trix.testing import MockAsyncTrix, create_mock_memory
        >>>
        >>> async def test_my_service():
        ...     mock_client = MockAsyncTrix()
        ...
        ...     # Configure mock responses
        ...     mock_mem = create_mock_memory(content="Test")
        ...     mock_client.memories.mock_create(mock_mem)
        ...
        ...     # Use in tests
        ...     result = await my_service.create_memory(mock_client, "Test")
        ...
        ...     assert result.id == mock_mem.id
        ...     assert len(mock_client.memories.create_calls) == 1
    """

    memories: MockAsyncMemoriesResource = field(default_factory=MockAsyncMemoriesResource)
    clusters: MockAsyncClustersResource = field(default_factory=MockAsyncClustersResource)
    entities: MockAsyncEntitiesResource = field(default_factory=MockAsyncEntitiesResource)
    facts: MockAsyncFactsResource = field(default_factory=MockAsyncFactsResource)

    def reset(self) -> None:
        """Reset all mock resources and call history."""
        self.memories.reset()
        self.clusters.reset()
        self.entities.reset()
        self.facts.reset()
