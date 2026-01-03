"""EU AI Act transparency report generation.

This module provides tools for generating transparency reports compliant with
the EU AI Act (Regulation 2024/1689), specifically addressing requirements from
Articles 13, 52, and Annex IV.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set


@dataclass
class RiskCategorySummary:
    """Summary of AI interactions by risk category."""
    minimal: int = 0
    limited: int = 0
    high: int = 0
    unacceptable: int = 0


@dataclass
class ModelUsageSummary:
    """Usage summary for a specific model."""
    model: str
    provider: str
    risk_category: str
    call_count: int
    first_used: Optional[str] = None
    last_used: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)


@dataclass
class AIActTransparencyReport:
    """EU AI Act Article 13/52 compliant transparency report.

    This report provides transparency documentation required by the EU AI Act,
    including risk classification, model inventory, and compliance metrics.
    """
    report_version: str = "1.0"
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Organization info (Annex IV requirements)
    organization_name: Optional[str] = None
    contact_email: Optional[str] = None
    reporting_period_start: Optional[str] = None
    reporting_period_end: Optional[str] = None

    # AI System Summary
    total_ai_interactions: int = 0
    unique_models_used: int = 0
    unique_traces: int = 0

    # Risk Assessment
    risk_category_summary: RiskCategorySummary = field(default_factory=RiskCategorySummary)
    high_risk_models: List[str] = field(default_factory=list)
    unacceptable_risk_models: List[str] = field(default_factory=list)

    # Model Inventory
    models_used: List[ModelUsageSummary] = field(default_factory=list)

    # Compliance Metrics
    policy_violations_count: int = 0
    policy_violations_by_model: Dict[str, int] = field(default_factory=dict)

    # Data Classification
    data_classifications_used: Dict[str, int] = field(default_factory=dict)


def build_ai_act_report(
    events: List[Dict[str, Any]],
    config: Optional[Dict[str, Any]] = None,
) -> AIActTransparencyReport:
    """Build AI Act transparency report from event log.

    Args:
        events: List of Monora event dictionaries.
        config: Optional Monora configuration dictionary containing
                ai_act and registry settings.

    Returns:
        AIActTransparencyReport instance with populated fields.

    Example:
        >>> events = load_jsonl("events.jsonl")
        >>> config = load_config("monora.yml")
        >>> report = build_ai_act_report(events, config)
        >>> write_ai_act_report(report, "transparency_report.json")
    """
    ai_act_config = (config or {}).get("ai_act", {})
    registry_config = (config or {}).get("registry", {})

    report = AIActTransparencyReport(
        organization_name=ai_act_config.get("organization_name"),
        contact_email=ai_act_config.get("contact_email"),
    )

    # Build provider risk category and capabilities maps
    provider_risk: Dict[str, str] = {}
    provider_capabilities: Dict[str, List[str]] = {}
    default_risk = ai_act_config.get("default_risk_category", "limited")

    for provider in registry_config.get("providers", []):
        name = provider.get("name", "")
        provider_risk[name] = provider.get("risk_category", default_risk)
        provider_capabilities[name] = provider.get("capabilities", [])

    # Process events
    trace_ids: Set[str] = set()
    model_stats: Dict[str, Dict[str, Any]] = {}
    timestamps: List[str] = []

    for event in events:
        # Skip trust summary events
        if event.get("event_type") == "trust_summary":
            continue

        # Track trace IDs
        trace_id = event.get("trace_id")
        if trace_id:
            trace_ids.add(trace_id)

        # Track timestamps
        timestamp = event.get("timestamp")
        if timestamp:
            timestamps.append(timestamp)

        body = event.get("body", {})

        # Track LLM calls
        if event.get("event_type") == "llm_call":
            model = body.get("model", "unknown")
            provider = body.get("provider", "unknown")

            if model not in model_stats:
                model_stats[model] = {
                    "provider": provider,
                    "count": 0,
                    "first_used": timestamp,
                    "last_used": timestamp,
                }

            model_stats[model]["count"] += 1
            model_stats[model]["last_used"] = timestamp

        # Track policy violations
        if body.get("status") == "policy_violation":
            report.policy_violations_count += 1
            model = body.get("model", "unknown")
            report.policy_violations_by_model[model] = \
                report.policy_violations_by_model.get(model, 0) + 1

        # Track data classifications
        data_class = event.get("data_classification")
        if data_class:
            report.data_classifications_used[data_class] = \
                report.data_classifications_used.get(data_class, 0) + 1

    # Set reporting period
    if timestamps:
        timestamps.sort()
        report.reporting_period_start = timestamps[0]
        report.reporting_period_end = timestamps[-1]

    # Build model summaries with risk categorization
    for model, stats in model_stats.items():
        provider = stats["provider"]
        risk = provider_risk.get(provider, default_risk)
        caps = provider_capabilities.get(provider, [])

        summary = ModelUsageSummary(
            model=model,
            provider=provider,
            risk_category=risk,
            call_count=stats["count"],
            first_used=stats["first_used"],
            last_used=stats["last_used"],
            capabilities=list(caps),
        )
        report.models_used.append(summary)

        # Update risk category counts
        if risk == "minimal":
            report.risk_category_summary.minimal += stats["count"]
        elif risk == "limited":
            report.risk_category_summary.limited += stats["count"]
        elif risk == "high":
            report.risk_category_summary.high += stats["count"]
            if model not in report.high_risk_models:
                report.high_risk_models.append(model)
        elif risk == "unacceptable":
            report.risk_category_summary.unacceptable += stats["count"]
            if model not in report.unacceptable_risk_models:
                report.unacceptable_risk_models.append(model)

    # Set summary counts
    report.total_ai_interactions = sum(s["count"] for s in model_stats.values())
    report.unique_models_used = len(model_stats)
    report.unique_traces = len(trace_ids)

    return report


def write_ai_act_report(
    report: AIActTransparencyReport,
    path: str,
    format: str = "json",
) -> None:
    """Write AI Act report to file.

    Args:
        report: The transparency report to write.
        path: Output file path.
        format: Output format - 'json' or 'markdown'.

    Raises:
        ValueError: If format is not 'json' or 'markdown'.
    """
    # Ensure output directory exists
    output_dir = os.path.dirname(path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    if format == "json":
        _write_json(report, path)
    elif format == "markdown":
        _write_markdown(report, path)
    else:
        raise ValueError(f"Unsupported format: {format}")


def _write_json(report: AIActTransparencyReport, path: str) -> None:
    """Write report as JSON."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(report), f, indent=2)


