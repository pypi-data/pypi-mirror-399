"""Authentication handling for Trix SDK."""

from typing import Dict, Optional


class Auth:
    """Handles authentication for Trix API requests."""

    def __init__(self, api_key: Optional[str] = None, jwt_token: Optional[str] = None) -> None:
        """
        Initialize authentication.

        Args:
            api_key: API key for authentication
            jwt_token: JWT token for authentication

        Raises:
            ValueError: If neither api_key nor jwt_token is provided
        """
        if not api_key and not jwt_token:
            raise ValueError("Either api_key or jwt_token must be provided")

        self._api_key = api_key
        self._jwt_token = jwt_token

    def get_headers(self) -> Dict[str, str]:
        """
        Get authentication headers.

        Returns:
            Dictionary of headers with Authorization bearer token
        """
        token = self._jwt_token or self._api_key
        return {"Authorization": f"Bearer {token}"}

    @property
    def api_key(self) -> Optional[str]:
        """Get the API key."""
        return self._api_key

    @property
    def jwt_token(self) -> Optional[str]:
        """Get the JWT token."""
        return self._jwt_token

    def update_jwt_token(self, jwt_token: str) -> None:
        """
        Update the JWT token.

        Args:
            jwt_token: New JWT token
        """
        self._jwt_token = jwt_token

    def clear(self) -> None:
        """
        Clear all stored credentials.

        This method should be called when closing the client to ensure
        credentials are not retained in memory longer than necessary.
        """
        self._api_key = None
        self._jwt_token = None

    @property
    def is_authenticated(self) -> bool:
        """
        Check if valid credentials are present.

        Returns:
            True if either API key or JWT token is set, False otherwise.
        """
        return bool(self._api_key or self._jwt_token)
