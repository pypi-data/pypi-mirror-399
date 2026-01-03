"""FastAPI application for stateless MCP server with optional v2 features."""

import inspect
import uuid
from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .registry import get_registry
from .rpc import parse_request, serialize_response
from .dispatcher import dispatch_tool
from .streaming import stream_generator
from .models import JSONRPCErrorResponse

# Import example tools to register them
from .tools import example

# Initialize logging (structured if v2 features enabled, basic otherwise)
if settings.metrics_enabled or settings.auth_enabled or settings.rate_limit_enabled:
    # Use v2 structured logging
    from .logging import configure_logging, get_logger, set_request_id, mask_sensitive_data
    configure_logging(log_level=settings.log_level, log_format=settings.log_format)
    logger = get_logger(__name__)
else:
    # Use basic logging
    import logging
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

# Import v2 features if enabled
if settings.metrics_enabled:
    from .metrics import (
        MetricsContext, export_metrics, get_metrics_content_type,
        set_server_info, tools_registered
    )

if settings.auth_enabled:
    from .auth import APIKeyAuth, AuthContext

if settings.rate_limit_enabled:
    from .ratelimit import get_rate_limit_manager, parse_rate_limit, get_client_identifier

# Determine version
version = "2.0.0" if any([settings.metrics_enabled, settings.auth_enabled, settings.rate_limit_enabled]) else "1.0.0"

# Create FastAPI app
app = FastAPI(
    title="Stateless MCP Server",
    description="JSON-RPC 2.0 server with streaming support" + (" and observability features" if version == "2.0.0" else ""),
    version=version,
)

# Add CORS middleware if any v2 features enabled
if settings.metrics_enabled or settings.auth_enabled or settings.rate_limit_enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Initialize auth if enabled
api_key_auth = None
if settings.auth_enabled and settings.api_keys:
    api_key_auth = APIKeyAuth(settings.api_keys, settings.auth_header_name)
    if hasattr(logger, 'info') and callable(getattr(logger, 'info')):
        if version == "2.0.0":
            logger.info("API key authentication enabled", api_key_count=len(settings.api_keys))
        else:
            logger.info(f"API key authentication enabled with {len(settings.api_keys)} keys")


@app.on_event("startup")
async def startup_event():
    """Initialize server on startup."""
    registry = get_registry()
    registry.lock()

    tool_count = len(registry.list_tools())

    # Log startup with appropriate format
    if version == "2.0.0":
        logger.info(
            "Server starting",
            version=version,
            tools=tool_count,
            auth_enabled=settings.auth_enabled,
            metrics_enabled=settings.metrics_enabled,
            rate_limit_enabled=settings.rate_limit_enabled,
        )
    else:
        logger.info(f"Registry locked with {tool_count} tools")

    # Set server metrics if enabled
    if settings.metrics_enabled:
        tools_registered.set(tool_count)
        set_server_info(version=version, workers=settings.workers)

    # Setup rate limiting if enabled
    if settings.rate_limit_enabled:
        rate_manager = get_rate_limit_manager()
        max_req, window = parse_rate_limit(settings.default_rate_limit)
        rate_manager.add_limiter("global", max_req, window)
        if version == "2.0.0":
            logger.info("Rate limiting enabled", limit=settings.default_rate_limit)
        else:
            logger.info(f"Rate limiting enabled: {settings.default_rate_limit}")

    # Log registered tools
    for tool_name, metadata in registry.list_tools().items():
        if version == "2.0.0":
            logger.info(
                "Tool registered",
                tool=tool_name,
                streaming=metadata.streaming,
                timeout=metadata.timeout,
            )
        else:
            logger.info(f"  - {tool_name}: streaming={metadata.streaming}, timeout={metadata.timeout}s")


