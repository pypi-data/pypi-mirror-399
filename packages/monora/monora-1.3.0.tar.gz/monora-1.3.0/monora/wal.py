"""Write-Ahead Log (WAL) for crash-resilient event persistence.

The WAL ensures events are durably written to disk before being processed,
allowing recovery of uncommitted events after a crash.
"""
from __future__ import annotations

import json
import os
import re
import threading
import time
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional


@dataclass
class WALEntry:
    """A single entry in the write-ahead log."""

    lsn: int  # Log Sequence Number
    status: str  # "pending" | "committed"
    timestamp: str
    event: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: Dict[str, Any] = {
            "lsn": self.lsn,
            "status": self.status,
            "timestamp": self.timestamp,
        }
        if self.event is not None:
            result["event"] = self.event
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WALEntry":
        """Create from dictionary."""
        return cls(
            lsn=data["lsn"],
            status=data["status"],
            timestamp=data["timestamp"],
            event=data.get("event"),
        )


@dataclass
class WALConfig:
    """Configuration for the Write-Ahead Log."""

    enabled: bool = False
    path: str = "./monora_wal"
    sync_mode: str = "fsync"  # fsync | async | none
    max_file_size_mb: int = 100
    retention_hours: int = 24
    recovery_on_startup: bool = True


