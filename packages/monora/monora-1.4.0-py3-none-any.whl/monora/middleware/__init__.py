"""Middleware integrations for popular web frameworks."""
from __future__ import annotations

# Note: Each middleware is imported lazily to avoid requiring
# framework dependencies if not used.

__all__ = [
    "FlaskMiddleware",
    "FastAPIMiddleware",
]


def __getattr__(name: str):
    """Lazy import of middleware classes."""
    if name == "FlaskMiddleware":
        from .flask import FlaskMiddleware
        return FlaskMiddleware
    if name == "FastAPIMiddleware":
        from .fastapi import FastAPIMiddleware
        return FastAPIMiddleware
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
