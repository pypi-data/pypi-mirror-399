"""JSON-RPC 2.0 parsing and validation."""

import json
from typing import Tuple, Union
from pydantic import ValidationError

from .models import JSONRPCRequest, JSONRPCResponse, JSONRPCErrorResponse
from .errors import parse_error, invalid_request


def parse_request(raw_body: bytes) -> Tuple[Union[JSONRPCRequest, None], Union[JSONRPCErrorResponse, None]]:
    """
    Parse and validate a JSON-RPC request.

    Args:
        raw_body: Raw request body bytes

    Returns:
        Tuple of (request, error_response)
        - If successful: (JSONRPCRequest, None)
        - If failed: (None, JSONRPCErrorResponse)
    """
    # Try to parse JSON
    try:
        data = json.loads(raw_body)
    except json.JSONDecodeError as e:
        return None, parse_error(data=str(e))

    # Try to validate JSON-RPC structure
    try:
        request = JSONRPCRequest(**data)
        return request, None
    except ValidationError as e:
        # Extract request ID if possible
        request_id = data.get("id") if isinstance(data, dict) else None
        return None, invalid_request(request_id=request_id, data=str(e))
    except Exception as e:
        # Catch any other validation errors
        request_id = data.get("id") if isinstance(data, dict) else None
        return None, invalid_request(request_id=request_id, data=str(e))


def create_success_response(result: any, request_id: Union[str, int, None]) -> JSONRPCResponse:
    """
    Create a JSON-RPC success response.

    Args:
        result: The result data to return
        request_id: ID from the original request

    Returns:
        JSONRPCResponse object
    """
    return JSONRPCResponse(result=result, id=request_id)


def serialize_response(response: Union[JSONRPCResponse, JSONRPCErrorResponse]) -> str:
    """
    Serialize a JSON-RPC response to JSON string.

    Args:
        response: JSONRPCResponse or JSONRPCErrorResponse

    Returns:
        JSON string
    """
    return response.model_dump_json(exclude_none=False)
