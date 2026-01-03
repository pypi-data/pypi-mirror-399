"""Configuration settings for stateless MCP server."""

from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_prefix="SMCP_", case_sensitive=False)

    # V1 Settings (backward compatible)
    # Default timeout for tool execution (seconds)
    default_tool_timeout: int = 60

    # Maximum timeout allowed for any tool (seconds)
    max_tool_timeout: int = 300

    # Maximum request body size (bytes)
    max_request_size: int = 10 * 1024 * 1024  # 10MB

    # Streaming chunk flush interval (seconds)
    stream_flush_interval: float = 0.1

    # Enable debug logging
    debug: bool = False

    # Server host
    host: str = "0.0.0.0"

    # Server port
    port: int = 8000

    # Number of workers (for production deployment)
    workers: int = 4

    # V2 Settings - Observability
    log_level: str = "INFO"
    log_format: str = "json"  # json or console
    metrics_enabled: bool = True

    # V2 Settings - Security
    auth_enabled: bool = False
    api_keys: List[str] = []
    auth_header_name: str = "X-API-Key"

    # V2 Settings - Rate Limiting
    rate_limit_enabled: bool = True
    default_rate_limit: str = "100/minute"
    per_tool_rate_limits: dict = {}

    # V2 Settings - Validation
    strict_validation: bool = True


# Global settings instance
settings = Settings()
