"""Tests for Trix metrics and observability utilities."""

import time

import pytest

from trix.utils.metrics import (
    CallbackCollector,
    CompositeCollector,
    InMemoryCollector,
    NoOpCollector,
    RequestMetrics,
    get_metrics_collector,
    record_retry,
    set_metrics_collector,
    timed_request,
)


class TestRequestMetrics:
    """Tests for RequestMetrics dataclass."""

    def test_default_values(self):
        """Test default values."""
        metrics = RequestMetrics(method="GET", path="/memories")
        assert metrics.method == "GET"
        assert metrics.path == "/memories"
        assert metrics.status_code is None
        assert metrics.duration_ms == 0.0
        assert metrics.retry_count == 0
        assert metrics.labels == {}

    def test_success_property(self):
        """Test success property."""
        metrics = RequestMetrics(method="GET", path="/test")
        assert not metrics.success

        metrics.status_code = 200
        assert metrics.success

        metrics.status_code = 201
        assert metrics.success

        metrics.status_code = 400
        assert not metrics.success

        metrics.status_code = 500
        assert not metrics.success


class TestNoOpCollector:
    """Tests for NoOpCollector."""

    def test_does_nothing(self):
        """Test that NoOpCollector does nothing."""
        collector = NoOpCollector()
        metrics = RequestMetrics(method="GET", path="/test")
        # Should not raise
        collector.on_request_complete(metrics)


class TestInMemoryCollector:
    """Tests for InMemoryCollector."""

    def test_records_metrics(self):
        """Test recording metrics."""
        collector = InMemoryCollector()
        metrics = RequestMetrics(method="GET", path="/memories", status_code=200)
        collector.on_request_complete(metrics)

        assert collector.request_count == 1
        assert collector.metrics[0] == metrics

    def test_success_and_error_counts(self):
        """Test success and error counts."""
        collector = InMemoryCollector()

        # Success
        collector.on_request_complete(RequestMetrics(method="GET", path="/test", status_code=200))
        collector.on_request_complete(RequestMetrics(method="POST", path="/test", status_code=201))

        # Errors
        collector.on_request_complete(RequestMetrics(method="GET", path="/test", status_code=404))
        collector.on_request_complete(
            RequestMetrics(method="GET", path="/test", error="NetworkError")
        )

        assert collector.success_count == 2
        assert collector.error_count == 2
        assert collector.request_count == 4

    def test_average_latency(self):
        """Test average latency calculation."""
        collector = InMemoryCollector()

        collector.on_request_complete(RequestMetrics(method="GET", path="/test", duration_ms=10))
        collector.on_request_complete(RequestMetrics(method="GET", path="/test", duration_ms=20))
        collector.on_request_complete(RequestMetrics(method="GET", path="/test", duration_ms=30))

        assert collector.average_latency_ms == 20.0

    def test_percentile_latency(self):
        """Test percentile latency calculations."""
        collector = InMemoryCollector()

        # Add 100 metrics with latencies 1-100
        for i in range(1, 101):
            collector.on_request_complete(
                RequestMetrics(method="GET", path="/test", duration_ms=float(i))
            )

        assert collector.p50_latency_ms == 50.0
        assert collector.p95_latency_ms == 95.0
        assert collector.p99_latency_ms == 99.0

    def test_filter_by_method(self):
        """Test filtering by method."""
        collector = InMemoryCollector()

        collector.on_request_complete(RequestMetrics(method="GET", path="/test"))
        collector.on_request_complete(RequestMetrics(method="POST", path="/test"))
        collector.on_request_complete(RequestMetrics(method="GET", path="/test"))

        get_metrics = collector.get_metrics_by_method("GET")
        assert len(get_metrics) == 2

    def test_filter_by_path(self):
        """Test filtering by path."""
        collector = InMemoryCollector()

        collector.on_request_complete(RequestMetrics(method="GET", path="/memories"))
        collector.on_request_complete(RequestMetrics(method="GET", path="/spaces"))
        collector.on_request_complete(RequestMetrics(method="GET", path="/memories/123"))

        memories_metrics = collector.get_metrics_by_path("/memories")
        assert len(memories_metrics) == 2

    def test_clear(self):
        """Test clearing metrics."""
        collector = InMemoryCollector()

        collector.on_request_complete(RequestMetrics(method="GET", path="/test"))
        assert collector.request_count == 1

        collector.clear()
        assert collector.request_count == 0

    def test_max_entries(self):
        """Test max entries limit."""
        collector = InMemoryCollector(max_entries=5)

        for i in range(10):
            collector.on_request_complete(RequestMetrics(method="GET", path=f"/test/{i}"))

        assert collector.request_count == 5
        # Should have the last 5 entries
        assert collector.metrics[0].path == "/test/5"
        assert collector.metrics[-1].path == "/test/9"

    def test_records_retries(self):
        """Test recording retries."""
        collector = InMemoryCollector()

        collector.on_retry("GET", "/test", 1, ValueError("Test"), 100)
        collector.on_retry("GET", "/test", 2, ValueError("Test"), 200)

        assert collector.retry_count == 2


