"""TDD-style tests for security utilities."""

import pytest
from trix.utils.security import (
    validate_id,
    validate_base_url,
    validate_webhook_url,
    redact_sensitive_data,
    get_env_credential,
    mask_credential,
    validate_limit,
    validate_offset,
    validate_threshold,
    validate_positive_int,
)


class TestValidateId:
    """Tests for validate_id function."""

    class TestValidIds:
        """Tests for valid ID inputs."""

        def test_accepts_alphanumeric_ids(self):
            assert validate_id("mem123") == "mem123"
            assert validate_id("MEM123") == "MEM123"
            assert validate_id("abc") == "abc"

        def test_accepts_ids_with_underscores(self):
            assert validate_id("mem_123") == "mem_123"
            assert validate_id("my_memory_id") == "my_memory_id"

        def test_accepts_ids_with_hyphens(self):
            assert validate_id("mem-123") == "mem-123"
            assert validate_id("my-memory-id") == "my-memory-id"

        def test_accepts_ids_with_mixed_characters(self):
            assert validate_id("mem_123-abc") == "mem_123-abc"
            assert validate_id("MEM-123_ABC") == "MEM-123_ABC"

        def test_accepts_single_character_ids(self):
            assert validate_id("a") == "a"
            assert validate_id("1") == "1"

        def test_accepts_255_character_ids(self):
            long_id = "a" * 255
            assert validate_id(long_id) == long_id

    class TestInvalidIdsEmptyNull:
        """Tests for empty/null ID inputs."""

        def test_rejects_empty_string(self):
            with pytest.raises(ValueError, match="cannot be empty"):
                validate_id("")

        def test_rejects_none(self):
            with pytest.raises(ValueError):
                validate_id(None)  # type: ignore

    class TestInvalidIdsPathTraversal:
        """Tests for path traversal attempts."""

        def test_rejects_ids_with_double_dots(self):
            with pytest.raises(ValueError, match="path traversal"):
                validate_id("..")
            with pytest.raises(ValueError, match="path traversal"):
                validate_id("mem/../etc")
            with pytest.raises(ValueError, match="path traversal"):
                validate_id("..mem")

        def test_rejects_ids_with_forward_slashes(self):
            with pytest.raises(ValueError, match="path traversal"):
                validate_id("mem/123")
            with pytest.raises(ValueError, match="path traversal"):
                validate_id("/mem")
            with pytest.raises(ValueError, match="path traversal"):
                validate_id("mem/")

        def test_rejects_ids_with_backslashes(self):
            with pytest.raises(ValueError, match="path traversal"):
                validate_id("mem\\123")
            with pytest.raises(ValueError, match="path traversal"):
                validate_id("\\mem")

    class TestInvalidIdsSpecialCharacters:
        """Tests for special characters in IDs."""

        def test_rejects_ids_with_spaces(self):
            with pytest.raises(ValueError):
                validate_id("mem 123")

        def test_rejects_ids_with_periods(self):
            with pytest.raises(ValueError):
                validate_id("mem.123")

        def test_rejects_ids_with_special_characters(self):
            with pytest.raises(ValueError):
                validate_id("mem@123")
            with pytest.raises(ValueError):
                validate_id("mem#123")
            with pytest.raises(ValueError):
                validate_id("mem$123")
            with pytest.raises(ValueError):
                validate_id("mem%123")

        def test_rejects_ids_exceeding_255_characters(self):
            too_long_id = "a" * 256
            with pytest.raises(ValueError):
                validate_id(too_long_id)

    class TestCustomResourceType:
        """Tests for custom resource type in error messages."""

        def test_includes_resource_type_in_error_message(self):
            with pytest.raises(ValueError, match="memory ID cannot be empty"):
                validate_id("", "memory")
            with pytest.raises(ValueError, match="cluster ID cannot be empty"):
                validate_id("", "cluster")


