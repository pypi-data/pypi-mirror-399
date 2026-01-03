"""Clusters resource for Trix SDK."""

from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional

from ..protocols import AsyncClientProtocol, SyncClientProtocol
from ..types import (
    Cluster,
    ClusterCreate,
    ClusterList,
    ClusterMembership,
    ClusterUpdate,
)
from ..utils.pagination import AsyncPaginator, SyncPaginator
from ..utils.security import validate_id, validate_limit, validate_threshold

if TYPE_CHECKING:
    from ..types import ClusterQuality, ClusterStats, ClusterTopics, IncrementalClusterResult


class ClustersResource:
    """Resource for managing clusters."""

    def __init__(self, client: SyncClientProtocol) -> None:
        """Initialize clusters resource with client."""
        self._client = client

    def create(
        self,
        name: str,
        description: Optional[str] = None,
        color: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Cluster:
        """
        Create a new cluster.

        Args:
            name: Cluster name
            description: Optional description
            color: Optional color code
            metadata: Additional metadata

        Returns:
            Created cluster object

        Example:
            >>> cluster = client.clusters.create(
            ...     name="Work Projects",
            ...     description="All work-related memories",
            ...     color="#FF5733"
            ... )
        """
        data = ClusterCreate(
            name=name,
            description=description,
            color=color,
            metadata=metadata,
        )
        response = self._client._request(
            "POST", "/clusters", json=data.model_dump(exclude_none=True)
        )
        return Cluster.model_validate(response)

    def list(
        self,
        q: Optional[str] = None,
        sort: Optional[str] = None,
        limit: int = 100,
        cursor: Optional[str] = None,
    ) -> ClusterList:
        """
        List clusters with optional filtering.

        Args:
            q: Search query
            sort: Sort field
            limit: Maximum number of results
            cursor: Pagination cursor

        Returns:
            List of clusters with pagination

        Example:
            >>> clusters = client.clusters.list(q="work", limit=50)
        """
        params: Dict[str, Any] = {"limit": limit}
        if q:
            params["q"] = q
        if sort:
            params["sort"] = sort
        if cursor:
            params["cursor"] = cursor

        response = self._client._request("GET", "/clusters", params=params)
        return ClusterList.model_validate(response)

    def iter(
        self,
        q: Optional[str] = None,
        sort: Optional[str] = None,
        page_size: int = 100,
        max_items: Optional[int] = None,
    ) -> Iterator[Cluster]:
        """
        Iterate through all clusters with automatic pagination.

        Args:
            q: Search query
            sort: Sort field
            page_size: Number of items per page
            max_items: Maximum total items to fetch

        Yields:
            Cluster objects

        Example:
            >>> for cluster in client.clusters.iter():
            ...     print(cluster.name)
        """
        params: Dict[str, Any] = {}
        if q:
            params["q"] = q
        if sort:
            params["sort"] = sort

        paginator = SyncPaginator(
            self.list,
            initial_params=params,
            limit=page_size,
            max_items=max_items,
        )
        for item in paginator:
            yield Cluster.model_validate(item)

    def get(self, id: str) -> Cluster:
        """
        Get a cluster by ID.

        Args:
            id: Cluster ID

        Returns:
            Cluster object

        Example:
            >>> cluster = client.clusters.get("cluster_123")
        """
        validate_id(id, "cluster")
        response = self._client._request("GET", f"/clusters/{id}")
        return Cluster.model_validate(response)

    def update(
        self,
        id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        color: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Cluster:
        """
        Update a cluster.

        Args:
            id: Cluster ID
            name: New name
            description: New description
            color: New color
            metadata: New metadata

        Returns:
            Updated cluster object

        Example:
            >>> cluster = client.clusters.update(
            ...     "cluster_123",
            ...     name="Updated Name"
            ... )
        """
        validate_id(id, "cluster")
        data = ClusterUpdate(
            name=name,
            description=description,
            color=color,
            metadata=metadata,
        )
        response = self._client._request(
            "PATCH", f"/clusters/{id}", json=data.model_dump(exclude_none=True)
        )
        return Cluster.model_validate(response)

    def delete(self, id: str) -> None:
        """
        Delete a cluster.

        Args:
            id: Cluster ID

        Example:
            >>> client.clusters.delete("cluster_123")
        """
        validate_id(id, "cluster")
        self._client._request("DELETE", f"/clusters/{id}")

    def bulk_create(self, clusters: List[ClusterCreate]) -> List[Cluster]:
        """
        Create multiple clusters at once.

        Args:
            clusters: List of cluster creation requests

        Returns:
            List of created clusters

        Example:
            >>> clusters = client.clusters.bulk_create([
            ...     ClusterCreate(name="Cluster 1"),
            ...     ClusterCreate(name="Cluster 2"),
            ... ])
        """
        data = [c.model_dump(exclude_none=True) for c in clusters]
        response = self._client._request("POST", "/clusters/bulk", json={"clusters": data})
        return [Cluster.model_validate(c) for c in response.get("data", [])]

    def bulk_update(self, updates: List[Dict[str, Any]]) -> List[Cluster]:
        """
        Update multiple clusters at once.

        Args:
            updates: List of update objects with 'id' and update fields

        Returns:
            List of updated clusters

        Example:
            >>> clusters = client.clusters.bulk_update([
            ...     {"id": "cluster_123", "name": "New Name"},
            ...     {"id": "cluster_456", "color": "#FF0000"},
            ... ])
        """
        # Validate all IDs before making the request
        for i, update in enumerate(updates):
            if "id" not in update:
                raise ValueError(f"Update at index {i} is missing an 'id'")
            validate_id(update["id"], f"cluster[{i}]")
        response = self._client._request("PATCH", "/clusters/bulk", json={"updates": updates})
        return [Cluster.model_validate(c) for c in response.get("data", [])]

    def bulk_delete(self, ids: List[str]) -> None:
        """
        Delete multiple clusters at once.

        Args:
            ids: List of cluster IDs to delete

        Example:
            >>> client.clusters.bulk_delete(["cluster_123", "cluster_456"])
        """
        # Validate all IDs before making the request
        for i, item_id in enumerate(ids):
            validate_id(item_id, f"cluster[{i}]")
        self._client._request("DELETE", "/clusters/bulk", json={"ids": ids})

    def add_memory(
        self, cluster_id: str, memory_id: str, confidence: float = 1.0
    ) -> ClusterMembership:
        """
        Add a memory to a cluster.

        Args:
            cluster_id: Cluster ID
            memory_id: Memory ID
            confidence: Confidence score for membership (0.0-1.0)

        Returns:
            Cluster membership object

        Example:
            >>> membership = client.clusters.add_memory(
            ...     "cluster_123",
            ...     "mem_456",
            ...     confidence=0.95
            ... )
        """
        validate_id(cluster_id, "cluster")
        validate_id(memory_id, "memory")
        validate_threshold(confidence, param_name="confidence")
        response = self._client._request(
            "POST",
            f"/clusters/{cluster_id}/memories/{memory_id}",
            json={"confidence": confidence},
        )
        return ClusterMembership.model_validate(response)

    def remove_memory(self, cluster_id: str, memory_id: str) -> None:
        """
        Remove a memory from a cluster.

        Args:
            cluster_id: Cluster ID
            memory_id: Memory ID

        Example:
            >>> client.clusters.remove_memory("cluster_123", "mem_456")
        """
        validate_id(cluster_id, "cluster")
        validate_id(memory_id, "memory")
        self._client._request("DELETE", f"/clusters/{cluster_id}/memories/{memory_id}")

    def expand(
        self, cluster_id: str, limit: int = 10, threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Expand a cluster by finding similar memories.

        Args:
            cluster_id: Cluster ID
            limit: Maximum number of suggestions (1-100)
            threshold: Similarity threshold (0.0-1.0)

        Returns:
            List of suggested memories with similarity scores

        Example:
            >>> suggestions = client.clusters.expand("cluster_123", limit=20)
        """
        validate_id(cluster_id, "cluster")
        validate_limit(limit, max_limit=100)
        validate_threshold(threshold)
        params = {"limit": limit, "threshold": threshold}
        response = self._client._request("POST", f"/clusters/{cluster_id}/expand", params=params)
        return list(response.get("suggestions", []))

    def get_stats(self) -> "ClusterStats":
        """Get cluster statistics."""
        from ..types import ClusterStats

        response = self._client._request("GET", "/clusters/stats")
        return ClusterStats.model_validate(response)

    def incremental_clustering(
        self,
        space_id: Optional[str] = None,
        threshold: Optional[float] = None,
        max_new_clusters: Optional[int] = None,
    ) -> "IncrementalClusterResult":
        """Trigger incremental clustering."""
        from ..types import IncrementalClusterResult

        params: Dict[str, Any] = {}
        if space_id:
            params["space_id"] = space_id
        if threshold is not None:
            params["threshold"] = threshold
        if max_new_clusters is not None:
            params["max_new_clusters"] = max_new_clusters
        response = self._client._request("POST", "/clusters/incremental", json=params)
        return IncrementalClusterResult.model_validate(response)

    def refresh_metrics(self, cluster_id: str) -> Cluster:
        """Refresh quality metrics for a cluster."""
        validate_id(cluster_id, "cluster")
        response = self._client._request("POST", f"/clusters/{cluster_id}/refresh-metrics")
        return Cluster.model_validate(response)

    def recompute_centroid(self, cluster_id: str) -> Cluster:
        """Recompute centroid for a cluster."""
        validate_id(cluster_id, "cluster")
        response = self._client._request("POST", f"/clusters/{cluster_id}/recompute-centroid")
        return Cluster.model_validate(response)

    def get_quality(self, cluster_id: str) -> "ClusterQuality":
        """Get quality metrics for a cluster."""
        from ..types import ClusterQuality

        validate_id(cluster_id, "cluster")
        response = self._client._request("GET", f"/clusters/{cluster_id}/quality")
        return ClusterQuality.model_validate(response)

    def get_topics(self, cluster_id: str) -> "ClusterTopics":
        """Get topics for a cluster."""
        from ..types import ClusterTopics

        validate_id(cluster_id, "cluster")
        response = self._client._request("GET", f"/clusters/{cluster_id}/topics")
        return ClusterTopics.model_validate(response)


class AsyncClustersResource:
    """Async resource for managing clusters."""

    def __init__(self, client: AsyncClientProtocol) -> None:
        """Initialize async clusters resource with client."""
        self._client = client

    async def create(
        self,
        name: str,
        description: Optional[str] = None,
        color: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Cluster:
        """Create a new cluster (async)."""
        data = ClusterCreate(
            name=name,
            description=description,
            color=color,
            metadata=metadata,
        )
        response = await self._client._request(
            "POST", "/clusters", json=data.model_dump(exclude_none=True)
        )
        return Cluster.model_validate(response)

    async def list(
        self,
        q: Optional[str] = None,
        sort: Optional[str] = None,
        limit: int = 100,
        cursor: Optional[str] = None,
    ) -> ClusterList:
        """List clusters with optional filtering (async)."""
        params: Dict[str, Any] = {"limit": limit}
        if q:
            params["q"] = q
        if sort:
            params["sort"] = sort
        if cursor:
            params["cursor"] = cursor

        response = await self._client._request("GET", "/clusters", params=params)
        return ClusterList.model_validate(response)

    async def iter(
        self,
        q: Optional[str] = None,
        sort: Optional[str] = None,
        page_size: int = 100,
        max_items: Optional[int] = None,
    ) -> AsyncPaginator:
        """Get async iterator for all clusters with automatic pagination."""
        params: Dict[str, Any] = {}
        if q:
            params["q"] = q
        if sort:
            params["sort"] = sort

        return AsyncPaginator(
            self.list,
            initial_params=params,
            limit=page_size,
            max_items=max_items,
        )

    async def get(self, id: str) -> Cluster:
        """Get a cluster by ID (async)."""
        validate_id(id, "cluster")
        response = await self._client._request("GET", f"/clusters/{id}")
        return Cluster.model_validate(response)

    async def update(
        self,
        id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        color: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Cluster:
        """Update a cluster (async)."""
        validate_id(id, "cluster")
        data = ClusterUpdate(
            name=name,
            description=description,
            color=color,
            metadata=metadata,
        )
        response = await self._client._request(
            "PATCH", f"/clusters/{id}", json=data.model_dump(exclude_none=True)
        )
        return Cluster.model_validate(response)

    async def delete(self, id: str) -> None:
        """Delete a cluster (async)."""
        validate_id(id, "cluster")
        await self._client._request("DELETE", f"/clusters/{id}")

    async def bulk_create(self, clusters: List[ClusterCreate]) -> List[Cluster]:
        """Create multiple clusters at once (async)."""
        data = [c.model_dump(exclude_none=True) for c in clusters]
        response = await self._client._request("POST", "/clusters/bulk", json={"clusters": data})
        return [Cluster.model_validate(c) for c in response.get("data", [])]

    async def bulk_update(self, updates: List[Dict[str, Any]]) -> List[Cluster]:
        """Update multiple clusters at once (async)."""
        # Validate all IDs before making the request
        for i, update in enumerate(updates):
            if "id" not in update:
                raise ValueError(f"Update at index {i} is missing an 'id'")
            validate_id(update["id"], f"cluster[{i}]")
        response = await self._client._request("PATCH", "/clusters/bulk", json={"updates": updates})
        return [Cluster.model_validate(c) for c in response.get("data", [])]

    async def bulk_delete(self, ids: List[str]) -> None:
        """Delete multiple clusters at once (async)."""
        # Validate all IDs before making the request
        for i, item_id in enumerate(ids):
            validate_id(item_id, f"cluster[{i}]")
        await self._client._request("DELETE", "/clusters/bulk", json={"ids": ids})

    async def add_memory(
        self, cluster_id: str, memory_id: str, confidence: float = 1.0
    ) -> ClusterMembership:
        """Add a memory to a cluster (async)."""
        validate_id(cluster_id, "cluster")
        validate_id(memory_id, "memory")
        validate_threshold(confidence, param_name="confidence")
        response = await self._client._request(
            "POST",
            f"/clusters/{cluster_id}/memories/{memory_id}",
            json={"confidence": confidence},
        )
        return ClusterMembership.model_validate(response)

    async def remove_memory(self, cluster_id: str, memory_id: str) -> None:
        """Remove a memory from a cluster (async)."""
        validate_id(cluster_id, "cluster")
        validate_id(memory_id, "memory")
        await self._client._request("DELETE", f"/clusters/{cluster_id}/memories/{memory_id}")

    async def expand(
        self, cluster_id: str, limit: int = 10, threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Expand a cluster by finding similar memories (async)."""
        validate_id(cluster_id, "cluster")
        validate_limit(limit, max_limit=100)
        validate_threshold(threshold)
        params = {"limit": limit, "threshold": threshold}
        response = await self._client._request(
            "POST", f"/clusters/{cluster_id}/expand", params=params
        )
        return list(response.get("suggestions", []))

    async def get_stats(self) -> "ClusterStats":
        """Get cluster statistics (async)."""
        from ..types import ClusterStats

        response = await self._client._request("GET", "/clusters/stats")
        return ClusterStats.model_validate(response)

    async def incremental_clustering(
        self,
        space_id: Optional[str] = None,
        threshold: Optional[float] = None,
        max_new_clusters: Optional[int] = None,
    ) -> "IncrementalClusterResult":
        """Trigger incremental clustering (async)."""
        from ..types import IncrementalClusterResult

        params: Dict[str, Any] = {}
        if space_id:
            params["space_id"] = space_id
        if threshold is not None:
            params["threshold"] = threshold
        if max_new_clusters is not None:
            params["max_new_clusters"] = max_new_clusters
        response = await self._client._request("POST", "/clusters/incremental", json=params)
        return IncrementalClusterResult.model_validate(response)

    async def refresh_metrics(self, cluster_id: str) -> Cluster:
        """Refresh quality metrics for a cluster (async)."""
        validate_id(cluster_id, "cluster")
        response = await self._client._request("POST", f"/clusters/{cluster_id}/refresh-metrics")
        return Cluster.model_validate(response)

    async def recompute_centroid(self, cluster_id: str) -> Cluster:
        """Recompute centroid for a cluster (async)."""
        validate_id(cluster_id, "cluster")
        response = await self._client._request("POST", f"/clusters/{cluster_id}/recompute-centroid")
        return Cluster.model_validate(response)

    async def get_quality(self, cluster_id: str) -> "ClusterQuality":
        """Get quality metrics for a cluster (async)."""
        from ..types import ClusterQuality

        validate_id(cluster_id, "cluster")
        response = await self._client._request("GET", f"/clusters/{cluster_id}/quality")
        return ClusterQuality.model_validate(response)

    async def get_topics(self, cluster_id: str) -> "ClusterTopics":
        """Get topics for a cluster (async)."""
        from ..types import ClusterTopics

        validate_id(cluster_id, "cluster")
        response = await self._client._request("GET", f"/clusters/{cluster_id}/topics")
        return ClusterTopics.model_validate(response)
