"""Streaming helpers for in-band HTTP streaming."""

import json
from typing import AsyncGenerator, Any, Union

from .models import JSONRPCResponse, JSONRPCErrorResponse
from .rpc import serialize_response


async def stream_generator(
    generator: AsyncGenerator,
    final_response: Union[JSONRPCResponse, JSONRPCErrorResponse],
) -> AsyncGenerator[str, None]:
    """
    Stream chunks from an async generator, then send final JSON-RPC response.

    This implements in-band streaming:
    1. Stream each yielded chunk as a JSON line
    2. After generator completes, stream final JSON-RPC response

    Args:
        generator: Async generator that yields streaming chunks
        final_response: Final JSON-RPC response to send after streaming

    Yields:
        JSON-encoded strings (one per line)
    """
    try:
        # Stream all intermediate chunks
        async for chunk in generator:
            # Serialize chunk to JSON
            if isinstance(chunk, dict):
                chunk_json = json.dumps(chunk)
            else:
                # Wrap non-dict values
                chunk_json = json.dumps({"value": chunk})

            yield chunk_json + "\n"

    except Exception as e:
        # If generator fails, we still need to send a final response
        # but we can't change the final_response here as it's passed in
        # The dispatcher should handle this case
        raise

    finally:
        # Always send final JSON-RPC response
        final_json = serialize_response(final_response)
        yield final_json + "\n"


async def collect_stream_result(generator: AsyncGenerator) -> Any:
    """
    Collect all values from an async generator and return the last one.

    This is used when a streaming tool needs to produce a final result.

    Args:
        generator: Async generator

    Returns:
        Last yielded value, or None if generator was empty
    """
    last_value = None
    async for value in generator:
        last_value = value
    return last_value


def format_chunk(chunk_type: str, value: Any) -> dict:
    """
    Format a streaming chunk.

    Args:
        chunk_type: Type of chunk (e.g., "progress", "log", "data")
        value: Chunk value

    Returns:
        Formatted chunk dictionary
    """
    return {"type": chunk_type, "value": value}
