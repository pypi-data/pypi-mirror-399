"""Tool registry and decorator for registering MCP tools."""

from typing import Callable, Dict, Optional, Any, get_origin, get_args
from functools import wraps
import inspect
from enum import Enum

from .config import settings


class ParameterPattern(str, Enum):
    """Enumeration of supported parameter patterns for tools."""

    DICT = "dict"  # async def tool(params: dict)
    KWARGS = "kwargs"  # async def tool(a: int, b: str, ...)
    PYDANTIC = "pydantic"  # async def tool(params: SomeModel)


class ResponsePattern(str, Enum):
    """Enumeration of supported response patterns for tools."""

    ANY = "any"  # No validation, return any value
    DICT = "dict"  # Return type is dict, basic validation
    PYDANTIC = "pydantic"  # Return type is Pydantic model, full validation


def _is_pydantic_model(type_hint: Any) -> bool:
    """
    Check if a type hint is a Pydantic BaseModel subclass.

    Args:
        type_hint: The type annotation to check

    Returns:
        True if it's a Pydantic BaseModel subclass
    """
    try:
        # Import pydantic here to avoid making it a hard dependency
        from pydantic import BaseModel

        # Check if it's a class and subclass of BaseModel (but not BaseModel itself)
        return (
            inspect.isclass(type_hint)
            and issubclass(type_hint, BaseModel)
            and type_hint is not BaseModel
        )
    except ImportError:
        # Pydantic not installed
        return False


def _detect_parameter_pattern(fn: Callable) -> tuple[ParameterPattern, Optional[type], Dict[str, Any]]:
    """
    Detect the parameter pattern of a function.

    Args:
        fn: The function to inspect

    Returns:
        Tuple of (pattern, pydantic_model, param_info)
        - pattern: The detected parameter pattern
        - pydantic_model: The Pydantic model class if pattern is PYDANTIC, else None
        - param_info: Dictionary of parameter information for KWARGS pattern
    """
    sig = inspect.signature(fn)
    params = list(sig.parameters.values())

    # Filter out *args, **kwargs, and self/cls
    params = [
        p
        for p in params
        if p.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        and p.name not in ("self", "cls")
    ]

    if len(params) == 0:
        # No parameters - treat as dict pattern with empty dict
        return ParameterPattern.DICT, None, {}

    if len(params) == 1:
        # Single parameter - could be dict or Pydantic model
        param = params[0]
        annotation = param.annotation

        # Check if it's a Pydantic model
        if annotation != inspect.Parameter.empty and _is_pydantic_model(annotation):
            return ParameterPattern.PYDANTIC, annotation, {}

        # Check if it's explicitly annotated as dict
        if annotation == dict or annotation == Dict or annotation == Dict[str, Any]:
            return ParameterPattern.DICT, None, {}

        # If no annotation or other type, default to dict
        return ParameterPattern.DICT, None, {}

    # Multiple parameters - kwargs pattern
    param_info = {}
    for param in params:
        param_info[param.name] = {
            "annotation": param.annotation,
            "default": param.default if param.default != inspect.Parameter.empty else None,
            "has_default": param.default != inspect.Parameter.empty,
        }

    return ParameterPattern.KWARGS, None, param_info


def _detect_response_pattern(fn: Callable) -> tuple[ResponsePattern, Optional[type]]:
    """
    Detect the response pattern of a function from its return type annotation.

    Args:
        fn: The function to inspect

    Returns:
        Tuple of (pattern, response_model)
        - pattern: The detected response pattern
        - response_model: The Pydantic model class if pattern is PYDANTIC, else None
    """
    sig = inspect.signature(fn)
    return_annotation = sig.return_annotation

    # No return annotation or any type
    if return_annotation in (inspect.Parameter.empty, None, Any):
        return ResponsePattern.ANY, None

    # Check if it's a Pydantic model
    if _is_pydantic_model(return_annotation):
        return ResponsePattern.PYDANTIC, return_annotation

    # Check if it's explicitly dict
    if return_annotation == dict or return_annotation == Dict or return_annotation == Dict[str, Any]:
        return ResponsePattern.DICT, None

    # For any other type annotation, treat as ANY (no validation)
    # Could be extended to support other types in the future
    return ResponsePattern.ANY, None


