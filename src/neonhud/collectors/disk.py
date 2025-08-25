"""
Disk I/O collector.

Returns:
{
    "read_bytes": int,
    "write_bytes": int
}
"""

from __future__ import annotations

from typing import Dict

import psutil


def sample() -> Dict[str, int]:
    # Aggregate over all disks
    io = psutil.disk_io_counters(nowrap=True)
    if io is None:
        # Some platforms/containers may return None; be resilient
        return {"read_bytes": 0, "write_bytes": 0}

    return {
        "read_bytes": int(getattr(io, "read_bytes", 0) or 0),
        "write_bytes": int(getattr(io, "write_bytes", 0) or 0),
    }
