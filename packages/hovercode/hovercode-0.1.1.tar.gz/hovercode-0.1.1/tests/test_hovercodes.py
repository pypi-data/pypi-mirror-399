"""Tests for hovercode.hovercodes."""

from __future__ import annotations

import json
from enum import Enum
from typing import Any
from urllib.parse import parse_qs, urlparse

import pytest
import responses

from hovercode.enums import ErrorCorrection, EyeStyle, Frame, Pattern, QrType
from hovercode.exceptions import ValidationError
from hovercode.hovercodes import HovercodesClient, _normalize_str_enum
from hovercode.models import TagInput


def _json_body(request_body: Any) -> object:
    """Decode a JSON request body from responses call."""

    if isinstance(request_body, bytes):
        return json.loads(request_body.decode("utf-8"))
    if isinstance(request_body, str):
        return json.loads(request_body)
    raise AssertionError(f"Unexpected request body type: {type(request_body)}")


@responses.activate
def test_create_posts_expected_payload() -> None:
    """create() should POST to the correct endpoint with normalized values."""

    client = HovercodesClient(api_token="t")
    url = "https://hovercode.com/api/v2/hovercode/create/"
    responses.add(responses.POST, url, json={"id": "1"}, status=200)

    out = client.create(
        workspace="w",
        qr_data="https://example.com",
        qr_type=QrType.LINK,
        dynamic=True,
        error_correction=ErrorCorrection.Q,
        pattern=Pattern.DIAMONDS,
        eye_style=EyeStyle.ROUNDED,
        frame=Frame.CIRCLE_VIEWFINDER,
        has_border=True,
    )
    assert out["id"] == "1"

    body = _json_body(responses.calls[0].request.body)
    assert isinstance(body, dict)
    assert body["workspace"] == "w"
    assert body["qr_data"] == "https://example.com"
    assert body["qr_type"] == "Link"
    assert body["dynamic"] is True
    assert body["error_correction"] == "Q"
    assert body["pattern"] == "Diamonds"
    assert body["eye_style"] == "Rounded"
    assert body["frame"] == "circle-viewfinder"
    assert body["has_border"] is True


@responses.activate
def test_create_includes_all_optional_fields_and_accepts_str_values() -> None:
    """create() should include all optional fields when provided (string inputs)."""

    client = HovercodesClient(api_token="t")
    url = "https://hovercode.com/api/v2/hovercode/create/"
    responses.add(responses.POST, url, json={"id": "2"}, status=200)

    out = client.create(
        workspace="w",
        qr_data="hello",
        qr_type="Text",
        dynamic=False,
        display_name="name",
        domain="example.com",
        generate_png=True,
        gps_tracking=False,
        error_correction="H",
        size=220,
        logo_url="https://example.com/logo.png",
        logo_round=True,
        primary_color="#111111",
        background_color="#ffffff",
        pattern="Circles",
        eye_style="Drop",
        frame="border",
        has_border=False,
        text="hi",
    )
    assert out["id"] == "2"

    body = _json_body(responses.calls[0].request.body)
    assert isinstance(body, dict)
    assert body["qr_type"] == "Text"
    assert body["dynamic"] is False
    assert body["display_name"] == "name"
    assert body["domain"] == "example.com"
    assert body["generate_png"] is True
    assert body["gps_tracking"] is False
    assert body["error_correction"] == "H"
    assert body["size"] == 220
    assert body["logo_url"] == "https://example.com/logo.png"
    assert body["logo_round"] is True
    assert body["primary_color"] == "#111111"
    assert body["background_color"] == "#ffffff"
    assert body["pattern"] == "Circles"
    assert body["eye_style"] == "Drop"
    assert body["frame"] == "border"
    assert body["has_border"] is False
    assert body["text"] == "hi"


@responses.activate
def test_create_raises_on_non_object_response() -> None:
    """create() should raise if the API returns a non-object response."""

    client = HovercodesClient(api_token="t")
    url = "https://hovercode.com/api/v2/hovercode/create/"
    responses.add(responses.POST, url, json=["no"], status=200)

    with pytest.raises(ValidationError):
        client.create(workspace="w", qr_data="x")


