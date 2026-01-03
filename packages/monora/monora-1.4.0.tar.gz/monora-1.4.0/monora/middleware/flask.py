"""Flask middleware for Monora trace context propagation.

This middleware automatically extracts W3C Trace Context headers from
incoming requests and injects them into outgoing responses.

Usage:
    from flask import Flask
    from monora.middleware.flask import FlaskMiddleware

    app = Flask(__name__)
    app.wsgi_app = FlaskMiddleware(app.wsgi_app)
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, Optional, Tuple

from ..propagation import continue_trace, extract_context, inject_headers


class FlaskMiddleware:
    """WSGI middleware that propagates W3C Trace Context.

    This middleware wraps a WSGI application and:
    1. Extracts trace context from incoming request headers
    2. Creates a trace span for the request
    3. Injects trace context into response headers

    Args:
        app: The WSGI application to wrap.
        span_name_func: Optional function to customize span names.
            Takes (environ) and returns a string.
        skip_paths: Optional list of paths to skip (e.g., health checks).
    """

    def __init__(
        self,
        app: Any,
        span_name_func: Optional[Callable[[Dict[str, Any]], str]] = None,
        skip_paths: Optional[list[str]] = None,
    ):
        self.app = app
        self.span_name_func = span_name_func or self._default_span_name
        self.skip_paths = set(skip_paths or [])

    def __call__(
        self,
        environ: Dict[str, Any],
        start_response: Callable[..., Any],
    ) -> Iterable[bytes]:
        """WSGI entry point."""
        path = environ.get("PATH_INFO", "/")

        # Skip specified paths
        if path in self.skip_paths:
            return self.app(environ, start_response)

        # Extract headers from WSGI environ
        headers = self._extract_headers(environ)

        # Get span name
        span_name = self.span_name_func(environ)

        # Capture response headers for modification
        response_headers: list[Tuple[str, str]] = []
        response_started = False

        def traced_start_response(
            status: str,
            headers_list: list[Tuple[str, str]],
            exc_info: Any = None,
        ) -> Callable[..., Any]:
            nonlocal response_started, response_headers
            response_started = True
            response_headers = list(headers_list)

            # Inject trace context into response headers
            injected = inject_headers()
            for key, value in injected.items():
                response_headers.append((key, value))

            return start_response(status, response_headers, exc_info)

        # Continue or start trace
        with continue_trace(headers, span_name):
            return self.app(environ, traced_start_response)

    def _extract_headers(self, environ: Dict[str, Any]) -> Dict[str, str]:
        """Extract HTTP headers from WSGI environ."""
        headers: Dict[str, str] = {}
        for key, value in environ.items():
            if key.startswith("HTTP_"):
                # Convert HTTP_HEADER_NAME to header-name
                header_name = key[5:].replace("_", "-").lower()
                headers[header_name] = value
        return headers

    def _default_span_name(self, environ: Dict[str, Any]) -> str:
        """Generate default span name from request."""
        method = environ.get("REQUEST_METHOD", "GET")
        path = environ.get("PATH_INFO", "/")
        return f"{method} {path}"


def create_flask_middleware(
    app: Any,
    span_name_func: Optional[Callable[[Dict[str, Any]], str]] = None,
    skip_paths: Optional[list[str]] = None,
) -> FlaskMiddleware:
    """Create a Flask middleware instance.

    This is a convenience function for creating the middleware.

    Args:
        app: The Flask/WSGI application.
        span_name_func: Optional custom span name function.
        skip_paths: Optional list of paths to skip.

    Returns:
        Configured FlaskMiddleware instance.

    Example:
        >>> from flask import Flask
        >>> from monora.middleware.flask import create_flask_middleware
        >>>
        >>> app = Flask(__name__)
        >>> app.wsgi_app = create_flask_middleware(
        ...     app.wsgi_app,
        ...     skip_paths=["/health", "/ready"]
        ... )
    """
    return FlaskMiddleware(app, span_name_func, skip_paths)
