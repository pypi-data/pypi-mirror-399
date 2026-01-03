"""Unit tests for parameter pattern detection and handling."""

import pytest
from typing import Optional
from stateless_mcp.registry import ToolRegistry, ToolMetadata, ParameterPattern, ResponsePattern
from stateless_mcp.errors import ParameterValidationError, ResponseValidationError


class TestParameterPatternDetection:
    """Test parameter pattern detection."""

    def test_detect_dict_pattern(self):
        """Test detection of dict parameter pattern."""
        async def dict_tool(params: dict) -> dict:
            return {"result": "success"}

        metadata = ToolMetadata(fn=dict_tool, name="dict_tool")
        assert metadata.param_pattern == ParameterPattern.DICT
        assert metadata.param_model is None
        assert metadata.param_info == {}

    def test_detect_dict_pattern_no_annotation(self):
        """Test detection of dict pattern when no annotation is provided."""
        async def dict_tool(params) -> dict:
            return {"result": "success"}

        metadata = ToolMetadata(fn=dict_tool, name="dict_tool")
        assert metadata.param_pattern == ParameterPattern.DICT

    def test_detect_kwargs_pattern(self):
        """Test detection of kwargs parameter pattern."""
        async def kwargs_tool(a: int, b: str, c: Optional[float] = None) -> dict:
            return {"a": a, "b": b, "c": c}

        metadata = ToolMetadata(fn=kwargs_tool, name="kwargs_tool")
        assert metadata.param_pattern == ParameterPattern.KWARGS
        assert metadata.param_model is None
        assert len(metadata.param_info) == 3
        assert "a" in metadata.param_info
        assert "b" in metadata.param_info
        assert "c" in metadata.param_info
        assert metadata.param_info["c"]["has_default"] is True

    def test_detect_pydantic_pattern(self):
        """Test detection of Pydantic model parameter pattern."""
        try:
            from pydantic import BaseModel

            class MyParams(BaseModel):
                name: str
                age: int

            async def pydantic_tool(params: MyParams) -> dict:
                return {"name": params.name, "age": params.age}

            metadata = ToolMetadata(fn=pydantic_tool, name="pydantic_tool")
            assert metadata.param_pattern == ParameterPattern.PYDANTIC
            assert metadata.param_model == MyParams
            assert metadata.param_info == {}

        except ImportError:
            pytest.skip("Pydantic not installed")

    def test_detect_no_params(self):
        """Test detection when function has no parameters."""
        async def no_param_tool() -> dict:
            return {"result": "success"}

        metadata = ToolMetadata(fn=no_param_tool, name="no_param_tool")
        # Should default to dict pattern
        assert metadata.param_pattern == ParameterPattern.DICT


class TestDictPatternExecution:
    """Test execution of tools with dict parameters."""

    @pytest.mark.asyncio
    async def test_dict_tool_execution(self):
        """Test executing a tool with dict parameters."""
        from stateless_mcp.dispatcher import _execute_tool

        async def dict_tool(params: dict) -> dict:
            a = params.get("a", 0)
            b = params.get("b", 0)
            return {"result": a + b}

        metadata = ToolMetadata(fn=dict_tool, name="dict_tool", timeout=30)
        params = {"a": 5, "b": 3}

        result = await _execute_tool(metadata, params)
        assert result["result"] == 8

    @pytest.mark.asyncio
    async def test_dict_streaming_tool(self):
        """Test executing a streaming tool with dict parameters."""
        from stateless_mcp.dispatcher import _execute_streaming_tool

        async def dict_stream_tool(params: dict):
            count = params.get("count", 3)
            for i in range(count):
                yield {"index": i}

        metadata = ToolMetadata(fn=dict_stream_tool, name="dict_stream_tool", streaming=True, timeout=30)
        params = {"count": 3}

        generator = await _execute_streaming_tool(metadata, params, request_id=1)
        results = []
        async for item in generator:
            results.append(item)

        assert len(results) == 3
        assert results[0]["index"] == 0
        assert results[2]["index"] == 2


