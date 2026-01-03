"""Structured logging configuration for stateless MCP."""

import logging
import sys
import structlog
from typing import Any, Dict
from contextvars import ContextVar

# Context variable for request ID tracking
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def add_request_id(logger: Any, method_name: str, event_dict: Dict) -> Dict:
    """Add request ID to log context."""
    request_id = request_id_var.get()
    if request_id:
        event_dict["request_id"] = request_id
    return event_dict


def configure_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """
    Configure structured logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_format: Format (json, console)
    """
    # Validate log format
    if log_format not in ["json", "console"]:
        raise ValueError(f"Invalid log format: {log_format}")

    # Configure structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        add_request_id,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Structured logger instance
    """
    return structlog.get_logger(name)


def set_request_id(request_id: str) -> None:
    """Set request ID for current context."""
    request_id_var.set(request_id)


def get_request_id() -> str:
    """Get request ID from current context."""
    return request_id_var.get()


def clear_request_id() -> None:
    """Clear request ID from current context."""
    request_id_var.set("")


def mask_sensitive_data(data: Dict, sensitive_keys: set = None) -> Dict:
    """
    Mask sensitive data in logs.

    Args:
        data: Dictionary to mask
        sensitive_keys: Set of keys to mask (default: common sensitive keys)

    Returns:
        Masked dictionary
    """
    if sensitive_keys is None:
        sensitive_keys = {
            "password", "token", "api_key", "secret", "authorization",
            "auth", "credential", "private_key", "access_token"
        }

    def _mask_recursive(obj):
        """Recursively mask sensitive data in nested structures."""
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                # Check if key contains any sensitive keywords
                if any(sens in key.lower() for sens in sensitive_keys):
                    result[key] = "***MASKED***"
                else:
                    result[key] = _mask_recursive(value)
            return result
        elif isinstance(obj, list):
            return [_mask_recursive(item) for item in obj]
        else:
            return obj

    return _mask_recursive(data)
