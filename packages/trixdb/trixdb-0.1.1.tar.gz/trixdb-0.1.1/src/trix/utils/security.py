"""Security utilities for Trix SDK."""

import os
import re
from typing import Any, Optional
from urllib.parse import urlparse


# Pattern for valid resource IDs - alphanumeric, underscores, hyphens
ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{1,255}$")

# Pattern for valid webhook URLs - must be HTTPS
WEBHOOK_URL_PATTERN = re.compile(r"^https://")

# Sensitive keys that should be redacted in logs
SENSITIVE_KEYS = frozenset(
    {
        "api_key",
        "apikey",
        "api-key",
        "token",
        "jwt_token",
        "jwt",
        "bearer",
        "password",
        "secret",
        "credential",
        "authorization",
        "auth",
    }
)


def validate_id(resource_id: str, resource_type: str = "resource") -> str:
    """
    Validate a resource ID to prevent path traversal attacks.

    Args:
        resource_id: The ID to validate
        resource_type: Type of resource for error messages

    Returns:
        The validated ID

    Raises:
        ValueError: If the ID is invalid
    """
    if not resource_id:
        raise ValueError(f"{resource_type} ID cannot be empty")

    if not isinstance(resource_id, str):
        raise ValueError(f"{resource_type} ID must be a string, got {type(resource_id).__name__}")

    # Check for path traversal attempts
    if ".." in resource_id or "/" in resource_id or "\\" in resource_id:
        raise ValueError(f"Invalid {resource_type} ID: contains path traversal characters")

    # Validate against pattern
    if not ID_PATTERN.match(resource_id):
        raise ValueError(
            f"Invalid {resource_type} ID: must be 1-255 characters, "
            "containing only letters, numbers, underscores, and hyphens"
        )

    return resource_id


def validate_base_url(url: str, allow_http: bool = False) -> str:
    """
    Validate a base URL for the API.

    Args:
        url: The URL to validate
        allow_http: Whether to allow HTTP (insecure, for local dev only)

    Returns:
        The validated URL (without trailing slash)

    Raises:
        ValueError: If the URL is invalid or insecure
    """
    if not url:
        raise ValueError("Base URL cannot be empty")

    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValueError(f"Invalid URL format: {e}")

    # Check scheme
    if not parsed.scheme:
        raise ValueError("URL must include a scheme (https://)")

    if parsed.scheme == "http":
        if not allow_http:
            raise ValueError(
                "HTTP is not allowed for security reasons. Use HTTPS. "
                "Set allow_http=True only for local development."
            )
    elif parsed.scheme != "https":
        raise ValueError(f"Invalid URL scheme '{parsed.scheme}'. Only HTTPS is allowed.")

    # Check host
    if not parsed.netloc:
        raise ValueError("URL must include a host")

    # Block localhost in production (unless allow_http is set)
    if not allow_http:
        host = parsed.netloc.lower().split(":")[0]
        if host in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
            raise ValueError(
                "Localhost URLs are not allowed in production. "
                "Set allow_http=True for local development."
            )

    return url.rstrip("/")


