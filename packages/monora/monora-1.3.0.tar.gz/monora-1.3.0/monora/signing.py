"""Per-event digital signatures for event authenticity verification.

This module provides Ed25519 and HMAC-SHA256 signing capabilities
to cryptographically prove event authorship and integrity.
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, Optional

# Optional Ed25519 support (requires pynacl)
try:
    from nacl.signing import SigningKey, VerifyKey
    from nacl.exceptions import BadSignatureError

    NACL_AVAILABLE = True
except ImportError:
    NACL_AVAILABLE = False
    SigningKey = None  # type: ignore
    VerifyKey = None  # type: ignore
    BadSignatureError = Exception  # type: ignore


@dataclass
class SigningConfig:
    """Configuration for event signing."""

    enabled: bool = False
    algorithm: str = "ed25519"  # ed25519 | hmac-sha256
    key_id: Optional[str] = None
    key_file: Optional[str] = None
    key_env: str = "MONORA_SIGNING_KEY"


@dataclass
class EventSignature:
    """Represents a cryptographic signature on an event."""

    algorithm: str
    key_id: Optional[str]
    signature: str  # Base64-encoded signature bytes

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: Dict[str, Any] = {
            "algorithm": self.algorithm,
            "signature": self.signature,
        }
        if self.key_id:
            result["key_id"] = self.key_id
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EventSignature":
        """Create from dictionary."""
        return cls(
            algorithm=data["algorithm"],
            key_id=data.get("key_id"),
            signature=data["signature"],
        )


class EventSigner:
    """Signs events using Ed25519 or HMAC-SHA256.

    The signature covers the canonical JSON representation of the event,
    excluding the signature and hash fields themselves.

    Example:
        >>> config = SigningConfig(enabled=True, algorithm='hmac-sha256')
        >>> signer = EventSigner(config)
        >>> event = {'event_id': 'evt_123', 'event_type': 'llm_call', ...}
        >>> signature = signer.sign(event)
        >>> event['event_signature'] = signature.to_dict()
    """

    def __init__(self, config: SigningConfig):
        self.config = config
        self._signing_key: Optional[bytes] = None
        self._ed25519_key: Any = None  # SigningKey when using Ed25519

        if config.enabled:
            self._load_key()

    def _load_key(self) -> None:
        """Load the signing key from file or environment."""
        key_data: Optional[bytes] = None

        # Try loading from file first
        if self.config.key_file and os.path.exists(self.config.key_file):
            with open(self.config.key_file, "rb") as f:
                key_data = f.read()
        # Then try environment variable
        elif self.config.key_env:
            env_value = os.environ.get(self.config.key_env)
            if env_value:
                # Environment variables are base64-encoded
                try:
                    key_data = base64.b64decode(env_value, validate=True)
                except (binascii.Error, ValueError) as exc:
                    # If not valid base64, treat as raw bytes
                    preview_hash = hashlib.sha256(env_value.encode("utf-8")).hexdigest()[:8]
                    print(
                        "Monora: invalid base64 signing key in env; "
                        f"using utf-8 bytes (len={len(env_value)}, sha256_prefix={preview_hash}): {exc}",
                        file=sys.stderr,
                    )
                    key_data = env_value.encode("utf-8")

        if key_data is None:
            if self.config.algorithm == "ed25519":
                raise ValueError(
                    "Ed25519 signing enabled but no key provided. "
                    f"Set {self.config.key_env} or provide key_file."
                )
            # For HMAC, we can generate a warning but continue
            return

        self._signing_key = key_data

        # Initialize Ed25519 key if needed
        if self.config.algorithm == "ed25519":
            if not NACL_AVAILABLE:
                raise ImportError(
                    "Ed25519 signing requires pynacl. Install with: pip install pynacl"
                )
            # Handle different key formats
            if len(key_data) == 32:
                # Raw 32-byte seed
                self._ed25519_key = SigningKey(key_data)
            elif len(key_data) == 64:
                # Full 64-byte key (seed + public)
                self._ed25519_key = SigningKey(key_data[:32])
            else:
                raise ValueError(
                    f"Ed25519 key must be 32 or 64 bytes, got {len(key_data)}"
                )

    def sign(self, event: Dict[str, Any]) -> Optional[EventSignature]:
        """Sign an event and return the signature.

        Args:
            event: The event dictionary to sign. Should not contain
                   'event_signature', 'prev_hash', or 'event_hash' fields
                   as these are excluded from the canonical representation.

        Returns:
            EventSignature object, or None if signing is disabled.
        """
        if not self.config.enabled:
            return None

        # Create canonical JSON representation (sorted keys, no whitespace)
        canonical = self._canonical_json(event)

        if self.config.algorithm == "ed25519":
            return self._sign_ed25519(canonical)
        elif self.config.algorithm == "hmac-sha256":
            return self._sign_hmac(canonical)
        else:
            raise ValueError(f"Unknown signing algorithm: {self.config.algorithm}")

    def _canonical_json(self, event: Dict[str, Any]) -> bytes:
        """Create canonical JSON representation for signing.

        Excludes signature and hash fields to allow signing before hashing.
        """
        # Create a copy without fields that are added after signing
        signable = {
            k: v
            for k, v in event.items()
            if k not in ("event_signature", "prev_hash", "event_hash")
        }
        return json.dumps(signable, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def _sign_ed25519(self, data: bytes) -> EventSignature:
        """Sign data using Ed25519."""
        if self._ed25519_key is None:
            raise ValueError("Ed25519 key not loaded")

        signed = self._ed25519_key.sign(data)
        signature_bytes = signed.signature

        return EventSignature(
            algorithm="ed25519",
            key_id=self.config.key_id,
            signature=base64.b64encode(signature_bytes).decode("ascii"),
        )

    def _sign_hmac(self, data: bytes) -> EventSignature:
        """Sign data using HMAC-SHA256."""
        if self._signing_key is None:
            raise ValueError(
                "HMAC signing enabled but no key provided. "
                f"Set {self.config.key_env} or provide key_file."
            )

        signature_bytes = hmac.new(
            self._signing_key, data, hashlib.sha256
        ).digest()

        return EventSignature(
            algorithm="hmac-sha256",
            key_id=self.config.key_id,
            signature=base64.b64encode(signature_bytes).decode("ascii"),
        )


class SignatureVerifier:
    """Verifies event signatures.

    Example:
        >>> verifier = SignatureVerifier()
        >>> verifier.load_key('ed25519', public_key_bytes)
        >>> is_valid = verifier.verify(event)
    """

    def __init__(self) -> None:
        self._keys: Dict[str, Any] = {}  # key_id -> key material

    def load_key(
        self,
        algorithm: str,
        key_data: bytes,
        key_id: Optional[str] = None,
    ) -> None:
        """Load a verification key.

        Args:
            algorithm: 'ed25519' or 'hmac-sha256'
            key_data: Key bytes (public key for Ed25519, secret for HMAC)
            key_id: Optional key identifier for key rotation
        """
        storage_id = key_id or f"_default_{algorithm}"

        if algorithm == "ed25519":
            if not NACL_AVAILABLE:
                raise ImportError(
                    "Ed25519 verification requires pynacl. Install with: pip install pynacl"
                )
            if len(key_data) == 32:
                # Public key
                self._keys[storage_id] = ("ed25519", VerifyKey(key_data))
            elif len(key_data) == 64:
                # Full key - extract public portion
                self._keys[storage_id] = ("ed25519", VerifyKey(key_data[32:]))
            else:
                raise ValueError(
                    f"Ed25519 public key must be 32 or 64 bytes, got {len(key_data)}"
                )
        elif algorithm == "hmac-sha256":
            self._keys[storage_id] = ("hmac-sha256", key_data)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

    def load_key_from_env(
        self,
        algorithm: str,
        env_var: str = "MONORA_SIGNING_KEY",
        key_id: Optional[str] = None,
    ) -> bool:
        """Load a verification key from environment variable.

        Returns True if key was loaded, False if env var not set.
        """
        env_value = os.environ.get(env_var)
        if not env_value:
            return False

        try:
            key_data = base64.b64decode(env_value)
        except Exception:
            key_data = env_value.encode("utf-8")

        self.load_key(algorithm, key_data, key_id)
        return True

    def verify(self, event: Dict[str, Any]) -> bool:
        """Verify an event's signature.

        Args:
            event: Event dictionary containing 'event_signature' field.

        Returns:
            True if signature is valid, False otherwise.
        """
        sig_data = event.get("event_signature")
        if not sig_data:
            return False

        try:
            signature = EventSignature.from_dict(sig_data)
        except (KeyError, TypeError):
            return False

        # Find the key to use
        storage_id = signature.key_id or f"_default_{signature.algorithm}"
        if storage_id not in self._keys:
            # Try default for algorithm
            storage_id = f"_default_{signature.algorithm}"
            if storage_id not in self._keys:
                return False

        algorithm, key_material = self._keys[storage_id]

        # Reconstruct canonical JSON
        canonical = self._canonical_json(event)

        try:
            signature_bytes = base64.b64decode(signature.signature)
        except Exception:
            return False

        if algorithm == "ed25519":
            return self._verify_ed25519(canonical, signature_bytes, key_material)
        elif algorithm == "hmac-sha256":
            return self._verify_hmac(canonical, signature_bytes, key_material)

        return False

    def _canonical_json(self, event: Dict[str, Any]) -> bytes:
        """Create canonical JSON representation for verification."""
        signable = {
            k: v
            for k, v in event.items()
            if k not in ("event_signature", "prev_hash", "event_hash")
        }
        return json.dumps(signable, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def _verify_ed25519(
        self, data: bytes, signature: bytes, verify_key: Any
    ) -> bool:
        """Verify Ed25519 signature."""
        try:
            verify_key.verify(data, signature)
            return True
        except BadSignatureError:
            return False

    def _verify_hmac(
        self, data: bytes, signature: bytes, key: bytes
    ) -> bool:
        """Verify HMAC-SHA256 signature."""
        expected = hmac.new(key, data, hashlib.sha256).digest()
        return hmac.compare_digest(signature, expected)


def create_signer_from_config(config: Dict[str, Any]) -> EventSigner:
    """Create an EventSigner from a configuration dictionary.

    Args:
        config: Configuration dictionary with 'signing' section.

    Returns:
        Configured EventSigner instance.
    """
    signing_config = config.get("signing", {})
    return EventSigner(
        SigningConfig(
            enabled=signing_config.get("enabled", False),
            algorithm=signing_config.get("algorithm", "ed25519"),
            key_id=signing_config.get("key_id"),
            key_file=signing_config.get("key_file"),
            key_env=signing_config.get("key_env", "MONORA_SIGNING_KEY"),
        )
    )


def verify_event_signature(
    event: Dict[str, Any],
    key_data: Optional[bytes] = None,
    key_env: str = "MONORA_SIGNING_KEY",
) -> bool:
    """Convenience function to verify a single event's signature.

    Args:
        event: Event dictionary with 'event_signature' field.
        key_data: Optional key bytes. If not provided, loads from environment.
        key_env: Environment variable name to load key from.

    Returns:
        True if signature is valid, False otherwise.
    """
    sig_data = event.get("event_signature")
    if not sig_data:
        return False

    try:
        signature = EventSignature.from_dict(sig_data)
    except (KeyError, TypeError):
        return False

    verifier = SignatureVerifier()

    if key_data:
        verifier.load_key(signature.algorithm, key_data)
    else:
        if not verifier.load_key_from_env(signature.algorithm, key_env):
            return False

    return verifier.verify(event)
