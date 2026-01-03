"""Comprehensive tests for structured logging module."""

import json
import logging
from io import StringIO
from unittest.mock import patch

import pytest
import structlog

from stateless_mcp.logging import (
    configure_logging,
    get_logger,
    set_request_id,
    get_request_id,
    clear_request_id,
    mask_sensitive_data,
)


class TestStructuredLogging:
    """Test structured logging configuration and usage."""

    def test_configure_logging_json_format(self):
        """Test JSON log format configuration."""
        configure_logging(log_level="INFO", log_format="json")
        logger = get_logger("test")

        # Capture log output
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            logger.info("test message", extra_field="value")
            output = mock_stdout.getvalue()

            # Should be valid JSON
            log_entry = json.loads(output)
            assert log_entry["event"] == "test message"
            assert log_entry["extra_field"] == "value"
            assert "timestamp" in log_entry
            assert log_entry["level"] == "info"

    def test_configure_logging_console_format(self):
        """Test console log format configuration."""
        configure_logging(log_level="DEBUG", log_format="console")
        logger = get_logger("test")

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            logger.debug("debug message")
            output = mock_stdout.getvalue()

            # Console format should be human-readable
            assert "debug message" in output
            assert "DEBUG" in output or "debug" in output

    def test_configure_logging_invalid_format(self):
        """Test invalid log format raises error."""
        with pytest.raises(ValueError, match="Invalid log format"):
            configure_logging(log_level="INFO", log_format="invalid")

    def test_log_levels(self):
        """Test different log levels."""
        configure_logging(log_level="INFO", log_format="json")
        logger = get_logger("test")

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            logger.debug("debug")  # Should not appear
            logger.info("info")
            logger.warning("warning")
            logger.error("error")

            output = mock_stdout.getvalue()
            lines = [line for line in output.strip().split("\n") if line]

            # Debug should be filtered out
            assert len(lines) == 3

            # Check each level
            info_log = json.loads(lines[0])
            assert info_log["level"] == "info"

            warning_log = json.loads(lines[1])
            assert warning_log["level"] == "warning"

            error_log = json.loads(lines[2])
            assert error_log["level"] == "error"


class TestRequestIdTracking:
    """Test request ID context tracking."""

    def test_set_and_get_request_id(self):
        """Test setting and retrieving request ID."""
        request_id = "test-request-123"
        set_request_id(request_id)

        assert get_request_id() == request_id

    def test_clear_request_id(self):
        """Test clearing request ID."""
        set_request_id("test-request-123")
        assert get_request_id() == "test-request-123"

        clear_request_id()
        assert get_request_id() is None

    def test_request_id_in_logs(self):
        """Test request ID appears in log output."""
        configure_logging(log_level="INFO", log_format="json")
        logger = get_logger("test")

        request_id = "req-456"
        set_request_id(request_id)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            logger.info("test message")
            output = mock_stdout.getvalue()

            log_entry = json.loads(output)
            assert log_entry["request_id"] == request_id

        clear_request_id()

    def test_request_id_isolation(self):
        """Test request ID is isolated per context."""
        # Simulate different requests
        set_request_id("request-1")
        assert get_request_id() == "request-1"

        clear_request_id()
        assert get_request_id() is None

        set_request_id("request-2")
        assert get_request_id() == "request-2"

        clear_request_id()


class TestSensitiveDataMasking:
    """Test sensitive data masking functionality."""

    def test_mask_default_sensitive_keys(self):
        """Test masking default sensitive keys."""
        data = {
            "username": "user123",
            "password": "secret123",
            "api_key": "key123",
            "token": "token123",
            "secret": "secret123",
            "authorization": "Bearer token",
            "safe_field": "visible",
        }

        masked = mask_sensitive_data(data)

        assert masked["username"] == "user123"
        assert masked["password"] == "***MASKED***"
        assert masked["api_key"] == "***MASKED***"
        assert masked["token"] == "***MASKED***"
        assert masked["secret"] == "***MASKED***"
        assert masked["authorization"] == "***MASKED***"
        assert masked["safe_field"] == "visible"

    def test_mask_custom_sensitive_keys(self):
        """Test masking custom sensitive keys."""
        data = {
            "custom_secret": "secret",
            "public_field": "visible",
        }

        masked = mask_sensitive_data(data, sensitive_keys={"custom_secret"})

        assert masked["custom_secret"] == "***MASKED***"
        assert masked["public_field"] == "visible"

    def test_mask_nested_data(self):
        """Test masking nested dictionaries."""
        data = {
            "user": {
                "username": "user123",
                "password": "secret",
            },
            "config": {
                "api_key": "key123",
                "timeout": 30,
            },
        }

        masked = mask_sensitive_data(data)

        assert masked["user"]["username"] == "user123"
        assert masked["user"]["password"] == "***MASKED***"
        assert masked["config"]["api_key"] == "***MASKED***"
        assert masked["config"]["timeout"] == 30

    def test_mask_list_data(self):
        """Test masking data in lists."""
        data = {
            "items": [
                {"name": "item1", "password": "secret1"},
                {"name": "item2", "api_key": "key2"},
            ]
        }

        masked = mask_sensitive_data(data)

        assert masked["items"][0]["name"] == "item1"
        assert masked["items"][0]["password"] == "***MASKED***"
        assert masked["items"][1]["name"] == "item2"
        assert masked["items"][1]["api_key"] == "***MASKED***"

    def test_mask_preserves_original(self):
        """Test that masking doesn't modify original data."""
        original = {
            "password": "secret",
            "public": "visible",
        }

        masked = mask_sensitive_data(original)

        # Original should be unchanged
        assert original["password"] == "secret"
        assert original["public"] == "visible"

        # Masked should have masked values
        assert masked["password"] == "***MASKED***"
        assert masked["public"] == "visible"

    def test_mask_non_dict_values(self):
        """Test masking handles non-dict values correctly."""
        data = {
            "password": "secret",
            "number": 42,
            "boolean": True,
            "none_value": None,
            "list_value": [1, 2, 3],
        }

        masked = mask_sensitive_data(data)

        assert masked["password"] == "***MASKED***"
        assert masked["number"] == 42
        assert masked["boolean"] is True
        assert masked["none_value"] is None
        assert masked["list_value"] == [1, 2, 3]

    def test_mask_empty_dict(self):
        """Test masking empty dictionary."""
        data = {}
        masked = mask_sensitive_data(data)
        assert masked == {}

    def test_mask_case_insensitive(self):
        """Test masking is case-sensitive by default."""
        data = {
            "PASSWORD": "secret",
            "Password": "secret2",
            "password": "secret3",
        }

        masked = mask_sensitive_data(data)

        # Only exact match should be masked
        assert masked["PASSWORD"] == "secret"  # Not masked (case-sensitive)
        assert masked["Password"] == "secret2"  # Not masked (case-sensitive)
        assert masked["password"] == "***MASKED***"  # Masked


