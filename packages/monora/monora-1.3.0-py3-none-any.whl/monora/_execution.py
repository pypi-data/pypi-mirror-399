"""Shared execution logic for LLM, tool, and agent calls.

This module contains the core execution logic used by both decorators and direct callables.
"""
from __future__ import annotations

import asyncio
import dataclasses
import inspect
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

from .context import next_step_number, pop_span, start_span
from .data_handling import DataHandlingViolation, build_data_violation
from .events import EventBuilder
from .policy import PolicyViolation
from .registry import ModelRegistry
from .runtime import emit_event, ensure_state, notify_violation


def _execute_llm_call(
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: Dict[str, Any],
    *,
    model: Optional[str] = None,
    data_classification: Optional[str] = None,
    purpose: str,
    reason: Optional[str] = None,
    explain_fn: Optional[Callable[[dict], str]] = None,
    context: Any = None,
    func_name: Optional[str] = None,
) -> Any:
    """Execute an LLM call with full Monora governance.

    Args:
        func: The function to execute
        args: Positional arguments for func
        kwargs: Keyword arguments for func
        model: Model identifier (optional, can be extracted from kwargs)
        data_classification: Data classification level
        purpose: Purpose of the call
        reason: Optional reason/justification
        explain_fn: Optional function to explain the response
        context: Optional context object (for method binding)
        func_name: Optional function name for span naming

    Returns:
        The result from func
    """
    # Check if function is async
    if inspect.iscoroutinefunction(func):
        return _execute_llm_call_async(
            func, args, kwargs,
            model=model,
            data_classification=data_classification,
            purpose=purpose,
            reason=reason,
            explain_fn=explain_fn,
            context=context,
            func_name=func_name,
        )

    state = ensure_state()
    span_name = func_name or getattr(func, "__name__", "unknown")
    start_span(f"llm_call:{span_name}")
    builder: EventBuilder = state.event_builder
    data_class = data_classification
    effective_class = data_class or state.config["defaults"]["data_classification"]
    bound = _bind_arguments(func, args, kwargs)
    resolved_model = model or bound.get("model")
    registry = state.registry
    provider = registry.default_provider if registry else "unknown"
    matched_provider = False
    provider_entry = None
    registry_override_event_id = None
    registry_status = "unknown"
    registry_override_event_id = None
    registry_status = "unknown"

    if registry and resolved_model:
        provider, matched_provider, provider_entry = registry.resolve_entry(resolved_model)
        registry_status = "known" if matched_provider else "unknown"
        if not matched_provider and not registry.allow_unknown:
            registry_violation = PolicyViolation(
                event_type="llm_call",
                model=resolved_model,
                policy_name="model_registry.unknown_model",
                message=f"Model '{resolved_model}' not found in registry",
                timestamp=datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            )
            _emit_policy_violation(builder, registry_violation, data_class, purpose, reason)
            notify_violation(registry_violation)
        elif not matched_provider and registry.allow_unknown:
            registry_override_event_id = _emit_registry_override(
                builder,
                registry,
                resolved_model,
                data_class,
                purpose,
                reason,
            )

    violation = None
    if resolved_model:
        try:
            violation = state.policy_engine.check_model(
                resolved_model,
                data_class or state.config["defaults"]["data_classification"],
            )
        except PolicyViolation as exc:
            _emit_policy_violation(builder, exc, data_class, purpose, reason)
            notify_violation(exc)
            pop_span()
            raise
    if violation:
        _emit_policy_violation(builder, violation, data_class, purpose, reason)
        notify_violation(violation)
        # Note: if enforce=True, check_model() would have raised, not returned.
        # So a returned violation means enforce=False (warn mode) - continue execution.

    provider_metadata = None
    if registry:
        metadata = {
            "registry_version": registry.version,
            "registry_hash": registry.registry_hash,
            "registry_status": registry_status,
        }
        if registry_override_event_id:
            metadata["registry_override_event_id"] = registry_override_event_id
        if provider_entry:
            if provider_entry.version_range:
                metadata["version_range"] = provider_entry.version_range
            if provider_entry.deprecated:
                metadata["deprecated"] = True
            if provider_entry.deprecation_message:
                metadata["deprecation_message"] = provider_entry.deprecation_message
        provider_metadata = metadata

    if state.data_handler and state.data_handler.should_block():
        matches = state.data_handler.inspect("request", bound, effective_class)
        if matches:
            violation = build_data_violation(
                event_type="llm_call",
                classification=effective_class,
                rule_names=matches,
                model=resolved_model,
            )
            redacted_request, applied = state.data_handler.sanitize_payload(
                "request", bound, effective_class
            )
            body = _build_llm_body(
                resolved_model,
                redacted_request,
                provider=provider,
                provider_metadata=provider_metadata,
                response=None,
                duration_ms=0.0,
                status="policy_violation",
                error=None,
                explain_fn=None,
            )
            body["data_handling"] = {
                "action": "block",
                "rules": sorted(matches),
                "target": "request",
            }
            if applied:
                body["redaction"] = {
                    "applied": True,
                    "rules": sorted(applied),
                    "mode": state.data_handler.mode,
                }
            event = builder.build(
                "llm_call",
                body,
                data_classification=data_class,
                purpose=purpose,
                reason=reason,
            )
            emit_event(event)
            notify_violation(violation)
            pop_span()
            raise violation

    start_time = time.perf_counter()
    try:
        if context is not None:
            response = func(context, *args, **kwargs)
        else:
            response = func(*args, **kwargs)
    except DataHandlingViolation:
        pop_span()
        raise
    except PolicyViolation as exc:
        pop_span()
        raise
    except Exception as exc:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        log_errors = state.config.get("error_handling", {}).get(
            "log_user_exceptions", True
        )
        body = _build_llm_body(
            resolved_model,
            bound,
            provider=provider,
            provider_metadata=provider_metadata,
            response=None,
            duration_ms=duration_ms,
            status="error",
            error=exc if log_errors else None,
            explain_fn=explain_fn,
        )
        event = builder.build(
            "llm_call",
            body,
            data_classification=data_class,
            purpose=purpose,
            reason=reason,
        )
        emit_event(event)
        pop_span()
        raise

    duration_ms = (time.perf_counter() - start_time) * 1000.0
    body = _build_llm_body(
        resolved_model,
        bound,
        provider=provider,
        provider_metadata=provider_metadata,
        response=response,
        duration_ms=duration_ms,
        status="success",
        error=None,
        explain_fn=explain_fn,
    )
    event = builder.build(
        "llm_call",
        body,
        data_classification=data_class,
        purpose=purpose,
        reason=reason,
    )
    emit_event(event)
    pop_span()
    return response


