"""Public API helpers."""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from ._execution import _execute_llm_call, _execute_tool_call, _execute_agent_step
from .trust_package import export_trust_package
from .runtime import emit_event, ensure_state


def log_event(
    event_type: str,
    data: Optional[Dict[str, Any]] = None,
    *,
    data_classification: Optional[str] = None,
    purpose: Optional[str] = None,
    reason: Optional[str] = None,
    **fields: Any,
) -> None:
    """Log a custom event.

    When both ``data`` and ``fields`` are provided, their keys must not overlap;
    overlapping keys raise a ``ValueError`` listing the conflicts.
    """
    if data is None:
        data = dict(fields)
    elif fields:
        if not isinstance(data, dict):
            raise TypeError("log_event data must be a dict when combining with fields")
        intersection = set(data.keys()) & set(fields.keys())
        if intersection:
            raise ValueError(
                "log_event data and fields keys conflict: "
                + ", ".join(sorted(intersection))
            )
        merged = dict(data)
        merged.update(fields)
        data = merged
    state = ensure_state()
    event = state.event_builder.build(
        event_type,
        data,
        data_classification=data_classification,
        purpose=purpose,
        reason=reason,
    )
    emit_event(event)


def call_llm(
    call_fn: Callable[..., Any],
    *,
    model: Optional[str] = None,
    data_classification: Optional[str] = None,
    purpose: str,
    reason: Optional[str] = None,
    explain_fn: Optional[Callable[[dict], str]] = None,
    **call_kwargs: Any
) -> Any:
    """Execute an LLM API call with Monora governance (direct callable).

    This function provides a direct, non-decorator way to instrument LLM calls.
    It wraps the execution with policy enforcement, data handling, and event logging.

    Args:
        call_fn: The function to execute (e.g., client.chat.completions.create)
        model: Optional model identifier (extracted from call_kwargs if not provided)
        data_classification: Data classification level for the call
        purpose: Required purpose/intent of the call
        reason: Optional reason or justification
        explain_fn: Optional function to generate explanations from responses
        **call_kwargs: All other arguments passed directly to call_fn

    Returns:
        The result from call_fn

    Example:
        from openai import OpenAI
        client = OpenAI()

        response = monora.call_llm(
            client.chat.completions.create,
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            purpose="CUSTOMER_SUPPORT",
            data_classification="PUBLIC"
        )
    """
    return _execute_llm_call(
        call_fn,
        (),  # No positional args
        call_kwargs,
        model=model,
        data_classification=data_classification,
        purpose=purpose,
        reason=reason,
        explain_fn=explain_fn,
        func_name=getattr(call_fn, "__name__", "direct_call"),
    )


def call_tool(
    call_fn: Callable[..., Any],
    *,
    tool_name: str,
    data_classification: Optional[str] = None,
    purpose: str,
    reason: Optional[str] = None,
    **call_kwargs: Any
) -> Any:
    """Execute a tool call with Monora governance (direct callable).

    This function provides a direct, non-decorator way to instrument tool calls.
    It wraps the execution with data handling and event logging.

    Args:
        call_fn: The function to execute
        tool_name: Name of the tool being called
        data_classification: Data classification level for the call
        purpose: Required purpose/intent of the call
        reason: Optional reason or justification
        **call_kwargs: All other arguments passed directly to call_fn

    Returns:
        The result from call_fn

    Example:
        result = monora.call_tool(
            fetch_from_database,
            tool_name="customer_lookup",
            customer_id="123",
            purpose="CUSTOMER_SUPPORT"
        )
    """
    return _execute_tool_call(
        call_fn,
        (),  # No positional args
        call_kwargs,
        tool_name=tool_name,
        data_classification=data_classification,
        purpose=purpose,
        reason=reason,
    )


def call_agent(
    call_fn: Callable[..., Any],
    *,
    agent_name: str,
    step_type: str,
    data_classification: Optional[str] = None,
    purpose: str,
    **call_kwargs: Any
) -> Any:
    """Execute an agent step with Monora governance (direct callable).

    This function provides a direct, non-decorator way to instrument agent steps.
    It wraps the execution with data handling, step counting, and event logging.

    Args:
        call_fn: The function to execute
        agent_name: Name of the agent
        step_type: Type of step (e.g., "reasoning", "planning", "execution")
        data_classification: Data classification level for the step
        purpose: Required purpose/intent of the step
        **call_kwargs: All other arguments passed directly to call_fn

    Returns:
        The result from call_fn

    Example:
        thought = monora.call_agent(
            reasoning_function,
            agent_name="sales_agent",
            step_type="planning",
            context={"customer": "Acme Corp"},
            purpose="SALES_AUTOMATION"
        )
    """
    return _execute_agent_step(
        call_fn,
        (),  # No positional args
        call_kwargs,
        agent_name=agent_name,
        step_type=step_type,
        data_classification=data_classification,
        purpose=purpose,
    )
