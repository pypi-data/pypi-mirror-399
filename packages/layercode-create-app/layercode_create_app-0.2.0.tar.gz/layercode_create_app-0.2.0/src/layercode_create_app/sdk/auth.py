"""Signature verification helpers for LayerCode webhooks."""

from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass


@dataclass(slots=True)
class InvalidSignatureError(Exception):
    """Raised when a LayerCode webhook signature verification fails."""

    reason: str

    def __str__(self) -> str:
        return f"Invalid signature: {self.reason}"


def verify_signature(
    payload: str,
    signature: str,
    secret: str,
    tolerance_seconds: int = 300,
) -> None:
    """Verify LayerCode webhook signature, raising InvalidSignatureError if invalid."""

    try:
        components = dict(item.split("=", 1) for item in signature.split(","))
    except ValueError as exc:
        raise InvalidSignatureError("Malformed signature header") from exc

    timestamp_str = components.get("t")
    provided_sig = components.get("v1")

    if not timestamp_str or not provided_sig:
        raise InvalidSignatureError("Signature header missing required fields")

    try:
        timestamp = int(timestamp_str)
    except ValueError as exc:
        raise InvalidSignatureError("Invalid timestamp in signature header") from exc

    current_time = int(time.time())
    if abs(current_time - timestamp) > tolerance_seconds:
        raise InvalidSignatureError("Signature timestamp outside tolerance window")

    signed_payload = timestamp_str.encode("utf-8") + b"." + payload.encode("utf-8")
    expected_sig = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_sig, provided_sig):
        raise InvalidSignatureError("Signature mismatch")