async def _execute_llm_call_async(
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: Dict[str, Any],
    *,
    model: Optional[str] = None,
    data_classification: Optional[str] = None,
    purpose: str,
    reason: Optional[str] = None,
    explain_fn: Optional[Callable[[dict], str]] = None,
    context: Any = None,
    func_name: Optional[str] = None,
) -> Any:
    """Async version of _execute_llm_call."""
    state = ensure_state()
    span_name = func_name or getattr(func, "__name__", "unknown")
    start_span(f"llm_call:{span_name}")
    builder: EventBuilder = state.event_builder
    data_class = data_classification
    effective_class = data_class or state.config["defaults"]["data_classification"]
    bound = _bind_arguments(func, args, kwargs)
    resolved_model = model or bound.get("model")
    registry = state.registry
    provider = registry.default_provider if registry else "unknown"
    matched_provider = False
    provider_entry = None

    if registry and resolved_model:
        provider, matched_provider, provider_entry = registry.resolve_entry(resolved_model)
        registry_status = "known" if matched_provider else "unknown"
        if not matched_provider and not registry.allow_unknown:
            registry_violation = PolicyViolation(
                event_type="llm_call",
                model=resolved_model,
                policy_name="model_registry.unknown_model",
                message=f"Model '{resolved_model}' not found in registry",
                timestamp=datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            )
            _emit_policy_violation(builder, registry_violation, data_class, purpose, reason)
            notify_violation(registry_violation)
        elif not matched_provider and registry.allow_unknown:
            registry_override_event_id = _emit_registry_override(
                builder,
                registry,
                resolved_model,
                data_class,
                purpose,
                reason,
            )

    violation = None
    if resolved_model:
        try:
            violation = state.policy_engine.check_model(
                resolved_model,
                data_class or state.config["defaults"]["data_classification"],
            )
        except PolicyViolation as exc:
            _emit_policy_violation(builder, exc, data_class, purpose, reason)
            notify_violation(exc)
            pop_span()
            raise
    if violation:
        _emit_policy_violation(builder, violation, data_class, purpose, reason)
        notify_violation(violation)
        # Note: if enforce=True, check_model() would have raised, not returned.
        # So a returned violation means enforce=False (warn mode) - continue execution.

    provider_metadata = None
    if registry:
        metadata = {
            "registry_version": registry.version,
            "registry_hash": registry.registry_hash,
            "registry_status": registry_status,
        }
        if registry_override_event_id:
            metadata["registry_override_event_id"] = registry_override_event_id
        if provider_entry:
            if provider_entry.version_range:
                metadata["version_range"] = provider_entry.version_range
            if provider_entry.deprecated:
                metadata["deprecated"] = True
            if provider_entry.deprecation_message:
                metadata["deprecation_message"] = provider_entry.deprecation_message
        provider_metadata = metadata

    if state.data_handler and state.data_handler.should_block():
        matches = state.data_handler.inspect("request", bound, effective_class)
        if matches:
            violation = build_data_violation(
                event_type="llm_call",
                classification=effective_class,
                rule_names=matches,
                model=resolved_model,
            )
            redacted_request, applied = state.data_handler.sanitize_payload(
                "request", bound, effective_class
            )
            body = _build_llm_body(
                resolved_model,
                redacted_request,
                provider=provider,
                provider_metadata=provider_metadata,
                response=None,
                duration_ms=0.0,
                status="policy_violation",
                error=None,
                explain_fn=None,
            )
            body["data_handling"] = {
                "action": "block",
                "rules": sorted(matches),
                "target": "request",
            }
            if applied:
                body["redaction"] = {
                    "applied": True,
                    "rules": sorted(applied),
                    "mode": state.data_handler.mode,
                }
            event = builder.build(
                "llm_call",
                body,
                data_classification=data_class,
                purpose=purpose,
                reason=reason,
            )
            emit_event(event)
            notify_violation(violation)
            pop_span()
            raise violation

    start_time = time.perf_counter()
    try:
        if context is not None:
            response = await func(context, *args, **kwargs)
        else:
            response = await func(*args, **kwargs)
    except DataHandlingViolation:
        pop_span()
        raise
    except PolicyViolation as exc:
        pop_span()
        raise
    except Exception as exc:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        log_errors = state.config.get("error_handling", {}).get(
            "log_user_exceptions", True
        )
        body = _build_llm_body(
            resolved_model,
            bound,
            provider=provider,
            provider_metadata=provider_metadata,
            response=None,
            duration_ms=duration_ms,
            status="error",
            error=exc if log_errors else None,
            explain_fn=explain_fn,
        )
        event = builder.build(
            "llm_call",
            body,
            data_classification=data_class,
            purpose=purpose,
            reason=reason,
        )
        emit_event(event)
        pop_span()
        raise

    duration_ms = (time.perf_counter() - start_time) * 1000.0
    body = _build_llm_body(
        resolved_model,
        bound,
        provider=provider,
        provider_metadata=provider_metadata,
        response=response,
        duration_ms=duration_ms,
        status="success",
        error=None,
        explain_fn=explain_fn,
    )
    event = builder.build(
        "llm_call",
        body,
        data_classification=data_class,
        purpose=purpose,
        reason=reason,
    )
    emit_event(event)
    pop_span()
    return response