def validate_webhook_url(url: str) -> str:
    """
    Validate a webhook URL.

    Args:
        url: The webhook URL to validate

    Returns:
        The validated URL

    Raises:
        ValueError: If the URL is invalid or insecure
    """
    if not url:
        raise ValueError("Webhook URL cannot be empty")

    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValueError(f"Invalid webhook URL format: {e}")

    # Must be HTTPS
    if parsed.scheme != "https":
        raise ValueError("Webhook URL must use HTTPS for security")

    if not parsed.netloc:
        raise ValueError("Webhook URL must include a host")

    # Block internal/private IPs
    # Use parsed.hostname to correctly handle IPv6 addresses
    host = parsed.hostname
    if not host:
        raise ValueError("Webhook URL must include a host")

    # Normalize: lowercase and strip brackets for IPv6
    normalized_host = host.lower().strip("[]")

    # Block localhost variants
    if normalized_host in ("localhost", "0.0.0.0"):
        raise ValueError("Webhook URL cannot point to localhost")

    # Block IPv4 loopback (127.0.0.0/8)
    if normalized_host.startswith("127."):
        raise ValueError("Webhook URL cannot point to localhost")

    # Block IPv6 loopback (::1)
    if normalized_host == "::1":
        raise ValueError("Webhook URL cannot point to localhost")

    # Block IPv6 zero address (::)
    if normalized_host in ("::", "0:0:0:0:0:0:0:0"):
        raise ValueError("Webhook URL cannot point to the zero address")

    # Block private IPv4 ranges
    # 10.0.0.0/8
    if normalized_host.startswith("10."):
        raise ValueError("Webhook URL cannot point to private IP addresses")

    # 192.168.0.0/16
    if normalized_host.startswith("192.168."):
        raise ValueError("Webhook URL cannot point to private IP addresses")

    # 172.16.0.0/12 (172.16.0.0 - 172.31.255.255)
    if normalized_host.startswith("172."):
        parts = normalized_host.split(".")
        if len(parts) >= 2 and parts[1].isdigit():
            second_octet = int(parts[1])
            if 16 <= second_octet <= 31:
                raise ValueError("Webhook URL cannot point to private IP addresses")

    # Block link-local addresses (169.254.0.0/16)
    if normalized_host.startswith("169.254."):
        raise ValueError("Webhook URL cannot point to link-local addresses")

    # Block AWS/cloud metadata service
    if normalized_host == "169.254.169.254":
        raise ValueError("Webhook URL cannot point to metadata service")

    # Block IPv6 private/link-local ranges
    # fc00::/7 (Unique Local Addresses - includes fc and fd prefixes)
    if normalized_host.startswith("fc") or normalized_host.startswith("fd"):
        raise ValueError("Webhook URL cannot point to private IPv6 addresses")

    # fe80::/10 (Link-local addresses)
    if (
        normalized_host.startswith("fe8")
        or normalized_host.startswith("fe9")
        or normalized_host.startswith("fea")
        or normalized_host.startswith("feb")
    ):
        raise ValueError("Webhook URL cannot point to IPv6 link-local addresses")

    # Block IPv4-mapped IPv6 addresses (::ffff:x.x.x.x)
    # These could be used to bypass IPv4 checks
    if "ffff:" in normalized_host.lower():
        import re

        ipv4_match = re.search(r"::ffff:(\d+\.\d+\.\d+\.\d+)$", normalized_host, re.IGNORECASE)
        if not ipv4_match:
            ipv4_match = re.search(r":ffff:(\d+\.\d+\.\d+\.\d+)$", normalized_host, re.IGNORECASE)
        if ipv4_match:
            ipv4 = ipv4_match.group(1)
            if (
                ipv4.startswith("127.")
                or ipv4.startswith("10.")
                or ipv4.startswith("192.168.")
                or ipv4.startswith("169.254.")
                or ipv4 == "0.0.0.0"
            ):
                raise ValueError("Webhook URL cannot point to private IPv4-mapped IPv6 addresses")
            if ipv4.startswith("172."):
                parts = ipv4.split(".")
                if len(parts) >= 2 and parts[1].isdigit():
                    second_octet = int(parts[1])
                    if 16 <= second_octet <= 31:
                        raise ValueError(
                            "Webhook URL cannot point to private IPv4-mapped IPv6 addresses"
                        )

    # Block site-local addresses (deprecated but still valid: fec0::/10)
    if (
        normalized_host.startswith("fec")
        or normalized_host.startswith("fed")
        or normalized_host.startswith("fee")
        or normalized_host.startswith("fef")
    ):
        raise ValueError("Webhook URL cannot point to deprecated IPv6 site-local addresses")

    return url


def redact_sensitive_data(data: Any, max_depth: int = 10) -> Any:
    """
    Redact sensitive data from a dictionary or object for safe logging.

    Args:
        data: Data to redact
        max_depth: Maximum recursion depth

    Returns:
        Data with sensitive values replaced with "[REDACTED]"
    """
    if max_depth <= 0:
        return "[MAX DEPTH EXCEEDED]"

    if isinstance(data, dict):
        return {
            key: (
                "[REDACTED]"
                if _is_sensitive_key(key)
                else redact_sensitive_data(value, max_depth - 1)
            )
            for key, value in data.items()
        }
    elif isinstance(data, (list, tuple)):
        return type(data)(redact_sensitive_data(item, max_depth - 1) for item in data)
    elif isinstance(data, str):
        # Redact Bearer tokens in strings
        if data.startswith("Bearer "):
            return "Bearer [REDACTED]"
        return data
    else:
        return data


