"""
OpenTelemetry integration for Trix SDK.

This module provides optional OpenTelemetry integration for distributed tracing.
The opentelemetry-api package is an optional dependency.

Example:
    >>> from opentelemetry import trace
    >>> from trix import configure_telemetry
    >>>
    >>> # Configure with your tracer
    >>> configure_telemetry(
    ...     tracer=trace.get_tracer("my-service"),
    ...     record_request_body=False,
    ...     record_response_body=False,
    ... )
    >>>
    >>> # All requests will now create spans automatically
    >>> client = Trix(api_key="...")
"""

from __future__ import annotations

import functools
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Generator,
    Optional,
    Protocol,
    TypeVar,
    Union,
)

if TYPE_CHECKING:
    pass


# Type definitions that mirror OpenTelemetry API to avoid hard dependency
class SpanProtocol(Protocol):
    """Protocol for OpenTelemetry-compatible Span."""

    def set_attribute(self, key: str, value: Union[str, int, float, bool]) -> None:
        """Set an attribute on the span."""
        ...

    def set_status(self, status: Any) -> None:
        """Set the status of the span."""
        ...

    def record_exception(self, exception: BaseException) -> None:
        """Record an exception on the span."""
        ...

    def end(self) -> None:
        """End the span."""
        ...


class TracerProtocol(Protocol):
    """Protocol for OpenTelemetry-compatible Tracer."""

    def start_span(
        self,
        name: str,
        kind: Optional[Any] = None,
        attributes: Optional[dict[str, Any]] = None,
    ) -> SpanProtocol:
        """Start a new span."""
        ...


# Span status codes (mirrors OpenTelemetry)
class SpanStatusCode:
    """Span status codes matching OpenTelemetry conventions."""

    UNSET = 0
    OK = 1
    ERROR = 2


# Span kinds (mirrors OpenTelemetry)
class SpanKind:
    """Span kinds matching OpenTelemetry conventions."""

    INTERNAL = 0
    SERVER = 1
    CLIENT = 2
    PRODUCER = 3
    CONSUMER = 4


@dataclass
class TelemetryConfig:
    """Configuration for OpenTelemetry integration.

    Attributes:
        tracer: OpenTelemetry Tracer instance
        record_request_body: Whether to record request bodies in span attributes
        record_response_body: Whether to record response bodies in span attributes
        span_name_prefix: Custom span name prefix (default: 'trix')
        default_attributes: Additional attributes to add to all spans
    """

    tracer: Optional[TracerProtocol] = None
    record_request_body: bool = False
    record_response_body: bool = False
    span_name_prefix: str = "trix"
    default_attributes: dict[str, Union[str, int, float, bool]] = field(default_factory=dict)


# Global telemetry configuration
_global_config = TelemetryConfig()


def configure_telemetry(
    tracer: Optional[TracerProtocol] = None,
    record_request_body: bool = False,
    record_response_body: bool = False,
    span_name_prefix: str = "trix",
    default_attributes: Optional[dict[str, Union[str, int, float, bool]]] = None,
) -> None:
    """Configure OpenTelemetry integration.

    Args:
        tracer: OpenTelemetry Tracer instance
        record_request_body: Whether to record request bodies in span attributes
        record_response_body: Whether to record response bodies in span attributes
        span_name_prefix: Custom span name prefix (default: 'trix')
        default_attributes: Additional attributes to add to all spans

    Example:
        >>> from opentelemetry import trace
        >>> from trix import configure_telemetry
        >>>
        >>> configure_telemetry(
        ...     tracer=trace.get_tracer("my-service", "1.0.0"),
        ...     span_name_prefix="trix",
        ...     default_attributes={
        ...         "service.name": "my-app",
        ...         "deployment.environment": "production",
        ...     },
        ... )
    """
    global _global_config
    _global_config = TelemetryConfig(
        tracer=tracer,
        record_request_body=record_request_body,
        record_response_body=record_response_body,
        span_name_prefix=span_name_prefix,
        default_attributes=default_attributes or {},
    )


def get_telemetry_config() -> TelemetryConfig:
    """Get current telemetry configuration."""
    return _global_config


def is_telemetry_enabled() -> bool:
    """Check if telemetry is enabled."""
    return _global_config.tracer is not None


class RequestSpan:
    """Request span wrapper interface."""

    def set_request_body(self, body: Any) -> None:
        """Set request body attribute (if enabled in config)."""
        pass

    def set_status_code(self, code: int) -> None:
        """Set response status code."""
        pass

    def set_response_body(self, body: Any) -> None:
        """Set response body attribute (if enabled in config)."""
        pass

    def set_response_size(self, size: int) -> None:
        """Set response size in bytes."""
        pass

    def record_error(self, error: BaseException) -> None:
        """Record an error."""
        pass

    def success(self) -> None:
        """Mark span as successful and end it."""
        pass

    def failure(self, message: Optional[str] = None) -> None:
        """Mark span as failed and end it."""
        pass

    def set_attribute(self, key: str, value: Union[str, int, float, bool]) -> None:
        """Add custom attribute."""
        pass