class TestValidateBaseUrl:
    """Tests for validate_base_url function."""

    class TestValidUrls:
        """Tests for valid URL inputs."""

        def test_accepts_https_urls(self):
            assert validate_base_url("https://api.example.com") == "https://api.example.com"

        def test_accepts_https_urls_with_port(self):
            assert (
                validate_base_url("https://api.example.com:8443") == "https://api.example.com:8443"
            )

        def test_accepts_https_urls_with_path(self):
            assert validate_base_url("https://api.example.com/v1") == "https://api.example.com/v1"

        def test_strips_trailing_slashes(self):
            assert validate_base_url("https://api.example.com/") == "https://api.example.com"
            assert validate_base_url("https://api.example.com///") == "https://api.example.com"

    class TestHttpUrls:
        """Tests for HTTP URL handling."""

        def test_rejects_http_by_default(self):
            with pytest.raises(ValueError, match="HTTP is not allowed"):
                validate_base_url("http://api.example.com")

        def test_allows_http_when_allow_http_is_true(self):
            result = validate_base_url("http://localhost:3000", allow_http=True)
            assert result == "http://localhost:3000"

    class TestLocalhostUrls:
        """Tests for localhost URL handling."""

        def test_rejects_localhost_without_allow_http(self):
            with pytest.raises(ValueError, match="Localhost"):
                validate_base_url("https://localhost")
            with pytest.raises(ValueError, match="Localhost"):
                validate_base_url("https://127.0.0.1")
            with pytest.raises(ValueError, match="Localhost"):
                validate_base_url("https://0.0.0.0")

        def test_allows_localhost_with_allow_http(self):
            result = validate_base_url("http://localhost:3000", allow_http=True)
            assert result == "http://localhost:3000"
            result = validate_base_url("http://127.0.0.1:3000", allow_http=True)
            assert result == "http://127.0.0.1:3000"

    class TestInvalidUrls:
        """Tests for invalid URL inputs."""

        def test_rejects_empty_url(self):
            with pytest.raises(ValueError, match="cannot be empty"):
                validate_base_url("")

        def test_rejects_invalid_url_format(self):
            with pytest.raises(ValueError, match="scheme"):
                validate_base_url("not-a-url")

        def test_rejects_unsupported_schemes(self):
            with pytest.raises(ValueError, match="Invalid URL scheme"):
                validate_base_url("ftp://api.example.com")


