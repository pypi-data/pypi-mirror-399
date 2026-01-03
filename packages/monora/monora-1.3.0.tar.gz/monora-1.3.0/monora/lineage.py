"""Causal lineage tracking utilities.

This module provides context-based tracking for event lineage, enabling
automatic capture of parent events and input events in the trace graph.
"""
from __future__ import annotations

import functools
from contextvars import ContextVar
from typing import Callable, List, Optional, TypeVar

# Track current event ID within a span for parent_event_id linkage
_current_event_id: ContextVar[Optional[str]] = ContextVar(
    "monora_current_event_id", default=None
)

# Track input event IDs for the next emitted event
_input_events: ContextVar[List[str]] = ContextVar(
    "monora_input_events", default=[]
)

# Track prompt and template IDs for provenance
_prompt_id: ContextVar[Optional[str]] = ContextVar(
    "monora_prompt_id", default=None
)
_template_id: ContextVar[Optional[str]] = ContextVar(
    "monora_template_id", default=None
)

# Track data source IDs for data lineage
_data_source_ids: ContextVar[List[str]] = ContextVar(
    "monora_data_source_ids", default=[]
)


def set_current_event(event_id: str) -> None:
    """Set the current event ID for lineage tracking.

    This is automatically called when an event is emitted, linking
    subsequent events to their parent.

    Args:
        event_id: The ID of the event that was just emitted.
    """
    _current_event_id.set(event_id)


def get_parent_event_id() -> Optional[str]:
    """Get the parent event ID for a new event.

    Returns:
        The event_id of the most recently emitted event in this context,
        or None if this is the first event in the trace.
    """
    return _current_event_id.get()


def add_input_event(event_id: str) -> None:
    """Add an event ID to the input list for the next event.

    Use this to track data dependencies between events, such as when
    a tool result feeds into an LLM call.

    Args:
        event_id: The ID of an event that provides input data.

    Example:
        >>> rag_result = retrieve_documents(query)
        >>> add_input_event(rag_result.event_id)
        >>> llm_response = call_llm(prompt_with_rag_context)
        # llm_response event will have rag_result.event_id in input_event_ids
    """
    current = list(_input_events.get())
    current.append(event_id)
    _input_events.set(current)


def get_input_events() -> List[str]:
    """Get and clear input events for a new event.

    Returns:
        List of event_ids that provide input to the next event.
        The list is cleared after retrieval.
    """
    events = list(_input_events.get())
    _input_events.set([])
    return events


def set_prompt_id(prompt_id: Optional[str]) -> None:
    """Set the prompt ID for provenance tracking.

    Args:
        prompt_id: Identifier for the prompt template or version.
    """
    _prompt_id.set(prompt_id)


def get_prompt_id() -> Optional[str]:
    """Get the current prompt ID.

    Returns:
        The prompt ID if set, None otherwise.
    """
    return _prompt_id.get()


def set_template_id(template_id: Optional[str]) -> None:
    """Set the template ID for provenance tracking.

    Args:
        template_id: Identifier for the template used.
    """
    _template_id.set(template_id)


def get_template_id() -> Optional[str]:
    """Get the current template ID.

    Returns:
        The template ID if set, None otherwise.
    """
    return _template_id.get()


def add_data_source(source_id: str) -> None:
    """Add a data source ID for data lineage tracking.

    Use this to track which data sources (databases, APIs, files)
    contributed to an LLM call.

    Args:
        source_id: Identifier for the data source.

    Example:
        >>> add_data_source("db://users")
        >>> add_data_source("api://weather")
        >>> response = call_llm(query_with_external_data)
        # response event will have both sources in data_source_ids
    """
    current = list(_data_source_ids.get())
    current.append(source_id)
    _data_source_ids.set(current)


def get_data_sources() -> List[str]:
    """Get and clear data source IDs for a new event.

    Returns:
        List of data source identifiers.
        The list is cleared after retrieval.
    """
    sources = list(_data_source_ids.get())
    _data_source_ids.set([])
    return sources


def clear_lineage_context() -> None:
    """Clear all lineage tracking state.

    Useful for testing or when starting a completely new trace context.
    """
    _current_event_id.set(None)
    _input_events.set([])
    _prompt_id.set(None)
    _template_id.set(None)
    _data_source_ids.set([])


T = TypeVar("T")


def with_inputs(*event_ids: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to specify input events for a function's output.

    The decorated function's resulting event will include the specified
    event IDs in its input_event_ids field.

    Args:
        *event_ids: Event IDs that provide input to this function.

    Returns:
        Decorator function.

    Example:
        >>> @with_inputs(rag_event.event_id, context_event.event_id)
        ... def process_with_context(query):
        ...     return call_llm(query)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for eid in event_ids:
                add_input_event(eid)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def with_data_sources(*source_ids: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to specify data sources for a function.

    The decorated function's resulting event will include the specified
    source IDs in its data_source_ids field.

    Args:
        *source_ids: Data source identifiers.

    Returns:
        Decorator function.

    Example:
        >>> @with_data_sources("db://users", "cache://session")
        ... def query_user_data(user_id):
        ...     return fetch_and_process(user_id)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for sid in source_ids:
                add_data_source(sid)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def with_prompt(
    prompt_id: Optional[str] = None,
    template_id: Optional[str] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to specify prompt/template IDs for a function.

    Args:
        prompt_id: Identifier for the prompt.
        template_id: Identifier for the template.

    Returns:
        Decorator function.

    Example:
        >>> @with_prompt(prompt_id="qa-v2", template_id="tpl_customer_support")
        ... def answer_question(question):
        ...     return call_llm(format_prompt(question))
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if prompt_id:
                set_prompt_id(prompt_id)
            if template_id:
                set_template_id(template_id)
            return func(*args, **kwargs)
        return wrapper
    return decorator