class TestCompositeCollector:
    """Tests for CompositeCollector."""

    def test_delegates_to_all_collectors(self):
        """Test that it delegates to all collectors."""
        collector1 = InMemoryCollector()
        collector2 = InMemoryCollector()
        composite = CompositeCollector([collector1, collector2])

        metrics = RequestMetrics(method="GET", path="/test")
        composite.on_request_complete(metrics)

        assert collector1.request_count == 1
        assert collector2.request_count == 1

    def test_add_and_remove(self):
        """Test adding and removing collectors."""
        collector1 = InMemoryCollector()
        collector2 = InMemoryCollector()
        composite = CompositeCollector([collector1])

        composite.add(collector2)

        metrics = RequestMetrics(method="GET", path="/test")
        composite.on_request_complete(metrics)

        assert collector1.request_count == 1
        assert collector2.request_count == 1

        composite.remove(collector2)
        composite.on_request_complete(metrics)

        assert collector1.request_count == 2
        assert collector2.request_count == 1  # No new metrics


class TestCallbackCollector:
    """Tests for CallbackCollector."""

    def test_calls_on_complete_callback(self):
        """Test on_complete callback."""
        results = []

        def on_complete(m: RequestMetrics) -> None:
            results.append(m)

        collector = CallbackCollector(on_complete=on_complete)
        metrics = RequestMetrics(method="GET", path="/test")
        collector.on_request_complete(metrics)

        assert len(results) == 1
        assert results[0] == metrics

    def test_calls_on_retry_callback(self):
        """Test on_retry callback."""
        results = []

        def on_retry(method: str, path: str, attempt: int, error: Exception, delay: float) -> None:
            results.append((method, path, attempt))

        collector = CallbackCollector(on_retry=on_retry)
        collector.on_retry("GET", "/test", 1, ValueError("Test"), 100)

        assert len(results) == 1
        assert results[0] == ("GET", "/test", 1)


class TestGlobalCollector:
    """Tests for global collector functions."""

    def test_default_is_noop(self):
        """Test default collector is NoOpCollector."""
        # Reset to default first
        set_metrics_collector(NoOpCollector())
        collector = get_metrics_collector()
        assert isinstance(collector, NoOpCollector)

    def test_set_and_get(self):
        """Test setting and getting global collector."""
        in_memory = InMemoryCollector()
        set_metrics_collector(in_memory)

        assert get_metrics_collector() is in_memory

        # Reset to NoOp
        set_metrics_collector(NoOpCollector())


class TestTimedRequest:
    """Tests for timed_request context manager."""

    def test_measures_duration(self):
        """Test that duration is measured."""
        collector = InMemoryCollector()

        with timed_request("GET", "/test", collector=collector) as metrics:
            time.sleep(0.01)  # 10ms
            metrics.status_code = 200

        assert collector.request_count == 1
        recorded = collector.metrics[0]
        assert recorded.duration_ms >= 10
        assert recorded.status_code == 200

    def test_records_error_on_exception(self):
        """Test that errors are recorded on exception."""
        collector = InMemoryCollector()

        with pytest.raises(ValueError):
            with timed_request("GET", "/test", collector=collector):
                raise ValueError("Test error")

        assert collector.request_count == 1
        recorded = collector.metrics[0]
        assert recorded.error == "ValueError"

    def test_uses_global_collector(self):
        """Test that global collector is used by default."""
        in_memory = InMemoryCollector()
        set_metrics_collector(in_memory)

        with timed_request("GET", "/test") as metrics:
            metrics.status_code = 200

        assert in_memory.request_count == 1

        # Reset
        set_metrics_collector(NoOpCollector())


class TestRecordRetry:
    """Tests for record_retry function."""

    def test_records_with_specified_collector(self):
        """Test recording with specified collector."""
        collector = InMemoryCollector()
        record_retry("GET", "/test", 1, ValueError("Test"), 100, collector=collector)

        assert collector.retry_count == 1

    def test_uses_global_collector(self):
        """Test that global collector is used by default."""
        in_memory = InMemoryCollector()
        set_metrics_collector(in_memory)

        record_retry("GET", "/test", 1, ValueError("Test"), 100)

        assert in_memory.retry_count == 1

        # Reset
        set_metrics_collector(NoOpCollector())
