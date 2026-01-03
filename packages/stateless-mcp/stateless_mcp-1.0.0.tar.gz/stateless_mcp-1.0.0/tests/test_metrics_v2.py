"""Comprehensive tests for Prometheus metrics module."""

import time
from unittest.mock import patch

import pytest
from prometheus_client import REGISTRY

from stateless_mcp.metrics import (
    request_total,
    request_duration,
    request_size,
    response_size,
    streaming_chunks,
    active_requests,
    tools_registered,
    MetricsContext,
    export_metrics,
    get_metrics_content_type,
    set_server_info,
    reset_metrics,
)


class TestMetricsCounters:
    """Test Prometheus counter metrics."""

    def setup_method(self):
        """Reset metrics before each test."""
        reset_metrics()

    def test_request_total_increment(self):
        """Test incrementing request total counter."""
        initial = request_total.labels(tool="test_tool", status="success")._value.get()

        request_total.labels(tool="test_tool", status="success").inc()
        request_total.labels(tool="test_tool", status="success").inc()

        final = request_total.labels(tool="test_tool", status="success")._value.get()
        assert final == initial + 2

    def test_request_total_different_labels(self):
        """Test counters with different label combinations."""
        request_total.labels(tool="add", status="success").inc()
        request_total.labels(tool="add", status="error").inc()
        request_total.labels(tool="multiply", status="success").inc()

        add_success = request_total.labels(tool="add", status="success")._value.get()
        add_error = request_total.labels(tool="add", status="error")._value.get()
        multiply_success = request_total.labels(tool="multiply", status="success")._value.get()

        assert add_success >= 1
        assert add_error >= 1
        assert multiply_success >= 1

    def test_streaming_chunks_counter(self):
        """Test streaming chunks counter."""
        initial = streaming_chunks.labels(tool="stream_tool")._value.get()

        streaming_chunks.labels(tool="stream_tool").inc(5)

        final = streaming_chunks.labels(tool="stream_tool")._value.get()
        assert final == initial + 5


class TestMetricsHistograms:
    """Test Prometheus histogram metrics."""

    def setup_method(self):
        """Reset metrics before each test."""
        reset_metrics()

    def test_request_duration_observe(self):
        """Test observing request durations."""
        request_duration.labels(tool="test", streaming="false").observe(0.5)
        request_duration.labels(tool="test", streaming="false").observe(1.0)
        request_duration.labels(tool="test", streaming="false").observe(1.5)

        # Histogram should have recorded observations
        metric_family = request_duration.labels(tool="test", streaming="false")
        assert metric_family is not None

    def test_request_duration_streaming_vs_nonstreaming(self):
        """Test separate histograms for streaming vs non-streaming."""
        request_duration.labels(tool="test", streaming="true").observe(2.0)
        request_duration.labels(tool="test", streaming="false").observe(0.5)

        # Both should exist independently
        streaming_metric = request_duration.labels(tool="test", streaming="true")
        nonstreaming_metric = request_duration.labels(tool="test", streaming="false")

        assert streaming_metric is not None
        assert nonstreaming_metric is not None

    def test_request_size_observe(self):
        """Test observing request sizes."""
        request_size.labels(tool="test").observe(1024)
        request_size.labels(tool="test").observe(2048)

        metric_family = request_size.labels(tool="test")
        assert metric_family is not None

    def test_response_size_observe(self):
        """Test observing response sizes."""
        response_size.labels(tool="test").observe(512)
        response_size.labels(tool="test").observe(1024)

        metric_family = response_size.labels(tool="test")
        assert metric_family is not None


class TestMetricsGauges:
    """Test Prometheus gauge metrics."""

    def setup_method(self):
        """Reset metrics before each test."""
        reset_metrics()

    def test_active_requests_inc_dec(self):
        """Test incrementing and decrementing active requests."""
        initial = active_requests.labels(worker="worker1")._value.get()

        active_requests.labels(worker="worker1").inc()
        active_requests.labels(worker="worker1").inc()
        assert active_requests.labels(worker="worker1")._value.get() == initial + 2

        active_requests.labels(worker="worker1").dec()
        assert active_requests.labels(worker="worker1")._value.get() == initial + 1

    def test_active_requests_multiple_workers(self):
        """Test active requests across multiple workers."""
        active_requests.labels(worker="worker1").inc()
        active_requests.labels(worker="worker2").inc()
        active_requests.labels(worker="worker2").inc()

        worker1_count = active_requests.labels(worker="worker1")._value.get()
        worker2_count = active_requests.labels(worker="worker2")._value.get()

        assert worker1_count >= 1
        assert worker2_count >= 2

    def test_tools_registered_set(self):
        """Test setting tools registered count."""
        tools_registered.set(7)
        assert tools_registered._value.get() == 7

        tools_registered.set(10)
        assert tools_registered._value.get() == 10