class TestLoggerRetrieval:
    """Test logger retrieval and usage."""

    def test_get_logger_with_name(self):
        """Test getting logger with specific name."""
        logger = get_logger("my.module")
        assert logger is not None

    def test_get_logger_different_names(self):
        """Test getting loggers with different names."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        # Both should be valid loggers
        assert logger1 is not None
        assert logger2 is not None

    def test_logger_info_method(self):
        """Test logger info method."""
        configure_logging(log_level="INFO", log_format="json")
        logger = get_logger("test")

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            logger.info("info message", key="value")
            output = mock_stdout.getvalue()

            log_entry = json.loads(output)
            assert log_entry["event"] == "info message"
            assert log_entry["key"] == "value"

    def test_logger_error_method(self):
        """Test logger error method."""
        configure_logging(log_level="ERROR", log_format="json")
        logger = get_logger("test")

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            logger.error("error message", error_code=500)
            output = mock_stdout.getvalue()

            log_entry = json.loads(output)
            assert log_entry["event"] == "error message"
            assert log_entry["error_code"] == 500
            assert log_entry["level"] == "error"

    def test_logger_warning_method(self):
        """Test logger warning method."""
        configure_logging(log_level="WARNING", log_format="json")
        logger = get_logger("test")

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            logger.warning("warning message")
            output = mock_stdout.getvalue()

            log_entry = json.loads(output)
            assert log_entry["event"] == "warning message"
            assert log_entry["level"] == "warning"


class TestLoggingIntegration:
    """Integration tests for logging in realistic scenarios."""

    def test_request_lifecycle_logging(self):
        """Test logging throughout a request lifecycle."""
        configure_logging(log_level="INFO", log_format="json")
        logger = get_logger("api")

        request_id = "req-789"
        set_request_id(request_id)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            logger.info("Request received", method="POST", path="/mcp")
            logger.info("Tool invoked", tool="add", params={"a": 5, "b": 3})
            logger.info("Request completed", status=200, duration_ms=45)

            output = mock_stdout.getvalue()
            lines = [json.loads(line) for line in output.strip().split("\n") if line]

            # All logs should have same request ID
            assert all(log["request_id"] == request_id for log in lines)

            # Check sequence
            assert lines[0]["event"] == "Request received"
            assert lines[1]["event"] == "Tool invoked"
            assert lines[2]["event"] == "Request completed"

        clear_request_id()

    def test_error_logging_with_context(self):
        """Test error logging with full context."""
        configure_logging(log_level="ERROR", log_format="json")
        logger = get_logger("api")

        set_request_id("req-error-123")

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            try:
                raise ValueError("Invalid parameter")
            except ValueError as e:
                logger.error(
                    "Tool execution failed",
                    error=str(e),
                    error_type=type(e).__name__,
                    tool="add",
                )

            output = mock_stdout.getvalue()
            log_entry = json.loads(output)

            assert log_entry["event"] == "Tool execution failed"
            assert log_entry["error"] == "Invalid parameter"
            assert log_entry["error_type"] == "ValueError"
            assert log_entry["tool"] == "add"
            assert log_entry["request_id"] == "req-error-123"

        clear_request_id()

    def test_sensitive_data_in_logs(self):
        """Test that sensitive data gets masked in logs."""
        configure_logging(log_level="INFO", log_format="json")
        logger = get_logger("api")

        request_data = {
            "username": "user123",
            "password": "secret123",
            "action": "login",
        }

        masked_data = mask_sensitive_data(request_data)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            logger.info("User action", data=masked_data)
            output = mock_stdout.getvalue()

            log_entry = json.loads(output)
            assert log_entry["data"]["password"] == "***MASKED***"
            assert log_entry["data"]["username"] == "user123"
            assert log_entry["data"]["action"] == "login"
