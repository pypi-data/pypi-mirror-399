"""Highlights resource for Trix SDK."""

from typing import Any, Dict, List, Optional

from ..protocols import AsyncClientProtocol, SyncClientProtocol

from ..types import (
    ExtractionType,
    ExtractedHighlights,
    Highlight,
    HighlightCreate,
    HighlightLinkResult,
    HighlightList,
    HighlightSearchResult,
    HighlightTypeInfo,
    HighlightUpdate,
)
from ..utils.security import validate_id


class HighlightsResource:
    """Resource for managing highlights within memories."""

    def __init__(self, client: SyncClientProtocol) -> None:
        """Initialize highlights resource with client."""
        self._client = client

    def create(
        self,
        memory_id: str,
        text: str,
        note: Optional[str] = None,
        importance: Optional[int] = None,
        tags: Optional[List[str]] = None,
        color: Optional[str] = None,
    ) -> Highlight:
        """
        Create a highlight within a memory.

        Args:
            memory_id: Memory ID
            text: Highlighted text
            note: Optional note about the highlight
            importance: Importance level
            tags: Tags for categorization
            color: Color code for the highlight

        Returns:
            Created highlight object

        Example:
            >>> highlight = client.highlights.create(
            ...     memory_id="mem_123",
            ...     text="This is important",
            ...     note="Key insight",
            ...     importance=5,
            ...     color="#FFFF00"
            ... )
        """
        validate_id(memory_id, "memory")
        data = HighlightCreate(
            text=text,
            note=note,
            importance=importance,
            tags=tags,
            color=color,
        )
        response = self._client._request(
            "POST",
            f"/highlights/{memory_id}",
            json=data.model_dump(exclude_none=True),
        )
        return Highlight.model_validate(response)

    def list(self, memory_id: str, limit: int = 100) -> HighlightList:
        """
        List highlights for a memory.

        Args:
            memory_id: Memory ID
            limit: Maximum number of highlights

        Returns:
            List of highlights

        Example:
            >>> highlights = client.highlights.list("mem_123")
        """
        validate_id(memory_id, "memory")
        params = {"limit": limit}
        response = self._client._request("GET", f"/highlights/{memory_id}", params=params)
        return HighlightList.model_validate(response)

    def get(self, highlight_id: str) -> Highlight:
        """
        Get a highlight by ID.

        Args:
            highlight_id: Highlight ID

        Returns:
            Highlight object

        Example:
            >>> highlight = client.highlights.get("highlight_123")
        """
        validate_id(highlight_id, "highlight")
        response = self._client._request("GET", f"/highlights/item/{highlight_id}")
        return Highlight.model_validate(response)

    def update(
        self,
        highlight_id: str,
        text: Optional[str] = None,
        note: Optional[str] = None,
        importance: Optional[int] = None,
        tags: Optional[List[str]] = None,
        color: Optional[str] = None,
    ) -> Highlight:
        """
        Update a highlight.

        Args:
            highlight_id: Highlight ID
            text: New text
            note: New note
            importance: New importance
            tags: New tags
            color: New color

        Returns:
            Updated highlight object

        Example:
            >>> highlight = client.highlights.update(
            ...     "highlight_123",
            ...     importance=10
            ... )
        """
        validate_id(highlight_id, "highlight")
        data = HighlightUpdate(
            text=text,
            note=note,
            importance=importance,
            tags=tags,
            color=color,
        )
        response = self._client._request(
            "PATCH",
            f"/highlights/item/{highlight_id}",
            json=data.model_dump(exclude_none=True),
        )
        return Highlight.model_validate(response)

    def delete(self, highlight_id: str) -> None:
        """
        Delete a highlight.

        Args:
            highlight_id: Highlight ID

        Example:
            >>> client.highlights.delete("highlight_123")
        """
        validate_id(highlight_id, "highlight")
        self._client._request("DELETE", f"/highlights/item/{highlight_id}")

    def extract(
        self,
        memory_id: str,
        extraction_types: Optional[List[ExtractionType]] = None,
        limit: int = 10,
    ) -> List[ExtractedHighlights]:
        """
        Automatically extract highlights from a memory.

        Args:
            memory_id: Memory ID
            extraction_types: Types of extractions to perform
            limit: Maximum number of extractions per type

        Returns:
            List of extracted highlights by type

        Example:
            >>> extractions = client.highlights.extract(
            ...     memory_id="mem_123",
            ...     extraction_types=[ExtractionType.KEY_POINTS, ExtractionType.ENTITIES]
            ... )
        """
        validate_id(memory_id, "memory")
        data: Dict[str, Any] = {"limit": limit}
        if extraction_types:
            data["extraction_types"] = [et.value for et in extraction_types]

        response = self._client._request("POST", f"/highlights/{memory_id}/extract", json=data)
        return [ExtractedHighlights.model_validate(e) for e in response.get("extractions", [])]

    def list_global(self, limit: int = 100, offset: int = 0) -> HighlightList:
        """
        List all highlights across all memories.

        Args:
            limit: Maximum number of highlights
            offset: Offset for pagination

        Returns:
            List of highlights

        Example:
            >>> highlights = client.highlights.list_global(limit=50)
        """
        params = {"limit": limit, "offset": offset}
        response = self._client._request("GET", "/highlights", params=params)
        return HighlightList.model_validate(response)

    def search(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.7,
    ) -> HighlightSearchResult:
        """
        Search highlights semantically.

        Args:
            query: Search query
            limit: Maximum number of results
            threshold: Minimum similarity threshold

        Returns:
            Search results

        Example:
            >>> results = client.highlights.search("important findings", limit=5)
        """
        data: Dict[str, Any] = {"query": query, "limit": limit, "threshold": threshold}
        response = self._client._request("POST", "/highlights/search", json=data)
        return HighlightSearchResult.model_validate(response)

    def get_types(self) -> List[HighlightTypeInfo]:
        """
        Get available highlight types.

        Returns:
            List of highlight types

        Example:
            >>> types = client.highlights.get_types()
            >>> for t in types:
            ...     print(f"{t.name}: {t.description}")
        """
        response = self._client._request("GET", "/highlights/types")
        return [HighlightTypeInfo.model_validate(t) for t in response.get("types", [])]

    def link(
        self,
        highlight_id: str,
        memory_id: str,
        note: Optional[str] = None,
    ) -> HighlightLinkResult:
        """
        Link a highlight to a memory.

        Args:
            highlight_id: Highlight ID
            memory_id: Memory ID to link to
            note: Optional note about the link

        Returns:
            Link result

        Example:
            >>> result = client.highlights.link(
            ...     highlight_id="highlight_123",
            ...     memory_id="mem_456",
            ...     note="Related reference"
            ... )
        """
        validate_id(highlight_id, "highlight")
        validate_id(memory_id, "memory")
        data: Dict[str, Any] = {"memory_id": memory_id}
        if note:
            data["note"] = note
        response = self._client._request("POST", f"/highlights/{highlight_id}/link", json=data)
        return HighlightLinkResult.model_validate(response)


