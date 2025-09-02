"""
Network I/O collectors (totals and per-interface).
"""

from __future__ import annotations
from typing import Dict, TypedDict
import time

import psutil
from neonhud.core.logging import get_logger

log = get_logger()


class NetCounters(TypedDict):
    ts: float
    bytes_sent: int
    bytes_recv: int


class NetRates(TypedDict):
    tx_bps: float
    rx_bps: float
    send_bps: float
    recv_bps: float
    interval: float


def sample() -> NetCounters:
    """
    Back-compat wrapper expected by tests and snapshot model.
    Returns total network cumulative counters plus timestamp.
    """
    return sample_counters()


def sample_counters() -> NetCounters:
    io = psutil.net_io_counters()
    return {
        "ts": float(time.time()),
        "bytes_sent": int(io.bytes_sent) if io else 0,
        "bytes_recv": int(io.bytes_recv) if io else 0,
    }


def sample_counters_per_nic() -> Dict[str, NetCounters]:
    """
    Return per-interface cumulative byte counters (each includes its own timestamp).
    """
    per = psutil.net_io_counters(pernic=True) or {}
    now = float(time.time())
    out: Dict[str, NetCounters] = {}
    for name, io in per.items():
        out[name] = {
            "ts": now,
            "bytes_sent": int(io.bytes_sent),
            "bytes_recv": int(io.bytes_recv),
        }
    return out


def rates_from(
    prev: NetCounters, curr: NetCounters, interval_sec: float | None = None
) -> NetRates:
    """
    Compute rates either from explicit interval_sec or from prev/curr timestamps.

    Tests expect keys:
      - 'interval', 'tx_bps', 'rx_bps'
    We also return aliases:
      - 'send_bps' == tx_bps, 'recv_bps' == rx_bps
    """
    if interval_sec is None:
        dt = max(0.0, float(curr["ts"]) - float(prev["ts"]))
    else:
        dt = max(0.0, float(interval_sec))

    if dt == 0.0:
        return {
            "tx_bps": 0.0,
            "rx_bps": 0.0,
            "send_bps": 0.0,
            "recv_bps": 0.0,
            "interval": 0.0,
        }

    tx = max(0, int(curr["bytes_sent"]) - int(prev["bytes_sent"])) / dt
    rx = max(0, int(curr["bytes_recv"]) - int(prev["bytes_recv"])) / dt
    return {
        "tx_bps": float(tx),
        "rx_bps": float(rx),
        "send_bps": float(tx),
        "recv_bps": float(rx),
        "interval": dt,
    }