def _execute_tool_call(
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: Dict[str, Any],
    *,
    tool_name: str,
    data_classification: Optional[str] = None,
    purpose: str,
    reason: Optional[str] = None,
    context: Any = None,
) -> Any:
    """Execute a tool call with full Monora governance.

    Args:
        func: The function to execute
        args: Positional arguments for func
        kwargs: Keyword arguments for func
        tool_name: Name of the tool
        data_classification: Data classification level
        purpose: Purpose of the call
        reason: Optional reason/justification
        context: Optional context object (for method binding)

    Returns:
        The result from func
    """
    # Check if function is async
    if inspect.iscoroutinefunction(func):
        return _execute_tool_call_async(
            func, args, kwargs,
            tool_name=tool_name,
            data_classification=data_classification,
            purpose=purpose,
            reason=reason,
            context=context,
        )

    state = ensure_state()
    start_span(f"tool_call:{tool_name}")
    builder = state.event_builder
    data_class = data_classification
    effective_class = data_class or state.config["defaults"]["data_classification"]
    bound = _bind_arguments(func, args, kwargs)

    if state.data_handler and state.data_handler.should_block():
        matches = state.data_handler.inspect("tool_args", bound, effective_class)
        if matches:
            violation = build_data_violation(
                event_type="tool_call",
                classification=effective_class,
                rule_names=matches,
            )
            redacted_args, applied = state.data_handler.sanitize_payload(
                "tool_args", bound, effective_class
            )
            body = {
                "tool_name": tool_name,
                "arguments": _safe_serialize(redacted_args),
                "result": None,
                "duration_ms": 0.0,
                "error": None,
                "status": "policy_violation",
                "data_handling": {
                    "action": "block",
                    "rules": sorted(matches),
                    "target": "tool_args",
                },
            }
            if applied:
                body["redaction"] = {
                    "applied": True,
                    "rules": sorted(applied),
                    "mode": state.data_handler.mode,
                }
            event = builder.build(
                "tool_call",
                body,
                data_classification=data_class,
                purpose=purpose,
                reason=reason,
            )
            emit_event(event)
            notify_violation(violation)
            pop_span()
            raise violation

    start_time = time.perf_counter()
    try:
        if context is not None:
            result = func(context, *args, **kwargs)
        else:
            result = func(*args, **kwargs)
    except DataHandlingViolation:
        pop_span()
        raise
    except Exception as exc:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        log_errors = state.config.get("error_handling", {}).get(
            "log_user_exceptions", True
        )
        body = {
            "tool_name": tool_name,
            "arguments": _safe_serialize(bound),
            "result": None,
            "duration_ms": duration_ms,
            "error": _format_error(exc) if log_errors else None,
        }
        event = builder.build(
            "tool_call",
            body,
            data_classification=data_class,
            purpose=purpose,
            reason=reason,
        )
        emit_event(event)
        pop_span()
        raise

    duration_ms = (time.perf_counter() - start_time) * 1000.0
    body = {
        "tool_name": tool_name,
        "arguments": _safe_serialize(bound),
        "result": _safe_serialize(result),
        "duration_ms": duration_ms,
        "error": None,
    }
    event = builder.build(
        "tool_call",
        body,
        data_classification=data_class,
        purpose=purpose,
        reason=reason,
    )
    emit_event(event)
    pop_span()
    return result


