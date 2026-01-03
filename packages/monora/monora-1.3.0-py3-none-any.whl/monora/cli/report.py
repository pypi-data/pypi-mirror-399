"""CLI reporting for Monora logs."""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Set

import click

from monora.config import load_config
from monora.policy import compile_patterns
from monora.cli.init import init_command
from monora.cli.diagnostics import validate_command, doctor_command

def _load_jsonl(path: str) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError as exc:
                print(f"Monora: skipping invalid JSON line: {exc}", file=sys.stderr)
    return events


def _parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _format_timestamp(value: Optional[str]) -> Optional[str]:
    parsed = _parse_timestamp(value)
    if parsed is None:
        return value
    return parsed.astimezone(timezone.utc).isoformat(timespec="microseconds")


def _normalize_model(model: Optional[str]) -> Optional[str]:
    if not model:
        return None
    return str(model).strip().lower()


def _coerce_token(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number


def _build_report(
    events: List[Dict[str, Any]], policies: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    filtered_events = [
        event for event in events if event.get("event_type") != "trust_summary"
    ]
    trace_ids = {e.get("trace_id") for e in filtered_events if e.get("trace_id")}
    timestamps = [
        ts
        for ts in (_parse_timestamp(e.get("timestamp")) for e in filtered_events)
        if ts is not None
    ]
    start = min(timestamps).astimezone(timezone.utc).isoformat() if timestamps else None
    end = max(timestamps).astimezone(timezone.utc).isoformat() if timestamps else None

    by_event_type = Counter(
        e.get("event_type") for e in filtered_events if e.get("event_type")
    )
    by_purpose = Counter(e.get("purpose") for e in filtered_events if e.get("purpose"))
    by_classification = Counter(
        e.get("data_classification")
        for e in filtered_events
        if e.get("data_classification")
    )

    by_model = Counter()
    token_usage = {
        "total_prompt_tokens": 0,
        "total_completion_tokens": 0,
        "total_tokens": 0,
        "by_model": defaultdict(lambda: {"prompt": 0, "completion": 0, "total": 0}),
        "missing_usage_events": 0,
        "missing_usage_models": set(),
    }

    violations = []
    errors = []
    models_used = set()
    forbidden_models_blocked = set()
    unknown_models_used = set()
    allowed_models_used = set()
    allowlist_patterns: List[Tuple[str, Any]] = []
    denylist_patterns: List[Tuple[str, Any]] = []
    used_allowlist_patterns: Set[str] = set()

    for event in filtered_events:
        body = event.get("body", {})
        event_type = event.get("event_type")
        if event_type == "llm_call":
            model = _normalize_model(body.get("model"))
            if model:
                by_model[model] += 1
                models_used.add(model)
            response = body.get("response")
            if isinstance(response, dict):
                usage = response.get("usage")
                if isinstance(usage, dict):
                    prompt_val = _coerce_token(usage.get("prompt_tokens"))
                    completion_val = _coerce_token(usage.get("completion_tokens"))
                    total_val = _coerce_token(usage.get("total_tokens"))
                    if prompt_val is None and completion_val is None and total_val is None:
                        token_usage["missing_usage_events"] += 1
                        if model:
                            token_usage["missing_usage_models"].add(model)
                    else:
                        prompt = prompt_val or 0
                        completion = completion_val or 0
                        total = total_val or prompt + completion
                        token_usage["total_prompt_tokens"] += prompt
                        token_usage["total_completion_tokens"] += completion
                        token_usage["total_tokens"] += total
                        if model:
                            token_usage["by_model"][model]["prompt"] += prompt
                            token_usage["by_model"][model]["completion"] += completion
                            token_usage["by_model"][model]["total"] += total
                else:
                    token_usage["missing_usage_events"] += 1
                    if model:
                        token_usage["missing_usage_models"].add(model)

        if body.get("status") == "policy_violation":
            policy_name = body.get("policy_name") or "UNKNOWN_POLICY"
            message = body.get("message") or "Policy violation recorded"
            violations.append(
                {
                    "timestamp": _format_timestamp(event.get("timestamp")),
                    "model": _normalize_model(body.get("model")),
                    "policy": policy_name,
                    "message": message,
                }
            )
            model = _normalize_model(body.get("model"))
            if model:
                forbidden_models_blocked.add(model)

        if body.get("error"):
            errors.append(
                {
                    "timestamp": event.get("timestamp"),
                    "event_type": event_type,
                    "error": body.get("error"),
                }
            )

    if policies:
        allowlist_patterns = compile_patterns(policies.get("model_allowlist", []))
        denylist_patterns = compile_patterns(policies.get("model_denylist", []))

        for model in models_used:
            if model in forbidden_models_blocked:
                continue
            allow_match = (
                bool(allowlist_patterns)
                and _matches_any(allowlist_patterns, model, used_allowlist_patterns)
            )
            deny_match = bool(denylist_patterns) and _matches_any(
                denylist_patterns, model, None
            )
            if allow_match:
                allowed_models_used.add(model)
            elif deny_match:
                forbidden_models_blocked.add(model)
            elif allowlist_patterns:
                unknown_models_used.add(model)
            else:
                allowed_models_used.add(model)
    else:
        allowed_models_used = set(models_used)

    unknown_models_used -= allowed_models_used
    unknown_models_used -= forbidden_models_blocked

    unused_allowlist_patterns = []
    if allowlist_patterns:
        unused_allowlist_patterns = sorted(
            {raw for raw, _ in allowlist_patterns if raw not in used_allowlist_patterns}
        )

    model_compliance = {
        "allowed_models_used": sorted(allowed_models_used),
        "forbidden_models_blocked": sorted(forbidden_models_blocked),
        "unknown_models_used": sorted(unknown_models_used) if policies else [],
        "unused_allowlist_patterns": unused_allowlist_patterns,
    }

    return {
        "total_events": len(filtered_events),
        "traces": len(trace_ids),
        "date_range": {"start": start, "end": end},
        "by_event_type": dict(by_event_type),
        "by_model": dict(by_model),
        "by_purpose": dict(by_purpose),
        "by_classification": dict(by_classification),
        "violations": violations,
        "errors": errors,
        "token_usage": {
            "total_prompt_tokens": token_usage["total_prompt_tokens"],
            "total_completion_tokens": token_usage["total_completion_tokens"],
            "total_tokens": token_usage["total_tokens"],
            "by_model": dict(token_usage["by_model"]),
            "missing_usage_events": token_usage["missing_usage_events"],
            "missing_usage_models": sorted(token_usage["missing_usage_models"]),
        },
        "model_compliance": model_compliance,
    }


def _write_json(path: str, report: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)


def _write_markdown(path: str, report: Dict[str, Any]) -> None:
    lines = [
        "# Monora Compliance Report",
        f"**Period:** {report['date_range']['start']} to {report['date_range']['end']}",
        f"**Total Events:** {report['total_events']}",
        f"**Traces:** {report['traces']}",
        "",
        "## Event Breakdown",
    ]
    for event_type, count in report["by_event_type"].items():
        lines.append(f"- **{event_type}:** {count}")

    lines.append("")
    lines.append("## Models Used")
    for model, count in report["by_model"].items():
        lines.append(f"- {model}: {count} calls")

    violations = report.get("violations", [])
    lines.append("")
    lines.append(f"## Policy Violations ({len(violations)})")
    if violations:
        lines.append("| Timestamp | Model | Policy | Message |")
        lines.append("|-----------|-------|--------|---------|")
        for violation in violations:
            lines.append(
                f"| {violation['timestamp']} | {violation['model']} | {violation['policy']} | {violation['message']} |"
            )

    errors = report.get("errors", [])
    lines.append("")
    lines.append(f"## Errors ({len(errors)})")
    for error in errors:
        lines.append(
            f"- {error['timestamp']} ({error['event_type']}): {error['error']}"
        )

    compliance = report.get("model_compliance", {})
    if compliance:
        lines.append("")
        lines.append("## Model Compliance")
        lines.append(f"- Allowed models used: {', '.join(compliance.get('allowed_models_used', [])) or 'None'}")
        lines.append(
            f"- Forbidden models blocked: {', '.join(compliance.get('forbidden_models_blocked', [])) or 'None'}"
        )
        lines.append(
            f"- Unknown models used: {', '.join(compliance.get('unknown_models_used', [])) or 'None'}"
        )
        lines.append(
            f"- Unused allowlist patterns: {', '.join(compliance.get('unused_allowlist_patterns', [])) or 'None'}"
        )

    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


@click.group()
def cli() -> None:
    """Monora CLI."""


cli.add_command(init_command)
cli.add_command(validate_command)
cli.add_command(doctor_command)


@cli.command()
@click.option("--input", "input_path", required=True, help="Path to JSON-lines event log")
@click.option("--output", "output_path", required=True, help="Output file path")
@click.option("--config", "config_path", required=False, help="Path to config YAML/JSON")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "markdown"]),
    default="json",
)
def report(
    input_path: str, output_path: str, output_format: str, config_path: Optional[str]
) -> None:
    """Generate a compliance report from JSON-lines logs."""
    events = _load_jsonl(input_path)
    policies = _load_policies(config_path) if config_path else None
    report_data = _build_report(events, policies=policies)
    if output_format == "json":
        _write_json(output_path, report_data)
    else:
        _write_markdown(output_path, report_data)


