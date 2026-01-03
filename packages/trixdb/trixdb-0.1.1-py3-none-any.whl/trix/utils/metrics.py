"""Metrics and observability utilities for Trix SDK."""

import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterator, List, Optional


@dataclass
class RequestMetrics:
    """Metrics for a single HTTP request.

    Attributes:
        method: HTTP method (GET, POST, etc.)
        path: Request path
        status_code: HTTP status code (None if request failed)
        duration_ms: Request duration in milliseconds
        request_size: Size of request body in bytes (if known)
        response_size: Size of response body in bytes (if known)
        error: Error type if request failed
        retry_count: Number of retries before success/failure
        timestamp: Unix timestamp when request started
        labels: Additional custom labels
    """

    method: str
    path: str
    status_code: Optional[int] = None
    duration_ms: float = 0.0
    request_size: Optional[int] = None
    response_size: Optional[int] = None
    error: Optional[str] = None
    retry_count: int = 0
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """Whether the request was successful."""
        return self.status_code is not None and 200 <= self.status_code < 400


class MetricsCollector(ABC):
    """Abstract base class for metrics collectors.

    Implement this interface to send metrics to your preferred
    monitoring system (Prometheus, Datadog, OpenTelemetry, etc.).

    Example:
        >>> class PrometheusCollector(MetricsCollector):
        ...     def on_request_complete(self, metrics: RequestMetrics) -> None:
        ...         # Send to Prometheus
        ...         requests_total.labels(
        ...             method=metrics.method,
        ...             status=str(metrics.status_code)
        ...         ).inc()
        ...         request_duration.labels(
        ...             method=metrics.method
        ...         ).observe(metrics.duration_ms / 1000)
    """

    @abstractmethod
    def on_request_complete(self, metrics: RequestMetrics) -> None:
        """Called when a request completes (success or failure).

        Args:
            metrics: Metrics for the completed request.
        """
        pass

    def on_request_start(
        self, method: str, path: str, labels: Optional[Dict[str, str]] = None
    ) -> None:
        """Called when a request starts.

        Override to track in-flight requests or start spans.

        Args:
            method: HTTP method
            path: Request path
            labels: Additional labels
        """
        pass

    def on_retry(
        self,
        method: str,
        path: str,
        attempt: int,
        error: Exception,
        delay_ms: float,
    ) -> None:
        """Called when a request is being retried.

        Args:
            method: HTTP method
            path: Request path
            attempt: Retry attempt number (1, 2, 3, ...)
            error: The error that triggered the retry
            delay_ms: Delay before retry in milliseconds
        """
        pass


class NoOpCollector(MetricsCollector):
    """No-op metrics collector that does nothing."""

    def on_request_complete(self, metrics: RequestMetrics) -> None:
        pass


class InMemoryCollector(MetricsCollector):
    """In-memory metrics collector for testing and debugging.

    Stores metrics in memory for later inspection.

    Example:
        >>> collector = InMemoryCollector()
        >>> # ... make requests ...
        >>> print(f"Total requests: {collector.request_count}")
        >>> print(f"Avg latency: {collector.average_latency_ms}ms")
    """

    def __init__(self, max_entries: int = 10000) -> None:
        self.max_entries = max_entries
        self._metrics: List[RequestMetrics] = []
        self._retries: List[Dict[str, Any]] = []

    @property
    def metrics(self) -> List[RequestMetrics]:
        """Get all recorded metrics."""
        return list(self._metrics)

    @property
    def request_count(self) -> int:
        """Get total number of requests."""
        return len(self._metrics)

    @property
    def success_count(self) -> int:
        """Get number of successful requests."""
        return sum(1 for m in self._metrics if m.success)

    @property
    def error_count(self) -> int:
        """Get number of failed requests."""
        return sum(1 for m in self._metrics if not m.success)

    @property
    def retry_count(self) -> int:
        """Get total number of retries."""
        return len(self._retries)

    @property
    def average_latency_ms(self) -> float:
        """Get average request latency in milliseconds."""
        if not self._metrics:
            return 0.0
        return sum(m.duration_ms for m in self._metrics) / len(self._metrics)

    @property
    def p50_latency_ms(self) -> float:
        """Get 50th percentile latency."""
        return self._percentile(50)

    @property
    def p95_latency_ms(self) -> float:
        """Get 95th percentile latency."""
        return self._percentile(95)

    @property
    def p99_latency_ms(self) -> float:
        """Get 99th percentile latency."""
        return self._percentile(99)

    def _percentile(self, p: float) -> float:
        """Calculate percentile of latencies."""
        if not self._metrics:
            return 0.0
        sorted_latencies = sorted(m.duration_ms for m in self._metrics)
        idx = int((len(sorted_latencies) - 1) * p / 100)
        return sorted_latencies[idx]

    def get_metrics_by_method(self, method: str) -> List[RequestMetrics]:
        """Get metrics filtered by HTTP method."""
        return [m for m in self._metrics if m.method == method]

    def get_metrics_by_path(self, path: str) -> List[RequestMetrics]:
        """Get metrics filtered by path."""
        return [m for m in self._metrics if path in m.path]

    def get_error_metrics(self) -> List[RequestMetrics]:
        """Get metrics for failed requests."""
        return [m for m in self._metrics if not m.success]

    def clear(self) -> None:
        """Clear all recorded metrics."""
        self._metrics.clear()
        self._retries.clear()

    def on_request_complete(self, metrics: RequestMetrics) -> None:
        if len(self._metrics) >= self.max_entries:
            self._metrics.pop(0)
        self._metrics.append(metrics)

    def on_retry(
        self,
        method: str,
        path: str,
        attempt: int,
        error: Exception,
        delay_ms: float,
    ) -> None:
        if len(self._retries) >= self.max_entries:
            self._retries.pop(0)
        self._retries.append(
            {
                "method": method,
                "path": path,
                "attempt": attempt,
                "error": type(error).__name__,
                "delay_ms": delay_ms,
                "timestamp": time.time(),
            }
        )


