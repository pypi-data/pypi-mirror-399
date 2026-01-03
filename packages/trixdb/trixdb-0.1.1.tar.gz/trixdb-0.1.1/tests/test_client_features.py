"""Tests for new Trix client features: connection pooling, timeouts, interceptors."""

import pytest
import httpx

from trix import (
    Trix,
    AsyncTrix,
    PoolConfig,
    RequestContext,
    ResponseContext,
)


class TestPoolConfig:
    """Tests for PoolConfig."""

    def test_default_values(self):
        """Test PoolConfig default values."""
        config = PoolConfig()
        assert config.max_connections == 100
        assert config.max_keepalive_connections == 20
        assert config.keepalive_expiry == 5.0

    def test_custom_values(self):
        """Test PoolConfig with custom values."""
        config = PoolConfig(
            max_connections=50,
            max_keepalive_connections=10,
            keepalive_expiry=10.0,
        )
        assert config.max_connections == 50
        assert config.max_keepalive_connections == 10
        assert config.keepalive_expiry == 10.0

    def test_to_httpx_limits(self):
        """Test conversion to httpx.Limits."""
        config = PoolConfig(
            max_connections=50,
            max_keepalive_connections=10,
            keepalive_expiry=10.0,
        )
        limits = config.to_httpx_limits()
        assert isinstance(limits, httpx.Limits)
        assert limits.max_connections == 50
        assert limits.max_keepalive_connections == 10
        assert limits.keepalive_expiry == 10.0


class TestClientPoolConfig:
    """Tests for client with pool configuration."""

    def test_sync_client_with_pool_config(self):
        """Test sync client accepts pool configuration."""
        pool_config = PoolConfig(max_connections=50)
        client = Trix(api_key="test_key", pool_config=pool_config)
        assert client._pool_config.max_connections == 50
        client.close()

    def test_sync_client_default_pool_config(self):
        """Test sync client has default pool configuration."""
        client = Trix(api_key="test_key")
        assert client._pool_config is not None
        assert client._pool_config.max_connections == 100
        client.close()

    @pytest.mark.asyncio
    async def test_async_client_with_pool_config(self):
        """Test async client accepts pool configuration."""
        pool_config = PoolConfig(max_connections=75)
        client = AsyncTrix(api_key="test_key", pool_config=pool_config)
        assert client._pool_config.max_connections == 75
        await client.close()


class TestRequestContext:
    """Tests for RequestContext dataclass."""

    def test_request_context_creation(self):
        """Test RequestContext creation."""
        ctx = RequestContext(
            method="GET",
            path="/test",
            headers={"Authorization": "Bearer token"},
            json={"key": "value"},
            params={"limit": 10},
        )
        assert ctx.method == "GET"
        assert ctx.path == "/test"
        assert ctx.headers["Authorization"] == "Bearer token"
        assert ctx.json == {"key": "value"}
        assert ctx.params == {"limit": 10}

    def test_request_context_optional_fields(self):
        """Test RequestContext with optional fields."""
        ctx = RequestContext(
            method="GET",
            path="/test",
            headers={},
        )
        assert ctx.json is None
        assert ctx.params is None


class TestResponseContext:
    """Tests for ResponseContext dataclass."""

    def test_response_context_creation(self):
        """Test ResponseContext creation."""
        req_ctx = RequestContext(method="GET", path="/test")
        ctx = ResponseContext(
            request=req_ctx,
            status_code=200,
            headers={"Content-Type": "application/json"},
            data={"id": "123"},
        )
        assert ctx.status_code == 200
        assert ctx.headers["Content-Type"] == "application/json"
        assert ctx.data == {"id": "123"}
        assert ctx.request.method == "GET"


