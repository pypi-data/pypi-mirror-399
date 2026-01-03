"""Tests for hovercode.base_client."""

from __future__ import annotations

from typing import Any
from urllib.parse import parse_qs, urlparse

import pytest
import requests
import responses

import hovercode.base_client as base_client_module
from hovercode.base_client import BaseClient
from hovercode.exceptions import (
    ApiError,
    AuthenticationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)


def _make_client(**kwargs: Any) -> BaseClient:
    """Create a BaseClient with sensible defaults for tests."""

    params = {
        "api_token": "test-token",
        "base_url": "https://hovercode.com/api/v2/",
        "timeout_seconds": 10.0,
        "max_retries": 2,
        "retry_backoff_seconds": 0.0,
    }
    params.update(kwargs)
    return BaseClient(**params)


def test_init_requires_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing token should raise AuthenticationError."""

    monkeypatch.delenv("HOVERCODE_API_TOKEN", raising=False)
    with pytest.raises(AuthenticationError):
        BaseClient(api_token=None, base_url="https://hovercode.com/api/v2")


def test_init_reads_token_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Token can be sourced from the environment variable."""

    monkeypatch.setenv("HOVERCODE_API_TOKEN", "env-token")
    client = BaseClient(api_token=None, base_url="https://hovercode.com/api/v2")
    assert client._session.headers["Authorization"] == "Token env-token"


def test_init_prefers_explicit_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Explicit token should override the env token."""

    monkeypatch.setenv("HOVERCODE_API_TOKEN", "env-token")
    client = BaseClient(
        api_token="param-token", base_url="https://hovercode.com/api/v2"
    )
    assert client._session.headers["Authorization"] == "Token param-token"


def test_init_requires_base_url() -> None:
    """Empty base_url should raise ValidationError."""

    with pytest.raises(ValidationError):
        BaseClient(api_token="t", base_url="")


def test_env_parsing_valid_values(monkeypatch: pytest.MonkeyPatch) -> None:
    """Timeout and retry config should be read from env when not provided."""

    monkeypatch.setenv("HOVERCODE_API_TOKEN", "env-token")
    monkeypatch.setenv("HOVERCODE_TIMEOUT_SECONDS", "12.5")
    monkeypatch.setenv("HOVERCODE_MAX_RETRIES", "4")
    monkeypatch.setenv("HOVERCODE_RETRY_BACKOFF_SECONDS", "0.25")

    client = BaseClient(api_token=None, base_url="https://hovercode.com/api/v2")
    assert client._timeout_seconds == 12.5
    assert client._max_retries == 4
    assert client._retry_backoff_seconds == 0.25


def test_env_parsing_invalid_values_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Invalid env values should fall back to defaults."""

    monkeypatch.setenv("HOVERCODE_API_TOKEN", "env-token")
    monkeypatch.setenv("HOVERCODE_TIMEOUT_SECONDS", "not-a-float")
    monkeypatch.setenv("HOVERCODE_MAX_RETRIES", "not-an-int")
    monkeypatch.setenv("HOVERCODE_RETRY_BACKOFF_SECONDS", "nope")

    client = BaseClient(api_token=None, base_url="https://hovercode.com/api/v2")
    assert client._timeout_seconds == 10.0
    assert client._max_retries == 3
    assert client._retry_backoff_seconds == 0.5


@responses.activate
def test_get_joins_url_and_parses_json() -> None:
    """Leading slashes should be tolerated in endpoints."""

    client = _make_client()
    url = "https://hovercode.com/api/v2/hovercode/abc/"
    responses.add(responses.GET, url, json={"ok": True}, status=200)

    out = client.get("/hovercode/abc/")
    assert out == {"ok": True}
    assert responses.calls[0].request.url == url