@responses.activate
def test_list_for_workspace_encodes_query_params() -> None:
    """list_for_workspace() should use the workspace URL and encode query params."""

    client = HovercodesClient(api_token="t")
    url = "https://hovercode.com/api/v2/workspace/ws/hovercodes/"
    responses.add(
        responses.GET,
        url,
        json={"count": 0, "next": None, "previous": None, "results": []},
        status=200,
    )

    out = client.list_for_workspace("ws", q="twitter", page=2)
    assert out["count"] == 0

    parsed = urlparse(responses.calls[0].request.url)
    query = parse_qs(parsed.query)
    assert query["q"] == ["twitter"]
    assert query["page"] == ["2"]


@responses.activate
def test_list_for_workspace_without_query_params() -> None:
    """list_for_workspace() should omit query params when none are provided."""

    client = HovercodesClient(api_token="t")
    url = "https://hovercode.com/api/v2/workspace/ws/hovercodes/"
    responses.add(
        responses.GET,
        url,
        json={"count": 0, "next": None, "previous": None, "results": []},
        status=200,
    )

    client.list_for_workspace("ws")
    assert responses.calls[0].request.url == url


@responses.activate
def test_list_for_workspace_raises_on_non_object_response() -> None:
    """list_for_workspace() should raise on unexpected response types."""

    client = HovercodesClient(api_token="t")
    url = "https://hovercode.com/api/v2/workspace/ws/hovercodes/"
    responses.add(responses.GET, url, json=["no"], status=200)

    with pytest.raises(ValidationError):
        client.list_for_workspace("ws")


@responses.activate
def test_get_uses_correct_path() -> None:
    """get() should call /hovercode/{id}/."""

    client = HovercodesClient(api_token="t")
    url = "https://hovercode.com/api/v2/hovercode/abc/"
    responses.add(responses.GET, url, json={"id": "abc"}, status=200)

    out = client.get_hovercode("abc")
    assert out["id"] == "abc"


@responses.activate
def test_get_raises_on_non_object_response() -> None:
    """get() should raise on unexpected response types."""

    client = HovercodesClient(api_token="t")
    url = "https://hovercode.com/api/v2/hovercode/abc/"
    responses.add(responses.GET, url, json=["no"], status=200)

    with pytest.raises(ValidationError):
        client.get_hovercode("abc")


def test_get_activity_page_size_validation() -> None:
    """page_size must be <= 200."""

    client = HovercodesClient(api_token="t")
    with pytest.raises(ValidationError):
        client.get_activity("abc", page_size=201)


@responses.activate
def test_get_activity_success_with_params() -> None:
    """get_activity() should include page and page_size when provided."""

    client = HovercodesClient(api_token="t")
    url = "https://hovercode.com/api/v2/hovercode/abc/activity/"
    responses.add(
        responses.GET,
        url,
        json={"count": 0, "next": None, "previous": None, "results": []},
        status=200,
    )

    client.get_activity("abc", page=2, page_size=50)
    parsed = urlparse(responses.calls[0].request.url)
    query = parse_qs(parsed.query)
    assert query["page"] == ["2"]
    assert query["page_size"] == ["50"]


@responses.activate
def test_get_activity_success_without_params() -> None:
    """get_activity() should omit query params when none are provided."""

    client = HovercodesClient(api_token="t")
    url = "https://hovercode.com/api/v2/hovercode/abc/activity/"
    responses.add(
        responses.GET,
        url,
        json={"count": 0, "next": None, "previous": None, "results": []},
        status=200,
    )

    client.get_activity("abc")
    assert responses.calls[0].request.url == url


@responses.activate
def test_get_activity_raises_on_non_object_response() -> None:
    """get_activity() should raise on unexpected response types."""

    client = HovercodesClient(api_token="t")
    url = "https://hovercode.com/api/v2/hovercode/abc/activity/"
    responses.add(responses.GET, url, json=["no"], status=200)

    with pytest.raises(ValidationError):
        client.get_activity("abc")