class TestRequestInterceptors:
    """Tests for request interceptors."""

    def test_add_request_interceptor(self):
        """Test adding a request interceptor."""
        client = Trix(api_key="test_key")

        interceptor_called = []

        def interceptor(ctx: RequestContext) -> RequestContext:
            interceptor_called.append(ctx.method)
            return ctx

        remove = client.add_request_interceptor(interceptor)
        assert callable(remove)
        assert len(client._request_interceptors) == 1
        client.close()

    def test_remove_request_interceptor(self):
        """Test removing a request interceptor."""
        client = Trix(api_key="test_key")

        def interceptor(ctx: RequestContext) -> RequestContext:
            return ctx

        remove = client.add_request_interceptor(interceptor)
        assert len(client._request_interceptors) == 1

        remove()
        assert len(client._request_interceptors) == 0
        client.close()

    def test_multiple_request_interceptors(self):
        """Test multiple request interceptors run in order."""
        client = Trix(api_key="test_key")

        call_order = []

        def interceptor1(ctx: RequestContext) -> RequestContext:
            call_order.append(1)
            return ctx

        def interceptor2(ctx: RequestContext) -> RequestContext:
            call_order.append(2)
            return ctx

        client.add_request_interceptor(interceptor1)
        client.add_request_interceptor(interceptor2)

        ctx = RequestContext(method="GET", path="/test")
        client._run_request_interceptors(ctx)

        assert call_order == [1, 2]
        client.close()

    def test_request_interceptor_modifies_context(self):
        """Test request interceptor can modify context."""
        client = Trix(api_key="test_key")

        def add_header(ctx: RequestContext) -> RequestContext:
            ctx.headers["X-Custom"] = "value"
            return ctx

        client.add_request_interceptor(add_header)

        ctx = RequestContext(method="GET", path="/test", headers={})
        result = client._run_request_interceptors(ctx)

        assert result.headers["X-Custom"] == "value"
        client.close()

    def test_request_interceptor_from_config(self):
        """Test request interceptor from config."""
        interceptor_called = []

        def interceptor(ctx: RequestContext) -> RequestContext:
            interceptor_called.append(True)
            return ctx

        client = Trix(
            api_key="test_key",
            request_interceptors=[interceptor],
        )
        assert len(client._request_interceptors) == 1
        client.close()


class TestResponseInterceptors:
    """Tests for response interceptors."""

    def test_add_response_interceptor(self):
        """Test adding a response interceptor."""
        client = Trix(api_key="test_key")

        def interceptor(ctx: ResponseContext) -> ResponseContext:
            return ctx

        remove = client.add_response_interceptor(interceptor)
        assert callable(remove)
        assert len(client._response_interceptors) == 1
        client.close()

    def test_response_interceptor_modifies_context(self):
        """Test response interceptor can modify context."""
        client = Trix(api_key="test_key")

        def transform_data(ctx: ResponseContext) -> ResponseContext:
            ctx.data["transformed"] = True
            return ctx

        client.add_response_interceptor(transform_data)

        req_ctx = RequestContext(method="GET", path="/test")
        ctx = ResponseContext(request=req_ctx, status_code=200, headers={}, data={"id": "123"})
        result = client._run_response_interceptors(ctx)

        assert result.data["transformed"] is True
        client.close()


class TestErrorInterceptors:
    """Tests for error interceptors."""

    def test_add_error_interceptor(self):
        """Test adding an error interceptor."""
        client = Trix(api_key="test_key")

        def interceptor(err: Exception, ctx: RequestContext) -> Exception:
            return err

        remove = client.add_error_interceptor(interceptor)
        assert callable(remove)
        assert len(client._error_interceptors) == 1
        client.close()

    def test_error_interceptor_transforms_error(self):
        """Test error interceptor can transform errors."""
        client = Trix(api_key="test_key")

        class CustomError(Exception):
            pass

        def transform_error(err: Exception, ctx: RequestContext) -> Exception:
            return CustomError(f"Wrapped: {err}")

        client.add_error_interceptor(transform_error)

        original_error = ValueError("Original error")
        ctx = RequestContext(method="GET", path="/test")
        result = client._run_error_interceptors(original_error, ctx)

        assert isinstance(result, CustomError)
        assert "Wrapped:" in str(result)
        client.close()

    def test_error_interceptor_receives_request_context(self):
        """Test error interceptor receives request context."""
        client = Trix(api_key="test_key")

        received_ctx = []

        def log_error(err: Exception, ctx: RequestContext) -> Exception:
            received_ctx.append(ctx)
            return err

        client.add_error_interceptor(log_error)

        ctx = RequestContext(method="POST", path="/memories")
        client._run_error_interceptors(ValueError("test"), ctx)

        assert len(received_ctx) == 1
        assert received_ctx[0].method == "POST"
        assert received_ctx[0].path == "/memories"
        client.close()