class NoOpRequestSpan(RequestSpan):
    """No-op span implementation when telemetry is disabled."""

    pass


class ActiveRequestSpan(RequestSpan):
    """Active span implementation."""

    def __init__(self, span: SpanProtocol, config: TelemetryConfig) -> None:
        self._span = span
        self._config = config

    def set_request_body(self, body: Any) -> None:
        if self._config.record_request_body and body:
            try:
                import json

                body_str = body if isinstance(body, str) else json.dumps(body)
                # Truncate large bodies
                if len(body_str) > 1000:
                    body_str = body_str[:1000] + "..."
                self._span.set_attribute("http.request.body", body_str)
            except Exception:
                pass  # Ignore serialization errors

    def set_status_code(self, code: int) -> None:
        self._span.set_attribute("http.status_code", code)

    def set_response_body(self, body: Any) -> None:
        if self._config.record_response_body and body:
            try:
                import json

                body_str = body if isinstance(body, str) else json.dumps(body)
                if len(body_str) > 1000:
                    body_str = body_str[:1000] + "..."
                self._span.set_attribute("http.response.body", body_str)
            except Exception:
                pass  # Ignore serialization errors

    def set_response_size(self, size: int) -> None:
        self._span.set_attribute("http.response_content_length", size)

    def record_error(self, error: BaseException) -> None:
        self._span.record_exception(error)
        self._span.set_attribute("error.type", type(error).__name__)
        self._span.set_attribute("error.message", str(error))

    def success(self) -> None:
        try:
            from opentelemetry.trace import Status, StatusCode

            self._span.set_status(Status(StatusCode.OK))
        except ImportError:
            pass
        self._span.end()

    def failure(self, message: Optional[str] = None) -> None:
        try:
            from opentelemetry.trace import Status, StatusCode

            self._span.set_status(Status(StatusCode.ERROR, message))
        except ImportError:
            pass
        self._span.end()

    def set_attribute(self, key: str, value: Union[str, int, float, bool]) -> None:
        self._span.set_attribute(key, value)


def create_request_span(method: str, path: str, operation: str) -> RequestSpan:
    """Create a span for an HTTP request.

    Args:
        method: HTTP method
        path: Request path
        operation: Operation name (e.g., 'memories.create')

    Returns:
        RequestSpan wrapper with helper methods
    """
    config = _global_config

    if not config.tracer:
        return NoOpRequestSpan()

    span_name = f"{config.span_name_prefix}.{operation}"

    try:
        from opentelemetry.trace import SpanKind as OTelSpanKind

        span = config.tracer.start_span(
            span_name,
            kind=OTelSpanKind.CLIENT,
            attributes={
                "http.method": method,
                "http.url": path,
                "rpc.system": "http",
                "rpc.service": "trix",
                "rpc.method": operation,
                **config.default_attributes,
            },
        )
    except ImportError:
        # Fallback if opentelemetry not installed with full types
        span = config.tracer.start_span(
            span_name,
            attributes={
                "http.method": method,
                "http.url": path,
                "rpc.system": "http",
                "rpc.service": "trix",
                "rpc.method": operation,
                **config.default_attributes,
            },
        )

    return ActiveRequestSpan(span, config)


F = TypeVar("F", bound=Callable[..., Any])


def traced(operation: str) -> Callable[[F], F]:
    """Decorator to automatically create spans for methods.

    Args:
        operation: Operation name for the span

    Example:
        >>> class MyResource:
        ...     @traced("myResource.do_something")
        ...     def do_something(self) -> Result:
        ...         # This method will automatically create a span
        ...         pass
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            span = create_request_span("INTERNAL", operation, operation)
            try:
                result = func(*args, **kwargs)
                span.success()
                return result
            except Exception as e:
                span.record_error(e)
                span.failure(str(e))
                raise

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            span = create_request_span("INTERNAL", operation, operation)
            try:
                result = await func(*args, **kwargs)
                span.success()
                return result
            except Exception as e:
                span.record_error(e)
                span.failure(str(e))
                raise

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper  # type: ignore

    return decorator


@contextmanager
def with_tracing(operation: str) -> Generator[RequestSpan, None, None]:
    """Context manager to wrap code with tracing.

    Args:
        operation: Operation name for the span

    Yields:
        RequestSpan for adding custom attributes

    Example:
        >>> with with_tracing("custom.operation") as span:
        ...     span.set_attribute("custom.key", "value")
        ...     result = some_work()
    """
    span = create_request_span("INTERNAL", operation, operation)
    try:
        yield span
        span.success()
    except Exception as e:
        span.record_error(e)
        span.failure(str(e))
        raise


async def with_tracing_async(operation: str, func: Callable[[], Awaitable[Any]]) -> Any:
    """Utility to wrap an async function with tracing.

    Args:
        operation: Operation name for the span
        func: Async function to trace

    Returns:
        Result of the function

    Example:
        >>> result = await with_tracing_async(
        ...     "custom.operation",
        ...     some_async_work
        ... )
    """
    span = create_request_span("INTERNAL", operation, operation)
    try:
        result = await func()
        span.success()
        return result
    except Exception as e:
        span.record_error(e)
        span.failure(str(e))
        raise
