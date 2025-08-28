"""
Network I/O counters & rate helpers.

Public API:
- sample() -> dict[str, int | float]      # cumulative counters (for snapshot/CLI)
- sample_counters() -> NetCounters        # strongly-typed cumulative counters
- rates_from(prev, curr) -> NetRates      # bytes-per-second between snapshots
"""

from __future__ import annotations

import time
from typing import Dict, TypedDict

import psutil
from neonhud.core.logging import get_logger

log = get_logger()


class NetCounters(TypedDict):
    ts: float
    bytes_sent: int
    bytes_recv: int


class NetRates(TypedDict):
    interval: float
    tx_bps: float
    rx_bps: float


def sample_counters() -> NetCounters:
    """
    Return cumulative network I/O counters (all NICs aggregated) with timestamp.

    Keys:
      ts: epoch seconds (float)
      bytes_sent: int
      bytes_recv: int
    """
    log.debug("Collecting network I/O via psutil.net_io_counters")
    nio = psutil.net_io_counters()
    ts = time.time()
    data: NetCounters = {
        "ts": float(ts),
        "bytes_sent": int(getattr(nio, "bytes_sent", 0) or 0),
        "bytes_recv": int(getattr(nio, "bytes_recv", 0) or 0),
    }
    log.debug("Net counters: %s", data)
    return data


def rates_from(prev: NetCounters, curr: NetCounters) -> NetRates:
    """
    Compute rx/tx bytes-per-second between two snapshots.
    """
    dt = max(0.0, float(curr["ts"]) - float(prev["ts"]))
    if dt == 0.0:
        return {"interval": 0.0, "tx_bps": 0.0, "rx_bps": 0.0}

    d_tx = max(0, int(curr["bytes_sent"]) - int(prev["bytes_sent"]))
    d_rx = max(0, int(curr["bytes_recv"]) - int(prev["bytes_recv"]))
    rates: NetRates = {
        "interval": dt,
        "tx_bps": float(d_tx) / dt,
        "rx_bps": float(d_rx) / dt,
    }
    log.debug("Net rates: %s", rates)
    return rates


def sample() -> Dict[str, int | float]:
    """
    Compatibility wrapper used by snapshot/build(): returns a plain dict
    with cumulative counters (includes 'ts', 'bytes_sent', 'bytes_recv').
    """
    c = sample_counters()
    return {
        "ts": float(c["ts"]),
        "bytes_sent": int(c["bytes_sent"]),
        "bytes_recv": int(c["bytes_recv"]),
    }
