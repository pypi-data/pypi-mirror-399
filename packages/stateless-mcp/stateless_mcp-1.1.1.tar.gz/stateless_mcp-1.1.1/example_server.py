#!/usr/bin/env python3
"""
Example server demonstrating how to use stateless-mcp.

This example shows:
1. How to define non-streaming tools
2. How to define streaming tools
3. How to run the server

To run:
    python example_server.py

Then test with:
    curl -X POST http://localhost:8000/mcp \\
      -H "Content-Type: application/json" \\
      -d '{"jsonrpc":"2.0","method":"hello","params":{"name":"World"},"id":"1"}'
"""

import asyncio
from stateless_mcp import tool, app
import uvicorn


# Define a simple non-streaming tool
@tool(name="hello", streaming=False, timeout=30)
async def hello_world(params: dict) -> dict:
    """
    Simple hello world tool.

    Args:
        params: Dict with optional 'name' field

    Returns:
        Greeting message
    """
    name = params.get("name", "World")
    return {
        "message": f"Hello, {name}!",
        "timestamp": "2025-01-01T00:00:00Z"
    }


# Define a math tool
@tool(name="calculate", streaming=False, timeout=30)
async def calculate(params: dict) -> dict:
    """
    Perform basic math operations.

    Args:
        params: Dict with 'operation', 'a', and 'b'

    Returns:
        Calculation result
    """
    operation = params.get("operation", "add")
    a = params.get("a", 0)
    b = params.get("b", 0)

    result = None
    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b != 0:
            result = a / b
        else:
            raise ValueError("Cannot divide by zero")

    return {
        "operation": operation,
        "a": a,
        "b": b,
        "result": result
    }


# Define a streaming tool that generates a countdown
@tool(name="countdown", streaming=True, timeout=60)
async def countdown(params: dict):
    """
    Stream a countdown from a given number.

    Args:
        params: Dict with 'start' (number to count down from)

    Yields:
        Progress updates for each number
    """
    start = params.get("start", 10)

    for i in range(start, 0, -1):
        await asyncio.sleep(0.5)
        yield {
            "type": "countdown",
            "current": i,
            "remaining": i - 1
        }

    yield {
        "type": "complete",
        "message": "Countdown finished!"
    }


# Define a streaming data processor
@tool(name="process_items", streaming=True, timeout=120)
async def process_items(params: dict):
    """
    Process a list of items with progress updates.

    Args:
        params: Dict with 'items' (list of items to process)

    Yields:
        Processing progress and results
    """
    items = params.get("items", [])
    total = len(items)

    yield {"type": "log", "message": f"Starting to process {total} items"}

    processed = []
    for i, item in enumerate(items):
        # Simulate processing
        await asyncio.sleep(0.2)

        processed_item = f"processed_{item}"
        processed.append(processed_item)

        yield {
            "type": "progress",
            "item": item,
            "processed": processed_item,
            "current": i + 1,
            "total": total,
            "percentage": ((i + 1) / total) * 100
        }

    yield {
        "type": "result",
        "processed_items": processed,
        "total": len(processed)
    }


if __name__ == "__main__":
    print("=" * 60)
    print("Stateless MCP Example Server")
    print("=" * 60)
    print("\nRegistered tools:")
    print("  - hello (non-streaming)")
    print("  - calculate (non-streaming)")
    print("  - countdown (streaming)")
    print("  - process_items (streaming)")
    print("\nStarting server on http://0.0.0.0:8000")
    print("\nExample requests:")
    print("\n1. Hello World:")
    print('   curl -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -d \'{"jsonrpc":"2.0","method":"hello","params":{"name":"Alice"},"id":"1"}\'')
    print("\n2. Calculate:")
    print('   curl -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -d \'{"jsonrpc":"2.0","method":"calculate","params":{"operation":"multiply","a":6,"b":7},"id":"2"}\'')
    print("\n3. Countdown (streaming):")
    print('   curl -X POST http://localhost:8000/mcp -H "Content-Type: application/json" -d \'{"jsonrpc":"2.0","method":"countdown","params":{"start":5},"id":"3"}\'')
    print("\n" + "=" * 60 + "\n")

    # Run with single worker for development
    uvicorn.run(
        "example_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