async def _execute_tool_call_async(
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: Dict[str, Any],
    *,
    tool_name: str,
    data_classification: Optional[str] = None,
    purpose: str,
    reason: Optional[str] = None,
    context: Any = None,
) -> Any:
    """Async version of _execute_tool_call."""
    state = ensure_state()
    start_span(f"tool_call:{tool_name}")
    builder = state.event_builder
    data_class = data_classification
    effective_class = data_class or state.config["defaults"]["data_classification"]
    bound = _bind_arguments(func, args, kwargs)

    if state.data_handler and state.data_handler.should_block():
        matches = state.data_handler.inspect("tool_args", bound, effective_class)
        if matches:
            violation = build_data_violation(
                event_type="tool_call",
                classification=effective_class,
                rule_names=matches,
            )
            redacted_args, applied = state.data_handler.sanitize_payload(
                "tool_args", bound, effective_class
            )
            body = {
                "tool_name": tool_name,
                "arguments": _safe_serialize(redacted_args),
                "result": None,
                "duration_ms": 0.0,
                "error": None,
                "status": "policy_violation",
                "data_handling": {
                    "action": "block",
                    "rules": sorted(matches),
                    "target": "tool_args",
                },
            }
            if applied:
                body["redaction"] = {
                    "applied": True,
                    "rules": sorted(applied),
                    "mode": state.data_handler.mode,
                }
            event = builder.build(
                "tool_call",
                body,
                data_classification=data_class,
                purpose=purpose,
                reason=reason,
            )
            emit_event(event)
            notify_violation(violation)
            pop_span()
            raise violation

    start_time = time.perf_counter()
    try:
        if context is not None:
            result = await func(context, *args, **kwargs)
        else:
            result = await func(*args, **kwargs)
    except DataHandlingViolation:
        pop_span()
        raise
    except Exception as exc:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        log_errors = state.config.get("error_handling", {}).get(
            "log_user_exceptions", True
        )
        body = {
            "tool_name": tool_name,
            "arguments": _safe_serialize(bound),
            "result": None,
            "duration_ms": duration_ms,
            "error": _format_error(exc) if log_errors else None,
        }
        event = builder.build(
            "tool_call",
            body,
            data_classification=data_class,
            purpose=purpose,
            reason=reason,
        )
        emit_event(event)
        pop_span()
        raise

    duration_ms = (time.perf_counter() - start_time) * 1000.0
    body = {
        "tool_name": tool_name,
        "arguments": _safe_serialize(bound),
        "result": _safe_serialize(result),
        "duration_ms": duration_ms,
        "error": None,
    }
    event = builder.build(
        "tool_call",
        body,
        data_classification=data_class,
        purpose=purpose,
        reason=reason,
    )
    emit_event(event)
    pop_span()
    return result


