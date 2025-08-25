"""
Network I/O collector.

Returns:
{
    "bytes_sent": int,
    "bytes_recv": int
}
"""

from __future__ import annotations

from typing import Dict

import psutil


def sample() -> Dict[str, int]:
    io = psutil.net_io_counters(nowrap=True)
    if io is None:
        return {"bytes_sent": 0, "bytes_recv": 0}

    return {
        "bytes_sent": int(getattr(io, "bytes_sent", 0) or 0),
        "bytes_recv": int(getattr(io, "bytes_recv", 0) or 0),
    }
