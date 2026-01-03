"""Pagination helpers for Trix SDK."""

from typing import Any, AsyncIterator, Callable, Dict, Iterator, Optional, TypeVar

T = TypeVar("T")


class SyncPaginator:
    """Iterator for paginated list endpoints (sync)."""

    def __init__(
        self,
        fetch_func: Callable[..., Any],
        initial_params: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        max_items: Optional[int] = None,
    ) -> None:
        """
        Initialize paginator.

        Args:
            fetch_func: Function to call for fetching pages
            initial_params: Initial parameters for the request
            limit: Number of items per page
            max_items: Maximum total items to fetch (None for unlimited)
        """
        self._fetch_func = fetch_func
        self._params = initial_params or {}
        self._params["limit"] = limit
        self._limit = limit
        self._max_items = max_items
        self._items_fetched = 0

    def __iter__(self) -> Iterator[Any]:
        """Iterate through all pages."""
        offset = self._params.get("offset", 0)
        cursor = self._params.get("cursor")

        while True:
            # Check if we've reached max items
            if self._max_items and self._items_fetched >= self._max_items:
                break

            # Adjust limit if we're near max_items
            if self._max_items:
                remaining = self._max_items - self._items_fetched
                current_limit = min(self._limit, remaining)
                self._params["limit"] = current_limit

            # Fetch page
            if cursor is not None:
                self._params["cursor"] = cursor
            else:
                self._params["offset"] = offset

            response = self._fetch_func(**self._params)

            # Convert pydantic model to dict if needed
            if hasattr(response, "model_dump"):
                response = response.model_dump()

            # Handle different response formats
            if isinstance(response, dict) and "data" in response:
                items = response["data"]
            else:
                items = response

            if not items:
                break

            # Yield items
            for item in items:
                yield item
                self._items_fetched += 1
                if self._max_items and self._items_fetched >= self._max_items:
                    return

            # Check for next page
            if isinstance(response, dict) and "cursor" in response and response["cursor"]:
                cursor = response["cursor"]
            elif len(items) < self._limit:
                # No more pages
                break
            else:
                offset += len(items)


class AsyncPaginator:
    """Async iterator for paginated list endpoints."""

    def __init__(
        self,
        fetch_func: Callable[..., Any],
        initial_params: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        max_items: Optional[int] = None,
    ) -> None:
        """
        Initialize async paginator.

        Args:
            fetch_func: Async function to call for fetching pages
            initial_params: Initial parameters for the request
            limit: Number of items per page
            max_items: Maximum total items to fetch (None for unlimited)
        """
        self._fetch_func = fetch_func
        self._params = initial_params or {}
        self._params["limit"] = limit
        self._limit = limit
        self._max_items = max_items
        self._items_fetched = 0

    async def __aiter__(self) -> AsyncIterator[Any]:
        """Async iterate through all pages."""
        offset = self._params.get("offset", 0)
        cursor = self._params.get("cursor")

        while True:
            # Check if we've reached max items
            if self._max_items and self._items_fetched >= self._max_items:
                break

            # Adjust limit if we're near max_items
            if self._max_items:
                remaining = self._max_items - self._items_fetched
                current_limit = min(self._limit, remaining)
                self._params["limit"] = current_limit

            # Fetch page
            if cursor is not None:
                self._params["cursor"] = cursor
            else:
                self._params["offset"] = offset

            response = await self._fetch_func(**self._params)

            # Convert pydantic model to dict if needed
            if hasattr(response, "model_dump"):
                response = response.model_dump()

            # Handle different response formats
            if isinstance(response, dict) and "data" in response:
                items = response["data"]
            else:
                items = response

            if not items:
                break

            # Yield items
            for item in items:
                yield item
                self._items_fetched += 1
                if self._max_items and self._items_fetched >= self._max_items:
                    return

            # Check for next page
            if isinstance(response, dict) and "cursor" in response and response["cursor"]:
                cursor = response["cursor"]
            elif len(items) < self._limit:
                # No more pages
                break
            else:
                offset += len(items)
