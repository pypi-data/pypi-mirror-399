"""Automatic report generation and trust summary support."""
from __future__ import annotations

import hashlib
import os
import sys
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from monora.attestation import (
    build_attestation_bundle,
    compute_sha256,
    serialize_report,
    sign_report_gpg,
    AttestationError,
)
from monora.cli.report import _build_report, _write_markdown
from monora.cli.security_report import generate_security_report
from monora.verify import compute_events_digest, verify_chain, verify_chain_with_proof

TRUST_SUMMARY_EVENT_TYPE = "trust_summary"


@dataclass
class ReportArtifact:
    report_type: str
    format: str
    path: Optional[str]
    sha256: Optional[str]
    status: str
    error: Optional[str] = None


class TraceReportManager:
    def __init__(self, config: Dict[str, Any]):
        reporting = config.get("reporting", {}) if isinstance(config, dict) else {}
        self.enabled = bool(reporting.get("enabled", True))
        self.emit_trust_summary = bool(reporting.get("emit_trust_summary", True))
        self.output_dir = str(reporting.get("output_dir", "./monora_reports"))
        self.formats = _normalize_formats(reporting.get("formats"))
        self.include_security_report = bool(reporting.get("include_security_report", False))
        self.max_events_per_trace = _coerce_positive_int(
            reporting.get("max_events_per_trace", 10000)
        )
        self._config = config
        self._lock = threading.Lock()
        self._events_by_trace: Dict[str, List[Dict[str, Any]]] = {}
        self._dropped_by_trace: Dict[str, int] = {}

    def record_event(self, event: Dict[str, Any]) -> None:
        if not self.enabled:
            return
        if event.get("event_type") == TRUST_SUMMARY_EVENT_TYPE:
            return
        trace_id = event.get("trace_id")
        if not trace_id:
            return
        with self._lock:
            events = self._events_by_trace.setdefault(trace_id, [])
            if self.max_events_per_trace and len(events) >= self.max_events_per_trace:
                self._dropped_by_trace[trace_id] = (
                    self._dropped_by_trace.get(trace_id, 0) + 1
                )
                return
            events.append(event)

    def get_trace_events(self, trace_id: str) -> Optional[List[Dict[str, Any]]]:
        if not self.enabled:
            return None
        with self._lock:
            events = self._events_by_trace.get(trace_id)
            if not events:
                return None
            return list(events)

    def finalize_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        if not self.enabled:
            return None
        with self._lock:
            events = self._events_by_trace.pop(trace_id, None)
            dropped = self._dropped_by_trace.pop(trace_id, 0)
        if not events:
            return None

        report = _build_report(events, policies=self._config.get("policies"))
        artifacts: List[ReportArtifact] = []
        report_dir = self._resolve_report_dir(trace_id)
        report_paths: Dict[str, str] = {}
        if report_dir:
            try:
                report_dir.mkdir(parents=True, exist_ok=True)
            except Exception as exc:
                print(f"Monora: failed to create report directory: {exc}", file=sys.stderr)
                report_dir = None

        for fmt in self.formats:
            if fmt == "json":
                artifact = _write_json_report(report_dir, report)
            elif fmt in {"markdown", "md"}:
                artifact = _write_markdown_report(report_dir, report)
            else:
                artifact = ReportArtifact(
                    report_type="compliance",
                    format=fmt,
                    path=None,
                    sha256=None,
                    status="skipped",
                    error=f"unsupported format: {fmt}",
                )
            artifacts.append(artifact)
            if artifact.path:
                report_paths[f"{artifact.report_type}.{artifact.format}"] = artifact.path

        if self.include_security_report:
            security_report = generate_security_report(events, config_dict=self._config)
            security_artifact = _write_security_report(report_dir, security_report)
            artifacts.append(security_artifact)
            if security_artifact.path:
                report_paths[
                    f"{security_artifact.report_type}.{security_artifact.format}"
                ] = security_artifact.path

        # AUTOMATIC CHAIN VERIFICATION with proof
        chain_status, chain_error, chain_proof = _verify_chain_status(events, self._config)

        # Build and write trust proof bundle (v2.0.0)
        trust_bundle_path: Optional[str] = None
        immutability = self._config.get("immutability", {}) if isinstance(self._config, dict) else {}
        if immutability.get("enabled", True) and chain_proof is not None:
            trust_bundle = _build_trust_proof_bundle(
                trace_id=trace_id,
                report=report,
                events=events,
                chain_proof=chain_proof,
                artifacts=artifacts,
                config=self._config,
            )
            if trust_bundle:
                trust_artifact = _write_trust_bundle(report_dir, trust_bundle, trace_id)
                artifacts.append(trust_artifact)
                if trust_artifact.path:
                    trust_bundle_path = trust_artifact.path
                    report_paths[
                        f"{trust_artifact.report_type}.{trust_artifact.format}"
                    ] = trust_artifact.path

        compliance = report.get("model_compliance", {}) if isinstance(report, dict) else {}
        summary = {
            "summary_version": "1.1.0",  # Updated version for trust proof support
            "trace_id": trace_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "events": {"captured": len(events), "dropped": dropped},
            "chain_integrity": {
                "status": chain_status,
                "error": chain_error,
                "events_verified": len(events),
                "proof": chain_proof,  # Include full proof data
            },
            "compliance": {
                "total_events": report.get("total_events", 0),
                "total_traces": report.get("traces", 0),
                "policy_violations": len(report.get("violations", [])),
                "unknown_models_used": compliance.get("unknown_models_used", []),
                "forbidden_models_blocked": compliance.get("forbidden_models_blocked", []),
            },
            "artifacts": [artifact.__dict__ for artifact in artifacts],
            "report_paths": report_paths,
            "trust_bundle_path": trust_bundle_path,
        }
        return summary

    def _resolve_report_dir(self, trace_id: str) -> Optional[Path]:
        if not self.output_dir:
            return None
        return Path(self.output_dir) / trace_id

    def get_pending_trace_ids(self) -> List[str]:
        """Return list of trace IDs with pending events.

        Used by shutdown verification to finalize all pending traces.
        """
        with self._lock:
            return list(self._events_by_trace.keys())


