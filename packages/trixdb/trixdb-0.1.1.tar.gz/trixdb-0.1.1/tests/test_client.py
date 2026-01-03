"""Tests for Trix client."""

import pytest
from trix import Trix, AsyncTrix


def test_client_initialization_with_api_key():
    """Test client initialization with API key."""
    client = Trix(api_key="test_key")
    assert client._auth.api_key == "test_key"
    client.close()


def test_client_initialization_with_jwt():
    """Test client initialization with JWT token."""
    client = Trix(jwt_token="test_token")
    assert client._auth.jwt_token == "test_token"
    client.close()


def test_client_initialization_without_auth():
    """Test client initialization without authentication raises error."""
    with pytest.raises(ValueError):
        Trix()


def test_client_context_manager():
    """Test client as context manager."""
    with Trix(api_key="test_key") as client:
        assert client._auth.api_key == "test_key"


def test_client_custom_base_url():
    """Test client with custom base URL."""
    client = Trix(api_key="test_key", base_url="https://custom.api.com")
    assert client._base_url == "https://custom.api.com"
    client.close()


def test_client_custom_timeout():
    """Test client with custom timeout."""
    client = Trix(api_key="test_key", timeout=60.0)
    assert client._timeout == 60.0
    client.close()


@pytest.mark.asyncio
async def test_async_client_initialization():
    """Test async client initialization."""
    async with AsyncTrix(api_key="test_key") as client:
        assert client._auth.api_key == "test_key"


@pytest.mark.asyncio
async def test_async_client_context_manager():
    """Test async client as context manager."""
    client = AsyncTrix(api_key="test_key")
    async with client:
        assert client._auth.api_key == "test_key"
