"""Trust package export utilities."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .attestation import SignatureResult, serialize_report, sign_report_gpg
from .cli.report import _build_report
from .config import load_config
from .reporting import TRUST_SUMMARY_EVENT_TYPE
from .runtime import get_state
from .verify import verify_chain


def export_trust_package(
    *,
    trace_id: str,
    events: Optional[Iterable[Dict[str, Any]]] = None,
    input_path: Optional[str] = None,
    config_path: Optional[str] = None,
    config_dict: Optional[Dict[str, Any]] = None,
    sign: bool = False,
    gpg_key: Optional[str] = None,
    gpg_home: Optional[str] = None,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Export a vendor trust package for a specific trace."""
    config = _resolve_config(config_path=config_path, config_dict=config_dict)
    trace_events = _resolve_trace_events(
        trace_id=trace_id,
        events=events,
        input_path=input_path,
        config=config,
    )

    compliance_report = _build_report(trace_events, policies=config.get("policies"))
    config_snapshot = _build_config_snapshot(config)
    chain_proof = _build_hash_chain_proof(trace_events, config, trace_id)

    trust_package: Dict[str, Any] = {
        "trust_package_version": "1.0.0",
        "trace_id": trace_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "compliance_report": compliance_report,
        "hash_chain_proof": chain_proof,
        "config_snapshot": config_snapshot,
        "gpg_signature": None,
    }

    if sign or gpg_key or gpg_home:
        signature = _sign_trust_package(trust_package, gpg_key=gpg_key, gpg_home=gpg_home)
        trust_package["gpg_signature"] = signature.signature
        trust_package["gpg_signature_metadata"] = {
            "type": signature.signature_type,
            "key_id": signature.key_id,
            "fingerprint": signature.fingerprint,
        }

    if output_path:
        _write_trust_package(output_path, trust_package)

    return trust_package


def _resolve_config(
    *, config_path: Optional[str], config_dict: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    if config_path or config_dict:
        return load_config(config_path=config_path, config_dict=config_dict)
    state = get_state()
    if state:
        return state.config
    return load_config()


def _resolve_trace_events(
    *,
    trace_id: str,
    events: Optional[Iterable[Dict[str, Any]]],
    input_path: Optional[str],
    config: Dict[str, Any],
) -> List[Dict[str, Any]]:
    if events is not None:
        return _filter_trace_events(events, trace_id)

    state = get_state()
    if state and getattr(state, "report_manager", None):
        manager = state.report_manager
        stored = manager.get_trace_events(trace_id)
        if stored:
            return _filter_trace_events(stored, trace_id)

    resolved_path = input_path or _find_event_source(config)
    if resolved_path:
        return _filter_trace_events(_load_jsonl(resolved_path), trace_id)

    raise ValueError(
        "No events found for trace; provide events, input_path, or configure a file sink."
    )


def _filter_trace_events(
    events: Iterable[Dict[str, Any]], trace_id: str
) -> List[Dict[str, Any]]:
    filtered = [
        event
        for event in events
        if event.get("trace_id") == trace_id
        and event.get("event_type") != TRUST_SUMMARY_EVENT_TYPE
    ]
    if not filtered:
        raise ValueError(f"No events found for trace_id={trace_id}")
    return _sort_events(filtered)


def _sort_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    def sort_key(event: Dict[str, Any]) -> Tuple[int, Any]:
        seq = event.get("event_sequence")
        if isinstance(seq, int):
            return (0, seq)
        return (1, event.get("timestamp") or "")

    return sorted(events, key=sort_key)


def _find_event_source(config: Dict[str, Any]) -> Optional[str]:
    for sink in config.get("sinks", []):
        if str(sink.get("type", "")).lower() == "file" and sink.get("path"):
            return str(sink["path"])
    fallback = config.get("error_handling", {}).get("fallback_path")
    return str(fallback) if fallback else None


def _load_jsonl(path: str) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def _build_config_snapshot(config: Dict[str, Any]) -> Dict[str, Any]:
    config_json = json.dumps(config, sort_keys=True, separators=(",", ":"))
    config_hash = hashlib.sha256(config_json.encode()).hexdigest()
    return {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "config_hash": f"sha256:{config_hash}",
        "policies": config.get("policies", {}),
        "immutability": config.get("immutability", {}),
        "defaults": config.get("defaults", {}),
        "registry": config.get("registry", {}),
    }


def _build_hash_chain_proof(
    events: List[Dict[str, Any]], config: Dict[str, Any], trace_id: str
) -> Dict[str, Any]:
    immutability = config.get("immutability", {})
    scope = immutability.get("scope", "per_trace")
    algorithm = immutability.get("hash_algorithm", "sha256")
    status, error = _verify_chain_status(events, config)
    chain = [
        {
            "event_id": event.get("event_id"),
            "event_hash": event.get("event_hash"),
            "prev_hash": event.get("prev_hash"),
            "event_sequence": event.get("event_sequence"),
            "timestamp": event.get("timestamp"),
        }
        for event in events
    ]
    chain_root = chain[0]["event_hash"] if chain else None
    chain_head = chain[-1]["event_hash"] if chain else None
    return {
        "trace_id": trace_id,
        "scope": scope,
        "hash_algorithm": algorithm,
        "verification_status": status,
        "verification_error": error,
        "event_count": len(events),
        "chain_root": chain_root,
        "chain_head": chain_head,
        "chain": chain,
    }


def _verify_chain_status(
    events: List[Dict[str, Any]], config: Dict[str, Any]
) -> Tuple[str, Optional[str]]:
    immutability = config.get("immutability", {})
    if immutability.get("enabled") is False:
        return "disabled", None
    if immutability.get("scope") == "global":
        return "global_scope", "global chain verification requires cross-trace events"
    is_valid, error = verify_chain(events)
    return ("verified", None) if is_valid else ("failed", error)


def _sign_trust_package(
    trust_package: Dict[str, Any],
    *,
    gpg_key: Optional[str],
    gpg_home: Optional[str],
) -> SignatureResult:
    payload = dict(trust_package)
    payload.pop("gpg_signature", None)
    payload.pop("gpg_signature_metadata", None)
    report_bytes = serialize_report(payload)
    return sign_report_gpg(report_bytes, key_id=gpg_key, gpg_home=gpg_home)


def _write_trust_package(path: str, trust_package: Dict[str, Any]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_bytes = serialize_report(trust_package)
    output_path.write_bytes(report_bytes)
