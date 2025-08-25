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


def sample() -> Dict[str, object]:
    vm = psutil.virtual_memory()
    return {
        "total": int(vm.total),
        "used": int(vm.used),
        "available": int(vm.available),
        "percent": round(float(vm.percent), 1),
    }