@responses.activate
def test_query_params_encoded() -> None:
    """Query parameters should be sent correctly."""

    client = _make_client()
    url = "https://hovercode.com/api/v2/workspace/w/hovercodes/"
    responses.add(
        responses.GET,
        url,
        json={"count": 0, "next": None, "previous": None, "results": []},
        status=200,
    )

    out = client.get("workspace/w/hovercodes/", params={"q": "twitter", "page": 2})
    assert isinstance(out, dict)

    parsed = urlparse(responses.calls[0].request.url)
    query = parse_qs(parsed.query)
    assert query["q"] == ["twitter"]
    assert query["page"] == ["2"]


@responses.activate
def test_post_sets_json_content_type() -> None:
    """JSON requests should include application/json content type."""

    client = _make_client()
    url = "https://hovercode.com/api/v2/hovercode/create/"
    responses.add(responses.POST, url, json={"ok": True}, status=200)

    out = client.post("hovercode/create/", json_data={"a": 1})
    assert out == {"ok": True}

    headers = responses.calls[0].request.headers
    assert headers["Content-Type"].startswith("application/json")


@responses.activate
def test_post_with_files_does_not_force_json_content_type() -> None:
    """Multipart requests should not be forced to application/json."""

    client = _make_client()
    url = "https://hovercode.com/api/v2/upload/"
    responses.add(responses.POST, url, json={"ok": True}, status=200)

    out = client.post(
        "upload/",
        data={"note": "x"},
        files={"file": ("hello.txt", b"hello", "text/plain")},
    )
    assert out == {"ok": True}

    content_type = responses.calls[0].request.headers.get("Content-Type", "")
    assert "application/json" not in content_type


@responses.activate
def test_204_returns_empty_object() -> None:
    """204 should return an empty object."""

    client = _make_client()
    url = "https://hovercode.com/api/v2/resource/"
    responses.add(responses.DELETE, url, status=204)
    assert client.delete("resource/") == {}


@responses.activate
def test_invalid_json_falls_back_to_text() -> None:
    """If response is not JSON, return text."""

    client = _make_client()
    url = "https://hovercode.com/api/v2/text/"
    responses.add(
        responses.GET, url, body="not json", status=200, content_type="text/plain"
    )
    assert client.get("text/") == "not json"


@responses.activate
def test_error_message_from_text_payload() -> None:
    """Non-JSON error bodies should be included in the message."""

    client = _make_client()
    url = "https://hovercode.com/api/v2/text-error/"
    responses.add(
        responses.GET, url, body="oops", status=418, content_type="text/plain"
    )
    with pytest.raises(ApiError) as exc:
        client.get("text-error/")
    assert "oops" in str(exc.value)


@responses.activate
def test_error_message_from_dict_without_detail_keys() -> None:
    """Dict payloads without detail keys should use a generic message."""

    client = _make_client()
    url = "https://hovercode.com/api/v2/empty-error/"
    responses.add(responses.GET, url, json={}, status=400)
    with pytest.raises(ValidationError) as exc:
        client.get("empty-error/")
    assert str(exc.value).endswith("(400).")


@responses.activate
def test_error_mapping_400() -> None:
    """400 should map to ValidationError."""

    client = _make_client()
    url = "https://hovercode.com/api/v2/bad/"
    responses.add(responses.GET, url, json={"detail": "bad"}, status=400)
    with pytest.raises(ValidationError) as exc:
        client.get("bad/")
    assert exc.value.status_code == 400
    assert exc.value.response_data == {"detail": "bad"}
    assert "bad" in str(exc.value)


@responses.activate
def test_error_mapping_401() -> None:
    """401 should map to AuthenticationError."""

    client = _make_client()
    url = "https://hovercode.com/api/v2/auth/"
    responses.add(responses.GET, url, json={"detail": "nope"}, status=401)
    with pytest.raises(AuthenticationError):
        client.get("auth/")


@responses.activate
def test_error_mapping_404() -> None:
    """404 should map to NotFoundError."""

    client = _make_client()
    url = "https://hovercode.com/api/v2/missing/"
    responses.add(responses.GET, url, json={"detail": "missing"}, status=404)
    with pytest.raises(NotFoundError):
        client.get("missing/")


