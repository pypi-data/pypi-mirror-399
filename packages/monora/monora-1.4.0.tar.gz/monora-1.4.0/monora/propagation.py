"""W3C Trace Context propagation for cross-service telemetry.

This module implements the W3C Trace Context specification
(https://www.w3.org/TR/trace-context/) for distributed tracing.

The trace context is propagated using two HTTP headers:
- traceparent: Required header containing trace-id, parent-id, and flags
- tracestate: Optional header for vendor-specific data
"""
from __future__ import annotations

import re
from contextlib import contextmanager
from typing import Dict, Optional, Tuple

from .context import get_current_span
from .tracing import trace as monora_trace

# W3C Trace Context header names
TRACEPARENT_HEADER = "traceparent"
TRACESTATE_HEADER = "tracestate"

# traceparent format: version-trace_id-parent_id-flags
# Example: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
TRACEPARENT_REGEX = re.compile(
    r"^([0-9a-f]{2})-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$"
)


class TraceContextData:
    """Represents extracted W3C Trace Context data."""

    def __init__(
        self,
        trace_id: str,
        parent_span_id: str,
        flags: str,
        monora_trace_id: Optional[str] = None,
        monora_span_id: Optional[str] = None,
    ):
        self.trace_id = trace_id
        self.parent_span_id = parent_span_id
        self.flags = flags
        self.monora_trace_id = monora_trace_id or trace_id
        self.monora_span_id = monora_span_id

    @property
    def sampled(self) -> bool:
        """Check if the trace is sampled (flag bit 0)."""
        return int(self.flags, 16) & 0x01 == 1


def inject_headers(headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Inject W3C Trace Context headers from current span.

    Args:
        headers: Optional existing headers dict to update.

    Returns:
        Headers dict with traceparent (and optionally tracestate).

    Example:
        >>> with trace("my-service"):
        ...     headers = inject_headers()
        ...     requests.get("http://other-service/api", headers=headers)
    """
    headers = dict(headers) if headers else {}

    span = get_current_span()
    if not span:
        return headers

    # Convert Monora IDs to W3C format
    trace_id = _monora_to_w3c_trace_id(span.trace_id)
    parent_id = _monora_to_w3c_span_id(span.span_id)

    # Version 00, sampled flag 01
    traceparent = f"00-{trace_id}-{parent_id}-01"
    headers[TRACEPARENT_HEADER] = traceparent

    # Add tracestate with Monora-specific data (use ; as internal delimiter)
    tracestate = f"monora=trace_id:{span.trace_id};span_id:{span.span_id}"
    headers[TRACESTATE_HEADER] = tracestate

    return headers


def extract_context(headers: Dict[str, str]) -> Optional[TraceContextData]:
    """Extract trace context from W3C headers.

    Args:
        headers: HTTP headers dict (case-insensitive lookup).

    Returns:
        TraceContextData if valid headers found, None otherwise.

    Example:
        >>> @app.route("/api/endpoint")
        ... def handle_request():
        ...     ctx = extract_context(dict(request.headers))
        ...     if ctx:
        ...         with trace("handle-request", trace_id=ctx.monora_trace_id):
        ...             # Continue trace from caller
        ...             process_request()
    """
    # Case-insensitive header lookup
    headers_lower = {k.lower(): v for k, v in headers.items()}

    traceparent = headers_lower.get(TRACEPARENT_HEADER)
    if not traceparent:
        return None

    match = TRACEPARENT_REGEX.match(traceparent)
    if not match:
        return None

    _, trace_id, parent_id, flags = match.groups()

    # Check for Monora-specific tracestate
    tracestate = headers_lower.get(TRACESTATE_HEADER, "")
    monora_state = _parse_tracestate(tracestate, "monora")

    monora_trace_id = None
    monora_span_id = None

    if monora_state:
        # Use ; as internal delimiter (avoiding comma which separates vendor entries)
        parts = monora_state.split(";")
        for part in parts:
            if part.startswith("trace_id:"):
                monora_trace_id = part.split(":", 1)[1]
            elif part.startswith("span_id:"):
                monora_span_id = part.split(":", 1)[1]

    return TraceContextData(
        trace_id=trace_id,
        parent_span_id=parent_id,
        flags=flags,
        monora_trace_id=monora_trace_id,
        monora_span_id=monora_span_id,
    )


@contextmanager
def continue_trace(headers: Dict[str, str], name: str):
    """Context manager to continue a trace from incoming headers.

    This extracts the trace context from headers and creates a new span
    that is linked to the caller's trace.

    Args:
        headers: HTTP headers dict.
        name: Name for the new span.

    Yields:
        The span object.

    Example:
        >>> @app.route("/api/endpoint")
        ... def handle_request():
        ...     with continue_trace(dict(request.headers), "handle-request"):
        ...         # This span is linked to caller's trace
        ...         process_request()
    """
    ctx = extract_context(headers)
    if ctx:
        trace_id = ctx.monora_trace_id or ctx.trace_id
        metadata = {"parent_span_id": ctx.parent_span_id}
        if ctx.monora_span_id:
            metadata["caller_span_id"] = ctx.monora_span_id

        with monora_trace(name, trace_id=trace_id, metadata=metadata) as span:
            yield span
    else:
        with monora_trace(name) as span:
            yield span


def _monora_to_w3c_trace_id(monora_id: str) -> str:
    """Convert Monora ULID trace_id to W3C 32-hex format.

    Monora uses ULIDs like 'trc_01ARZXQGK3NTPY8D3XQFG2H4Y5'.
    W3C requires 32 lowercase hex characters.
    ULIDs use Base32 encoding, so we hash to get valid hex.
    """
    import hashlib

    # Strip prefix
    raw = monora_id.replace("trc_", "").replace("spn_", "")
    # Hash to get valid hex representation
    hex_id = hashlib.sha256(raw.encode()).hexdigest()[:32]
    return hex_id


def _monora_to_w3c_span_id(monora_id: str) -> str:
    """Convert Monora ULID span_id to W3C 16-hex format.

    W3C requires 16 lowercase hex characters for span IDs.
    ULIDs use Base32 encoding, so we hash to get valid hex.
    """
    import hashlib

    raw = monora_id.replace("spn_", "").replace("trc_", "")
    # Hash to get valid hex representation
    hex_id = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return hex_id


def _parse_tracestate(tracestate: str, vendor: str) -> Optional[str]:
    """Extract vendor-specific value from tracestate header.

    tracestate format: vendor1=value1,vendor2=value2,...
    """
    for pair in tracestate.split(","):
        pair = pair.strip()
        if pair.startswith(f"{vendor}="):
            return pair[len(vendor) + 1:]
    return None


def make_traceparent(trace_id: str, span_id: str, sampled: bool = True) -> str:
    """Create a traceparent header value.

    Args:
        trace_id: 32-character hex trace ID.
        span_id: 16-character hex span ID.
        sampled: Whether the trace is sampled.

    Returns:
        W3C traceparent header value.
    """
    flags = "01" if sampled else "00"
    return f"00-{trace_id}-{span_id}-{flags}"


def make_tracestate(entries: Dict[str, str]) -> str:
    """Create a tracestate header value.

    Args:
        entries: Dict of vendor keys to values.

    Returns:
        W3C tracestate header value.
    """
    parts = [f"{key}={value}" for key, value in entries.items()]
    return ",".join(parts)