class TestValidateWebhookUrl:
    """Tests for validate_webhook_url function."""

    class TestValidWebhookUrls:
        """Tests for valid webhook URL inputs."""

        def test_accepts_https_urls(self):
            result = validate_webhook_url("https://webhook.example.com")
            assert result == "https://webhook.example.com"

        def test_accepts_https_urls_with_paths(self):
            result = validate_webhook_url("https://example.com/webhook")
            assert result == "https://example.com/webhook"

        def test_accepts_https_urls_with_query_strings(self):
            result = validate_webhook_url("https://example.com/webhook?key=value")
            assert result == "https://example.com/webhook?key=value"

    class TestBlockedLocalhost:
        """Tests for blocking localhost."""

        def test_rejects_localhost(self):
            with pytest.raises(ValueError, match="localhost"):
                validate_webhook_url("https://localhost/webhook")

        def test_rejects_0_0_0_0(self):
            with pytest.raises(ValueError, match="localhost"):
                validate_webhook_url("https://0.0.0.0/webhook")

        def test_rejects_ipv4_loopback(self):
            with pytest.raises(ValueError, match="localhost"):
                validate_webhook_url("https://127.0.0.1/webhook")
            with pytest.raises(ValueError, match="localhost"):
                validate_webhook_url("https://127.1.2.3/webhook")
            with pytest.raises(ValueError, match="localhost"):
                validate_webhook_url("https://127.255.255.255/webhook")

        def test_rejects_ipv6_loopback(self):
            with pytest.raises(ValueError, match="localhost"):
                validate_webhook_url("https://[::1]/webhook")

    class TestBlockedPrivateIpv4Ranges:
        """Tests for blocking private IPv4 ranges."""

        def test_rejects_10_x_x_x(self):
            with pytest.raises(ValueError, match="private IP"):
                validate_webhook_url("https://10.0.0.1/webhook")
            with pytest.raises(ValueError, match="private IP"):
                validate_webhook_url("https://10.255.255.255/webhook")

        def test_rejects_192_168_x_x(self):
            with pytest.raises(ValueError, match="private IP"):
                validate_webhook_url("https://192.168.0.1/webhook")
            with pytest.raises(ValueError, match="private IP"):
                validate_webhook_url("https://192.168.255.255/webhook")

        def test_rejects_172_16_31_x_x(self):
            with pytest.raises(ValueError, match="private IP"):
                validate_webhook_url("https://172.16.0.1/webhook")
            with pytest.raises(ValueError, match="private IP"):
                validate_webhook_url("https://172.31.255.255/webhook")
            with pytest.raises(ValueError, match="private IP"):
                validate_webhook_url("https://172.20.0.1/webhook")

        def test_allows_172_outside_12_range(self):
            # These should not raise private IP error
            # 172.15.x.x and 172.32.x.x are technically public
            try:
                validate_webhook_url("https://172.15.0.1/webhook")
            except ValueError as e:
                assert "private IP" not in str(e)
            try:
                validate_webhook_url("https://172.32.0.1/webhook")
            except ValueError as e:
                assert "private IP" not in str(e)

    class TestBlockedLinkLocalAddresses:
        """Tests for blocking link-local addresses."""

        def test_rejects_169_254_x_x(self):
            with pytest.raises(ValueError, match="link-local"):
                validate_webhook_url("https://169.254.0.1/webhook")
            with pytest.raises(ValueError, match="link-local"):
                validate_webhook_url("https://169.254.255.255/webhook")

        def test_rejects_metadata_service(self):
            with pytest.raises(ValueError):
                validate_webhook_url("https://169.254.169.254/webhook")

    class TestBlockedIpv6PrivateRanges:
        """Tests for blocking IPv6 private ranges."""

        def test_rejects_fc00_7_unique_local(self):
            with pytest.raises(ValueError, match="private IPv6"):
                validate_webhook_url("https://[fc00::1]/webhook")
            with pytest.raises(ValueError, match="private IPv6"):
                validate_webhook_url("https://[fd00::1]/webhook")

        def test_rejects_fe80_10_link_local(self):
            with pytest.raises(ValueError, match="link-local"):
                validate_webhook_url("https://[fe80::1]/webhook")
            with pytest.raises(ValueError, match="link-local"):
                validate_webhook_url("https://[fe90::1]/webhook")
            with pytest.raises(ValueError, match="link-local"):
                validate_webhook_url("https://[fea0::1]/webhook")
            with pytest.raises(ValueError, match="link-local"):
                validate_webhook_url("https://[feb0::1]/webhook")

        def test_rejects_fec0_10_site_local_deprecated(self):
            with pytest.raises(ValueError, match="site-local"):
                validate_webhook_url("https://[fec0::1]/webhook")
            with pytest.raises(ValueError, match="site-local"):
                validate_webhook_url("https://[fed0::1]/webhook")
            with pytest.raises(ValueError, match="site-local"):
                validate_webhook_url("https://[fee0::1]/webhook")
            with pytest.raises(ValueError, match="site-local"):
                validate_webhook_url("https://[fef0::1]/webhook")

    class TestBlockedIpv6ZeroAddress:
        """Tests for blocking IPv6 zero address."""

        def test_rejects_zero_address(self):
            with pytest.raises(ValueError, match="zero address"):
                validate_webhook_url("https://[::]/webhook")

        def test_rejects_expanded_zero_address(self):
            with pytest.raises(ValueError, match="zero address"):
                validate_webhook_url("https://[0:0:0:0:0:0:0:0]/webhook")

    class TestBlockedIpv4MappedIpv6:
        """Tests for blocking IPv4-mapped IPv6 addresses."""

        def test_rejects_ffff_with_private_ipv4(self):
            with pytest.raises(ValueError, match="IPv4-mapped"):
                validate_webhook_url("https://[::ffff:127.0.0.1]/webhook")
            with pytest.raises(ValueError, match="IPv4-mapped"):
                validate_webhook_url("https://[::ffff:10.0.0.1]/webhook")
            with pytest.raises(ValueError, match="IPv4-mapped"):
                validate_webhook_url("https://[::ffff:192.168.1.1]/webhook")
            with pytest.raises(ValueError, match="IPv4-mapped"):
                validate_webhook_url("https://[::ffff:172.16.0.1]/webhook")
            with pytest.raises(ValueError, match="IPv4-mapped"):
                validate_webhook_url("https://[::ffff:169.254.1.1]/webhook")

    class TestBlockedNonHttps:
        """Tests for blocking non-HTTPS schemes."""

        def test_rejects_http(self):
            with pytest.raises(ValueError, match="HTTPS"):
                validate_webhook_url("http://example.com/webhook")

        def test_rejects_other_schemes(self):
            with pytest.raises(ValueError, match="HTTPS"):
                validate_webhook_url("ftp://example.com/webhook")


