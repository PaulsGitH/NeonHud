"""
Lightweight smoothing utilities (EMA).
"""

from __future__ import annotations
from typing import Iterable, List


def ema(series: Iterable[float], alpha: float) -> List[float]:
    """
    Exponential Moving Average.
      series: input samples (oldest→newest)
      alpha:  smoothing factor in [0.0, 1.0] (higher = more responsive)

    Returns a list of same length as input.
    """
    a = float(alpha)
    if a <= 0.0:
        # no smoothing
        return list(float(x) for x in series)
    if a > 1.0:
        a = 1.0

    it = iter(series)
    try:
        first = float(next(it))
    except StopIteration:
        return []

    out = [first]
    last = first
    for x in it:
        v = float(x)
        last = a * v + (1.0 - a) * last
        out.append(last)
    return out
