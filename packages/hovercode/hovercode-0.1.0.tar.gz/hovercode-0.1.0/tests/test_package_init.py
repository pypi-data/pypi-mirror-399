"""Tests for hovercode package exports."""

from __future__ import annotations

import hovercode


def test_package_exports_version_and_client() -> None:
    """The top-level package should export the main client and version."""

    assert isinstance(hovercode.__version__, str)
    assert hovercode.__version__ == "0.1.0"
    assert hovercode.HovercodeClient is not None
