"""Anthropic SDK integration for Monora.

Provides automatic instrumentation for Anthropic SDK calls (messages, completions).

Example:
    ```python
    from anthropic import Anthropic
    from monora.integrations import patch_anthropic

    client = Anthropic()
    patch_anthropic(client, purpose="customer_support")

    # All calls are now automatically traced
    response = client.messages.create(
        model="claude-3-opus-20240229",
        messages=[{"role": "user", "content": "Hello"}]
    )
    ```
"""

from typing import Any, Callable, Generator, Optional, Iterator
from functools import wraps

try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None  # type: ignore

from monora.runtime import ensure_state, emit_event
from monora.lineage import set_current_event


def patch_anthropic(
    client: Any,
    data_classification: str = "internal",
    purpose: str = "general",
    reason: Optional[str] = None,
) -> None:
    """Patch an Anthropic client to automatically trace all API calls.

    Args:
        client: Anthropic client instance to patch
        data_classification: Data classification for events
        purpose: Purpose/intent for API calls
        reason: Optional reason for the calls
    """
    if not ANTHROPIC_AVAILABLE:
        raise ImportError("Anthropic SDK is not installed. Install it with: pip install anthropic")

    # Patch messages API (modern API)
    if hasattr(client, "messages"):
        original_create = client.messages.create
        client.messages.create = _wrap_messages_create(
            original_create,
            data_classification=data_classification,
            purpose=purpose,
            reason=reason,
        )

        # Patch streaming if available
        if hasattr(client.messages, "stream"):
            original_stream = client.messages.stream
            client.messages.stream = _wrap_messages_stream(
                original_stream,
                data_classification=data_classification,
                purpose=purpose,
                reason=reason,
            )

    # Patch completions API (legacy API)
    if hasattr(client, "completions"):
        original_create = client.completions.create
        client.completions.create = _wrap_completions(
            original_create,
            data_classification=data_classification,
            purpose=purpose,
            reason=reason,
        )