# Add request middleware if v2 features enabled
if settings.metrics_enabled or settings.auth_enabled or settings.rate_limit_enabled:
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        """Add request ID and logging context."""
        request_id = str(uuid.uuid4())
        set_request_id(request_id)

        logger.info(
            "Request received",
            method=request.method,
            path=request.url.path,
            client=get_client_identifier(request) if settings.rate_limit_enabled else (request.client.host if request.client else "unknown"),
        )

        response = await call_next(request)

        logger.info(
            "Request completed",
            status_code=response.status_code,
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        return response


@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """
    Main MCP endpoint for JSON-RPC 2.0 requests.

    Accepts POST requests with JSON-RPC 2.0 format.
    Returns either:
    - JSON response for non-streaming tools
    - Streaming response for streaming tools (chunks + final JSON-RPC response)

    Optional features (enabled via settings):
    - Structured logging
    - Metrics collection
    - Authentication
    - Rate limiting
    - Request tracing
    """
    auth = None

    # Apply authentication if enabled
    if settings.auth_enabled and api_key_auth:
        try:
            auth = await api_key_auth()
        except HTTPException as e:
            # Return auth error as JSON-RPC error
            from .errors import server_error
            error_response = server_error(
                request_id=None,
                message=e.detail,
                data={"error_type": "AuthenticationError"}
            )
            return JSONResponse(
                content=error_response.model_dump(exclude_none=False),
                status_code=e.status_code,
            )

    # Apply rate limiting if enabled
    if settings.rate_limit_enabled:
        try:
            client_id = get_client_identifier(request)
            rate_manager = get_rate_limit_manager()
            rate_manager.check_limit("global", client_id)
        except HTTPException as e:
            # Return rate limit headers
            return JSONResponse(
                content={"error": e.detail},
                status_code=e.status_code,
                headers=e.headers if hasattr(e, 'headers') and e.headers else {},
            )

    # Read raw body
    raw_body = await request.body()

    # Parse JSON-RPC request
    rpc_request, error_response = parse_request(raw_body)

    if error_response:
        if version == "2.0.0":
            logger.warning("Invalid JSON-RPC request", error=error_response.error.message)
        else:
            logger.error(f"Parsing error: {error_response.error.message}")
        return JSONResponse(
            content=error_response.model_dump(exclude_none=False),
            status_code=200,
        )

    tool_name = rpc_request.method

    if version == "2.0.0":
        logger.info(
            "Tool invocation",
            tool=tool_name,
            request_id=rpc_request.id,
            authenticated=auth.authenticated if auth else False,
        )
    else:
        logger.debug(f"Received request: method={tool_name}, id={rpc_request.id}")

    # Get tool metadata for metrics
    registry = get_registry()
    tool_metadata = registry.get(tool_name)
    is_streaming = tool_metadata.streaming if tool_metadata else False

    # Track metrics if enabled
    metrics_ctx = None
    if settings.metrics_enabled:
        metrics_ctx = MetricsContext(tool_name, is_streaming)
        metrics_ctx.__enter__()

    try:
        # Dispatch tool
        result = await dispatch_tool(rpc_request)

        # Handle different result types
        if isinstance(result, JSONRPCErrorResponse):
            if version == "2.0.0":
                logger.error(
                    "Tool execution failed",
                    tool=tool_name,
                    error_code=result.error.code,
                    error_message=result.error.message,
                )
            else:
                logger.error(f"Tool error: {result.error.message}")

            if metrics_ctx:
                metrics_ctx.__exit__(Exception, None, None)

            return JSONResponse(
                content=result.model_dump(exclude_none=False),
                status_code=200,
            )

        elif inspect.isasyncgen(result):
            # Streaming tool
            if version == "2.0.0":
                logger.debug("Starting stream", tool=tool_name)
            else:
                logger.debug(f"Starting stream for method={tool_name}")

            async def stream_wrapper():
                import json
                from .rpc import create_success_response
                from .errors import server_error

                last_chunk = None
                chunk_count = 0

                try:
                    async for chunk in result:
                        last_chunk = chunk
                        chunk_count += 1

                        # Track streaming metrics
                        if metrics_ctx:
                            metrics_ctx.add_streaming_chunk()

                        if isinstance(chunk, dict):
                            yield json.dumps(chunk) + "\n"
                        else:
                            yield json.dumps({"value": chunk}) + "\n"

                    if version == "2.0.0":
                        logger.info(
                            "Stream completed",
                            tool=tool_name,
                            chunks=chunk_count,
                        )

                    # Create final success response
                    final_result = last_chunk if last_chunk is not None else {}
                    final_response = create_success_response(
                        result=final_result,
                        request_id=rpc_request.id
                    )

                    # Mark success in metrics
                    if metrics_ctx:
                        metrics_ctx.mark_success()

                except Exception as e:
                    if version == "2.0.0":
                        logger.error(
                            "Streaming failed",
                            tool=tool_name,
                            error=str(e),
                            error_type=type(e).__name__,
                        )
                    else:
                        logger.error(f"Streaming error: {str(e)}")

                    final_response = server_error(
                        request_id=rpc_request.id,
                        message=f"Streaming failed: {str(e)}",
                        data={"error_type": type(e).__name__},
                    )

                # Always send final JSON-RPC response
                yield serialize_response(final_response) + "\n"

                # Exit metrics context
                if metrics_ctx:
                    metrics_ctx.__exit__(None, None, None)

            return StreamingResponse(
                stream_wrapper(),
                media_type="application/x-ndjson",
                headers={
                    "Cache-Control": "no-cache",
                    "X-Accel-Buffering": "no",
                },
            )

        else:
            # Non-streaming tool
            if version == "2.0.0":
                logger.info("Tool execution successful", tool=tool_name)
            else:
                logger.debug(f"Returning result for method={tool_name}")

            if metrics_ctx:
                metrics_ctx.mark_success()
                metrics_ctx.__exit__(None, None, None)

            return JSONResponse(
                content=result.model_dump(exclude_none=False),
                status_code=200,
            )

    except Exception as e:
        if version == "2.0.0":
            logger.error(
                "Unexpected error",
                tool=tool_name,
                error=str(e),
                error_type=type(e).__name__,
            )
        else:
            logger.error(f"Unexpected error: {str(e)}")

        if metrics_ctx:
            metrics_ctx.__exit__(type(e), e, None)

        raise


# Metrics endpoint (v2 only)
if settings.metrics_enabled:
    @app.get("/metrics")
    async def metrics_endpoint():
        """
        Prometheus metrics endpoint.

        Returns metrics in Prometheus text format.
        """
        return Response(
            content=export_metrics(),
            media_type=get_metrics_content_type(),
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    registry = get_registry()

    response = {
        "status": "healthy",
        "tools": len(registry.list_tools()),
        "locked": registry.is_locked(),
    }

    # Add v2 features info if enabled
    if version == "2.0.0":
        response["version"] = version
        response["features"] = {
            "auth": settings.auth_enabled,
            "metrics": settings.metrics_enabled,
            "rate_limiting": settings.rate_limit_enabled,
        }

    return response


# Kubernetes probes (v2 only)
if settings.metrics_enabled or settings.auth_enabled or settings.rate_limit_enabled:
    @app.get("/health/live")
    async def liveness_probe():
        """
        Kubernetes liveness probe.

        Returns 200 if process is alive.
        """
        return {"status": "alive"}

    @app.get("/health/ready")
    async def readiness_probe():
        """
        Kubernetes readiness probe.

        Returns 200 if server is ready to accept traffic.
        """
        registry = get_registry()
        if not registry.is_locked():
            raise HTTPException(status_code=503, detail="Registry not initialized")

        return {"status": "ready", "tools": len(registry.list_tools())}


@app.get("/tools")
async def list_tools():
    """List all registered tools."""
    registry = get_registry()
    tools = {}

    for name, metadata in registry.list_tools().items():
        tools[name] = {
            "name": metadata.name,
            "streaming": metadata.streaming,
            "timeout": metadata.timeout,
        }

    # Add count for v2
    if version == "2.0.0":
        return {"tools": tools, "count": len(tools)}
    else:
        return {"tools": tools}


# Tool info endpoint (v2 only)
if settings.metrics_enabled or settings.auth_enabled or settings.rate_limit_enabled:
    @app.get("/tools/{tool_name}")
    async def get_tool_info(tool_name: str):
        """
        Get detailed information about a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool metadata
        """
        registry = get_registry()
        metadata = registry.get(tool_name)

        if not metadata:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

        return {
            "name": metadata.name,
            "streaming": metadata.streaming,
            "timeout": metadata.timeout,
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "stateless_mcp.app:app",
        host=settings.host,
        port=settings.port,
        reload=False,  # Never use reload in production
        workers=1,  # Use 1 for development, multiple for production
    )