class AsyncHighlightsResource:
    """Async resource for managing highlights within memories."""

    def __init__(self, client: AsyncClientProtocol) -> None:
        """Initialize async highlights resource with client."""
        self._client = client

    async def create(
        self,
        memory_id: str,
        text: str,
        note: Optional[str] = None,
        importance: Optional[int] = None,
        tags: Optional[List[str]] = None,
        color: Optional[str] = None,
    ) -> Highlight:
        """Create a highlight within a memory (async)."""
        validate_id(memory_id, "memory")
        data = HighlightCreate(
            text=text,
            note=note,
            importance=importance,
            tags=tags,
            color=color,
        )
        response = await self._client._request(
            "POST",
            f"/highlights/{memory_id}",
            json=data.model_dump(exclude_none=True),
        )
        return Highlight.model_validate(response)

    async def list(self, memory_id: str, limit: int = 100) -> HighlightList:
        """List highlights for a memory (async)."""
        validate_id(memory_id, "memory")
        params = {"limit": limit}
        response = await self._client._request("GET", f"/highlights/{memory_id}", params=params)
        return HighlightList.model_validate(response)

    async def get(self, highlight_id: str) -> Highlight:
        """Get a highlight by ID (async)."""
        validate_id(highlight_id, "highlight")
        response = await self._client._request("GET", f"/highlights/item/{highlight_id}")
        return Highlight.model_validate(response)

    async def update(
        self,
        highlight_id: str,
        text: Optional[str] = None,
        note: Optional[str] = None,
        importance: Optional[int] = None,
        tags: Optional[List[str]] = None,
        color: Optional[str] = None,
    ) -> Highlight:
        """Update a highlight (async)."""
        validate_id(highlight_id, "highlight")
        data = HighlightUpdate(
            text=text,
            note=note,
            importance=importance,
            tags=tags,
            color=color,
        )
        response = await self._client._request(
            "PATCH",
            f"/highlights/item/{highlight_id}",
            json=data.model_dump(exclude_none=True),
        )
        return Highlight.model_validate(response)

    async def delete(self, highlight_id: str) -> None:
        """Delete a highlight (async)."""
        validate_id(highlight_id, "highlight")
        await self._client._request("DELETE", f"/highlights/item/{highlight_id}")

    async def extract(
        self,
        memory_id: str,
        extraction_types: Optional[List[ExtractionType]] = None,
        limit: int = 10,
    ) -> List[ExtractedHighlights]:
        """Automatically extract highlights from a memory (async)."""
        validate_id(memory_id, "memory")
        data: Dict[str, Any] = {"limit": limit}
        if extraction_types:
            data["extraction_types"] = [et.value for et in extraction_types]

        response = await self._client._request(
            "POST", f"/highlights/{memory_id}/extract", json=data
        )
        return [ExtractedHighlights.model_validate(e) for e in response.get("extractions", [])]

    async def list_global(self, limit: int = 100, offset: int = 0) -> HighlightList:
        """List all highlights across all memories (async)."""
        params = {"limit": limit, "offset": offset}
        response = await self._client._request("GET", "/highlights", params=params)
        return HighlightList.model_validate(response)

    async def search(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.7,
    ) -> HighlightSearchResult:
        """Search highlights semantically (async)."""
        data: Dict[str, Any] = {"query": query, "limit": limit, "threshold": threshold}
        response = await self._client._request("POST", "/highlights/search", json=data)
        return HighlightSearchResult.model_validate(response)

    async def get_types(self) -> List[HighlightTypeInfo]:
        """Get available highlight types (async)."""
        response = await self._client._request("GET", "/highlights/types")
        return [HighlightTypeInfo.model_validate(t) for t in response.get("types", [])]

    async def link(
        self,
        highlight_id: str,
        memory_id: str,
        note: Optional[str] = None,
    ) -> HighlightLinkResult:
        """Link a highlight to a memory (async)."""
        validate_id(highlight_id, "highlight")
        validate_id(memory_id, "memory")
        data: Dict[str, Any] = {"memory_id": memory_id}
        if note:
            data["note"] = note
        response = await self._client._request(
            "POST", f"/highlights/{highlight_id}/link", json=data
        )
        return HighlightLinkResult.model_validate(response)
