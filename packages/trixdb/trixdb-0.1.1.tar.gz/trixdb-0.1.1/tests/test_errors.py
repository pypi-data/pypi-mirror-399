"""Tests for error handling."""

import pytest
from unittest.mock import Mock
import httpx

from trix import Trix
from trix.exceptions import (
    TrixError,
    APIError,
    APIVersionMismatchError,
    AuthenticationError,
    PermissionError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
    ConnectionError,
    TimeoutError,
)


class TestExceptionHierarchy:
    """Test exception class hierarchy."""

    def test_all_exceptions_inherit_from_trix_error(self):
        """Test all exceptions inherit from TrixError."""
        exceptions = [
            APIError("test"),
            APIVersionMismatchError("test"),
            AuthenticationError("test"),
            PermissionError("test"),
            NotFoundError("test"),
            ValidationError("test"),
            RateLimitError("test"),
            ServerError("test"),
            ConnectionError("test"),
            TimeoutError("test"),
        ]
        for exc in exceptions:
            assert isinstance(exc, TrixError)

    def test_exception_attributes(self):
        """Test exception attributes are set correctly."""
        exc = APIError("Test message", status_code=400, response={"error": "details"})
        assert exc.message == "Test message"
        assert exc.status_code == 400
        assert exc.response == {"error": "details"}

    def test_rate_limit_error_retry_after(self):
        """Test RateLimitError includes retry_after."""
        exc = RateLimitError("Rate limited", retry_after=60)
        assert exc.retry_after == 60

    def test_version_mismatch_error_attributes(self):
        """Test APIVersionMismatchError includes version info."""
        exc = APIVersionMismatchError(
            "Version mismatch",
            sdk_version="1.0.0",
            api_version="v2",
            min_supported="v1",
            max_supported="v1",
        )
        assert exc.sdk_version == "1.0.0"
        assert exc.api_version == "v2"
        assert exc.min_supported == "v1"
        assert exc.max_supported == "v1"


class TestErrorResponseHandling:
    """Test HTTP error response handling."""

    def _create_mock_response(self, status_code, json_data=None, headers=None):
        """Create a mock httpx.Response."""
        response = Mock(spec=httpx.Response)
        response.status_code = status_code
        response.is_success = 200 <= status_code < 300
        response.headers = headers or {}
        response.text = json_data.get("message", "") if json_data else ""
        if json_data:
            response.json.return_value = json_data
        else:
            response.json.side_effect = Exception("No JSON")
        return response

    def test_401_raises_authentication_error(self):
        """Test 401 response raises AuthenticationError."""
        from trix.client import _handle_response

        response = self._create_mock_response(401, {"message": "Invalid credentials"})

        with pytest.raises(AuthenticationError) as exc_info:
            _handle_response(response)
        assert "Invalid credentials" in str(exc_info.value)

    def test_403_raises_permission_error(self):
        """Test 403 response raises PermissionError."""
        from trix.client import _handle_response

        response = self._create_mock_response(403, {"message": "Access denied"})

        with pytest.raises(PermissionError) as exc_info:
            _handle_response(response)
        assert "Access denied" in str(exc_info.value)

    def test_404_raises_not_found_error(self):
        """Test 404 response raises NotFoundError."""
        from trix.client import _handle_response

        response = self._create_mock_response(404, {"message": "Memory not found"})

        with pytest.raises(NotFoundError) as exc_info:
            _handle_response(response)
        assert "Memory not found" in str(exc_info.value)

    def test_422_raises_validation_error(self):
        """Test 422 response raises ValidationError."""
        from trix.client import _handle_response

        response = self._create_mock_response(422, {"message": "Invalid input"})

        with pytest.raises(ValidationError) as exc_info:
            _handle_response(response)
        assert "Invalid input" in str(exc_info.value)

    def test_429_raises_rate_limit_error(self):
        """Test 429 response raises RateLimitError."""
        from trix.client import _handle_response

        response = self._create_mock_response(
            429, {"message": "Too many requests"}, headers={"Retry-After": "60"}
        )

        with pytest.raises(RateLimitError) as exc_info:
            _handle_response(response)
        assert exc_info.value.retry_after == 60

    def test_500_raises_server_error(self):
        """Test 500 response raises ServerError."""
        from trix.client import _handle_response

        response = self._create_mock_response(500, {"message": "Internal error"})

        with pytest.raises(ServerError) as exc_info:
            _handle_response(response)
        assert "Internal error" in str(exc_info.value)

    def test_502_raises_server_error(self):
        """Test 502 response raises ServerError."""
        from trix.client import _handle_response

        response = self._create_mock_response(502, {"message": "Bad gateway"})

        with pytest.raises(ServerError):
            _handle_response(response)

    def test_unknown_error_raises_api_error(self):
        """Test unknown status code raises APIError."""
        from trix.client import _handle_response

        response = self._create_mock_response(418, {"message": "I'm a teapot"})

        with pytest.raises(APIError) as exc_info:
            _handle_response(response)
        assert exc_info.value.status_code == 418


class TestVersionChecking:
    """Test API version checking."""

    def _create_mock_response_with_version(self, api_version):
        """Create a mock response with X-API-Version header."""
        response = Mock(spec=httpx.Response)
        response.status_code = 200
        response.is_success = True
        response.headers = {"X-API-Version": api_version} if api_version else {}
        return response

    def test_compatible_version_passes(self):
        """Test compatible API version doesn't raise."""
        from trix.client import _check_api_version

        response = self._create_mock_response_with_version("v1")
        # Should not raise
        _check_api_version(response)

    def test_incompatible_version_raises(self):
        """Test incompatible API version raises APIVersionMismatchError."""
        from trix.client import _check_api_version

        response = self._create_mock_response_with_version("v99")

        with pytest.raises(APIVersionMismatchError) as exc_info:
            _check_api_version(response)
        assert "v99" in str(exc_info.value)
        assert exc_info.value.api_version == "v99"

    def test_no_version_header_passes(self):
        """Test missing version header doesn't raise."""
        from trix.client import _check_api_version

        response = self._create_mock_response_with_version(None)
        # Should not raise
        _check_api_version(response)

    def test_invalid_version_format_logs_warning(self):
        """Test invalid version format logs warning but doesn't raise."""
        from trix.client import _check_api_version

        response = self._create_mock_response_with_version("invalid")
        # Should not raise, just log warning
        _check_api_version(response)


class TestCredentialClearing:
    """Test credentials are cleared on close."""

    def test_sync_client_clears_credentials(self):
        """Test sync client clears credentials on close."""
        client = Trix(api_key="secret_key")
        assert client._auth._api_key == "secret_key"

        client.close()

        assert client._auth._api_key is None
        assert client._auth._jwt_token is None

    @pytest.mark.asyncio
    async def test_async_client_clears_credentials(self):
        """Test async client clears credentials on close."""
        from trix import AsyncTrix

        client = AsyncTrix(api_key="secret_key")
        assert client._auth._api_key == "secret_key"

        await client.close()

        assert client._auth._api_key is None
        assert client._auth._jwt_token is None
