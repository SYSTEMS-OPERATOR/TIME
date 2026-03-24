"""Timeline helpers for TIME-EVE.

Dev Agent Breadcrumbs:
    This module keeps timeline logic deterministic and testable outside the
    Evennia runtime so developers can reason about canonical UTC behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

_KEY_PREFIX = "UTC:"


@dataclass(frozen=True, slots=True)
class TimelineAnchor:
    """Representation of one canonical timeline anchor room."""

    utc: int
    key: str
    iso_alias: str


def utc_room_key(utc_seconds: int) -> str:
    """Return the canonical room key for a UTC second value."""
    return f"{_KEY_PREFIX}{int(utc_seconds)}"


def parse_utc_room_key(key: str) -> int:
    """Parse ``UTC:<seconds>`` room keys into integer UTC seconds.

    Raises:
        ValueError: If the key is not in canonical format.
    """
    if not isinstance(key, str) or not key.startswith(_KEY_PREFIX):
        raise ValueError(f"Invalid timeline room key: {key!r}")

    suffix = key[len(_KEY_PREFIX):]
    if suffix == "":
        raise ValueError(f"Missing UTC seconds in room key: {key!r}")

    try:
        return int(suffix)
    except (TypeError, ValueError) as err:
        raise ValueError(f"Invalid UTC seconds in room key: {key!r}") from err


def iso_z_from_utc(utc_seconds: int) -> str:
    """Render UTC seconds as ``YYYY-mm-ddTHH:MM:SSZ``."""
    dt = datetime.fromtimestamp(int(utc_seconds), tz=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_monthly_anchors(
    start_year: int = 1970, end_year: int = 2069
) -> list[TimelineAnchor]:
    """Generate first-of-month UTC anchors, inclusive across years.

    Args:
        start_year: First year in the sequence.
        end_year: Last year in the sequence.

    Returns:
        A list of monthly anchors in chronological order.
    """
    if end_year < start_year:
        raise ValueError(
            "end_year must be greater than or equal to start_year"
        )

    anchors = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            dt = datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)
            utc = int(dt.timestamp())
            anchors.append(
                TimelineAnchor(
                    utc=utc,
                    key=utc_room_key(utc),
                    iso_alias=iso_z_from_utc(utc),
                )
            )
    return anchors


def validate_chronological_keys(keys: list[str]) -> bool:
    """Return ``True`` if key sequence is non-decreasing chronologically."""
    utc_values = [parse_utc_room_key(key) for key in keys]
    return utc_values == sorted(utc_values)