def _is_sensitive_key(key: str) -> bool:
    """Check if a key name suggests sensitive data."""
    if not isinstance(key, str):
        return False
    key_lower = key.lower().replace("_", "").replace("-", "")
    return any(sensitive in key_lower for sensitive in SENSITIVE_KEYS)


def get_env_credential(
    env_var: str = "TRIX_API_KEY",
    required: bool = True,
) -> Optional[str]:
    """
    Get API credential from environment variable.

    Args:
        env_var: Environment variable name
        required: Whether to raise if not found

    Returns:
        The credential value or None

    Raises:
        ValueError: If required and not found
    """
    value = os.environ.get(env_var)

    if value is None and required:
        raise ValueError(
            f"Environment variable {env_var} is not set. "
            f"Either set {env_var} or pass api_key explicitly."
        )

    if value is not None:
        value = value.strip()
        if not value:
            if required:
                raise ValueError(f"Environment variable {env_var} is empty")
            return None

    return value


def mask_credential(credential: str, visible_chars: int = 4) -> str:
    """
    Mask a credential for display, showing only the last few characters.

    Args:
        credential: The credential to mask
        visible_chars: Number of characters to show at the end

    Returns:
        Masked credential like "****abcd"
    """
    if not credential:
        return "[EMPTY]"

    if len(credential) <= visible_chars:
        return "*" * len(credential)

    return "*" * (len(credential) - visible_chars) + credential[-visible_chars:]


def validate_limit(limit: int, max_limit: int = 1000, param_name: str = "limit") -> int:
    """
    Validate a limit parameter for pagination.

    Args:
        limit: The limit value to validate
        max_limit: Maximum allowed limit value
        param_name: Name of the parameter for error messages

    Returns:
        The validated limit

    Raises:
        ValueError: If the limit is invalid
    """
    if not isinstance(limit, int):
        raise ValueError(f"{param_name} must be an integer, got {type(limit).__name__}")

    if limit < 1:
        raise ValueError(f"{param_name} must be at least 1, got {limit}")

    if limit > max_limit:
        raise ValueError(f"{param_name} cannot exceed {max_limit}, got {limit}")

    return limit


def validate_offset(offset: int, param_name: str = "offset") -> int:
    """
    Validate an offset parameter for pagination.

    Args:
        offset: The offset value to validate
        param_name: Name of the parameter for error messages

    Returns:
        The validated offset

    Raises:
        ValueError: If the offset is invalid
    """
    if not isinstance(offset, int):
        raise ValueError(f"{param_name} must be an integer, got {type(offset).__name__}")

    if offset < 0:
        raise ValueError(f"{param_name} cannot be negative, got {offset}")

    return offset


def validate_threshold(
    threshold: float, min_value: float = 0.0, max_value: float = 1.0, param_name: str = "threshold"
) -> float:
    """
    Validate a threshold/confidence parameter.

    Args:
        threshold: The threshold value to validate
        min_value: Minimum allowed value (default: 0.0)
        max_value: Maximum allowed value (default: 1.0)
        param_name: Name of the parameter for error messages

    Returns:
        The validated threshold

    Raises:
        ValueError: If the threshold is invalid
    """
    if not isinstance(threshold, (int, float)):
        raise ValueError(f"{param_name} must be a number, got {type(threshold).__name__}")

    if threshold < min_value or threshold > max_value:
        raise ValueError(
            f"{param_name} must be between {min_value} and {max_value}, got {threshold}"
        )

    return float(threshold)


def validate_positive_int(value: int, param_name: str = "value", allow_zero: bool = False) -> int:
    """
    Validate a positive integer parameter.

    Args:
        value: The value to validate
        param_name: Name of the parameter for error messages
        allow_zero: Whether to allow zero as a valid value

    Returns:
        The validated value

    Raises:
        ValueError: If the value is invalid
    """
    if not isinstance(value, int):
        raise ValueError(f"{param_name} must be an integer, got {type(value).__name__}")

    if allow_zero:
        if value < 0:
            raise ValueError(f"{param_name} cannot be negative, got {value}")
    else:
        if value < 1:
            raise ValueError(f"{param_name} must be at least 1, got {value}")

    return value