class TestPerRequestTimeout:
    """Tests for per-request timeout override."""

    def test_client_stores_default_timeout(self):
        """Test client stores default timeout."""
        client = Trix(api_key="test_key", timeout=45.0)
        assert client._timeout == 45.0
        client.close()

    @pytest.mark.asyncio
    async def test_async_client_stores_default_timeout(self):
        """Test async client stores default timeout."""
        client = AsyncTrix(api_key="test_key", timeout=60.0)
        assert client._timeout == 60.0
        await client.close()


class TestStreamingSupport:
    """Tests for streaming response support."""

    def test_client_has_request_stream_method(self):
        """Test sync client has _request_stream method."""
        client = Trix(api_key="test_key")
        assert hasattr(client, "_request_stream")
        assert callable(client._request_stream)
        client.close()

    @pytest.mark.asyncio
    async def test_async_client_has_request_stream_method(self):
        """Test async client has _request_stream method."""
        client = AsyncTrix(api_key="test_key")
        assert hasattr(client, "_request_stream")
        assert callable(client._request_stream)
        await client.close()


class TestMultipartSupport:
    """Tests for multipart/form-data support."""

    def test_client_has_request_multipart_method(self):
        """Test sync client has _request_multipart method."""
        client = Trix(api_key="test_key")
        assert hasattr(client, "_request_multipart")
        assert callable(client._request_multipart)
        client.close()

    @pytest.mark.asyncio
    async def test_async_client_has_request_multipart_method(self):
        """Test async client has _request_multipart method."""
        client = AsyncTrix(api_key="test_key")
        assert hasattr(client, "_request_multipart")
        assert callable(client._request_multipart)
        await client.close()


class TestInterceptorIntegration:
    """Integration tests for interceptors with actual request flow."""

    def test_interceptors_chain_correctly(self):
        """Test interceptors chain in correct order."""
        client = Trix(api_key="test_key")

        execution_order = []

        def req_interceptor1(ctx: RequestContext) -> RequestContext:
            execution_order.append("req1")
            return ctx

        def req_interceptor2(ctx: RequestContext) -> RequestContext:
            execution_order.append("req2")
            return ctx

        def res_interceptor1(ctx: ResponseContext) -> ResponseContext:
            execution_order.append("res1")
            return ctx

        def res_interceptor2(ctx: ResponseContext) -> ResponseContext:
            execution_order.append("res2")
            return ctx

        client.add_request_interceptor(req_interceptor1)
        client.add_request_interceptor(req_interceptor2)
        client.add_response_interceptor(res_interceptor1)
        client.add_response_interceptor(res_interceptor2)

        # Run request interceptors
        req_ctx = RequestContext(method="GET", path="/test")
        client._run_request_interceptors(req_ctx)

        # Run response interceptors
        res_ctx = ResponseContext(request=req_ctx, status_code=200, headers={}, data={})
        client._run_response_interceptors(res_ctx)

        assert execution_order == ["req1", "req2", "res1", "res2"]
        client.close()

    def test_interceptor_returns_none_preserves_context(self):
        """Test interceptor returning None preserves previous context."""
        client = Trix(api_key="test_key")

        def observe_only(ctx: RequestContext):
            # Just observe, don't return anything
            pass

        def modify(ctx: RequestContext) -> RequestContext:
            ctx.headers["Modified"] = "true"
            return ctx

        client.add_request_interceptor(observe_only)
        client.add_request_interceptor(modify)

        ctx = RequestContext(method="GET", path="/test", headers={})
        result = client._run_request_interceptors(ctx)

        assert result.headers.get("Modified") == "true"
        client.close()
