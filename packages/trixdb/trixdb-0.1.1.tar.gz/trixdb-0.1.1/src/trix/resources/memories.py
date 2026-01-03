"""Memories resource for Trix SDK."""

import json
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    BinaryIO,
    Dict,
    Iterator,
    List,
    Optional,
    Union,
)

from ..protocols import AsyncClientProtocol, SyncClientProtocol
from ..types import (
    Memory,
    MemoryConfig,
    MemoryCreate,
    MemoryList,
    MemoryOptions,
    MemoryType,
    MemoryUpdate,
    SearchMode,
)
from ..utils.pagination import AsyncPaginator, SyncPaginator
from ..utils.security import validate_id

if TYPE_CHECKING:
    from ..types import MemoryStats


class MemoriesResource:
    """Resource for managing memories."""

    def __init__(self, client: SyncClientProtocol) -> None:
        """Initialize memories resource with client."""
        self._client = client

    def create(
        self,
        content: str,
        type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        priority: Optional[int] = None,
        space_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Memory:
        """
        Create a new memory.

        Args:
            content: The content of the memory
            type: Type of memory (text, markdown, url, audio)
            tags: List of tags for categorization
            metadata: Additional metadata
            priority: Priority level for the memory
            space_id: ID of the space to add memory to
            options: Additional options (transcribe_audio, language, skip_embedding)

        Returns:
            Created memory object

        Example:
            >>> memory = client.memories.create(
            ...     content="Important information",
            ...     tags=["work", "important"],
            ...     metadata={"source": "meeting"}
            ... )
        """
        data = MemoryCreate(
            content=content,
            type=type or MemoryType.TEXT,
            tags=tags,
            metadata=metadata,
            priority=priority,
            space_id=space_id,
            options=MemoryOptions(**options) if options else None,
        )
        response = self._client._request(
            "POST", "/memories", json=data.model_dump(exclude_none=True)
        )
        return Memory.model_validate(response)

    def list(
        self,
        q: Optional[str] = None,
        mode: Optional[SearchMode] = None,
        limit: int = 100,
        offset: int = 0,
        tags: Optional[List[str]] = None,
        space_id: Optional[str] = None,
    ) -> MemoryList:
        """
        List memories with optional filtering.

        Args:
            q: Search query
            mode: Search mode (semantic, keyword, hybrid)
            limit: Maximum number of results
            offset: Offset for pagination
            tags: Filter by tags
            space_id: Filter by space

        Returns:
            List of memories with pagination info

        Example:
            >>> results = client.memories.list(
            ...     q="important",
            ...     mode=SearchMode.HYBRID,
            ...     tags=["work"]
            ... )
        """
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if q:
            params["q"] = q
        if mode:
            params["mode"] = mode.value
        if tags:
            params["tags"] = ",".join(tags)
        if space_id:
            params["space_id"] = space_id

        response = self._client._request("GET", "/memories", params=params)
        return MemoryList.model_validate(response)

    def iter(
        self,
        q: Optional[str] = None,
        mode: Optional[SearchMode] = None,
        tags: Optional[List[str]] = None,
        space_id: Optional[str] = None,
        page_size: int = 100,
        max_items: Optional[int] = None,
    ) -> Iterator[Memory]:
        """
        Iterate through all memories with automatic pagination.

        Args:
            q: Search query
            mode: Search mode
            tags: Filter by tags
            space_id: Filter by space
            page_size: Number of items per page
            max_items: Maximum total items to fetch

        Yields:
            Memory objects

        Example:
            >>> for memory in client.memories.iter(tags=["work"]):
            ...     print(memory.content)
        """
        params: Dict[str, Any] = {}
        if q:
            params["q"] = q
        if mode:
            params["mode"] = mode.value
        if tags:
            params["tags"] = ",".join(tags)
        if space_id:
            params["space_id"] = space_id

        paginator = SyncPaginator(
            self.list,
            initial_params=params,
            limit=page_size,
            max_items=max_items,
        )
        for item in paginator:
            yield Memory.model_validate(item)

    def get(self, id: str) -> Memory:
        """
        Get a memory by ID.

        Args:
            id: Memory ID

        Returns:
            Memory object

        Example:
            >>> memory = client.memories.get("mem_123")
        """
        validate_id(id, "memory")
        response = self._client._request("GET", f"/memories/{id}")
        return Memory.model_validate(response)

    def update(
        self,
        id: str,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        priority: Optional[int] = None,
    ) -> Memory:
        """
        Update a memory.

        Args:
            id: Memory ID
            content: New content
            tags: New tags
            metadata: New metadata
            priority: New priority

        Returns:
            Updated memory object

        Example:
            >>> memory = client.memories.update(
            ...     "mem_123",
            ...     tags=["updated", "important"]
            ... )
        """
        validate_id(id, "memory")
        data = MemoryUpdate(
            content=content,
            tags=tags,
            metadata=metadata,
            priority=priority,
        )
        response = self._client._request(
            "PATCH", f"/memories/{id}", json=data.model_dump(exclude_none=True)
        )
        return Memory.model_validate(response)

    def delete(self, id: str) -> None:
        """
        Delete a memory.

        Args:
            id: Memory ID

        Example:
            >>> client.memories.delete("mem_123")
        """
        validate_id(id, "memory")
        self._client._request("DELETE", f"/memories/{id}")

    def bulk_create(self, memories: List[MemoryCreate]) -> List[Memory]:
        """
        Create multiple memories at once.

        Args:
            memories: List of memory creation requests

        Returns:
            List of created memories

        Example:
            >>> memories = client.memories.bulk_create([
            ...     MemoryCreate(content="First memory"),
            ...     MemoryCreate(content="Second memory"),
            ... ])
        """
        data = [m.model_dump(exclude_none=True) for m in memories]
        response = self._client._request("POST", "/memories/bulk", json={"memories": data})
        return [Memory.model_validate(m) for m in response.get("data", [])]

    def bulk_update(self, updates: List[Dict[str, Any]]) -> List[Memory]:
        """
        Update multiple memories at once.

        Args:
            updates: List of update objects with 'id' and update fields

        Returns:
            List of updated memories

        Example:
            >>> memories = client.memories.bulk_update([
            ...     {"id": "mem_123", "tags": ["updated"]},
            ...     {"id": "mem_456", "priority": 5},
            ... ])
        """
        # Validate all IDs before making the request
        for i, update in enumerate(updates):
            if "id" not in update:
                raise ValueError(f"Update at index {i} is missing an 'id'")
            validate_id(update["id"], f"memory[{i}]")
        response = self._client._request("PATCH", "/memories/bulk", json={"updates": updates})
        return [Memory.model_validate(m) for m in response.get("data", [])]

    def bulk_delete(self, ids: List[str]) -> None:
        """
        Delete multiple memories at once.

        Args:
            ids: List of memory IDs to delete

        Example:
            >>> client.memories.bulk_delete(["mem_123", "mem_456"])
        """
        # Validate all IDs before making the request
        for i, item_id in enumerate(ids):
            validate_id(item_id, f"memory[{i}]")
        self._client._request("DELETE", "/memories/bulk", json={"ids": ids})

    def get_config(self) -> MemoryConfig:
        """
        Get memory system configuration.

        Returns:
            Memory configuration

        Example:
            >>> config = client.memories.get_config()
            >>> print(config.max_content_length)
        """
        response = self._client._request("GET", "/memories/config")
        return MemoryConfig.model_validate(response)

    def stream_audio(self, id: str) -> bytes:
        """
        Get audio content for an audio memory.

        Args:
            id: Memory ID

        Returns:
            Audio data as bytes

        Example:
            >>> audio_data = client.memories.stream_audio("mem_123")
        """
        validate_id(id, "memory")
        return self._client._request_raw("GET", f"/memories/{id}/audio")

    def stream_audio_chunks(self, id: str, chunk_size: int = 8192) -> Iterator[bytes]:
        """
        Stream audio content in chunks for efficient memory usage.

        Args:
            id: Memory ID
            chunk_size: Size of each chunk in bytes

        Yields:
            Chunks of audio data

        Example:
            >>> with open("audio.mp3", "wb") as f:
            ...     for chunk in client.memories.stream_audio_chunks("mem_123"):
            ...         f.write(chunk)
        """
        validate_id(id, "memory")
        return self._client._request_stream("GET", f"/memories/{id}/audio", chunk_size=chunk_size)

    def create_with_audio(
        self,
        audio_file: Union[BinaryIO, Path, str],
        filename: Optional[str] = None,
        content_type: str = "audio/mpeg",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        space_id: Optional[str] = None,
        transcribe: bool = True,
        language: Optional[str] = None,
    ) -> Memory:
        """
        Create a memory from an audio file.

        Args:
            audio_file: File object, path, or string path to the audio file
            filename: Override filename (default: extracted from path or "audio")
            content_type: MIME type of the audio file
            tags: List of tags for categorization
            metadata: Additional metadata
            space_id: ID of the space to add memory to
            transcribe: Whether to transcribe the audio
            language: Language code for transcription

        Returns:
            Created memory object

        Example:
            >>> memory = client.memories.create_with_audio(
            ...     "recording.mp3",
            ...     tags=["meeting", "important"],
            ...     transcribe=True
            ... )
        """
        # Handle different input types
        file_handle: BinaryIO
        if isinstance(audio_file, (str, Path)):
            path = Path(audio_file)
            filename = filename or path.name
            file_handle = open(path, "rb")
            should_close = True
        else:
            filename = filename or "audio"
            file_handle = audio_file
            should_close = False

        try:
            # Build form data
            data: Dict[str, Any] = {"type": "audio"}
            if tags:
                data["tags"] = ",".join(tags)
            if metadata:
                data["metadata"] = json.dumps(metadata)
            if space_id:
                data["space_id"] = space_id
            if transcribe:
                data["transcribe"] = "true"
            if language:
                data["language"] = language

            files: Dict[str, Any] = {"file": (filename, file_handle, content_type)}

            response = self._client._request_multipart("POST", "/memories", data=data, files=files)
            return Memory.model_validate(response)
        finally:
            if should_close:
                file_handle.close()

    def get_transcript(self, id: str) -> str:
        """
        Get transcript for an audio memory.

        Args:
            id: Memory ID

        Returns:
            Transcript text

        Example:
            >>> transcript = client.memories.get_transcript("mem_123")
        """
        validate_id(id, "memory")
        response = self._client._request("GET", f"/memories/{id}/transcript")
        return str(response.get("transcript", ""))

    def transcribe(self, id: str, language: Optional[str] = None, force: bool = False) -> str:
        """
        Transcribe or re-transcribe an audio memory.

        Args:
            id: Memory ID
            language: Language code for transcription
            force: Force re-transcription even if transcript exists

        Returns:
            Transcript text

        Example:
            >>> transcript = client.memories.transcribe("mem_123", language="en")
        """
        validate_id(id, "memory")
        params: Dict[str, Any] = {}
        if language:
            params["language"] = language
        if force:
            params["force"] = "true"

        response = self._client._request("POST", f"/memories/{id}/transcribe", params=params)
        return str(response.get("transcript", ""))

    def get_stats(
        self,
        space_id: Optional[str] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
        include_type_distribution: bool = False,
        include_tag_distribution: bool = False,
        include_timeline: bool = False,
        timeline_granularity: Optional[str] = None,
    ) -> "MemoryStats":
        """
        Get memory statistics.

        Args:
            space_id: Filter by space ID
            created_after: Filter by creation date (ISO format)
            created_before: Filter by creation date (ISO format)
            include_type_distribution: Include type distribution in stats
            include_tag_distribution: Include tag distribution in stats
            include_timeline: Include timeline in stats
            timeline_granularity: Timeline granularity (hour, day, week, month)

        Returns:
            Memory statistics

        Example:
            >>> stats = client.memories.get_stats(include_type_distribution=True)
            >>> print(f"Total memories: {stats.total}")
        """
        from ..types import MemoryStats

        params: Dict[str, Any] = {}
        if space_id:
            params["space_id"] = space_id
        if created_after:
            params["created_after"] = created_after
        if created_before:
            params["created_before"] = created_before
        if include_type_distribution:
            params["include_type_distribution"] = "true"
        if include_tag_distribution:
            params["include_tag_distribution"] = "true"
        if include_timeline:
            params["include_timeline"] = "true"
        if timeline_granularity:
            params["timeline_granularity"] = timeline_granularity

        response = self._client._request("GET", "/memories/stats", params=params)
        return MemoryStats.model_validate(response)


class AsyncMemoriesResource:
    """Async resource for managing memories."""

    def __init__(self, client: AsyncClientProtocol) -> None:
        """Initialize async memories resource with client."""
        self._client = client

    async def create(
        self,
        content: str,
        type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        priority: Optional[int] = None,
        space_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Memory:
        """Create a new memory (async)."""
        data = MemoryCreate(
            content=content,
            type=type or MemoryType.TEXT,
            tags=tags,
            metadata=metadata,
            priority=priority,
            space_id=space_id,
            options=MemoryOptions(**options) if options else None,
        )
        response = await self._client._request(
            "POST", "/memories", json=data.model_dump(exclude_none=True)
        )
        return Memory.model_validate(response)

    async def list(
        self,
        q: Optional[str] = None,
        mode: Optional[SearchMode] = None,
        limit: int = 100,
        offset: int = 0,
        tags: Optional[List[str]] = None,
        space_id: Optional[str] = None,
    ) -> MemoryList:
        """List memories with optional filtering (async)."""
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if q:
            params["q"] = q
        if mode:
            params["mode"] = mode.value
        if tags:
            params["tags"] = ",".join(tags)
        if space_id:
            params["space_id"] = space_id

        response = await self._client._request("GET", "/memories", params=params)
        return MemoryList.model_validate(response)

    async def iter(
        self,
        q: Optional[str] = None,
        mode: Optional[SearchMode] = None,
        tags: Optional[List[str]] = None,
        space_id: Optional[str] = None,
        page_size: int = 100,
        max_items: Optional[int] = None,
    ) -> AsyncPaginator:
        """
        Get async iterator for all memories with automatic pagination.

        Returns:
            Async paginator that yields Memory objects

        Example:
            >>> async for memory in await client.memories.iter(tags=["work"]):
            ...     print(memory.content)
        """
        params: Dict[str, Any] = {}
        if q:
            params["q"] = q
        if mode:
            params["mode"] = mode.value
        if tags:
            params["tags"] = ",".join(tags)
        if space_id:
            params["space_id"] = space_id

        return AsyncPaginator(
            self.list,
            initial_params=params,
            limit=page_size,
            max_items=max_items,
        )

    async def get(self, id: str) -> Memory:
        """Get a memory by ID (async)."""
        validate_id(id, "memory")
        response = await self._client._request("GET", f"/memories/{id}")
        return Memory.model_validate(response)

    async def update(
        self,
        id: str,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        priority: Optional[int] = None,
    ) -> Memory:
        """Update a memory (async)."""
        validate_id(id, "memory")
        data = MemoryUpdate(
            content=content,
            tags=tags,
            metadata=metadata,
            priority=priority,
        )
        response = await self._client._request(
            "PATCH", f"/memories/{id}", json=data.model_dump(exclude_none=True)
        )
        return Memory.model_validate(response)

    async def delete(self, id: str) -> None:
        """Delete a memory (async)."""
        validate_id(id, "memory")
        await self._client._request("DELETE", f"/memories/{id}")

    async def bulk_create(self, memories: List[MemoryCreate]) -> List[Memory]:
        """Create multiple memories at once (async)."""
        data = [m.model_dump(exclude_none=True) for m in memories]
        response = await self._client._request("POST", "/memories/bulk", json={"memories": data})
        return [Memory.model_validate(m) for m in response.get("data", [])]

    async def bulk_update(self, updates: List[Dict[str, Any]]) -> List[Memory]:
        """Update multiple memories at once (async)."""
        # Validate all IDs before making the request
        for i, update in enumerate(updates):
            if "id" not in update:
                raise ValueError(f"Update at index {i} is missing an 'id'")
            validate_id(update["id"], f"memory[{i}]")
        response = await self._client._request("PATCH", "/memories/bulk", json={"updates": updates})
        return [Memory.model_validate(m) for m in response.get("data", [])]

    async def bulk_delete(self, ids: List[str]) -> None:
        """Delete multiple memories at once (async)."""
        # Validate all IDs before making the request
        for i, item_id in enumerate(ids):
            validate_id(item_id, f"memory[{i}]")
        await self._client._request("DELETE", "/memories/bulk", json={"ids": ids})

    async def get_config(self) -> MemoryConfig:
        """Get memory system configuration (async)."""
        response = await self._client._request("GET", "/memories/config")
        return MemoryConfig.model_validate(response)

    async def stream_audio(self, id: str) -> bytes:
        """Get audio content for an audio memory (async)."""
        validate_id(id, "memory")
        return await self._client._request_raw("GET", f"/memories/{id}/audio")

    async def stream_audio_chunks(self, id: str, chunk_size: int = 8192) -> AsyncIterator[bytes]:
        """
        Stream audio content in chunks for efficient memory usage (async).

        Args:
            id: Memory ID
            chunk_size: Size of each chunk in bytes

        Yields:
            Chunks of audio data

        Example:
            >>> async with aiofiles.open("audio.mp3", "wb") as f:
            ...     async for chunk in client.memories.stream_audio_chunks("mem_123"):
            ...         await f.write(chunk)
        """
        validate_id(id, "memory")
        stream = self._client._request_stream("GET", f"/memories/{id}/audio", chunk_size=chunk_size)
        async for chunk in stream:
            yield chunk

    async def create_with_audio(
        self,
        audio_file: Union[BinaryIO, Path, str],
        filename: Optional[str] = None,
        content_type: str = "audio/mpeg",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        space_id: Optional[str] = None,
        transcribe: bool = True,
        language: Optional[str] = None,
    ) -> Memory:
        """
        Create a memory from an audio file (async).

        Args:
            audio_file: File object, path, or string path to the audio file
            filename: Override filename (default: extracted from path or "audio")
            content_type: MIME type of the audio file
            tags: List of tags for categorization
            metadata: Additional metadata
            space_id: ID of the space to add memory to
            transcribe: Whether to transcribe the audio
            language: Language code for transcription

        Returns:
            Created memory object

        Example:
            >>> memory = await client.memories.create_with_audio(
            ...     "recording.mp3",
            ...     tags=["meeting", "important"],
            ...     transcribe=True
            ... )
        """
        # Handle different input types
        file_handle: BinaryIO
        if isinstance(audio_file, (str, Path)):
            path = Path(audio_file)
            filename = filename or path.name
            file_handle = open(path, "rb")
            should_close = True
        else:
            filename = filename or "audio"
            file_handle = audio_file
            should_close = False

        try:
            # Build form data
            data: Dict[str, Any] = {"type": "audio"}
            if tags:
                data["tags"] = ",".join(tags)
            if metadata:
                data["metadata"] = json.dumps(metadata)
            if space_id:
                data["space_id"] = space_id
            if transcribe:
                data["transcribe"] = "true"
            if language:
                data["language"] = language

            files: Dict[str, Any] = {"file": (filename, file_handle, content_type)}

            response = await self._client._request_multipart(
                "POST", "/memories", data=data, files=files
            )
            return Memory.model_validate(response)
        finally:
            if should_close:
                file_handle.close()

    async def get_transcript(self, id: str) -> str:
        """Get transcript for an audio memory (async)."""
        validate_id(id, "memory")
        response = await self._client._request("GET", f"/memories/{id}/transcript")
        return str(response.get("transcript", ""))

    async def transcribe(self, id: str, language: Optional[str] = None, force: bool = False) -> str:
        """Transcribe or re-transcribe an audio memory (async)."""
        validate_id(id, "memory")
        params: Dict[str, Any] = {}
        if language:
            params["language"] = language
        if force:
            params["force"] = "true"

        response = await self._client._request("POST", f"/memories/{id}/transcribe", params=params)
        return str(response.get("transcript", ""))

    async def get_stats(
        self,
        space_id: Optional[str] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
        include_type_distribution: bool = False,
        include_tag_distribution: bool = False,
        include_timeline: bool = False,
        timeline_granularity: Optional[str] = None,
    ) -> "MemoryStats":
        """Get memory statistics (async)."""
        from ..types import MemoryStats

        params: Dict[str, Any] = {}
        if space_id:
            params["space_id"] = space_id
        if created_after:
            params["created_after"] = created_after
        if created_before:
            params["created_before"] = created_before
        if include_type_distribution:
            params["include_type_distribution"] = "true"
        if include_tag_distribution:
            params["include_tag_distribution"] = "true"
        if include_timeline:
            params["include_timeline"] = "true"
        if timeline_granularity:
            params["timeline_granularity"] = timeline_granularity

        response = await self._client._request("GET", "/memories/stats", params=params)
        return MemoryStats.model_validate(response)
