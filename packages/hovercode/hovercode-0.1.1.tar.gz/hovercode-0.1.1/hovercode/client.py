"""Facade client for the Hovercode API."""

from __future__ import annotations

from typing import Optional

from hovercode.hovercodes import HovercodesClient


class HovercodeClient:
    """Facade client that exposes resource-specific sub-clients.

    This is the primary entrypoint for library users.

    Example:
        ```python
        from hovercode import HovercodeClient

        client = HovercodeClient()
        qr = client.hovercodes.create(
            workspace="YOUR-WORKSPACE-ID",
            qr_data="https://example.com",
        )
        ```

    Args:
        api_token: Hovercode API token. If not provided, `HOVERCODE_API_TOKEN`
            is used.
        base_url: Base URL for the API. Defaults to `https://hovercode.com/api/v2`.
        timeout_seconds: Per-request timeout in seconds.
        max_retries: Maximum number of retries for transient failures.
        retry_backoff_seconds: Base backoff duration (seconds) used for exponential
            backoff between retries.
        load_dotenv: If True, load environment variables from a `.env` file using
            `python-dotenv` (must be installed via `hovercode[dotenv]`).
    """

    def __init__(
        self,
        *,
        api_token: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        max_retries: Optional[int] = None,
        retry_backoff_seconds: Optional[float] = None,
        load_dotenv: bool = False,
    ) -> None:
        if load_dotenv:
            try:
                from dotenv import load_dotenv as _load_dotenv
            except ImportError as exc:  # pragma: no cover
                raise ImportError(
                    "python-dotenv is not installed. Install with: "
                    "pip install 'hovercode[dotenv]'"
                ) from exc
            _load_dotenv()

        self._api_token = api_token
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._retry_backoff_seconds = retry_backoff_seconds

        self._hovercodes: Optional[HovercodesClient] = None

    @property
    def hovercodes(self) -> HovercodesClient:
        """Access the Hovercodes domain client (lazy-loaded)."""

        if self._hovercodes is None:
            self._hovercodes = HovercodesClient(
                api_token=self._api_token,
                base_url=self._base_url,
                timeout_seconds=self._timeout_seconds,
                max_retries=self._max_retries,
                retry_backoff_seconds=self._retry_backoff_seconds,
            )
        return self._hovercodes

    def close(self) -> None:
        """Close any instantiated sub-client sessions."""

        if self._hovercodes is not None:
            self._hovercodes.close()