class TestKwargsPatternExecution:
    """Test execution of tools with kwargs parameters."""

    @pytest.mark.asyncio
    async def test_kwargs_tool_execution(self):
        """Test executing a tool with kwargs parameters."""
        from stateless_mcp.dispatcher import _execute_tool

        async def kwargs_tool(a: int, b: int, operation: str = "add") -> dict:
            if operation == "add":
                result = a + b
            elif operation == "multiply":
                result = a * b
            else:
                result = 0
            return {"result": result, "operation": operation}

        metadata = ToolMetadata(fn=kwargs_tool, name="kwargs_tool", timeout=30)
        params = {"a": 5, "b": 3, "operation": "multiply"}

        result = await _execute_tool(metadata, params)
        assert result["result"] == 15
        assert result["operation"] == "multiply"

    @pytest.mark.asyncio
    async def test_kwargs_with_defaults(self):
        """Test kwargs tool with default parameters."""
        from stateless_mcp.dispatcher import _execute_tool

        async def kwargs_tool(a: int, b: int = 10) -> dict:
            return {"result": a + b}

        metadata = ToolMetadata(fn=kwargs_tool, name="kwargs_tool", timeout=30)
        params = {"a": 5}  # b should use default value

        result = await _execute_tool(metadata, params)
        assert result["result"] == 15

    @pytest.mark.asyncio
    async def test_kwargs_streaming_tool(self):
        """Test executing a streaming tool with kwargs parameters."""
        from stateless_mcp.dispatcher import _execute_streaming_tool

        async def kwargs_stream_tool(count: int, prefix: str = "item"):
            for i in range(count):
                yield {"name": f"{prefix}_{i}"}

        metadata = ToolMetadata(fn=kwargs_stream_tool, name="kwargs_stream_tool", streaming=True, timeout=30)
        params = {"count": 2, "prefix": "test"}

        generator = await _execute_streaming_tool(metadata, params, request_id=1)
        results = []
        async for item in generator:
            results.append(item)

        assert len(results) == 2
        assert results[0]["name"] == "test_0"
        assert results[1]["name"] == "test_1"


class TestPydanticPatternExecution:
    """Test execution of tools with Pydantic model parameters."""

    @pytest.mark.asyncio
    async def test_pydantic_tool_execution(self):
        """Test executing a tool with Pydantic model parameters."""
        try:
            from pydantic import BaseModel
            from stateless_mcp.dispatcher import _execute_tool

            class AddParams(BaseModel):
                a: int
                b: int
                operation: str = "add"

            async def pydantic_tool(params: AddParams) -> dict:
                if params.operation == "add":
                    result = params.a + params.b
                elif params.operation == "multiply":
                    result = params.a * params.b
                else:
                    result = 0
                return {"result": result}

            metadata = ToolMetadata(fn=pydantic_tool, name="pydantic_tool", timeout=30)
            params = {"a": 5, "b": 3, "operation": "add"}

            result = await _execute_tool(metadata, params)
            assert result["result"] == 8

        except ImportError:
            pytest.skip("Pydantic not installed")

    @pytest.mark.asyncio
    async def test_pydantic_validation_error(self):
        """Test that Pydantic validation errors are properly handled."""
        try:
            from pydantic import BaseModel
            from stateless_mcp.dispatcher import _execute_tool

            class StrictParams(BaseModel):
                name: str
                age: int

            async def pydantic_tool(params: StrictParams) -> dict:
                return {"name": params.name, "age": params.age}

            metadata = ToolMetadata(fn=pydantic_tool, name="pydantic_tool", timeout=30)
            params = {"name": "John", "age": "not_a_number"}  # Invalid type

            with pytest.raises(ParameterValidationError, match="Parameter validation failed"):
                await _execute_tool(metadata, params)

        except ImportError:
            pytest.skip("Pydantic not installed")

    @pytest.mark.asyncio
    async def test_pydantic_missing_required_field(self):
        """Test that missing required fields are caught."""
        try:
            from pydantic import BaseModel
            from stateless_mcp.dispatcher import _execute_tool

            class StrictParams(BaseModel):
                required_field: str

            async def pydantic_tool(params: StrictParams) -> dict:
                return {"field": params.required_field}

            metadata = ToolMetadata(fn=pydantic_tool, name="pydantic_tool", timeout=30)
            params = {}  # Missing required field

            with pytest.raises(ParameterValidationError, match="Parameter validation failed"):
                await _execute_tool(metadata, params)

        except ImportError:
            pytest.skip("Pydantic not installed")

    @pytest.mark.asyncio
    async def test_pydantic_streaming_tool(self):
        """Test executing a streaming tool with Pydantic parameters."""
        try:
            from pydantic import BaseModel
            from stateless_mcp.dispatcher import _execute_streaming_tool

            class StreamParams(BaseModel):
                count: int
                message: str = "item"

            async def pydantic_stream_tool(params: StreamParams):
                for i in range(params.count):
                    yield {"index": i, "message": params.message}

            metadata = ToolMetadata(
                fn=pydantic_stream_tool, name="pydantic_stream_tool", streaming=True, timeout=30
            )
            params = {"count": 2, "message": "hello"}

            generator = await _execute_streaming_tool(metadata, params, request_id=1)
            results = []
            async for item in generator:
                results.append(item)

            assert len(results) == 2
            assert results[0]["message"] == "hello"

        except ImportError:
            pytest.skip("Pydantic not installed")


