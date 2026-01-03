"""Tests for hovercode.webhooks."""

from __future__ import annotations

import hashlib
import hmac

import pytest

from hovercode.exceptions import WebhookSignatureError
from hovercode.webhooks import (
    compute_signature,
    verify_signature,
    verify_signature_or_raise,
)


def test_compute_signature_matches_hmac_sha256() -> None:
    """compute_signature should return hex HMAC-SHA256."""

    secret = "secret"
    payload = b'{"hello":"world"}'

    expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    assert compute_signature(secret=secret, raw_payload=payload) == expected


def test_verify_signature_true_and_strips_whitespace() -> None:
    """verify_signature should return True on matching signature."""

    secret = "secret"
    payload = b"abc"
    sig = compute_signature(secret=secret, raw_payload=payload)
    assert verify_signature(
        secret=secret, raw_payload=payload, received_signature=f" {sig} "
    )


def test_verify_signature_false() -> None:
    """verify_signature should return False on mismatch."""

    assert (
        verify_signature(secret="s", raw_payload=b"x", received_signature="nope")
        is False
    )


def test_verify_signature_or_raise() -> None:
    """verify_signature_or_raise should raise WebhookSignatureError on mismatch."""

    secret = "secret"
    payload = b"abc"
    sig = compute_signature(secret=secret, raw_payload=payload)

    verify_signature_or_raise(
        secret=secret, raw_payload=payload, received_signature=sig
    )

    with pytest.raises(WebhookSignatureError):
        verify_signature_or_raise(
            secret=secret, raw_payload=payload, received_signature="wrong"
        )
