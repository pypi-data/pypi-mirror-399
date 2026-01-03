"""Unit tests for tool registry."""

import pytest
from stateless_mcp.registry import ToolRegistry, ToolMetadata


class TestToolRegistry:
    """Test the tool registry."""

    def test_register_tool(self):
        """Test registering a tool."""
        registry = ToolRegistry()

        async def test_tool(params: dict) -> dict:
            return {"result": "success"}

        registry.register("test_tool", test_tool, streaming=False, timeout=30)

        metadata = registry.get("test_tool")
        assert metadata is not None
        assert metadata.name == "test_tool"
        assert metadata.streaming is False
        assert metadata.timeout == 30

    def test_register_duplicate_tool(self):
        """Test that registering duplicate tool raises error."""
        registry = ToolRegistry()

        async def test_tool(params: dict) -> dict:
            return {}

        registry.register("test_tool", test_tool)

        with pytest.raises(ValueError, match="already registered"):
            registry.register("test_tool", test_tool)

    def test_get_nonexistent_tool(self):
        """Test getting a tool that doesn't exist."""
        registry = ToolRegistry()
        metadata = registry.get("nonexistent")
        assert metadata is None

    def test_list_tools(self):
        """Test listing all tools."""
        registry = ToolRegistry()

        async def tool1(params: dict) -> dict:
            return {}

        async def tool2(params: dict) -> dict:
            return {}

        registry.register("tool1", tool1)
        registry.register("tool2", tool2)

        tools = registry.list_tools()
        assert len(tools) == 2
        assert "tool1" in tools
        assert "tool2" in tools

    def test_lock_registry(self):
        """Test locking the registry."""
        registry = ToolRegistry()

        async def test_tool(params: dict) -> dict:
            return {}

        registry.register("test_tool", test_tool)
        registry.lock()

        assert registry.is_locked()

        with pytest.raises(ValueError, match="locked"):
            registry.register("another_tool", test_tool)

    def test_non_async_function_raises_error(self):
        """Test that non-async functions raise an error."""
        registry = ToolRegistry()

        def sync_tool(params: dict) -> dict:
            return {}

        with pytest.raises(ValueError, match="must be async"):
            registry.register("sync_tool", sync_tool)

    def test_timeout_validation(self):
        """Test that excessive timeout raises error."""
        from stateless_mcp.config import settings

        registry = ToolRegistry()

        async def test_tool(params: dict) -> dict:
            return {}

        # This should work
        registry.register("tool1", test_tool, timeout=settings.max_tool_timeout)

        # This should fail
        with pytest.raises(ValueError, match="exceeds maximum"):
            registry.register("tool2", test_tool, timeout=settings.max_tool_timeout + 1)


class TestToolMetadata:
    """Test ToolMetadata class."""

    def test_create_metadata(self):
        """Test creating tool metadata."""
        async def test_tool(params: dict) -> dict:
            return {}

        metadata = ToolMetadata(
            fn=test_tool,
            name="test_tool",
            streaming=True,
            timeout=60,
        )

        assert metadata.name == "test_tool"
        assert metadata.streaming is True
        assert metadata.timeout == 60

    def test_default_timeout(self):
        """Test default timeout value."""
        from stateless_mcp.config import settings

        async def test_tool(params: dict) -> dict:
            return {}

        metadata = ToolMetadata(fn=test_tool, name="test_tool")

        assert metadata.timeout == settings.default_tool_timeout