class TestRegistryWithPatterns:
    """Test registry integration with different parameter patterns."""

    def test_register_all_patterns(self):
        """Test that all parameter patterns can be registered."""
        registry = ToolRegistry()

        async def dict_tool(params: dict) -> dict:
            return {}

        async def kwargs_tool(a: int, b: str) -> dict:
            return {}

        registry.register("dict_tool", dict_tool)
        registry.register("kwargs_tool", kwargs_tool)

        dict_meta = registry.get("dict_tool")
        kwargs_meta = registry.get("kwargs_tool")

        assert dict_meta.param_pattern == ParameterPattern.DICT
        assert kwargs_meta.param_pattern == ParameterPattern.KWARGS

    def test_register_pydantic_pattern(self):
        """Test registering a Pydantic model tool."""
        try:
            from pydantic import BaseModel

            class MyParams(BaseModel):
                value: int

            async def pydantic_tool(params: MyParams) -> dict:
                return {"value": params.value}

            registry = ToolRegistry()
            registry.register("pydantic_tool", pydantic_tool)

            metadata = registry.get("pydantic_tool")
            assert metadata.param_pattern == ParameterPattern.PYDANTIC
            assert metadata.param_model == MyParams

        except ImportError:
            pytest.skip("Pydantic not installed")


class TestResponsePatternDetection:
    """Test response pattern detection."""

    def test_detect_any_response_no_annotation(self):
        """Test detection when no return type annotation is provided."""
        async def no_return_annotation(params: dict):
            return {"result": "success"}

        metadata = ToolMetadata(fn=no_return_annotation, name="test")
        assert metadata.response_pattern == ResponsePattern.ANY
        assert metadata.response_model is None

    def test_detect_dict_response(self):
        """Test detection of dict response pattern."""
        async def dict_response(params: dict) -> dict:
            return {"result": "success"}

        metadata = ToolMetadata(fn=dict_response, name="test")
        assert metadata.response_pattern == ResponsePattern.DICT
        assert metadata.response_model is None

    def test_detect_pydantic_response(self):
        """Test detection of Pydantic model response pattern."""
        try:
            from pydantic import BaseModel

            class MyResponse(BaseModel):
                message: str
                count: int

            async def pydantic_response(params: dict) -> MyResponse:
                return MyResponse(message="hello", count=5)

            metadata = ToolMetadata(fn=pydantic_response, name="test")
            assert metadata.response_pattern == ResponsePattern.PYDANTIC
            assert metadata.response_model == MyResponse

        except ImportError:
            pytest.skip("Pydantic not installed")

    def test_streaming_tools_have_any_response(self):
        """Test that streaming tools default to ANY response pattern."""
        async def streaming_tool(params: dict):
            yield {"chunk": 1}

        metadata = ToolMetadata(fn=streaming_tool, name="test", streaming=True)
        assert metadata.response_pattern == ResponsePattern.ANY


