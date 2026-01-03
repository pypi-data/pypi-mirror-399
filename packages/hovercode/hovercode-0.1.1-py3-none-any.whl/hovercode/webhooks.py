"""Webhook utilities for Hovercode.

Hovercode can send webhooks when a dynamic QR code is scanned. Each webhook
request includes a header called `X-Signature` (documented as `x-signature`)
containing an HMAC-SHA256 signature of the raw request body.
"""

from __future__ import annotations

import hashlib
import hmac

from hovercode.exceptions import WebhookSignatureError


def compute_signature(secret: str, raw_payload: bytes) -> str:
    """Compute a Hovercode webhook signature.

    Args:
        secret: Webhook secret configured in Hovercode.
        raw_payload: Raw request body bytes.

    Returns:
        Hex-encoded HMAC-SHA256 signature.
    """

    return hmac.new(secret.encode("utf-8"), raw_payload, hashlib.sha256).hexdigest()


def verify_signature(secret: str, raw_payload: bytes, received_signature: str) -> bool:
    """Verify a Hovercode webhook signature.

    Args:
        secret: Webhook secret configured in Hovercode.
        raw_payload: Raw request body bytes.
        received_signature: Signature received in the request header. Leading and
            trailing whitespace is ignored.

    Returns:
        True if the signature matches; otherwise False.
    """

    expected_signature = compute_signature(secret=secret, raw_payload=raw_payload)
    return hmac.compare_digest(expected_signature, received_signature.strip())


def verify_signature_or_raise(
    secret: str, raw_payload: bytes, received_signature: str
) -> None:
    """Verify a Hovercode webhook signature or raise an error.

    Args:
        secret: Webhook secret configured in Hovercode.
        raw_payload: Raw request body bytes.
        received_signature: Signature received in the request header.

    Raises:
        WebhookSignatureError: If the signature does not match.
    """

    if not verify_signature(
        secret=secret, raw_payload=raw_payload, received_signature=received_signature
    ):
        raise WebhookSignatureError(message="Invalid webhook signature.")