def test_update_requires_at_least_one_field() -> None:
    """update() requires at least one field."""

    client = HovercodesClient(api_token="t")
    with pytest.raises(ValidationError):
        client.update("abc")


@responses.activate
def test_update_sends_payload() -> None:
    """update() should send only provided fields."""

    client = HovercodesClient(api_token="t")
    url = "https://hovercode.com/api/v2/hovercode/abc/update/"
    responses.add(responses.PUT, url, json={"id": "abc"}, status=200)

    out = client.update("abc", display_name="name")
    assert out["id"] == "abc"

    body = _json_body(responses.calls[0].request.body)
    assert body == {"display_name": "name"}


@responses.activate
def test_update_sends_qr_data_and_gps_tracking() -> None:
    """update() should include qr_data and gps_tracking when provided."""

    client = HovercodesClient(api_token="t")
    url = "https://hovercode.com/api/v2/hovercode/abc/update/"
    responses.add(responses.PUT, url, json={"id": "abc"}, status=200)

    client.update("abc", qr_data="https://x", gps_tracking=True)
    body = _json_body(responses.calls[0].request.body)
    assert body == {"qr_data": "https://x", "gps_tracking": True}


@responses.activate
def test_update_raises_on_non_object_response() -> None:
    """update() should raise on unexpected response types."""

    client = HovercodesClient(api_token="t")
    url = "https://hovercode.com/api/v2/hovercode/abc/update/"
    responses.add(responses.PUT, url, json=["no"], status=200)

    with pytest.raises(ValidationError):
        client.update("abc", display_name="x")


def test_add_tags_requires_non_empty_list() -> None:
    """add_tags() requires at least one tag."""

    client = HovercodesClient(api_token="t")
    with pytest.raises(ValidationError):
        client.add_tags("abc", [])


@responses.activate
def test_add_tags_accepts_taginput_and_mapping() -> None:
    """add_tags() should accept TagInput and raw mappings."""

    client = HovercodesClient(api_token="t")
    url = "https://hovercode.com/api/v2/hovercode/abc/tags/add/"
    responses.add(responses.POST, url, json={"id": "abc"}, status=200)

    out = client.add_tags("abc", [TagInput(title="t1"), {"title": "t2"}])
    assert out["id"] == "abc"

    body = _json_body(responses.calls[0].request.body)
    assert body == [{"title": "t1"}, {"title": "t2"}]


@responses.activate
def test_add_tags_raises_on_non_object_response() -> None:
    """add_tags() should raise on unexpected response types."""

    client = HovercodesClient(api_token="t")
    url = "https://hovercode.com/api/v2/hovercode/abc/tags/add/"
    responses.add(responses.POST, url, json=["no"], status=200)

    with pytest.raises(ValidationError):
        client.add_tags("abc", [TagInput(title="t")])


@responses.activate
def test_delete_returns_empty_dict_for_204() -> None:
    """delete() should return {} when the API returns 204."""

    client = HovercodesClient(api_token="t")
    url = "https://hovercode.com/api/v2/hovercode/abc/delete/"
    responses.add(responses.DELETE, url, status=204)

    out = client.delete_hovercode("abc")
    assert out == {}


@responses.activate
def test_delete_raises_on_non_object_response() -> None:
    """delete() should raise on unexpected response types."""

    client = HovercodesClient(api_token="t")
    url = "https://hovercode.com/api/v2/hovercode/abc/delete/"
    responses.add(responses.DELETE, url, json=["no"], status=200)

    with pytest.raises(ValidationError):
        client.delete_hovercode("abc")


def test_normalize_str_enum_rejects_non_str_enum_value() -> None:
    """_normalize_str_enum should reject enums whose value is not a string."""

    class Bad(Enum):
        """Bad enum for testing."""

        X = 1

    with pytest.raises(ValidationError):
        _normalize_str_enum(Bad.X)
