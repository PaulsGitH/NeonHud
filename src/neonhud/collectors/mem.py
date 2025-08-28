"""
Memory metrics collector.
Returns:
{
    "total": int,      # bytes
    "used": int,       # bytes
    "available": int,  # bytes
    "percent": float   # 0.0–100.0
}
"""

from __future__ import annotations

from typing import Dict

import psutil
from neonhud.core.logging import get_logger

log = get_logger()


def sample() -> Dict[str, object]:
    log.debug("Collecting memory metrics via psutil.virtual_memory")
    vm = psutil.virtual_memory()
    data: Dict[str, object] = {
        "total": int(vm.total),
        "used": int(vm.used),
        "available": int(vm.available),
        "percent": round(float(vm.percent), 1),
    }
    log.debug("Memory sample: %s", data)
    return data
