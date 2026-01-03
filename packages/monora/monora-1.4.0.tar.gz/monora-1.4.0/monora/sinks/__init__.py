"""Sink factory."""
from __future__ import annotations

import os
import sys
from typing import Any, Dict, List

from .base import Sink, SinkError
from .file import FileSink
from .https import HttpSink
from .stdout import StdoutSink


def build_sinks(configs: List[Dict[str, Any]], *, fail_fast: bool = False) -> List[Sink]:
    sinks: List[Sink] = []
    for config in configs:
        sink_type = (config.get("type") or "").lower()
        try:
            if sink_type == "stdout":
                sinks.append(StdoutSink(format=config.get("format", "json")))
            elif sink_type == "file":
                sinks.append(
                    FileSink(
                        config["path"],
                        batch_size=config.get("batch_size", 100),
                        flush_interval_sec=config.get("flush_interval_sec", 5.0),
                        rotation=config.get("rotation", "none"),
                        max_size_mb=config.get("max_size_mb"),
                    )
                )
            elif sink_type == "https":
                headers = _expand_headers(config.get("headers", {}))
                api_key = config.get("api_key")
                if api_key:
                    headers = _inject_api_key(headers, str(api_key))
                sinks.append(
                    HttpSink(
                        config["endpoint"],
                        headers,
                        batch_size=config.get("batch_size", 50),
                        timeout_sec=config.get("timeout_sec", 10.0),
                        retry_attempts=config.get("retry_attempts", 3),
                        backoff_base_sec=config.get("backoff_base_sec", 0.5),
                    )
                )
            else:
                raise ValueError(f"Unknown sink type: {sink_type}")
        except Exception as exc:
            if fail_fast:
                raise
            print(f"Monora: failed to init sink {sink_type}: {exc}", file=sys.stderr)
    return sinks


def _expand_headers(headers: Dict[str, Any]) -> Dict[str, str]:
    expanded: Dict[str, str] = {}
    for key, value in headers.items():
        expanded[key] = _expand_env(str(value))
    return expanded


def _inject_api_key(headers: Dict[str, str], api_key: str) -> Dict[str, str]:
    if _has_header(headers, "Authorization"):
        return headers
    resolved = _resolve_api_key(api_key)
    if not resolved:
        return headers
    headers = dict(headers)
    headers["Authorization"] = f"Bearer {resolved}"
    return headers


def _resolve_api_key(value: str) -> str:
    if not value:
        return ""
    env_value = os.getenv(value)
    return env_value if env_value is not None else value


def _has_header(headers: Dict[str, str], header_name: str) -> bool:
    header_name = header_name.lower()
    return any(key.lower() == header_name for key in headers)


def _expand_env(value: str) -> str:
    if "${" not in value:
        return value
    result = value
    for part in value.split("${"):
        if "}" not in part:
            continue
        env_key = part.split("}")[0]
        env_val = os.getenv(env_key, "")
        result = result.replace(f"${{{env_key}}}", env_val)
    return result


__all__ = [
    "Sink",
    "SinkError",
    "StdoutSink",
    "FileSink",
    "HttpSink",
    "build_sinks",
]