class CompositeCollector(MetricsCollector):
    """Composite collector that delegates to multiple collectors.

    Example:
        >>> collector = CompositeCollector([
        ...     PrometheusCollector(),
        ...     InMemoryCollector(),
        ... ])
    """

    def __init__(self, collectors: List[MetricsCollector]) -> None:
        self._collectors = collectors

    def add(self, collector: MetricsCollector) -> None:
        """Add a collector."""
        self._collectors.append(collector)

    def remove(self, collector: MetricsCollector) -> None:
        """Remove a collector."""
        self._collectors.remove(collector)

    def on_request_start(
        self, method: str, path: str, labels: Optional[Dict[str, str]] = None
    ) -> None:
        for collector in self._collectors:
            collector.on_request_start(method, path, labels)

    def on_request_complete(self, metrics: RequestMetrics) -> None:
        for collector in self._collectors:
            collector.on_request_complete(metrics)

    def on_retry(
        self,
        method: str,
        path: str,
        attempt: int,
        error: Exception,
        delay_ms: float,
    ) -> None:
        for collector in self._collectors:
            collector.on_retry(method, path, attempt, error, delay_ms)


class CallbackCollector(MetricsCollector):
    """Collector that calls user-provided callbacks.

    Example:
        >>> def on_complete(m: RequestMetrics):
        ...     print(f"{m.method} {m.path}: {m.duration_ms}ms")
        >>> collector = CallbackCollector(on_complete=on_complete)
    """

    def __init__(
        self,
        on_complete: Optional[Callable[[RequestMetrics], None]] = None,
        on_start: Optional[Callable[[str, str, Optional[Dict[str, str]]], None]] = None,
        on_retry: Optional[Callable[[str, str, int, Exception, float], None]] = None,
    ) -> None:
        self._on_complete = on_complete
        self._on_start = on_start
        self._on_retry = on_retry

    def on_request_start(
        self, method: str, path: str, labels: Optional[Dict[str, str]] = None
    ) -> None:
        if self._on_start:
            self._on_start(method, path, labels)

    def on_request_complete(self, metrics: RequestMetrics) -> None:
        if self._on_complete:
            self._on_complete(metrics)

    def on_retry(
        self,
        method: str,
        path: str,
        attempt: int,
        error: Exception,
        delay_ms: float,
    ) -> None:
        if self._on_retry:
            self._on_retry(method, path, attempt, error, delay_ms)


# Global metrics collector
_global_collector: MetricsCollector = NoOpCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector."""
    return _global_collector


def set_metrics_collector(collector: MetricsCollector) -> None:
    """Set the global metrics collector.

    Args:
        collector: The collector to use globally.

    Example:
        >>> from trix.utils.metrics import set_metrics_collector, InMemoryCollector
        >>> collector = InMemoryCollector()
        >>> set_metrics_collector(collector)
    """
    global _global_collector
    _global_collector = collector


@contextmanager
def timed_request(
    method: str,
    path: str,
    labels: Optional[Dict[str, str]] = None,
    collector: Optional[MetricsCollector] = None,
) -> Iterator[RequestMetrics]:
    """Context manager for timing requests and recording metrics.

    Args:
        method: HTTP method
        path: Request path
        labels: Additional labels
        collector: Metrics collector (uses global if not specified)

    Yields:
        RequestMetrics object to populate with results

    Example:
        >>> with timed_request("GET", "/memories") as metrics:
        ...     response = make_request()
        ...     metrics.status_code = response.status_code
        ...     metrics.response_size = len(response.content)
    """
    if collector is None:
        collector = _global_collector

    metrics = RequestMetrics(
        method=method,
        path=path,
        labels=labels or {},
    )

    collector.on_request_start(method, path, labels)
    start = time.perf_counter()

    try:
        yield metrics
    except Exception as e:
        metrics.error = type(e).__name__
        raise
    finally:
        metrics.duration_ms = (time.perf_counter() - start) * 1000
        collector.on_request_complete(metrics)


def record_retry(
    method: str,
    path: str,
    attempt: int,
    error: Exception,
    delay_ms: float,
    collector: Optional[MetricsCollector] = None,
) -> None:
    """Record a retry attempt.

    Args:
        method: HTTP method
        path: Request path
        attempt: Retry attempt number
        error: Error that triggered the retry
        delay_ms: Delay before retry in milliseconds
        collector: Metrics collector (uses global if not specified)
    """
    if collector is None:
        collector = _global_collector
    collector.on_retry(method, path, attempt, error, delay_ms)