class WriteAheadLog:
    """Write-Ahead Log for crash-resilient event persistence.

    Events are written to the WAL before being processed. After successful
    processing, they are marked as committed. On startup, uncommitted events
    are replayed to ensure no data loss.

    Example:
        >>> wal = WriteAheadLog(WALConfig(enabled=True, path="./wal"))
        >>> lsn = wal.write({"event_id": "evt_123", ...})
        >>> # Process event through sinks
        >>> wal.commit(lsn)
    """

    def __init__(self, config: WALConfig):
        self.config = config
        self._lock = threading.Lock()
        self._current_lsn = 0
        self._file_handle: Optional[Any] = None
        self._current_file_path: Optional[Path] = None
        self._current_file_size = 0

        if config.enabled:
            self._ensure_wal_directory()
            self._load_current_lsn()

    def _ensure_wal_directory(self) -> None:
        """Create WAL directory if it doesn't exist."""
        Path(self.config.path).mkdir(parents=True, exist_ok=True)

    def _load_current_lsn(self) -> None:
        """Load the highest LSN from existing WAL files."""
        wal_path = Path(self.config.path)
        meta_path = self._meta_path()
        if meta_path.exists():
            try:
                data = json.loads(meta_path.read_text(encoding="utf-8"))
                max_lsn = int(data.get("max_lsn", 0))
                self._current_lsn = max(max_lsn, 0)
                return
            except (ValueError, OSError, json.JSONDecodeError):
                pass

        wal_files = sorted(
            wal_path.glob("*.wal"),
            key=lambda path: path.stat().st_mtime if path.exists() else 0,
        )
        if not wal_files:
            self._current_lsn = 0
            return

        latest = wal_files[-1]
        match = re.search(r"(?:lsn|seq)(\d+)", latest.stem)
        if match:
            self._current_lsn = int(match.group(1))
            return

        max_lsn = 0
        for entry in self._read_entries_from_file(latest):
            if entry.lsn > max_lsn:
                max_lsn = entry.lsn
        self._current_lsn = max_lsn

    def _meta_path(self) -> Path:
        return Path(self.config.path) / "wal_meta.json"

    def _get_current_file_path(self) -> Path:
        """Get the path to the current WAL file."""
        if self._current_file_path is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            service_name = os.environ.get("MONORA_SERVICE_NAME", "monora")
            self._current_file_path = Path(self.config.path) / f"{service_name}_{timestamp}.wal"
        return self._current_file_path

    def _should_rotate(self) -> bool:
        """Check if we should rotate to a new WAL file."""
        max_bytes = self.config.max_file_size_mb * 1024 * 1024
        return self._current_file_size >= max_bytes

    def _rotate_file(self) -> None:
        """Rotate to a new WAL file."""
        if self._file_handle is not None:
            self._file_handle.close()
            self._file_handle = None
        self._current_file_path = None
        self._current_file_size = 0

    def _get_file_handle(self) -> Any:
        """Get or create the file handle for writing."""
        if self._should_rotate():
            self._rotate_file()

        if self._file_handle is None:
            file_path = self._get_current_file_path()
            self._file_handle = open(file_path, "a", encoding="utf-8")
            if file_path.exists():
                self._current_file_size = file_path.stat().st_size

        return self._file_handle

    def write(self, event: Dict[str, Any]) -> int:
        """Write an event to the WAL.

        Args:
            event: The event to write.

        Returns:
            The Log Sequence Number (LSN) for this event.
        """
        if not self.config.enabled:
            return 0

        with self._lock:
            self._current_lsn += 1
            entry = WALEntry(
                lsn=self._current_lsn,
                status="pending",
                timestamp=datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                event=event,
            )
            self._append_entry(entry)
            return self._current_lsn

    def commit(self, lsn: int) -> None:
        """Mark an event as successfully processed.

        Args:
            lsn: The Log Sequence Number of the event to commit.
        """
        if not self.config.enabled or lsn == 0:
            return

        with self._lock:
            entry = WALEntry(
                lsn=lsn,
                status="committed",
                timestamp=datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            )
            self._append_entry(entry)

    def _append_entry(self, entry: WALEntry) -> None:
        """Append an entry to the current WAL file."""
        handle = self._get_file_handle()
        line = json.dumps(entry.to_dict(), separators=(",", ":")) + "\n"
        handle.write(line)
        self._current_file_size += len(line.encode("utf-8"))

        self._update_meta(entry.lsn)

        if self.config.sync_mode == "fsync":
            handle.flush()
            os.fsync(handle.fileno())
        elif self.config.sync_mode == "async":
            handle.flush()
        # sync_mode == "none": no flush

    def _update_meta(self, lsn: int) -> None:
        meta_path = self._meta_path()
        payload = {
            "max_lsn": max(self._current_lsn, lsn),
            "updated_at": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        }
        tmp_path = meta_path.with_suffix(".json.tmp")
        try:
            tmp_path.write_text(json.dumps(payload), encoding="utf-8")
            os.replace(tmp_path, meta_path)
        except OSError:
            try:
                if tmp_path.exists():
                    tmp_path.unlink()
            except OSError:
                pass

    def recover(self) -> List[Dict[str, Any]]:
        """Recover uncommitted events from WAL files.

        Returns:
            List of events that were not committed.
        """
        if not self.config.enabled or not self.config.recovery_on_startup:
            return []

        pending: Dict[int, Dict[str, Any]] = {}
        committed: set[int] = set()

        for entry in self._read_all_entries():
            if entry.status == "pending" and entry.event is not None:
                event = dict(entry.event)
                event["_wal_lsn"] = entry.lsn
                pending[entry.lsn] = event
            elif entry.status == "committed":
                committed.add(entry.lsn)

        # Return events that are pending but not committed
        uncommitted = [
            pending[lsn] for lsn in sorted(pending.keys()) if lsn not in committed
        ]
        return uncommitted

    def _read_all_entries(self) -> Iterator[WALEntry]:
        """Read all entries from all WAL files."""
        wal_path = Path(self.config.path)
        if not wal_path.exists():
            return

        for file_path in sorted(wal_path.glob("*.wal")):
            yield from self._read_entries_from_file(file_path)

    def _read_entries_from_file(self, file_path: Path) -> Iterator[WALEntry]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        yield WALEntry.from_dict(data)
                    except (json.JSONDecodeError, KeyError):
                        # Skip malformed entries
                        continue
        except OSError:
            # Skip files we can't read
            return

    def commit_batch(self, lsns: List[int]) -> None:
        """Commit multiple LSNs in a single batch."""
        if not self.config.enabled:
            return
        if not lsns:
            return
        with self._lock:
            for lsn in sorted(set(lsns)):
                if lsn == 0:
                    continue
                entry = WALEntry(
                    lsn=lsn,
                    status="committed",
                    timestamp=datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                )
                self._append_entry(entry)

    def cleanup_old_files(self) -> int:
        """Remove WAL files older than retention period.

        Returns:
            Number of files removed.
        """
        if not self.config.enabled:
            return 0

        wal_path = Path(self.config.path)
        if not wal_path.exists():
            return 0

        cutoff_time = time.time() - (self.config.retention_hours * 3600)
        removed = 0

        active_path = self._current_file_path.resolve() if self._current_file_path else None

        for file_path in wal_path.glob("*.wal"):
            try:
                if active_path and file_path.resolve() == active_path:
                    continue
                if file_path.stat().st_mtime < cutoff_time:
                    has_uncommitted = self._file_has_uncommitted_entries(file_path)
                    if has_uncommitted is None:
                        print(
                            f"Monora: skipping WAL cleanup for unreadable file {file_path}",
                            file=sys.stderr,
                        )
                        continue
                    if has_uncommitted:
                        print(
                            f"Monora: skipping WAL cleanup for uncommitted file {file_path}",
                            file=sys.stderr,
                        )
                        continue
                    file_path.unlink()
                    removed += 1
            except OSError:
                continue

        return removed

    def close(self) -> None:
        """Close the WAL file handle."""
        with self._lock:
            if self._file_handle is not None:
                self._file_handle.close()
                self._file_handle = None

    def _file_has_uncommitted_entries(self, file_path: Path) -> Optional[bool]:
        pending: set[int] = set()
        committed: set[int] = set()
        try:
            with file_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        entry = WALEntry.from_dict(data)
                    except (json.JSONDecodeError, KeyError):
                        return None
                    if entry.status == "pending":
                        pending.add(entry.lsn)
                    elif entry.status == "committed":
                        committed.add(entry.lsn)
        except OSError:
            return None

        return any(lsn not in committed for lsn in pending)

    def __enter__(self) -> "WriteAheadLog":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()


def create_wal_from_config(config: Dict[str, Any]) -> WriteAheadLog:
    """Create a WriteAheadLog from a configuration dictionary.

    Args:
        config: Configuration dictionary with 'wal' section.

    Returns:
        Configured WriteAheadLog instance.
    """
    wal_config = config.get("wal", {})
    return WriteAheadLog(
        WALConfig(
            enabled=wal_config.get("enabled", False),
            path=wal_config.get("path", "./monora_wal"),
            sync_mode=wal_config.get("sync_mode", "fsync"),
            max_file_size_mb=wal_config.get("max_file_size_mb", 100),
            retention_hours=wal_config.get("retention_hours", 24),
            recovery_on_startup=wal_config.get("recovery_on_startup", True),
        )
    )
