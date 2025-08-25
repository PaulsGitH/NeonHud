"""
CPU metrics collector.
Returns:
{
    "percent_total": float,  # 0.0–100.0
    "per_cpu": [float, ...]  # one entry per logical CPU
}
"""

from __future__ import annotations

from typing import Dict, List

import psutil


def sample() -> Dict[str, object]:
    """
    Take a non-blocking snapshot of CPU load.
    Uses psutil instantaneous counters (interval=0.0).
    """
    per_cpu: List[float] = psutil.cpu_percent(interval=0.0, percpu=True)
    total: float = psutil.cpu_percent(interval=0.0, percpu=False)

    # Normalize floats to one decimal place for stable output
    per_cpu = [round(v, 1) for v in per_cpu]
    total = round(total, 1)

    return {
        "percent_total": total,
        "per_cpu": per_cpu,
    }
