"""Core execution logic for dispatching tool calls."""

import asyncio
import inspect
from typing import Union, AsyncGenerator

from .models import JSONRPCRequest, JSONRPCResponse, JSONRPCErrorResponse
from .registry import get_registry, ParameterPattern, ResponsePattern
from .rpc import create_success_response
from .errors import (
    method_not_found,
    server_error,
    invalid_params,
    ParameterValidationError,
    ResponseValidationError,
)
from .streaming import stream_generator, collect_stream_result


def _validate_response(result, tool_metadata):
    """
    Validate tool response according to its response pattern.

    Args:
        result: The result returned by the tool
        tool_metadata: Tool metadata containing response pattern info

    Returns:
        The validated result (may be converted to dict for Pydantic models)

    Raises:
        ResponseValidationError: If response doesn't match expected pattern
    """
    if tool_metadata.response_pattern == ResponsePattern.ANY:
        # No validation needed
        return result

    elif tool_metadata.response_pattern == ResponsePattern.DICT:
        # Validate that result is a dict
        if not isinstance(result, dict):
            raise ResponseValidationError(
                f"Expected dict response, got {type(result).__name__}. "
                f"Tool '{tool_metadata.name}' has return type annotation 'dict'."
            )
        return result

    elif tool_metadata.response_pattern == ResponsePattern.PYDANTIC:
        # Result can be either:
        # 1. A Pydantic model instance (we convert to dict)
        # 2. A dict that we validate against the model
        model_class = tool_metadata.response_model

        if isinstance(result, model_class):
            # It's already a Pydantic model instance, convert to dict
            return result.model_dump()

        elif isinstance(result, dict):
            # It's a dict, validate it against the model
            try:
                validated = model_class(**result)
                return validated.model_dump()
            except Exception as e:
                raise ResponseValidationError(
                    f"Response validation failed for model {model_class.__name__}: {str(e)}"
                ) from e

        else:
            raise ResponseValidationError(
                f"Expected {model_class.__name__} or dict response, got {type(result).__name__}. "
                f"Tool '{tool_metadata.name}' has return type annotation '{model_class.__name__}'."
            )

    return result


async def dispatch_tool(request: JSONRPCRequest) -> Union[JSONRPCResponse, JSONRPCErrorResponse, AsyncGenerator]:
    """
    Dispatch a tool call based on JSON-RPC request.

    This is the core dispatcher that:
    1. Looks up the tool in the registry
    2. Executes it (with timeout)
    3. Returns result or error

    Args:
        request: Validated JSON-RPC request

    Returns:
        - JSONRPCResponse: For successful non-streaming tools
        - JSONRPCErrorResponse: For errors
        - AsyncGenerator: For streaming tools (will be wrapped by caller)
    """
    registry = get_registry()

    # Lookup tool
    tool_metadata = registry.get(request.method)
    if not tool_metadata:
        return method_not_found(request_id=request.id, method=request.method)

    # Prepare params
    params = request.params or {}

    try:
        # Execute tool with timeout
        if tool_metadata.streaming:
            # For streaming tools, return the generator directly
            # The caller will wrap it with stream_generator
            return await _execute_streaming_tool(
                tool_metadata,
                params,
                request.id,
            )
        else:
            # For non-streaming tools, await result
            result = await _execute_tool(
                tool_metadata,
                params,
            )
            return create_success_response(result=result, request_id=request.id)

    except asyncio.TimeoutError:
        return server_error(
            request_id=request.id,
            message="Tool execution timed out",
            data={"timeout": tool_metadata.timeout},
        )
    except ParameterValidationError as e:
        # Pydantic validation error or parameter validation failures
        return invalid_params(
            request_id=request.id,
            data=str(e),
        )
    except ResponseValidationError as e:
        # Response validation error
        return server_error(
            request_id=request.id,
            message=f"Response validation failed: {str(e)}",
            data={"error_type": "ResponseValidationError"},
        )
    except TypeError as e:
        # Invalid params passed to function (e.g., missing required kwargs)
        return invalid_params(
            request_id=request.id,
            data=str(e),
        )
    except Exception as e:
        # Any other error from tool execution
        return server_error(
            request_id=request.id,
            message=f"Tool execution failed: {str(e)}",
            data={"error_type": type(e).__name__},
        )


async def _execute_tool(tool_metadata, params: dict):
    """
    Execute a non-streaming tool with timeout and validate response.

    Args:
        tool_metadata: Tool metadata containing function and parameter pattern
        params: Tool parameters as dict

    Returns:
        Validated tool result
    """
    fn = tool_metadata.fn
    timeout = tool_metadata.timeout

    # Call the function based on its parameter pattern
    if tool_metadata.param_pattern == ParameterPattern.DICT:
        # Pass params as a single dict argument
        result = await asyncio.wait_for(fn(params), timeout=timeout)

    elif tool_metadata.param_pattern == ParameterPattern.KWARGS:
        # Unpack params as keyword arguments
        result = await asyncio.wait_for(fn(**params), timeout=timeout)

    elif tool_metadata.param_pattern == ParameterPattern.PYDANTIC:
        # Validate and instantiate Pydantic model, then pass it
        try:
            model_instance = tool_metadata.param_model(**params)
        except Exception as e:
            # Re-raise as ParameterValidationError for proper error handling
            raise ParameterValidationError(f"Parameter validation failed: {str(e)}") from e

        result = await asyncio.wait_for(fn(model_instance), timeout=timeout)

    else:
        raise ValueError(f"Unknown parameter pattern: {tool_metadata.param_pattern}")

    # Validate response before returning
    return _validate_response(result, tool_metadata)


async def _execute_streaming_tool(tool_metadata, params: dict, request_id):
    """
    Execute a streaming tool and return an async generator.

    Args:
        tool_metadata: Tool metadata containing function and parameter pattern
        params: Tool parameters as dict
        request_id: JSON-RPC request ID

    Returns:
        AsyncGenerator that yields streaming chunks
    """
    fn = tool_metadata.fn

    # Start the generator based on parameter pattern
    if tool_metadata.param_pattern == ParameterPattern.DICT:
        # Pass params as a single dict argument
        generator = fn(params)

    elif tool_metadata.param_pattern == ParameterPattern.KWARGS:
        # Unpack params as keyword arguments
        generator = fn(**params)

    elif tool_metadata.param_pattern == ParameterPattern.PYDANTIC:
        # Validate and instantiate Pydantic model, then pass it
        try:
            model_instance = tool_metadata.param_model(**params)
        except Exception as e:
            # Re-raise as ParameterValidationError for proper error handling
            raise ParameterValidationError(f"Parameter validation failed: {str(e)}") from e

        generator = fn(model_instance)

    else:
        raise ValueError(f"Unknown parameter pattern: {tool_metadata.param_pattern}")

    # Verify it's actually an async generator
    if not inspect.isasyncgen(generator):
        raise TypeError(f"Streaming tool must return an async generator, got {type(generator)}")

    # Simply return the generator - app.py will handle final response
    return generator
