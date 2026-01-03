"""Tests for hovercode.client."""

from __future__ import annotations

import sys
import types

import pytest

from hovercode.client import HovercodeClient


def test_facade_lazy_loads_and_caches_subclient() -> None:
    """Sub-clients should be instantiated lazily and cached."""

    client = HovercodeClient(
        api_token="t",
        base_url="https://example.com/api/v2/",
        timeout_seconds=1.5,
        max_retries=7,
        retry_backoff_seconds=0.1,
    )

    assert client._hovercodes is None
    hc1 = client.hovercodes
    hc2 = client.hovercodes
    assert hc1 is hc2

    assert hc1._base_url == "https://example.com/api/v2"
    assert hc1._timeout_seconds == 1.5
    assert hc1._max_retries == 7
    assert hc1._retry_backoff_seconds == 0.1


def test_close_noop_when_not_initialized() -> None:
    """close() should not error if no sub-clients were created."""

    client = HovercodeClient()
    client.close()


def test_close_closes_initialized_clients(monkeypatch: pytest.MonkeyPatch) -> None:
    """close() should close any instantiated sub-client sessions."""

    client = HovercodeClient(api_token="t")
    hc = client.hovercodes

    called = {"closed": False}

    def _close() -> None:
        called["closed"] = True

    monkeypatch.setattr(hc, "close", _close)
    client.close()
    assert called["closed"] is True


def test_load_dotenv_calls_loader(monkeypatch: pytest.MonkeyPatch) -> None:
    """When load_dotenv=True, the dotenv loader should be called."""

    called = {"loaded": False}
    module = types.ModuleType("dotenv")

    def _load_dotenv() -> None:
        called["loaded"] = True

    module.load_dotenv = _load_dotenv  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "dotenv", module)

    HovercodeClient(load_dotenv=True)
    assert called["loaded"] is True
