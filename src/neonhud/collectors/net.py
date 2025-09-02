"""
Network I/O collector.

Provides:
- sample_counters() -> NetCounters
    Raw cumulative bytes sent/received with a timestamp.
- rates_from(prev, curr) -> NetRates
    Bytes-per-second (rx/tx) computed from two counter snapshots.
"""

from __future__ import annotations

from typing import TypedDict
import time
import psutil

# ----- Types -----------------------------------------------------------------


class NetCounters(TypedDict):
    ts: float
    bytes_sent: int
    bytes_recv: int


class NetRates(TypedDict):
    interval: float
    rx_bps: float
    tx_bps: float


# ----- Sampling ---------------------------------------------------------------


def sample_counters() -> NetCounters:
    """
    Take a single snapshot of cumulative network I/O counters.

    Returns:
        {
            "ts": float,          # seconds since epoch
            "bytes_sent": int,    # cumulative
            "bytes_recv": int,    # cumulative
        }
    """
    io = psutil.net_io_counters()
    # Some platforms may return None if no NICs; guard just in case
    bytes_sent = int(getattr(io, "bytes_sent", 0))
    bytes_recv = int(getattr(io, "bytes_recv", 0))
    return {
        "ts": float(time.time()),
        "bytes_sent": bytes_sent,
        "bytes_recv": bytes_recv,
    }


# ----- Rates -----------------------------------------------------------------


def rates_from(prev: NetCounters, curr: NetCounters) -> NetRates:
    """
    Compute instantaneous RX/TX bytes-per-second between two snapshots.

    Safe for zero/negative intervals (returns zeros).
    """
    dt = float(curr["ts"] - prev["ts"])
    if dt <= 0.0:
        return {"interval": 0.0, "rx_bps": 0.0, "tx_bps": 0.0}

    rx_delta = int(curr["bytes_recv"]) - int(prev["bytes_recv"])
    tx_delta = int(curr["bytes_sent"]) - int(prev["bytes_sent"])

    rx_bps = float(rx_delta) / dt if rx_delta >= 0 else 0.0
    tx_bps = float(tx_delta) / dt if tx_delta >= 0 else 0.0

    return {"interval": dt, "rx_bps": rx_bps, "tx_bps": tx_bps}
