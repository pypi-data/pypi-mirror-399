"""Hovercode API client library.

This package provides a typed Python client for the Hovercode API, including QR
code creation, retrieval, updates, tags management, and activity tracking.
"""

from __future__ import annotations

from hovercode.client import HovercodeClient
from hovercode.enums import ErrorCorrection, EyeStyle, Frame, Pattern, QrType
from hovercode.exceptions import (
    ApiError,
    AuthenticationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
    WebhookSignatureError,
)
from hovercode.hovercodes import HovercodesClient
from hovercode.models import PaginatedResponse, TagInput

__version__ = "0.1.1"

__all__ = [
    "ApiError",
    "AuthenticationError",
    "ErrorCorrection",
    "EyeStyle",
    "Frame",
    "HovercodeClient",
    "HovercodesClient",
    "NetworkError",
    "NotFoundError",
    "PaginatedResponse",
    "Pattern",
    "QrType",
    "RateLimitError",
    "ServerError",
    "TagInput",
    "ValidationError",
    "WebhookSignatureError",
    "__version__",
]
