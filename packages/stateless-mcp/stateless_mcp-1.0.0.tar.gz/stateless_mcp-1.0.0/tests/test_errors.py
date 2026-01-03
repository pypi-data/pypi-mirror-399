"""Unit tests for error handling."""

import pytest
from stateless_mcp.errors import (
    create_error_response,
    parse_error,
    invalid_request,
    method_not_found,
    invalid_params,
    internal_error,
    server_error,
    PARSE_ERROR,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    INVALID_PARAMS,
    INTERNAL_ERROR,
    SERVER_ERROR,
)


class TestErrorResponses:
    """Test error response creation."""

    def test_parse_error(self):
        """Test parse error response."""
        error_response = parse_error(request_id="123", data="Invalid JSON")

        assert error_response.jsonrpc == "2.0"
        assert error_response.error.code == PARSE_ERROR
        assert error_response.error.message == "Parse error"
        assert error_response.error.data == "Invalid JSON"
        assert error_response.id == "123"

    def test_invalid_request(self):
        """Test invalid request error response."""
        error_response = invalid_request(request_id="123")

        assert error_response.error.code == INVALID_REQUEST
        assert error_response.error.message == "Invalid Request"
        assert error_response.id == "123"

    def test_method_not_found(self):
        """Test method not found error response."""
        error_response = method_not_found(request_id="123", method="unknown_tool")

        assert error_response.error.code == METHOD_NOT_FOUND
        assert error_response.error.message == "Method not found"
        assert error_response.error.data == {"method": "unknown_tool"}
        assert error_response.id == "123"

    def test_invalid_params(self):
        """Test invalid params error response."""
        error_response = invalid_params(request_id="123", data="Missing required param")

        assert error_response.error.code == INVALID_PARAMS
        assert error_response.error.message == "Invalid params"
        assert error_response.error.data == "Missing required param"

    def test_internal_error(self):
        """Test internal error response."""
        error_response = internal_error(request_id="123")

        assert error_response.error.code == INTERNAL_ERROR
        assert error_response.error.message == "Internal error"

    def test_server_error(self):
        """Test server error response."""
        error_response = server_error(
            request_id="123",
            message="Tool execution failed",
            data={"error": "Something went wrong"}
        )

        assert error_response.error.code == SERVER_ERROR
        assert error_response.error.message == "Tool execution failed"
        assert error_response.error.data == {"error": "Something went wrong"}

    def test_error_with_null_id(self):
        """Test error response with null request ID."""
        error_response = parse_error(request_id=None)

        assert error_response.id is None

    def test_create_custom_error(self):
        """Test creating a custom error response."""
        error_response = create_error_response(
            code=-32001,
            message="Custom error",
            data={"custom": "data"},
            request_id="123"
        )

        assert error_response.error.code == -32001
        assert error_response.error.message == "Custom error"
        assert error_response.error.data == {"custom": "data"}
        assert error_response.id == "123"

    def test_default_error_messages(self):
        """Test that default messages are used when not provided."""
        error_response = create_error_response(
            code=PARSE_ERROR,
            request_id="123"
        )

        assert error_response.error.message == "Parse error"
