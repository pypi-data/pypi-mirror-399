# Stateless MCP Dockerfile
# Multi-stage build for production deployment

# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY stateless_mcp/ ./stateless_mcp/
COPY setup.py pyproject.toml README.md ./

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Install the package in editable mode
RUN pip install --no-cache-dir -e .

# Expose port
EXPOSE 8000

# Environment variables with defaults
ENV SMCP_HOST=0.0.0.0
ENV SMCP_PORT=8000
ENV SMCP_WORKERS=4
ENV SMCP_DEBUG=false

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Single entrypoint - NO reload, NO uv run
# Deterministic startup with multiple workers
CMD ["sh", "-c", "uvicorn stateless_mcp.app:app --host $SMCP_HOST --port $SMCP_PORT --workers $SMCP_WORKERS"]
