"""Prometheus metrics for stateless MCP."""

from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from typing import Optional
import time

# Request counters
request_total = Counter(
    "mcp_requests_total",
    "Total number of MCP requests",
    ["tool", "status"]  # status: success, error
)

# Request duration histogram
request_duration = Histogram(
    "mcp_request_duration_seconds",
    "Request duration in seconds",
    ["tool", "streaming"]
)

# Request/response size histograms
request_size = Histogram(
    "mcp_request_size_bytes",
    "Request size in bytes",
    ["tool"]
)

response_size = Histogram(
    "mcp_response_size_bytes",
    "Response size in bytes",
    ["tool"]
)

# Active requests gauge
active_requests = Gauge(
    "mcp_active_requests",
    "Number of currently active requests",
    ["worker"]
)

# Tool execution errors
tool_errors = Counter(
    "mcp_tool_errors_total",
    "Total number of tool execution errors",
    ["tool", "error_type"]
)

# Streaming metrics
streaming_chunks = Counter(
    "mcp_streaming_chunks_total",
    "Total number of streaming chunks sent",
    ["tool"]
)

# Tool registry info
tools_registered = Gauge(
    "mcp_tools_registered",
    "Number of registered tools"
)

# Server info
server_info = Info(
    "mcp_server",
    "Server information"
)


class MetricsContext:
    """Context manager for tracking request metrics."""

    def __init__(self, tool_name: str, streaming: bool = False):
        self.tool_name = tool_name
        self.streaming = streaming
        self.start_time = None
        self.success = False

    def __enter__(self):
        self.start_time = time.time()
        active_requests.labels(worker="default").inc()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Record duration
        duration = time.time() - self.start_time
        request_duration.labels(
            tool=self.tool_name,
            streaming=str(self.streaming).lower()
        ).observe(duration)

        # Record status
        status = "success" if exc_type is None and self.success else "error"
        request_total.labels(tool=self.tool_name, status=status).inc()

        # Record error type if failed
        if exc_type is not None:
            error_type = exc_type.__name__
            tool_errors.labels(tool=self.tool_name, error_type=error_type).inc()

        # Decrement active requests
        active_requests.labels(worker="default").dec()

    def mark_success(self):
        """Mark the request as successful."""
        self.success = True

    def add_streaming_chunk(self):
        """Increment streaming chunk counter."""
        streaming_chunks.labels(tool=self.tool_name).inc()


def export_metrics() -> bytes:
    """Export Prometheus metrics."""
    return generate_latest()


def get_metrics_content_type() -> str:
    """Get Prometheus metrics content type."""
    return CONTENT_TYPE_LATEST


def set_server_info(version: str, workers: int):
    """Set server information metrics."""
    server_info.info({
        "version": version,
        "workers": str(workers)
    })


def reset_metrics():
    """
    Reset all metrics to initial state.

    Note: Prometheus metrics cannot be truly reset, this is mainly for testing.
    In production, metrics accumulate over the process lifetime.
    """
    # This is a no-op for Prometheus metrics
    # Metrics are designed to accumulate
    # Individual tests should use isolated registries if needed
    pass
