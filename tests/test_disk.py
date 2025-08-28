"""
Sparkline utility for compact history graphs.

Usage:
  sparkline([10, 20, 15], max_width=20)
"""

from __future__ import annotations

from typing import Iterable, List

# Default charset: 8-level ramp (low→high)
DEFAULT_CHARS = "▁▂▃▄▅▆▇█"


def clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v


def sparkline(
    values: Iterable[float], charset: str = DEFAULT_CHARS, max_width: int | None = None
) -> str:
    """
    Convert a sequence of non-negative values into a unicode sparkline.

    - If all values are 0 or empty, returns '' (or a run of the lowest glyph if you prefer).
    - max_width truncates the sequence to the last N points.

    Normalization: each value is scaled against the max of the slice to map into the charset.
    """
    buf: List[float] = [float(x) if x is not None else 0.0 for x in values]
    if not buf:
        return ""
    if max_width is not None and max_width > 0 and len(buf) > max_width:
        buf = buf[-max_width:]

    m = max(buf)
    if m <= 0.0:
        return ""  # no signal

    n_levels = len(charset)
    out_chars: List[str] = []
    for v in buf:
        # Scale to [0, n_levels-1]
        idx = int(round(clamp(v / m, 0.0, 1.0) * (n_levels - 1)))
        out_chars.append(charset[idx])
    return "".join(out_chars)
