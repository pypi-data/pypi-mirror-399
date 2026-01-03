"""Shared type aliases for Hovercode.

The Hovercode API returns JSON. These type aliases describe JSON values without
using `Any`, which helps keep `mypy --strict` useful for API client code.
"""

from __future__ import annotations

from typing import Dict, List, Union

from typing_extensions import TypeAlias

JsonPrimitive: TypeAlias = Union[str, int, float, bool, None]
JsonValue: TypeAlias = Union[JsonPrimitive, "JsonObject", "JsonArray"]
JsonObject: TypeAlias = Dict[str, JsonValue]
JsonArray: TypeAlias = List[JsonValue]