def _execute_agent_step(
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: Dict[str, Any],
    *,
    agent_name: str,
    step_type: str,
    data_classification: Optional[str] = None,
    purpose: str,
    context: Any = None,
) -> Any:
    """Execute an agent step with full Monora governance.

    Args:
        func: The function to execute
        args: Positional arguments for func
        kwargs: Keyword arguments for func
        agent_name: Name of the agent
        step_type: Type of step (e.g., "reasoning", "planning")
        data_classification: Data classification level
        purpose: Purpose of the step
        context: Optional context object (for method binding)

    Returns:
        The result from func
    """
    # Check if function is async
    if inspect.iscoroutinefunction(func):
        return _execute_agent_step_async(
            func, args, kwargs,
            agent_name=agent_name,
            step_type=step_type,
            data_classification=data_classification,
            purpose=purpose,
            context=context,
        )

    state = ensure_state()
    start_span(f"agent_step:{agent_name}")
    builder = state.event_builder
    data_class = data_classification
    effective_class = data_class or state.config["defaults"]["data_classification"]
    bound = _bind_arguments(func, args, kwargs)
    step_number = next_step_number()

    if state.data_handler and state.data_handler.should_block():
        matches = state.data_handler.inspect("agent_input", bound, effective_class)
        if matches:
            violation = build_data_violation(
                event_type="agent_step",
                classification=effective_class,
                rule_names=matches,
            )
            redacted_input, applied = state.data_handler.sanitize_payload(
                "agent_input", bound, effective_class
            )
            body = {
                "agent_name": agent_name,
                "step_type": step_type,
                "step_number": step_number,
                "input": _safe_serialize(redacted_input),
                "output": None,
                "duration_ms": 0.0,
                "error": None,
                "status": "policy_violation",
                "data_handling": {
                    "action": "block",
                    "rules": sorted(matches),
                    "target": "agent_input",
                },
            }
            if applied:
                body["redaction"] = {
                    "applied": True,
                    "rules": sorted(applied),
                    "mode": state.data_handler.mode,
                }
            event = builder.build(
                "agent_step",
                body,
                data_classification=data_class,
                purpose=purpose,
            )
            emit_event(event)
            notify_violation(violation)
            pop_span()
            raise violation

    start_time = time.perf_counter()
    try:
        if context is not None:
            result = func(context, *args, **kwargs)
        else:
            result = func(*args, **kwargs)
    except DataHandlingViolation:
        pop_span()
        raise
    except Exception as exc:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        log_errors = state.config.get("error_handling", {}).get(
            "log_user_exceptions", True
        )
        body = {
            "agent_name": agent_name,
            "step_type": step_type,
            "step_number": step_number,
            "input": _safe_serialize(bound),
            "output": None,
            "duration_ms": duration_ms,
            "error": _format_error(exc) if log_errors else None,
        }
        event = builder.build(
            "agent_step",
            body,
            data_classification=data_class,
            purpose=purpose,
        )
        emit_event(event)
        pop_span()
        raise

    duration_ms = (time.perf_counter() - start_time) * 1000.0
    body = {
        "agent_name": agent_name,
        "step_type": step_type,
        "step_number": step_number,
        "input": _safe_serialize(bound),
        "output": _safe_serialize(result),
        "duration_ms": duration_ms,
        "error": None,
    }
    event = builder.build(
        "agent_step",
        body,
        data_classification=data_class,
        purpose=purpose,
    )
    emit_event(event)
    pop_span()
    return result