def _normalize_formats(value: Any) -> List[str]:
    if value is None:
        return ["json"]
    if isinstance(value, str):
        return [value.strip().lower()]
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip().lower() for item in value if str(item).strip()]
    return ["json"]


def _coerce_positive_int(value: Any) -> Optional[int]:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _resolve_project_name(config: Dict[str, Any]) -> str:
    project_name = (
        os.getenv("MONORA_PROJECT_NAME")
        or os.getenv("PROJECT_NAME")
        or config.get("defaults", {}).get("service_name")
        or "monora"
    )
    if not project_name or project_name == "unknown":
        print("Monora: project name missing; defaulting to 'monora'", file=sys.stderr)
        return "monora"
    return project_name


def _resolve_environment(config: Dict[str, Any]) -> str:
    return config.get("defaults", {}).get("environment") or os.getenv("MONORA_ENV") or "dev"


def _should_redact_host(config: Dict[str, Any]) -> bool:
    reporting = config.get("reporting", {}) if isinstance(config, dict) else {}
    return reporting.get("redact_host", True) is not False


def _redact_event_hosts(events: List[Dict[str, Any]], prefix: str) -> List[Dict[str, Any]]:
    mapping: Dict[str, str] = {}
    redacted: List[Dict[str, Any]] = []
    for event in events:
        if not isinstance(event, dict) or not event.get("host"):
            redacted.append(event)
            continue
        host = str(event.get("host"))
        if host not in mapping:
            hashed = hashlib.sha256(host.encode("utf-8")).hexdigest()[:12]
            mapping[host] = f"{prefix}{hashed}"
        clone = dict(event)
        clone["host"] = mapping[host]
        redacted.append(clone)
    return redacted


def _write_json_report(report_dir: Optional[Path], report: Dict[str, Any]) -> ReportArtifact:
    if report_dir is None:
        return ReportArtifact(
            report_type="compliance",
            format="json",
            path=None,
            sha256=None,
            status="skipped",
            error="output_dir not set",
        )
    path = report_dir / "compliance.json"
    try:
        report_bytes = serialize_report(report)
        path.write_bytes(report_bytes)
        return ReportArtifact(
            report_type="compliance",
            format="json",
            path=str(path),
            sha256=compute_sha256(report_bytes),
            status="generated",
        )
    except Exception as exc:
        return ReportArtifact(
            report_type="compliance",
            format="json",
            path=str(path),
            sha256=None,
            status="error",
            error=str(exc),
        )


def _write_markdown_report(
    report_dir: Optional[Path], report: Dict[str, Any]
) -> ReportArtifact:
    if report_dir is None:
        return ReportArtifact(
            report_type="compliance",
            format="markdown",
            path=None,
            sha256=None,
            status="skipped",
            error="output_dir not set",
        )
    path = report_dir / "compliance.md"
    try:
        _write_markdown(str(path), report)
        return ReportArtifact(
            report_type="compliance",
            format="markdown",
            path=str(path),
            sha256=None,
            status="generated",
        )
    except Exception as exc:
        return ReportArtifact(
            report_type="compliance",
            format="markdown",
            path=str(path),
            sha256=None,
            status="error",
            error=str(exc),
        )


def _write_security_report(
    report_dir: Optional[Path], report: Dict[str, Any]
) -> ReportArtifact:
    if report_dir is None:
        return ReportArtifact(
            report_type="security_review",
            format="json",
            path=None,
            sha256=None,
            status="skipped",
            error="output_dir not set",
        )
    path = report_dir / "security_review.json"
    try:
        report_bytes = serialize_report(report)
        path.write_bytes(report_bytes)
        return ReportArtifact(
            report_type="security_review",
            format="json",
            path=str(path),
            sha256=compute_sha256(report_bytes),
            status="generated",
        )
    except Exception as exc:
        return ReportArtifact(
            report_type="security_review",
            format="json",
            path=str(path),
            sha256=None,
            status="error",
            error=str(exc),
        )


