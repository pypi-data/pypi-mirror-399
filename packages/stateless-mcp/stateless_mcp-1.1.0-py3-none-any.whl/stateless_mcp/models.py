"""JSON-RPC 2.0 request and response models."""

from typing import Any, Optional, Union, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict


class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 request model."""

    model_config = ConfigDict(extra="forbid")

    jsonrpc: Literal["2.0"] = "2.0"
    method: str
    params: Optional[dict] = None
    id: Union[str, int, None] = None


class JSONRPCError(BaseModel):
    """JSON-RPC 2.0 error object."""

    code: int
    message: str
    data: Optional[Any] = None


class JSONRPCResponse(BaseModel):
    """JSON-RPC 2.0 success response model."""

    model_config = ConfigDict(extra="forbid")

    jsonrpc: Literal["2.0"] = "2.0"
    result: Any
    id: Union[str, int, None]


class JSONRPCErrorResponse(BaseModel):
    """JSON-RPC 2.0 error response model."""

    model_config = ConfigDict(extra="forbid")

    jsonrpc: Literal["2.0"] = "2.0"
    error: JSONRPCError
    id: Union[str, int, None]


class StreamingChunk(BaseModel):
    """Model for streaming progress chunks (non-JSON-RPC)."""

    model_config = ConfigDict(extra="allow")

    type: str
    value: Any