async def _execute_agent_step_async(
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: Dict[str, Any],
    *,
    agent_name: str,
    step_type: str,
    data_classification: Optional[str] = None,
    purpose: str,
    context: Any = None,
) -> Any:
    """Async version of _execute_agent_step."""
    state = ensure_state()
    start_span(f"agent_step:{agent_name}")
    builder = state.event_builder
    data_class = data_classification
    effective_class = data_class or state.config["defaults"]["data_classification"]
    bound = _bind_arguments(func, args, kwargs)
    step_number = next_step_number()

    if state.data_handler and state.data_handler.should_block():
        matches = state.data_handler.inspect("agent_input", bound, effective_class)
        if matches:
            violation = build_data_violation(
                event_type="agent_step",
                classification=effective_class,
                rule_names=matches,
            )
            redacted_input, applied = state.data_handler.sanitize_payload(
                "agent_input", bound, effective_class
            )
            body = {
                "agent_name": agent_name,
                "step_type": step_type,
                "step_number": step_number,
                "input": _safe_serialize(redacted_input),
                "output": None,
                "duration_ms": 0.0,
                "error": None,
                "status": "policy_violation",
                "data_handling": {
                    "action": "block",
                    "rules": sorted(matches),
                    "target": "agent_input",
                },
            }
            if applied:
                body["redaction"] = {
                    "applied": True,
                    "rules": sorted(applied),
                    "mode": state.data_handler.mode,
                }
            event = builder.build(
                "agent_step",
                body,
                data_classification=data_class,
                purpose=purpose,
            )
            emit_event(event)
            notify_violation(violation)
            pop_span()
            raise violation

    start_time = time.perf_counter()
    try:
        if context is not None:
            result = await func(context, *args, **kwargs)
        else:
            result = await func(*args, **kwargs)
    except DataHandlingViolation:
        pop_span()
        raise
    except Exception as exc:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        log_errors = state.config.get("error_handling", {}).get(
            "log_user_exceptions", True
        )
        body = {
            "agent_name": agent_name,
            "step_type": step_type,
            "step_number": step_number,
            "input": _safe_serialize(bound),
            "output": None,
            "duration_ms": duration_ms,
            "error": _format_error(exc) if log_errors else None,
        }
        event = builder.build(
            "agent_step",
            body,
            data_classification=data_class,
            purpose=purpose,
        )
        emit_event(event)
        pop_span()
        raise

    duration_ms = (time.perf_counter() - start_time) * 1000.0
    body = {
        "agent_name": agent_name,
        "step_type": step_type,
        "step_number": step_number,
        "input": _safe_serialize(bound),
        "output": _safe_serialize(result),
        "duration_ms": duration_ms,
        "error": None,
    }
    event = builder.build(
        "agent_step",
        body,
        data_classification=data_class,
        purpose=purpose,
    )
    emit_event(event)
    pop_span()
    return result