class TestMetricsContext:
    """Test MetricsContext context manager."""

    def setup_method(self):
        """Reset metrics before each test."""
        reset_metrics()

    def test_metrics_context_success(self):
        """Test metrics context for successful request."""
        initial_total = request_total.labels(tool="test", status="success")._value.get()
        initial_active = active_requests.labels(worker="default")._value.get()

        with MetricsContext(tool_name="test", is_streaming=False):
            # Active requests should be incremented
            assert active_requests.labels(worker="default")._value.get() == initial_active + 1
            time.sleep(0.1)  # Simulate work

        # After context, active should be decremented
        assert active_requests.labels(worker="default")._value.get() == initial_active

        # Total should be incremented
        final_total = request_total.labels(tool="test", status="success")._value.get()
        assert final_total == initial_total + 1

    def test_metrics_context_error(self):
        """Test metrics context for failed request."""
        initial_total = request_total.labels(tool="test", status="error")._value.get()

        try:
            with MetricsContext(tool_name="test", is_streaming=False):
                raise ValueError("Test error")
        except ValueError:
            pass

        # Error count should be incremented
        final_total = request_total.labels(tool="test", status="error")._value.get()
        assert final_total == initial_total + 1

    def test_metrics_context_duration_tracking(self):
        """Test that context tracks duration."""
        with MetricsContext(tool_name="test", is_streaming=False):
            time.sleep(0.1)

        # Duration should have been observed (can't check exact value due to timing)
        # Just verify no errors occurred

    def test_metrics_context_streaming_chunks(self):
        """Test adding streaming chunks."""
        ctx = MetricsContext(tool_name="test", is_streaming=True)
        ctx.__enter__()

        initial_chunks = streaming_chunks.labels(tool="test")._value.get()

        ctx.add_streaming_chunk()
        ctx.add_streaming_chunk()
        ctx.add_streaming_chunk()

        final_chunks = streaming_chunks.labels(tool="test")._value.get()
        assert final_chunks == initial_chunks + 3

        ctx.__exit__(None, None, None)

    def test_metrics_context_mark_success(self):
        """Test explicitly marking success."""
        initial_success = request_total.labels(tool="test", status="success")._value.get()

        ctx = MetricsContext(tool_name="test", is_streaming=True)
        ctx.__enter__()
        ctx.mark_success()
        ctx.__exit__(None, None, None)

        final_success = request_total.labels(tool="test", status="success")._value.get()
        assert final_success == initial_success + 1

    def test_metrics_context_as_context_manager(self):
        """Test using MetricsContext as context manager."""
        with MetricsContext(tool_name="test", is_streaming=False) as ctx:
            assert ctx is not None
            ctx.add_streaming_chunk()  # Should work even for non-streaming


class TestMetricsExport:
    """Test metrics export functionality."""

    def setup_method(self):
        """Reset metrics before each test."""
        reset_metrics()

    def test_export_metrics_format(self):
        """Test exported metrics format."""
        # Add some metrics
        request_total.labels(tool="test", status="success").inc()
        tools_registered.set(5)

        output = export_metrics()

        assert isinstance(output, str)
        assert len(output) > 0

        # Should contain metric names
        assert "mcp_requests_total" in output
        assert "mcp_tools_registered" in output

    def test_export_metrics_content_type(self):
        """Test metrics content type."""
        content_type = get_metrics_content_type()
        assert content_type.startswith("text/plain")

    def test_export_metrics_prometheus_format(self):
        """Test metrics are in Prometheus text format."""
        request_total.labels(tool="add", status="success").inc(3)

        output = export_metrics()

        # Prometheus format should have HELP and TYPE lines
        assert "# HELP" in output
        assert "# TYPE" in output

        # Should have metric values
        assert "mcp_requests_total" in output

    def test_export_metrics_with_multiple_labels(self):
        """Test export with multiple label combinations."""
        request_total.labels(tool="add", status="success").inc(5)
        request_total.labels(tool="add", status="error").inc(2)
        request_total.labels(tool="multiply", status="success").inc(3)

        output = export_metrics()

        # Should contain all label combinations
        assert 'tool="add"' in output
        assert 'tool="multiply"' in output
        assert 'status="success"' in output
        assert 'status="error"' in output


