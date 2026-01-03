"""Graph resource for Trix SDK."""

from typing import Any, Dict, List, Optional

from .base import BaseAsyncResource, BaseSyncResource, validate_ids
from ..types import (
    Direction,
    GraphContext,
    GraphNeighbors,
    GraphStats,
    GraphTraversal,
    RelationshipType,
    ShortestPath,
)
from ..utils.security import validate_id


def _build_traverse_data(
    start_ids: List[str],
    depth: int,
    relationship_types: Optional[List[RelationshipType]],
    direction: Direction,
) -> Dict[str, Any]:
    """Build traverse request data with validation."""
    validate_ids(start_ids, "memory")
    data: Dict[str, Any] = {
        "start_ids": start_ids,
        "depth": depth,
        "direction": direction.value,
    }
    if relationship_types:
        data["relationship_types"] = [rt.value for rt in relationship_types]
    return data


def _build_shortest_path_data(source_id: str, target_id: str, max_hops: int) -> Dict[str, Any]:
    """Build shortest path request data with validation."""
    validate_id(source_id, "source memory")
    validate_id(target_id, "target memory")
    return {
        "source_id": source_id,
        "target_id": target_id,
        "max_hops": max_hops,
    }


class GraphResource(BaseSyncResource):
    """Resource for graph traversal and analysis.

    This resource provides methods to explore the relationship graph
    between memories, including traversal, context queries, and
    shortest path finding.

    Example:
        >>> # Traverse from a starting point
        >>> result = client.graph.traverse(
        ...     start_ids=["mem_123"],
        ...     depth=3,
        ...     direction=Direction.OUTGOING
        ... )
        >>>
        >>> # Find shortest path
        >>> path = client.graph.shortest_path("mem_123", "mem_456")
    """

    def traverse(
        self,
        start_ids: List[str],
        depth: int = 2,
        relationship_types: Optional[List[RelationshipType]] = None,
        direction: Direction = Direction.BOTH,
    ) -> GraphTraversal:
        """Traverse the memory graph from starting points.

        Args:
            start_ids: List of starting memory IDs
            depth: Maximum traversal depth
            relationship_types: Filter by relationship types
            direction: Traversal direction (outgoing, incoming, both)

        Returns:
            Graph traversal result with nodes and relationships

        Example:
            >>> result = client.graph.traverse(
            ...     start_ids=["mem_123", "mem_456"],
            ...     depth=3,
            ...     direction=Direction.OUTGOING
            ... )
        """
        data = _build_traverse_data(start_ids, depth, relationship_types, direction)
        response = self._request("POST", "/graph/traverse", json=data)
        return GraphTraversal.model_validate(response)

    def get_context(self, query: str, depth: int = 2, semantic_limit: int = 10) -> GraphContext:
        """Get contextual graph around a semantic query.

        Args:
            query: Search query
            depth: Graph traversal depth
            semantic_limit: Maximum number of semantic matches

        Returns:
            Graph context with relevant memories and relationships

        Example:
            >>> context = client.graph.get_context(
            ...     query="machine learning projects",
            ...     depth=3
            ... )
        """
        data = {
            "query": query,
            "depth": depth,
            "semantic_limit": semantic_limit,
        }
        response = self._request("POST", "/graph/context", json=data)
        return GraphContext.model_validate(response)

    def shortest_path(
        self, source_id: str, target_id: str, max_hops: int = 10
    ) -> Optional[ShortestPath]:
        """Find shortest path between two memories.

        Args:
            source_id: Source memory ID
            target_id: Target memory ID
            max_hops: Maximum number of hops to search

        Returns:
            Shortest path result or None if no path exists

        Example:
            >>> path = client.graph.shortest_path(
            ...     source_id="mem_123",
            ...     target_id="mem_456",
            ...     max_hops=5
            ... )
        """
        data = _build_shortest_path_data(source_id, target_id, max_hops)
        response = self._request("POST", "/graph/shortest-path", json=data)
        if response:
            return ShortestPath.model_validate(response)
        return None

    def neighbors(self, node_id: str) -> GraphNeighbors:
        """Get neighbors of a node in the graph.

        Args:
            node_id: Node ID (memory ID)

        Returns:
            Graph neighbors with incoming and outgoing connections

        Example:
            >>> neighbors = client.graph.neighbors("mem_123")
            >>> print(f"Incoming: {len(neighbors.incoming)}")
            >>> print(f"Outgoing: {len(neighbors.outgoing)}")
        """
        validate_id(node_id, "node")
        response = self._request("GET", f"/graph/neighbors/{node_id}")
        return GraphNeighbors.model_validate(response)

    def get_stats(self) -> GraphStats:
        """Get graph statistics.

        Returns:
            Statistics about the knowledge graph

        Example:
            >>> stats = client.graph.get_stats()
            >>> print(f"Total nodes: {stats.total_nodes}")
            >>> print(f"Total edges: {stats.total_edges}")
        """
        response = self._request("GET", "/graph/stats")
        return GraphStats.model_validate(response)


class AsyncGraphResource(BaseAsyncResource):
    """Async resource for graph traversal and analysis.

    Example:
        >>> result = await client.graph.traverse(["mem_123"], depth=3)
        >>> path = await client.graph.shortest_path("mem_123", "mem_456")
    """

    async def traverse(
        self,
        start_ids: List[str],
        depth: int = 2,
        relationship_types: Optional[List[RelationshipType]] = None,
        direction: Direction = Direction.BOTH,
    ) -> GraphTraversal:
        """Traverse the memory graph from starting points (async).

        Args:
            start_ids: List of starting memory IDs
            depth: Maximum traversal depth
            relationship_types: Filter by relationship types
            direction: Traversal direction

        Returns:
            Graph traversal result with nodes and relationships
        """
        data = _build_traverse_data(start_ids, depth, relationship_types, direction)
        response = await self._request("POST", "/graph/traverse", json=data)
        return GraphTraversal.model_validate(response)

    async def get_context(
        self, query: str, depth: int = 2, semantic_limit: int = 10
    ) -> GraphContext:
        """Get contextual graph around a semantic query (async).

        Args:
            query: Search query
            depth: Graph traversal depth
            semantic_limit: Maximum number of semantic matches

        Returns:
            Graph context with relevant memories and relationships
        """
        data = {
            "query": query,
            "depth": depth,
            "semantic_limit": semantic_limit,
        }
        response = await self._request("POST", "/graph/context", json=data)
        return GraphContext.model_validate(response)

    async def shortest_path(
        self, source_id: str, target_id: str, max_hops: int = 10
    ) -> Optional[ShortestPath]:
        """Find shortest path between two memories (async).

        Args:
            source_id: Source memory ID
            target_id: Target memory ID
            max_hops: Maximum number of hops

        Returns:
            Shortest path result or None if no path exists
        """
        data = _build_shortest_path_data(source_id, target_id, max_hops)
        response = await self._request("POST", "/graph/shortest-path", json=data)
        if response:
            return ShortestPath.model_validate(response)
        return None

    async def neighbors(self, node_id: str) -> GraphNeighbors:
        """Get neighbors of a node in the graph (async).

        Args:
            node_id: Node ID (memory ID)

        Returns:
            Graph neighbors with incoming and outgoing connections
        """
        validate_id(node_id, "node")
        response = await self._request("GET", f"/graph/neighbors/{node_id}")
        return GraphNeighbors.model_validate(response)

    async def get_stats(self) -> GraphStats:
        """Get graph statistics (async).

        Returns:
            Statistics about the knowledge graph
        """
        response = await self._request("GET", "/graph/stats")
        return GraphStats.model_validate(response)
