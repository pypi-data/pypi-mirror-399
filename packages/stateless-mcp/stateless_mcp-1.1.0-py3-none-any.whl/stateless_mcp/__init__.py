"""Stateless MCP - A stateless JSON-RPC 2.0 server with MCP protocol support."""

from .registry import tool, get_registry, ParameterPattern, ResponsePattern
from .app import app
from .config import settings

<<<<<<< HEAD
__version__ = "1.1.0"
=======
__version__ = "2.0.0"
>>>>>>> 96a1b87fa679a092aec52f8a0f22008f13db9238
__all__ = ["tool", "get_registry", "app", "settings", "ParameterPattern", "ResponsePattern"]
