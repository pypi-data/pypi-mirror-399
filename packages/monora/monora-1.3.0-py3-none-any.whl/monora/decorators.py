"""Decorators for Monora events."""
from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Optional

from ._execution import _execute_llm_call, _execute_tool_call, _execute_agent_step


def llm_call(
    *,
    model: Optional[str] = None,
    data_classification: Optional[str] = None,
    purpose: str,
    reason: Optional[str] = None,
    explain_fn: Optional[Callable[[dict], str]] = None,
):
    """Wrap an LLM API call with Monora governance.

    This decorator instruments LLM API calls with policy enforcement, data handling,
    and structured event logging.

    Args:
        model: Optional model identifier (can be extracted from function arguments)
        data_classification: Data classification level for the call
        purpose: Required purpose/intent of the call
        reason: Optional reason or justification
        explain_fn: Optional function to generate explanations from responses

    Returns:
        Decorated function that executes with Monora governance

    Example:
        @monora.llm_call(purpose="CUSTOMER_SUPPORT", data_classification="PUBLIC")
        def ask_gpt(prompt: str, model: str = "gpt-4o-mini"):
            return client.chat.completions.create(model=model, messages=[...])
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return _execute_llm_call(
                func,
                args,
                kwargs,
                model=model,
                data_classification=data_classification,
                purpose=purpose,
                reason=reason,
                explain_fn=explain_fn,
                func_name=func.__name__,
            )

        return wrapper

    return decorator


def tool_call(
    *,
    tool_name: str,
    data_classification: Optional[str] = None,
    purpose: str,
    reason: Optional[str] = None,
):
    """Wrap a tool execution with Monora governance.

    This decorator instruments tool/function calls with data handling and
    structured event logging.

    Args:
        tool_name: Name of the tool being called
        data_classification: Data classification level for the call
        purpose: Required purpose/intent of the call
        reason: Optional reason or justification

    Returns:
        Decorated function that executes with Monora governance

    Example:
        @monora.tool_call(tool_name="database_query", purpose="ANALYTICS")
        def query_db(sql: str):
            return execute_query(sql)
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return _execute_tool_call(
                func,
                args,
                kwargs,
                tool_name=tool_name,
                data_classification=data_classification,
                purpose=purpose,
                reason=reason,
            )

        return wrapper

    return decorator


def agent_step(
    *,
    agent_name: str,
    step_type: str,
    data_classification: Optional[str] = None,
    purpose: str,
):
    """Wrap a single agent reasoning step with Monora governance.

    This decorator instruments agent steps with data handling, step counting,
    and structured event logging.

    Args:
        agent_name: Name of the agent
        step_type: Type of step (e.g., "reasoning", "planning", "execution")
        data_classification: Data classification level for the step
        purpose: Required purpose/intent of the step

    Returns:
        Decorated function that executes with Monora governance

    Example:
        @monora.agent_step(agent_name="sales_agent", step_type="planning", purpose="SALES")
        def plan_next_action(context: dict):
            return generate_plan(context)
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return _execute_agent_step(
                func,
                args,
                kwargs,
                agent_name=agent_name,
                step_type=step_type,
                data_classification=data_classification,
                purpose=purpose,
            )

        return wrapper

    return decorator