def _wrap_messages_create(
    original_fn: Callable,
    data_classification: str,
    purpose: str,
    reason: Optional[str],
) -> Callable:
    """Wrap messages.create to emit events, with streaming support."""

    @wraps(original_fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        model = kwargs.get("model", "unknown")
        messages = kwargs.get("messages", [])
        is_streaming = kwargs.get("stream", False)

        # Emit start event
        state = ensure_state()
        start_event = state.event_builder.build(
            "llm_call",
            {
                "model": model,
                "provider": "anthropic",
                "api": "messages",
                "num_messages": len(messages),
                "messages": messages[:10],  # Limit to first 10
                "stream": is_streaming,
                "max_tokens": kwargs.get("max_tokens"),
                "temperature": kwargs.get("temperature"),
                "top_p": kwargs.get("top_p"),
                "system": kwargs.get("system", "")[:500] if kwargs.get("system") else None,
            },
            data_classification=data_classification,
            purpose=purpose,
            reason=reason,
        )
        emit_event(start_event)
        set_current_event(start_event["event_id"])

        try:
            response = original_fn(*args, **kwargs)

            if is_streaming:
                # Return a wrapped streaming response
                return _wrap_streaming_response(
                    response,
                    model,
                    start_event["event_id"],
                    data_classification,
                    purpose,
                    state,
                )
            else:
                # Non-streaming response
                completion_data = _extract_message_response(response, model)
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


def _wrap_messages_stream(
    original_fn: Callable,
    data_classification: str,
    purpose: str,
    reason: Optional[str],
) -> Callable:
    """Wrap messages.stream context manager."""

    @wraps(original_fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        model = kwargs.get("model", "unknown")
        messages = kwargs.get("messages", [])

        state = ensure_state()
        start_event = state.event_builder.build(
            "llm_call",
            {
                "model": model,
                "provider": "anthropic",
                "api": "messages.stream",
                "num_messages": len(messages),
                "messages": messages[:10],
                "stream": True,
                "max_tokens": kwargs.get("max_tokens"),
                "temperature": kwargs.get("temperature"),
            },
            data_classification=data_classification,
            purpose=purpose,
            reason=reason,
        )
        emit_event(start_event)
        set_current_event(start_event["event_id"])

        # Call original and wrap the context manager
        stream_manager = original_fn(*args, **kwargs)
        return _StreamManagerWrapper(
            stream_manager,
            model,
            start_event["event_id"],
            data_classification,
            purpose,
            state,
        )

    return wrapper


class _StreamManagerWrapper:
    """Wrapper for Anthropic's streaming context manager."""

    def __init__(
        self,
        stream_manager: Any,
        model: str,
        parent_event_id: str,
        data_classification: str,
        purpose: str,
        state: Any,
    ):
        self._stream_manager = stream_manager
        self._model = model
        self._parent_event_id = parent_event_id
        self._data_classification = data_classification
        self._purpose = purpose
        self._state = state
        self._accumulated_text = ""
        self._usage = {}

    def __enter__(self) -> Any:
        self._stream = self._stream_manager.__enter__()
        return _StreamWrapper(self, self._stream)

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Any:
        result = self._stream_manager.__exit__(exc_type, exc_val, exc_tb)

        # Emit completion event
        completion_event = self._state.event_builder.build(
            "llm_call",
            {
                "model": self._model,
                "content": self._accumulated_text[:500] if self._accumulated_text else None,
                "content_length": len(self._accumulated_text),
                "usage": self._usage,
                "stream_complete": True,
            },
            data_classification=self._data_classification,
            purpose=self._purpose,
            parent_event_id=self._parent_event_id,
        )
        emit_event(completion_event)

        return result


class _StreamWrapper:
    """Wrapper for the stream object to track content."""

    def __init__(self, manager: _StreamManagerWrapper, stream: Any):
        self._manager = manager
        self._stream = stream

    def __iter__(self) -> Iterator[Any]:
        return self

    def __next__(self) -> Any:
        chunk = next(self._stream)

        # Track text content
        if hasattr(chunk, "type"):
            if chunk.type == "content_block_delta":
                if hasattr(chunk, "delta") and hasattr(chunk.delta, "text"):
                    self._manager._accumulated_text += chunk.delta.text
            elif chunk.type == "message_delta":
                if hasattr(chunk, "usage"):
                    self._manager._usage = {
                        "output_tokens": getattr(chunk.usage, "output_tokens", 0),
                    }

        return chunk

    def __getattr__(self, name: str) -> Any:
        return getattr(self._stream, name)


def _wrap_streaming_response(
    response: Any,
    model: str,
    parent_event_id: str,
    data_classification: str,
    purpose: str,
    state: Any,
) -> Generator[Any, None, None]:
    """Wrap a streaming response to track chunks."""
    accumulated_text = ""
    usage = {}

    try:
        for chunk in response:
            # Track content from streaming chunks
            if hasattr(chunk, "type"):
                if chunk.type == "content_block_delta":
                    if hasattr(chunk, "delta") and hasattr(chunk.delta, "text"):
                        accumulated_text += chunk.delta.text
                elif chunk.type == "message_delta":
                    if hasattr(chunk, "usage"):
                        usage = {
                            "output_tokens": getattr(chunk.usage, "output_tokens", 0),
                        }
            yield chunk

    finally:
        # Emit completion event when stream ends
        completion_event = state.event_builder.build(
            "llm_call",
            {
                "model": model,
                "content": accumulated_text[:500] if accumulated_text else None,
                "content_length": len(accumulated_text),
                "usage": usage,
                "stream_complete": True,
            },
            data_classification=data_classification,
            purpose=purpose,
            parent_event_id=parent_event_id,
        )
        emit_event(completion_event)


def _extract_message_response(response: Any, model: str) -> dict[str, Any]:
    """Extract data from a non-streaming message response."""
    data: dict[str, Any] = {
        "model": getattr(response, "model", model),
    }

    if hasattr(response, "usage"):
        data["usage"] = {
            "input_tokens": getattr(response.usage, "input_tokens", 0),
            "output_tokens": getattr(response.usage, "output_tokens", 0),
        }

    if hasattr(response, "content"):
        content_blocks = response.content
        data["num_content_blocks"] = len(content_blocks)
        data["content"] = []
        for block in content_blocks[:5]:  # Limit to first 5
            if hasattr(block, "text"):
                data["content"].append({
                    "type": "text",
                    "text": block.text[:500] if block.text else None,
                })
            elif hasattr(block, "type"):
                data["content"].append({"type": block.type})

    if hasattr(response, "stop_reason"):
        data["stop_reason"] = response.stop_reason

    return data


def _wrap_completions(
    original_fn: Callable,
    data_classification: str,
    purpose: str,
    reason: Optional[str],
) -> Callable:
    """Wrap legacy completions.create to emit events."""

    @wraps(original_fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        model = kwargs.get("model", "unknown")
        prompt = kwargs.get("prompt", "")

        state = ensure_state()
        start_event = state.event_builder.build(
            "llm_call",
            {
                "model": model,
                "provider": "anthropic",
                "api": "completions",
                "prompt": str(prompt)[:1000],
                "max_tokens_to_sample": kwargs.get("max_tokens_to_sample"),
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

            completion_data: dict[str, Any] = {
                "model": getattr(response, "model", model),
            }

            if hasattr(response, "completion"):
                completion_data["completion"] = response.completion[:500]

            if hasattr(response, "stop_reason"):
                completion_data["stop_reason"] = response.stop_reason

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
