"""Public trace API with span events."""
from __future__ import annotations

import dataclasses
import sys
import time
from contextlib import contextmanager
from typing import Any, Dict, Optional

from ._internal.ids import generate_ulid
from .context import Span, TraceContext, get_current_span, pop_span, push_span, _trace_context
from .reporting import TRUST_SUMMARY_EVENT_TYPE
from .runtime import emit_event, ensure_state


@contextmanager
def trace(
    name: Optional[str] = None,
    *,
    trace_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    **metadata_fields: Any,
):
    """Create a trace/span context and emit span start/end events."""
    span_name = name or "trace"
    merged_metadata = _merge_metadata(metadata, metadata_fields)
    span_metadata = _safe_serialize(merged_metadata)

    current = get_current_span()
    token = None
    if current is None or trace_id:
        root_trace_id = trace_id or generate_ulid("trc")
        span = Span(
            trace_id=root_trace_id,
            span_id=generate_ulid("spn"),
            parent_span_id=None,
            name=span_name,
            metadata=span_metadata,
        )
        ctx = TraceContext(
            current_span=span,
            span_stack=[span],
            hash_chain=[],
            step_counter=0,
            event_counter=0,
        )
        token = _trace_context.set(ctx)
        is_root = True
    else:
        span = Span(
            trace_id=current.trace_id,
            span_id=generate_ulid("spn"),
            parent_span_id=current.span_id,
            name=span_name,
            metadata=span_metadata,
        )
        push_span(span)
        is_root = False

    start_time = time.perf_counter()
    try:
        _emit_span_event("span_start", span, metadata=span_metadata)
        yield span
    finally:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        _emit_span_event("span_end", span, metadata=span_metadata, duration_ms=duration_ms)
        if is_root:
            _emit_trust_summary(span.trace_id)
            _trace_context.reset(token)
        else:
            pop_span()


def _emit_span_event(
    event_type: str,
    span: Span,
    *,
    metadata: Dict[str, Any],
    duration_ms: Optional[float] = None,
) -> None:
    state = ensure_state()
    if not state.config.get("tracing", {}).get("emit_span_events", True):
        return
    body = {"name": span.name, "metadata": metadata}
    if duration_ms is not None:
        body["duration_ms"] = duration_ms
    event = state.event_builder.build(event_type, body)
    emit_event(event)


def _merge_metadata(
    metadata: Optional[Dict[str, Any]],
    extra: Dict[str, Any],
) -> Dict[str, Any]:
    if metadata is None and not extra:
        return {}
    if metadata is not None and not isinstance(metadata, dict):
        raise TypeError("trace metadata must be a dict when provided")
    merged: Dict[str, Any] = dict(metadata or {})
    merged.update(extra)
    return merged


def _emit_trust_summary(trace_id: str) -> None:
    state = ensure_state()
    manager = getattr(state, "report_manager", None)
    if not manager or not manager.enabled:
        return
    try:
        summary = manager.finalize_trace(trace_id)
    except Exception as exc:
        print(f"Monora: trust report generation failed: {exc}", file=sys.stderr)
        return
    if not summary or not manager.emit_trust_summary:
        return
    event = state.event_builder.build(TRUST_SUMMARY_EVENT_TYPE, summary, purpose="compliance")
    emit_event(event)


def _safe_serialize(obj: Any) -> Any:
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {str(k): _safe_serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_safe_serialize(item) for item in obj]
    if dataclasses.is_dataclass(obj):
        return _safe_serialize(dataclasses.asdict(obj))
    for attr in ("model_dump", "dict", "to_dict"):
        if hasattr(obj, attr):
            try:
                return _safe_serialize(getattr(obj, attr)())
            except Exception:
                continue
    if hasattr(obj, "__dict__"):
        return _safe_serialize(vars(obj))
    return repr(obj)
