"""Models and helpers for Hovercode requests/responses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional

from hovercode.exceptions import ValidationError
from hovercode.types import JsonArray, JsonObject, JsonValue


@dataclass(frozen=True)
class TagInput:
    """Tag input for `HovercodesClient.add_tags`.

    The Hovercode API supports adding tags by title or by ID.

    Args:
        title: Tag title. If the tag does not exist, it may be created and added
            by the API.
        id: Tag ID. The tag is only added if it exists.

    Raises:
        ValidationError: If neither `title` nor `id` are provided.
    """

    title: Optional[str] = None
    id: Optional[str] = None

    def to_request_dict(self) -> JsonObject:
        """Convert to a request payload dictionary.

        Returns:
            A JSON object suitable for the Hovercode API.

        Raises:
            ValidationError: If neither `title` nor `id` are provided.
        """

        if self.title is None and self.id is None:
            raise ValidationError(
                message="TagInput requires at least one of: title, id.",
                status_code=None,
                response_data=None,
            )

        payload: JsonObject = {}
        if self.title is not None:
            payload["title"] = self.title
        if self.id is not None:
            payload["id"] = self.id
        return payload


@dataclass(frozen=True)
class PaginatedResponse:
    """Pagination wrapper returned by list endpoints.

    The Hovercode API includes:
    - `count`: total number of results
    - `next`: URL for next page (or null)
    - `previous`: URL for previous page (or null)
    - `results`: list of result objects

    Args:
        count: Total number of items across all pages.
        next: URL of the next page, if any.
        previous: URL of the previous page, if any.
        results: List of result objects.
    """

    count: int
    next: Optional[str]
    previous: Optional[str]
    results: JsonArray

    @classmethod
    def from_dict(cls, data: Mapping[str, JsonValue]) -> "PaginatedResponse":
        """Parse a paginated API response.

        Args:
            data: Parsed JSON response from the API.

        Returns:
            A `PaginatedResponse` instance.

        Raises:
            ValidationError: If required keys are missing or have unexpected types.
        """

        count = data.get("count")
        next_url = data.get("next")
        previous_url = data.get("previous")
        results = data.get("results")

        if not isinstance(count, int):
            raise ValidationError(
                message="Expected integer 'count' in paginated response.",
                status_code=None,
                response_data=dict(data),
            )

        if next_url is not None and not isinstance(next_url, str):
            raise ValidationError(
                message="Expected 'next' to be a string URL or null.",
                status_code=None,
                response_data=dict(data),
            )

        if previous_url is not None and not isinstance(previous_url, str):
            raise ValidationError(
                message="Expected 'previous' to be a string URL or null.",
                status_code=None,
                response_data=dict(data),
            )

        if not isinstance(results, list):
            raise ValidationError(
                message="Expected list 'results' in paginated response.",
                status_code=None,
                response_data=dict(data),
            )

        parsed_results: JsonArray = []
        for item in results:
            if not isinstance(item, dict):
                raise ValidationError(
                    message="Expected each item in 'results' to be an object.",
                    status_code=None,
                    response_data=dict(data),
                )
            parsed_results.append(item)

        return cls(
            count=count, next=next_url, previous=previous_url, results=parsed_results
        )

    def to_dict(self) -> JsonObject:
        """Convert this pagination wrapper back to a JSON object."""

        return {
            "count": self.count,
            "next": self.next,
            "previous": self.previous,
            "results": self.results,
        }
