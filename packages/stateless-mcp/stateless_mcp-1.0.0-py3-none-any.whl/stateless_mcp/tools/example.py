"""Example tools demonstrating streaming and non-streaming functionality."""

import asyncio
from typing import Optional
from stateless_mcp import tool

try:
    from pydantic import BaseModel

    PYDANTIC_AVAILABLE = True

    class CalculateParams(BaseModel):
        """Pydantic model for calculation parameters."""

        a: float
        b: float
        operation: str = "add"

    class StreamTextParams(BaseModel):
        """Pydantic model for text streaming parameters."""

        text: str
        chunk_size: int = 10

    class CalculationResult(BaseModel):
        """Pydantic model for validated calculation responses."""

        operation: str
        a: float
        b: float
        result: float

    class UserInfo(BaseModel):
        """Pydantic model for user information responses."""

        name: str
        email: str
        age: int
        active: bool = True

except ImportError:
    PYDANTIC_AVAILABLE = False


@tool(name="echo", streaming=False, timeout=30)
async def echo_tool(params: dict) -> dict:
    """
    Simple echo tool that returns the input parameters.

    Args:
        params: Input parameters

    Returns:
        Same parameters echoed back
    """
    return {"echo": params}


@tool(name="add", streaming=False, timeout=30)
async def add_tool(params: dict) -> dict:
    """
    Add two numbers.

    Args:
        params: Dict with 'a' and 'b' keys

    Returns:
        Sum of a and b
    """
    a = params.get("a", 0)
    b = params.get("b", 0)
    return {"result": a + b}


@tool(name="slow_operation", streaming=False, timeout=60)
async def slow_operation(params: dict) -> dict:
    """
    Simulates a slow operation.

    Args:
        params: Dict with optional 'duration' key (seconds)

    Returns:
        Result after delay
    """
    duration = params.get("duration", 2)
    await asyncio.sleep(duration)
    return {"completed": True, "duration": duration}


@tool(name="generate_numbers", streaming=True, timeout=60)
async def generate_numbers(params: dict):
    """
    Streaming tool that generates a sequence of numbers.

    Args:
        params: Dict with 'count' (number of items to generate)

    Yields:
        Progress chunks with current number
    """
    count = params.get("count", 10)

    for i in range(count):
        await asyncio.sleep(0.1)  # Simulate work
        yield {
            "type": "progress",
            "current": i + 1,
            "total": count,
            "percentage": ((i + 1) / count) * 100,
        }

    # Final result
    yield {"type": "result", "generated": count}


@tool(name="process_with_progress", streaming=True, timeout=120)
async def process_with_progress(params: dict):
    """
    Simulates a long-running process with progress updates.

    Args:
        params: Dict with 'steps' (number of processing steps)

    Yields:
        Progress updates and final result
    """
    steps = params.get("steps", 5)
    task_name = params.get("task_name", "processing")

    yield {"type": "log", "message": f"Starting {task_name}..."}

    for step in range(steps):
        await asyncio.sleep(0.5)  # Simulate work

        yield {
            "type": "progress",
            "step": step + 1,
            "total_steps": steps,
            "percentage": ((step + 1) / steps) * 100,
            "message": f"Completed step {step + 1}/{steps}",
        }

    yield {"type": "log", "message": f"Finished {task_name}"}

    # Final result
    yield {
        "type": "result",
        "task_name": task_name,
        "steps_completed": steps,
        "status": "success",
    }


@tool(name="create_job_from_text", streaming=False, timeout=60)
async def create_job_from_text(params: dict) -> dict:
    """
    Example tool that mimics creating a job from text.

    Args:
        params: Dict with 'text' and optional 'job_type'

    Returns:
        Job creation result
    """
    text = params.get("text", "")
    job_type = params.get("job_type", "default")

    # Simulate processing
    await asyncio.sleep(0.5)

    return {
        "job_id": "job_12345",
        "job_type": job_type,
        "text_length": len(text),
        "status": "created",
        "created_at": "2025-01-01T00:00:00Z",
    }