def _write_markdown(report: AIActTransparencyReport, path: str) -> None:
    """Write report as Markdown."""
    lines = [
        "# EU AI Act Transparency Report",
        "",
        f"**Generated:** {report.generated_at}",
        f"**Organization:** {report.organization_name or 'N/A'}",
        f"**Contact:** {report.contact_email or 'N/A'}",
        "",
        f"**Reporting Period:** {report.reporting_period_start or 'N/A'} to {report.reporting_period_end or 'N/A'}",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"- **Total AI Interactions:** {report.total_ai_interactions}",
        f"- **Unique Models Used:** {report.unique_models_used}",
        f"- **Unique Traces:** {report.unique_traces}",
        f"- **Policy Violations:** {report.policy_violations_count}",
        "",
        "---",
        "",
        "## Risk Category Breakdown",
        "",
        f"| Category | Interactions |",
        f"|----------|--------------|",
        f"| Minimal Risk | {report.risk_category_summary.minimal} |",
        f"| Limited Risk | {report.risk_category_summary.limited} |",
        f"| High Risk | {report.risk_category_summary.high} |",
        f"| Unacceptable Risk | {report.risk_category_summary.unacceptable} |",
        "",
    ]

    # High risk models warning
    if report.high_risk_models:
        lines.extend([
            "### High Risk Models Used",
            "",
        ])
        for model in report.high_risk_models:
            lines.append(f"- {model}")
        lines.append("")

    # Unacceptable risk models warning
    if report.unacceptable_risk_models:
        lines.extend([
            "### Unacceptable Risk Models Used",
            "",
        ])
        for model in report.unacceptable_risk_models:
            lines.append(f"- {model}")
        lines.append("")

    # Model inventory
    lines.extend([
        "---",
        "",
        "## Model Inventory",
        "",
        "| Model | Provider | Risk Category | Calls | Capabilities |",
        "|-------|----------|---------------|-------|--------------|",
    ])
    for m in report.models_used:
        caps = ", ".join(m.capabilities) if m.capabilities else "N/A"
        lines.append(f"| {m.model} | {m.provider} | {m.risk_category} | {m.call_count} | {caps} |")

    # Data classifications
    if report.data_classifications_used:
        lines.extend([
            "",
            "---",
            "",
            "## Data Classifications",
            "",
            "| Classification | Events |",
            "|----------------|--------|",
        ])
        for classification, count in sorted(report.data_classifications_used.items()):
            lines.append(f"| {classification} | {count} |")

    # Policy violations by model
    if report.policy_violations_by_model:
        lines.extend([
            "",
            "---",
            "",
            "## Policy Violations by Model",
            "",
            "| Model | Violations |",
            "|-------|------------|",
        ])
        for model, count in sorted(report.policy_violations_by_model.items()):
            lines.append(f"| {model} | {count} |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Report generated by Monora SDK*")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
