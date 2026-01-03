"""Trace context propagation using context variables."""
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from functools import wraps
from typing import Callable, Dict, List, Optional, TypeVar

from ._internal.ids import generate_ulid

T = TypeVar("T")


@dataclass
class Span:
    """Represents a single span in a trace."""

    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    name: str
    metadata: Dict = field(default_factory=dict)

    def add_metadata(self, **kwargs) -> None:
        """Add metadata to the span."""
        self.metadata.update(kwargs)

    def set_tag(self, key: str, value: str) -> None:
        """Set a tag on the span."""
        self.metadata[key] = value


@dataclass
class TraceContext:
    """Context for a trace, including span stack and hash chain."""

    current_span: Optional[Span]
    span_stack: List[Span] = field(default_factory=list)
    hash_chain: List[str] = field(default_factory=list)  # Per-trace hash chain
    step_counter: int = 0
    event_counter: int = 0


# Thread-safe and async-safe context variable
_trace_context: ContextVar[Optional[TraceContext]] = ContextVar(
    "monora_trace_context", default=None
)


def get_current_context() -> Optional[TraceContext]:
    """Get the current trace context."""
    return _trace_context.get()


def get_current_span() -> Optional[Span]:
    """Get the current span from context."""
    ctx = get_current_context()
    return ctx.current_span if ctx else None


def push_span(span: Span) -> None:
    """Push a new span onto the stack."""
    ctx = get_current_context()
    if ctx is None:
        # Create new context
        ctx = TraceContext(current_span=span, span_stack=[span])
        _trace_context.set(ctx)
    else:
        # Add to existing context
        ctx.span_stack.append(span)
        ctx.current_span = span


def pop_span() -> Optional[Span]:
    """Pop the current span from the stack."""
    ctx = get_current_context()
    if ctx is None or not ctx.span_stack:
        return None

    span = ctx.span_stack.pop()

    # Update current span to parent or clear context if empty
    if ctx.span_stack:
        ctx.current_span = ctx.span_stack[-1]
    else:
        ctx.current_span = None
        _trace_context.set(None)

    return span


@contextmanager
def trace(
    name: str,
    *,
    trace_id: Optional[str] = None,
    metadata: Optional[Dict] = None,
):
    """Create a new trace context and yield the root span."""
    root_trace_id = trace_id or generate_ulid("trc")
    span = Span(
        trace_id=root_trace_id,
        span_id=generate_ulid("spn"),
        parent_span_id=None,
        name=name,
        metadata=metadata or {},
    )
    ctx = TraceContext(current_span=span, span_stack=[span], hash_chain=[], step_counter=0)
    token = _trace_context.set(ctx)
    try:
        yield span
    finally:
        _trace_context.reset(token)


def start_span(name: str, metadata: Optional[Dict] = None) -> Span:
    """Create and push a child span, returning it."""
    current = get_current_span()
    trace_id = current.trace_id if current else generate_ulid("trc")
    parent_span_id = current.span_id if current else None
    span = Span(
        trace_id=trace_id,
        span_id=generate_ulid("spn"),
        parent_span_id=parent_span_id,
        name=name,
        metadata=metadata or {},
    )
    push_span(span)
    return span


def next_step_number() -> int:
    """Increment and return the agent step counter for the current trace."""
    ctx = get_current_context()
    if ctx is None:
        return 1
    ctx.step_counter += 1
    return ctx.step_counter


def next_event_sequence() -> Optional[int]:
    """Increment and return the event sequence for the current trace."""
    ctx = get_current_context()
    if ctx is None:
        return None
    ctx.event_counter += 1
    return ctx.event_counter


def capture_context() -> Optional[TraceContext]:
    """Capture the current trace context for later use.

    This is useful for preserving context across async boundaries like
    threading, multiprocessing, or callback-based APIs.

    Returns:
        The current trace context, or None if no trace is active.

    Example:
        >>> with trace("my-workflow"):
        ...     ctx = capture_context()
        ...     # Pass ctx to another thread or callback
    """
    return _trace_context.get()


def run_in_context(ctx: Optional[TraceContext], fn: Callable[[], T]) -> T:
    """Run a function within a specific trace context.

    This allows executing code as if it were inside a particular trace,
    even when called from outside that trace's async context.

    Args:
        ctx: The trace context to run within (or None for no context).
        fn: The function to execute.

    Returns:
        The result of the function.

    Example:
        >>> with trace("my-workflow"):
        ...     ctx = capture_context()
        ...
        >>> def delayed_work():
        ...     span = get_current_span()  # Would be None without run_in_context
        ...     print(f"In span: {span.name if span else 'none'}")
        ...
        >>> run_in_context(ctx, delayed_work)
        In span: my-workflow
    """
    if ctx is None:
        return fn()
    token = _trace_context.set(ctx)
    try:
        return fn()
    finally:
        _trace_context.reset(token)


def bind_context(fn: Callable[..., T]) -> Callable[..., T]:
    """Bind a function to the current trace context.

    The returned function, when called, will execute within the captured
    trace context regardless of where it's called from. This is essential
    for preserving trace context through:
    - Thread pool executors
    - Callback-based APIs
    - asyncio.run_in_executor
    - Any other async scheduling mechanism

    Args:
        fn: The function to bind to the current context.

    Returns:
        A wrapped function that will execute in the captured context.

    Example:
        >>> with trace("my-workflow"):
        ...     bound_callback = bind_context(lambda: print(get_current_span().name))
        ...
        >>> # Call from anywhere - context is preserved
        >>> bound_callback()
        my-workflow
    """
    captured = capture_context()
    if captured is None:
        return fn

    @wraps(fn)
    def bound(*args, **kwargs):
        return run_in_context(captured, lambda: fn(*args, **kwargs))

    return bound