class ToolMetadata:
    """Metadata for a registered tool."""

    def __init__(
        self,
        fn: Callable,
        name: str,
        streaming: bool = False,
        timeout: Optional[int] = None,
    ):
        self.fn = fn
        self.name = name
        self.streaming = streaming
        self.timeout = timeout or settings.default_tool_timeout

        # Detect parameter pattern
        self.param_pattern, self.param_model, self.param_info = _detect_parameter_pattern(fn)

        # Detect response pattern (only for non-streaming tools)
        if not streaming:
            self.response_pattern, self.response_model = _detect_response_pattern(fn)
        else:
            # Streaming tools yield items, so response validation doesn't apply the same way
            self.response_pattern = ResponsePattern.ANY
            self.response_model = None

        # Validate timeout
        if self.timeout > settings.max_tool_timeout:
            raise ValueError(
                f"Tool timeout {self.timeout}s exceeds maximum allowed {settings.max_tool_timeout}s"
            )

        # Validate function signature
        if not inspect.iscoroutinefunction(fn) and not inspect.isasyncgenfunction(fn):
            raise ValueError(f"Tool function must be async (either async def or async generator)")

    def __repr__(self):
        return (
            f"ToolMetadata(name={self.name}, streaming={self.streaming}, "
            f"timeout={self.timeout}, param_pattern={self.param_pattern}, "
            f"response_pattern={self.response_pattern})"
        )


class ToolRegistry:
    """Registry for MCP tools."""

    def __init__(self):
        self._tools: Dict[str, ToolMetadata] = {}
        self._locked = False

    def register(
        self,
        name: str,
        fn: Callable,
        streaming: bool = False,
        timeout: Optional[int] = None,
    ) -> None:
        """
        Register a tool.

        Args:
            name: Tool name (method name in JSON-RPC)
            fn: Async callable or async generator
            streaming: Whether the tool streams results
            timeout: Tool execution timeout in seconds

        Raises:
            ValueError: If registry is locked or tool already exists
        """
        if self._locked:
            raise ValueError("Registry is locked. Cannot register tools after startup.")

        if name in self._tools:
            raise ValueError(f"Tool '{name}' is already registered.")

        metadata = ToolMetadata(fn=fn, name=name, streaming=streaming, timeout=timeout)
        self._tools[name] = metadata

    def get(self, name: str) -> Optional[ToolMetadata]:
        """
        Get tool metadata by name.

        Args:
            name: Tool name

        Returns:
            ToolMetadata if found, None otherwise
        """
        return self._tools.get(name)

    def list_tools(self) -> Dict[str, ToolMetadata]:
        """
        Get all registered tools.

        Returns:
            Dictionary of tool name to metadata
        """
        return self._tools.copy()

    def lock(self) -> None:
        """Lock the registry to prevent further modifications."""
        self._locked = True

    def is_locked(self) -> bool:
        """Check if registry is locked."""
        return self._locked


# Global tool registry
_global_registry = ToolRegistry()


def tool(
    name: Optional[str] = None,
    streaming: bool = False,
    timeout: Optional[int] = None,
):
    """
    Decorator to register a tool in the global registry.

    Args:
        name: Tool name (defaults to function name)
        streaming: Whether the tool streams results
        timeout: Tool execution timeout in seconds

    Returns:
        Decorated function

    Example:
        @tool(name="my_tool", streaming=False, timeout=30)
        async def my_tool(params: dict) -> dict:
            return {"result": "success"}
    """

    def decorator(fn: Callable) -> Callable:
        tool_name = name or fn.__name__

        # Register the tool
        _global_registry.register(
            name=tool_name,
            fn=fn,
            streaming=streaming,
            timeout=timeout,
        )

        # Return the original function unchanged
        return fn

    return decorator


def get_registry() -> ToolRegistry:
    """
    Get the global tool registry.

    Returns:
        Global ToolRegistry instance
    """
    return _global_registry