@tool(name="generate_jd_stream", streaming=True, timeout=120)
async def generate_jd_stream(params: dict):
    """
    Example streaming tool that generates a job description.

    Args:
        params: Dict with job details

    Yields:
        Streaming chunks of the generated JD
    """
    job_title = params.get("job_title", "Software Engineer")
    company = params.get("company", "Tech Corp")

    sections = [
        f"# Job Description: {job_title}",
        f"\n## Company\n{company}",
        "\n## Responsibilities\n- Design and develop software solutions",
        "- Collaborate with cross-functional teams",
        "- Write clean, maintainable code",
        "\n## Requirements\n- 3+ years of experience",
        "- Strong problem-solving skills",
        "- Excellent communication",
    ]

    for i, section in enumerate(sections):
        await asyncio.sleep(0.3)  # Simulate generation time

        yield {
            "type": "content",
            "chunk": section,
            "progress": ((i + 1) / len(sections)) * 100,
        }

    # Final result with complete JD
    yield {
        "type": "result",
        "job_title": job_title,
        "company": company,
        "full_text": "".join(sections),
        "status": "completed",
    }


# ============================================================================
# KWARGS PATTERN EXAMPLES - Named parameters
# ============================================================================


@tool(name="multiply_kwargs", streaming=False, timeout=30)
async def multiply_kwargs(a: float, b: float, decimals: int = 2) -> dict:
    """
    Multiply two numbers using named parameters (kwargs pattern).

    This demonstrates the kwargs parameter pattern where parameters
    are passed as individual named arguments instead of a dict.

    Args:
        a: First number
        b: Second number
        decimals: Number of decimal places (default: 2)

    Returns:
        Multiplication result
    """
    result = a * b
    return {
        "operation": "multiply",
        "a": a,
        "b": b,
        "result": round(result, decimals),
    }


@tool(name="greet", streaming=False, timeout=30)
async def greet(name: str, greeting: str = "Hello", punctuation: str = "!") -> dict:
    """
    Greet a person using kwargs pattern.

    Args:
        name: Person's name
        greeting: Greeting word (default: "Hello")
        punctuation: Ending punctuation (default: "!")

    Returns:
        Greeting message
    """
    message = f"{greeting}, {name}{punctuation}"
    return {"message": message}


@tool(name="count_up", streaming=True, timeout=60)
async def count_up(start: int = 0, end: int = 10, step: int = 1):
    """
    Streaming tool that counts from start to end using kwargs pattern.

    Args:
        start: Starting number (default: 0)
        end: Ending number (default: 10)
        step: Step size (default: 1)

    Yields:
        Progress updates with current count
    """
    current = start
    total_steps = (end - start) // step

    for i, num in enumerate(range(start, end, step)):
        await asyncio.sleep(0.1)
        yield {
            "type": "progress",
            "current": num,
            "step_number": i + 1,
            "total_steps": total_steps,
        }

    yield {"type": "result", "final_value": current, "steps": total_steps}


# ============================================================================
# PYDANTIC PATTERN EXAMPLES - Pydantic model validation
# ============================================================================

if PYDANTIC_AVAILABLE:

    @tool(name="calculate_pydantic", streaming=False, timeout=30)
    async def calculate_pydantic(params: CalculateParams) -> dict:
        """
        Perform calculations with type validation using Pydantic model.

        This demonstrates the Pydantic parameter pattern which provides
        automatic validation, type checking, and better IDE support.

        Args:
            params: Validated calculation parameters

        Returns:
            Calculation result
        """
        a, b, operation = params.a, params.b, params.operation

        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return {"error": "Division by zero"}
            result = a / b
        else:
            return {"error": f"Unknown operation: {operation}"}

        return {
            "operation": operation,
            "a": a,
            "b": b,
            "result": result,
        }

    @tool(name="stream_text_chunks", streaming=True, timeout=60)
    async def stream_text_chunks(params: StreamTextParams):
        """
        Stream text in chunks using Pydantic model validation.

        Args:
            params: Validated streaming parameters

        Yields:
            Text chunks with progress
        """
        text = params.text
        chunk_size = params.chunk_size
        total_chunks = (len(text) + chunk_size - 1) // chunk_size

        for i in range(0, len(text), chunk_size):
            chunk = text[i : i + chunk_size]
            chunk_number = i // chunk_size + 1

            await asyncio.sleep(0.2)

            yield {
                "type": "chunk",
                "chunk_number": chunk_number,
                "total_chunks": total_chunks,
                "content": chunk,
                "progress": (chunk_number / total_chunks) * 100,
            }

        yield {
            "type": "result",
            "total_chunks": total_chunks,
            "total_length": len(text),
            "status": "completed",
        }