@cli.command()
@click.option("--input", "input_path", required=True, help="Path to JSON-lines event log")
@click.option("--output", "output_path", required=True, help="Output file path")
@click.option("--config", "config_path", required=False, help="Path to config YAML/JSON")
@click.option(
    "--sign",
    "signing_type",
    type=click.Choice(["gpg"]),
    required=False,
    help="Create a signed attestation bundle",
)
@click.option("--gpg-key", "gpg_key", required=False, help="GPG key ID/email for signing")
@click.option("--gpg-home", "gpg_home", required=False, help="GPG home directory")
@click.option(
    "--bundle",
    "bundle_path",
    required=False,
    help="Output path for attestation bundle (defaults to <output>.bundle.json)",
)
def security_review(
    input_path: str,
    output_path: str,
    config_path: Optional[str],
    signing_type: Optional[str],
    gpg_key: Optional[str],
    gpg_home: Optional[str],
    bundle_path: Optional[str],
) -> None:
    """Generate a security review report with attestations."""
    from monora.cli.security_report import generate_security_report
    from monora.attestation import (
        AttestationError,
        build_attestation_bundle,
        serialize_report,
        sign_report_gpg,
    )

    events = _load_jsonl(input_path)
    report = generate_security_report(events, config_path=config_path)

    report_bytes = serialize_report(report)
    with open(output_path, "wb") as f:
        f.write(report_bytes)

    bundle_output = None
    if signing_type:
        try:
            if signing_type == "gpg":
                signature = sign_report_gpg(
                    report_bytes, key_id=gpg_key, gpg_home=gpg_home
                )
            else:
                raise AttestationError(f"Unsupported signing type: {signing_type}")
        except AttestationError as exc:
            raise click.ClickException(f"Signing failed: {exc}") from exc

        bundle = build_attestation_bundle(report, report_bytes, signature)
        bundle_output = bundle_path or f"{output_path}.bundle.json"
        with open(bundle_output, "w", encoding="utf-8") as f:
            json.dump(bundle, f, indent=2)

    click.echo(f"Security review report generated: {output_path}")
    if bundle_output:
        click.echo(f"Attestation bundle generated: {bundle_output}")


