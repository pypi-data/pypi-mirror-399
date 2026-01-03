"""Configuration loading and normalization."""
from __future__ import annotations

import json
import os
from copy import deepcopy
from typing import Any, Dict, List, Optional

try:
    import yaml
except Exception:  # pragma: no cover - optional import
    yaml = None


DEFAULT_CONFIG: Dict[str, Any] = {
    "defaults": {
        "data_classification": "internal",
        "purpose": "general",
        "service_name": None,
        "environment": "dev",
    },
    "sinks": [
        {"type": "stdout", "format": "json"},
    ],
    "immutability": {
        "enabled": True,
        "scope": "per_trace",
        "hash_algorithm": "sha256",
        "verify_on_emit": False,  # Real-time verification (default: off for performance)
        "verify_on_shutdown": True,  # Automatic verification on shutdown (default: on)
        "persist_chain": False,  # Write chain snapshots to disk
    },
    "attestation": {
        "enabled": False,
        "gpg": {
            "enabled": False,
            "key_id": None,
            "gpg_home": None,
        },
    },
    "registry": {
        "version": "1.0.0",
        "history": [],
        "default_provider": "unknown",
        "allow_unknown": True,
        "providers": [
            {"name": "openai", "model_patterns": ["gpt-*", "o1-*"]},
            {"name": "anthropic", "model_patterns": ["claude-*"]},
            {"name": "deepseek", "model_patterns": ["deepseek:*", "deepseek*"]},
        ],
    },
    "instrumentation": {
        "enabled": False,
        "targets": ["openai", "anthropic"],
        "default_purpose": None,
        "data_classification": None,
        "reason": None,
        "fail_fast": False,
    },
    "tracing": {
        "emit_span_events": True,
    },
    "reporting": {
        "enabled": True,
        "emit_trust_summary": True,
        "output_dir": "./monora_reports",
        "formats": ["json"],
        "include_security_report": False,
        "max_events_per_trace": 10000,
        "redact_host": True,
    },
    "data_handling": {
        "enabled": False,
        "mode": "redact",
        "apply_to": [
            "request",
            "response",
            "tool_args",
            "tool_result",
            "agent_input",
            "agent_output",
            "custom",
        ],
        "rules": [],
    },
    "policies": {
        "model_allowlist": [],
        "model_denylist": [],
        "classification_max_models": {},
        "enforce": True,
    },
    "alerts": {
        "violation_webhook": None,
        "headers": {},
        "timeout_sec": 5.0,
        "retry_attempts": 3,
        "backoff_base_sec": 0.5,
        "queue_size": 200,
    },
    "error_handling": {
        "sink_failure_mode": "warn",
        "log_user_exceptions": True,
        "queue_full_mode": "warn",
        "fallback_path": "./monora_fallback.jsonl",
    },
    "buffering": {
        "queue_size": 1000,
        "batch_size": 50,
        "flush_interval_sec": 1.0,
        "queue_full_timeout_sec": None,
    },
    "wal": {
        "enabled": False,
        "path": "./monora_wal",
        "sync_mode": "fsync",  # fsync | async | none
        "max_file_size_mb": 100,
        "retention_hours": 24,
        "recovery_on_startup": True,
    },
    "signing": {
        "enabled": False,
        "algorithm": "ed25519",  # ed25519 | hmac-sha256
        "key_id": None,
        "key_file": None,
        "key_env": "MONORA_SIGNING_KEY",
    },
    "ai_act": {
        "enabled": False,
        "organization_name": None,
        "contact_email": None,
        "default_risk_category": "limited",
        "generate_transparency_report": True,
        "transparency_report_formats": ["json"],
    },
}


def load_config(
    *,
    config_path: Optional[str] = None,
    config_dict: Optional[Dict[str, Any]] = None,
    env_prefix: str = "MONORA_",
) -> Dict[str, Any]:
    """Load config with precedence: dict > file > env > defaults."""
    config = deepcopy(DEFAULT_CONFIG)

    env_config = _config_from_env(env_prefix)
    _merge_dicts(config, env_config)

    if config_path:
        file_config = _load_config_file(config_path)
        _merge_dicts(config, file_config)

    if config_dict:
        _merge_dicts(config, config_dict)

    # Expand environment variables in string values
    _expand_env_vars(config)
    _normalize_legacy_config(config)

    return config


def _load_config_file(config_path: str) -> Dict[str, Any]:
    if not os.path.exists(config_path):
        raise FileNotFoundError(config_path)
    with open(config_path, "r", encoding="utf-8") as handle:
        raw = handle.read()
    if config_path.endswith(".json"):
        return json.loads(raw) if raw.strip() else {}
    if yaml is None:
        raise RuntimeError("PyYAML is required to load YAML config files")
    return yaml.safe_load(raw) or {}


