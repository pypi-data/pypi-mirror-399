"""TDD tests for Auth class."""

import pytest
from trix.auth import Auth


class TestAuth:
    """Tests for Auth class."""

    class TestInitialization:
        """Tests for Auth initialization."""

        def test_creates_with_api_key(self):
            """Test Auth can be created with API key."""
            auth = Auth(api_key="test_api_key")
            assert auth.api_key == "test_api_key"
            assert auth.jwt_token is None

        def test_creates_with_jwt_token(self):
            """Test Auth can be created with JWT token."""
            auth = Auth(jwt_token="test_jwt_token")
            assert auth.jwt_token == "test_jwt_token"
            assert auth.api_key is None

        def test_creates_with_both(self):
            """Test Auth can be created with both API key and JWT token."""
            auth = Auth(api_key="test_api_key", jwt_token="test_jwt_token")
            assert auth.api_key == "test_api_key"
            assert auth.jwt_token == "test_jwt_token"

        def test_raises_without_credentials(self):
            """Test Auth raises ValueError without credentials."""
            with pytest.raises(ValueError, match="Either api_key or jwt_token must be provided"):
                Auth()

    class TestGetHeaders:
        """Tests for get_headers method."""

        def test_returns_bearer_token_with_api_key(self):
            """Test get_headers returns correct bearer token with API key."""
            auth = Auth(api_key="test_api_key")
            headers = auth.get_headers()
            assert headers["Authorization"] == "Bearer test_api_key"

        def test_prefers_jwt_token_over_api_key(self):
            """Test get_headers prefers JWT token over API key."""
            auth = Auth(api_key="test_api_key", jwt_token="test_jwt_token")
            headers = auth.get_headers()
            assert headers["Authorization"] == "Bearer test_jwt_token"

    class TestUpdateJwtToken:
        """Tests for update_jwt_token method."""

        def test_updates_jwt_token(self):
            """Test update_jwt_token updates the token."""
            auth = Auth(api_key="test_api_key")
            auth.update_jwt_token("new_jwt_token")
            assert auth.jwt_token == "new_jwt_token"

        def test_updated_token_used_in_headers(self):
            """Test updated JWT token is used in headers."""
            auth = Auth(api_key="test_api_key")
            auth.update_jwt_token("new_jwt_token")
            headers = auth.get_headers()
            assert headers["Authorization"] == "Bearer new_jwt_token"

    class TestClear:
        """Tests for clear method."""

        def test_clears_api_key(self):
            """Test clear removes API key."""
            auth = Auth(api_key="test_api_key")
            auth.clear()
            assert auth.api_key is None

        def test_clears_jwt_token(self):
            """Test clear removes JWT token."""
            auth = Auth(jwt_token="test_jwt_token")
            auth.clear()
            assert auth.jwt_token is None

        def test_clears_both_credentials(self):
            """Test clear removes both credentials."""
            auth = Auth(api_key="test_api_key", jwt_token="test_jwt_token")
            auth.clear()
            assert auth.api_key is None
            assert auth.jwt_token is None

    class TestIsAuthenticated:
        """Tests for is_authenticated property."""

        def test_returns_true_with_api_key(self):
            """Test is_authenticated returns True with API key."""
            auth = Auth(api_key="test_api_key")
            assert auth.is_authenticated is True

        def test_returns_true_with_jwt_token(self):
            """Test is_authenticated returns True with JWT token."""
            auth = Auth(jwt_token="test_jwt_token")
            assert auth.is_authenticated is True

        def test_returns_false_after_clear(self):
            """Test is_authenticated returns False after clear."""
            auth = Auth(api_key="test_api_key")
            auth.clear()
            assert auth.is_authenticated is False
