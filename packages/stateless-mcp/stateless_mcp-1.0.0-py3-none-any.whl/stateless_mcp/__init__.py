"""Stateless MCP - A stateless JSON-RPC 2.0 server with streaming support."""

from .registry import tool, get_registry, ParameterPattern, ResponsePattern
from .app import app
from .config import settings

__version__ = "1.0.0"
__all__ = ["tool", "get_registry", "app", "settings", "ParameterPattern", "ResponsePattern"]