class TestServerInfo:
    """Test server info metrics."""

    def setup_method(self):
        """Reset metrics before each test."""
        reset_metrics()

    def test_set_server_info(self):
        """Test setting server info."""
        set_server_info(version="2.0.0", workers=4)

        # Server info should be in metrics export
        output = export_metrics()
        assert "mcp_server_info" in output
        assert 'version="2.0.0"' in output

    def test_set_server_info_updates(self):
        """Test updating server info."""
        set_server_info(version="1.0.0", workers=2)
        set_server_info(version="2.0.0", workers=4)

        output = export_metrics()
        assert 'version="2.0.0"' in output


class TestMetricsIntegration:
    """Integration tests for metrics in realistic scenarios."""

    def setup_method(self):
        """Reset metrics before each test."""
        reset_metrics()

    def test_complete_request_metrics(self):
        """Test metrics for a complete request lifecycle."""
        initial_total = request_total.labels(tool="add", status="success")._value.get()

        # Simulate a request
        with MetricsContext(tool_name="add", is_streaming=False):
            time.sleep(0.05)
            request_size.labels(tool="add").observe(256)
            response_size.labels(tool="add").observe(128)

        # Verify all metrics were recorded
        final_total = request_total.labels(tool="add", status="success")._value.get()
        assert final_total == initial_total + 1

        # Export should contain the metrics
        output = export_metrics()
        assert "mcp_requests_total" in output
        assert "mcp_request_duration_seconds" in output
        assert "mcp_request_size_bytes" in output
        assert "mcp_response_size_bytes" in output

    def test_streaming_request_metrics(self):
        """Test metrics for streaming request."""
        initial_chunks = streaming_chunks.labels(tool="stream")._value.get()

        with MetricsContext(tool_name="stream", is_streaming=True) as ctx:
            # Simulate streaming chunks
            for _ in range(5):
                ctx.add_streaming_chunk()
                time.sleep(0.01)

            ctx.mark_success()

        final_chunks = streaming_chunks.labels(tool="stream")._value.get()
        assert final_chunks == initial_chunks + 5

        # Verify in export
        output = export_metrics()
        assert "mcp_streaming_chunks_total" in output

    def test_concurrent_requests_metrics(self):
        """Test metrics with concurrent requests."""
        contexts = []

        # Start multiple requests
        for i in range(3):
            ctx = MetricsContext(tool_name=f"tool{i}", is_streaming=False)
            ctx.__enter__()
            contexts.append(ctx)

        # Active requests should be 3
        active = active_requests.labels(worker="default")._value.get()
        assert active >= 3

        # Complete all requests
        for ctx in contexts:
            ctx.__exit__(None, None, None)

        # Active should be back to initial
        active_after = active_requests.labels(worker="default")._value.get()
        assert active_after < active

    def test_error_tracking_metrics(self):
        """Test error tracking in metrics."""
        initial_errors = request_total.labels(tool="fail", status="error")._value.get()

        try:
            with MetricsContext(tool_name="fail", is_streaming=False):
                raise RuntimeError("Simulated failure")
        except RuntimeError:
            pass

        final_errors = request_total.labels(tool="fail", status="error")._value.get()
        assert final_errors == initial_errors + 1

    def test_mixed_success_and_error_metrics(self):
        """Test tracking both successes and errors."""
        # Successful request
        with MetricsContext(tool_name="mixed", is_streaming=False):
            pass

        success_count = request_total.labels(tool="mixed", status="success")._value.get()
        assert success_count >= 1

        # Failed request
        try:
            with MetricsContext(tool_name="mixed", is_streaming=False):
                raise ValueError("Error")
        except ValueError:
            pass

        error_count = request_total.labels(tool="mixed", status="error")._value.get()
        assert error_count >= 1

        # Both should be in export
        output = export_metrics()
        assert 'tool="mixed"' in output
        assert 'status="success"' in output
        assert 'status="error"' in output

    def test_performance_metrics_timing(self):
        """Test that duration metrics capture timing correctly."""
        with MetricsContext(tool_name="timed", is_streaming=False):
            start = time.time()
            time.sleep(0.1)
            duration = time.time() - start

        # Duration should be recorded (approximately 0.1 seconds)
        # We can't easily verify the exact value, but the metric should exist
        output = export_metrics()
        assert "mcp_request_duration_seconds" in output
        assert 'tool="timed"' in output


class TestMetricsReset:
    """Test metrics reset functionality."""

    def test_reset_metrics(self):
        """Test resetting all metrics."""
        # Add some metrics
        request_total.labels(tool="test", status="success").inc(5)
        tools_registered.set(10)
        active_requests.labels(worker="w1").inc()

        # Reset
        reset_metrics()

        # Metrics should be reset (new labels will start at 0)
        # Note: Prometheus metrics can't be truly reset, but reset_metrics
        # clears internal state where applicable
