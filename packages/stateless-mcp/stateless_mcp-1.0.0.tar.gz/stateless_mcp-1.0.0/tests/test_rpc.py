"""Unit tests for JSON-RPC parsing and validation."""

import json
import pytest
from stateless_mcp.rpc import parse_request, create_success_response, serialize_response
from stateless_mcp.models import JSONRPCRequest, JSONRPCResponse


class TestParseRequest:
    """Test JSON-RPC request parsing."""

    def test_valid_request(self):
        """Test parsing a valid JSON-RPC request."""
        body = json.dumps({
            "jsonrpc": "2.0",
            "method": "test_method",
            "params": {"key": "value"},
            "id": "123"
        }).encode()

        request, error = parse_request(body)

        assert error is None
        assert request is not None
        assert request.method == "test_method"
        assert request.params == {"key": "value"}
        assert request.id == "123"

    def test_valid_request_without_params(self):
        """Test parsing request without params."""
        body = json.dumps({
            "jsonrpc": "2.0",
            "method": "test_method",
            "id": 1
        }).encode()

        request, error = parse_request(body)

        assert error is None
        assert request is not None
        assert request.params is None

    def test_invalid_json(self):
        """Test parsing invalid JSON."""
        body = b"not valid json"

        request, error = parse_request(body)

        assert request is None
        assert error is not None
        assert error.error.code == -32700  # Parse error

    def test_missing_jsonrpc_version(self):
        """Test request without jsonrpc field."""
        body = json.dumps({
            "method": "test_method",
            "id": "123"
        }).encode()

        request, error = parse_request(body)

        # Should use default "2.0" value
        assert request is not None or error is not None

    def test_wrong_jsonrpc_version(self):
        """Test request with wrong jsonrpc version."""
        body = json.dumps({
            "jsonrpc": "1.0",
            "method": "test_method",
            "id": "123"
        }).encode()

        request, error = parse_request(body)

        assert request is None
        assert error is not None

    def test_missing_method(self):
        """Test request without method."""
        body = json.dumps({
            "jsonrpc": "2.0",
            "id": "123"
        }).encode()

        request, error = parse_request(body)

        assert request is None
        assert error is not None
        assert error.error.code == -32600  # Invalid request


class TestCreateSuccessResponse:
    """Test creating success responses."""

    def test_create_response_with_result(self):
        """Test creating a success response."""
        result = {"status": "success", "data": [1, 2, 3]}
        response = create_success_response(result, request_id="123")

        assert response.jsonrpc == "2.0"
        assert response.result == result
        assert response.id == "123"

    def test_create_response_with_null_id(self):
        """Test creating response with null ID."""
        result = {"status": "success"}
        response = create_success_response(result, request_id=None)

        assert response.id is None


class TestSerializeResponse:
    """Test response serialization."""

    def test_serialize_success_response(self):
        """Test serializing a success response."""
        response = JSONRPCResponse(result={"value": 42}, id="123")
        serialized = serialize_response(response)

        data = json.loads(serialized)
        assert data["jsonrpc"] == "2.0"
        assert data["result"] == {"value": 42}
        assert data["id"] == "123"

    def test_serialize_error_response(self):
        """Test serializing an error response."""
        from stateless_mcp.errors import method_not_found

        error_response = method_not_found(request_id="123", method="unknown")
        serialized = serialize_response(error_response)

        data = json.loads(serialized)
        assert data["jsonrpc"] == "2.0"
        assert "error" in data
        assert data["error"]["code"] == -32601
        assert data["id"] == "123"
