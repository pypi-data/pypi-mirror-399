"""Integration tests for the complete MCP server."""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from stateless_mcp import app, tool, get_registry


# Define test tools (don't use test_ prefix to avoid pytest collection)
@tool(name="test_echo", streaming=False, timeout=30)
async def echo_tool(params: dict) -> dict:
    """Test echo tool."""
    return {"echo": params}


@tool(name="test_add", streaming=False, timeout=30)
async def add_tool(params: dict) -> dict:
    """Test add tool."""
    a = params.get("a", 0)
    b = params.get("b", 0)
    return {"result": a + b}


@tool(name="test_stream", streaming=True, timeout=30)
async def stream_tool(params: dict):
    """Test streaming tool."""
    count = params.get("count", 3)
    for i in range(count):
        await asyncio.sleep(0.01)
        yield {"type": "progress", "value": i}
    yield {"type": "result", "value": count}


@tool(name="test_error", streaming=False, timeout=30)
async def error_tool(params: dict) -> dict:
    """Test tool that raises an error."""
    raise ValueError("Test error")


@tool(name="test_slow", streaming=False, timeout=1)
async def slow_tool(params: dict) -> dict:
    """Test tool that times out."""
    await asyncio.sleep(5)
    return {"result": "done"}


class TestMCPEndpoint:
    """Integration tests for /mcp endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "tools" in data

    def test_tools_endpoint(self, client):
        """Test tools listing endpoint."""
        response = client.get("/tools")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert isinstance(data["tools"], dict)

    def test_non_streaming_tool(self, client):
        """Test calling a non-streaming tool."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "test_add",
                "params": {"a": 5, "b": 3},
                "id": "test-1"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["result"] == {"result": 8}
        assert data["id"] == "test-1"

    def test_echo_tool(self, client):
        """Test echo tool."""
        params = {"key1": "value1", "key2": 42}
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "test_echo",
                "params": params,
                "id": "test-2"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["result"] == {"echo": params}

    def test_streaming_tool(self, client):
        """Test calling a streaming tool."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "test_stream",
                "params": {"count": 3},
                "id": "test-3"
            }
        )

        assert response.status_code == 200

        # Parse NDJSON response
        lines = response.text.strip().split('\n')
        assert len(lines) > 3  # At least 3 progress chunks + 1 result + 1 final

        # Check that we got progress chunks
        import json
        chunks = [json.loads(line) for line in lines]

        # Check progress chunks
        progress_chunks = [c for c in chunks if c.get("type") == "progress"]
        assert len(progress_chunks) == 3

        # Check final JSON-RPC response is present
        final_response = chunks[-1]
        assert "jsonrpc" in final_response
        assert final_response["jsonrpc"] == "2.0"
        assert final_response["id"] == "test-3"

    def test_method_not_found(self, client):
        """Test calling a non-existent method."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "nonexistent_method",
                "params": {},
                "id": "test-4"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32601  # Method not found

    def test_invalid_json(self, client):
        """Test sending invalid JSON."""
        response = client.post(
            "/mcp",
            content=b"not valid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32700  # Parse error

    def test_invalid_jsonrpc_request(self, client):
        """Test sending invalid JSON-RPC request."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                # Missing method field
                "params": {},
                "id": "test-5"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32600  # Invalid request

    def test_tool_execution_error(self, client):
        """Test tool that raises an error."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "test_error",
                "params": {},
                "id": "test-6"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32000  # Server error
        assert "Test error" in data["error"]["message"]

    def test_request_without_params(self, client):
        """Test request without params field."""
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "test_echo",
                "id": "test-7"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        # Echo should return empty or None params

    def test_concurrent_requests(self, client):
        """Test multiple concurrent requests."""
        import concurrent.futures

        def make_request(i):
            return client.post(
                "/mcp",
                json={
                    "jsonrpc": "2.0",
                    "method": "test_add",
                    "params": {"a": i, "b": i},
                    "id": f"concurrent-{i}"
                }
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(10)]
            responses = [f.result() for f in futures]

        # All should succeed
        for i, response in enumerate(responses):
            assert response.status_code == 200
            data = response.json()
            assert data["result"]["result"] == i + i


@pytest.mark.asyncio
class TestAsyncIntegration:
    """Async integration tests."""

    async def test_streaming_with_async_client(self):
        """Test streaming with async client."""
        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            async with client.stream(
                "POST",
                "/mcp",
                json={
                    "jsonrpc": "2.0",
                    "method": "test_stream",
                    "params": {"count": 3},
                    "id": "async-stream-1"
                }
            ) as response:
                chunks = []
                async for line in response.aiter_lines():
                    if line:
                        import json
                        chunks.append(json.loads(line))

                # Should have progress chunks and final response
                assert len(chunks) > 3

                # Final chunk should be JSON-RPC response
                final = chunks[-1]
                assert final["jsonrpc"] == "2.0"
                assert final["id"] == "async-stream-1"
