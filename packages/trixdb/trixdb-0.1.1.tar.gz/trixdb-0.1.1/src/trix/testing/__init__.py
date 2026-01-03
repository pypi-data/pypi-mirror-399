"""
Testing utilities for Trix SDK.

This module provides mock clients and factory functions for testing
code that uses the Trix SDK without making real API calls.

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
    ...     memory = mock_client.memories.create(content="Test")
    ...     assert memory.content == "Test"
    ...
    ...     # Verify calls
    ...     assert len(mock_client.memories.create_calls) == 1
"""

from .mock_client import (
    # Main mock client
    MockTrix,
    MockAsyncTrix,
    # Mock resource classes
    MockMemoriesResource,
    MockAsyncMemoriesResource,
    MockClustersResource,
    MockAsyncClustersResource,
    MockEntitiesResource,
    MockAsyncEntitiesResource,
    MockFactsResource,
    MockAsyncFactsResource,
    # Factory functions
    create_mock_memory,
    create_mock_cluster,
    create_mock_relationship,
    create_mock_entity,
    create_mock_fact,
    create_mock_paginated_response,
    create_mock_bulk_result,
    random_id,
)

__all__ = [
    # Main mock clients
    "MockTrix",
    "MockAsyncTrix",
    # Mock resource classes
    "MockMemoriesResource",
    "MockAsyncMemoriesResource",
    "MockClustersResource",
    "MockAsyncClustersResource",
    "MockEntitiesResource",
    "MockAsyncEntitiesResource",
    "MockFactsResource",
    "MockAsyncFactsResource",
    # Factory functions
    "create_mock_memory",
    "create_mock_cluster",
    "create_mock_relationship",
    "create_mock_entity",
    "create_mock_fact",
    "create_mock_paginated_response",
    "create_mock_bulk_result",
    "random_id",
]
