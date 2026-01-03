"""
MCP (Model Context Protocol) implementation for stateless-mcp.

Implements the standard MCP methods:
- initialize: Protocol handshake
- tools/list: List available tools
- tools/call: Execute a tool
"""

from typing import Dict, Any, Optional
from .registry import get_registry
from .rpc import create_success_response
from .models import JSONRPCRequest, JSONRPCErrorResponse
from .errors import method_not_found, invalid_params


async def handle_mcp_method(rpc_request: JSONRPCRequest) -> Dict[str, Any]:
    """
    Handle MCP protocol methods.

    Args:
        rpc_request: Parsed JSON-RPC request

    Returns:
        JSON-RPC response dict or None if method not recognized
    """
    method = rpc_request.method

    # MCP Initialize
    if method == "initialize":
        return await handle_initialize(rpc_request)

    # MCP Tools List
    elif method == "tools/list":
        return await handle_tools_list(rpc_request)

    # MCP Tools Call
    elif method == "tools/call":
        # Extract tool name and arguments from params
        if not rpc_request.params:
            return invalid_params(
                request_id=rpc_request.id,
                message="tools/call requires 'name' and 'arguments' in params"
            ).model_dump(exclude_none=False)

        # Return None to let dispatcher handle the actual tool call
        # But we need to transform the request first
        return None

    # Not an MCP method
    return None


async def handle_initialize(rpc_request: JSONRPCRequest) -> Dict[str, Any]:
    """
    Handle MCP initialize method.

    Returns server capabilities and protocol version.
    """
    registry = get_registry()

    result = {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {
                "listChanged": False  # Tools are static (registry is locked)
            }
        },
        "serverInfo": {
            "name": "stateless-mcp",
            "version": "1.0.0"
        }
    }

    response = create_success_response(
        result=result,
        request_id=rpc_request.id
    )

    return response.model_dump(exclude_none=False)


async def handle_tools_list(rpc_request: JSONRPCRequest) -> Dict[str, Any]:
    """
    Handle MCP tools/list method.

    Returns list of all available tools with their schemas.
    """
    registry = get_registry()
    tools_list = []

    for name, metadata in registry.list_tools().items():
        # Build tool schema
        tool_schema = {
            "name": metadata.name,
            "description": metadata.fn.__doc__ or f"Tool: {metadata.name}",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }

        # Try to extract parameter info from function signature
        import inspect
        sig = inspect.signature(metadata.fn)

        for param_name, param in sig.parameters.items():
            if param_name == "params":
                # Generic dict parameter - can't introspect schema
                tool_schema["inputSchema"]["properties"]["params"] = {
                    "type": "object",
                    "description": "Tool parameters"
                }
            else:
                # Individual parameter
                param_type = "string"  # Default
                if param.annotation != inspect.Parameter.empty:
                    if param.annotation == int:
                        param_type = "integer"
                    elif param.annotation == float:
                        param_type = "number"
                    elif param.annotation == bool:
                        param_type = "boolean"

                tool_schema["inputSchema"]["properties"][param_name] = {
                    "type": param_type
                }

                if param.default == inspect.Parameter.empty:
                    tool_schema["inputSchema"]["required"].append(param_name)

        tools_list.append(tool_schema)

    result = {
        "tools": tools_list
    }

    response = create_success_response(
        result=result,
        request_id=rpc_request.id
    )

    return response.model_dump(exclude_none=False)


def transform_tools_call_request(rpc_request: JSONRPCRequest) -> JSONRPCRequest:
    """
    Transform MCP tools/call request to stateless-mcp format.

    MCP format:
        {"method": "tools/call", "params": {"name": "tool_name", "arguments": {...}}}

    Stateless-MCP format:
        {"method": "tool_name", "params": {...}}

    Args:
        rpc_request: Original MCP tools/call request

    Returns:
        Transformed request with tool name as method
    """
    if rpc_request.method != "tools/call":
        return rpc_request

    if not rpc_request.params:
        return rpc_request

    # Extract tool name and arguments
    tool_name = rpc_request.params.get("name")
    arguments = rpc_request.params.get("arguments", {})

    if not tool_name:
        return rpc_request

    # Create new request with tool name as method
    transformed = JSONRPCRequest(
        jsonrpc=rpc_request.jsonrpc,
        method=tool_name,
        params=arguments,
        id=rpc_request.id
    )

    return transformed
