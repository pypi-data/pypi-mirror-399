"""Shared enums for the Hovercode API client."""

from __future__ import annotations

from enum import Enum


class QrType(str, Enum):
    """QR code type.

    The API documentation currently lists:
    - `Link`: A URL QR code (default).
    - `Text`: A plain text QR code (static only).
    """

    LINK = "Link"
    TEXT = "Text"


class ErrorCorrection(str, Enum):
    """QR code error correction level.

    The API documentation lists these options:
    - `L`
    - `M`
    - `Q`
    - `H`
    """

    L = "L"
    M = "M"
    Q = "Q"
    H = "H"


class Pattern(str, Enum):
    """QR code pattern style."""

    ORIGINAL = "Original"
    CIRCLES = "Circles"
    SQUARES = "Squares"
    DIAMONDS = "Diamonds"
    TRIANGLES = "Triangles"


class EyeStyle(str, Enum):
    """QR code eye style."""

    SQUARE = "Square"
    ROUNDED = "Rounded"
    DROP = "Drop"
    LEAF = "Leaf"


class Frame(str, Enum):
    """QR code frame name."""

    BORDER = "border"
    BORDER_SMALL = "border-small"
    BORDER_LARGE = "border-large"
    SQUARE = "square"
    SPEECH_BUBBLE = "speech-bubble"
    SPEECH_BUBBLE_ABOVE = "speech-bubble-above"
    CARD = "card"
    CARD_ABOVE = "card-above"
    TEXT_FRAME = "text-frame"
    ROUND_FRAME = "round-frame"
    CIRCLE_VIEWFINDER = "circle-viewfinder"
    SOLID_SPIN = "solid-spin"
    BURST = "burst"
    SCATTERED_LINES = "scattered-lines"
    POLKADOT = "polkadot"
    SWIRL = "swirl"
