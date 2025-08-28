"""
Disk I/O counters & rate helpers.

Public API:
- sample() -> dict[str, int | float]      # cumulative counters (for snapshot/CLI)
- sample_counters() -> DiskCounters       # strongly-typed cumulative counters
- rates_from(prev, curr) -> DiskRates     # bytes-per-second between snapshots
"""

from __future__ import annotations

import time
from typing import Dict, TypedDict

import psutil
from neonhud.core.logging import get_logger

log = get_logger()


class DiskCounters(TypedDict):
    ts: float
    read_bytes: int
    write_bytes: int


class DiskRates(TypedDict):
    interval: float
    read_bps: float
    write_bps: float


def sample_counters() -> DiskCounters:
    """
    Return cumulative disk I/O counters (all disks aggregated) with timestamp.

    Keys:
      ts: epoch seconds (float)
      read_bytes: int (cumulative)
      write_bytes: int (cumulative)
    """
    log.debug("Collecting disk I/O counters via psutil.disk_io_counters")
    # nowrap=True is not available on all psutil versions; fall back gracefully.
    try:
        dio = psutil.disk_io_counters(nowrap=True)  # type: ignore[call-arg]
    except TypeError:
        dio = psutil.disk_io_counters()

    ts = time.time()
    data: DiskCounters = {
        "ts": float(ts),
        "read_bytes": int(getattr(dio, "read_bytes", 0) or 0),
        "write_bytes": int(getattr(dio, "write_bytes", 0) or 0),
    }
    log.debug("Disk counters: %s", data)
    return data


def rates_from(prev: DiskCounters, curr: DiskCounters) -> DiskRates:
    """
    Compute read/write bytes-per-second between two snapshots.

    Returns:
      interval: seconds between snapshots
      read_bps: float
      write_bps: float
    """
    dt = max(0.0, float(curr["ts"]) - float(prev["ts"]))
    if dt == 0.0:
        return {"interval": 0.0, "read_bps": 0.0, "write_bps": 0.0}

    d_read = max(0, int(curr["read_bytes"]) - int(prev["read_bytes"]))
    d_write = max(0, int(curr["write_bytes"]) - int(prev["write_bytes"]))
    rates: DiskRates = {
        "interval": dt,
        "read_bps": float(d_read) / dt,
        "write_bps": float(d_write) / dt,
    }
    log.debug("Disk rates: %s", rates)
    return rates


def sample() -> Dict[str, int | float]:
    """
    Compatibility wrapper used by snapshot/build(): returns a plain dict
    with cumulative counters (includes 'ts', 'read_bytes', 'write_bytes').
    """
    c = sample_counters()
    return {
        "ts": float(c["ts"]),
        "read_bytes": int(c["read_bytes"]),
        "write_bytes": int(c["write_bytes"]),
    }
