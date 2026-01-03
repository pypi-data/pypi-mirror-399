"""Signed attestation bundle helpers."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class AttestationError(RuntimeError):
    """Raised when attestation signing fails."""


@dataclass
class SignatureResult:
    signature: str
    signature_type: str
    key_id: Optional[str] = None
    fingerprint: Optional[str] = None


def serialize_report(report: Dict[str, Any]) -> bytes:
    return json.dumps(report, indent=2, ensure_ascii=True).encode("utf-8")


def compute_sha256(payload: bytes) -> str:
    digest = hashlib.sha256(payload).hexdigest()
    return f"sha256:{digest}"


def sign_report_gpg(
    report_bytes: bytes,
    *,
    key_id: Optional[str] = None,
    gpg_home: Optional[str] = None,
) -> SignatureResult:
    gpg_bin = shutil.which("gpg")
    if not gpg_bin:
        raise AttestationError("gpg not found on PATH")

    with tempfile.TemporaryDirectory() as tmpdir:
        report_path = f"{tmpdir}/report.json"
        sig_path = f"{tmpdir}/report.json.asc"
        with open(report_path, "wb") as handle:
            handle.write(report_bytes)

        cmd = [gpg_bin, "--armor", "--detach-sign", "--output", sig_path]
        if gpg_home:
            cmd.extend(["--homedir", gpg_home])
        if key_id:
            cmd.extend(["--local-user", key_id])
        cmd.append(report_path)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise AttestationError(result.stderr.strip() or "gpg signing failed")

        with open(sig_path, "r", encoding="utf-8") as handle:
            signature = handle.read()

    fingerprint = _gpg_fingerprint(key_id, gpg_home)
    return SignatureResult(
        signature=signature,
        signature_type="gpg",
        key_id=key_id,
        fingerprint=fingerprint,
    )


def build_attestation_bundle(
    report: Dict[str, Any],
    report_bytes: bytes,
    signature: Optional[SignatureResult] = None,
    *,
    chain_proof: Optional[Dict] = None,
    events_digest: Optional[Dict] = None,
    trace_info: Optional[Dict] = None,
    events: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """Build enhanced attestation bundle with chain proof.

    Args:
        report: Compliance report
        report_bytes: Serialized report
        signature: Optional GPG signature
        chain_proof: Chain verification proof data
        events_digest: Events digest data
        trace_info: Trace metadata
        events: Optional raw events to embed in bundle

    Returns:
        Trust proof bundle (v2.0.0 format if chain_proof provided, v1.0.0 otherwise)
    """
    # Determine bundle version and type
    is_trust_proof = chain_proof is not None
    bundle_version = "2.0.0" if is_trust_proof else "1.0.0"
    bundle_type = "trust_proof" if is_trust_proof else "compliance_report"

    bundle = {
        "bundle_version": bundle_version,
        "bundle_type": bundle_type,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    # Add trace info (v2.0.0 only)
    if trace_info:
        bundle["trace_info"] = trace_info

    # Add chain proof (v2.0.0 only)
    if chain_proof:
        bundle["chain_proof"] = chain_proof

    # Add events digest (v2.0.0 only)
    if events_digest:
        bundle["events_digest"] = events_digest

    # Embed raw events if provided (v2.0.0 only)
    if events:
        bundle["events"] = events

    # Add compliance summary (v2.0.0 only)
    if is_trust_proof:
        bundle["compliance_summary"] = _extract_compliance_summary(report)

    # Add report artifacts (v2.0.0 only)
    if is_trust_proof:
        bundle["report_artifacts"] = report.get("artifacts", [])

    # v1.0.0 format (backward compatibility)
    if not is_trust_proof:
        bundle["report_sha256"] = compute_sha256(report_bytes)
        bundle["report_json"] = report_bytes.decode("utf-8")

    # Add signature if provided
    if signature:
        # For v2.0.0, compute signature over entire bundle (excluding signature itself)
        if is_trust_proof:
            payload = {k: v for k, v in bundle.items() if k != "signature"}
            payload_bytes = serialize_report(payload)
            payload_sha = compute_sha256(payload_bytes)

            bundle["signature"] = {
                "type": signature.signature_type,
                "value": signature.signature,
                "key_id": signature.key_id,
                "fingerprint": signature.fingerprint,
                "signed_at": datetime.now(timezone.utc).isoformat(),
                "signed_payload_sha256": payload_sha,
            }
        else:
            # v1.0.0 format
            bundle["signature"] = {
                "type": signature.signature_type,
                "value": signature.signature,
                "key_id": signature.key_id,
                "fingerprint": signature.fingerprint,
                "signed_at": datetime.now(timezone.utc).isoformat(),
            }

    return bundle


def _extract_compliance_summary(report: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key compliance metrics for bundle.

    Args:
        report: Full compliance report

    Returns:
        Compact compliance summary
    """
    model_compliance = report.get("model_compliance", {})
    violations = report.get("violations", [])
    token_usage = report.get("token_usage", {})

    return {
        "policy_violations": len(violations) if isinstance(violations, list) else 0,
        "data_handling_issues": 0,  # TODO: Extract from data handling events
        "unknown_models": model_compliance.get("unknown_models_used", []),
        "forbidden_models_blocked": len(model_compliance.get("forbidden_models_blocked", [])),
        "total_tokens": token_usage.get("total_tokens", 0),
    }


def _gpg_fingerprint(key_id: Optional[str], gpg_home: Optional[str]) -> Optional[str]:
    if not key_id:
        return None
    gpg_bin = shutil.which("gpg")
    if not gpg_bin:
        return None

    cmd = [gpg_bin, "--with-colons", "--fingerprint", key_id]
    if gpg_home:
        cmd.extend(["--homedir", gpg_home])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    for line in result.stdout.splitlines():
        if not line.startswith("fpr:"):
            continue
        parts = line.split(":")
        for part in reversed(parts):
            if part:
                return part
    return None
