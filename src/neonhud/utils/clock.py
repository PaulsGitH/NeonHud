"""
Time utilities for NeonHud.
"""

from __future__ import annotations

from datetime import datetime, timezone


def now_utc_iso() -> str:
    """UTC timestamp in ISO-8601 with 'Z' suffix, second precision."""
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
