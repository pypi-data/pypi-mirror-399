"""OpenAI SDK integration for Monora.

Provides automatic instrumentation for OpenAI SDK calls (chat, completions, embeddings).

Example:
    ```python
    from openai import OpenAI
    from monora.integrations import patch_openai

    client = OpenAI()
    patch_openai(client, purpose="customer_support")

    # All calls are now automatically traced
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}]
    )
    ```
"""

from typing import Any, Callable, Optional
from functools import wraps

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None  # type: ignore

from monora.runtime import ensure_state, emit_event
from monora.lineage import set_current_event


def patch_openai(
    client: Any,
    data_classification: str = "internal",
    purpose: str = "general",
    reason: Optional[str] = None,
) -> None:
    """Patch an OpenAI client to automatically trace all API calls.

    Args:
        client: OpenAI client instance to patch
        data_classification: Data classification for events
        purpose: Purpose/intent for API calls
        reason: Optional reason for the calls
    """
    if not OPENAI_AVAILABLE:
        raise ImportError("OpenAI SDK is not installed. Install it with: pip install openai")

    # Patch chat completions
    if hasattr(client, "chat") and hasattr(client.chat, "completions"):
        original_create = client.chat.completions.create
        client.chat.completions.create = _wrap_chat_completions(
            original_create,
            data_classification=data_classification,
            purpose=purpose,
            reason=reason,
        )

    # Patch regular completions
    if hasattr(client, "completions"):
        original_create = client.completions.create
        client.completions.create = _wrap_completions(
            original_create,
            data_classification=data_classification,
            purpose=purpose,
            reason=reason,
        )

    # Patch embeddings
    if hasattr(client, "embeddings"):
        original_create = client.embeddings.create
        client.embeddings.create = _wrap_embeddings(
            original_create,
            data_classification=data_classification,
            purpose=purpose,
            reason=reason,
        )


def _wrap_chat_completions(
    original_fn: Callable,
    data_classification: str,
    purpose: str,
    reason: Optional[str],
) -> Callable:
    """Wrap chat.completions.create to emit events."""

    @wraps(original_fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Extract model and messages
        model = kwargs.get("model", "unknown")
        messages = kwargs.get("messages", [])

        # Emit start event
        state = ensure_state()
        start_event = state.event_builder.build(
            "llm_call",
            {
                "model": model,
                "provider": "openai",
                "api": "chat.completions",
                "num_messages": len(messages),
                "messages": messages[:10],  # Limit to first 10
                "stream": kwargs.get("stream", False),
                "temperature": kwargs.get("temperature"),
                "max_tokens": kwargs.get("max_tokens"),
                "top_p": kwargs.get("top_p"),
            },
            data_classification=data_classification,
            purpose=purpose,
            reason=reason,
        )
        emit_event(start_event)
        set_current_event(start_event["event_id"])

        try:
            # Call original function
            response = original_fn(*args, **kwargs)

            # Extract completion data
            completion_data: dict[str, Any] = {
                "model": getattr(response, "model", model),
            }

            if hasattr(response, "usage"):
                completion_data["usage"] = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            if hasattr(response, "choices"):
                completion_data["num_choices"] = len(response.choices)
                completion_data["choices"] = [
                    {
                        "finish_reason": choice.finish_reason,
                        "message": {
                            "role": choice.message.role,
                            "content": choice.message.content[:500] if choice.message.content else None,
                        },
                    }
                    for choice in response.choices[:5]  # Limit to first 5 choices
                ]

            # Emit completion event
            completion_event = state.event_builder.build(
                "llm_call",
                completion_data,
                data_classification=data_classification,
                purpose=purpose,
                parent_event_id=start_event["event_id"],
            )
            emit_event(completion_event)

            return response

        except Exception as error:
            # Emit error event
            error_event = state.event_builder.build(
                "llm_call",
                {
                    "model": model,
                    "error": str(error),
                    "error_type": type(error).__name__,
                },
                data_classification=data_classification,
                purpose=purpose,
                parent_event_id=start_event["event_id"],
            )
            emit_event(error_event)
            raise

    return wrapper


def _wrap_completions(
    original_fn: Callable,
    data_classification: str,
    purpose: str,
    reason: Optional[str],
) -> Callable:
    """Wrap completions.create to emit events."""

    @wraps(original_fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        model = kwargs.get("model", "unknown")
        prompt = kwargs.get("prompt", "")

        state = ensure_state()
        start_event = state.event_builder.build(
            "llm_call",
            {
                "model": model,
                "provider": "openai",
                "api": "completions",
                "prompt": str(prompt)[:1000],  # Limit to 1000 chars
                "max_tokens": kwargs.get("max_tokens"),
                "temperature": kwargs.get("temperature"),
            },
            data_classification=data_classification,
            purpose=purpose,
            reason=reason,
        )
        emit_event(start_event)
        set_current_event(start_event["event_id"])

        try:
            response = original_fn(*args, **kwargs)

            completion_data: dict[str, Any] = {"model": getattr(response, "model", model)}

            if hasattr(response, "usage"):
                completion_data["usage"] = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            if hasattr(response, "choices"):
                completion_data["num_choices"] = len(response.choices)
                completion_data["choices"] = [
                    {"text": choice.text[:500], "finish_reason": choice.finish_reason}
                    for choice in response.choices[:5]
                ]

            completion_event = state.event_builder.build(
                "llm_call",
                completion_data,
                data_classification=data_classification,
                purpose=purpose,
                parent_event_id=start_event["event_id"],
            )
            emit_event(completion_event)

            return response

        except Exception as error:
            error_event = state.event_builder.build(
                "llm_call",
                {
                    "model": model,
                    "error": str(error),
                    "error_type": type(error).__name__,
                },
                data_classification=data_classification,
                purpose=purpose,
                parent_event_id=start_event["event_id"],
            )
            emit_event(error_event)
            raise

    return wrapper


def _wrap_embeddings(
    original_fn: Callable,
    data_classification: str,
    purpose: str,
    reason: Optional[str],
) -> Callable:
    """Wrap embeddings.create to emit events."""

    @wraps(original_fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        model = kwargs.get("model", "unknown")
        input_data = kwargs.get("input", "")

        # Handle both string and list inputs
        if isinstance(input_data, list):
            num_inputs = len(input_data)
            input_preview = input_data[:3]  # First 3 items
        else:
            num_inputs = 1
            input_preview = [str(input_data)[:500]]

        state = ensure_state()
        start_event = state.event_builder.build(
            "llm_call",
            {
                "model": model,
                "provider": "openai",
                "api": "embeddings",
                "num_inputs": num_inputs,
                "input_preview": input_preview,
            },
            data_classification=data_classification,
            purpose=purpose,
            reason=reason,
        )
        emit_event(start_event)
        set_current_event(start_event["event_id"])

        try:
            response = original_fn(*args, **kwargs)

            completion_data: dict[str, Any] = {
                "model": getattr(response, "model", model),
                "num_embeddings": len(response.data) if hasattr(response, "data") else 0,
            }

            if hasattr(response, "usage"):
                completion_data["usage"] = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            completion_event = state.event_builder.build(
                "llm_call",
                completion_data,
                data_classification=data_classification,
                purpose=purpose,
                parent_event_id=start_event["event_id"],
            )
            emit_event(completion_event)

            return response

        except Exception as error:
            error_event = state.event_builder.build(
                "llm_call",
                {
                    "model": model,
                    "error": str(error),
                    "error_type": type(error).__name__,
                },
                data_classification=data_classification,
                purpose=purpose,
                parent_event_id=start_event["event_id"],
            )
            emit_event(error_event)
            raise

    return wrapper
