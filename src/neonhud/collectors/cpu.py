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
from neonhud.core.logging import get_logger

log = get_logger()


def sample() -> Dict[str, object]:
    """
    Take a non-blocking snapshot of CPU load.
    Uses psutil instantaneous counters (interval=0.0).
    """
    log.debug("Collecting CPU metrics via psutil.cpu_percent")
    per_cpu: List[float] = psutil.cpu_percent(interval=0.0, percpu=True)
    total: float = psutil.cpu_percent(interval=0.0, percpu=False)

    per_cpu = [round(v, 1) for v in per_cpu]
    total = round(total, 1)

    data: Dict[str, object] = {"percent_total": total, "per_cpu": per_cpu}
    log.debug("CPU sample: total=%.1f, per_cpu=%s", total, per_cpu)
    return data