class TestRedactSensitiveData:
    """Tests for redact_sensitive_data function."""

    class TestRedactsSensitiveKeys:
        """Tests for redacting sensitive key values."""

        def test_redacts_api_key(self):
            data = {"api_key": "secret123", "name": "test"}
            result = redact_sensitive_data(data)
            assert result["api_key"] == "[REDACTED]"
            assert result["name"] == "test"

        def test_redacts_various_key_formats(self):
            data = {
                "apikey": "secret1",
                "api_key": "secret2",
                "api-key": "secret3",
                "token": "secret4",
                "jwt_token": "secret5",
                "password": "secret6",
                "secret": "secret7",
                "authorization": "secret8",
            }
            result = redact_sensitive_data(data)

            assert result["apikey"] == "[REDACTED]"
            assert result["api_key"] == "[REDACTED]"
            assert result["api-key"] == "[REDACTED]"
            assert result["token"] == "[REDACTED]"
            assert result["jwt_token"] == "[REDACTED]"
            assert result["password"] == "[REDACTED]"
            assert result["secret"] == "[REDACTED]"
            assert result["authorization"] == "[REDACTED]"

    class TestHandlesNestedObjects:
        """Tests for redacting nested objects."""

        def test_redacts_in_nested_objects(self):
            data = {
                "config": {
                    "api_key": "secret",
                    "name": "test",
                },
            }
            result = redact_sensitive_data(data)
            assert result["config"]["api_key"] == "[REDACTED]"
            assert result["config"]["name"] == "test"

    class TestHandlesArrays:
        """Tests for redacting arrays."""

        def test_redacts_in_arrays(self):
            data = [
                {"api_key": "secret1", "name": "test1"},
                {"api_key": "secret2", "name": "test2"},
            ]
            result = redact_sensitive_data(data)
            assert result[0]["api_key"] == "[REDACTED]"
            assert result[0]["name"] == "test1"
            assert result[1]["api_key"] == "[REDACTED]"

    class TestHandlesBearerTokens:
        """Tests for redacting Bearer tokens."""

        def test_redacts_bearer_tokens_in_strings(self):
            result = redact_sensitive_data("Bearer abc123xyz")
            assert result == "Bearer [REDACTED]"

        def test_does_not_modify_non_bearer_strings(self):
            result = redact_sensitive_data("normal string")
            assert result == "normal string"

    class TestHandlesMaxDepth:
        """Tests for max depth handling."""

        def test_stops_at_max_depth(self):
            deep_obj = {"a": {"b": {"c": {"d": {"e": "value"}}}}}
            result = redact_sensitive_data(deep_obj, max_depth=2)
            assert result["a"]["b"] == "[MAX DEPTH EXCEEDED]"

    class TestHandlesPrimitives:
        """Tests for primitive value handling."""

        def test_returns_primitives_unchanged(self):
            assert redact_sensitive_data(123) == 123
            assert redact_sensitive_data(True) is True
            assert redact_sensitive_data(None) is None


class TestMaskCredential:
    """Tests for mask_credential function."""

    def test_masks_all_but_last_4_characters_by_default(self):
        assert mask_credential("secretkey123") == "********y123"

    def test_masks_with_custom_visible_characters(self):
        assert mask_credential("secretkey123", 6) == "******key123"

    def test_handles_short_credentials(self):
        assert mask_credential("abc") == "***"
        assert mask_credential("ab") == "**"

    def test_handles_empty_credential(self):
        assert mask_credential("") == "[EMPTY]"

    def test_handles_credential_equal_to_visible_chars(self):
        assert mask_credential("abcd", 4) == "****"


