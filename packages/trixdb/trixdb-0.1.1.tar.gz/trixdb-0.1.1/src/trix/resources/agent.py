"""Agent resource for Trix SDK."""

from typing import Any, Dict, List, Optional

from ..protocols import AsyncClientProtocol, SyncClientProtocol
from ..types import (
    AgentContext,
    AgentSession,
    ConsolidationResult,
    ConsolidationStrategy,
    CoreMemory,
    CoreMemoryBlock,
    CoreMemoryContext,
    SessionMemory,
    SessionMemoryList,
    SessionList,
)
from ..utils.security import validate_id, validate_limit, validate_threshold, validate_offset


class AgentResource:
    """Resource for agent sessions and memory consolidation."""

    def __init__(self, client: SyncClientProtocol) -> None:
        """Initialize agent resource with client."""
        self._client = client

    def consolidate(
        self,
        space_id: Optional[str] = None,
        strategy: ConsolidationStrategy = ConsolidationStrategy.SIMILARITY,
        threshold: float = 0.8,
        dry_run: bool = False,
    ) -> ConsolidationResult:
        """
        Consolidate similar memories to reduce redundancy.

        Args:
            space_id: Optional space to limit consolidation
            strategy: Consolidation strategy
            threshold: Similarity threshold (0.0-1.0)
            dry_run: Preview changes without applying them

        Returns:
            Consolidation result

        Example:
            >>> result = client.agent.consolidate(
            ...     strategy=ConsolidationStrategy.SIMILARITY,
            ...     threshold=0.85,
            ...     dry_run=True
            ... )
        """
        validate_threshold(threshold)
        if space_id:
            validate_id(space_id, "space")
        data: Dict[str, Any] = {
            "strategy": strategy.value,
            "threshold": threshold,
            "dry_run": dry_run,
        }
        if space_id:
            data["space_id"] = space_id

        response = self._client._request("POST", "/agent/consolidate", json=data)
        return ConsolidationResult.model_validate(response)

    def create_session(
        self,
        session_id: str,
        space_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentSession:
        """
        Create a new agent session.

        Args:
            session_id: Unique session identifier
            space_id: Optional space for session
            metadata: Additional session metadata

        Returns:
            Created session object

        Example:
            >>> session = client.agent.create_session(
            ...     session_id="chat_123",
            ...     metadata={"user_id": "user_456"}
            ... )
        """
        validate_id(session_id, "session")
        if space_id:
            validate_id(space_id, "space")
        data: Dict[str, Any] = {"session_id": session_id}
        if space_id:
            data["space_id"] = space_id
        if metadata:
            data["metadata"] = metadata

        response = self._client._request("POST", "/agent/sessions", json=data)
        return AgentSession.model_validate(response)

    def add_session_memory(
        self,
        session_id: str,
        content: str,
        role: Optional[str] = None,
        importance: Optional[float] = None,
    ) -> SessionMemory:
        """
        Add a memory to an agent session.

        Args:
            session_id: Session ID
            content: Memory content
            role: Role (e.g., "user", "assistant")
            importance: Importance score

        Returns:
            Created session memory

        Example:
            >>> memory = client.agent.add_session_memory(
            ...     session_id="chat_123",
            ...     content="User asked about Python",
            ...     role="user",
            ...     importance=0.8
            ... )
        """
        validate_id(session_id, "session")
        data: Dict[str, Any] = {"content": content}
        if role:
            data["role"] = role
        if importance is not None:
            data["importance"] = importance

        response = self._client._request(
            "POST", f"/agent/sessions/{session_id}/memories", json=data
        )
        return SessionMemory.model_validate(response)

    def get_session(self, session_id: str, limit: int = 100, offset: int = 0) -> SessionMemoryList:
        """
        Get memories from an agent session.

        Args:
            session_id: Session ID
            limit: Maximum number of memories (1-1000)
            offset: Offset for pagination (>= 0)

        Returns:
            List of session memories

        Example:
            >>> memories = client.agent.get_session("chat_123", limit=50)
        """
        validate_id(session_id, "session")
        validate_limit(limit)
        validate_offset(offset)
        params = {"limit": limit, "offset": offset}
        response = self._client._request("GET", f"/agent/sessions/{session_id}", params=params)
        return SessionMemoryList.model_validate(response)

    def list_sessions(self, limit: int = 100, space_id: Optional[str] = None) -> SessionList:
        """
        List agent sessions.

        Args:
            limit: Maximum number of sessions (1-1000)
            space_id: Filter by space

        Returns:
            List of sessions

        Example:
            >>> sessions = client.agent.list_sessions(limit=20)
        """
        validate_limit(limit)
        if space_id:
            validate_id(space_id, "space")
        params: Dict[str, Any] = {"limit": limit}
        if space_id:
            params["space_id"] = space_id

        response = self._client._request("GET", "/agent/sessions", params=params)
        return SessionList.model_validate(response)

    def get_context(
        self, query: str, session_id: Optional[str] = None, limit: int = 10
    ) -> AgentContext:
        """
        Get contextual information for an agent query.

        Args:
            query: Agent query
            session_id: Optional session for context
            limit: Maximum number of memories (1-100)

        Returns:
            Agent context with relevant memories

        Example:
            >>> context = client.agent.get_context(
            ...     query="Tell me about our previous discussions",
            ...     session_id="chat_123"
            ... )
        """
        validate_limit(limit, max_limit=100)
        if session_id:
            validate_id(session_id, "session")
        data: Dict[str, Any] = {"query": query, "limit": limit}
        if session_id:
            data["session_id"] = session_id

        response = self._client._request("POST", "/agent/context", json=data)
        return AgentContext.model_validate(response)

    def end_session(
        self,
        session_id: str,
        summary: Optional[str] = None,
        key_insights: Optional[List[str]] = None,
    ) -> AgentSession:
        """
        End an agent session with optional summary.

        Args:
            session_id: Session ID
            summary: Optional session summary
            key_insights: Optional list of key insights

        Returns:
            Updated session object

        Example:
            >>> session = client.agent.end_session(
            ...     session_id="chat_123",
            ...     summary="Discussion about Python best practices"
            ... )
        """
        validate_id(session_id, "session")
        data: Dict[str, Any] = {}
        if summary:
            data["summary"] = summary
        if key_insights:
            data["key_insights"] = key_insights

        response = self._client._request("POST", f"/agent/sessions/{session_id}/end", json=data)
        return AgentSession.model_validate(response)

    def get_core_memory(self, session_id: Optional[str] = None) -> CoreMemory:
        """
        Get core memory for a session or globally.

        Args:
            session_id: Optional session ID (global if not provided)

        Returns:
            Core memory object

        Example:
            >>> core = client.agent.get_core_memory("chat_123")
            >>> for block in core.blocks:
            ...     print(f"{block.key}: {block.value}")
        """
        if session_id:
            validate_id(session_id, "session")
        params = {}
        if session_id:
            params["session_id"] = session_id

        response = self._client._request("GET", "/agent/core-memory", params=params)
        return CoreMemory.model_validate(response)

    def update_core_memory(
        self,
        blocks: List[Dict[str, Any]],
        session_id: Optional[str] = None,
    ) -> CoreMemory:
        """
        Update core memory blocks.

        Args:
            blocks: List of memory blocks to update
            session_id: Optional session ID (global if not provided)

        Returns:
            Updated core memory

        Example:
            >>> core = client.agent.update_core_memory(
            ...     blocks=[{"key": "user_name", "value": "Alice"}],
            ...     session_id="chat_123"
            ... )
        """
        if session_id:
            validate_id(session_id, "session")
        data: Dict[str, Any] = {"blocks": blocks}
        if session_id:
            data["session_id"] = session_id

        response = self._client._request("PUT", "/agent/core-memory", json=data)
        return CoreMemory.model_validate(response)

    def format_core_memory(self, session_id: Optional[str] = None) -> str:
        """
        Get formatted string representation of core memory.

        Args:
            session_id: Optional session ID (global if not provided)

        Returns:
            Formatted core memory string

        Example:
            >>> formatted = client.agent.format_core_memory("chat_123")
            >>> print(formatted)
        """
        if session_id:
            validate_id(session_id, "session")
        params = {}
        if session_id:
            params["session_id"] = session_id

        response = self._client._request("GET", "/agent/core-memory/format", params=params)
        return str(response.get("formatted", ""))

    def get_block(self, block_type: str) -> CoreMemoryBlock:
        """
        Get a specific core memory block.

        Args:
            block_type: The type of block (e.g., "persona", "human")

        Returns:
            Core memory block

        Example:
            >>> block = client.agent.get_block("persona")
            >>> print(block.content)
        """
        response = self._client._request("GET", f"/agent/memory/core/{block_type}")
        return CoreMemoryBlock.model_validate(response)

    def update_block(
        self,
        block_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CoreMemoryBlock:
        """
        Create or replace a core memory block.

        Args:
            block_type: The type of block
            content: Block content
            metadata: Optional metadata

        Returns:
            Updated core memory block

        Example:
            >>> block = client.agent.update_block(
            ...     "persona",
            ...     "I am a helpful assistant."
            ... )
        """
        data: Dict[str, Any] = {"content": content}
        if metadata:
            data["metadata"] = metadata

        response = self._client._request("PUT", f"/agent/memory/core/{block_type}", json=data)
        return CoreMemoryBlock.model_validate(response)

    def append_block(self, block_type: str, content: str) -> CoreMemoryBlock:
        """
        Append content to a core memory block.

        Args:
            block_type: The type of block
            content: Content to append

        Returns:
            Updated core memory block

        Example:
            >>> block = client.agent.append_block("persona", "\\nI also like cats.")
        """
        response = self._client._request(
            "PATCH", f"/agent/memory/core/{block_type}", json={"content": content}
        )
        return CoreMemoryBlock.model_validate(response)

    def delete_block(self, block_type: str) -> None:
        """
        Delete a core memory block.

        Args:
            block_type: The type of block

        Example:
            >>> client.agent.delete_block("persona")
        """
        self._client._request("DELETE", f"/agent/memory/core/{block_type}")

    def get_formatted_context(self) -> CoreMemoryContext:
        """
        Get formatted core memory context.

        Returns:
            Formatted context

        Example:
            >>> context = client.agent.get_formatted_context()
            >>> print(context.formatted)
        """
        response = self._client._request("GET", "/agent/memory/core/context")
        return CoreMemoryContext.model_validate(response)


class AsyncAgentResource:
    """Async resource for agent sessions and memory consolidation."""

    def __init__(self, client: AsyncClientProtocol) -> None:
        """Initialize async agent resource with client."""
        self._client = client

    async def consolidate(
        self,
        space_id: Optional[str] = None,
        strategy: ConsolidationStrategy = ConsolidationStrategy.SIMILARITY,
        threshold: float = 0.8,
        dry_run: bool = False,
    ) -> ConsolidationResult:
        """Consolidate similar memories to reduce redundancy (async)."""
        validate_threshold(threshold)
        if space_id:
            validate_id(space_id, "space")
        data: Dict[str, Any] = {
            "strategy": strategy.value,
            "threshold": threshold,
            "dry_run": dry_run,
        }
        if space_id:
            data["space_id"] = space_id

        response = await self._client._request("POST", "/agent/consolidate", json=data)
        return ConsolidationResult.model_validate(response)

    async def create_session(
        self,
        session_id: str,
        space_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentSession:
        """Create a new agent session (async)."""
        validate_id(session_id, "session")
        if space_id:
            validate_id(space_id, "space")
        data: Dict[str, Any] = {"session_id": session_id}
        if space_id:
            data["space_id"] = space_id
        if metadata:
            data["metadata"] = metadata

        response = await self._client._request("POST", "/agent/sessions", json=data)
        return AgentSession.model_validate(response)

    async def add_session_memory(
        self,
        session_id: str,
        content: str,
        role: Optional[str] = None,
        importance: Optional[float] = None,
    ) -> SessionMemory:
        """Add a memory to an agent session (async)."""
        validate_id(session_id, "session")
        data: Dict[str, Any] = {"content": content}
        if role:
            data["role"] = role
        if importance is not None:
            data["importance"] = importance

        response = await self._client._request(
            "POST", f"/agent/sessions/{session_id}/memories", json=data
        )
        return SessionMemory.model_validate(response)

    async def get_session(
        self, session_id: str, limit: int = 100, offset: int = 0
    ) -> SessionMemoryList:
        """Get memories from an agent session (async)."""
        validate_id(session_id, "session")
        validate_limit(limit)
        validate_offset(offset)
        params = {"limit": limit, "offset": offset}
        response = await self._client._request(
            "GET", f"/agent/sessions/{session_id}", params=params
        )
        return SessionMemoryList.model_validate(response)

    async def list_sessions(self, limit: int = 100, space_id: Optional[str] = None) -> SessionList:
        """List agent sessions (async)."""
        validate_limit(limit)
        if space_id:
            validate_id(space_id, "space")
        params: Dict[str, Any] = {"limit": limit}
        if space_id:
            params["space_id"] = space_id

        response = await self._client._request("GET", "/agent/sessions", params=params)
        return SessionList.model_validate(response)

    async def get_context(
        self, query: str, session_id: Optional[str] = None, limit: int = 10
    ) -> AgentContext:
        """Get contextual information for an agent query (async)."""
        validate_limit(limit, max_limit=100)
        if session_id:
            validate_id(session_id, "session")
        data: Dict[str, Any] = {"query": query, "limit": limit}
        if session_id:
            data["session_id"] = session_id

        response = await self._client._request("POST", "/agent/context", json=data)
        return AgentContext.model_validate(response)

    async def end_session(
        self,
        session_id: str,
        summary: Optional[str] = None,
        key_insights: Optional[List[str]] = None,
    ) -> AgentSession:
        """End an agent session with optional summary (async)."""
        validate_id(session_id, "session")
        data: Dict[str, Any] = {}
        if summary:
            data["summary"] = summary
        if key_insights:
            data["key_insights"] = key_insights

        response = await self._client._request(
            "POST", f"/agent/sessions/{session_id}/end", json=data
        )
        return AgentSession.model_validate(response)

    async def get_core_memory(self, session_id: Optional[str] = None) -> CoreMemory:
        """Get core memory for a session or globally (async)."""
        if session_id:
            validate_id(session_id, "session")
        params = {}
        if session_id:
            params["session_id"] = session_id

        response = await self._client._request("GET", "/agent/core-memory", params=params)
        return CoreMemory.model_validate(response)

    async def update_core_memory(
        self,
        blocks: List[Dict[str, Any]],
        session_id: Optional[str] = None,
    ) -> CoreMemory:
        """Update core memory blocks (async)."""
        if session_id:
            validate_id(session_id, "session")
        data: Dict[str, Any] = {"blocks": blocks}
        if session_id:
            data["session_id"] = session_id

        response = await self._client._request("PUT", "/agent/core-memory", json=data)
        return CoreMemory.model_validate(response)

    async def format_core_memory(self, session_id: Optional[str] = None) -> str:
        """Get formatted string representation of core memory (async)."""
        if session_id:
            validate_id(session_id, "session")
        params = {}
        if session_id:
            params["session_id"] = session_id

        response = await self._client._request("GET", "/agent/core-memory/format", params=params)
        return str(response.get("formatted", ""))

    async def get_block(self, block_type: str) -> CoreMemoryBlock:
        """Get a specific core memory block (async)."""
        response = await self._client._request("GET", f"/agent/memory/core/{block_type}")
        return CoreMemoryBlock.model_validate(response)

    async def update_block(
        self,
        block_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CoreMemoryBlock:
        """Create or replace a core memory block (async)."""
        data: Dict[str, Any] = {"content": content}
        if metadata:
            data["metadata"] = metadata

        response = await self._client._request("PUT", f"/agent/memory/core/{block_type}", json=data)
        return CoreMemoryBlock.model_validate(response)

    async def append_block(self, block_type: str, content: str) -> CoreMemoryBlock:
        """Append content to a core memory block (async)."""
        response = await self._client._request(
            "PATCH", f"/agent/memory/core/{block_type}", json={"content": content}
        )
        return CoreMemoryBlock.model_validate(response)

    async def delete_block(self, block_type: str) -> None:
        """Delete a core memory block (async)."""
        await self._client._request("DELETE", f"/agent/memory/core/{block_type}")

    async def get_formatted_context(self) -> CoreMemoryContext:
        """Get formatted core memory context (async)."""
        response = await self._client._request("GET", "/agent/memory/core/context")
        return CoreMemoryContext.model_validate(response)
