"""HTTP transport layer for the Hovercode client library."""

from __future__ import annotations

import os
import time
from typing import (
    Iterable,
    Mapping,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    cast,
)

import requests

from hovercode.exceptions import (
    ApiError,
    AuthenticationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from hovercode.types import JsonValue

QueryParamScalar = Union[str, bytes, int, float]
QueryParamValue = Union[QueryParamScalar, None, Sequence[QueryParamScalar]]
QueryParams = Mapping[str, QueryParamValue]

TRead = TypeVar("TRead", covariant=True)


class SupportsRead(Protocol[TRead]):
    """Protocol for file-like objects accepted by requests."""

    def read(self, n: int = ...) -> TRead:
        """Read up to n bytes/chars from the underlying stream."""


FileData = Union[SupportsRead[Union[str, bytes]], str, bytes]
FileValue = Union[
    FileData,
    Tuple[Optional[str], FileData],
    Tuple[Optional[str], FileData, str],
    Tuple[Optional[str], FileData, str, Mapping[str, str]],
]
Files = Union[Mapping[str, FileValue], Iterable[Tuple[str, FileValue]]]


class BaseClient:
    """Base HTTP client used by all Hovercode sub-clients.

    This class owns the `requests.Session` and implements:

    - Authentication header injection
    - Timeouts and retries with exponential backoff
    - Consistent JSON decoding and error mapping

    Environment variables:
        - `HOVERCODE_API_TOKEN`: API token (used when `api_token` is not provided)
        - `HOVERCODE_TIMEOUT_SECONDS`: request timeout (default: 10.0)
        - `HOVERCODE_MAX_RETRIES`: retry count (default: 3)
        - `HOVERCODE_RETRY_BACKOFF_SECONDS`: base backoff seconds (default: 0.5)

    Retry behavior:
        Retries are attempted for transient failures:

        - HTTP 500/502/503/504 responses
        - `requests` transport exceptions (connection errors, timeouts, etc.)

        Backoff is exponential: `retry_backoff_seconds * (2 ** attempt)`.

    Error mapping:
        Non-2xx responses are mapped to exception types:

        - 400 → `ValidationError`
        - 401 → `AuthenticationError`
        - 404 → `NotFoundError`
        - 429 → `RateLimitError`
        - 5xx → `ServerError`
        - otherwise → `ApiError`

    Response decoding:
        - For HTTP 204, returns `{}`.
        - Attempts to decode JSON; falls back to `response.text` if JSON decoding fails.

    Args:
        api_token: Hovercode API token. If not provided, `HOVERCODE_API_TOKEN`
            is used.
        base_url: Base URL for the API, e.g. `https://hovercode.com/api/v2`.
        timeout_seconds: Per-request timeout in seconds. If not provided,
            `HOVERCODE_TIMEOUT_SECONDS` is used (or defaults to 10.0).
        max_retries: Maximum number of retries for transient failures. If not
            provided, `HOVERCODE_MAX_RETRIES` is used (or defaults to 3).
        retry_backoff_seconds: Base backoff duration (seconds) used for
            exponential backoff between retries. If not provided,
            `HOVERCODE_RETRY_BACKOFF_SECONDS` is used (or defaults to 0.5).
        session: Optional pre-configured `requests.Session` (useful for tests).

    Raises:
        AuthenticationError: If no API token is provided and the environment
            variable is missing.
        ValidationError: If `base_url` is empty.
    """

    _API_TOKEN_ENV_VAR = "HOVERCODE_API_TOKEN"  # nosec B105
    _ENV_PREFIX = "HOVERCODE"
    _RETRYABLE_STATUS_CODES = frozenset({500, 502, 503, 504})

    def __init__(
        self,
        *,
        api_token: Optional[str],
        base_url: str,
        timeout_seconds: Optional[float] = None,
        max_retries: Optional[int] = None,
        retry_backoff_seconds: Optional[float] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        if not base_url:
            raise ValidationError("base_url must be a non-empty string.")

        resolved_token = api_token or os.getenv(self._API_TOKEN_ENV_VAR)
        if not resolved_token:
            raise AuthenticationError(
                f"Missing Hovercode API token. Provide api_token= or set "
                f"{self._API_TOKEN_ENV_VAR}."
            )

        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = (
            timeout_seconds
            if timeout_seconds is not None
            else self._get_env_float("TIMEOUT_SECONDS", default=10.0)
        )
        self._max_retries = (
            max_retries
            if max_retries is not None
            else self._get_env_int("MAX_RETRIES", default=3)
        )
        self._retry_backoff_seconds = (
            retry_backoff_seconds
            if retry_backoff_seconds is not None
            else self._get_env_float("RETRY_BACKOFF_SECONDS", default=0.5)
        )

        self._session = session or requests.Session()
        self._session.headers.update(
            {
                "Accept": "application/json",
                "Authorization": f"Token {resolved_token}",
            }
        )

    def close(self) -> None:
        """Close the underlying HTTP session."""

        self._session.close()

    def get(
        self,
        endpoint: str,
        *,
        params: Optional[QueryParams] = None,
        timeout_seconds: Optional[float] = None,
    ) -> JsonValue:
        """Send a GET request.

        Args:
            endpoint: Relative API endpoint.
            params: Optional query parameters.
            timeout_seconds: Optional per-request timeout override.

        Returns:
            Parsed response payload (JSON decoded), or raw text when JSON decoding
            fails. For `204 No Content`, returns `{}`.
        """

        return self._request(
            "GET", endpoint, params=params, timeout_seconds=timeout_seconds
        )

    def post(
        self,
        endpoint: str,
        *,
        params: Optional[QueryParams] = None,
        json_data: Optional[JsonValue] = None,
        data: Optional[Mapping[str, object]] = None,
        files: Optional[Files] = None,
        timeout_seconds: Optional[float] = None,
    ) -> JsonValue:
        """Send a POST request.

        Args:
            endpoint: Relative API endpoint.
            params: Optional query parameters.
            json_data: Optional JSON-serializable payload.
            data: Optional form payload.
            files: Optional multipart files payload. When set, `json_data` is not
                sent.
            timeout_seconds: Optional per-request timeout override.

        Returns:
            Parsed response payload (JSON decoded), or raw text when JSON decoding
            fails. For `204 No Content`, returns `{}`.

        Raises:
            ApiError: For non-2xx responses (mapped to more specific subclasses).
            NetworkError: For transport exceptions after exhausting retries.
        """

        return self._request(
            "POST",
            endpoint,
            params=params,
            json_data=json_data,
            data=data,
            files=files,
            timeout_seconds=timeout_seconds,
        )

    def put(
        self,
        endpoint: str,
        *,
        params: Optional[QueryParams] = None,
        json_data: Optional[JsonValue] = None,
        data: Optional[Mapping[str, object]] = None,
        files: Optional[Files] = None,
        timeout_seconds: Optional[float] = None,
    ) -> JsonValue:
        """Send a PUT request.

        Args:
            endpoint: Relative API endpoint.
            params: Optional query parameters.
            json_data: Optional JSON-serializable payload.
            data: Optional form payload.
            files: Optional multipart files payload. When set, `json_data` is not
                sent.
            timeout_seconds: Optional per-request timeout override.

        Returns:
            Parsed response payload (JSON decoded), or raw text when JSON decoding
            fails. For `204 No Content`, returns `{}`.

        Raises:
            ApiError: For non-2xx responses (mapped to more specific subclasses).
            NetworkError: For transport exceptions after exhausting retries.
        """

        return self._request(
            "PUT",
            endpoint,
            params=params,
            json_data=json_data,
            data=data,
            files=files,
            timeout_seconds=timeout_seconds,
        )

    def patch(
        self,
        endpoint: str,
        *,
        params: Optional[QueryParams] = None,
        json_data: Optional[JsonValue] = None,
        data: Optional[Mapping[str, object]] = None,
        files: Optional[Files] = None,
        timeout_seconds: Optional[float] = None,
    ) -> JsonValue:
        """Send a PATCH request.

        Args:
            endpoint: Relative API endpoint.
            params: Optional query parameters.
            json_data: Optional JSON-serializable payload.
            data: Optional form payload.
            files: Optional multipart files payload. When set, `json_data` is not
                sent.
            timeout_seconds: Optional per-request timeout override.

        Returns:
            Parsed response payload (JSON decoded), or raw text when JSON decoding
            fails. For `204 No Content`, returns `{}`.

        Raises:
            ApiError: For non-2xx responses (mapped to more specific subclasses).
            NetworkError: For transport exceptions after exhausting retries.
        """

        return self._request(
            "PATCH",
            endpoint,
            params=params,
            json_data=json_data,
            data=data,
            files=files,
            timeout_seconds=timeout_seconds,
        )

    def delete(
        self,
        endpoint: str,
        *,
        params: Optional[QueryParams] = None,
        timeout_seconds: Optional[float] = None,
    ) -> JsonValue:
        """Send a DELETE request.

        Args:
            endpoint: Relative API endpoint.
            params: Optional query parameters.
            timeout_seconds: Optional per-request timeout override.

        Returns:
            Parsed response payload (JSON decoded), or raw text when JSON decoding
            fails. For `204 No Content`, returns `{}`.

        Raises:
            ApiError: For non-2xx responses (mapped to more specific subclasses).
            NetworkError: For transport exceptions after exhausting retries.
        """

        return self._request(
            "DELETE", endpoint, params=params, timeout_seconds=timeout_seconds
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[QueryParams] = None,
        json_data: Optional[JsonValue] = None,
        data: Optional[Mapping[str, object]] = None,
        files: Optional[Files] = None,
        timeout_seconds: Optional[float] = None,
    ) -> JsonValue:
        """Send an HTTP request with retries and error handling.

        Args:
            method: HTTP method (e.g. GET, POST).
            endpoint: Relative API endpoint path.
            params: Optional query parameters.
            json_data: Optional JSON-serializable payload.
            data: Optional form data payload.
            files: Optional multipart files payload. When set, `json_data` is not
                sent and `requests` will set the multipart content type.
            timeout_seconds: Optional per-request timeout override.

        Returns:
            Parsed response payload (JSON decoded), or raw text when JSON decoding
            fails. For `204 No Content`, returns `{}`.

        Raises:
            ApiError: For non-2xx responses (mapped to more specific subclasses).
            NetworkError: For transport exceptions after exhausting retries.
        """

        url = f"{self._base_url}/{endpoint.lstrip('/')}"
        timeout = (
            timeout_seconds if timeout_seconds is not None else self._timeout_seconds
        )

        for attempt in range(self._max_retries + 1):
            try:
                headers: Optional[dict[str, str]] = None
                if files is None and json_data is not None:
                    headers = {"Content-Type": "application/json"}

                response = self._session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=None if files is not None else json_data,
                    data=data,
                    files=files,
                    timeout=timeout,
                    headers=headers,
                )
            except requests.exceptions.RequestException as exc:
                if attempt < self._max_retries:
                    self._sleep_backoff(attempt)
                    continue
                raise NetworkError(
                    message=f"Network error calling {method} {url}: {exc!s}",
                    status_code=None,
                    response_data=None,
                ) from exc

            if (
                response.status_code in self._RETRYABLE_STATUS_CODES
                and attempt < self._max_retries
            ):
                self._sleep_backoff(attempt)
                continue

            response_data = self._parse_response_data(response)
            if 200 <= response.status_code < 300:
                return response_data

            raise self._map_http_error(response.status_code, response_data, method, url)

        raise NetworkError(  # pragma: no cover
            message=(  # pragma: no cover
                f"Unexpected retry loop exit for {method} {url}"  # pragma: no cover
            ),  # pragma: no cover
            status_code=None,  # pragma: no cover
            response_data=None,  # pragma: no cover
        )  # pragma: no cover

    def _sleep_backoff(self, attempt: int) -> None:
        """Sleep according to exponential backoff schedule.

        Args:
            attempt: Attempt index (0-based) for computing backoff.
        """

        delay = self._retry_backoff_seconds * (2**attempt)
        time.sleep(delay)

    def _parse_response_data(self, response: requests.Response) -> JsonValue:
        """Parse response payload into JSON (preferred) or raw text.

        Args:
            response: HTTP response.

        Returns:
            Parsed JSON payload, raw text, or `{}` for 204 responses.
        """

        if response.status_code == 204:
            return {}

        try:
            return cast(JsonValue, response.json())
        except ValueError:
            return response.text

    def _map_http_error(
        self, status_code: int, response_data: object, method: str, url: str
    ) -> ApiError:
        """Map an HTTP error response to an exception type."""

        message = self._extract_error_message(status_code, response_data, method, url)
        if status_code == 400:
            return ValidationError(
                message=message, status_code=status_code, response_data=response_data
            )
        if status_code == 401:
            return AuthenticationError(
                message=message, status_code=status_code, response_data=response_data
            )
        if status_code == 404:
            return NotFoundError(
                message=message, status_code=status_code, response_data=response_data
            )
        if status_code == 429:
            return RateLimitError(
                message=message, status_code=status_code, response_data=response_data
            )
        if 500 <= status_code <= 599:
            return ServerError(
                message=message, status_code=status_code, response_data=response_data
            )
        return ApiError(
            message=message, status_code=status_code, response_data=response_data
        )

    def _extract_error_message(
        self, status_code: int, response_data: object, method: str, url: str
    ) -> str:
        """Try to derive a useful error message from an error payload."""

        if isinstance(response_data, dict):
            for key in ("detail", "error", "message"):
                value = response_data.get(key)
                if isinstance(value, str) and value.strip():
                    return f"{method} {url} failed ({status_code}): {value}"
            return f"{method} {url} failed ({status_code})."

        if isinstance(response_data, str) and response_data.strip():
            return f"{method} {url} failed ({status_code}): {response_data}"

        return f"{method} {url} failed ({status_code})."

    def _get_env_float(self, suffix: str, *, default: float) -> float:
        """Read and parse a float from an env var, with safe fallback."""

        key = f"{self._ENV_PREFIX}_{suffix}"
        raw = os.getenv(key)
        if raw is None:
            return default
        try:
            return float(raw)
        except ValueError:
            return default

    def _get_env_int(self, suffix: str, *, default: int) -> int:
        """Read and parse an int from an env var, with safe fallback."""

        key = f"{self._ENV_PREFIX}_{suffix}"
        raw = os.getenv(key)
        if raw is None:
            return default
        try:
            return int(raw)
        except ValueError:
            return default
