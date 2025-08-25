"""
Snapshot assembly for `neonhud report`.
"""

from __future__ import annotations

from typing import Dict, Any

from neonhud.utils import now_utc_iso
from neonhud.utils.platform import platform_host
from neonhud.collectors import cpu as cpu_col
from neonhud.collectors import mem as mem_col
from neonhud.collectors import disk as disk_col
from neonhud.collectors import net as net_col


SCHEMA_ID = "neonhud.report.v1"


def build() -> Dict[str, Any]:
    """
    Build a single JSON-serializable snapshot of the system state.
    """
    host = platform_host()
    cpu = cpu_col.sample()
    memory = mem_col.sample()
    disk_io = disk_col.sample()
    net_io = net_col.sample()

    return {
        "schema": SCHEMA_ID,
        "timestamp": now_utc_iso(),
        "host": host,
        "cpu": cpu,
        "memory": memory,
        "disk_io": disk_io,
        "net_io": net_io,
    }
