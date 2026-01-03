"""FastAPI middleware for Monora trace context propagation.

This middleware automatically extracts W3C Trace Context headers from
incoming requests and injects them into outgoing responses.

Usage:
    from fastapi import FastAPI
    from monora.middleware.fastapi import FastAPIMiddleware

    app = FastAPI()
    app.add_middleware(FastAPIMiddleware)
"""
from __future__ import annotations

from typing import Any, Callable, Optional, Set

from ..propagation import extract_context, inject_headers
from ..tracing import trace

try:
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    from starlette.responses import Response
    STARLETTE_AVAILABLE = True
except ImportError:
    STARLETTE_AVAILABLE = False
    BaseHTTPMiddleware = object  # type: ignore
    Request = Any  # type: ignore
    Response = Any  # type: ignore


class FastAPIMiddleware(BaseHTTPMiddleware):
    """ASGI middleware that propagates W3C Trace Context.

    This middleware wraps FastAPI/Starlette applications and:
    1. Extracts trace context from incoming request headers
    2. Creates a trace span for the request
    3. Injects trace context into response headers

    Args:
        app: The ASGI application to wrap.
        span_name_func: Optional function to customize span names.
            Takes (Request) and returns a string.
        skip_paths: Optional set of paths to skip (e.g., health checks).
    """

    def __init__(
        self,
        app: Any,
        span_name_func: Optional[Callable[[Any], str]] = None,
        skip_paths: Optional[Set[str]] = None,
    ):
        if not STARLETTE_AVAILABLE:
            raise ImportError(
                "FastAPI/Starlette not installed. "
                "Install with: pip install fastapi starlette"
            )
        super().__init__(app)
        self.span_name_func = span_name_func or self._default_span_name
        self.skip_paths = skip_paths or set()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request with trace context."""
        path = request.url.path

        # Skip specified paths
        if path in self.skip_paths:
            return await call_next(request)

        # Extract headers
        headers = dict(request.headers)

        # Get span name
        span_name = self.span_name_func(request)

        # Extract trace context
        ctx = extract_context(headers)

        # Create trace options
        trace_kwargs = {}
        if ctx:
            trace_kwargs["trace_id"] = ctx.monora_trace_id or ctx.trace_id
            trace_kwargs["metadata"] = {"parent_span_id": ctx.parent_span_id}
            if ctx.monora_span_id:
                trace_kwargs["metadata"]["caller_span_id"] = ctx.monora_span_id

        # Execute request within trace
        with trace(span_name, **trace_kwargs):
            response = await call_next(request)

            # Inject trace context into response headers
            injected = inject_headers()
            for key, value in injected.items():
                response.headers[key] = value

            return response

    def _default_span_name(self, request: Request) -> str:
        """Generate default span name from request."""
        return f"{request.method} {request.url.path}"


def create_fastapi_middleware(
    span_name_func: Optional[Callable[[Any], str]] = None,
    skip_paths: Optional[Set[str]] = None,
) -> type:
    """Create a configured FastAPI middleware class.

    This is useful when you need to pass configuration to the middleware.

    Args:
        span_name_func: Optional custom span name function.
        skip_paths: Optional set of paths to skip.

    Returns:
        Configured middleware class.

    Example:
        >>> from fastapi import FastAPI
        >>> from monora.middleware.fastapi import create_fastapi_middleware
        >>>
        >>> app = FastAPI()
        >>> MonoraMiddleware = create_fastapi_middleware(
        ...     skip_paths={"/health", "/ready"}
        ... )
        >>> app.add_middleware(MonoraMiddleware)
    """
    class ConfiguredMiddleware(FastAPIMiddleware):
        def __init__(self, app: Any):
            super().__init__(app, span_name_func, skip_paths)

    return ConfiguredMiddleware