class TestResponseValidation:
    """Test response validation logic."""

    @pytest.mark.asyncio
    async def test_dict_response_validation_success(self):
        """Test successful validation of dict response."""
        from stateless_mcp.dispatcher import _execute_tool

        async def dict_tool(params: dict) -> dict:
            return {"result": params.get("value", 0) * 2}

        metadata = ToolMetadata(fn=dict_tool, name="dict_tool", timeout=30)
        result = await _execute_tool(metadata, {"value": 5})

        assert result == {"result": 10}

    @pytest.mark.asyncio
    async def test_dict_response_validation_failure(self):
        """Test that returning non-dict when dict is expected fails."""
        from stateless_mcp.dispatcher import _execute_tool

        async def bad_tool(params: dict) -> dict:
            return "not a dict"  # Wrong type!

        metadata = ToolMetadata(fn=bad_tool, name="bad_tool", timeout=30)

        with pytest.raises(ResponseValidationError, match="Expected dict response"):
            await _execute_tool(metadata, {})

    @pytest.mark.asyncio
    async def test_pydantic_response_validation_model_instance(self):
        """Test validation when tool returns Pydantic model instance."""
        try:
            from pydantic import BaseModel
            from stateless_mcp.dispatcher import _execute_tool

            class MyResponse(BaseModel):
                message: str
                count: int

            async def pydantic_tool(params: dict) -> MyResponse:
                return MyResponse(message="hello", count=5)

            metadata = ToolMetadata(fn=pydantic_tool, name="pydantic_tool", timeout=30)
            result = await _execute_tool(metadata, {})

            # Response should be converted to dict
            assert isinstance(result, dict)
            assert result["message"] == "hello"
            assert result["count"] == 5

        except ImportError:
            pytest.skip("Pydantic not installed")

    @pytest.mark.asyncio
    async def test_pydantic_response_validation_dict(self):
        """Test validation when tool returns dict matching Pydantic model."""
        try:
            from pydantic import BaseModel
            from stateless_mcp.dispatcher import _execute_tool

            class MyResponse(BaseModel):
                message: str
                count: int

            async def pydantic_tool(params: dict) -> MyResponse:
                # Return a dict instead of model instance
                return {"message": "world", "count": 10}

            metadata = ToolMetadata(fn=pydantic_tool, name="pydantic_tool", timeout=30)
            result = await _execute_tool(metadata, {})

            # Dict should be validated and returned
            assert result["message"] == "world"
            assert result["count"] == 10

        except ImportError:
            pytest.skip("Pydantic not installed")

    @pytest.mark.asyncio
    async def test_pydantic_response_validation_invalid_dict(self):
        """Test that invalid dict fails Pydantic validation."""
        try:
            from pydantic import BaseModel
            from stateless_mcp.dispatcher import _execute_tool

            class MyResponse(BaseModel):
                message: str
                count: int

            async def bad_tool(params: dict) -> MyResponse:
                # Missing required field
                return {"message": "incomplete"}

            metadata = ToolMetadata(fn=bad_tool, name="bad_tool", timeout=30)

            with pytest.raises(ResponseValidationError, match="Response validation failed"):
                await _execute_tool(metadata, {})

        except ImportError:
            pytest.skip("Pydantic not installed")

    @pytest.mark.asyncio
    async def test_pydantic_response_wrong_type(self):
        """Test that wrong return type fails validation."""
        try:
            from pydantic import BaseModel
            from stateless_mcp.dispatcher import _execute_tool

            class MyResponse(BaseModel):
                value: int

            async def bad_tool(params: dict) -> MyResponse:
                return "wrong type"

            metadata = ToolMetadata(fn=bad_tool, name="bad_tool", timeout=30)

            with pytest.raises(ResponseValidationError, match="Expected MyResponse"):
                await _execute_tool(metadata, {})

        except ImportError:
            pytest.skip("Pydantic not installed")

    @pytest.mark.asyncio
    async def test_any_response_no_validation(self):
        """Test that ANY pattern doesn't validate response."""
        from stateless_mcp.dispatcher import _execute_tool

        async def any_tool(params: dict):  # No return type annotation
            return "can return anything"

        metadata = ToolMetadata(fn=any_tool, name="any_tool", timeout=30)
        result = await _execute_tool(metadata, {})

        # Should accept any return value
        assert result == "can return anything"
