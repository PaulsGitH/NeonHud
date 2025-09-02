"""
Disk I/O collectors (totals and per-device).
"""

from __future__ import annotations
from typing import Dict, TypedDict

import psutil
from neonhud.core.logging import get_logger

log = get_logger()


class DiskCounters(TypedDict):
    read_bytes: int
    write_bytes: int


class DiskRates(TypedDict):
    read_bps: float
    write_bps: float


def sample() -> DiskCounters:
    """
    Back-compat wrapper expected by tests and snapshot model.
    Returns cumulative bytes read/written across all disks.
    """
    return sample_counters()


def sample_counters() -> DiskCounters:
    io = psutil.disk_io_counters()
    return {
        "read_bytes": int(io.read_bytes) if io else 0,
        "write_bytes": int(io.write_bytes) if io else 0,
    }


def sample_counters_per_device() -> Dict[str, DiskCounters]:
    """
    Return per-device cumulative byte counters.
    """
    per = psutil.disk_io_counters(perdisk=True) or {}
    out: Dict[str, DiskCounters] = {}
    for name, io in per.items():
        out[name] = {
            "read_bytes": int(io.read_bytes),
            "write_bytes": int(io.write_bytes),
        }
    return out


def rates_from(
    prev: DiskCounters, curr: DiskCounters, interval_sec: float = 1.0
) -> DiskRates:
    if interval_sec <= 0:
        interval_sec = 1.0
    dr = max(0, int(curr["read_bytes"]) - int(prev["read_bytes"])) / interval_sec
    dw = max(0, int(curr["write_bytes"]) - int(prev["write_bytes"])) / interval_sec
    return {"read_bps": float(dr), "write_bps": float(dw)}
