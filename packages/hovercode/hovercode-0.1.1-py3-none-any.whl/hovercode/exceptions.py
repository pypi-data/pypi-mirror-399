"""Exceptions used by the Hovercode client library."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ApiError(Exception):
    """Base exception for Hovercode API errors.

    Attributes:
        message: Human-readable error message.
        status_code: HTTP status code, if the error originated from an HTTP
            response.
        response_data: Parsed response payload (JSON-decoded object or text),
            when available.
    """

    message: str
    status_code: Optional[int] = None
    response_data: Optional[object] = None

    def __post_init__(self) -> None:
        """Initialize the base Exception message."""
        super().__init__(self.message)


class AuthenticationError(ApiError):
    """Raised when authentication fails (e.g., missing or invalid API token)."""


class ValidationError(ApiError):
    """Raised when the API reports invalid input (HTTP 400)."""


class NotFoundError(ApiError):
    """Raised when a requested resource is not found (HTTP 404)."""


class RateLimitError(ApiError):
    """Raised when the API rate limit is exceeded (HTTP 429)."""


class ServerError(ApiError):
    """Raised for server-side errors (HTTP 5xx)."""


class NetworkError(ApiError):
    """Raised for network/transport errors (e.g., DNS issues, timeouts)."""


class WebhookSignatureError(ValidationError):
    """Raised when a webhook signature fails verification."""