# ============================================================================
# RESPONSE VALIDATION EXAMPLES - Different response patterns
# ============================================================================


@tool(name="get_status_any", streaming=False, timeout=30)
async def get_status_any(params: dict):
    """
    Tool with no return type annotation - accepts any response (ANY pattern).

    This is the most flexible but provides no response validation.
    The tool can return any type of value.

    Args:
        params: Input parameters

    Returns:
        Any value (could be dict, str, int, etc.)
    """
    status = params.get("status", "ok")
    # Could return any type - no validation
    if status == "dict":
        return {"status": status, "message": "Working"}
    elif status == "string":
        return "Everything is fine"
    else:
        return {"status": status}


@tool(name="get_info_dict", streaming=False, timeout=30)
async def get_info_dict(params: dict) -> dict:
    """
    Tool with dict return type - validates that response is a dict (DICT pattern).

    The library ensures the return value is actually a dict.
    If you return something else, you'll get a ResponseValidationError.

    Args:
        params: Input parameters

    Returns:
        A dictionary (validated)
    """
    name = params.get("name", "Unknown")
    return {
        "name": name,
        "timestamp": "2025-01-01T00:00:00Z",
        "version": "1.0.0",
    }


if PYDANTIC_AVAILABLE:

    @tool(name="calculate_validated", streaming=False, timeout=30)
    async def calculate_validated(a: float, b: float, operation: str = "add") -> CalculationResult:
        """
        Tool with Pydantic response model - full type validation (PYDANTIC pattern).

        This provides the strongest type safety. The response is validated
        against the Pydantic model, ensuring all fields are present and
        have the correct types.

        You can return either:
        1. A Pydantic model instance (automatically converted to dict)
        2. A dict (validated against the model schema)

        Args:
            a: First number
            b: Second number
            operation: Operation to perform

        Returns:
            Validated CalculationResult model
        """
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            result = a / b if b != 0 else 0
        else:
            result = 0

        # Return a Pydantic model instance (will be converted to dict)
        return CalculationResult(operation=operation, a=a, b=b, result=result)

    @tool(name="create_user", streaming=False, timeout=30)
    async def create_user(name: str, email: str, age: int) -> UserInfo:
        """
        Create a user with validated response using Pydantic model.

        This example returns a dict instead of a model instance,
        but it's still validated against the UserInfo schema.

        Args:
            name: User's name
            email: User's email
            age: User's age

        Returns:
            Validated UserInfo model
        """
        # Return a dict - it will be validated against UserInfo
        return {"name": name, "email": email, "age": age, "active": True}

    @tool(name="get_user_stats", streaming=False, timeout=30)
    async def get_user_stats(params: dict) -> UserInfo:
        """
        Get user statistics with response validation.

        This demonstrates that Pydantic response validation catches
        errors if you return invalid data.

        Args:
            params: Parameters including user_id

        Returns:
            Validated UserInfo model
        """
        user_id = params.get("user_id", 1)

        # This dict will be validated - missing fields or wrong types
        # will raise ResponseValidationError
        return {
            "name": f"User{user_id}",
            "email": f"user{user_id}@example.com",
            "age": 25 + user_id,
            "active": True,
        }
