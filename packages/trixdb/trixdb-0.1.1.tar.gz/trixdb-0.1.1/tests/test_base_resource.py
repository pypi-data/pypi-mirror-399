"""Tests for base resource utilities."""

import pytest
from typing import Any, Dict, Optional
from unittest.mock import Mock, AsyncMock

from trix.resources.base import (
    BaseSyncResource,
    BaseAsyncResource,
    validate_params,
    validate_bulk_array,
    find_duplicate_ids,
    DEFAULT_BULK_LIMIT,
)


class TestValidateParams:
    """Tests for validate_params decorator."""

    def test_removes_none_values(self):
        """Test that None values are removed from params."""

        @validate_params
        def build_params(
            limit: Optional[int] = None,
            offset: Optional[int] = None,
            query: Optional[str] = None,
        ) -> Dict[str, Any]:
            return {"limit": limit, "offset": offset, "query": query}

        result = build_params(limit=10, offset=None, query="test")
        assert result == {"limit": 10, "query": "test"}
        assert "offset" not in result

    def test_keeps_all_non_none_values(self):
        """Test that all non-None values are kept."""

        @validate_params
        def build_params(a: int, b: str, c: bool) -> Dict[str, Any]:
            return {"a": a, "b": b, "c": c}

        result = build_params(a=1, b="hello", c=False)
        assert result == {"a": 1, "b": "hello", "c": False}

    def test_handles_empty_dict(self):
        """Test handling of all None values."""

        @validate_params
        def build_params(a: Optional[int] = None) -> Dict[str, Any]:
            return {"a": a}

        result = build_params()
        assert result == {}


class TestValidateBulkArray:
    """Tests for validate_bulk_array function."""

    def test_valid_array(self):
        """Test that valid array passes."""
        validate_bulk_array([1, 2, 3], "test")  # Should not raise

    def test_empty_array_raises(self):
        """Test that empty array raises ValueError."""
        with pytest.raises(ValueError, match="bulk_create: array cannot be empty"):
            validate_bulk_array([], "bulk_create")

    def test_exceeding_max_raises(self):
        """Test that exceeding max raises ValueError."""
        items = [{"id": "test"}] * 1001
        with pytest.raises(ValueError, match="bulk_update: array exceeds maximum of 1000 items"):
            validate_bulk_array(items, "bulk_update")

    def test_custom_max_limit(self):
        """Test custom max limit."""
        items = [{"id": "test"}] * 50
        validate_bulk_array(items, "small_batch", max_items=100)  # Should not raise
        with pytest.raises(ValueError, match="tiny_batch: array exceeds maximum of 10"):
            validate_bulk_array(items, "tiny_batch", max_items=10)

    def test_default_limit(self):
        """Test default limit is 1000."""
        assert DEFAULT_BULK_LIMIT == 1000


class TestFindDuplicateIds:
    """Tests for find_duplicate_ids function."""

    def test_no_duplicates(self):
        """Test with no duplicates."""
        items = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
        assert find_duplicate_ids(items) == []

    def test_finds_duplicates(self):
        """Test finding duplicate IDs."""
        items = [{"id": "a"}, {"id": "b"}, {"id": "a"}, {"id": "c"}, {"id": "b"}]
        assert find_duplicate_ids(items) == ["a", "b"]

    def test_custom_id_field(self):
        """Test with custom id field."""
        items = [{"memory_id": "a"}, {"memory_id": "b"}, {"memory_id": "a"}]
        assert find_duplicate_ids(items, "memory_id") == ["a"]

    def test_ignores_missing_id(self):
        """Test ignoring items without id field."""
        items = [{"id": "a"}, {"name": "test"}, {"id": "a"}]
        assert find_duplicate_ids(items) == ["a"]

    def test_empty_array(self):
        """Test with empty array."""
        assert find_duplicate_ids([]) == []


class TestBaseSyncResource:
    """Tests for BaseSyncResource."""

    def test_init_with_client(self):
        """Test initialization with client."""
        mock_client = Mock()
        resource = BaseSyncResource(mock_client)
        assert resource._client is mock_client

    def test_request_delegates_to_client(self):
        """Test that _request delegates to client."""
        mock_client = Mock()
        mock_client._request.return_value = {"id": "test"}

        resource = BaseSyncResource(mock_client)
        result = resource._request("GET", "/test")

        mock_client._request.assert_called_once_with(
            "GET", "/test", params=None, json=None, timeout=None
        )
        assert result == {"id": "test"}

    def test_request_with_params(self):
        """Test _request with params."""
        mock_client = Mock()
        mock_client._request.return_value = {"data": []}

        resource = BaseSyncResource(mock_client)
        resource._request("GET", "/test", params={"limit": 10})

        mock_client._request.assert_called_once_with(
            "GET", "/test", params={"limit": 10}, json=None, timeout=None
        )

    def test_request_with_json(self):
        """Test _request with json body."""
        mock_client = Mock()
        mock_client._request.return_value = {"id": "new"}

        resource = BaseSyncResource(mock_client)
        resource._request("POST", "/test", json={"name": "test"})

        mock_client._request.assert_called_once_with(
            "POST", "/test", params=None, json={"name": "test"}, timeout=None
        )

    def test_request_with_timeout(self):
        """Test _request with timeout override."""
        mock_client = Mock()
        mock_client._request.return_value = {}

        resource = BaseSyncResource(mock_client)
        resource._request("GET", "/test", timeout=30.0)

        mock_client._request.assert_called_once_with(
            "GET", "/test", params=None, json=None, timeout=30.0
        )


class TestBaseAsyncResource:
    """Tests for BaseAsyncResource."""

    @pytest.mark.asyncio
    async def test_init_with_client(self):
        """Test initialization with async client."""
        mock_client = AsyncMock()
        resource = BaseAsyncResource(mock_client)
        assert resource._client is mock_client

    @pytest.mark.asyncio
    async def test_request_delegates_to_client(self):
        """Test that _request delegates to async client."""
        mock_client = AsyncMock()
        mock_client._request.return_value = {"id": "test"}

        resource = BaseAsyncResource(mock_client)
        result = await resource._request("GET", "/test")

        mock_client._request.assert_called_once_with(
            "GET", "/test", params=None, json=None, timeout=None
        )
        assert result == {"id": "test"}

    @pytest.mark.asyncio
    async def test_request_with_params(self):
        """Test async _request with params."""
        mock_client = AsyncMock()
        mock_client._request.return_value = {"data": []}

        resource = BaseAsyncResource(mock_client)
        await resource._request("GET", "/test", params={"limit": 10})

        mock_client._request.assert_called_once_with(
            "GET", "/test", params={"limit": 10}, json=None, timeout=None
        )

    @pytest.mark.asyncio
    async def test_request_with_json(self):
        """Test async _request with json body."""
        mock_client = AsyncMock()
        mock_client._request.return_value = {"id": "new"}

        resource = BaseAsyncResource(mock_client)
        await resource._request("POST", "/test", json={"name": "test"})

        mock_client._request.assert_called_once_with(
            "POST", "/test", params=None, json={"name": "test"}, timeout=None
        )

    @pytest.mark.asyncio
    async def test_request_with_timeout(self):
        """Test async _request with timeout override."""
        mock_client = AsyncMock()
        mock_client._request.return_value = {}

        resource = BaseAsyncResource(mock_client)
        await resource._request("GET", "/test", timeout=30.0)

        mock_client._request.assert_called_once_with(
            "GET", "/test", params=None, json=None, timeout=30.0
        )