# Helper functions (imported from decorators.py logic)


def _bind_arguments_from_call(args: tuple[Any, ...], kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Convert function call arguments to a dict for inspection.

    This is used for direct callables where we don't have access to the function signature.

    Args:
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        Dictionary containing all arguments
    """
    if not args and kwargs:
        return dict(kwargs)
    if args and not kwargs:
        return {"args": args}
    return {"args": args, **kwargs}


def _bind_arguments(func: Callable[..., Any], args: tuple[Any, ...], kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Bind function arguments using signature inspection.

    This is used for decorators where we have access to the function signature.

    Args:
        func: The function being called
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        Dictionary containing bound arguments
    """
    try:
        bound = inspect.signature(func).bind_partial(*args, **kwargs)
        bound.apply_defaults()
        data = dict(bound.arguments)
        data.pop("self", None)
        data.pop("cls", None)
        return data
    except Exception:
        return {"args": args, "kwargs": kwargs}


def _emit_policy_violation(
    builder: EventBuilder,
    violation: PolicyViolation,
    data_classification: Optional[str],
    purpose: str,
    reason: Optional[str],
) -> None:
    """Emit a policy violation event."""
    body = {
        "model": violation.model,
        "policy_name": violation.policy_name,
        "message": violation.message,
        "status": "policy_violation",
        "error": None,
    }
    event = builder.build(
        "llm_call",
        body,
        data_classification=data_classification,
        purpose=purpose,
        reason=reason,
    )
    emit_event(event)


def _emit_registry_override(
    builder: EventBuilder,
    registry: ModelRegistry,
    model: str,
    data_classification: Optional[str],
    purpose: str,
    reason: Optional[str],
) -> Optional[str]:
    body = {
        "model": model,
        "action": "allow_unknown_model",
        "status": "policy_override",
        "registry_version": registry.version,
        "registry_hash": registry.registry_hash,
        "actor": "system",
        "reason": reason,
    }
    event = builder.build(
        "model_registry_update",
        body,
        data_classification=data_classification,
        purpose=purpose,
        reason=reason,
    )
    emit_event(event)
    return event.get("event_id")


def _build_llm_body(
    model: Optional[str],
    request_payload: Dict[str, Any],
    *,
    provider: str,
    provider_metadata: Optional[Dict[str, Any]],
    response: Any,
    duration_ms: float,
    status: str,
    error: Optional[Exception],
    explain_fn: Optional[Callable[[dict], str]],
) -> Dict[str, Any]:
    """Build the body for an LLM call event."""
    response_details = None
    explanation = None
    if response is not None:
        response_details = _extract_response_details(response)
        if explain_fn:
            try:
                explanation = explain_fn(response_details)
            except Exception:
                explanation = None

    body = {
        "model": model,
        "provider": provider,
        "request": _safe_serialize(request_payload),
        "response": response_details,
        "duration_ms": duration_ms,
        "status": status,
        "error": _format_error(error) if error else None,
        "explanation": explanation,
    }
    if provider_metadata:
        body["provider_metadata"] = provider_metadata
    return body


def _extract_response_details(response: Any) -> Dict[str, Any]:
    """Extract structured details from an LLM response."""
    data = _safe_serialize(response)
    content = None
    finish_reason = None
    usage = None
    if isinstance(data, dict):
        if "choices" in data and data["choices"]:
            choice = data["choices"][0]
            if isinstance(choice, dict):
                finish_reason = choice.get("finish_reason")
                message = choice.get("message")
                if isinstance(message, dict):
                    content = message.get("content")
                if content is None:
                    content = choice.get("text")
        if "content" in data and content is None:
            content = data.get("content")
        usage = data.get("usage")
    return {"content": content, "finish_reason": finish_reason, "usage": usage}


def _safe_serialize(obj: Any) -> Any:
    """Recursively serialize object to JSON-safe values."""
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


def _format_error(error: Exception) -> Dict[str, str]:
    """Format an exception as a dictionary."""
    return {"type": error.__class__.__name__, "message": str(error)}
