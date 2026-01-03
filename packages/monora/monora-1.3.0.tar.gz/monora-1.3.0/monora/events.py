"""Event envelope builder and helpers."""
from __future__ import annotations

from typing import Dict, List, Optional

from ._internal import (
    EnvironmentEnricher,
    HostEnricher,
    ProcessEnricher,
    ServiceNameEnricher,
    TimestampEnricher,
    generate_ulid,
)
from .context import get_current_span, next_event_sequence
from .lineage import (
    get_data_sources,
    get_input_events,
    get_parent_event_id,
    get_prompt_id,
    get_template_id,
    set_current_event,
)


class EventBuilder:
    def __init__(self, config: Dict):
        self.defaults = config.get("defaults", {})
        self.enrichers = [
            TimestampEnricher(),
            ServiceNameEnricher(config),
            EnvironmentEnricher(config),
            HostEnricher(),
            ProcessEnricher(),
        ]

    def build(
        self,
        event_type: str,
        body: Dict,
        data_classification: Optional[str] = None,
        purpose: Optional[str] = None,
        reason: Optional[str] = None,
        parent_event_id: Optional[str] = None,
        input_event_ids: Optional[List[str]] = None,
        prompt_id: Optional[str] = None,
        template_id: Optional[str] = None,
        data_source_ids: Optional[List[str]] = None,
    ) -> Dict:
        span = get_current_span()

        # Auto-capture lineage from context if not explicitly provided
        effective_parent_event_id = parent_event_id or get_parent_event_id()
        effective_input_event_ids = input_event_ids or get_input_events()
        effective_prompt_id = prompt_id or get_prompt_id()
        effective_template_id = template_id or get_template_id()
        effective_data_source_ids = data_source_ids or get_data_sources()

        event_id = generate_ulid("evt")
        event = {
            "schema_version": "1.1.0",
            "event_id": event_id,
            "event_type": event_type,
            "trace_id": span.trace_id if span else generate_ulid("trc"),
            "span_id": span.span_id if span else generate_ulid("spn"),
            "parent_span_id": span.parent_span_id if span else None,
            "parent_event_id": effective_parent_event_id,
            "input_event_ids": effective_input_event_ids if effective_input_event_ids else [],
            "prompt_id": effective_prompt_id,
            "template_id": effective_template_id,
            "data_source_ids": effective_data_source_ids if effective_data_source_ids else [],
            "data_classification": data_classification
            or self.defaults.get("data_classification", "internal"),
            "purpose": purpose or self.defaults.get("purpose", "general"),
            "reason": reason,
            "body": body,
        }
        sequence = next_event_sequence()
        if sequence is not None:
            event["event_sequence"] = sequence
        for enricher in self.enrichers:
            enricher.enrich(event)

        # Update current event for next event's parent_event_id
        set_current_event(event_id)

        return event