def _verify_chain_status(
    events: List[Dict[str, Any]], config: Dict[str, Any]
) -> Tuple[str, Optional[str], Optional[Dict[str, Any]]]:
    """Verify chain and return status with optional proof data.

    Returns:
        Tuple of (status, error, proof_data)
        - status: "verified", "failed", "disabled", or "global_scope"
        - error: Error message if failed, None otherwise
        - proof_data: Chain proof structure for trust bundles (None if disabled)
    """
    immutability = config.get("immutability", {}) if isinstance(config, dict) else {}
    if immutability.get("enabled") is False:
        return "disabled", None, None
    if immutability.get("scope") == "global":
        return "global_scope", "global chain verification requires cross-trace events", None
    try:
        is_valid, error, proof_data = verify_chain_with_proof(events)
        status = "verified" if is_valid else "failed"
        return status, error, proof_data
    except Exception as exc:
        print(f"Monora: chain verification failed: {exc}", file=sys.stderr)
        return "failed", str(exc), None


def _build_trust_proof_bundle(
    trace_id: str,
    report: Dict[str, Any],
    events: List[Dict[str, Any]],
    chain_proof: Optional[Dict[str, Any]],
    artifacts: List[ReportArtifact],
    config: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Build trust proof bundle with chain verification.

    Args:
        trace_id: Trace identifier
        report: Compliance report
        events: List of events for this trace
        chain_proof: Chain verification proof data
        artifacts: List of generated report artifacts
        config: Monora configuration

    Returns:
        Trust proof bundle (v2.0.0 format), or None if chain proof unavailable
    """
    if chain_proof is None:
        return None

    redact_hosts = _should_redact_host(config)
    redaction_prefix = "host-sha256:"
    sanitized_events = _redact_event_hosts(events, redaction_prefix) if redact_hosts else events

    # Compute events digest
    events_digest_hash = compute_events_digest(sanitized_events)

    # Build artifact list for bundle
    artifact_list = []
    for artifact in artifacts:
        if artifact.status == "generated" and artifact.path:
            artifact_list.append({
                "artifact_type": artifact.report_type,
                "format": artifact.format,
                "path": artifact.path,
                "sha256": artifact.sha256,
            })

    # Get project name from config
    project_name = _resolve_project_name(config)
    environment = _resolve_environment(config)

    # Build the bundle
    report_bytes = serialize_report(report)
    bundle = build_attestation_bundle(
        report=report,
        report_bytes=report_bytes,
        signature=None,  # Will add signature if GPG configured
        chain_proof=chain_proof,
        events_digest={
            "total_events": len(sanitized_events),
            "events_sha256": events_digest_hash,
            "events_included": True,  # Embed events by default (user decision)
            "events_url": None,
        },
        events=sanitized_events,  # Include raw events in bundle (user decision)
        trace_info={
            "trace_id": trace_id,
            "project_name": project_name,
            "environment": environment,
            **(
                {
                    "host_redaction": {
                        "method": "sha256",
                        "prefix": redaction_prefix,
                    }
                }
                if redact_hosts
                else {}
            ),
        },
    )

    # Update artifacts in bundle
    bundle["report_artifacts"] = artifact_list

    # Sign if GPG configured
    attestation_config = config.get("attestation", {}) if isinstance(config, dict) else {}
    gpg_config = attestation_config.get("gpg", {})
    if gpg_config.get("enabled", False):
        try:
            bundle_bytes = serialize_report(bundle)
            sig_result = sign_report_gpg(
                bundle_bytes,
                key_id=gpg_config.get("key_id"),
                gpg_home=gpg_config.get("gpg_home"),
            )
            # Re-build bundle with signature
            bundle = build_attestation_bundle(
                report=report,
                report_bytes=report_bytes,
                signature=sig_result,
                chain_proof=chain_proof,
                events_digest=bundle["events_digest"],
                events=sanitized_events,
                trace_info=bundle["trace_info"],
            )
            bundle["report_artifacts"] = artifact_list
        except AttestationError as exc:
            print(f"Monora: GPG signing failed: {exc}", file=sys.stderr)

    return bundle


def _write_trust_bundle(
    report_dir: Optional[Path], bundle: Dict[str, Any], trace_id: str
) -> ReportArtifact:
    """Write trust proof bundle to file.

    Args:
        report_dir: Directory to write to
        bundle: Trust proof bundle
        trace_id: Trace identifier

    Returns:
        ReportArtifact describing the written file
    """
    if report_dir is None:
        return ReportArtifact(
            report_type="trust_proof",
            format="json",
            path=None,
            sha256=None,
            status="skipped",
            error="output_dir not set",
        )
    path = report_dir / f"{trace_id}_trust_proof.json"
    try:
        bundle_bytes = serialize_report(bundle)
        path.write_bytes(bundle_bytes)
        return ReportArtifact(
            report_type="trust_proof",
            format="json",
            path=str(path),
            sha256=compute_sha256(bundle_bytes),
            status="generated",
        )
    except Exception as exc:
        return ReportArtifact(
            report_type="trust_proof",
            format="json",
            path=str(path),
            sha256=None,
            status="error",
            error=str(exc),
        )
