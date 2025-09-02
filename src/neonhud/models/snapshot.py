"""
Build a single JSON-serializable snapshot of the system state.

Shape:
{
  "schema": "neonhud.report.v1",
  "timestamp": "<UTC ISO8601>",
  "host": {"hostname": str, "os": str, "kernel": str},
  "cpu": {...},        # from collectors.cpu.sample()
  "memory": {...},     # from collectors.mem.sample()
  "disk_io": {...},    # from collectors.disk.sample_counters()
  "net_io": {...}      # from collectors.net.sample_counters()
}
"""

from __future__ import annotations

from typing import Any, Dict
import platform

from neonhud.utils import now_utc_iso
from neonhud.collectors import cpu as cpu_col
from neonhud.collectors import mem as mem_col
from neonhud.collectors import disk as disk_col
from neonhud.collectors import net as net_col


def _platform_host() -> Dict[str, str]:
    """Minimal host block with kernel string included."""
    try:
        hostname = platform.node() or ""
    except Exception:
        hostname = ""
    try:
        system = platform.system() or ""
        release = platform.release() or ""
        os_name = (system + (" " + release if release else "")).strip()
    except Exception:
        os_name = ""
    # Kernel string: prefer platform.version(); fall back to release
    try:
        kernel = platform.version() or release or ""
    except Exception:
        kernel = release if "release" in locals() else ""
    return {"hostname": hostname, "os": os_name, "kernel": kernel}


def build() -> Dict[str, Any]:
    """
    Build a single snapshot dict with stable top-level keys.
    """
    host = _platform_host()
    cpu = cpu_col.sample()
    memory = mem_col.sample()
    disk_io = disk_col.sample_counters()
    net_io = net_col.sample_counters()

    return {
        "schema": "neonhud.report.v1",
        "timestamp": now_utc_iso(),
        "host": host,
        "cpu": cpu,
        "memory": memory,
        "disk_io": disk_io,
        "net_io": net_io,
    }
