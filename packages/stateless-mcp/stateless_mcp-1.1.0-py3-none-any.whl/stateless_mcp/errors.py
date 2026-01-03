"""JSON-RPC 2.0 error codes and helpers."""

from typing import Any, Optional, Union
from .models import JSONRPCError, JSONRPCErrorResponse


class ParameterValidationError(Exception):
    """Raised when parameter validation fails (e.g., Pydantic validation)."""

    pass


class ResponseValidationError(Exception):
    """Raised when response validation fails (e.g., invalid return type)."""

    pass


# Standard JSON-RPC 2.0 error codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
SERVER_ERROR = -32000


ERROR_MESSAGES = {
    PARSE_ERROR: "Parse error",
    INVALID_REQUEST: "Invalid Request",
    METHOD_NOT_FOUND: "Method not found",
    INVALID_PARAMS: "Invalid params",
    INTERNAL_ERROR: "Internal error",
    SERVER_ERROR: "Server error",
}


def create_error_response(
    code: int,
    message: Optional[str] = None,
    data: Optional[Any] = None,
    request_id: Union[str, int, None] = None,
) -> JSONRPCErrorResponse:
    """
    Create a JSON-RPC error response.

    Args:
        code: JSON-RPC error code
        message: Error message (defaults to standard message for code)
        data: Additional error data
        request_id: ID from the original request

    Returns:
        JSONRPCErrorResponse object
    """
    if message is None:
        message = ERROR_MESSAGES.get(code, "Unknown error")

    error = JSONRPCError(code=code, message=message, data=data)
    return JSONRPCErrorResponse(error=error, id=request_id)


def parse_error(request_id: Union[str, int, None] = None, data: Optional[Any] = None) -> JSONRPCErrorResponse:
    """Create a parse error response."""
    return create_error_response(PARSE_ERROR, request_id=request_id, data=data)


def invalid_request(request_id: Union[str, int, None] = None, data: Optional[Any] = None) -> JSONRPCErrorResponse:
    """Create an invalid request error response."""
    return create_error_response(INVALID_REQUEST, request_id=request_id, data=data)


def method_not_found(request_id: Union[str, int, None] = None, method: Optional[str] = None) -> JSONRPCErrorResponse:
    """Create a method not found error response."""
    data = {"method": method} if method else None
    return create_error_response(METHOD_NOT_FOUND, request_id=request_id, data=data)


def invalid_params(request_id: Union[str, int, None] = None, data: Optional[Any] = None) -> JSONRPCErrorResponse:
    """Create an invalid params error response."""
    return create_error_response(INVALID_PARAMS, request_id=request_id, data=data)


def internal_error(request_id: Union[str, int, None] = None, data: Optional[Any] = None) -> JSONRPCErrorResponse:
    """Create an internal error response."""
    return create_error_response(INTERNAL_ERROR, request_id=request_id, data=data)


def server_error(
    request_id: Union[str, int, None] = None,
    message: Optional[str] = None,
    data: Optional[Any] = None,
) -> JSONRPCErrorResponse:
    """Create a server error response."""
    return create_error_response(SERVER_ERROR, message=message, request_id=request_id, data=data)