def _config_from_env(prefix: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in os.environ.items():
        if not key.startswith(prefix):
            continue
        path = _env_key_to_path(key[len(prefix) :])
        if not path:
            continue
        _set_path_value(result, path, _parse_env_value(value))
    return result


def _env_key_to_path(key: str) -> list[Any]:
    parts = [part for part in key.split("_") if part]
    if not parts:
        return []

    if len(parts) >= 2 and parts[0].upper() == "DATA" and parts[1].upper() == "HANDLING":
        root = "data_handling"
        rest = parts[2:]
    elif len(parts) >= 2 and parts[0].upper() == "ERROR" and parts[1].upper() == "HANDLING":
        root = "error_handling"
        rest = parts[2:]
    else:
        root = parts[0].lower()
        rest = parts[1:]

    if root == "policies" and rest[:3] == ["CLASSIFICATION", "MAX", "MODELS"]:
        if len(rest) < 5:
            return []
        classification = rest[3].lower()
        tail = rest[4:]
        return ["policies", "classification_max_models", classification, "_".join(tail).lower()]

    path: list[Any] = [root]
    buffer: list[str] = []
    for part in rest:
        if part.isdigit():
            if buffer:
                path.append("_".join(buffer).lower())
                buffer = []
            path.append(int(part))
        else:
            buffer.append(part)
    if buffer:
        path.append("_".join(buffer).lower())
    return path


def _set_path_value(target: Dict[str, Any], path: list[Any], value: Any) -> None:
    cursor: Any = target
    for idx, segment in enumerate(path):
        is_last = idx == len(path) - 1
        if isinstance(segment, int):
            if not isinstance(cursor, list):
                cursor_path = path[: idx]
                container = []
                if cursor_path:
                    _assign_container(target, cursor_path, container)
                cursor = container
            while len(cursor) <= segment:
                cursor.append({})
            if is_last:
                cursor[segment] = value
            else:
                if not isinstance(cursor[segment], (dict, list)):
                    cursor[segment] = {}
                cursor = cursor[segment]
        else:
            if is_last:
                cursor[segment] = value
            else:
                if segment not in cursor or not isinstance(cursor[segment], (dict, list)):
                    cursor[segment] = {}
                cursor = cursor[segment]


def _assign_container(target: Dict[str, Any], path: list[Any], container: Any) -> None:
    cursor: Any = target
    for segment in path[:-1]:
        if isinstance(segment, int):
            while len(cursor) <= segment:
                cursor.append({})
            cursor = cursor[segment]
        else:
            cursor = cursor.setdefault(segment, {})
    last = path[-1]
    if isinstance(last, int):
        while len(cursor) <= last:
            cursor.append({})
        cursor[last] = container
    else:
        cursor[last] = container


def _parse_env_value(value: str) -> Any:
    raw = value.strip()
    if not raw:
        return ""
    lowered = raw.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none"}:
        return None
    if raw.startswith("[") or raw.startswith("{"):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw
    if "," in raw:
        return [item.strip() for item in raw.split(",") if item.strip()]
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        return raw


def _merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> None:
    for key, value in (override or {}).items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _merge_dicts(base[key], value)
        elif key in base and isinstance(base[key], list) and isinstance(value, list):
            for idx, item in enumerate(value):
                if idx < len(base[key]) and isinstance(base[key][idx], dict) and isinstance(item, dict):
                    _merge_dicts(base[key][idx], item)
                else:
                    if idx >= len(base[key]):
                        base[key].append(item)
                    else:
                        base[key][idx] = item
        else:
            base[key] = value


def _expand_env_vars(obj: Any) -> None:
    """Expand environment variables in config strings.

    Supports ${VAR_NAME} and $VAR_NAME syntax.
    Modifies the object in-place.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str):
                obj[key] = os.path.expandvars(value)
            elif isinstance(value, (dict, list)):
                _expand_env_vars(value)
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            if isinstance(item, str):
                obj[idx] = os.path.expandvars(item)
            elif isinstance(item, (dict, list)):
                _expand_env_vars(item)


def _normalize_legacy_config(config: Dict[str, Any]) -> None:
    logging_cfg = config.get("logging")
    http_cfg = config.get("http_sink")
    env_value = config.get("env")
    defaults = config.setdefault("defaults", {})

    default_env = DEFAULT_CONFIG.get("defaults", {}).get("environment")
    if env_value and defaults.get("environment") == default_env:
        defaults["environment"] = env_value

    if isinstance(config.get("policies"), dict):
        policies = config["policies"]
        if "allowed_models" in policies and "model_allowlist" not in policies:
            policies["model_allowlist"] = policies["allowed_models"]
        if "forbidden_models" in policies and "model_denylist" not in policies:
            policies["model_denylist"] = policies["forbidden_models"]

    if isinstance(logging_cfg, dict) and _uses_default_sinks(config.get("sinks")):
        sink_config = _sink_from_logging(logging_cfg, http_cfg if isinstance(http_cfg, dict) else {})
        if sink_config:
            config["sinks"] = [sink_config]


def _uses_default_sinks(sinks: Optional[List[Any]]) -> bool:
    return sinks == DEFAULT_CONFIG.get("sinks")


def _sink_from_logging(logging_cfg: Dict[str, Any], http_cfg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    sink_type = (logging_cfg.get("sink") or "").lower()
    if sink_type == "stdout":
        return {"type": "stdout"}
    if sink_type == "file":
        return {
            "type": "file",
            "path": logging_cfg.get("file_path", "./monora.log"),
        }
    if sink_type == "https":
        endpoint = http_cfg.get("endpoint")
        if not endpoint:
            return None
        sink: Dict[str, Any] = {"type": "https", "endpoint": endpoint}
        if "headers" in http_cfg:
            sink["headers"] = http_cfg["headers"]
        if "api_key" in http_cfg:
            sink["api_key"] = http_cfg["api_key"]
        return sink
    return None