class TestGetEnvCredential:
    """Tests for get_env_credential function."""

    def test_gets_credential_from_environment(self, monkeypatch):
        monkeypatch.setenv("TRIX_API_KEY", "test_key")
        assert get_env_credential("TRIX_API_KEY") == "test_key"

    def test_trims_whitespace(self, monkeypatch):
        monkeypatch.setenv("TRIX_API_KEY", "  test_key  ")
        assert get_env_credential("TRIX_API_KEY") == "test_key"

    def test_throws_when_required_and_not_set(self, monkeypatch):
        monkeypatch.delenv("TRIX_API_KEY", raising=False)
        with pytest.raises(ValueError, match="not set"):
            get_env_credential("TRIX_API_KEY", required=True)

    def test_returns_none_when_not_required_and_not_set(self, monkeypatch):
        monkeypatch.delenv("TRIX_API_KEY", raising=False)
        result = get_env_credential("TRIX_API_KEY", required=False)
        assert result is None

    def test_throws_when_required_and_empty(self, monkeypatch):
        monkeypatch.setenv("TRIX_API_KEY", "   ")
        with pytest.raises(ValueError):
            get_env_credential("TRIX_API_KEY", required=True)


class TestValidateLimit:
    """Tests for validate_limit function."""

    def test_accepts_valid_limits(self):
        assert validate_limit(1) == 1
        assert validate_limit(100) == 100
        assert validate_limit(1000) == 1000

    def test_rejects_zero_limit(self):
        with pytest.raises(ValueError, match="at least 1"):
            validate_limit(0)

    def test_rejects_negative_limit(self):
        with pytest.raises(ValueError, match="at least 1"):
            validate_limit(-1)

    def test_rejects_limit_exceeding_max(self):
        with pytest.raises(ValueError, match="cannot exceed"):
            validate_limit(1001)

    def test_accepts_custom_max_limit(self):
        assert validate_limit(500, max_limit=500) == 500
        with pytest.raises(ValueError, match="cannot exceed"):
            validate_limit(501, max_limit=500)

    def test_rejects_non_integer(self):
        with pytest.raises(ValueError, match="must be an integer"):
            validate_limit(1.5)  # type: ignore


class TestValidateOffset:
    """Tests for validate_offset function."""

    def test_accepts_zero_offset(self):
        assert validate_offset(0) == 0

    def test_accepts_positive_offset(self):
        assert validate_offset(100) == 100

    def test_rejects_negative_offset(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            validate_offset(-1)

    def test_rejects_non_integer(self):
        with pytest.raises(ValueError, match="must be an integer"):
            validate_offset(1.5)  # type: ignore


class TestValidateThreshold:
    """Tests for validate_threshold function."""

    def test_accepts_valid_thresholds(self):
        assert validate_threshold(0.0) == 0.0
        assert validate_threshold(0.5) == 0.5
        assert validate_threshold(1.0) == 1.0

    def test_rejects_threshold_below_minimum(self):
        with pytest.raises(ValueError, match="between"):
            validate_threshold(-0.1)

    def test_rejects_threshold_above_maximum(self):
        with pytest.raises(ValueError, match="between"):
            validate_threshold(1.1)

    def test_accepts_custom_range(self):
        assert validate_threshold(5.0, min_value=0.0, max_value=10.0) == 5.0
        with pytest.raises(ValueError):
            validate_threshold(11.0, min_value=0.0, max_value=10.0)

    def test_accepts_integers(self):
        assert validate_threshold(1) == 1.0

    def test_rejects_non_numeric(self):
        with pytest.raises(ValueError, match="must be a number"):
            validate_threshold("0.5")  # type: ignore


class TestValidatePositiveInt:
    """Tests for validate_positive_int function."""

    def test_accepts_positive_integers(self):
        assert validate_positive_int(1) == 1
        assert validate_positive_int(100) == 100

    def test_rejects_zero_by_default(self):
        with pytest.raises(ValueError, match="at least 1"):
            validate_positive_int(0)

    def test_accepts_zero_when_allowed(self):
        assert validate_positive_int(0, allow_zero=True) == 0

    def test_rejects_negative(self):
        with pytest.raises(ValueError):
            validate_positive_int(-1)
        with pytest.raises(ValueError):
            validate_positive_int(-1, allow_zero=True)

    def test_rejects_non_integer(self):
        with pytest.raises(ValueError, match="must be an integer"):
            validate_positive_int(1.5)  # type: ignore
