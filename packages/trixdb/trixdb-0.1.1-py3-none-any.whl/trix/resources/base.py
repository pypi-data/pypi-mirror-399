"""Base resource classes and utilities for Trix SDK.

This module provides base classes that eliminate duplication between
sync and async resource implementations.
"""

from abc import ABC
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar

from ..protocols import AsyncClientProtocol, SyncClientProtocol
from ..utils.security import validate_id

# Type variables for generic base classes
T = TypeVar("T")
CreateT = TypeVar("CreateT")
UpdateT = TypeVar("UpdateT")


def validate_ids(ids: Optional[List[str]], resource_type: str) -> None:
    """Validate a list of IDs.

    Args:
        ids: List of IDs to validate (can be None)
        resource_type: Type name for error messages

    Raises:
        ValidationError: If any ID is invalid
    """
    if ids:
        for id_value in ids:
            validate_id(id_value, resource_type)


# Default maximum items for bulk operations
DEFAULT_BULK_LIMIT = 1000


def validate_bulk_array(
    items: List[Any],
    operation_name: str,
    max_items: int = DEFAULT_BULK_LIMIT,
) -> None:
    """Validate bulk operation array.

    Checks:
    - Array is not empty
    - Array doesn't exceed max size

    Args:
        items: List of items to validate
        operation_name: Name of operation for error messages
        max_items: Maximum allowed items (default: 1000)

    Raises:
        ValueError: If validation fails
    """
    if not items:
        raise ValueError(f"{operation_name}: array cannot be empty")
    if len(items) > max_items:
        raise ValueError(
            f"{operation_name}: array exceeds maximum of {max_items} items (got {len(items)})"
        )


def find_duplicate_ids(items: List[Dict[str, Any]], id_field: str = "id") -> List[str]:
    """Check for duplicate IDs in an array.

    Args:
        items: List of items with id field
        id_field: Field name containing the ID (default: "id")

    Returns:
        List of duplicate IDs found
    """
    seen: set[str] = set()
    duplicates: List[str] = []

    for item in items:
        id_value = item.get(id_field)
        if id_value:
            if id_value in seen:
                duplicates.append(id_value)
            else:
                seen.add(id_value)

    return duplicates


def validate_params(func: Callable[..., Dict[str, Any]]) -> Callable[..., Dict[str, Any]]:
    """Decorator that removes None values from returned dict.

    Use this to build request params dicts, automatically filtering
    out optional parameters that weren't provided.

    Example:
        @validate_params
        def build_list_params(limit: Optional[int] = None, offset: Optional[int] = None):
            return {"limit": limit, "offset": offset}

        # Returns {"limit": 10} - offset is removed because it's None
        build_list_params(limit=10)
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        result = func(*args, **kwargs)
        return {k: v for k, v in result.items() if v is not None}

    return wrapper


class BaseResource(ABC):
    """Abstract base for all resource classes.

    Provides common interface for both sync and async resources.
    """

    pass


class BaseSyncResource(BaseResource):
    """Base class for synchronous resource implementations.

    Provides common utilities for sync resources:
    - Client reference and request delegation
    - Parameter building helpers
    - Standard CRUD operation patterns

    Example:
        class MemoriesResource(BaseSyncResource):
            def list(self, limit: Optional[int] = None) -> List[Memory]:
                params = self._build_params(limit=limit)
                response = self._request("GET", "/memories", params=params)
                return [Memory.model_validate(m) for m in response["data"]]
    """

    def __init__(self, client: SyncClientProtocol) -> None:
        """Initialize resource with sync client.

        Args:
            client: Sync Trix client instance
        """
        self._client = client

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """Make an HTTP request through the client.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path
            params: Optional query parameters
            json: Optional JSON body
            timeout: Optional timeout override

        Returns:
            Response data from API
        """
        return self._client._request(method, path, params=params, json=json, timeout=timeout)


class BaseAsyncResource(BaseResource):
    """Base class for asynchronous resource implementations.

    Provides common utilities for async resources:
    - Client reference and request delegation
    - Parameter building helpers
    - Standard CRUD operation patterns

    Example:
        class AsyncMemoriesResource(BaseAsyncResource):
            async def list(self, limit: Optional[int] = None) -> List[Memory]:
                params = self._build_params(limit=limit)
                response = await self._request("GET", "/memories", params=params)
                return [Memory.model_validate(m) for m in response["data"]]
    """

    def __init__(self, client: AsyncClientProtocol) -> None:
        """Initialize resource with async client.

        Args:
            client: Async Trix client instance
        """
        self._client = client

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """Make an async HTTP request through the client.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path
            params: Optional query parameters
            json: Optional JSON body
            timeout: Optional timeout override

        Returns:
            Response data from API
        """
        return await self._client._request(method, path, params=params, json=json, timeout=timeout)
