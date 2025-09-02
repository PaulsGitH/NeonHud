"""
Fixed-length ring buffer for metric histories.
"""

from __future__ import annotations
from collections import deque
from typing import Deque, List


class HistoryBuffer:
    def __init__(self, maxlen: int = 120) -> None:
        self.maxlen = maxlen
        self._dq: Deque[float] = deque(maxlen=maxlen)

    def push(self, value: float) -> None:
        self._dq.append(float(value))

    def values(self) -> List[float]:
        return list(self._dq)

    def latest(self) -> float:
        return self._dq[-1] if self._dq else 0.0

    def __len__(self) -> int:
        return len(self._dq)

    def __iter__(self):
        return iter(self._dq)