@cli.command("trust-package")
@click.option("--input", "input_path", required=True, help="Path to JSON-lines event log")
@click.option("--trace-id", "trace_id", required=True, help="Trace ID to export")
@click.option("--output", "output_path", required=True, help="Output file path")
@click.option("--config", "config_path", required=False, help="Path to config YAML/JSON")
@click.option(
    "--sign",
    "signing_type",
    type=click.Choice(["gpg"]),
    required=False,
    help="Create a signed trust package",
)
@click.option("--gpg-key", "gpg_key", required=False, help="GPG key ID/email for signing")
@click.option("--gpg-home", "gpg_home", required=False, help="GPG home directory")
def trust_package(
    input_path: str,
    trace_id: str,
    output_path: str,
    config_path: Optional[str],
    signing_type: Optional[str],
    gpg_key: Optional[str],
    gpg_home: Optional[str],
) -> None:
    """Generate a vendor trust package for a specific trace."""
    from monora.trust_package import export_trust_package

    events = _load_jsonl(input_path)
    if signing_type and signing_type != "gpg":
        raise click.ClickException(f"Unsupported signing type: {signing_type}")

    export_trust_package(
        trace_id=trace_id,
        events=events,
        config_path=config_path,
        sign=bool(signing_type),
        gpg_key=gpg_key,
        gpg_home=gpg_home,
        output_path=output_path,
    )
    click.echo(f"Trust package generated: {output_path}")


@cli.command("ai-act-report")
@click.option("--input", "input_path", required=True, help="Path to JSON-lines event log")
@click.option("--output", "output_path", required=True, help="Output file path")
@click.option("--config", "config_path", required=False, help="Path to config YAML/JSON")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "markdown"]),
    default="json",
)
def ai_act_report(
    input_path: str, output_path: str, output_format: str, config_path: Optional[str]
) -> None:
    """Generate EU AI Act transparency report.

    Creates a transparency report compliant with the EU AI Act (2024/1689),
    including risk classification, model inventory, and compliance metrics.
    """
    from monora.ai_act_report import build_ai_act_report, write_ai_act_report

    events = _load_jsonl(input_path)
    config = load_config(config_path=config_path) if config_path else {}
    report = build_ai_act_report(events, config)
    write_ai_act_report(report, output_path, output_format)
    click.echo(f"AI Act transparency report generated: {output_path}")


if __name__ == "__main__":
    cli()


def _load_policies(config_path: str) -> Dict[str, Any]:
    try:
        config = load_config(config_path=config_path)
    except Exception as exc:
        raise click.ClickException(f"Failed to load config: {exc}") from exc
    return config.get("policies", {})


def _matches_any(
    patterns: List[Tuple[str, Any]],
    model: str,
    used_patterns: Optional[set],
) -> bool:
    for raw, pattern in patterns:
        if pattern.match(model):
            if used_patterns is not None:
                used_patterns.add(raw)
            return True
    return False
