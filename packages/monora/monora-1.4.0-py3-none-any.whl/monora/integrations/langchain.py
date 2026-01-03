"""LangChain integration for Monora.

Provides automatic tracing for LangChain chains, LLMs, tools, and retrievers.

Example:
    ```python
    from monora.integrations import MonoraCallbackHandler
    from langchain.chains import LLMChain

    handler = MonoraCallbackHandler()
    chain = LLMChain(llm=llm, prompt=prompt, callbacks=[handler])
    result = chain.run("What is AI?")
    ```
"""

from typing import Any, Dict, List, Optional, Union
from uuid import UUID

try:
    from langchain.callbacks.base import BaseCallbackHandler
    from langchain.schema import AgentAction, AgentFinish, LLMResult
    from langchain.schema.document import Document
    from langchain.schema.messages import BaseMessage

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    # Stub classes for type hints when LangChain is not installed
    BaseCallbackHandler = object  # type: ignore
    AgentAction = Any  # type: ignore
    AgentFinish = Any  # type: ignore
    LLMResult = Any  # type: ignore
    Document = Any  # type: ignore
    BaseMessage = Any  # type: ignore

from monora.context import get_current_span
from monora.lineage import set_current_event, add_input_event
from monora.runtime import ensure_state, emit_event


class MonoraCallbackHandler(BaseCallbackHandler):
    """LangChain callback handler that traces operations to Monora.

    This handler automatically:
    - Traces chain execution with spans
    - Captures LLM calls with model usage
    - Tracks tool invocations
    - Records retriever queries
    - Maintains causal lineage between operations
    """

    def __init__(
        self,
        data_classification: str = "internal",
        purpose: str = "general",
        capture_prompts: bool = True,
        capture_completions: bool = True,
    ):
        """Initialize the Monora callback handler.

        Args:
            data_classification: Data classification for events (default: "internal")
            purpose: Purpose for the operations (default: "general")
            capture_prompts: Whether to capture full prompts (default: True)
            capture_completions: Whether to capture full completions (default: True)
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError(
                "LangChain is not installed. Install it with: pip install langchain"
            )

        super().__init__()
        self.data_classification = data_classification
        self.purpose = purpose
        self.capture_prompts = capture_prompts
        self.capture_completions = capture_completions
        self._run_map: Dict[str, str] = {}  # Maps run_id to event_id

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Run when chain starts."""
        chain_type = serialized.get("name", serialized.get("id", ["unknown"])[-1])

        # Build and emit chain start event
        state = ensure_state()
        event = state.event_builder.build(
            "agent_step",
            {
                "step_type": "chain_start",
                "chain_type": chain_type,
                "inputs": inputs if self.capture_prompts else {"_truncated": True},
                "run_id": str(run_id),
                "parent_run_id": str(parent_run_id) if parent_run_id else None,
                "tags": tags or [],
                "metadata": metadata or {},
            },
            data_classification=self.data_classification,
            purpose=self.purpose,
        )
        emit_event(event)

        # Store mapping for lineage
        self._run_map[str(run_id)] = event["event_id"]
        set_current_event(event["event_id"])

    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Run when chain ends."""
        # Link to chain start if available
        parent_event_id = self._run_map.get(str(run_id))
        if parent_event_id:
            add_input_event(parent_event_id)

        state = ensure_state()
        event = state.event_builder.build(
            "agent_step",
            {
                "step_type": "chain_end",
                "outputs": outputs if self.capture_completions else {"_truncated": True},
                "run_id": str(run_id),
            },
            data_classification=self.data_classification,
            purpose=self.purpose,
        )
        emit_event(event)

        # Clean up mapping
        self._run_map.pop(str(run_id), None)

    def on_chain_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Run when chain errors."""
        parent_event_id = self._run_map.get(str(run_id))
        if parent_event_id:
            add_input_event(parent_event_id)

        state = ensure_state()
        event = state.event_builder.build(
            "agent_step",
            {
                "step_type": "chain_error",
                "error": str(error),
                "error_type": type(error).__name__,
                "run_id": str(run_id),
            },
            data_classification=self.data_classification,
            purpose=self.purpose,
        )
        emit_event(event)

        self._run_map.pop(str(run_id), None)

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Run when LLM starts."""
        # Extract model name
        model = serialized.get("name", serialized.get("id", ["unknown"])[-1])
        if "kwargs" in serialized and "model_name" in serialized["kwargs"]:
            model = serialized["kwargs"]["model_name"]

        # Link to parent chain if available
        if parent_run_id:
            parent_event_id = self._run_map.get(str(parent_run_id))
            if parent_event_id:
                add_input_event(parent_event_id)

        state = ensure_state()
        event = state.event_builder.build(
            "llm_call",
            {
                "model": model,
                "provider": serialized.get("provider", "unknown"),
                "prompts": prompts if self.capture_prompts else [f"<{len(p)} chars>" for p in prompts],
                "num_prompts": len(prompts),
                "run_id": str(run_id),
                "parent_run_id": str(parent_run_id) if parent_run_id else None,
                "tags": tags or [],
                "metadata": metadata or {},
            },
            data_classification=self.data_classification,
            purpose=self.purpose,
        )
        emit_event(event)

        self._run_map[str(run_id)] = event["event_id"]
        set_current_event(event["event_id"])

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Run when LLM ends."""
        parent_event_id = self._run_map.get(str(run_id))
        if parent_event_id:
            add_input_event(parent_event_id)

        # Extract token usage
        token_usage = {}
        if response.llm_output and "token_usage" in response.llm_output:
            token_usage = response.llm_output["token_usage"]

        # Extract completions
        completions = []
        for generations in response.generations:
            for gen in generations:
                text = gen.text if hasattr(gen, "text") else str(gen)
                if self.capture_completions:
                    completions.append(text)
                else:
                    completions.append(f"<{len(text)} chars>")

        state = ensure_state()
        event = state.event_builder.build(
            "llm_call",
            {
                "completions": completions,
                "num_completions": len(completions),
                "token_usage": token_usage,
                "run_id": str(run_id),
            },
            data_classification=self.data_classification,
            purpose=self.purpose,
        )
        emit_event(event)

        self._run_map.pop(str(run_id), None)

    def on_llm_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Run when LLM errors."""
        parent_event_id = self._run_map.get(str(run_id))
        if parent_event_id:
            add_input_event(parent_event_id)

        state = ensure_state()
        event = state.event_builder.build(
            "llm_call",
            {
                "error": str(error),
                "error_type": type(error).__name__,
                "run_id": str(run_id),
            },
            data_classification=self.data_classification,
            purpose=self.purpose,
        )
        emit_event(event)

        self._run_map.pop(str(run_id), None)

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Run when tool starts."""
        tool_name = serialized.get("name", "unknown")

        if parent_run_id:
            parent_event_id = self._run_map.get(str(parent_run_id))
            if parent_event_id:
                add_input_event(parent_event_id)

        state = ensure_state()
        event = state.event_builder.build(
            "tool_call",
            {
                "tool_name": tool_name,
                "input": input_str if self.capture_prompts else f"<{len(input_str)} chars>",
                "run_id": str(run_id),
                "parent_run_id": str(parent_run_id) if parent_run_id else None,
                "tags": tags or [],
                "metadata": metadata or {},
            },
            data_classification=self.data_classification,
            purpose=self.purpose,
        )
        emit_event(event)

        self._run_map[str(run_id)] = event["event_id"]
        set_current_event(event["event_id"])

    def on_tool_end(
        self,
        output: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Run when tool ends."""
        parent_event_id = self._run_map.get(str(run_id))
        if parent_event_id:
            add_input_event(parent_event_id)

        state = ensure_state()
        event = state.event_builder.build(
            "tool_call",
            {
                "output": output if self.capture_completions else f"<{len(output)} chars>",
                "run_id": str(run_id),
            },
            data_classification=self.data_classification,
            purpose=self.purpose,
        )
        emit_event(event)

        self._run_map.pop(str(run_id), None)

    def on_tool_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Run when tool errors."""
        parent_event_id = self._run_map.get(str(run_id))
        if parent_event_id:
            add_input_event(parent_event_id)

        state = ensure_state()
        event = state.event_builder.build(
            "tool_call",
            {
                "error": str(error),
                "error_type": type(error).__name__,
                "run_id": str(run_id),
            },
            data_classification=self.data_classification,
            purpose=self.purpose,
        )
        emit_event(event)

        self._run_map.pop(str(run_id), None)

    def on_retriever_start(
        self,
        serialized: Dict[str, Any],
        query: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Run when retriever starts."""
        if parent_run_id:
            parent_event_id = self._run_map.get(str(parent_run_id))
            if parent_event_id:
                add_input_event(parent_event_id)

        state = ensure_state()
        event = state.event_builder.build(
            "custom",
            {
                "custom_type": "retriever_query",
                "query": query if self.capture_prompts else f"<{len(query)} chars>",
                "run_id": str(run_id),
                "parent_run_id": str(parent_run_id) if parent_run_id else None,
                "tags": tags or [],
                "metadata": metadata or {},
            },
            data_classification=self.data_classification,
            purpose=self.purpose,
        )
        emit_event(event)

        self._run_map[str(run_id)] = event["event_id"]
        set_current_event(event["event_id"])

    def on_retriever_end(
        self,
        documents: List[Document],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Run when retriever ends."""
        parent_event_id = self._run_map.get(str(run_id))
        if parent_event_id:
            add_input_event(parent_event_id)

        # Extract document IDs/sources for lineage
        from monora.lineage import add_data_source
        for doc in documents:
            if hasattr(doc, "metadata") and "source" in doc.metadata:
                add_data_source(doc.metadata["source"])

        doc_summaries = []
        for doc in documents:
            summary = {
                "page_content_length": len(doc.page_content) if hasattr(doc, "page_content") else 0,
                "metadata": doc.metadata if hasattr(doc, "metadata") else {},
            }
            if self.capture_completions and hasattr(doc, "page_content"):
                summary["page_content"] = doc.page_content[:500]  # Limit to 500 chars
            doc_summaries.append(summary)

        state = ensure_state()
        event = state.event_builder.build(
            "custom",
            {
                "custom_type": "retriever_result",
                "num_documents": len(documents),
                "documents": doc_summaries,
                "run_id": str(run_id),
            },
            data_classification=self.data_classification,
            purpose=self.purpose,
        )
        emit_event(event)

        self._run_map.pop(str(run_id), None)

    def on_retriever_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Run when retriever errors."""
        parent_event_id = self._run_map.get(str(run_id))
        if parent_event_id:
            add_input_event(parent_event_id)

        state = ensure_state()
        event = state.event_builder.build(
            "custom",
            {
                "custom_type": "retriever_error",
                "error": str(error),
                "error_type": type(error).__name__,
                "run_id": str(run_id),
            },
            data_classification=self.data_classification,
            purpose=self.purpose,
        )
        emit_event(event)

        self._run_map.pop(str(run_id), None)