@responses.activate
def test_error_mapping_429() -> None:
    """429 should map to RateLimitError."""

    client = _make_client()
    url = "https://hovercode.com/api/v2/rate/"
    responses.add(responses.GET, url, json={"detail": "slow"}, status=429)
    with pytest.raises(RateLimitError):
        client.get("rate/")


@responses.activate
def test_error_mapping_5xx() -> None:
    """5xx should map to ServerError."""

    client = _make_client()
    url = "https://hovercode.com/api/v2/server/"
    responses.add(responses.GET, url, json={"detail": "oops"}, status=500)
    with pytest.raises(ServerError):
        client.get("server/")


@responses.activate
def test_error_mapping_other_status() -> None:
    """Other non-2xx codes should map to ApiError."""

    client = _make_client()
    url = "https://hovercode.com/api/v2/teapot/"
    responses.add(responses.GET, url, json=["weird"], status=418)
    with pytest.raises(ApiError) as exc:
        client.get("teapot/")
    assert exc.value.status_code == 418


@responses.activate
def test_retries_on_retryable_status(monkeypatch: pytest.MonkeyPatch) -> None:
    """Retryable 5xx responses should be retried."""

    client = _make_client(max_retries=2)
    monkeypatch.setattr(client, "_sleep_backoff", lambda attempt: None)

    url = "https://hovercode.com/api/v2/unstable/"
    responses.add(responses.GET, url, json={"detail": "no"}, status=500)
    responses.add(responses.GET, url, json={"ok": True}, status=200)

    out = client.get("unstable/")
    assert out == {"ok": True}
    assert len(responses.calls) == 2


@responses.activate
def test_retries_on_request_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    """Transport exceptions should be retried up to max_retries."""

    client = _make_client(max_retries=2)
    monkeypatch.setattr(client, "_sleep_backoff", lambda attempt: None)

    url = "https://hovercode.com/api/v2/flaky/"
    responses.add(responses.GET, url, body=requests.exceptions.ConnectionError("boom"))
    responses.add(responses.GET, url, json={"ok": True}, status=200)

    out = client.get("flaky/")
    assert out == {"ok": True}
    assert len(responses.calls) == 2


@responses.activate
def test_request_exception_exhausted(monkeypatch: pytest.MonkeyPatch) -> None:
    """After retries are exhausted, raise NetworkError."""

    client = _make_client(max_retries=1)
    monkeypatch.setattr(client, "_sleep_backoff", lambda attempt: None)

    url = "https://hovercode.com/api/v2/down/"
    responses.add(responses.GET, url, body=requests.exceptions.Timeout("timeout"))
    responses.add(responses.GET, url, body=requests.exceptions.Timeout("timeout"))

    with pytest.raises(NetworkError):
        client.get("down/")


def test_sleep_backoff_exponential(monkeypatch: pytest.MonkeyPatch) -> None:
    """Backoff should grow exponentially with attempt index."""

    client = _make_client(retry_backoff_seconds=0.5)
    delays: list[float] = []

    def _sleep(seconds: float) -> None:
        delays.append(seconds)

    monkeypatch.setattr(base_client_module.time, "sleep", _sleep)
    client._sleep_backoff(0)
    client._sleep_backoff(2)
    assert delays == [0.5, 2.0]


@responses.activate
def test_patch_wrapper() -> None:
    """patch() should delegate to the PATCH method."""

    client = _make_client()
    url = "https://hovercode.com/api/v2/patch/"
    responses.add(responses.PATCH, url, json={"ok": True}, status=200)
    assert client.patch("patch/", json_data={"x": "y"}) == {"ok": True}


def test_close_calls_session_close(monkeypatch: pytest.MonkeyPatch) -> None:
    """close() should close the underlying requests session."""

    client = _make_client()
    called = {"closed": False}

    def _close() -> None:
        called["closed"] = True

    monkeypatch.setattr(client._session, "close", _close)
    client.close()
    assert called["closed"] is True
