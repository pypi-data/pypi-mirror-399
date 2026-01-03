"""Tests for hovercode.models."""

from __future__ import annotations

import pytest

from hovercode.exceptions import ValidationError
from hovercode.models import PaginatedResponse, TagInput


def test_taginput_requires_title_or_id() -> None:
    """TagInput should validate required fields."""

    tag = TagInput()
    with pytest.raises(ValidationError):
        tag.to_request_dict()


def test_taginput_to_request_dict_title_only() -> None:
    """TagInput should serialize title."""

    tag = TagInput(title="t")
    assert tag.to_request_dict() == {"title": "t"}


def test_taginput_to_request_dict_id_only() -> None:
    """TagInput should serialize id."""

    tag = TagInput(id="123")
    assert tag.to_request_dict() == {"id": "123"}


def test_taginput_to_request_dict_both_fields() -> None:
    """TagInput should serialize both title and id if provided."""

    tag = TagInput(title="t", id="123")
    assert tag.to_request_dict() == {"title": "t", "id": "123"}


def test_paginated_response_from_dict_success() -> None:
    """PaginatedResponse should parse valid payloads."""

    data = {
        "count": 2,
        "next": "https://example.com?page=2",
        "previous": None,
        "results": [{"id": "1"}, {"id": "2"}],
    }
    parsed = PaginatedResponse.from_dict(data)
    assert parsed.count == 2
    assert parsed.next == "https://example.com?page=2"
    assert parsed.previous is None
    assert parsed.results == [{"id": "1"}, {"id": "2"}]
    assert parsed.to_dict() == data


def test_paginated_response_from_dict_invalid_count() -> None:
    """PaginatedResponse should validate count type."""

    data = {"count": "no", "next": None, "previous": None, "results": []}
    with pytest.raises(ValidationError):
        PaginatedResponse.from_dict(data)


def test_paginated_response_from_dict_invalid_next_previous() -> None:
    """PaginatedResponse should validate next/previous types."""

    data = {"count": 0, "next": 123, "previous": None, "results": []}
    with pytest.raises(ValidationError):
        PaginatedResponse.from_dict(data)

    data2 = {"count": 0, "next": None, "previous": 123, "results": []}
    with pytest.raises(ValidationError):
        PaginatedResponse.from_dict(data2)


def test_paginated_response_from_dict_invalid_results_shape() -> None:
    """PaginatedResponse should validate results list contents."""

    data = {"count": 1, "next": None, "previous": None, "results": "nope"}
    with pytest.raises(ValidationError):
        PaginatedResponse.from_dict(data)

    data2 = {"count": 1, "next": None, "previous": None, "results": ["bad"]}
    with pytest.raises(ValidationError):
        PaginatedResponse.from_dict(data2)
